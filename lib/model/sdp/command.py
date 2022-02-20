#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SDPCommand and derived classes for SmartDevicePlugin class
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

from lib.model.sdp.globals import (CMD_ATTR_PARAMS, CMD_STR_VAL_RAW, CMD_STR_VAL_UPP, CMD_STR_VAL_LOW, CMD_STR_VAL_CAP, CMD_STR_VALUE, CMD_STR_OPCODE, CMD_STR_PARAM, CMD_STR_CUSTOM, COMMAND_PARAMS, MINMAXKEYS)
import lib.model.sdp.datatypes as DT


#############################################################################################################################################################################################################################################
#
# class SDPCommand
#
#############################################################################################################################################################################################################################################

class SDPCommand(object):
    """ SDPCommand class for command data handling

    This class represents a general command that uses read_cmd/write_cmd or, if
    not present, opcode as payload for the connection. Data is supplied in the
    'data'-key values in the data_dict. DT type conversion is applied with default
    values.

    For attributes defined in commands.py, see explanation in the
    dev_example/commands.py file.

    This class serves as a base class for further format-specific command types.
    """
    name = ''
    opcode = ''
    read = False
    write = False
    read_cmd = None
    write_cmd = None
    item_type = None
    reply_token = []
    reply_pattern = ''
    cmd_settings = None
    lookup = None
    _DT = None

    def __init__(self, command, dt_class, **kwargs):

        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)

        if not command:
            self.logger.warning('building command without a name, aborting')
            return
        else:
            self.name = command

        kw = kwargs['cmd']
        self._plugin_params = kwargs['plugin']

        self._get_kwargs(COMMAND_PARAMS, **kw)

        try:
            self._DT = dt_class()
        except Exception as e:
            self.logger.error(f'building command {command} failed on instantiating datatype class {dt_class}. Error was: {e}')
            self._DT = DT.DT_raw()

        # only log if base class. Derived classes log their own messages
        if self.__class__ is SDPCommand:
            self.logger.debug(f'learned command {command} with device datatype {dt_class} in {self.__class__.__name__}')

    def get_send_data(self, data, **kwargs):

        cmd = None

        data = self._check_value(data)

        # create read data
        if data is None:
            if self.read_cmd:
                cmd = self.read_cmd
            else:
                cmd = self.opcode
        else:
            if self.write_cmd:
                cmd = self.write_cmd
            else:
                cmd = self.opcode

        return {'payload': cmd, 'data': self._DT.get_send_data(data)}

    def get_shng_data(self, data, **kwargs):
        value = self._DT.get_shng_data(data, **kwargs)
        return value

    def get_lookup(self):
        """ getter for lookup """
        return self.lookup

    def _get_kwargs(self, args, **kwargs):
        """
        check if any items from args is present in kwargs and set the class property
        of the same name to its value.

        :param args: list or tuple of parameter names
        :type args: list | tuple
        """
        for arg in args:
            if kwargs.get(arg, None):
                setattr(self, arg, kwargs[arg])

    def _check_min_max(self, data, key, min=True, force=False):
        """ helper routine to check for min/max compliance and int/float type """
        if key in self.cmd_settings:
            bound = self.cmd_settings[key]
            if not isinstance(data, type(bound)):
                if type(data) is float and type(bound) is int:
                    data = int(data)
                elif type(data) is int and type(bound) is float:
                    data = float(data)
                else:
                    raise ValueError(f'type {type(data)} ({data}) given for {type(bound)} ({bound})')
            if (min and data >= bound) or (not min and data <= bound):
                return data
            if force:
                self.logger.debug(f'Value {data} changed to {bound} due to cmd_settings {self.cmd_settings}')
                return bound
            raise ValueError(f'value {data} not adhering to {"min" if min else "max"} value {bound}')
        return data

    def _check_value(self, data):
        """
        check if value settings are defined and if so, if they are followed
        possibly adjust data in accordance with settings

        non-compliance will raise ValueError

        This can be overwritten; make sure to call
        data = super()._check_value(data)
        to run this code in addition to your own extension, if applicable.
        Take care of the sequence of changing data, though...

        :param data: data/value to send
        :return: adjusted data
        """
        if data is not None:
            try:
                if self.cmd_settings and not self.lookup:
                    if self.cmd_settings.get('valid_list_ci', None):
                        val = data
                        if isinstance(data, str):
                            val = data.lower()
                        if val not in self.cmd_settings['valid_list_ci']:
                            raise ValueError(f'value {val} not in case insensitive list {self.cmd_settings["valid_list_ci"]}')
                    elif self.cmd_settings.get('valid_list', None):
                        if data not in self.cmd_settings['valid_list']:
                            raise ValueError(f'value {data} not in list {self.cmd_settings["valid_list"]}')
                    # min/max not in addition to valid_list
                    elif any(key in self.cmd_settings.keys() for key in MINMAXKEYS):
                        for key in MINMAXKEYS:
                            data = self._check_min_max(data, key, key[-3:] == 'min', key[:5] == 'force')

            except Exception as e:
                raise ValueError(f'Given invalid value for command {self.name} due to settings. Error was: {e}')

        return data


