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
lib/item/_json.py
=================

JSON serialisation helpers extracted from lib/item/item.py.

Functions
---------
jsonvars(item)
    Return a plain ``dict`` of the item's key attributes, suitable for
    JSON serialisation.

to_json(item)
    Return a pretty-printed JSON string representation of the item.
"""

import json


def jsonvars(item):
    """
    Return a dict of the item's key attributes.

    The returned dict contains:

    * ``id``         — item path (``_path``)
    * ``name``       — item name (``_name``)
    * ``value``      — current value
    * ``type``       — item type string
    * ``attributes`` — raw configuration dict (``conf``)
    * ``children``   — list of child item paths

    :param item: ``Item`` instance.
    :return:     Serialisable attribute dict.
    :rtype:      dict
    """
    return {
        'id': item._path,
        'name': item._name,
        'value': item._value,
        'type': item._type,
        'attributes': item.conf,
        'children': item.get_children_path(),
    }


def to_json(item):
    """
    Return a pretty-printed JSON string for *item*.

    Keys are sorted alphabetically; indentation is 2 spaces.

    :param item: ``Item`` instance.
    :return:     JSON string.
    :rtype:      str
    """
    return json.dumps(jsonvars(item), sort_keys=True, indent=2)
