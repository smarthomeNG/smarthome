#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/item/_json.py

Coverage
--------
jsonvars():
  returns dict with the six expected keys
  id    == item._path
  name  == item._name
  value == item._value (current value)
  type  == item._type
  attributes == item.conf
  children == item.get_children_path()
  works for num / str / bool item types
  conf attributes are reflected in 'attributes' key

to_json():
  returns a valid JSON string
  parsed JSON matches jsonvars() output
  keys are sorted alphabetically (json.dumps sort_keys=True)
  indentation is 2 spaces
  round-trip: to_json then json.loads gives correct values
"""

import json
import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from lib.item._internal._json import jsonvars, to_json
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


def _item(sh, path, itype='num', value=None, **conf):
    conf['type'] = itype
    it = lib.item.item.Item(sh, sh.items, path, conf)
    if value is not None:
        it(value)
    return it


class TestJsonvarsKeys(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_returns_dict(self):
        item = _item(self.sh, 'myitem')
        self.assertIsInstance(jsonvars(item), dict)

    def test_has_all_six_keys(self):
        item = _item(self.sh, 'myitem')
        result = jsonvars(item)
        for key in ('id', 'name', 'value', 'type', 'attributes', 'children'):
            self.assertIn(key, result)

    def test_id_equals_path(self):
        item = _item(self.sh, 'sensor.temp')
        self.assertEqual(jsonvars(item)['id'], 'sensor.temp')

    def test_name_equals_item_name(self):
        item = _item(self.sh, 'sensor.temp')
        self.assertEqual(jsonvars(item)['name'], item._name)

    def test_value_reflects_current_value(self):
        item = _item(self.sh, 'myitem', itype='num', value=42)
        self.assertEqual(jsonvars(item)['value'], 42)

    def test_type_reflects_item_type(self):
        item = _item(self.sh, 'myitem', itype='str')
        self.assertEqual(jsonvars(item)['type'], 'str')

    def test_attributes_equals_conf(self):
        item = _item(self.sh, 'myitem', itype='num', knx_dpt='9.001')
        self.assertIs(jsonvars(item)['attributes'], item.conf)

    def test_children_is_list(self):
        item = _item(self.sh, 'myitem')
        self.assertIsInstance(jsonvars(item)['children'], list)


class TestJsonvarsTypes(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_num_item_value(self):
        item = _item(self.sh, 'n', itype='num', value=3.14)
        self.assertAlmostEqual(jsonvars(item)['value'], 3.14)

    def test_str_item_value(self):
        item = _item(self.sh, 's', itype='str', value='hello')
        self.assertEqual(jsonvars(item)['value'], 'hello')

    def test_bool_item_true(self):
        item = _item(self.sh, 'b', itype='bool', value=True)
        self.assertTrue(jsonvars(item)['value'])

    def test_bool_item_false(self):
        item = _item(self.sh, 'b', itype='bool', value=False)
        self.assertFalse(jsonvars(item)['value'])

    def test_type_num(self):
        self.assertEqual(jsonvars(_item(self.sh, 'n', itype='num'))['type'], 'num')

    def test_type_bool(self):
        self.assertEqual(jsonvars(_item(self.sh, 'b', itype='bool'))['type'], 'bool')

    def test_value_updates_after_set(self):
        item = _item(self.sh, 'n', itype='num', value=1)
        item(99)
        self.assertEqual(jsonvars(item)['value'], 99)


class TestJsonvarsConf(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_extra_conf_key_in_attributes(self):
        item = _item(self.sh, 'n', itype='num', knx_dpt='9.001')
        self.assertIn('knx_dpt', jsonvars(item)['attributes'])

    def test_extra_conf_value_correct(self):
        item = _item(self.sh, 'n', itype='num', knx_dpt='9.001')
        self.assertEqual(jsonvars(item)['attributes']['knx_dpt'], '9.001')


class TestToJson(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_returns_string(self):
        item = _item(self.sh, 'myitem')
        self.assertIsInstance(to_json(item), str)

    def test_valid_json(self):
        item = _item(self.sh, 'myitem', itype='num', value=7)
        result = to_json(item)
        parsed = json.loads(result)
        self.assertIsInstance(parsed, dict)

    def test_round_trip_id(self):
        item = _item(self.sh, 'sensor.temp')
        parsed = json.loads(to_json(item))
        self.assertEqual(parsed['id'], 'sensor.temp')

    def test_round_trip_value(self):
        item = _item(self.sh, 'n', itype='num', value=42)
        parsed = json.loads(to_json(item))
        self.assertEqual(parsed['value'], 42)

    def test_keys_are_sorted(self):
        item = _item(self.sh, 'n', itype='num')
        raw = to_json(item)
        keys_in_order = [
            line.split('"')[1] for line in raw.splitlines() if '":' in line and line.strip().startswith('"')
        ]
        self.assertEqual(keys_in_order, sorted(keys_in_order))

    def test_two_space_indent(self):
        item = _item(self.sh, 'n', itype='num', value=0)
        lines = to_json(item).splitlines()
        # at least one indented line starts with exactly two spaces
        indented = [ln for ln in lines if ln.startswith('  ') and not ln.startswith('   ')]
        self.assertTrue(len(indented) > 0)

    def test_matches_jsonvars(self):
        item = _item(self.sh, 'sensor.temp', itype='str', value='warm')
        parsed = json.loads(to_json(item))
        jv = jsonvars(item)
        self.assertEqual(parsed['id'], jv['id'])
        self.assertEqual(parsed['value'], jv['value'])
        self.assertEqual(parsed['type'], jv['type'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
