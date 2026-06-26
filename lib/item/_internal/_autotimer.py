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
Autotimer / cycle / cron scheduler helpers for Item.

Extracted from lib/item/item.py.

Public functions
----------------
get_attr_time(item, attr)
    Return the resolved time value for 'cycle' or 'autotimer' attributes.
    Replaces Item.get_attr_time().

get_attr_value(item, attr, value=None)
    Return the resolved value for 'cycle', 'autotimer', or 'cron' attributes.
    Replaces Item.get_attr_value().

get_items_from_string(item, string)
    Return a list of Item objects referenced in an eval-string.
    Replaces Item.__get_items_from_string().

init_start_scheduler(item)
    Register crontab / cycle scheduler entries for the item.
    Replaces Item._init_start_scheduler().

item_timer(item, time, value, auto=False, caller=None, source=None, compat=...)
    Start a one-shot or autotimer for the item.
    Replaces Item.timer().

item_remove_timer(item)
    Cancel the running timer for the item.
    Replaces Item.remove_timer().

item_autotimer(item, time=None, value=None)
    Set or clear the item's autotimer time/value.
    Replaces Item.autotimer().

All functions access only single-underscore attributes and the public proxies
_run_attribute_eval() / _cast_duration() / _castvalue_to_itemtype() that Item
exposes for extracted modules.
"""

import datetime
import logging
import re

logger = logging.getLogger(__name__)

# ATTRIB_COMPAT_LATEST is imported from lib.constants (same origin as item.py uses)
from lib.constants import ATTRIB_COMPAT_LATEST  # noqa: F401


# ---------------------------------------------------------------------------
# get_items_from_string  (replaces Item.__get_items_from_string)
# ---------------------------------------------------------------------------


def get_items_from_string(item, string):
    """
    Return a list of all Item objects referenced as ``sh.path.to.item()`` in *string*.

    :param item:   any Item instance (used only for the Items singleton lookup)
    :param string: string that may contain item references
    :return:       list of Item objects
    """
    if not string:
        return []

    from lib.item.items import Items

    items_instance = Items.get_instance()
    if items_instance is None:
        return []

    regex = re.compile(r'sh\.([a-zA-Z0-9_.]+)(?:\(\)|\.property\.[a-zA-Z_]+)')
    result = regex.findall(string)

    found = {items_instance.return_item(entry) for entry in result if entry}
    return list({i for i in found if i is not None})


# ---------------------------------------------------------------------------
# get_attr_time  (replaces Item.get_attr_time)
# ---------------------------------------------------------------------------


def get_attr_time(item, attr: str):
    """
    Return the resolved time value for 'cycle' or 'autotimer' attributes.

    Returns None when the attribute is not set or evaluates to 0 (for cycle).

    :param item: the Item instance
    :param attr: 'cycle' or 'autotimer'
    :return:     resolved duration in seconds (int) or None
    """
    if attr not in ('cycle', 'autotimer'):
        return

    var = getattr(item, f'_{attr}_time')
    if var is None:
        logger.debug(f'get_attr_time({attr}): item {item._path} has no member _{attr}_time.')
        return

    if isinstance(var, int):
        return var

    try:
        res = item._cast_duration(var, test=True)
        if type(res) is int:
            if attr == 'cycle' and res == 0:
                logger.warning(f'{item._path}: cycle time returned 0 from {item._cycle_time}, ignoring')
                return
            return res

        res = item._run_attribute_eval(var, result_type='str', result_error=None)
        if res is None:
            return

        res = item._cast_duration(res)
        if attr == 'cycle' and res == 0:
            logger.warning(f'{item._path}: cycle time returned 0 from {item._cycle_time}, ignoring')
            return

        if res is not None and res is not False:
            return int(res)
    except Exception as e:
        logger.warning(f'error on evaluation {attr} time "{var}" for item {item._path}: {e}')


# ---------------------------------------------------------------------------
# get_attr_value  (replaces Item.get_attr_value)
# ---------------------------------------------------------------------------


def get_attr_value(item, attr: str, value=None):
    """
    Return the resolved value for 'cycle', 'autotimer', or 'cron' attributes.

    :param item:  the Item instance
    :param attr:  'cycle', 'autotimer', or 'cron'
    :param value: override value (used for 'cron', stored in scheduler)
    :return:      resolved value or None
    """
    if attr not in ('cycle', 'autotimer', 'cron'):
        return

    var = value if value is not None else getattr(item, f'_{attr}_value')
    if var is None:
        return

    if not isinstance(var, str):
        return var

    try:
        res = item._run_attribute_eval(var, result_type='str', result_error=None)
        return res
    except Exception as e:
        logger.warning(f'error on evaluation {attr} value "{var}" for item {item._path}: {e}')


# ---------------------------------------------------------------------------
# init_start_scheduler  (replaces Item._init_start_scheduler)
# ---------------------------------------------------------------------------


def init_start_scheduler(item):
    """
    Register crontab / cycle scheduler entries for *item*.

    Called from Items.load_itemdefinitions() after all items are loaded.

    :param item: the Item instance
    """
    if item._crontab is None and item._cycle_time is None:
        return

    cycle_time = get_attr_time(item, 'cycle')
    cycle_value = None
    if cycle_time is not None:
        cycle_value = get_attr_value(item, 'cycle')

    items = get_items_from_string(item, item._cycle_time)
    item._sh.scheduler.add(
        item._itemname_prefix + item._path, item, cron=item._crontab, cycle=cycle_time, value=cycle_value, items=items
    )


# ---------------------------------------------------------------------------
# item_timer  (replaces Item.timer)
# ---------------------------------------------------------------------------


def item_timer(item, time, value, auto=False, caller=None, source=None, compat=ATTRIB_COMPAT_LATEST):
    """
    Start a timer for *item*.

    :param item:   the Item instance
    :param time:   duration until the value is set
    :param value:  value to set the item to
    :param auto:   if True, store as autotimer; otherwise one-shot timer
    :param caller: caller string
    :param source: source string
    :param compat: compatibility flag (unused, kept for backward compat)
    """
    time = item._cast_duration(time)
    value = item._castvalue_to_itemtype(value, compat)
    if caller is None:
        if auto:
            caller = 'Autotimer'
            item._autotimer_time = time
            item._autotimer_value = value
        else:
            caller = 'Timer'

    next_time = item.shtime.now() + datetime.timedelta(seconds=time)
    sched_value = {'value': value, 'caller': caller}
    if source is not None:
        sched_value['source'] = source

    item._sh.scheduler.add(
        item._itemname_prefix + item.id() + '-Timer', item.__call__, value=sched_value, next=next_time
    )


# ---------------------------------------------------------------------------
# item_remove_timer  (replaces Item.remove_timer)
# ---------------------------------------------------------------------------


def item_remove_timer(item):
    """
    Cancel the running timer for *item*.

    :param item: the Item instance
    """
    item._sh.scheduler.remove(item._itemname_prefix + item.id() + '-Timer')


# ---------------------------------------------------------------------------
# item_autotimer  (replaces Item.autotimer)
# ---------------------------------------------------------------------------


def item_autotimer(item, time=None, value=None):
    """
    Set or clear the item's autotimer time/value.

    If time and value are both provided, set the autotimer.
    Otherwise clear it.

    :param item:  the Item instance
    :param time:  time until the value is set
    :param value: value to set the item to
    """
    if time is not None and value is not None:
        # don't cast_duration here — that is done later in get_attr_time
        item._autotimer_time = time
        item._autotimer_value = value
    else:
        item._autotimer_time = None
        item._autotimer_value = None
