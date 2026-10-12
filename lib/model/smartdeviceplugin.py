#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms           Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG
#
#  SmartDevicePlugin class and standalone routines
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

# allow "modern" type hints in Python 3.9
from __future__ import annotations

import logging
import importlib
import re
import os
import sys
import time
import json
import datetime
from collections import ChainMap
from functools import partial
import textwrap
import ruamel.yaml as yaml
from copy import deepcopy
from ast import literal_eval
from collections import OrderedDict, deque
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, ClassVar, Tuple

import lib.shyaml as shyaml
from lib.metadata import Metadata
from lib.model.smartplugin import SmartPlugin, SmartPluginWebIf
from lib.item.item import Item
from lib.plugin import Plugins
from lib.shtime import Shtime

from lib.model.sdp.globals import (
    update,
    SDPError,
    PLUGIN_ATTR_SEND_TIMEOUT,
    ATTR_NAMES,
    CMD_ATTR_CMD_SETTINGS,
    CMD_ATTR_ITEM_ATTRS,
    CMD_ATTR_ITEM_TYPE,
    CMD_ATTR_LOOKUP,
    CMD_ATTR_OPCODE,
    CMD_ATTR_PARAMS,
    CMD_ATTR_READ,
    CMD_ATTR_READ_CMD,
    CMD_ATTR_WRITE,
    CMD_IATTR_ATTRIBUTES,
    CMD_ATTR_SEND_RETRIES,
    CMD_IATTR_CYCLE,
    CMD_IATTR_ENFORCE,
    CMD_IATTR_INITIAL,
    CMD_ATTR_REPLY_PATTERN,
    CMD_IATTR_LOOKUP_ITEM,
    CMD_IATTR_READ_GROUPS,
    CMD_IATTR_RG_LEVELS,
    CMD_IATTR_CUSTOM1,
    CMD_IATTR_CUSTOM2,
    CMD_IATTR_CUSTOM3,
    PATTERN_CUSTOM_PATTERN,
    CMD_IATTR_TEMPLATE,
    COMMAND_READ,
    COMMAND_SEP,
    COMMAND_WRITE,
    CUSTOM_SEP,
    INDEX_GENERIC,
    INDEX_MODEL,
    ITEM_ATTR_COMMAND,
    ITEM_ATTR_CUSTOM1,
    ITEM_ATTR_CUSTOM2,
    ITEM_ATTR_CUSTOM3,
    ITEM_ATTR_CYCLE,
    ITEM_ATTR_GROUP,
    ITEM_ATTR_LOOKUP,
    ITEM_ATTR_READ,
    ITEM_ATTR_READ_GRP,
    ITEM_ATTR_READ_INIT,
    ITEM_ATTR_WRITE,
    PLUGIN_ATTR_DELAY_INITIAL,
    PLUGIN_ATTR_CMD_CLASS,
    PLUGIN_ATTR_CONNECTION,
    PLUGIN_ATTR_SUSPEND_ITEM,
    PLUGIN_ATTR_CONN_AUTO_RECONN,
    PLUGIN_ATTR_CONN_AUTO_CONN,
    PLUGIN_ATTR_REREAD_INITIAL,
    PLUGIN_ATTR_PROTOCOL,
    PLUGIN_ATTR_RECURSIVE,
    PLUGIN_PATH,
    PLUGIN_ATTR_CYCLE,
    CMD_IATTR_CYCLIC,
    ITEM_ATTR_CYCLIC,
    ITEM_ATTR_VALID_LIST,
    PROTO_RESEND,
    PROTO_JSONRPC,
    PLUGIN_ATTR_SEND_RETRIES,
    PLUGIN_ATTR_SEND_RETRY_CYCLE,
    PLUGIN_ATTR_CONN_TERMINATOR,
    PLUGIN_ATTRS,
    JSON_MOVE_KEYS,
)
from lib.smarthome import SmartHome
from lib.model.sdp.binding import CommandRef, CyclicSchedule, ItemBinding, ItemRole, ValidListBinding
from lib.model.sdp.carriers import ConnectionHooks, DeviceConfig
from lib.model.sdp.commands import SDPCommands
from lib.model.sdp.declarations import CustomTokenSpec, TransportRule
from lib.model.sdp.command import SDPCommand
from lib.model.sdp.connection import SDPConnection
from lib.model.sdp.protocol import SDPProtocol  # noqa


class SDPResultError(OSError):
    pass


#: key of the item binding in an item's plugin config data (SmartPlugin.add_item())
BINDING_KEY = 'sdp'

#: marks a plugin parameter not (yet) set by plugin code
_NOT_SET = object()


