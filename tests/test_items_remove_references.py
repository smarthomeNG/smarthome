#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.remove_references() (lib/item/items.py) — strips dangling
unambiguous references to a target item from every other item, building on
find_references() and edit_item().
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
import lib.shyaml as shyaml
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


class _PersistedBase(unittest.TestCase):
    """Items are persisted to a real tempdir file, mirroring TestEditItemPersists
    in test_item_edit.py — remove_references() needs a referencing item's
    on-disk config as the base for its rebuilt config."""

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
        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        yf.load()
        return yf.data


class TestRemoveReferencesStripsTriggerEntry(_PersistedBase):
    def test_remove_references_drops_target_from_trigger_list(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('source', {'type': 'num', 'eval': '2', 'trigger': ['target']}, persist=True)

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertIsNone(source._trigger)
        self.assertEqual(result, {'removed': [('source', ['trigger'])], 'skipped_ambiguous': []})


class TestRemoveReferencesClearsHysteresisInput(_PersistedBase):
    def test_remove_references_clears_hysteresis_input(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('source', {'type': 'num', 'eval': '2', 'hysteresis_input': 'target'}, persist=True)

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertIsNone(source._hysteresis_input)
        self.assertEqual(result, {'removed': [('source', ['hysteresis_input'])], 'skipped_ambiguous': []})


class TestRemoveReferencesClearsUnambiguousEval(_PersistedBase):
    def test_remove_references_clears_whole_eval_when_unambiguous(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.target() * 9 / 5 + 32'}, persist=True)

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertIsNone(source._eval)
        self.assertEqual(result, {'removed': [('source', ['eval'])], 'skipped_ambiguous': []})

    def test_remove_references_leaves_ambiguous_eval_untouched(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('other', {'type': 'num', 'eval': '2'}, persist=True)
        self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.target() + sh.other()'}, persist=True)

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertEqual(source._eval, 'sh.target() + sh.other()')
        self.assertEqual(result['removed'], [])
        self.assertEqual(result['skipped_ambiguous'], [('source', 'eval', 'sh.target() + sh.other()')])


class TestRemoveReferencesFiltersOnChangeList(_PersistedBase):
    def test_remove_references_drops_only_the_matching_on_change_entry(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('other', {'type': 'num', 'eval': '3'}, persist=True)
        self.sh.items.create_item(
            'source', {'type': 'num', 'on_change': ['sh.target() + 1', 'sh.other() + 2']}, persist=True
        )

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertEqual(source._on_change, ['sh.other() + 2'])
        self.assertEqual(result, {'removed': [('source', ['on_change'])], 'skipped_ambiguous': []})


class TestRemoveReferencesBatchesPerItem(_PersistedBase):
    def test_remove_references_combines_multiple_dangling_attrs_into_one_edit(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'trigger': ['target'], 'remark': 'keep me'}, persist=True
        )

        result = self.sh.items.remove_references('target')

        source = self.sh.items.return_item('source')
        self.assertIsNone(source._eval)
        self.assertIsNone(source._trigger)
        self.assertEqual(source.property.remark, 'keep me')
        self.assertEqual(result, {'removed': [('source', ['eval', 'trigger'])], 'skipped_ambiguous': []})


class TestRemoveReferencesPersists(_PersistedBase):
    def test_remove_references_persists_the_stripped_config(self):
        self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('source', {'type': 'num', 'trigger': ['target']}, persist=True)

        self.sh.items.remove_references('target')

        data = self._read_file('created')
        self.assertNotIn('trigger', data['source'])
