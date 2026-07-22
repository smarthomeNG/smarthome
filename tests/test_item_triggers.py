#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Item trigger-registration methods:
  add_logic_trigger / remove_logic_trigger / get_logic_triggers
  add_method_trigger / remove_method_trigger / get_method_triggers
  get_item_triggers
  get_hysteresis_item_triggers

Coverage
--------
Logic triggers:
  add_logic_trigger → appended to list
  get_logic_triggers → returns the same list
  remove_logic_trigger → removes the entry
  remove non-existent logic → raises ValueError
  multiple logics → all stored; removed individually

Method triggers:
  add_method_trigger → appended to list
  get_method_triggers → returns the same list
  remove_method_trigger → removes the entry
  remove non-existent method → raises ValueError
  trigger fires on item change (integration)

Item triggers (eval_trigger wiring):
  get_item_triggers → returns _items_to_trigger list
  fresh item → empty list
  after _init_prerun wiring → target item appears in source's list

Hysteresis item triggers:
  get_hysteresis_item_triggers → returns _hysteresis_items_to_trigger
  fresh item → empty list
  after _init_prerun wiring → output appears in sensor's list
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


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh.items, path, c)
    sh.items.add_item(path, i)
    return i


def _load_items(sh, filename):
    path = os.path.join(common.BASE, 'tests', 'resources', filename + '.yaml')
    conf = lib.config.parse(path, None)
    for attr, value in conf.items():
        if isinstance(value, dict):
            child = lib.item.item.Item(sh, sh.items, attr, value)
            sh.items.add_item(attr, child)
            vars(sh)[attr] = child
    return conf


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


# ===========================================================================
# Logic triggers
# ===========================================================================


class TestLogicTriggers(_Base):
    def _make_logic(self, name='test_logic'):
        """Minimal logic-like object."""

        class _Logic:
            triggered = []

            def trigger(self, by, source, value):
                _Logic.triggered.append((by, source, value))

        logic = _Logic()
        logic.name = name
        return logic

    def test_fresh_item_has_empty_logic_trigger_list(self):
        item = _item(self.sh, 'a')
        self.assertEqual(item.get_logic_triggers(), [])

    def test_add_single_logic_trigger(self):
        item = _item(self.sh, 'a')
        logic = self._make_logic()
        item.add_logic_trigger(logic)
        self.assertIn(logic, item.get_logic_triggers())

    def test_add_multiple_logic_triggers(self):
        item = _item(self.sh, 'a')
        l1, l2, l3 = self._make_logic('l1'), self._make_logic('l2'), self._make_logic('l3')
        item.add_logic_trigger(l1)
        item.add_logic_trigger(l2)
        item.add_logic_trigger(l3)
        triggers = item.get_logic_triggers()
        self.assertIn(l1, triggers)
        self.assertIn(l2, triggers)
        self.assertIn(l3, triggers)
        self.assertEqual(len(triggers), 3)

    def test_remove_logic_trigger(self):
        item = _item(self.sh, 'a')
        logic = self._make_logic()
        item.add_logic_trigger(logic)
        item.remove_logic_trigger(logic)
        self.assertNotIn(logic, item.get_logic_triggers())

    def test_remove_one_of_several_logic_triggers(self):
        item = _item(self.sh, 'a')
        l1, l2 = self._make_logic('l1'), self._make_logic('l2')
        item.add_logic_trigger(l1)
        item.add_logic_trigger(l2)
        item.remove_logic_trigger(l1)
        self.assertNotIn(l1, item.get_logic_triggers())
        self.assertIn(l2, item.get_logic_triggers())

    def test_remove_nonexistent_logic_raises_valueerror(self):
        item = _item(self.sh, 'a')
        logic = self._make_logic()
        with self.assertRaises(ValueError):
            item.remove_logic_trigger(logic)

    def test_get_logic_triggers_returns_list(self):
        item = _item(self.sh, 'a')
        self.assertIsInstance(item.get_logic_triggers(), list)

    def test_add_same_logic_twice_stores_twice(self):
        # list.append has no uniqueness check
        item = _item(self.sh, 'a')
        logic = self._make_logic()
        item.add_logic_trigger(logic)
        item.add_logic_trigger(logic)
        self.assertEqual(item.get_logic_triggers().count(logic), 2)

    def test_logic_triggers_are_independent_per_item(self):
        a = _item(self.sh, 'a')
        b = _item(self.sh, 'b')
        logic = self._make_logic()
        a.add_logic_trigger(logic)
        self.assertNotIn(logic, b.get_logic_triggers())

    def test_logic_triggered_on_value_change(self):
        """Logic in trigger list fires when item value changes."""
        fired = []
        item = _item(self.sh, 'a')

        class _Logic:
            def trigger(self, by, source, value):
                fired.append(value)

        item.add_logic_trigger(_Logic())
        item(42)
        self.assertEqual(fired, [42])

    def test_logic_not_triggered_after_removal(self):
        fired = []
        item = _item(self.sh, 'a')

        class _Logic:
            def trigger(self, by, source, value):
                fired.append(value)

        logic = _Logic()
        item.add_logic_trigger(logic)
        item.remove_logic_trigger(logic)
        item(42)
        self.assertEqual(fired, [])

    def test_logic_removed_mid_iteration_does_not_skip_later_logics(self):
        """
        Regression test: __trigger_logics() used to iterate
        self.__logics_to_trigger directly (no snapshot) -- same failure mode
        as test_method_removed_mid_iteration_does_not_skip_later_methods,
        for the logic-trigger list.
        """
        fired = []
        item = _item(self.sh, 'a')

        class _Logic:
            def __init__(self, name):
                self.name = name

            def trigger(self, by, source, value):
                fired.append(self.name)

        l1, l2, l3, l4 = _Logic('l1'), _Logic('l2'), _Logic('l3'), _Logic('l4')

        class _RemovingLogic(_Logic):
            def trigger(self, by, source, value):
                super().trigger(by, source, value)
                item.remove_logic_trigger(l1)  # removes an already-visited entry

        l2 = _RemovingLogic('l2')

        for logic in (l1, l2, l3, l4):
            item.add_logic_trigger(logic)

        item(42)

        self.assertEqual(fired, ['l1', 'l2', 'l3', 'l4'])


