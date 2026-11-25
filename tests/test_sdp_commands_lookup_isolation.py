#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that SDPCommands._parse_lookups() does not mutate the cached device
commands.py module in place. locate() caches the module in sys.modules, so
it is shared across every SDPCommands instance for the same device type -
merging a model-specific lookup override into the shared generic table must
not leak into a differently-configured instance created afterward.
"""

import builtins

builtins.SDP_standalone = True

import unittest

from lib.model.sdp.commands import SDPCommands
from lib.model.sdp.command import SDPCommand


class TestLookupIsolationAcrossModels(unittest.TestCase):
    def test_model_specific_override_does_not_leak_into_generic_only_instance(self):
        # first instance: configured for 'modelB', which overrides/extends
        # the generic 'colors' lookup with an extra entry
        modelb_cmds = SDPCommands(SDPCommand, plugin_path='tests.fixture_sdp_lookups_plugin', model='modelB')
        modelb_colors = modelb_cmds.get_lookup('colors')
        self.assertEqual(modelb_colors.get('B'), 'Blue')

        # second instance: no model specified, should only ever see the
        # generic lookup table as defined in the fixture - NOT modelB's
        # 'B': 'Blue' addition, even though modelB was instantiated first
        generic_cmds = SDPCommands(SDPCommand, plugin_path='tests.fixture_sdp_lookups_plugin', model=None)
        generic_colors = generic_cmds.get_lookup('colors')
        self.assertNotIn('B', generic_colors, 'modelB lookup override leaked into the shared generic table')
        self.assertEqual(generic_colors, {'R': 'Red', 'G': 'Green'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
