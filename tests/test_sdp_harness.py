#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Smoke tests for tests/sdp_harness: the fixture SDP plugin loads through the
real plugin loader, its items are parsed, and item writes reach the
recording connection as real send data.
"""

import tempfile
import unittest

from tests.sdp_harness import load_sdp_plugin

ITEMS = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_write: true
"""


class TestSdpHarness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', ITEMS)
        self.rig.plugin.run()

    def tearDown(self):
        self.rig.plugin.stop()
        self._tmp.cleanup()

    def test_item_write_sends_command_payload(self):
        self.rig.item('dev.power')(True, 'test')

        self.assertEqual(['PW'], self.rig.connection.payloads)

    def test_run_connects_and_fires_connect_callback(self):
        self.assertTrue(self.rig.connection.connected())
        self.assertIsNotNone(self.rig.job('read_initial_values'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