# noinspection PyUnresolvedReferences
class SmartDevicePlugin(SmartPlugin):
    """
    The class SmartDevicePlugin implements the base class of smart-plugins
    designed especially for device connectivity.

    It implements a fully functional plugin with all necessary methods to
    set up network or serial connections, handle item parsing and updating
    and converting data from shng to the device and vice versa.

    In the easiest cases, only the command specifications in ``commands.py``
    and possibly DT-* datatype classes are needed; additional command classes
    or plugin code can be added if necessary or desired.

    The ``suspend_item`` parameter uses the pause item slot of SmartPlugin;
    pausing suspends device communication instead of stopping the plugin.

    The implemented methods are described below, inherited methods are only
    described if changed/overwritten.
    """

    STANDALONE_HELP_OPTIONS = (
        ''  #: extra text describing this plugin's own standalone options, inserted after the generic arg=value help
    )
    STANDALONE_HELP_EXTRA = ''  #: free-form additional text, appended at the end of the standalone usage message

    #: rules selecting the transport, first match wins
    TRANSPORTS: ClassVar[tuple[TransportRule, ...]] = ()
    #: protocol type or class to wrap the transport in, None for none (or the protocol parameter)
    PROTOCOL: ClassVar[str | type[SDPProtocol] | None] = None
    #: command class or its name in lib.model.sdp.command, None for the command_class parameter or SDPCommand
    COMMAND_CLASS: ClassVar[str | type[SDPCommand] | None] = None
    #: line-based device: commands end with the terminator parameter, replies are read up to it
    LINE_TERMINATED: ClassVar[bool] = False
    #: keys moved from the JSON-RPC data dict root to its params (JSON-RPC protocol only)
    JSON_MOVE_KEYS: ClassVar[tuple[str, ...]] = ()
    #: custom commands addressing one of several devices by a custom attribute, None for none
    CUSTOM_TOKEN: ClassVar[CustomTokenSpec | None] = None

    #: classes already warned about _use_callbacks
    _warned_use_callbacks: ClassVar[set[type]] = set()

    def __init__(self, sh: SmartHome, logger=None, **kwargs):
        """
        Initalizes the plugin.
        """
        # adjust imported ITEM_ATTR_xxx identifiers
        self._set_item_attributes()

        # cycles and due times of cyclic reads
        self._cyclic = CyclicSchedule()

        # None for normal operations, 1..3 for combined custom commands
        self.custom_commands: int | None = None

        # for extraction of custom token from reply
        self._token_pattern = ''

        # for detection of custom tokens in reply_pattern
        self._custom_patterns = {1: '', 2: '', 3: ''}

        # TRANSPORTS select the transport
        self._select_transport = False

        #
        # set class properties
        #

        # suspend mode
        self.suspended = False

        # loop guard: suppress MQTT feedback loops on write failure
        self._loop_guard: dict = {}
        _lgc = self.get_parameter_value('loop_guard_count')
        self._loop_guard_count: float = float(_lgc) if _lgc is not None else 0
        _lgw = self.get_parameter_value('loop_guard_window')
        self._loop_guard_window: float = float(_lgw) if _lgw is not None else 5.0
        _lgs = self.get_parameter_value('loop_guard_source')
        self._loop_guard_source: str = str(_lgs) if _lgs is not None else ''

        # mark device-mirroring items invalid in the database log on connection loss (opt-in)
        self._invalidate_on_disconnect = bool(self.get_parameter_value('invalidate_on_disconnect'))
        self._suspended_by_connection = False
        self._has_connected = False

        # connection instance
        # self._connection: SDPConnection | None = None
        # commands instance
        # self._commands: SDPCommands | None = None
        self._command_class: type[SDPCommand] | None = None

        # by default, discard data not assignable to known command
        self._discard_unknown_command = True
        # if not discarding data, set this command instead
        self._unknown_command = '.notify.'
        self._initial_value_read_done = False
        self._cyclic_update_active = False
        self._cyclic_errors = 0
        self._reconnect_on_cycle_error = True
        # plugin-wide cycle interval, -1 is undefined
        self._cycle = self.get_parameter_value(PLUGIN_ATTR_CYCLE)
        if self._cycle is None:
            self._cycle = -1
        # delay initial read
        self._initial_value_read_delay = self.get_parameter_value(PLUGIN_ATTR_DELAY_INITIAL)
        # resend initial commands on resume
        self._resume_initial_read = self.get_parameter_value(PLUGIN_ATTR_REREAD_INITIAL)

        # set (overwritable) callback
        self._dispatch_callback = self.dispatch_data

        self._webif: SmartPluginWebIf | None = None

        self._shtime = Shtime.get_instance()

        # init parameters in standalone mode
        if SDP_standalone:  # noqa  # type: ignore  (set by plugin implementation on load via builtins module)
            self._parameters = kwargs

        #: values for {PARAM:...} and {CUSTOM_PARAMn:...} command templates; falls back to the plugin parameters
        self.template_vars: ChainMap[str, Any] = ChainMap({}, self._parameters)

        if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_CONN, None) is None:
            self._parameters[PLUGIN_ATTR_CONN_AUTO_CONN] = self._parameters.get(PLUGIN_ATTR_CONN_AUTO_RECONN, False)

        if hasattr(self, '_classpath'):
            self._parameters[PLUGIN_PATH] = getattr(self, '_classpath')
        else:
            self._plugin_dir = self._parameters[PLUGIN_PATH].replace('.', '/')

        # Call init code of parent class (SmartPlugin)
        super().__init__()

        # make sure we have a proper SmartHome reference
        self._sh = sh

        # suspend item is handled as SmartPlugin's pause item
        self._pause_item_path = self.get_parameter_value(PLUGIN_ATTR_SUSPEND_ITEM)

        # init device

        # parameters set by _set_device_defaults() override declared defaults
        configured_connection = self._parameters.get(PLUGIN_ATTR_CONNECTION)
        self._apply_declared_defaults()
        if self.TRANSPORTS:
            # detects a connection set by _set_device_defaults(), even if equal to the configured one
            self._parameters[PLUGIN_ATTR_CONNECTION] = _NOT_SET
        declared = dict(self._parameters)
        self._set_device_defaults()
        self._check_legacy_defaults(declared, configured_connection)

        # save modified value for ing to SDPCommands
        self._parameters['custom_patterns'] = self._custom_patterns

        # set/update plugin configuration
        if not self.update_plugin_config(**kwargs):
            self._init_complete = False

        # call method for possible custom work (overwrite _post_init)
        self._post_init()

        # self._webif might be set by smartplugin init
        if self._webif and self._sh:
            self.init_webinterface(self._webif)

        self.logger.debug(f'device initialized from {self.__class__.__name__}')

    def update_plugin_config(self, **kwargs) -> bool:
        """
        update plugin configuration parameters and (re)run relevant
        configuration methods
        """
        if self.alive:
            return False

        self._parameters.update(kwargs)

        if self._select_transport:
            transport = self._transport_from_rules()
            if transport is None:
                self.logger.error(
                    f'none of {[r.requires for r in self.TRANSPORTS if r.requires]} is configured, plugin disabled'
                )
                return False
            self._parameters[PLUGIN_ATTR_CONNECTION] = transport

        # this is only viable for the base class. All derived plugin classes
        # will probably be created towards a specific command class
        # but, just in case, be well-behaved...
        self._command_class = self._parameters.get(PLUGIN_ATTR_CMD_CLASS, SDPCommand)

        # try to read configuration files
        try:
            if not self._read_configuration():
                self.logger.error('configuration could not be read, plugin disabled')
                return False
        except Exception as e:
            self.logger.error(f'configuration could not be read, plugin disabled. Original error was: {e}')
            return False

        # instantiate connection object
        try:
            self._connection = self._get_connection(name=self.get_fullname())
        except RuntimeError as e:
            self.logger.error(f'could not set up connection, plugin disabled: {e}')
            return False
        if not self._connection:
            self.logger.error(f'could not setup connection with {self._parameters}, plugin disabled')
            return False

        # try to import struct(s)
        if self._sh:
            self._import_structs()

        return True

    def _apply_declared_defaults(self) -> None:
        """Apply the device defaults declared as class attributes."""
        if self.TRANSPORTS:
            self._select_transport = True
        if self.PROTOCOL is not None:
            self._parameters[PLUGIN_ATTR_PROTOCOL] = self.PROTOCOL
        if self.COMMAND_CLASS is not None:
            self._parameters[PLUGIN_ATTR_CMD_CLASS] = self.COMMAND_CLASS
        if self.JSON_MOVE_KEYS:
            self._parameters[JSON_MOVE_KEYS] = list(self.JSON_MOVE_KEYS)
        if self.LINE_TERMINATED:
            terminator = self._parameters.get(PLUGIN_ATTR_CONN_TERMINATOR) or ''
            if isinstance(terminator, str):
                # plugin.yaml may hold the terminator escaped, e.g. '\\r'
                terminator = terminator.encode().decode('unicode-escape').encode()
            self._parameters[PLUGIN_ATTR_CONN_TERMINATOR] = terminator
        if self.CUSTOM_TOKEN is not None:
            spec = self.CUSTOM_TOKEN
            self.custom_commands = spec.index
            self._token_pattern = spec.token_re
            self._custom_patterns[spec.index] = spec.reply_re
            if spec.recursive:
                self._parameters[PLUGIN_ATTR_RECURSIVE] = spec.index

    def _check_legacy_defaults(self, declared: dict, configured_connection: Any) -> None:
        """
        Log framework parameters set by _set_device_defaults(), warn about _use_callbacks.

        :param declared: plugin parameters after applying the declared defaults
        :param configured_connection: configured conn_type parameter
        """
        changed = [key for key in (*PLUGIN_ATTRS, JSON_MOVE_KEYS) if self._parameters.get(key) is not declared.get(key)]
        if changed:
            self.logger.debug(
                f'_set_device_defaults() sets {changed}; consider declaring these as class attributes (TRANSPORTS etc.)'
            )

        if '_use_callbacks' in vars(self) and type(self) not in self._warned_use_callbacks:
            self._warned_use_callbacks.add(type(self))
            self.logger.warning(
                f'{type(self).__name__} sets _use_callbacks, which is obsolete: connection callbacks are always used'
            )

        if not self.TRANSPORTS:
            return
        if self._parameters.get(PLUGIN_ATTR_CONNECTION) is not _NOT_SET:
            self._select_transport = False
            return
        self._parameters[PLUGIN_ATTR_CONNECTION] = configured_connection
        if configured_connection:
            self.logger.warning(
                f'conn_type {configured_connection} is ignored, {type(self).__name__} selects its connection itself'
            )

    def _transport_from_rules(self) -> Any:
        """Transport of the first matching TRANSPORTS rule, None if no rule matches."""
        matching = [rule for rule in self.TRANSPORTS if rule.matches(self._parameters)]
        configured = [rule.requires for rule in matching if rule.requires]
        if len(configured) > 1:
            self.logger.warning(
                f'{" and ".join(configured)} are configured, using {matching[0].use} for {configured[0]}; remove the other(s)'
            )
        return matching[0].use if matching else None

    def suspend(self, by: str | None = None):
        """
        sets plugin into suspended mode, no network/serial activity and no item changed
        """
        if self.alive:
            self.logger.info(f'plugin suspended by {by if by else "unknown"}, connections will be closed')
            self.suspended = True
            if self._pause_item is not None:
                self._pause_item(True, self.get_fullname())
            self.disconnect()
            self.scheduler_remove_all()

            # call user-defined suspend actions
            self.on_suspend()

    def resume(self, by: str | None = None):
        """
        disabled suspended mode, network/serial connections are resumed
        """
        if self.alive:
            self.logger.info(f'plugin resumed by {by if by else "unknown"}, connections will be resumed')
            self.suspended = False
            self._suspended_by_connection = False
            if self._pause_item is not None:
                self._pause_item(False, self.get_fullname())
            self.connect()

            # call user-defined resume actions
            self.on_resume()

    def on_pause_item_change(self, paused: bool) -> None:
        """Suspend or resume device communication."""
        self.set_suspend(paused, by=f'suspend item {self._pause_item_path}')

    def on_suspend(self):
        """called when suspend is enabled. Overwrite as needed"""
        pass

    def on_resume(self):
        """called when suspend is disabled. Overwrite as needed"""
        pass

    def _on_connection_aborted(self, suspend_active: bool | None = None, by: str | None = None):
        """
        Connection callback for exhausted connect attempts: invalidate items, then suspend.

        Unlike a manual suspend, the connection loss is real, so the items are marked
        invalid here and the suspend-induced disconnect is not treated as manual.
        """
        if suspend_active:
            self._suspended_by_connection = True
            self._invalidate_items(by)
        self.set_suspend(suspend_active, by)

    def set_suspend(self, suspend_active: bool | None = None, by: str | None = None):
        """
        enable / disable suspend mode: open/close connections, schedulers
        """
        if suspend_active is None:
            if self._pause_item is not None:
                # if no parameter set, try to use item setting
                suspend_active = bool(self._pause_item())
            else:
                # if not available, default to "resume" (non-breaking default)
                suspend_active = False

        # print debug logging
        if suspend_active:
            msg = 'Suspend mode enabled'
        else:
            msg = 'Suspend mode disabled'
        if by:
            msg += f' (set by {by})'
        self.logger.debug(msg)

        # activate selected mode, use smartplugin methods
        if suspend_active:
            self.suspend(by)
        else:
            self.resume(by)

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'run()'}))

        if self.alive:
            return

        # start the devices
        self.alive = True
        self.set_suspend(by='run()')

        if self._connection.connected():
            # make sure this is called once at startup, even if resume_initial is not set
            self.read_initial_values()

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'stop()'}))

        self.alive = False
        self.scheduler_remove_all()
        self.disconnect()

    def connect(self):
        """
        Open connection
        """
        self._connection.open()

    def disconnect(self):
        """
        Close connection
        """
        self._connection.close()

    # def run_standalone(self):
    #     """
    #     If you want to provide a standalone function, you'll have to implement
    #     this function with the appropriate code. You can use all functions
    #     from the SmartDevicePlugin class (plugin), the connections and
    #     commands.
    #     You do not have an sh object, items or web interfaces.
    #
    #     As the base class should not have this method, it is commented out.
    #     """
    #     pass

    def parse_item(self, item: Item) -> Callable | None:
        """
        Bind the item; the suspend item is registered as pause item.

        :param item: the item to parse
        :return: update_item if the item needs change notifications, else None
        """
        if item.property.path == self._pause_item_path:
            return super().parse_item(item)

        binding, updating = self._bind_item(item)
        if binding is None:
            return None

        self.add_item(item, {BINDING_KEY: binding}, mapping=binding.command)
        return self.update_item if updating else None

    def _bind_item(self, item: Item) -> tuple[ItemBinding | None, bool]:
        """
        Derive the item's binding from its configuration.

        :param item: the item to bind
        :return: binding (None if the item isn't configured for the plugin), and whether it needs update_item()
        """
        command_name = self._iattr(item, 'ITEM_ATTR_COMMAND')
        binding = ItemBinding(custom=self._custom_attrs(item, command_name))

        custom_token = None
        if self.custom_commands and self._commands.custom_is_enabled_for(command_name):
            custom_token = binding.custom[self.custom_commands] or None
        token_suffix = CUSTOM_SEP + custom_token if custom_token else ''

        read_initial = bool(self._iattr(item, 'ITEM_ATTR_READ_INIT'))

        if command_name:
            if not self.is_valid_command(command_name):
                self.logger.warning(f'Item {item} requests undefined command {command_name}, ignoring item')
                return None, False
            binding.command = command = CommandRef(command_name, custom_token)

            read = self._iattr(item, 'ITEM_ATTR_READ')
            write = self._iattr(item, 'ITEM_ATTR_WRITE')
            if read:
                if self.is_valid_command(command_name, COMMAND_READ):
                    binding.roles |= ItemRole.READ
                    binding.read_groups = self._item_read_groups(item, token_suffix)
                    binding.read_initial = read_initial
                    binding.cycle = self._item_cycle(item)
                    self.logger.debug(f'Item {item} saved for reading command {command}')
                else:
                    self.logger.warning(
                        f'Item {item} requests command {command} for reading, which is not allowed, read configuration is ignored'
                    )
            if write and self.is_valid_command(command_name, COMMAND_WRITE):
                binding.roles |= ItemRole.WRITE
                self.logger.debug(f'Item {item} saved for writing command {command}')
                return binding, True
            if not read and not write:
                self.logger.debug(f'Item {item} saved for receiving command {command}')

        group = self._iattr(item, 'ITEM_ATTR_READ_GRP')
        if group:
            binding.roles |= ItemRole.GROUP_TRIGGER
            binding.trigger_group = group + token_suffix
            binding.read_initial = read_initial
            binding.cycle = self._item_cycle(item)
            self.logger.debug(f'Item {item} saved for triggering read group {binding.trigger_group}')
            return binding, True

        if self._bind_lookup(item, binding):
            return binding, True

        if self._bind_valid_list(item, binding):
            return binding, True

        if not binding.roles and binding.command is None:
            return None, False
        return binding, False

    def _iattr(self, item: Item, attr: str) -> Any:
        """Value of the item attribute named by ``attr`` (an ATTR_NAMES entry)."""
        return self.get_iattr_value(item.conf, self._item_attrs.get(attr, ''))

    def _custom_attrs(self, item: Item, command: str | None) -> dict[int, str | None]:
        """Custom attribute values by index, inherited from ancestors for recursive indices."""
        custom: dict[int, str | None] = {1: None, 2: None, 3: None}
        for index in custom:
            attr = f'ITEM_ATTR_CUSTOM{index}'
            value = self._iattr(item, attr)
            if value is not None:
                self.logger.debug(f'Item {item} has custom item attribute {index} with value {value}')
            elif self.has_recursive_custom_attribute(index):
                parent = item.return_parent()
                # the top item's parent is sh.items, not an item
                while type(parent) is type(item) and value is None:
                    value = self._iattr(parent, attr)
                    parent = parent.return_parent()
                if value is not None:
                    self.logger.debug(f'Item {item} inherited custom item attribute {index} with value {value}')
            if value is not None:
                self.set_custom_item(item, command, index, value)
                custom[index] = value
        return custom

    def _item_read_groups(self, item: Item, token_suffix: str) -> tuple[str, ...]:
        """Read groups of the item, with custom token."""
        groups = self._iattr(item, 'ITEM_ATTR_GROUP')
        if not groups:
            return ()
        if isinstance(groups, str):
            groups = [groups]
        if not isinstance(groups, list):
            self.logger.warning(
                f'Item {item} wants to be read in group with invalid group identifier "{groups}", ignoring.'
            )
            return ()
        return tuple(group + token_suffix for group in groups if group)

    def _item_cycle(self, item: Item) -> float | None:
        """Shortest of the plugin-wide cycle (ITEM_ATTR_CYCLIC) and the item cycle (ITEM_ATTR_CYCLE)."""
        cycles = []
        if self._iattr(item, 'ITEM_ATTR_CYCLIC'):
            if self._cycle > 0:
                cycles.append(self._cycle)
            else:
                self.logger.info(
                    f'Item {item} wants global cyclic reading, but global cycle is {self._cycle}, ignoring.'
                )
        cycle = self._iattr(item, 'ITEM_ATTR_CYCLE')
        if cycle:
            cycles.append(cycle)
        return min(cycles) if cycles else None

    def _bind_lookup(self, item: Item, binding: ItemBinding) -> bool:
        """
        Bind a lookup item.

        :return: True for a forward lookup item, which updates the table
        """
        table = self._iattr(item, 'ITEM_ATTR_LOOKUP')
        if not table:
            return False
        mode = 'fwd'
        if '#' in table:
            table, mode = table.split('#')
        lookup = self.get_lookup(table, mode)
        if mode in ('fwd', 'rev', 'rci') and item.type() != 'dict':
            self.logger.warning(
                f'Item {item} requested lookup and should be of type dict, but is type {item.type()}. Ignoring.'
            )
        elif mode == 'list' and item.type() != 'list':
            self.logger.warning(
                f'Item {item} requested list lookup and should be of type list, but is type {item.type()}. Ignoring.'
            )
        elif lookup:
            item.set(lookup, self.get_fullname(), source='Init')
            self.logger.debug(f'Item {item} assigned lookup {table} with contents {lookup}')
            binding.roles |= ItemRole.LOOKUP
            binding.lookup = (table, mode)
            return mode == 'fwd'
        else:
            self.logger.info(f'Item {item} requested lookup {table}, which was empty or non-existent')
        return False

    def _bind_valid_list(self, item: Item, binding: ItemBinding) -> bool:
        """
        Bind a valid_list item.

        :return: True if the item was bound
        """
        command = self._iattr(item, 'ITEM_ATTR_VALID_LIST')
        if not command:
            return False
        if item.type() != 'list':
            self.logger.warning(
                f'Item {item} requested valid_list for command {command}, should be of type list but is type {item.type()}. Ignoring.'
            )
            return False
        if not self._commands.is_valid_command(command):
            self.logger.info(
                f'Item {item} requested valid_list for command {command}, but command not found. Ignoring.'
            )
            return False
        if CMD_ATTR_CMD_SETTINGS in self._commands.get_commandlist(command):
            vlist, ci, is_re = self._commands.get_valid_list(command)
            if vlist:
                binding.roles |= ItemRole.VALID_LIST
                binding.valid_list = ValidListBinding(command, ci, is_re)
                kind = 'valid_list_ci' if ci else 'valid_list_re' if is_re else 'valid_list'
                self.logger.debug(f'Item {item} assigned {kind} for command {command} with contents {vlist}')
                item(vlist, self.get_fullname(), source='Init')
                return True
        self.logger.info(
            f'Item {item} requested valid_list for command {command}, but no valid_list present, ignoring.'
        )
        return False

    def _binding(self, item: Item) -> ItemBinding | None:
        """The item's binding, None if it has none."""
        entry = self._plg_item_dict.get(item.property.path)
        return entry['config_data'].get(BINDING_KEY) if entry else None

    def _bound_items(self) -> Iterator[tuple[Item, ItemBinding]]:
        """Items with a binding and their binding, in registration order."""
        for entry in list(self._plg_item_dict.values()):
            binding = entry['config_data'].get(BINDING_KEY)
            if binding:
                yield entry['item'], binding

    def _receiving_items(self, command: str) -> list[Item]:
        """Items bound to ``command``; each receives its values, whether bound for reading, writing or neither."""
        return [item for item in self.get_items_for_mapping(command) if self._binding(item)]

    def _read_commands(self, group: str = '') -> list[CommandRef]:
        """Commands of READ items, optionally only of ``group``, each once."""
        commands: dict[CommandRef, None] = {}
        for _, binding in self._bound_items():
            if binding.roles & ItemRole.READ and (not group or group in binding.read_groups):
                commands[binding.command] = None
        return list(commands)

    def _initial_commands(self) -> list[CommandRef]:
        """Commands to read on startup, each once."""
        return list(
            dict.fromkeys(b.command for _, b in self._bound_items() if b.roles & ItemRole.READ and b.read_initial)
        )

    def _initial_triggers(self) -> list[str]:
        """Read groups to trigger on startup, each once."""
        return list(
            dict.fromkeys(
                b.trigger_group for _, b in self._bound_items() if b.roles & ItemRole.GROUP_TRIGGER and b.read_initial
            )
        )

    def _lookup_items(self, table: str, mode: str) -> list[Item]:
        """Items holding lookup ``table`` in ``mode``."""
        return [item for item, binding in self._bound_items() if binding.lookup == (table, mode)]

    def _sync_cyclic(self) -> None:
        """Apply the configured cycles to the cyclic schedule."""
        commands: dict[str, float] = {}
        groups: dict[str, float] = {}
        for _, binding in self._bound_items():
            if binding.cycle is None:
                continue
            if binding.roles & ItemRole.READ:
                commands[binding.command] = min(binding.cycle, commands.get(binding.command, binding.cycle))
            if binding.roles & ItemRole.GROUP_TRIGGER:
                groups[binding.trigger_group] = min(binding.cycle, groups.get(binding.trigger_group, binding.cycle))
        self._cyclic.sync(commands, groups)

    def custom_tokens(self, index: int | None = None) -> list[str]:
        """Values of custom attribute ``index`` (default: the custom command index), each once."""
        index = index or self.custom_commands
        if not index:
            return []
        return list(dict.fromkeys(b.custom[index] for _, b in self._bound_items() if b.custom.get(index)))

    def update_lookup(self, table: str, data: dict) -> None:
        """Replace lookup ``table`` by ``data`` and update the items holding its other modes."""
        self._commands.update_lookup_table(table, data)
        for mode in ('rev', 'rci', 'list'):
            for lookup_item in self._lookup_items(table, mode):
                self.logger.debug(f'setting item {lookup_item} for lookup {table} and mode {mode}')
                lookup_item(self.get_lookup(table, mode), self.get_fullname())

    def update_item(self, item: Item, caller: str | None = None, source: str | None = None, dest: str | None = None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by
        SmartHomeNG. It should write the changed value out to the device
        (hardware/interface) that is managed by this plugin.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        if not self.alive:
            return

        self.logger.debug(
            f'Update_item was called with item "{item}" from caller {caller}, source {source} and dest {dest}'
        )

        if self._handle_pause_item(item, caller):
            return

        binding = self._binding(item)
        if binding is None:
            self.logger.warning(
                f"Update_item was called with item {item}, which is not configured for this plugin. This shouldn't happen..."
            )
            return

        # own changes are not sent to the device
        if caller == self.get_fullname():
            return

        self.logger.info(f'Update item: {item.property.path}: item has been changed outside this plugin')

        if binding.roles & ItemRole.WRITE:
            self._write_item(item, binding, caller)

        elif binding.roles & ItemRole.GROUP_TRIGGER:
            group = binding.trigger_group
            self.logger.debug(f'Triggering read_group {group}' if group != '0' else 'Triggering read_all')
            self.read_all_commands(group)

        elif binding.roles & ItemRole.LOOKUP:
            table = binding.lookup[0]
            if not isinstance(item(), dict):
                self.logger.debug(
                    f'update of lookup table {table} not possible, item value is {type(item())}, not dict'
                )
                return
            self.logger.debug(f'updating lookup {table}')
            self.update_lookup(table, item())

        elif binding.roles & ItemRole.VALID_LIST:
            vlist = binding.valid_list
            try:
                self.logger.debug(
                    f'trying to set valid_list (ci: {vlist.ci}, re: {vlist.re}) for command {vlist.command} to {item()}'
                )
                self._commands.set_valid_list(vlist.command, item(), vlist.ci, vlist.re)
            except RuntimeError as e:
                self.logger.warning(
                    f'error while updating valid_list for command {vlist.command} from item {item}: {e}'
                )

    def _write_item(self, item: Item, binding: ItemBinding, caller: str | None) -> None:
        """Send the item's value, reset the item on failure, schedule a read after write if configured."""
        command = binding.command
        if self._check_loop_guard(item.property.path, item(), caller):
            self.logger.warning(
                f'Loop guard triggered for item {item.property.path} (value={item()}, caller={caller}), suppressing write'
            )
            return

        self.logger.debug(f'Writing value "{item()}" from item {item.property.path} with command "{command}"')
        if not self.send_command(command, item(), custom=binding.custom):
            self.logger.debug(
                f'Writing value "{item()}" from item {item.property.path} with command "{command}" failed, resetting item value'
            )
            item(item.property.last_value, self.get_fullname())
            return

        readafterwrite = self._iattr(item, 'ITEM_ATTR_READAFTERWRITE')
        if readafterwrite is None:
            return
        try:
            readafterwrite = float(readafterwrite)
        except ValueError:
            self.logger.warning(
                f'Item {item} has readafterwrite set to {readafterwrite}, which is not parseable as (float) seconds. Ignoring.'
            )
            return
        if readafterwrite > 0:
            self.logger.debug(
                f'Attempting to schedule read after write for item {item}, command {command}, delay {readafterwrite}'
            )
            self.scheduler_add(
                f'{item}-readafterwrite',
                lambda: self.send_command(command),
                next=self.shtime.now() + datetime.timedelta(seconds=readafterwrite),
            )

    def _check_loop_guard(self, item_path: str, value, caller=None) -> bool:
        """
        Return True (and suppress the write) when the same value has been
        written to item_path more than _loop_guard_count times within
        _loop_guard_window seconds.

        If _loop_guard_source is set, only callers whose name starts with
        that prefix are subject to the guard; all others pass freely.
        caller=None always passes freely when a source filter is active.

        The guard unlocks automatically once all tracked timestamps have
        aged out of the time window.
        """
        if not self._loop_guard_count:
            return False

        if self._loop_guard_source:
            if not caller or not caller.startswith(self._loop_guard_source):
                return False

        now = time.time()
        entry = self._loop_guard.get(item_path)

        if entry is None or entry['value'] != value:
            self._loop_guard[item_path] = {'value': value, 'times': deque(), 'locked': False}
            entry = self._loop_guard[item_path]

        times = entry['times']
        cutoff = now - self._loop_guard_window
        while times and times[0] < cutoff:
            times.popleft()

        if entry['locked'] and not times:
            entry['locked'] = False
            return False

        times.append(now)

        if len(times) >= self._loop_guard_count:
            entry['locked'] = True

        return entry['locked']

    def _reset_loop_guard(self, item_path: str | None = None):
        """Clear loop guard state for item_path, or all items if None."""
        if item_path is not None:
            self._loop_guard.pop(item_path, None)
        else:
            self._loop_guard.clear()

    def _build_resend_info(self, command: str, value: Any, custom_value, kwargs: dict, captures_value) -> dict:
        """
        Build the resend_info dict consumed by SDPProtocolResend.
        Handles reply_pattern resolution, custom-token substitution, lookup
        table attachment, and per-command send_retries override.
        """
        reply_pattern = self._commands.get_commandlist(command).get(CMD_ATTR_REPLY_PATTERN)
        if custom_value and reply_pattern:
            for index in (1, 2, 3):
                custom_replacement = kwargs['custom'].get(index)
                if custom_replacement is not None:
                    pattern = '{' + PATTERN_CUSTOM_PATTERN + str(index) + '}'
                    if isinstance(reply_pattern, list):
                        reply_pattern = [r.replace(pattern, custom_replacement) for r in reply_pattern]
                        if len(reply_pattern) == 1:
                            reply_pattern = reply_pattern[0]
                    else:
                        reply_pattern = reply_pattern.replace(pattern, custom_replacement)

        read_cmd = self._transform_send_data(self._commands.get_send_data(command, None, **kwargs), **kwargs)
        resend_command = command if custom_value is None else f'{command}#{custom_value}'
        lookup_ci = self._commands.get_lookup(self._commands._get_cmd_lookup(command), 'rci')
        lookup = self._commands.get_lookup(self._commands._get_cmd_lookup(command))

        if reply_pattern is None or value is None:
            resend_info = {
                'command': resend_command,
                'returnvalue': None,
                'read_cmd': read_cmd,
                'lookup': lookup,
                'lookup_ci': lookup_ci,
            }
        elif not isinstance(reply_pattern, list) and not captures_value(reply_pattern):
            resend_info = {
                'command': resend_command,
                'returnvalue': re.compile(reply_pattern),
                'read_cmd': read_cmd,
                'lookup': lookup,
                'lookup_ci': lookup_ci,
            }
        elif isinstance(reply_pattern, list):
            return_list = []
            for r in reply_pattern:
                checked_value = self._commands._commands[command]._check_value(value)
                if not captures_value(r):
                    return_list.append(re.compile(r))
                elif checked_value not in return_list:
                    return_list.append(checked_value)
            reply_pattern = None if None in return_list else return_list
            resend_info = {
                'command': resend_command,
                'returnvalue': reply_pattern,
                'read_cmd': read_cmd,
                'lookup': lookup,
                'lookup_ci': lookup_ci,
            }
        else:
            resend_info = {
                'command': resend_command,
                'returnvalue': value,
                'read_cmd': read_cmd,
                'lookup': lookup,
                'lookup_ci': lookup_ci,
            }

        send_retries = self._commands.get_commandlist(command).get(CMD_ATTR_SEND_RETRIES)
        try:
            send_retries = int(send_retries)
        except Exception:
            send_retries = None
        if send_retries is not None:
            resend_info.update({'send_retries': send_retries})

        return resend_info

    def send_command(
        self, command: str, value: Any = None, return_result: bool = False, raise_on_error: bool = False, **kwargs
    ):
        """
        Sends the specified command to the device providing <value> as data
        Not providing data will issue a read command, trying to read the value
        from the device and writing it to the associated item. Commands not
        declared readable in commands.py are not requested.

        :param command: the command to send
        :param value: the data to send, if applicable
        :param raise_on_error: re-raise the underlying error instead of returning False on failure
        :type command: str
        :type raise_on_error: bool
        :return: True if send was successful, False otherwise
        :rtype: bool
        """

        def captures_value(pattern):
            try:
                re.compile(pattern)
                # Check for non-empty unescaped parentheses indicating capture groups
                has_nonempty_parentheses = bool(re.search(r'(?<!\\)\((?!\?:)[^)]{1,}\)', pattern))
                # Check for non-empty unescaped curly braces, for lookups
                has_nonempty_braces = bool(re.search(r'(?<!\\)\{[^}]{1,}\}', pattern))
                return has_nonempty_parentheses or has_nonempty_braces
            except re.error:
                # Not a valid regex
                return False

        if not self.alive:
            msg = f'trying to send command {command} with value {value}, but plugin is not active.'
            self.logger.warning(msg)
            if raise_on_error:
                raise SDPError(msg)
            return False

        if value is None and not self._commands.is_valid_command(CommandRef.parse(command).name, COMMAND_READ):
            msg = f'command {command} is not readable, read request not sent'
            self.logger.debug(msg)
            if raise_on_error:
                raise SDPError(msg)
            return False

        if self.suspended:
            msg = f'trying to send command {command} with value {value}, but plugin is suspended.'
            self.logger.warning(msg)
            if raise_on_error:
                raise SDPError(msg)
            return False

        if not self._connection:
            msg = (
                f"trying to send command {command} with value {value}, but connection is None. This shouldn't happen..."
            )
            self.logger.warning(msg)
            if raise_on_error:
                raise SDPError(msg)
            return False

        custom_value = None
        if self._commands.custom_is_enabled_for(command) and self.custom_commands:
            try:
                command, custom_value = command.split(CUSTOM_SEP)
                custom = dict(kwargs.get('custom') or {1: None, 2: None, 3: None})
                custom[self.custom_commands] = custom_value
                kwargs['custom'] = custom
            except ValueError:
                self.logger.debug(f'extracting custom token failed, maybe not present in command {command}')

        if not self._connection.connected():
            if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_CONN):
                self.connect()

            if not self._connection.connected():
                msg = (
                    f'trying to send command {command} with value {value}, but connection could not be re-established.'
                )
                self.logger.warning(msg)
                if raise_on_error:
                    raise SDPError(msg)
                return False

        # enable doing something before sending data normally
        # passing kwargs as dict is no error, possible modification is intended
        continue_send, result = self._do_before_send(command, value, kwargs)
        if not continue_send:
            return result

        try:
            data_dict = self._commands.get_send_data(command, value, **kwargs)
        except Exception as e:
            self.logger.warning(
                f'command {command} with value {value} produced error on converting value, aborting. Error was: {e}'
            )
            if raise_on_error:
                raise
            return False

        if data_dict['payload'] is None or data_dict['payload'] == '':
            msg = f'command {command} with value {value} yielded empty command payload, aborting'
            self.logger.warning(msg)
            if raise_on_error:
                raise SDPError(msg)
            return False

        data_dict = self._transform_send_data(data_dict, **kwargs)
        self.logger.debug(f'command {command} with value {value} yielded send data_dict {data_dict}')

        # creating resend info, necessary for resend protocol
        result = None
        resend_info = self._build_resend_info(command, value, custom_value, kwargs, captures_value)
        # if an error occurs on sending, an exception is thrownn below
        try:
            result = self._send(data_dict, resend_info=resend_info)
        except (SDPError, RuntimeError) as e:
            self.logger.debug(f'error on sending command {command}: {e}')
            if raise_on_error:
                raise
            return False
        if result:
            by = kwargs.get('by')
            self.logger.debug(f'command {command} received result {result} by {by}')

            if return_result:
                value, _ = self._process_received_data(result, command)
                return value
            else:
                self.on_data_received(by, result, command)

        return True

    def on_data_received(self, by: str | None, data: Any, command: str | None = None):
        """
        Callback function for received data e.g. from an event loop
        Processes data and dispatches value to plugin class

        :param command: the command in reply to which data was received
        :param data: received data in 'raw' connection format
        :param by: client object / name / identifier
        :type command: str
        """
        data = self._transform_received_data(data)
        commands = None

        if command is not None:
            self.logger.debug(f'received data "{data}" from {by} for command {command}')
            commands = [command]
        else:
            # command == None means that we got raw data from a callback and
            # don't know yet to which command this belongs to. So find out...
            self.logger.debug(f'received data "{data}" from {by} without command specification')

            # command can be a string (classic single command) or
            # - new - a list of strings if multiple commands are identified
            # in that case, work on all strings
            commands = self._commands.get_commands_from_reply(data)
            if not commands:
                if self._discard_unknown_command:
                    self.logger.debug(f'data "{data}" did not identify a known command, ignoring it')
                else:
                    if not self.suspended:
                        self.logger.debug(
                            f'data "{data}" did not identify a known command, forwarding it anyway for {self._unknown_command}'
                        )
                        self._dispatch_callback(self._unknown_command, data, by)
                    else:
                        self.logger.info(
                            f'received data "{data}" not identifying a known command while suspended, aborting.'
                        )
                return

        if self.suspended:
            self.logger.info(f'received data "{data}" from {by} for command {command} while suspended, ignoring.')
            return

        # process all commands
        for cmd in commands:
            try:
                value, custom = self._process_received_data(data, cmd)
            except SDPResultError:
                pass
            else:
                if custom and self._commands.custom_is_enabled_for(cmd):
                    cmd = cmd + CUSTOM_SEP + custom
                self._connection.check_reply(cmd, value)  # needed for resend protocol
                self._dispatch_callback(cmd, value, by)
                self._process_additional_data(cmd, data, value, custom, by)

    def _process_received_data(self, data: Any, command: str) -> Tuple[Any, Any]:
        """convert received data and handle custom token"""

        custom = None
        if self._commands.custom_is_enabled_for(command) and self.custom_commands:
            custom = self._get_custom_value(command, data)

        value = None
        try:
            value = self._commands.get_shng_data(command, data)

            if custom:
                command = command + CUSTOM_SEP + custom
        except (ValueError, OSError) as e:  # Exception as e:
            self.logger.info(
                f'received data "{data}" for command {command}, error {e} occurred while converting. Discarding data.'
            )
            raise SDPResultError
        else:
            self.logger.debug(f'received data "{data}" for command {command} converted to value {value}')
            return value, custom

    def dispatch_data(self, command: str, value: Any, by: str | None = None):
        """
        Callback function - new data has been received from device.
        Value is already in item-compatible format, so find appropriate item
        and update value

        :param command: command for or in reply to which data was received
        :param value: data
        :param by: str
        :type command: str
        """
        if not self.alive or self.suspended:
            return

        items = self._receiving_items(command)
        if not items:
            self.logger.info(
                f'Command {command} yielded value {value} by {by}, not assigned to any item, discarding data'
            )
            return

        for item in items:
            self.logger.debug(
                f'Command {command} wants to update item {item.property.path} with value {value} received from {by}'
            )
            item(value, self.get_fullname())

    def read_all_commands(self, group: str = ''):
        """
        Triggers all configured read commands or all configured commands of given group; group '0' is all commands
        """
        for command in self._read_commands('' if group == '0' else group):
            self.send_command(command)

    def is_valid_command(self, command: str, read: bool | None = None) -> bool | None:
        """
        Validate if 'command' is a valid command for this device
        Possible to check only for reading or writing

        :param command: the command to test
        :type command: str
        :param read: check for read (True) or write (False), or both (None)
        :type read: bool | NoneType
        :return: True if command is valid, False otherwise
        :rtype: bool
        """
        if self._commands.custom_is_enabled_for(command) and self.custom_commands:
            ref = CommandRef.parse(command)
            if ref.token is not None:
                tokens = self.custom_tokens()
                if ref.token not in tokens:
                    self.logger.debug(f'custom value {ref.token} not in known custom values {tokens}')
                    return
                command = ref.name

        if self._commands:
            return self._commands.is_valid_command(command, read)
        else:
            return False

    def get_lookup(self, lookup: str, mode: str = 'fwd') -> dict | list | None:
        """returns the lookup table for name <lookup>, None on error"""
        if self._commands:
            return self._commands.get_lookup(lookup, mode)
        else:
            return

    def has_recursive_custom_attribute(self, index: int = 1) -> bool:
        rec = self._parameters.get(PLUGIN_ATTR_RECURSIVE, [])
        if isinstance(rec, list):
            return index in rec
        else:
            return rec == index

    def set_custom_item(self, item: Item, command: str, index: int, value: Any):
        """Called by parse_item() for each custom attribute value found. Overwrite as needed."""
        pass

    #
    #
    # check if overwriting needed
    #
    #

    def _set_device_defaults(self):
        """Set device defaults in code; overrides the class attribute declarations. Overwrite as needed."""
        pass

    def _post_init(self):
        """do something after default initializing is done. Overwrite it"""
        pass

    def _transform_send_data(self, data_dict: dict, **kwargs) -> dict:
        """
        This method provides a way to adjust, modify or transform all data before
        it is sent to the device.
        This might be to add general parameters, include custom attributes,
        add/change line endings or add your favourite pet's name...
        For LINE_TERMINATED plugins, the terminator is appended and replies are read up to it.
        """
        if self.LINE_TERMINATED and isinstance(data_dict, dict):
            terminator = self._parameters[PLUGIN_ATTR_CONN_TERMINATOR]
            data_dict['limit_response'] = terminator
            data_dict['payload'] = f'{data_dict.get("payload", "")}{terminator.decode()}'
        return data_dict

    def _transform_received_data(self, data: Any) -> Any:
        """
        This method provides a way to adjust, modify or transform all data as soon
        as it is received from the device.
        This might be useful to clean or parse data.
        By default, nothing happens here.
        """
        return data

    def _do_before_send(self, command: str, value: Any, kwargs) -> Tuple[bool, bool]:
        """
        This method provides a way to act before send_command actually sends
        anything, e.g. checking for "special commands" which are internal
        trigger signals or something like this.

        You need to return two boolen values: continue_send and result
        If continue_send is True, send_command will behave normally and continue
        sending the specified command.
        If continue_send is False, send_command will abort and return <result>
        """
        return (True, True)

    def _send(self, data_dict: dict, **kwargs) -> Any:
        """
        This method acts as a overwritable intermediate between the handling
        logic of send_command() and the connection layer.
        If you need any special arrangements for or reaction to events on sending,
        you can implement this method in your plugin class.

        By default, this just forwards the data_dict to the connection instance
        and return the result.
        """
        self.logger.debug(f'sending {data_dict}, kwargs {kwargs}')
        return self._connection.send(data_dict, **kwargs)

    def on_connect(self, by: str | None = None):
        """callback if connection is made."""
        self._has_connected = True
        # neither of these are meaningful in standalone mode: there's no
        # shng scheduler (self._sh is None) to schedule either through, and
        # standalone diagnostic flows (e.g. run_standalone()) do their own
        # direct reads rather than relying on the general initial/cyclic
        # read machinery
        if self._connection.connected() and not SDP_standalone:  # noqa  # type: ignore
            if not self._initial_value_read_done or self._resume_initial_read:
                # read on first connect or on every reconnect if configured
                self._initial_value_read_done = False
                # Always schedule — on_connect may fire inside open() which holds _send_lock,
                # so any synchronous send path would deadlock. 1s minimum gives us a safe margin.
                if not self.scheduler_get('read_initial_values'):
                    delay = self._initial_value_read_delay if self._initial_value_read_delay else 1
                    self.scheduler_add(
                        'read_initial_values',
                        self._read_initial_values,
                        next=self.shtime.now() + datetime.timedelta(seconds=delay),
                    )
            self._create_cyclic_scheduler()

    def on_disconnect(self, by: str | None = None):
        """callback if connection is broken."""
        if not SDP_standalone and self.alive:  # noqa  # type: ignore
            if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_RECONN, False) and not self._connection.self_reconnects():
                reconnect_name = f'{self.get_fullname()}_reconnect'
                if not self.scheduler_get(reconnect_name):
                    self.logger.info('connection lost, scheduling reconnect in 5s')
                    self.scheduler_add(
                        reconnect_name, self.connect, next=self.shtime.now() + datetime.timedelta(seconds=5)
                    )
            if not self.suspended or self._suspended_by_connection:
                self._invalidate_items(by)

    def should_invalidate_item(self, item: Item, by: str | None = None) -> bool:
        """
        Whether ``item`` is marked invalid when the connection is lost. Overwrite to filter.

        By default these are the items that receive device data, i.e. those mapped to a
        readable or pseudo command. Write-only items and the suspend item hold values
        set by shng, not device state.

        :param item: item of this plugin that has ``db_mark_invalid``
        :param by: origin of the connection loss as reported by the connection
        """
        binding = self._binding(item)
        if binding is None or binding.command is None:
            return False
        return ItemRole.READ in binding.roles or ItemRole.WRITE not in binding.roles

    def _invalidate_items(self, by: str | None = None):
        """
        Mark this plugin's items invalid in the database log, if enabled by ``invalidate_on_disconnect``.

        Items without ``db_mark_invalid`` (not logged by the database plugin) are skipped.
        The item values stay unchanged; only the database log records a gap.
        """
        # before the first connect nothing was received, so there is nothing to invalidate
        if not self._invalidate_on_disconnect or not self._has_connected:
            return
        self.db_invalidate_items(
            self.get_item_list(), 'connection_lost', accept=lambda item: self.should_invalidate_item(item, by)
        )

    def _process_additional_data(self, command: str, data: Any, value: Any, custom: int, by: str | None = None):
        """do additional processing of received data

        Here you can do additional data examinating, filtering and possibly
        triggering additional commands or setting additional items.
        Overwrite as needed.
        """
        pass

    #
    #
    # utility methods
    #
    #

    def _get_custom_value(self, command: str, data: Any) -> str | None:
        """
        extract custom value from data
        At least PATTERN needs to be overwritten
        """
        if not self.custom_commands or not self._commands.custom_is_enabled_for(command):
            return
        if not isinstance(data, str):
            return
        res = re.search(self._token_pattern, data)
        if not res:
            self.logger.debug(f'custom token not found in {data}, ignoring')
            return
        tokens = self.custom_tokens()
        if res[0] in tokens:
            return res[0]
        self.logger.debug(f'received custom token {res[0]}, not in list of known tokens {tokens}')
        return

    def _get_connection(
        self,
        conn_type: str | None = None,
        conn_classname: str | None = None,
        conn_cls: type[SDPConnection] | None = None,
        proto_type: str | None = None,
        proto_classname: str | None = None,
        proto_cls: type[SDPProtocol] | None = None,
        name: str | None = None,
    ) -> SDPConnection:
        """
        return connection object.

        Try to identify the wanted connection and return the proper subclass
        instead. Without host or serial port, this is the base class
        SDPConnection, which is - externally - nonfunctional, but can stand as
        a debugging and diagnosis tool.

        If the PLUGIN_ATTR_PROTOCOL parameter is set, we need to change
        something. In this case, the protocol instance takes the place of the
        connection object and instantiates the connection object itself. Instead
        of the name of the connection class, we pass the class itself, so
        instantiating it poses no further challenge.

        If you need to use other connection types for your device, implement it
        and preselect with PLUGIN_ATTR_CONNECTION in /etc/plugin.yaml, so this
        class will never be used.

        :raises RuntimeError: if the configured connection or protocol is unknown
        """
        params = self._connection_params()
        conn_cls = SDPConnection._get_connection_class(conn_cls, conn_classname, conn_type, **params)
        params[PLUGIN_ATTR_CONNECTION] = conn_cls
        config = DeviceConfig.from_params(params)
        hooks = self._connection_hooks()

        if PLUGIN_ATTR_PROTOCOL in params:
            proto_cls = SDPProtocol._get_protocol_class(proto_cls, proto_classname, proto_type, **params)
            self.logger.debug(f'using protocol class {proto_cls}')
            return proto_cls(config, hooks, self, name)

        self.logger.debug(f'using connection class {conn_cls}')
        return conn_cls(config, hooks, self, name)

    def _connection_params(self) -> dict[str, Any]:
        """Plugin parameters for the connection, with the resend protocol selected if send_retries is set."""
        params = dict(self._parameters)
        resend = self.get_parameter_value(PLUGIN_ATTR_SEND_RETRIES)
        if not resend:
            return params

        for attr in (PLUGIN_ATTR_SEND_RETRIES, PLUGIN_ATTR_SEND_RETRY_CYCLE, PLUGIN_ATTR_SEND_TIMEOUT):
            val = self.get_parameter_value(attr)
            if val is not None:
                params[attr] = val

        protocol = params.get(PLUGIN_ATTR_PROTOCOL)
        if not protocol:
            params[PLUGIN_ATTR_PROTOCOL] = PROTO_RESEND
        elif protocol not in (PROTO_JSONRPC, PROTO_RESEND):
            self.logger.debug(
                f'{PLUGIN_ATTR_SEND_RETRIES} is set to {resend}, but protocol {protocol} is requested, so resend may not apply'
            )
        return params

    def _connection_hooks(self) -> ConnectionHooks:
        """Callbacks of the plugin for its connection."""
        return ConnectionHooks(
            on_data=self.on_data_received,
            on_connect=self.on_connect,
            on_disconnect=self.on_disconnect,
            on_abort=partial(self._on_connection_aborted, True),
        )

    def _create_cyclic_scheduler(self):
        """
        Setup the scheduler to handle cyclic read commands and find the proper
        time for the cycle.
        """
        if not self.alive:
            return

        self._sync_cyclic()
        shortestcycle = self._cyclic.shortest_cycle()
        if shortestcycle is None:
            return

        # Balance unnecessary calls and precision
        workercycle = int(shortestcycle / 2)

        # just in case it already exists...
        if self.scheduler_get(self.get_fullname() + '_cyclic'):
            self.scheduler_remove(self.get_fullname() + '_cyclic')
        self.scheduler_add(
            self.get_fullname() + '_cyclic', self._read_cyclic_values, cycle=workercycle, prio=5, offset=0
        )
        self._cyclic_errors = 0
        self.logger.info(
            f'Added cyclic worker thread {self.get_fullname()}_cyclic with {workercycle} s cycle. Shortest item update cycle found was {shortestcycle} s'
        )

    def read_initial_values(self):
        """control call of _read_initial_values - run instantly or delay"""
        if self.scheduler_get('read_initial_values'):
            return
        elif self._initial_value_read_delay:
            self.logger.dbghigh(f'Delaying reading initial values for {self._initial_value_read_delay} seconds.')
            self.scheduler_add(
                'read_initial_values',
                self._read_initial_values,
                next=self.shtime.now() + datetime.timedelta(seconds=self._initial_value_read_delay),
            )
        else:
            self._read_initial_values()

    def _read_initial_values(self):
        """
        Read all values configured to be read/triggered at startup
        """
        if self._initial_value_read_done:
            self.logger.debug('_read_initial_values() called, but inital values were already read. Ignoring')
        else:
            initial_commands = self._initial_commands()
            if initial_commands:
                self.logger.info('Starting initial read commands')
                for cmd in initial_commands:
                    self.logger.debug(f'Sending initial command {cmd}')
                    self.send_command(cmd)
                self.logger.info('Initial read commands sent')
            initial_triggers = self._initial_triggers()
            if initial_triggers:
                self.logger.info('Starting initial read group triggers')
                for grp in initial_triggers:
                    self.logger.debug(f'Triggering initial read group {grp}')
                    self.read_all_commands(grp)
                self.logger.info('Initial read group triggers sent')
            self._initial_value_read_done = True

    def _read_cyclic_values(self):
        """
        Recall function for cyclic scheduler.
        Reads all values configured to be read cyclically.
        """
        # check if another cyclic cmd run is still active
        if self._cyclic_update_active:
            self._cyclic_errors += 1
            if self._cyclic_errors >= 3 and self._reconnect_on_cycle_error:
                self.logger.warning(
                    f'Cyclic command read failed {self._cyclic_errors} times due to long previous cycle. Reconnecting... '
                )
                self.disconnect()
                self._cyclic_update_active = False

                # reconnect after 1 s without blocking the scheduler thread
                if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_RECONN, False):
                    reconnect_name = f'{self.get_fullname()}_reconnect'
                    if not self.scheduler_get(reconnect_name):
                        self.scheduler_add(
                            reconnect_name, self.connect, next=self.shtime.now() + datetime.timedelta(seconds=1)
                        )
            else:
                self.logger.warning(
                    'Triggered cyclic command read, but previous cyclic run is still active. Check device and cyclic configuration (too much/too short?)'
                )
            return
        else:
            self.logger.info('Triggering cyclic command read')
            self._cyclic_errors = 0

        # set lock
        self._cyclic_update_active = True
        try:
            self._sync_cyclic()
            currenttime = time.time()
            read_cmds = 0
            for cmd in self._cyclic.due_commands(currenttime):
                # repeatedly check if shng wants to stop to prevent stalling shng
                if not self.alive:
                    self.logger.info('Stop command issued, cancelling cyclic read')
                    return

                # also leave early on disconnect
                if not self._connection.connected():
                    self.logger.info('Disconnect detected, cancelling cyclic read')
                    return

                self.logger.debug(f'Triggering cyclic read of command {cmd}')
                self.send_command(cmd)
                self._cyclic.mark_command_read(cmd, currenttime)
                read_cmds += 1

            if read_cmds:
                self.logger.debug(
                    f'Cyclic command read took {(time.time() - currenttime):.1f} seconds for {read_cmds} items'
                )

            currenttime = time.time()
            read_grps = 0
            for grp in self._cyclic.due_groups(currenttime):
                # repeatedly check if shng wants to stop to prevent stalling shng
                if not self.alive:
                    self.logger.info('Stop command issued, cancelling cyclic trigger')
                    return

                # also leave early on disconnect
                if not self._connection.connected():
                    self.logger.info('Disconnect detected, cancelling cyclic trigger')
                    return

                self.logger.debug(f'Triggering cyclic read of group {grp}')
                self.read_all_commands(grp)
                self._cyclic.mark_group_triggered(grp, currenttime)
                read_grps += 1

            if read_grps:
                self.logger.debug(
                    f'Cyclic triggers took {(time.time() - currenttime):.1f} seconds for {read_grps} groups'
                )
        finally:
            self._cyclic_update_active = False

    def _read_configuration(self):
        """
        This initiates reading of configuration.
        Basically, this calls the SDPCommands object to fill itselt
        if needed, this can be overwritten to do something else.
        """
        cls = None
        if isinstance(self._command_class, type):
            cls = self._command_class
        elif isinstance(self._command_class, str):
            cmd_module = sys.modules.get('lib.model.sdp.command', '')
            if not cmd_module:
                self.logger.error('unable to get object handle of SDPCommand module')
                return

            cls = getattr(cmd_module, self._command_class, None)

        if cls is None:
            cls = SDPCommand
        self._commands = SDPCommands(cls, template_vars=self.template_vars, **self._parameters)
        return True

    def _import_structs(self):
        """check if additional MODEL struct is needed and insert it"""

        # check for and load struct definitions
        if not SDP_standalone:  # noqa  # type: ignore
            shstructs = self._sh.items.return_struct_definitions(False)  # type: ignore (if we don't have items in shng, we're really fubar)
            model = self._parameters.get('model', '')
            m_name = self.get_fullname() + '.' + model
            a_name = self.get_fullname() + '.' + INDEX_GENERIC
            m_struct = None

            if model and m_name in shstructs:
                m_struct = shstructs[m_name]
            elif a_name in shstructs:
                m_struct = shstructs[a_name]

            if m_struct:
                self.logger.debug(f'adding struct {self.get_fullname()}.{INDEX_MODEL}')
                self._sh.items.add_struct_definition(self.get_fullname(), INDEX_MODEL, m_struct)  # type: ignore (see above)

    def _set_item_attributes(self):
        """
        reads all item attributes defined in sdp.globals, tries to find the
        actual item attribute (as imported from plugin.yaml) and stores the
        actual item attribute in class member dict _item_attrs.

        This way, only the prefixes in plugin.yaml need to be adjusted for new
        plugin classes, and the symbolic names can be used without additional
        mangling.
        """

        plugins = Plugins.get_instance()
        globals_mod = sys.modules.get('lib.model.sdp.globals', '')

        self._item_attrs = {}

        if plugins and globals_mod:
            keys = list(self.metadata.itemdefinitions.keys())  # type: ignore (metadata member is dynamically inserted by lib.plugins on plugin load)
            for attr in ATTR_NAMES:
                attr_val = getattr(globals_mod, attr)
                for key in keys:
                    if key.endswith(attr_val):
                        self._item_attrs[attr] = key
                        break


