#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Shutdown behaviour of the websocket module (modules/websocket/__init__.py).

`Websocket.stop()` must bring the server thread down cleanly while clients are
connected, including clients that reconnect automatically as soon as their
connection is closed (smartVISU, shngadmin):

- the listening socket is closed before connections are torn down, so no new
  connection can be accepted while the event loop is draining
- no asyncio error is logged on the way out (an async generator still running
  when the loop shuts its async generators down)
- the server thread terminates
"""

import asyncio
import logging
import os
import socket
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock

import websockets

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from modules.websocket import Websocket


class _HoldOpenProtocol:
    """Payload protocol that keeps every connection open until the peer or the server closes it."""

    protocol_enabled = True

    def __init__(self):
        self.connected = threading.Event()

    def start_global_tasks(self, loop):
        pass

    async def handle_protocol(self, websocket):
        self.connected.set()
        async for _ in websocket:
            pass

    async def cleanup_connection(self, websocket):
        # connection cleanup that yields to the loop, like the real protocols' unregister path
        await asyncio.sleep(0.3)


def _free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def _make_module(port, protocol):
    module = Websocket.__new__(Websocket)
    module.logger = logging.getLogger('test.wsshutdown')
    module.translate = lambda txt, vars=None: str(txt)
    module._sh = MagicMock()
    module._sh.shng_status = {'code': 20}
    module.ip = '127.0.0.1'
    module.port = port
    module.tls_port = 0
    module.ssl_context = None
    module.loop = None
    module._servers = []
    module.protocols = {'/test': {'id': 'test', 'name': 'test', 'protocol': protocol}}
    return module


class _ReconnectingClient(threading.Thread):
    """Connects to the server and reconnects immediately whenever the connection ends."""

    def __init__(self, port):
        super().__init__(daemon=True)
        self._url = f'ws://127.0.0.1:{port}/test'
        self._stop_event = threading.Event()

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self._url) as ws:
                    async for _ in ws:
                        pass
            except Exception:
                await asyncio.sleep(0.01)

    def halt(self):
        self._stop_event.set()


class TestWebsocketShutdown(unittest.TestCase):
    def setUp(self):
        self.port = _free_port()
        self.protocol = _HoldOpenProtocol()
        self.module = _make_module(self.port, self.protocol)
        self.module.start()
        self.clients = []

    def tearDown(self):
        for client in self.clients:
            client.halt()
        thread = self.module._server_thread
        if thread.is_alive():
            self.module.loop.call_soon_threadsafe(self.module.loop.stop)
            thread.join(timeout=15)

    def _start_clients(self, count):
        for _ in range(count):
            client = _ReconnectingClient(self.port)
            client.start()
            self.clients.append(client)
        self.assertTrue(self.protocol.connected.wait(timeout=5), 'no client connected')
        time.sleep(0.2)

    def test_stop_with_reconnecting_clients_logs_no_asyncio_error(self):
        self._start_clients(3)
        with self.assertNoLogs('asyncio', level=logging.ERROR):
            self.module.stop()
        self.assertFalse(self.module._server_thread.is_alive())

    def test_stop_closes_listening_socket(self):
        self._start_clients(1)
        self.module.stop()
        with self.assertRaises(OSError):
            socket.create_connection(('127.0.0.1', self.port), timeout=1).close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
