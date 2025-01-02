#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Globals for SmartDevicePlugin class
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

""" Global definitions of constants and functions for SmartDevicePlugin """

from lib.utils import Utils
from ast import literal_eval
from collections import abc
import types

#############################################################################################################################################################################################################################################
#
# global constants used to configure plugin, device, connection and items
#
# do not change if not absolutely sure about the consequences!
#
#############################################################################################################################################################################################################################################

# this is the internal SDP version
SDP_VERSION = '1.0.4'

# plugin attributes, used in plugin config 'device' and instance creation (**kwargs)

# general attributes
PLUGIN_ATTR_MODEL            = 'model'                   # select model if applicable. Don't set if not necessary!
PLUGIN_ATTR_CMD_CLASS        = 'command_class'           # name of class to use for commands
PLUGIN_ATTR_RECURSIVE        = 'recursive_custom'        # indices of custom item attributes for which to enable recursive lookup (number or list of numbers)
PLUGIN_ATTR_SUSPEND_ITEM     = 'suspend_item'            # item to toggle suspend/resume mode
PLUGIN_ATTR_CYCLE            = 'cycle'                   # plugin-wide cyclic update interval
PLUGIN_ATTR_DELAY_INITIAL    = 'delay_initial_read'      # delay reading of initial commands
PLUGIN_ATTR_REREAD_INITIAL   = 'resume_initial_read'     # repeat initial read on resume

# general connection attributes
PLUGIN_ATTR_CONNECTION       = 'conn_type'               # manually set connection class, classname or type (see below)
PLUGIN_ATTR_CONN_TIMEOUT     = 'timeout'                 # timeout for reading from network or serial
PLUGIN_ATTR_CONN_TERMINATOR  = 'terminator'              # terminator for reading from network or serial
PLUGIN_ATTR_CONN_BINARY      = 'binary'                  # tell connection to handle data for binary parsing
PLUGIN_ATTR_CONN_RETRIES     = 'connect_retries'         # how often to try connecting (a "round")
PLUGIN_ATTR_CONN_CYCLE       = 'connect_cycle'           # how long to wait between attempts
PLUGIN_ATTR_CONN_AUTO_RECONN = 'autoreconnect'           # (re)connect automatically on disconnect or failed connection cycle
PLUGIN_ATTR_CONN_AUTO_CONN   = 'autoconnect'             # (re)connect automatically on send
PLUGIN_ATTR_CONN_RETRY_CYCLE = 'retry_cycle'             # if autoreconnect: how many seconds to wait between retry rounds
PLUGIN_ATTR_CONN_RETRY_SUSPD = 'retry_suspend'           # after this number of failed connect cycles, activate suspend mode (if enabled)

# network attributes
PLUGIN_ATTR_NET_HOST         = 'host'                    # hostname / IP for network connection
PLUGIN_ATTR_NET_PORT         = 'port'                    # port for network connection

# serial attributes
PLUGIN_ATTR_SERIAL_PORT      = 'serialport'              # serial port for serial connection
PLUGIN_ATTR_SERIAL_BAUD      = 'baudrate'                # baudrate for serial connection
PLUGIN_ATTR_SERIAL_BSIZE     = 'bytesize'                # bytesize for serial connection
PLUGIN_ATTR_SERIAL_PARITY    = 'parity'                  # parity for serial connection
PLUGIN_ATTR_SERIAL_STOP      = 'stopbits'                # stopbits for serial connection

# protocol attributes
PLUGIN_ATTR_PROTOCOL         = 'protocol'                # manually choose protocol class, classname or type (see below). Don't set if not necessary!
PLUGIN_ATTR_SEND_RETRIES     = 'send_retries'            # how often should a command be resent when not receiving expected answer (JSON-RPC/resend protocols only)
PLUGIN_ATTR_SEND_RETRY_CYCLE = 'send_retries_cycle'      # if using resend protocol: how many seconds to wait between resend rounds (JSON-RPC/resend protocols only)
PLUGIN_ATTR_SEND_TIMEOUT     = 'send_retries_timeout'    # how many seconds to wait for reply to command? (JSON-RPC/resend protocols only)

# callback functions, not in plugin.yaml
PLUGIN_ATTR_CB_ON_CONNECT    = 'connected_callback'      # callback function, called if connection is established
PLUGIN_ATTR_CB_ON_DISCONNECT = 'disconnected_callback'   # callback function, called if connection is lost
PLUGIN_ATTR_CB_SUSPEND       = 'suspend_callback'        # callback function, called if connection attempts are aborted

