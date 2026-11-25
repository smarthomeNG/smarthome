#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/item/helpers.py

Coverage
--------
Cast functions:
  cast_str, cast_list, cast_dict, cast_foo, cast_bool,
  cast_scene, cast_num, cast_timestamp, cast_datetime

Duration-value string helpers:
  split_duration_value_string, join_duration_value_string

JSON / cache helpers:
  json_serialize, json_obj_hook, cache_read, cache_write
"""

import collections
import datetime
import json
import logging
import os
import pickle
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.item.helpers import (
    cast_str,
    cast_list,
    cast_dict,
    cast_foo,
    cast_bool,
    cast_scene,
    cast_num,
    cast_timestamp,
    cast_datetime,
    split_duration_value_string,
    join_duration_value_string,
    json_serialize,
    json_obj_hook,
    cache_read,
    cache_write,
)
from lib.constants import CACHE_JSON, CACHE_PICKLE, ATTRIBUTE_SEPARATOR

COMPAT_DEFAULT = 'latest'


# ===========================================================================
# cast_str
# ===========================================================================


class TestCastStr(unittest.TestCase):
    def test_int_to_str(self):
        self.assertEqual(cast_str(42), '42')

    def test_float_to_str(self):
        self.assertEqual(cast_str(3.14), '3.14')

    def test_str_passthrough(self):
        self.assertEqual(cast_str('hello'), 'hello')

    def test_empty_string(self):
        self.assertEqual(cast_str(''), '')

    def test_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_str([1, 2, 3])

    def test_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_str({'a': 1})

    def test_none_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_str(None)

    def test_bool_to_str(self):
        # bool is a subclass of int, so True → '1', False → '0'
        self.assertIn(cast_str(True), ('True', '1'))


# ===========================================================================
# cast_list
# ===========================================================================


class TestCastList(unittest.TestCase):
    def test_list_passthrough(self):
        self.assertEqual(cast_list([1, 2, 3]), [1, 2, 3])

    def test_empty_list(self):
        self.assertEqual(cast_list([]), [])

    def test_string_literal_list(self):
        self.assertEqual(cast_list('[1, 2, 3]'), [1, 2, 3])

    def test_string_literal_nested(self):
        self.assertEqual(cast_list("['a', 'b']"), ['a', 'b'])

    def test_plain_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_list('hello')

    def test_int_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_list(42)

    def test_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_list({'a': 1})


# ===========================================================================
# cast_dict
# ===========================================================================


class TestCastDict(unittest.TestCase):
    def test_dict_passthrough(self):
        self.assertEqual(cast_dict({'a': 1}), {'a': 1})

    def test_empty_dict(self):
        self.assertEqual(cast_dict({}), {})

    def test_string_literal_dict(self):
        self.assertEqual(cast_dict("{'x': 10, 'y': 20}"), {'x': 10, 'y': 20})

    def test_plain_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_dict('hello')

    def test_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_dict([1, 2, 3])

    def test_int_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_dict(42)


# ===========================================================================
# cast_foo
# ===========================================================================


class TestCastFoo(unittest.TestCase):
    def test_int_passthrough(self):
        self.assertEqual(cast_foo(42), 42)

    def test_none_passthrough(self):
        self.assertIsNone(cast_foo(None))

    def test_list_passthrough(self):
        self.assertEqual(cast_foo([1, 2]), [1, 2])

    def test_string_passthrough(self):
        self.assertEqual(cast_foo('abc'), 'abc')


# ===========================================================================
# cast_bool
# ===========================================================================


class TestCastBool(unittest.TestCase):
    def test_true_bool(self):
        self.assertIs(cast_bool(True), True)

    def test_false_bool(self):
        self.assertIs(cast_bool(False), False)

    def test_int_1(self):
        self.assertIs(cast_bool(1), True)

    def test_int_0(self):
        self.assertIs(cast_bool(0), False)

    def test_float_1(self):
        self.assertIs(cast_bool(1.0), True)

    def test_float_0(self):
        self.assertIs(cast_bool(0.0), False)

    def test_int_2_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_bool(2)

    def test_str_true_variants(self):
        for v in ['1', 'true', 'True', 'TRUE', 'yes', 'on']:
            self.assertIs(cast_bool(v), True, msg=f'Failed for {v!r}')

    def test_str_false_variants(self):
        for v in ['0', 'false', 'False', 'FALSE', 'no', 'off', '']:
            self.assertIs(cast_bool(v), False, msg=f'Failed for {v!r}')

    def test_str_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_bool('maybe')

    def test_list_raises_type_error(self):
        with self.assertRaises(TypeError):
            cast_bool([])

    def test_none_raises_type_error(self):
        with self.assertRaises(TypeError):
            cast_bool(None)


# ===========================================================================
# cast_scene
# ===========================================================================


class TestCastScene(unittest.TestCase):
    def test_int_passthrough(self):
        self.assertEqual(cast_scene(3), 3)

    def test_str_to_int(self):
        self.assertEqual(cast_scene('5'), 5)

    def test_float_to_int(self):
        self.assertEqual(cast_scene(2.9), 2)


# ===========================================================================
# cast_num
# ===========================================================================


class TestCastNum(unittest.TestCase):
    def test_empty_string_returns_zero(self):
        self.assertEqual(cast_num(''), 0)

    def test_whitespace_string_returns_zero(self):
        self.assertEqual(cast_num('  '), 0)

    def test_int_string(self):
        self.assertEqual(cast_num('42'), 42)
        self.assertIsInstance(cast_num('42'), int)

    def test_float_string(self):
        self.assertAlmostEqual(cast_num('3.14'), 3.14)
        self.assertIsInstance(cast_num('3.14'), float)

    def test_float_passthrough(self):
        self.assertEqual(cast_num(3.14), 3.14)
        self.assertIsInstance(cast_num(3.14), float)

    def test_int_via_int_cast(self):
        self.assertEqual(cast_num(7), 7)
        self.assertIsInstance(cast_num(7), int)

    def test_invalid_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_num('abc')

    def test_none_raises_value_error(self):
        with self.assertRaises((ValueError, TypeError, AttributeError)):
            cast_num(None)


# ===========================================================================
# cast_timestamp  (int/float path only — no Shtime dependency)
# ===========================================================================


class TestCastTimestampSimple(unittest.TestCase):
    def test_int_passthrough(self):
        self.assertEqual(cast_timestamp(1000), 1000)

    def test_float_passthrough(self):
        self.assertAlmostEqual(cast_timestamp(1234567890.5), 1234567890.5)

    def test_invalid_type_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_timestamp(None)


class TestCastTimestampWithShtime(unittest.TestCase):
    """Tests that need a running Shtime instance."""

    def setUp(self):
        from lib.shtime import Shtime

        if Shtime.get_instance() is None:
            from tests.mock.core import MockSmartHome

            self._sh = MockSmartHome()

    def test_datetime_to_timestamp(self):
        from lib.shtime import Shtime

        Shtime.get_instance()  # ensure singleton is initialised
        dt = datetime.datetime.now(tz=datetime.timezone.utc)
        ts = cast_timestamp(dt)
        self.assertIsInstance(ts, float)

    def test_iso_string_to_timestamp(self):
        result = cast_timestamp('2024-06-01T12:00:00')
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)


# ===========================================================================
# cast_datetime
# ===========================================================================


class TestCastDatetime(unittest.TestCase):
    def test_datetime_passthrough(self):
        dt = datetime.datetime(2024, 6, 1, 12, 0, 0)
        self.assertEqual(cast_datetime(dt), dt)

    def test_none_returns_none(self):
        self.assertIsNone(cast_datetime(None))

    def test_iso_string(self):
        result = cast_datetime('2024-06-01T12:00:00')
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)
        self.assertEqual(result.day, 1)

    def test_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            cast_datetime('not-a-date')

    def test_invalid_type_raises_value_error(self):
        with self.assertRaises((ValueError, TypeError, AttributeError)):
            cast_datetime([1, 2, 3])


# ===========================================================================
# split_duration_value_string
# ===========================================================================


class TestSplitDurationValueString(unittest.TestCase):
    def test_separator_syntax(self):
        value = f'5m {ATTRIBUTE_SEPARATOR} 42'
        time, val, compat = split_duration_value_string(value, COMPAT_DEFAULT)
        self.assertEqual(time, '5m')
        self.assertEqual(val, '42')
        self.assertEqual(compat, COMPAT_DEFAULT)

    def test_equals_syntax(self):
        time, val, compat = split_duration_value_string('5m = 42', COMPAT_DEFAULT)
        self.assertEqual(time.strip(), '5m')
        self.assertEqual(val, '42')

    def test_time_only(self):
        time, val, compat = split_duration_value_string('10s', COMPAT_DEFAULT)
        self.assertEqual(time, '10s')
        self.assertIsNone(val)

    def test_number_is_time_only(self):
        for number in (60, 2.5):
            with self.subTest(number=number):
                time, val, compat = split_duration_value_string(number, COMPAT_DEFAULT)
                self.assertEqual(time, number)
                self.assertIsNone(val)
                self.assertEqual(compat, COMPAT_DEFAULT)

    def test_compat_from_default_when_absent(self):
        time, val, compat = split_duration_value_string('10s', 'latest')
        self.assertEqual(compat, 'latest')

    def test_separator_with_compat(self):
        value = f'5m {ATTRIBUTE_SEPARATOR} 42 {ATTRIBUTE_SEPARATOR} compat_1.2'
        time, val, compat = split_duration_value_string(value, COMPAT_DEFAULT)
        self.assertEqual(time, '5m')
        self.assertEqual(val, '42')
        self.assertEqual(compat, 'compat_1.2')

    def test_whitespace_stripped(self):
        time, val, compat = split_duration_value_string('  5m  ', COMPAT_DEFAULT)
        self.assertEqual(time, '5m')


# ===========================================================================
# join_duration_value_string
# ===========================================================================


class TestJoinDurationValueString(unittest.TestCase):
    def test_time_only(self):
        result = join_duration_value_string('5m', '')
        self.assertEqual(result, '5m')

    def test_time_and_value(self):
        result = join_duration_value_string('5m', '42')
        self.assertIn('5m', result)
        self.assertIn('42', result)
        self.assertIn(ATTRIBUTE_SEPARATOR, result)

    def test_time_value_compat(self):
        result = join_duration_value_string('5m', '42', 'compat_1.2')
        self.assertIn('5m', result)
        self.assertIn('42', result)
        self.assertIn('compat_1.2', result)

    def test_roundtrip(self):
        original = f'5m {ATTRIBUTE_SEPARATOR} 42'
        time, val, compat = split_duration_value_string(original, COMPAT_DEFAULT)
        rejoined = join_duration_value_string(time, val)
        self.assertIn('5m', rejoined)
        self.assertIn('42', rejoined)


# ===========================================================================
# json_serialize
# ===========================================================================


class TestJsonSerialize(unittest.TestCase):
    def test_datetime_to_isoformat(self):
        dt = datetime.datetime(2024, 6, 1, 12, 0, 0)
        result = json_serialize(dt)
        self.assertEqual(result, '2024-06-01T12:00:00')

    def test_date_to_isoformat(self):
        d = datetime.date(2024, 6, 1)
        result = json_serialize(d)
        self.assertEqual(result, '2024-06-01')

    def test_unsupported_raises_type_error(self):
        with self.assertRaises(TypeError):
            json_serialize(object())

    def test_used_in_json_dumps(self):
        data = {'ts': datetime.datetime(2024, 1, 1, 0, 0, 0)}
        result = json.dumps(data, default=json_serialize)
        self.assertIn('2024-01-01', result)


# ===========================================================================
# json_obj_hook
# ===========================================================================


class TestJsonObjHook(unittest.TestCase):
    def test_iso_string_converted_to_datetime(self):
        d = {'ts': '2024-06-01T12:00:00'}
        result = json_obj_hook(d)
        self.assertIsInstance(result['ts'], datetime.datetime)

    def test_non_date_string_unchanged(self):
        d = {'name': 'hello'}
        result = json_obj_hook(d)
        self.assertEqual(result['name'], 'hello')

    def test_multiple_keys(self):
        d = {'t1': '2024-01-01T00:00:00', 'label': 'test'}
        result = json_obj_hook(d)
        self.assertIsInstance(result['t1'], datetime.datetime)
        self.assertEqual(result['label'], 'test')


# ===========================================================================
# cache_write / cache_read
# ===========================================================================


class TestCacheReadWrite(unittest.TestCase):
    def setUp(self):
        self._tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self._tmpfile.close()
        self._path = self._tmpfile.name

    def tearDown(self):
        if os.path.exists(self._path):
            os.unlink(self._path)

    def _get_tz(self):
        import dateutil.tz

        return dateutil.tz.tzlocal()

    def test_pickle_roundtrip_int(self):
        cache_write(self._path, 42, CACHE_PICKLE)
        _, value = cache_read(self._path, self._get_tz(), CACHE_PICKLE)
        self.assertEqual(value, 42)

    def test_pickle_roundtrip_float(self):
        cache_write(self._path, 3.14, CACHE_PICKLE)
        _, value = cache_read(self._path, self._get_tz(), CACHE_PICKLE)
        self.assertAlmostEqual(value, 3.14)

    def test_pickle_roundtrip_string(self):
        cache_write(self._path, 'hello', CACHE_PICKLE)
        _, value = cache_read(self._path, self._get_tz(), CACHE_PICKLE)
        self.assertEqual(value, 'hello')

    def test_pickle_roundtrip_list(self):
        cache_write(self._path, [1, 2, 3], CACHE_PICKLE)
        _, value = cache_read(self._path, self._get_tz(), CACHE_PICKLE)
        self.assertEqual(value, [1, 2, 3])

    def test_json_roundtrip_int(self):
        cache_write(self._path, 99, CACHE_JSON)
        _, value = cache_read(self._path, self._get_tz(), CACHE_JSON)
        self.assertEqual(value, 99)

    def test_json_roundtrip_string(self):
        cache_write(self._path, 'world', CACHE_JSON)
        _, value = cache_read(self._path, self._get_tz(), CACHE_JSON)
        self.assertEqual(value, 'world')

    def test_json_roundtrip_bool(self):
        cache_write(self._path, True, CACHE_JSON)
        _, value = cache_read(self._path, self._get_tz(), CACHE_JSON)
        self.assertEqual(value, True)

    def test_cache_read_returns_mtime_as_datetime(self):
        cache_write(self._path, 1, CACHE_PICKLE)
        dt, _ = cache_read(self._path, self._get_tz(), CACHE_PICKLE)
        self.assertIsInstance(dt, datetime.datetime)

    def test_json_roundtrip_datetime(self):
        # datetime values survive a json round-trip via json_serialize / json_obj_hook
        dt_value = datetime.datetime(2024, 6, 1, 12, 0, 0)
        cache_write(self._path, {'ts': dt_value}, CACHE_JSON)
        _, value = cache_read(self._path, self._get_tz(), CACHE_JSON)
        self.assertIn('ts', value)
        self.assertIsInstance(value['ts'], datetime.datetime)


if __name__ == '__main__':
    unittest.main()
