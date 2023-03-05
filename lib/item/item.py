#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2020   Martin Sinn                         m.sinn@gmx.de
# Copyright 2016        Christian Straßburg           c.strassburg@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.
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


import logging
import datetime
import dateutil.parser
import os
import copy
import json
import threading
import ast

import time             # for calls to time in eval
import math             # for calls to math in eval
from math import *


from lib.shtime import Shtime
from lib.plugin import Plugins

from lib.constants import (ITEM_DEFAULTS, FOO, KEY_ENFORCE_UPDATES, KEY_ENFORCE_CHANGE, KEY_CACHE, KEY_CYCLE, KEY_CRONTAB, KEY_EVAL,
                           KEY_EVAL_TRIGGER, KEY_TRIGGER, KEY_CONDITION, KEY_NAME, KEY_TYPE, KEY_STRUCT, KEY_REMARK, KEY_INSTANCE,
                           KEY_VALUE, KEY_INITVALUE, PLUGIN_PARSE_ITEM, KEY_AUTOTIMER, KEY_ON_UPDATE, KEY_ON_CHANGE,
                           KEY_LOG_CHANGE, KEY_LOG_LEVEL, KEY_LOG_TEXT, KEY_LOG_MAPPING, KEY_LOG_RULES,
                           KEY_THRESHOLD, KEY_ATTRIB_COMPAT, ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST)
from lib.utils import Utils

from .property import Property
from .helpers import *

_items_instance = None


ATTRIB_COMPAT_DEFAULT_FALLBACK = ATTRIB_COMPAT_V12
ATTRIB_COMPAT_DEFAULT = ''

logger = logging.getLogger(__name__)
items_count = 0

#####################################################################
# Item Class
#####################################################################

"""
The class ``Item`` implements the methods and attributes of an item. Each item is represented by an instance of the class ``Item``.
"""

