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

import inspect

import time             # for calls to time in eval
import math             # for calls to math in eval
from math import *


from lib.shtime import Shtime
import lib.env
from lib.plugin import Plugins


from lib.constants import (ITEM_DEFAULTS, FOO, KEY_ENFORCE_UPDATES, KEY_ENFORCE_CHANGE, KEY_CACHE, KEY_CYCLE, KEY_CRONTAB,
                           KEY_EVAL, KEY_EVAL_TRIGGER, KEY_TRIGGER, KEY_CONDITION, KEY_NAME, KEY_DESCRIPTION, KEY_TYPE,
                           KEY_STRUCT, KEY_REMARK, KEY_INSTANCE, KEY_VALUE, KEY_INITVALUE, PLUGIN_PARSE_ITEM,
                           KEY_AUTOTIMER, KEY_ON_UPDATE, KEY_ON_CHANGE, KEY_LOG_CHANGE, KEY_LOG_LEVEL, KEY_LOG_TEXT,
                           KEY_LOG_MAPPING, KEY_LOG_RULES, KEY_THRESHOLD, KEY_EVAL_TRIGGER_ONLY,
                           KEY_ATTRIB_COMPAT, ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST,
                           KEY_HYSTERESIS_INPUT, KEY_HYSTERESIS_UPPER_THRESHOLD, KEY_HYSTERESIS_LOWER_THRESHOLD,
                           ATTRIBUTE_SEPARATOR)


from lib.utils import Utils

from .property import Property
from .helpers import *

_items_instance = None


