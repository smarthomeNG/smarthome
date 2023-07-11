#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016-     Martin Sinn                          m.sinn@gmx.de
#  Copyright 2016      Christian Strassburg           c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
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

"""
This file describes a group of system wide constants for items, plugins and file extensions
"""

#item types
ITEM_TYPES=["num","str","bool", "list","dict","foo","scene"]
ITEM_DEFAULTS= __defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
FOO = 'foo'

#metadata types
META_DATA_TYPES=['bool', 'int', 'float', 'num', 'scene', 'str', 'password', 'list', 'dict', 'ip', 'ipv4', 'ipv6', 'mac', 'knx_ga', 'foo']
META_DATA_DEFAULTS={'bool': False, 'int': 0, 'float': 0.0, 'num': 0, 'scene': 0, 'str': '',  'password': '',
                    'list': [], 'dict': {}, 'OrderedDict': {},
                    'ip': '0.0.0.0', 'ipv4': '0.0.0.0', 'ipv6': '', 'mac': '00:00:00:00:00:00', 'knx_ga': '', 'foo': None}

#config params for items
KEY_ENFORCE_UPDATES = 'enforce_updates'
KEY_ENFORCE_CHANGE = 'enforce_change'
KEY_CACHE = 'cache'
KEY_CYCLE = 'cycle'
KEY_NAME = 'name'
KEY_DESCRIPTION = 'description'
KEY_TYPE = 'type'
KEY_VALUE = 'value'
KEY_INITVALUE = 'initial_value'
KEY_CRONTAB = 'crontab'
KEY_EVAL_TRIGGER = 'eval_trigger'
KEY_TRIGGER = 'trigger'
KEY_CONDITION = 'trigger_condition'
KEY_EVAL = 'eval'
KEY_THRESHOLD = 'threshold'
KEY_AUTOTIMER = 'autotimer'
KEY_ON_UPDATE = 'on_update'
KEY_ON_CHANGE = 'on_change'

KEY_LOG_CHANGE =  'log_change'
KEY_LOG_LEVEL =   'log_level'
KEY_LOG_TEXT =    'log_text'
KEY_LOG_MAPPING = 'log_mapping'
KEY_LOG_RULES =   'log_rules'

KEY_HYSTERESIS_INPUT = 'hysteresis_input'
KEY_HYSTERESIS_UPPER_THRESHOLD = 'hysteresis_upper_threshold'
KEY_HYSTERESIS_LOWER_THRESHOLD = 'hysteresis_lower_threshold'

ATTRIBUTE_SEPARATOR = ';'

KEY_STRUCT = 'struct'
KEY_REMARK = 'remark'

#global config params for plugins
KEY_INSTANCE =         'instance'
KEY_WEBIF_PAGELENGTH = 'webif_pagelength'
KEY_CLASS_PATH = 'class_path'
KEY_CLASS_NAME = 'class_name'

CACHE_PICKLE = 'pickle'
CACHE_JSON = 'json'
CACHE_FORMAT=CACHE_PICKLE

#plugin methods
PLUGIN_PARSE_ITEM = 'parse_item'
PLUGIN_PARSE_LOGIC = 'parse_logic'
PLUGIN_REMOVE_ITEM = 'remove_item'

#file extensions
CONF_FILE = '.conf'
YAML_FILE = '.yaml'
DEFAULT_FILE = '.default'


#attributes for 'autotimer' parameter
KEY_ATTRIB_COMPAT     = 'assign_compatibility'	# name of key in smarthome.yaml
ATTRIB_COMPAT_V12     = 'compat_1.2'
ATTRIB_COMPAT_LATEST  = 'latest'
