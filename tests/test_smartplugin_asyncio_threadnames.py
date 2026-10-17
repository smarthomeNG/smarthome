#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the names of the worker threads behind the plugin's asyncio loop
(lib/model/smartplugin.py): executor workers must be attributable to their plugin.
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

    ALLOW_MULTIINSTANCE = True

    def run(self):
        self.alive = True
        self.start_asyncio(self.wait_for_asyncio_termination())

    def stop(self):
        self.alive = False


class TestExecutorThreadNames(unittest.TestCase):
    def setUp(self):
        self.plugin = AsyncioPlugin()
        self.plugin._shortname = 'nameplug'
        self.plugin._set_instance_name('inst1')
        self.plugin.run()
        for _ in range(200):
            if self.plugin._asyncio_state == 'running':
                break
            threading.Event().wait(0.01)
        self.assertEqual(self.plugin._asyncio_state, 'running')

    def tearDown(self):
        self.plugin.stop_asyncio()

    def _worker_thread_name(self) -> str:
        async def thread_name():
            return await asyncio.to_thread(lambda: threading.current_thread().name)

        return self.plugin.run_asyncio_coro(thread_name())

    def test_executor_worker_is_named_after_plugin_and_instance(self):
        self.assertEqual(self.plugin.get_fullname(), 'nameplug_inst1')

        name = self._worker_thread_name()

        self.assertTrue(name.startswith('plugins.nameplug_inst1.asyncio'), name)


if __name__ == '__main__':
    unittest.main()
