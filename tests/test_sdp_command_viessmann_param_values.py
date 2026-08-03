#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that SDPCommandViessmann.__init__() does not crash when 'params' and
'param_values' have mismatched lengths in a device's commands.py. The
sibling method _build_dict() was already fixed to pair them by zip(names,
values) instead of list.index() lookups; __init__ still used the old,
unguarded index-based pairing.
"""

import builtins

builtins.SDP_standalone = False

import unittest

import lib.model.sdp.datatypes as DT
from lib.model.sdp.command import SDPCommandViessmann


class TestParamValuesLengthMismatch(unittest.TestCase):
    def test_init_does_not_raise_on_length_mismatch(self):
        # 'params' names 4 attributes, but 'param_values' only supplies 2 -
        # a plausible authoring mistake in a device's commands.py
        cmd_conf = {'params': ['value', 'mult', 'signed', 'len'], 'param_values': ['VAL', 0]}
        # must not raise IndexError
        cmd = SDPCommandViessmann('temp_cmd', DT.DT_raw, cmd=cmd_conf, plugin={})
        # len/mult/signed default to 1/0/False when a value can't be paired
        self.assertEqual(cmd.mult, 0)

    def test_init_still_applies_values_when_lengths_match(self):
        cmd_conf = {'params': ['value', 'mult', 'signed', 'len'], 'param_values': ['VAL', 10, True, 2]}
        cmd = SDPCommandViessmann('temp_cmd', DT.DT_raw, cmd=cmd_conf, plugin={})
        self.assertEqual(cmd.mult, 10)
        self.assertEqual(cmd.signed, True)
        self.assertEqual(cmd.len, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
