#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_files.py's FilesController.save_logging_config().

Coverage: while the built-in debug logging (``smarthome.py -d``) is active, the saved
logging.yaml is written but not applied, and the response says so.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from modules.admin.api_files import FilesController
from tests.mock.core import MockSmartHome


class TestSaveLoggingConfigInDebugMode(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.logging_yaml = os.path.join(self.tmpdir.name, 'logging.yaml')
        with open(self.logging_yaml, 'w', encoding='utf-8') as f:
            f.write('old: content\n')

        self.sh = MockSmartHome()
        self.sh._extern_conf_dir = self.tmpdir.name
        self.sh._structs_dir = self.tmpdir.name
        self.sh._items_dir = self.tmpdir.name
        self.sh._scenes_dir = self.tmpdir.name
        self.sh._functions_dir = self.tmpdir.name
        self.sh._logic_dir = self.tmpdir.name
        self.sh.get_config_file = lambda config, extension='.yaml': self.logging_yaml
        module = MagicMock()
        module._sh = self.sh
        self.controller = FilesController(module)
        self.controller.get_body = lambda text=False, binary=False: 'new: content\n'

    def test_save_is_written_but_not_applied_in_debug_mode(self):
        self.sh.logs.uses_logging_yaml = False
        self.addCleanup(setattr, self.sh.logs, 'uses_logging_yaml', True)

        result = json.loads(self.controller.save_logging_config())

        self.assertEqual(result, {'result': 'ok', 'config_reloaded': False, 'debug_mode': True})
        with open(self.logging_yaml, encoding='utf-8') as f:
            self.assertEqual(f.read(), 'new: content\n')


if __name__ == '__main__':
    unittest.main()
