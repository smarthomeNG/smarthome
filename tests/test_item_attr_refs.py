#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for attribute references (``..:attr``, ``.:attr``, ``{..:attr}``) on the
base text attributes ``name``, ``description`` and ``remark``
(lib/item/item.py, lib/item/_internal/_parsing.py).

These three attributes can be reference targets and reference sources, next to
the plugin-specific attributes that support references already.
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


def _build(sh, path, conf):
    """Create the item tree described by *conf* (nested dicts are children) and return the top item."""
    item = lib.item.item.Item(sh, sh, path, conf)
    sh.items.add_item(path, item)
    return item


class _Base(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def tearDown(self):
        _reset()

    def build(self, conf, path='top'):
        _build(self.sh, path, conf)
        return self.sh.items.return_item


class TestCopyFromParent(_Base):
    def test_description_is_copied_from_parent(self):
        get = self.build({'description': 'Kitchen window', 'child': {'description': '..:.'}})

        self.assertEqual(get('top.child').property.description, 'Kitchen window')

    def test_remark_is_copied_from_parent(self):
        get = self.build({'remark': 'check battery', 'child': {'remark': '..:.'}})

        self.assertEqual(get('top.child').property.remark, 'check battery')

    def test_name_is_copied_from_parent(self):
        get = self.build({'name': 'Window', 'child': {'name': '..:.'}})

        self.assertEqual(get('top.child').property.name, 'Window')

    def test_grandparent_level(self):
        get = self.build({'description': 'Kitchen window', 'mid': {'child': {'description': '...:.'}}})

        self.assertEqual(get('top.mid.child').property.description, 'Kitchen window')

    def test_other_attribute_name(self):
        get = self.build({'description': 'Kitchen window', 'child': {'remark': '..:description'}})

        self.assertEqual(get('top.child').property.remark, 'Kitchen window')

    def test_chain_through_intermediate_item(self):
        get = self.build(
            {'description': 'Kitchen window', 'mid': {'description': '..:.', 'child': {'description': '..:.'}}}
        )

        self.assertEqual(get('top.mid.child').property.description, 'Kitchen window')

    def test_unset_source_keeps_default(self):
        get = self.build({'child': {'name': '..:.', 'description': '..:.', 'remark': '..:.'}})

        child = get('top.child').property
        self.assertEqual(child.name, 'top.child')
        self.assertIsNone(child.description)
        self.assertIsNone(child.remark)

    def test_text_with_colon_is_not_a_reference(self):
        get = self.build({'description': 'Note: see manual', 'child': {'description': 'Sensor: ..:x'}})

        self.assertEqual(get('top.child').property.description, 'Sensor: ..:x')


class TestSelfReference(_Base):
    def test_base_attribute_from_other_base_attribute(self):
        get = self.build({'child': {'remark': 'check battery', 'description': '.:remark'}})

        self.assertEqual(get('top.child').property.description, 'check battery')

    def test_self_reference_is_independent_of_definition_order(self):
        get = self.build({'child': {'description': '.:remark', 'remark': 'check battery'}})

        self.assertEqual(get('top.child').property.description, 'check battery')

    def test_self_reference_to_reference_resolves_through(self):
        get = self.build({'remark': 'check battery', 'child': {'description': '.:remark', 'remark': '..:.'}})

        self.assertEqual(get('top.child').property.description, 'check battery')

    def test_cycle_resolves_to_unset(self):
        get = self.build({'child': {'description': '.:remark', 'remark': '.:description'}})

        child = get('top.child').property
        self.assertIsNone(child.description)
        self.assertIsNone(child.remark)

    def test_reference_to_self_resolves_to_unset(self):
        get = self.build({'child': {'description': '.:.'}})

        self.assertIsNone(get('top.child').property.description)


class TestPlaceholders(_Base):
    def test_description_placeholder_with_base_source(self):
        get = self.build({'name': 'Window', 'child': {'description_': 'Handle of {..:name}'}})

        self.assertEqual(get('top.child').property.description, 'Handle of Window')

    def test_name_placeholder_with_base_source(self):
        get = self.build({'description': 'Window', 'child': {'name_': 'Handle of {..:description}'}})

        self.assertEqual(get('top.child').property.name, 'Handle of Window')

    def test_remark_placeholder_with_self_source(self):
        get = self.build({'child': {'description': 'Window', 'remark_': 'about {.:description}'}})

        self.assertEqual(get('top.child').property.remark, 'about Window')

    def test_placeholder_with_plugin_attribute_source(self):
        get = self.build({'room': 'kitchen', 'child': {'description_': 'In {..:room}'}})

        self.assertEqual(get('top.child').property.description, 'In kitchen')

    def test_underscore_form_does_not_leak_into_conf(self):
        get = self.build({'name': 'Window', 'child': {'description_': 'Handle of {..:name}'}})

        self.assertNotIn('description_', get('top.child').conf)
        self.assertNotIn('description', get('top.child').conf)


class TestPluginAttributeTargets(_Base):
    def test_plugin_attribute_copies_parent_base_attribute(self):
        get = self.build({'name': 'Window', 'child': {'foo': '..:name'}})

        self.assertEqual(get('top.child').conf['foo'], 'Window')

    def test_plugin_attribute_copies_own_base_attribute(self):
        get = self.build({'child': {'description': 'Window', 'foo': '.:description'}})

        self.assertEqual(get('top.child').conf['foo'], 'Window')

    def test_plugin_attribute_placeholder_uses_base_attribute(self):
        get = self.build({'name': 'Window', 'child': {'foo_': 'dev/{..:name}/state'}})

        self.assertEqual(get('top.child').conf['foo'], 'dev/Window/state')


class TestOtherBaseAttributesUntouched(_Base):
    def test_enforce_updates_reference_is_not_resolved(self):
        get = self.build({'enforce_updates': 'yes', 'child': {'enforce_updates': '..:.'}})

        self.assertTrue(get('top').property.enforce_updates)
        self.assertFalse(get('top.child').property.enforce_updates)

    def test_eval_text_is_not_resolved(self):
        get = self.build({'eval': 'x', 'child': {'eval': '..:.'}})

        self.assertEqual(get('top.child').property.eval, '..:.')


class TestEditItem(_Base):
    def test_edit_item_resolves_against_parent(self):
        self.sh.items.create_item('top', {'type': 'foo', 'description': 'Kitchen window'}, persist=False)
        child = self.sh.items.create_item('top.child', {'type': 'foo'}, persist=False)

        self.sh.items.edit_item(child, {'type': 'foo', 'description': '..:.'}, notify_plugins=False)

        self.assertEqual(child.property.description, 'Kitchen window')


if __name__ == '__main__':
    unittest.main()