PLUGIN_ATTRS = (PLUGIN_ATTR_MODEL, PLUGIN_ATTR_CMD_CLASS, PLUGIN_ATTR_RECURSIVE, PLUGIN_ATTR_CYCLE,
                PLUGIN_ATTR_SUSPEND_ITEM, PLUGIN_ATTR_CONNECTION, PLUGIN_ATTR_DELAY_INITIAL, PLUGIN_ATTR_REREAD_INITIAL,
                PLUGIN_ATTR_CONN_TIMEOUT, PLUGIN_ATTR_CONN_TERMINATOR, PLUGIN_ATTR_CONN_BINARY,
                PLUGIN_ATTR_CONN_RETRIES, PLUGIN_ATTR_CONN_CYCLE, PLUGIN_ATTR_CONN_AUTO_RECONN, PLUGIN_ATTR_CONN_AUTO_CONN,
                PLUGIN_ATTR_CONN_RETRY_CYCLE, PLUGIN_ATTR_CONN_RETRY_SUSPD, PLUGIN_ATTR_NET_HOST, PLUGIN_ATTR_NET_PORT,
                PLUGIN_ATTR_SERIAL_PORT, PLUGIN_ATTR_SERIAL_BAUD, PLUGIN_ATTR_SERIAL_BSIZE, PLUGIN_ATTR_SERIAL_PARITY,
                PLUGIN_ATTR_SERIAL_STOP, PLUGIN_ATTR_PROTOCOL, 
                PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_ON_DISCONNECT, PLUGIN_ATTR_CB_SUSPEND,
                PLUGIN_ATTR_SEND_RETRIES, PLUGIN_ATTR_SEND_RETRY_CYCLE, PLUGIN_ATTR_SEND_TIMEOUT)

# connection types for PLUGIN_ATTR_CONNECTION
CONN_NULL                    = ''                 # use base connection class without real connection functionality, for testing
CONN_NET_TCP_REQ             = 'net_tcp_request'  # TCP client connection with URL-based requests
CONN_NET_TCP_CLI             = 'net_tcp_client'   # persistent TCP client connection with async callback for responses
CONN_NET_TCP_JSONRPC         = 'net_tcp_jsonrpc'  # JSON RPC via persistent TCP client connection with async callback for responses
CONN_NET_UDP_SRV             = 'net_udp_server'   # UDP server connection with async data callback
CONN_SER_DIR                 = 'serial'           # serial connection with query-reply logic
CONN_SER_ASYNC               = 'serial_async'     # serial connection with only async data callback

CONNECTION_TYPES = (CONN_NULL, CONN_NET_TCP_REQ, CONN_NET_TCP_CLI, CONN_NET_TCP_JSONRPC, CONN_NET_UDP_SRV, CONN_SER_DIR, CONN_SER_ASYNC)

# protocol types for PLUGIN_ATTR_PROTOCOL
PROTO_NULL                   = ''                 # use base protocol class without added functionality (why??)
PROTO_JSONRPC                = 'jsonrpc'          # JSON-RPC 2.0 support with send queue, msgid and resend of unanswered commands
PROTO_VIESSMANN              = 'viessmann'        # Viessmann P300 / KW
PROTO_RESEND                 = 'resend'           # protocol implementing resending commands which are not answered (in time)

PROTOCOL_TYPES = (PROTO_NULL, PROTO_JSONRPC, PROTO_VIESSMANN, PROTO_RESEND)

# item attribute suffixes (as defined with individual prefix in plugin.yaml)
ITEM_ATTR_COMMAND            = '_command'             # command to issue/read for the item
ITEM_ATTR_READ               = '_read'                # command can be triggered for reading
ITEM_ATTR_CYCLIC             = '_read_cyclic'         # trigger cyclic reading using plugin-wide cycle setting
ITEM_ATTR_CYCLE              = '_read_cycle'          # trigger cyclic read every x seconds (item-specific)
ITEM_ATTR_READ_INIT          = '_read_initial'        # trigger read on initial connect
ITEM_ATTR_GROUP              = '_read_group'          # trigger read with read group <foo>
ITEM_ATTR_WRITE              = '_write'               # command can be called for writing values
ITEM_ATTR_READAFTERWRITE     = '_readafterwrite'      # after writing: read value from device after x seconds
ITEM_ATTR_READ_GRP           = '_read_group_trigger'  # item triggers reading of read group <foo>
ITEM_ATTR_LOOKUP             = '_lookup'              # create lookup item <item>.lookup
ITEM_ATTR_CUSTOM1            = '_custom1'             # custom attribute 1
ITEM_ATTR_CUSTOM2            = '_custom2'             # custom attribute 2
ITEM_ATTR_CUSTOM3            = '_custom3'             # custom attribute 3

