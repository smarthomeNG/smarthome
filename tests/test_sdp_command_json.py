#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""SDPCommandJSON send data from command params."""

import builtins

builtins.SDP_standalone = False

import unittest  # noqa: E402

import lib.model.sdp.datatypes as DT  # noqa: E402
from lib.model.sdp.command import SDPCommandJSON  # noqa: E402


def _command(**cmd):
    return SDPCommandJSON('test.cmd', DT.DT_raw, cmd={'opcode': 'Player.GetActivePlayers', **cmd}, template_vars={})


class TestSDPCommandJSONSendData(unittest.TestCase):
    def test_none_params_send_without_params(self):
        self.assertEqual({'payload': 'Player.GetActivePlayers', 'data': {}}, _command(params=None).get_send_data(None))

    def test_missing_params_send_without_params(self):
        self.assertEqual({'payload': 'Player.GetActivePlayers', 'data': {}}, _command().get_send_data(None))

    def test_dict_params_get_value(self):
        data = _command(params={'mute': '{VALUE}'}).get_send_data(True)

        self.assertEqual({'mute': True}, data['data'])

    def test_invalid_params_raise(self):
        with self.assertRaises(ValueError):
            _command(params='mute').get_send_data(None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
