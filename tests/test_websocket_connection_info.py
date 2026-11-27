#!/usr/bin/env python3
"""Connection details of the websocket module (local port, TLS) without deprecated websockets attributes."""

import asyncio
import logging
import os
import shutil
import socket
import ssl
import subprocess
import tempfile
import sys
import threading
import time
import unittest
import warnings

import websockets

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from tests.test_websocket_shutdown import _free_port, _make_module


class _RecordingProtocol:
    """Payload protocol that records what the module reports about the connection, and the warnings that raised."""

    protocol_enabled = True

    def __init__(self):
        self.module = None
        self.done = threading.Event()
        self.port = self.secure = None
        self.error: Exception | None = None
        self.warnings: list[warnings.WarningMessage] = []

    def start_global_tasks(self, loop):
        pass

    async def handle_protocol(self, websocket):
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                self.port = self.module.local_port(websocket)
                self.secure = self.module.is_secure(websocket)
                await self.module.log_connection_event('connected', websocket)
            self.warnings = list(caught)
        except Exception as e:
            self.error = e
        finally:
            self.done.set()

    async def cleanup_connection(self, websocket):
        pass


class TestWebsocketConnectionInfo(unittest.TestCase):
    scheme = 'ws'
    secure = False
    client_ssl: ssl.SSLContext | None = None

    def setUp(self):
        self.port = _free_port()
        self.protocol = _RecordingProtocol()
        self.module = _make_module(self.port, self.protocol)
        self.module.USERS = set()
        self.protocol.module = self.module
        self.configure()
        self.module.start()

    def configure(self):
        pass

    def tearDown(self):
        self.module.stop()

    def _wait_listening(self):
        deadline = time.monotonic() + 5
        while True:
            try:
                socket.create_connection(('127.0.0.1', self.port), timeout=1).close()
                return
            except OSError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)

    def _connect(self):
        self._wait_listening()

        async def run():
            async with websockets.connect(f'{self.scheme}://127.0.0.1:{self.port}/test', ssl=self.client_ssl):
                await asyncio.get_running_loop().run_in_executor(None, self.protocol.done.wait, 5)

        asyncio.run(run())
        self.assertTrue(self.protocol.done.is_set(), 'protocol did not run')
        self.assertIsNone(self.protocol.error)

    def test_a_connection_reports_its_server_port_and_whether_it_uses_tls(self):
        with self.assertLogs('test.wsshutdown', level=logging.INFO) as logs:
            self._connect()
        self.assertEqual((self.protocol.port, self.protocol.secure), (self.port, self.secure))
        self.assertIn(f'local port: {self.port}', ' '.join(logs.output))

    def test_connection_details_use_no_deprecated_websockets_attributes(self):
        self._connect()
        self.assertEqual([str(w.message) for w in self.protocol.warnings], [])


@unittest.skipIf(shutil.which('openssl') is None, 'openssl not installed')
class TestSecureWebsocketConnectionInfo(TestWebsocketConnectionInfo):
    scheme = 'wss'
    secure = True

    def configure(self):
        certdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, certdir)
        cert, key = os.path.join(certdir, 'cert.pem'), os.path.join(certdir, 'key.pem')
        subprocess.run(
            [
                'openssl',
                'req',
                '-x509',
                '-newkey',
                'rsa:2048',
                '-nodes',
                '-days',
                '1',
                '-subj',
                '/CN=127.0.0.1',
                '-keyout',
                key,
                '-out',
                cert,
            ],
            check=True,
            capture_output=True,
        )
        server_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_ssl.load_cert_chain(cert, key)
        self.module.ssl_context = server_ssl
        self.module.tls_port, self.module.port = self.port, _free_port()
        self.client_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.client_ssl.load_verify_locations(cert)
        self.client_ssl.check_hostname = False


if __name__ == '__main__':
    unittest.main(verbosity=2)
