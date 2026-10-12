#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Read group '0' reads all readable commands, however it is triggered."""

import tempfile
import unittest

from tests.sdp_harness import load_sdp_plugin

ITEMS = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
    volume:
        type: num
        fx_command: status.volume
        fx_read: true
    read_all:
        type: bool
        fx_read_group_trigger: '0'
        fx_read_initial: true
        fx_read_cycle: 10
"""


class TestReadAllTrigger(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', ITEMS)
        self.plugin = self.rig.plugin

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    def test_initial_trigger_reads_all(self):
        self.plugin.run()

        self.rig.plugin_jobs()['read_initial_values'].fire()

        self.assertEqual(['PW', 'VO'], self.rig.connection.payloads)

    def test_cyclic_trigger_reads_all(self):
        self.plugin.run()
        self.rig.connection.sent.clear()

        self.rig.plugin_jobs()[self.plugin.get_fullname() + '_cyclic'].fire()

        self.assertEqual(['PW', 'VO'], self.rig.connection.payloads)

    def test_item_trigger_reads_all(self):
        self.plugin.run()
        self.rig.connection.sent.clear()

        self.rig.item('dev.read_all')(True, 'test')

        self.assertEqual(['PW', 'VO'], self.rig.connection.payloads)


if __name__ == '__main__':
    unittest.main(verbosity=2)
