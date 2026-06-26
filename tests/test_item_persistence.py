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

        data = self._read_file('created')
        self.assertNotIn('new', data)

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

        data = self._read_file('created')
        self.assertNotIn('static_item', data)

    def _write_to_existing_file(self, filename, path, config):
        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        if os.path.isfile(self._file_path(filename)):
            yf.load()
        yf.setvalue(path, config)
        yf.save()


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
