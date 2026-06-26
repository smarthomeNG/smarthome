#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for hysteresis state machine (lib/item/item.py)

Planned extraction target: lib/item/_hysteresis.py

hysteresis_state() semantics (from source):
  -  1  (On)   = input >= upper threshold
  - -1  (Off)  = input <= lower threshold
  -  0  (Stay) = input between thresholds → no change to output
  - None       = _hysteresis_input is None (not configured)

  time.sleep(0.1) inside hysteresis_state() and hysteresis_data()
  is mocked out so tests run at full speed.

Coverage
--------
Config parsing:
  hysteresis_input path stored in _hysteresis_input
  upper / lower thresholds stored

_init_prerun wiring:
  input item gets output in _hysteresis_items_to_trigger
  missing input item → error logged, no crash

hysteresis_state():
  None when not configured
  above upper → 1 (On)
  below lower → -1 (Off)
  between thresholds → 0 (Stay)
  boundary conditions

hysteresis_data():
  returns dict with expected keys

Helper methods:
  _onoff(True) → 'On'
  _onoff(False) → 'Off'
  _get_hysterisis_state_string above/below/between

get_hysteresis_item_triggers():
  returns list; contains output item after _init_prerun
"""

import logging
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.config
from lib.item.items import Items
from lib.item._internal._hysteresis import _onoff, _get_hysteresis_state_string
from tests.mock.core import MockSmartHome
import tests.common as common


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _make_sh():
    _reset()
    return MockSmartHome()


def _load_items(sh, filename):
    path = os.path.join(common.BASE, 'tests', 'resources', filename + '.yaml')
    conf = lib.config.parse(path, None)
    for attr, value in conf.items():
        if isinstance(value, dict):
            child = lib.item.item.Item(sh, sh, attr, value)
            sh.items.add_item(attr, child)
            vars(sh)[attr] = child
    return conf


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh, path, c)
    sh.items.add_item(path, i)
    return i


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


class _HystBase(_Base):
    """Sets up the sensor_temp / heating_active pair from item_hysteresis.yaml."""

    def setUp(self):
        super().setUp()
        _load_items(self.sh, 'item_hysteresis')
        self.sensor = self.sh.items.return_item('sensor_temp')
        self.output = self.sh.items.return_item('heating_active')
        # Wire hysteresis linkage (normally done by load_itemdefinitions)
        self.output._init_prerun()


# ===========================================================================
# Config parsing
# ===========================================================================


class TestHysteresisConfigParsing(_Base):
    def setUp(self):
        super().setUp()
        _load_items(self.sh, 'item_hysteresis')

    def test_input_path_stored(self):
        output = self.sh.items.return_item('heating_active')
        self.assertEqual(output._hysteresis_input, 'sensor_temp')

    def test_upper_threshold_stored(self):
        output = self.sh.items.return_item('heating_active')
        self.assertIsNotNone(output._hysteresis_upper_threshold)

    def test_lower_threshold_stored(self):
        output = self.sh.items.return_item('heating_active')
        self.assertIsNotNone(output._hysteresis_lower_threshold)

    def test_unconfigured_item_has_none_input(self):
        plain = _item(self.sh, 'plain', 'bool')
        self.assertIsNone(plain._hysteresis_input)


# ===========================================================================
# _init_prerun wiring
# ===========================================================================


class TestHysteresisInitPrerun(_HystBase):
    def test_input_item_gets_output_in_trigger_list(self):
        self.assertIn(self.output, self.sensor._hysteresis_items_to_trigger)

    def test_missing_input_item_no_crash(self):
        bad_output = _item(
            self.sh,
            'bad_out',
            'bool',
            hysteresis_input='does.not.exist',
            hysteresis_upper_threshold='10',
            hysteresis_lower_threshold='5',
        )
        bad_output._init_prerun()  # must not raise

    def test_self_trigger_not_added(self):
        # Output item referencing itself as input
        self_ref = _item(
            self.sh,
            'self_ref',
            'bool',
            hysteresis_input='self_ref',
            hysteresis_upper_threshold='10',
            hysteresis_lower_threshold='5',
        )
        self_ref._init_prerun()
        self.assertNotIn(self_ref, self_ref._hysteresis_items_to_trigger)


# ===========================================================================
# hysteresis_state()
# ===========================================================================


class TestHysteresisState(_HystBase):
    """
    hysteresis_state() returns a string, not an int.
    Docstring values (1/-1/0) are outdated — actual returns:
      input > upper  → 'On'   (or 'Timer -> On')
      input < lower  → 'Off'  (or 'Timer -> Off')
      between        → 'Stay (On)' or 'Stay (Off)'
    """

    def _state(self, temp):
        self.sensor(temp)
        with patch('time.sleep'):  # skip the 0.1s guard sleep
            return self.output.hysteresis_state()

    def test_none_when_not_configured(self):
        plain = _item(self.sh, 'plain', 'bool')
        with patch('time.sleep'):
            self.assertIsNone(plain.hysteresis_state())

    def test_above_upper_returns_on_string(self):
        # upper=22; input 25 > 22 → 'On'
        state = self._state(25)
        self.assertIn('On', state)
        self.assertNotIn('Off', state)

    def test_below_lower_returns_off_string(self):
        # lower=18; input 10 < 18 → 'Off'
        state = self._state(10)
        self.assertIn('Off', state)
        self.assertNotIn('On', state)

    def test_between_thresholds_returns_stay_string(self):
        # 18 < 20 < 22 → 'Stay (...)'
        state = self._state(20)
        self.assertIn('Stay', state)

    def test_at_upper_boundary(self):
        # At exactly 22 (upper): > is strict, so 22 is NOT above upper → Stay
        state = self._state(22)
        self.assertIn('Stay', state)

    def test_at_lower_boundary(self):
        # At exactly 18 (lower): < is strict, so 18 is NOT below lower → Stay
        state = self._state(18)
        self.assertIn('Stay', state)

    def test_state_changes_with_input(self):
        s1 = self._state(25)  # above upper → On
        s2 = self._state(10)  # below lower → Off
        self.assertNotEqual(s1, s2)


# ===========================================================================
# hysteresis_data()
# ===========================================================================


class TestHysteresisData(_HystBase):
    def _data(self, temp):
        self.sensor(temp)
        with patch('time.sleep'):
            return self.output.hysteresis_data()

    def test_returns_dict(self):
        data = self._data(20)
        self.assertIsInstance(data, dict)

    def test_contains_upper_threshold(self):
        data = self._data(20)
        self.assertIn('upper_threshold', data)

    def test_contains_lower_threshold(self):
        data = self._data(20)
        self.assertIn('lower_threshold', data)

    def test_contains_input_value(self):
        self.sensor(15)
        data = self._data(15)
        self.assertIn('input', data)

    def test_contains_output_value(self):
        data = self._data(20)
        self.assertIn('output', data)

    def test_contains_state(self):
        data = self._data(20)
        self.assertIn('state', data)

    def test_input_value_matches_sensor(self):
        data = self._data(25)
        self.assertEqual(data['input'], 25)


# ===========================================================================
# Helper methods
# ===========================================================================


class TestHysteresisHelpers(_HystBase):
    def test_onoff_true_returns_on_string(self):
        result = _onoff(True)
        self.assertIn('On', result)

    def test_onoff_false_returns_off_string(self):
        result = _onoff(False)
        self.assertIn('Off', result)

    def test_state_string_above_upper(self):
        result = _get_hysteresis_state_string(self.output, 18, 22, 25)
        self.assertIn('On', result)

    def test_state_string_below_lower(self):
        result = _get_hysteresis_state_string(self.output, 18, 22, 10)
        self.assertIn('Off', result)

    def test_state_string_between(self):
        result = _get_hysteresis_state_string(self.output, 18, 22, 20)
        # Between thresholds → 'Stay (On)' or 'Stay (Off)'
        self.assertIn('Stay', result)


# ===========================================================================
# get_hysteresis_item_triggers
# ===========================================================================


class TestGetHysteresisItemTriggers(_HystBase):
    def test_returns_list(self):
        self.assertIsInstance(self.sensor.get_hysteresis_item_triggers(), list)

    def test_contains_output_item(self):
        self.assertIn(self.output, self.sensor.get_hysteresis_item_triggers())

    def test_plain_item_has_empty_trigger_list(self):
        plain = _item(self.sh, 'plain', 'bool')
        self.assertEqual(plain.get_hysteresis_item_triggers(), [])


if __name__ == '__main__':
    unittest.main()
