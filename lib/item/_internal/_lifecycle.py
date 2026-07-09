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
lib/item/_lifecycle.py
======================

Item lifecycle helpers extracted from lib/item/item.py.

Functions
---------
remove(item)
    Remove *item*'s own scheduler jobs, stop an in-progress fade, detach
    it from its parent's child collection, from any sh/items attribute
    binding, and from other items' trigger lists, then notify all loaded
    plugins that *item* is being deleted so they can release any
    references they hold to it.
"""

import logging

from lib.constants import PLUGIN_REMOVE_ITEM

logger = logging.getLogger('lib.item')


def _remove_scheduler_jobs(item):
    """
    Remove all scheduler jobs that may have been registered for *item*
    (cycle/crontab, autotimer/threshold timer, hysteresis up/low timers).

    ``scheduler.remove()`` is a safe no-op if a given job was never
    registered, so all four names are removed unconditionally.
    """
    base = item._itemname_prefix + item.id()
    for suffix in ('', '-Timer', '-UpTimer', '-LoTimer'):
        item._sh.scheduler.remove(base + suffix)


def _stop_fading(item):
    """
    Abort an in-progress fade on *item*, if any.

    Mirrors the pattern ``Items.stop()`` already uses globally for all
    items: clear the flag the fade loop checks (``helpers.fadejob``) and
    wake it immediately instead of letting it run out its current
    ``delta_time`` wait.
    """
    item._fading = False
    with item._lock:
        item._lock.notify_all()


def _detach_from_parent(item):
    """
    Remove *item* from its parent's child collection.

    *item*'s parent is either another ``Item`` (nested item) or the
    ``Items`` singleton (top-level item) — both expose ``_remove_child()``,
    so the call site doesn't need to distinguish the two. Tolerates a
    parent that has no ``_remove_child()`` (e.g. ``None``, or a minimal
    test setup that passes ``sh`` itself as the parent).
    """
    try:
        item._parent._remove_child(item)
    except AttributeError:
        pass


def _detach_sh_attribute(item):
    """
    Remove the ``parent.<leaf_attr>`` attribute binding every item gets
    (set by ``Items._construct_and_link()``/``Item.__init__``'s nested-child
    loop), plus the additional ``sh.<leaf_attr>`` binding top-level items
    also get.

    Only removes an attribute if it still points at exactly *item* — the
    name may since have been reassigned to something else (another item, a
    plugin, ...), in which case it must be left alone.

    Uses the leaf name (the last path segment), not the full dotted path —
    that's what was actually set as the attribute name, for both top-level
    items (whose path *is* just the leaf name) and nested ones (whose
    parent only ever got the leaf name as an attribute, never the full
    path).
    """
    leaf_attr = item.property.path.rsplit('.', 1)[-1]
    for obj in (item._parent, item._sh):
        if getattr(obj, leaf_attr, None) is item:
            delattr(obj, leaf_attr)


def _detach_from_other_items_triggers(item):
    """
    Remove *item* from every other item's ``_items_to_trigger`` /
    ``_hysteresis_items_to_trigger`` list.

    ``_parsing.init_prerun()`` appends *item* to another item's
    ``_items_to_trigger`` when that other item is named in *item*'s
    ``eval_trigger``/``trigger`` attribute, and to a sensor item's
    ``_hysteresis_items_to_trigger`` when *item*'s ``hysteresis_input``
    names that sensor. Without this, the other item keeps trying to
    trigger a deleted item on every value change.
    """
    from lib.item.items import Items

    items_instance = Items.get_instance()
    if items_instance is None:
        return

    for other in items_instance.return_items():
        if other is item:
            continue
        try:
            other._items_to_trigger.remove(item)
        except ValueError:
            pass
        try:
            other._hysteresis_items_to_trigger.remove(item)
        except ValueError:
            pass


def remove(item):
    """
    Clean up *item* usage before deletion.

    Removes *item*'s own scheduler jobs, stops an in-progress fade, detaches
    it from its parent's child collection, from any sh/items attribute
    binding, and from other items' trigger lists, then iterates over all
    loaded plugins and calls ``plugin.remove_item(item)`` on each one that
    implements the ``PLUGIN_REMOVE_ITEM`` interface. Plugins that do not
    implement the interface are collected and reported in a warning.

    :param item: ``Item`` instance being removed.
    :return:     ``True`` if all plugins handled the removal cleanly;
                 ``False`` if any plugin was incompatible.
    :rtype:      bool
    """
    _remove_scheduler_jobs(item)
    _stop_fading(item)
    _detach_from_parent(item)
    _detach_sh_attribute(item)
    _detach_from_other_items_triggers(item)

    incompatible = []

    for plugin in item.plugins.return_plugins():
        if hasattr(plugin, PLUGIN_REMOVE_ITEM):
            try:
                plugin.remove_item(item)
            except Exception as e:
                logger.warning(f'while removing item {item} from plugin {plugin}, the following error occurred: {e}')
        else:
            incompatible.append(plugin.get_shortname())

    if incompatible:
        logger.warning(
            f'while removing item {item}, the following plugins were incompatible: {", ".join(incompatible)}'
        )
        return False

    return True