#ATTRIB_COMPAT_DEFAULT_FALLBACK = ATTRIB_COMPAT_V12
ATTRIB_COMPAT_DEFAULT_FALLBACK = ATTRIB_COMPAT_LATEST
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
        self._autotimer_time = None
        self._autotimer_value = None
        self._cycle_time = None
        self._cycle_value = None
        self._cache = False
        self.cast = cast_bool
        self.__changed_by = 'Init:None'
        self.__updated_by = self.__changed_by
        self.__triggered_by = 'N/A'
        self.__children = []
        self.conf = {}
        self._crontab = None
        self._enforce_updates = False
        self._enforce_change = False

        self._eval = None				    # -> KEY_EVAL
        self._eval_unexpanded = ''
        self._eval_trigger = False
        self._eval_on_trigger_only = False
        self._trigger = False
        self._trigger_unexpanded = []
        self._trigger_condition_raw = []
        self._trigger_condition = None

        self._hysteresis_input = None
        self._hysteresis_input_unexpanded = None
        self._hysteresis_upper_threshold = None
        self._hysteresis_lower_threshold = None
        self._hysteresis_upper_timer = None
        self._hysteresis_lower_timer = None
        self._hysteresis_upper_timer_active = False
        self._hysteresis_lower_timer_active = False
        self._hysteresis_active_timer_ends = None
        self._hysteresis_items_to_trigger = []
        self._hysteresis_log = False


        self._on_update = None				# -> KEY_ON_UPDATE eval expression
        self._on_change = None				# -> KEY_ON_CHANGE eval expression
        self._on_update_dest_var = None		# -> KEY_ON_UPDATE destination var (list: only filled if '=' syntax is used)
        self._on_change_dest_var = None		# -> KEY_ON_CHANGE destination var (list: only filled if '=' syntax is used)
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
        self._description = None
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

        if self._path.split('.')[-1] in dir(self):
            logger.warning(f'Item {self._path} has a name with collides with Item class member. Unexpected behaviour might occur, renaming the item is recommended.')

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

        self._filename = dict(config.items()).get('_filename', None)

        #############################################################
        # Item Attribute 'Type'
        #############################################################
        setattr(self, '_type', dict(config.items()).get(KEY_TYPE))
        if self._type is None:
            self._type = FOO  # Every item has a type, type is FOO, if not defined in item
        #__defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
        if self._type not in ITEM_DEFAULTS:
            logger.error(f"Item {self._path}: type '{self._type}' unknown. Please use one of: {', '.join(list(ITEM_DEFAULTS.keys()))}.")
            raise AttributeError
        self.cast = globals()['cast_' + self._type]

        #############################################################
        # Item Attributes
        #############################################################
        for attr, value in config.items():
            if not isinstance(value, dict):
                if attr in [KEY_NAME, KEY_DESCRIPTION, KEY_TYPE, KEY_STRUCT, KEY_VALUE, KEY_INITVALUE, KEY_EVAL_TRIGGER_ONLY]:
                    if attr == KEY_INITVALUE:
                        attr = KEY_VALUE
                    setattr(self, '_' + attr, value)
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

                elif attr in [KEY_EVAL]:
                    self._parse_eval_attribute(attr, value)
                elif attr in [KEY_EVAL_TRIGGER] or (self._use_conditional_triggers and attr in [KEY_TRIGGER]):  # cast to list
                    self._parse_eval_trigger_list_attribute(attr, value)

                elif (attr in [KEY_CONDITION]) and self._use_conditional_triggers:  # cast to list
                    if isinstance(value, list):
                        cond_list = []
                        for cond in value:
                            cond_list.append(dict(cond))
                        self._trigger_condition = self._build_trigger_condition_eval(cond_list)
                        self._trigger_condition_raw = cond_list
                    else:
                        logger.warning(f"Item __init__: {self._path}: Invalid trigger_condition specified! Must be a list")

                elif attr in [KEY_HYSTERESIS_INPUT]:
                    self._parse_hysteresis_input_attribute(attr, value)
                elif attr in [KEY_HYSTERESIS_UPPER_THRESHOLD, KEY_HYSTERESIS_LOWER_THRESHOLD]:
                    self._parse_hysteresis_xx_threshold_attribute(attr, value)
                elif attr == '_hysteresis_log':
                    self._hysteresis_log = value

                elif attr in [KEY_ON_CHANGE, KEY_ON_UPDATE]:
                    self._parse_on_xx_list_attribute(attr, value)

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
                        if value[0] != '_':
                            self._log_change_logger = logging.getLogger('items.'+value)
                        else:
                            self._log_change_logger = logging.getLogger(value[1:])
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
                    self._parse_autotimer_attribute(attr, value)

                elif attr == KEY_CYCLE:
                    self._parse_cycle_attribute(attr, value)

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
                    # at the moment only current, parent, grandparent and greatgrandparent items are supported
                    if (type(value) is str):
                        value = self._get_attribute_value(value, current_attr=attr, ignore_current_item=True)
                    self.conf[attr] = value
        # end of loop 'for attr, value in config.items()' - handling of all attributes of an item

        # test for attribute copy within the same item to ensure replace in every definition order of attributes
        for attr in self.conf:
            if str(self.conf[attr]).startswith('.:'):
                value = self.conf[attr]
                fromattr = value.split(':')[1]
                if fromattr in ['', '.']:
                    fromattr = attr
                value = self._get_attr(fromattr)
                self.conf[attr] = value

        # variable replacement for attributes
        for attr in dict(self.conf):
            if attr.endswith('_'):
                # Only for attributes which's name ends with an underline
                attr_value = str(self.conf[attr])
                while attr_value.find('{') > -1:
                    wrk = attr_value.split('{')[1]
                    if wrk.find('}') > -1:
                        # varname = attr_value.split('{')[1].split('}')[0]
                        varname = wrk.split('}')[0]
                        value = self._get_attribute_value(varname, current_attr=attr)
                        attr_value = attr_value.replace('{' + varname + '}', value)
                    else:
                        logger.warning(f"Item {self._path}, attribute {attr}: " + "Invalid var definition - '}' is missing")
                        break

                # store resolved attribute value under name w/o underline
                attr_new = attr[:-1]
                if attr_new == 'name':
                    self._name = attr_value
                    del self.conf[attr]
                else:
                    self.conf[attr_new] = attr_value
                    del self.conf[attr]

        # Test if attributes are defined in metadata
        for attr in self.conf:
            if hasattr(self.plugins, 'meta'):
                self.conf[attr] = self.plugins.meta.check_itemattribute(self, attr.split('@')[0], self.conf[attr], self._filename)


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
                self.__last_change, self._value = cache_read(self._cache, self.shtime.tzinfo())
                self._value = self.cast(self._value)
                self.__changed_by = 'Init:Cache'
                self.__prev_change = self.__last_change
                self.__updated_by = self.__changed_by
                self.__triggered_by = 'N/A'
                self.__last_update = self.__last_change
                self.__prev_update = self.__prev_change

                # Write item value to log, if Item has attribute log_change set
                self._log_on_change(self._value, self.__changed_by, 'Cache', None)
            except ValueError:
                logger.warning(f'Item {self._path}: cached value {self._value} does not match type {self._type}')
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

    def remove(self):
        """
        Cleanup item usage before item deletion
        Calls all plugins to remove the item and its references.
        :return: success
        :rtype: bool
        """
        incompatible = []

        for plugin in self.plugins.return_plugins():
            if hasattr(plugin, PLUGIN_REMOVE_ITEM):
                try:
                    plugin.remove_item(self)
                except Exception as e:
                    logger.warning(f"while removing item {self} from plugin {plugin}, the following error occurred: {e}")
            else:
                incompatible.append(plugin.get_shortname())

        if incompatible:
            logger.warning(f"while removing item {self}, the following plugins were incompatible: {', '.join(incompatible)}")
            return False

        return True

    def _get_attribute_value(self, attr_ref: str, current_attr: str, default: str='', ignore_current_item: bool=False) -> str:
        """
        Get the value of an other attribute using a relative reference

        at the moment only the current, parent, grandparent and greatgrandparent items are supported

        :param attr_ref: Reference to attribute
        :param ignore_current_item: Skip attributes of current item (needed in attr loop)

        :return: Value of the referenced attribute
        """
        value = attr_ref
        attr_ref = attr_ref.strip()
        if attr_ref.startswith( ('.:', '..:', '...:', '....:') ):
            fromitem = attr_ref.split(':')[0]
            fromattr = attr_ref.split(':')[1]
            if fromattr in ['', '.']:
                fromattr = current_attr
            if fromitem == '.':
                if not ignore_current_item:
                    value = self._get_attr(fromattr, default)
            elif fromitem == '..':
                value = self._get_attr_from_parent(fromattr, default)
            elif fromitem == '...':
                value = self._get_attr_from_grandparent(fromattr, default)
            elif fromitem == '....':
                value = self._get_attr_from_greatgrandparent(fromattr, default)
        return value


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


    def _castvalue_to_itemtype(self, value, compat=ATTRIB_COMPAT_LATEST):
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
                    logger.warning(f"Item {self._path}: Unable to cast '{str(value)}' to {self._type}")
                    if isinstance(value, list):
                        value = []
                    elif isinstance(value, dict):
                        value = {}
                    else:
                        value = mycast('')
            else:
                logger.warning(f"Item {self._path}: Unable to cast '{str(value)}' to {self._type}")
        return value


    def _cast_duration(self, time, test=False):
        """
        casts a time value string (e.g. '5m') to an integer (duration in seconds)
        used for autotimer, timer, cycle

        if 'test' is set to True the warning log message is suppressed

        supported formats for time parameter:
        - seconds as integer (45)
        - seconds as a string ('45')
        - seconds as a string, trailed by 's' (e.g. '45s')
        - minutes as a string, trailed by 'm' (e.g. '5m'), is converted to seconds (300)
        - hours as a string, trailed by 'h' (e.g. '2h'), is converted to seconds (7200)
        - a combination of the above (e.g. '2h5m45s')

        :param time: string containing the duration
        :param test: if set to True, no warning ist logged in case of an error, only False is returned
        :return: number of seconds as an integer
        """
        if isinstance(time, str):
            time_in_sec= self.shtime.to_seconds(time, test=True)
            if time_in_sec == -1:
                if not test:
                    logger.warning(f"Item {self._path} - _cast_duration: Unable to convert parameter 'time' to seconds (time={time})")
                time_in_sec = False
        elif isinstance(time, int):
            time_in_sec = int(time)
        elif isinstance(time, float):
            time_in_sec = int(time)
        else:
            if not test:
                logger.warning(
                    f"Item {self._path} - _cast_duration: Unable to convert parameter 'time' to int (time={time})")
            time_in_sec = False

        return (time_in_sec)


    def _cast_duration_old(self, time, test=False):

        if isinstance(time, str):
            try:
                time = time.strip()
                time_in_sec = 0

                wrk = time.split('h')
                if len(wrk) > 1:
                    time_in_sec += int(wrk[0]) * 60 * 60
                    time = wrk[1].strip()

                wrk = time.split('m')
                if len(wrk) > 1:
                    time_in_sec += int(wrk[0]) * 60
                    time = wrk[1].strip()

                wrk = time.split('s')
                if len(wrk) > 1:
                    time_in_sec += int(wrk[0])
                    #time = wrk[1].strip()
                elif wrk[0] != '':
                    time_in_sec += int(wrk[0])
            except Exception as e:
                if not test:
                    logger.warning(f"Item {self._path} - _cast_duration: (time={time}) - problem: {e}")
                time_in_sec = False

        elif isinstance(time, int):
            time_in_sec = int(time)
        elif isinstance(time, float):
            time_in_sec = int(time)
        else:
            if not test:
                logger.warning(f"Item {self._path} - _cast_duration: (time={time}) problem: unable to convert to int")
            time_in_sec = False
        return(time_in_sec)


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
    The following methods are used to process attributes during parsing of standard attributes
    --------------------------------------------------------------------------------------------
    """

    def _parse_eval_attribute(self, attribute_name, value):
        """
        Parsing eval attribute during parsing of standard attributes

        :param value: attribute from item configuration
        :param attribute_name: attribute name from item configuration

        :return: None
        """

        if value == '':
            self._eval_unexpanded = ''
            self._eval = None
        else:
            self._eval_unexpanded = value
            value = self.get_stringwithabsolutepathes(value, 'sh.', '(', attribute_name)
            #value = self.get_stringwithabsolutepathes(value, 'sh.', '.property', KEY_EVAL)
            self._eval = value


    def _parse_eval_trigger_list_attribute(self, attribute_name, value):
        """
        Parsing eval_trigger attribute during parsing of standard attributes

        :param value: attribute from item configuration
        :param attribute_name: attribute name from item configuration

        :return: None
        """
        if isinstance(value, str):
            value = [value, ]
        self._trigger_unexpanded = value
        expandedvalue = []
        for path in value:
            expandedvalue.append(self.get_absolutepath(path, attribute_name))
        self._trigger = expandedvalue


    def _parse_hysteresis_input_attribute(self, attribute_name, value):

        self._hysteresis_input_unexpanded = value
        self._hysteresis_input = self.get_absolutepath(value, attribute_name)


    def _parse_hysteresis_xx_threshold_attribute(self, attr, value):

        if value.find(ATTRIBUTE_SEPARATOR) == -1:
            threshold = self.get_stringwithabsolutepathes(value, 'sh.', '(', attr)
            timer = None
        else:
            threshold_unex, __, timer_unex = value.rpartition(ATTRIBUTE_SEPARATOR)
            threshold = self.get_stringwithabsolutepathes(threshold_unex.strip(), 'sh.', '(', attr)
            timer = self.get_stringwithabsolutepathes(timer_unex.strip(), 'sh.', '(', attr)

        if attr == KEY_HYSTERESIS_UPPER_THRESHOLD:
            self._hysteresis_upper_threshold = threshold
            self._hysteresis_upper_timer = timer
        elif attr == KEY_HYSTERESIS_LOWER_THRESHOLD:
            self._hysteresis_lower_threshold = threshold
            self._hysteresis_lower_timer = timer


    def _parse_on_xx_list_attribute(self, attr, value):

        if isinstance(value, str):
            value = [value]
        val_list = []
        val_list_unexpanded = []
        dest_var_list = []
        dest_var_list_unexp = []
        for val in value:
            # separate destination item (if it exists)
            dest_item, val = self._split_destitem_from_value(val)
            dest_item = dest_item.strip()
            if dest_item.startswith('sh.'):
                dest_item = dest_item[3:]
            dest_var_list_unexp.append(dest_item.strip())
            # expand relative item paths
            dest_item = self.get_absolutepath(dest_item.strip()).strip()
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


    def _parse_cycle_attribute(self, attr, value):

        cycle_time, cycle_value, compat = split_duration_value_string(value, ATTRIB_COMPAT_DEFAULT)
        self._cycle_time = self.get_stringwithabsolutepathes(cycle_time, 'sh.', '(', attr)
        self._cycle_value = self.get_stringwithabsolutepathes(cycle_value, 'sh.', '(', attr)
        #logger.notice(f"_parse_cycle_attribute: {self._path} - value={value} -> _cycle_time={self._cycle_time}, _cycle_value={self._cycle_value}")


    def _parse_autotimer_attribute(self, attr, value):

        auto_time, auto_value, compat = split_duration_value_string(value, ATTRIB_COMPAT_DEFAULT)
        self._autotimer_time = self.get_stringwithabsolutepathes(auto_time, 'sh.', '(', attr)
        self._autotimer_value = self.get_stringwithabsolutepathes(auto_value, 'sh.', '(', attr)
        #logger.notice(f"_parse_autotimer_attribute: {self._path} - value={value} -> _autotimer_time={self._autotimer_time}, _autotimer_value={self._autotimer_value}")


    """
    --------------------------------------------------------------------------------------------
    END of methods to process attributes during parsing of standard attributes
    --------------------------------------------------------------------------------------------
    """

    def _build_on_xx_list(self, on_dest_list, on_eval_list):
        """
        build on_xx data   (seens to be never called???)
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
        Old method name - Use item.property.path instead of item.property.path
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


    def _get_attr(self, attr, default=''):
        """
        Get attribute value from actual item

        :param attr: Get the value from this attribute of the parent item
        :return: value from attribute of parent item
        """
        pitem = self
        pattr_value = pitem.conf.get(attr, default)
        return pattr_value


    def _get_attr_from_parent(self, attr, default=''):
        """
        Get attribute value from parent item

        :param attr: Get the value from this attribute of the parent item
        :return: value from attribute of parent item
        """
        pitem = self.return_parent()
        pattr_value = pitem.conf.get(attr, default)
        return pattr_value


    def _get_attr_from_grandparent(self, attr, default=''):
        """
        Get attribute value from grandparent item

        :param attr: Get the value from this attribute of the grandparent item
        :return: value from attribute of grandparent item
        """
        pitem = self.return_parent()
        gpitem = pitem.return_parent()
        gpattr_value = gpitem.conf.get(attr, default)
        return gpattr_value


    def _get_attr_from_greatgrandparent(self, attr, default=''):
        """
        Get attribute value from grandparent item

        :param attr: Get the value from this attribute of the grandparent item
        :return: value from attribute of grandparent item
        """
        pitem = self.return_parent()
        gpitem = pitem.return_parent()
        ggpitem = gpitem.return_parent()
        ggpattr_value = ggpitem.conf.get(attr, default)
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


    def __call__(self, value=None, caller='Logic', source=None, dest=None, key=None, index=None, default=None):
        # return value
        if value is None or self._type is None:
            if key is not None and self._type == 'dict':
                return self.__get_dictentry(key, default)
            elif index is not None and self._type == 'list':
                return self.__get_listentry(index, default)
            return copy.deepcopy(self._value)

        # set value
        if self._eval:
            args = {'value': value, 'caller': caller, 'source': source, 'dest': dest}
            self._sh.trigger(name=self._path + '-eval', obj=self.__run_eval, value=args, by=caller, source=source, dest=dest)
        else:
            self.__update(value, caller, source, dest, key, index)


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


    def __get_listentry(self, index, default):
        if isinstance(index, int):
            try:
                return self._value[index]
            except Exception as e:
                if default is None:
                    msg = f"Item '{self._path}': Cannot access list entry (index={index}) : {e}"
                    logger.warning(msg)
                    raise ValueError(msg)  # needed additionally to show error message in eval syntax checker
            return default
        else:
            msg = f"Item '{self._path}': Cannot access list entry: 'index' must be an integer not a {str(type(index)).split(chr(39))[1]} value ({index})"
            logger.warning(msg)
            raise TypeError(msg)  # needed additionally to show error message in eval syntax checker


    def __set_listentry(self, value, index):
        # Update a list item element (selected by index)
        if isinstance(index, str):
            if index.lower() == 'append':
                valuelist = copy.deepcopy(self._value)
                valuelist.append(value)
                return valuelist
            elif index.lower() == 'prepend':
                valuelist = copy.deepcopy(self._value)
                valuelist.insert(0, value)
                return valuelist
        if isinstance(index, int):
            valuelist = copy.deepcopy(self._value)
            try:
                valuelist[index] = value
            except Exception as e:
                msg = f"Item '{self._path}': Cannot access list entry (index={index}) : {e}"
                logger.warning(msg)
                raise ValueError(msg)  # needed additionally to show error message in eval syntax checker
            return valuelist
        else:
            msg = f"Item '{self._path}': Cannot access list entry: 'index' must be an integer not a {str(type(index)).split(chr(39))[1]} value ({index})"
            logger.warning(msg)
            raise TypeError(msg)  # needed additionally to show error message in eval syntax checker


    def get_class_from_frame(self, fr):
        # https://stackoverflow.com/questions/2203424/python-how-to-retrieve-class-information-from-a-frame-object
        #import inspect
        args, _, _, value_dict = inspect.getargvalues(fr)
        # we check the first parameter for the frame function is
        # named 'self'
        if len(args) and args[0] == 'self' and False:    # Don't execute this if-branch
            # in that case, 'self' will be referenced in value_dict
            instance = value_dict.get('self', None)
            if instance:
                # return its class
