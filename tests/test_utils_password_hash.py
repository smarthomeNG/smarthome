#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for the salted password hashes of lib.utils (hash_password, check_hashed_password, is_hash)."""

import unittest
from unittest.mock import patch

from lib.utils import Utils

LEGACY_HASH_42 = Utils.create_hash('42')


class TestHashPassword(unittest.TestCase):
    def test_format(self):
        algorithm, iterations, salt, digest = Utils.hash_password('secret').split('$')

        self.assertEqual('pbkdf2_sha256', algorithm)
        self.assertGreaterEqual(int(iterations), 600_000)
        self.assertTrue(salt)
        self.assertTrue(digest)

    def test_salted(self):
        self.assertNotEqual(Utils.hash_password('secret'), Utils.hash_password('secret'))

    def test_empty_password_is_refused(self):
        with self.assertRaises(ValueError):
            Utils.hash_password('')


class TestCheckHashedPassword(unittest.TestCase):
    def test_matching_password(self):
        self.assertTrue(Utils.check_hashed_password('secret', Utils.hash_password('secret')))

    def test_wrong_password(self):
        self.assertFalse(Utils.check_hashed_password('Secret', Utils.hash_password('secret')))

    def test_empty_password_is_rejected(self):
        self.assertFalse(Utils.check_hashed_password('', Utils.hash_password('secret')))
        self.assertFalse(Utils.check_hashed_password(None, Utils.hash_password('secret')))

    def test_legacy_sha512_hash_still_matches(self):
        self.assertTrue(Utils.check_hashed_password('42', LEGACY_HASH_42))
        self.assertTrue(Utils.check_hashed_password('42', LEGACY_HASH_42.upper()))
        self.assertFalse(Utils.check_hashed_password('43', LEGACY_HASH_42))

    def test_unknown_or_missing_hash_is_rejected(self):
        self.assertFalse(Utils.check_hashed_password('secret', ''))
        self.assertFalse(Utils.check_hashed_password('secret', None))
        self.assertFalse(Utils.check_hashed_password('secret', 'md5$1$a$b'))
        self.assertFalse(Utils.check_hashed_password('secret', 'pbkdf2_sha256$x$a$b'))

    def test_repeated_check_does_not_rederive(self):
        hashed = Utils.hash_password('secret')
        Utils.check_hashed_password('secret', hashed)
        with patch('lib.utils.hashlib.pbkdf2_hmac', side_effect=AssertionError('derived again')):
            self.assertTrue(Utils.check_hashed_password('secret', hashed))


class TestIsHash(unittest.TestCase):
    def test_salted_hash(self):
        self.assertTrue(Utils.is_hash(Utils.hash_password('secret')))

    def test_legacy_hash(self):
        self.assertTrue(Utils.is_hash(LEGACY_HASH_42))

    def test_legacy_hash_is_flagged(self):
        self.assertTrue(Utils.is_legacy_password_hash(LEGACY_HASH_42))
        self.assertFalse(Utils.is_legacy_password_hash(Utils.hash_password('secret')))
        self.assertFalse(Utils.is_legacy_password_hash(''))


if __name__ == '__main__':
    unittest.main()
