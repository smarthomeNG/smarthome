#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Item bookkeeping of SmartDevicePlugin: dispatch, read groups, rename, removal."""

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
        fx_read_group: grp
    power_mirror:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_read_group: grp
    power_pseudo:
        type: bool
        fx_command: status.power
    volume:
        type: num
        fx_command: status.volume
        fx_read: true
        fx_read_group: grp
    volume_pseudo:
        type: num
        fx_command: status.volume
    read_grp:
        type: bool
        fx_read_group_trigger: grp
    colors:
        type: dict
        fx_lookup: COLORS
    color_names:
        type: list
        fx_lookup: COLORS#list
"""


class _RegistryTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', ITEMS)
        self.rig.plugin.run()
        self.conn = self.rig.connection
        self.conn.sent.clear()

    def tearDown(self):
        self.rig.plugin.stop()
        self._tmp.cleanup()

    def receive(self, command, value):
        self.conn.replies[{'status.power': 'PW', 'status.volume': 'VO'}[command]] = value
        self.rig.plugin.send_command(command)

    def remove(self, item):
        # shng stops a running plugin for an item removal and runs it again afterwards
        self.rig.plugin.remove_item(item)
        if not self.rig.plugin.alive:
            self.rig.plugin.run()
        self.conn.sent.clear()


class TestDispatch(_RegistryTestBase):
    def test_value_reaches_read_and_pseudo_items(self):
        self.receive('status.power', True)

        for path in ('dev.power', 'dev.power_mirror', 'dev.power_pseudo'):
            self.assertTrue(self.rig.item(path)(), path)

    def test_each_item_updated_once_per_received_value(self):
        updates = []
        self.rig.item('dev.volume_pseudo').add_method_trigger(lambda item, *a, **kw: updates.append(item()))
        for value in (1, 2, 3):
            self.receive('status.volume', value)

        self.assertEqual([1, 2, 3], updates)


class TestReadGroup(_RegistryTestBase):
    def test_group_trigger_reads_each_command_once(self):
        self.rig.item('dev.read_grp')(True, 'test')

        self.assertEqual(['PW', 'VO'], self.conn.payloads)


class TestRename(_RegistryTestBase):
    def test_renamed_write_item_still_writes(self):
        item = self.rig.item('dev.power')
        self.rig.rename(item, 'dev.power_renamed')

        item(True, 'test')

        self.assertEqual(['PW'], self.conn.payloads)

    def test_renamed_group_trigger_still_triggers(self):
        item = self.rig.item('dev.read_grp')
        self.rig.rename(item, 'dev.read_grp_renamed')

        item(True, 'test')

        self.assertEqual(['PW', 'VO'], self.conn.payloads)


class TestRemove(_RegistryTestBase):
    def test_removed_write_item_no_longer_writes(self):
        item = self.rig.item('dev.power')
        self.remove(item)

        item(True, 'test')

        self.assertEqual([], self.conn.payloads)

    def test_removed_read_item_no_longer_receives(self):
        item = self.rig.item('dev.power_mirror')
        self.remove(item)

        self.receive('status.power', True)

        self.assertFalse(item())
        self.assertTrue(self.rig.item('dev.power')())

    def test_lookup_items_follow_table_until_removed(self):
        names = self.rig.item('dev.color_names')
        self.rig.item('dev.colors')({'R': 'Rot', 'G': 'Grün'}, 'test')
        self.assertEqual(['Rot', 'Grün'], names())

        self.remove(names)
        self.rig.item('dev.colors')({'R': 'Rouge', 'G': 'Vert'}, 'test')

        self.assertEqual(['Rot', 'Grün'], names())

    def test_removed_item_command_no_longer_read_in_group(self):
        self.remove(self.rig.item('dev.volume'))

        self.rig.item('dev.read_grp')(True, 'test')

        self.assertEqual(['PW'], self.conn.payloads)


if __name__ == '__main__':
    unittest.main(verbosity=2)
