#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Cyclic reads: the shortest requested cycle wins, the worker runs at half of it."""

import tempfile
import unittest

from tests.sdp_harness import load_sdp_plugin

CYCLIC_JOB = '_cyclic'


class _CyclicTestBase(unittest.TestCase):
    params: dict = {}
    items: str = ''

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', self.items, params=self.params
        )
        self.rig.plugin.run()

    def tearDown(self):
        self.rig.plugin.stop()
        self._tmp.cleanup()

    def worker_cycle(self):
        job = self.rig.plugin_jobs().get(self.rig.plugin.get_fullname() + CYCLIC_JOB)
        return job.cycle if job else None


class TestTwoItemsSameCommand(_CyclicTestBase):
    items = """
dev:
    slow:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_read_cycle: 30
    fast:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_read_cycle: 10
"""

    def test_shortest_item_cycle_drives_worker(self):
        self.assertEqual(5, self.worker_cycle())

    def test_both_items_receive_cyclic_reply(self):
        self.rig.connection.replies['PW'] = True
        self.rig.plugin_jobs()[self.rig.plugin.get_fullname() + CYCLIC_JOB].fire()

        self.assertTrue(self.rig.item('dev.slow')())
        self.assertTrue(self.rig.item('dev.fast')())


class TestItemWithPluginCycleAndOwnCycle(_CyclicTestBase):
    params = {'cycle': 30}
    items = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_read_cyclic: true
        fx_read_cycle: 10
"""

    def test_shorter_own_cycle_wins_over_plugin_cycle(self):
        self.assertEqual(5, self.worker_cycle())


class TestTwoTriggersSameGroup(_CyclicTestBase):
    items = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_read_group: grp
    slow_trigger:
        type: bool
        fx_read_group_trigger: grp
        fx_read_cycle: 30
    fast_trigger:
        type: bool
        fx_read_group_trigger: grp
        fx_read_cycle: 10
"""

    def test_shortest_trigger_cycle_drives_worker(self):
        self.assertEqual(5, self.worker_cycle())


if __name__ == '__main__':
    unittest.main(verbosity=2)
