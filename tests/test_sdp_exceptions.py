#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the SDP exception hierarchy and send_command() error handling.

Covers:
  - SDPError / SDPConnectionError / SDPProtocolError class relationships
  - SDPConnection.send() raises correctly when not connected or init fails
  - SmartDevicePlugin.send_command() returns False on all SDPError subclasses
    and on RuntimeError (backward compat), returns True on success
"""

import builtins
builtins.SDP_standalone = False

import logging
import unittest
from unittest.mock import MagicMock

from lib.model.sdp.globals import (
    SDPError, SDPConnectionError, SDPProtocolError,
    CMD_ATTR_REPLY_PATTERN, CMD_ATTR_SEND_RETRIES,
    PLUGIN_ATTR_CONN_AUTO_CONN,
)
from lib.model.sdp.connection import SDPConnection
from lib.model.smartdeviceplugin import SmartDevicePlugin


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sdp():
    """
    Return a minimal SmartDevicePlugin instance created without __init__,
    with just enough attributes to exercise send_command().
    """
    sdp = object.__new__(SmartDevicePlugin)
    sdp.alive = True
    sdp.suspended = False
    sdp.custom_commands = None
    sdp.logger = logging.getLogger('test.sdp')
    sdp.shtime = MagicMock()
    sdp.get_fullname = lambda: 'testplugin'

    conn = MagicMock()
    conn.connected.return_value = True
    sdp._connection = conn

    sdp._parameters = {PLUGIN_ATTR_CONN_AUTO_CONN: False}

    cmds = MagicMock()
    cmds.custom_is_enabled_for.return_value = False
    cmds.get_send_data.return_value = {'payload': b'\x41\x05\x00', 'data': {}}
    cmds.get_commandlist.return_value = {
        CMD_ATTR_REPLY_PATTERN: None,
        CMD_ATTR_SEND_RETRIES: None,
    }
    cmds.get_lookup.return_value = None
    cmds._get_cmd_lookup.return_value = None
    sdp._commands = cmds

    return sdp, conn


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class TestSDPExceptionHierarchy(unittest.TestCase):

    def test_sdp_error_is_exception(self):
        self.assertTrue(issubclass(SDPError, Exception))

    def test_sdp_connection_error_is_sdp_error(self):
        self.assertTrue(issubclass(SDPConnectionError, SDPError))

    def test_sdp_connection_error_is_oserror(self):
        """SDPConnectionError inherits OSError for backward compat."""
        self.assertTrue(issubclass(SDPConnectionError, OSError))

    def test_sdp_protocol_error_is_sdp_error(self):
        self.assertTrue(issubclass(SDPProtocolError, SDPError))

    def test_sdp_protocol_error_is_not_oserror(self):
        self.assertFalse(issubclass(SDPProtocolError, OSError))

    def test_sdp_connection_error_caught_as_sdp_error(self):
        with self.assertRaises(SDPError):
            raise SDPConnectionError('wire broken')

    def test_sdp_connection_error_caught_as_oserror(self):
        """Existing except-OSError clauses still work."""
        with self.assertRaises(OSError):
            raise SDPConnectionError('wire broken')

    def test_sdp_protocol_error_caught_as_sdp_error(self):
        with self.assertRaises(SDPError):
            raise SDPProtocolError('bad checksum')

    def test_exception_messages_preserved(self):
        msg = 'serial port vanished'
        e = SDPConnectionError(msg)
        self.assertIn(msg, str(e))


# ---------------------------------------------------------------------------
# SDPConnection.send() — guard rails
# ---------------------------------------------------------------------------

class TestSDPConnectionSendGuards(unittest.TestCase):

    def _make_conn(self):
        """Minimal SDPConnection with _send and _send_init_on_send overridable."""
        conn = object.__new__(SDPConnection)
        conn.logger = logging.getLogger('test.conn')
        conn._is_connected = True
        conn._params = {PLUGIN_ATTR_CONN_AUTO_CONN: False}
        conn._send_lock = __import__('threading').Lock()
        conn.use_send_lock = False
        conn.dummy = None
        return conn

    def test_send_raises_sdp_connection_error_when_not_connected_no_autoconn(self):
        conn = self._make_conn()
        conn._is_connected = False
        conn._params[PLUGIN_ATTR_CONN_AUTO_CONN] = False
        with self.assertRaises(SDPConnectionError):
            conn.send({'payload': b'\x01'})

    def test_send_raises_sdp_connection_error_when_autoconn_fails(self):
        conn = self._make_conn()
        conn._is_connected = False
        conn._params[PLUGIN_ATTR_CONN_AUTO_CONN] = True
        conn._open = lambda: None   # _open() succeeds but doesn't set _is_connected
        with self.assertRaises(SDPConnectionError):
            conn.send({'payload': b'\x01'})

    def test_send_raises_sdp_protocol_error_when_init_returns_false(self):
        """_send_init_on_send() returning False must raise SDPProtocolError."""
        conn = self._make_conn()
        conn._send_init_on_send = lambda: False
        conn._send = lambda d, **kw: None
        with self.assertRaises(SDPProtocolError):
            conn.send({'payload': b'\x01'})

    def test_send_succeeds_when_init_returns_true(self):
        conn = self._make_conn()
        conn._send_init_on_send = lambda: True
        conn._send = lambda d, **kw: b'\xaa\xbb'
        result = conn.send({'payload': b'\x01'})
        self.assertEqual(result, b'\xaa\xbb')


# ---------------------------------------------------------------------------
# SmartDevicePlugin.send_command() — exception handling
# ---------------------------------------------------------------------------

class TestSendCommandExceptionHandling(unittest.TestCase):

    def setUp(self):
        self.sdp, self.conn = _make_sdp()

    def test_returns_false_on_sdp_connection_error(self):
        self.conn.send.side_effect = SDPConnectionError('serial gone')
        self.assertFalse(self.sdp.send_command('Allgemein.Temperatur.Aussen', 42))

    def test_returns_false_on_sdp_protocol_error(self):
        self.conn.send.side_effect = SDPProtocolError('bad ACK')
        self.assertFalse(self.sdp.send_command('Allgemein.Temperatur.Aussen', 42))

    def test_returns_false_on_runtime_error(self):
        """RuntimeError must still be caught for backward compatibility."""
        self.conn.send.side_effect = RuntimeError('legacy error')
        self.assertFalse(self.sdp.send_command('Allgemein.Temperatur.Aussen', 42))

    def test_returns_true_on_successful_write(self):
        """Write commands return None from _send; send_command must report True."""
        self.conn.send.return_value = None
        self.conn.send.side_effect = None
        self.assertTrue(self.sdp.send_command('Allgemein.Temperatur.Aussen', 42))

    def test_returns_false_when_not_alive(self):
        self.sdp.alive = False
        self.conn.send.return_value = None
        self.assertFalse(self.sdp.send_command('cmd', 1))

    def test_returns_false_when_suspended(self):
        self.sdp.suspended = True
        self.conn.send.return_value = None
        self.assertFalse(self.sdp.send_command('cmd', 1))

    def test_returns_false_when_payload_empty(self):
        self.sdp._commands.get_send_data.return_value = {'payload': None, 'data': {}}
        self.assertFalse(self.sdp.send_command('cmd', 1))


if __name__ == '__main__':
    unittest.main(verbosity=2)
