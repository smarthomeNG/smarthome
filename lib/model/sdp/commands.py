#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SDPCommands for MultiDevice plugin
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
#
#########################################################################

import logging
import re
from pydoc import locate

from lib.model.sdp.globals import (update, CommandsError, CMD_ATTR_CMD_SETTINGS, CMD_ATTR_DEV_TYPE, CMD_ATTR_ITEM_ATTRS, CMD_ATTR_ITEM_TYPE, CMD_ATTR_LOOKUP, CMD_ATTR_OPCODE, CMD_ATTR_READ, CMD_ATTR_READ_CMD, CMD_ATTR_REPLY_PATTERN, CMD_ATTR_WRITE, CMD_ATTR_WRITE_CMD, COMMAND_PARAMS, COMMAND_SEP, INDEX_GENERIC, PATTERN_LOOKUP, PATTERN_VALID_LIST, PATTERN_VALID_LIST_CI, PATTERN_CUSTOM_PATTERN, PLUGIN_PATH)
from lib.model.sdp.command import SDPCommand
import lib.model.sdp.datatypes as DT


#############################################################################################################################################################################################################################################
#
# class SDPCommands
#
#############################################################################################################################################################################################################################################

class SDPCommands(object):
    """ SDPCommands class for managing commands support

    This class represents a command list to save some error handling code on
    every access (in comparison to using a dict). Not much more functionality
    here, most calls check for errors and pass thru the request to the selected
    SDPCommand-object

    Furthermore, this could be overwritten if so needed for special extensions.
    """
    def __init__(self, command_obj_class=SDPCommand, **kwargs):

        # get MultiDevice.device logger
        self.logger = logging.getLogger(__name__)

        self.logger.debug(f'commands initializing from {command_obj_class.__name__}')
        self._commands = {}         # { 'cmd_x': SDPCommand(params), ... }
        self._lookups = {}          # { 'name_x': {'fwd': {'K1': 'V1', ...}, 'rev': {'V1': 'K1', ...}, 'rci': {'v1': 'K1', ...}}}
        self._lookup_tables = []
        self._dev_structs = []
        self._cmd_class = command_obj_class
        self._params = {}
        self._params.update(kwargs)

        self._model = self._params.get('model', None)

        self._dt = {}
        self._return_value = None

        self._read_dt_classes()

        if not self._read_commands():
            return None

        if self._commands is not None:
            self.logger.debug(f'{len(self._commands)} commands initialized')
        elif not SDP_standalone:
            self.logger.error('commands could not be initialized')

    def is_valid_command(self, command, read=None):
        if command not in self._commands:
            return False

        if read is None:
            return True

        # if the corresponding attribute is not defined, assume False (fail safe)
        return getattr(self._commands[command], CMD_ATTR_READ if read else CMD_ATTR_WRITE, False)

    def get_send_data(self, command, data=None, **kwargs):
        if command in self._commands:
            lu = self._get_cmd_lookup(command)
            if lu:
                data = self._lookup(data, lu, rev=True)
            return self._commands[command].get_send_data(data, **kwargs)

        raise Exception(f'command {command} not found in commands')

    def get_shng_data(self, command, data, **kwargs):
        if command in self._commands:
            result = self._commands[command].get_shng_data(data, **kwargs)
            lu = self._get_cmd_lookup(command)
            if lu:
                result = self._lookup(result, lu)
            return result

        raise Exception(f'command {command} not found in commands')

    def get_command_from_reply(self, data):
        if data is None:
            return None

        if type(data) in (bytes, bytearray):
            data = str(data.decode('utf-8'))

        for command in self._commands:
            patterns = getattr(self._commands[command], CMD_ATTR_REPLY_PATTERN, None)
            if patterns:
                for pattern in patterns:
                    if pattern:
                        try:
                            regex = re.compile(pattern)
                            if regex.match(data) is not None:
                                self.logger.debug(f'matched reply_pattern {pattern} as regex against data {data}, found command {command}')
                                return command
                        except Exception as e:
                            self.logger.warning(f'parsing or matching reply_pattern {getattr(self._commands[command], CMD_ATTR_REPLY_PATTERN)} from command {command} as regex failed. Error was: {e}. Ignoring')

        return None

    def get_lookup(self, lookup, type='fwd'):
        """ returns the contents of the lookup table named <lookup>, None on error """
        if lookup in self._lookups and type in ('fwd', 'rev', 'rci'):
            return self._lookups[lookup][type]
        elif lookup in self._lookups and type == 'list':
            return list(self._lookups[lookup]['rev'].keys())
        else:
            return None

    def _lookup(self, data, table, rev=False, ci=True):
        """
        try to lookup data from lookup dict <table>

        normal mode is device data -> shng data (rev=False, ci is ignored)
        reverse mode is shng data -> device data (rev=True, ci=False)
        ci mode is reverse mode, but case insensitive lookup (rev=True, ci=True, default for rev)

        As data is used as key in dict lookups, it must be a hashable type (num, int, float, str)

        Per definition, data can be None, e.g. for read commands. In this case, return None

        On success, lookup result is returned. On error, an exception is raised.

        :param data: data to look up
        :param table: name of lookup dict
        :param rev: reverse mode (see above)
        :param ci: case insensitive reverse mode (see above)
        :type table: str
        :type rev: bool
        :type ci: bool
        :return: lookup result
        """
        if data is None or isinstance(data, (list, tuple, set, dict)):
            return None

        mode = 'fwd'
        if rev:
            mode = 'rci' if ci else 'rev'

        lu = self.get_lookup(table, mode)
        if not lu:
            raise ValueError(f'Lookup table {table} not found.')

        if rev and ci and isinstance(data, str):
            data = data.lower()

        if data in lu:
            return lu[data]

        raise ValueError(f'Lookup of value {data} in table {table} failed, entry not found.')

    def _get_cmd_lookup(self, command):
        """ returns lookup name for command or None """
        if command in self._commands:
            return self._commands[command].get_lookup()

        raise Exception(f'command {command} not found in commands')

    def _read_dt_classes(self):
        """
        This method enumerates all classes named 'DT_*' from the Datatypes module
        and tries to load custom 'DT_*' classes from the device's subdirectory
        datatypes.py file and collect all in the self._dt dict.
        Integrating custom classes into the DT module would change this for all
        loaded devices and name collisions could not be resolved.
        """
        def _enum_dt_cls(mod):
            classes = [cls for cls in dir(mod) if cls[:3] == 'DT_']
            for cls in classes:
                self._dt[cls] = getattr(mod, cls)

        self._dt['Datatype'] = DT.Datatype

        # enumerate 'DT_*' classes from DT
        _enum_dt_cls(DT)

        # try to load datatypes.py from device directory
        mod_str = self._params[PLUGIN_PATH] + '.datatypes'
        #if not SDP_standalone:
        #    mod_str = '.'.join(self.__module__.split('.')[:-1]) + '.' + mod_str

        cust_mod = locate(mod_str)
        if cust_mod:
            _enum_dt_cls(cust_mod)

    def _flatten_cmds(self, cmds):
        def walk(node, node_name, parent=None, func=None):
            for child in list(k for k in node.keys() if isinstance(node[k], dict)):
                walk(node[child], child, parent=node, func=func)
            if func:
                func(node, node_name, parent=parent)

        def moveItems(node, node_name, parent):
            # make sure we can move "upwards"
            if parent:
                # if node[CMD_ATTR_OPCODE] is not present, node is not a command
                if CMD_ATTR_ITEM_TYPE not in node:
                    for child in list(k for k in node.keys() if isinstance(node[k], dict)):
                        # node has dict elements node[child]
                        parent[node_name + COMMAND_SEP + child] = node[child]
                        del node[child]

        def removeEmptyItems(node, node_name, parent):
            if len(node) == 0:
                del parent[node_name]

        # flatten cmds
        walk(cmds, '', None, moveItems)
        # remove empty dicts (old 'level names')
        walk(cmds, '', None, removeEmptyItems)

    def _get_cmdlist(self, cmds, cmdlist):
        # now get command list, if not already provided
        if cmdlist is None:
            cmdlist = cmds.keys()

        # find all commands starting with any entry in cmdlist to capture categories
        # e.g. cmdlist = ['generic'] -> get all commands starting with generic + COMMAND_SEP
        new_cmdlist = []
        for cmd in cmds:
            if any(cmdspec + COMMAND_SEP == cmd[:len(cmdspec) + len(COMMAND_SEP)] or cmdspec == cmd for cmdspec in cmdlist):
                new_cmdlist.append(cmd)

        return new_cmdlist

    def _read_commands(self):
        """
        This is the loader portion for the commands.py file.

        Errors preventing the device from working raise `Exception`
        """

        # did we get a device type?
        # try to load commands.py from device directory
        mod_str = self._params[PLUGIN_PATH] + '.commands'

        try:
            # get module
            cmd_module = locate(mod_str)
        except ImportError:
            raise CommandsError('importing external module commands.py failed')
        except Exception as e:
            raise CommandsError(f'importing commands from external module commands.py failed. Error was: "{e}"')
            return False

        # param is read by yaml parser which converts None to "None"...
        if self._model == 'None':
            self._model = None

        if self._model == INDEX_GENERIC:
            self.logger.warning('configured model is identical to generic identifier, loading all commands.')
            self._model = None

        if self._model:
            if hasattr(cmd_module, 'models'):
                if isinstance(cmd_module.models, dict):
                    if self._model in cmd_module.models:
                        self.logger.info(f'model {self._model} identified')
                    else:
                        raise CommandsError(f'configured model {self._model} not found in commands.py models {cmd_module.models.keys()}')
                else:
                    raise CommandsError(f'model configuration for device type {self._device_type} invalid, "models" is not a dict')
        if hasattr(cmd_module, 'commands') and isinstance(cmd_module.commands, dict) and not SDP_standalone:
            cmds = cmd_module.commands
            cmdlist = None
            if INDEX_GENERIC in cmds:

                # if INDEX_GENERIC is present, take all generic commands.from commands dict..
                cmds = cmd_module.commands[INDEX_GENERIC]
                # and add model-specific, if present
                cmds.update(cmd_module.commands.get(self._model, {}))

            elif self._model:

                # otherwise, take list of generic and specific commands from models dict
                cmdlist = cmd_module.models.get(INDEX_GENERIC, []) + cmd_module.models.get(self._model, [])
                self.logger.debug(f'found {len(cmd_module.models.get(INDEX_GENERIC, []))} generic commands')
                if self._model:
                    self.logger.debug(f'found {len(cmd_module.models.get(self._model, []))} commands for model {self._model}')
            self._flatten_cmds(cmds)

            # do this before importing commands, because reply_patterns might need lookups
            if hasattr(cmd_module, 'lookups') and isinstance(cmd_module.lookups, dict):
                self._parse_lookups(cmd_module.lookups)
            else:
                self.logger.debug('no lookups found')

            # actually import commands
            self._parse_commands(cmds, self._get_cmdlist(cmds, cmdlist))
        else:
            if not SDP_standalone:
                self.logger.warning('no command definitions found. This device probably will not work...')

        if hasattr(cmd_module, 'structs') and isinstance(cmd_module.structs, dict):
            self._dev_structs = cmd_module.structs.get(INDEX_GENERIC, [])
            self.logger.debug(f'found {len(self._dev_structs)} generic structs')
            if self._model:
                self._dev_structs += cmd_module.structs.get(self._model, [])
                self.logger.debug(f'found {len(cmd_module.structs.get(self._model, []))} model-specific structs')

        return True

    def _parse_commands(self, commands, cmds=[]):
        """
        This is a reference implementation for parsing the commands dict imported
        from the commands.py file in the device subdirectory.
        For special purposes, this can be overwritten, if you want to use your
        own file format.
        """
        custom_patterns = self._params.get('custom_patterns')

        for cmd in cmds:
            # we found a "section" entry for which initial or cyclic read is specified. Just skip it...
            # the commands dict might look like this:
            #
            # 'zone2': {
            #     'control': { 'item_attrs': {...},
            #         'power': {'read': True,
            #
            # 'control' is only a section, and the only valid 'content' apart from sections or commands is 'item_attrs' to provide
            # for read triggers or other extensions. If 'item_attrs' is defined, it is syntactically identical to the following
            # commands, so the identifier 'item_attrs' is read as command name.
            if cmd[-len(CMD_ATTR_ITEM_ATTRS) - len(COMMAND_SEP):] == COMMAND_SEP + CMD_ATTR_ITEM_ATTRS:
                continue

            cmd_dict = commands[cmd]

            # preset default values
            kw = {CMD_ATTR_READ: True, CMD_ATTR_WRITE: False, CMD_ATTR_OPCODE: '', CMD_ATTR_ITEM_TYPE: 'bool', CMD_ATTR_DEV_TYPE: 'raw'}

            # update with command attributes
            for arg in COMMAND_PARAMS:
                if arg in cmd_dict:
                    kw[arg] = cmd_dict[arg]

            # if valid_list_ci is present in settings, convert all str elements to lowercase only once
            if CMD_ATTR_CMD_SETTINGS in kw:
                if 'valid_list_ci' in kw[CMD_ATTR_CMD_SETTINGS]:
                    kw[CMD_ATTR_CMD_SETTINGS]['valid_list_ci'] = [entry.lower() if isinstance(entry, str) else entry for entry in kw[CMD_ATTR_CMD_SETTINGS]['valid_list_ci']]

            dt_class = None
            dev_datatype = kw.get(CMD_ATTR_DEV_TYPE, '')
            if dev_datatype:
                class_name = '' if dev_datatype[:2] == 'DT_' else 'DT_' + dev_datatype
                dt_class = self._dt.get(class_name)

            # process pattern substitution
            if CMD_ATTR_REPLY_PATTERN in kw:
                if not isinstance(kw[CMD_ATTR_REPLY_PATTERN], list):
                    kw[CMD_ATTR_REPLY_PATTERN] = [kw[CMD_ATTR_REPLY_PATTERN]]
                processed_patterns = []

                for pattern in kw[CMD_ATTR_REPLY_PATTERN]:

                    if pattern == '*':
                        pattern = cmd_dict.get(CMD_ATTR_READ_CMD, cmd_dict.get(CMD_ATTR_OPCODE, ''))

                    if custom_patterns and PATTERN_CUSTOM_PATTERN in pattern:
                        for index in (1, 2, 3):
                            pattern = pattern.replace('{' + PATTERN_CUSTOM_PATTERN + str(index) + '}', custom_patterns[index])

                    if cmd_dict.get(CMD_ATTR_LOOKUP) and '{' + PATTERN_LOOKUP + '}' in pattern:

                        lu_pattern = '(' + '|'.join(re.escape(key) for key in self._lookups[cmd_dict[CMD_ATTR_LOOKUP]]['fwd'].keys()) + ')'
                        pattern = pattern.replace('{' + PATTERN_LOOKUP + '}', lu_pattern)

                    if cmd_dict.get(CMD_ATTR_CMD_SETTINGS) and 'valid_list' in cmd_dict[CMD_ATTR_CMD_SETTINGS] and '{' + PATTERN_VALID_LIST + '}' in pattern:

                        vl_pattern = '(' + '|'.join(re.escape(key) for key in cmd_dict[CMD_ATTR_CMD_SETTINGS]['valid_list']) + ')'
                        pattern = pattern.replace('{' + PATTERN_VALID_LIST + '}', vl_pattern)

                    if cmd_dict.get(CMD_ATTR_CMD_SETTINGS) and 'valid_list_ci' in cmd_dict[CMD_ATTR_CMD_SETTINGS] and '{' + PATTERN_VALID_LIST_CI + '}' in pattern:

                        vl_pattern = '((?i:' + '|'.join(re.escape(key) for key in cmd_dict[CMD_ATTR_CMD_SETTINGS]['valid_list_ci']) + '))'
                        pattern = pattern.replace('{' + PATTERN_VALID_LIST_CI + '}', vl_pattern)

                    processed_patterns.append(pattern)

                # store processed patterns
                kw[CMD_ATTR_REPLY_PATTERN] = processed_patterns

            if kw.get(CMD_ATTR_READ, False) and kw.get(CMD_ATTR_OPCODE, '') == '' and kw.get(CMD_ATTR_READ_CMD, '') == '':
                self.logger.info(f'command {cmd} will not create a command for reading values. Check commands.py configuration...')
            if kw.get(CMD_ATTR_WRITE, False) and kw.get(CMD_ATTR_OPCODE, '') == '' and kw.get(CMD_ATTR_WRITE_CMD, '') == '':
                self.logger.info(f'command {cmd} will not create a command for writing values. Check commands.py configuration...')
            if not dt_class:
                self.logger.error(f'importing command {cmd} found invalid datatype "{dev_datatype}", replacing with DT_raw. Check function of device')
                dt_class = DT.DT_raw
            self._commands[cmd] = self._cmd_class(cmd, dt_class, **{'cmd': kw, 'plugin': self._params})

    def _parse_lookups(self, lookups):
        """
        This is a reference implementation for parsing the lookups dict imported
        from the commands.py file in the device subdirectory.
        For special purposes, this can be overwritten, if you want to use your
        own file format.
        """
        if INDEX_GENERIC in lookups:
            lu = lookups[INDEX_GENERIC]
            self.logger.debug(f'found {len(lu)} generic lookup table{"" if len(lu) == 1 else "s"}')

            if self._model and self._model in lookups:
                update(lu, lookups[self._model])
                self.logger.debug(f'found {len(lookups[self._model])} lookup table{"" if len(lookups[self._model]) == 1 else "s"} for model {self._model}')
        else:
            lu = lookups

        try:
            for table in lu:
                if isinstance(lu[table], dict):

                    self._lookups[table] = {}

                    # original dict
                    self._lookups[table]['fwd'] = lu[table]
                    # reversed dict
                    self._lookups[table]['rev'] = {v: k for (k, v) in lu[table].items()}
                    # reversed dict, keys are lowercase for case insensitive lookup
                    self._lookups[table]['rci'] = {v.lower() if isinstance(v, str) else v: k for (k, v) in lu[table].items()}

                    self._lookup_tables.append(table)
                    self.logger.debug(f'imported lookup table {table} with {len(lu[table])} items')
                else:
                    self.logger.warning(f'key {table} in lookups not in dict format, ignoring')
        except Exception as e:
            self.logger.error(f'importing lookup tables not possible, check syntax. Error was: {e}')
