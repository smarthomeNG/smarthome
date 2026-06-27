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


class TestEditItemPreservesIncomingReferences(_Base):
    def test_edit_item_keeps_other_items_triggering_on_it(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )
        self.assertIn(source, target.get_item_triggers())

        self.sh.items.edit_item(target, {'type': 'num', 'eval': '1', 'remark': 'edited'})

        self.assertIn(source, target.get_item_triggers())


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
