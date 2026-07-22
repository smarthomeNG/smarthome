#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/log.py

Coverage
--------
Logs class:
  - add_logging_level()    — registers a new Python logging level
  - add_log() / return_logs() — memory-log registry management
  - get_shng_logging_levels() — returns level dict

Log class (in-memory deque):
  - __init__               — default and custom mapping, maxlen, handler
  - add()                  — prepends entries, notifies event listeners
  - last()                 — returns N newest entries
  - export()               — returns N entries as list of dicts
  - clean()                — removes entries older than a given datetime

EnglishLocale:
  - _convert_strftime_to_babel() — converts strftime format codes to Babel
"""

import collections
import datetime
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.log as _log_module
from lib.log import Logs, Log, EnglishLocale


# ---------------------------------------------------------------------------
# Helper: create a minimal Logs instance without configure_logging
# ---------------------------------------------------------------------------


def _make_logs():
    _log_module.logs_instance = None
    sh = MagicMock()
    sh.return_event_listeners.return_value = []
    logs = Logs(sh)
    logs._logs = {}
    logs.logging_levels = {}
    return logs


# ===========================================================================
# Logs.add_logging_level
# ===========================================================================


class TestAddLoggingLevel(unittest.TestCase):
    def setUp(self):
        self.logs = _make_logs()

    def test_level_registered_in_logging(self):
        self.logs.add_logging_level('TESTLEVEL99', 99)
        self.assertEqual(logging.getLevelName(99), 'TESTLEVEL99')

    def test_level_registered_in_logging_levels_dict(self):
        self.logs.add_logging_level('TESTLEVEL98', 98)
        self.assertIn(98, self.logs.logging_levels)
        self.assertEqual(self.logs.logging_levels[98], 'TESTLEVEL98')

    def test_level_method_added_to_logger_class(self):
        self.logs.add_logging_level('TESTLEVEL97', 97)
        self.assertTrue(hasattr(logging.getLoggerClass(), 'testlevel97'))

    def test_level_constant_added_to_logging_module(self):
        self.logs.add_logging_level('TESTLEVEL96', 96)
        self.assertEqual(logging.TESTLEVEL96, 96)


# ===========================================================================
# Logs.add_log / return_logs
# ===========================================================================


class TestLogsRegistry(unittest.TestCase):
    def setUp(self):
        self.logs = _make_logs()

    def test_add_log_stores_entry(self):
        mock_log = MagicMock()
        self.logs.add_log('mylog', mock_log)
        self.assertIn('mylog', self.logs.return_logs())

    def test_return_logs_empty_initially(self):
        self.assertEqual(self.logs.return_logs(), {})

    def test_return_logs_contains_added_log(self):
        mock_log = MagicMock()
        self.logs.add_log('testlog', mock_log)
        result = self.logs.return_logs()
        self.assertIs(result['testlog'], mock_log)

    def test_add_multiple_logs(self):
        self.logs.add_log('log_a', MagicMock())
        self.logs.add_log('log_b', MagicMock())
        result = self.logs.return_logs()
        self.assertIn('log_a', result)
        self.assertIn('log_b', result)


# ===========================================================================
# Logs.get_shng_logging_levels
# ===========================================================================


class TestGetShngLoggingLevels(unittest.TestCase):
    def setUp(self):
        self.logs = _make_logs()

    def test_returns_dict(self):
        self.logs.logging_levels = {29: 'NOTICE', 13: 'DBGHIGH'}
        result = self.logs.get_shng_logging_levels()
        self.assertIsInstance(result, dict)

    def test_returns_populated_dict(self):
        self.logs.logging_levels = {29: 'NOTICE', 10: 'DEBUG'}
        result = self.logs.get_shng_logging_levels()
        self.assertEqual(result[29], 'NOTICE')


# ===========================================================================
# Log (in-memory deque)
# ===========================================================================


def _make_log(name='test_log', mapping=None, maxlen=10):
    """Create a Log instance using a pre-existing logs_instance."""
    logs = _make_logs()
    sh = logs._sh
    return Log(sh, name, mapping, maxlen=maxlen)


class TestLogInit(unittest.TestCase):
    def test_default_mapping(self):
        log = _make_log()
        self.assertEqual(log.mapping, ['time', 'thread', 'level', 'message'])

    def test_custom_mapping(self):
        log = _make_log(mapping=['ts', 'msg'])
        self.assertEqual(log.mapping, ['ts', 'msg'])

    def test_none_mapping_uses_default(self):
        log = _make_log(mapping=None)
        self.assertEqual(log.mapping, ['time', 'thread', 'level', 'message'])

    def test_empty_mapping_uses_default(self):
        log = _make_log(mapping=[])
        self.assertEqual(log.mapping, ['time', 'thread', 'level', 'message'])

    def test_maxlen_respected(self):
        log = _make_log(maxlen=5)
        for i in range(10):
            log.append((i, '', '', ''))
        self.assertEqual(len(log), 5)

    def test_registered_in_logs_instance(self):
        _make_log(name='unique_log_xyz')
        self.assertIn('unique_log_xyz', _log_module.logs_instance.return_logs())


class TestLogAdd(unittest.TestCase):
    def setUp(self):
        self.log = _make_log()
        self.log._sh.return_event_listeners.return_value = []

    def test_add_prepends_entry(self):
        entry = (datetime.datetime(2024, 1, 1), 'main', 'INFO', 'msg')
        self.log.add(entry)
        self.assertEqual(list(self.log)[0], entry)

    def test_add_multiple_newest_first(self):
        e1 = (datetime.datetime(2024, 1, 1), '', '', 'first')
        e2 = (datetime.datetime(2024, 1, 2), '', '', 'second')
        self.log.add(e1)
        self.log.add(e2)
        # Most recent is at index 0 (appendleft)
        self.assertEqual(list(self.log)[0][3], 'second')
        self.assertEqual(list(self.log)[1][3], 'first')

    def test_add_notifies_event_listeners(self):
        listener = MagicMock()
        self.log._sh.return_event_listeners.return_value = [listener]
        entry = (datetime.datetime(2024, 1, 1), '', '', 'test')
        self.log.add(entry)
        listener.assert_called_once()


class TestLogLast(unittest.TestCase):
    def setUp(self):
        self.log = _make_log()
        self.log._sh.return_event_listeners.return_value = []
        # add() uses appendleft, so entries are added oldest-first here and
        # msg4 (added last) ends up newest, at index 0
        for i in range(5):
            self.log.add((i, '', '', f'msg{i}'))

    def test_last_returns_n_entries(self):
        result = self.log.last(3)
        self.assertEqual(len(result), 3)

    def test_last_returns_newest_n(self):
        # regression test: last() used to return list(self)[-number:], the
        # OLDEST surviving entries, contradicting its own docstring and its
        # sibling export(), which correctly uses [:number] on the same deque
        result = self.log.last(1)
        self.assertEqual(result[0][3], 'msg4')

    def test_last_returns_newest_n_in_order(self):
        result = self.log.last(3)
        self.assertEqual([entry[3] for entry in result], ['msg4', 'msg3', 'msg2'])

    def test_last_zero_returns_empty_list(self):
        result = self.log.last(0)
        self.assertEqual(len(result), 0)


class TestLogExport(unittest.TestCase):
    def setUp(self):
        self.log = _make_log(mapping=['time', 'level', 'message'])
        self.log._sh.return_event_listeners.return_value = []
        now = datetime.datetime(2024, 6, 1, 10, 0, 0)
        self.log.add((now, 'INFO', 'hello'))
        self.log.add((now, 'WARNING', 'world'))

    def test_export_returns_list_of_dicts(self):
        result = self.log.export(2)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)

    def test_export_uses_mapping_as_keys(self):
        result = self.log.export(1)
        self.assertIn('time', result[0])
        self.assertIn('level', result[0])
        self.assertIn('message', result[0])

    def test_export_n_limits_count(self):
        result = self.log.export(1)
        self.assertEqual(len(result), 1)

    def test_export_values_match_entries(self):
        result = self.log.export(2)
        messages = [r['message'] for r in result]
        self.assertIn('hello', messages)
        self.assertIn('world', messages)


class TestLogClean(unittest.TestCase):
    def setUp(self):
        self.log = _make_log()
        self.log._sh.return_event_listeners.return_value = []

    def test_clean_removes_old_entries(self):
        old = datetime.datetime(2024, 1, 1)
        new = datetime.datetime(2024, 6, 1)
        # appendleft = newest first; log internal order newest→oldest
        self.log.appendleft((new, '', '', 'new'))
        self.log.appendleft((old, '', '', 'old'))
        # Wait: appendleft puts things at left — but clean() pops from RIGHT
        # Rebuild with correct order: newest at left (index 0)
        self.log.clear()
        self.log.appendleft((old, '', '', 'old'))  # goes to right after next
        self.log.appendleft((new, '', '', 'new'))  # now at index 0

        threshold = datetime.datetime(2024, 3, 1)
        self.log.clean(threshold)
        # Only 'new' should remain (it is > threshold)
        remaining = [e[3] for e in list(self.log)]
        self.assertIn('new', remaining)
        self.assertNotIn('old', remaining)


# ===========================================================================
# EnglishLocale._convert_strftime_to_babel
# ===========================================================================


class TestConvertStrftimeToBabel(unittest.TestCase):
    def setUp(self):
        import pytz

        self.tz = pytz.timezone('UTC')
        self.formatter = EnglishLocale.__new__(EnglishLocale)
        self.formatter.tzinfo = self.tz

    def test_year_4_digit(self):
        result = self.formatter._convert_strftime_to_babel('%Y')
        self.assertIn('yyyy', result)

    def test_month_number(self):
        result = self.formatter._convert_strftime_to_babel('%m')
        self.assertIn('MM', result)

    def test_day(self):
        result = self.formatter._convert_strftime_to_babel('%d')
        self.assertIn('dd', result)

    def test_hour_24(self):
        result = self.formatter._convert_strftime_to_babel('%H')
        self.assertIn('HH', result)

    def test_minute(self):
        result = self.formatter._convert_strftime_to_babel('%M')
        self.assertIn('mm', result)

    def test_second(self):
        result = self.formatter._convert_strftime_to_babel('%S')
        self.assertIn('ss', result)

    def test_combined_format(self):
        result = self.formatter._convert_strftime_to_babel('%Y-%m-%d %H:%M:%S')
        self.assertIn('yyyy', result)
        self.assertIn('MM', result)
        self.assertIn('dd', result)
        self.assertIn('HH', result)

    def test_none_input_returns_none(self):
        # None datefmt → return None (consistent with __init__'s if datefmt else None)
        result = self.formatter._convert_strftime_to_babel(None)
        self.assertIsNone(result)

    def test_abbreviated_month_name(self):
        result = self.formatter._convert_strftime_to_babel('%b')
        self.assertIn('MMM', result)

    def test_full_month_name(self):
        result = self.formatter._convert_strftime_to_babel('%B')
        self.assertIn('MMMM', result)

    def test_2_digit_year(self):
        result = self.formatter._convert_strftime_to_babel('%y')
        self.assertIn('yy', result)


if __name__ == '__main__':
    unittest.main()
