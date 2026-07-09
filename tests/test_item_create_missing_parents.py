#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.create_item()'s path-based parent resolution and the
create_missing_parents flag (lib/item/items.py).

Coverage
--------
- parent=None with a dotted path resolves the parent by path (previously
  unsupported — a direct create_item() call with a dotted path and no
  explicit parent object used to silently misconstruct a broken top-level
  item; it now behaves the same as the admin API's own resolution did).
- Missing parent, flag off: raises ValueError, nothing is created.
- Missing parent, flag on: the whole missing ancestor chain is created (in
  order, shallow to deep) as empty items, then the requested item itself
  with its real config.
- A partially-existing chain only creates the missing segments.
- Auto-created ancestors share persist/filename with the requested item.
- A name collision on an auto-created ancestor raises ValueError naming
  that ancestor specifically, not the originally requested path.
"""

import os
import sys
import tempfile
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
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'

    def tearDown(self):
        _reset()


class TestMissingParentFlagOff(_Base):
    def test_raises_without_creating_anything(self):
        with self.assertRaises(ValueError):
            self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False)

        self.assertIsNone(self.sh.items.return_item('a'))
        self.assertIsNone(self.sh.items.return_item('a.b'))
        self.assertIsNone(self.sh.items.return_item('a.b.c'))

    def test_error_names_the_missing_parent(self):
        with self.assertRaises(ValueError) as ctx:
            self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False)

        self.assertIn('a.b', str(ctx.exception))


class TestMissingParentFlagOn(_Base):
    def test_creates_the_whole_missing_chain(self):
        leaf = self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False, create_missing_parents=True)

        self.assertIsNotNone(self.sh.items.return_item('a'))
        self.assertIsNotNone(self.sh.items.return_item('a.b'))
        self.assertIs(self.sh.items.return_item('a.b.c'), leaf)

    def test_auto_created_ancestors_are_empty_items(self):
        self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False, create_missing_parents=True)

        ancestor = self.sh.items.return_item('a.b')
        # An untyped item defaults to type 'foo' internally (Item.__init__) —
        # confirms it was created with an empty config, not copying the
        # leaf's config.
        self.assertEqual(ancestor.type(), 'foo')

    def test_leaf_keeps_its_own_requested_config(self):
        leaf = self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False, create_missing_parents=True)

        self.assertEqual(leaf.type(), 'num')

    def test_only_creates_the_segments_that_are_actually_missing(self):
        existing_a = self.sh.items.create_item('a', {'type': 'num'}, persist=False)

        leaf = self.sh.items.create_item('a.b.c', {'type': 'num'}, persist=False, create_missing_parents=True)

        self.assertIs(self.sh.items.return_item('a'), existing_a)
        self.assertIsNotNone(self.sh.items.return_item('a.b'))
        self.assertIs(self.sh.items.return_item('a.b.c'), leaf)

    def test_auto_created_ancestors_persist_to_the_same_file_as_the_leaf(self):
        self.sh.items.create_item(
            'a.b.c', {'type': 'num'}, persist=True, filename='mychain', create_missing_parents=True
        )

        self.assertEqual(self.sh.items.return_item('a')._filename, 'mychain')
        self.assertEqual(self.sh.items.return_item('a.b')._filename, 'mychain')
        self.assertEqual(self.sh.items.return_item('a.b.c')._filename, 'mychain')

    def test_collision_on_an_auto_created_ancestor_raises_and_names_that_ancestor(self):
        with self.assertRaises(ValueError) as ctx:
            self.sh.items.create_item('scheduler.b.c', {'type': 'num'}, persist=False, create_missing_parents=True)

        self.assertIn('scheduler', str(ctx.exception))
        self.assertIsNone(self.sh.items.return_item('scheduler.b'))
        self.assertIsNone(self.sh.items.return_item('scheduler.b.c'))


class TestExplicitParentStillWorksUnchanged(_Base):
    def test_explicit_parent_object_bypasses_path_resolution_entirely(self):
        parent = self.sh.items.create_item('existing', {'type': 'num'}, persist=False)

        child = self.sh.items.create_item('existing.child', {'type': 'num'}, parent=parent, persist=False)

        self.assertIsNotNone(child)
        self.assertIs(self.sh.items.return_item('existing.child'), child)
