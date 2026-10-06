#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the built-in debug logging setup (``smarthome.py -d``) in lib/log.py

Coverage
--------
Logs.configure_debug_logging():
  - DEBUG output of the shng logger families reaches the debug logfile
  - third-party loggers are limited to INFO
  - works without any logging.yaml
  - Logs.uses_logging_yaml reflects which configuration is active

SmartHome.init_logging():
  - MODE 'debug' ignores a broken logging.yaml
"""

import logging
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.log as _log_module
from lib.log import Logs

SHNG_LOGGER_FAMILIES = ['functions', 'lib', 'lib.smarthome', 'modules', 'plugins', 'logics', 'items']


class _LoggingStateGuard(unittest.TestCase):
    """Restores global logging state touched by dictConfig after each test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.logfile = os.path.join(self._tmp.name, 'smarthome-debug.log')

        names = ['', 'somepackage', *SHNG_LOGGER_FAMILIES, 'plugins.testplugin', '_shng_all_handlers_logger']
        saved = {}
        for name in names:
            lg = logging.getLogger(name)
            saved[name] = (lg.level, list(lg.handlers), lg.propagate)

        def restore():
            for name, (level, handlers, propagate) in saved.items():
                lg = logging.getLogger(name)
                for h in list(lg.handlers):
                    if h not in handlers:
                        lg.removeHandler(h)
                        h.close()
                lg.setLevel(level)
                lg.propagate = propagate

        self.addCleanup(restore)

    def make_logs(self):
        _log_module.logs_instance = None
        sh = MagicMock()
        sh.return_event_listeners.return_value = []
        return Logs(sh)

    def read_logfile(self):
        for h in logging.getLogger('').handlers:
            h.flush()
        with open(self.logfile, encoding='utf-8') as f:
            return f.read()


class TestConfigureDebugLogging(_LoggingStateGuard):
    def test_debug_output_of_plugin_logger_reaches_debug_logfile(self):
        logs = self.make_logs()

        self.assertTrue(logs.configure_debug_logging(logfile=self.logfile))
        logging.getLogger('plugins.testplugin').debug('plugin-debug-marker')

        self.assertIn('plugin-debug-marker', self.read_logfile())

    def test_third_party_logger_is_limited_to_info(self):
        logs = self.make_logs()

        logs.configure_debug_logging(logfile=self.logfile)
        logging.getLogger('somepackage').debug('thirdparty-debug-marker')
        logging.getLogger('somepackage').info('thirdparty-info-marker')

        content = self.read_logfile()
        self.assertNotIn('thirdparty-debug-marker', content)
        self.assertIn('thirdparty-info-marker', content)

    def test_all_shng_logger_families_log_debug(self):
        logs = self.make_logs()

        logs.configure_debug_logging(logfile=self.logfile)
        for name in SHNG_LOGGER_FAMILIES:
            logging.getLogger(name).debug(f'family-marker-{name}')

        content = self.read_logfile()
        for name in SHNG_LOGGER_FAMILIES:
            self.assertIn(f'family-marker-{name}', content)

    def test_logfile_directory_is_created(self):
        logs = self.make_logs()
        self.logfile = os.path.join(self._tmp.name, 'var', 'log', 'smarthome-debug.log')

        logs.configure_debug_logging(logfile=self.logfile)
        logging.getLogger('lib').debug('dir-marker')

        self.assertIn('dir-marker', self.read_logfile())

    def test_uses_logging_yaml_is_false_while_debug_config_is_active(self):
        logs = self.make_logs()
        self.assertTrue(logs.uses_logging_yaml)

        logs.configure_debug_logging(logfile=self.logfile)

        self.assertFalse(logs.uses_logging_yaml)


class TestInitLoggingDebugMode(_LoggingStateGuard):
    """SmartHome.init_logging() is exercised with a real Logs; only the SmartHome attributes it reads are stubbed."""

    def setUp(self):
        super().setUp()
        self.broken_yaml = os.path.join(self._tmp.name, 'logging.yaml')
        with open(self.broken_yaml, 'w', encoding='utf-8') as f:
            f.write('handlers: [unclosed\n  : : :')
        self._cwd = os.getcwd()
        os.chdir(self._tmp.name)
        self.addCleanup(os.chdir, self._cwd)
        self.logfile = os.path.join(self._tmp.name, 'var', 'log', 'smarthome-debug.log')

    def init_logging(self, mode):
        import lib.smarthome

        logs = self.make_logs()
        logs._sh.get_config_file.return_value = self.broken_yaml
        logs._sh.get_config_dir.return_value = self._tmp.name
        stub = SimpleNamespace(logs=logs, _log_conf_basename='logging')
        return lib.smarthome.SmartHome.init_logging(stub, 'logging', mode), logs

    def test_debug_mode_ignores_broken_logging_yaml(self):
        result, logs = self.init_logging('debug')

        logging.getLogger('plugins.testplugin').debug('broken-yaml-marker')
        self.assertIs(result, True)
        self.assertFalse(logs.uses_logging_yaml)
        self.assertIn('broken-yaml-marker', self.read_logfile())


if __name__ == '__main__':
    unittest.main()
