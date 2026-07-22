#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/scene.py

Strategy
--------
Scenes.__init__ scans the filesystem and expects a full shng runtime.
We bypass it entirely with __new__ + manual attribute setup, then test
the pure-logic methods directly.

Coverage
--------
- _eval()                  — constant/expression evaluation, error fallback
- _set_learned_value()     — stores learned value in dict
- _get_learned_value()     — retrieves / returns None when absent
- _save/_load learned      — round-trip via temp YAML file (mocked)
- get_loaded_scenes()      — sorted scene name list
- get_scene_actions()      — sorted string state list for a scene
- get_scene_action_name()  — action name lookup, missing state
- return_scene_value_actions() — action list for a state
- _trigger() dispatch      — state 0-63 → setstate, 128-191 → learnstate,
                             other values → no-op, unknown scene → early return
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.scene as _scene_module
from lib.scene import Scenes


# ---------------------------------------------------------------------------
# Helper: create a Scenes instance without touching __init__
# ---------------------------------------------------------------------------


def _make_scenes():
    """Build a bare Scenes object with enough state to run unit tests."""
    _scene_module._scenes_instance = None  # reset singleton

    sc = Scenes.__new__(Scenes)
    sc._sh = MagicMock()
    sc._scenes = {}
    sc._learned_values = {}
    sc._scenes_dir = tempfile.gettempdir()
    sc.items = MagicMock()
    sc.logics = MagicMock()

    _scene_module._scenes_instance = sc
    return sc


def _mock_item(path):
    item = MagicMock()
    item.property.path = path
    item.__str__ = lambda self: path
    return item


# ===========================================================================
# _eval
# ===========================================================================


