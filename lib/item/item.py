#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2020   Martin Sinn                         m.sinn@gmx.de
# Copyright 2016        Christian Straßburg           c.strassburg@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
# Copyright 2025        Bernd Meiners
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

from __future__ import annotations  # noqa: I001
from typing import Any

import logging
import datetime
import os
import copy
import json
import threading
import ast
import re
import sys

import inspect

import dateutil.tz as _tz

from lib.shtime import Shtime
import lib.env
from lib.plugin import Plugins


from lib.constants import (
    ITEM_DEFAULTS,
    FOO,
    KEY_ENFORCE_UPDATES,
    KEY_ENFORCE_CHANGE,
    KEY_CACHE,
    KEY_CYCLE,
    KEY_CRONTAB,
    KEY_EVAL,
    KEY_EVAL_TRIGGER,
    KEY_TRIGGER,
    KEY_CONDITION,
    KEY_NAME,
    KEY_DESCRIPTION,
    KEY_TYPE,
    KEY_STRUCT,
    KEY_REMARK,
    KEY_INSTANCE,
    KEY_VALUE,
    KEY_INITVALUE,
    PLUGIN_PARSE_ITEM,
    KEY_AUTOTIMER,
    KEY_ON_UPDATE,
    KEY_ON_CHANGE,
    KEY_LOG_CHANGE,
    KEY_LOG_LEVEL,
    KEY_LOG_TEXT,
    KEY_LOG_MAPPING,
    KEY_LOG_RULES,
    KEY_LOG_RULES_LOWLIMIT,
    KEY_LOG_RULES_HIGHLIMIT,
    KEY_LOG_RULES_FILTER,
    KEY_LOG_RULES_EXCLUDE,
    KEY_LOG_RULES_ITEMVALUE,
    KEY_THRESHOLD,
    KEY_EVAL_TRIGGER_ONLY,
    KEY_ATTRIB_COMPAT,
    ATTRIB_COMPAT_V12,
    ATTRIB_COMPAT_LATEST,
    PLUGIN_REMOVE_ITEM,
    KEY_HYSTERESIS_INPUT,
    KEY_HYSTERESIS_UPPER_THRESHOLD,
    KEY_HYSTERESIS_LOWER_THRESHOLD,
    ATTRIBUTE_SEPARATOR,
)


from lib.utils import Utils

from .property import Property
from .helpers import (  # noqa - cast_foo methods are accessed via globals()
    cast_str,
    cast_list,
    cast_dict,
    cast_foo,
    cast_bool,
    cast_scene,
    cast_num,
    split_duration_value_string,
    cache_read,
    cache_write,
    fadejob,
    cast_timestamp,
    cast_datetime,
)
from ._internal._typehandler import TypeHandler, ListHandler, DictHandler, HANDLER_MAP  # noqa: F401
from ._internal._history import ItemHistory
from ._internal._logchange import log_on_change
from ._internal._eval import run_eval, run_on_xxx, run_on_update, run_on_change
from ._internal._hysteresis import run_hysteresis, get_hysteresis_state, get_hysteresis_data
from ._internal._pathresolution import (
    get_absolutepath as _get_absolutepath,
    get_stringwithabsolutepathes as _get_stringwithabsolutepathes,
    find_attribute as _find_attribute,
    split_destitem_from_value as _split_destitem_from_value,
    expand_relativepathes as _expand_relativepathes,
    get_attr as _get_attr_fn,
)
from ._internal._autotimer import (
    get_attr_time as _get_attr_time,
    get_attr_value as _get_attr_value,
    get_items_from_string as _get_items_from_string,
    init_start_scheduler as _init_start_scheduler,
    item_timer as _item_timer,
    item_remove_timer as _item_remove_timer,
    item_autotimer as _item_autotimer,
)
from ._internal._casting import (
    castvalue_to_itemtype as _castvalue_to_itemtype,
    cast_duration as _cast_duration,
    run_attribute_eval as _run_attribute_eval_fn,
)
from ._internal._triggers import (
    add_logic_trigger as _add_logic_trigger,
    remove_logic_trigger as _remove_logic_trigger,
    get_logic_triggers as _get_logic_triggers,
    add_method_trigger as _add_method_trigger,
    remove_method_trigger as _remove_method_trigger,
    get_method_triggers as _get_method_triggers,
    get_item_triggers as _get_item_triggers,
    get_hysteresis_item_triggers as _get_hysteresis_item_triggers,
)
from ._internal._parsing import (
    parse_eval_attribute as _parse_eval_attribute,
    parse_eval_trigger_list_attribute as _parse_eval_trigger_list_attribute,
    parse_hysteresis_input_attribute as _parse_hysteresis_input_attribute,
    parse_hysteresis_xx_threshold_attribute as _parse_hysteresis_xx_threshold_attribute,
    parse_on_xx_list_attribute as _parse_on_xx_list_attribute,
    parse_cycle_attribute as _parse_cycle_attribute,
    parse_autotimer_attribute as _parse_autotimer_attribute,
    build_trigger_condition_eval as _build_trigger_condition_eval,
    get_attribute_value as _get_attribute_value_fn,
    build_on_xx_list as _build_on_xx_list_fn,
    init_prerun as _init_prerun_fn,
    check_item_name_collision as _check_item_name_collision,
)
from ._internal._lifecycle import remove as _remove_item
from ._internal._navigation import (
    return_parent_item as _return_parent_item,
    is_top_of_item_tree as _is_top_of_item_tree_fn,
)
from ._internal._stackinfo import (
    get_class_from_frame as _get_class_from_frame,
    get_calling_item_from_frame as _get_calling_item_from_frame,
    get_stack_info as _get_stack_info,
)
from ._internal._fade import fade as _fade
from ._internal._json import jsonvars as _jsonvars, to_json as _to_json

_items_instance = None


ATTRIB_COMPAT_DEFAULT_FALLBACK = ATTRIB_COMPAT_LATEST
ATTRIB_COMPAT_DEFAULT = ''

