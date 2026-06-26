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
    Remove *item*'s own scheduler jobs and notify all loaded plugins that
    *item* is being deleted so they can release any references they hold
    to it.
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


def remove(item):
    """
    Clean up *item* usage before deletion.

    Removes *item*'s own scheduler jobs, then iterates over all loaded
    plugins and calls ``plugin.remove_item(item)`` on each one that
    implements the ``PLUGIN_REMOVE_ITEM`` interface. Plugins that do not
    implement the interface are collected and reported in a warning.

    :param item: ``Item`` instance being removed.
    :return:     ``True`` if all plugins handled the removal cleanly;
                 ``False`` if any plugin was incompatible.
    :rtype:      bool
    """
    _remove_scheduler_jobs(item)

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
