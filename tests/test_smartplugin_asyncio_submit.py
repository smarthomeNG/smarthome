#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartPlugin.submit_asyncio_coro() (lib/model/smartplugin.py) - the
non-blocking counterpart to run_asyncio_coro(), run against a real asyncio
loop thread started via start_asyncio().
"""

import asyncio
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartplugin import SmartPlugin


class AsyncioPlugin(SmartPlugin):
    """Minimal concrete SmartPlugin whose plugin_coro just waits for termination."""

    def run(self):
        self.alive = True
        self.start_asyncio(self.wait_for_asyncio_termination())

    def stop(self):
        self.alive = False


class _RecordingLogger:
    def __init__(self):
        self.errors = []

    def error(self, msg, *args, **kwargs):
        self.errors.append(msg)

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class TestSubmitAsyncioCoro(unittest.TestCase):
    def setUp(self):
        self.plugin = AsyncioPlugin()
        self.plugin.logger = _RecordingLogger()
        self.plugin.run()
        for _ in range(200):
            if self.plugin._asyncio_state == 'running':
                break
            threading.Event().wait(0.01)
        self.assertEqual(self.plugin._asyncio_state, 'running')

    def tearDown(self):
        loop = self.plugin._asyncio_loop
        if loop is not None:
            asyncio.run_coroutine_threadsafe(self.plugin._run_queue.put('STOP'), loop)
        self.plugin.pluginThread.join(timeout=5)

    def test_returns_without_waiting_for_the_coroutine(self):
        release = threading.Event()

        async def blocked():
            await asyncio.get_running_loop().run_in_executor(None, release.wait)
            return 'done'

        future = self.plugin.submit_asyncio_coro(blocked())

        self.assertFalse(future.done())
        release.set()
        self.assertEqual(future.result(timeout=5), 'done')

    def test_exception_is_passed_to_on_error(self):
        received = []
        done = threading.Event()

        def on_error(ex):
            received.append(ex)
            done.set()

        async def failing():
            raise ValueError('boom')

        self.plugin.submit_asyncio_coro(failing(), on_error=on_error)

        self.assertTrue(done.wait(5))
        self.assertIsInstance(received[0], ValueError)

    def test_exception_without_on_error_is_logged(self):
        async def failing():
            raise ValueError('boom')

        future = self.plugin.submit_asyncio_coro(failing())
        with self.assertRaises(ValueError):
            future.result(timeout=5)

        for _ in range(100):
            if self.plugin.logger.errors:
                break
            threading.Event().wait(0.01)
        self.assertIn('boom', self.plugin.logger.errors[0])


class TestSubmitAsyncioCoroWithoutLoop(unittest.TestCase):
    def test_returns_none_and_closes_the_coroutine(self):
        plugin = AsyncioPlugin()
        plugin.logger = _RecordingLogger()

        async def never_run():
            return None

        coro = never_run()
        self.assertIsNone(plugin.submit_asyncio_coro(coro))
        self.assertIsNone(coro.cr_frame)
        self.assertEqual(len(plugin.logger.errors), 1)


if __name__ == '__main__':
    unittest.main()