# ===========================================================================
# Method triggers
# ===========================================================================


class TestMethodTriggers(_Base):
    def _make_method(self):
        calls = []

        def method(item, caller, source, dest):
            calls.append((caller, source))

        method.calls = calls
        return method

    def test_fresh_item_has_empty_method_trigger_list(self):
        item = _item(self.sh, 'a')
        self.assertEqual(item.get_method_triggers(), [])

    def test_add_single_method_trigger(self):
        item = _item(self.sh, 'a')
        m = self._make_method()
        item.add_method_trigger(m)
        self.assertIn(m, item.get_method_triggers())

    def test_add_multiple_method_triggers(self):
        item = _item(self.sh, 'a')
        m1, m2 = self._make_method(), self._make_method()
        item.add_method_trigger(m1)
        item.add_method_trigger(m2)
        triggers = item.get_method_triggers()
        self.assertIn(m1, triggers)
        self.assertIn(m2, triggers)

    def test_remove_method_trigger(self):
        item = _item(self.sh, 'a')
        m = self._make_method()
        item.add_method_trigger(m)
        item.remove_method_trigger(m)
        self.assertNotIn(m, item.get_method_triggers())

    def test_remove_one_of_several_method_triggers(self):
        item = _item(self.sh, 'a')
        m1, m2 = self._make_method(), self._make_method()
        item.add_method_trigger(m1)
        item.add_method_trigger(m2)
        item.remove_method_trigger(m1)
        self.assertNotIn(m1, item.get_method_triggers())
        self.assertIn(m2, item.get_method_triggers())

    def test_remove_nonexistent_method_raises_valueerror(self):
        item = _item(self.sh, 'a')
        m = self._make_method()
        with self.assertRaises(ValueError):
            item.remove_method_trigger(m)

    def test_get_method_triggers_returns_list(self):
        item = _item(self.sh, 'a')
        self.assertIsInstance(item.get_method_triggers(), list)

    def test_method_triggers_are_independent_per_item(self):
        a = _item(self.sh, 'a')
        b = _item(self.sh, 'b')
        m = self._make_method()
        a.add_method_trigger(m)
        self.assertNotIn(m, b.get_method_triggers())

    def test_method_called_on_value_change(self):
        called = []
        item = _item(self.sh, 'a')
        item.add_method_trigger(lambda i, c, s, d: called.append(c))
        item(99, 'TestCaller')
        self.assertIn('TestCaller', called)

    def test_method_not_called_after_removal(self):
        called = []
        item = _item(self.sh, 'a')

        def m(i, c, s, d):
            called.append(1)

        item.add_method_trigger(m)
        item.remove_method_trigger(m)
        item(99)
        self.assertEqual(called, [])

    def test_method_receives_correct_caller_and_source(self):
        received = []
        item = _item(self.sh, 'a')
        item.add_method_trigger(lambda i, c, s, d: received.append((c, s)))
        item(1, 'MyPlugin', 'my_source')
        self.assertEqual(received, [('MyPlugin', 'my_source')])

    def test_method_exception_does_not_crash_item(self):
        """A failing method trigger must not prevent the item value from being set."""
        item = _item(self.sh, 'a')
        item.add_method_trigger(lambda i, c, s, d: 1 / 0)
        item(42)  # should not raise
        self.assertEqual(item(), 42)

    def test_method_removed_mid_iteration_does_not_skip_later_methods(self):
        """
        Regression test: __update() used to iterate self.__methods_to_trigger
        directly (no snapshot). Removing an already-visited entry from within
        a still-running trigger callback (simulating a concurrent
        remove_method_trigger() call from another thread, e.g. a plugin
        deregistering during reload) shifts list positions under the
        for-loop's cursor and silently skips whatever trigger was next in
        line -- confirmed via plain-list iteration semantics independent of
        Item: removing an earlier element while iterating skips the element
        that shifts into the current cursor position.
        """
        calls = []
        item = _item(self.sh, 'a')

        def m1(i, c, s, d):
            calls.append('m1')

        def m2(i, c, s, d):
            calls.append('m2')
            item.remove_method_trigger(m1)  # removes an already-visited entry

        def m3(i, c, s, d):
            calls.append('m3')

        def m4(i, c, s, d):
            calls.append('m4')

        for m in (m1, m2, m3, m4):
            item.add_method_trigger(m)

        item(42)

        self.assertEqual(calls, ['m1', 'm2', 'm3', 'm4'])


