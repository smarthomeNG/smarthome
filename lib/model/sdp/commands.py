#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SDPCommands for SmartDevicePlugin class
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
from copy import deepcopy
from pydoc import locate

from lib.model.sdp.globals import (
    update, CommandsError, CMD_ATTR_CMD_SETTINGS, CMD_ATTR_DEV_TYPE,
    CMD_ATTR_ITEM_ATTRS, CMD_ATTR_ITEM_TYPE, CMD_ATTR_LOOKUP, CMD_ATTR_OPCODE, CMD_STR_PARAM,
    CMD_ATTR_READ, CMD_ATTR_READ_CMD, CMD_ATTR_REPLY_PATTERN, CMD_ATTR_WRITE,
    CMD_ATTR_WRITE_CMD, CMD_ATTR_ORG_PARAMS, COMMAND_PARAMS, COMMAND_SEP, INDEX_GENERIC,
    PATTERN_LOOKUP, PATTERN_VALID_LIST, PATTERN_VALID_LIST_CI, PATTERN_VALID_LIST_RE,
    PATTERN_CUSTOM_PATTERN, PLUGIN_PATH, CUSTOM_SEP)
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

        self.logger = logging.getLogger(__name__)

        self.logger.debug(f'commands initializing from {command_obj_class.__name__}')
        self._commands = {}         # { 'cmd_x': SDPCommand(params), ... }
        self._lookups = {}          # { 'name_x': {'fwd': {'K1': 'V1', ...}, 'rev': {'V1': 'K1', ...}, 'rci': {'v1': 'K1', ...}}}
        self._lookup_tables = []
        self._dev_structs = []
        self._cmd_class = command_obj_class
        self._params = {}
        self._params.update(kwargs)
        self._parsed_commands = {}

        self._model = self._params.get('model', None)

        self._dt = {}
        self._cust_dt = {}
        self._return_value = None

        self._read_dt_classes()

        if not self._read_commands():
            return

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
                try:
                    result = self._lookup(result, lu)
                except ValueError as e:
                    self.logger.warning(f'while parsing reply to {command}, the lookup of {lu} failed: {e}')
                    return
            return result

        raise Exception(f'command {command} not found in commands')

    def custom_is_enabled_for(self, command: str) -> bool:
        """
        return if custom handling is allowed or disabled for given command

        If a custom command <cmd>#<custval> is given, also check the base command.
        This seems nonsensical, but might help discover configuration errors
        """
        if not command:
            return True
        cmd = self._commands.get(command)
        if cmd:
            return not cmd.custom_disabled
        else:
            try:
                cmd, _ = command.split(CUSTOM_SEP)
                return self.custom_is_enabled_for(cmd)
            except (AttributeError, ValueError):
                pass
            self.logger.warning(f'command {command} not found while checking for custom handling')
            return True

    def get_commands_from_reply(self, data):
        """ return list of commands for received data """
        if data is None:
            return []

        if type(data) in (bytes, bytearray):
            data = str(data.decode('utf-8'))

        commands = []

        for command in self._commands:
            patterns = getattr(self._commands[command], CMD_ATTR_REPLY_PATTERN, None)
            if patterns:
                for pattern in patterns:
                    # check for empty pattern is superfluous as re.compile is in a try/except block, but...
                    # empty patterns would match anywhere and create false matches, so exclude those
                    if pattern:
                        try:
                            regex = re.compile(pattern)
                            if regex.search(data) is not None:
                                self.logger.debug(f'matched reply_pattern {pattern} as regex against data {data}, found command {command}')
                                commands.append(command)
                        except Exception as e:
                            self.logger.warning(f'parsing or matching reply_pattern {pattern} from command {command} as regex failed. Error was: {e}. Ignoring')

        return commands

    def get_lookup(self, lookup, type='fwd'):
        """ returns the contents of the lookup table named <lookup>, None on error """
        if lookup in self._lookups and type in ('fwd', 'rev', 'rci'):
            return self._lookups[lookup][type]
        elif lookup in self._lookups and type == 'list':
            return list(self._lookups[lookup]['rev'].keys())
        else:
            return None

    def get_commandlist(self, cmd=None):
        """ return list of (or single given) commands with command config for use eg. in webif """
        if cmd:
            return self._parsed_commands.get(cmd)
        else:
            return self._parsed_commands

    def get_dtlist(self, custom=True):
        """ return list of DT class names """
        if custom:
            return list(self._cust_dt.keys())
        else:
            return list(self._dt.keys())

    def update_lookup_table(self, name, table):
        """
        update lookup table

        take given dict as forward lookup table `name`, create rev and rci tables
        and store tables in lookups dict.
        Also, call all commands and if necessary, update reply_patterns to reflect
        changed lookup pattern

        As commands requiring LOOKUP in reply_patterns are rejected if no lookup is
        present at startup, creation of new lookups is pointless as no command would
        be able to access those.
        """
        if not isinstance(table, dict):
            self.logger.warning(f'lookup table {name} not in dict format, aborting')
            return

        if not self._create_lookup_tables(name, table):
            return

        for cmd in self._commands:
            cmd_dict = self._commands[cmd]._cmd_params[CMD_ATTR_ORG_PARAMS]
            if any('{LOOKUP}' in pat for pat in cmd_dict.get(CMD_ATTR_REPLY_PATTERN, [])):
                patterns = self._parse_command_reply_patterns(cmd_dict[CMD_ATTR_REPLY_PATTERN], cmd_dict)
                setattr(self._commands[cmd], CMD_ATTR_REPLY_PATTERN, patterns)

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
        def _enum_dt_cls(mod, custom=False):
            classes = [cls for cls in dir(mod) if cls[:3] == 'DT_']
            for cls in classes:
                self._dt[cls] = getattr(mod, cls)
                if custom:
                    self._cust_dt[cls] = getattr(mod, cls)

        self._dt['Datatype'] = DT.Datatype

        # enumerate 'DT_*' classes from DT
        _enum_dt_cls(DT)

        # try to load datatypes.py from device directory
        mod_str = self._params[PLUGIN_PATH] + '.datatypes'
        cust_mod = locate(mod_str)
        if cust_mod:
            _enum_dt_cls(cust_mod, True)

    def _flatten_cmds(self, cmds):
        def walk(node, node_name, parent=None, func=None):
            for child in list(k for k in node.keys() if isinstance(node[k], dict)):
                walk(node[child], child, parent=node, func=func)
            if func:
                func(node, node_name, parent=parent)

        def move_items(node, node_name, parent):
            # make sure we can move "upwards"
            if parent:
                # if node[CMD_ATTR_OPCODE] is not present, node is not a command
                if CMD_ATTR_ITEM_TYPE not in node:
                    for child in list(k for k in node.keys() if isinstance(node[k], dict)):
                        # node has dict elements node[child]
                        parent[node_name + COMMAND_SEP + child] = node[child]
                        del node[child]

        def remove_empty_items(node, node_name, parent):
            if len(node) == 0:
                del parent[node_name]

        # flatten cmds
        walk(cmds, '', None, move_items)
        # remove empty dicts (old 'level names')
        walk(cmds, '', None, remove_empty_items)

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
                    raise CommandsError('model configuration invalid, "models" is not a dict')
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

    def _parse_command_reply_patterns(self, reply_patterns: list, cmd_dict: dict) -> list:
        """ parse command's reply patterns and return parsed patterns as list """
        def get_param(matchobj):
            returnvalue = self._params.get(matchobj.group(2))
            if returnvalue is None:
                self.logger.warning(f'Parameter {matchobj.group(2)} does not exist.')
                returnvalue = ''
            return str(returnvalue)

        custom_patterns = self._params.get('custom_patterns')

        processed_patterns = []

        for pattern in reply_patterns:

            if pattern == '*':
                pattern = cmd_dict.get(CMD_ATTR_READ_CMD, cmd_dict.get(CMD_ATTR_OPCODE, ''))

            if custom_patterns and PATTERN_CUSTOM_PATTERN in pattern:
                for index in (1, 2, 3):
                    pattern = pattern.replace('{' + PATTERN_CUSTOM_PATTERN + str(index) + '}', custom_patterns[index])

            if CMD_STR_PARAM in pattern:
                regex = r'(\{' + CMD_STR_PARAM + r'([^}]+)\})'
                while re.search(regex, pattern):
                    pattern = re.sub(regex, get_param, pattern)

            if cmd_dict.get(CMD_ATTR_LOOKUP) and '{' + PATTERN_LOOKUP + '}' in pattern:

                lu_pattern = '(' + '|'.join(re.escape(key) for key in self._lookups[cmd_dict[CMD_ATTR_LOOKUP]]['fwd'].keys()) + ')'
                pattern = pattern.replace('{' + PATTERN_LOOKUP + '}', lu_pattern)

            if cmd_dict.get(CMD_ATTR_CMD_SETTINGS) and 'valid_list' in cmd_dict[CMD_ATTR_CMD_SETTINGS] and '{' + PATTERN_VALID_LIST + '}' in pattern:

                vl_pattern = '(' + '|'.join(re.escape(key) for key in cmd_dict[CMD_ATTR_CMD_SETTINGS]['valid_list']) + ')'
                pattern = pattern.replace('{' + PATTERN_VALID_LIST + '}', vl_pattern)

            if cmd_dict.get(CMD_ATTR_CMD_SETTINGS) and 'valid_list_ci' in cmd_dict[CMD_ATTR_CMD_SETTINGS] and '{' + PATTERN_VALID_LIST_CI + '}' in pattern:

                vl_pattern = '((?i:' + '|'.join(re.escape(key) for key in cmd_dict[CMD_ATTR_CMD_SETTINGS]['valid_list_ci']) + '))'
                pattern = pattern.replace('{' + PATTERN_VALID_LIST_CI + '}', vl_pattern)

            if cmd_dict.get(CMD_ATTR_CMD_SETTINGS) and 'valid_list_re' in cmd_dict[CMD_ATTR_CMD_SETTINGS] and '{' + PATTERN_VALID_LIST_RE + '}' in pattern:

                vl_pattern = '(' + '|'.join(cmd_dict[CMD_ATTR_CMD_SETTINGS]['valid_list_re']) + ')'
                pattern = pattern.replace('{' + PATTERN_VALID_LIST_RE + '}', vl_pattern)

            processed_patterns.append(pattern)

        return processed_patterns

    def _parse_commands(self, commands, cmds=None):
        """
        This is a reference implementation for parsing the commands dict imported
        from the commands.py file in the device subdirectory.
        For special purposes, this can be overwritten, if you want to use your
        own file format.
        """
        if not cmds:
            cmds = []

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
            if cmd == CMD_ATTR_ITEM_ATTRS:
                continue

            cmd_dict = commands[cmd]

            # preset default values
            cmd_params = {CMD_ATTR_READ: True, CMD_ATTR_WRITE: False, CMD_ATTR_OPCODE: '', CMD_ATTR_ITEM_TYPE: 'bool', CMD_ATTR_DEV_TYPE: 'raw'}

            # sanitize patterns if not stored as list
            if CMD_ATTR_REPLY_PATTERN in cmd_dict and not isinstance(cmd_dict[CMD_ATTR_REPLY_PATTERN], list):
                # reply_pattern can be supplied as list or str, so don't warn...
                # self.logger.warning(f'error reading commands.py: for {cmd}, reply_patterns should be a list, is {type(cmd_dict[CMD_ATTR_REPLY_PATTERN])}. Please fix.')
                cmd_dict[CMD_ATTR_REPLY_PATTERN] = [cmd_dict[CMD_ATTR_REPLY_PATTERN]]

            # update with command attributes
            cmd_params.update({arg: cmd_dict[arg] for arg in COMMAND_PARAMS if arg in cmd_dict})

            # store original config for later parsing
            cmd_params[CMD_ATTR_ORG_PARAMS] = deepcopy(cmd_dict)

            # if valid_list_ci is present in settings, convert all str elements to lowercase only once
            if CMD_ATTR_CMD_SETTINGS in cmd_params and 'valid_list_ci' in cmd_params[CMD_ATTR_CMD_SETTINGS]:
                cmd_params[CMD_ATTR_CMD_SETTINGS]['valid_list_ci'] = [entry.lower() if isinstance(entry, str) else entry for entry in cmd_params[CMD_ATTR_CMD_SETTINGS]['valid_list_ci']]

            # if valid_list_re is present in settings, compile all patterns for later reuse
            if CMD_ATTR_CMD_SETTINGS in cmd_params and 'valid_list_re' in cmd_params[CMD_ATTR_CMD_SETTINGS]:
                cmd_params[CMD_ATTR_CMD_SETTINGS]['valid_list_re_compiled'] = [re.compile(entry) for entry in cmd_params[CMD_ATTR_CMD_SETTINGS]['valid_list_re']]

            dt_class = None
            dev_datatype = cmd_params.get(CMD_ATTR_DEV_TYPE, '')
            if dev_datatype:
                class_name = '' if dev_datatype[:2] == 'DT_' else 'DT_' + dev_datatype
                dt_class = self._dt.get(class_name)

            # process pattern substitution
            if CMD_ATTR_REPLY_PATTERN in cmd_params:

                # store processed reply patterns
                cmd_params[CMD_ATTR_REPLY_PATTERN] = self._parse_command_reply_patterns(cmd_params[CMD_ATTR_REPLY_PATTERN], cmd_dict)

            if cmd_params.get(CMD_ATTR_READ, False) and cmd_params.get(CMD_ATTR_OPCODE, '') == '' and cmd_params.get(CMD_ATTR_READ_CMD, '') == '':
                self.logger.info(f'command {cmd} will not create a command for reading values. Check commands.py configuration...')
            if cmd_params.get(CMD_ATTR_WRITE, False) and cmd_params.get(CMD_ATTR_OPCODE, '') == '' and cmd_params.get(CMD_ATTR_WRITE_CMD, '') == '':
                self.logger.info(f'command {cmd} will not create a command for writing values. Check commands.py configuration...')
            if not dt_class:
                self.logger.error(f'importing command {cmd} found invalid datatype "{dev_datatype}", replacing with DT_raw. Check function of device')
                dt_class = DT.DT_raw
            self._commands[cmd] = self._cmd_class(cmd, dt_class, **{'cmd': cmd_params, 'plugin': self._params})

            # store in self.parsed_commands for access by webif
            # skip sections only including section settings
            if not cmd.endswith('.' + CMD_ATTR_ITEM_ATTRS):
                self._parsed_commands[cmd] = cmd_params

    def _create_lookup_tables(self, name, table) -> bool:
        """ create and store all partial lookup tables for the given one """
        if isinstance(table, dict):

            try:
                self._lookups[name] = {
                    # original dict
                    'fwd': table,
                    # reversed dict
                    'rev': {v: k for (k, v) in table.items()},
                    # reversed dict, keys are lowercase for case insensitive lookup
                    'rci': {v.lower() if isinstance(v, str) else v: k for (k, v) in table.items()}
                }
            except Exception as e:
                self.logger.warning(f'error while converting lookup table {name}: {e}')
                return False

            self.logger.debug(f'imported lookup table {name} with {len(table)} items')
            return True
        else:
            self.logger.warning(f'key {name} in lookups not in dict format, ignoring')
            return False

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
                if self._create_lookup_tables(table, lu[table]):
                    if table not in self._lookup_tables:
                        self._lookup_tables.append(table)
                elif table in self._lookup_tables:
                    self._lookup_tables.remove(table)

        except Exception as e:
            self.logger.error(f'importing lookup tables not possible, check syntax. Error was: {e}')
