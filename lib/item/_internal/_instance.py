#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
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
The item attribute ``instance``: normalization and inheritance by child items.

An item's own ``instance`` is a section name of ``plugin.yaml`` or a list of them. The value that applies
to the item (its own, or the nearest ancestor's) is stored in ``item.conf['instance']`` as a list of
strings, where ``''`` stands for the default (unnamed) plugin instance. SmartPlugin reads it when it
resolves plugin attributes.
"""

import logging
from collections.abc import Collection

from lib.constants import INSTANCE_DEFAULT, KEY_INSTANCE

logger = logging.getLogger(__name__)


def normalize_instances(value) -> list[str]:
    """
    Convert the configured value of ``instance`` to a list of section names

    :param value: a section name, a list of section names, or None
    :return: list of names; ``''`` for an empty value or the keyword ``default``
    """
    entries = value if isinstance(value, (list, tuple)) else [value]
    names = (str(entry).strip() if entry is not None else '' for entry in entries)
    return ['' if name == INSTANCE_DEFAULT else name for name in names]


def apply_effective_instance(item, config: Collection[str]) -> None:
    """
    Record the item's own ``instance`` and store the effective value in ``item.conf``

    An item without an own ``instance`` takes the effective value of its parent. Nothing is stored if
    no item in the chain sets one, or if ``legacy_instances`` is set: ``instance`` then only names the
    instance of a struct.

    :param item: ``Item`` instance whose ``conf`` has been built from *config*
    :param config: attribute configuration the item is built from
    """
    item._own_instance = None
    if getattr(item._sh, '_legacy_instances', False):
        return
    own = normalize_instances(config[KEY_INSTANCE]) if KEY_INSTANCE in config else None
    item._own_instance = own
    if own:
        _warn_unknown_sections(item, own)
    effective = own if own is not None else _inherited_instances(item)
    if effective is not None:
        item.conf[KEY_INSTANCE] = list(effective)


def _warn_unknown_sections(item, names: Collection[str]) -> None:
    """
    Log a warning for every name that is no section of the plugin configuration

    :param item: ``Item`` instance that sets the names
    :param names: normalized ``instance`` entries of the item
    """
    plugins = item.plugins
    if plugins is None:
        return
    sections = plugins.get_section_names()
    for name in names:
        if name and name not in sections:
            logger.warning(f"Item {item._path}: instance '{name}' is not a section of the plugin configuration")


def _inherited_instances(item) -> list[str] | None:
    """
    Return the effective ``instance`` of the item's parent, or None if there is none

    :param item: ``Item`` instance
    """
    return getattr(item._parent, 'conf', {}).get(KEY_INSTANCE)


def inheriting_descendants(item) -> list:
    """
    Return the descendants whose effective ``instance`` comes from *item* or its ancestors

    The walk does not enter the subtree of a descendant that sets its own ``instance``. A parent is
    listed before its children.

    :param item: ``Item`` instance to start at
    :return: list of ``Item`` instances
    """
    found = []
    for child in item.return_children():
        if child._own_instance is None:
            found.append(child)
            found.extend(inheriting_descendants(child))
    return found


def refresh_inherited_instance(item) -> None:
    """
    Take over the effective ``instance`` of the parent into the ``conf`` of an item without its own

    :param item: ``Item`` instance that sets no ``instance`` itself
    """
    inherited = _inherited_instances(item)
    if inherited is None:
        item.conf.pop(KEY_INSTANCE, None)
    else:
        item.conf[KEY_INSTANCE] = list(inherited)
