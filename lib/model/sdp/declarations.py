#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG.
#
#  Declarative device defaults for SmartDevicePlugin
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

"""Types for the device defaults SmartDevicePlugin classes declare as class attributes."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal


@dataclass(frozen=True)
class TransportRule:
    """Transport ``use`` (connection type or class) if parameter ``requires`` is set; always without ``requires``."""

    use: Any
    requires: str | None = None

    def matches(self, params: Mapping[str, Any]) -> bool:
        """True if the rule applies to the plugin parameters ``params``."""
        return self.requires is None or bool(params.get(self.requires))


@dataclass(frozen=True)
class CustomTokenSpec:
    """
    Custom commands addressed by custom attribute ``index``.

    ``token_re`` finds the token in replies, ``reply_re`` replaces
    ``{CUSTOM_PATTERN<index>}`` in reply patterns, ``recursive`` inherits the
    attribute from ancestor items.
    """

    index: Literal[1, 2, 3]
    token_re: str
    reply_re: str
    recursive: bool = False
