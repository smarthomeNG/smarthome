#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that _open() on the request-style connection classes sets
_is_connected itself, instead of relying on the caller to interpret its
return value.

SDPConnection.send()'s autoconnect branch calls the raw _open() (not the
public open() wrapper) and then checks self._is_connected directly - it
does not look at _open()'s return value at all. The public open() wrapper
is the only place that translates a truthy return value into
_is_connected = True. SDPConnectionSerial._open() already sets the flag
itself; the request-style connections (used for one-shot HTTP/UDP query
plugins) did not, so send()'s autoconnect spuriously failed with
"autoconnect failed to open connection" for these connection types even
though the open genuinely succeeded.
"""

import builtins

builtins.SDP_standalone = False

import logging
import unittest
from unittest.mock import patch

from lib.model.sdp.connection import SDPConnection, SDPConnectionNetTcpRequest, SDPConnectionNetUdpRequest


def _make_conn(cls):
    conn = object.__new__(cls)
    conn.logger = logging.getLogger('test.conn.request')
    conn._params = {}
    conn._is_connected = False
    return conn


class TestOpenSetsIsConnected(unittest.TestCase):
    def test_base_connection_open_sets_is_connected(self):
        conn = _make_conn(SDPConnection)
        conn._open()
        self.assertTrue(conn._is_connected)

    def test_tcp_request_open_sets_is_connected(self):
        conn = _make_conn(SDPConnectionNetTcpRequest)
        conn._open()
        self.assertTrue(conn._is_connected)

    def test_udp_request_open_sets_is_connected(self):
        conn = _make_conn(SDPConnectionNetUdpRequest)
        # don't actually spawn the real UDP listener thread/socket - only
        # _open()'s own _is_connected bookkeeping is under test here
        with patch('lib.model.sdp.connection.Thread'):
            conn._open()
        self.assertTrue(conn._is_connected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
