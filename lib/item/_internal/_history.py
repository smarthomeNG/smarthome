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
Item history data holder.

Extracted from lib/item/item.py.

``ItemHistory`` stores the timestamp, caller, and value history for an Item.
Item creates one instance as ``self._history`` during ``__init__`` and
delegates all reads and writes through it.

Write paths (called from item.py):
  record_change(old_value, caller, source, shtime, ...)
      fired by _set_value() when the item's value actually changes

  record_update_only(caller, source, shtime)
      fired by __update() when the same value is written again
      (no change → last_update advances but last_change does not)

  record_trigger(caller, source, shtime)
      fired by __run_eval() when an eval trigger fires

  set_initial_value_caller(caller)
      called after the initial value is set in __init__

  set_from_cache(cache_time, caller)
      called when a cached value is restored

Read paths:
  Getters mirror the private attribute names that were previously held
  directly on Item (``__last_change`` etc.) so that all call-sites in
  item.py and property.py need only trivial one-line changes.
"""


class ItemHistory:
    """
    Holds change, update, trigger and value history for an Item.

    All attributes use a single underscore (no name-mangling) because this
    class lives outside the Item class body.
    """

    __slots__ = (
        '_last_change',
        '_prev_change',
        '_changed_by',
        '_prev_change_by',
        '_last_update',
        '_prev_update',
        '_updated_by',
        '_prev_update_by',
        '_last_trigger',
        '_prev_trigger',
        '_triggered_by',
        '_prev_trigger_by',
        '_last_value',
        '_prev_value',
    )

    def __init__(self, initial_time):
        now = initial_time
        self._last_change = now
        self._prev_change = now
        self._last_update = now
        self._prev_update = now
        self._last_trigger = now
        self._prev_trigger = now
        self._changed_by = 'Init:None'
        self._updated_by = 'Init:None'
        self._triggered_by = 'N/A'
        self._prev_change_by = 'N/A'
        self._prev_update_by = 'N/A'
        self._prev_trigger_by = 'N/A'
        self._last_value = None
        self._prev_value = None

    # -----------------------------------------------------------------------
    # Write paths
    # -----------------------------------------------------------------------

    def record_change(self, old_value, caller, source, shtime, prev_change=None, last_change=None):
        """
        Record a value change.  Called from Item._set_value() after the
        value has already been mutated.

        :param old_value:   the item's _value *before* the mutation
        :param caller:      caller string
        :param source:      source string (may be None)
        :param shtime:      Shtime instance (for current timestamp)
        :param prev_change: override for prev_change (used on cache restore)
        :param last_change: override for last_change (used on cache restore)
        """
        self._prev_value = self._last_value
        self._last_value = old_value

        self._prev_change = self._last_change if prev_change is None else prev_change
        self._last_change = shtime.now() if last_change is None else last_change

        self._prev_update = self._last_update
        self._last_update = self._last_change

        caller_source = '{0}:{1}'.format(caller, source)
        self._prev_change_by = self._changed_by
        self._prev_update_by = self._updated_by
        self._changed_by = caller_source
        self._updated_by = caller_source
        self._triggered_by = caller_source

    def record_update_only(self, caller, source, shtime):
        """
        Record a same-value write (no change).  Called from Item.__update()
        when the new value equals the current value and enforce_change is off.

        last_change is *not* advanced; only last_update moves.
        """
        self._prev_update = self._last_update
        self._last_update = shtime.now()
        self._prev_update_by = self._updated_by
        self._updated_by = '{0}:{1}'.format(caller, source)

    def record_trigger(self, caller, source, shtime):
        """
        Record an eval-trigger event.  Called from Item.__run_eval().
        Advances last_trigger / prev_trigger tracking.
        """
        self._prev_trigger_by = self._triggered_by
        self._triggered_by = '{0}:{1}'.format(caller, source)
        self._prev_trigger = self._last_trigger
        self._last_trigger = shtime.now()

    def set_initial_value_caller(self, caller):
        """Called when an initial value is set in Item.__init__."""
        self._changed_by = caller
        self._updated_by = caller

    def set_from_cache(self, cache_time, caller):
        """
        Restore history from a cache read.  Called during Item.__init__
        after cache_read() succeeds.

        :param cache_time: mtime of the cache file (datetime with tz)
        :param caller:     caller string (e.g. 'Init:Cache')
        """
        self._last_change = cache_time
        self._prev_change = cache_time
        self._last_update = cache_time
        self._prev_update = cache_time
        self._changed_by = caller
        self._updated_by = caller
        self._triggered_by = 'N/A'

    def record_trigger_none(self, caller, source):
        """
        Called from __run_eval when the eval result is None.
        Only updates triggered_by (no timestamp advance).
        """
        self._triggered_by = '{0}:{1}:None'.format(caller, source)

    # -----------------------------------------------------------------------
    # Read paths (used by Item._get_*() delegation methods)
    # -----------------------------------------------------------------------

    def get_last_change(self):
        return self._last_change

    def get_last_change_by(self):
        return self._changed_by

    def get_last_update(self):
        return self._last_update

    def get_last_update_by(self):
        return self._updated_by

    def get_last_trigger(self):
        return self._last_trigger

    def get_last_trigger_by(self):
        return self._triggered_by

    def get_last_value(self):
        return self._last_value

    def get_prev_change(self):
        return self._prev_change

    def get_prev_change_by(self):
        return self._prev_change_by

    def get_prev_update(self):
        return self._prev_update

    def get_prev_update_by(self):
        return self._prev_update_by

    def get_prev_trigger(self):
        return self._prev_trigger

    def get_prev_trigger_by(self):
        return self._prev_trigger_by

    def get_prev_value(self):
        return self._prev_value