ITEM_ATTRS = (ITEM_ATTR_COMMAND, ITEM_ATTR_READ, ITEM_ATTR_CYCLIC, ITEM_ATTR_CYCLE, ITEM_ATTR_READAFTERWRITE,
              ITEM_ATTR_READ_INIT, ITEM_ATTR_WRITE, ITEM_ATTR_READ_GRP, ITEM_ATTR_GROUP,
              ITEM_ATTR_LOOKUP, ITEM_ATTR_CUSTOM1, ITEM_ATTR_CUSTOM2, ITEM_ATTR_CUSTOM3)
ATTR_NAMES = ('ITEM_ATTR_COMMAND', 'ITEM_ATTR_READ', 'ITEM_ATTR_CYCLIC', 'ITEM_ATTR_CYCLE', 'ITEM_ATTR_READAFTERWRITE',
              'ITEM_ATTR_READ_INIT', 'ITEM_ATTR_GROUP', 'ITEM_ATTR_WRITE', 'ITEM_ATTR_READ_GRP',
              'ITEM_ATTR_LOOKUP', 'ITEM_ATTR_CUSTOM1', 'ITEM_ATTR_CUSTOM2', 'ITEM_ATTR_CUSTOM3')

# command definition
COMMAND_READ                 = True                     # used internally
COMMAND_WRITE                = False                    # used internally
COMMAND_SEP                  = '.'                      # divider for command path items
CUSTOM_SEP                   = '#'                      # divider for command and custom token

# command definition attributes
CMD_ATTR_OPCODE              = 'opcode'                 # code or string to send to device
CMD_ATTR_READ                = 'read'                   # command can request/receive value
CMD_ATTR_WRITE               = 'write'                  # command can set value
CMD_ATTR_ITEM_TYPE           = 'item_type'              # type of associated shng item
CMD_ATTR_DEV_TYPE            = 'dev_datatype'           # type of DT class for device
CMD_ATTR_READ_CMD            = 'read_cmd'               # code or string to send for reading (if different from opcode)
CMD_ATTR_WRITE_CMD           = 'write_cmd'              # code or string to send for writing (if different from opcode)
CMD_ATTR_REPLY_PATTERN       = 'reply_pattern'          # regex pattern(s) to identify reply and capture reply value
CMD_ATTR_CMD_SETTINGS        = 'cmd_settings'           # additional settings for command, e.g. data validity
CMD_ATTR_LOOKUP              = 'lookup'                 # use lookup table <foo> to translate between plugin and items
CMD_ATTR_PARAMS              = 'params'                 # parameters to send (e.g. in JSON-RPC)
CMD_ATTR_ITEM_ATTRS          = 'item_attrs'             # item attributes for struct generation (see below)
CMD_ATTR_CUSTOM_DISABLE      = 'custom_disabled'        # disable custom token detection for this command

CMD_ATTR_ORG_PARAMS          = 'org_cmd_dict'           # store original command configuration, internal use only!

CMD_IATTR_RG_LEVELS          = 'read_group_levels'      # include this number of read groups (max, 0=no read groups)
CMD_IATTR_LOOKUP_ITEM        = 'lookup_item'            # create lookup item <item>.lookup
CMD_IATTR_ATTRIBUTES         = 'attributes'             # additional item attributes (copy 1:1)
CMD_IATTR_READ_GROUPS        = 'read_groups'            # add custom read group(s) and read group trigger(s)
CMD_IATTR_ENFORCE            = 'enforce'                # add ``enforce_updates: true``
CMD_IATTR_INITIAL            = 'initial'                # add ``ex_read_initial: true``
CMD_IATTR_CYCLE              = 'cycle'                  # add ``ex_read_cycle: <val>`` (item-speficic cycle)
CMD_IATTR_CYCLIC             = 'cyclic'                 # add ``ex_read_cyclic: true`` (plugin-wide cycle)
CMD_IATTR_TEMPLATE           = 'item_template'          # add item template <foo>
CMD_IATTR_CUSTOM1            = 'custom1'                # add item-specific custom attribute 1
CMD_IATTR_CUSTOM2            = 'custom2'                # add item-specific custom attribute 2
CMD_IATTR_CUSTOM3            = 'custom3'                # add item-specific custom attribute 3

# commands definition parameters
COMMAND_PARAMS = (CMD_ATTR_OPCODE, CMD_ATTR_READ, CMD_ATTR_WRITE, CMD_ATTR_ITEM_TYPE, CMD_ATTR_DEV_TYPE,
                  CMD_ATTR_READ_CMD, CMD_ATTR_WRITE_CMD, CMD_ATTR_REPLY_PATTERN, CMD_ATTR_CMD_SETTINGS,
                  CMD_ATTR_LOOKUP, CMD_ATTR_PARAMS, CMD_ATTR_ITEM_ATTRS, CMD_ATTR_CUSTOM_DISABLE)

