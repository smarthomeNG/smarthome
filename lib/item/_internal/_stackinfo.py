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
lib/item/_stackinfo.py
======================

Call-stack inspection helpers extracted from lib/item/item.py.

Used to enrich log messages with caller context when dict/list entries
are accessed via eval expressions.

Functions
---------
get_class_from_frame(item, fr)
    Return a debug string describing the arguments visible in frame *fr*.

get_calling_item_from_frame(item, fr)
    Return the string representation of the ``self`` argument in frame *fr*,
    used to identify which Item triggered an eval call.

get_stack_info(item)
    Walk the call stack (level 4) and return a human-readable caller string.
"""

import inspect


def get_class_from_frame(item, fr):
    """
    Return a debug string for the given frame.

    Inspects the local variables of *fr* and returns a string of the form
    ``args=<names>  - value_dict=<locals>`` for diagnostic purposes.

    :param item: ``Item`` instance (unused but kept for API symmetry).
    :param fr:   Frame object (e.g. from ``inspect.stack()[n].frame``).
    :return:     Diagnostic string.
    :rtype:      str
    """
    args, _, _, value_dict = inspect.getargvalues(fr)
    return f'args={args}  - value_dict={value_dict}'


def get_calling_item_from_frame(item, fr):
    """
    Return the ``self`` argument visible in *fr* as a string.

    If the frame belongs to an Item method, this returns the string
    representation of that Item — useful for identifying which Item's
    eval triggered a dict/list lookup.

    :param item: ``Item`` instance (unused but kept for API symmetry).
    :param fr:   Frame object.
    :return:     ``str(self)`` from the frame's local scope, or ``'None'``.
    :rtype:      str
    """
    args, _, _, value_dict = inspect.getargvalues(fr)
    return f'{value_dict.get("self", None)}'


def get_stack_info(item):
    """
    Return a one-line caller description from call-stack level 4.

    If level 4 is ``__run_eval``, the calling Item is identified via
    :func:`get_calling_item_from_frame`.  Otherwise the function name is
    returned with ``()`` appended.

    :param item: ``Item`` instance (used to call helper functions).
    :return:     Short caller description string.
    :rtype:      str
    """
    msg = ''
    for level in range(4, 5):
        try:
            frame_info = inspect.stack()[level]
            if frame_info.function == '__run_eval':
                msg += f"Item '{get_calling_item_from_frame(item, frame_info.frame)}'"
            else:
                msg += f'{frame_info.function}()'
        except Exception as ex:
            msg += f' - error getting code {ex}'
    return msg
