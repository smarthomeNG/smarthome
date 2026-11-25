#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartPlugin.stop_asyncio() / put_command_to_run_queue()
(lib/model/smartplugin.py), run against a real asyncio loop thread started via
start_asyncio().
"""

import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartplugin import SmartPlugin

# Generous upper bound for operations that must not wait on fixed delays
FAST = 1.5


class AsyncioPlugin(SmartPlugin):
    """Minimal concrete SmartPlugin whose plugin_coro just waits for termination."""

    def run(self):
        self.alive = True
        self.start_asyncio(self.wait_for_asyncio_termination())

    def stop(self):
        self.alive = False
        self.stop_asyncio()


class CommandPlugin(AsyncioPlugin):
    """Plugin whose plugin_coro records commands from the run-queue until 'STOP'."""

    def __init__(self):
        super().__init__()
        self.commands = []
        self.received = threading.Event()

    def run(self):
        self.alive = True
        self.start_asyncio(self._consume())

    async def _consume(self):
        command = ''
        while command != 'STOP':
            command = await self.get_command_from_run_queue()
            self.commands.append(command)
            self.received.set()


def _start(plugin):
    plugin.run()
    for _ in range(200):
        if plugin.asyncio_state() == 'running':
            return
        threading.Event().wait(0.01)
    raise AssertionError('asyncio loop did not start')


class TestStopAsyncio(unittest.TestCase):
    def test_stop_returns_promptly_and_stops_the_loop_thread(self):
        plugin = AsyncioPlugin()
        _start(plugin)

        started = time.monotonic()
        plugin.stop()
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, FAST)
        self.assertEqual(plugin.asyncio_state(), 'stopped')
        self.assertFalse(plugin.pluginThread.is_alive())

    def test_stop_without_running_loop_returns_promptly(self):
        plugin = AsyncioPlugin()

        started = time.monotonic()
        plugin.stop_asyncio()

        self.assertLess(time.monotonic() - started, FAST)


class TestPutCommandToRunQueue(unittest.TestCase):
    def test_command_reaches_the_plugin_coro_and_call_returns_promptly(self):
        plugin = CommandPlugin()
        _start(plugin)
        try:
            started = time.monotonic()
            plugin.put_command_to_run_queue('PING')
            elapsed = time.monotonic() - started

            self.assertLess(elapsed, FAST)
            self.assertTrue(plugin.received.wait(FAST))
            self.assertEqual(plugin.commands, ['PING'])
        finally:
            plugin.stop()


if __name__ == '__main__':
    unittest.main()
