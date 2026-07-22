#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/item/property.py

Strategy
--------
Property is tightly coupled to Item (it holds a reference to the parent
item and delegates everything to item internals). Tests create real Item
objects through MockSmartHome so that all item internals are properly
initialised, then exercise every Property descriptor:

  - Read-only properties: verify they return the correct item attribute
    and that the setter logs an error without changing anything.
  - Read-write properties: verify both getter and setter paths, including
    type-error guards (non-bool for enforce_*, non-string for eval, etc.).
  - Composite properties: trigger, on_change/on_update, value.

Coverage
--------
attributes, defined_in,
enforce_updates, enforce_change,
eval, eval_unexpanded,
last_change, last_change_age, last_change_by,
last_update, last_update_age, last_update_by,
last_trigger, last_trigger_age, last_trigger_by,
last_value, prev_value,
prev_change, prev_change_age, prev_change_by,
prev_update, prev_update_age, prev_update_by,
prev_trigger, prev_trigger_age, prev_trigger_by,
name, description, remark, type, path,
on_change, on_change_unexpanded,
on_update, on_update_unexpanded,
trigger, trigger_unexpanded,
value, hysteresis_state,
_ro_error, _type_error, _cast_warning helper paths
"""

import logging
import os
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item
import lib.item.item
import lib.item.items
from tests.mock.core import MockSmartHome


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_items():
    """Reset Items class-level state (prevents bleeding between test files).

    lib.item.items and lib.item.item each hold their own _items_instance global.
    Both must be cleared so that subsequent test files get a fresh registry.
    """
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None  # separate global in item.py
    lib.item.items.Items._Items__items = []
    lib.item.items.Items._Items__item_dict = {}
    lib.item.items.Items._children = []
    lib.item.items.Items.plugin_attributes = {}
    lib.item.items.Items.plugin_attribute_prefixes = {}
    lib.item.items.Items.plugin_prefixes_tuple = None


def _make_sh():
    """Return a fresh MockSmartHome, resetting Items singleton state."""
    _reset_items()
    return MockSmartHome()


class _PropertyTestBase(unittest.TestCase):
    """Resets Items class-level state before AND after each test."""

    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset_items()


def _make_item(sh, path='test.item', itype='foo', **extra_conf):
    conf = {'type': itype}
    conf.update(extra_conf)
    return lib.item.item.Item(sh, sh, path, conf)


# ===========================================================================
# attributes
# ===========================================================================


class TestPropertyAttributes(_PropertyTestBase):
    def test_attributes_empty_when_no_conf(self):
        item = _make_item(self.sh)
        # 'type' is consumed during init and not stored in conf
        self.assertIsInstance(item.property.attributes, list)

    def test_attributes_contains_plugin_keys(self):
        item = _make_item(self.sh, my_plugin_attr='hello')
        self.assertIn('my_plugin_attr', item.property.attributes)

    def test_attributes_multiple_keys(self):
        item = _make_item(self.sh, attr_a='1', attr_b='2')
        attrs = item.property.attributes
        self.assertIn('attr_a', attrs)
        self.assertIn('attr_b', attrs)


# ===========================================================================
# defined_in (read-only)
# ===========================================================================


class TestPropertyDefinedIn(_PropertyTestBase):
    def test_defined_in_returns_filename(self):
        item = _make_item(self.sh)
        item._filename = '/path/to/items.yaml'
        self.assertEqual(item.property.defined_in, '/path/to/items.yaml')

    def test_defined_in_none_when_not_set(self):
        item = _make_item(self.sh)
        self.assertIsNone(item.property.defined_in)

    def test_defined_in_is_readonly(self):
        item = _make_item(self.sh)
        item._filename = 'original.yaml'
        item.property.defined_in = 'other.yaml'  # must be silently ignored
        self.assertEqual(item._filename, 'original.yaml')


# ===========================================================================
# enforce_updates
# ===========================================================================


class TestPropertyEnforceUpdates(_PropertyTestBase):
    def test_default_is_false(self):
        item = _make_item(self.sh)
        self.assertIs(item.property.enforce_updates, False)

    def test_set_true(self):
        item = _make_item(self.sh)
        item.property.enforce_updates = True
        self.assertIs(item.property.enforce_updates, True)

    def test_set_false(self):
        item = _make_item(self.sh)
        item.property.enforce_updates = True
        item.property.enforce_updates = False
        self.assertIs(item.property.enforce_updates, False)

    def test_set_non_bool_ignored(self):
        item = _make_item(self.sh)
        item.property.enforce_updates = 'yes'  # type error path
        self.assertIs(item.property.enforce_updates, False)  # unchanged


# ===========================================================================
# enforce_change
# ===========================================================================


class TestPropertyEnforceChange(_PropertyTestBase):
    def test_default_is_false(self):
        item = _make_item(self.sh)
        self.assertIs(item.property.enforce_change, False)

    def test_set_true(self):
        item = _make_item(self.sh)
        item.property.enforce_change = True
        self.assertIs(item.property.enforce_change, True)

    def test_set_non_bool_ignored(self):
        item = _make_item(self.sh)
        item.property.enforce_change = 42
        self.assertIs(item.property.enforce_change, False)


# ===========================================================================
# eval
# ===========================================================================


class TestPropertyEval(_PropertyTestBase):
    def test_eval_default_is_empty_string(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.eval, '')

    def test_set_eval_expression(self):
        item = _make_item(self.sh, itype='num')
        item.property.eval = '1 + 1'
        self.assertEqual(item.property.eval, '1 + 1')

    def test_set_empty_string_clears_eval(self):
        item = _make_item(self.sh, itype='num')
        item.property.eval = '1 + 1'
        item.property.eval = ''
        self.assertEqual(item.property.eval, '')
        self.assertIsNone(item._eval)

    def test_set_non_string_ignored(self):
        item = _make_item(self.sh, itype='num')
        item.property.eval = 42  # type error path — no exception, just logged
        self.assertEqual(item.property.eval, '')


# ===========================================================================
# name
# ===========================================================================


class TestPropertyName(_PropertyTestBase):
    def test_default_name_is_path(self):
        item = _make_item(self.sh, 'my.item')
        self.assertEqual(item.property.name, 'my.item')

    def test_set_name_string(self):
        item = _make_item(self.sh)
        item.property.name = 'My Custom Name'
        self.assertEqual(item.property.name, 'My Custom Name')

    def test_set_empty_name_uses_path(self):
        item = _make_item(self.sh, 'a.b')
        item.property.name = 'Custom'
        item.property.name = ''
        self.assertEqual(item.property.name, 'a.b')

    def test_set_non_string_casts_to_str(self):
        item = _make_item(self.sh)
        item.property.name = 42  # triggers _cast_warning, then coerces
        self.assertEqual(item.property.name, '42')


# ===========================================================================
# description / remark (read-only)
# ===========================================================================


class TestPropertyDescriptionRemark(_PropertyTestBase):
    def test_description_default_none(self):
        item = _make_item(self.sh)
        self.assertIsNone(item.property.description)

    def test_description_is_readonly(self):
        item = _make_item(self.sh)
        item._description = 'A description'
        item.property.description = 'changed'  # silently ignored
        self.assertEqual(item._description, 'A description')

    def test_remark_default_none(self):
        item = _make_item(self.sh)
        self.assertIsNone(item.property.remark)

    def test_remark_is_readonly(self):
        item = _make_item(self.sh)
        item._remark = 'a remark'
        item.property.remark = 'changed'
        self.assertEqual(item._remark, 'a remark')


# ===========================================================================
# type (read-only)
# ===========================================================================


class TestPropertyType(_PropertyTestBase):
    def test_type_reflects_item_type(self):
        item = _make_item(self.sh, itype='num')
        self.assertEqual(item.property.type, 'num')

    def test_type_foo(self):
        item = _make_item(self.sh, itype='foo')
        self.assertEqual(item.property.type, 'foo')

    def test_type_is_readonly(self):
        item = _make_item(self.sh, itype='bool')
        item.property.type = 'num'  # silently ignored
        self.assertEqual(item._type, 'bool')


# ===========================================================================
# path (read-only)
# ===========================================================================


class TestPropertyPath(_PropertyTestBase):
    def test_path_matches_creation_path(self):
        item = _make_item(self.sh, 'floor.room.light')
        self.assertEqual(item.property.path, 'floor.room.light')

    def test_path_is_readonly(self):
        item = _make_item(self.sh, 'a.b.c')
        item.property.path = 'x.y.z'  # silently ignored
        self.assertEqual(item._path, 'a.b.c')


# ===========================================================================
# value
# ===========================================================================


class TestPropertyValue(_PropertyTestBase):
    def test_value_get_initial_num(self):
        item = _make_item(self.sh, itype='num')
        self.assertEqual(item.property.value, 0)

    def test_value_get_initial_bool(self):
        item = _make_item(self.sh, itype='bool')
        self.assertIs(item.property.value, False)

    def test_value_get_initial_str(self):
        item = _make_item(self.sh, itype='str')
        self.assertEqual(item.property.value, '')

    def test_value_set_triggers_item_call(self):
        item = _make_item(self.sh, itype='num')
        item.property.value = 42
        self.assertEqual(item._value, 42)

    def test_value_get_returns_deep_copy(self):
        item = _make_item(self.sh, itype='list')
        item(([1, 2, 3]))
        copy = item.property.value
        copy.append(99)
        self.assertEqual(item._value, [1, 2, 3])  # original unchanged


# ===========================================================================
# last_change / last_change_age / last_change_by (read-only)
# ===========================================================================


class TestPropertyLastChange(_PropertyTestBase):
    def test_last_change_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_change, datetime.datetime)

    def test_last_change_age_is_float(self):
        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_change_age, float)
        self.assertGreaterEqual(item.property.last_change_age, 0)

    def test_last_change_by_is_string(self):
        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_change_by, str)

    def test_last_change_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        orig = item.property.last_change
        item.property.last_change = 'ignored'
        self.assertEqual(item.property.last_change, orig)

    def test_last_change_age_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        item.property.last_change_age = 999
        self.assertNotEqual(item.property.last_change_age, 999)

    def test_last_change_by_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        item.property.last_change_by = 'hacker'
        self.assertNotEqual(item.property.last_change_by, 'hacker')


# ===========================================================================
# last_update / last_update_age / last_update_by (read-only)
# ===========================================================================


class TestPropertyLastUpdate(_PropertyTestBase):
    def test_last_update_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_update, datetime.datetime)

    def test_last_update_age_nonnegative(self):
        item = _make_item(self.sh, itype='num')
        self.assertGreaterEqual(item.property.last_update_age, 0)

    def test_last_update_by_is_string(self):
        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_update_by, str)

    def test_all_readonly(self):
        item = _make_item(self.sh, itype='num')
        for attr in ('last_update', 'last_update_age', 'last_update_by'):
            setattr(item.property, attr, 'x')
            # Value must be unchanged (or at least not 'x')
            self.assertNotEqual(getattr(item.property, attr), 'x')


# ===========================================================================
# last_trigger / last_trigger_age / last_trigger_by (read-only)
# ===========================================================================


class TestPropertyLastTrigger(_PropertyTestBase):
    def test_last_trigger_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_trigger, datetime.datetime)

    def test_last_trigger_age_nonnegative(self):
        item = _make_item(self.sh, itype='num')
        self.assertGreaterEqual(item.property.last_trigger_age, 0)

    def test_last_trigger_by_is_string(self):
        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.last_trigger_by, str)

    def test_all_readonly(self):
        item = _make_item(self.sh, itype='num')
        for attr in ('last_trigger', 'last_trigger_age', 'last_trigger_by'):
            setattr(item.property, attr, 'x')
            self.assertNotEqual(getattr(item.property, attr), 'x')


# ===========================================================================
# prev_value / prev_change / prev_update / prev_trigger (read-only)
# ===========================================================================


class TestPropertyPrevious(_PropertyTestBase):
    def test_prev_value_after_two_sets(self):
        # Sequence: init→0, item(10), item(20)
        # __last_value tracks the value *before* current; __prev_value is one further back.
        # After two calls: __prev_value = 0 (the initial value), __last_value = 10.
        item = _make_item(self.sh, itype='num')
        item(10)
        item(20)
        self.assertEqual(item.property.prev_value, 0)  # initial num default

    def test_prev_value_after_three_sets(self):
        item = _make_item(self.sh, itype='num')
        item(10)
        item(20)
        item(30)
        self.assertEqual(item.property.prev_value, 10)

    def test_prev_change_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.prev_change, datetime.datetime)

    def test_prev_change_age_nonnegative(self):
        item = _make_item(self.sh, itype='num')
        self.assertGreaterEqual(item.property.prev_change_age, 0)

    def test_prev_change_by_is_string(self):
        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.prev_change_by, str)

    def test_prev_update_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.prev_update, datetime.datetime)

    def test_prev_trigger_is_datetime(self):
        import datetime

        item = _make_item(self.sh, itype='num')
        self.assertIsInstance(item.property.prev_trigger, datetime.datetime)

    def test_prev_value_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        item.property.prev_value = 999
        self.assertNotEqual(item.property.prev_value, 999)

    def test_prev_change_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        orig = item.property.prev_change
        item.property.prev_change = 'x'
        self.assertEqual(item.property.prev_change, orig)


# ===========================================================================
# last_value (read-only)
# ===========================================================================


class TestPropertyLastValue(_PropertyTestBase):
    def test_last_value_after_set(self):
        item = _make_item(self.sh, itype='num')
        item(55)
        item(66)
        self.assertEqual(item.property.last_value, 55)

    def test_last_value_is_readonly(self):
        item = _make_item(self.sh, itype='num')
        item.property.last_value = 999
        self.assertNotEqual(item.property.last_value, 999)


# ===========================================================================
# trigger
# ===========================================================================


class TestPropertyTrigger(_PropertyTestBase):
    def test_trigger_default_empty(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.trigger, [])

    def test_set_trigger_list(self):
        item = _make_item(self.sh)
        item.property.trigger = ['other.item']
        self.assertEqual(item.property.trigger, ['other.item'])

    def test_set_empty_list_clears_trigger(self):
        item = _make_item(self.sh)
        item.property.trigger = ['other.item']
        item.property.trigger = []
        self.assertEqual(item.property.trigger, [])
        self.assertIs(item._trigger, False)

    def test_set_non_list_ignored(self):
        item = _make_item(self.sh)
        item.property.trigger = 'other.item'  # type error path
        self.assertEqual(item.property.trigger, [])

    def test_set_list_with_non_string_ignored(self):
        item = _make_item(self.sh)
        item.property.trigger = [42, 'valid']  # mixed: type error
        self.assertEqual(item.property.trigger, [])


# ===========================================================================
# hysteresis_state (read-only)
# ===========================================================================


class TestPropertyHysteresisState(_PropertyTestBase):
    def test_hysteresis_state_none_when_no_input_configured(self):
        # When _hysteresis_input is None (default), hysteresis_state() returns None.
        item = _make_item(self.sh, itype='bool')
        self.assertIsNone(item.property.hysteresis_state)


# ===========================================================================
# on_change / on_update read-only getters
# ===========================================================================


class TestPropertyOnChangeUpdate(_PropertyTestBase):
    def test_on_change_default_empty_list(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.on_change, [])

    def test_on_update_default_empty_list(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.on_update, [])

    def test_on_change_is_readonly(self):
        item = _make_item(self.sh)
        item.property.on_change = ['x']  # silently ignored
        self.assertEqual(item.property.on_change, [])

    def test_on_update_is_readonly(self):
        item = _make_item(self.sh)
        item.property.on_update = ['x']
        self.assertEqual(item.property.on_update, [])

    def test_on_change_unexpanded_default_empty(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.on_change_unexpanded, [])

    def test_on_update_unexpanded_default_empty(self):
        item = _make_item(self.sh)
        self.assertEqual(item.property.on_update_unexpanded, [])


# ===========================================================================
# _unexpanded setters — regression test
# ===========================================================================
#
# eval_unexpanded/on_change_unexpanded/on_update_unexpanded/trigger_unexpanded
# setters used to call self._item._process_eval() / _process_on_xx_list() /
# _process_trigger_list(), none of which exist on Item - guaranteed
# AttributeError on every call. Only the getters were covered above; these
# setters were never exercised, so the break went unnoticed.


class TestUnexpandedSetters(_PropertyTestBase):
    def test_set_eval_unexpanded_does_not_raise_and_updates_value(self):
        item = _make_item(self.sh, itype='num')
        item.property.eval_unexpanded = '1 + 1'
        self.assertEqual(item.property.eval_unexpanded, '1 + 1')
        self.assertEqual(item._eval, '1 + 1')

    def test_set_on_change_unexpanded_does_not_raise_and_updates_value(self):
        item = _make_item(self.sh)
        item.property.on_change_unexpanded = 'value + 1'
        self.assertEqual(item._on_change_unexpanded, ['value + 1'])

    def test_set_on_update_unexpanded_does_not_raise_and_updates_value(self):
        item = _make_item(self.sh)
        item.property.on_update_unexpanded = 'value + 1'
        self.assertEqual(item._on_update_unexpanded, ['value + 1'])

    def test_set_trigger_unexpanded_does_not_raise_and_updates_value(self):
        item = _make_item(self.sh)
        item.property.trigger_unexpanded = 'other.item'
        self.assertEqual(item.property.trigger_unexpanded, ['other.item'])
        self.assertEqual(item._trigger, ['other.item'])


class TestUnexpandedSettersReleaseLockOnException(_PropertyTestBase):
    """
    Regression test: these setters used to acquire item._lock with a bare
    acquire()/release() pair, no try/finally. If the underlying _parse_*
    call raised, release() was skipped and the lock leaked. Since
    item._lock is an RLock, checking "is it free" from the same thread
    that (maybe) leaked it is meaningless - the owning thread can always
    re-acquire an RLock regardless of whether it released it - so these
    checks run from a separate thread.
    """

    def _assert_lock_is_free(self, item):
        result = {}

        def check():
            result['acquired'] = item._lock.acquire(timeout=0.2)
            if result['acquired']:
                item._lock.release()

        t = threading.Thread(target=check)
        t.start()
        t.join(timeout=2)
        self.assertTrue(result.get('acquired'), 'item._lock was left held after the setter raised')

    def test_eval_unexpanded_releases_lock_if_parse_raises(self):
        item = _make_item(self.sh, itype='num')
        with patch.object(item, '_parse_eval_attribute', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                item.property.eval_unexpanded = '1 + 1'
        self._assert_lock_is_free(item)

    def test_on_change_unexpanded_releases_lock_if_parse_raises(self):
        item = _make_item(self.sh)
        with patch.object(item, '_parse_on_xx_list_attribute', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                item.property.on_change_unexpanded = 'value + 1'
        self._assert_lock_is_free(item)

    def test_on_update_unexpanded_releases_lock_if_parse_raises(self):
        item = _make_item(self.sh)
        with patch.object(item, '_parse_on_xx_list_attribute', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                item.property.on_update_unexpanded = 'value + 1'
        self._assert_lock_is_free(item)

    def test_trigger_unexpanded_releases_lock_if_parse_raises(self):
        item = _make_item(self.sh)
        with patch.object(item, '_parse_eval_trigger_list_attribute', side_effect=RuntimeError('boom')):
            with self.assertRaises(RuntimeError):
                item.property.trigger_unexpanded = 'other.item'
        self._assert_lock_is_free(item)


if __name__ == '__main__':
    unittest.main()
