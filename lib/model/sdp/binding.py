#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG.
#
#  Item bindings and command references for SmartDevicePlugin
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

"""Item bindings, command references and the cyclic read schedule of SmartDevicePlugin."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Flag, auto
from typing import Literal

from lib.model.sdp.globals import CUSTOM_SEP


class CommandRef(str):
    """
    Device command, optionally with a custom token.

    Its str value is the wire form ``name`` or ``name#token``; ``name`` and
    ``token`` hold the parts. String operations return plain str, see parse().
    """

    name: str
    token: str | None

    def __new__(cls, name: str, token: str | None = None) -> CommandRef:
        ref = super().__new__(cls, name if token is None else f'{name}{CUSTOM_SEP}{token}')
        ref.name = name
        ref.token = token
        return ref

    def __getnewargs__(self) -> tuple[str, str | None]:
        return self.name, self.token

    @classmethod
    def parse(cls, raw: str | CommandRef) -> CommandRef:
        """Return ``raw`` as CommandRef, split at the first ``#``."""
        if isinstance(raw, CommandRef):
            return raw
        name, sep, token = raw.partition(CUSTOM_SEP)
        return cls(name, token if sep else None)

    def with_token(self, token: str | None) -> CommandRef:
        """This command with ``token`` (None: without token)."""
        return CommandRef(self.name, token)


class ItemRole(Flag):
    """What an item does for the plugin; roles combine. Every item with a command receives its values."""

    NONE = 0
    #: has its (readable) command read on request, initially, cyclically or in read groups
    READ = auto()
    #: sends its value to the device with its (writable) command
    WRITE = auto()
    #: triggers reading its read group when set
    GROUP_TRIGGER = auto()
    #: holds a lookup table of the plugin
    LOOKUP = auto()
    #: holds the valid_list of a command
    VALID_LIST = auto()


#: lookup table modes an item can hold: forward/reverse dict, case-insensitive reverse dict, key list
LookupMode = Literal['fwd', 'rev', 'rci', 'list']


@dataclass(frozen=True)
class ValidListBinding:
    """The valid_list of ``command`` held by an item, ``ci``/``re`` for its variants."""

    command: str
    ci: bool = False
    re: bool = False


@dataclass
class ItemBinding:
    """
    An item's configuration for the plugin, as derived by parse_item().

    ``read_initial`` and ``cycle`` apply to the command of a READ item and to
    the trigger group of a GROUP_TRIGGER item.
    """

    roles: ItemRole = ItemRole.NONE
    #: command of the item, with custom token if custom commands are active
    command: CommandRef | None = None
    #: read groups the command is read in (READ role), with custom token
    read_groups: tuple[str, ...] = ()
    #: read on startup
    read_initial: bool = False
    #: cyclic read interval in seconds, shortest of item and plugin-wide cycle
    cycle: float | None = None
    #: read group triggered by the item (GROUP_TRIGGER role), with custom token; '0' is all commands
    trigger_group: str | None = None
    #: lookup table name and mode held by the item (LOOKUP role)
    lookup: tuple[str, LookupMode] | None = None
    #: valid_list held by the item (VALID_LIST role)
    valid_list: ValidListBinding | None = None
    #: custom attribute values by index 1..3
    custom: dict[int, str | None] = field(default_factory=lambda: {1: None, 2: None, 3: None})


@dataclass
class _CyclicEntry:
    cycle: float
    next: float = 0


class CyclicSchedule:
    """Cycles and due times of cyclically read commands and triggered read groups."""

    def __init__(self) -> None:
        self._commands: dict[str, _CyclicEntry] = {}
        self._groups: dict[str, _CyclicEntry] = {}

    @staticmethod
    def _sync(entries: dict[str, _CyclicEntry], cycles: Mapping[str, float]) -> dict[str, _CyclicEntry]:
        return {key: _CyclicEntry(cycle, entries[key].next if key in entries else 0) for key, cycle in cycles.items()}

    def sync(self, commands: Mapping[str, float], groups: Mapping[str, float]) -> None:
        """Set the cycles by command and by group; due times of kept entries stay."""
        self._commands = self._sync(self._commands, commands)
        self._groups = self._sync(self._groups, groups)

    def shortest_cycle(self) -> float | None:
        """Shortest cycle, None if none is configured."""
        cycles = [e.cycle for e in (*self._commands.values(), *self._groups.values())]
        return min(cycles) if cycles else None

    def due_commands(self, now: float) -> list[str]:
        """Commands due at ``now``."""
        return [key for key, e in self._commands.items() if e.next <= now]

    def due_groups(self, now: float) -> list[str]:
        """Read groups due at ``now``."""
        return [key for key, e in self._groups.items() if e.next <= now]

    def mark_command_read(self, command: str, now: float) -> None:
        """``command`` was read at ``now``."""
        entry = self._commands[command]
        entry.next = now + entry.cycle

    def mark_group_triggered(self, group: str, now: float) -> None:
        """``group`` was triggered at ``now``."""
        entry = self._groups[group]
        entry.next = now + entry.cycle
