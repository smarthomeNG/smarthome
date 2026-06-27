#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for editing an existing item's attributes at runtime (lib/item/items.py
Items.edit_item()).

Coverage
--------
TODO: filled in incrementally, test by test.
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


def _make_sh():
    _reset()
    return MockSmartHome()


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


class TestEditItemPreservesIdentity(_Base):
    def test_edit_item_returns_the_same_object(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        edited = self.sh.items.edit_item(item, {'type': 'num'})

        self.assertIs(edited, item)

    def test_edit_item_updates_a_generic_attribute(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'my_custom_attr': 'old'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'my_custom_attr': 'new'})

        self.assertEqual(item.conf['my_custom_attr'], 'new')


class TestEditItemPreservesValueAndHistory(_Base):
    def test_edit_item_preserves_current_value(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(item(), 5)

    def test_edit_item_preserves_history(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')
        prev_value_before = item.prev_value()

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(item.prev_value(), prev_value_before)


class TestEditItemTypeChange(_Base):
    def test_edit_item_casts_preserved_value_to_new_type(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')

        self.sh.items.edit_item(item, {'type': 'str'})

        self.assertEqual(item(), '5')

    def test_edit_item_falls_back_to_type_default_when_cast_fails(self):
        item = self.sh.items.create_item('target', {'type': 'str'}, persist=False)
        item('not a number', caller='test')

        self.sh.items.edit_item(item, {'type': 'num'})

        self.assertEqual(item(), 0)
