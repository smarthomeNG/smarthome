"""
Contract tests for the sample_smartdevice_standalone_plugin example.

This file demonstrates how to wire up the plugin_contract test framework for a
SmartDevicePlugin variant that also supports standalone mode (running outside
of SmartHomeNG for device discovery/testing).  When you copy this sample to
plugins/myplugin/, adapt as follows:

    from plugins.myplugin import MyPlugin          # rename class

    class TestMyPlugin(BasePluginContractTest,
                       YamlPluginContractTest,
                       SdpPluginContractTest):
        PLUGIN_CLASS = MyPlugin
        PLUGIN_INIT_PARAMS = {}    # runs on the null transport automatically
        SDP_ITEM_ATTR_SETS = [
            {'ex_command': 'Device.Power', 'ex_read': True},
            {'ex_command': 'Device.Power', 'ex_write': True},
        ]
        ITEM_ATTR_SETS = [
            {'ex_command': 'Device.Power', 'ex_read': True},
        ]

Standalone mode (``if __name__ == '__main__'``) is not exercised by these tests
— they test the plugin as a normal SmartHomeNG plugin, importing it via the
``else`` branch of the standalone guard.

Note on connections: SdpPluginContractTest runs plugins declaring TRANSPORTS
on the null transport (and injects conn_type=CONN_NULL for others), so no real
network or serial connection is attempted.
"""

import os
import sys

# ensure shng root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.plugin_contract.base import BasePluginContractTest
from tests.plugin_contract.with_yaml import YamlPluginContractTest
from tests.plugin_contract.sdp import SdpPluginContractTest
from dev.sample_smartdevice_standalone_plugin import SdpExample


class TestSdpExampleStandalone(BasePluginContractTest, YamlPluginContractTest, SdpPluginContractTest):
    """
    Tier 1 + Tier 2 + Tier 4 contract tests for the sample_smartdevice_standalone_plugin.

    Functionally identical to sample_smartdevice_plugin — the standalone variant
    adds a run_standalone() method and the __main__ guard but is otherwise the
    same plugin class.
    """

    PLUGIN_CLASS = SdpExample
    PLUGIN_INIT_PARAMS = {}  # SdpPluginContractTest runs the plugin on the null transport

    def test_run_standalone_exists(self):
        """run_standalone() must be defined for standalone-capable SDP plugins."""
        self.assertTrue(
            callable(getattr(self.plugin, 'run_standalone', None)),
            'run_standalone() is not defined — standalone-mode plugins must implement it',
        )

    # Command names in the model-specific format (Style 3) are referenced without
    # the 'ALL.' prefix — SDP flattens 'ALL.cmd1' to 'cmd1' when loading commands.
    SDP_ITEM_ATTR_SETS = [{'ex_command': 'cmd1', 'ex_read': True}, {'ex_command': 'cmd1', 'ex_write': True}]
    # Same sets used by YamlPluginContractTest for the item-attribute wiring check
    ITEM_ATTR_SETS = [{'ex_command': 'cmd1', 'ex_read': True}]
