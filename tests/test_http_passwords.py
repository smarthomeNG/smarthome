#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for the password handling of modules/http (configured passwords and basic auth checks)."""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.utils import Utils
from modules.http import Http


def make_http():
    """Return an Http instance with only what the password methods use."""
    http = object.__new__(Http)
    http.logger = logging.getLogger('modules.http.test')
    return http


class TestResolvePasswordHash(unittest.TestCase):
    def resolve(self, password, hashed):
        return make_http()._resolve_password_hash('Webinterfaces', 'password', password, 'hashed_password', hashed)

    def test_plaintext_password_is_hashed_salted(self):
        resolved = self.resolve('secret', '')

        self.assertFalse(Utils.is_legacy_password_hash(resolved))
        self.assertTrue(Utils.check_hashed_password('secret', resolved))

    def test_hashed_password_wins(self):
        hashed = Utils.hash_password('other')
        self.assertEqual(hashed, self.resolve('secret', hashed))

    def test_legacy_hash_is_kept_with_warning(self):
        legacy = Utils.create_hash('secret')
        with self.assertLogs('modules.http.test', level=logging.WARNING) as logs:
            self.assertEqual(legacy, self.resolve(None, legacy))
        self.assertIn('unsalted', logs.output[0])

    def test_nothing_configured(self):
        self.assertFalse(make_http()._is_set(self.resolve(None, '')))


class TestValidatePassword(unittest.TestCase):
    def setUp(self):
        self.http = make_http()
        self.http._user_dict = {'admin': {'password_hash': Utils.hash_password('secret')}}

    def test_valid(self):
        self.assertTrue(self.http.validate_password('realm', 'admin', 'secret'))

    def test_wrong_password(self):
        self.assertFalse(self.http.validate_password('realm', 'admin', 'nope'))

    def test_unknown_user(self):
        self.assertFalse(self.http.validate_password('realm', 'root', 'secret'))

    def test_legacy_hash(self):
        self.http._user_dict = {'admin': {'password_hash': Utils.create_hash('secret')}}
        self.assertTrue(self.http.validate_password('realm', 'admin', 'secret'))


if __name__ == '__main__':
    unittest.main()