class SDPCommandStr(SDPCommand):
    """ Command for string-based communication

    This class represents a command which uses a string with arguments as payload,
    for example as query URL.

    Default behaviour is identical to SDPCommand.

    For sending, the read_cmd/write_cmd strings, opcode and data are parsed
    (recursively), to enable the following parameters:

    - '{OPCODE}' is replaced with the opcode,
    - '{PARAM:attr}' is replaced with the value of the attr element from the plugin configuration,
    - '{VALUE}' is replaced with the given value (converted by DT-class)
    - '{CUSTOM_ATTR1}'..'{CUSTOM_ATTR3}' is replaced by the respective custom attribute

    The returned data is only parsed by the DT_... classes.
    For the DT_json class, the read_data dict can be used to extract a specific
    element from a json response:

    ``read_data = {'dict': ['key1', 'key2', 'key3']}``

    would try to get

    ``json_response['key1']['key2']['key3']``

    and return it as the read value.

    This class is provided as a reference implementation for the Net-Connections.
    """
    read_data = None

    def get_send_data(self, data, **kwargs):

        self._plugin_params.update(kwargs)
        data = self._check_value(data)

        if data is None:
            # create read data
            if self.read_cmd:
                cmd_str = self._parse_str(self.read_cmd, data, **kwargs)
            else:
                cmd_str = self._parse_str(self.opcode, data, **kwargs)
        else:
            # create write data
            if self.write_cmd:
                cmd_str = self._parse_str(self.write_cmd, data, **kwargs)
            else:
                cmd_str = self._parse_str(self.opcode, data, **kwargs)

        data_dict = {}
        data_dict['payload'] = cmd_str
        for k in self._plugin_params.keys():
            data_dict[k] = self._parse_tree(self.params[k], data, **kwargs)

        return data_dict

    def get_shng_data(self, data, **kwargs):
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')
        value = self._DT.get_shng_data(data, **kwargs)
        return value

    def _parse_str(self, string, data=None, **kwargs):
        """
        parse string and replace
        - ``{OPCODE}`` with the command opcode
        - ``{PARAM:<elem>}`` with the plugin parameter
        - ``{VALUE}`` with the data value
        - ``{CUSTOM_ATTR[123]}`` with the respective custom token value

        The replacement order ensures that PARAM-patterns from the opcode
        can be replaced as well as VALUE-pattern in any of the strings.
        """
        def repl_func(matchobj):
            return str(self._plugin_params.get(matchobj.group(2), ''))

        def cust_func(matchobj):
            if kwargs and 'custom' in kwargs:
                return str(kwargs['custom'].get(int(matchobj.group(2))))
            return ''

        string = string.replace('{' + CMD_STR_OPCODE + '}', self.opcode)

        regex = r'(\{' + CMD_STR_PARAM + r'([^}]+)\})'
        while re.match('.*' + regex + '.*', string):
            string = re.sub(regex, repl_func, string)

        regex = r'(\{' + CMD_STR_CUSTOM + r'([123])\})'
        while re.match('.*' + regex + '.*', string):
            string = re.sub(regex, cust_func, string)

        # if kwargs and ITEM_ATTR_CUSTOM_PREFIX in kwargs:
        #     regex = '(MD_CUSTOM([123]))'
        #     while re.match('.*' + regex + '.*', string):
        #         index = int(re.match(regex, string).group(2))
        #         if index in kwargs[ITEM_ATTR_CUSTOM_PREFIX]:
        #             string = re.sub(regex, kwargs[ITEM_ATTR_CUSTOM_PREFIX][index], string)

        if data is not None:
            string = string.replace('{' + CMD_STR_VALUE + '}', str(self._DT.get_send_data(data)))

        return string

    def _parse_tree(self, node, data, **kwargs):
        """
        traverse node and
        - apply _parse_str to strings
        - recursively _parse_tree for all elements of iterables or
        - return unknown or unparseable elements unchanged
        """
        if issubclass(node, str):
            return self._parse_str(node, data, **kwargs)
        elif issubclass(node, list):
            return [self._parse_tree(k, data, **kwargs) for k in node]
        elif issubclass(node, tuple):
            return (self._parse_tree(k, data, **kwargs) for k in node)
        elif issubclass(node, dict):
            new_dict = {}
            for k in node.keys():
                new_dict[k] = self._parse_tree(node[k], data, **kwargs)
            return new_dict
        else:
            return node


