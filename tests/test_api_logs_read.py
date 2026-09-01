#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_logs.py's LogsController.read() serving chunked
content of a real log file on disk (as opposed to the in-memory 'env.core.log'
buffer covered by test_api_logs_memlog.py).
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from modules.admin.api_logs import LogsController


class FakeLogs:
    def return_logs(self):
        return {}


class FakeSh:
    def __init__(self):
        self.logs = FakeLogs()

    def get_basedir(self):
        return common.BASE

    def get_config_dir(self, config):
        return os.path.join(common.BASE, 'tests', 'resources', 'etc')

    def get_config_file(self, config):
        return os.path.join(common.BASE, 'tests', 'resources', 'etc', 'logging.yaml')


class FakeModule:
    def __init__(self, sh, chunksize=500):
        self._sh = sh
        self.log_chunksize = chunksize


def _make_controller(tmp_path, chunksize=500):
    """Build a LogsController whose log_dir is an isolated tmp directory."""
    controller = LogsController(FakeModule(FakeSh(), chunksize=chunksize))
    controller.log_dir = str(tmp_path)
    return controller


def _write_log(tmp_path, filename, lines):
    """Write *lines* (already newline-terminated) as filename under tmp_path."""
    with open(os.path.join(tmp_path, filename), 'w', encoding='UTF-8') as f:
        f.writelines(lines)


class TestReadServesFileChunks(unittest.TestCase):
    def setUp(self):
        import tempfile

        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = self._tmpdir.name
        self.addCleanup(self._tmpdir.cleanup)

    def test_whole_file_fits_in_one_chunk(self):
        lines = [f'2026-08-15 10:00:0{i} INFO entry {i}\n' for i in range(5)]
        controller = _make_controller(self.tmp_path, chunksize=500)
        _write_log(self.tmp_path, 'test.log', lines)

        result = json.loads(controller.read(id='test.log', chunk='1'))

        self.assertEqual(result['chunk'], 1)
        self.assertTrue(result['lastchunk'])
        self.assertEqual(result['lines'], [1, 5])
        self.assertEqual(result['chunks'], 1)

    def test_multi_chunk_file_walks_without_gaps_or_duplicates(self):
        # 23 entries, chunksize 10 -> 3 chunks (10, 10, 3), no tracebacks.
        lines = [f'2026-08-15 10:00:00 INFO entry {i}\n' for i in range(23)]
        controller = _make_controller(self.tmp_path, chunksize=10)
        _write_log(self.tmp_path, 'test.log', lines)

        chunk1 = json.loads(controller.read(id='test.log', chunk='1'))
        chunk2 = json.loads(controller.read(id='test.log', chunk='2'))
        chunk3 = json.loads(controller.read(id='test.log', chunk='3'))

        self.assertEqual(chunk1['chunks'], 3)
        self.assertEqual(chunk2['chunks'], 3)
        self.assertEqual(chunk3['chunks'], 3)

        self.assertEqual(chunk1['lines'], [1, 10])
        self.assertEqual(chunk2['lines'], [11, 20])
        self.assertEqual(chunk3['lines'], [21, 23])

        self.assertFalse(chunk1['lastchunk'])
        self.assertFalse(chunk2['lastchunk'])
        self.assertTrue(chunk3['lastchunk'])

        # The reader replaces spaces with NBSP (chr(160)) - existing, unrelated
        # behavior preserved by _iter_log_entries(), not something this test
        # is about; compare against that same transform rather than raw lines.
        expected = [line.replace(' ', chr(160)) for line in lines]
        reassembled = chunk1['loglines'] + chunk2['loglines'] + chunk3['loglines']
        self.assertEqual(reassembled, expected)

    def test_chunk_zero_returns_last_chunk(self):
        lines = [f'2026-08-15 10:00:00 INFO entry {i}\n' for i in range(23)]
        controller = _make_controller(self.tmp_path, chunksize=10)
        _write_log(self.tmp_path, 'test.log', lines)

        result = json.loads(controller.read(id='test.log', chunk='0'))

        self.assertEqual(result['chunk'], 3)
        self.assertEqual(result['lines'], [21, 23])
        self.assertTrue(result['lastchunk'])

    def test_traceback_within_one_chunk_reports_true_raw_line_span(self):
        # 5 raw lines, but only 2 logical entries (the middle 3 lines are a
        # traceback merged into entry 1). 'lines' must reflect the 5 raw
        # lines actually shown, not len(loglines) == 2.
        lines = [
            'INFO entry 0\n',
            'Traceback (most recent call last):\n',
            '  File "x.py", line 1, in <module>\n',
            'ValueError: boom\n',
            'INFO entry 1\n',
        ]
        controller = _make_controller(self.tmp_path, chunksize=500)
        _write_log(self.tmp_path, 'test.log', lines)

        result = json.loads(controller.read(id='test.log', chunk='1'))

        self.assertEqual(len(result['loglines']), 2)
        self.assertEqual(result['lines'], [1, 5])
        self.assertEqual(result['chunks'], 1)
        self.assertTrue(result['lastchunk'])

    def test_traceback_spanning_chunk_boundary_keeps_next_chunk_aligned(self):
        # chunksize=2 (logical entries). Entry 1 merges a 3-line traceback, so
        # chunk 1 (entries 0-1) consumes 5 raw lines, not 2 - chunk 2 must
        # start at raw line 6, right after chunk 1's true raw-line span.
        lines = [
            'INFO entry 0\n',
            'INFO entry 1\n',
            'Traceback (most recent call last):\n',
            '  File "x.py", line 1, in <module>\n',
            'ValueError: boom\n',
            'INFO entry 2\n',
            'INFO entry 3\n',
            'INFO entry 4\n',
        ]
        controller = _make_controller(self.tmp_path, chunksize=2)
        _write_log(self.tmp_path, 'test.log', lines)

        chunk1 = json.loads(controller.read(id='test.log', chunk='1'))
        chunk2 = json.loads(controller.read(id='test.log', chunk='2'))
        chunk3 = json.loads(controller.read(id='test.log', chunk='3'))

        for c in (chunk1, chunk2, chunk3):
            self.assertEqual(c['chunks'], 3)

        self.assertEqual(chunk1['lines'], [1, 5])
        self.assertEqual(chunk2['lines'], [6, 7])
        self.assertEqual(chunk3['lines'], [8, 8])

        self.assertFalse(chunk1['lastchunk'])
        self.assertFalse(chunk2['lastchunk'])
        self.assertTrue(chunk3['lastchunk'])

        # Chunk 2 must start clean on entry 2, not a leftover traceback
        # fragment from entry 1.
        self.assertEqual(len(chunk2['loglines']), 2)
        self.assertTrue(chunk2['loglines'][0].startswith('INFO\xa0entry\xa02'))
        self.assertTrue(chunk2['loglines'][1].startswith('INFO\xa0entry\xa03'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
