#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2025   Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Handler classes for list- and dict-typed Items.

Extracted from lib/item/item.py (formerly inner classes of Item).

TypeHandler is the base class; ListHandler and DictHandler are the concrete
implementations.  An instance is attached to the item as ``item.list`` or
``item.dict`` so logic code can call ``item.list.append(v)`` etc. while
still routing every mutation through Item.__call__() to ensure all metadata
(last_change, last_update, on_change triggers …) is updated correctly.
"""

import copy


class TypeHandler:
    """
    Base class for dict/list type item handling.

    Subclasses are instantiated as <item>.list / <item>.dict when an Item
    of that type is created.  Every mutating method delegates to
    ``self._item.__call__()`` so the full item-update pipeline fires.
    """

    _type = ''
    item_functions = []

    def __init__(self, item):
        if item is None:
            raise ValueError(f'{self.__class__.__name__}: no item given')
        if item._type != self._type:
            raise ValueError(f'{self.__class__.__name__}: item not of type {self._type}')
        self._item = item


class ListHandler(TypeHandler):
    """Handle list-type items — mirrors Python list mutation methods."""

    _type = 'list'
    item_functions = ['append', 'prepend', 'insert', 'pop', 'extend', 'clear', 'delete', 'remove']

    # All methods route through item.__call__() to ensure item-update pipeline fires.

    def append(self, value, caller='Logic', source=None, dest=None):
        self._item.__call__(value, caller, source, dest, index='append')

    def prepend(self, value, caller='Logic', source=None, dest=None):
        self._item.__call__(value, caller, source, dest, index='prepend')

    def insert(self, index, value, caller='Logic', source=None, dest=None):
        tmplist = copy.deepcopy(self._item._value)
        tmplist.insert(index, value)
        self._item.__call__(tmplist, caller, source, dest)

    def pop(self, index=None, caller='Logic', source=None, dest=None):
        tmplist = copy.deepcopy(self._item._value)
        if index is None:
            ret = tmplist.pop()
        else:
            ret = tmplist.pop(index)
        self._item.__call__(tmplist, caller, source, dest)
        return ret

    def extend(self, value, caller='Logic', source=None, dest=None):
        tmplist = copy.deepcopy(self._item._value)
        tmplist.extend(value)
        self._item.__call__(tmplist, caller, source, dest)

    def clear(self, caller='Logic', source=None, dest=None):
        self._item.__call__([], caller, source, dest)

    def delete(self, value, caller='Logic', source=None, dest=None):
        """
        Mimic ``del list[x:y]`` — supply ``"x:y"`` as *value*.
        Named *delete* rather than *del* for syntax reasons.
        """
        splits = str(value).count(':')
        tmplist = copy.deepcopy(self._item._value)
        if splits == 0:
            x = int(value)
            del tmplist[x]
        if splits == 1:
            x, y = [int(i) for i in value.split(':')]
            del tmplist[x:y]
        elif splits == 2:
            x, y, z = [int(i) for i in value.split(':')]
            del tmplist[x:y:z]
        self._item.__call__(tmplist, caller, source, dest)

    def remove(self, value, caller='Logic', source=None, dest=None):
        tmplist = copy.deepcopy(self._item._value)
        tmplist.remove(value)
        self._item.__call__(tmplist, caller, source, dest)


class DictHandler(TypeHandler):
    """Handle dict-type items — mirrors Python dict mutation methods."""

    _type = 'dict'
    item_functions = ['get', 'delete', 'clear', 'pop', 'popitem', 'update']

    def get(self, key, default=None):
        value = self._item._value
        if not isinstance(value, dict):
            return default
        return value.get(key, default)

    def delete(self, key, caller='Logic', source=None, dest=None):
        """Named *delete* rather than *del* for syntax reasons."""
        tmpdict = copy.deepcopy(self._item._value)
        del tmpdict[key]
        self._item.__call__(tmpdict, caller, source, dest)

    def clear(self, caller='Logic', source=None, dest=None):
        self._item.__call__({}, caller, source, dest)

    def pop(self, key, caller='Logic', source=None, dest=None, default=None):
        tmpdict = copy.deepcopy(self._item._value)
        ret = tmpdict.pop(key, default)
        self._item.__call__(tmpdict, caller, source, dest)
        return ret

    def popitem(self, caller='Logic', source=None, dest=None):
        tmpdict = copy.deepcopy(self._item._value)
        ret = tmpdict.popitem()
        self._item.__call__(tmpdict, caller, source, dest)
        return ret

    def update(self, value, caller='Logic', source=None, dest=None):
        tmpdict = copy.deepcopy(self._item._value)
        tmpdict.update(value)
        self._item.__call__(tmpdict, caller, source, dest)


# Map from item type string to handler class — used by Item.__init__
HANDLER_MAP = {'list': ListHandler, 'dict': DictHandler}
