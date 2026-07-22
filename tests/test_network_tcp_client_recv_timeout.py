#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib.network.Tcp_client.__receive_thread_worker()'s
recv() timeout handling.

The exception filter used to be `e.errno not in (60, 65)` -- hardcoded
macOS/BSD errno values for ETIMEDOUT/EHOSTUNREACH. On Linux (shng's
primary deployment target) those numbers are different (110/113), so the
filter never matched there. Worse: a plain socket recv timeout (raised via
socket.settimeout()) is a TimeoutError with errno=None, not a numbered
errno at all -- confirmed empirically with a real local socket pair below
-- so even fixing the numbers to be portable (errno.ETIMEDOUT/EHOSTUNREACH)
would not be enough on its own; the exception type itself must be checked,
not just its errno.

Drives __receive_thread_worker() directly (bypassing connect(), which
would need a real reachable host) with a mocked selector reporting one
read-ready event and a mocked socket whose recv() raises the exception
under test, then checks whether _log_exception() -- the "receive thread
died with unexpected error" path -- was invoked.
"""

import errno
import os
import socket
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.network import Tcp_client
import selectors as selectors_module


def _make_client():
    tc = Tcp_client('127.0.0.1', 65500, autoreconnect=False, autoconnect=False)
    tc._socket = MagicMock()
    tc._is_connected = True
    tc._Tcp_client__running = True
    return tc


def _run_one_iteration(tc, recv_side_effect):
    """
    Run __receive_thread_worker() with a mocked selector that reports one
    read-ready event, then stops the loop. Returns the mocked _log_exception
    call args (or None if it wasn't called).
    """
    tc._socket.recv.side_effect = recv_side_effect

    fake_key = MagicMock()
    call_count = {'n': 0}

    def fake_select(timeout=None):
        call_count['n'] += 1
        if call_count['n'] == 1:
            return [(fake_key, selectors_module.EVENT_READ)]
        # stop the loop after the first (only) event has been handled
        tc._Tcp_client__running = False
        return []

    fake_selector = MagicMock()
    fake_selector.select.side_effect = fake_select

    with patch('lib.network.selectors.DefaultSelector', return_value=fake_selector):
        with patch.object(tc, '_log_exception') as mock_log_exception:
            tc._Tcp_client__receive_thread_worker()

    return mock_log_exception.call_args if mock_log_exception.called else None


class TestTcpClientRecvTimeoutHandling(unittest.TestCase):
    def test_real_socket_recv_timeout_has_errno_none(self):
        """
        Grounding check, not exercising Tcp_client: confirms the premise the
        rest of this file's fix depends on against a real local socket pair,
        independent of any mocking.
        """
        a, b = socket.socketpair()
        try:
            a.settimeout(0.05)
            with self.assertRaises(TimeoutError) as ctx:
                a.recv(10)
            self.assertIsNone(ctx.exception.errno)
        finally:
            a.close()
            b.close()

    def test_plain_timeout_error_with_errno_none_is_not_logged_as_unexpected(self):
        # exactly what a real settimeout()-triggered recv() raises
        exc = TimeoutError()
        exc.errno = None
        call = _run_one_iteration(_make_client(), exc)
        self.assertIsNone(call, f'a plain recv timeout must not be logged as an unexpected error, got: {call}')

    def test_oserror_with_etimedout_errno_is_not_logged_as_unexpected(self):
        exc = OSError()
        exc.errno = errno.ETIMEDOUT
        call = _run_one_iteration(_make_client(), exc)
        self.assertIsNone(call, f'ETIMEDOUT must not be logged as an unexpected error, got: {call}')

    def test_oserror_with_ehostunreach_errno_is_not_logged_as_unexpected(self):
        exc = OSError()
        exc.errno = errno.EHOSTUNREACH
        call = _run_one_iteration(_make_client(), exc)
        self.assertIsNone(call, f'EHOSTUNREACH must not be logged as an unexpected error, got: {call}')

    def test_genuine_unexpected_oserror_is_still_logged(self):
        # e.g. EBADF -- a real, unrelated error must still be reported, not
        # silently swallowed
        exc = OSError()
        exc.errno = errno.EBADF
        call = _run_one_iteration(_make_client(), exc)
        self.assertIsNotNone(call, 'a genuine unexpected OSError must still be logged')
        self.assertIn('unexpected error', call.args[1])


if __name__ == '__main__':
    unittest.main(verbosity=2)