################################################################################
#
#
# Standalone functions
#
#
################################################################################


class Standalone:
    HELP_USAGE = """
        Usage:
        ------------------------------------------------------------------------

        This plugin is meant to be used inside SmartHomeNG.

        Is is generally possible to run this plugin in standalone mode, usually
        for diagnostic purposes - IF the plugin supports this mode.

        ========================================================================
        """
    HELP_DEVICE = """
        If you call this plugin, any necessary configuration options can be
        specified either as arg=value pairs or as a python dict(this needs to be
        enclosed in quotes).
        Be aware that later parameters, be they dict or pair type, overwrite
        earlier parameters of the same name.

        ``__init__.py host=www.smarthomeng.de port=80``

        or

        ``__init__.py '{'host': 'www.smarthomeng.de', 'port': 80}'``

        If you set -v as a parameter, you get additional debug information:

        ``__init__.py -v``

        """
    HELP_STRUCT = """
        ========================================================================

        If you call this plugin with -s as a parameter, the plugin will insert
        the struct into the plugins' `plugins/<plugin_name>/plugin.yaml` file.
        Old struct content will be overwritten:

        ``__init__.py -s``

        If you add the -a parameter, all items will have an added

        ``visu_acl: <ro>/<rw>``

        attribute depending on the read/write configuration.

        If you add the -l parameter, all items will be lowercase.

        """

    def __init__(self, plugin_class, plugin_file):

        self.plugin_class = plugin_class

        self.item_tree = {}
        self.item_templates = {}
        self.yaml = None
        self.cmdlist = []

        self.struct_mode = False
        self.acl = False
        self.lc = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(message)s  @ %(lineno)d')
        ch.setFormatter(formatter)

        # attach the handler to the ROOT logger, not just this one -
        # SDPConnection and friends create their own, differently-named
        # loggers in standalone mode (e.g. logging.getLogger('__main__') -
        # see lib/model/sdp/connection.py), which would otherwise never
        # reach a handler at all and be silently discarded. A logger with
        # no explicit level of its own (the default for any of those)
        # inherits its effective level from the nearest ancestor that has
        # one set - setting it on root here makes -v/'critical only' apply
        # to them too, not just to this specific logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)
        root_logger.addHandler(ch)

        # make sure we are in shng base dir - needed below to locate
        # plugin.yaml, for both the help text and actually running the
        # plugin, so this has to happen before either
        if not (Path('bin') / 'smarthome.py').exists():
            print('Plugin needs to be called from SmartHomeNG base directory. Aborting.')
            return

        # make sure plugin_file resolves inside the current directory tree
        # - relpath() is always cwd-relative regardless of whether
        # plugin_file itself was absolute, so a leading '..' is the only
        # way this can mean "outside of here"
        rel_file = Path(os.path.relpath(plugin_file))
        if rel_file.is_absolute() or rel_file.parts[0] == '..':
            print(f'Plugin needs to be called with relative path; called as {plugin_file}. Aborting.')
            return

        # calculate files, paths and modules - from rel_file, not the raw
        # (possibly absolute) plugin_file argument
        self.plugin_path = rel_file.parent
        self.plugin_mod_path = '.'.join(self.plugin_path.parts)
        self.plugin_name = self.plugin_path.name

        # no shng instance exists in standalone mode - Metadata tolerates
        # sh=None (falls back to cwd, which the base-dir check above just
        # verified, and skips the http-module-only global parameter)
        self.meta = Metadata(None, self.plugin_name, 'plugin', str(self.plugin_path))

        self.usage = '<Error: Help text not set>'
        self.set_usage()

        if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ['-h', '--help', '-?', '/?', '/h', '/help']):
            flags, raw_args = self._parse_argv(sys.argv[1:])

            if flags['v']:
                print('Debug logging enabled')
                self.logger.setLevel(logging.DEBUG)
                root_logger.setLevel(logging.DEBUG)

            self.struct_mode = flags['s']
            self.acl = flags['a']
            self.lc = flags['l']

        else:
            print(self.usage)
            return

        if self.struct_mode:
            # struct export doesn't connect to a device, so the usual
            # mandatory-parameter/type checking below doesn't apply here
            self.params = raw_args
            self.params[PLUGIN_PATH] = self.plugin_mod_path
            self.create_struct_yaml()
            return

        # resolve declared defaults, type-convert, and check that every
        # mandatory parameter (with no default) was actually supplied -
        # instead of finding out however many calls deep into the plugin
        # once it tries to use a parameter that was never set
        self.params, allparams_ok, _ = self.meta.check_parameters(raw_args, source='the command line')
        if not allparams_ok:
            print('Missing required parameter(s) - see -h for available options and defaults.')
            return
        self.params[PLUGIN_PATH] = self.plugin_mod_path

        s = f'This is the {self.plugin_name} plugin running in standalone mode'
        print(s)
        print('=' * len(s))

        pl = plugin_class(None, logger=self.logger, **self.params)

        if getattr(pl, 'run_standalone', ''):
            print('running standalone method...')

            pl.run_standalone()
        else:
            print("plugin doesn't have a standalone function.")

        print('Done.')

    @staticmethod
    def _parse_argv(argv: list) -> Tuple[dict, dict]:
        """
        Parses standalone-mode CLI tokens (``sys.argv[1:]``) into mode
        flags and raw plugin-parameter args.

        Flags must match exactly (case-insensitive), not by prefix - a
        param arg starting with '-s'/'-a'/'-l' (e.g. ``-serial=...``) must
        not be misread as a mode flag.

        Every other token is parsed as a python dict literal (quoted as a
        single shell arg) or, failing that, a 'name=value' pair; a
        leading '--' is stripped first as a friendlier alias for either.

        :param argv: command line arguments, excluding argv[0]
        :return: (flags, raw_args); flags has keys 'v'/'s'/'a'/'l' -> bool
        """
        flags = {'v': False, 's': False, 'a': False, 'l': False}
        raw_args = {}
        for arg_str in argv:
            lowered = arg_str.lower()
            if lowered in ('-v', '-s', '-a', '-l'):
                flags[lowered[1]] = True
                continue

            if arg_str.startswith('--'):
                # '--key=val' is just 'key=val' with a friendlier,
                # more familiar-looking CLI flag prefix
                arg_str = arg_str[2:]
            try:
                # convertible to dict?
                raw_args.update(literal_eval(arg_str))
            except Exception:
                # if not: try to parse as 'name=value'
                match = re.match('([^= \n]+)=([^= \n]+)', arg_str)
                if match:
                    name, value = match.groups(0)
                    raw_args[name] = value

        return flags, raw_args

    def set_usage(self):
        options = getattr(self.plugin_class, 'STANDALONE_HELP_OPTIONS', '')
        extra = getattr(self.plugin_class, 'STANDALONE_HELP_EXTRA', '')
        parameters = self._format_parameters()
        self.usage = self.HELP_USAGE + self.HELP_DEVICE + options + parameters + self.HELP_STRUCT + extra

    def _format_parameters(self) -> str:
        """
        Formats this plugin's declared parameters (name, type, default or
        mandatory-flag, description) from plugin.yaml, for inclusion in the
        standalone usage text.

        Indentation matches HELP_USAGE/HELP_DEVICE/HELP_STRUCT (8 spaces),
        since this is spliced in between them in set_usage() rather than
        printed standalone. No separator line before the listing - it reads
        as a continuation of the general option help above it, not a new
        section (HELP_STRUCT's own topic change still gets one).
        """
        if not self.meta or not self.meta.parameters:
            return ''

        indent = ' ' * 8
        desc_indent = indent + '      '
        lines = [f'{indent}Available parameters (from plugin.yaml):', '']

        for name in self.meta._paramlist:
            definition = self.meta.parameters.get(name) or {}
            ptype = definition.get('type') or '?'
            description = definition.get('description', '')
            if isinstance(description, dict):
                if 'en' in description:
                    description = description['en']
                elif description:
                    # no English translation provided - fall back to
                    # whatever's there, but say so instead of silently
                    # mixing languages across the parameter list
                    lang, text = next(iter(description.items()))
                    description = f'{text} [{lang}]'
                else:
                    description = ''

            if definition.get('mandatory'):
                info = f'{ptype}, mandatory'
            else:
                default = self.meta.get_parameter_defaultvalue(name)
                info = f'{ptype}, default: {default}'

            lines.append(f'{indent}  {name:<24} ({info})')
            if description:
                lines.extend(
                    textwrap.wrap(description, width=76, initial_indent=desc_indent, subsequent_indent=desc_indent)
                )

        return '\n' + '\n'.join(lines) + '\n'

    def add_item_to_tree(self, item_path, item_dict):
        """add entry for custom read group triggers"""

        if self.lc:
            # make lowercase items
            dst_path_elems = item_path.lower().split('.')
            # ensure that the ALL branch stays in caps
            if item_path == 'ALL' or item_path[0:4] == 'ALL.':
                dst_path_elems[0] = 'ALL'
        else:
            # make items with original commands case
            dst_path_elems = item_path.split('.')
        item = {dst_path_elems[-1]: item_dict}
        for elem in reversed(dst_path_elems[:-1]):
            item = {elem: item}

        update(self.item_tree, item)

    #: opaque per-command data, not further command-tree levels - must
    #: not be descended into (a dict-valued custom attribute would else
    #: be mistaken for a command-tree level of its own)
    CMD_STRUCTURAL_SKIP_KEYS = (CMD_ATTR_CMD_SETTINGS, CMD_ATTR_PARAMS, CMD_ATTR_ITEM_ATTRS)

    def walk_commands(self, node, node_name, parent, func, path, gpathlist, cut_levels=0):
        """pre-order traversal of a (model/section-scoped) commands dict,
        calling func(node, node_name, parent, path, gpathlist, cut_levels)
        for every node before recursing into its structural child dicts.
        Does not descend into CMD_STRUCTURAL_SKIP_KEYS children.

        :param node: starting node
        :param node_name: name of the starting node on parent level ('key')
        :param parent: parent node
        :param func: function to call for each node
        :param path: dotted command path of the current node
        :param gpathlist: list of all read groups above the current node
        :param cut_levels: cut <n> levels from front of path
        """
        if func:
            func(node, node_name, parent, path, gpathlist, cut_levels)

        for child in (k for k in node.keys() if isinstance(node[k], dict) and k not in self.CMD_STRUCTURAL_SKIP_KEYS):
            new_path = (path + COMMAND_SEP if path else '') + child
            self.walk_commands(
                node[child], child, node, func, new_path, gpathlist + ([path] if path else []), cut_levels
            )

    def prune(self, node, node_name, parent, path, predicate):
        """post-order traversal that deletes node from parent whenever
        predicate(node, path) is True, after first recursing into all of
        node's dict-valued children.

        :param node: starting node
        :param node_name: name of the starting node on parent level ('key')
        :param parent: parent node, from which node_name may be deleted
        :param path: dotted command path of the current node
        :param predicate: called as predicate(node, path) -> bool
        """
        for child in list(k for k in node.keys() if isinstance(node[k], dict)):
            new_path = (path + COMMAND_SEP if path else '') + child
            self.prune(node[child], child, node, new_path, predicate)

        if predicate(node, path):
            del parent[node_name]

    def _is_undefined_for_model(self, node, path):
        return CMD_ATTR_ITEM_TYPE in node and path not in self.cmdlist

    @staticmethod
    def _is_empty_dict(node, path):
        return len(node) == 0

    def find_read_group_triggers(self, node, node_name, parent, path, gpathlist, cut_levels):
        """find custom read trigger definitions, create trigger item

        for params see walk_commands() above, they are the same there

        To keep things manageable, we only support relative addressing in the
        most simple form:

        ...path.to.item

        Every leading dot means 'up one level', so without a leading dot, the
        item will be created 'inside' the item with the 'read_groups' directive.
        """
        if CMD_ATTR_ITEM_ATTRS in node:
            # set sub-node for readability
            rg_list = node[CMD_ATTR_ITEM_ATTRS].get(CMD_IATTR_READ_GROUPS)
            if rg_list:
                if not isinstance(rg_list, list):
                    rg_list = [rg_list]
                for entry in rg_list:
                    itempath = entry.get('trigger')
                    if not itempath:
                        print(
                            f"Warning: read_groups entry for '{path}' is missing "
                            f"required 'trigger' key, skipping: {entry}"
                        )
                        continue

                    # resolve relative item position
                    lvl_up = 0
                    while itempath[:1] == '.':
                        lvl_up += 1
                        itempath = itempath[1:]

                    if lvl_up:
                        src_path_elems = path.split(COMMAND_SEP)[:-lvl_up]
                    else:
                        src_path_elems = path.split(COMMAND_SEP)
                    item_path = '.'.join(['.'.join(src_path_elems), itempath])

                    self.add_item_to_tree(
                        item_path,
                        {
                            'type': 'bool',
                            'enforce_updates': 'true',
                            self._item_attrs.get('ITEM_ATTR_READ_GRP', ITEM_ATTR_READ_GRP): entry.get('name'),
                        },
                    )

    def create_item(self, node, node_name, parent, path, gpathlist, cut_levels=0):
        """create item or read item for current node/command

        for params see walk_commands() above, they are the same there.
        Only ever called for real command-tree nodes - walk_commands()
        already filters out CMD_STRUCTURAL_SKIP_KEYS - so no need to
        re-check for those here.
        """
        if not node_name:
            return

        # item name = item path is in path
        # item contents goes in item
        item = {}

        if CMD_ATTR_ITEM_TYPE in node or 'type' not in node:
            # item -> print item attributes
            if CMD_ATTR_ITEM_TYPE in node:
                item['type'] = node.get(CMD_ATTR_ITEM_TYPE, 'foo')
                cmd = path if path else node_name
                if cut_levels:
                    cmd = COMMAND_SEP.join(cmd.split(COMMAND_SEP)[cut_levels:])
                # add '@instance' to enable multi-instance usage
                item[self._item_attrs.get('ITEM_ATTR_COMMAND', ITEM_ATTR_COMMAND) + '@instance'] = cmd
                item[self._item_attrs.get('ITEM_ATTR_READ', ITEM_ATTR_READ) + '@instance'] = node.get(
                    CMD_ATTR_READ, True
                )
                item[self._item_attrs.get('ITEM_ATTR_WRITE', ITEM_ATTR_WRITE) + '@instance'] = node.get(
                    CMD_ATTR_WRITE, False
                )
                if self.acl:
                    item['visu_acl'] = 'rw' if node.get(CMD_ATTR_WRITE, False) else 'ro'

                # set sub-node for readability
                ia_node = node.get(CMD_ATTR_ITEM_ATTRS)

                rg_level = None
                rg_list = None
                if ia_node:
                    rg_level = ia_node.get(CMD_IATTR_RG_LEVELS, None)
                    rg_list = ia_node.get(CMD_IATTR_READ_GROUPS)

                # rg_level = None: print all read groups (default)
                # rg_level = 0: don't print read groups
                # rg_level > 0: print last <x> levels of read groups
                #               (plus custom read groups)

                # only set read_groups if item 'can' trigger read.
                # no logging because standalone mode and syntax output active
                grps = gpathlist
                if rg_level != 0 and (node.get(CMD_ATTR_OPCODE) or node.get(CMD_ATTR_READ_CMD)):
                    if rg_level is not None:
                        grps = grps[-rg_level:]
                    if rg_list:
                        if not isinstance(rg_list, list):
                            rg_list = [rg_list]
                        for entry in rg_list:
                            grps.append(entry.get('name'))
                    # only create read_groups if they actually exist
                    if grps:
                        item[self._item_attrs.get('ITEM_ATTR_GROUP', ITEM_ATTR_GROUP) + '@instance'] = grps

                # item attributes
                if ia_node:
                    if ia_node.get(CMD_IATTR_ENFORCE):
                        item['enforce_updates'] = True
                    if ia_node.get(CMD_IATTR_INITIAL):
                        item[self._item_attrs.get('ITEM_ATTR_READ_INIT', ITEM_ATTR_READ_INIT) + '@instance'] = True
                    if ia_node.get(CMD_IATTR_CYCLIC):
                        item[self._item_attrs.get('ITEM_ATTR_CYCLIC', ITEM_ATTR_CYCLIC) + '@instance'] = True
                    cycle = ia_node.get(CMD_IATTR_CYCLE)
                    if cycle:
                        item[self._item_attrs.get('ITEM_ATTR_CYCLE', ITEM_ATTR_CYCLE) + '@instance'] = cycle
                    custom = ia_node.get(CMD_IATTR_CUSTOM1)
                    if custom is not None:
                        item[self._item_attrs.get('ITEM_ATTR_CUSTOM1', ITEM_ATTR_CUSTOM1) + '@instance'] = custom
                    custom = ia_node.get(CMD_IATTR_CUSTOM2)
                    if custom is not None:
                        item[self._item_attrs.get('ITEM_ATTR_CUSTOM2', ITEM_ATTR_CUSTOM2) + '@instance'] = custom
                    custom = ia_node.get(CMD_IATTR_CUSTOM3)
                    if custom is not None:
                        item[self._item_attrs.get('ITEM_ATTR_CUSTOM3', ITEM_ATTR_CUSTOM3) + '@instance'] = custom

                    # custom item attributes: add 1:1
                    attrs = ia_node.get(CMD_IATTR_ATTRIBUTES)
                    if attrs:
                        update(item, attrs)

                    # custom item templates: add 1:!
                    templates = ia_node.get(CMD_IATTR_TEMPLATE)
                    if templates:
                        if not isinstance(templates, list):
                            templates = [templates]
                        for tmpl in templates:
                            if tmpl in self.item_templates:
                                update(item, self.item_templates[tmpl])

                    # if item has 'xx_lookup' and item_attrs['lookup_item'] is
                    # set, create additional item with lookup values
                    lu_item = ia_node.get(CMD_IATTR_LOOKUP_ITEM)
                    if lu_item and node.get(CMD_ATTR_LOOKUP):
                        ltyp = ia_node.get(CMD_IATTR_LOOKUP_ITEM)
                        if ltyp is True:
                            ltyp = 'list'
                        item['lookup'] = {'type': 'list' if ltyp == 'list' else 'dict'}
                        item['lookup'][self._item_attrs.get('ITEM_ATTR_LOOKUP', ITEM_ATTR_LOOKUP) + '@instance'] = (
                            f'{node.get(CMD_ATTR_LOOKUP)}#{ltyp}'
                        )

            # 'level node' -> print read item
            else:
                item['read'] = {'type': 'bool', 'enforce_updates': True}
                item['read'][self._item_attrs.get('ITEM_ATTR_READ_GRP', ITEM_ATTR_READ_GRP) + '@instance'] = (
                    path if path else node_name
                )
                try:
                    # set sub-node for readability
                    ia_node = node.get(CMD_ATTR_ITEM_ATTRS)
                    if ia_node.get(CMD_IATTR_INITIAL):
                        item['read'][self._item_attrs.get('ITEM_ATTR_READ_INIT', ITEM_ATTR_READ_INIT) + '@instance'] = (
                            True
                        )
                    if ia_node.get(CMD_IATTR_CYCLE):
                        item['read'][self._item_attrs.get('ITEM_ATTR_CYCLE', ITEM_ATTR_CYCLE) + '@instance'] = (
                            ia_node.get(CMD_IATTR_CYCLE)
                        )
                except AttributeError:
                    pass

            if item:
                self.add_item_to_tree(path, item)

            if CMD_ATTR_ITEM_ATTRS in node:
                self.find_read_group_triggers(node, node_name, parent, path, gpathlist, cut_levels)

    def update_item_attributes(self):
        """
        Resolves this plugin's actual (possibly prefixed) item attribute
        names from plugin.yaml's 'item_attributes' section into
        self._item_attrs, e.g. {'ITEM_ATTR_COMMAND': 'viess_command'}.

        Same mechanism as SmartDevicePlugin._set_item_attributes() (this
        module's runtime counterpart), just sourced from the plugin.yaml
        file directly since no live Metadata/itemdefinitions exist in
        standalone mode.
        """
        global_mod = sys.modules.get('lib.model.sdp.globals', '')
        file = self.plugin_path / 'plugin.yaml'
        yaml = shyaml.yaml_load(file)
        keys = list((yaml.get('item_attributes') or {}).keys())

        self._item_attrs = {}
        if keys and global_mod:
            for attr in ATTR_NAMES:
                attr_val = getattr(global_mod, attr)
                for key in keys:
                    if key.endswith(attr_val):
                        self._item_attrs[attr] = key
                        break

    def create_struct_yaml(self):
        """read commands.py and export struct.yaml"""

        def isnumstr(val):
            return all(c in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.') for c in val)

        def is_block_safe(data):
            """
            True if shyaml.yaml_save() writes ``data`` as a literal block that reads back unchanged

            yaml_save() halves every doubled line break and puts a blank line before each line ending in ':'
            unless a list entry follows. Blocks therefore hold the text with doubled line breaks (see
            str_presenter()), and cannot hold carriage returns, a leading or doubled trailing line break, or
            a line ending in ':' that no list entry follows.
            """
            if '\r' in data or data.startswith('\n') or data.strip('\n') == '' or data.endswith('\n\n'):
                return False
            lines = data[:-1].split('\n') if data.endswith('\n') else data.split('\n')
            following = lines[1:] + ['']
            return not any(
                line.endswith(':') and not nxt.strip().startswith('-') for line, nxt in zip(lines, following)
            )

        def str_presenter(dumper, data):
            """configures yaml for dumping multiline strings and version number strings"""

            # quote strings like '1.2' or '1.2.3' to make is more apparent that this is not a number
            if isnumstr(data):
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

            if '\n' in data:
                if not is_block_safe(data):
                    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
                text, end = (data[:-1], '\n') if data.endswith('\n') else (data, '')
                return dumper.represent_scalar('tag:yaml.org,2002:str', text.replace('\n', '\n\n') + end, style='|')

            # default
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        self.update_item_attributes()

        mod_str = self.plugin_mod_path + '.commands'
        try:
            cmd_module = importlib.import_module(mod_str, __name__)
        except Exception as e:
            raise ImportError(f'error on importing commands, aborting. Error was {e}')

        commands = cmd_module.commands
        top_level_entries = list(commands.keys())

        self.item_templates = getattr(cmd_module, 'item_templates', {})

        # load plugin's plugin.yaml
        file = self.plugin_path / 'plugin.yaml'
        try:
            plugin_yaml_text = file.read_text(encoding='utf8')
        except OSError as e:
            print(f'Error: file {file} could not be opened. Original error: {e}')
            return
        # not shyaml.yaml_load(): it doubles every line break, which changes multiline values
        self.yaml, error = shyaml.yaml_load_fromstring(plugin_yaml_text, ordered=True)
        if self.yaml is None:
            print(f'Error: file {file} could not be parsed. Original error: {error}')
            return

        self.yaml['item_structs'] = OrderedDict()

        # this means the commands dict has 'ALL' and model names at the top level
        # otherwise, the top level nodes are commands or sections
        cmds_has_models = INDEX_GENERIC in top_level_entries

        if cmds_has_models:
            for model in top_level_entries:
                # create model-specific commands dict
                m_commands = deepcopy(commands.get(INDEX_GENERIC))
                update(m_commands, deepcopy(commands.get(model)))

                # create work obj for entry
                obj = {model: m_commands}

                self.item_tree = {}

                # create item tree
                self.walk_commands(obj[model], '', None, self.create_item, '', [model])

                # easiest way to move dict to OrderedDict
                jdata = json.dumps(self.item_tree)
                self.yaml['item_structs'][model] = json.loads(jdata, object_pairs_hook=OrderedDict)

        else:
            # create flat commands, 'valid command' needs full cmd path
            flat_commands = deepcopy(commands)
            SDPCommands._flatten_cmds(flat_commands)

            # output sections separately and unchanged
            for section in top_level_entries:
                self.item_tree = {}

                obj = {section: commands[section]}

                # create item tree
                self.walk_commands(obj[section], section, None, self.create_item, section, [])

                # easiest way to move dict to OrderedDict
                jdata = json.dumps(self.item_tree)
                self.yaml['item_structs'][section] = json.loads(jdata, object_pairs_hook=OrderedDict)[section]

            # get model definitions
            # if not present, fake it to include all sections
            models = getattr(cmd_module, 'models', [])
            if not models:
                models = {'ALL': list(commands.keys())}

            for model in models:
                self.item_tree = {}

                # copy - models[model] is the commands.py module's own
                # list; += below would otherwise mutate it in place
                self.cmdlist = list(models[model])
                # add generic commands to every other model
                if model != INDEX_GENERIC:
                    self.cmdlist += models.get(INDEX_GENERIC, [])
                self.cmdlist = SDPCommands._get_cmdlist(flat_commands, self.cmdlist)

                # create new obj for model m, include m['ALL']
                # as we modify obj, we need to copy this
                obj = {model: deepcopy(commands)}

                # remove all items with model-invalid 'xx_command'
                self.prune(obj[model], model, obj, '', self._is_undefined_for_model)

                # remove all empty items from obj
                self.prune(obj[model], model, obj, '', self._is_empty_dict)

                # create item tree
                self.walk_commands(obj[model], model, obj, self.create_item, model, [], cut_levels=1)

                jdata = json.dumps(self.item_tree)
                self.yaml['item_structs'][model] = json.loads(jdata, object_pairs_hook=OrderedDict)[model]

        # insert yaml string formatters into ruamel module before final export
        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)

        shyaml.yaml_save(file, self.yaml)
        print(f'Updated file {file}')
