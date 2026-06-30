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
lib/item/_parsing.py
====================

Attribute-parsing helpers extracted from lib/item/item.py.

Functions
---------
parse_eval_attribute(item, attribute_name, value)
parse_eval_trigger_list_attribute(item, attribute_name, value)
parse_hysteresis_input_attribute(item, attribute_name, value)
parse_hysteresis_xx_threshold_attribute(item, attr, value)
parse_on_xx_list_attribute(item, attr, value)
parse_cycle_attribute(item, attr, value, compat_default)
parse_autotimer_attribute(item, attr, value, compat_default)
build_trigger_condition_eval(item, trigger_condition)

All path-resolution calls go through the existing public/delegate API
on ``Item`` (``get_absolutepath``, ``get_stringwithabsolutepathes``,
``_split_destitem_from_value``) so no additional proxies are needed.

The ``compat_default`` parameter of ``parse_cycle_attribute`` and
``parse_autotimer_attribute`` is supplied by the ``item.py`` delegate,
which reads the module-level ``ATTRIB_COMPAT_DEFAULT`` global.  Passing
it as an argument avoids a circular import.  The returned ``compat``
value from ``split_duration_value_string`` is intentionally discarded by
these two functions (it is not used further in parsing).
"""

import logging

from lib.constants import (
    ATTRIBUTE_SEPARATOR,
    KEY_HYSTERESIS_UPPER_THRESHOLD,
    KEY_HYSTERESIS_LOWER_THRESHOLD,
    KEY_ON_CHANGE,
    KEY_CONDITION,
)

from ..helpers import split_duration_value_string
from lib.model.smartplugin import SmartPlugin

logger = logging.getLogger('lib.item')

# Names reserved by convention even when they aren't (yet) a real attribute
# on the object they'd collide with — e.g. 'get' is only dynamically bound
# for dict-type items (see DictHandler), so hasattr() can't reliably detect
# it at item-construction time, before the item's type has been resolved.
RESERVED_ITEM_NAMES = {'get'}


def check_item_name_collision(sh, objects_to_check, leaf_attr, path):
    """
    Check whether creating an item named *leaf_attr* (full path *path*)
    would collide with an existing attribute on any of *objects_to_check*
    — e.g. an existing sibling item, an Item class member/property, or,
    for top-level items, an attribute of the smarthome object itself
    (both get the item set as an attribute on construction, see
    Items._construct_and_link()) — or with RESERVED_ITEM_NAMES.

    An item shadowing a plugin instance bound onto ``sh`` (e.g. ``sh.arduino``
    set by a plugin with instance name ``arduino``) is not treated as a
    collision: plugins are only ever bound onto ``sh`` as a legacy
    convenience (see lib/plugin.py), not because anything depends on the
    item tree staying clear of those names, so flagging it would block
    item names a user could otherwise reasonably choose.

    Behavior is gated by ``sh._ignore_item_collision``: if it is True,
    logs a warning and returns False (construction/move proceeds
    anyway); if False (the default), logs a warning and returns True
    (the caller must not construct the item, and must drop the item's
    whole subtree along with it, since none of its own children get
    constructed either if the item itself is never created).

    :param sh: The smarthome object (for the ``_ignore_item_collision`` flag)
    :param objects_to_check: Objects the new item would be set as an attribute on
    :param leaf_attr: The item's own (last path segment) name
    :param path: Full path of the item, for the log message
    :type objects_to_check: list
    :type leaf_attr: str
    :type path: str

    :return: True if the item must NOT be constructed/moved
    :rtype: bool
    """

    def _is_real_collision(obj):
        if not hasattr(obj, leaf_attr):
            return False
        if obj is sh and isinstance(getattr(obj, leaf_attr), SmartPlugin):
            return False
        return True

    collision = leaf_attr in RESERVED_ITEM_NAMES or any(_is_real_collision(obj) for obj in objects_to_check)
    if not collision:
        return False

    if sh._ignore_item_collision:
        logger.warning(f"Name of item '{path}' collides with an existing attribute. Unexpected behaviour might occur.")
        return False

    logger.warning(
        f"Name of item '{path}' collides with an existing attribute — item was NOT created. "
        f'Set sh._ignore_item_collision to True to create it anyway.'
    )
    return True


# ---------------------------------------------------------------------------
# Eval attribute
# ---------------------------------------------------------------------------


def parse_eval_attribute(item, attribute_name, value):
    """
    Parse and store the ``eval`` attribute on *item*.

    If *value* is an empty string the eval expression is cleared.
    Otherwise relative ``sh.`` paths are expanded to absolute item paths.

    :param item:           ``Item`` instance.
    :param attribute_name: Attribute key (used for logging in path resolution).
    :param value:          Raw attribute value from item configuration.
    """
    if value == '':
        item._eval_unexpanded = ''
        item._eval = None
    else:
        item._eval_unexpanded = value
        value = item.get_stringwithabsolutepathes(value, 'sh.', '(', attribute_name)
        item._eval = value


# ---------------------------------------------------------------------------
# Eval trigger list attribute
# ---------------------------------------------------------------------------


def parse_eval_trigger_list_attribute(item, attribute_name, value):
    """
    Parse and store the ``eval_trigger`` attribute on *item*.

    A bare string is wrapped in a list; each path is expanded from
    relative to absolute.

    :param item:           ``Item`` instance.
    :param attribute_name: Attribute key.
    :param value:          Raw attribute value (string or list of strings).
    """
    if isinstance(value, str):
        value = [value]
    item._trigger_unexpanded = value
    expanded = []
    for path in value:
        expanded.append(item.get_absolutepath(path, attribute_name))
    item._trigger = expanded


# ---------------------------------------------------------------------------
# Hysteresis input attribute
# ---------------------------------------------------------------------------


def parse_hysteresis_input_attribute(item, attribute_name, value):
    """
    Parse and store the ``hysteresis_input`` attribute on *item*.

    The value (an item path, possibly relative) is expanded to an
    absolute path.

    :param item:           ``Item`` instance.
    :param attribute_name: Attribute key.
    :param value:          Raw attribute value.
    """
    item._hysteresis_input_unexpanded = value
    item._hysteresis_input = item.get_absolutepath(value, attribute_name)


# ---------------------------------------------------------------------------
# Hysteresis upper / lower threshold attribute
# ---------------------------------------------------------------------------


def parse_hysteresis_xx_threshold_attribute(item, attr, value):
    """
    Parse and store the upper or lower hysteresis threshold attribute.

    The *value* may optionally contain a timer separated by
    ``ATTRIBUTE_SEPARATOR``.  Both the threshold expression and the
    optional timer expression are expanded for relative ``sh.`` paths.

    :param item:  ``Item`` instance.
    :param attr:  Either ``KEY_HYSTERESIS_UPPER_THRESHOLD`` or
                  ``KEY_HYSTERESIS_LOWER_THRESHOLD``.
    :param value: Raw attribute value.
    """
    if value.find(ATTRIBUTE_SEPARATOR) == -1:
        threshold = item.get_stringwithabsolutepathes(value, 'sh.', '(', attr)
        timer = None
    else:
        threshold_unex, __, timer_unex = value.rpartition(ATTRIBUTE_SEPARATOR)
        threshold = item.get_stringwithabsolutepathes(threshold_unex.strip(), 'sh.', '(', attr)
        timer = item.get_stringwithabsolutepathes(timer_unex.strip(), 'sh.', '(', attr)

    if attr == KEY_HYSTERESIS_UPPER_THRESHOLD:
        item._hysteresis_upper_threshold = threshold
        item._hysteresis_upper_timer = timer
    elif attr == KEY_HYSTERESIS_LOWER_THRESHOLD:
        item._hysteresis_lower_threshold = threshold
        item._hysteresis_lower_timer = timer


# ---------------------------------------------------------------------------
# on_change / on_update list attribute
# ---------------------------------------------------------------------------


def parse_on_xx_list_attribute(item, attr, value):
    """
    Parse and store an ``on_change`` or ``on_update`` attribute.

    Each entry is optionally prefixed by a destination item path
    (``dest_item = eval_expression`` syntax).  Both paths and expressions
    are expanded from relative to absolute.

    :param item:  ``Item`` instance.
    :param attr:  Attribute name (``'on_change'`` or ``'on_update'``).
    :param value: Raw attribute value (string or list of strings).
    """
    if isinstance(value, str):
        value = [value]
    val_list = []
    val_list_unexpanded = []
    dest_var_list = []
    dest_var_list_unexp = []

    for val in value:
        # Separate destination item (if present: ``dest = expr`` syntax).
        dest_item, val = item._split_destitem_from_value(val)
        dest_item = dest_item.strip()
        if dest_item.startswith('sh.'):
            dest_item = dest_item[3:]
        dest_var_list_unexp.append(dest_item.strip())

        # Expand relative destination path.
        dest_item = item.get_absolutepath(dest_item.strip()).strip()

        val_list_unexpanded.append(val)
        val = item.get_stringwithabsolutepathes(val, 'sh.', '(', KEY_ON_CHANGE)
        val_list.append(val)
        dest_var_list.append(dest_item)

    setattr(item, '_' + attr + '_unexpanded', val_list_unexpanded)
    setattr(item, '_' + attr, val_list)
    setattr(item, '_' + attr + '_dest_var', dest_var_list)
    setattr(item, '_' + attr + '_dest_var_unexp', dest_var_list_unexp)


# ---------------------------------------------------------------------------
# Cycle attribute
# ---------------------------------------------------------------------------


def parse_cycle_attribute(item, attr, value, compat_default=''):
    """
    Parse and store the ``cycle`` attribute on *item*.

    The raw *value* is split into a time component and an optional value
    component; both are expanded for relative ``sh.`` references and
    stored as ``item._cycle_time`` / ``item._cycle_value``.

    The *compat_default* is forwarded to ``split_duration_value_string``
    and the returned ``compat`` token is discarded — it is not used in
    parsing.

    :param item:          ``Item`` instance.
    :param attr:          Attribute key (used for path resolution logs).
    :param value:         Raw attribute string.
    :param compat_default: Current ``ATTRIB_COMPAT_DEFAULT`` from ``item.py``
                           (passed by the delegate to avoid circular import).
    """
    cycle_time, cycle_value, _compat = split_duration_value_string(value, compat_default)
    item._cycle_time = item.get_stringwithabsolutepathes(cycle_time, 'sh.', '(', attr)
    item._cycle_value = item.get_stringwithabsolutepathes(cycle_value, 'sh.', '(', attr)


# ---------------------------------------------------------------------------
# Autotimer attribute
# ---------------------------------------------------------------------------


def parse_autotimer_attribute(item, attr, value, compat_default=''):
    """
    Parse and store the ``autotimer`` attribute on *item*.

    Analogous to :func:`parse_cycle_attribute` but populates
    ``item._autotimer_time`` / ``item._autotimer_value``.

    :param item:          ``Item`` instance.
    :param attr:          Attribute key.
    :param value:         Raw attribute string.
    :param compat_default: Current ``ATTRIB_COMPAT_DEFAULT`` from ``item.py``.
    """
    auto_time, auto_value, _compat = split_duration_value_string(value, compat_default)
    item._autotimer_time = item.get_stringwithabsolutepathes(auto_time, 'sh.', '(', attr)
    item._autotimer_value = item.get_stringwithabsolutepathes(auto_value, 'sh.', '(', attr)


# ---------------------------------------------------------------------------
# Trigger condition eval builder
# ---------------------------------------------------------------------------


def build_trigger_condition_eval(item, trigger_condition):
    """
    Build a Python boolean expression from the ``trigger_condition``
    attribute list.

    Each entry in *trigger_condition* is an OR-clause dict whose values
    are lists of AND conditions.  The function:

    * skips the special ``'value'`` key (handled elsewhere at eval time),
    * rewrites bare ``=`` to ``==`` (but not ``==``, ``<=``, ``>=``,
      ``=>``, ``=<``),
    * normalises ``true``/``false`` (case-insensitive) to Python
      ``True``/``False``,
    * expands relative ``sh.`` item references to absolute paths,
    * joins AND conditions with ``') and ('`` and OR clauses with
      ``') or ('``.

    :param item:              ``Item`` instance.
    :param trigger_condition: List of OR-clause dicts from item config.
    :return:                  Python boolean expression string.
    :rtype:                   str
    """
    wrk_eval = []
    for or_cond in trigger_condition:
        for ckey in or_cond:
            if ckey.lower() == 'value':
                # 'value' is handled separately at eval time — skip.
                pass
            else:
                and_cond = []
                for cond in or_cond[ckey]:
                    wrk = cond

                    # Rewrite bare ``=`` to ``==``, but guard compound
                    # operators (``==``, ``<=``, ``>=``, ``=>``, ``=<``).
                    if (
                        (wrk.find('=') != -1)
                        and (wrk.find('==') == -1)
                        and (wrk.find('<=') == -1)
                        and (wrk.find('>=') == -1)
                        and (wrk.find('=<') == -1)
                        and (wrk.find('=>') == -1)
                    ):
                        wrk = wrk.replace('=', '==')

                    # Normalise ``true`` / ``false`` → Python booleans.
                    p = wrk.lower().find('true')
                    if p != -1:
                        wrk = wrk[:p] + 'True' + wrk[p + 4 :]
                    p = wrk.lower().find('false')
                    if p != -1:
                        wrk = wrk[:p] + 'False' + wrk[p + 5 :]

                    # Expand relative item paths.
                    wrk = item.get_stringwithabsolutepathes(wrk, 'sh.', '(', KEY_CONDITION)

                    and_cond.append(wrk)

                wrk = ') and ('.join(and_cond)
                if len(or_cond[ckey]) > 1:
                    wrk = '(' + wrk + ')'
                wrk_eval.append(wrk)

                result = ') or ('.join(wrk_eval)

    if len(trigger_condition) > 1:
        result = '(' + result + ')'

    return result


# ---------------------------------------------------------------------------
# get_attribute_value
# ---------------------------------------------------------------------------


def get_attribute_value(
    item, attr_ref: str, current_attr: str, default: str = '', ignore_current_item: bool = False
) -> str:
    """
    Resolve a relative attribute reference to its value.

    If *attr_ref* contains a colon (``item:attr`` syntax) the referenced
    attribute is looked up on an ancestor item.  A leading run of dots in the
    item-part selects the ancestor level (one dot = current item, two dots =
    parent, etc.).

    When *ignore_current_item* is ``True`` and the item part resolves to the
    current item, the raw *attr_ref* is returned unchanged — used to break
    infinite loops during attribute expansion.

    :param item:               ``Item`` instance.
    :param attr_ref:           Raw attribute reference string.
    :param current_attr:       Name of the attribute currently being processed
                               (used as fallback attr name when the colon
                               syntax omits the attribute part).
    :param default:            Value returned when the attribute is not found.
    :param ignore_current_item: Skip resolution for the current item.
    :return:                   Resolved value string (or *attr_ref* unchanged).
    :rtype:                    str
    """
    value = attr_ref
    attr_ref = attr_ref.strip()
    if ':' in attr_ref:
        fromattr = attr_ref.split(':')[1]
        if fromattr in ['', '.']:
            fromattr = current_attr

        fromitem = attr_ref.split(':')[0]
        if fromitem == '.' and ignore_current_item:
            return value

        if all(x == '.' for x in fromitem):
            level = len(fromitem) - 1
            value = item.find_attribute(fromattr, default, level=level, strict=True)
    return value


# ---------------------------------------------------------------------------
# build_on_xx_list
# ---------------------------------------------------------------------------


def build_on_xx_list(on_dest_list, on_eval_list):
    """
    Reconstruct an ``on_change``/``on_update`` attribute list from its
    split destination and eval components.

    Each entry is either plain ``eval`` (when *on_dest* is empty) or
    ``dest = eval``.  Both scalar and list inputs are supported.

    Called from ``lib/item/property.py`` to reconstruct the human-readable
    attribute value from the parsed internal representation.

    :param on_dest_list: Destination item path(s) — string or list of strings.
    :param on_eval_list: Eval expression(s) — string or list of strings.
    :return:             List of formatted ``on_xx`` strings.
    :rtype:              list
    """
    on_list = []
    if on_dest_list is not None:
        if isinstance(on_dest_list, list):
            for on_dest, on_eval in zip(on_dest_list, on_eval_list):
                if on_dest != '':
                    on_list.append(on_dest.strip() + ' = ' + on_eval)
                else:
                    on_list.append(on_eval)
        else:
            if on_dest_list != '':
                on_list.append(on_dest_list + ' = ' + on_eval_list)
            else:
                on_list.append(on_eval_list)
    return on_list


# ---------------------------------------------------------------------------
# init_prerun
# ---------------------------------------------------------------------------


def init_prerun(item):
    """
    Wire up eval triggers and hysteresis triggers before the first item run.

    Called from ``Items.load_itemdefinitions`` after all items are loaded
    so that cross-item references (``eval_trigger``, ``hysteresis_input``)
    can be resolved.

    For each trigger path in ``item._trigger``:
    - Matches live Item objects via the Items singleton.
    - Warns if no match is found.
    - Appends *item* to each match's ``_items_to_trigger`` list (excluding
      self-references).
    - Rewrites the magic eval keywords ``and``, ``or``, ``sum``, ``avg``,
      ``max``, ``min`` into proper Python expressions over the trigger items.

    For ``hysteresis_input``:
    - Looks up the triggering item.
    - Appends *item* to ``_hysteresis_items_to_trigger`` on that item.

    :param item: ``Item`` instance.
    """
    from lib.item.items import Items

    items_instance = Items.get_instance()

    if item._trigger:
        _items = []
        for trigger in item._trigger:
            if items_instance.match_items(trigger) == [] and item._eval:
                logger.warning(f"item '{item._path}': trigger item '{trigger}' not found for function '{item._eval}'")
            _items.extend(items_instance.match_items(trigger))
        for triggered in _items:
            if triggered != item:
                triggered._items_to_trigger.append(item)
        if item._eval:
            items_expr = ['sh.' + str(x.id()) + '()' for x in _items]
            if item._eval == 'and':
                item._eval = ' and '.join(items_expr)
            elif item._eval == 'or':
                item._eval = ' or '.join(items_expr)
            elif item._eval == 'sum':
                item._eval = ' + '.join(items_expr)
            elif item._eval == 'avg':
                item._eval = '({0})/{1}'.format(' + '.join(items_expr), len(items_expr))
            elif item._eval == 'max':
                item._eval = 'max({0})'.format(','.join(items_expr))
            elif item._eval == 'min':
                item._eval = 'min({0})'.format(','.join(items_expr))

    if item._hysteresis_input:
        triggering_item = items_instance.return_item(item._hysteresis_input)
        if triggering_item is None:
            logger.error(
                f"item '{item._path}': trigger item '{item._hysteresis_input}' not found for function 'hysteresis'"
            )
        else:
            if triggering_item != item:
                if item._hysteresis_log:
                    logger.notice(f'_init_prerun: Adding to triggering_item {item}')
                triggering_item._hysteresis_items_to_trigger.append(item)
