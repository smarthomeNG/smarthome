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
Hysteresis state-machine execution for Item.

Extracted from lib/item/item.py.

Entry points
------------
run_hysteresis(item, value, caller, source, dest)
    Evaluate the hysteresis state machine for an item.
    Replaces Item.__run_hysteresis().

get_hysteresis_state(item)
    Return the human-readable hysteresis state string.
    Replaces Item.hysteresis_state().

get_hysteresis_data(item)
    Return a dict with full hysteresis diagnostics.
    Replaces Item.hysteresis_data().

All functions access only single-underscore attributes and the proxies
_update_item() / _run_attribute_eval() that Item exposes for extracted modules.
"""

import datetime
import logging
import time as _time

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _onoff(value: bool) -> str:
    return 'On' if value else 'Off'


def _get_hysteresis_state_string(
    item, lower: float, upper: float, input_value: float, log: bool = False, txt: str = ''
) -> str:
    """
    Return a human-readable representation of the current hysteresis state.

    :param item:        Item instance
    :param lower:       resolved lower threshold value
    :param upper:       resolved upper threshold value
    :param input_value: current value of the hysteresis input item
    :param log:         emit notice-level log messages if True
    :param txt:         context label for log messages
    :return:            state string
    """
    if log:
        logger.notice(f'{item._path}: {txt}')

    state = ''
    if input_value > upper:
        if item._hysteresis_upper_timer_active:
            state = 'Timer -> '
        state += 'On'
        if log:
            logger.notice(f' -> {state} - {txt}')
    elif input_value < lower:
        if item._hysteresis_lower_timer_active:
            state = 'Timer -> '
        state += 'Off'
        if log:
            logger.notice(f' -> {state} - {txt}')
    else:
        state = 'Stay (' + _onoff(item._value) + ')'
        if log:
            logger.notice(f' -> {state} - {txt}')

    if not item._hysteresis_upper_timer_active and not item._hysteresis_lower_timer_active:
        if item._history.get_last_update_by().lower() == 'init:cache':
            if not state.startswith('Stay'):
                if state != _onoff(item._value):
                    state = 'Cached (' + _onoff(item._value) + ')'
                    if log:
                        logger.notice(f' -> {state} - {txt}')

    return state


# ---------------------------------------------------------------------------
# run_hysteresis  (replaces Item.__run_hysteresis)
# ---------------------------------------------------------------------------


def run_hysteresis(item, value=None, caller='Hysteresis', source=None, dest=None):
    """
    Evaluate the hysteresis state machine for *item*.

    Called from Item.__run_hysteresis() which is passed to the scheduler as
    a callable.
    """
    item._hysteresis_state_set = None

    upper = item._run_attribute_eval(item._hysteresis_upper_threshold)
    lower = item._run_attribute_eval(item._hysteresis_lower_threshold)

    if item._hysteresis_upper_timer_active and value <= upper:
        item._sh.scheduler.remove(item._itemname_prefix + item.id() + '-UpTimer')
        item._hysteresis_upper_timer_active = False
        item._hysteresis_active_timer_ends = None

    if item._hysteresis_lower_timer_active and value >= lower:
        item._sh.scheduler.remove(item._itemname_prefix + item.id() + '-LoTimer')
        item._hysteresis_lower_timer_active = False
        item._hysteresis_active_timer_ends = None

    if value > upper:
        if item._hysteresis_upper_timer is None:
            item._update_item(True, caller, source, dest)
        else:
            if not item._hysteresis_upper_timer_active and item._value is False:
                timer = item._run_attribute_eval(item._hysteresis_upper_timer)
                if timer < 0:
                    logger.warning(
                        f"Item '{item._path}': Hysteresis upper-timer evaluated to"
                        f' an value less than zero ({timer}), using 0 instead'
                    )
                    timer = 0
                item._hysteresis_upper_timer_active = True
                next_time = item.shtime.now() + datetime.timedelta(seconds=timer)
                item.active_timer_ends = next_time
                if item._hysteresis_log:
                    logger.notice(f'__run_hysteresis {item._path}: scheduler.add {item._path}-UpTimer')
                item._sh.scheduler.add(
                    item._itemname_prefix + item.id() + '-UpTimer',
                    item.__call__,
                    value={'value': True, 'caller': 'Hysteresis'},
                    next=next_time,
                )

    if value < lower:
        if item._hysteresis_lower_timer is None:
            item._update_item(False, caller, source, dest)
        else:
            if not item._hysteresis_lower_timer_active and item._value is True:
                timer = item._run_attribute_eval(item._hysteresis_lower_timer)
                if timer < 0:
                    logger.warning(
                        f"Item '{item._path}': Hysteresis lower-timer evaluated to"
                        f' an value less than zero ({timer}), using 0 instead'
                    )
                    timer = 0
                item._hysteresis_lower_timer_active = True
                next_time = item.shtime.now() + datetime.timedelta(seconds=timer)
                item._hysteresis_active_timer_ends = next_time
                if item._hysteresis_log:
                    logger.notice(f'__run_hysteresis {item._path}: scheduler.add {item._path}-LoTimer')
                item._sh.scheduler.add(
                    item._itemname_prefix + item.id() + '-LoTimer',
                    item.__call__,
                    value={'value': False, 'caller': 'Hysteresis'},
                    next=next_time,
                )


# ---------------------------------------------------------------------------
# get_hysteresis_state  (replaces Item.hysteresis_state)
# ---------------------------------------------------------------------------


def get_hysteresis_state(item):
    """
    Return the inner hysteresis state as a human-readable string.

    Available in SmartHomeNG v1.10 and above.
    """
    if item._hysteresis_input is None:
        return None

    _time.sleep(0.1)  # prevent execution before xxx_timer_active could be updated

    upper = item._run_attribute_eval(item._hysteresis_upper_threshold)
    lower = item._run_attribute_eval(item._hysteresis_lower_threshold)

    from lib.item.items import Items

    input_value = Items.get_instance().return_item(item._hysteresis_input)()

    if item._hysteresis_state_set is None:
        state = _get_hysteresis_state_string(
            item, lower, upper, input_value, log=item._hysteresis_log, txt='hysteresis_state'
        )
    else:
        state = ['Set (Off)', 'Set (On)'][item._hysteresis_state_set]

    if item._hysteresis_log:
        logger.notice(
            f'hysteresis_state ({item._path}): state={state},'
            f' input_value={input_value}, value={item._value},'
            f' __updated_by={item._history.get_last_update_by()}'
        )
    return state


# ---------------------------------------------------------------------------
# get_hysteresis_data  (replaces Item.hysteresis_data)
# ---------------------------------------------------------------------------


def get_hysteresis_data(item):
    """
    Return a dict with full hysteresis diagnostics.

    Returns a dict with the current hysteresis data:
    lower threshold, upper threshold, input value, output value and internal state.

    Available in SmartHomeNG v1.10 and above.
    """
    _time.sleep(0.1)  # prevent execution before xxx_timer_active could be updated

    upper = item._run_attribute_eval(item._hysteresis_upper_threshold)
    upper_timer = (
        None if item._hysteresis_upper_timer is None else item._run_attribute_eval(item._hysteresis_upper_timer)
    )
    lower = item._run_attribute_eval(item._hysteresis_lower_threshold)
    lower_timer = (
        None if item._hysteresis_lower_timer is None else item._run_attribute_eval(item._hysteresis_lower_timer)
    )

    from lib.item.items import Items

    input_value = Items.get_instance().return_item(item._hysteresis_input)()

    if item._hysteresis_state_set is None:
        state = _get_hysteresis_state_string(
            item, lower, upper, input_value, log=item._hysteresis_log, txt='hysteresis_data'
        )
    else:
        state = ['Set (Off)', 'Set (On)'][item._hysteresis_state_set]

    data = {
        'lower_threshold': lower,
        'lower_timer': lower_timer,
        'upper_threshold': upper,
        'upper_timer': upper_timer,
        'input': input_value,
        'output': item._value,
        'state': state,
        'lower_timer_active': item._hysteresis_lower_timer_active,
        'upper_timer_active': item._hysteresis_upper_timer_active,
        'state_set': item._hysteresis_state_set,
    }
    if (
        item._hysteresis_lower_timer_active or item._hysteresis_upper_timer_active
    ) and item._hysteresis_active_timer_ends is not None:
        data['active_timer_ends'] = (
            item._hysteresis_active_timer_ends.strftime('%d.%m.%Y %H:%M:%S')
            + ' '
            + item._hysteresis_active_timer_ends.tzname()
        )
    if item._hysteresis_log:
        logger.notice(f'hysteresis_data ({item._path}): {data}, __updated_by={item._history.get_last_update_by()}')
    return data
