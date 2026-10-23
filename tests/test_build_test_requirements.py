#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the plugin selection of tools/build_test_requirements.py.

Coverage
--------
- a plugin with tests and no version bounds contributes its requirements.txt
- a plugin whose py_minversion is above the running Python is skipped
- a plugin whose py_maxversion is below the running Python is skipped
- a plugin without test_*.py files is skipped
"""

import importlib.util
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.shpypi import Requirements_files

TOOL_PATH = os.path.join(os.path.dirname(__file__), '..', 'tools', 'build_test_requirements.py')


def load_tool():
    spec = importlib.util.spec_from_file_location('build_test_requirements', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCollectTestedPluginRequirements(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.plugins_dir = self._tmp.name
        self.req_files = Requirements_files(version='1.12.2.2', for_tests=True)
        self.collect = load_tool().collect_tested_plugin_requirements

    def _make_plugin(self, name, bounds='', with_tests=True):
        plugin_dir = os.path.join(self.plugins_dir, name)
        os.makedirs(os.path.join(plugin_dir, 'tests'))
        with open(os.path.join(plugin_dir, 'plugin.yaml'), 'w') as f:
            f.write(f'plugin:\n    version: 1.0.0\n{bounds}')
        with open(os.path.join(plugin_dir, 'requirements.txt'), 'w') as f:
            f.write('somepackage\n')
        if with_tests:
            with open(os.path.join(plugin_dir, 'tests', 'test_x.py'), 'w') as f:
                f.write('')
        return os.path.join(plugin_dir, 'requirements.txt')

    def _collected_names(self):
        files = self.collect(self.plugins_dir, self.req_files)
        return [os.path.basename(os.path.dirname(path)) for path in files]

    def test_plugin_without_bounds_is_included(self):
        self._make_plugin('plain')
        self.assertEqual(self._collected_names(), ['plain'])

    def test_plugin_requiring_newer_python_is_skipped(self):
        self._make_plugin('future', bounds="    py_minversion: '99.0'\n")
        self.assertEqual(self._collected_names(), [])

    def test_plugin_limited_to_older_python_is_skipped(self):
        self._make_plugin('past', bounds="    py_maxversion: '1.0'\n")
        self.assertEqual(self._collected_names(), [])

    def test_plugin_without_test_files_is_skipped(self):
        self._make_plugin('untested', with_tests=False)
        self.assertEqual(self._collected_names(), [])


if __name__ == '__main__':
    unittest.main()
