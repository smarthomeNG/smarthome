#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_logs.py's LogsController.read() serving the
in-memory 'env.core.log' warning/error buffer (lib.log.ShngMemLogHandler)
alongside its existing file-log content.

The memory log is already maintained incrementally at log-emit time with no
disk I/O (see lib/log.py's Logs.initMemLog()/ShngMemLogHandler) - this just
exposes the existing buffer via the id dispatch read() already uses for
file logs, so a dashboard widget can tail it without scanning log files.
"""

import datetime
import json
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.log as _log_module
from lib.log import Log, Logs
from modules.admin.api_logs import LogsController


class FakeSh:
    def get_basedir(self):
        return common.BASE

    def get_config_dir(self, config):
        return os.path.join(common.BASE, 'tests', 'resources', 'etc')

    def get_config_file(self, config):
        return os.path.join(common.BASE, 'tests', 'resources', 'etc', 'logging.yaml')


class FakeModule:
    log_chunksize = 500

    def __init__(self, sh):
        self._sh = sh


def _make_controller_with_memlog(maxlen=50):
    """Build a LogsController wired to a real (but isolated) Logs/Log pair."""
    _log_module.logs_instance = None
    sh = FakeSh()
    sh.return_event_listeners = MagicMock(return_value=[])
    logs = Logs(sh)
    logs._logs = {}
    logs.logging_levels = {}
    sh.logs = logs

    mem_log = Log(sh, 'env.core.log', None, maxlen=maxlen)

    controller = LogsController(FakeModule(sh))
    return controller, mem_log


class TestReadServesMemlogById(unittest.TestCase):
    def setUp(self):
        self.controller, self.mem_log = _make_controller_with_memlog()
        # lib.log.logs_instance is a process-global singleton; leaving it
        # pointed at this test's FakeSh (no .shtime) breaks any later test
        # file that builds a real MockSmartHome() in the same pytest run.
        self.addCleanup(setattr, _log_module, 'logs_instance', None)

    def test_unregistered_id_falls_through_to_file_lookup(self):
        # id that is neither a registered memory log nor a real file on disk
        # must still 404 like before this change, not silently succeed.
        with self.assertRaises(Exception):
            self.controller.read(id='not_a_real_log_or_file')

    def test_registered_memlog_id_returns_its_entries(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        self.mem_log.add([now, 'MainThread', 'WARNING', 'knx plugin paused'])
        self.mem_log.add([now, 'MainThread', 'ERROR', 'weather station timeout'])

        result = json.loads(self.controller.read(id='env.core.log'))

        self.assertEqual(result['name'], 'env.core.log')
        self.assertEqual(len(result['entries']), 2)
        # Log.add() prepends (appendleft), so newest entry comes first
        self.assertEqual(result['entries'][0]['message'], 'weather station timeout')
        self.assertEqual(result['entries'][0]['level'], 'ERROR')
        self.assertEqual(result['entries'][1]['message'], 'knx plugin paused')

    def test_count_param_limits_returned_entries(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        for i in range(5):
            self.mem_log.add([now, 'MainThread', 'WARNING', f'entry {i}'])

        result = json.loads(self.controller.read(id='env.core.log', count='2'))

        self.assertEqual(len(result['entries']), 2)
        self.assertEqual(result['entries'][0]['message'], 'entry 4')
        self.assertEqual(result['entries'][1]['message'], 'entry 3')

    def test_non_numeric_count_falls_back_to_default(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        for i in range(15):
            self.mem_log.add([now, 'MainThread', 'WARNING', f'entry {i}'])

        result = json.loads(self.controller.read(id='env.core.log', count='bogus'))

        self.assertEqual(len(result['entries']), 10)

    def test_empty_memlog_returns_empty_entries(self):
        result = json.loads(self.controller.read(id='env.core.log'))

        self.assertEqual(result['entries'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
