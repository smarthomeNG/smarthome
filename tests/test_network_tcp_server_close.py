#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib.network.Tcp_server.close(), with real sockets and threads.

A plugin starts its server on the plugin thread, while the main thread may already stop the plugin.
"""

import asyncio
import contextlib
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.network import Tcp_server

HOST = '127.0.0.1'
JOIN_TIMEOUT = 5


def _free_port() -> int:
    with socket.socket() as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


def _accepts_connections(port: int) -> bool:
    try:
        with socket.create_connection((HOST, port), timeout=1):
            return True
    except OSError:
        return False


class TestTcpServerClose(unittest.TestCase):
    def setUp(self):
        self.port = _free_port()
        self.server = Tcp_server(self.port, host=HOST, name='test')

    def test_close_stops_listening(self):
        self.assertTrue(self.server.start())
        self.assertTrue(_accepts_connections(self.port))

        self.server.close()

        self.assertFalse(_accepts_connections(self.port))

    def test_close_during_start_returns_and_stops_listening(self):
        real_start_server = asyncio.start_server
        starting = threading.Event()
        loops = []

        async def slow_start_server(*args, **kwargs):
            """Start the real server, then block the loop so that close() is called before start() gets on."""
            server = await real_start_server(*args, **kwargs)
            loops.append(asyncio.get_running_loop())
            starting.set()
            time.sleep(0.3)
            return server

        def stop_loops():
            for loop in loops:
                with contextlib.suppress(RuntimeError):
                    loop.call_soon_threadsafe(loop.stop)

        self.addCleanup(stop_loops)
        with patch('lib.network.asyncio.start_server', slow_start_server):
            starter = threading.Thread(target=self.server.start, daemon=True)
            starter.start()
            self.assertTrue(starting.wait(JOIN_TIMEOUT))
            closer = threading.Thread(target=self.server.close, daemon=True)
            closer.start()
            starter.join(JOIN_TIMEOUT)
            closer.join(JOIN_TIMEOUT)

        self.assertFalse(starter.is_alive())
        self.assertFalse(closer.is_alive(), 'close() did not return')
        self.assertFalse(_accepts_connections(self.port))


if __name__ == '__main__':
    unittest.main()
