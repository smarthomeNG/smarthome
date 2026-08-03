#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that SDPCommands.set_valid_list()/update_reply_patterns() do not crash
for a command that has no reply_pattern configured. reply_pattern is
optional in a device's commands.py; the sibling method update_lookup_table()
already guards this same access with .get(..., []).
"""

import builtins

builtins.SDP_standalone = False

import unittest

from lib.model.sdp.commands import SDPCommands
from lib.model.sdp.command import SDPCommand


class TestSetValidListWithoutReplyPattern(unittest.TestCase):
    def test_set_valid_list_does_not_raise_for_command_without_reply_pattern(self):
        cmds = SDPCommands(SDPCommand, plugin_path='tests.fixture_sdp_no_reply_pattern_plugin')

        # must not raise KeyError('reply_pattern')
        cmds.set_valid_list('no_pattern_cmd', ['a', 'b'])

        # and the valid_list itself must actually have been applied
        vl, ci, re = cmds.get_valid_list('no_pattern_cmd')
        self.assertEqual(vl, ['a', 'b'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
