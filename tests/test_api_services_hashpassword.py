#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for PUT /api/services/hashpassword/ of modules/admin/api_services.py."""

import json
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

from lib.utils import Utils
from modules.admin.api_services import ServicesController
from tests.mock.core import MockSmartHome


class TestHashPassword(unittest.TestCase):
    def setUp(self):
        module = MagicMock()
        module._sh = MockSmartHome()
        self.controller = ServicesController(module)

    def put(self, body: bytes):
        request = MagicMock()
        request.headers = {'Content-Length': str(len(body))}
        request.body.read = lambda n: body
        with patch.object(cherrypy, 'request', request):
            return self.controller.hashpassword()

    def test_returns_salted_hash(self):
        result = json.loads(self.put(b'secret'))

        self.assertTrue(Utils.check_hashed_password('secret', result['hash']))
        self.assertFalse(Utils.is_legacy_password_hash(result['hash']))

    def test_password_is_not_logged(self):
        self.controller.logger.setLevel(logging.DEBUG)
        with self.assertLogs(level=logging.DEBUG) as logs:
            logging.getLogger('dummy').debug('x')
            self.put(b'secret-pw')
        self.assertNotIn('secret-pw', '\n'.join(logs.output))

    def test_checkpassword(self):
        hashed = Utils.hash_password('secret')
        for password, expected in (('secret', True), ('wrong', False)):
            body = json.dumps({'password': password, 'hash': hashed}).encode()
            request = MagicMock()
            request.headers = {'Content-Length': str(len(body))}
            request.body.read = lambda n, body=body: body
            with patch.object(cherrypy, 'request', request):
                self.assertEqual(expected, json.loads(self.controller.checkpassword())['match'])

    def test_empty_password_is_refused(self):
        with self.assertRaises(cherrypy.HTTPError):
            self.put(b'')


if __name__ == '__main__':
    unittest.main()
