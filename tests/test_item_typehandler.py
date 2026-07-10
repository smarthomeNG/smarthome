#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for TypeHandler / ListHandler / DictHandler (lib/item/item.py inner classes)

Planned extraction target: lib/item/_typehandler.py

Coverage
--------
TypeHandler.__init__:
  - None item raises ValueError
  - Wrong type raises ValueError

ListHandler (all methods not covered by test_item.py):
  - prepend()       inserts at front
  - insert(i, v)    inserts at position
  - extend([...])   appends multiple elements
  - pop() (no index) removes last
  - error paths: pop on empty list, remove missing value

DictHandler:
  - clear()         empties the dict

Caller passthrough:
  - list.append / dict.update carry caller into item history
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
from lib.item.items import Items
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


def _make_sh():
    _reset()
    return MockSmartHome()


def _item(sh, path, itype, **conf):
    c = {'type': itype}
    c.update(conf)
    return lib.item.item.Item(sh, sh, path, c)


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


# ===========================================================================
# TypeHandler.__init__ error paths
# ===========================================================================


class TestTypeHandlerInit(_Base):
    def _ListHandler(self, item):
        # Access the inner class through a real list item's .list attribute
        # then test instantiation directly via the class reference
        li = _item(self.sh, 'li', 'list')
        cls = type(li.list)
        return cls, li

    def test_list_handler_exists_on_list_item(self):
        li = _item(self.sh, 'li', 'list')
        self.assertTrue(hasattr(li, 'list'))

    def test_dict_handler_exists_on_dict_item(self):
        di = _item(self.sh, 'di', 'dict')
        self.assertTrue(hasattr(di, 'dict'))

    def test_bool_item_has_no_list_handler(self):
        bi = _item(self.sh, 'bi', 'bool')
        self.assertFalse(hasattr(bi, 'list'))

    def test_bool_item_has_no_dict_handler(self):
        bi = _item(self.sh, 'bi', 'bool')
        self.assertFalse(hasattr(bi, 'dict'))

    def test_num_item_has_no_list_handler(self):
        ni = _item(self.sh, 'ni', 'num')
        self.assertFalse(hasattr(ni, 'list'))

    def test_wrong_type_raises_value_error(self):
        # Instantiating ListHandler on a non-list item raises ValueError
        ni = _item(self.sh, 'ni', 'num')
        li = _item(self.sh, 'li', 'list')
        ListHandler = type(li.list)
        with self.assertRaises(ValueError):
            ListHandler(ni)

    def test_none_item_raises_value_error(self):
        li = _item(self.sh, 'li', 'list')
        ListHandler = type(li.list)
        with self.assertRaises(ValueError):
            ListHandler(None)

    def test_dict_handler_wrong_type_raises(self):
        di = _item(self.sh, 'di', 'dict')
        ni = _item(self.sh, 'ni', 'num')
        DictHandler = type(di.dict)
        with self.assertRaises(ValueError):
            DictHandler(ni)


# ===========================================================================
# ListHandler.prepend
# ===========================================================================


class TestListPrepend(_Base):
    def setUp(self):
        super().setUp()
        self.li = _item(self.sh, 'li', 'list')
        self.li(['a', 'b', 'c'])

    def test_prepend_inserts_at_front(self):
        self.li.list.prepend('z')
        self.assertEqual(self.li()[0], 'z')

    def test_prepend_preserves_existing(self):
        self.li.list.prepend('z')
        self.assertIn('a', self.li())
        self.assertIn('b', self.li())
        self.assertIn('c', self.li())

    def test_prepend_grows_list(self):
        self.li.list.prepend('z')
        self.assertEqual(len(self.li()), 4)

    def test_prepend_on_empty_list(self):
        self.li([])
        self.li.list.prepend('first')
        self.assertEqual(self.li(), ['first'])

    def test_prepend_multiple_keeps_order(self):
        self.li([])
        self.li.list.prepend('second')
        self.li.list.prepend('first')
        self.assertEqual(self.li()[0], 'first')
        self.assertEqual(self.li()[1], 'second')


# ===========================================================================
# ListHandler.insert
# ===========================================================================


