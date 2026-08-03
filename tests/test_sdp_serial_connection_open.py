#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SDPConnectionSerial._open() retry behavior.

Covers: a failed connection attempt must be retried (paced by
PLUGIN_ATTR_CONN_CYCLE) up to PLUGIN_ATTR_CONN_RETRIES times before giving up,
instead of returning False on the first failure.
"""

import builtins

builtins.SDP_standalone = False

import logging
import threading
import unittest
from unittest.mock import MagicMock, patch

from lib.model.sdp.globals import (
    PLUGIN_ATTR_SERIAL_PORT,
    PLUGIN_ATTR_CONN_RETRIES,
    PLUGIN_ATTR_CONN_CYCLE,
    PLUGIN_ATTR_CB_ON_CONNECT,
)
from lib.model.sdp.connection import SDPConnectionSerial


def _make_serial_conn(retries=3, cycle=1):
    """
    Create SDPConnectionSerial via object.__new__ and set only the attributes
    exercised by _open(), using a MagicMock serial port.
    """

    class _SerialException(OSError):
        pass

    class _SerialTimeoutException(_SerialException):
        pass

    mock_serial_module = MagicMock()
    mock_serial_module.SerialException = _SerialException
    mock_serial_module.SerialTimeoutException = _SerialTimeoutException

    mock_port = MagicMock()

    conn = object.__new__(SDPConnectionSerial)
    conn.logger = logging.getLogger('test.serial.open')
    conn._is_connected = False
    conn._connection_attempts = 0
    conn._lock = threading.Lock()
    conn.serial = mock_serial_module
    conn._connection = mock_port
    conn._setup_listener = MagicMock()
    conn._params = {
        PLUGIN_ATTR_SERIAL_PORT: '/dev/mock_tty',
        PLUGIN_ATTR_CONN_RETRIES: retries,
        PLUGIN_ATTR_CONN_CYCLE: cycle,
        PLUGIN_ATTR_CB_ON_CONNECT: None,
    }

    return conn, mock_port, mock_serial_module


class TestOpenRetry(unittest.TestCase):
    def test_retries_after_failed_attempt_and_succeeds(self):
        """A failure on the first attempt must not give up - it should retry
        (paced by connect_cycle) and succeed once the underlying open() stops
        raising, instead of returning False immediately."""
        conn, port, serial_mod = _make_serial_conn(retries=3, cycle=0.01)

        # first call raises, second call succeeds
        port.open.side_effect = [serial_mod.SerialException('busy'), None]

        with patch('lib.model.sdp.connection.sleep') as mock_sleep:
            result = conn._open()

        self.assertTrue(result)
        self.assertTrue(conn._is_connected)
        self.assertEqual(port.open.call_count, 2)
        mock_sleep.assert_called_once_with(0.01)

    def test_gives_up_after_exhausting_retries(self):
        """If every attempt fails, _open() must return False only after
        exhausting connect_retries, not after the first failure."""
        conn, port, serial_mod = _make_serial_conn(retries=2, cycle=0.01)
        port.open.side_effect = serial_mod.SerialException('busy')

        with patch('lib.model.sdp.connection.sleep'):
            result = conn._open()

        self.assertFalse(result)
        self.assertFalse(conn._is_connected)
        # connect_retries=2 means attempts 0,1,2 -> 3 tries total
        self.assertEqual(port.open.call_count, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
