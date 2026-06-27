#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_items.py's ItemsController.

Calls the controller methods directly (not through the real CherryPy
dispatch/HTTP layer) — first tests for this controller layer, no
existing convention to follow.

Coverage
--------
add():        POST /api/items/<path> - create_item()
delete():     DELETE /api/items/<path> - remove_item()
references(): GET /api/items/<path>/references - find_references()
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

import lib.item.item
import lib.item.items
import lib.shyaml as shyaml
from lib.item.items import Items
from modules.admin.api_items import ItemsController
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
        module = MagicMock()
        module._sh = self.sh
        self.controller = ItemsController(module)

    def tearDown(self):
        _reset()

    def _post_body(self, data):
        """Patch cherrypy.request.body.read() to return the given dict as JSON bytes."""
        body = MagicMock()
        body.read.return_value = json.dumps(data).encode('utf-8')
        request = MagicMock()
        request.body = body
        return patch.object(cherrypy, 'request', request)


class TestReadAttributes(_Base):
    def test_read_attributes_includes_type_attribute_with_valid_list(self):
        result = json.loads(self.controller.read(id='attributes'))

        self.assertEqual(result['type']['type'], 'str')
        self.assertEqual(result['type']['valid_list'], ['bool', 'num', 'str', 'list', 'dict', 'foo', 'scene'])

    def test_read_attributes_omits_valid_list_when_absent(self):
        result = json.loads(self.controller.read(id='attributes'))

        self.assertNotIn('valid_list', result['autotimer'])

    def test_read_attributes_includes_description(self):
        result = json.loads(self.controller.read(id='attributes'))

        self.assertIn('de', result['autotimer']['description'])
        self.assertIn('en', result['autotimer']['description'])


class TestAdd(_Base):
    def test_add_creates_item(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        self.assertIsNotNone(self.sh.items.return_item('new'))

    def test_add_returns_ok_json(self):
        with self._post_body({'config': {'type': 'num'}}):
            result = self.controller.add(id='new')

        self.assertEqual(json.loads(result), {'result': 'ok'})

    def test_add_with_broken_body_returns_400(self):
        body = MagicMock()
        body.read.return_value = b'not json'
        request = MagicMock()
        request.body = body
        with patch.object(cherrypy, 'request', request):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.add(id='new')

        self.assertEqual(ctx.exception.status, 400)

    def test_add_nested_item_appears_in_parent_children(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='parent')
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='parent.child')

        parent = self.sh.items.return_item('parent')
        child = self.sh.items.return_item('parent.child')
        self.assertIn(child, list(parent.return_children()))

    def test_add_with_missing_parent_returns_400(self):
        with self._post_body({'config': {'type': 'num'}}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.add(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 400)

    def test_add_persist_false_writes_no_file(self):
        with self._post_body({'config': {'type': 'num'}, 'persist': False}):
            self.controller.add(id='new')

        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir.name, 'created.yaml')))

    def test_add_with_explicit_filename_writes_that_file(self):
        with self._post_body({'config': {'type': 'num'}, 'filename': 'custom'}):
            self.controller.add(id='new')

        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir.name, 'custom.yaml')))
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir.name, 'created.yaml')))


class TestDelete(_Base):
    def test_delete_removes_item(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        self.controller.delete(id='new')

        self.assertIsNone(self.sh.items.return_item('new'))

    def test_delete_returns_ok_json(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        result = self.controller.delete(id='new')

        self.assertEqual(json.loads(result), {'result': 'ok'})

    def test_delete_missing_item_returns_404(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.delete(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)

    def test_delete_persist_false_keeps_file_entry(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        with self._post_body({'persist': False}):
            self.controller.delete(id='new')

        self.assertIsNone(self.sh.items.return_item('new'))
        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, 'created'))
        yf.load()
        self.assertIsNotNone(yf.getnode('new'))

    def test_delete_without_body_defaults_to_persist_true(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        self.controller.delete(id='new')

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, 'created'))
        yf.load()
        self.assertIsNone(yf.getnode('new'))


class TestReferences(_Base):
    def test_references_finds_eval_reference(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')
        with self._post_body({'config': {'type': 'num', 'eval': 'sh.target()'}}):
            self.controller.add(id='source')

        result = json.loads(self.controller.references(id='target'))

        self.assertEqual(result, [{'item': 'source', 'attribute': 'eval', 'value': 'sh.target()'}])

    def test_references_no_match_returns_empty_list(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='alone')

        result = json.loads(self.controller.references(id='alone'))

        self.assertEqual(result, [])

    def test_references_missing_item_returns_404(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.references(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
