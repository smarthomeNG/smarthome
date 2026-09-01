#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SDPCommandViessmann's handling of the 'params' command attribute.

Viessmann device commands.py files (e.g. plugins/viessmann/commands.py)
define 'params' as a single dict of {name: value} pairs, e.g.
{'value': 'VAL', 'len': 2} - there is no separate 'param_values' list in
any real command definition. get_send_data()/_build_dict() must turn that
dict into a populated data-dict.
"""

import builtins

builtins.SDP_standalone = False

import unittest

import lib.model.sdp.datatypes as DT
from lib.model.sdp.command import SDPCommandViessmann


class TestParamsDictFormat(unittest.TestCase):
    def test_init_applies_len_mult_signed_from_params_dict(self):
        cmd_conf = {'params': {'value': 'VAL', 'mult': 10, 'signed': True, 'len': 2}}
        cmd = SDPCommandViessmann('temp_cmd', DT.DT_raw, cmd=cmd_conf, plugin={})
        self.assertEqual(cmd.len, 2)
        self.assertEqual(cmd.mult, 10)
        self.assertEqual(cmd.signed, True)

    def test_init_defaults_when_attr_missing_from_params_dict(self):
        cmd_conf = {'params': {'value': 'VAL', 'len': 2}}
        cmd = SDPCommandViessmann('temp_cmd', DT.DT_raw, cmd=cmd_conf, plugin={})
        self.assertEqual(cmd.len, 2)
        self.assertEqual(cmd.mult, 0)
        self.assertEqual(cmd.signed, False)

    def test_build_dict_replaces_val_and_keeps_other_params(self):
        cmd_conf = {'params': {'value': 'VAL', 'len': 2}}
        cmd = SDPCommandViessmann('temp_cmd', DT.DT_raw, cmd=cmd_conf, plugin={})
        result = cmd._build_dict(b'\x01\x02')
        self.assertEqual(result, {'value': b'\x01\x02', 'len': 2})

    def test_get_send_data_produces_non_empty_data_for_read_command(self):
        # mirrors the real 'Anlagentyp' command (viessmann/commands.py)
        cmd_conf = {'read': True, 'write': False, 'opcode': '00f8', 'params': {'value': 'VAL', 'len': 2}}
        cmd = SDPCommandViessmann('Anlagentyp', DT.DT_raw, cmd=cmd_conf, plugin={})
        data_dict = cmd.get_send_data(None)
        self.assertEqual(data_dict['payload'], '00f8')
        self.assertIn('len', data_dict['data'])
        self.assertEqual(data_dict['data']['len'], 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
