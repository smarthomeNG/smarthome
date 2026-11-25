"""Tests for lib.log.iter_log_entries: logical entries of a logfile with tracebacks merged."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.log import LogEntry, iter_log_entries


def write_log(tmp_path, lines):
    """Write the (newline-terminated) lines to a logfile and return its path."""
    path = tmp_path / 'test.log'
    path.write_text(''.join(lines), encoding='UTF-8')
    return str(path)


def test_every_plain_line_is_an_entry_numbered_by_its_physical_line(tmp_path):
    path = write_log(tmp_path, ['INFO one\n', 'INFO two\n'])
    assert list(iter_log_entries(path)) == [
        LogEntry(end_line=1, lines=('INFO one\n',)),
        LogEntry(end_line=2, lines=('INFO two\n',)),
    ]


def test_empty_file_has_no_entries(tmp_path):
    assert list(iter_log_entries(write_log(tmp_path, []))) == []


def test_traceback_is_merged_into_the_preceding_entry(tmp_path):
    path = write_log(
        tmp_path,
        [
            'INFO entry 0\n',
            'ERROR failed\n',
            'Traceback (most recent call last):\n',
            '  File "x.py", line 1, in <module>\n',
            'ValueError: boom\n',
            'INFO entry 1\n',
        ],
    )
    entries = list(iter_log_entries(path))
    assert [entry.end_line for entry in entries] == [1, 5, 6]
    assert entries[1].lines == (
        'ERROR failed\n',
        'Traceback (most recent call last):\n',
        '  File "x.py", line 1, in <module>\n',
        'ValueError: boom\n',
    )


def test_last_line_without_newline_is_kept(tmp_path):
    path = write_log(tmp_path, ['INFO one\n', 'INFO two'])
    assert list(iter_log_entries(path))[-1] == LogEntry(end_line=2, lines=('INFO two',))


def test_text_joins_continuation_lines(tmp_path):
    path = write_log(tmp_path, ['ERROR failed\n', 'Traceback (most recent call last):\n', 'ValueError: boom\n'])
    (entry,) = iter_log_entries(path)
    assert entry.text == 'ERROR failed\nTraceback (most recent call last):\nValueError: boom\n'
