#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms           Morg @ knx-user-forum
#  Copyright 2017-      Martin Sinn                       m.sinn@gmx.de
#  Copyright 2016       Christian Strassburg      c.strassburg(a)gmx.de
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

import logging
import importlib
import re
import os
import sys
import time
import json
from copy import deepcopy
from ast import literal_eval
from collections import OrderedDict

from lib.model.smartplugin import SmartPlugin

import lib.shyaml as shyaml
from lib.module import Modules
from lib.plugin import Plugins

from lib.model.sdp.globals import (
    update, ATTR_NAMES, CMD_ATTR_CMD_SETTINGS, CMD_ATTR_ITEM_ATTRS,
    CMD_ATTR_ITEM_TYPE, CMD_ATTR_LOOKUP, CMD_ATTR_OPCODE, CMD_ATTR_PARAMS,
    CMD_ATTR_READ, CMD_ATTR_READ_CMD, CMD_ATTR_WRITE, CMD_IATTR_ATTRIBUTES,
    CMD_IATTR_CYCLE, CMD_IATTR_ENFORCE, CMD_IATTR_INITIAL,
    CMD_IATTR_LOOKUP_ITEM, CMD_IATTR_READ_GROUPS, CMD_IATTR_RG_LEVELS,
    CMD_IATTR_CUSTOM1, CMD_IATTR_CUSTOM2, CMD_IATTR_CUSTOM3,
    CMD_IATTR_TEMPLATE, COMMAND_READ, COMMAND_SEP, COMMAND_WRITE, CUSTOM_SEP,
    INDEX_GENERIC, INDEX_MODEL, ITEM_ATTR_COMMAND, ITEM_ATTR_CUSTOM1,
    ITEM_ATTR_CYCLE, ITEM_ATTR_GROUP, ITEM_ATTR_LOOKUP, ITEM_ATTR_READ,
    ITEM_ATTR_READ_GRP, ITEM_ATTR_READ_INIT, ITEM_ATTR_WRITE,
    PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_ON_DISCONNECT,
    PLUGIN_ATTR_CMD_CLASS, PLUGIN_ATTR_CONNECTION,
    PLUGIN_ATTR_CONN_AUTO_RECONN, PLUGIN_ATTR_CONN_AUTO_CONN,
    PLUGIN_ATTR_PROTOCOL, PLUGIN_ATTR_RECURSIVE, PLUGIN_PATH)
