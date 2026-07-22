#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib.model.smartdeviceplugin.SmartDevicePlugin.remove_item():

_plg_item_dict and _items_write are keyed by item.property.path (a string)
everywhere they're populated (see SmartPlugin.add_item()/parse_item() and
SmartDevicePlugin.parse_item()), but remove_item() looked both up by the
Item object itself. Both lookups always missed (a KeyError caught into
cmd=None, and `item in self._items_write` always False), so the cleanup of
_commands_read/_commands_pseudo/_commands_initial/_commands_cyclic/
_commands_read_grp and _items_write silently never ran on item removal --
stale references accumulated indefinitely across item reload/reconfiguration.

Bypasses SmartDevicePlugin.__init__() (which needs a real device
connection) and seeds only the dict state remove_item() actually touches,
matching the exact shapes SmartPlugin.add_item()/SmartDevicePlugin.parse_item()
produce.
"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartdeviceplugin import SmartDevicePlugin
from tests.plugin_contract._mockitem import MockItem


def _make_plugin_with_item(item, cmd='SomeCommand'):
    plugin = SmartDevicePlugin.__new__(SmartDevicePlugin)
    plugin.logger = logging.getLogger('test.sdp_remove_item')
    plugin.alive = False
    plugin.STOP_ON_ITEM_CHANGE = False
    plugin._pause_item_path = ''
    plugin._suspend_item_path = ''

    # state SmartPlugin.add_item()/SDP.parse_item() would have produced for
    # an item registered for both read and write on `cmd`
    plugin._plg_item_dict = {
        item.property.path: {'item': item, 'mapping': cmd, 'config_data': {}, 'is_updating': False}
    }
    plugin._item_lookup_dict = {cmd: [item]}
    plugin._items_write = {item.property.path: cmd}
    plugin._items_read_grp = {}
    plugin._items_custom = {}
    plugin._items_read_all = []
    plugin._commands_read = {cmd: [item]}
    plugin._commands_pseudo = {}
    plugin._commands_initial = []
    plugin._commands_cyclic = {}
    plugin._commands_read_grp = {}
    return plugin


class TestSmartDevicePluginRemoveItem(unittest.TestCase):
    def test_remove_item_returns_true(self):
        item = MockItem('sdp.remove.a')
        plugin = _make_plugin_with_item(item)
        self.assertTrue(plugin.remove_item(item))

    def test_remove_item_cleans_up_items_write(self):
        item = MockItem('sdp.remove.b')
        plugin = _make_plugin_with_item(item)
        plugin.remove_item(item)
        self.assertNotIn(item.property.path, plugin._items_write)

    def test_remove_item_cleans_up_commands_read(self):
        item = MockItem('sdp.remove.c')
        cmd = 'SomeCommand'
        plugin = _make_plugin_with_item(item, cmd=cmd)
        plugin.remove_item(item)
        self.assertNotIn(item, plugin._commands_read[cmd])

    def test_remove_item_twice_second_call_returns_false(self):
        # _plg_item_dict entry is deleted by the first call (base class
        # behaviour); the item is no longer known to the plugin at all
        item = MockItem('sdp.remove.d')
        plugin = _make_plugin_with_item(item)
        self.assertTrue(plugin.remove_item(item))
        self.assertFalse(plugin.remove_item(item))


if __name__ == '__main__':
    unittest.main(verbosity=2)
