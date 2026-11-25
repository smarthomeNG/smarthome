#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for autotimer / cycle / crontab / scheduler wiring (lib/item/item.py)

Planned extraction target: lib/item/_autotimer.py

Coverage
--------
_parse_cycle_attribute:
  integer string → _cycle_time
  'seconds = value' string → _cycle_time + _cycle_value

_parse_autotimer_attribute (supplements test_item.py::test_item_autotimers):
  autotimer parsed to _autotimer_time and _autotimer_value (already tested)
  here we focus on the EXECUTION side

_init_start_scheduler:
  item with cycle → scheduler.add() called with cycle kwarg
  item with crontab → scheduler.add() called with cron kwarg
  plain item → scheduler.add() NOT called

Autotimer armed on value change (in __update):
  item with autotimer → scheduler.add() called when value changes
  caller='Autotimer' suppresses re-arming
  autotimer time None → warning, no crash

timer() / autotimer() public API:
  timer(60, value) → scheduler.add()
  autotimer(time, value) → sets internal attrs

remove_timer():
  → scheduler.remove() called
"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.config
from lib.item.items import Items
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


class RecordingScheduler:
    """Drop-in replacement for MockScheduler that records calls."""

    def __init__(self):
        self.calls = []

    def add(self, name, obj=None, prio=3, cron=None, cycle=None, value=None, offset=None, next=None, items=None):
        self.calls.append({'action': 'add', 'name': name, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next})

    def remove(self, name):
        self.calls.append({'action': 'remove', 'name': name})

    def adds(self):
        return [c for c in self.calls if c['action'] == 'add']

    def removes(self):
        return [c for c in self.calls if c['action'] == 'remove']

    def added_names(self):
        return [c['name'] for c in self.adds()]


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()


# ===========================================================================
# _parse_cycle_attribute
# ===========================================================================


class TestCycleConfigParsing(_Base):
    def test_integer_cycle_sets_cycle_time(self):
        item = _item(self.sh, 'cy', cycle='30')
        self.assertEqual(item._cycle_time, '30')

    def test_cycle_with_value_sets_both(self):
        item = _item(self.sh, 'cy2', cycle='60 = 99')
        # Duration string: time part = '60', value part = '99'
        self.assertIn('60', item._cycle_time)
        self.assertIn('99', str(item._cycle_value))

    def test_numeric_cycle_kept_as_number(self):
        item = _item(self.sh, 'cyn', cycle=30)
        self.assertEqual(item._cycle_time, 30)
        self.assertIsNone(item._cycle_value)

    def test_numeric_autotimer_kept_as_number(self):
        item = _item(self.sh, 'atn', autotimer=30)
        self.assertEqual(item._autotimer_time, 30)
        self.assertIsNone(item._autotimer_value)

    def test_no_cycle_leaves_cycle_time_none(self):
        item = _item(self.sh, 'nc')
        self.assertIsNone(item._cycle_time)

    def test_crontab_string_sets_crontab(self):
        item = _item(self.sh, 'cr', crontab='0 * * * *')
        self.assertIsNotNone(item._crontab)


# ===========================================================================
# _init_start_scheduler
# ===========================================================================


class TestInitStartScheduler(_Base):
    def test_cycle_registers_scheduler(self):
        item = _item(self.sh, 'cy', cycle='30')
        item._init_start_scheduler()
        self.assertGreater(len(self.recorder.adds()), 0)

    def test_cycle_scheduler_name_contains_path(self):
        item = _item(self.sh, 'my.item', cycle='30')
        item._init_start_scheduler()
        added = self.recorder.added_names()
        self.assertTrue(any('my.item' in n for n in added))

    def test_cycle_scheduler_call_has_cycle_kwarg(self):
        item = _item(self.sh, 'cy2', cycle='60')
        item._init_start_scheduler()
        add_calls = self.recorder.adds()
        self.assertTrue(any(c['cycle'] is not None for c in add_calls))

    def test_numeric_cycle_registers_scheduler(self):
        item = _item(self.sh, 'cyn', cycle=45)
        item._init_start_scheduler()
        self.assertEqual([c['cycle'] for c in self.recorder.adds()], [45])

    def test_crontab_registers_scheduler(self):
        item = _item(self.sh, 'cr', crontab='0 * * * *')
        item._init_start_scheduler()
        self.assertGreater(len(self.recorder.adds()), 0)

    def test_crontab_scheduler_call_has_cron_kwarg(self):
        item = _item(self.sh, 'cr2', crontab='0 * * * *')
        item._init_start_scheduler()
        add_calls = self.recorder.adds()
        self.assertTrue(any(c['cron'] is not None for c in add_calls))

    def test_plain_item_does_not_register_scheduler(self):
        item = _item(self.sh, 'plain')
        item._init_start_scheduler()
        self.assertEqual(len(self.recorder.adds()), 0)

    def test_autotimer_alone_does_not_register_cycle_scheduler(self):
        # autotimer items are armed in __update, NOT in _init_start_scheduler
        item = _item(self.sh, 'at', autotimer='5m = 42')
        item._init_start_scheduler()
        self.assertEqual(len(self.recorder.adds()), 0)


# ===========================================================================
# Autotimer armed on value change
# ===========================================================================


