#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Admin._error_page_json() (modules/admin/__init__.py) — the
JSON error body wired into the /api tree's error_page.* hooks.

Before this existed, every /api/* error (400/401/404/405/411/500) went
through _error_page(), which always returns an HTML page regardless of
the client's Accept header. The shngadmin frontend reads error text via
``err.error.error`` (an HttpErrorResponse's parsed JSON body) — against
an HTML response, that's always undefined, so every error-message-driven
frontend flow (cycle/collision wording, offering to auto-create missing
parent items on rename, etc.) silently fell back to a generic message
instead, with no way to tell flows apart.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

from modules.admin import Admin


class _FakeAdmin:
    """Stand-in for an Admin instance — _error_page_json() only reads
    self._showtraceback, so nothing heavier is needed."""

    def __init__(self, showtraceback=False):
        self._showtraceback = showtraceback


class TestErrorPageJson(unittest.TestCase):
    def test_returns_json_with_the_error_message(self):
        result = Admin._error_page_json(_FakeAdmin(), '400 Bad Request', 'name collision', 'tb', '18')

        self.assertEqual(json.loads(result), {'error': 'name collision', 'status': '400'})

    def test_sets_json_content_type(self):
        Admin._error_page_json(_FakeAdmin(), '400 Bad Request', 'name collision', 'tb', '18')

        self.assertEqual(cherrypy.response.headers.get('Content-Type'), 'application/json')

    def test_omits_traceback_by_default(self):
        result = Admin._error_page_json(_FakeAdmin(), '500 Internal Server Error', 'boom', 'the traceback', '18')

        self.assertNotIn('traceback', json.loads(result))

    def test_includes_traceback_for_500_when_showtraceback_is_enabled(self):
        result = Admin._error_page_json(
            _FakeAdmin(showtraceback=True), '500 Internal Server Error', 'boom', 'the traceback', '18'
        )

        self.assertEqual(json.loads(result)['traceback'], 'the traceback')

    def test_omits_traceback_for_non_500_even_when_showtraceback_is_enabled(self):
        result = Admin._error_page_json(
            _FakeAdmin(showtraceback=True), '400 Bad Request', 'name collision', 'the traceback', '18'
        )

        self.assertNotIn('traceback', json.loads(result))


if __name__ == '__main__':
    unittest.main()
