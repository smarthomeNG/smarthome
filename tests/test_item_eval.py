#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for eval / eval_trigger / on_change / on_update (lib/item/item.py)

Planned extraction target: lib/item/_eval.py

Coverage
--------
Config parsing:
  _parse_eval_attribute        eval string stored in _eval
  _parse_eval_trigger_list_attribute  trigger paths stored in _trigger
  _parse_on_xx_list_attribute  on_change/on_update dest + eval stored

_init_prerun (trigger wiring):
  eval_trigger 'source' → source._items_to_trigger contains target
  special eval keywords 'and','or','sum','avg','max','min' → _eval expanded
  self-trigger prevention

_init_run (initial eval):
  constant eval → item gets that value
  bad eval → item value unchanged, no crash
  value already restored by a plugin (changed_by not 'Init:*') → skipped (#804)

__run_eval:
  constant expression → value set
  expression referencing sh.other_item() → value from other item
  None-returning expression → value unchanged
  exception in expression → no crash

on_change execution:
  changing source fires on_change → target item gets new value
  same-value write does NOT fire on_change
  on_change with no dest evaluates expression only

on_update execution:
  every write fires on_update (including same-value)
  on_update with dest → target updated
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
    vars(sh)[path] = i
    return i


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


class _EvalBase(_Base):
    def setUp(self):
        super().setUp()
        _load_items(self.sh, 'item_eval')


# ===========================================================================
# Config parsing: _parse_eval_attribute
# ===========================================================================


class TestEvalConfigParsing(_EvalBase):
    def test_eval_string_stored_in_eval(self):
        item = self.sh.items.return_item('eval_constant')
        self.assertEqual(item._eval, '42')

    def test_eval_reference_item_stored(self):
        item = self.sh.items.return_item('target_eval')
        # eval = 'sh.source_num()' — stored after path expansion
        self.assertIn('source_num', item._eval)

    def test_no_eval_leaves_eval_none(self):
        item = self.sh.items.return_item('source_num')
        self.assertIsNone(item._eval)


# ===========================================================================
# Config parsing: _parse_eval_trigger_list_attribute
# ===========================================================================


class TestEvalTriggerConfigParsing(_EvalBase):
    def test_single_trigger_stored(self):
        item = self.sh.items.return_item('target_eval')
        self.assertIsNotNone(item._trigger)
        self.assertGreater(len(item._trigger), 0)

    def test_trigger_contains_source_path(self):
        item = self.sh.items.return_item('target_eval')
        self.assertTrue(any('source_num' in t for t in item._trigger))

    def test_multiple_triggers_stored(self):
        item = self.sh.items.return_item('combined_and')
        self.assertGreaterEqual(len(item._trigger), 2)

    def test_no_trigger_is_false_or_empty(self):
        item = self.sh.items.return_item('source_num')
        self.assertFalse(item._trigger)


# ===========================================================================
# Config parsing: _parse_on_xx_list_attribute
# ===========================================================================


class TestOnXxConfigParsing(_EvalBase):
    def test_on_change_dest_stored(self):
        item = self.sh.items.return_item('on_change_source')
        self.assertIsNotNone(item._on_change_dest_var)
        self.assertIn('on_change_target', item._on_change_dest_var)

    def test_on_change_eval_stored(self):
        item = self.sh.items.return_item('on_change_source')
        self.assertIsNotNone(item._on_change)
        self.assertIn('value', item._on_change)

    def test_on_update_dest_stored(self):
        item = self.sh.items.return_item('on_update_source')
        self.assertIn('on_update_target', item._on_update_dest_var)

    def test_no_on_change_leaves_attr_none_or_empty(self):
        item = self.sh.items.return_item('source_num')
        self.assertFalse(item._on_change)


# ===========================================================================
# _init_prerun: trigger wiring
# ===========================================================================


class TestInitPrerun(_EvalBase):
    def test_trigger_wires_source_to_target(self):
        source = self.sh.items.return_item('source_num')
        target = self.sh.items.return_item('target_eval')
        # Wire triggers
        target._init_prerun()
        self.assertIn(target, source._items_to_trigger)

    def test_self_trigger_not_added(self):
        source = self.sh.items.return_item('source_num')
        source._init_prerun()
        self.assertNotIn(source, source._items_to_trigger)

    def test_eval_and_keyword_expanded(self):
        item = self.sh.items.return_item('combined_and')
        item._init_prerun()
        self.assertIn(' and ', item._eval)

    def test_eval_sum_keyword_expanded(self):
        item = self.sh.items.return_item('combined_sum')
        item._init_prerun()
        self.assertIn('+', item._eval)

    def test_eval_avg_keyword_has_division(self):
        item = self.sh.items.return_item('combined_avg')
        item._init_prerun()
        self.assertIn('/', item._eval)

    def test_unknown_trigger_item_no_crash(self):
        # Item with trigger pointing to non-existent path — should log warning, not crash
        bad = _item(self.sh, 'bad_trigger', eval='sh.nonexistent()', eval_trigger='nonexistent.item.path')
        bad._init_prerun()  # must not raise


# ===========================================================================
# _init_run: initial eval execution
# ===========================================================================


class TestInitRun(_EvalBase):
    """
    _init_run() only fires (returns True) for items that have BOTH _trigger AND _eval.
    It schedules the eval via sh.trigger() — MockSmartHome.trigger() logs but does not
    actually execute the callback, so _value is unchanged after the call.
    """

    def test_returns_true_for_trigger_and_eval(self):
        target = self.sh.items.return_item('target_eval')
        result = target._init_run()
        self.assertTrue(result)

    def test_returns_false_for_eval_without_trigger(self):
        # eval_constant has eval but no eval_trigger
        item = self.sh.items.return_item('eval_constant')
        result = item._init_run()
        self.assertFalse(result)

    def test_returns_false_for_no_trigger_no_eval(self):
        item = self.sh.items.return_item('source_num')
        result = item._init_run()
        self.assertFalse(result)

    def test_value_unchanged_after_init_run_via_mock(self):
        # MockSmartHome.trigger() does not execute the callback, so value stays 0
        target = self.sh.items.return_item('target_eval')
        target._init_run()
        self.assertEqual(target._value, 0)  # unchanged — callback not executed

    def test_eval_runs_when_called_directly(self):
        # Direct __run_eval works independently of _init_run
        item = self.sh.items.return_item('eval_constant')
        item._Item__run_eval()
        self.assertEqual(item._value, 42)

    def test_returns_false_when_value_restored_by_plugin(self):
        # database plugin's 'database: init' restore (issue #804) - must not be re-evaled
        target = self.sh.items.return_item('target_eval')
        target.set(99, 'Database', source='DBInit')
        result = target._init_run()
        self.assertFalse(result)

    def test_returns_false_when_value_restored_without_source(self):
        # rrd plugin's item.set(value, 'RRDtool') has no source - must still be skipped
        target = self.sh.items.return_item('target_eval')
        target.set(7, 'RRDtool')
        result = target._init_run()
        self.assertFalse(result)

    def test_value_retained_when_init_run_skipped(self):
        target = self.sh.items.return_item('target_eval')
        target.set(99, 'Database', source='DBInit')
        target._init_run()
        self.assertEqual(target._value, 99)  # not overwritten by a skipped _init_run


# ===========================================================================
# __run_eval
# ===========================================================================


class TestRunEvalDirect(_Base):
    def test_constant_sets_value(self):
        item = _item(self.sh, 'ev', eval='2 + 3')
        item._Item__run_eval()
        self.assertEqual(item._value, 5)

    def test_reference_to_other_item(self):
        source = _item(self.sh, 'src')
        source(42)
        target = _item(self.sh, 'tgt', eval='sh.src()')
        target._Item__run_eval()
        self.assertEqual(target._value, 42)

    def test_none_returning_expression_skips_update(self):
        # item(value) on an eval item schedules the eval, not a direct set.
        # Use item.set() to establish the value, then verify __run_eval with
        # a None-returning expression leaves the value unchanged.
        item = _item(self.sh, 'ev_none', eval='None')
        item.set(99)  # direct set, bypasses eval path
        item._Item__run_eval()  # eval returns None → __update not called
        self.assertEqual(item._value, 99)  # still 99

    def test_exception_in_expression_no_crash(self):
        item = _item(self.sh, 'ev_bad', eval='undefined_name_xyz')
        item._Item__run_eval()  # must not raise

    def test_eval_caller_reflected_in_changed_by(self):
        item = _item(self.sh, 'ev_caller', eval='7')
        item._Item__run_eval()
        self.assertIn('Eval', item.changed_by())


# ===========================================================================
# on_change execution
# ===========================================================================


class TestOnChangeExecution(_Base):
    def setUp(self):
        super().setUp()
        self.target = _item(self.sh, 'tgt')
        self.source = _item(self.sh, 'src', on_change='tgt = value')

    def test_value_change_fires_on_change(self):
        self.source(42)
        self.assertEqual(self.target._value, 42)

    def test_second_different_value_fires_again(self):
        self.source(10)
        self.source(20)
        self.assertEqual(self.target._value, 20)

    def test_same_value_does_not_fire_on_change(self):
        self.source(5)
        self.target(0)  # reset target
        self.source(5)  # same value — on_change must NOT fire
        self.assertEqual(self.target._value, 0)

    def test_on_change_dest_gets_item_value(self):
        self.source(99)
        self.assertEqual(self.target._value, 99)

    def test_on_change_none_result_does_not_update_target(self):
        # on_change evaluates to None → target not touched
        src2 = _item(self.sh, 'src2', on_change='tgt = None')
        self.target(77)
        src2(1)
        self.assertEqual(self.target._value, 77)

    def test_on_change_missing_dest_item_no_crash(self):
        # Dest item path doesn't exist → error logged, no exception
        src3 = _item(self.sh, 'src3', on_change='does.not.exist = value')
        src3(1)  # must not raise


# ===========================================================================
# on_update execution
# ===========================================================================


class TestOnUpdateExecution(_Base):
    def setUp(self):
        super().setUp()
        self.target = _item(self.sh, 'upd_tgt')
        self.source = _item(self.sh, 'upd_src', on_update='upd_tgt = value')

    def test_value_change_fires_on_update(self):
        self.source(42)
        self.assertEqual(self.target._value, 42)

    def test_same_value_also_fires_on_update(self):
        self.source(5)
        self.target(0)  # reset
        self.source(5)  # same value — on_update STILL fires
        self.assertEqual(self.target._value, 5)

    def test_on_update_fires_twice_on_two_writes(self):
        call_count = [0]
        orig = self.target._Item__update

        def counting_update(value, *a, **kw):
            call_count[0] += 1
            orig(value, *a, **kw)

        self.target._Item__update = counting_update
        self.source(1)
        self.source(2)
        self.assertGreaterEqual(call_count[0], 2)

    def test_on_update_passes_current_value(self):
        self.source(77)
        self.assertEqual(self.target._value, 77)


if __name__ == '__main__':
    unittest.main()
