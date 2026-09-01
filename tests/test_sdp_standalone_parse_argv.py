#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression tests for Standalone._parse_argv() (lib.model.smartdeviceplugin).

Mode flags ('-s'/'-a'/'-l') must be matched exactly, like the '-v' check
right above them (which uses '=='), not via an `arg_str[:2].lower() == '-s'`
prefix match - a prefix match would silently swallow any arg starting with
'-s'/'-a'/'-l' as a mode flag instead of reaching the name=value/dict
parser, e.g. a plugin parameter typed with a stray leading dash
(`-address=...`, a natural typo of the documented `address=...` form)
would enable ACL mode instead of setting the address parameter, with no
error.

_parse_argv() is extracted out of __init__ (which also needs a real cwd
with bin/smarthome.py and reads sys.argv) so this can be tested directly.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartdeviceplugin import Standalone


class TestParseArgvModeFlags(unittest.TestCase):
    def test_dash_v_enables_debug_flag(self):
        flags, raw_args = Standalone._parse_argv(['-v'])
        self.assertTrue(flags['v'])

    def test_dash_s_enables_struct_mode(self):
        flags, raw_args = Standalone._parse_argv(['-s'])
        self.assertTrue(flags['s'])

    def test_dash_a_enables_acl(self):
        flags, raw_args = Standalone._parse_argv(['-a'])
        self.assertTrue(flags['a'])

    def test_dash_l_enables_lowercase(self):
        flags, raw_args = Standalone._parse_argv(['-l'])
        self.assertTrue(flags['l'])

    def test_flags_are_case_insensitive_exact_match(self):
        flags, raw_args = Standalone._parse_argv(['-S', '-A', '-L', '-V'])
        self.assertTrue(all(flags.values()))


class TestParseArgvDoesNotSwallowParametersStartingWithFlagLetters(unittest.TestCase):
    """The actual bug: a parameter arg whose value happens to start with
    '-s'/'-a'/'-l' must not be misread as the struct/acl/lowercase flag."""

    def test_dash_address_is_not_read_as_acl_flag(self):
        flags, raw_args = Standalone._parse_argv(['-address=192.168.1.1'])
        self.assertFalse(flags['a'])

    def test_dash_address_value_still_reaches_raw_args(self):
        flags, raw_args = Standalone._parse_argv(['-address=192.168.1.1'])
        self.assertTrue(raw_args, 'arg was silently dropped instead of being parsed as name=value')

    def test_dash_serial_is_not_read_as_struct_flag(self):
        flags, raw_args = Standalone._parse_argv(['-serial=/dev/ttyUSB0'])
        self.assertFalse(flags['s'])

    def test_dash_list_is_not_read_as_lowercase_flag(self):
        flags, raw_args = Standalone._parse_argv(['-list=1'])
        self.assertFalse(flags['l'])


class TestParseArgvNameValueAndDictForms(unittest.TestCase):
    def test_bare_name_value_pair(self):
        flags, raw_args = Standalone._parse_argv(['host=www.smarthomeng.de', 'port=80'])
        self.assertEqual(raw_args, {'host': 'www.smarthomeng.de', 'port': '80'})

    def test_double_dash_alias_for_name_value(self):
        flags, raw_args = Standalone._parse_argv(['--host=www.smarthomeng.de'])
        self.assertEqual(raw_args, {'host': 'www.smarthomeng.de'})

    def test_dict_literal_form(self):
        flags, raw_args = Standalone._parse_argv(["{'host': 'www.smarthomeng.de', 'port': 80}"])
        self.assertEqual(raw_args, {'host': 'www.smarthomeng.de', 'port': 80})

    def test_later_argument_overwrites_earlier_same_name(self):
        flags, raw_args = Standalone._parse_argv(['host=1.1.1.1', 'host=2.2.2.2'])
        self.assertEqual(raw_args['host'], '2.2.2.2')


if __name__ == '__main__':
    unittest.main(verbosity=2)
