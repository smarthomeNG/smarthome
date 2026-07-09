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
Eval / on_change / on_update execution for Item.

Extracted from lib/item/item.py.

Entry points
------------
run_eval(item, value, caller, source, dest)
    Called when an item's eval expression must be evaluated.
    Replaces Item.__run_eval().

run_on_xxx(item, path, value, on_dest, on_eval, attr, caller, source, dest)
    Common runner for on_update and on_change entries.
    Replaces Item._run_on_xxx().

run_on_update(item, value, caller, source, dest)
    Runs all on_update entries for the item.
    Replaces Item.__run_on_update().

run_on_change(item, value, caller, source, dest)
    Runs all on_change entries for the item.
    Replaces Item.__run_on_change().

All functions access only single-underscore attributes and public methods on
the Item to avoid Python name-mangling problems.  The one exception is calling
item._update_item() — a thin public proxy that Item exposes for this purpose
(it delegates to the private Item.__update()).

Eval namespace
--------------
All eval calls use the explicit namespace built by :func:`_make_eval_env`.
See its docstring for the full list of names available to user expressions.
"""

import logging
import lib.env

# COMPAT-SHIM: remove this import together with _eval_compat.py
from ._eval_compat import _eval_with_legacy_fallback, _EVAL_FAILED

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# _make_eval_env
# ---------------------------------------------------------------------------


def _make_eval_env(item, value=None, caller=None, source=None, dest=None) -> dict:
    """
    Build the standard eval namespace for item expressions.

    This is the single authoritative definition of what names are available
    inside ``eval``, ``on_change``, and ``on_update`` expressions.

    Documented names
    ~~~~~~~~~~~~~~~~
    * ``sh``      — the SmartHomeNG instance (same as ``item._sh``)
    * ``shtime``  — the Shtime library (date/time helpers)
    * ``items``   — the Items singleton (``items.return_item(...)``)
    * ``math``    — Python ``math`` module
    * ``uf``      — loaded user-functions (``lib.userfunctions``)
    * ``env``     — ``lib.env`` (environment/platform info)
    * ``value``   — the trigger value passed to the current eval call
    * ``datetime`` — Python ``datetime`` module (documented in examples)
    * ``time``    — Python ``time`` module (documented in item.py comment)

    Additional names (not documented, but technically accessible today)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    * ``caller`` — string identifying what triggered the eval
    * ``source`` — source item path or ``None``
    * ``dest``   — destination or ``None``
    * ``item``   — the ``Item`` instance itself

    :param item:   ``Item`` instance being evaluated.
    :param value:  Current trigger value (``None`` for attribute evals).
    :param caller: Caller label (``None`` for attribute evals).
    :param source: Source path (``None`` for attribute evals).
    :param dest:   Destination (``None`` for attribute evals).
    :returns:      Namespace dict suitable for passing to ``eval()``.
    """
    import math
    import time
    import datetime
    import lib.userfunctions as uf
    from lib.item.items import Items

    return {
        # ── documented public API ──────────────────────────────────────────
        'sh': item._sh,
        'shtime': item.shtime,
        'items': Items.get_instance(),
        'math': math,
        'uf': uf,
        'env': lib.env,
        # ── trigger call parameters ───────────────────────────────────────
        'value': value,
        'caller': caller,
        'source': source,
        'dest': dest,
        # ── modules documented in official examples ────────────────────────
        'datetime': datetime,
        'time': time,
        # ── item itself (not documented but was accessible before) ─────────
        'item': item,
        # ── builtins ──────────────────────────────────────────────────────
        '__builtins__': __builtins__,
    }


# ---------------------------------------------------------------------------
# run_eval  (replaces Item.__run_eval)
# ---------------------------------------------------------------------------


def run_eval(item, value=None, caller='Eval', source=None, dest=None):
    """
    Evaluate the item's ``eval`` expression.

    Called from Item.__run_eval() which is passed to the scheduler as a
    callable.  All scheduler bookkeeping stays in the Item method; this
    function contains only the evaluation logic.
    """
    if caller.lower().startswith('admin:'):
        caller = caller[6:] + ':admin'
    if (not caller.lower().startswith('eval:')) and (not caller.lower().endswith(':eval')):
        caller = 'Eval:' + caller

    if item._sh.shng_status['code'] < 14:
        logger.dbghigh(
            f'Item {item._path}: Running __run_eval before initialization is finished'
            f' - eval run ignored- caller={caller}, source={source}'
            f'  -  shng_status{item._sh.shng_status}'
        )
        return
    if item._sh.shng_status['code'] < 20 and not caller.startswith('Init'):
        logger.info(
            f'Item {item._path}: Running __run_eval before initialization is finished'
            f' - caller={caller}, source={source}, value={value}'
            f'  -  shng_status{item._sh.shng_status}'
        )
    if item._sh.shng_status['code'] > 20:
        logger.info(
            f'Item {item._path}: Running __run_eval after leaving run-mode'
            f' - caller={caller}, source={source}, value={value}'
            f'  -  shng_status{item._sh.shng_status}'
        )

    if not item._eval:
        return

    # Build the eval namespace once; reused for both condition and main eval.
    _ns = _make_eval_env(item, value=value, caller=caller, source=source, dest=dest)

    # Test if a conditional trigger is defined
    if item._trigger_condition is not None:
        try:
            try:
                cond = eval(item._trigger_condition, _ns)
            except Exception as _ce:  # COMPAT-SHIM
                cond = _eval_with_legacy_fallback(  # COMPAT-SHIM
                    item._trigger_condition, _ns, item, 'trigger_condition', _ce
                )  # COMPAT-SHIM
                if cond is _EVAL_FAILED:  # COMPAT-SHIM
                    raise _ce  # COMPAT-SHIM
            logger.warning(
                f"Item '{item._path}': Condition result '{cond}' evaluating trigger condition {item._trigger_condition}"
            )
        except Exception as e:
            log_msg = f"Item '{item._path}': Problem evaluating trigger condition '{item._trigger_condition}': {e}"
            if item._sh.shng_status['code'] != 20 and caller != 'Init':
                logger.debug(log_msg)
            else:
                logger.warning(log_msg)
            return
    else:
        cond = True

    if cond is not True:
        return

    try:
        item._history.record_trigger(caller, source, item.shtime)

        try:
            triggered = source in item._trigger
        except Exception:
            triggered = False

        if item._eval_on_trigger_only and not triggered:
            logger.info(
                f'Item {item._path} Eval triggered by:'
                f' {item._history.get_last_trigger_by()},'
                f' not in eval_triggers, but eval_on_trigger_only set.'
                f' Ignoring eval expression, setting value "{value}"'
            )
        else:
            logger.debug(
                f'Item {item._path} Eval triggered by:'
                f' {item._history.get_last_trigger_by()},'
                f' Evaluating item with value {value}.'
                f' Eval expression: {item._eval}'
            )

            # if crontab: init = x is set, x is transferred as a string;
            # re-try eval with x converted to float for that case
            _first_exc = None  # COMPAT-SHIM
            try:
                try:
                    value = eval(item._eval, _ns)
                except Exception as _e0:
                    _first_exc = _e0  # COMPAT-SHIM
                    _ns['value'] = item.cast(_ns.get('value'))
                    value = eval(item._eval, _ns)
            except Exception as _e:  # COMPAT-SHIM
                _fb = _eval_with_legacy_fallback(  # COMPAT-SHIM
                    item._eval,
                    _ns,
                    item,
                    'eval',  # COMPAT-SHIM
                    _first_exc if _first_exc is not None else _e,
                )  # COMPAT-SHIM
                if _fb is _EVAL_FAILED:  # COMPAT-SHIM
                    raise _e  # COMPAT-SHIM
                value = _fb  # COMPAT-SHIM

    except Exception as e:
        # Adding "None" as the "destination" information at end of triggered_by
        # helps figure out whether an eval expression was successfully evaluated.
        item._history.record_trigger_none(caller, source)
        if e.__class__.__name__ == 'KeyError':
            log_msg = f"Item '{item._path}': problem evaluating '{item._eval}' - KeyError (in dict)"
        else:
            log_msg = f"Item '{item._path}': problem evaluating '{item._eval}' - {e.__class__.__name__}: {e}"
        if item._sh.shng_status['code'] != 20 and caller != 'Init':
            logger.debug(log_msg + ' (status_code={}/caller={})'.format(item._sh.shng_status['code'], caller))
        else:
            logger.warning(log_msg)
    else:
        if value is None:
            logger.debug(f'Item {item._path}: evaluating {item._eval} returns None')
        else:
            item._update_item(value, caller, source, dest)


# ---------------------------------------------------------------------------
# run_on_xxx  (replaces Item._run_on_xxx)
# ---------------------------------------------------------------------------


def run_on_xxx(item, path, value, on_dest, on_eval, attr='?', caller=None, source=None, dest=None):
    """
    Common runner for on_update and on_change entries.

    :param item:    Item instance that owns this on_update/on_change list
    :param path:    item path (same as item._path)
    :param value:   current item value
    :param on_dest: destination item path, or '' for no-dest syntax
    :param on_eval: eval expression string
    :param attr:    descriptive label ('On_Change' or 'On_Update')
    """
    _ns = _make_eval_env(item, value=value, caller=caller, source=source, dest=dest)
    _ns['path'] = path  # path is also available as a convenience name

    from lib.item.items import Items

    _items_instance = Items.get_instance()

    logger.info(f"Item '{path}': '{attr}' evaluating {on_dest} = {on_eval}")

    # if syntax without '=' is used, inject caller and source into the call
    if on_dest == '':
        on_eval = on_eval.strip()
        if on_eval.endswith(')'):
            test = on_eval.replace(' ', '')
            if test.lower().find(',caller=') == -1 and test.lower().find(',source=') == -1:
                on_eval = on_eval[:-1] + ", caller='" + attr + "', source='" + path + "')"
            if test.lower().find(',caller=') > -1 and test.lower().find(',source=') == -1:
                on_eval = on_eval[:-1] + ", source='" + path + "')"
            if test.lower().find(',caller=') == -1 and test.lower().find(',source=') > -1:
                on_eval = on_eval[:-1] + ", caller='" + attr + "')"

    # evaluate the expression
    dest_value = None
    try:
        dest_value = eval(on_eval, _ns)
    except Exception as _e:
        dest_value = _eval_with_legacy_fallback(  # COMPAT-SHIM
            on_eval, _ns, item, f'{attr} on_eval', _e
        )  # COMPAT-SHIM
        if dest_value is _EVAL_FAILED:  # COMPAT-SHIM
            logger.warning(  # COMPAT-SHIM
                f"Item {path}: '{attr}' item-value='{value}'"  # COMPAT-SHIM
                f' problem evaluating {on_eval}: {_e}'  # COMPAT-SHIM
            )  # COMPAT-SHIM
            dest_value = None  # COMPAT-SHIM

    if dest_value is not None:
        if on_dest != '':
            dest_item = _items_instance.return_item(on_dest)
            if dest_item is not None:
                dest_item._update_item(dest_value, caller=attr, source=path)
                logger.debug(f" - : '{attr}' finally evaluating {on_dest} = {on_eval}, result={dest_value}")
            else:
                logger.error(
                    f"Item {path}: '{attr}' has not found dest_item '{on_dest}' = {on_eval}, result={dest_value}"
                )
        else:
            _ = eval(on_eval, _ns)
            logger.debug(f" - : '{attr}' finally evaluating {on_eval}, result={dest_value}")
    else:
        logger.debug(f" - : '{attr}' {on_dest} not set (cause: eval=None)")


# ---------------------------------------------------------------------------
# run_on_update  (replaces Item.__run_on_update)
# ---------------------------------------------------------------------------


def run_on_update(item, value=None, caller=None, source=None, dest=None):
    """Evaluate all on_update entries for *item*."""
    if item._on_update:
        for on_update_dest, on_update_eval in zip(item._on_update_dest_var, item._on_update):
            run_on_xxx(
                item,
                item._path,
                value,
                on_update_dest,
                on_update_eval,
                'On_Update',
                caller=caller,
                source=source,
                dest=dest,
            )


# ---------------------------------------------------------------------------
# run_on_change  (replaces Item.__run_on_change)
# ---------------------------------------------------------------------------


def run_on_change(item, value=None, caller=None, source=None, dest=None):
    """Evaluate all on_change entries for *item*."""
    if item._on_change:
        for on_change_dest, on_change_eval in zip(item._on_change_dest_var, item._on_change):
            run_on_xxx(
                item,
                item._path,
                value,
                on_change_dest,
                on_change_eval,
                'On_Change',
                caller=caller,
                source=source,
                dest=dest,
            )
