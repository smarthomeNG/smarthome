#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression tests for lib.env.location_name()/location_address() crashing on
a reverse-geocode API response with no 'address' key (rate-limited/no-match
responses from the external Nominatim API).

location_name() explicitly detected this case ("No 'address' in json
response") and set result = '' -- but the suburb lookup right after that
if/else block was not actually inside the else branch, so it unconditionally
indexed json_obj['address'] again regardless, raising KeyError exactly on
the case the code above it just handled.

location_address() had no such check at all: `return json_obj['address']`
raised KeyError unconditionally whenever 'address' was absent.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.env


def _fake_response(json_body, status_code=200):
    resp = MagicMock()
    resp.ok = status_code < 400
    resp.status_code = status_code
    resp.json.return_value = json_body
    return resp


class TestLocationName(unittest.TestCase):
    def setUp(self):
        # module-level cache in lib.env -- reset so each test starts fresh
        lib.env.LOCATION_NAME = ''
        lib.env.LAT_LON = ''

    def test_no_address_key_does_not_raise(self):
        with patch('requests.get', return_value=_fake_response({'display_name': 'somewhere'})):
            result = lib.env.location_name(1.0, 2.0)
        self.assertEqual(result, '')

    def test_address_with_city_and_suburb(self):
        body = {'address': {'city': 'Springfield', 'suburb': 'Downtown'}}
        with patch('requests.get', return_value=_fake_response(body)):
            result = lib.env.location_name(1.0, 2.0)
        self.assertEqual(result, 'Springfield, Downtown')

    def test_address_with_suburb_only(self):
        body = {'address': {'suburb': 'Downtown'}}
        with patch('requests.get', return_value=_fake_response(body)):
            result = lib.env.location_name(3.0, 4.0)
        self.assertEqual(result, 'Downtown')


class TestLocationAddress(unittest.TestCase):
    def test_no_address_key_does_not_raise(self):
        with patch('requests.get', return_value=_fake_response({'display_name': 'somewhere'})):
            result = lib.env.location_address(1.0, 2.0)
        self.assertEqual(result, {})

    def test_returns_address_dict_on_success(self):
        body = {'address': {'city': 'Springfield'}}
        with patch('requests.get', return_value=_fake_response(body)):
            result = lib.env.location_address(1.0, 2.0)
        self.assertEqual(result, {'city': 'Springfield'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
