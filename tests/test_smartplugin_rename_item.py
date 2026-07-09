#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartPlugin.rename_item() (lib/model/smartplugin.py) — the
base-class default implementation of the PLUGIN_RENAME_ITEM hook. Re-keys
_plg_item_dict/_pause_item_path, respecting STOP_ON_ITEM_CHANGE. See
~/.claude/handoff/shng-rename-item-design.md.
"""

import os
import sys
import unittest
import unittest.mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartplugin import SmartPlugin


class FakeSmartPlugin(SmartPlugin):
    """Minimal concrete SmartPlugin subclass — run()/stop() are abstract
    on the base class (raise NotImplementedError), so any direct test of
    SmartPlugin's own methods needs a trivial override."""

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False


class TestRenameItemDefault(unittest.TestCase):
    def setUp(self):
        self.plugin = FakeSmartPlugin()

    def test_rekeys_plg_item_dict_entry(self):
        self.plugin._plg_item_dict['old.path'] = {'item': 'fake', 'is_updating': False}

        self.plugin.rename_item(None, 'old.path', 'new.path')

        self.assertNotIn('old.path', self.plugin._plg_item_dict)
        self.assertEqual(self.plugin._plg_item_dict['new.path'], {'item': 'fake', 'is_updating': False})

    def test_does_nothing_if_item_not_tracked(self):
        self.plugin.rename_item(None, 'old.path', 'new.path')

        self.assertEqual(self.plugin._plg_item_dict, {})

    def test_updates_pause_item_path_if_it_matches(self):
        self.plugin._pause_item_path = 'old.path'

        self.plugin.rename_item(None, 'old.path', 'new.path')

        self.assertEqual(self.plugin._pause_item_path, 'new.path')


class TestRenameItemDoesNotPauseTheCallingPlugin(unittest.TestCase):
    """
    SmartPlugin.rename_item() itself never touches alive/stop()/run() —
    Items.rename_item() (lib/item/items.py) is responsible for pausing
    and resuming each affected plugin, once for the whole rename
    operation rather than once per descendant, since stop()/run() can be
    expensive (e.g. reconnecting to real hardware/network) and a renamed
    subtree may have many descendants. See
    TestRenameItemPausesEachAffectedPluginOnceForTheWholeOperation in
    test_item_rename.py for that batching behavior.
    """

    def test_does_not_call_stop_or_run_regardless_of_stop_on_item_change(self):
        plugin = FakeSmartPlugin()
        plugin.STOP_ON_ITEM_CHANGE = True
        plugin.alive = True
        plugin.stop = unittest.mock.Mock(side_effect=AssertionError('stop() must not be called'))
        plugin.run = unittest.mock.Mock(side_effect=AssertionError('run() must not be called'))

        plugin.rename_item(None, 'old.path', 'new.path')

        plugin.stop.assert_not_called()
        plugin.run.assert_not_called()
