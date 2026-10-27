"""
Tests for modules/admin/api_config.py's handling of http passwords saved from the admin UI: plaintext
passwords are stored as salted hashes, never as plaintext.
"""

import unittest

from . import common

common.register_shng_log_levels()

from lib.utils import Utils
from modules.admin.api_config import hash_plain_passwords


class TestHashPlainPasswords(unittest.TestCase):
    def test_plaintext_password_becomes_salted_hash(self):
        data = {'password': 'secret', 'hashed_password': None}

        hash_plain_passwords(data)

        self.assertIsNone(data['password'])
        self.assertTrue(Utils.check_hashed_password('secret', data['hashed_password']))
        self.assertFalse(Utils.is_legacy_password_hash(data['hashed_password']))

    def test_service_password_becomes_salted_hash(self):
        data = {'service_password': 'svc'}

        hash_plain_passwords(data)

        self.assertIsNone(data['service_password'])
        self.assertTrue(Utils.check_hashed_password('svc', data['service_hashed_password']))

    def test_given_hash_is_kept(self):
        hashed = Utils.hash_password('other')
        data = {'password': 'secret', 'hashed_password': hashed}

        hash_plain_passwords(data)

        self.assertEqual(hashed, data['hashed_password'])
        self.assertIsNone(data['password'])

    def test_nothing_to_do(self):
        data = {'hashed_password': 'x', 'port': 8383}

        hash_plain_passwords(data)

        self.assertEqual({'hashed_password': 'x', 'port': 8383}, data)
