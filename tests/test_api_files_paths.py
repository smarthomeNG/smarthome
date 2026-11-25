#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for file names taken from admin API URLs: they must stay inside their config directory,
and a failed config restore must give SmartHomeNG its previous status back.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

from modules.admin.api_files import FilesController
from modules.admin.rest import contained_path
from tests.mock.core import MockSmartHome


class TestContainedPath(unittest.TestCase):
    def test_name_inside_base_dir(self):
        self.assertEqual(os.path.join('/conf', 'items', 'a.yaml'), contained_path('/conf/items', 'a.yaml'))

    def test_subdirectory_is_allowed(self):
        self.assertEqual(os.path.join('/conf', 'items', 'sub', 'a.yaml'), contained_path('/conf/items/', 'sub/a.yaml'))

    def test_parent_reference_is_refused(self):
        with self.assertRaises(cherrypy.HTTPError) as raised:
            contained_path('/conf/items', '../etc/admin.yaml')
        self.assertEqual(400, raised.exception.status)

    def test_absolute_name_is_refused(self):
        with self.assertRaises(cherrypy.HTTPError):
            contained_path('/conf/items', '/etc/passwd')

    def test_sibling_with_common_prefix_is_refused(self):
        with self.assertRaises(cherrypy.HTTPError):
            contained_path('/conf/items', '../items2/a.yaml')


class _FilesBase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._extern_conf_dir = self.tmpdir.name
        for name in ('structs', 'items', 'scenes', 'functions', 'logic'):
            setattr(self.sh, f'_{name}_dir', os.path.join(self.tmpdir.name, name))
            os.makedirs(os.path.join(self.tmpdir.name, name))
        module = MagicMock()
        module._sh = self.sh
        self.controller = FilesController(module)


class TestFilesControllerRefusesTraversal(_FilesBase):
    def test_struct_config_outside_structs_dir_is_refused(self):
        with open(os.path.join(self.tmpdir.name, 'secret.yaml'), 'w') as f:
            f.write('x')

        with self.assertRaises(cherrypy.HTTPError):
            self.controller.get_struct_config('../secret')


class TestRestoreConfigStatus(_FilesBase):
    def setUp(self):
        super().setUp()
        self.sh.shng_status = {'code': 20, 'text': 'Running'}
        self.sh.get_vardir = lambda: self.tmpdir.name

    def test_failed_upload_restores_previous_status(self):
        request = MagicMock()
        request.headers = {}
        with patch.object(cherrypy, 'request', request), self.assertRaises(cherrypy.HTTPError):
            self.controller.restore_config('backup.zip')

        self.assertEqual(20, self.sh.shng_status['code'])

    def test_failed_restore_restores_previous_status(self):
        body = b'data:application/zip;base64,UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        request = MagicMock()
        request.headers = {'Content-Length': str(len(body))}
        request.body.read = lambda n: body
        with patch.object(cherrypy, 'request', request), patch('lib.backup.restore_backup', return_value=None):
            self.controller.restore_config('backup.zip')

        self.assertEqual(20, self.sh.shng_status['code'])

    def test_upload_name_outside_restore_dir_is_refused(self):
        body = b'data:application/zip;base64,UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA=='
        request = MagicMock()
        request.headers = {'Content-Length': str(len(body))}
        request.body.read = lambda n: body
        with patch.object(cherrypy, 'request', request), self.assertRaises(cherrypy.HTTPError):
            self.controller.restore_config('../../evil.zip')

        self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.tmpdir.name), 'evil.zip')))
        self.assertEqual(20, self.sh.shng_status['code'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
