#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for persisting runtime item create/remove to YAML (lib/item/items.py).

Coverage
--------
create_item(persist=True):
  writes items_dir/<filename>.yaml (default 'created', explicit override,
  configured sh._created_items_file default)
  sets item._filename (extension-less)
  two items persisted to the same file don't clobber each other
  nested config (grandchildren) get _filename too
  persist=False writes nothing

remove_item(item, persist=True):
  removes the item's entry from its file
  no-op if item._filename is None
  works generically for an item whose _filename was set externally
  (simulating a statically-loaded item)

Comments in an existing file survive a create_item() call that adds
another entry.
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
from lib.constants import YAML_FILE
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


class _Base(unittest.TestCase):
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

    def _file_path(self, filename):
        return os.path.join(self.tmpdir.name, filename + YAML_FILE)


class TestCreateItemPersistDefault(_Base):
    def test_persist_default_writes_created_yaml(self):
        self.sh.items.create_item('new', {'type': 'num'})

        self.assertTrue(os.path.isfile(self._file_path('created')))

    def test_persisted_content_matches(self):
        self.sh.items.create_item('new', {'type': 'num', 'eval': '1'})

        data = self._read_file('created')
        self.assertEqual(data['new']['type'], 'num')
        self.assertEqual(data['new']['eval'], '1')
        # the internal bookkeeping key must not leak into the file on disk
        self.assertNotIn('_filename', data['new'])

    def test_item_filename_set_without_extension(self):
        item = self.sh.items.create_item('new', {'type': 'num'})

        self.assertEqual(item.property.defined_in, 'created')

    def test_explicit_filename_overrides_default(self):
        self.sh.items.create_item('new', {'type': 'num'}, filename='custom')

        self.assertTrue(os.path.isfile(self._file_path('custom')))
        self.assertFalse(os.path.isfile(self._file_path('created')))

    def test_configured_default_is_used_when_no_filename_given(self):
        self.sh._created_items_file = 'mycustom'

        self.sh.items.create_item('new', {'type': 'num'})

        self.assertTrue(os.path.isfile(self._file_path('mycustom')))

    def test_two_items_in_same_file_both_present(self):
        self.sh.items.create_item('first', {'type': 'num'})
        self.sh.items.create_item('second', {'type': 'num'})

        data = self._read_file('created')
        self.assertIn('first', data)
        self.assertIn('second', data)

    def test_nested_child_gets_filename_too(self):
        item = self.sh.items.create_item('top', {'type': 'num', 'sub': {'type': 'num'}})

        child = next(item.return_children())
        self.assertEqual(child.property.defined_in, 'created')

    def test_persist_false_writes_nothing(self):
        item = self.sh.items.create_item('new', {'type': 'num'}, persist=False)

        self.assertFalse(os.path.isfile(self._file_path('created')))
        self.assertIsNone(item.property.defined_in)


class TestRemoveItemPersist(_Base):
    def test_remove_persisted_item_removes_entry_from_file(self):
        item = self.sh.items.create_item('new', {'type': 'num'})

        self.sh.items.remove_item(item)

        # 'new' was the only entry in 'created.yaml' - removing it leaves
        # the file empty, so it gets deleted rather than left behind as
        # a redundant '{}' document.
        self.assertFalse(os.path.isfile(self._file_path('created')))

    def test_remove_without_filename_is_noop(self):
        item = self.sh.items.create_item('new', {'type': 'num'}, persist=False)

        self.sh.items.remove_item(item)  # must not raise, must not create a file

        self.assertFalse(os.path.isfile(self._file_path('created')))

    def test_remove_works_generically_for_externally_set_filename(self):
        # simulate a statically-loaded item: _filename present, but the
        # item was never created via create_item()
        item = lib.item.item.Item(self.sh, self.sh, 'static_item', {'type': 'num', '_filename': 'created'})
        self.sh.items.add_item('static_item', item)
        self._write_to_existing_file('created', 'static_item', {'type': 'num'})

        self.sh.items.remove_item(item)

        # 'static_item' was the only entry - file is now empty, so it
        # gets deleted rather than left behind as a redundant '{}' doc.
        self.assertFalse(os.path.isfile(self._file_path('created')))

    def _write_to_existing_file(self, filename, path, config):
        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        if os.path.isfile(self._file_path(filename)):
            yf.load()
        yf.setvalue(path, config)
        yf.save()


class TestRemoveItemRecursive(_Base):
    def test_removing_an_item_with_children_without_recursive_raises(self):
        parent = self.sh.items.create_item('parent', {'type': 'num', 'child': {'type': 'num'}})

        with self.assertRaises(ValueError):
            self.sh.items.remove_item(parent)

        self.assertIsNotNone(self.sh.items.return_item('parent'))
        self.assertIsNotNone(self.sh.items.return_item('parent.child'))

    def test_removing_recursively_removes_parent_and_every_descendant(self):
        parent = self.sh.items.create_item(
            'parent', {'type': 'num', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}}
        )

        self.sh.items.remove_item(parent, recursive=True)

        self.assertIsNone(self.sh.items.return_item('parent'))
        self.assertIsNone(self.sh.items.return_item('parent.child'))
        self.assertIsNone(self.sh.items.return_item('parent.child.grandchild'))

    def test_removing_recursively_persists_removal_of_every_descendant(self):
        self.sh.items.create_item('parent', {'type': 'num', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}})
        parent = self.sh.items.return_item('parent')

        self.sh.items.remove_item(parent, recursive=True)

        # 'parent' (with its nested children) was the only entry - file
        # is now empty, so it gets deleted rather than left behind as a
        # redundant '{}' doc.
        self.assertFalse(os.path.isfile(self._file_path('created')))

    def test_removing_recursively_cleans_up_a_child_persisted_to_a_different_file_than_its_parent(self):
        parent = self.sh.items.create_item('parent', {'type': 'num'}, filename='parentfile')
        child = self.sh.items.create_item('parent.child', {'type': 'num'}, parent=parent, filename='childfile')
        self.assertEqual(child._filename, 'childfile')

        self.sh.items.remove_item(parent, recursive=True)

        # 'parent' was the only entry in parentfile - it's now empty and
        # gets deleted rather than left behind as a redundant '{}' doc.
        self.assertFalse(os.path.isfile(self._file_path('parentfile')))

        # childfile only ever held the nested 'parent.child' path — 'parent'
        # itself is just a structural bridge here, never a real item entry
        # in this file, so removing the nested path value.setvalue(None)s it
        # rather than removing the 'parent' key outright (same shyaml
        # behavior as a nested-path edit anywhere else in this codebase).
        self.assertIsNone(self._read_file('childfile').get('parent'))

    def test_removing_recursively_with_persist_false_writes_nothing(self):
        self.sh.items.create_item('parent', {'type': 'num', 'child': {'type': 'num'}})

        self.sh.items.remove_item(self.sh.items.return_item('parent'), persist=False, recursive=True)

        # 'created' still exists (created by create_item's persist=True
        # above) but the entry itself must remain untouched by a
        # persist=False removal.
        data = self._read_file('created')
        self.assertIn('parent', data)


class TestPersistencePreservesComments(_Base):
    def test_existing_comment_survives_create_item(self):
        path = self._file_path('created')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('# a hand-written comment\nexisting:\n    type: num\n')

        self.sh.items.create_item('new', {'type': 'num'})

        with open(path, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('# a hand-written comment', content)
        self.assertIn('existing', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
