#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for Utils.generate_token() of lib.utils."""

import base64
import unittest

from lib.utils import Utils


def _decoded_length(token: str) -> int:
    return len(base64.urlsafe_b64decode(token + '=' * (-len(token) % 4)))


class TestGenerateToken(unittest.TestCase):
    def test_default_is_256_bit(self):
        self.assertEqual(32, _decoded_length(Utils.generate_token()))

    def test_nbytes(self):
        self.assertEqual(48, _decoded_length(Utils.generate_token(48)))

    def test_urlsafe_alphabet(self):
        token = Utils.generate_token()
        self.assertRegex(token, r'^[A-Za-z0-9_-]+$')

    def test_random(self):
        self.assertNotEqual(Utils.generate_token(), Utils.generate_token())

    def test_weak_length_is_refused(self):
        for nbytes in (0, 15, -1):
            with self.subTest(nbytes=nbytes), self.assertRaises(ValueError):
                Utils.generate_token(nbytes)


if __name__ == '__main__':
    unittest.main()
