#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for modules/admin/api_loggers.py's LoggersController.read().

GET /api/loggers must require a valid token like every sibling controller's
read handler (api_items, api_system, api_plugin, ...) - the shngadmin
frontend only calls this API from logged-in routes, so there's no
legitimate pre-auth caller.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

from modules.admin.api_loggers import LoggersController


class FakeSh:
    def get_basedir(self):
        return '/tmp'

    _etc_dir = '/tmp'


class FakeModule:
    _sh = FakeSh()


class TestLoggersReadRequiresAuth(unittest.TestCase):
    def setUp(self):
        self.controller = LoggersController(FakeModule())
        request = MagicMock()
        request.method = 'GET'
        request.headers = {'Origin': 'http://example.test'}
        response = MagicMock()
        response.headers = {}
        self._patches = [patch.object(cherrypy, 'request', request), patch.object(cherrypy, 'response', response)]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self._patches])

    def test_read_is_flagged_authentication_needed(self):
        self.assertTrue(LoggersController.read.authentication_needed)

    def test_get_loggers_without_token_is_rejected(self):
        # FakeSh has no .logs, so if read() actually ran (auth bypassed) this
        # would fail with an AttributeError-flavored error response instead
        # of the specific 'Unauthorized' one - distinguishing "auth rejected"
        # from "read() ran and crashed" without needing to mock read() away.
        result = self.controller.default()

        self.assertIn('"description": "Unauthorized"', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
