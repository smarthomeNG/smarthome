#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/item/_fade.py

Coverage
--------
Parameter validation:
  stop_fade not a list → warning logged, parameter set to None
  stop_fade is a list → accepted as-is
  continue_fade not a list → warning logged, parameter set to None
  continue_fade is a list → accepted as-is

dest conversion:
  integer dest → stored as float
  string dest → converted to float
  float dest → stored unchanged

_fadingdetails population:
  when not fading → _fadingdetails populated with all fields
  when fading and update=False → _fadingdetails NOT overwritten
  when fading and update=True → _fadingdetails overwritten with new values
  stored fields: value, dest, step, delta, caller, stop_fade,
                 continue_fade, instant_set

Trigger:
  _sh.trigger is always called (regardless of fading state)
  trigger receives correct item path
  trigger receives fadejob callable

Default parameters:
  step defaults to 1
  delta defaults to 1
  instant_set defaults to True
  caller defaults to None
"""

import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from lib.item._internal._fade import fade
from lib.item.helpers import fadejob
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


def _item(sh, path='test.item', itype='num', value=0):
    conf = {'type': itype}
    it = lib.item.item.Item(sh, sh.items, path, conf)
    it(value)
    return it


class TestFadeParameterValidation(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_stop_fade_non_list_warns_and_clears(self):
        item = _item(self.sh, value=10)
        with self.assertLogs('lib.item', level='WARNING') as cm:
            fade(item, 0, stop_fade='Logic')
        self.assertTrue(any('stop_fade' in m for m in cm.output))
        self.assertIsNone(item._fadingdetails['stop_fade'])

    def test_stop_fade_list_accepted(self):
        item = _item(self.sh, value=10)
        fade(item, 0, stop_fade=['Logic', 'Admin'])
        self.assertEqual(item._fadingdetails['stop_fade'], ['Logic', 'Admin'])

    def test_stop_fade_none_accepted(self):
        item = _item(self.sh, value=10)
        fade(item, 0, stop_fade=None)
        self.assertIsNone(item._fadingdetails['stop_fade'])

    def test_continue_fade_non_list_warns_and_clears(self):
        item = _item(self.sh, value=10)
        with self.assertLogs('lib.item', level='WARNING') as cm:
            fade(item, 0, continue_fade='Fader')
        self.assertTrue(any('continue_fade' in m for m in cm.output))
        self.assertIsNone(item._fadingdetails['continue_fade'])

    def test_continue_fade_list_accepted(self):
        item = _item(self.sh, value=10)
        fade(item, 0, continue_fade=['Fader'])
        self.assertEqual(item._fadingdetails['continue_fade'], ['Fader'])

    def test_continue_fade_none_accepted(self):
        item = _item(self.sh, value=10)
        fade(item, 0, continue_fade=None)
        self.assertIsNone(item._fadingdetails['continue_fade'])


class TestFadeDestConversion(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_integer_dest_stored_as_float(self):
        item = _item(self.sh, value=0)
        fade(item, 100)
        self.assertIsInstance(item._fadingdetails['dest'], float)
        self.assertEqual(item._fadingdetails['dest'], 100.0)

    def test_float_dest_stored(self):
        item = _item(self.sh, value=0)
        fade(item, 3.14)
        self.assertAlmostEqual(item._fadingdetails['dest'], 3.14)

    def test_string_dest_converted(self):
        item = _item(self.sh, value=0)
        fade(item, '50')
        self.assertEqual(item._fadingdetails['dest'], 50.0)

    def test_negative_dest(self):
        item = _item(self.sh, value=0)
        fade(item, -5)
        self.assertEqual(item._fadingdetails['dest'], -5.0)


class TestFadingDetails(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_fadingdetails_populated_when_not_fading(self):
        item = _item(self.sh, value=10)
        item._fading = False
        fade(item, 0, step=2, delta=0.5, caller='test')
        d = item._fadingdetails
        self.assertEqual(d['value'], 10)
        self.assertEqual(d['dest'], 0.0)
        self.assertEqual(d['step'], 2)
        self.assertEqual(d['delta'], 0.5)
        self.assertEqual(d['caller'], 'test')

    def test_fadingdetails_not_overwritten_when_fading_no_update(self):
        item = _item(self.sh, value=10)
        item._fading = False
        fade(item, 0, step=1, delta=1)
        original_dest = item._fadingdetails['dest']
        item._fading = True
        fade(item, 99, step=5, delta=5, update=False)
        self.assertEqual(item._fadingdetails['dest'], original_dest)

    def test_fadingdetails_overwritten_when_fading_and_update(self):
        item = _item(self.sh, value=10)
        item._fading = False
        fade(item, 0)
        item._fading = True
        fade(item, 99, step=5, delta=5, update=True)
        self.assertEqual(item._fadingdetails['dest'], 99.0)
        self.assertEqual(item._fadingdetails['step'], 5)

    def test_fadingdetails_has_all_expected_keys(self):
        item = _item(self.sh, value=10)
        item._fading = False
        fade(item, 0)
        expected_keys = {'value', 'dest', 'step', 'delta', 'caller', 'stop_fade', 'continue_fade', 'instant_set'}
        self.assertEqual(set(item._fadingdetails.keys()), expected_keys)

    def test_instant_set_default_true(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertTrue(item._fadingdetails['instant_set'])

    def test_instant_set_false(self):
        item = _item(self.sh, value=0)
        fade(item, 10, instant_set=False)
        self.assertFalse(item._fadingdetails['instant_set'])

    def test_value_snapshot_is_current_value(self):
        item = _item(self.sh, value=42)
        item._fading = False
        fade(item, 0)
        self.assertEqual(item._fadingdetails['value'], 42)


class TestFadeTrigger(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_trigger_called(self):
        item = _item(self.sh, path='myitem', value=5)
        item._fading = False
        trigger_calls = []
        item._sh.trigger = lambda path, fn, value=None: trigger_calls.append((path, fn))
        fade(item, 0)
        self.assertEqual(len(trigger_calls), 1)

    def test_trigger_receives_item_path(self):
        item = _item(self.sh, path='zone.dimmer', value=5)
        item._fading = False
        trigger_calls = []
        item._sh.trigger = lambda path, fn, value=None: trigger_calls.append((path, fn))
        fade(item, 0)
        self.assertEqual(trigger_calls[0][0], 'zone.dimmer')

    def test_trigger_receives_fadejob(self):
        item = _item(self.sh, value=5)
        item._fading = False
        trigger_calls = []
        item._sh.trigger = lambda path, fn, value=None: trigger_calls.append((path, fn))
        fade(item, 0)
        self.assertIs(trigger_calls[0][1], fadejob)

    def test_trigger_called_even_when_fading(self):
        item = _item(self.sh, value=5)
        item._fading = True
        trigger_calls = []
        item._sh.trigger = lambda path, fn, value=None: trigger_calls.append((path, fn))
        fade(item, 0, update=False)
        self.assertEqual(len(trigger_calls), 1)


class TestFadeDefaults(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def test_default_step_is_one(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertEqual(item._fadingdetails['step'], 1)

    def test_default_delta_is_one(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertEqual(item._fadingdetails['delta'], 1)

    def test_default_caller_is_none(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertIsNone(item._fadingdetails['caller'])

    def test_default_stop_fade_is_none(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertIsNone(item._fadingdetails['stop_fade'])

    def test_default_continue_fade_is_none(self):
        item = _item(self.sh, value=0)
        fade(item, 10)
        self.assertIsNone(item._fadingdetails['continue_fade'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
