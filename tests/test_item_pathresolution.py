#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Item path resolution (lib/item/item.py)

Planned extraction target: lib/item/_pathresolution.py

The existing test_item.py::test_item_relative_references covers get_absolutepath,
get_stringwithabsolutepathes and expand_relativepathes thoroughly.  This file
covers the parts that have zero coverage:

  find_attribute(attr, default, level, strict)
    - attribute on self, parent, grandparent
    - level cap limits search depth
    - strict=True returns '' when exact level not reached
    - default returned when attribute not found anywhere

  return_parent(level, strict)
    - level 1 = immediate parent
    - level 2 = grandparent
    - top-level item returns Items instance (not another Item)
    - strict past tree depth returns None

  _is_top_of_item_tree()
    - True for root, False for child

  return_children()
    - yields child items, empty for leaf

  get_children_path()
    - returns list of child paths

  get_attr_time(attr)
    - integer string → seconds
    - duration string '5m' → 300

  get_attr_value(attr, value)
    - returns config attribute value when present
"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.config
from lib.item.items import Items
from lib.model.smartplugin import SmartPlugin
from tests.mock.core import MockSmartHome
import tests.common as common


def _make_plugin(instance=''):
    """Minimal real SmartPlugin instance (bypasses __init__'s heavier sh/config
    plumbing, irrelevant here) - has_iattr()/get_iattr_value() are the real,
    unmocked implementations, only _SmartPlugin__instance is set directly the
    way _set_instance_name() actually sets it."""
    plugin = SmartPlugin.__new__(SmartPlugin)
    plugin._SmartPlugin__instance = instance
    return plugin


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _make_sh():
    _reset()
    return MockSmartHome()


def _load_items(sh, filename):
    """Load items from tests/resources/<filename>.yaml into sh.items registry.

    Uses sh.items (the Items instance) as the parent for top-level items so that
    _is_top_of_item_tree() returns True for root items — matching production behaviour.
    """
    path = os.path.join(common.BASE, 'tests', 'resources', filename + '.yaml')
    conf = lib.config.parse(path, None)
    for attr, value in conf.items():
        if isinstance(value, dict):
            child = lib.item.item.Item(sh, sh.items, attr, value)
            sh.items.add_item(attr, child)
            vars(sh)[attr] = child
    return conf


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        _load_items(self.sh, 'item_tree')

    def tearDown(self):
        _reset()


# ===========================================================================
# find_attribute
# ===========================================================================


