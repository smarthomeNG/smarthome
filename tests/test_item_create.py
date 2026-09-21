#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for item creation at runtime (lib/item/items.py).

Coverage
--------
create_item():
  top-level item is registered (Items.return_item, items_instance/sh
  attribute binding, Items._children)
  init phases ran (_init_start_scheduler, _init_prerun) for the new item
  nested item under an existing parent (no sh binding, not in
  Items._children, but registered and findable)
  nested config (grandchildren) are created and fully initialized too
  a 'struct' attribute (top-level or in a nested child config) is
  expanded, and the persisted yaml keeps the struct reference unexpanded
"""

import collections
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.shyaml as shyaml
from lib.constants import YAML_FILE
from lib.item.items import Items
from lib.item.structs import Structs
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
    Structs._struct_definitions = collections.OrderedDict()
    Structs._finalized_structs = []


def _make_sh():
    _reset()
    return MockSmartHome()


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh, path, c)
    sh.items.add_item(path, i)
    return i


class RecordingScheduler:
    """Drop-in replacement for MockScheduler that records calls."""

    def __init__(self):
        self.calls = []

    def add(self, name, obj=None, prio=3, cron=None, cycle=None, value=None, offset=None, next=None, items=None):
        self.calls.append({'action': 'add', 'name': name, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next})

    def remove(self, name):
        self.calls.append({'action': 'remove', 'name': name})

    def adds(self):
        return [c for c in self.calls if c['action'] == 'add']

    def added_names(self):
        return [c['name'] for c in self.adds()]


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()


class TestCreateItemToplevel(_Base):
    def test_create_item_is_findable_by_path(self):
        self.sh.items.create_item('new', {'type': 'num'}, persist=False)

        self.assertIsNotNone(self.sh.items.return_item('new'))

    def test_create_item_sets_sh_and_items_attribute(self):
        item = self.sh.items.create_item('new', {'type': 'num'}, persist=False)

        self.assertIs(self.sh.items.new, item)
        self.assertIs(self.sh.new, item)

    def test_create_item_appears_in_toplevel_children(self):
        item = self.sh.items.create_item('new', {'type': 'num'}, persist=False)

        self.assertIn(item, self.sh.items._children)


class TestCreateItemRunsInitPhases(_Base):
    def test_cycle_attribute_registers_scheduler_job(self):
        self.sh.items.create_item('cy', {'type': 'num', 'cycle': '30'}, persist=False)

        self.assertIn('items.cy', self.recorder.added_names())

    def test_eval_trigger_wires_into_existing_items_to_trigger(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)

        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )

        self.assertIn(source, target.get_item_triggers())


class TestCreateItemUnderExistingParent(_Base):
    def test_nested_item_appears_in_parent_children_not_toplevel(self):
        parent = self.sh.items.create_item('parent', {'type': 'num'}, persist=False)

        child = self.sh.items.create_item('parent.child', {'type': 'num'}, parent=parent, persist=False)

        self.assertIn(child, parent.return_children())
        self.assertNotIn(child, self.sh.items._children)

    def test_nested_item_has_no_sh_attribute_but_is_findable(self):
        parent = self.sh.items.create_item('parent', {'type': 'num'}, persist=False)

        self.sh.items.create_item('parent.child', {'type': 'num'}, parent=parent, persist=False)

        self.assertFalse(hasattr(self.sh, 'parent.child'))
        self.assertIsNotNone(self.sh.items.return_item('parent.child'))


class TestCreateItemWithNestedConfig(_Base):
    def test_grandchild_from_nested_config_is_findable_and_initialized(self):
        self.sh.items.create_item('top', {'type': 'num', 'sub': {'type': 'num', 'cycle': '30'}}, persist=False)

        grandchild = self.sh.items.return_item('top.sub')

        self.assertIsNotNone(grandchild)
        self.assertIn('items.top.sub', self.recorder.added_names())


def _register_widget_struct(sh):
    """A struct with a top-level attribute and a nested child item, for the struct-expansion tests below."""
    struct = collections.OrderedDict({'type': 'num', 'sub': collections.OrderedDict({'type': 'bool'})})
    sh.items.structs.add_struct_definition('', 'test.widget', struct)


class TestCreateItemStructExpansion(_Base):
    def test_toplevel_struct_attribute_is_expanded(self):
        _register_widget_struct(self.sh)

        item = self.sh.items.create_item('x', {'struct': 'test.widget'}, persist=False)

        self.assertEqual(item.type(), 'num')
        sub = self.sh.items.return_item('x.sub')
        self.assertIsNotNone(sub)
        self.assertEqual(sub.type(), 'bool')

    def test_struct_attribute_on_nested_child_config_is_expanded(self):
        _register_widget_struct(self.sh)

        self.sh.items.create_item('top', {'type': 'num', 'child': {'struct': 'test.widget'}}, persist=False)

        child = self.sh.items.return_item('top.child')
        grandchild = self.sh.items.return_item('top.child.sub')
        self.assertIsNotNone(child)
        self.assertEqual(child.type(), 'num')
        self.assertIsNotNone(grandchild)
        self.assertEqual(grandchild.type(), 'bool')

    def test_config_without_struct_keeps_attribute_value_types(self):
        # no 'struct' anywhere must skip the stringifying expansion machinery entirely
        item = self.sh.items.create_item('plain', {'type': 'bool', 'custom_flag': True}, persist=False)

        self.assertIs(item.conf['custom_flag'], True)


class TestCreateItemStructPersistence(_Base):
    def setUp(self):
        super().setUp()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'

    def test_persisted_yaml_keeps_struct_reference_unexpanded(self):
        _register_widget_struct(self.sh)

        self.sh.items.create_item('x', {'struct': 'test.widget'})

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, 'created' + YAML_FILE))
        yf.load()
        data = yf.data
        self.assertEqual(data['x']['struct'], 'test.widget')
        # struct content must stay unexpanded on disk - only the live Item gets it
        self.assertNotIn('sub', data['x'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