class Item():
    """
    Class from which item objects are created

    The class ``Item`` implements the methods and attributes of an item. Each item is represented by an instance
    of the class ``Item``. For an item to be valid and usable, it has to be part of the item tree, which is
    maintained by an object of class ``Items``.

    This class is used by the method ```load_itemdefinitions()`` of the **Items** object.
    """

    _itemname_prefix = 'items.'     # prefix for scheduler names

    def __init__(self, smarthome, parent, path, config, items_instance=None):

        global _items_instance
        if items_instance:
            _items_instance = items_instance

        # get instance if running tests (pytest tests in test_item.py call Item() without 5. parameter (items_instance)
        if _items_instance is None:
            _items_instance = smarthome.items

        self._sh = smarthome
        self._use_conditional_triggers = False
        try:
            if self._sh._use_conditional_triggers.lower() == 'true':
                self._use_conditional_triggers = True
        except: pass

        self.plugins = Plugins.get_instance()
        self.shtime = Shtime.get_instance()

        #count items on creation
        global items_count
        items_count += 1
        if items_count % 50 == 0:
            self._sh.shng_status['details'] = str(items_count)  # Item Zähler übertragen

        self._filename = None
        self._autotimer = False
        self._cache = False
        self.cast = cast_bool
        self.__changed_by = 'Init:None'
        self.__updated_by = self.__changed_by
        self.__triggered_by = 'N/A'
        self.__children = []
        self.conf = {}
        self._crontab = None
        self._cycle = None
        self._enforce_updates = False
        self._enforce_change = False
        self._eval = None				    # -> KEY_EVAL
        self._eval_unexpanded = ''
        self._eval_trigger = False
        self._trigger = False
        self._trigger_unexpanded = []
        self._trigger_condition_raw = []
        self._trigger_condition = None
        self._on_update = None				# -> KEY_ON_UPDATE eval expression
        self._on_change = None				# -> KEY_ON_CHANGE eval expression
        self._on_update_dest_var = None		# -> KEY_ON_UPDATE destination var
        self._on_change_dest_var = None		# -> KEY_ON_CHANGE destination var
        self._on_update_unexpanded = [] 	# -> KEY_ON_UPDATE eval expression (with unexpanded item references)
        self._on_change_unexpanded = [] 	# -> KEY_ON_CHANGE eval expression (with unexpanded item references)
        self._on_update_dest_var_unexp = []	# -> KEY_ON_UPDATE destination var (with unexpanded item reference)
        self._on_change_dest_var_unexp = []	# -> KEY_ON_CHANGE destination var (with unexpanded item reference)
        self._log_change = None
        self._log_change_logger = None
        self._log_level = None
        self._log_level_name = None
        self._log_mapping = {}
        self._log_rules = {}
        self._log_text = None
        self._fading = False
        self._items_to_trigger = []
        self.__last_change = self.shtime.now()
        self.__last_update = self.__last_change
        self.__last_trigger = self.__last_change
        self.__prev_change = self.__last_change
        self.__prev_update = self.__prev_change
        self.__prev_trigger = self.__prev_change
        self.__prev_change_by = 'N/A'
        self.__prev_update_by = self.__prev_change_by
        self.__prev_trigger_by = self.__prev_change_by
        self._lock = threading.Condition()
        self.__logics_to_trigger = []
        self._name = path
        self.__methods_to_trigger = []
        self.__parent = parent
        self._path = path
        self._sh = smarthome
        self._threshold = False
        self._threshold_data = [0,0,False]
        self._type = None
        self._struct = None
        self._value = None
        self.__last_value = None
        self.__prev_value = None

        self.property = Property(self)
        # history
        # TODO: create history Arrays for some values (value, last_change, last_update  (usage: multiklick,...)
        # self.__history = [None, None, None, None, None]
        #
        # def getValue(num):
        #    return (str(self.__history[(num - 1)]))
        #
        # def addValue(avalue):
        #    self.__history.append(avalue)
        #    if len(self.__history) > 5:
        #        self.__history.pop(0)
        #

        #  if 'item_change_log' is set in etc/smarthome.yaml, set loglevel for logging every item change to INFO (instead of DEBUG)
        if hasattr(smarthome, '_item_change_log'):
            self._change_logger = logger.info
        else:
            self._change_logger = logger.debug

        #############################################################
        # Initialize attribute assignment compatibility
        #############################################################
        global ATTRIB_COMPAT_DEFAULT
        if ATTRIB_COMPAT_DEFAULT == '':
            if hasattr(smarthome, '_'+KEY_ATTRIB_COMPAT):
                config_attrib = getattr(smarthome,'_'+KEY_ATTRIB_COMPAT)
                if str(config_attrib) in [ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST]:
                    logger.info("Global configuration: '{}' = '{}'.".format(KEY_ATTRIB_COMPAT, str(config_attrib)))
                    ATTRIB_COMPAT_DEFAULT = config_attrib
                else:
                    logger.warning("Global configuration: '{}' has invalid value '{}'.".format(KEY_ATTRIB_COMPAT, str(config_attrib)))
            if ATTRIB_COMPAT_DEFAULT == '':
                ATTRIB_COMPAT_DEFAULT = ATTRIB_COMPAT_DEFAULT_FALLBACK

        #############################################################
        # Item Attributes
        #############################################################
        self._filename = dict(config.items()).get('_filename', None)
        setattr(self, '_type', dict(config.items()).get(KEY_TYPE))
        for attr, value in config.items():
            if not isinstance(value, dict):
                if attr in [KEY_CYCLE, KEY_NAME, KEY_TYPE, KEY_STRUCT, KEY_VALUE, KEY_INITVALUE]:
                    if attr == KEY_INITVALUE:
                        attr = KEY_VALUE
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_EVAL]:
                    self._process_eval(value)
                elif attr in [KEY_CACHE, KEY_ENFORCE_UPDATES, KEY_ENFORCE_CHANGE]:  # cast to bool
                    try:
                        setattr(self, '_' + attr, cast_bool(value))
                    except:
                        logger.warning("Item '{0}': problem parsing '{1}'.".format(self._path, attr))
                        continue
                elif attr in [KEY_CRONTAB]:  # cast to list
                    if isinstance(value, str):
                        value = [value, ]
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_EVAL_TRIGGER] or (self._use_conditional_triggers and attr in [KEY_TRIGGER]):  # cast to list
                    self._process_trigger_list(attr, value)
                elif (attr in [KEY_CONDITION]) and self._use_conditional_triggers:  # cast to list
                    if isinstance(value, list):
                        cond_list = []
                        for cond in value:
                            cond_list.append(dict(cond))
                        self._trigger_condition = self._build_trigger_condition_eval(cond_list)
                        self._trigger_condition_raw = cond_list
                    else:
                        logger.warning("Item __init__: {}: Invalid trigger_condition specified! Must be a list".format(self._path))
                elif attr in [KEY_ON_CHANGE, KEY_ON_UPDATE]:
                    self._process_on_xx_list(attr, value)

                elif attr in [KEY_LOG_LEVEL]:
                    if value != '':
                        level = value.upper()
                        level_name = level
                        if Utils.is_int(level):
                            level = int(level)
                            level_name = logging.getLevelName(level)
                        if logging.getLevelName(level) == 'Level ' + str(level):
                            logger.warning(f"Item {self._path}: Invalid loglevel '{value}' defined in attribute '{KEY_LOG_LEVEL}' - Level 'INFO' will be used instead")
                            setattr(self, '_log_level_name', 'INFO')
                            setattr(self, '_log_level', logging.getLevelName('INFO'))
                        else:
                            setattr(self, '_log_level_name', level_name)
                            setattr(self, '_log_level', logging.getLevelName(level_name))
                elif attr in [KEY_LOG_CHANGE]:
                    if value != '':
                        setattr(self, '_log_change', value)
                        self._log_change_logger = logging.getLogger('items.'+value)
                        # set level to make logger appear in internal list of loggers (if not configured by logging.yaml)
                        if self._log_change_logger.level == 0:
                            if self._log_level == 'DEBUG':
                                self._log_change_logger.setLevel('DEBUG')
                            else:
                                self._log_change_logger.setLevel('INFO')
                        if self._log_level is None:
                            setattr(self, '_log_level_name', 'INFO')
                            setattr(self, '_log_level', logging.getLevelName('INFO'))
                elif attr in [KEY_LOG_MAPPING]:
                    if value != '':
                        try:
                            value_dict = ast.literal_eval(value)
                            setattr(self, '_log_mapping', value_dict)
                        except Exception as e:
                            logger.warning(f"Item {self._path}: Invalid data for attribute '{KEY_LOG_MAPPING}': {value} - Exception: {e}")
                elif attr in [KEY_LOG_RULES]:
                    if value != '':
                        try:
                            value_dict = ast.literal_eval(value)
                            setattr(self, '_log_rules', value_dict)
                        except Exception as e:
                            logger.warning(f"Item {self._path}: Invalid data for attribute '{KEY_LOG_RULES}': {value} - Exception: {e}")
                elif attr in [KEY_LOG_TEXT]:
                    if value != '':
                        setattr(self, '_log_text', value)

                elif attr == KEY_AUTOTIMER:
                    time, value, compat = split_duration_value_string(value, ATTRIB_COMPAT_DEFAULT)
                    timeitem = None
                    valueitem = None
                    if time.lower().startswith('sh.') and time.endswith('()'):
                        timeitem = self.get_absolutepath(time[3:-2], KEY_AUTOTIMER)
                        time = 0
                    if value.lower().startswith('sh.') and value.endswith('()'):
                        valueitem = self.get_absolutepath(value[3:-2], KEY_AUTOTIMER)
                        value = ''
                    value = self._castvalue_to_itemtype(value, compat)
                    self._autotimer = [ (self._cast_duration(time), value), compat, timeitem, valueitem]
                elif attr == KEY_THRESHOLD:
                    low, __, high = value.rpartition(':')
                    if not low:
                        low = high
                    self._threshold = True
                    self.__th_crossed = False
                    self.__th_low = float(low.strip())
                    self.__th_high = float(high.strip())
                    self._threshold_data[0] = self.__th_low
                    self._threshold_data[1] = self.__th_high
                    self._threshold_data[2] = self.__th_crossed
                    logger.debug("Item {}: set threshold => low: {} high: {}".format(self._path, self.__th_low, self.__th_high))
                elif attr == KEY_REMARK:
                    pass
                elif attr == KEY_INSTANCE:
                    pass
                elif attr == '_filename':
                    # name of file, which defines this item
                    #setattr(self, attr, value)    # assignment moved to top (before for loop)
                    pass
                else:
                    #------------------------------------------------------------
                    # Plugin-specific Item Attributes
                    #------------------------------------------------------------

                    # the following code is executed for plugin specific attributes:
                    #
                    # get value from attribute of other (relative addressed) item
                    # at the moment only parent and grandparent item are supported
                    if (type(value) is str) and (value.startswith('..:') or value.startswith('...:')):
                        fromitem = value.split(':')[0]
                        fromattr = value.split(':')[1]
                        if fromattr in ['', '.']:
                            fromattr = attr
                        if fromitem == '..':
                            #self.conf[attr] = self._get_attr_from_parent(fromattr)
                            value = self._get_attr_from_parent(fromattr)
                        elif fromitem == '...':
                            #self.conf[attr] = self._get_attr_from_grandparent(fromattr)
                            value = self._get_attr_from_grandparent(fromattr)
                        elif fromitem == '....':
                            #self.conf[attr] = self._get_attr_from_greatgrandparent(fromattr)
                            value = self._get_attr_from_greatgrandparent(fromattr)

                    # Test if the plugin-specific attribute contains a valid value
                    # and set the default value, if needed
                    if hasattr(self.plugins, 'meta'):
                        value = self.plugins.meta.check_itemattribute(self, attr.split('@')[0], value, self._filename)
                        self.conf[attr] = value

        self.property.init_dynamic_properties()

        #############################################################
        # Child Items
        #############################################################
        for attr, value in config.items():
            if isinstance(value, dict):
                child_path = self._path + '.' + attr
                try:
                    child = Item(smarthome, self, child_path, value)
                except Exception as e:
                    logger.exception("Item {}: problem creating: {}".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    _items_instance.add_item(child_path, child)
                    self.__children.append(child)

        #############################################################
        # Type
        #############################################################
        #__defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
        if self._type is None:
            self._type = FOO  # Every item has a type, type is FOO, if not defined in item
        if self._type not in ITEM_DEFAULTS:
            logger.error("Item {}: type '{}' unknown. Please use one of: {}.".format(self._path, self._type, ', '.join(list(ITEM_DEFAULTS.keys()))))
            raise AttributeError
        self.cast = globals()['cast_' + self._type]

        #############################################################
        # Value
        #############################################################
        initial_value = False
        if self._value is None:
            initial_value = False
            self._value = ITEM_DEFAULTS[self._type]
        else:
            initial_value = True
        try:
            self._value = self.cast(self._value)
            if initial_value:
                self.__changed_by = 'Init:Initial_Value'
                self.__updated_by = self.__changed_by
                # Write item value to log, if Item has attribute log_change set
                self._log_on_change(self._value, 'Init', 'Initial_Value', None)
        except:
            logger.error("Item {}: value {} does not match type {}.".format(self._path, self._value, self._type))
            raise
        self.__prev_value = self.__last_value
        self.__last_value = self._value

        #############################################################
        # Cache
        #############################################################
        if self._cache:
            self._cache = os.path.join(self._sh._cache_dir, self._path)
            try:
                self.__changed_by = 'Init:Cache'
                self.__last_change, self._value = cache_read(self._cache, self.shtime.tzinfo())
                self.__prev_change = self.__last_change
                self.__updated_by = self.__changed_by
                self.__triggered_by = 'N/A'
                self.__last_update = self.__last_change
                self.__prev_update = self.__prev_change

                # Write item value to log, if Item has attribute log_change set
                self._log_on_change(self._value, self.__changed_by, 'Cache', None)
            except Exception as e:
                if str(e).startswith('[Errno 2]'):
                    logger.info(f"Item {self._path}: No cached value: {e}")
                else:
                    if os.stat(self._cache).st_size == 0:
                        logger.warning(f"Item {self._path}: Problem reading cache: Filesize is 0 bytes. Deleting invalid cache file")
                        os.remove(self._cache)
                    else:
                        logger.warning(f"Item {self._path}: Problem reading cache: {e}")

        #############################################################
        # Cache write/init
        #############################################################
        if self._cache:
            if not os.path.isfile(self._cache):
                cache_write(self._cache, self._value)
                logger.notice(f"Created cache for item {self._cache} in file {self._cache}")

        #############################################################
        # Plugins
        #############################################################
        for plugin in self.plugins.return_plugins():
            #plugin.xxx = []  # Empty reference list list of items
            if hasattr(plugin, PLUGIN_PARSE_ITEM):
                update = plugin.parse_item(self)
                if update:
                    try:
                        plugin.add_item(self, updating=True)
                    except:
                        pass
                    self.add_method_trigger(update)



    def _split_destitem_from_value(self, value):
        """
        For on_change and on_update: spit destination item from attribute value

        :param value: attribute value

        :return: dest_item, value
        :rtype: str, str
        """
        dest_item = ''
        # Check if assignment operator ('=') exists ('=' before first '(')
        if ((value.find('=') != -1) and (value.find('(') == -1)) or \
           ((value.find('=') != -1) and (value.find('=') < value.find('('))):
            # If delimiter exists, check if equal operator exists
            if value.find('==') != -1:
                # equal operator exists
                if value.find('=') < value.find('=='):
                    # assignment operator exists in front of equal operator
                    dest_item = value[:value.find('=')].strip()
                    value = value[value.find('=')+1:].strip()
            else:
                # if equal operator does not exist
                dest_item = value[:value.find('=')]
                value = value[value.find('=')+1:].strip()
        return dest_item, value


    def _castvalue_to_itemtype(self, value, compat):
        """
        casts the value to the type of the item, if backward compatibility
        to version 1.2 (ATTRIB_COMPAT_V12) is not enabled

        If backward compatibility is enabled, the value is returned unchanged

        :param value: value to be casted
        :param compat: compatibility attribute
        :return: return casted value
        """
        # casting of value, if compat = latest
        if compat == ATTRIB_COMPAT_LATEST:
            if self._type != None:
                mycast = globals()['cast_' + self._type]
                try:
                    value = mycast(value)
                except:
                    logger.warning("Item {}: Unable to cast '{}' to {}".format(self._path, str(value), self._type))
                    if isinstance(value, list):
                        value = []
                    elif isinstance(value, dict):
                        value = {}
                    else:
                        value = mycast('')
            else:
                logger.warning("Item {}: Unable to cast '{}' to {}".format(self._path, str(value), self._type))
        return value


    def _cast_duration(self, time):
        """
        casts a time value string (e.g. '5m') to an duration integer
        used for autotimer, timer, cycle

        supported formats for time parameter:
        - seconds as integer (45)
        - seconds as a string ('45')
        - seconds as a string, trailed by 's' ('45s')
        - minutes as a string, trailed by 'm' ('5m'), is converted to seconds (300)

        :param time: string containing the duration
        :param itempath: item path as additional information for logging
        :return: number of seconds as an integer
        """
        if isinstance(time, str):
            try:
                time = time.strip()
                if time.endswith('m'):
                    time = int(time.strip('m')) * 60
                elif time.endswith('s'):
                    time = int(time.strip('s'))
                else:
                    time = int(time)
            except Exception as e:
                logger.warning("Item {}: _cast_duration ({}) problem: {}".format(self._path, time, e))
                time = False
        elif isinstance(time, int):
            time = int(time)
        elif isinstance(time, float):
            time = int(time)
        else:
            logger.warning("Item {}: _cast_duration ({}) problem: unable to convert to int".format(self._path, time))
            time = False
        return(time)


    def _build_cycledict(self, value):
        """
        builds a dict for a cycle parameter from a duration_value_string

        This dict is to be passed to the scheduler to circumvent the parameter
        parsing within the scheduler, which can't to casting

        :param value: raw attribute string containing duration, value (and compatibility)
        :return: cycle-dict for a call to scheduler.add
        """
        # try:
        #     result = int(value)
        # except ValueError:
        #     time, value, compat = split_duration_value_string(value, ATTRIB_COMPAT_DEFAULT)
        #     time = self._cast_duration(time)
        #     value = self._castvalue_to_itemtype(value, compat)
        #     cycle = {time: value}
        #     result = cycle
        time, value, compat = split_duration_value_string(value, ATTRIB_COMPAT_DEFAULT)
        time = self._cast_duration(time)
        value = self._castvalue_to_itemtype(value, compat)
        cycle = {time: value}
        result = cycle
        return result

    """
    --------------------------------------------------------------------------------------------
    """


    def _build_on_xx_list(self, on_dest_list, on_eval_list):
        """
        build on_xx data
        """
        on_list = []
        if on_dest_list is not None:
            if isinstance(on_dest_list, list):
                for on_dest, on_eval in zip(on_dest_list, on_eval_list):
                    if on_dest != '':
                        on_list.append(on_dest.strip() + ' = ' + on_eval)
                    else:
                        on_list.append(on_eval)
            else:
                if on_dest_list != '':
                    on_list.append(on_dest_list + ' = ' + on_eval_list)
                else:
                    on_list.append(on_eval_list)
        return on_list


    def _process_eval(self, value):

        if value == '':
            self._eval_unexpanded = ''
            self._eval = None
        else:
            self._eval_unexpanded = value
            value = self.get_stringwithabsolutepathes(value, 'sh.', '(', KEY_EVAL)
            #value = self.get_stringwithabsolutepathes(value, 'sh.', '.property', KEY_EVAL)
            self._eval = value


    def _process_trigger_list(self, attr, value):

        if isinstance(value, str):
            value = [value, ]
        self._trigger_unexpanded = value
        expandedvalue = []
        for path in value:
            expandedvalue.append(self.get_absolutepath(path, attr))
        self._trigger = expandedvalue


    def _process_on_xx_list(self, attr, value):

        if isinstance(value, str):
            value = [value]
        val_list = []
        val_list_unexpanded = []
        dest_var_list = []
        dest_var_list_unexp = []
        for val in value:
            # separate destination item (if it exists)
            dest_item, val = self._split_destitem_from_value(val)
            dest_var_list_unexp.append(dest_item)
            # expand relative item paths
            dest_item = self.get_absolutepath(dest_item, KEY_ON_CHANGE).strip()
            #                        val = 'sh.'+dest_item+'( '+ self.get_stringwithabsolutepathes(val, 'sh.', '(', KEY_ON_CHANGE) +' )'
            val_list_unexpanded.append(val)
            val = self.get_stringwithabsolutepathes(val, 'sh.', '(', KEY_ON_CHANGE)
            #val = self.get_stringwithabsolutepathes(val, 'sh.', '.property', KEY_ON_CHANGE)
            #                        logger.warning("Item __init__: {}: for attr '{}', dest_item '{}', val '{}'".format(self._path, attr, dest_item, val))
            val_list.append(val)
            dest_var_list.append(dest_item)
        setattr(self, '_' + attr + '_unexpanded', val_list_unexpanded)
        setattr(self, '_' + attr, val_list)
        setattr(self, '_' + attr + '_dest_var', dest_var_list)
        setattr(self, '_' + attr + '_dest_var_unexp', dest_var_list_unexp)
        return


    def _get_last_change(self):
        return self.__last_change

    def _get_last_change_age(self):
        delta = self.shtime.now() - self.__last_change
        return delta.total_seconds()

    def _get_last_change_by(self):
        return self.__changed_by

    def _get_last_update(self):
        return self.__last_update

    def _get_last_update_by(self):
        return self.__updated_by

    def _get_last_update_age(self):
        delta = self.shtime.now() - self.__last_update
        return delta.total_seconds()

    def _get_last_trigger(self):
        return self.__last_trigger

    def _get_last_trigger_age(self):
        delta = self.shtime.now() - self.__last_trigger
        return delta.total_seconds()

    def _get_last_trigger_by(self):
        return self.__triggered_by

    def _get_last_value(self):
        return self.__last_value

    def _get_prev_change(self):
        return self.__prev_change

    def _get_prev_change_age(self):
        delta = self.__last_change - self.__prev_change
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_change_by(self):
        return self. __prev_change_by

    def _get_prev_update(self):
        return self.__prev_change

    def _get_prev_update_age(self):

        delta = self.__last_update - self.__prev_update
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_update_by(self):
        return self. __prev_update_by

    def _get_prev_value(self):
        return self.__prev_value

    def _get_prev_trigger(self):
        return self.__prev_trigger

    def _get_prev_trigger_age(self):

        delta = self.__last_trigger - self.__prev_trigger
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_trigger_by(self):
        return self. __prev_trigger_by


    """
    Following are methods to get attributes of the item
    """

    def path(self):
        """
        Path of the item

        Available only in SmartHomeNG v1.6, not in versions above

        :return: String with the path of the item
        :rtype: str
        """
        return self.property.path

    def id(self):
        """
        Old method name - Use item.path() instead of item.id()
        """
        return self.property.path


    def type(self):
        """
        Datatype of the item

        :return: Datatype of the item
        :rtype: str
        """
        return self.property.type


    def last_change(self):
        """
        Timestamp of last change of item's value

        :return: Timestamp of last change
        """
        return self.property.last_change

    def age(self):
        """
        Age of the item's actual value. Returns the time in seconds since the last change of the value

        :return: Age of the value
        :rtype: int
        """
        return self.property.last_change_age


    def last_update(self):
        """
        Timestamp of last update of item's value (not necessarily change)

        :return: Timestamp of last update
        """
        return self.property.last_update

    def update_age(self):
        """
        Update-age of the item's actual value. Returns the time in seconds since the value has been updated (not necessarily changed)

        :return: Update-age of the value
        :rtype: int
        """
        return self.property.last_update_age

    def last_trigger(self):
        """
        Timestamp of last trigger of item's eval expression (if available)

        :return: Timestamp of last update
        """
        return self.property.last_trigger

    def trigger_age(self):
        """
        Trigger-age of the item's last eval trigger. Returns the time in seconds since the eval has been triggered

        :return: Update-age of the value
        :rtype: int
        """
        return self.property.last_trigger_age

    def prev_change(self):
        """
        Timestamp of the previous (next-to-last) change of item's value

        :return: Timestamp of previous change
        """
        return self.property.prev_change

    def prev_age(self):
        """
        Age of the item's previous value. Returns the time in seconds the item had the the previous value

        :return: Age of the previous value
        :rtype: int
        """
        return self.property.prev_change_age

    def prev_update(self):
        """
        Timestamp of previous (next-to-last) update of item's value (not necessarily change)

        :return: Timestamp of previous update
        """
        return self.property.prev_update

    def prev_update_age(self):
        """
        Update-age of the item's previous value. Returns the time in seconds the previous value existed
        since it had been updated (not necessarily changed)

        :return: Update-age of the previous value
        :rtype: int
        """
        return self.property.prev_update_age

    def prev_trigger(self):
        """
        Timestamp of previous (next-to-last) trigger of item's eval

        :return: Timestamp of previous update
        """
        return self.property.prev_trigger

    def prev_trigger_age(self):
        """
        Trigger-age of the item's previous eval trigger. Returns the time in seconds of the previous eval trigger

        :return: Update-age of the previous value
        :rtype: int
        """
        return self.property.prev_trigger_age

    def prev_value(self):
        """
        Next-to-last value of the item

        :return: Next-to-last value of the item
        """
        return self.property.last_value

    def changed_by(self):
        """
        Returns an indication, which plugin, logic or event changed the item's value

        :return: Changer of item's value
        :rtype: str
        """
        return self.property.last_change_by

    def updated_by(self):
        """
        Returns an indication, which plugin, logic or event updated (not necessarily changed) the item's value

        :return: Updater of item's value
        :rtype: str
        """
        return self.property.last_update_by

    def triggered_by(self):
        """
        Returns an indication, which plugin, logic or event triggered the item's eval

        :return: Updater of item's value
        :rtype: str
        """
        return self.property.last_trigger_by

    """
    Following are methods to handle relative item paths
    """

    def get_absolutepath(self, relativepath, attribute=''):
        """
        Builds an absolute item path relative to the current item

        :param relativepath: string with the relative item path
        :param attribute: string with the name of the item's attribute, which contains the relative path (for log entries)

        :return: string with the absolute item path
        """
        if not isinstance(relativepath, str):
            return relativepath
        if (len(relativepath) == 0) or ((len(relativepath) > 0) and (relativepath[0] != '.')):
            return relativepath
        relpath = relativepath.rstrip()
        rootpath = self._path

        while (len(relpath) > 0) and (relpath[0] == '.'):
            relpath = relpath[1:]
            if (len(relpath) > 0) and (relpath[0] == '.'):
                if rootpath.rfind('.') == -1:
                    if rootpath == '':
                        relpath = ''
                        logger.error("{}.get_absolutepath(): Relative path trying to access above root level on attribute '{}'".format(self._path, attribute))
                    else:
                        rootpath = ''
                else:
                    rootpath = rootpath[:rootpath.rfind('.')]

        trailing_str = ''
        if relpath.startswith('self') and len(relpath) > 4:
            if relpath[4]  in "() +-*/<>!=&%":
                trailing_str = relpath[4:]
                relpath = ''

        if relpath != '':
            if rootpath != '':
                rootpath += '.' + relpath
            else:
                rootpath = relpath
        rootpath += trailing_str

        logger.info("{}.get_absolutepath('{}'): Result = '{}' (for attribute '{}')".format(self._path, relativepath, rootpath, attribute))
        if rootpath[-5:] == '.self':
            rootpath = rootpath.replace('.self', '')
        rootpath = rootpath.replace('.self.', '.')
        return rootpath

    def expand_relativepathes(self, attr, begintag, endtag):
        """
        converts a configuration attribute containing relative item paths
        to absolute paths

        The item's attribute can be of type str or list (of strings)

        The begintag and the endtag remain in the result string!

        :param attr: Name of the attribute. Use * as a wildcard at the end
        :param begintag: string or list of strings that signals the beginning of a relative path is following
        :param endtag: string or list of strings that signals the end of a relative path

        """
        def __checkforentry(attr):
            if isinstance(self.conf[attr], str):
                if (begintag != '') and (endtag != ''):
                    self.conf[attr] = self.get_stringwithabsolutepathes(self.conf[attr], begintag, endtag, attr)
                elif (begintag == '') and (endtag == ''):
                    self.conf[attr] = self.get_absolutepath(self.conf[attr], attr)
            elif isinstance(self.conf[attr], list):
                logger.debug("expand_relativepathes(1): to expand={}".format(self.conf[attr]))
                new_attr = []
                for a in self.conf[attr]:
                    # Convert accidentally wrong dict entries to string
                    if isinstance(a, dict):
                        a = list("{!s}:{!s}".format(k,v) for (k,v) in a.items())[0]
                    logger.debug("expand_relativepathes: before : to expand={}".format(a))
                    if (begintag != '') and (endtag != ''):
                        a = self.get_stringwithabsolutepathes(a, begintag, endtag, attr)
                    elif (begintag == '') and (endtag == ''):
                        a = self.get_absolutepath(a, attr)
                    logger.debug("expand_relativepathes: after: to expand={}".format(a))
                    new_attr.append(a)
                self.conf[attr] = new_attr
                logger.debug("expand_relativepathes(2): expanded={}".format(self.conf[attr]))
            else:
                logger.warning("expand_relativepathes: attr={} can not expand for type(self.conf[attr])={}".format(attr, type(self.conf[attr])))

        # Check if wildcard is used
        if isinstance(attr, str) and attr[-1:] == "*":
            for entry in self.conf:
                if attr[:-1] in entry:
                    __checkforentry(entry)
        elif attr in self.conf:
            __checkforentry(attr)
        return


    def get_stringwithabsolutepathes(self, evalstr, begintag, endtag, attribute=''):
        """
        converts a string containing relative item paths
        to a string with absolute item paths

        The begintag and the endtag remain in the result string!

        :param evalstr: string with the statement that may contain relative item paths
        :param begintag: string that signals the beginning of a relative path is following
        :param endtag: string that signals the end of a relative path
        :param attribute: string with the name of the item's attribute, which contains the relative path

        :return: string with the statement containing absolute item paths
        """
        def __checkfortags(evalstr, begintag, endtag):

            pref = ''
            rest = evalstr
            while (rest.find(begintag+'.') != -1):
                pref += rest[:rest.find(begintag+'.')+len(begintag)]
                rest = rest[rest.find(begintag+'.')+len(begintag):]
                if endtag == '' or rest.find(endtag) == -1:
                    rel = rest
                    rest = ''
                else:
                    rel = rest[:rest.find(endtag)]
                rest = rest[rest.find(endtag):]
                pref += self.get_absolutepath(rel, attribute)
                # Re-combine string for next loop
                rest = pref+rest
                pref = ''

            pref += rest
            logger.debug("{}.get_stringwithabsolutepathes('{}') with begintag = '{}', endtag = '{}': result = '{}'".format(
                self._path, evalstr, begintag, endtag, pref))
            return pref # end of __checkfortags(...)


        if not isinstance(evalstr, str):
            return evalstr

        if isinstance(begintag, list):
            # Fill end or begintag with empty tags if list length is not equal
            diff_len = len(begintag) - len(endtag)
            begintag = begintag + [''] * abs(diff_len) if diff_len < 0 else begintag
            endtag = endtag + [''] * diff_len if diff_len > 0 else endtag
            for i, _ in enumerate(begintag):
                if not evalstr.find(begintag[i]+'.') == -1:
                    evalstr = __checkfortags(evalstr, begintag[i], endtag[i])
            pref = evalstr
        else:
            if evalstr.find(begintag+'.') == -1:
                return evalstr
            pref = __checkfortags(evalstr, begintag, endtag)
        return pref


    def _get_attr_from_parent(self, attr):
        """
        Get value from parent

        :param attr: Get the value from this attribute of the parent item
        :return: value from attribute of parent item
        """
        pitem = self.return_parent()
        pattr_value = pitem.conf.get(attr, '')
        #        logger.warning("_get_attr_from_parent Item {}: for attr '{}'".format(self._path, attr))
        #        logger.warning("_get_attr_from_parent Item {}: for parent '{}', pattr_value '{}'".format(self._path, pitem._path, pattr_value))
        return pattr_value


    def _get_attr_from_grandparent(self, attr):
        """
        Get value from grandparent

        :param attr: Get the value from this attribute of the grandparent item
        :return: value from attribute of grandparent item
        """
        pitem = self.return_parent()
        gpitem = pitem.return_parent()
        gpattr_value = gpitem.conf.get(attr, '')
#        logger.warning("_get_attr_from_grandparent Item {}: for attr '{}'".format(self._path, attr))
#        logger.warning("_get_attr_from_grandparent Item {}: for grandparent '{}', gpattr_value '{}'".format(self._path, gpitem._path, gpattr_value))
        return gpattr_value


    def _get_attr_from_greatgrandparent(self, attr):
        """
        Get value from grandparent

        :param attr: Get the value from this attribute of the grandparent item
        :return: value from attribute of grandparent item
        """
        pitem = self.return_parent()
        gpitem = pitem.return_parent()
        ggpitem = gpitem.return_parent()
        ggpattr_value = ggpitem.conf.get(attr, '')
        return ggpattr_value


    def _build_trigger_condition_eval(self, trigger_condition):
        """
        Build conditional eval expression from trigger_condition attribute

        :param trigger_condition: list of condition dicts
        :return:
        """
        wrk_eval = []
        for or_cond in trigger_condition:
            for ckey in or_cond:
                if ckey.lower() == 'value':
                    pass
                else:
                    and_cond = []
                    for cond in or_cond[ckey]:
                        wrk = cond
                        if (wrk.find('=') != -1) and (wrk.find('==') == -1) and \
                                (wrk.find('<=') == -1) and (wrk.find('>=') == -1) and \
                                (wrk.find('=<') == -1) and (wrk.find('=>') == -1):
                            wrk = wrk.replace('=', '==')

                        p = wrk.lower().find('true')
                        if p != -1:
                            wrk = wrk[:p]+'True'+wrk[p+4:]
                        p = wrk.lower().find('false')
                        if p != -1:
                            wrk = wrk[:p]+'False'+wrk[p+5:]

                        # expand relative item paths
                        wrk = self.get_stringwithabsolutepathes(wrk, 'sh.', '(', KEY_CONDITION)
                        #wrk = self.get_stringwithabsolutepathes(wrk, 'sh.', '.property', KEY_CONDITION)

                        and_cond.append(wrk)

                    wrk = ') and ('.join(and_cond)
                    if len(or_cond[ckey]) > 1:
                        wrk = '(' + wrk + ')'
                    wrk_eval.append(wrk)

    #                wrk_eval.append(str(or_cond[ckey]))
                    result = ') or ('.join(wrk_eval)

        if len(trigger_condition) > 1:
            result = '(' + result + ')'

        return result


    def __call__(self, value=None, caller='Logic', source=None, dest=None):
        if value is None or self._type is None:
            return copy.deepcopy(self._value)
        if self._eval:
            args = {'value': value, 'caller': caller, 'source': source, 'dest': dest}
            self._sh.trigger(name=self._path + '-eval', obj=self.__run_eval, value=args, by=caller, source=source, dest=dest)
        else:
            self.__update(value, caller, source, dest)

    def __iter__(self):
        for child in self.__children:
            yield child

    def __setitem__(self, item, value):
        vars(self)[item] = value

    def __getitem__(self, item):
        return vars(self)[item]

    def __bool__(self):
        return bool(self._value)

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Item: {}".format(self._path)


    # feature moved to lib.metadata
    # def _test_attribute_existance(self):
    #     """
    #
    #     :return:
    #     """
    #     for attr in self.conf:
    #         if not self._sh.items.plugin_attribute_exists(attr.split('@')[0]):
    #             if not (self._path.startswith('env')):
    #                 value = self.conf[attr]
    #                 log_msg = "Undefined attribute '{}' with value '{}' used by item {}".format(attr, value, self._path)
    #                 if self._filename:
    #                     log_msg += " (defined in {})".format(self._filename)
    #                 if hasattr(self._sh, '_undef_item_attr_loglevel_info') and self._sh._undef_item_attr_loglevel_info:
    #                     logger.info(log_msg)
    #                 else:
    #                     logger.warning(log_msg)


    def _init_prerun(self):
        """
        Build eval expressions from special functions and triggers before first run

        Called from Items.load_itemdefinitions
        """
        if self._trigger:
            # Only if item has an eval_trigger
            _items = []
            for trigger in self._trigger:
                if _items_instance.match_items(trigger) == [] and self._eval:
                    logger.warning("item '{}': trigger item '{}' not found for function '{}'".format(self._path, trigger, self._eval))
                _items.extend(_items_instance.match_items(trigger))
            for item in _items:
                if item != self:  # prevent loop
                        item._items_to_trigger.append(self)
            if self._eval:
                # Build eval statement from trigger items (joined by given function)
                items = ['sh.' + str(x.id()) + '()' for x in _items]
                if self._eval == 'and':
                    self._eval = ' and '.join(items)
                elif self._eval == 'or':
                    self._eval = ' or '.join(items)
                elif self._eval == 'sum':
                    self._eval = ' + '.join(items)
                elif self._eval == 'avg':
                    self._eval = '({0})/{1}'.format(' + '.join(items), len(items))
                elif self._eval == 'max':
                    self._eval = 'max({0})'.format(','.join(items))
                elif self._eval == 'min':
                    self._eval = 'min({0})'.format(','.join(items))


    def _init_start_scheduler(self):
        """
        Start schedulers of the items which have a crontab or a cycle attribute

        up to version 1.5 of SmartHomeNG the schedulers were started when initializing the item. That
        could lead to a scheduler to fire a routine, which references an item which is not yet initialized
        :return:
        """

        #############################################################
        # Crontab/Cycle
        #############################################################
        if self._crontab is not None or self._cycle is not None:
            cycle = self._cycle
            if cycle is not None:
                cycle = self._build_cycledict(cycle)
            self._sh.scheduler.add(self._itemname_prefix+self._path, self, cron=self._crontab, cycle=cycle)

        return


    def _init_run(self):
        """
        Run initial eval to set an initial value for the item

        Called from Items.load_itemdefinitions
        """
        if self._trigger:
            # Only if item has an eval_trigger
            if self._eval and not self._cache:
                # Only if item has an eval expression
                self._sh.trigger(name=self._path, obj=self.__run_eval, by='Init', value={'value': self._value, 'caller': 'Init:Eval'})
                return True
        return False


    def __run_eval(self, value=None, caller='Eval', source=None, dest=None):
        """
        evaluate the 'eval' entry of the actual item
        """
        if (self._sh.shng_status['code'] != 20) and (caller != 'Init'):
            logger.info(f"Item {self._path}: Running __run_eval before initialization is finished - caller={caller}, source={source}")
        if self._eval:
            # Test if a conditional trigger is defined
            if self._trigger_condition is not None:
                #logger.warning("Item {}: Evaluating trigger condition {}".format(self._path, self._trigger_condition))
                try:
                    # set up environment for calculating eval-expression
                    sh = self._sh
                    shtime = self.shtime
                    items = _items_instance
                    import math
                    import lib.userfunctions as uf
                    # uf.import_user_modules()  -  Modules were loaded during initialization phase of shng

                    cond = eval(self._trigger_condition)
                    logger.warning("Item {}: Condition result '{}' evaluating trigger condition {}".format(self._path, cond, self._trigger_condition))
                except Exception as e:
                    log_msg = "Item {}: Problem evaluating trigger condition '{}': {}".format(self._path, self._trigger_condition, e)
                    if (self._sh.shng_status['code'] != 20) and (caller != 'Init'):
                        logger.debug(log_msg)
                    else:
                        logger.warning(log_msg)
                    return
            else:
                cond = True

            if cond == True:
    #            if self._path == 'wohnung.flur.szenen_helper':
    #                logger.info("__run_eval: item = {}, value = {}, self._eval = {}".format(self._path, value, self._eval))
                # set up environment for calculating eval-expression
                sh = self._sh
                shtime = self.shtime
                items = _items_instance
                import math
                import lib.userfunctions as uf
                # uf.import_user_modules()  -  Modules were loaded during initialization phase of shng

                try:
                    self.__prev_trigger_by = self.__triggered_by
                    self.__triggered_by = "{0}:{1}".format(caller, source)
                    self.__prev_trigger = self.__last_trigger
                    self.__last_trigger = self.shtime.now()

                    logger.debug("Item {}: Eval triggered by: {}. Evaluating item with value {}. Eval expression: {}".format(self._path, self.__triggered_by, value, self._eval))
                    #value = eval(self._eval)

                    # ms if contab: init = x is set, x is transfered as a string, for that case re-try eval with x converted to float
                    try:
                       value = eval(self._eval)
                    except:
                        #value = float(value)
                        value = self._value = self.cast(value)
                        value = eval(self._eval)
                    # ms end

                except Exception as e:
                    # adding "None" as the "destination" information at end of triggered_by
                    # This helps figuring out whether an eval expression was successfully evaluated or not.
                    self.__triggered_by = "{0}:{1}:None".format(caller, source)
                    log_msg = "Item {}: problem evaluating '{}': {}".format(self._path, self._eval, e)
                    if (self._sh.shng_status['code'] != 20) and (caller != 'Init'):
                        logger.debug(log_msg + " (status_code={}/caller={})".format(self._sh.shng_status['code'], caller))
                    else:
                        logger.warning(log_msg)
                else:
                    if value is None:
                        logger.debug("Item {}: evaluating {} returns None".format(self._path, self._eval))
                    else:
                        if self._path == 'wohnung.flur.szenen_helper':
                            logger.info("__run_eval: item = {}, value = {}".format(self._path, value))
                        self.__update(value, caller, source, dest)


    # New for on_update / on_change
    def _run_on_xxx(self, path, value, on_dest, on_eval, attr='?'):
        """
        common method for __run_on_update and __run_on_change

        :param path: path to this item

        :param attr: Descriptive text for origin of update of item ('on_change', 'on_update')
        :type: path: str

        :type attr: str
        """

        # set up environment for calculating eval-expression
        sh = self._sh
        shtime = self.shtime
        items = _items_instance
        import math
        import lib.userfunctions as uf
        #uf.import_user_modules()  -  Modules were loaded during initialization phase of shng

        logger.info("Item {}: '{}' evaluating {} = {}".format(self._path, attr, on_dest, on_eval))

        # if syntax without '=' is used, add caller and source to the item assignement
        if on_dest == '':
            on_eval = on_eval.strip()
            if on_eval[-1] == ')':
                test = on_eval.replace(' ', '')
                if test.lower().find(',caller=') == -1 and test.lower().find(',source=') == -1:
                    # if neither 'caller' nor 'source' is given
                    on_eval = on_eval[:-1] + ", caller='" + attr + "', source='" + self._path + "')"
                if test.lower().find(',caller=') > -1 and test.lower().find(',source=') == -1:
                    # if only 'caller' is given
                    on_eval = on_eval[:-1] + ", source='" + self._path + "')"
                if test.lower().find(',caller=') == -1 and test.lower().find(',source=') > -1:
                    # if only 'source' is given
                    on_eval = on_eval[:-1] + ", caller='" + attr + "')"

        # try if on_eval contains a valid eval expression
        # Attention: This already assignes the value, if syntax without '=' is used
        try:
            dest_value = eval(on_eval)       # calculate to test if expression computes and see if it computes to None
        except Exception as e:
            logger.warning("Item {}: '{}' item-value='{}' problem evaluating {}: {}".format(self._path, attr, value, on_eval, e))
        else:
            if dest_value is not None:
                # expression computes and does not result in None
                if on_dest != '':
                    dest_item = _items_instance.return_item(on_dest)
                    if dest_item is not None:
                        dest_item.__update(dest_value, caller=attr, source=self._path)
                        logger.debug(" - : '{}' finally evaluating {} = {}, result={}".format(attr, on_dest, on_eval, dest_value))
                    else:
                        logger.error("Item {}: '{}' has not found dest_item '{}' = {}, result={}".format(self._path, attr, on_dest, on_eval, dest_value))
                else:
                    dummy = eval(on_eval)
                    logger.debug(" - : '{}' finally evaluating {}, result={}".format(attr, on_eval, dest_value))
            else:
                logger.debug(" - : '{}' {} not set (cause: eval=None)".format(attr, on_dest))
                pass


    def __run_on_update(self, value=None):
        """
        evaluate all 'on_update' entries of the actual item
        """
        if self._on_update:
            # sh = self._sh  # noqa
#            logger.info("Item {}: 'on_update' evaluating {} = {}".format(self._path, self._on_update_dest_var, self._on_update))
            for on_update_dest, on_update_eval in zip(self._on_update_dest_var, self._on_update):
                self._run_on_xxx(self._path, value, on_update_dest, on_update_eval, 'On_Update')


    def __run_on_change(self, value=None):
        """
        evaluate all 'on_change' entries of the actual item
        """
        if self._on_change:
            # sh = self._sh  # noqa
#            logger.info("Item {}: 'on_change' evaluating lists {} = {}".format(self._path, self._on_change_dest_var, self._on_change))
            for on_change_dest, on_change_eval in zip(self._on_change_dest_var, self._on_change):
                self._run_on_xxx(self._path, value, on_change_dest, on_change_eval, 'On_Change')


    def _log_build_standardtext(self, value, caller, source=None, dest=None):

        log_src = ''
        if source is not None:
            log_src += ' (' + source + ')'
        log_dst = ''
        if dest is not None:
            log_dst += ', dest: ' + dest
        txt = f"Item Change: {self._path} = {value}  -  caller: {caller}{log_src}{log_dst}"
        return txt


    def _log_build_text(self, value, caller, source=None, dest=None):

        # value
        # caller
        # source
        # dest
        lvalue = self.property.last_value
        mlvalue = self._log_mapping.get(lvalue, lvalue)
        name = self._name
        age = round(self._get_last_change_age(), 2)
        pname = self.__parent._name
        id = self._path
        pid = self.__parent._path
        mvalue = self._log_mapping.get(value, value)
        lowlimit = self._log_rules.get('lowlimit', None)
        highlimit = self._log_rules.get('highlimit', None)

        try:
            #logger.warning(f"self._log_text: {self._log_text}, type={type(self._log_text)}")
            txt = eval(f"f'{self._log_text}'")
        except Exception as e:
            logger.error(f"{id}: Invalid log_text template ' {self._log_text}' - (Exception: {e})")
            txt = self._log_text
        return txt


    def _log_on_change(self, value, caller, source=None, dest=None):
        """
        Write log, if Item has attribute log_change set
        :return:
        """
        if self._log_change_logger is not None:
            filter_list = self._log_rules.get('filter', [])

            if self._type == 'num':
                low_limit =  self._log_rules.get('lowlimit', None)
                if low_limit:
                    if low_limit > float(value):
                        return
                high_limit =  self._log_rules.get('highlimit', None)
                if high_limit:
                    if high_limit <= float(value):
                        return
                if filter_list != []:
                    if not float(value) in filter_list:
                        return
            else:
                if filter_list != []:
                    if not value in filter_list:
                        return

            if self._log_text is None:
                txt = self._log_build_standardtext(value, caller, source, dest)
            else:
                txt = self._log_build_text(value, caller, source, dest)

            # log_src = ''
            # if source is not None:
            #     log_src += ' (' + source + ')'
            # log_dst = ''
            # if dest is not None:
            #     log_dst += ', dest: ' + dest
            #self._log_change_logger.log(self._log_level, "Item Change: {} = {}  -  caller: {}{}{}".format(self._path, value, caller, log_src, log_dst))
            self._log_change_logger.log(self._log_level, txt)


    def __trigger_logics(self, source_details=None):
        source={'item': self._path, 'details': source_details}
        for logic in self.__logics_to_trigger:
#            logic.trigger(by='Item', source=self._path, value=self._value)
            logic.trigger(by='Item', source=source, value=self._value)

    # logic.trigger(by='Logic', source=None, value=None, dest=None, dt=None):


    def _set_value(self, value, caller, source=None, dest=None, prev_change=None, last_change=None):
        """
        Set item value, update last aund prev information and perform log_change for item

        :param value:
        :param caller:
        :param source:
        :param dest:
        :param prev_change:
        :param last_change:
        :return:
        """
        self.__prev_value = self.__last_value
        self.__last_value = self._value
        self._value = value

        if prev_change is None:
            self.__prev_change = self.__last_change
        else:
            self.__prev_change = prev_change
        if last_change is None:
            self.__last_change = self.shtime.now()
        else:
            self.__last_change = last_change

        self.__prev_update = self.__last_update
        self.__last_update = self.__last_change

        self.__prev_change_by = self.__changed_by
        self.__prev_update_by = self.__updated_by
        self.__changed_by = "{0}:{1}".format(caller, source)
        self.__updated_by = "{0}:{1}".format(caller, source)
        self.__triggered_by = "{0}:{1}".format(caller, source)

        if caller != "fader":
            # log every item change to standard logger, if level is DEBUG
            # log with level INFO, if 'item_change_log' is set in etc/smarthome.yaml
            self._change_logger("Item {} = {} via {} {} {}".format(self._path, value, caller, source, dest))

            # Write item value to log, if Item has attribute log_change set
            self._log_on_change(value, caller, source, dest)
        return


    def __update(self, value, caller='Logic', source=None, dest=None):
        try:
            value = self.cast(value)
        except:
            try:
                logger.warning('Item {}: value "{}" does not match type {}. Via {} {}'.format(self._path, value, self._type, caller, source))
            except:
                pass
            return

        self._lock.acquire()
        _changed = False
        trigger_source_details = self.__updated_by
        if value != self._value or self._enforce_change:
            _changed = True
            self._set_value(value, caller, source, dest, prev_change=None, last_change=None)
            trigger_source_details = self.__changed_by
            if caller != "fader":
                self._fading = False
                self._lock.notify_all()
        else:
            self.__prev_update = self.__last_update
            self.__last_update = self.shtime.now()
            self.__prev_update_by = self.__updated_by
            self.__updated_by = "{0}:{1}".format(caller, source)
        self._lock.release()

        # ms: call run_on_update() from here
        self.__run_on_update(value)
        if _changed or self._enforce_updates or self._type == 'scene':
            # ms: call run_on_change() from here -> noved down
            #self.__run_on_change(value)
            for method in self.__methods_to_trigger:
                try:
                    method(self, caller, source, dest)
                except Exception as e:
                    logger.exception("Item {}: problem running {}: {}".format(self._path, method, e))
            if self._threshold and self.__logics_to_trigger:
                if self.__th_crossed and self._value <= self.__th_low:  # cross lower bound
                    self.__th_crossed = False
                    self._threshold_data[2] = self.__th_crossed
                    self.__trigger_logics(trigger_source_details)
                elif not self.__th_crossed and self._value >= self.__th_high:  # cross upper bound
                    self.__th_crossed = True
                    self._threshold_data[2] = self.__th_crossed
                    self.__trigger_logics(trigger_source_details)
            elif self.__logics_to_trigger:
                self.__trigger_logics(trigger_source_details)
            for item in self._items_to_trigger:
                args = {'value': value, 'source': self._path}
                self._sh.trigger(name='items.' + item.id(), obj=item.__run_eval, value=args, by=caller, source=source, dest=dest)
            # ms: call run_on_change() from here - after eval is run
            self.__run_on_change(value)

        if _changed and self._cache and not self._fading:
            try:
                cache_write(self._cache, self._value)
            except Exception as e:
                logger.warning("Item: {}: could update cache {}".format(self._path, e))
        if self._autotimer and caller != 'Autotimer' and not self._fading:

            _time, _value = self._autotimer[0]
            compat = self._autotimer[1]
            if self._autotimer[2]:
                try:
                    _time = eval('self._sh.'+self._autotimer[2]+'()')
                except:
                    logger.warning("Item '{}': Attribute 'autotimer': Item '{}' does not exist".format(self._path, self._autotimer[2]))
            if self._autotimer[3]:
                try:
                    _value = self._castvalue_to_itemtype(eval('self._sh.'+self._autotimer[3]+'()'), compat)
                except:
                    logger.warning("Item '{}': Attribute 'autotimer': Item '{}' does not exist".format(self._path, self._autotimer[3]))
            self._autotimer[0] = (_time, _value)     # for display of active/last timer configuration in backend

            next = self.shtime.now() + datetime.timedelta(seconds=_time)
            self._sh.scheduler.add(self._itemname_prefix+self.id() + '-Timer', self.__call__, value={'value': _value, 'caller': 'Autotimer'}, next=next)


    def add_logic_trigger(self, logic):
        """
        Add a logic trigger to the item

        :param logic:
        :type logic:
        :return:
        """
        self.__logics_to_trigger.append(logic)

    def remove_logic_trigger(self, logic):
        self.__logics_to_trigger.remove(logic)

    def get_logic_triggers(self):
        """
        Returns a list of logics to trigger, if the item gets changed

        :return: Logics to trigger
        :rtype: list
        """
        return self.__logics_to_trigger

    def add_method_trigger(self, method):
        self.__methods_to_trigger.append(method)

    def remove_method_trigger(self, method):
        self.__methods_to_trigger.remove(method)

    def get_method_triggers(self):
        """
        Returns a list of item methods to trigger, if this item gets changed

        :return: methods to trigger
        :rtype: list
        """
        return self.__methods_to_trigger


    def timer(self, time, value, auto=False, compat=ATTRIB_COMPAT_DEFAULT, caller=None, source=None):
        time = self._cast_duration(time)
        value = self._castvalue_to_itemtype(value, compat)
        if auto:
            caller = 'Autotimer'
            self._autotimer = [(time, value), compat, None, None]
        else:
            caller = 'Timer'
        next = self.shtime.now() + datetime.timedelta(seconds=time)
        if source is None:
            self._sh.scheduler.add(self._itemname_prefix+self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller}, next=next)
        else:
            self._sh.scheduler.add(self._itemname_prefix+self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller, 'source': source}, next=next)


    def remove_timer(self):
        self._sh.scheduler.remove(self._itemname_prefix+self.id() + '-Timer')


    def autotimer(self, time=None, value=None, compat=ATTRIB_COMPAT_V12):
        if time is not None and value is not None:
            time = self._cast_duration(time)
            self._autotimer = [(time, value), compat, None, None]
        else:
            self._autotimer = False


    def fade(self, dest, step=1, delta=1):
        dest = float(dest)
        self._sh.trigger(self._path, fadejob, value={'item': self, 'dest': dest, 'step': step, 'delta': delta})

    def return_children(self):
        for child in self.__children:
            yield child

    def return_parent(self):
        return self.__parent


    def set(self, value, caller='Logic', source=None, dest=None, prev_change=None, last_change=None):
        """
        Set an Item value and optionally set prev_change and last_change timestamps

        (This method is called eg. by the database plugin to initialize items from the database on start)

        :param value:
        :param caller:
        :param source:
        :param dest:
        :param prev_change:
        :param last_change:
        :return:
        """
        try:
            value = self.cast(value)
        except:
            try:
                logger.warning("Item {}: value {} does not match type {}. Via {} {}".format(self._path, value, self._type, caller, source))
            except:
                pass
            return
        self._lock.acquire()
        self._set_value(value, caller, source, dest, prev_change, last_change)
        self._lock.release()
        return


    def get_children_path(self):
        return [item._path
                for item in self.__children]

    def jsonvars(self):
        """
        Translation method from object members to json
        :return: Key / Value pairs from object members
        """
        return { "id": self._path,
                 "name": self._name,
                 "value" : self._value,
                 "type": self._type,
                 "attributes": self.conf,
                 "children": self.get_children_path() }

# alternative method to get all class members
#    @staticmethod
#    def get_members(instance):
#        return {k: v
#                for k, v in vars(instance).items()
#                if str(k) in ["_value", "conf"] }
#                #if not str(k).startswith('_')}

    def to_json(self):
       return json.dumps(self.jsonvars(), sort_keys=True, indent=2)