class TestAutotimerArmedOnChange(_Base):
    def test_autotimer_arms_scheduler_on_value_change(self):
        item = _item(self.sh, 'at', autotimer='5m = 42')
        item(1)  # triggers __update → autotimer fires
        names = self.recorder.added_names()
        self.assertTrue(any('Timer' in n for n in names))

    def test_numeric_autotimer_arms_scheduler_on_value_change(self):
        item = _item(self.sh, 'atn', autotimer=30)
        item(1)
        self.assertEqual(len(self.recorder.adds()), 1)

    def test_autotimer_scheduler_call_has_next_kwarg(self):
        item = _item(self.sh, 'at2', autotimer='5m = 42')
        item(1)
        add_calls = self.recorder.adds()
        timer_calls = [c for c in add_calls if 'Timer' in c['name']]
        self.assertTrue(any(c['next'] is not None for c in timer_calls))

    def test_autotimer_not_armed_when_caller_is_autotimer(self):
        item = _item(self.sh, 'at3', autotimer='5m = 42')
        self.recorder.calls.clear()
        item(1, caller='Autotimer')  # must NOT re-arm
        names = self.recorder.added_names()
        self.assertFalse(any('Timer' in n for n in names))

    def test_autotimer_uses_item_path_in_scheduler_name(self):
        item = _item(self.sh, 'my.timed.item', autotimer='60 = 0')
        item(1)
        names = self.recorder.added_names()
        self.assertTrue(any('my.timed.item' in n for n in names))

    def test_no_autotimer_no_scheduler_add_on_change(self):
        item = _item(self.sh, 'plain')
        item(1)
        # MockScheduler.add may be called for other reasons; check for -Timer suffix
        names = self.recorder.added_names()
        self.assertFalse(any('Timer' in n for n in names))


# ===========================================================================
# timer() public method
# ===========================================================================


class TestTimerPublicMethod(_Base):
    def test_timer_calls_scheduler_add(self):
        item = _item(self.sh, 'ti')
        item.timer(60, 'hello')
        self.assertGreater(len(self.recorder.adds()), 0)

    def test_timer_name_contains_path(self):
        item = _item(self.sh, 'path.item')
        item.timer(30, 0)
        names = self.recorder.added_names()
        self.assertTrue(any('path.item' in n for n in names))

    def test_timer_value_passed_to_scheduler(self):
        item = _item(self.sh, 'tv')
        item.timer(10, 99)
        add_calls = self.recorder.adds()
        # value is passed as dict {'value': ..., 'caller': ...}
        self.assertTrue(any(isinstance(c.get('value'), dict) and c['value'].get('value') == 99 for c in add_calls))


# ===========================================================================
# autotimer() public method
# ===========================================================================


class TestAutotimerPublicMethod(_Base):
    def test_autotimer_sets_internal_time_attr(self):
        # autotimer() only stores the config; scheduling happens in __update
        item = _item(self.sh, 'at')
        item.autotimer('2m', 99)
        self.assertEqual(item._autotimer_time, '2m')

    def test_autotimer_sets_internal_value_attr(self):
        item = _item(self.sh, 'at_v')
        item.autotimer('2m', 99)
        self.assertEqual(item._autotimer_value, 99)

    def test_autotimer_arms_scheduler_on_next_value_change(self):
        item = _item(self.sh, 'at_arm')
        item.autotimer('2m', 0)
        item(1)  # value change → scheduler armed
        self.assertTrue(any('Timer' in n for n in self.recorder.added_names()))

    def test_autotimer_none_disables(self):
        item = _item(self.sh, 'at2', autotimer='5m = 1')
        item.autotimer(None)
        # After disabling, _autotimer_time should be falsy
        self.assertFalse(item._autotimer_time)


# ===========================================================================
# remove_timer()
# ===========================================================================


class TestRemoveTimer(_Base):
    def test_remove_timer_calls_scheduler_remove(self):
        item = _item(self.sh, 'rt', autotimer='5m = 42')
        item(1)  # arm the timer first
        self.recorder.calls.clear()
        item.remove_timer()
        removes = self.recorder.removes()
        self.assertGreater(len(removes), 0)

    def test_remove_timer_name_contains_path(self):
        item = _item(self.sh, 'my.rt.item', autotimer='60 = 0')
        item(1)
        self.recorder.calls.clear()
        item.remove_timer()
        removed_names = [c['name'] for c in self.recorder.removes()]
        self.assertTrue(any('my.rt.item' in n for n in removed_names))


# ===========================================================================
# _cast_duration edge cases (supplements test_item.py::test_cast_duration)
# ===========================================================================


class TestCastDurationEdgeCases(_Base):
    def setUp(self):
        super().setUp()
        self.item = _item(self.sh, 'cd', autotimer='5m = 42')

    def test_plain_integer_string(self):
        self.assertEqual(self.item._cast_duration('120'), 120)

    def test_minutes(self):
        self.assertEqual(self.item._cast_duration('2m'), 120)

    def test_seconds_suffix(self):
        self.assertEqual(self.item._cast_duration('45s'), 45)

    def test_numeric_int(self):
        self.assertEqual(self.item._cast_duration(30), 30)

    def test_invalid_string_returns_false(self):
        self.assertFalse(self.item._cast_duration('not_a_time'))

    def test_none_returns_false(self):
        self.assertFalse(self.item._cast_duration(None))

    def test_empty_string_returns_false(self):
        result = self.item._cast_duration('')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
