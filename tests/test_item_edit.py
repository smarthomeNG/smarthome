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


class FakePlugin:
    """Minimal stand-in for a SmartPlugin implementing PLUGIN_REMOVE_ITEM/
    PLUGIN_PARSE_ITEM, for testing the plugin remove/parse bracket in
    Items.edit_item() without any real plugin machinery."""

    def __init__(self):
        self.removed_items = []
        self.parsed_items = []

    def remove_item(self, item):
        self.removed_items.append(item)
        return True

    def parse_item(self, item):
        self.parsed_items.append(item)
        return None


def _make_sh():
    _reset()
    return MockSmartHome()


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


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

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


class TestEditItemAllowsIncomingStructuralReferences(_Base):
    def test_edit_item_type_change_with_live_incoming_trigger_is_safe(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )
        self.assertIn(source, target.get_item_triggers())

        self.sh.items.edit_item(target, {'type': 'str'})

        self.assertIn(source, target.get_item_triggers())

    def test_edit_item_succeeds_when_item_is_a_trigger_target(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )
        self.assertIn(source, target.get_item_triggers())

        self.sh.items.edit_item(target, {'type': 'num', 'eval': '1', 'remark': 'edited'})

        self.assertEqual(target.property.remark, 'edited')
        self.assertIn(source, target.get_item_triggers())

    def test_edit_item_allows_plain_eval_reference_with_no_trigger(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.target()'}, persist=False)

        self.sh.items.edit_item(target, {'type': 'num', 'eval': '1', 'remark': 'edited'})


class TestEditItemRewiresOwnOutgoingTriggers(_Base):
    def test_edit_item_moving_its_own_trigger_rewires_correctly(self):
        target_a = self.sh.items.create_item('target_a', {'type': 'num', 'eval': '1'}, persist=False)
        target_b = self.sh.items.create_item('target_b', {'type': 'num', 'eval': '2'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target_a()', 'eval_trigger': 'target_a'}, persist=False
        )
        self.assertIn(source, target_a.get_item_triggers())
        self.assertNotIn(source, target_b.get_item_triggers())

        self.sh.items.edit_item(source, {'type': 'num', 'eval': 'sh.target_b()', 'eval_trigger': 'target_b'})

        self.assertNotIn(source, target_a.get_item_triggers())
        self.assertIn(source, target_b.get_item_triggers())


class TestEditItemRewiresScheduler(_Base):
    def test_edit_item_changing_cycle_removes_old_job_and_adds_new(self):
        item = self.sh.items.create_item('cy', {'type': 'num', 'cycle': '30'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'cycle': '60'})

        self.assertIn('items.cy', [c['name'] for c in self.recorder.removes()])
        cycle_adds = [c for c in self.recorder.adds() if c['name'] == 'items.cy']
        self.assertEqual(cycle_adds[-1]['cycle'], 60)


class TestEditItemRebindsPlugins(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)

    def test_edit_item_calls_plugin_remove_then_parse(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        self.assertIn(item, self.fake_plugin.parsed_items)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertIn(item, self.fake_plugin.removed_items)
        self.assertEqual(self.fake_plugin.parsed_items.count(item), 2)


class TestEditItemPersists(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()

    def _read_file(self, filename):
        import lib.shyaml as shyaml

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        yf.load()
        return yf.data

    def test_edit_item_persists_new_config_to_its_existing_file(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)

        self.sh.items.edit_item(item, {'type': 'num', 'eval': '2'})

        data = self._read_file('created')
        self.assertEqual(data['target']['eval'], '2')

    def test_edit_item_omitted_attribute_is_removed_from_file(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'eval': '1', 'remark': 'old'}, persist=True)

        self.sh.items.edit_item(item, {'type': 'num', 'eval': '1'})

        data = self._read_file('created')
        self.assertNotIn('remark', data['target'])

    def test_edit_item_preserves_childs_yaml_entry(self):
        self.sh.items.create_item('parent', {'type': 'num', 'eval': '1', 'child': {'type': 'str'}}, persist=True)
        parent = self.sh.items.return_item('parent')

        self.sh.items.edit_item(parent, {'type': 'num', 'eval': '2'})

        data = self._read_file('created')
        self.assertIn('child', data['parent'])
        self.assertEqual(data['parent']['child']['type'], 'str')