#                return getattr(instance, '__class__', None)
                return getattr(instance, '__class__', f"args={args}  - value_dict={value_dict}")
        # return None otherwise
        return f"args={args}  - value_dict={value_dict}"

    def get_calling_item_from_frame(self, fr):
        # Info from: https://stackoverflow.com/questions/2203424/python-how-to-retrieve-class-information-from-a-frame-object
        # import inspect
        args, _, _, value_dict = inspect.getargvalues(fr)
        # we check the first parameter for the frame function is
        # named 'self'
        if len(args) and args[0] == 'self' and False:
            # in that case, 'self' will be referenced in value_dict
            instance = value_dict.get('self', None)
            if instance:
                return getattr(instance, '__class__', f"args={args}  - value_dict={value_dict}")
        return f"{value_dict.get('self', None)}"

    def get_stack_info(self):

        # msg = "call stack:"
        #msg += f" {inspect.stack()[1][3]}() / {inspect.stack()[2][3]}() / {inspect.stack()[3][3]}() / {inspect.stack()[4][4]}() / {inspect.stack()[5][5]}()"
        for level in range(4,5):
            msg = ''
            try:
                # f_code.__class__.__name__ == 'code'
                # f_code.__class__.__class__.__name__ == 'type'
                #msg += f" - f_code={inspect.stack()[level].frame.f_code}   -  classname={inspect.stack()[level].frame.f_code.__class__.__class__.__class__.__name__}   -   dir(__class__.__class__.__class__)={dir(inspect.stack()[level].frame.f_code.__class__.__class__.__class__)}"
                if inspect.stack()[level].function == '__run_eval':
                    msg += f"Item '{self.get_calling_item_from_frame(inspect.stack()[level].frame)}'"
                else:
                    msg += f"{inspect.stack()[level].function}()"
            except Exception as ex:
                msg += f" - error getting code {ex}"

        return msg


    def __get_dictentry(self, key, default):
        try:
            return self._value[key]
        except Exception as e:
            if default is None:
                msg = f"Item '{self._path}': {e.__class__.__name__}: {e}"
                stack_info = self.get_stack_info()
                if stack_info.startswith('Item'):
                    msg += f"  -  called from: {self.get_stack_info()}"
                logger.info(msg)
                raise KeyError(msg)  # msg needed to show error message in eval syntax checker
        return default


    def __set_dictentry(self, value, key):
        # Update a dict item element (selected by key) or add an element, if the key does not exist
        valuedict = copy.deepcopy(self._value)
        valuedict[key] = value
        return valuedict


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
                    logger.warning(f"item '{self._path}': trigger item '{trigger}' not found for function '{self._eval}'")
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

        if self._hysteresis_input:
            # Only if item has a hysteresis_input attribute
            triggering_item = _items_instance.return_item(self._hysteresis_input)
            if triggering_item is None: # triggering item was not found
                logger.error(f"item '{self._path}': trigger item '{self._hysteresis_input}' not found for function 'hysteresis'")
            #elif self._hysteresis_upper_threshold < self._hysteresis_lower_threshold:
            #    logger.error(f"item '{self._path}': Hysteresis upper threshod is lower than lower threshod")
            else:
                if triggering_item != self:  # prevent loop
                    if self._hysteresis_log:
                        logger.notice(f"_init_prerun: Adding to triggering_item {self}")
                    triggering_item._hysteresis_items_to_trigger.append(self)


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
        if self._crontab is not None or self._cycle_time is not None:
            cycle = None
            if self._cycle_time is not None:
                #cycle = self._build_cycledict(cycle)
                if self._cycle_value is None:
                    cycle = {self._cast_duration(self._cycle_time): self._value}
                else:
                    cycle = {self._cast_duration(self._cycle_time): self._cycle_value}
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
                self._sh.trigger(name=self._path, obj=self.__run_eval, by='Init', source='_init_run', value={'value': self._value, 'caller': 'Init:Eval'})
                return True
        return False


    def __run_attribute_eval(self, eval_expression, result_type='num'):
        """
        Evaluates an expression string for item attributes like
         - autotimer
         - cycle
         - hysteresis_upper_threshold
         - hysteresis_lower_threshold

        :param eval_expression: string to evaluate
        :param result_type: type for the result (num | str)
        :return:
        """

        # set up environment for calculating eval-expression
        sh = self._sh
        shtime = self.shtime
        items = _items_instance
        import math
        import lib.userfunctions as uf
        env = lib.env

        eval_expression = str(eval_expression)
        try:
            result = eval(eval_expression)
        except Exception as e:
            logger.error(f"Item '{self._path}': __run_attribute_eval({eval_expression}): Problem evaluating '{eval_expression}' - Exception {e}")
            result = ''
        if result_type == 'num':
            if not isinstance(result, (int, float)):
                logger.error(f"Item '{self._path}': __run_attribute_eval({eval_expression}): Attribute expression '{eval_expression}' evaluated to a non-numeric value '{result}', using 0 instead")
                result = 0

        return result


    def __run_hysteresis(self, value=None, caller='Hysteresis', source=None, dest=None):
        """
        evaluate the 'hysteresis' entry of the actual item
        """
        upper = self.__run_attribute_eval(self._hysteresis_upper_threshold)
        lower = self.__run_attribute_eval(self._hysteresis_lower_threshold)

        if self._hysteresis_upper_timer_active and (value <= upper):
            self._sh.scheduler.remove(self._itemname_prefix + self.id() + '-UpTimer')
            self._hysteresis_upper_timer_active = False
            self._hysteresis_active_timer_ends = None
        if self._hysteresis_lower_timer_active and (value >= lower):
            self._sh.scheduler.remove(self._itemname_prefix + self.id() + '-LoTimer')
            self._hysteresis_lower_timer_active = False
            self._hysteresis_active_timer_ends = None

        if value > upper:
            if self._hysteresis_upper_timer is None:
                self.__update(True, caller, source, dest)
            else:
                if not self._hysteresis_upper_timer_active and (self._value == False): ###ms value = self._value
                    timer = self.__run_attribute_eval(self._hysteresis_upper_timer)
                    if timer < 0:
                        logger.warning(f"Item '{self._path}': Hysteresis upper-timer evaluated to an value less than zero ({timer}), using 0 instead")
                        timer = 0
                    self._hysteresis_upper_timer_active = True
                    next = self.shtime.now() + datetime.timedelta(seconds=timer)
                    self.active_timer_ends = next
                    #next = self.shtime.now() + datetime.timedelta(seconds=self._hysteresis_upper_timer)
                    if self._hysteresis_log:
                        logger.notice(f"__run_hysteresis {self._path}: scheduler.add {self._path}-UpTimer")
                    self._sh.scheduler.add(self._itemname_prefix+self.id() + '-UpTimer', self.__call__, value={'value': True, 'caller': 'Hysteresis'}, next=next)

        if value < lower:
            if self._hysteresis_lower_timer is None:
                self.__update(False, caller, source, dest)
            else:
                if not self._hysteresis_lower_timer_active and (self._value == True):
                    timer = self.__run_attribute_eval(self._hysteresis_lower_timer)
                    if timer < 0:
                        logger.warning(f"Item '{self._path}': Hysteresis lower-timer evaluated to an value less than zero ({timer}), using 0 instead")
                        timer = 0
                    self._hysteresis_lower_timer_active = True
                    next = self.shtime.now() + datetime.timedelta(seconds=timer)
                    self._hysteresis_active_timer_ends = next
                    #next = self.shtime.now() + datetime.timedelta(seconds=self._hysteresis_lower_timer)
                    if self._hysteresis_log:
                        logger.notice(f"__run_hysteresis {self._path}: scheduler.add {self._path}-LoTimer")
                    self._sh.scheduler.add(self._itemname_prefix + self.id() + '-LoTimer', self.__call__, value={'value': False, 'caller': 'Hysteresis'}, next=next)
        return


    def _onoff(self, value: bool) -> str:
        if value:
            return 'On'
        return 'Off'

    def _get_hysterisis_state_string(self, lower: float, upper: float, input_value: float, log: bool=False, txt: str='') -> str:
        """
        Helper method to return the inner hysteresis-state as a readable string

        TODO: Return right state, if value is from init:cache

        :param lower: hysteresis lower threshold
        :param upper: hysteresis upper threshold
        :param input_value: hysteresis input

        :return: hysteresis-state as a readable string
        """

        if log:
            logger.notice(f"{self._path}: {txt}")
        state = ''
        if input_value > upper:
            if self._hysteresis_upper_timer_active:
                state = 'Timer -> '
            state += 'On'
            if log:
                logger.notice(f" -> {state} - {txt}")
        elif input_value < lower:
            if self._hysteresis_lower_timer_active:
                state = 'Timer -> '
            state += 'Off'
            if log:
                logger.notice(f" -> {state} - {txt}")
        else:
            state = 'Stay (' + self._onoff(self._value) + ')'
            if log:
                logger.notice(f" -> {state} - {txt}")

        if not (self._hysteresis_upper_timer_active) and not (self._hysteresis_lower_timer_active):
            if self.__updated_by.lower() == 'init:cache':
                if not state.startswith('Stay'):
                    if state != self._onoff(self._value):
                        state = 'Cached (' + self._onoff(self._value) + ')'
                        if log:
                            logger.notice(f" -> {state} - {txt}")

        return state


    def hysteresis_state(self):
        """
        Return the inner hysteresis_state

        Available in SmartHomeNG v1.10 and above

        TODO: Return right state, if value is from init:cache

        :return: hysteresis state of the item
        :rtype: str
        """
        time.sleep(0.1)     # to prevent execution before xxx_timer_active could be updated

        upper = self.__run_attribute_eval(self._hysteresis_upper_threshold)
        lower = self.__run_attribute_eval(self._hysteresis_lower_threshold)
        input_value = _items_instance.return_item(self._hysteresis_input)()

        state = self._get_hysterisis_state_string(lower, upper, input_value, log=self._hysteresis_log, txt='hysteresis_state')

        if self._hysteresis_log:
            logger.notice(f"hysteresis_state ({self._path}): state={state}, input_value={input_value}, value={self._value}, __updated_by={self.__updated_by}")
        return state


    def hysteresis_data(self):
        """
        Return the inner hysteresis_state

        returns a dict with the current hysteresis data
        (lower threshold, upper threshold, input value, output value and internal state)

        Available in SmartHomeNG v1.10 and above

        :return: hysteresis state of the item
        :rtype: dict
        """
        time.sleep(0.1)     # to prevent execution before xxx_timer_active could be updated

        upper = self.__run_attribute_eval(self._hysteresis_upper_threshold)
        if self._hysteresis_upper_timer is None:
            upper_timer = self._hysteresis_upper_timer
        else:
            upper_timer = self.__run_attribute_eval(self._hysteresis_upper_timer)
        lower = self.__run_attribute_eval(self._hysteresis_lower_threshold)
        if self._hysteresis_lower_timer is None:
            lower_timer = self._hysteresis_lower_timer
        else:
            lower_timer = self.__run_attribute_eval(self._hysteresis_lower_timer)
        input_value = _items_instance.return_item(self._hysteresis_input)()

        state = self._get_hysterisis_state_string(lower, upper, input_value, log=self._hysteresis_log, txt='hysteresis_data')

        data = {'lower_threshold': lower, 'lower_timer': lower_timer, 'upper_threshold': upper, 'upper_timer': upper_timer, 'input': input_value, 'output': self._value, 'state': state, 'lower_timer_active': self._hysteresis_lower_timer_active, 'upper_timer_active': self._hysteresis_upper_timer_active}
        if (self._hysteresis_lower_timer_active or self._hysteresis_upper_timer_active) and self._hysteresis_active_timer_ends is not None:
            data['active_timer_ends'] = self._hysteresis_active_timer_ends.strftime("%d.%m.%Y %H:%M:%S") + " " + self._hysteresis_active_timer_ends.tzname()
        if self._hysteresis_log:
            logger.notice(f"hysteresis_data ({self._path}): {data}, __updated_by={self.__updated_by}")
        return data


    def __run_eval(self, value=None, caller='Eval', source=None, dest=None):
        """
        evaluate the 'eval' entry of the actual item
        """
        if caller.lower().startswith('admin:'):
            caller = caller[6:] + ':admin'
        if (not caller.lower().startswith('eval:')) and (not caller.lower().endswith(':eval')):
            caller = 'Eval:' + caller

        if (self._sh.shng_status['code'] < 14):
            # items are not (completly) loaded
            logger.dbghigh(f"Item {self._path}: Running __run_eval before initialization is finished - eval run ignored- caller={caller}, source={source}  -  shng_status{self._sh.shng_status}")
            return
        if (self._sh.shng_status['code'] < 20) and (not caller.startswith('Init')):
            logger.info(f"Item {self._path}: Running __run_eval before initialization is finished - caller={caller}, source={source}, value={value}  -  shng_status{self._sh.shng_status}")
        if (self._sh.shng_status['code'] > 20):
            logger.info(f"Item {self._path}: Running __run_eval after leaving run-mode - caller={caller}, source={source}, value={value}  -  shng_status{self._sh.shng_status}")

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
                    env = lib.env

                    cond = eval(self._trigger_condition)
                    logger.warning(f"Item '{self._path}': Condition result '{cond}' evaluating trigger condition {self._trigger_condition}")
                except Exception as e:
                    log_msg = f"Item '{self._path}': Problem evaluating trigger condition '{self._trigger_condition}': {e}"
                    if (self._sh.shng_status['code'] != 20) and (caller != 'Init'):
                        logger.debug(log_msg)
                    else:
                        logger.warning(log_msg)
                    return
            else:
                cond = True

            if cond == True:
                # set up environment for calculating eval-expression
                sh = self._sh
                shtime = self.shtime
                items = _items_instance
                import math
                import lib.userfunctions as uf
                # uf.import_user_modules()  -  Modules were loaded during initialization phase of shng
                env = lib.env

                try:
                    self.__prev_trigger_by = self.__triggered_by
                    self.__triggered_by = "{0}:{1}".format(caller, source)
                    self.__prev_trigger = self.__last_trigger
                    self.__last_trigger = self.shtime.now()

                    try:
                        triggered = source in self._trigger
                    except:
                        triggered = False

                    if self._eval_on_trigger_only and not triggered:
                        # logger.debug(f'Item {self._path} Eval triggered by: {self.__triggered_by}, not in eval triggers {self._trigger}, but eval_on_trigger only set, so eval is ignored. Value is "{value}"')
                        logger.info(f'Item {self._path} Eval triggered by: {self.__triggered_by}, not in eval_triggers, but eval_on_trigger_only set. Ignoring eval expression, setting value "{value}"')
                    else:
                        logger.debug(f"Item {self._path} Eval triggered by: {self.__triggered_by}, Evaluating item with value {value}. Eval expression: {self._eval}")

                        # ms if contab: init = x is set, x is transfered as a string, for that case re-try eval with x converted to float
                        try:
                            value = eval(self._eval)
                        except Exception as e:
                            #value = self._value = self.cast(value)
                            value = self.cast(value)
                            value = eval(self._eval)
                        # ms end
                except Exception as e:
                    # adding "None" as the "destination" information at end of triggered_by
                    # This helps figuring out whether an eval expression was successfully evaluated or not.
                    self.__triggered_by = f"{caller}:{source}:None"
                    if e.__class__.__name__ == 'KeyError':
                        log_msg = f"Item '{self._path}': problem evaluating '{self._eval}' - KeyError (in dict)"
                    else:
                        log_msg = f"Item '{self._path}': problem evaluating '{self._eval}' - {e.__class__.__name__}: {e}"
                    if (self._sh.shng_status['code'] != 20) and (caller != 'Init'):
                        logger.debug(log_msg + " (status_code={}/caller={})".format(self._sh.shng_status['code'], caller))
                    else:
                        logger.warning(log_msg)
                else:
                    if value is None:
                        logger.debug(f"Item {self._path}: evaluating {self._eval} returns None")
                    else:
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
        env = lib.env

        logger.info(f"Item '{self._path}': '{attr}' evaluating {on_dest} = {on_eval}")

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
            logger.warning(f"Item {self._path}: '{attr}' item-value='{value}' problem evaluating {on_eval}: {e}")
        else:
            if dest_value is not None:
                # expression computes and does not result in None
                if on_dest != '':
                    dest_item = _items_instance.return_item(on_dest)
                    if dest_item is not None:
                        dest_item.__update(dest_value, caller=attr, source=self._path)
                        logger.debug(" - : '{}' finally evaluating {} = {}, result={}".format(attr, on_dest, on_eval, dest_value))
                    else:
                        logger.error(f"Item {self._path}: '{attr}' has not found dest_item '{on_dest}' = {on_eval}, result={dest_value}")
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
        id = self._path
        if self.__parent == _items_instance:
            pname = None
            pid = None
        else:
            pname = self.__parent._name
            pid = self.__parent._path
        mvalue = self._log_mapping.get(value, value)
        lowlimit = self._get_rule('lowlimit')
        highlimit = self._get_rule('highlimit')
        filter = self._get_rule('filter')
        exclude = self._get_rule('exclude')

        sh = self._sh
        shtime = self.shtime
        time = shtime.now().strftime("%H:%M:%S")
        date = shtime.now().strftime("%d.%m.%Y")
        stamp = shtime.now().timestamp()
        now = str(shtime.now())

        items = _items_instance
        try:
            entry = self._log_rules.get('itemvalue', None)
            if entry is not None:
                item = self.get_absolutepath(entry.strip().replace("sh.", ""), "log_rules")
                itemvalue = str(_items_instance.return_item(item).property.value)
            else:
                itemvalue = None
        except Exception as e:
            logger.error(f"{id}: Invalid item in log_text '{self._log_text}'"
                         f" or log_rules '{self._log_rules}' - (Exception: {e})")
            itemvalue = "INVALID"

        import math
        import lib.userfunctions as uf
        env = lib.env

        try:
            #logger.warning(f"self._log_text: {self._log_text}, type={type(self._log_text)}")
            txt = eval(f"f'{self._log_text}'")
        except Exception as e:
            logger.error(f"{id}: Invalid log_text template ' {self._log_text}' - (Exception: {e})")
            txt = self._log_text
        return txt


    def _get_rule(self, rule_entry):
        def convert_entry(entry, to):
            returnvalue = entry
            if isinstance(returnvalue, str) and to != "str":
                try:
                    # try to get value from item
                    item = self.get_absolutepath(entry.strip().replace("sh.", ""), "log_rules")
                    returnvalue = _items_instance.return_item(item).property.value
                except Exception as e:
                    pass
            if isinstance(returnvalue, (str, int)) and to == "num":
                try:
                    returnvalue = float(returnvalue)
                except ValueError as e:
                    returnvalue = None
            elif isinstance(entry, list):
                entry = [convert_entry(val, self._type) for val in entry]
            elif isinstance(returnvalue, (float, int)) and to == "str":
                returnvalue = str(returnvalue)
            if returnvalue is None:
                logger.warning(f"Given log_rules entry '{entry}' is invalid.")
            return returnvalue

        defaults = {'filter': [], 'exclude': [], 'lowlimit': None, 'highlimit': None}
        types = {'filter': 'list', 'exclude': 'list', 'lowlimit': 'num', 'highlimit': 'num'}
        entry =  self._log_rules.get(rule_entry, defaults.get(rule_entry))
        if entry is not None and entry != []:
            entry = convert_entry(entry, types.get(rule_entry) or self._type)

        return entry

    def _log_on_change(self, value, caller, source=None, dest=None):
        """
        Write log, if Item has attribute log_change set
        :return:
        """

        if self._log_change_logger is not None:
            filter_list = self._get_rule('filter')
            exclude_list = self._get_rule('exclude')
            if filter_list != [] and exclude_list != []:
                logger.warning(f"Defining filter AND exclude does not work. "
                               f"Ignoring exclude list {exclude_list} "
                               f"Using filter: {filter_list}")

            if self._type == 'num':
                low_limit =  self._get_rule('lowlimit')
                if low_limit is not None:
                    if low_limit > float(value):
                        return
                high_limit =  self._get_rule('highlimit')
                if high_limit is not None:
                    if high_limit <= float(value):
                        return
                if filter_list != []:
                    if not float(value) in filter_list:
                        return
                elif exclude_list != []:
                    if float(value) in exclude_list:
                        return
            else:
                if filter_list != []:
                    if not value in filter_list:
                        return
                elif exclude_list != []:
                    if value in exclude_list:
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


    def __update(self, value, caller='Logic', source=None, dest=None, key=None, index=None):

        # special handling, if item is a hysteresys item (has a hysteresis_input attribute)
        if self._hysteresis_input is not None:
            if self._hysteresis_upper_timer_active:
                if self._hysteresis_log:
                    logger.notice(f"__update: upper_timer caller={caller}, value={value}")
                self._hysteresis_upper_timer_active = False
                self.active_timer_ends = None
            if self._hysteresis_lower_timer_active:
                self._hysteresis_lower_timer_active = False
                self.active_timer_ends = None
                if self._hysteresis_log:
                    logger.notice(f"__update: lower_timer caller={caller}, value={value}")

        if key is None and index is None:
            # don't cast for elements of complex types
            try:
                value = self.cast(value)
            except:
                try:
                    logger.warning(f'Item {self._path}: value "{value}" does not match type {self._type}. Via caller {caller}, source {source}')
                except:
                    pass
                return

        self._lock.acquire()
        _changed = False
        trigger_source_details = self.__updated_by


        if key is not None and self._type == 'dict':
            # Update a dict item element or add an element (selected by key)
            value = self.__set_dictentry(value, key)
        elif index is not None and self._type == 'list':
            # Update a list item element (selected by index)
            value = self.__set_listentry(value, index)

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
                self._sh.trigger(name='items.' + item.property.path, obj=item.__run_eval, value=args, by=caller, source=source, dest=dest)
            for item in self._hysteresis_items_to_trigger:
                args = {'value': value, 'source': self._path}
                self._sh.trigger(name='items.' + item.property.path, obj=item.__run_hysteresis, value=args, by=caller, source=source, dest=dest)
            # ms: call run_on_change() from here - after eval is run
            self.__run_on_change(value)

        if _changed and self._cache and not self._fading:
            try:
                cache_write(self._cache, self._value)
            except Exception as e:
                logger.warning("Item: {}: could not update cache {}".format(self._path, e))

        if self._autotimer_time and caller != 'Autotimer' and not self._fading:
            # cast_duration for fixed attribute
            _time = self._cast_duration(self._autotimer_time, test=True)
            if _time == False:
                _time = self._autotimer_time
            # cast_duration for result of eval expression
            _time = self._cast_duration(self.__run_attribute_eval(_time, 'str'))
            if self._autotimer_value is None:
                _value = self._value
            else:
                _value = self.__run_attribute_eval(self._autotimer_value, 'str')

            #logger.notice(f"Item {self._path} __update: _time={_time}, _value={_value}")

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
        Returns a list of plugin methods to trigger, if this item gets changed

        :return: methods to trigger
        :rtype: list
        """
        return self.__methods_to_trigger


    def get_item_triggers(self):
        """
        Returns a list of items to trigger, if this item gets changed

        :return: methods to trigger
        :rtype: list
        """
        return self._items_to_trigger


    def get_hysteresis_item_triggers(self):
        """
        Returns a list of items to trigger, if this item gets changed

        :return: methods to trigger
        :rtype: list
        """
        return self._hysteresis_items_to_trigger


    def timer(self, time, value, auto=False, caller=None, source=None, compat=ATTRIB_COMPAT_LATEST):
        """
        Starts a timer for this item

        :param time: Duration till the value of the item is set
        :param value: Value the item should be set to
        :param auto: Optional: If False a single timer is started, else the duration/value information is set as an autotimer
        :param caller: Optional: The caller of this function
        :param source: Optional: The source of the timer-request
        :param compat: Not used anymore, only defined for backward compatibility
        """
        time = self._cast_duration(time)
        value = self._castvalue_to_itemtype(value, compat)
        if caller is None:
            if auto:
                caller = 'Autotimer'
                self._autotimer_time = time
                self._autotimer_value = value
            else:
                caller = 'Timer'
        next = self.shtime.now() + datetime.timedelta(seconds=time)
        if source is None:
            self._sh.scheduler.add(self._itemname_prefix+self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller}, next=next)
        else:
            self._sh.scheduler.add(self._itemname_prefix+self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller, 'source': source}, next=next)
        return


    def remove_timer(self):
        """
        Remove a running timer for this item from the scheduler
        """
        self._sh.scheduler.remove(self._itemname_prefix+self.id() + '-Timer')
        return


    def autotimer(self, time=None, value=None, compat=ATTRIB_COMPAT_LATEST):
        """
        Defines or removes an autotimer for the item

        If time and value are not given (or None), an existing autotimer is removed

        :param time: Time until the value is set
        :param value: Value to set the item to
        :param compat: Not used anymore, only defined for backward compatibility
        """
        if time is not None and value is not None:
            time = self._cast_duration(time)
            self._autotimer_time = time
            self._autotimer_value = value
        else:
            self._autotimer_time = None
            self._autotimer_value = None


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
