#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for PluginLoggingAdapter, the ``self.logger`` of SmartPlugins.

Records go through a real logger into ``assertLogs``; ``lib.plugin._SH.logs`` is the ``Logs``
class, whose level constants are class attributes.
"""

import logging
import os
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.log import Logs
from lib.plugin import PluginLoggingAdapter

CUSTOM_LEVEL_METHODS = {
    'notice': Logs.NOTICE_level,
    'develop': Logs.DEVELOP_level,
    'dbghigh': Logs.DBGHIGH_level,
    'dbgmed': Logs.DBGMED_level,
    'dbglow': Logs.DBGLOW_level,
}


class TestCustomLevelMethods(unittest.TestCase):
    """The custom level methods log like the standard ones: caller location, instance prefix and extra."""

    def setUp(self):
        patcher = patch('lib.plugin._SH', types.SimpleNamespace(logs=Logs))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.logger = logging.getLogger('tests.plugin_logging_adapter')
        self.logger.setLevel(1)
        self.addCleanup(self.logger.setLevel, logging.NOTSET)
        self.adapter = PluginLoggingAdapter(self.logger, {'plugininstance': 'inst: '})

    def _record(self, method_name: str) -> tuple[logging.LogRecord, int]:
        """Log through ``method_name``; return the record and the line of the call."""
        with self.assertLogs(self.logger, 1) as logs:
            getattr(self.adapter, method_name)('msg %s', 'arg')
            line = sys._getframe().f_lineno - 1
        return logs.records[0], line

    def test_record_names_the_callers_location(self):
        for name in CUSTOM_LEVEL_METHODS:
            with self.subTest(name):
                record, line = self._record(name)
                self.assertEqual(os.path.basename(__file__), record.filename)
                self.assertEqual('_record', record.funcName)
                self.assertEqual(line, record.lineno)

    def test_record_has_level_prefix_and_extra(self):
        for name, level in CUSTOM_LEVEL_METHODS.items():
            with self.subTest(name):
                record, _ = self._record(name)
                self.assertEqual(level, record.levelno)
                self.assertEqual('inst: msg arg', record.getMessage())
                self.assertEqual('inst: ', record.plugininstance)

    def test_explicit_stacklevel_is_honoured(self):
        def helper():
            self.adapter.dbghigh('msg', stacklevel=2)

        with self.assertLogs(self.logger, 1) as logs:
            helper()

        self.assertEqual('test_explicit_stacklevel_is_honoured', logs.records[0].funcName)


if __name__ == '__main__':
    unittest.main()
