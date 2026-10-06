#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for starting SmartHomeNG without installed or configured plugins.

Coverage
--------
bin.shngversion:
  - imports and reports a plugins version although the ``plugins`` package is not importable

lib.config.parse_basename():
  - an empty plugin configuration is a WARNING ("no plugins configured"), not an ERROR

SmartHome.check_plugins_installed():
  - a missing plugins folder is a WARNING and does not abort
"""

import importlib.util
import logging
import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.config
import lib.smarthome

BASE = os.path.join(os.path.dirname(__file__), '..')


class TestShngversionWithoutPluginsPackage(unittest.TestCase):
    def test_plugins_version_is_reported_without_plugins_package(self):
        spec = importlib.util.spec_from_file_location(
            'shngversion_without_plugins', os.path.join(BASE, 'bin', 'shngversion.py')
        )
        module = importlib.util.module_from_spec(spec)
        saved = sys.modules.get('plugins.__init__', ...)
        sys.modules['plugins.__init__'] = None  # makes 'import plugins.__init__' raise ImportError
        try:
            spec.loader.exec_module(module)
        finally:
            if saved is ...:
                del sys.modules['plugins.__init__']
            else:
                sys.modules['plugins.__init__'] = saved

        self.assertIsInstance(module.get_plugins_version(), str)


class TestEmptyPluginConfiguration(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.basename = os.path.join(self._tmp.name, 'plugin')

    def parse_logging(self):
        with self.assertLogs('lib.config', level=logging.DEBUG) as captured:
            result = lib.config.parse_basename(self.basename, configtype='plugin')
        return result, [(r.levelname, r.getMessage()) for r in captured.records]

    def test_empty_plugin_yaml_warns_that_no_plugins_are_configured(self):
        open(self.basename + '.yaml', 'w').close()

        result, records = self.parse_logging()

        self.assertEqual(result, {})
        self.assertEqual([level for level, _ in records], ['WARNING'])
        self.assertIn('No plugins configured', records[0][1])

    def test_missing_plugin_yaml_warns_that_no_plugins_are_configured(self):
        _, records = self.parse_logging()

        self.assertEqual([level for level, _ in records], ['WARNING'])
        self.assertIn('No plugins configured', records[0][1])

    def test_missing_config_of_other_type_is_still_an_error(self):
        with self.assertLogs('lib.config', level=logging.DEBUG) as captured:
            lib.config.parse_basename(os.path.join(self._tmp.name, 'other'), configtype='something')

        self.assertEqual([r.levelname for r in captured.records], ['ERROR'])


class TestCheckPluginsInstalled(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def check(self, plugins_dir):
        logger = logging.getLogger('test_check_plugins_installed')
        stub = SimpleNamespace(_plugins_dir=plugins_dir, _logger=logger)
        with self.assertLogs(logger, level=logging.DEBUG) as captured:
            logger.debug('sentinel')  # assertLogs fails if nothing is logged
            result = lib.smarthome.SmartHome.check_plugins_installed(stub)
        return result, [(r.levelname, r.getMessage()) for r in captured.records if r.getMessage() != 'sentinel']

    def test_missing_plugins_folder_warns_without_aborting(self):
        missing = os.path.join(self._tmp.name, 'plugins')

        result, records = self.check(missing)

        self.assertFalse(result)
        self.assertEqual([level for level, _ in records], ['WARNING'])
        self.assertIn('No plugins installed', records[0][1])
        self.assertIn(missing, records[0][1])

    def test_plugins_folder_without_database_plugin_is_accepted_silently(self):
        os.mkdir(os.path.join(self._tmp.name, 'cli'))

        result, records = self.check(self._tmp.name)

        self.assertTrue(result)
        self.assertEqual(records, [])


if __name__ == '__main__':
    unittest.main()