class TestListInsert(_Base):
    def setUp(self):
        super().setUp()
        self.li = _item(self.sh, 'li', 'list')
        self.li(['a', 'b', 'c'])

    def test_insert_at_zero_is_prepend(self):
        self.li.list.insert(0, 'z')
        self.assertEqual(self.li()[0], 'z')

    def test_insert_at_mid(self):
        self.li.list.insert(1, 'x')
        self.assertEqual(self.li()[1], 'x')
        self.assertEqual(self.li()[0], 'a')
        self.assertEqual(self.li()[2], 'b')

    def test_insert_at_end(self):
        self.li.list.insert(3, 'z')
        self.assertEqual(self.li()[-1], 'z')

    def test_insert_negative_index(self):
        # Python -1 inserts before the last element
        self.li.list.insert(-1, 'x')
        self.assertEqual(self.li()[-2], 'x')

    def test_insert_grows_list(self):
        self.li.list.insert(1, 'x')
        self.assertEqual(len(self.li()), 4)


# ===========================================================================
# ListHandler.extend
# ===========================================================================


class TestListExtend(_Base):
    def setUp(self):
        super().setUp()
        self.li = _item(self.sh, 'li', 'list')
        self.li(['a', 'b'])

    def test_extend_appends_all(self):
        self.li.list.extend(['c', 'd'])
        self.assertIn('c', self.li())
        self.assertIn('d', self.li())

    def test_extend_preserves_existing(self):
        self.li.list.extend(['c'])
        self.assertIn('a', self.li())
        self.assertIn('b', self.li())

    def test_extend_grows_list(self):
        self.li.list.extend(['c', 'd'])
        self.assertEqual(len(self.li()), 4)

    def test_extend_with_empty_leaves_unchanged(self):
        self.li.list.extend([])
        self.assertEqual(self.li(), ['a', 'b'])

    def test_extend_preserves_order(self):
        self.li.list.extend(['c', 'd'])
        self.assertEqual(self.li(), ['a', 'b', 'c', 'd'])


# ===========================================================================
# ListHandler.pop (no-index variant — removes last)
# ===========================================================================


class TestListPopNoIndex(_Base):
    def setUp(self):
        super().setUp()
        self.li = _item(self.sh, 'li', 'list')
        self.li(['a', 'b', 'c'])

    def test_pop_no_index_returns_last(self):
        ret = self.li.list.pop()
        self.assertEqual(ret, 'c')

    def test_pop_no_index_removes_last(self):
        self.li.list.pop()
        self.assertEqual(self.li(), ['a', 'b'])

    def test_pop_no_index_shrinks_list(self):
        self.li.list.pop()
        self.assertEqual(len(self.li()), 2)


# ===========================================================================
# ListHandler error / edge paths
# ===========================================================================


class TestListEdgePaths(_Base):
    def setUp(self):
        super().setUp()
        self.li = _item(self.sh, 'li', 'list')

    def test_remove_missing_value_raises(self):
        self.li(['a', 'b'])
        with self.assertRaises(ValueError):
            self.li.list.remove('z')

    def test_pop_index_out_of_range_raises(self):
        self.li(['a'])
        with self.assertRaises(IndexError):
            self.li.list.pop(99)

    def test_delete_step_slice(self):
        self.li([0, 1, 2, 3, 4, 5])
        self.li.list.delete('0:6:2')  # delete every other element
        self.assertEqual(self.li(), [1, 3, 5])


# ===========================================================================
# DictHandler.clear
# ===========================================================================


class TestDictClear(_Base):
    def setUp(self):
        super().setUp()
        self.di = _item(self.sh, 'di', 'dict')
        self.di({'a': 1, 'b': 2})

    def test_clear_empties_dict(self):
        self.di.dict.clear()
        self.assertEqual(self.di(), {})

    def test_clear_on_already_empty(self):
        self.di({})
        self.di.dict.clear()  # must not raise
        self.assertEqual(self.di(), {})

    def test_can_add_after_clear(self):
        self.di.dict.clear()
        self.di.dict.update({'x': 10})
        self.assertEqual(self.di(), {'x': 10})


# ===========================================================================
# Caller passthrough via handlers
# ===========================================================================


