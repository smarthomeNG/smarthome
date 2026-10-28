#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Item trees spread over several yaml files: loading them merges the files
into one tree, and persisted structural edits (rename) must leave every
file in a state that reloads to the same tree.
"""

import os
import sys
import tempfile
import unittest

from ruamel.yaml import YAML

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


def load_item_types(items_dir):
    """Load *items_dir* into a fresh Items instance and return {path: type} of all loaded items."""
    _reset()
    sh = MockSmartHome()
    sh._items_dir = items_dir
    with tempfile.TemporaryDirectory() as empty:
        sh.items.load_itemdefinitions(empty + os.sep, items_dir + os.sep, empty, empty)
    return {item.property.path: item.type() for item in sh.items.return_items()}


def load_item_paths(items_dir):
    """Like load_item_types(), but only the sorted paths."""
    return sorted(load_item_types(items_dir))


class _MultiFileBase(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.addCleanup(_reset)

    def write_file(self, name, text):
        with open(os.path.join(self.tmpdir.name, name + '.yaml'), 'w') as fh:
            fh.write('%YAML 1.1\n---\n' + text)


class TestLoadingNullNodes(_MultiFileBase):
    """A key without value (``b:``) in a later file is an empty node, not a replacement of the subtree an earlier file defined."""

    DEFINITION = 'a:\n    b:\n        type: num\n        x:\n            type: num\n'

    def test_null_node_in_a_later_file_keeps_the_subtree_of_an_earlier_file(self):
        self.write_file('fa', self.DEFINITION)
        self.write_file('fz', 'a:\n    b:\n')

        self.assertEqual(['a', 'a.b', 'a.b.x'], load_item_paths(self.tmpdir.name))

    def test_null_node_in_an_earlier_file_does_not_hide_the_subtree_of_a_later_file(self):
        self.write_file('fa', 'a:\n    b:\n')
        self.write_file('fz', self.DEFINITION)

        self.assertEqual(['a', 'a.b', 'a.b.x'], load_item_paths(self.tmpdir.name))


class TestRenameWithChildrenInOtherFiles(_MultiFileBase):
    """An item's children may be defined in other files than the item itself; a rename must carry them along."""

    def setUp(self):
        super().setUp()
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.items = self.sh.items
        self.items.create_item('p', {'type': 'num'}, filename='fa')
        self.items.create_item('p.c', {'type': 'num'}, filename='fb')
        self.items.create_item('p.c.g', {'type': 'num'}, filename='fb')
        self.items.create_item('t', {'type': 'num'}, filename='fa')

    def _live_paths(self):
        return sorted(item.property.path for item in self.items.return_items())

    def _live_types(self):
        return {item.property.path: item.type() for item in self.items.return_items()}

    def test_rename_keeps_the_tree_reloadable_when_children_live_in_another_file(self):
        self.items.rename_item(self.items.return_item('p'), 'q')

        self.assertEqual(['q', 'q.c', 'q.c.g', 't'], self._live_paths())
        self.assertEqual(self._live_types(), load_item_types(self.tmpdir.name))

    def test_move_under_another_parent_keeps_the_tree_reloadable(self):
        self.items.rename_item(self.items.return_item('p'), 't.p')

        self.assertEqual(['t', 't.p', 't.p.c', 't.p.c.g'], self._live_paths())
        self.assertEqual(self._live_types(), load_item_types(self.tmpdir.name))

    def test_rename_into_another_file_leaves_the_children_in_their_own_file(self):
        self.items.rename_item(self.items.return_item('p'), 'q', filename='fz')

        self.assertEqual('fz', self.items.return_item('q')._filename)
        self.assertEqual('fb', self.items.return_item('q.c')._filename)
        self.assertEqual(self._live_types(), load_item_types(self.tmpdir.name))

    def test_rename_into_the_file_that_holds_the_children_keeps_both_nodes(self):
        self.items.rename_item(self.items.return_item('p'), 'q', filename='fb')

        self.assertEqual(['q', 'q.c', 'q.c.g', 't'], self._live_paths())
        self.assertEqual(self._live_types(), load_item_types(self.tmpdir.name))


class TestRemovingTheLastChild(_MultiFileBase):
    """The parent of a moved or removed last child stays an item, in the live tree and after a reload."""

    def setUp(self):
        super().setUp()
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.items = self.sh.items
        self.items.create_item('a', {}, filename='fa')
        self.items.create_item('a.b', {'type': 'num'}, filename='fa')

    def test_moving_the_last_child_away_keeps_the_parent_after_a_reload(self):
        self.items.rename_item(self.items.return_item('a.b'), 'c')

        self.assertEqual(['a', 'c'], load_item_paths(self.tmpdir.name))

    def test_removing_the_last_child_keeps_the_parent_after_a_reload(self):
        self.items.remove_item(self.items.return_item('a.b'))

        self.assertEqual(['a'], load_item_paths(self.tmpdir.name))


class TestEmptiedContainerBranches(_MultiFileBase):
    """A file only holds ancestors of a moved or removed item as containers; those go with it, unless an item is defined there."""

    def setUp(self):
        super().setUp()
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.items = self.sh.items
        self.items.create_item('p', {'type': 'num'}, filename='fa')
        self.items.create_item('p.c', {'type': 'num'}, filename='fb')
        self.items.create_item('t', {'type': 'num'}, filename='fa')

    def _file_data(self, name):
        path = os.path.join(self.tmpdir.name, name + '.yaml')
        if not os.path.isfile(path):
            return {}
        with open(path) as fh:
            return YAML(typ='safe').load(fh) or {}

    def test_moving_the_child_away_removes_the_containers_it_leaves_empty(self):
        self.items.rename_item(self.items.return_item('p.c'), 't.c')

        self.assertNotIn('p', self._file_data('fb'))
        self.assertEqual({'p': 'num', 't': 'num', 't.c': 'num'}, load_item_types(self.tmpdir.name))

    def test_removing_the_child_removes_the_containers_it_leaves_empty(self):
        self.items.remove_item(self.items.return_item('p.c'))

        self.assertNotIn('p', self._file_data('fb'))
        self.assertEqual({'p': 'num', 't': 'num'}, load_item_types(self.tmpdir.name))

    def test_container_branch_of_a_file_that_still_holds_siblings_stays(self):
        self.items.create_item('p.d', {'type': 'num'}, filename='fb')

        self.items.rename_item(self.items.return_item('p.c'), 't.c')

        self.assertEqual({'d'}, set(self._file_data('fb')['p']))


class TestNullItemNodeGate(_MultiFileBase):
    """A file written by the core never holds a live item as a null node, whatever state the file was in before."""

    def setUp(self):
        super().setUp()
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.items = self.sh.items
        self.items.create_item('a', {'type': 'num'}, filename='fa')
        self.items.create_item('a.b', {'type': 'num'}, filename='fa')
        self.write_file('fa', 'a:\n    type: num\n    b:\n')

    def _file_data(self, name):
        with open(os.path.join(self.tmpdir.name, name + '.yaml')) as fh:
            return YAML(typ='safe').load(fh)

    def test_saving_a_file_turns_a_null_item_node_into_an_empty_item(self):
        self.items.create_item('a.c', {'type': 'num'}, filename='fa')

        self.assertEqual({}, self._file_data('fa')['a']['b'])

    def test_null_attribute_values_are_left_alone(self):
        self.write_file('fa', 'a:\n    type: num\n    name:\n    b:\n')

        self.items.create_item('a.c', {'type': 'num'}, filename='fa')

        self.assertIsNone(self._file_data('fa')['a']['name'])


if __name__ == '__main__':
    unittest.main()