class TestFindAttribute(_Base):
    def test_finds_attr_on_self(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertEqual(lamp.find_attribute('lamp_attr'), 'ceiling')

    def test_finds_attr_on_parent_when_not_on_self(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        # room_attr is on 'room', not on 'lamp'
        self.assertEqual(lamp.find_attribute('room_attr'), 'kitchen')

    def test_finds_attr_on_grandparent(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        # zone_attr is on 'zone', two levels up from lamp
        self.assertEqual(lamp.find_attribute('zone_attr'), 'living')

    def test_returns_default_when_not_found(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertEqual(lamp.find_attribute('nonexistent_attr', default='fallback'), 'fallback')

    def test_default_is_empty_string_when_not_found(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertEqual(lamp.find_attribute('nonexistent_attr'), '')

    def test_level_0_only_checks_self(self):
        # level=0 is the item itself: finds lamp_attr, not room_attr
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertEqual(lamp.find_attribute('lamp_attr', level=0), 'ceiling')

    def test_level_cap_stops_search(self):
        # dimmer is 3 levels below zone; level=1 only reaches lamp
        dimmer = self.sh.items.return_item('zone.room.lamp.dimmer')
        # zone_attr is 3 hops up; level=1 should not find it
        result = dimmer.find_attribute('zone_attr', level=1)
        self.assertEqual(result, '')

    def test_strict_returns_empty_when_level_not_reached(self):
        # strict=True: must find attr at exactly level=2 hops up
        # dimmer at level=2 from zone has room not zone
        dimmer = self.sh.items.return_item('zone.room.lamp.dimmer')
        result = dimmer.find_attribute('zone_attr', level=2, strict=True)
        self.assertEqual(result, '')

    def test_nearest_wins_when_multiple_levels_have_attr(self):
        # Both zone and room have 'shared_attr' — room is closer to lamp
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertEqual(lamp.find_attribute('shared_attr'), 'from_room')

    def test_root_item_finds_own_attr(self):
        zone = self.sh.items.return_item('zone')
        self.assertEqual(zone.find_attribute('zone_attr'), 'living')

    def test_root_item_missing_attr_returns_default(self):
        zone = self.sh.items.return_item('zone')
        self.assertEqual(zone.find_attribute('no_such_attr', default='x'), 'x')


# ===========================================================================
# find_attribute_with_instance
# ===========================================================================


class TestFindAttributeWithInstance(_Base):
    def test_plugin_none_behaves_exactly_like_find_attribute(self):
        lamp = self.sh.items.return_item('inst_room.inst_lamp')
        self.assertEqual(
            lamp.find_attribute_with_instance('inst_attr', default='x'), lamp.find_attribute('inst_attr', default='x')
        )
        self.assertEqual(lamp.find_attribute_with_instance('inst_attr', default='x'), 'from_room_default')

    def test_named_instance_resolves_its_own_suffixed_attr(self):
        lamp = self.sh.items.return_item('inst_room.inst_lamp')
        home = _make_plugin('home')
        shop = _make_plugin('shop')

        self.assertEqual(lamp.find_attribute_with_instance('inst_attr', plugin=home), 'from_room_home')
        self.assertEqual(lamp.find_attribute_with_instance('inst_attr', plugin=shop), 'from_room_shop')

    def test_bare_attr_is_invisible_to_a_named_instance(self):
        """A bare attr (meant for the default/unnamed instance) must not leak
        into a named instance's resolution - inst_lamp itself has no
        inst_attr@other anywhere in its ancestor chain, only the bare
        default one."""
        lamp = self.sh.items.return_item('inst_room.inst_lamp')
        other = _make_plugin('other')

        self.assertEqual(lamp.find_attribute_with_instance('inst_attr', default='fallback', plugin=other), 'fallback')

    def test_wildcard_resolves_for_any_named_instance(self):
        lamp = self.sh.items.return_item('inst_room.inst_lamp')
        other = _make_plugin('other')

        self.assertEqual(lamp.find_attribute_with_instance('wild_attr', plugin=other), 'from_room_wild')

    def test_child_override_wins_over_ancestor_for_the_same_instance(self):
        override = self.sh.items.return_item('inst_room.inst_lamp.inst_override')
        home = _make_plugin('home')

        self.assertEqual(override.find_attribute_with_instance('inst_attr', plugin=home), 'from_override_home')

    def test_child_override_does_not_affect_other_instances(self):
        """inst_override only sets inst_attr@home - a shop-instance lookup on
        the same item must still fall through to the ancestor's inst_attr@shop,
        not be shadowed by the unrelated override."""
        override = self.sh.items.return_item('inst_room.inst_lamp.inst_override')
        shop = _make_plugin('shop')

        self.assertEqual(override.find_attribute_with_instance('inst_attr', plugin=shop), 'from_room_shop')


# ===========================================================================
# return_parent
# ===========================================================================


class TestReturnParent(_Base):
    def test_return_parent_level_1(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        parent = lamp.return_parent()
        self.assertEqual(parent._path, 'zone.room')

    def test_return_parent_level_2(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        grandparent = lamp.return_parent(level=2)
        self.assertEqual(grandparent._path, 'zone')

    def test_return_parent_from_root_is_items_instance(self):
        # Top-level item's parent is the Items instance, not another Item
        zone = self.sh.items.return_item('zone')
        parent = zone.return_parent()
        self.assertIsInstance(parent, Items)

    def test_return_parent_strict_past_root_returns_none_or_empty(self):
        zone = self.sh.items.return_item('zone')
        # Asking for level=2 from a root item goes past the top
        result = zone.return_parent(level=2, strict=True)
        # Strict=True and can't reach requested depth: returns '' or None
        self.assertFalse(result)


# ===========================================================================
# _is_top_of_item_tree
# ===========================================================================


class TestIsTopOfTree(_Base):
    def test_root_item_is_top(self):
        zone = self.sh.items.return_item('zone')
        self.assertTrue(zone._is_top_of_item_tree())

    def test_child_item_is_not_top(self):
        lamp = self.sh.items.return_item('zone.room.lamp')
        self.assertFalse(lamp._is_top_of_item_tree())

    def test_second_level_is_not_top(self):
        room = self.sh.items.return_item('zone.room')
        self.assertFalse(room._is_top_of_item_tree())


# ===========================================================================
# return_children
# ===========================================================================


class TestReturnChildren(_Base):
    def test_root_item_yields_children(self):
        zone = self.sh.items.return_item('zone')
        children = list(zone.return_children())
        paths = {c._path for c in children}
        self.assertIn('zone.room', paths)

    def test_leaf_item_yields_nothing(self):
        orphan = self.sh.items.return_item('orphan')
        children = list(orphan.return_children())
        self.assertEqual(children, [])

    def test_mid_item_yields_direct_children_only(self):
        room = self.sh.items.return_item('zone.room')
        children = list(room.return_children())
        paths = [c._path for c in children]
        # room has 'lamp' as direct child — not dimmer (grandchild)
        self.assertIn('zone.room.lamp', paths)
        self.assertNotIn('zone.room.lamp.dimmer', paths)


# ===========================================================================
# get_children_path
# ===========================================================================


class TestGetChildrenPath(_Base):
    def test_returns_list_of_strings(self):
        zone = self.sh.items.return_item('zone')
        paths = zone.get_children_path()
        self.assertIsInstance(paths, list)
        for p in paths:
            self.assertIsInstance(p, str)

    def test_contains_direct_child_paths(self):
        zone = self.sh.items.return_item('zone')
        paths = zone.get_children_path()
        self.assertIn('zone.room', paths)

    def test_leaf_returns_empty(self):
        orphan = self.sh.items.return_item('orphan')
        self.assertEqual(orphan.get_children_path(), [])


# ===========================================================================
# get_attr_time
# ===========================================================================


class TestGetAttrTime(_Base):
    def test_integer_string_returns_seconds(self):
        item = lib.item.item.Item(self.sh, self.sh, 'ti', {'type': 'num', 'cycle': '60'})
        self.sh.items.add_item('ti', item)
        result = item.get_attr_time('cycle')
        self.assertEqual(result, 60)

    def test_duration_minutes_string(self):
        item = lib.item.item.Item(self.sh, self.sh, 'ta', {'type': 'num', 'autotimer': '5m = 42'})
        self.sh.items.add_item('ta', item)
        result = item.get_attr_time('autotimer')
        self.assertEqual(result, 300)

    def test_duration_seconds_string(self):
        item = lib.item.item.Item(self.sh, self.sh, 'ts', {'type': 'num', 'autotimer': '30s = 0'})
        self.sh.items.add_item('ts', item)
        result = item.get_attr_time('autotimer')
        self.assertEqual(result, 30)

    def test_missing_attr_returns_none(self):
        item = lib.item.item.Item(self.sh, self.sh, 'tm', {'type': 'num'})
        self.sh.items.add_item('tm', item)
        result = item.get_attr_time('autotimer')
        self.assertIsNone(result)


# ===========================================================================
# get_attr_value
# ===========================================================================


class TestGetAttrValue(_Base):
    def test_returns_attr_value_from_config(self):
        item = lib.item.item.Item(self.sh, self.sh, 'av', {'type': 'num', 'cycle': '60 = 99'})
        self.sh.items.add_item('av', item)
        result = item.get_attr_value('cycle')
        # cycle with value '60 = 99' → get_attr_value returns '99'
        self.assertEqual(str(result), '99')

    def test_returns_none_when_no_value_in_duration_str(self):
        item = lib.item.item.Item(self.sh, self.sh, 'av2', {'type': 'num', 'cycle': '60'})
        self.sh.items.add_item('av2', item)
        result = item.get_attr_value('cycle')
        # cycle without value part → value is ''
        self.assertIn(result, [None, ''])


if __name__ == '__main__':
    unittest.main()
