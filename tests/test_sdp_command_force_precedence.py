#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""cmd_settings force_min/force_max take precedence over valid_min/valid_max."""

import builtins

builtins.SDP_standalone = False

import unittest

import lib.model.sdp.datatypes as DT
from lib.model.sdp.command import SDPCommand


def command(**cmd_settings) -> SDPCommand:
    return SDPCommand('x', DT.DT_int, cmd={'cmd_settings': cmd_settings}, plugin={}, template_vars={})


class TestForcePrecedence(unittest.TestCase):
    def test_force_min_clamps_although_valid_min_is_set(self):
        self.assertEqual(0, command(valid_min=0, force_min=0)._check_value(-5))

    def test_force_max_clamps_although_valid_max_is_set(self):
        self.assertEqual(100, command(valid_max=100, force_max=100)._check_value(150))

    def test_force_min_above_valid_min_clamps_to_force_value(self):
        self.assertEqual(5, command(valid_min=0, force_min=5)._check_value(-1))

    def test_valid_min_alone_still_raises(self):
        with self.assertRaises(ValueError):
            command(valid_min=0)._check_value(-5)

    def test_value_within_bounds_is_unchanged(self):
        self.assertEqual(7, command(valid_min=0, valid_max=10, force_min=0, force_max=10)._check_value(7))


if __name__ == '__main__':
    unittest.main(verbosity=2)
