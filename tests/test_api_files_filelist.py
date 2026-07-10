#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_files.py's FilesController filelist endpoints.

Coverage: get_structs_filelist(), get_items_filelist(), get_scenes_filelist(),
get_functions_filelist(), get_logics_filelist() correctly drop macOS
AppleDouble sidecar files ("._<name>") that a filesystem can leave next to
a real file — never real config content, never something a user should be
offered to pick in shngadmin's file selectors.
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


class _Base(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._extern_conf_dir = self.tmpdir.name
        self.sh._structs_dir = self.tmpdir.name
        self.sh._items_dir = self.tmpdir.name
        self.sh._scenes_dir = self.tmpdir.name
        self.sh._functions_dir = self.tmpdir.name
        self.sh._logic_dir = self.tmpdir.name
        module = MagicMock()
        module._sh = self.sh
        self.controller = FilesController(module)

    def _touch(self, *names):
        for name in names:
            open(os.path.join(self.tmpdir.name, name), 'w').close()


class TestFilelistsDropAppleDoubleSidecars(_Base):
    def test_structs_filelist_drops_sidecar(self):
        self._touch('foo.yaml', '._foo.yaml')

        result = json.loads(self.controller.get_structs_filelist())

        self.assertEqual(result['files'], ['foo.yaml'])

    def test_items_filelist_drops_sidecar(self):
        self._touch('foo.yaml', '._foo.yaml', 'bar.conf', '._bar.conf')

        result = json.loads(self.controller.get_items_filelist())

        self.assertEqual(sorted(result), ['bar.conf', 'foo.yaml'])

    def test_scenes_filelist_drops_sidecar(self):
        self._touch('foo.yaml', '._foo.yaml')

        result = json.loads(self.controller.get_scenes_filelist())

        self.assertEqual(result, ['foo.yaml'])

    def test_functions_filelist_drops_sidecar(self):
        self._touch('foo.py', '._foo.py')

        result = json.loads(self.controller.get_functions_filelist())

        self.assertEqual(result, ['foo.py'])

    def test_logics_filelist_drops_sidecar(self):
        self._touch('foo.py', '._foo.py')

        result = json.loads(self.controller.get_logics_filelist())

        self.assertEqual(result, ['foo.py'])
