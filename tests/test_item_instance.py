#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""The ``instance`` attribute of items: own value, inheritance by child items, and the stored effective value."""

import os
import sys
import unittest
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.config
import lib.item.item
import lib.metadata
import lib.plugin
from tests.mock.core import MockSmartHome
from tests.test_item_edit import FakePlugin
from tests.test_item_pathresolution import _make_sh, _reset as _reset_items

INSTANCE_LOGGER = 'lib.item._internal._instance'


def _reset():
    """Reset the item registry, the plugin registry and the plugin metadata."""
    _reset_items()
    lib.metadata.all_itemdefinitions.clear()
    lib.metadata.all_itemprefixdefinitions.clear()
    lib.metadata.all_prefixes_tuple = None
    lib.plugin._plugins_instance = None
    lib.plugin.Plugins._plugins = []
    lib.plugin.Plugins._threads = []
    lib.plugin.Plugins._plugindict = {}


def _load(sh, tree):
    """Create the top-level items of *tree* (dict of item configs) below sh.items."""
    for name, config in tree.items():
        item = lib.item.item.Item(sh, sh.items, name, config)
        sh.items.add_item(name, item)
        vars(sh)[name] = item


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()

    def conf_instance(self, path):
        return self.sh.items.return_item(path).conf.get('instance')


class TestEffectiveInstance(_Base):
    def test_own_scalar_instance_is_stored_as_list(self):
        _load(self.sh, {'room': {'instance': 'fb2'}})
        self.assertEqual(['fb2'], self.conf_instance('room'))

    def test_item_without_instance_in_the_chain_has_none(self):
        _load(self.sh, {'room': {'lamp': {'type': 'bool'}}})
        self.assertNotIn('instance', self.sh.items.return_item('room.lamp').conf)

    def test_child_inherits_the_parents_instance(self):
        _load(self.sh, {'room': {'instance': 'fb2', 'lamp': {'type': 'bool', 'sub': {'type': 'num'}}}})
        self.assertEqual(['fb2'], self.conf_instance('room.lamp'))
        self.assertEqual(['fb2'], self.conf_instance('room.lamp.sub'))

    def test_childs_own_instance_overrides_and_passes_on(self):
        _load(self.sh, {'room': {'instance': 'fb2', 'lamp': {'instance': 'fb3', 'sub': {'type': 'num'}}}})
        self.assertEqual(['fb3'], self.conf_instance('room.lamp'))
        self.assertEqual(['fb3'], self.conf_instance('room.lamp.sub'))

    def test_default_resets_to_the_empty_instance(self):
        _load(self.sh, {'room': {'instance': 'fb2', 'lamp': {'instance': 'default', 'sub': {'type': 'num'}}}})
        self.assertEqual([''], self.conf_instance('room.lamp'))
        self.assertEqual([''], self.conf_instance('room.lamp.sub'))

    def test_list_is_kept(self):
        _load(self.sh, {'room': {'instance': ['fb2', 'db_2'], 'lamp': {'type': 'bool'}}})
        self.assertEqual(['fb2', 'db_2'], self.conf_instance('room.lamp'))


class TestInstanceIsNotReportedAsUndefined(_Base):
    def test_no_undefined_attribute_notice_for_instance(self):
        with self.assertNoLogs('lib.metadata', level=0):
            _load(self.sh, {'room': {'instance': 'fb2', 'lamp': {'type': 'bool'}}})


class TestUnknownInstanceWarning(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()
        self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def tearDown(self):
        _reset()

    def test_instance_naming_no_section_is_warned_about(self):
        with self.assertLogs(INSTANCE_LOGGER, level='WARNING') as logs:
            _load(self.sh, {'room': {'instance': 'nosuch', 'lamp': {'type': 'bool'}}})
        self.assertEqual(1, len([line for line in logs.output if "'nosuch'" in line]))

    def test_instance_naming_a_section_is_not_warned_about(self):
        with self.assertNoLogs(INSTANCE_LOGGER, level='WARNING'):
            _load(self.sh, {'room': {'instance': ['bind', 'wol'], 'lamp': {'type': 'bool'}}})


class TestLegacyInstances(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()
        self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')
        self.sh._legacy_instances = True

    def tearDown(self):
        _reset()

    def test_instance_keeps_its_struct_only_meaning(self):
        with self.assertNoLogs(INSTANCE_LOGGER, level='WARNING'):
            _load(self.sh, {'room': {'instance': 'home', 'lamp': {'type': 'bool'}}})
        self.assertNotIn('instance', self.sh.items.return_item('room').conf)
        self.assertNotIn('instance', self.sh.items.return_item('room.lamp').conf)


class TestEditItem(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)
        self.room = self.sh.items.create_item(
            'room',
            {'instance': 'fb2', 'lamp': {'type': 'bool'}, 'own': {'type': 'bool', 'instance': 'fb3'}},
            persist=False,
        )

    def test_editing_the_parents_instance_updates_inheriting_children_only(self):
        self.sh.items.edit_item(self.room, {'instance': 'fb4'})
        self.assertEqual(['fb4'], self.conf_instance('room.lamp'))
        self.assertEqual(['fb3'], self.conf_instance('room.own'))

    def test_removing_the_parents_instance_removes_it_from_inheriting_children(self):
        self.sh.items.edit_item(self.room, {})
        self.assertIsNone(self.conf_instance('room.lamp'))
        self.assertEqual(['fb3'], self.conf_instance('room.own'))

    def test_inheriting_children_are_rebound_in_plugins(self):
        lamp = self.sh.items.return_item('room.lamp')
        own = self.sh.items.return_item('room.own')
        self.sh.items.edit_item(self.room, {'instance': 'fb4'})
        self.assertIn(lamp, self.fake_plugin.removed_items)
        self.assertEqual(2, self.fake_plugin.parsed_items.count(lamp))
        self.assertNotIn(own, self.fake_plugin.removed_items)

    def test_editable_config_of_an_inheriting_child_does_not_contain_the_inherited_instance(self):
        lamp = self.sh.items.return_item('room.lamp')
        self.assertNotIn('instance', self.sh.items.current_config_for_edit(lamp))

    def test_editable_config_keeps_the_own_instance(self):
        own = self.sh.items.return_item('room.own')
        self.assertEqual(['fb3'], self.sh.items.current_config_for_edit(own)['instance'])


class TestStructInstancePlaceholder(unittest.TestCase):
    def replaced(self, instance):
        subtree = OrderedDict([('avm_x@instance', 1), ('name', 'n')])
        lib.config.replace_struct_instance('room', subtree, instance)
        return list(subtree)

    def test_scalar_instance_is_substituted(self):
        self.assertEqual(['name', 'avm_x@fb2'], self.replaced('fb2'))

    def test_empty_instance_strips_the_placeholder(self):
        self.assertEqual(['name', 'avm_x'], self.replaced(''))

    def test_list_instance_strips_the_placeholder(self):
        self.assertEqual(['name', 'avm_x'], self.replaced(['fb2', 'db_2']))

    def test_default_keyword_strips_the_placeholder(self):
        self.assertEqual(['name', 'avm_x'], self.replaced('default'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
