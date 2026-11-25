#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""CommandRef wire form and parts."""

import copy
import pickle
import unittest

from lib.model.sdp.binding import CommandRef


class TestCommandRef(unittest.TestCase):
    def test_plain_command_equals_its_name(self):
        ref = CommandRef('zone1.control.power')

        self.assertEqual('zone1.control.power', ref)
        self.assertEqual('zone1.control.power', ref.name)
        self.assertIsNone(ref.token)

    def test_token_command_is_wire_form(self):
        ref = CommandRef('player.control.stop', 'aa:bb')

        self.assertEqual('player.control.stop#aa:bb', ref)
        self.assertEqual('player.control.stop', ref.name)
        self.assertEqual('aa:bb', ref.token)

    def test_parse_splits_wire_form(self):
        ref = CommandRef.parse('player.control.stop#aa:bb')

        self.assertEqual(('player.control.stop', 'aa:bb'), (ref.name, ref.token))

    def test_parse_is_idempotent(self):
        ref = CommandRef('a', 't')

        self.assertIs(ref, CommandRef.parse(ref))

    def test_hashes_like_plain_string(self):
        self.assertEqual({'a#t': 1}['a#t'], {CommandRef('a', 't'): 1}['a#t'])

    def test_usable_in_string_comparisons_of_plugins(self):
        ref = CommandRef('zone1.control.power')

        self.assertIn(ref, ['zone1.control.power', 'other'])
        self.assertEqual('zone1.control.power#x', f'{ref}#x')

    def test_survives_copy_and_pickle(self):
        ref = CommandRef('a', 't')

        for clone in (copy.deepcopy(ref), pickle.loads(pickle.dumps(ref))):
            self.assertEqual(('a#t', 'a', 't'), (clone, clone.name, clone.token))

    def test_with_token_replaces_token(self):
        self.assertEqual('a#u', CommandRef('a', 't').with_token('u'))
        self.assertEqual('a', CommandRef('a', 't').with_token(None))


if __name__ == '__main__':
    unittest.main(verbosity=2)
