#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
SmartPlugin.db_invalidate_items(): marks items invalid in the database log through the
``db_mark_invalid``/``db_is_invalid`` functions the database plugin injects into the items it logs.

Real items and a real plugin; the injected functions are replaced by :class:`GapRecorder`.
"""

import tempfile
import unittest

from tests.gap_recorder import GapRecorder
from tests.sdp_harness import PluginRig, load_plugin

ITEMS = """
dev:
    a:
        type: num
    b:
        type: num
    unlogged:
        type: num
"""


class TestDbInvalidateItems(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.rig: PluginRig = load_plugin(self._tmp.name, 'tests.fixture_pause_plugin', 'FixturePause', ITEMS)
        self.plugin = self.rig.plugin
        self.a, self.b, self.unlogged = (self.rig.item(f'dev.{name}') for name in ('a', 'b', 'unlogged'))
        self.gaps = {item: GapRecorder(item) for item in (self.a, self.b)}

    def test_logged_items_are_marked_with_plugin_name_and_source(self):
        self.plugin.db_invalidate_items([self.a, self.b], 'connection_lost')

        expected = [(self.plugin.get_fullname(), 'connection_lost')]
        self.assertEqual(expected, self.gaps[self.a].calls)
        self.assertEqual(expected, self.gaps[self.b].calls)

    def test_items_without_database_logging_are_skipped(self):
        self.plugin.db_invalidate_items([self.unlogged, self.a], 'lwt_offline')

        self.assertEqual(1, len(self.gaps[self.a].calls))

    def test_item_with_open_gap_is_not_marked_again(self):
        self.plugin.db_invalidate_items([self.a], 'lwt_offline')
        self.plugin.db_invalidate_items([self.a], 'timeout')

        self.assertEqual(1, len(self.gaps[self.a].calls))

    def test_item_is_marked_again_after_its_gap_was_closed(self):
        self.plugin.db_invalidate_items([self.a], 'lwt_offline')
        self.gaps[self.a].open_gap = False
        self.plugin.db_invalidate_items([self.a], 'timeout')

        self.assertEqual(2, len(self.gaps[self.a].calls))

    def test_accept_filter_excludes_items(self):
        self.plugin.db_invalidate_items([self.a, self.b], 'timeout', accept=lambda item: item is self.b)

        self.assertEqual([], self.gaps[self.a].calls)
        self.assertEqual(1, len(self.gaps[self.b].calls))

    def test_item_without_is_invalid_function_is_marked(self):
        self.b.db_mark_invalid = self.gaps[self.b].mark_invalid
        del self.b.db_is_invalid

        self.plugin.db_invalidate_items([self.b], 'timeout')

        self.assertEqual(1, len(self.gaps[self.b].calls))

    def test_any_iterable_of_items_is_accepted(self):
        self.plugin.db_invalidate_items((item for item in (self.a, self.b)), 'timeout')

        self.assertEqual(1, len(self.gaps[self.a].calls))
        self.assertEqual(1, len(self.gaps[self.b].calls))


if __name__ == '__main__':
    unittest.main(verbosity=2)
