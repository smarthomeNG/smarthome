#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.rename_item() (lib/item/items.py) — renames an item
in-place (same parent only, v1) by mutating its path, see
~/.claude/handoff/shng-rename-item-design.md for the full design.
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
import lib.plugin
from lib.item.items import Items
from tests.mock.core import MockSmartHome


class FakePlugin:
    """Minimal stand-in for a SmartPlugin implementing PLUGIN_RENAME_ITEM,
    for testing the rename_item() hook call-site without any real plugin
    machinery."""

    def __init__(self):
        self.renamed_items = []

    def rename_item(self, item, old_path, new_path):
        self.renamed_items.append((item, old_path, new_path))
        return True


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

    def removes(self):
        return [c for c in self.calls if c['action'] == 'remove']

    def added_names(self):
        return [c['name'] for c in self.adds()]


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None
    lib.plugin._plugins_instance = None
    lib.plugin.Plugins._plugins = []


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


class TestRenameItemCascadesToDescendants(_Base):
    def test_rename_updates_descendant_paths(self):
        parent = self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}}, persist=False
        )
        child = self.sh.items.return_item('old.child')
        grandchild = self.sh.items.return_item('old.child.grandchild')

        self.sh.items.rename_item(parent, 'new')

        self.assertEqual(child.property.path, 'new.child')
        self.assertEqual(grandchild.property.path, 'new.child.grandchild')
        self.assertIsNone(self.sh.items.return_item('old.child'))
        self.assertIsNone(self.sh.items.return_item('old.child.grandchild'))
        self.assertIs(self.sh.items.return_item('new.child'), child)
        self.assertIs(self.sh.items.return_item('new.child.grandchild'), grandchild)
        self.assertIs(child.return_parent(), parent)


class TestRenameItemRekeysScheduler(_Base):
    def setUp(self):
        super().setUp()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def test_rename_removes_old_job_and_adds_new(self):
        item = self.sh.items.create_item('cy', {'type': 'num', 'cycle': '30'}, persist=False)

        self.sh.items.rename_item(item, 'cynew')

        self.assertIn('items.cy', [c['name'] for c in self.recorder.removes()])
        self.assertIn('items.cynew', self.recorder.added_names())


class TestRenameItemPersists(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'

    def tearDown(self):
        _reset()

    def _read_file(self, filename):
        import lib.shyaml as shyaml

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        yf.load()
        return yf.data

    def test_rename_moves_the_yaml_node_to_the_new_path(self):
        item = self.sh.items.create_item('old', {'type': 'num', 'eval': '1', 'child': {'type': 'num'}}, persist=True)

        self.sh.items.rename_item(item, 'new')

        data = self._read_file('created')
        self.assertNotIn('old', data)
        self.assertEqual(data['new']['eval'], '1')
        self.assertIn('child', data['new'])


class TestRenameItemCallsPluginHook(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)

    def test_rename_calls_plugin_rename_item_hook_per_item_in_subtree(self):
        item = self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}}, persist=False)
        child = self.sh.items.return_item('old.child')

        self.sh.items.rename_item(item, 'new')

        self.assertIn((item, 'old', 'new'), self.fake_plugin.renamed_items)
        self.assertIn((child, 'old.child', 'new.child'), self.fake_plugin.renamed_items)
