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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Exceptions raised by item writes.

A regular item write (``item(value)``, ``item.set(value)``) logs a warning and drops a value the item does not
accept. With ``strict=True`` the write raises :class:`ItemWriteRejected` instead, so the caller learns that and
why the value was dropped.
"""

from enum import Enum


class WriteRejectReason(str, Enum):
    """Why an item dropped a written value."""

    TYPE = 'type'
    """The value cannot be cast to the item type."""

    FADING = 'fading'
    """The item is fading, and the fade's ``stop_fade``/``continue_fade`` lists do not let this caller stop it."""


class ItemWriteRejected(ValueError):
    """
    Raised by a strict item write that the item dropped; the item keeps its value.

    :ivar item_path: path of the item written to
    :ivar value: the value as passed by the caller
    :ivar reason: why the item dropped it
    """

    def __init__(self, item_path: str, value: object, reason: WriteRejectReason, message: str):
        """
        :param item_path: path of the item written to
        :param value: the value as passed by the caller
        :param reason: why the item dropped it
        :param message: human-readable description, also the exception's ``str()``
        """
        super().__init__(message)
        self.item_path = item_path
        self.value = value
        self.reason = reason
