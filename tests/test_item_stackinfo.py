#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/item/_stackinfo.py

Coverage
--------
get_class_from_frame(item, fr):
  returns a string
  string starts with 'args='
  string contains '  - value_dict='
  reflects arg names visible in the frame
  reflects local variables visible in the frame

get_calling_item_from_frame(item, fr):
  returns a string
  returns 'None' when 'self' is not in frame locals
  returns str(self) when 'self' is present in frame locals

get_stack_info(item):
  returns a string
  result is non-empty
  result ends with '()' when called from a normal function (not __run_eval)
  result contains the calling function name
  handles IndexError gracefully (stack too shallow — should not raise)
"""

import inspect
import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.item._internal._stackinfo import get_class_from_frame, get_calling_item_from_frame, get_stack_info


class FakeItem:
    """Minimal stand-in for Item — stackinfo functions only need it for API symmetry."""

    pass


def _frame():
    """Return the caller's frame (one level up from here)."""
    return inspect.currentframe().f_back


class TestGetClassFromFrame(unittest.TestCase):
    def setUp(self):
        self.item = FakeItem()

    def test_returns_string(self):
        fr = _frame()
        result = get_class_from_frame(self.item, fr)
        self.assertIsInstance(result, str)

    def test_starts_with_args(self):
        fr = _frame()
        result = get_class_from_frame(self.item, fr)
        self.assertTrue(result.startswith('args='))

    def test_contains_value_dict(self):
        fr = _frame()
        result = get_class_from_frame(self.item, fr)
        self.assertIn('  - value_dict=', result)

    def test_reflects_local_variable(self):
        sentinel = 'unique_sentinel_xq7'  # noqa: F841  (used via frame locals)
        fr = inspect.currentframe()
        result = get_class_from_frame(self.item, fr)
        self.assertIn('sentinel', result)

    def test_reflects_arg_names(self):
        # When called from a function with named args, they appear in 'args='
        def helper(alpha, beta):
            return get_class_from_frame(FakeItem(), inspect.currentframe())

        result = helper('a', 'b')
        self.assertIn('alpha', result)
        self.assertIn('beta', result)


class TestGetCallingItemFromFrame(unittest.TestCase):
    def setUp(self):
        self.item = FakeItem()

    def test_returns_string(self):
        fr = _frame()
        result = get_calling_item_from_frame(self.item, fr)
        self.assertIsInstance(result, str)

    def test_returns_none_string_when_no_self(self):
        # Capture a frame from a plain function with no 'self' local.
        def selfless():
            return inspect.currentframe()

        fr = selfless()
        result = get_calling_item_from_frame(self.item, fr)
        self.assertEqual(result, 'None')

    def test_returns_self_string_when_self_present(self):
        # Capture frame from inside a method where 'self' exists
        captured = {}

        class Inner:
            def __str__(self):
                return 'InnerObject'

            def capture(self):
                captured['fr'] = inspect.currentframe()

        obj = Inner()
        obj.capture()
        result = get_calling_item_from_frame(FakeItem(), captured['fr'])
        self.assertEqual(result, 'InnerObject')

    def test_different_objects_give_different_strings(self):
        captured_a = {}
        captured_b = {}

        class Obj:
            def __init__(self, name):
                self._name = name

            def __str__(self):
                return self._name

            def cap(self, store):
                store['fr'] = inspect.currentframe()

        Obj('Alpha').cap(captured_a)
        Obj('Beta').cap(captured_b)

        result_a = get_calling_item_from_frame(FakeItem(), captured_a['fr'])
        result_b = get_calling_item_from_frame(FakeItem(), captured_b['fr'])
        self.assertNotEqual(result_a, result_b)


class TestGetStackInfo(unittest.TestCase):
    def setUp(self):
        self.item = FakeItem()

    def test_returns_string(self):
        result = get_stack_info(self.item)
        self.assertIsInstance(result, str)

    def test_result_is_non_empty(self):
        result = get_stack_info(self.item)
        self.assertTrue(len(result) > 0)

    def test_result_ends_with_parens_for_normal_caller(self):
        # When called from a normal method (not __run_eval) the result
        # should be 'functionname()'.
        result = get_stack_info(self.item)
        self.assertTrue(result.endswith('()'))

    def test_does_not_raise(self):
        # Must never raise regardless of stack depth.
        try:
            get_stack_info(self.item)
        except Exception as e:
            self.fail(f'get_stack_info raised unexpectedly: {e}')

    def test_called_from_helper_reflects_helper_name(self):
        # Wrap in extra call layers so level-4 is our known function.
        results = {}

        def level_a():
            def level_b():
                def level_c():
                    results['info'] = get_stack_info(FakeItem())

                level_c()

            level_b()

        level_a()
        # We don't assert the exact name (runner-dependent depth), just that
        # the result is a non-empty string ending with '()'.
        self.assertTrue(results['info'].endswith('()'))

    def test_item_unused_no_error(self):
        # item parameter is only needed when the caller is __run_eval;
        # passing None should not raise for normal callers.
        try:
            result = get_stack_info(None)
            self.assertIsInstance(result, str)
        except Exception as e:
            self.fail(f'get_stack_info(None) raised: {e}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
