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
log_change implementation for Item.

Extracted from lib/item/item.py.

Entry point: ``log_on_change(item, value, caller, source, dest)``
Called from Item._set_value() for every value write (when the item has
``log_change`` configured) — but skipped when caller is 'Fader'.

Accesses only single-underscore attributes and public methods on the Item
so the extraction avoids Python name-mangling issues.
"""

import logging
import lib.env
import lib.userfunctions as _uf  # noqa: F401  # available to eval templates

from lib.constants import KEY_LOG_CHANGE
from lib.utils import Utils

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public entry point (replaces Item._log_on_change)
# ---------------------------------------------------------------------------


def log_on_change(item, value, caller, source=None, dest=None):
    """
    Write an entry to the item's log_change logger, applying all configured
    rules (lowlimit, highlimit, filter, exclude).

    :param item:   the Item instance
    :param value:  new item value
    :param caller: caller string
    :param source: source string (may be None)
    :param dest:   destination string (may be None)
    """
    if item._log_change_logger is None:
        return

    issue_list = []

    low_limit = get_rule(item, 'lowlimit')
    high_limit = get_rule(item, 'highlimit')

    if isinstance(low_limit, dict):
        issue_list.append(low_limit.get('issue'))
        low_limit = None
    if isinstance(high_limit, dict):
        issue_list.append(high_limit.get('issue'))
        high_limit = None

    if item._type != 'num' and low_limit:
        issue_list.append(f'Low limit {low_limit} given, however item is not num type - ignoring')
        low_limit = None
    if item._type != 'num' and high_limit:
        issue_list.append(f'High limit {high_limit} given, however item is not num type - ignoring')
        high_limit = None
    if low_limit is not None and high_limit is not None and low_limit >= high_limit:
        issue_list.append(f'Low limit {low_limit} >= High limit {high_limit} - ignoring high limit')
        high_limit = None

    filter_list = get_rule(item, 'filter')
    if isinstance(filter_list, dict):
        issue_list.append(filter_list.get('issue'))
        filter_list = []
    f_list = []
    for f in filter_list:
        if type(value) is not type(f):
            issue_list.append(f'Filter entry {f} is type {type(f)}, item is {item._type} - ignoring')
        else:
            f_list.append(f)
    filter_list = f_list

    exclude_list = get_rule(item, 'exclude')
    if isinstance(exclude_list, dict):
        issue_list.append(exclude_list.get('issue'))
        exclude_list = []
    e_list = []
    for e in exclude_list:
        if type(value) is not type(e):
            issue_list.append(f'Exclude entry {e} is type {type(e)}, item is {item._type} - ignoring')
        else:
            e_list.append(e)
    exclude_list = e_list

    if filter_list and exclude_list:
        issue_list.append('Defining filter AND exclude does not work - ignoring exclude list')
        exclude_list = []

    if issue_list and item._log_rules_cache.get('issues') != issue_list:
        logger.warning(
            f'Item {item._path} log_rules has issues: {", ".join(issue_list)}. '
            f'Cleaned log_rules: lowlimit = {low_limit}, highlimit = {high_limit}, '
            f'filter = {filter_list}, exclude = {exclude_list}'
        )

    item._log_rules_cache = {
        'issues': issue_list,
        'filter': filter_list,
        'exclude': exclude_list,
        'lowlimit': low_limit,
        'highlimit': high_limit,
    }

    if item._type == 'num':
        if low_limit is not None and low_limit > float(value):
            return
        if high_limit is not None and high_limit <= float(value):
            return
        if filter_list and float(value) not in filter_list:
            return
        if exclude_list and float(value) in exclude_list:
            return
    else:
        if filter_list and value not in filter_list:
            return
        if exclude_list and value in exclude_list:
            return

    if item._log_text is None:
        txt = build_standardtext(item, value, caller, source, dest)
    else:
        txt = build_text(item, value, caller, source, dest)

    # Resolve the log level from the template attribute (may contain f-string)
    try:
        val = item._log_level_attrib.replace("'", '"')
        log_level = eval(f"f'{val}'")
    except Exception as e:
        log_level = item._log_level_attrib
        logger.error(f"Item {item._path}: Invalid log_level template '{log_level}' - (Exception: {e})")

    level = log_level.upper()
    level_name = level
    if Utils.is_int(level):
        level = int(level)
        level_name = logging.getLevelName(level)
    if logging.getLevelName(level) == 'Level ' + str(level):
        logger.warning(
            f"Item {item._path}: Invalid loglevel '{log_level}' defined in log_level attribute "
            f"- Level 'INFO' will be used instead"
        )
        item._log_level_name = 'INFO'
        item._log_level = logging.getLevelName('INFO')
    else:
        item._log_level_name = level_name
        item._log_level = logging.getLevelName(level_name)

    item._log_change_logger.log(item._log_level, txt)


# ---------------------------------------------------------------------------
# Rule lookup (replaces Item._get_rule)
# ---------------------------------------------------------------------------


def get_rule(item, rule_entry):
    """
    Retrieve and normalise a single rule entry from item._log_rules.

    Returns the rule value or a dict with an 'issue' key on invalid input.
    """

    def convert_entry(entry, to):
        returnvalue = entry
        if isinstance(returnvalue, str) and to != 'str':
            try:
                from lib.item.items import Items

                rule_item_path = item.get_absolutepath(entry.strip().replace('sh.', ''), KEY_LOG_CHANGE)
                returnvalue = Items.get_instance().return_item(rule_item_path).property.value
            except Exception:
                if to == 'list':
                    returnvalue = [entry]
        if isinstance(returnvalue, (str, int)) and to == 'num':
            try:
                returnvalue = float(returnvalue)
            except ValueError:
                returnvalue = None
        elif isinstance(entry, list):
            entry = [convert_entry(val, item._type) for val in entry]
        elif not isinstance(returnvalue, list) and to == 'list':
            returnvalue = [returnvalue]
        elif isinstance(returnvalue, (float, int)) and to == 'str':
            returnvalue = str(returnvalue)
        if returnvalue is None:
            returnvalue = {'value': None, 'issue': f"Given log_rules entry '{entry}' for {rule_entry} is invalid"}
        return returnvalue

    defaults = {'filter': [], 'exclude': [], 'lowlimit': None, 'highlimit': None}
    types = {'filter': 'list', 'exclude': 'list', 'lowlimit': 'num', 'highlimit': 'num'}
    entry = item._log_rules.get(rule_entry, defaults.get(rule_entry))
    if entry is not None and entry != []:
        entry = convert_entry(entry, types.get(rule_entry) or item._type)
    return entry


# ---------------------------------------------------------------------------
# Text builders (replace Item._log_build_standardtext / _log_build_text)
# ---------------------------------------------------------------------------


def build_standardtext(item, value, caller, source=None, dest=None):
    """Build the default log text (no custom log_text template)."""
    if item._sh.get_defaultlogtext() is not None:
        item._log_text = item._sh.get_defaultlogtext().replace("'", '"')
        return build_text(item, value, caller, source, dest)
    log_src = f' ({source})' if source is not None else ''
    log_dst = f', dest: {dest}' if dest is not None else ''
    return f'Item Change: {item._path} = {value}  -  caller: {caller}{log_src}{log_dst}'


def build_text(item, value, caller, source=None, dest=None):
    """Build log text using item._log_text as an f-string template."""
    # Variables available to the template
    lvalue = item.property.last_value  # noqa: F841
    mlvalue = item._log_mapping.get(lvalue, lvalue)  # noqa: F841
    name = item._name  # noqa: F841
    age = round(item._get_last_change_age(), 2)  # noqa: F841
    id = item._path  # noqa: F841

    if item._is_top_of_item_tree():
        pname = None  # noqa: F841
        pid = None  # noqa: F841
    else:
        _parent = item.return_parent()
        pname = _parent._name  # noqa: F841
        pid = _parent._path  # noqa: F841

    mvalue = item._log_mapping.get(value, value)  # noqa: F841
    lowlimit = item._log_rules_cache.get('lowlimit')  # noqa: F841
    highlimit = item._log_rules_cache.get('highlimit')  # noqa: F841
    filter = item._log_rules_cache.get('filter')  # noqa: F841
    exclude = item._log_rules_cache.get('exclude')  # noqa: F841
    sh = item._sh  # noqa: F841
    shtime = item.shtime
    time = shtime.now().strftime('%H:%M:%S')  # noqa: F841
    date = shtime.now().strftime('%d.%m.%Y')  # noqa: F841
    stamp = shtime.now().timestamp()  # noqa: F841
    now = str(shtime.now())  # noqa: F841

    from lib.item.items import Items

    items = Items.get_instance()  # noqa: F841

    import math  # noqa: F401, F841

    env = lib.env  # noqa: F841

    try:
        log_rules_item = item._log_rules.get('itemvalue', None)
        if log_rules_item is not None:
            rule_path = item.get_absolutepath(log_rules_item.strip().replace('sh.', ''), KEY_LOG_CHANGE)
            itemvalue = str(items.return_item(rule_path).property.value)  # noqa: F841
        else:
            itemvalue = None  # noqa: F841
    except Exception as e:
        logger.error(
            f"{id}: Invalid item in log_text '{item._log_text}' or log_rules '{item._log_rules}' - Exception: {e}"
        )
        itemvalue = 'INVALID'  # noqa: F841

    item._log_text = item._log_text.replace("'", '"')
    try:
        txt = eval(f"f'{item._log_text}'")
    except Exception as e:
        logger.error(f"{id}: Invalid log_text template '{item._log_text}' - Exception: {e}")
        txt = item._log_text
    return txt
