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
Trigger-registration helpers extracted from lib/item/item.py:
add/remove_logic_trigger, get_logic_triggers, add/remove_method_trigger,
get_method_triggers, get_item_triggers, get_hysteresis_item_triggers.

Item.__logics_to_trigger/__methods_to_trigger are double-underscore
(name-mangled outside the class body) - rather than use the mangled form,
Item exposes proxy properties item._logics_to_trigger/_methods_to_trigger
returning the *same* list objects, so in-place mutations here are
immediately visible inside the class. _items_to_trigger and
_hysteresis_items_to_trigger are already single-underscore, no proxy needed.
"""


# ---------------------------------------------------------------------------
# Logic triggers
# ---------------------------------------------------------------------------


def add_logic_trigger(item, logic):
    """
    Append *logic* to the list of logics that are triggered when *item*
    changes.

    :param item:  ``Item`` instance.
    :param logic: Logic object to register.
    """
    item._logics_to_trigger.append(logic)


def remove_logic_trigger(item, logic):
    """
    Remove *logic* from the list of logics triggered by *item*.

    :param item:  ``Item`` instance.
    :param logic: Logic object to deregister.
    """
    item._logics_to_trigger.remove(logic)


def get_logic_triggers(item):
    """
    Return the list of logics that are triggered when *item* changes.

    :param item: ``Item`` instance.
    :return:     List of logic objects.
    :rtype:      list
    """
    return item._logics_to_trigger


# ---------------------------------------------------------------------------
# Method triggers
# ---------------------------------------------------------------------------


def add_method_trigger(item, method):
    """
    Append *method* to the list of plugin methods triggered when *item*
    changes.

    :param item:   ``Item`` instance.
    :param method: Callable to register.
    """
    item._methods_to_trigger.append(method)


def remove_method_trigger(item, method):
    """
    Remove *method* from the list of plugin methods triggered by *item*.

    :param item:   ``Item`` instance.
    :param method: Callable to deregister.
    """
    item._methods_to_trigger.remove(method)


def get_method_triggers(item):
    """
    Return the list of plugin methods that are triggered when *item*
    changes.

    :param item: ``Item`` instance.
    :return:     List of callables.
    :rtype:      list
    """
    return item._methods_to_trigger


# ---------------------------------------------------------------------------
# Item triggers
# ---------------------------------------------------------------------------


def get_item_triggers(item):
    """
    Return the list of items whose eval is re-triggered when *item*
    changes.

    :param item: ``Item`` instance.
    :return:     List of ``Item`` objects.
    :rtype:      list
    """
    return item._items_to_trigger


def get_hysteresis_item_triggers(item):
    """
    Return the list of items whose hysteresis eval is re-triggered when
    *item* changes.

    :param item: ``Item`` instance.
    :return:     List of ``Item`` objects.
    :rtype:      list
    """
    return item._hysteresis_items_to_trigger
