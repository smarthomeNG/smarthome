#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""SDP contract tests run plugins declaring TRANSPORTS without host or serial port."""

import builtins

builtins.SDP_standalone = False

import unittest  # noqa: E402

from lib.model.sdp.connection import SDPConnection  # noqa: E402
from tests.fixture_sdp_plugin import FixtureSDPRules  # noqa: E402
from tests.plugin_contract.sdp import SdpPluginContractTest  # noqa: E402


class TestTransportRulesPluginContract(SdpPluginContractTest):
    PLUGIN_CLASS = FixtureSDPRules
    SDP_ITEM_ATTR_SETS = [{'fx_command': 'status.power', 'fx_read': True}]

    def test_plugin_runs_on_null_transport(self):
        self.assertIs(SDPConnection, type(self.plugin._connection))

    def test_plugin_is_still_the_plugin_class(self):
        self.assertIsInstance(self.plugin, FixtureSDPRules)


if __name__ == '__main__':
    unittest.main(verbosity=2)