from lib.model.sdp.commands import SDPCommands
from lib.model.sdp.command import SDPCommand
from lib.model.sdp.connection import SDPConnection
from lib.model.sdp.protocol import SDPProtocol  # noqa


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

    The implemented methods are described below, inherited methods are only
    described if changed/overwritten.
    """

    # this is the placeholder version of the derived plugin, not of SDP
    PLUGIN_VERSION = '0.0.1'

    def __init__(self, sh, logger=None, **kwargs):
        """
        Initalizes the plugin.
        """

        # adjust imported ITEM_ATTR_xxx identifiers
        self._set_item_attributes()

        # set item properties

# TODO: include self._item_dict from new SmartPlugin
#       as far as I can see at the moment, we do not
#       use a dict/list of "associated items", only
#       compiled lists of "special" items which need
#       to exist in addition for quicker lookup and
#       not needing to iterate over item_dict every
#       time, e.g. self._items_write:
#
# self._items_write = {i.key(): i['device_command'] for i in self._item_dict where i['config_data']['write']}
#       
#       so for now, I don't see much reduction potential here
#       nevertheless, check all (!) the code for ways to reduce overhead
#       and revert to directly using self._item_dict...

        # contains all items with write command
        # <item_id>: <command>
        self._items_write = {}
        # contains items which trigger 'read all'
        # <item_id>
        self._items_read_all = []
        # contains items which trigger 'read group foo'
        # <item_id>: <foo>
        self._items_read_grp = {}
# replace with self._item_lookup_dict?
        # contains all commands with read command
        # <command>: [<item_object>, <item_object>...]
        self._commands_read = {}
        # contains all pseudo commands (without command sequence)
        # <command>: [<item_object>, <item_object>...]
        self._commands_pseudo = {}
        # contains all commands with read group command
        # <group>: [<command>, <command>...]
        self._commands_read_grp = {}
        # contains all commands to be read after run() is called
        # 'command'
        self._commands_initial = []
        # contains all commands to be read cyclically
        # <command>: {'cycle': <cycle>, 'next': <next>}
        self._commands_cyclic = {}
        # contains all read groups to be triggered after run() is called
        # 'grp'
        self._triggers_initial = []
        # contains all read groups per device to be triggered cyclically
        # <grp>: {'cycle': <cycle>, 'next': <next>}
        self._triggers_cyclic = {}
        # contains item xx_custom<x> attributes
        # <item_id>: {1: custom1, 2: custom2, 3:custom3}
        self._items_custom = {}

        # None for normal operations, 1..3 for combined custom commands
        self.custom_commands = None

        # for extraction of custom token from reply
        self._token_pattern = ''

        # for detection of custom tokens in reply_pattern
        self._custom_patterns = {1: '', 2: '', 3: ''}

        # set to True to use on_connect and on_disconnect callbacks
        self._use_callbacks = False

        # set class properties

        # connection instance
        self._connection = None
        # commands instance
        self._commands = None
        # keep custom123 values
        self._custom_values = {1: [], 2: [], 3: []}

        # by default, discard data not assignable to known command
        self._discard_unknown_command = True
        # if not discarding data, set this command instead
        self._unknown_command = '.notify.'
        self._initial_value_read_done = False
        self._cyclic_update_active = False

        # set (overwritable) callback
        self._dispatch_callback = self.dispatch_data

        self._webif = None

        # init parameters in standalone mode
        if SDP_standalone:
            self._parameters = kwargs

        if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_CONN, None) is None:
            self._parameters[PLUGIN_ATTR_CONN_AUTO_CONN] = self._parameters.get(PLUGIN_ATTR_CONN_AUTO_RECONN, False)

        if hasattr(self, '_classpath'):
            self._parameters[PLUGIN_PATH] = self._classpath
        else:
            self._plugin_dir = self._parameters[PLUGIN_PATH].replace('.', '/')

        # Call init code of parent class (SmartPlugin)
        super().__init__()

        # init device

        # possibly initialize additional (overwrite _set_device_defaults)
        self._set_device_defaults()

        # save modified value for passing to SDPCommands
        self._parameters['custom_patterns'] = self._custom_patterns

        # set/update plugin configuration
        if not self.update_plugin_config(**kwargs):
            self._init_complete = False

        # call method for possible custom work (overwrite _post_init)
        self._post_init()

        if self._webif and self._sh:
            self.init_webinterface(self._webif)

        self.logger.debug(f'device initialized from {self.__class__.__name__}')

    def deinit(self, items=[]):
        """
        If the plugin needs special code to be executed before it is unloaded,
        this method has to be overwritten for de-initialization
        """
        if self.alive:
            self.stop()

        # if standalone, only stop (we have no items)
        if not self._sh:     
            return

        # remove items from internal lists
        if not items:
            items = self.get_items()
        elif not isinstance(items, list):
            items = [items]

        for item in items:
            try:
                del self._items_write[item]
            except Exception:
                pass
            try:
                del self._items_read_grp[item.path()]
                del self._items_custom[item.path()]
            except Exception:
                pass
            try:
                self._items_read_all.remove(item.path())
            except Exception:
                pass
            cmd = self._item_dict[item]['device_command']
            if cmd:
                try:
                    self._commands_read[cmd].remove(item)
                    self._commands_pseudo[cmd].remove(item)
                except Exception:
                    pass
                try:
                    self._commands_initial.remove(cmd)
                except Exception:
                    pass
                try:
                    del self._commands_cyclic[cmd]
                except Exception:
                    pass

                for grp in self._commands_read_grp:
                    try:
                        self._commands_read_grp[grp].remove(cmd)
                    except Exception:
                        pass

    def update_plugin_config(self, **kwargs):
        """
        update plugin configuration parameters and (re)run relevant
        configuration methods
        """
        if self.alive:
            return False

        self._parameters.update(kwargs)

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
        self._connection = self._get_connection(name=self.get_fullname())
        if not self._connection:
            self.logger.error(f'could not setup connection with {self._parameters}, plugin disabled')
            return False

        # try to import struct(s)
        if self._sh:
            self._import_structs()

        return True

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.debug('Run method called')

        if self.alive:
            return

        # start the devices
        self.alive = True

        self._connection.open()

        if self._connection.connected():
            self._read_initial_values()
            if not SDP_standalone:
                self._create_cyclic_scheduler()

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug('Stop method called')
        self.alive = False

        if self.scheduler_get(self.get_shortname() + '_cyclic'):
            self.scheduler_remove(self.get_shortname() + '_cyclic')
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

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is
        initialized. The plugin can, corresponding to its attribute keywords,
        decide what to do with the item in future, like adding it to an
        internal array for future reference
        :param item:    The item to process.
        :return:        Recall function for item updates
        """

        def find_custom_attr(item, index=1):
            """ find custom item attribute recursively.
            Returns attribute or None
            """
            parent = item.return_parent()

            # parent(top_item) is sh.items
            if type(parent) != type(item):
                # reached top of item tree
                return None

            if self.has_iattr(parent.conf, self._item_attrs.get('ITEM_ATTR_CUSTOM' + str(index), 'foo')):
                return self.get_iattr_value(parent.conf, self._item_attrs.get('ITEM_ATTR_CUSTOM' + str(index), 'foo'))

            return find_custom_attr(parent, index)

        command = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_COMMAND', 'foo'))

        # handle custom item attributes
        self._items_custom[item.id()] = {1: None, 2: None, 3: None}
        for index in (1, 2, 3):

            val = None
            if self.has_iattr(item.conf, self._item_attrs.get('ITEM_ATTR_CUSTOM' + str(index), 'foo')):
                val = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_CUSTOM' + str(index), 'foo'))
                self.logger.debug(f'Item {item} has custom item attribute {index} with value {val}')
            elif self.has_recursive_custom_attribute(index):
                val = find_custom_attr(item, index)
                if val is not None:
                    self.logger.debug(f'Item {item} inherited custom item attribute {index} with value {val}')
            if val is not None:
                self.set_custom_item(item, command, index, val)
                self._items_custom[item.id()][index] = val

        custom_token = ''
        if self.custom_commands and self._items_custom[item.id()][self.custom_commands]:
            custom_token = CUSTOM_SEP + self._items_custom[item.id()][self.custom_commands]

        if command:

            # command found, validate command for device
            if not self.is_valid_command(command):
                self.logger.warning(f'Item {item} requests undefined command {command}, ignoring item')
                return

            # if "custom commands" are active for this device, modify command to
            # be <command>#<customx>, where x is the index of the xx_custom<x>
            # item attribute and <customx> is the value of the attribute.
            # By this modification, multiple items with the same command but
            # different customx-values can "coexist" and be differentiated by
            # the plugin and the device.
            command += custom_token

            # from here on command is combined if device.custom_commands is set
            # and a valid custom token is found

            self.add_item(item, device_command=command)

            # command marked for reading
            if self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_READ', 'foo')):
                if self.is_valid_command(command, COMMAND_READ):
                    if command not in self._commands_read:
                        self._commands_read[command] = []
                    self._commands_read[command].append(item)
                    self.logger.debug(f'Item {item} saved for reading command {command}')
                else:
                    self.logger.warning(f'Item {item} requests command {command} for reading, which is not allowed, read configuration is ignored')

                # read in group?
                group = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_GROUP', 'foo'))
                if group:
                    if isinstance(group, str):
                        group = [group]
                    if isinstance(group, list):
                        for grp in group:
                            if grp:
                                grp += custom_token
                                if grp not in self._commands_read_grp:
                                    self._commands_read_grp[grp] = []
                                self._commands_read_grp[grp].append(command)
                                self.logger.debug(f'Item {item} saved for reading in group {grp}')
                    else:
                        self.logger.warning(f'Item {item} wants to be read in group with invalid group identifier "{group}", ignoring.')

                # read on startup?
                if self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_READ_INIT', 'foo')):
                    if command not in self._commands_initial:
                        self._commands_initial.append(command)
                        self.logger.debug(f'Item {item} saved for startup reading command {command}')

                # read cyclically?
                cycle = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_CYCLE', 'foo'))
                if cycle:
                    # if cycle is already set for command, use the lower value of the two
                    self._commands_cyclic[command] = {'cycle': min(cycle, self._commands_cyclic.get(command, cycle)), 'next': 0}
                    self.logger.debug(f'Item {item} saved for cyclic reading command {command}')

            # command marked for writing
            if self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_WRITE', 'foo')):
                if self.is_valid_command(command, COMMAND_WRITE):
                    self._items_write[item.id()] = command
                    self.logger.debug(f'Item {item} saved for writing command {command}')
                    return self.update_item

            # pseudo commands
            if not self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_READ', 'foo')) and not self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_WRITE', 'foo')):
                if command not in self._commands_pseudo:
                    self._commands_pseudo[command] = []
                self._commands_pseudo[command].append(item)
                self.logger.debug(f'Item {item} saved for pseudo command {command}')

        # is read_grp trigger item?
        grp = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_READ_GRP', 'foo'))
        if grp:

            grp += custom_token
            item_msg = f'Item {item}'
            if custom_token:
                item_msg += f' with token {custom_token}'
            item_msg += ' saved for '

            # trigger read on startup?
            if self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_READ_INIT', 'foo')):
                if grp not in self._triggers_initial:
                    self._triggers_initial.append(grp)
                    self.logger.debug(f'{item_msg} startup triggering of read group {grp}')

            # read cyclically?
            cycle = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_CYCLE', 'foo'))
            if cycle:
                # if cycle is already set for command, use the lower value of the two
                self._triggers_cyclic[grp] = {'cycle': min(cycle, self._triggers_cyclic.get(grp, cycle)), 'next': 0}
                self.logger.debug(f'{item_msg} cyclic triggering of read group {grp}')

            if grp == '0':
                self._items_read_all.append(item.id())
                self.logger.debug(f'{item_msg} read_all')
                return self.update_item
            elif grp:
                self._items_read_grp[item.id()] = grp
                self.logger.debug(f'{item_msg} reading group {grp}')
                return self.update_item
            else:
                self.logger.warning(f'Item {item} wants to trigger group read with invalid group identifier "{grp}", ignoring.')

        # is lookup table item?
        table = self.get_iattr_value(item.conf, self._item_attrs.get('ITEM_ATTR_LOOKUP', 'foo'))
        if table:

            mode = 'fwd'
            if '#' in table:
                (table, mode) = table.split('#')
            lu = self.get_lookup(table, mode)
            item.set(lu, self.get_shortname, source='Init')
            if lu:
                self.logger.debug(f'Item {item} assigned lookup {table} with contents {lu}')
            else:
                self.logger.info(f'Item {item} requested lookup {table}, which was empty or non-existent')

    def update_item(self, item, caller=None, source=None, dest=None):
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
        if self.alive:

            self.logger.debug(f'Update_item was called with item "{item}" from caller {caller}, source {source} and dest {dest}')
            if not (self.has_iattr(item.conf, self._item_attrs.get('ITEM_ATTR_COMMAND', 'foo')) or self.has_iattr(item.conf, self._item_attrs.get('ITEM_ATTR_READ_GRP', 'foo'))):
                self.logger.warning(f'Update_item was called with item {item}, which is not configured for this plugin. This shouldn\'t happen...')
                return

            # test if source of item change was not ourselves...
            if caller != self.get_shortname():

                # okay, go ahead
                self.logger.info(f'Update item: {item.id()}: item has been changed outside this plugin')

                # item in list of write-configured items?
                if item.id() in self._items_write:

                    # get data and send new value
                    command = self._items_write[item.id()]
                    self.logger.debug(f'Writing value "{item()}" from item {item.id()} with command "{command}"')
                    if not self.send_command(command, item(), custom=self._items_custom[item.id()]):
                        self.logger.debug(f'Writing value "{item()}" from item {item.id()} with command "{command}" failed, resetting item value')
                        item(item.property.last_value, self.get_shortname())
                        return None

                elif item.id() in self._items_read_all:

                    # get data and trigger read_all
                    self.logger.debug('Triggering read_all')
                    self.read_all_commands()

                elif item.id() in self._items_read_grp:

                    # get data and trigger read_grp
                    group = self._items_read_grp[item.id()]
                    self.logger.debug(f'Triggering read_group {group}')
                    self.read_all_commands(group)

    def send_command(self, command, value=None, **kwargs):
        """
        Sends the specified command to the device providing <value> as data
        Not providing data will issue a read command, trying to read the value
        from the device and writing it to the associated item.

        :param command: the command to send
        :param value: the data to send, if applicable
        :type command: str
        :return: True if send was successful, False otherwise
        :rtype: bool
        """
        if not self.alive:
            self.logger.warning(f'trying to send command {command} with value {value}, but device is not active.')
            return False

        if not self._connection:
            self.logger.warning(f'trying to send command {command} with value {value}, but connection is None. This shouldn\'t happen...')
            return False

        kwargs.update(self._parameters)
        if self.custom_commands:
            try:
                command, custom_value = command.split(CUSTOM_SEP)
                if 'custom' not in kwargs:
                    kwargs['custom'] = {1: None, 2: None, 3: None}
                kwargs['custom'][self.custom_commands] = custom_value
            except ValueError:
                self.logger.debug(f'extracting custom token failed, maybe not present in command {command}')

        if not self._connection.connected():
            if self._parameters.get(PLUGIN_ATTR_CONN_AUTO_CONN):
                self._connection.open()

            if not self._connection.connected():
                self.logger.warning(f'trying to send command {command} with value {value}, but connection could not be established.')
                return False

        try:
            data_dict = self._commands.get_send_data(command, value, **kwargs)
        except Exception as e:
            self.logger.warning(f'command {command} with value {value} produced error on converting value, aborting. Error was: {e}')
            return False

        if data_dict['payload'] is None or data_dict['payload'] == '':
            self.logger.warning(f'command {command} with value {value} yielded empty command payload, aborting')
            return False

        data_dict = self._transform_send_data(data_dict, **kwargs)
        self.logger.debug(f'command {command} with value {value} yielded send data_dict {data_dict}')

        # if an error occurs on sending, an exception is thrown "below"
        result = None
        try:
            result = self._send(data_dict)
        except OSError as e:  # Exception as e:
            self.logger.debug(f'error on sending command {command}, error was {e}')
            return False

        if result:
            by = kwargs.get('by')
            self.logger.debug(f'command {command} received result {result} by {by}')
            self.on_data_received(by, value, command)

        return True

    def on_data_received(self, by, data, command=None):
        """
        Callback function for received data e.g. from an event loop
        Processes data and dispatches value to plugin class

        :param command: the command in reply to which data was received
        :param data: received data in 'raw' connection format
        :param by: client object / name / identifier
        :type command: str
        """
        data = self._transform_received_data(data)
        if command is not None:
            self.logger.debug(f'received data "{data}" from {by} for command {command}')
        else:
            # command == None means that we got raw data from a callback and
            # don't know yet to which command this belongs to. So find out...
            self.logger.debug(f'received data "{data}" from {by} without command specification')

            # command can be a string (classic single command) or 
            # - new - a list of strings if multiple commands are identified
            # in that case, work on all strings
            commands = self._commands.get_command_from_reply(data)
            if not commands:
                if self._discard_unknown_command:
                    self.logger.debug(f'data "{data}" did not identify a known command, ignoring it')
                    return
                else:
                    self.logger.debug(f'data "{data}" did not identify a known command, forwarding it anyway for {self._unknown_command}')
                    self._dispatch_callback(self._unknown_command, data, by)

        # TODO: remove later?
        assert(isinstance(commands, list))

        # process all commands
        for command in commands:

            custom = None
            if self.custom_commands:
                custom = self._get_custom_value(command, data)

            base_command = command
            value = None
            try:
                value = self._commands.get_shng_data(command, data)
                if custom:
                    command = command + CUSTOM_SEP + custom
            except OSError as e:  # Exception as e:
                self.logger.info(f'received data "{data}" for command {command}, error {e} occurred while converting. Discarding data.')
            else:
                self.logger.debug(f'received data "{data}" for command {command} converted to value {value}')
                self._dispatch_callback(command, value, by)

            self._process_additional_data(base_command, data, value, custom, by)

    def dispatch_data(self, command, value, by=None):
        """
        Callback function - new data has been received from device.
        Value is already in item-compatible format, so find appropriate item
        and update value

        :param command: command for or in reply to which data was received
        :param value: data
        :param by: str
        :type command: str
        """
        if self.alive:

            item = None

            # check if command is configured for reading
            items = self._commands_read.get(command, [])
            items += self._commands_pseudo.get(command, [])

            if not items:
                self.logger.warning(f'Command {command} yielded value {value}, not assigned to any item, discarding data')
                return

            for item in items:
                self.logger.debug(f'Command {command} wants to update item {item.id()} with value {value}')
                item(value, self.get_shortname())

    def read_all_commands(self, group=''):
        """
        Triggers all configured read commands or all configured commands of given group
        """
        if not group:
            for cmd in self._commands_read:
                self.send_command(cmd)
        else:
            if group in self._commands_read_grp:
                for cmd in self._commands_read_grp[group]:
                    self.send_command(cmd)

    def is_valid_command(self, command, read=None):
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
        if self.custom_commands:
            try:
                command, custom_value = command.split(CUSTOM_SEP)
                if custom_value not in self._custom_values[self.custom_commands]:
                    self.logger.debug(f'custom value {custom_value} not in known custom values {self._custom_values[self.custom_commands]}')
                    return None
            except ValueError:
                pass

        if self._commands:
            return self._commands.is_valid_command(command, read)
        else:
            return False

    def get_lookup(self, lookup, mode='fwd'):
        """ returns the lookup table for name <lookup>, None on error """
        if self._commands:
            return self._commands.get_lookup(lookup, mode)
        else:
            return None

    def has_recursive_custom_attribute(self, index=1):
        rec = self._parameters.get(PLUGIN_ATTR_RECURSIVE, [])
        if isinstance(rec, list):
            return index in rec
        else:
            return rec == index

    def set_custom_item(self, item, command, index, value):
        """ this is called by parse_items if xx_custom[123] is found. """
        self._custom_values[index].append(value)
        self._custom_values[index] = list(set(self._custom_values[index]))

    #
    #
    # check if overwriting needed
    #
    #

    def _set_device_defaults(self):
        """ Set custom class properties. Overwrite as needed... """

        # if you want to enable callbacks, overwrite this method and set
        # self._use_callbacks = True
        pass

    def _post_init(self):
        """ do something after default initializing is done. Overwrite it """
        pass

    def _transform_send_data(self, data_dict, **kwargs):
        """
        This method provides a way to adjust, modify or transform all data before
        it is sent to the device.
        This might be to add general parameters, include custom attributes,
        add/change line endings or add your favourite pet's name...
        By default, nothing happens here.
        """
        return data_dict

    def _transform_received_data(self, data):
        """
        This method provides a way to adjust, modify or transform all data as soon
        as it is received from the device.
        This might be useful to clean or parse data.
        By default, nothing happens here.
        """
        return data

    def _send(self, data_dict):
        """
        This method acts as a overwritable intermediate between the handling
        logic of send_command() and the connection layer.
        If you need any special arrangements for or reaction to events on sending,
        you can implement this method in your plugin class.

        By default, this just forwards the data_dict to the connection instance
        and return the result.
        """
        self.logger.debug(f'sending {data_dict}')
        return self._connection.send(data_dict)

    def on_connect(self, by=None):
        """ callback if connection is made. """
        pass

    def on_disconnect(self, by=None):
        """ callback if connection is broken. """
        pass

    def _process_additional_data(self, command, data, value, custom, by):
        """ do additional processing of received data

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

    def _get_custom_value(self, command, data):
        """
        extract custom value from data
        At least PATTERN needs to be overwritten
        """
        if not self.custom_commands:
            return None
        if not isinstance(data, str):
            return None
        res = re.search(self._token_pattern, data)
        if not res:
            self.logger.debug(f'custom token not found in {data}, ignoring')
            return None
        elif res[0] in self._custom_values[self.custom_commands]:
            return res[0]
        else:
            self.logger.debug(f'received custom token {res[0]}, not in list of known tokens {self._custom_values[self.custom_commands]}')
            return None

    def _get_connection(self, conn_type=None, conn_classname=None, conn_cls=None, proto_type=None, proto_classname=None, proto_cls=None, name=None):
        """
        return connection object.

        Try to identify the wanted connection and return the proper subclass
        instead. If no decision is possible, just return an instance of the
        base class SDPConnection, which is - externally - nonfunctional, but
        can stand as a debugging and diagnosis tool.

        If the PLUGIN_ATTR_PROTOCOL parameter is set, we need to change
        something. In this case, the protocol instance takes the place of the
        connection object and instantiates the connection object itself. Instead
        of the name of the connection class, we pass the class itself, so
        instantiating it poses no further challenge.

        If you need to use other connection types for your device, implement it
        and preselect with PLUGIN_ATTR_CONNECTION in /etc/plugin.yaml, so this
        class will never be used.
        """
        if self._use_callbacks:
            self.logger.debug('setting callbacks')
            self._parameters[PLUGIN_ATTR_CB_ON_CONNECT] = self.on_connect
            self._parameters[PLUGIN_ATTR_CB_ON_DISCONNECT] = self.on_disconnect

        params = self._parameters.copy()

        conn_cls = SDPConnection._get_connection_class(self, conn_cls, conn_classname, conn_type, **params)
        if not conn_cls:
            return None

        # if protocol is specified, find second class
        if PLUGIN_ATTR_PROTOCOL in self._parameters:

            proto_cls = SDPConnection._get_protocol_class(self, proto_cls, proto_classname, proto_type, **params)
            if not proto_cls:
                return None

            # set connection class in _params dict for protocol class to use
            self._parameters[PLUGIN_ATTR_CONNECTION] = conn_cls

            # return protocol instance as connection instance
            self.logger.debug(f'using protocol class {proto_cls}')
            return proto_cls(self.on_data_received, name=name, **self._parameters)

        self.logger.debug(f'using connection class {conn_cls}')
        return conn_cls(self.on_data_received, name=name, **self._parameters)

    def _create_cyclic_scheduler(self):
        """
        Setup the scheduler to handle cyclic read commands and find the proper
        time for the cycle.
        """
        if not self.alive:
            return

        # find shortest cycle
        shortestcycle = -1
        for cmd in self._commands_cyclic:
            cycle = self._commands_cyclic[cmd]['cycle']
            if shortestcycle == -1 or cycle < shortestcycle:
                shortestcycle = cycle
        for grp in self._triggers_cyclic:
            cycle = self._triggers_cyclic[grp]['cycle']
            if shortestcycle == -1 or cycle < shortestcycle:
                shortestcycle = cycle

        # Start the worker thread
        if shortestcycle != -1:

            # Balance unnecessary calls and precision
            workercycle = int(shortestcycle / 2)

            # just in case it already exists...
            if self.scheduler_get(self.get_shortname() + '_cyclic'):
                self.scheduler_remove(self.get_shortname() + '_cyclic')
            self.scheduler_add(self.get_shortname() + '_cyclic', self._read_cyclic_values, cycle=workercycle, prio=5, offset=0)
            self.logger.info(f'Added cyclic worker thread {self.get_shortname()}_cyclic with {workercycle} s cycle. Shortest item update cycle found was {shortestcycle} s')

    def _read_initial_values(self):
        """
        Read all values configured to be read/triggered at startup
        """
        if self._initial_value_read_done:
            self.logger.debug('_read_initial_values() called, but inital values were already read. Ignoring')
        else:
            if self._commands_initial:
                self.logger.info('Starting initial read commands')
                for cmd in self._commands_initial:
                    self.logger.debug(f'Sending initial command {cmd}')
                    self.send_command(cmd)
                self._initial_value_read_done = True
                self.logger.info('Initial read commands sent')
            if self._triggers_initial:
                self.logger.info('Starting initial read group triggers')
                for grp in self._triggers_initial:
                    self.logger.debug(f'Triggering initial read group {grp}')
                    self.read_all_commands(grp)
                self.logger.info('Initial read group triggers sent')

    def _read_cyclic_values(self):
        """
        Recall function for cyclic scheduler.
        Reads all values configured to be read cyclically.
        """
        # check if another cyclic cmd run is still active
        if self._cyclic_update_active:
            self.logger.warning('Triggered cyclic command read, but previous cyclic run is still active. Check device and cyclic configuration (too much/too short?)')
            return
        else:
            self.logger.info('Triggering cyclic command read')

        # set lock
        self._cyclic_update_active = True
        currenttime = time.time()
        read_cmds = 0
        todo = []
        for cmd in self._commands_cyclic:

            # Is the command already due?
            if self._commands_cyclic[cmd]['next'] <= currenttime:
                todo.append(cmd)

        for cmd in todo:
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
            self._commands_cyclic[cmd]['next'] = currenttime + self._commands_cyclic[cmd]['cycle']
            read_cmds += 1

        if read_cmds:
            self.logger.debug(f'Cyclic command read took {(time.time() - currenttime):.1f} seconds for {read_cmds} items')

        currenttime = time.time()
        read_grps = 0
        todo = []
        for grp in self._triggers_cyclic:

            # Is the trigger already due?
            if self._triggers_cyclic[grp]['next'] <= currenttime:
                todo.append(grp)

        for grp in todo:
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
            self._triggers_cyclic[grp]['next'] = currenttime + self._triggers_cyclic[grp]['cycle']
            read_grps += 1

        if read_grps:
            self.logger.debug(f'Cyclic triggers took {(time.time() - currenttime):.1f} seconds for {read_grps} groups')

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
                return None

            cls = getattr(cmd_module, self._command_class, None)

        if cls is None:
            cls = SDPCommand
        self._commands = SDPCommands(cls, **self._parameters)
        return True

    def _import_structs(self):
        """ check if additional MODEL struct is needed and insert it """

        # check for and load struct definitions
        if not SDP_standalone:

            shstructs = self._sh.items.return_struct_definitions(False)
            model = self._parameters.get('model', '')
            m_name = self.get_shortname() + '.' + model
            a_name = self.get_shortname() + '.' + INDEX_GENERIC
            m_struct = None

            if model and m_name in shstructs:
                m_struct = shstructs[m_name]
            elif a_name in shstructs:
                m_struct = shstructs[a_name]

            if m_struct:
                self.logger.debug(f'adding struct {self.get_shortname()}.{INDEX_MODEL}')
                self._sh.items.add_struct_definition(self.get_shortname(), INDEX_MODEL, m_struct)

    def _set_item_attributes(self):
        """
        reads all item attributes defined in sdp.globals, tries to find the
        actual item attribute (as imported from plugin.yaml) and modifies the
        global variable to refer to the actual item attribute.

        This way, only the prefixes in plugin.yaml need to be adjusted for new
        plugin classes, and the symbolic names can be used without additional
        mangling.
        """

        plugins = Plugins.get_instance()
        global_mod = sys.modules.get('lib.model.sdp.globals', '')

        self._item_attrs = {}

        if plugins and global_mod:
            keys = list(self.metadata.itemdefinitions.keys())
            for attr in ATTR_NAMES:
                attr_val = getattr(global_mod, attr)
                for key in keys:
                    if key.endswith(attr_val):
                        self._item_attrs[attr] = key
                        break

#
        print(f'W 0000 000000 {self.get_fullname()}: {keys}\nW 0000 000000 {self._item_attrs}')

    def init_webinterface(self, WebInterface=None):
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        if WebInterface is None:
            return False

        try:
            # handle running in a core version that does not support modules
            self.mod_http = Modules.get_instance().get_module('http')
        except Exception:
            self.mod_http = None
        if self.mod_http is None:
            self.logger.warning("Module 'http' not loaded. Not initializing the web interface for the plugin")
            return False

        # set application configuration for cherrypy
        webif_dir = self.path_join(self.get_plugin_dir(), 'webif')
        config = {
            '/': {
                'tools.staticdir.root': webif_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static'
            }
        }

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True


################################################################################
#
#
# Standalone functions
#
#
################################################################################

class Standalone():

    def __init__(self, plugin_class, plugin_file):

        self.item_tree = {}

        pfitems = plugin_file.split('/')

        self.plugin_mod_path = '.'.join(pfitems[:-1])
        self.plugin_path = os.path.join(*pfitems[:-1])
        self.plugin_name = pfitems[-2]

        usage = """
        Usage:
        ------------------------------------------------------------------------

        This plugin is meant to be used inside SmartHomeNG.

        Is is generally possible to run this plugin in standalone mode, usually
        for diagnostic purposes - IF the plugin supports this mode.

        ========================================================================

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

        If you add the -a parameter, all items will have an added

        ``visu_acl: <ro>/<rw>``

        attribute depending on the read/write configuration.
        ========================================================================

        If you call it with -s as a parameter, the plugin will insert the struct
        into the plugins' `plugins/<plugin_name>/plugin.yaml` file. Old struct
        content will be overwritten:

        ``__init__.py -s``

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(message)s  @ %(lineno)d')
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(ch)

        self.struct_mode = False
        self.acl = False

        self.indentwidth = 4

        if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ['-h', '--help', '-?', '/?', '/h', '/help']):

            # check for further command line arguments
            self.params = {}
            for arg in range(1, len(sys.argv)):

                arg_str = sys.argv[arg]

                if arg_str == '-v':
                    print('Debug logging enabled')
                    self.logger.setLevel(logging.DEBUG)

                elif arg_str[:2].lower() == '-s':
                    self.struct_mode = True

                elif arg_str[:2].lower() == '-a':
                    self.acl = True

                else:
                    try:
                        # convertible to dict?
                        self.params.update(literal_eval(arg_str))
                    except Exception:
                        # if not: try to parse as 'name=value'
                        match = re.match('([^= \n]+)=([^= \n]+)', arg_str)
                        if match:
                            name, value = match.groups(0)
                            self.params[name] = value

        else:
            print(usage)
            return

        self.params[PLUGIN_PATH] = self.plugin_mod_path

        if self.struct_mode:

            # as we output a formatted syntax, we can not create any output now
            self.create_struct_yaml()
            return

        s = f'This is the {self.plugin_name} plugin running in standalone mode'
        print(s)
        print('=' * len(s))

        pl = plugin_class(None, logger=self.logger, **self.params)

        if getattr(pl, 'run_standalone', ''):
            print('running standalone method...')

            pl.run_standalone()
        else:
            print('plugin doesn\'t have a standalone function.')

        print('Done.')

    def add_item_to_tree(self, item_path, item_dict):
        """ add entry for custom read group triggers """

        dst_path_elems = item_path.split('.')
        item = {dst_path_elems[-1]: item_dict}
        for elem in reversed(dst_path_elems[:-1]):
            item = {elem: item}

        update(self.item_tree, item)

    def walk(self, node, node_name, parent, func, path, indent, gpath, gpathlist, has_models, func_first=True, cut_levels=0):
        """ traverses a nested dict

        :param node: starting node
        :param node_name: name of the starting node on parent level ('key')
        :param parent: parent node
        :param func: function to call for each node
        :param path: path of the current node (pparent.parent.node)
        :param indent: indent level (indent is INDENT ** indent)
        :param gpath: path of 'current' (next above) read group
        :param gpathlist: list of all current (above) read groups
        :param has_models: True is command dict has models ('ALL')
        -> include top level = model name in read groups and in command paths
        :param func_first: order of work (func) and walk, True is work first
        :param cut_levels: cut <n> levels from front of path
        :type node: dict
        :type node_name: str
        :type parent: dict
        :type func: function
        :type path: str
        :type indent: int
        :type gpath: str
        :type gpathlist: list
        :type has_models: bool
        :type func_first: bool
        """

        if func and func_first:
            # first call func -> print current node before descending
            func(node, node_name, parent, path, indent, gpath, gpathlist, cut_levels)

        # iterate over all children who are dicts
        for child in list(k for k in node.keys() if isinstance(node[k], dict)):

            if path:
                new_path = path + COMMAND_SEP
            elif not has_models:
                new_path = node_name + COMMAND_SEP
            else:
                new_path = ''
            new_path += child

            # and recursively walk them
            self.walk(node[child], child, node, func, new_path, indent + 1, path, gpathlist + ([path] if path else []), has_models, func_first, cut_levels)

        if func and not func_first:
            # last call func -> process current node after descending
            func(node, node_name, parent, path, indent, gpath, gpathlist)

    def find_read_group_triggers(self, node, node_name, parent, path, indent, gpath, gpathlist, cut_levels):
        """ find custom read trigger definitions, create trigger item

        for params see walk() above, they are the same there

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

                    self.add_item_to_tree(item_path, {'type': 'bool', 'enforce_updates': 'true', ITEM_ATTR_READ_GRP: entry.get('name')})

    def create_item(self, node, node_name, parent, path, indent, gpath, gpathlist, cut_levels=0):
        """ create item or read item for current node/command

        for params see walk() above, they are the same there
        """
        if not node_name:
            return

        # item name = item path is in path
        # item contents goes in item
        item = {}

        # skip known command sub-dict nodes, but include command nodes
        if CMD_ATTR_ITEM_TYPE in node or (node_name not in (CMD_ATTR_CMD_SETTINGS, CMD_ATTR_PARAMS, CMD_ATTR_ITEM_ATTRS, CMD_IATTR_ATTRIBUTES) and 'type' not in node):

            # item -> print item attributes
            if CMD_ATTR_ITEM_TYPE in node:
                item['type'] = node.get(CMD_ATTR_ITEM_TYPE, 'foo')
                cmd = path if path else node_name
                if cut_levels:
                    cmd = COMMAND_SEP.join(cmd.split(COMMAND_SEP)[cut_levels:])
                item[ITEM_ATTR_COMMAND] = cmd
                item[ITEM_ATTR_READ] = node.get(CMD_ATTR_READ, True)
                item[ITEM_ATTR_WRITE] = node.get(CMD_ATTR_WRITE, False)
                if self.acl:
                    item['visu_acl'] = 'rw' if node.get(CMD_ATTR_WRITE, False) else 'ro'

                # set sub-node for readability
                inode = node.get(CMD_ATTR_ITEM_ATTRS)

                rg_level = None
                rg_list = None
                if inode:
                    rg_level = inode.get(CMD_IATTR_RG_LEVELS, None)
                    rg_list = inode.get(CMD_IATTR_READ_GROUPS)

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
                    item[ITEM_ATTR_GROUP] = grps

                if inode:
                    if inode.get(CMD_IATTR_ENFORCE):
                        item['enforce_updates'] = True
                    if inode.get(CMD_IATTR_INITIAL):
                        item[ITEM_ATTR_READ_INIT] = True
                    cycle = inode.get(CMD_IATTR_CYCLE)
                    if cycle:
                        item[ITEM_ATTR_CYCLE] = cycle
                    custom = inode.get(CMD_IATTR_CUSTOM1)
                    if custom is not None:
                        item[ITEM_ATTR_CUSTOM1] = custom
                    custom = inode.get(CMD_IATTR_CUSTOM2)
                    if custom is not None:
                        item[ITEM_ATTR_CUSTOM1[:-1] + '2'] = custom
                    custom = inode.get(CMD_IATTR_CUSTOM3)
                    if custom is not None:
                        item[ITEM_ATTR_CUSTOM1[:-1] + '3'] = custom

                    # custom item attributes: add 1:1
                    attrs = inode.get(CMD_IATTR_ATTRIBUTES)
                    if attrs:
                        update(item, attrs)

                    # custom item templates: add 1:!
                    templates = inode.get(CMD_IATTR_TEMPLATE)
                    if templates:
                        if not isinstance(templates, list):
                            templates = [templates]
                        for tmpl in templates:
                            if tmpl in self.item_templates:
                                update(item, self.item_templates[tmpl])

                    # if item has 'xx_lookup' and item_attrs['lookup_item'] is
                    # set, create additional item with lookup values
                    lu_item = inode.get(CMD_IATTR_LOOKUP_ITEM)
                    if lu_item and node.get(CMD_ATTR_LOOKUP):
                        ltyp = inode.get(CMD_IATTR_LOOKUP_ITEM)
                        if ltyp is True:
                            ltyp = 'list'
                        item['lookup'] = {'type': 'list' if ltyp == 'list' else 'dict'}
                        item['lookup'][ITEM_ATTR_LOOKUP] = f'{node.get(CMD_ATTR_LOOKUP)}#{ltyp}'

            # 'level node' -> print read item
            elif node_name not in (CMD_ATTR_CMD_SETTINGS, CMD_ATTR_PARAMS, CMD_ATTR_ITEM_ATTRS, CMD_IATTR_ATTRIBUTES, CMD_IATTR_READ_GROUPS):

                item['read'] = {'type': 'bool'}
                item['read']['enforce_updates'] = True
                item['read'][ITEM_ATTR_READ_GRP] = path if path else node_name
                try:
                    # set sub-node for readability
                    inode = node.get(CMD_ATTR_ITEM_ATTRS)
                    if inode.get(CMD_IATTR_INITIAL):
                        item['read'][ITEM_ATTR_READ_INIT] = True
                    if inode.get(CMD_IATTR_CYCLE):
                        item['read'][ITEM_ATTR_CYCLE] = inode.get(CMD_IATTR_CYCLE)
                except AttributeError:
                    pass

            if item:
                self.add_item_to_tree(path, item)

            if CMD_ATTR_ITEM_ATTRS in node:
                self.find_read_group_triggers(node, node_name, parent, path, indent, gpath, gpathlist, cut_levels)

    def removeItemsUndefCmd(self, node, node_name, parent, path, indent, gpath, gpathlist, cut_levels=0):
        if CMD_ATTR_ITEM_TYPE in node and path not in self.cmdlist:
            del parent[node_name]

    def removeEmptyItems(self, node, node_name, parent, path, indent, gpath, gpathlist, cut_levels=0):
        if len(node) == 0:
            del parent[node_name]

    def update_item_attributes(self):
        global_mod = sys.modules.get('lib.model.sdp.globals', '')
        global_vars = globals()
        file = self.plugin_path + '/plugin.yaml'
        yaml = shyaml.yaml_load(file)
        keys = list(yaml.get('item_attributes').keys())

        if keys and global_mod:

            new = {}
            for attr in ATTR_NAMES:
                attr_val = getattr(global_mod, attr)
                for key in keys:
                    if key.endswith(attr_val):
                        new[attr] = key
                        break

            for attr in new:
                global_vars[attr] = new[attr]

    def create_struct_yaml(self):
        """ read commands.py and export struct.yaml """

        self.update_item_attributes()

        mod_str = self.plugin_mod_path + '.commands'
        try:
            cmd_module = importlib.import_module(mod_str, __name__)
        except Exception as e:
            raise ImportError(f'error on importing commands, aborting. Error was {e}')

        commands = cmd_module.commands
        top_level_entries = list(commands.keys())

        self.item_templates = getattr(cmd_module, 'item_templates', {})
        err = None

        try:
            file = os.path.join(self.plugin_path, 'plugin.yaml')
            self.yaml = shyaml.yaml_load(file, ordered=True)
            self.yaml['item_structs'] = OrderedDict()

            # this means the commands dict has 'ALL' and model names at the top
            # level otherwise, these be commands or sections
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
                    self.walk(obj[model], '', None, self.create_item, '', 0, model, [model], True)

                    jdata = json.dumps(self.item_tree)
                    self.yaml['item_structs'][model] = json.loads(jdata, object_pairs_hook=OrderedDict)

            else:

                # create flat commands, 'valid command' needs full cmd path
                flat_commands = deepcopy(commands)
                SDPCommands._flatten_cmds(None, flat_commands)

                # output sections separately and unchanged
                for section in top_level_entries:

                    self.item_tree = {}

                    obj = {section: commands[section]}

                    # create item tree
                    self.walk(obj[section], section, None, self.create_item, section, 0, '', [], True)

                    jdata = json.dumps(self.item_tree)
                    self.yaml['item_structs'][section] = json.loads(jdata, object_pairs_hook=OrderedDict)[section]

                # get model definitions
                # if not present, fake it to include all sections
                models = getattr(cmd_module, 'models', [])
                if not models:
                    models = {'ALL': list(commands.keys())}

                for model in models:

                    self.item_tree = {}

                    # create list of valid commands
                    self.cmdlist = models[model]
                    if model != INDEX_GENERIC:
                        self.cmdlist += models.get(INDEX_GENERIC, [])
                    self.cmdlist = SDPCommands._get_cmdlist(None, flat_commands, self.cmdlist)

                    # create new obj for model m, include m['ALL']
                    # as we modify obj, we need to copy this
                    obj = {model: deepcopy(commands)}

                    # remove all items with model-invalid 'xx_command'
                    self.walk(obj[model], model, obj, self.removeItemsUndefCmd, '', 0, model, [model], True, False)

                    # remove all empty items from obj
                    self.walk(obj[model], model, obj, self.removeEmptyItems, '', 0, model, [model], True, False)

                    # create item tree
                    self.walk(obj[model], model, obj, self.create_item, model, 0, '', [], False, cut_levels=1)

                    jdata = json.dumps(self.item_tree)
                    self.yaml['item_structs'][model] = json.loads(jdata, object_pairs_hook=OrderedDict)[model]

        except OSError as e:
            err = f'Error: file {file} could not be opened. Original error: {e}'
        except Exception as e:
            err = f'Unknown error occured while processing. Original error: {e}'

        shyaml.yaml_save(file, self.yaml)

        if err:
            print(err)
        else:
            print(f'Updated file {file}')
