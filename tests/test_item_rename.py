#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.rename_item() (lib/item/items.py) — renames an item
in-place (same parent only, v1) by mutating its path, see
~/.claude/handoff/shng-rename-item-design.md for the full design.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from tests.mock.core import MockSmartHome


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = MockSmartHome()

    def tearDown(self):
        _reset()


class TestRenameItemBasic(_Base):
    def test_rename_updates_item_path_and_item_dict(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        renamed = self.sh.items.rename_item(item, 'new')

        self.assertIs(renamed, item)
        self.assertEqual(item.property.path, 'new')
        self.assertIsNone(self.sh.items.return_item('old'))
        self.assertIs(self.sh.items.return_item('new'), item)


class TestRenameItemValidatesNewName(_Base):
    def test_rename_refuses_colliding_name(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)
        self.sh.items.create_item('scheduler_clash', {'type': 'num'}, persist=False)

        with self.assertRaises(ValueError):
            self.sh.items.rename_item(item, 'scheduler')

        self.assertEqual(item.property.path, 'old')
        self.assertIsNotNone(self.sh.items.return_item('old'))

    def test_rename_to_same_path_is_a_silent_no_op(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        renamed = self.sh.items.rename_item(item, 'old')

        self.assertIs(renamed, item)
        self.assertEqual(item.property.path, 'old')