# ===========================================================================
# get_item_triggers  (eval_trigger wiring)
# ===========================================================================


class TestGetItemTriggers(_Base):
    def test_fresh_item_has_empty_item_trigger_list(self):
        item = _item(self.sh, 'a')
        self.assertEqual(item.get_item_triggers(), [])

    def test_get_item_triggers_returns_list(self):
        item = _item(self.sh, 'a')
        self.assertIsInstance(item.get_item_triggers(), list)

    def test_item_triggers_populated_after_init_prerun(self):
        """
        _init_prerun() wires: source has eval_trigger pointing at target →
        source is appended to target._items_to_trigger ("when target changes,
        trigger source's eval").  So target.get_item_triggers() contains source.
        """
        target = _item(self.sh, 'target', eval='1')
        source = _item(self.sh, 'source', eval='sh.target()', eval_trigger='target')

        target._init_prerun()
        source._init_prerun()

        # target's trigger list should contain source (the eval-watcher)
        self.assertIn(source, target.get_item_triggers())

    def test_item_not_in_own_triggers(self):
        """An item with self-trigger is excluded (prevents infinite loop)."""
        item = _item(self.sh, 'a', eval='1', eval_trigger='a')
        item._init_prerun()
        self.assertNotIn(item, item.get_item_triggers())

    def test_two_sources_watching_same_target(self):
        """Two items with eval_trigger on the same target both appear in target's list."""
        target = _item(self.sh, 'target')
        src1 = _item(self.sh, 'src1', eval='sh.target()', eval_trigger='target')
        src2 = _item(self.sh, 'src2', eval='sh.target()', eval_trigger='target')
        target._init_prerun()
        src1._init_prerun()
        src2._init_prerun()
        self.assertIn(src1, target.get_item_triggers())
        self.assertIn(src2, target.get_item_triggers())


# ===========================================================================
# get_hysteresis_item_triggers
# ===========================================================================


class TestGetHysteresisItemTriggers(_Base):
    def test_fresh_item_has_empty_hysteresis_triggers(self):
        item = _item(self.sh, 'a')
        self.assertEqual(item.get_hysteresis_item_triggers(), [])

    def test_get_hysteresis_item_triggers_returns_list(self):
        item = _item(self.sh, 'a')
        self.assertIsInstance(item.get_hysteresis_item_triggers(), list)

    def test_hysteresis_trigger_wired_after_init_prerun(self):
        """
        After _init_prerun(), the sensor item should appear in the output
        item's _hysteresis_items_to_trigger.
        """
        sensor = _item(self.sh, 'sensor', 'num')
        output = _item(
            self.sh,
            'output',
            'bool',
            hysteresis_input='sensor',
            hysteresis_upper_threshold='22',
            hysteresis_lower_threshold='18',
        )
        sensor._init_prerun()
        output._init_prerun()

        self.assertIn(output, sensor.get_hysteresis_item_triggers())

    def test_non_hysteresis_item_not_in_triggers(self):
        sensor = _item(self.sh, 'sensor', 'num')
        plain = _item(self.sh, 'plain', 'num')
        sensor._init_prerun()
        plain._init_prerun()
        self.assertNotIn(plain, sensor.get_hysteresis_item_triggers())


if __name__ == '__main__':
    unittest.main()
