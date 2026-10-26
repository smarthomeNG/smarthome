#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib.network.Http.get_binary().

Like its siblings get_json()/get_text()/download(), get_binary() must
check the return value of the internal __get() call before touching
self._response: on a failed request, __get() sets self._response = None
and returns False, so get_binary() must return None like the rest of the
family, not raise AttributeError ('NoneType' object has no attribute
'content').
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.network import Http


class TestHttpGetBinary(unittest.TestCase):
    def test_returns_none_on_failed_request(self):
        http = Http(baseurl='http://example.invalid')
        with patch.object(http._session, 'get', side_effect=ConnectionError('boom')):
            result = http.get_binary('/some/path')
        self.assertIsNone(result)

    def test_returns_content_on_successful_request(self):
        http = Http(baseurl='http://example.invalid')

        class _FakeResponse:
            content = b'\x00\x01binarydata'
            url = 'http://example.invalid/some/path'

        with patch.object(http._session, 'get', return_value=_FakeResponse()):
            result = http.get_binary('/some/path')
        self.assertEqual(result, b'\x00\x01binarydata')

    def test_passes_auth_and_timeout_to_the_request(self):
        http = Http(baseurl='http://example.invalid')

        class _FakeResponse:
            content = b'x'
            url = 'http://example.invalid/'
            status_code = 200

        with patch.object(http._session, 'get', return_value=_FakeResponse()) as get:
            http.get_binary('/', auth=('user', 'secret'), timeout=2)
        _, kwargs = get.call_args
        self.assertEqual(('user', 'secret'), kwargs['auth'])
        self.assertEqual(2, kwargs['timeout'])

    def test_require_ok_returns_none_for_other_status_codes(self):
        http = Http(baseurl='http://example.invalid')

        class _NotFound:
            content = b'<html>not found</html>'
            url = 'http://example.invalid/missing'
            status_code = 404
            reason = 'Not Found'

        with patch.object(http._session, 'get', return_value=_NotFound()):
            self.assertEqual(b'<html>not found</html>', http.get_binary('/missing'))
            self.assertIsNone(http.get_binary('/missing', require_ok=True))

    def test_require_ok_returns_content_for_status_200(self):
        http = Http(baseurl='http://example.invalid')

        class _Ok:
            content = b'data'
            url = 'http://example.invalid/'
            status_code = 200
            reason = 'OK'

        with patch.object(http._session, 'get', return_value=_Ok()):
            self.assertEqual(b'data', http.get_binary('/', require_ok=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