class TestCallerPassthrough(_Base):
    def test_list_append_caller_reflected_in_changed_by(self):
        li = _item(self.sh, 'li', 'list')
        li([])
        li.list.append('v', caller='TestCaller')
        self.assertIn('TestCaller', li.property.last_change_by)

    def test_dict_update_caller_reflected(self):
        di = _item(self.sh, 'di', 'dict')
        di({})
        di.dict.update({'k': 1}, caller='DictCaller')
        self.assertIn('DictCaller', di.property.last_change_by)

    def test_list_prepend_caller_reflected(self):
        li = _item(self.sh, 'li', 'list')
        li(['x'])
        li.list.prepend('y', caller='PrependCaller')
        self.assertIn('PrependCaller', li.property.last_change_by)


# ===========================================================================
# DictHandler.get — via item.dict.get()
# ===========================================================================


class TestDictHandlerGet(_Base):
    def setUp(self):
        super().setUp()
        self.di = _item(self.sh, 'di', 'dict')
        self.di({'a': 1, 'b': 2})

    def test_get_existing_key_returns_value(self):
        self.assertEqual(self.di.dict.get('a'), 1)

    def test_get_missing_key_returns_none(self):
        self.assertIsNone(self.di.dict.get('missing'))

    def test_get_missing_key_returns_explicit_default(self):
        self.assertEqual(self.di.dict.get('missing', 42), 42)

    def test_get_missing_key_default_none_returns_none(self):
        self.assertIsNone(self.di.dict.get('missing', None))

    def test_get_on_unpopulated_item_returns_default(self):
        di = _item(self.sh, 'di2', 'dict')
        # _value is None — item never set
        self.assertIsNone(di.dict.get('key'))

    def test_get_on_unpopulated_item_returns_explicit_default(self):
        di = _item(self.sh, 'di2', 'dict')
        self.assertEqual(di.dict.get('key', 'fallback'), 'fallback')


# ===========================================================================
# Item.get() — direct shortcut attached on dict-type items
# ===========================================================================


class TestItemGetShortcut(_Base):
    def setUp(self):
        super().setUp()
        self.di = _item(self.sh, 'di', 'dict')
        self.di({'x': 10, 'y': 20})

    def test_get_shortcut_exists_on_dict_item(self):
        self.assertTrue(hasattr(self.di, 'get'))

    def test_get_shortcut_missing_on_non_dict_item(self):
        ni = _item(self.sh, 'ni', 'num')
        self.assertFalse(hasattr(ni, 'get'))

    def test_get_shortcut_returns_value(self):
        self.assertEqual(self.di.get('x'), 10)

    def test_get_shortcut_missing_key_returns_none(self):
        self.assertIsNone(self.di.get('missing'))

    def test_get_shortcut_missing_key_returns_explicit_default(self):
        self.assertEqual(self.di.get('missing', 99), 99)

    def test_get_shortcut_default_none_returns_none(self):
        self.assertIsNone(self.di.get('missing', None))

    def test_get_shortcut_on_unpopulated_item(self):
        di = _item(self.sh, 'di2', 'dict')
        self.assertIsNone(di.get('key'))


# ===========================================================================
# Item.__call__(key=, default=) — _NOTSET sentinel fix
# ===========================================================================


class TestItemCallDictAccess(_Base):
    def setUp(self):
        super().setUp()
        self.di = _item(self.sh, 'di', 'dict')
        self.di({'k': 'v'})

    def test_call_with_key_returns_value(self):
        self.assertEqual(self.di(key='k'), 'v')

    def test_call_missing_key_no_default_raises(self):
        with self.assertRaises(KeyError):
            self.di(key='missing')

    def test_call_missing_key_default_none_returns_none(self):
        # Previously raised KeyError because None was the sentinel — now fixed
        self.assertIsNone(self.di(key='missing', default=None))

    def test_call_missing_key_explicit_default_returns_default(self):
        self.assertEqual(self.di(key='missing', default='fallback'), 'fallback')

    def test_call_missing_key_default_false_returns_false(self):
        self.assertIs(self.di(key='missing', default=False), False)

    def test_call_missing_key_default_zero_returns_zero(self):
        self.assertEqual(self.di(key='missing', default=0), 0)


if __name__ == '__main__':
    unittest.main()
