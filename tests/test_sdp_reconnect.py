#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Reconnect of SmartDevicePlugin after a lost connection."""

import tempfile
import unittest

from tests.sdp_harness import load_sdp_plugin


class TestReconnect(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', '', params={'autoreconnect': True}
        )
        self.rig.plugin.run()
        self.reconnect_job = self.rig.plugin.get_fullname() + '_reconnect'

    def tearDown(self):
        self.rig.plugin.stop()
        self._tmp.cleanup()

    def test_lost_connection_schedules_reconnect(self):
        self.rig.connection.close()

        self.assertIsNotNone(self.rig.job(self.reconnect_job))

    def test_no_reconnect_scheduled_if_transport_reconnects_itself(self):
        self.rig.connection.SELF_RECONNECTS = True

        self.rig.connection.close()

        self.assertIsNone(self.rig.job(self.reconnect_job))


if __name__ == '__main__':
    unittest.main(verbosity=2)