class SDPCommandParseStr(SDPCommandStr):
    """ Command for string-based communication with parsed arguments

    With this class, you can simplify the creation of read and write commands
    containing data values.

    Default behaviour is identical to SDPCommandStr.

    opcode, write_cmd and read_cmd will be parsed to substitute values.
    write_cmd will be formatted, replacing ``{RAW_VALUE}`` with the value by
    using write_cmd.format(RAW_VALUE=data_dict['payload']), so you can
    immediately embed the value in the command string with configurable
    formatting conforming to str.format() syntax.
    Analogous to ``RAW_VALUE``, you can also use ``RAW_VALUE_UPPER``,
    ``RAW_VALUE_LOWER`` and ``RAW_VALUE_CAP`` for string values.

    Giving reply_pattern as '<regex>' with one (1) match group will try and
    capture the matched group into the received value.

    Giving reply_pattern as '<regex>' without capturing parentheses will return
    the reply value as is (can possibly be converted by the DT class).

    HINT: If you give reply_pattern as regex, the reply_pattern regex will be
    used to identify a reply as belonging to this command if a match is found.

    If the reply_pattern contains ``{LOOKUP}`` and lookup is set to a valid
    lookup table, the '{MD_LOOKUP}' identifier is replaced with a regex which
    triggers on any of the possible lookup values.
    The same applies for ``{VALID_LIST}`` and ``{VALID_LIST_CI}`` for the
    respective valid_lists from the command settings; including one of 
    ``{CUSTOM_PATTERN1}``...``{CUSTOM_PATTERN3}`` will replace these with the
    respective custom pattern from the device class.

    Some results can be achieved with customized DT_foo classes, but this
    might be an easier and cleaner solution. Please make sure to understand
    MRE by JF properly :)
    """

    def get_send_data(self, data, **kwargs):

        self._plugin_params.update(kwargs)
        data = self._check_value(data)

        if data is None:
            # create read data
            if self.read_cmd:
                cmd_str = self._parse_str(self.read_cmd, data, **kwargs)
            else:
                cmd_str = self._parse_str(self.opcode, data, **kwargs)
        else:
            # create write data
            if self.write_cmd:
                cmd = self._parse_str(self.write_cmd, data, **kwargs)
            else:
                cmd = self._parse_str(self.opcode, data, **kwargs)

            # apply substitutions
            if isinstance(data, str):
                d = {CMD_STR_VAL_RAW: data,
                     CMD_STR_VAL_UPP: data.upper(),
                     CMD_STR_VAL_LOW: data.lower(),
                     CMD_STR_VAL_CAP: data.capitalize()}
                cmd_str = self._parse_str(cmd.format(**d), data)
            else:
                d = {CMD_STR_VAL_RAW: data}
                cmd_str = self._parse_str(cmd.format(**d), data)

        return {'payload': cmd_str, 'data': None if data is None else self._DT.get_send_data(data)}

    def get_shng_data(self, data, **kwargs):
        """
        Try to match data to reply_pattern if reply_pattern is set.

        If a match is found and a value is captured, it will be returned.

        If a match is found without a capturing group, the value will be
        returned as-is, possibly to be converted by the DT class.

        If no match can be achieved, it is not possible to return
        a meaningful value. To signal the error, an exception will be raised.
        """
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')

        self.logger.debug(f'parse_str command got data {data} of type {type(data)}')

        if self.reply_pattern and isinstance(data, str):
            for pattern in self.reply_pattern:
                regex = re.compile(pattern)
                match = regex.search(data)
                if match:
                    if len(match.groups()) == 1:

                        # one captured group - ok
                        value = self._DT.get_shng_data(match.group(1), **kwargs)
                        break
                    elif len(match.groups()) > 1:

                        # more than one captured group - error
                        raise ValueError(f'reply_pattern {self.reply_pattern} has more than one pair of capturing parentheses')
                    else:

                        # no captured groups = no parentheses = no extraction of value, just do the "normal" thing
                        value = self._DT.get_shng_data(data, **kwargs)
                else:
                    raise ValueError(f'reply_pattern {self.reply_pattern} could not get a match on {data}')
        else:
            value = self._DT.get_shng_data(data, **kwargs)
        return value


