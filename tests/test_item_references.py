#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.find_references() — best-effort text search for an item
path inside other items' eval/on_change/on_update/trigger/hysteresis_input
attributes (lib/item/items.py).

This is the "Fall B" helper from ENTWICKLUNGSRICHTLINIEN.md: it gives no
guarantee, it's a review aid for a human deciding whether to delete an
item, not a safety mechanism.
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


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh, path, c)
    sh.items.add_item(path, i)
    return i


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


class TestFindReferencesEval(_Base):
    def test_eval_reference_is_found(self):
        _item(self.sh, 'a')
        source = _item(self.sh, 'b', eval='sh.a()')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'eval', 'sh.a()', True), refs)

    def test_no_match_returns_empty_list(self):
        _item(self.sh, 'a')
        _item(self.sh, 'b', eval='1')

        refs = self.sh.items.find_references('a')

        self.assertEqual(refs, [])

    def test_word_boundary_avoids_partial_name_collision(self):
        """Searching for 'a.b' must not match an eval referencing 'a.bb'."""
        _item(self.sh, 'a.bb', eval='1')

        refs = self.sh.items.find_references('a.b')

        self.assertEqual(refs, [])

    def test_target_items_own_eval_is_not_reported_against_itself(self):
        target = _item(self.sh, 'a', eval='sh.a()')

        refs = self.sh.items.find_references('a')

        self.assertEqual(refs, [])
        self.assertIsNotNone(target)

    def test_arithmetic_around_single_reference_is_unambiguous(self):
        _item(self.sh, 'd.aussentemperatur')
        source = _item(self.sh, 'd.aussentemperatur.fahrenheit', eval='sh.d.aussentemperatur()*9/5+32')

        refs = self.sh.items.find_references('d.aussentemperatur')

        self.assertIn((source, 'eval', 'sh.d.aussentemperatur()*9/5+32', True), refs)

    def test_property_access_without_call_resolves_to_item(self):
        _item(self.sh, 'a.b')
        source = _item(self.sh, 'c', eval='sh.a.b.last_change')

        refs = self.sh.items.find_references('a.b')

        self.assertIn((source, 'eval', 'sh.a.b.last_change', True), refs)

    def test_two_distinct_references_is_ambiguous(self):
        _item(self.sh, 'a')
        _item(self.sh, 'b')
        source = _item(self.sh, 'c', eval='sh.a() + sh.b()')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'eval', 'sh.a() + sh.b()', False), refs)


class TestFindReferencesOnChangeOnUpdate(_Base):
    def test_on_change_reference_is_found(self):
        target = _item(self.sh, 'a')
        source = _item(self.sh, 'b', on_change='sh.a(1)')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'on_change', 'sh.a(1)', True), refs)
        self.assertIsNotNone(target)

    def test_on_update_reference_is_found(self):
        target = _item(self.sh, 'a')
        source = _item(self.sh, 'b', on_update='sh.a(1)')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'on_update', 'sh.a(1)', True), refs)
        self.assertIsNotNone(target)

    def test_on_change_with_second_reference_is_ambiguous(self):
        _item(self.sh, 'a')
        _item(self.sh, 'b')
        source = _item(self.sh, 'c', on_change='sh.a(1) if sh.b() else None')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'on_change', 'sh.a(1) if sh.b() else None', False), refs)


class TestFindReferencesTriggerAndHysteresis(_Base):
    def test_eval_trigger_reference_is_found(self):
        target = _item(self.sh, 'a')
        source = _item(self.sh, 'b', eval='1', eval_trigger='a')

        refs = self.sh.items.find_references('a')

        self.assertIn((source, 'trigger', 'a', True), refs)
        self.assertIsNotNone(target)

    def test_hysteresis_input_reference_is_found(self):
        _item(self.sh, 'sensor')
        output = _item(
            self.sh,
            'output',
            'bool',
            hysteresis_input='sensor',
            hysteresis_upper_threshold='22',
            hysteresis_lower_threshold='18',
        )

        refs = self.sh.items.find_references('sensor')

        self.assertIn((output, 'hysteresis_input', 'sensor', True), refs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
