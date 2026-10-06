#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartDevicePlugin's opt-in invalidation of device-mirroring items on connection loss.

Runs the real SDP stack via tests/sdp_harness. The database plugin's injected item
functions (``db_mark_invalid``/``db_is_invalid``) are replaced by :class:`GapRecorder`.
"""

import tempfile
import unittest

from lib.model.sdp.globals import PLUGIN_ATTR_CB_SUSPEND
from tests.gap_recorder import GapRecorder
from tests.sdp_harness import SDPRig, load_sdp_plugin

ITEMS = """
dev:
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_write: true
    key:
        type: bool
        fx_command: control.key
        fx_write: true
"""


class InvalidateOnDisconnectBase(unittest.TestCase):
    items_yaml = ITEMS
    params: dict = {'invalidate_on_disconnect': True}
    unlogged: set[str] = set()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig: SDPRig = load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', self.items_yaml, params=self.params
        )
        self.gaps = {
            item.property.path: GapRecorder(item)
            for item in self.rig.plugin.get_item_list()
            if item.property.path not in self.unlogged
        }
        self.before_run()
        self.rig.plugin.run()

    def before_run(self) -> None:
        """Hook for subclasses: adjust the rig before the plugin starts."""

    def tearDown(self):
        self.rig.plugin.stop()
        self._tmp.cleanup()

    def drop_connection(self) -> None:
        """The transport reports that the connection was lost."""
        self.rig.connection.on_disconnect('test')

    def abort_connecting(self) -> None:
        """The transport gives up reconnecting and asks the plugin to suspend (``retry_suspend`` reached)."""
        self.rig.connection._params[PLUGIN_ATTR_CB_SUSPEND](True, by='test')


class TestInvalidateOnDisconnect(InvalidateOnDisconnectBase):
    def test_connection_loss_marks_readable_item_invalid(self):
        self.drop_connection()

        self.assertEqual([(self.rig.plugin.get_fullname(), 'connection_lost')], self.gaps['dev.power'].calls)

    def test_repeated_disconnect_opens_only_one_gap(self):
        self.drop_connection()
        self.drop_connection()

        self.assertEqual(1, len(self.gaps['dev.power'].calls))

    def test_write_only_item_is_not_marked(self):
        self.drop_connection()

        self.assertEqual([], self.gaps['dev.key'].calls)

    def test_manual_suspend_marks_nothing(self):
        self.rig.plugin.suspend(by='test')

        self.assertEqual([], self.gaps['dev.power'].calls)

    def test_connection_failure_suspend_marks_item_once(self):
        self.abort_connecting()

        self.assertTrue(self.rig.plugin.suspended)
        self.assertEqual(1, len(self.gaps['dev.power'].calls))

    def test_connection_failure_suspend_marks_item_even_if_closing_fires_no_disconnect(self):
        self.rig.connection._close = lambda: None

        self.abort_connecting()

        self.assertEqual(1, len(self.gaps['dev.power'].calls))

    def test_overwritten_hook_filters_items(self):
        self.rig.plugin.should_invalidate_item = lambda item, by=None: False

        self.drop_connection()

        self.assertEqual([], self.gaps['dev.power'].calls)

    def test_manual_suspend_after_resume_from_failure_marks_nothing(self):
        self.abort_connecting()
        self.rig.plugin.resume(by='test')
        self.gaps['dev.power'].open_gap = False
        self.gaps['dev.power'].calls.clear()

        self.rig.plugin.suspend(by='test')

        self.assertEqual([], self.gaps['dev.power'].calls)


class TestUnloggedItem(InvalidateOnDisconnectBase):
    items_yaml = (
        ITEMS
        + """
    volume:
        type: num
        fx_command: status.volume
        fx_read: true
"""
    )
    unlogged = {'dev.power'}

    def test_item_unknown_to_database_plugin_is_skipped_others_are_marked(self):
        self.drop_connection()

        self.assertEqual(1, len(self.gaps['dev.volume'].calls))


class TestSuspendItem(InvalidateOnDisconnectBase):
    items_yaml = (
        ITEMS
        + """
    suspend:
        type: bool
"""
    )
    params = {'invalidate_on_disconnect': True, 'suspend_item': 'dev.suspend'}

    def test_suspend_item_is_not_marked(self):
        self.drop_connection()

        self.assertEqual([], self.gaps['dev.suspend'].calls)


class TestNeverConnected(InvalidateOnDisconnectBase):
    def before_run(self) -> None:
        self.rig.connection._open = lambda: False

    def test_connection_failure_suspend_marks_nothing(self):
        self.abort_connecting()

        self.assertEqual([], self.gaps['dev.power'].calls)


class TestOptionOff(InvalidateOnDisconnectBase):
    params = {'invalidate_on_disconnect': False}

    def test_connection_loss_marks_nothing(self):
        self.drop_connection()

        self.assertEqual([], self.gaps['dev.power'].calls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