logger = logging.getLogger(__name__)
items_count = 0
_NOTSET = object()  # sentinel: distinguishes "no default given" from default=None


#####################################################################
# Item Class
#####################################################################

"""
The class ``Item`` implements the methods and attributes of an item. Each item is represented by an instance of the class ``Item``.
"""


class Item:
    """
    Class from which item objects are created

    The class ``Item`` implements the methods and attributes of an item. Each item is represented by an instance
    of the class ``Item``. For an item to be valid and usable, it has to be part of the item tree, which is
    maintained by an object of class ``Items``.

    This class is used by the method ```load_itemdefinitions()`` of the **Items** object.
    """

    _itemname_prefix = 'items.'  # prefix for scheduler names

    # TypeHandler / ListHandler / DictHandler have been extracted to
    # lib/item/_typehandler.py and are imported at the top of this module.
    # They are kept accessible as Item.ListHandler / Item.DictHandler via
    # class-level assignments below so existing code using
    #   getattr(self, self._type.capitalize() + 'Handler')
    # continues to work during the transition.
    ListHandler = ListHandler  # noqa: F821 — resolved by module-level import
    DictHandler = DictHandler  # noqa: F821

    # class Item
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
        except Exception:
            pass

        self.plugins = Plugins.get_instance()
        self.shtime = Shtime.get_instance()

        # count items on creation
        global items_count
        items_count += 1
        if items_count % 50 == 0:
            self._sh.shng_status['details'] = str(items_count)  # Item Zähler übertragen

        self._filename = None
        self.__children = []
        self.conf = {}
        self._fading = False
        self._items_to_trigger = []
        self._hysteresis_items_to_trigger = []
        self._history = ItemHistory(self.shtime.now())
        self._lock = threading.Condition()
        self.__logics_to_trigger = []
        self._name = path
        self.__methods_to_trigger = []
        self.__parent = parent
        self._path = path
        self._sh = smarthome
        self._type = None
        self._value = None

        self.property = Property(self)
        # history
        # TODO: create history Arrays for some values (value, last_change, last_update  (usage: multiklick,...)
        # self.__history = [None, None, None, None, None]
        #
        # def getValue(num: int = 0):
        #    pos = max(0, len(self.__history) - 1 - num)
        #    return self.__history[pos]
        #
        # def addValue(avalue):
        #    self.__history.append(avalue)
        #    if len(self.__history) > HISTORY_MAX:
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
            if hasattr(smarthome, '_' + KEY_ATTRIB_COMPAT):
                config_attrib = getattr(smarthome, '_' + KEY_ATTRIB_COMPAT)
                if str(config_attrib) in [ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST]:
                    logger.info("Global configuration: '{}' = '{}'.".format(KEY_ATTRIB_COMPAT, str(config_attrib)))
                    ATTRIB_COMPAT_DEFAULT = config_attrib
                else:
                    logger.warning(
                        "Global configuration: '{}' has invalid value '{}'.".format(
                            KEY_ATTRIB_COMPAT, str(config_attrib)
                        )
                    )
            if ATTRIB_COMPAT_DEFAULT == '':
                ATTRIB_COMPAT_DEFAULT = ATTRIB_COMPAT_DEFAULT_FALLBACK

        self._filename = dict(config.items()).get('_filename', None)

        self._apply_config(config)

        #############################################################
        # Child Items
        #############################################################
        for attr, value in config.items():
            if isinstance(value, dict):
                child_path = self._path + '.' + attr
                if _check_item_name_collision(smarthome, [self], attr, child_path):
                    continue
                try:
                    child = Item(smarthome, self, child_path, value)
                except Exception as e:
                    logger.exception('Item {}: problem creating: {}'.format(child_path, e))
                else:
                    vars(self)[attr] = child
                    _items_instance.add_item(child_path, child)
                    self.__children.append(child)

        #############################################################
        # Value
        #############################################################
        if self._value is None:
            initial_value = False
            self._value = ITEM_DEFAULTS[self._type]
        else:
            initial_value = True
        try:
            self._value = self.cast(self._value)
            if initial_value:
                self._history.set_initial_value_caller('Init:Initial_Value')
                # Write item value to log, if Item has attribute log_change set
                log_on_change(self, self._value, 'Init', 'Initial_Value', None)
        except Exception:
            logger.error('Item {}: value {} does not match type {}.'.format(self._path, self._value, self._type))
            raise
        self._history._prev_value = self._history._last_value
        self._history._last_value = self._value

        #############################################################
        # Cache
        #############################################################
        if self._cache:
            self._cache = os.path.join(self._sh._cache_dir, self._path)
            try:
                cache_time, self._value = cache_read(self._cache, self.shtime.tzinfo())
                self._value = self.cast(self._value)
                self._history.set_from_cache(cache_time, 'Init:Cache')

                # Write item value to log, if Item has attribute log_change set
                log_on_change(self, self._value, self._history.get_last_change_by(), 'Cache', None)
            except ValueError:
                logger.warning(f'Item {self._path}: cached value {self._value} does not match type {self._type}')
            except Exception as e:
                if str(e).startswith('[Errno 2]'):
                    logger.info(f'Item {self._path}: No cached value: {e}')
                else:
                    if os.stat(self._cache).st_size == 0:
                        logger.warning(
                            f'Item {self._path}: Problem reading cache: Filesize is 0 bytes. Deleting invalid cache file'
                        )
                        os.remove(self._cache)
                    else:
                        logger.warning(f'Item {self._path}: Problem reading cache: {e}')

        #############################################################
        # Cache write/init
        #############################################################
        if self._cache:
            if not os.path.isfile(self._cache):
                cache_write(self._cache, self._value)
                logger.notice(f'Created cache for item {self._cache} in file {self._cache}')

        #############################################################
        # add list/dict/datetime methods
        #############################################################
        if self._type in ['list', 'dict']:
            # get proper subclass - ListHandler / DictHandler
            type_class = getattr(self, self._type.capitalize() + 'Handler')
            # instantiate class
            obj = type_class(item=self)
            # create item member <item>.list / <item>.dict
            setattr(self, self._type, obj)
            # expose get() directly on dict items so evals can use sh.my.item.get('key')
            if self._type == 'dict':
                setattr(self, 'get', obj.get)
        if self._type == 'timestamp':
            setattr(self, 'as_dt', self.__ts_as_dt)
            setattr(self, 'as_str', self.__ts_as_str)
        if self._type == 'datetime':
            setattr(self, 'as_ts', self.__dt_as_ts)
            setattr(self, 'as_str', self.__dt_as_str)

        #############################################################
        # Plugins
        #############################################################
        for plugin in self.plugins.return_plugins():
            # plugin.xxx = []  # Empty reference list list of items
            if hasattr(plugin, PLUGIN_PARSE_ITEM):
                update = plugin.parse_item(self)
                if update:
                    try:
                        plugin.add_item(self, updating=True)
                    except Exception:
                        pass
                    self.add_method_trigger(update)

    def _apply_config(self, config):
        """
        Reset config-derived attributes to their construction-time defaults,
        then parse *config* onto self — the same logic __init__ uses to build
        a fresh item, factored out so Items.edit_item() can re-run it on an
        EXISTING object (preserving identity) instead of constructing a new
        one. __init__ calls this too (see below), so there is one parsing
        implementation, not two.

        Deliberately does NOT touch, on either call path:
        - self._value / self._history — preserve current value+history
          across an edit (explicit ``value:``/``init_value:`` in *config* is
          still honored below, same as __init__ — this is about not
          resetting to a default when *config* doesn't mention it)
        - self._items_to_trigger / _hysteresis_items_to_trigger — other
          items' incoming trigger/hysteresis registrations onto THIS item;
          unrelated to this item's own config
        - self.__children — child items
        - self._lock — other threads may be waiting on this Condition
        - self._name / self._path / self.__parent — identity (no rename via
          edit_item(); self._name does get a config-derived DEFAULT reset
          below, matching __init__, but the identity fields it derives
          from — self._path — never change)
        - self._filename — which YAML file this item persists to; callers
          decide that separately, it is not part of attribute config

        :param config: Attribute configuration dict (same shape create_item()
                        and a static item definition use)
        :type config: dict
        """
        self._autotimer_time = None
        self._autotimer_value = None
        self._cycle_time = None
        self._cycle_value = None
        self._cache = False
        self.cast = cast_bool
        self.conf = {}
        self._crontab = None
        self._enforce_updates = False
        self._enforce_change = False

        self._eval = None
        self._eval_unexpanded = ''
        self._eval_trigger = False
        self._eval_on_trigger_only = False
        self._trigger = None
        self._trigger_unexpanded = []
        self._trigger_condition_raw = []
        self._trigger_condition = None

        self._hysteresis_state_set = None
        self._hysteresis_input = None
        self._hysteresis_input_unexpanded = None
        self._hysteresis_upper_threshold = None
        self._hysteresis_lower_threshold = None
        self._hysteresis_upper_timer = None
        self._hysteresis_lower_timer = None
        self._hysteresis_upper_timer_active = False
        self._hysteresis_lower_timer_active = False
        self._hysteresis_active_timer_ends = None
        self._hysteresis_log = False

        self._on_update = None
        self._on_change = None
        self._on_update_dest_var = None
        self._on_change_dest_var = None
        self._on_update_unexpanded = []
        self._on_change_unexpanded = []
        self._on_update_dest_var_unexp = []
        self._on_change_dest_var_unexp = []
        self._log_change = None
        self._log_change_logger = None
        self._log_level_attrib = 'INFO'
        self._log_level = None
        self._log_level_name = None
        self._log_mapping = {}
        self._log_rules = {}
        self._log_rules_cache = {}
        self._log_text = None
        self._fadingdetails = {}
        self._threshold = False
        self._threshold_data = [0, 0, False]
        self._description = None
        self._struct = None
        self._remark = None
        self._name = self._path

        #############################################################
        # Item Attribute 'Type'
        #############################################################
        setattr(self, '_type', dict(config.items()).get(KEY_TYPE))
        if self._type is None:
            self._type = FOO  # Every item has a type, type is FOO, if not defined in item
        # __defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0, 'timestamp': 0}
        if self._type not in ITEM_DEFAULTS:
            logger.error(
                f"Item {self._path}: type '{self._type}' unknown. Please use one of: {', '.join(list(ITEM_DEFAULTS.keys()))}."
            )
            raise AttributeError
        self.cast = globals()['cast_' + self._type]

        #############################################################
        # Item Attributes
        #############################################################
        for attr, value in config.items():
            if not isinstance(value, dict):
                log_rules_keys = [
                    KEY_LOG_RULES_LOWLIMIT,
                    KEY_LOG_RULES_HIGHLIMIT,
                    KEY_LOG_RULES_EXCLUDE,
                    KEY_LOG_RULES_FILTER,
                    KEY_LOG_RULES_ITEMVALUE,
                ]
                if attr in [
                    KEY_NAME,
                    KEY_DESCRIPTION,
                    KEY_TYPE,
                    KEY_STRUCT,
                    KEY_VALUE,
                    KEY_INITVALUE,
                    KEY_EVAL_TRIGGER_ONLY,
                ]:
                    if attr == KEY_INITVALUE:
                        attr = KEY_VALUE
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_CACHE, KEY_ENFORCE_UPDATES, KEY_ENFORCE_CHANGE]:  # cast to bool
                    try:
                        setattr(self, '_' + attr, cast_bool(value))
                    except Exception:
                        logger.warning("Item '{0}': problem parsing '{1}'.".format(self._path, attr))
                        continue
                elif attr in [KEY_CRONTAB]:  # cast to list
                    if isinstance(value, str):
                        value = [value]
                    setattr(self, '_' + attr, value)

                elif attr in [KEY_EVAL]:
                    self._parse_eval_attribute(attr, value)
                elif attr in [KEY_EVAL_TRIGGER] or (
                    self._use_conditional_triggers and attr in [KEY_TRIGGER]
                ):  # cast to list
                    self._parse_eval_trigger_list_attribute(attr, value)

                elif (attr in [KEY_CONDITION]) and self._use_conditional_triggers:  # cast to list
                    if isinstance(value, list):
                        cond_list = []
                        for cond in value:
                            cond_list.append(dict(cond))
                        self._trigger_condition = self._build_trigger_condition_eval(cond_list)
                        self._trigger_condition_raw = cond_list
                    else:
                        logger.warning(
                            f'Item __init__: {self._path}: Invalid trigger_condition specified! Must be a list'
                        )

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
                        setattr(self, '_log_level_attrib', value)

                elif attr in [KEY_LOG_CHANGE]:
                    if value != '':
                        setattr(self, '_log_change', value)
                        if value[0] != '_':
                            self._log_change_logger = logging.getLogger('items.' + value)
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
                    if isinstance(value, list):
                        try:
                            value_dict = {k: v for od in value for k, v in od.items()}
                            setattr(self, '_log_mapping', value_dict)
                        except Exception as e:
                            logger.warning(
                                f"Item {self._path}: Invalid list data for attribute '{KEY_LOG_MAPPING}': {value} - Exception: {e}"
                            )
                    elif value != '':
                        try:
                            value_dict = ast.literal_eval(value)
                            setattr(self, '_log_mapping', value_dict)
                        except Exception as e:
                            logger.warning(
                                f"Item {self._path}: Invalid data for attribute '{KEY_LOG_MAPPING}': {value} - Exception: {e}"
                            )
                elif attr in [KEY_LOG_RULES]:
                    if isinstance(value, list):
                        try:
                            value_dict = {}
                            for od in value:
                                for k, v in od.items():
                                    if k in log_rules_keys:
                                        value_dict[k] = v
                                    else:
                                        logger.warning(
                                            f"Item {self._path}: Ignoring '{k}' as it is not a valid log rule"
                                        )
                            setattr(self, '_log_rules', value_dict)
                        except Exception as e:
                            logger.warning(
                                f"Item {self._path}: Invalid list data for attribute '{KEY_LOG_RULES}': {value} - Exception: {e}"
                            )
                    elif value != '':
                        try:
                            value_dict = ast.literal_eval(value)
                            setattr(self, '_log_rules', value_dict)
                        except Exception as e:
                            logger.warning(
                                f"Item {self._path}: Invalid data for attribute '{KEY_LOG_RULES}': {value} - Exception: {e}"
                            )
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
                    logger.debug(
                        'Item {}: set threshold => low: {} high: {}'.format(self._path, self.__th_low, self.__th_high)
                    )
                elif attr == KEY_REMARK:
                    self._remark = value
                elif attr == KEY_INSTANCE:
                    pass
                elif attr == '_filename':
                    # name of file, which defines this item
                    # assignment intentionally skipped here — callers
                    # (Item.__init__, Items.edit_item()) decide _filename
                    # separately, see this method's docstring
                    pass
                else:
                    # ------------------------------------------------------------
                    # Plugin-specific Item Attributes
                    # ------------------------------------------------------------

                    # the following code is executed for plugin specific attributes:
                    #
                    # get value from attribute of other (relative addressed) item
                    # at the moment only current, parent, grandparent and greatgrandparent items are supported
                    if type(value) is str:
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
                        logger.warning(
                            f'Item {self._path}, attribute {attr}: ' + "Invalid var definition - '}' is missing"
                        )
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
                self.conf[attr] = self.plugins.meta.check_itemattribute(
                    self, attr.split('@')[0], self.conf[attr], self._filename
                )

        self.property.init_dynamic_properties()

    def remove(self):
        """Notify plugins of item deletion — delegates to _lifecycle.remove()."""
        return _remove_item(self)

    def _get_attribute_value(
        self, attr_ref: str, current_attr: str, default: str = '', ignore_current_item: bool = False
    ) -> str:
        """Resolve relative attribute reference — delegates to _parsing.get_attribute_value()."""
        return _get_attribute_value_fn(
            self, attr_ref, current_attr, default=default, ignore_current_item=ignore_current_item
        )

    def find_attribute(self, attr, default: str = '', level: int = -1, strict: bool = False) -> str:
        """Find attribute value walking up the item tree — delegates to _pathresolution."""
        return _find_attribute(self, attr, default=default, level=level, strict=strict)

    def _split_destitem_from_value(self, value):
        """Split 'dest = expr' syntax — delegates to _pathresolution.split_destitem_from_value."""
        return _split_destitem_from_value(value)

    def _castvalue_to_itemtype(self, value, compat=ATTRIB_COMPAT_LATEST):
        """Cast value to the item's type — delegates to _casting.castvalue_to_itemtype()."""
        return _castvalue_to_itemtype(self, value, compat=compat)

    def _cast_duration(self, time, test=False):
        """Convert a duration string to seconds — delegates to _casting.cast_duration()."""
        return _cast_duration(self, time, test=test)

    # _cast_duration_old — removed (superseded by _cast_duration / _casting.cast_duration)
    # _build_cycledict   — removed (dead code, never called)

    """
    --------------------------------------------------------------------------------------------
    The following methods are used to process attributes during parsing of standard attributes
    --------------------------------------------------------------------------------------------
    """

    def _parse_eval_attribute(self, attribute_name, value):
        """Parse eval attribute — delegates to _parsing.parse_eval_attribute()."""
        _parse_eval_attribute(self, attribute_name, value)

    def _parse_eval_trigger_list_attribute(self, attribute_name, value):
        """Parse eval_trigger attribute — delegates to _parsing.parse_eval_trigger_list_attribute()."""
        _parse_eval_trigger_list_attribute(self, attribute_name, value)

    def _parse_hysteresis_input_attribute(self, attribute_name, value):
        """Parse hysteresis_input attribute — delegates to _parsing.parse_hysteresis_input_attribute()."""
        _parse_hysteresis_input_attribute(self, attribute_name, value)

    def _parse_hysteresis_xx_threshold_attribute(self, attr, value):
        """Parse hysteresis upper/lower threshold — delegates to _parsing.parse_hysteresis_xx_threshold_attribute()."""
        _parse_hysteresis_xx_threshold_attribute(self, attr, value)

    def _parse_on_xx_list_attribute(self, attr, value):
        """Parse on_change/on_update list — delegates to _parsing.parse_on_xx_list_attribute()."""
        _parse_on_xx_list_attribute(self, attr, value)

    def _parse_cycle_attribute(self, attr, value):
        """Parse cycle attribute — delegates to _parsing.parse_cycle_attribute()."""
        _parse_cycle_attribute(self, attr, value, ATTRIB_COMPAT_DEFAULT)

    def _parse_autotimer_attribute(self, attr, value):
        """Parse autotimer attribute — delegates to _parsing.parse_autotimer_attribute()."""
        _parse_autotimer_attribute(self, attr, value, ATTRIB_COMPAT_DEFAULT)

    """
    --------------------------------------------------------------------------------------------
    END of methods to process attributes during parsing of standard attributes
    --------------------------------------------------------------------------------------------
    """

    def _build_on_xx_list(self, on_dest_list, on_eval_list):
        """Reconstruct on_change/on_update list — delegates to _parsing.build_on_xx_list()."""
        return _build_on_xx_list_fn(on_dest_list, on_eval_list)

    # -----------------------------------------------------------------------
    # History getters — delegate to self._history (lib/item/_history.py)
    # -----------------------------------------------------------------------

    def _get_last_change(self):
        return self._history.get_last_change()

    def _get_last_change_age(self):
        delta = self.shtime.now() - self._history.get_last_change()
        return delta.total_seconds()

    def _get_last_change_by(self):
        return self._history.get_last_change_by()

    def _get_last_update(self):
        return self._history.get_last_update()

    def _get_last_update_by(self):
        return self._history.get_last_update_by()

    def _get_last_update_age(self):
        delta = self.shtime.now() - self._history.get_last_update()
        return delta.total_seconds()

    def _get_last_trigger(self):
        return self._history.get_last_trigger()

    def _get_last_trigger_age(self):
        delta = self.shtime.now() - self._history.get_last_trigger()
        return delta.total_seconds()

    def _get_last_trigger_by(self):
        return self._history.get_last_trigger_by()

    def _get_last_value(self):
        return self._history.get_last_value()

    def _get_prev_change(self):
        return self._history.get_prev_change()

    def _get_prev_change_age(self):
        delta = self._history.get_last_change() - self._history.get_prev_change()
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_change_by(self):
        return self._history.get_prev_change_by()

    def _get_prev_update(self):
        return self._history.get_prev_update()

    def _get_prev_update_age(self):
        delta = self._history.get_last_update() - self._history.get_prev_update()
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_update_by(self):
        return self._history.get_prev_update_by()

    def _get_prev_value(self):
        return self._history.get_prev_value()

    def _get_prev_trigger(self):
        return self._history.get_prev_trigger()

    def _get_prev_trigger_age(self):
        delta = self._history.get_last_trigger() - self._history.get_prev_trigger()
        if delta.total_seconds() < 0.0001:
            return 0.0
        return delta.total_seconds()

    def _get_prev_trigger_by(self):
        return self._history.get_prev_trigger_by()

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
        """Build an absolute item path from a relative path — delegates to _pathresolution."""
        return _get_absolutepath(self, relativepath, attribute)

    def expand_relativepathes(self, attr, begintag, endtag):
        """Convert relative paths in a conf attribute to absolute paths — delegates to _pathresolution."""
        return _expand_relativepathes(self, attr, begintag, endtag)

    def get_stringwithabsolutepathes(self, evalstr, begintag, endtag, attribute=''):
        """Convert relative path references in a string to absolute paths — delegates to _pathresolution."""
        return _get_stringwithabsolutepathes(self, evalstr, begintag, endtag, attribute)

    def _get_attr(self, attr, default=''):
        """Get attribute from item's own conf — delegates to _pathresolution.get_attr()."""
        return _get_attr_fn(self, attr, default=default)

    # _get_attr_from_parent / _get_attr_from_grandparent / _get_attr_from_greatgrandparent
    # — removed (dead code, never called)

    def _build_trigger_condition_eval(self, trigger_condition):
        """Build trigger condition eval string — delegates to _parsing.build_trigger_condition_eval()."""
        return _build_trigger_condition_eval(self, trigger_condition)

    def __call__(self, value=None, caller='Logic', source=None, dest=None, key=None, index=None, default=_NOTSET):
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
            self._sh.trigger(
                name=self._path + '-eval', obj=self.__run_eval, value=args, by=caller, source=source, dest=dest
            )
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
        return 'Item: {}'.format(self._path)

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

    #
    # helper methods for timestamp item output
    #

    def __ts_as_dt(self, tz=None) -> datetime.datetime:
        if tz is None:
            tz = self.shtime.tzinfo()  # type: ignore : shtime is set dynamically
        return datetime.datetime.fromtimestamp(self._value, tz)  # type: ignore : method is only made "public" if type matches

    def __ts_as_str(self, format=None, tz=None) -> str:
        dt = self.__ts_as_dt(tz)
        if not format:
            return str(dt)
        return dt.strftime(format)

    #
    # helper methods for datetime item output
    #

    def __dt_as_ts(self) -> float:
        return self._value.timestamp()  # type: ignore : self._value is set dynamically

    def __dt_as_str(self, format=None) -> str:
        if not format:
            return str(self._value)
        return self._value.strftime(format)  # type: ignore : self.value is set dynamically

    #
    #
    #

    def get_class_from_frame(self, fr):
        """Return debug frame string — delegates to _stackinfo.get_class_from_frame()."""
        return _get_class_from_frame(self, fr)

    def get_calling_item_from_frame(self, fr):
        """Return calling item string from frame — delegates to _stackinfo.get_calling_item_from_frame()."""
        return _get_calling_item_from_frame(self, fr)

    def get_stack_info(self):
        """Return caller info from call stack — delegates to _stackinfo.get_stack_info()."""
        return _get_stack_info(self)

    def __get_dictentry(self, key, default=_NOTSET):
        try:
            return self._value[key]
        except Exception as e:
            if default is _NOTSET:
                msg = f"Item '{self._path}': {e.__class__.__name__}: {e}"
                stack_info = self.get_stack_info()
                if stack_info.startswith('Item'):
                    msg += f'  -  called from: {self.get_stack_info()}'
                logger.info(msg)
                raise KeyError(msg)  # msg needed to show error message in eval syntax checker
        return default

    def __set_dictentry(self, value, key):
        # Update a dict item element (selected by key) or add an element, if the key does not exist
        valuedict = copy.deepcopy(self._value)
        valuedict[key] = value
        return valuedict

    def _init_prerun(self):
        """Wire eval/hysteresis triggers before first run — delegates to _parsing.init_prerun()."""
        _init_prerun_fn(self)

    def _init_start_scheduler(self):
        """Start crontab/cycle schedulers — delegates to _autotimer.init_start_scheduler()."""
        _init_start_scheduler(self)

    def __get_items_from_string(self, string):
        """Return Item objects referenced in string — delegates to _autotimer.get_items_from_string()."""
        return _get_items_from_string(self, string)

    def get_attr_time(self, attr: str):
        """Return resolved time for 'cycle' or 'autotimer' — delegates to _autotimer.get_attr_time()."""
        return _get_attr_time(self, attr)

    def get_attr_value(self, attr: str, value=None):
        """Return resolved value for 'cycle'/'autotimer'/'cron' — delegates to _autotimer.get_attr_value()."""
        return _get_attr_value(self, attr, value)

    def _init_run(self):
        """
        Run initial eval to set an initial value for the item

        Called from Items.load_itemdefinitions
        """
        if self._trigger:
            # Only if item has an eval_trigger
            if self._eval and not self._cache:
                # Only if item has an eval expression
                self._sh.trigger(
                    name=self._path,
                    obj=self.__run_eval,
                    by='Init',
                    source='_init_run',
                    value={'value': self._value, 'caller': 'Init:Eval'},
                )
                return True
        return False

    def _run_attribute_eval(self, eval_expression, result_type='num', result_error=''):
        """Public proxy for __run_attribute_eval — used by extracted submodules."""
        return self.__run_attribute_eval(eval_expression, result_type, result_error)

    def __run_attribute_eval(self, eval_expression, result_type='num', result_error: Any = ''):
        """Evaluate attribute expression — delegates to _casting.run_attribute_eval()."""
        return _run_attribute_eval_fn(self, eval_expression, result_type=result_type, result_error=result_error)

    def __run_hysteresis(self, value=None, caller='Hysteresis', source=None, dest=None):
        """evaluate the 'hysteresis' entry of the item — delegates to _hysteresis.run_hysteresis()"""
        run_hysteresis(self, value=value, caller=caller, source=source, dest=dest)

    def hysteresis_state(self):
        """Return the inner hysteresis state — delegates to _hysteresis.get_hysteresis_state()"""
        return get_hysteresis_state(self)

    def hysteresis_data(self):
        """Return hysteresis diagnostics dict — delegates to _hysteresis.get_hysteresis_data()"""
        return get_hysteresis_data(self)

    def __run_eval(self, value=None, caller='Eval', source=None, dest=None):
        """evaluate the 'eval' entry of the actual item — delegates to _eval.run_eval()"""
        run_eval(self, value=value, caller=caller, source=source, dest=dest)

    # New for on_update / on_change
    def _run_on_xxx(self, path, value, on_dest, on_eval, attr='?', caller=None, source=None, dest=None):
        """common method for __run_on_update and __run_on_change — delegates to _eval.run_on_xxx()"""
        run_on_xxx(self, path, value, on_dest, on_eval, attr=attr, caller=caller, source=source, dest=dest)

    def __run_on_update(self, value=None, caller=None, source=None, dest=None):
        """evaluate all 'on_update' entries of the actual item — delegates to _eval.run_on_update()"""
        run_on_update(self, value=value, caller=caller, source=source, dest=dest)

    def __run_on_change(self, value=None, caller=None, source=None, dest=None):
        """evaluate all 'on_change' entries of the actual item — delegates to _eval.run_on_change()"""
        run_on_change(self, value=value, caller=caller, source=source, dest=dest)

    def __trigger_logics(self, source_details=None):
        source = {'item': self._path, 'details': source_details}
        for logic in self.__logics_to_trigger:
            logic.trigger(by='Item', source=source, value=self._value)

    def _set_value(self, value, caller, source=None, dest=None, prev_change=None, last_change=None):
        """
        Set item value, update last and prev information and perform log_change for item

        :param value:
        :param caller:
        :param source:
        :param dest:
        :param prev_change:
        :param last_change:
        :return:
        """
        old_value = self._value
        self._value = value
        self._history.record_change(
            old_value, caller, source, self.shtime, prev_change=prev_change, last_change=last_change
        )

        if caller != 'Fader':
            # log every item change to standard logger, if level is DEBUG
            # log with level INFO, if 'item_change_log' is set in etc/smarthome.yaml
            # attention:
            # huge int values (created e.g. by eval) get dimensions above 4300 digits
            # when converted to strings and will raise a Value error.
            # This will stop threads and kill SHNG
            if isinstance(value, int) and value.bit_length() > 14300:
                logger.warning(
                    f'int value is too large to convert to string: {value.bit_length()} bits → ignored for logging'
                )
                self._change_logger(
                    'Item {} = {} via {} {} {}'.format(self._path, 'too large int', caller, source, dest)
                )
            else:
                self._change_logger('Item {} = {} via {} {} {}'.format(self._path, value, caller, source, dest))

            # Write item value to log, if Item has attribute log_change set
            log_on_change(self, value, caller, source, dest)
        return

    def _update_item(self, value, caller='Logic', source=None, dest=None, key=None, index=None):
        """Public proxy for __update — used by extracted submodules (_eval.py etc.)."""
        self.__update(value, caller, source, dest, key, index)

    # ------------------------------------------------------------------
    # Proxy properties for name-mangled trigger lists
    # (_triggers.py cannot access self.__logics_to_trigger directly)
    # ------------------------------------------------------------------

    @property
    def _logics_to_trigger(self):
        """Proxy for __logics_to_trigger — used by _triggers.py."""
        return self.__logics_to_trigger

    @property
    def _methods_to_trigger(self):
        """Proxy for __methods_to_trigger — used by _triggers.py."""
        return self.__methods_to_trigger

    @property
    def _parent(self):
        """Proxy for __parent — used by _navigation.py."""
        return self.__parent

    def __update(self, value, caller='Logic', source=None, dest=None, key=None, index=None):
        def check_external_change(entry_type, entry_value):
            matches = []
            for pattern in entry_value:
                regex = re.compile(pattern, re.IGNORECASE)
                if regex.match(f'{caller}:{source}'):
                    if entry_type == 'stop_fade':
                        matches.append(True)  # Match in stop_fade, should stop
                    else:
                        matches.append(False)  # Match in continue_fade, should continue fading
                else:
                    if entry_type == 'continue_fade':
                        matches.append(True)  # No match in continue_fade -> we can stop
                    else:
                        matches.append(False)  # No match in stop_fade -> keep fading
            return matches

        # special handling, if item is a hysteresis item (has a hysteresis_input attribute)
        if self._hysteresis_input is not None:
            if self._hysteresis_upper_timer_active:
                if self._hysteresis_log:
                    logger.notice(f'__update: upper_timer caller={caller}, value={value}')
                self._sh.scheduler.remove(self._itemname_prefix + self.id() + '-UpTimer')
                self._hysteresis_upper_timer_active = False
                self.active_timer_ends = None
            if self._hysteresis_lower_timer_active:
                self._sh.scheduler.remove(self._itemname_prefix + self.id() + '-LoTimer')
                self._hysteresis_lower_timer_active = False
                self.active_timer_ends = None
                if self._hysteresis_log:
                    logger.notice(f'__update: lower_timer caller={caller}, value={value}')
            if caller != 'Hysteresis':
                self._hysteresis_state_set = cast_bool(value)

        if key is None and index is None:
            # don't cast for elements of complex types
            try:
                value = self.cast(value)
            except Exception:
                try:
                    logger.warning(
                        f'Item {self._path}: value "{value}" does not match type {self._type}. Via caller {caller}, source {source}'
                    )
                except Exception:
                    pass
                return

        self._lock.acquire()
        _changed = False
        trigger_source_details = self._history.get_last_update_by()

        if key is not None and self._type == 'dict':
            # Update a dict item element or add an element (selected by key)
            value = self.__set_dictentry(value, key)
        elif index is not None and self._type == 'list':
            # Update a list item element (selected by index)
            value = self.__set_listentry(value, index)
        if self._fading:
            stop_fade = self._fadingdetails.get('stop_fade')
            continue_fade = self._fadingdetails.get('continue_fade')
            stopping = check_external_change('stop_fade', stop_fade) if stop_fade else [False]
            continuing = check_external_change('continue_fade', continue_fade) if continue_fade else [True]
            # If stop_fade is set and there's a match, stop fading immediately
            if stop_fade and True in stopping:
                logger.dbghigh(f'Item {self._path}: Stopping fade loop, {caller} matches stop list {stop_fade}')
                self._fading = False
                self._lock.notify_all()

            # If continue_fade is set and there is no match, stop fading immediately
            elif continue_fade and False not in continuing and caller != 'Fader':
                logger.dbghigh(
                    f'Item {self._path}: Stopping fade loop, {caller} matches no value in continue list {continue_fade}'
                )
                self._fading = False
                self._lock.notify_all()

            # If nothing is set, stop (original behaviour)
            elif not continue_fade and not stop_fade and caller != 'Fader':
                logger.dbghigh(f'Item {self._path}: Stopping fade loop by {caller}, current value {value}')
                self._fading = False
                self._lock.notify_all()

            elif value == self._fadingdetails.get('value'):
                pass
            else:
                logger.dbghigh(f'Item {self._path}: Ignoring update by {caller} as item is fading')
                self._lock.release()
                return

        if value != self._value or self._enforce_change:
            _changed = True
            self._set_value(value, caller, source, dest, prev_change=None, last_change=None)
            trigger_source_details = self._history.get_last_change_by()
        else:
            self._history.record_update_only(caller, source, self.shtime)
        self._lock.release()

        # Test for fix for unwanted plugin retrigger in combination with eval expressions
        # remove existing prefix from caller
        caller_without_prefix = caller
        try:
            if caller.lower().startswith('eval:'):
                # clean up caller for update_item methods
                caller_without_prefix = caller[5:]
        except AttributeError:
            pass
        # END Test for fix for unwanted plugin retrigger in combination with eval expressions

        self.__run_on_update(value, caller=caller, source=source, dest=dest)

        if _changed or self._enforce_updates or self._type == 'scene':
            # Trigger methods (update_item methods of plugins)
            ### Test for fix for unwanted plugin retrigger in combination with eval expressions
            for method in self.__methods_to_trigger:
                # shortname={method.__self__._shortname} - not every plugin has a var _shortname !!!
                try:
                    method(self, caller_without_prefix, source, dest)
                except Exception as e:
                    logger.exception(f'Item {self._path}: problem running {method}: {e}')
            ### END Test for fix for unwanted plugin retrigger in combination with eval expressions

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
                self._sh.trigger(
                    name='items.' + item.property.path,
                    obj=item.__run_eval,
                    value=args,
                    by=caller,
                    source=source,
                    dest=dest,
                )
            for item in self._hysteresis_items_to_trigger:
                args = {'value': value, 'source': self._path}
                self._sh.trigger(
                    name='items.' + item.property.path,
                    obj=item.__run_hysteresis,
                    value=args,
                    by=caller,
                    source=source,
                    dest=dest,
                )
            # ms: call run_on_change() from here - after eval is run
            self.__run_on_change(value, caller=caller, source=source, dest=dest)

        if _changed and self._cache and not self._fading:
            try:
                cache_write(self._cache, self._value)
            except Exception as e:
                logger.warning('Item: {}: could not update cache {}'.format(self._path, e))

        if self._autotimer_time and caller_without_prefix != 'Autotimer' and not self._fading:
            # cast_duration for fixed attribute
            # logger.debug(f'autotimer: {self._autotimer_time} / {self._autotimer_value}')
            _time = self.get_attr_time('autotimer')
            _value = value
            if _time is None:
                logger.warning(f'evaluating autotimer time {self._autotimer_time} returned None, ignoring')
            elif type(_time) is not int:
                logger.warning(
                    f"autotimer time {self._autotimer_time} didn't result in int, but in {_time}, type {type(_time)}"
                )
            else:
                _value = self._autotimer_value

                # logger.notice(f"Item {self._path} __update: _time={_time}, _value={_value}")

                next = self.shtime.now() + datetime.timedelta(seconds=_time)
                self._sh.scheduler.add(
                    self._itemname_prefix + self.id() + '-Timer',
                    self,
                    value={'value': _value, 'caller': 'Autotimer'},
                    next=next,
                )

    def add_logic_trigger(self, logic):
        """Add a logic trigger — delegates to _triggers.add_logic_trigger()."""
        _add_logic_trigger(self, logic)

    def remove_logic_trigger(self, logic):
        """Remove a logic trigger — delegates to _triggers.remove_logic_trigger()."""
        _remove_logic_trigger(self, logic)

    def get_logic_triggers(self):
        """Return logic triggers list — delegates to _triggers.get_logic_triggers()."""
        return _get_logic_triggers(self)

    def add_method_trigger(self, method):
        """Add a method trigger — delegates to _triggers.add_method_trigger()."""
        _add_method_trigger(self, method)

    def remove_method_trigger(self, method):
        """Remove a method trigger — delegates to _triggers.remove_method_trigger()."""
        _remove_method_trigger(self, method)

    def get_method_triggers(self):
        """Return method triggers list — delegates to _triggers.get_method_triggers()."""
        return _get_method_triggers(self)

    def get_item_triggers(self):
        """Return item triggers list — delegates to _triggers.get_item_triggers()."""
        return _get_item_triggers(self)

    def get_hysteresis_item_triggers(self):
        """Return hysteresis item triggers list — delegates to _triggers.get_hysteresis_item_triggers()."""
        return _get_hysteresis_item_triggers(self)

    def timer(self, time, value, auto=False, caller=None, source=None, compat=ATTRIB_COMPAT_LATEST):
        """Start a one-shot or autotimer — delegates to _autotimer.item_timer()."""
        _item_timer(self, time, value, auto=auto, caller=caller, source=source, compat=compat)

    def remove_timer(self):
        """Cancel the running timer — delegates to _autotimer.item_remove_timer()."""
        _item_remove_timer(self)

    def autotimer(self, time=None, value=None, compat=ATTRIB_COMPAT_LATEST):
        """Set or clear the autotimer time/value — delegates to _autotimer.item_autotimer()."""
        _item_autotimer(self, time=time, value=value)

    def fade(
        self, dest, step=1, delta=1, caller=None, stop_fade=None, continue_fade=None, instant_set=True, update=False
    ):
        """Fade item value to dest — delegates to _fade.fade()."""
        _fade(
            self,
            dest,
            step=step,
            delta=delta,
            caller=caller,
            stop_fade=stop_fade,
            continue_fade=continue_fade,
            instant_set=instant_set,
            update=update,
        )

    def return_children(self):
        for child in self.__children:
            yield child

    def _remove_child(self, child) -> None:
        """Remove child from __children — used by _lifecycle.py when child is deleted, and by Items.rename_item() when moving it to a different parent."""
        try:
            self.__children.remove(child)
        except ValueError:
            pass

    def _append_child(self, child) -> None:
        """Append child to __children — used by Items._construct_and_link() when child is created, and by Items.rename_item() when moving it under this item."""
        self.__children.append(child)

    def _reassign_parent(self, new_parent) -> None:
        """Reassign __parent — used by Items.rename_item() when moving an item to a new parent."""
        self.__parent = new_parent

    def return_parent(self, level: int = 1, strict: bool = False):
        """Return ancestor item at given level — delegates to _navigation.return_parent_item()."""
        return _return_parent_item(self, level=level, strict=strict)

    def _is_top_of_item_tree(self):
        """Return True if item has no parent in tree — delegates to _navigation.is_top_of_item_tree()."""
        return _is_top_of_item_tree_fn(self)

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
        except Exception:
            try:
                logger.warning(
                    'Item {}: value {} does not match type {}. Via {} {}'.format(
                        self._path, value, self._type, caller, source
                    )
                )
            except Exception:
                pass
            return
        self._lock.acquire()
        self._set_value(value, caller, source, dest, prev_change, last_change)
        self._lock.release()
        return

    def get_children_path(self):
        return [item._path for item in self.__children]

    def jsonvars(self):
        """Return serialisable attribute dict — delegates to _json.jsonvars()."""
        return _jsonvars(self)

    def to_json(self):
        """Return pretty-printed JSON string — delegates to _json.to_json()."""
        return _to_json(self)
