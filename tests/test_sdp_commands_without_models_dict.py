#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Loading of commands.py for a configured model when commands.py defines no ``models`` dict:
with an 'ALL' key, 'ALL' plus the model's commands are loaded; with a flat (not model-specific)
commands dict, all commands are loaded.
"""

import builtins

builtins.SDP_standalone = False

import unittest

from lib.model.sdp.command import SDPCommand
from lib.model.sdp.commands import SDPCommands

FLAT = 'tests.fixture_sdp_flat_commands_plugin'
WITH_ALL = 'tests.fixture_sdp_all_without_models_plugin'


class TestCommandsWithoutModelsDict(unittest.TestCase):
    def test_flat_commands_load_completely_with_model_configured(self):
        cmds = SDPCommands(SDPCommand, plugin_path=FLAT, model='whatever')

        self.assertEqual({'cmd_a', 'cmd_b'}, set(cmds._commands))

    def test_flat_commands_load_completely_without_model(self):
        cmds = SDPCommands(SDPCommand, plugin_path=FLAT)

        self.assertEqual({'cmd_a', 'cmd_b'}, set(cmds._commands))

    def test_all_key_loads_all_and_model_commands(self):
        cmds = SDPCommands(SDPCommand, plugin_path=WITH_ALL, model='modelX')

        self.assertEqual({'cmd_all', 'cmd_x'}, set(cmds._commands))

    def test_all_key_without_model_loads_only_all(self):
        cmds = SDPCommands(SDPCommand, plugin_path=WITH_ALL)

        self.assertEqual({'cmd_all'}, set(cmds._commands))


if __name__ == '__main__':
    unittest.main(verbosity=2)