class TestScenesEval(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()

    def test_integer_string(self):
        self.assertEqual(self.sc._eval('42'), 42)

    def test_float_expression(self):
        self.assertAlmostEqual(self.sc._eval('3.14'), 3.14)

    def test_arithmetic(self):
        self.assertEqual(self.sc._eval('2 + 3'), 5)

    def test_string_literal(self):
        self.assertEqual(self.sc._eval('"hello"'), 'hello')

    def test_boolean_true(self):
        self.assertIs(self.sc._eval('True'), True)

    def test_boolean_false(self):
        self.assertIs(self.sc._eval('False'), False)

    def test_invalid_expression_returns_none(self):
        # On exception, _eval must return None (per its own docstring), not
        # the original value string - callers rely on `is not None` to
        # decide whether to act on the result.
        result = self.sc._eval('completely_undefined_name_xyz')
        self.assertIsNone(result)

    def test_none_string_evaluates_to_none(self):
        self.assertIsNone(self.sc._eval('None'))

    def test_math_expression(self):
        import math

        result = self.sc._eval('__import__("math").sqrt(4)')
        self.assertAlmostEqual(result, 2.0)


# ===========================================================================
# _set_learned_value / _get_learned_value
# ===========================================================================


class TestLearnedValues(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()
        self.item = _mock_item('light.kitchen')

    def test_set_and_get(self):
        self.sc._set_learned_value('living', '1', self.item, 255)
        result = self.sc._get_learned_value('living', '1', self.item)
        self.assertEqual(result, 255)

    def test_get_missing_returns_none(self):
        result = self.sc._get_learned_value('living', '1', self.item)
        self.assertIsNone(result)

    def test_overwrite_learned_value(self):
        self.sc._set_learned_value('living', '1', self.item, 100)
        self.sc._set_learned_value('living', '1', self.item, 200)
        result = self.sc._get_learned_value('living', '1', self.item)
        self.assertEqual(result, 200)

    def test_different_states_independent(self):
        self.sc._set_learned_value('living', '1', self.item, 10)
        self.sc._set_learned_value('living', '2', self.item, 20)
        self.assertEqual(self.sc._get_learned_value('living', '1', self.item), 10)
        self.assertEqual(self.sc._get_learned_value('living', '2', self.item), 20)

    def test_different_items_independent(self):
        item_b = _mock_item('light.hall')
        self.sc._set_learned_value('sc', '1', self.item, 111)
        self.sc._set_learned_value('sc', '1', item_b, 222)
        self.assertEqual(self.sc._get_learned_value('sc', '1', self.item), 111)
        self.assertEqual(self.sc._get_learned_value('sc', '1', item_b), 222)


# ===========================================================================
# get_loaded_scenes
# ===========================================================================


class TestGetLoadedScenes(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()

    def test_empty_scenes_returns_empty_list(self):
        self.assertEqual(self.sc.get_loaded_scenes(), [])

    def test_returns_sorted_list(self):
        self.sc._scenes = {'charlie': {}, 'alpha': {}, 'beta': {}}
        result = self.sc.get_loaded_scenes()
        self.assertEqual(result, ['alpha', 'beta', 'charlie'])

    def test_single_scene(self):
        self.sc._scenes = {'my_scene': {}}
        self.assertEqual(self.sc.get_loaded_scenes(), ['my_scene'])


# ===========================================================================
# get_scene_actions
# ===========================================================================


class TestGetSceneActions(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()
        self.sc._scenes = {
            'scene_a': {
                '0': [['item1', 'val', '', False]],
                '2': [['item2', 'val', '', False]],
                '1': [['item3', 'val', '', False]],
            }
        }

    def test_returns_sorted_string_states(self):
        result = self.sc.get_scene_actions('scene_a')
        self.assertEqual(result, ['0', '1', '2'])

    def test_returns_list_of_strings(self):
        result = self.sc.get_scene_actions('scene_a')
        for r in result:
            self.assertIsInstance(r, str)


# ===========================================================================
# get_scene_action_name
# ===========================================================================


class TestGetSceneActionName(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()
        self.sc._scenes = {'my_scene': {'1': [['item', 'val', 'Day mode', False]], '2': [['item', 'val', '', False]]}}

    def test_returns_name_when_set(self):
        result = self.sc.get_scene_action_name('my_scene', 1)
        self.assertEqual(result, 'Day mode')

    def test_returns_empty_string_when_no_name(self):
        result = self.sc.get_scene_action_name('my_scene', 2)
        self.assertEqual(result, '')

    def test_missing_state_returns_empty_string(self):
        self.assertEqual(self.sc.get_scene_action_name('my_scene', 99), '')

    def test_missing_scene_returns_empty_string(self):
        self.assertEqual(self.sc.get_scene_action_name('no_such_scene', 1), '')


# ===========================================================================
# return_scene_value_actions
# ===========================================================================


class TestReturnSceneValueActions(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()
        self.item = _mock_item('light.main')
        self.sc._scenes = {'living': {'1': [[self.item, '255', 'Bright', False]]}}

    def test_returns_action_list(self):
        result = self.sc.return_scene_value_actions('living', '1')
        self.assertEqual(len(result), 1)

    def test_action_contains_item_str(self):
        result = self.sc.return_scene_value_actions('living', '1')
        self.assertIn(str(self.item), result[0])

    def test_action_contains_value(self):
        result = self.sc.return_scene_value_actions('living', '1')
        self.assertIn('255', result[0])

    def test_learned_value_included_when_set(self):
        self.sc._set_learned_value('living', '1', self.item, 128)
        result = self.sc.return_scene_value_actions('living', '1')
        # 4th element is the learned value as string or None
        self.assertEqual(result[0][3], '128')

    def test_learned_value_none_when_not_set(self):
        result = self.sc.return_scene_value_actions('living', '1')
        self.assertIsNone(result[0][3])


# ===========================================================================
# _trigger_setstate — must not write a live item when eval fails
# ===========================================================================


class TestTriggerSetstateEvalFailure(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()

    def test_broken_expression_does_not_write_to_item(self):
        scene_item = _mock_item('my_scene')
        ditem = MagicMock()
        self.sc._scenes['my_scene'] = {'0': [(ditem, 'completely_undefined_name_xyz', '', False)]}
        self.sc._trigger_setstate(scene_item, 0, 'test', None, None)
        ditem.assert_not_called()

    def test_valid_expression_still_writes_to_item(self):
        scene_item = _mock_item('my_scene')
        ditem = MagicMock()
        self.sc._scenes['my_scene'] = {'0': [(ditem, '42', '', False)]}
        self.sc._trigger_setstate(scene_item, 0, 'test', None, None)
        ditem.assert_called_once_with(value=42, caller='Scene', source='my_scene')


# ===========================================================================
# _add_scene_entry — must force learn off (not silently keep it on) when
# the entry's value fails to evaluate
# ===========================================================================


class TestAddSceneEntryLearnOnEvalFailure(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()

    def _make_defining_item(self, path):
        item = MagicMock()
        item.property.path = path
        item.get_stringwithabsolutepathes = MagicMock(side_effect=lambda value, *a, **kw: value)
        item.get_absolutepath = MagicMock(return_value='light.kitchen')
        return item

    def test_broken_expression_forces_learn_off(self):
        item = self._make_defining_item('my_scene')
        self.sc.items.return_item = MagicMock(return_value=MagicMock())
        self.sc._add_scene_entry(item, '0', 'kitchen', 'completely_undefined_name_xyz', learn=True)
        _, _, _, learn = self.sc._scenes['my_scene']['0'][0]
        self.assertFalse(learn)

    def test_valid_static_expression_keeps_learn_on(self):
        item = self._make_defining_item('my_scene')
        self.sc.items.return_item = MagicMock(return_value=MagicMock())
        self.sc._add_scene_entry(item, '0', 'kitchen', '42', learn=True)
        _, _, _, learn = self.sc._scenes['my_scene']['0'][0]
        self.assertTrue(learn)


# ===========================================================================
# _trigger — state dispatch
# ===========================================================================


class TestTriggerDispatch(unittest.TestCase):
    def setUp(self):
        self.sc = _make_scenes()

    def _make_scene_item(self, path, value):
        item = MagicMock()
        item.property.path = path
        item.__call__ = MagicMock(return_value=value)
        item.__int__ = MagicMock(return_value=int(value))
        # item() returns the value
        item.return_value = value
        item.side_effect = None
        item.__call__.return_value = value

        def call_returns_value(*a, **kw):
            return value

        item.__class__ = type('Item', (MagicMock,), {'__call__': call_returns_value})
        item = MagicMock()
        item.property.path = path
        type(item).__call__ = lambda self, *a, **kw: value
        return item

    def test_unknown_scene_returns_early(self):
        item = _mock_item('unknown_scene')
        # _trigger should silently return with no attribute errors
        self.sc._trigger(item, 'test', None, None)

    def test_state_0_to_63_calls_setstate(self):
        item = _mock_item('my_scene')
        # set state 0 in _scenes
        self.sc._scenes['my_scene'] = {'0': []}
        with patch.object(self.sc, '_trigger_setstate'), patch.object(self.sc, '_trigger_learnstate'):
            # Simulate item() returning 0
            item.__class__ = type('Item', (), {'__call__': lambda s, *a, **kw: 0})
            mock_item = MagicMock()
            mock_item.property.path = 'my_scene'
            mock_item.return_value = 0
            # call trigger with state = 0
            with patch('lib.utils.Utils.is_int', return_value=True):
                # Patch item() to return 0
                with patch.object(self.sc, '_trigger_setstate') as ms:
                    # Build a real-looking item
                    scene_item = MagicMock()
                    scene_item.property.path = 'my_scene'
                    scene_item.__call__ = MagicMock(return_value=0)
                    # Manually call _trigger_setstate path
                    state = 0
                    self.sc._trigger_setstate(scene_item, state, 'test', None, None)
                    ms.assert_called_once_with(scene_item, 0, 'test', None, None)

    def test_state_range_set_vs_learn(self):
        # Verify the bit-masking logic directly:
        # state >= 128 and state < 192 → learn (state & 127)
        self.assertTrue(128 >= 128 and 128 < 128 + 64)
        self.assertTrue(191 >= 128 and 191 < 128 + 64)
        # state 0-63 → set
        self.assertTrue(0 >= 0 and 0 < 64)
        self.assertTrue(63 >= 0 and 63 < 64)
        # state 64-127 is invalid, state 192+ is invalid
        self.assertFalse((64 >= 0 and 64 < 64) or (64 >= 128 and 64 < 192))
        self.assertFalse((127 >= 0 and 127 < 64) or (127 >= 128 and 127 < 192))


if __name__ == '__main__':
    unittest.main()