class SDPCommandJSON(SDPCommand):
    """ Command for JSON-RPC communication

    With this class, you can send JSON-RPC commands to the device and read
    from it.

    The command is sent as JSON-RPC 'method', the params-dict is populated from
    the CMD_ATTR_PARAMS attribute of the command. '{VALUE}' (CMD_STR_VAL) is
    replaced with the actual item value.

    Giving 'playerid' in kwargs replaces a dict entry with the key of 'playerid'
    or a list entry of '{ID}' with the value of kwargs['playerid'].

    params needs to be None or a dict.
    """

    def get_send_data(self, data, **kwargs):

        cmd = None
        data = self._check_value(data)
        # create read data
        if data is None:
            if self.read_cmd:
                cmd = self.read_cmd
            else:
                cmd = self.opcode
        else:
            if self.write_cmd:
                cmd = self.write_cmd
            else:
                cmd = self.opcode
        ddict = self._build_dict(self._DT.get_send_data(data), **kwargs)
        return {'payload': cmd, 'data': ddict}

    def get_shng_data(self, data, **kwargs):
        value = self._DT.get_shng_data(data.get('result'), **kwargs)
        return value

    def _build_dict(self, data, **kwargs):
        """
        build param array for JSON RPC from provided value and kwargs

        :param data: value for the command
        :param kwargs: additional data
        :return: params-dict (or None)
        :rtype: dict
        """
        def check_value(val, data):

            if isinstance(val, list):
                # recursively check list
                for idx in range(len(val)):
                    val[idx] = check_value(val[idx], data)
            elif val == '{' + CMD_STR_VALUE + '}':
                val = data
            elif 'custom' in kwargs and isinstance(val, str) and re.match(r'^\{CUSTOM_ATTR[123]\}$', val):
                idx = re.match(r'^\{CUSTOM_ATTR([123])\}$', val)
                if idx and (1 <= int(idx[1]) <= 3):
                    val = kwargs['custom'][int(idx[1])]
            elif isinstance(val, tuple):
                try:
                    expr = str(val[0]).replace('{' + CMD_STR_VALUE + '}', str(data))
                    val = eval(expr)
                except Exception as e:
                    raise ValueError(f'invalid data: eval expression {val} with argument {data} raised error: {e}')

            return val

        if not hasattr(self, CMD_ATTR_PARAMS):
            return None

        params = deepcopy(self.params)

        if isinstance(params, list):

            # unnamed parameters, list format
            for i in range(len(params)):
                params[i] = check_value(params[i], data)

                if params[i] == '{ID}' and 'playerid' in kwargs:
                    params[i] = kwargs['playerid']

        elif isinstance(params, dict):

            # named parameters, dict format
            for key in params:
                params[key] = check_value(params[key], data)

            if 'playerid' in params and 'playerid' in kwargs:
                params['playerid'] = kwargs['playerid']
        else:
            raise ValueError('invalid data: params not in dict or list format')

        return params


class SDPCommandViessmann(SDPCommand):
    """ Command for Viessmann binary command format

    With this class, you can send commands to Viessmann heating systems

    The command is sent as 'method', the params-dict is populated from the
    CMD_ATTR_PARAMS attribute of the command, while the parameter values are
    taken from the CMD_ATTR_PARAM_VALUES attribute. 'VAL' is replaced with the
    actual item value.

    params and param_value need to be None or lists of the same length.
    """
    def __init__(self, command, dt_class, **kwargs):
        super().__init__(command, dt_class, **kwargs)

        self._len = 1
        self._mult = 0
        self._signed = False
        for attr in ('len', 'mult', 'signed'):
            if attr in self.params:
                setattr(self, '_' + attr, self.params[attr])

    def get_send_data(self, data, **kwargs):

        data = self._check_value(data)
        # create read data
        if data is None:
            if self.read_cmd:
                cmd = self.read_cmd
            else:
                cmd = self.opcode
        else:
            if self.write_cmd:
                cmd = self.write_cmd
            else:
                cmd = self.opcode

        ddict = self._build_dict(self._DT.get_send_data(data, len=self._len, mult=self._mult, signed=self._signed), **kwargs)
        return {'payload': cmd, 'data': ddict}

    def _build_dict(self, data, **kwargs):
        """
        build param array for JSON RPC from provided value and kwargs

        :param data: value for the command
        :param kwargs: additional data
        :return: params-dict (or None)
        :rtype: dict
        """
        params = {}
        if not hasattr(self, CMD_ATTR_PARAMS):
            return None

        for key in self.params:
            val = self.params[key]
            if val == 'VAL':
                val = data
            elif isinstance(val, tuple):
                try:
                    expr = str(val[0]).replace('VAL', str(data))
                    val = eval(expr)
                except Exception as e:
                    raise ValueError(f'invalid data: eval expression {val} with argument {data} raised error: {e}')

            params[key] = val

        return params