COMMAND_ITEM_ATTRS = (CMD_IATTR_RG_LEVELS, CMD_IATTR_LOOKUP_ITEM, CMD_IATTR_ATTRIBUTES, CMD_IATTR_TEMPLATE,
                      CMD_IATTR_READ_GROUPS, CMD_IATTR_CYCLE, CMD_IATTR_INITIAL, CMD_IATTR_ENFORCE,
                      CMD_IATTR_CUSTOM1, CMD_IATTR_CUSTOM2, CMD_IATTR_CUSTOM3, CMD_IATTR_CYCLIC)

# reply pattern substitution tokens, set token in {<token>}
PATTERN_LOOKUP               = 'LOOKUP'                 # replace with lookup values    
PATTERN_VALID_LIST           = 'VALID_LIST'             # replace with valid_list items
PATTERN_VALID_LIST_CI        = 'VALID_LIST_CI'          # replace with valid_list_ci items
PATTERN_VALID_LIST_RE        = 'VALID_LIST_RE'          # replace with valid_list_re patterns
PATTERN_CUSTOM_PATTERN       = 'CUSTOM_PATTERN'         # replace with custom pattern <x>

PATTERN_MARKERS = (PATTERN_LOOKUP, PATTERN_VALID_LIST, PATTERN_VALID_LIST_CI, PATTERN_VALID_LIST_RE, PATTERN_CUSTOM_PATTERN)

# command string substitution tokens, set token in {<token>}
CMD_STR_VAL_RAW              = 'RAW_VALUE'              # replace with raw value
CMD_STR_VAL_UPP              = 'RAW_VALUE_UPPER'        # replace with raw value uppercase (if string)
CMD_STR_VAL_LOW              = 'RAW_VALUE_LOWER'        # replace with raw value lowercase (if string)
CMD_STR_VAL_CAP              = 'RAW_VALUE_CAP'          # replace with raw value capitalized (if string)
CMD_STR_VALUE                = 'VALUE'                  # replace with DT converted value
CMD_STR_OPCODE               = 'OPCODE'                 # replace with opcode string/bytes
CMD_STR_PARAM                = 'PARAM:'                 # replace with kwargs[foo] (``{PARAM:foo}``)
CMD_STR_CUSTOM               = 'CUSTOM_ATTR'            # replace with value of custom attribute <x>

CMD_STRINGS = (CMD_STR_VAL_RAW, CMD_STR_VAL_UPP, CMD_STR_VAL_LOW, CMD_STR_VAL_CAP, CMD_STR_VALUE, CMD_STR_OPCODE, CMD_STR_PARAM, CMD_STR_CUSTOM)

# JSON keys to move from dict root to data.params
JSON_MOVE_KEYS               = 'json_move_keys'

# keys for min / max values for data bounds
MINMAXKEYS                   = ('valid_min', 'valid_max', 'force_min', 'force_max')

# name of non-model specific key for commands, models and lookups
INDEX_GENERIC                = 'ALL'                    # placeholder for generic data
INDEX_MODEL                  = 'MODEL'                  # placeholder for model-specific struct

# dict keys for request data_dict
REQUEST_DICT_ARGS = ('params', 'headers', 'data', 'cookies', 'files')

PLUGIN_PATH = 'plugin_path'                             # module path to the plugin class


#############################################################################################################################################################################################################################################
#
# Exceptions
#
#############################################################################################################################################################################################################################################

class CommandsError(Exception):
    pass


#############################################################################################################################################################################################################################################
#
# non-class functions
#
#############################################################################################################################################################################################################################################

def sanitize_param(val):
    """
    Try to correct type of val if val is string:
    - return int(val) if val is integer
    - return float(val) if val is float
    - return bool(val) is val follows conventions for bool
    - try if string can be converted to list, tuple or dict; do so if possible
    - return val unchanged otherwise

    :param val: value to sanitize
    :return: sanitized (or unchanged) value
    """
    if isinstance(val, (int, float, bool)) or isinstance(val, type) or type(val) == types.FunctionType:
        return val
    if Utils.is_int(str(val)):
        val = int(val)
    elif Utils.is_float(str(val)):
        val = float(val)
    elif isinstance(val, str) and val.lower() in ('true', 'false', 'on', 'off', 'yes', 'no'):
        val = Utils.to_bool(val)
    else:
        try:
            new = literal_eval(val)
            if type(new) in (list, dict, tuple):
                val = new
        except Exception:
            pass
    return val


def update(d, u):
    for k, v in u.items():
        if isinstance(v, abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
