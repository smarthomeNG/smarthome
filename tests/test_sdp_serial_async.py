#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Serial connection with async listener, against a device on a pseudo terminal."""

import builtins

builtins.SDP_standalone = False

import os  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
import tty  # noqa: E402
import unittest  # noqa: E402

from lib.model.sdp.carriers import ConnectionHooks, DeviceConfig  # noqa: E402
from lib.model.sdp.connection import SDPConnectionSerialAsync  # noqa: E402
from lib.model.sdp.globals import SDPConnectionError  # noqa: E402

#: serial read timeout; replies must not wait for it
TIMEOUT = 2


class SerialAsyncTestCase(unittest.TestCase):
    """Async serial connection on a pty; ``self.device`` is the device end, ``self.received`` the dispatched lines."""

    CONNECT_RETRIES = 0

    def setUp(self):
        self.device, port = os.openpty()
        tty.setraw(port)
        self.port_name = os.ttyname(port)
        self.received = []
        self.dispatched = threading.Event()
        self.disconnected = threading.Event()
        self.conn = SDPConnectionSerialAsync(
            DeviceConfig.from_params(
                {
                    'serialport': self.port_name,
                    'timeout': TIMEOUT,
                    'terminator': b'\r',
                    'connect_retries': self.CONNECT_RETRIES,
                    'connect_cycle': 0,
                    'autoconnect': False,
                }
            ),
            self.hooks(),
            None,
            'test',
        )

    def tearDown(self):
        self.conn.close()
        try:
            os.close(self.device)
        except OSError:
            pass

    def hooks(self) -> ConnectionHooks:
        """Hooks recording dispatched lines and disconnects."""
        return ConnectionHooks(on_data=self.on_data, on_disconnect=lambda by: self.disconnected.set())

    def on_data(self, by, line):
        self.received.append(line)
        self.dispatched.set()

    def wait_for(self, count: int, timeout: float) -> bool:
        """Wait until ``count`` lines are dispatched, at most ``timeout`` seconds."""
        end = time.time() + timeout
        while len(self.received) < count and time.time() < end:
            time.sleep(0.01)
        return len(self.received) >= count


class TestReplyLatency(SerialAsyncTestCase):
    def test_line_is_dispatched_before_read_timeout(self):
        self.conn.open()
        os.write(self.device, b'MUOFF\r')

        self.assertTrue(self.wait_for(1, TIMEOUT / 2))
        self.assertEqual(['MUOFF'], self.received)

    def test_line_is_dispatched_while_device_keeps_sending(self):
        self.conn.open()
        os.write(self.device, b'MUOFF\r')
        stop = threading.Event()

        def chatter():
            while not stop.wait(TIMEOUT / 4):
                os.write(self.device, b'NSE1\r')

        threading.Thread(target=chatter, daemon=True).start()
        try:
            self.assertTrue(self.wait_for(1, TIMEOUT / 2))
        finally:
            stop.set()
        self.assertEqual('MUOFF', self.received[0])


class TestBadInput(SerialAsyncTestCase):
    def test_line_with_invalid_utf8_is_dispatched_with_replacement(self):
        self.conn.open()
        os.write(self.device, b'\xffPWON\r')

        self.assertTrue(self.wait_for(1, TIMEOUT / 2))
        self.assertEqual(['�PWON'], self.received)

    def test_lines_after_invalid_utf8_are_dispatched(self):
        self.conn.open()
        os.write(self.device, b'\xffPWON\r')
        self.wait_for(1, TIMEOUT / 2)
        os.write(self.device, b'MUOFF\r')

        self.assertTrue(self.wait_for(2, TIMEOUT / 2))
        self.assertEqual('MUOFF', self.received[1])

    def test_lines_after_failing_data_callback_are_dispatched(self):
        self.conn.open()
        self.fail_next = True
        os.write(self.device, b'PWON\r')
        self.wait_for(1, TIMEOUT / 2)
        os.write(self.device, b'MUOFF\r')

        self.assertTrue(self.wait_for(2, TIMEOUT / 2))
        self.assertEqual(['PWON', 'MUOFF'], self.received)

    def on_data(self, by, line):
        super().on_data(by, line)
        if getattr(self, 'fail_next', False):
            self.fail_next = False
            raise ValueError('plugin error')


class TestSend(SerialAsyncTestCase):
    def test_reply_is_dispatched_not_returned(self):
        self.conn.open()
        threading.Timer(0.1, os.write, (self.device, b'MUOFF\r')).start()

        self.assertIsNone(self.conn.send({'payload': 'MU?\r', 'limit_response': b'\r'}))
        self.assertTrue(self.wait_for(1, TIMEOUT / 2))
        self.assertEqual(['MUOFF'], self.received)


class TestDeviceLoss(SerialAsyncTestCase):
    def test_lost_device_disconnects(self):
        self.conn.open()
        os.close(self.device)

        self.assertTrue(self.disconnected.wait(TIMEOUT * 2))
        self.assertFalse(self.conn.connected())

    def test_send_after_lost_device_raises(self):
        self.conn.open()
        os.close(self.device)
        self.disconnected.wait(TIMEOUT * 2)

        with self.assertRaises(SDPConnectionError):
            self.conn.send({'payload': 'MU?\r', 'limit_response': b'\r'})


class TestNumParams(SerialAsyncTestCase):
    CONNECT_RETRIES = 3.0

    def test_opens_with_retries_from_num_param(self):
        self.assertTrue(self.conn.open())


class TestConcurrentOpen(SerialAsyncTestCase):
    CONNECT_RETRIES = 3

    def hooks(self) -> ConnectionHooks:
        self.connects = []
        return ConnectionHooks(on_data=self.on_data, on_connect=self.connects.append)

    def open_concurrently(self):
        """Open from two threads while opening the port takes a while."""
        port = self.conn._connection
        port_open = port.open

        def slow_open():
            time.sleep(0.2)
            port_open()

        port.open = slow_open
        openers = [threading.Thread(target=self.conn.open) for _ in range(2)]
        for opener in openers:
            opener.start()
        for opener in openers:
            opener.join()

    def test_concurrent_open_connects_once(self):
        self.open_concurrently()

        self.assertEqual(1, len(self.connects))
        self.assertTrue(self.conn.connected())

    def test_concurrent_open_dispatches_each_line_once(self):
        self.open_concurrently()
        os.write(self.device, b'PWON\rMUOFF\rZMON\r')

        self.wait_for(3, TIMEOUT / 2)
        self.assertEqual(['PWON', 'MUOFF', 'ZMON'], self.received)


if __name__ == '__main__':
    unittest.main(verbosity=2)
