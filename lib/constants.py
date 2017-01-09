#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Strassburg  c.strassburg@gmx.de
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

#item types
ITEM_DEFAULTS= __defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
ITEM_TYPES=["num","str","bool", "list","dict","foo","scene"]
FOO = 'foo'

#config params for items
KEY_ENFORCE_UPDATES = 'enforce_updates'
KEY_CACHE = 'cache'
KEY_CYCLE = 'cycle'
KEY_NAME = 'name'
KEY_TYPE = 'type'
KEY_VALUE = 'value'
KEY_CRONTAB = 'crontab'
KEY_EVAL_TRIGGER = 'eval_trigger'
KEY_EVAL = 'eval'
KEY_THRESHOLD = 'threshold'
KEY_AUTOTIMER = 'autotimer'

#config params for plugins
KEY_INSTANCE = 'instance'
KEY_CLASS_PATH = 'class_path'
KEY_CLASS_NAME = 'class_name'

#plugin methods
PLUGIN_PARSE_ITEM = 'parse_item'
PLUGIN_PARSE_LOGIC = 'parse_logic'

#file extensions
CONF_FILE = '.conf'
YAML_FILE = '.yaml'

#attributes for 'autotimer' parameter
KEY_ATTRIB_COMPAT     = 'assign_compatibility'	# name of key in smarthome.yaml
ATTRIB_COMPAT_V12     = 'compat_1.2'
ATTRIB_COMPAT_LATEST  = 'latest'
