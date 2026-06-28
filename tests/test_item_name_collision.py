#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for item-name collision detection at construction time (replaces the
old item.py _item_methods notice-only check and closes the gap where
runtime-created items had no protection at all against names that collide
with an existing attribute — see lib/item/_internal/_parsing.py
check_item_name_collision()).
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


class TestNameCollisionDropsByDefault(_Base):
    def test_colliding_nested_item_is_not_created(self):
        parent = self.sh.items.create_item('d', {'type': 'num'}, persist=False)

        child = self.sh.items.create_item('d.property', {'type': 'num'}, parent=parent, persist=False)

        self.assertIsNone(child)
        self.assertIsNone(self.sh.items.return_item('d.property'))
