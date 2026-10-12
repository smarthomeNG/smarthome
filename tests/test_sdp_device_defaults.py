#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Device defaults declared as SmartDevicePlugin class attributes; connection callbacks."""

import logging
import tempfile
import unittest

from lib.model.sdp.connection import (
    SDPConnection,
    SDPConnectionNetTcpClient,
    SDPConnectionNetTcpRequest,
    SDPConnectionSerialAsync,
)
from lib.model.sdp.protocol import SDPProtocol, SDPProtocolJsonrpc
from tests.sdp_harness import PluginNotLoaded, load_sdp_plugin, transport

ITEMS = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_write: true
        fx_read_initial: true
        fx_read_cycle: 10
"""


class _DefaultsTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def load(self, class_name, record=False, items='', **params):
        return load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', class_name, items, params=params, record=record
        )


class TestTransportRules(_DefaultsTestBase):
    def test_host_selects_network_transport(self):
        rig = self.load('FixtureSDPRules', host='h')
        self.assertIs(SDPConnectionNetTcpClient, type(transport(rig.connection)))

    def test_serialport_selects_serial_transport(self):
        rig = self.load('FixtureSDPRules', serialport='/dev/null')
        self.assertIs(SDPConnectionSerialAsync, type(transport(rig.connection)))

    def test_first_matching_rule_wins_with_warning(self):
        rig = self.load('FixtureSDPRules', host='h', serialport='/dev/null')

        self.assertIs(SDPConnectionNetTcpClient, type(transport(rig.connection)))
        warnings = rig.logs.messages()
        self.assertTrue(any('host' in line and 'serialport' in line for line in warnings), warnings)

    def test_no_matching_rule_disables_plugin(self):
        with self.assertRaises(PluginNotLoaded) as loading:
            self.load('FixtureSDPRules')

        errors = loading.exception.logs.messages(logging.ERROR)
        self.assertTrue(any('host' in line and 'serialport' in line for line in errors), errors)

    def test_rule_without_requirement_is_fallback(self):
        rig = self.load('FixtureSDPNullFallback')
        self.assertIs(SDPConnection, type(transport(rig.connection)))

    def test_legacy_parameter_default_wins_over_rules(self):
        rig = self.load('FixtureSDPLegacyDefaults', host='h')
        self.assertIs(SDPConnectionNetTcpRequest, type(transport(rig.connection)))

    def test_declared_protocol_wraps_transport(self):
        rig = self.load('FixtureSDPProtocol', host='h')
        self.assertIs(SDPProtocolJsonrpc, type(rig.connection))
        self.assertIs(SDPConnectionNetTcpClient, type(transport(rig.connection)))


class TestLineTermination(_DefaultsTestBase):
    def test_line_terminated_sends_terminator_and_reads_up_to_it(self):
        rig = self.load('FixtureSDPNullFallback', record=True, items=ITEMS)
        rig.plugin.run()
        rig.connection.sent.clear()

        rig.item('dev.power')(True, 'test')

        self.assertEqual([('PW\r', b'\r')], [(d['payload'], d['limit_response']) for d in rig.connection.sent])
        rig.plugin.stop()


class TestConnectionCallbacks(_DefaultsTestBase):
    def test_connect_schedules_initial_and_cyclic_reads(self):
        rig = self.load('FixtureSDP', record=True, items=ITEMS)
        rig.plugin.run()

        self.assertIsNotNone(rig.job('read_initial_values'))
        self.assertIsNotNone(rig.job(rig.plugin.get_fullname() + '_cyclic'))
        rig.plugin.stop()

    def test_setting_use_callbacks_is_deprecated(self):
        rig = self.load('FixtureSDPLegacyCallbacks')

        warnings = rig.logs.messages()
        self.assertTrue(any('_use_callbacks' in line for line in warnings), warnings)


if __name__ == '__main__':
    unittest.main(verbosity=2)
