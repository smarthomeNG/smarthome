#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Replies on the synchronous serial connection, against a device on a pseudo terminal."""

import builtins

builtins.SDP_standalone = False

import os  # noqa: E402
import threading  # noqa: E402
import tty  # noqa: E402
import unittest  # noqa: E402

from lib.model.sdp.connection import SDPConnectionSerial  # noqa: E402
from lib.model.sdp.globals import (  # noqa: E402
    PLUGIN_ATTR_CONN_RETRIES,
    PLUGIN_ATTR_CONN_TIMEOUT,
    PLUGIN_ATTR_SERIAL_PORT,
)


class TestSerialReply(unittest.TestCase):
    def setUp(self):
        self.device, port = os.openpty()
        tty.setraw(port)
        self.port_name = os.ttyname(port)
        self.received = []
        self.conn = SDPConnectionSerial(
            lambda *args: self.received.append(args),
            name='test',
            **{PLUGIN_ATTR_SERIAL_PORT: self.port_name, PLUGIN_ATTR_CONN_TIMEOUT: 0.2, PLUGIN_ATTR_CONN_RETRIES: 0},
        )
        self.conn.open()
        self.device_thread = threading.Thread(target=self.answer, daemon=True)
        self.device_thread.start()

    def tearDown(self):
        self.conn.close()
        os.close(self.device)

    def answer(self):
        request = b''
        while not request.endswith(b'\r'):
            request += os.read(self.device, 64)
        os.write(self.device, b'OK\r')

    def test_reply_is_returned(self):
        reply = self.conn.send({'payload': 'Q\r', 'limit_response': b'\r'})

        self.assertEqual('OK', reply)

    def test_reply_is_not_pushed_to_data_callback(self):
        self.conn.send({'payload': 'Q\r', 'limit_response': b'\r'})

        self.assertEqual([], self.received)


if __name__ == '__main__':
    unittest.main(verbosity=2)
