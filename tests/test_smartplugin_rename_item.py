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


class TestRenameItemRespectsStopOnItemChange(unittest.TestCase):
    def test_pauses_and_resumes_when_stop_on_item_change_is_true(self):
        plugin = FakeSmartPlugin()
        plugin.STOP_ON_ITEM_CHANGE = True
        plugin.alive = True

        plugin.rename_item(None, 'old.path', 'new.path')

        self.assertTrue(plugin.alive)

    def test_does_not_touch_alive_state_when_stop_on_item_change_is_false(self):
        plugin = FakeSmartPlugin()
        plugin.STOP_ON_ITEM_CHANGE = False
        plugin.alive = True

        plugin.rename_item(None, 'old.path', 'new.path')

        self.assertTrue(plugin.alive)

    def test_does_not_resume_if_something_else_already_restarted_it(self):
        plugin = FakeSmartPlugin()
        plugin.STOP_ON_ITEM_CHANGE = True
        plugin.alive = True
        original_stop = plugin.stop

        def stop_and_get_restarted_by_someone_else():
            original_stop()
            plugin.alive = True  # simulate a concurrent restart during the pause window

        plugin.stop = stop_and_get_restarted_by_someone_else
        plugin.run = unittest.mock.Mock(side_effect=AssertionError('run() must not be called again'))

        plugin.rename_item(None, 'old.path', 'new.path')

        plugin.run.assert_not_called()
