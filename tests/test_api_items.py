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


class TestReadItemDetail(_Base):
    def test_read_includes_editable_config_with_core_attributes(self):
        with self._post_body({'config': {'type': 'num', 'eval': '1', 'cycle': '30'}}):
            self.controller.add(id='target')

        result = json.loads(self.controller.read(id='target'))[0]

        self.assertEqual(result['editable_config']['type'], 'num')
        self.assertEqual(result['editable_config']['eval'], '1')
        self.assertEqual(result['editable_config']['cycle'], '30')

    def test_editable_config_is_distinct_from_the_generic_config_field(self):
        # 'config' stays item.conf-only (generic/plugin attrs, used by the
        # existing read-only attributes table) — editable_config is the new,
        # separate, complete attribute set meant for pre-populating an edit form.
        with self._post_body({'config': {'type': 'num', 'eval': '1', 'my_custom_attr': 'x'}}):
            self.controller.add(id='target')

        result = json.loads(self.controller.read(id='target'))[0]

        self.assertNotIn('eval', result['config'])
        self.assertIn('eval', result['editable_config'])
        self.assertEqual(result['config']['my_custom_attr'], 'x')


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

    def test_add_with_colliding_name_returns_400_not_ok(self):
        with self._post_body({'config': {'type': 'num'}}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.add(id='scheduler')

        self.assertEqual(ctx.exception.status, 400)
        self.assertIsNone(self.sh.items.return_item('scheduler'))


class TestRename(_Base):
    def _post_body_as_post_method(self, data):
        """Like _post_body(), but also sets request.method = 'POST' —
        needed for rename(), a vpath sub-resource endpoint that isn't
        verb-gated by RESTResource's dispatcher and so checks the method
        itself (same reasoning as remove_references())."""
        body = MagicMock()
        body.read.return_value = json.dumps(data).encode('utf-8')
        request = MagicMock()
        request.method = 'POST'
        request.body = body
        return patch.object(cherrypy, 'request', request)

    def test_rename_updates_item_path(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        with self._post_body_as_post_method({'new_path': 'new'}):
            self.controller.rename(id='old')

        self.assertIsNone(self.sh.items.return_item('old'))
        self.assertIsNotNone(self.sh.items.return_item('new'))

    def test_rename_returns_ok_json_with_report(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        with self._post_body_as_post_method({'new_path': 'new'}):
            result = self.controller.rename(id='old')

        self.assertEqual(
            json.loads(result), {'result': 'ok', 'new_path': 'new', 'rewritten_references': [], 'failed_references': []}
        )

    def test_rename_missing_item_returns_404(self):
        with self._post_body_as_post_method({'new_path': 'new'}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.rename(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)

    def test_rename_can_move_to_a_different_existing_parent(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new_parent')
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        with self._post_body_as_post_method({'new_path': 'new_parent.old'}):
            self.controller.rename(id='old')

        self.assertIsNone(self.sh.items.return_item('old'))
        self.assertIsNotNone(self.sh.items.return_item('new_parent.old'))

    def test_rename_move_to_nonexistent_parent_returns_400(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        with self._post_body_as_post_method({'new_path': 'different.parent.new'}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.rename(id='old')

        self.assertEqual(ctx.exception.status, 400)

    def test_rename_name_collision_returns_400(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        with self._post_body_as_post_method({'new_path': 'scheduler'}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.rename(id='old')

        self.assertEqual(ctx.exception.status, 400)

    def test_rename_rejects_get(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='old')

        body = MagicMock()
        body.read.return_value = json.dumps({'new_path': 'new'}).encode('utf-8')
        request = MagicMock()
        request.method = 'GET'
        request.body = body
        with patch.object(cherrypy, 'request', request):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.rename(id='old')

        self.assertEqual(ctx.exception.status, 405)


class TestEdit(_Base):
    def test_edit_updates_item_config(self):
        with self._post_body({'config': {'type': 'num', 'eval': '1'}}):
            self.controller.add(id='target')

        with self._post_body({'config': {'type': 'num', 'eval': '2'}}):
            self.controller.edit(id='target')

        self.assertEqual(self.sh.items.return_item('target')._eval, '2')

    def test_edit_returns_ok_json(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')

        with self._post_body({'config': {'type': 'num', 'remark': 'x'}}):
            result = self.controller.edit(id='target')

        self.assertEqual(json.loads(result), {'result': 'ok'})

    def test_edit_missing_item_returns_404(self):
        with self._post_body({'config': {'type': 'num'}}):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.edit(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)

    def test_edit_with_incoming_trigger_reference_succeeds(self):
        with self._post_body({'config': {'type': 'num', 'eval': '1'}}):
            self.controller.add(id='target')
        with self._post_body({'config': {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}}):
            self.controller.add(id='source')

        with self._post_body({'config': {'type': 'num', 'eval': '2'}}):
            result = self.controller.edit(id='target')

        self.assertEqual(json.loads(result), {'result': 'ok'})
        self.assertEqual(self.sh.items.return_item('target')._eval, '2')

    def test_edit_with_broken_body_returns_400(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')

        body = MagicMock()
        body.read.return_value = b'not json'
        request = MagicMock()
        request.body = body
        with patch.object(cherrypy, 'request', request):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.edit(id='target')

        self.assertEqual(ctx.exception.status, 400)


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

    def test_delete_persist_false_query_param_keeps_file_entry(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        self.controller.delete(id='new', persist='false')

        self.assertIsNone(self.sh.items.return_item('new'))
        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, 'created'))
        yf.load()
        self.assertIsNotNone(yf.getnode('new'))

    def test_delete_without_persist_param_defaults_to_true(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        self.controller.delete(id='new')

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, 'created'))
        yf.load()
        self.assertIsNone(yf.getnode('new'))

    def test_delete_invalid_persist_param_returns_400(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='new')

        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.delete(id='new', persist='not-a-bool')

        self.assertEqual(ctx.exception.status, 400)


class TestReferences(_Base):
    def test_references_finds_eval_reference(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')
        with self._post_body({'config': {'type': 'num', 'eval': 'sh.target()'}}):
            self.controller.add(id='source')

        result = json.loads(self.controller.references(id='target'))

        self.assertEqual(result, [{'item': 'source', 'attribute': 'eval', 'value': 'sh.target()', 'unambiguous': True}])

    def test_references_no_match_returns_empty_list(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='alone')

        result = json.loads(self.controller.references(id='alone'))

        self.assertEqual(result, [])

    def test_references_missing_item_returns_404(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.references(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)


class TestRemoveReferences(_Base):
    def _post_request(self):
        request = MagicMock()
        request.method = 'POST'
        return patch.object(cherrypy, 'request', request)

    def test_remove_references_strips_dangling_reference_and_returns_result(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')
        with self._post_body({'config': {'type': 'num', 'trigger': ['target']}}):
            self.controller.add(id='source')

        with self._post_request():
            result = json.loads(self.controller.remove_references(id='target'))

        self.assertEqual(result, {'removed': [['source', ['trigger']]], 'skipped_ambiguous': []})
        self.assertIsNone(self.sh.items.return_item('source')._trigger)

    def test_remove_references_missing_item_returns_404(self):
        with self._post_request():
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.remove_references(id='does.not.exist')

        self.assertEqual(ctx.exception.status, 404)

    def test_remove_references_rejects_get(self):
        with self._post_body({'config': {'type': 'num'}}):
            self.controller.add(id='target')

        request = MagicMock()
        request.method = 'GET'
        with patch.object(cherrypy, 'request', request):
            with self.assertRaises(cherrypy.HTTPError) as ctx:
                self.controller.remove_references(id='target')

        self.assertEqual(ctx.exception.status, 405)


if __name__ == '__main__':
    unittest.main(verbosity=2)
