#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that SDPConnectionSerial._send() marks the connection disconnected
when a real write failure occurs.

_send_bytes() always raises SDPConnectionError on a genuine write failure
(timeout/SerialException) rather than returning a falsy value, so a bare
`if not self._send_bytes(data): self._is_connected = False` guard in _send()
never actually runs for real failures - the exception propagates straight
past it, leaving a broken connection marked as still connected.
"""

import builtins

builtins.SDP_standalone = False

import logging
import threading
import unittest
from unittest.mock import MagicMock

from lib.model.sdp.globals import (
    SDPConnectionError,
    PLUGIN_ATTR_SERIAL_PORT,
    PLUGIN_ATTR_CONN_AUTO_CONN,
    PLUGIN_ATTR_CONN_BINARY,
)
from lib.model.sdp.connection import SDPConnectionSerial


def _make_serial_conn():
    class _SerialException(OSError):
        pass

    class _SerialTimeoutException(_SerialException):
        pass

    mock_serial_module = MagicMock()
    mock_serial_module.SerialException = _SerialException
    mock_serial_module.SerialTimeoutException = _SerialTimeoutException

    mock_port = MagicMock()

    conn = object.__new__(SDPConnectionSerial)
    conn.logger = logging.getLogger('test.serial.send')
    conn._is_connected = True
    conn._listener_active = False
    conn.serial = mock_serial_module
    conn._connection = mock_port
    conn._lock = threading.Lock()
    conn._params = {
        PLUGIN_ATTR_SERIAL_PORT: '/dev/mock_tty',
        PLUGIN_ATTR_CONN_AUTO_CONN: False,
        PLUGIN_ATTR_CONN_BINARY: True,
    }
    return conn, mock_port, mock_serial_module


class TestSendMarksDisconnectOnWriteFailure(unittest.TestCase):
    def test_is_connected_false_after_write_failure(self):
        conn, port, serial_mod = _make_serial_conn()
        port.write.side_effect = serial_mod.SerialException('cable pulled')

        with self.assertRaises(SDPConnectionError):
            conn._send({'payload': b'\x01'})

        self.assertFalse(conn._is_connected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
