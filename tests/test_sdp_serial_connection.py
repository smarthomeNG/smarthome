#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SDPConnectionSerial._send_bytes() and _read_bytes().

Covers our exception-refactor changes:
  - _send_bytes() raises SDPConnectionError instead of returning False
  - _read_bytes() fires the disconnect callback and marks _is_connected=False
    on read timeout; returns b'' (does not raise on normal timeout)
  - _read_bytes() raises SDPConnectionError on lock contention
"""

import builtins

builtins.SDP_standalone = False

import logging
import threading
import time
import unittest
from unittest.mock import MagicMock, call

from lib.model.sdp.globals import (
    SDPConnectionError,
    PLUGIN_ATTR_SERIAL_PORT,
    PLUGIN_ATTR_CONN_AUTO_CONN,
    PLUGIN_ATTR_CONN_TIMEOUT,
    PLUGIN_ATTR_CB_ON_DISCONNECT,
)
from lib.model.sdp.connection import SDPConnectionSerial


# ---------------------------------------------------------------------------
# Helper — build a minimal SDPConnectionSerial without touching serial hardware
# ---------------------------------------------------------------------------


def _make_serial_conn(is_connected=True, disconnect_cb=None):
    """
    Create SDPConnectionSerial via object.__new__ and set only the attributes
    exercised by _send_bytes() and _read_bytes(), using a MagicMock serial port.
    """

    # Define lightweight exception types that mirror pyserial's hierarchy
    class _SerialException(OSError):
        pass

    class _SerialTimeoutException(_SerialException):
        pass

    mock_serial_module = MagicMock()
    mock_serial_module.SerialException = _SerialException
    mock_serial_module.SerialTimeoutException = _SerialTimeoutException

    mock_port = MagicMock()

    conn = object.__new__(SDPConnectionSerial)
    conn.logger = logging.getLogger('test.serial')
    conn._is_connected = is_connected
    conn._listener_active = False
    conn._read_buffer = b''
    conn._lastbyte = b''
    conn._lastbytetime = 0
    conn.__lock_timeout = 2
    conn._timeout_mult = 3
    conn.serial = mock_serial_module
    conn._connection = mock_port

    cb = disconnect_cb if disconnect_cb else MagicMock()
    conn._params = {
        PLUGIN_ATTR_SERIAL_PORT: '/dev/mock_tty',
        PLUGIN_ATTR_CONN_AUTO_CONN: False,
        PLUGIN_ATTR_CONN_TIMEOUT: 0.1,  # short for tests
        PLUGIN_ATTR_CB_ON_DISCONNECT: cb,
    }
    # __lock_timeout uses Python name-mangling; must be set with the mangled name
    conn._SDPConnectionSerial__lock_timeout = 2
    conn._lock = _make_timeout_lock()

    return conn, mock_port, mock_serial_module, cb


def _make_timeout_lock():
    """Recreate the TimeoutLock inner class from SDPConnectionSerial."""
    from contextlib import contextmanager

    class TimeoutLock:
        def __init__(self):
            self._lock = threading.Lock()

        def acquire(self, blocking=True, timeout=-1):
            return self._lock.acquire(blocking, timeout)

        @contextmanager
        def acquire_timeout(self, timeout):
            result = self._lock.acquire(timeout=timeout)
            yield result
            if result:
                self._lock.release()

        def release(self):
            self._lock.release()

    return TimeoutLock()


# ---------------------------------------------------------------------------
# _send_bytes() tests
# ---------------------------------------------------------------------------


class TestSendBytes(unittest.TestCase):
    def test_raises_when_not_connected(self):
        conn, port, serial_mod, _ = _make_serial_conn(is_connected=False)
        with self.assertRaises(SDPConnectionError):
            conn._send_bytes(b'\x04')

    def test_raises_on_serial_timeout_exception(self):
        conn, port, serial_mod, _ = _make_serial_conn()
        port.write.side_effect = serial_mod.SerialTimeoutException('timeout')
        with self.assertRaises(SDPConnectionError) as ctx:
            conn._send_bytes(b'\x04')
        self.assertIn('timeout', str(ctx.exception).lower())

    def test_raises_on_serial_exception(self):
        conn, port, serial_mod, _ = _make_serial_conn()
        port.write.side_effect = serial_mod.SerialException('port vanished')
        with self.assertRaises(SDPConnectionError) as ctx:
            conn._send_bytes(b'\x04')
        self.assertIn('/dev/mock_tty', str(ctx.exception))

    def test_returns_byte_count_on_success(self):
        conn, port, serial_mod, _ = _make_serial_conn()
        port.write.return_value = 3
        result = conn._send_bytes(b'\x41\x05\x00')
        self.assertEqual(result, 3)
        port.write.assert_called_once_with(b'\x41\x05\x00')

    def test_serial_exception_is_oserror_subclass(self):
        """Ensure the exception chaining preserves OSError identity."""
        conn, port, serial_mod, _ = _make_serial_conn()
        port.write.side_effect = serial_mod.SerialException('broken')
        with self.assertRaises(OSError):  # SDPConnectionError IS OSError
            conn._send_bytes(b'\x04')


# ---------------------------------------------------------------------------
# _read_bytes() — timeout / disconnect behaviour
# ---------------------------------------------------------------------------


class TestReadBytesDisconnect(unittest.TestCase):
    def _make_conn_with_instant_timeout(self, disconnect_cb=None):
        """Serial port whose read() always returns b'' immediately."""
        conn, port, serial_mod, cb = _make_serial_conn(disconnect_cb=disconnect_cb)
        # read() returns b'' → triggers timeout path immediately
        port.read.return_value = b''
        # Make the lock acquire succeed immediately
        return conn, port, cb

    def test_does_not_change_is_connected_on_timeout(self):
        # A read timeout means the device did not respond in time — normal for P300
        # SYNC wait. Setting _is_connected = False would cause _send_bytes and
        # subsequent _read_bytes to bail immediately, killing the protocol retry loop.
        # Real disconnects surface through SerialException on write, not read timeout.
        conn, port, cb = self._make_conn_with_instant_timeout()
        conn._is_connected = True
        conn._read_bytes(1)
        self.assertTrue(conn._is_connected)

    def test_does_not_fire_disconnect_callback_on_timeout(self):
        cb = MagicMock()
        conn, port, _ = self._make_conn_with_instant_timeout(disconnect_cb=cb)
        conn._is_connected = True
        conn._read_bytes(1)
        cb.assert_not_called()

    def test_returns_empty_bytes_on_timeout(self):
        """_read_bytes does NOT raise on timeout — returns b''."""
        conn, port, cb = self._make_conn_with_instant_timeout()
        result = conn._read_bytes(1)
        self.assertEqual(result, b'')

    def test_returns_data_when_available(self):
        """When bytes are returned by the port, they come back from _read_bytes."""
        conn, port, serial_mod, cb = _make_serial_conn()
        # read() returns a byte the first time, then b'' to stop the loop
        port.read.side_effect = [b'\x06', b'']
        result = conn._read_bytes(1)
        self.assertEqual(result, b'\x06')
        self.assertTrue(conn._is_connected)  # still connected
        cb.assert_not_called()

    def test_raises_on_lock_contention(self):
        """If the lock cannot be acquired within timeout, raise SDPConnectionError."""
        conn, port, serial_mod, cb = _make_serial_conn()

        # Replace lock with one that always fails to acquire
        class NeverAcquireLock:
            @__import__('contextlib').contextmanager
            def acquire_timeout(self, timeout):
                yield False  # locked = False

        conn._lock = NeverAcquireLock()
        with self.assertRaises(SDPConnectionError):
            conn._read_bytes(1)


class TestReadBytesStaleDetection(unittest.TestCase):
    """
    Stale connection detection: if _read_bytes() times out AND the device has
    been silent for > _STALE_CONNECTION_TIMEOUT seconds, _close() must be called
    to trigger the reconnect path.
    """

    def _make_conn_stale(self, lastbytetime):
        conn, port, serial_mod, cb = _make_serial_conn()
        port.read.return_value = b''
        conn._lastbytetime = lastbytetime
        conn._close = MagicMock()
        return conn, port, cb

    def test_closes_when_stale(self):
        from lib.model.sdp.connection import _STALE_CONNECTION_TIMEOUT

        stale_time = time.time() - _STALE_CONNECTION_TIMEOUT - 5
        conn, port, cb = self._make_conn_stale(stale_time)
        conn._read_bytes(1)
        conn._close.assert_called_once()

    def test_does_not_close_when_recent(self):
        conn, port, cb = self._make_conn_stale(time.time() - 5)
        conn._read_bytes(1)
        conn._close.assert_not_called()

    def test_does_not_close_when_lastbytetime_zero(self):
        """_lastbytetime == 0 means no bytes ever received; skip stale check."""
        conn, port, cb = self._make_conn_stale(0)
        conn._read_bytes(1)
        conn._close.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
