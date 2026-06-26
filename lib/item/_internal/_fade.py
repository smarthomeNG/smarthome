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
lib/item/_fade.py
=================

Fade/ramp helper extracted from lib/item/item.py.

Functions
---------
fade(item, dest, step, delta, caller, stop_fade, continue_fade,
     instant_set, update)
    Smoothly ramp an item's value to *dest* by scheduling repeated
    ``fadejob`` calls via the SmartHomeNG scheduler.

The actual step-by-step logic lives in ``fadejob`` (``lib/item/helpers.py``);
this function only validates parameters, stores fade state, and triggers the
first scheduler call.
"""

import logging

from ..helpers import fadejob

logger = logging.getLogger('lib.item')


def fade(item, dest, step=1, delta=1, caller=None, stop_fade=None, continue_fade=None, instant_set=True, update=False):
    """
    Fade (ramp) *item*'s value to *dest*.

    :param item:          ``Item`` instance.
    :param dest:          Target value (converted to ``float``).
    :param step:          Step size per interval.
    :param delta:         Seconds between steps.
    :param caller:        Passed as source to downstream item updates.
                          The caller recorded on the item will always be
                          ``'Fader'``.
    :param stop_fade:     List of caller names that will abort an ongoing
                          fade.  Any other caller is ignored.  Pass ``None``
                          to let any caller stop the fade.
    :param continue_fade: List of caller names that exclusively *continue*
                          fading; all other callers will stop it.
    :param instant_set:   When ``True`` the first step is applied immediately;
                          when ``False`` only after *delta* seconds.
    :param update:        When ``True`` an already-running fade is updated
                          with the new parameters on the fly.
    """
    if stop_fade and not isinstance(stop_fade, list):
        logger.warning(f'stop_fade parameter {stop_fade} for fader {item} has to be a list. Ignoring')
        stop_fade = None
    if continue_fade and not isinstance(continue_fade, list):
        logger.warning(f'continue_fade parameter {continue_fade} for fader {item} has to be a list. Ignoring')
        continue_fade = None

    dest = float(dest)
    if not item._fading or (item._fading and update):
        item._fadingdetails = {
            'value': item._value,
            'dest': dest,
            'step': step,
            'delta': delta,
            'caller': caller,
            'stop_fade': stop_fade,
            'continue_fade': continue_fade,
            'instant_set': instant_set,
        }
    item._sh.trigger(item._path, fadejob, value={'item': item})
