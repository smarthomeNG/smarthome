#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG.
#
#  Typed contracts between SmartDevicePlugin, protocols and connections
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
Typed contracts between SmartDevicePlugin, protocols and connections.

- ``DeviceConfig``: static connection and protocol settings
- ``ConnectionHooks``: callbacks a connection or protocol reports to
- ``SchedulerPort``: scheduler access for protocols with timed jobs
- ``SendData``: keys of the ``data_dict`` sent to a connection
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Protocol, TypedDict

from lib.model.sdp.globals import (
    PLUGIN_ATTR_CB_ON_CONNECT,
    PLUGIN_ATTR_CB_ON_DISCONNECT,
    PLUGIN_ATTR_CB_SUSPEND,
    sanitize_param,
)

#: parameters holding runtime objects instead of configuration
RUNTIME_PARAMS = frozenset(('plugin', PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_ON_DISCONNECT, PLUGIN_ATTR_CB_SUSPEND))


def _empty_mapping() -> Mapping[str, Any]:
    return MappingProxyType({})


@dataclass(frozen=True)
class DeviceConfig:
    """
    Connection and protocol settings of a device.

    Field names are the plugin parameter names. ``explicit`` holds the fields
    set from parameters or defaults; ``with_defaults`` only fills the others.
    ``extra`` holds all other configuration parameters, e.g. ``viess_proto``.
    """

    host: str = ''
    port: int = 0
    serialport: str = ''
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = 'N'
    stopbits: int = 1
    timeout: float = 1.0
    terminator: str | bytes | int = ''
    binary: bool = False
    autoreconnect: bool = True
    autoconnect: bool = True
    connect_retries: int = 3
    connect_cycle: int = 5
    retry_cycle: int = 30
    retry_suspend: int = 0
    conn_type: str | type | None = None
    protocol: str | type | None = None
    send_retries: int = 0
    send_retries_cycle: int = 1
    send_timeout: float = 5
    json_move_keys: tuple[str, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=_empty_mapping)
    explicit: frozenset[str] = frozenset()

    @classmethod
    def fields(cls) -> frozenset[str]:
        """Names of the settings fields."""
        return frozenset(f.name for f in dataclasses.fields(cls)) - {'extra', 'explicit'}

    @classmethod
    def from_params(cls, params: Mapping[str, Any]) -> DeviceConfig:
        """
        Build the configuration from plugin parameters.

        ``None`` values count as unset, string values are sanitized.

        :param params: plugin parameters
        """
        names = cls.fields()
        values: dict[str, Any] = {}
        for name in names:
            value = params.get(name)
            if value is None:
                continue
            value = sanitize_param(value)
            values[name] = tuple(value) if name == 'json_move_keys' else value
        extra = {key: val for key, val in params.items() if key not in names and key not in RUNTIME_PARAMS}
        return cls(**values, extra=MappingProxyType(extra), explicit=frozenset(values))

    def with_defaults(self, defaults: Mapping[str, Any]) -> DeviceConfig:
        """
        Return the configuration with ``defaults`` for the fields not set yet.

        :param defaults: field values by field name
        :raises TypeError: if ``defaults`` names an unknown field
        """
        unset = {name: value for name, value in defaults.items() if name not in self.explicit}
        return dataclasses.replace(self, **unset, explicit=self.explicit | frozenset(defaults))


def _abort_by_suspend(suspend: Callable[..., Any]) -> Callable[[str], None]:
    def on_abort(by: str) -> None:
        suspend(True, by=by)

    return on_abort


@dataclass(frozen=True)
class ConnectionHooks:
    """
    Callbacks of a connection or protocol.

    ``on_data(by, data)`` receives data, ``on_connect(by)`` and
    ``on_disconnect(by)`` report connection changes, ``on_abort(by)`` reports
    giving up on connecting.
    """

    on_data: Callable[..., None] | None = None
    on_connect: Callable[[Any], None] | None = None
    on_disconnect: Callable[[Any], None] | None = None
    on_abort: Callable[[str], None] | None = None

    @classmethod
    def from_params(cls, on_data: Callable[..., None] | None, params: Mapping[str, Any]) -> ConnectionHooks:
        """
        Build the hooks from a data callback and the callback parameters of the pre-2.0 constructor.

        :param on_data: data callback
        :param params: parameters with the callbacks under the ``PLUGIN_ATTR_CB_*`` keys
        """
        suspend = params.get(PLUGIN_ATTR_CB_SUSPEND)
        return cls(
            on_data=on_data,
            on_connect=params.get(PLUGIN_ATTR_CB_ON_CONNECT),
            on_disconnect=params.get(PLUGIN_ATTR_CB_ON_DISCONNECT),
            on_abort=_abort_by_suspend(suspend) if suspend else None,
        )


class SchedulerPort(Protocol):
    """Scheduler access by job name, as provided by SmartPlugin."""

    def scheduler_add(
        self, name: str, obj: object, prio: int = 3, cron=None, cycle=None, value=None, offset=None, next=None
    ) -> None: ...

    def scheduler_get(self, name: str) -> Any: ...

    def scheduler_remove(self, name: str) -> None: ...


class SendData(TypedDict, total=False):
    """Keys of the ``data_dict`` sent to a connection."""

    payload: Any
    data: Any
    limit_response: bytes | int
    request_method: str
    params: dict[str, Any]
    headers: dict[str, Any]
    cookies: dict[str, Any]
    files: dict[str, Any]
    command: str
    method: str
    message_id: str
    repeat: int
