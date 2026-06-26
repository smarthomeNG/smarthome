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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
lib/item/_navigation.py
=======================

Item-tree navigation helpers extracted from lib/item/item.py.

Functions
---------
return_parent_item(item, level, strict)
    Walk up the item tree and return the ancestor at *level* hops.

is_top_of_item_tree(item)
    Return ``True`` when *item* has no parent inside the item tree.

Name-mangling note
------------------
``Item.__parent`` is a double-underscore attribute.  A ``_parent``
property proxy is added to ``Item`` so that these module-level functions
can access it without using the mangled name ``_Item__parent``:

    @property
    def _parent(self):
        return self.__parent
"""


def is_top_of_item_tree(item):
    """
    Return ``True`` when *item* has no parent inside the SmartHomeNG item
    tree — i.e. its parent is either ``None`` or the ``Items`` singleton.

    :param item: ``Item`` instance.
    :return:     ``True`` if *item* is a top-level item.
    :rtype:      bool
    """
    from lib.item.items import Items

    items_instance = Items.get_instance()
    return item._parent is None or item._parent is items_instance


def return_parent_item(item, level: int = 1, strict: bool = False):
    """
    Return the ancestor item *level* hops above *item*.

    * ``level == 1`` → direct parent (fast path via ``item._parent``).
    * ``level < 1``  → returns *item* itself.
    * ``strict=False`` (default): if fewer than *level* ancestors exist,
      the highest reachable ancestor is returned.
    * ``strict=True``: if fewer than *level* ancestors exist, ``None`` is
      returned.

    :param item:   ``Item`` instance.
    :param level:  Number of parent hops (default 1).
    :param strict: Whether to enforce exact depth (default ``False``).
    :return:       Ancestor ``Item``, *item* itself, or ``None``.
    """
    if level == 1:
        return item._parent

    current = item
    while level >= 1:
        if is_top_of_item_tree(current):
            if strict:
                return None
            else:
                return current
        current = current.return_parent()
        level -= 1

    return current
