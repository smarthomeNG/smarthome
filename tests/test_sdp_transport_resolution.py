#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Connection and protocol class resolution from plugin configuration."""

import tempfile
import unittest

from lib.model.sdp.connection import (
    SDPConnection,
    SDPConnectionNetTcpClient,
    SDPConnectionNetTcpRequest,
    SDPConnectionNetUdpRequest,
    SDPConnectionSerialAsync,
)
from lib.model.sdp.protocol import SDPProtocol, SDPProtocolJsonrpc
from tests.sdp_harness import load_sdp_plugin, transport


class TestTransportResolution(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def connection_for(self, **params):
        rig = load_sdp_plugin(self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', '', params=params, record=False)
        return rig.connection

    def assert_not_loaded(self, **params):
        with self.assertRaises(RuntimeError):
            self.connection_for(**params)

    def test_udp_server_type_yields_udp_connection(self):
        self.assertIs(
            SDPConnectionNetUdpRequest, type(transport(self.connection_for(conn_type='net_udp_server', port=40000)))
        )

    def test_tcp_client_type_yields_tcp_client(self):
        self.assertIs(
            SDPConnectionNetTcpClient, type(transport(self.connection_for(conn_type='net_tcp_client', host='h')))
        )

    def test_host_without_type_yields_tcp_request(self):
        self.assertIs(SDPConnectionNetTcpRequest, type(transport(self.connection_for(host='h'))))

    def test_nothing_configured_yields_null_connection(self):
        self.assertIs(SDPConnection, type(transport(self.connection_for())))

    def test_class_name_yields_that_class(self):
        conn = self.connection_for(conn_type='SDPConnectionSerialAsync', serialport='/dev/null')
        self.assertIs(SDPConnectionSerialAsync, type(transport(conn)))

    def test_jsonrpc_is_not_a_connection_type(self):
        self.assert_not_loaded(conn_type='net_tcp_jsonrpc', host='h')

    def test_unknown_connection_type_disables_plugin(self):
        self.assert_not_loaded(conn_type='no_such_type')

    def test_jsonrpc_protocol_type_yields_jsonrpc_protocol(self):
        conn = self.connection_for(conn_type='net_tcp_client', host='h', protocol='jsonrpc')
        self.assertIs(SDPProtocolJsonrpc, type(conn))

    def test_plugin_local_protocol_name_disables_plugin(self):
        self.assert_not_loaded(protocol='viessmann', serialport='/dev/null')

    def test_unknown_protocol_disables_plugin(self):
        self.assert_not_loaded(protocol='no_such_protocol')


if __name__ == '__main__':
    unittest.main(verbosity=2)
