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


def load_item_paths(items_dir):
    """Load *items_dir* into a fresh Items instance and return the sorted paths of all loaded items."""
    _reset()
    sh = MockSmartHome()
    sh._items_dir = items_dir
    with tempfile.TemporaryDirectory() as empty:
        sh.items.load_itemdefinitions(empty + os.sep, items_dir + os.sep, empty, empty)
    return sorted(item.property.path for item in sh.items.return_items())


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


if __name__ == '__main__':
    unittest.main()
