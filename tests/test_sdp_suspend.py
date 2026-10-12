#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Suspend mode of SmartDevicePlugin."""

import tempfile
import unittest

from tests.sdp_harness import load_sdp_plugin

ITEMS = """
dev:
    suspend:
        type: bool
    power:
        type: bool
        fx_command: status.power
        fx_write: true
"""


class TestSuspendItem(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', ITEMS, params={'suspend_item': 'dev.suspend'}
        )
        self.plugin = self.rig.plugin
        self.plugin.run()
        self.suspend_item = self.rig.item('dev.suspend')

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    def test_suspend_item_suspends_communication_but_keeps_plugin_running(self):
        self.suspend_item(True, 'test')

        self.assertTrue(self.plugin.suspended)
        self.assertTrue(self.plugin.alive)
        self.assertFalse(self.rig.connection.connected())

    def test_suspend_item_resumes_communication(self):
        self.suspend_item(True, 'test')
        self.suspend_item(False, 'test')

        self.assertFalse(self.plugin.suspended)
        self.assertTrue(self.rig.connection.connected())

    def test_suspended_plugin_does_not_write(self):
        self.suspend_item(True, 'test')

        self.rig.item('dev.power')(True, 'test')

        self.assertEqual([], self.rig.connection.payloads)

    def test_plugin_triggered_suspend_is_written_to_suspend_item(self):
        suspends = []
        self.plugin.on_suspend = lambda: suspends.append(True)

        self.plugin.set_suspend(True, by='connection')

        self.assertTrue(self.suspend_item())
        self.assertEqual([True], suspends)

    def test_renamed_suspend_item_still_suspends(self):
        self.rig.rename(self.suspend_item, 'dev.suspend_renamed')

        self.suspend_item(True, 'test')

        self.assertTrue(self.plugin.suspended)

    def test_removed_suspend_item_is_no_longer_written(self):
        self.plugin.remove_item(self.suspend_item)
        if not self.plugin.alive:
            self.plugin.run()

        self.plugin.set_suspend(True, by='connection')

        self.assertTrue(self.plugin.suspended)
        self.assertFalse(self.suspend_item())


if __name__ == '__main__':
    unittest.main(verbosity=2)
