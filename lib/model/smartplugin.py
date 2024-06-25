#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2017-      Martin Sinn                       m.sinn@gmx.de
#  Copyright 2016       Christian Strassburg      c.strassburg(a)gmx.de
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

from lib.model.smartobject import SmartObject
from lib.shtime import Shtime
from lib.module import Modules
import lib.shyaml as shyaml
from lib.utils import Utils
from lib.translation import translate as lib_translate

import logging
import os
import threading
import asyncio
import time
from typing import Coroutine, Any


class SmartPlugin(SmartObject, Utils):
    """
    The class SmartPlugin implements the base class of all smart-plugins.
    The implemented methods are described below.

    In addition the methods implemented in lib.utils.Utils are inherited.

    """

    PLUGIN_VERSION = ''
    ALLOW_MULTIINSTANCE = None
    STOP_ON_ITEM_CHANGE = True      # Plugin needs to be stopped on/before item changes
                                    # needed by self.remove_item(), don't change unless you know how and why

    # these variables are initialized by the plugin loader for each plugin

    __instance = ''             #: Name of this instance of the plugin
    _sh = None                  #: Variable containing a pointer to the main SmartHomeNG object; is initialized during loading of the plugin; :Warning: Don't change it
    _configfilename = ''        #: Configfilename of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _configname = ''            #: Configname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _shortname = ''             #: Shortname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _classname = ''             #: Classname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    shtime = None               #: Variable containing a pointer to the SmartHomeNG time handling object; is initialized during loading of the plugin; :Warning: Don't change it

    _parameters = {}            # Dict for storing the configuration parameters read from /etc/plugin.yaml
    _hide_parameters = {}       # Dict for storing parameters to hide from AdminUI

    _pluginname_prefix = 'plugins.'

    # these variables _should_ be instance members (not class members) ...
    # BUT if a plugin fails to call the parent class' __init__(), these are
    # not present and cause errors.
    # So - until a proper QA for 3rd party plugins is in place - we define these
    # as class members to prevent AttributeErrors later on...

    logger = logging.getLogger(__name__)

    _plg_item_dict = {}         # dict to hold the items assigned to the plugin and their plugin specific information
    _item_lookup_dict = {}      # dict for the reverse lookup from a mapping (device-command or matchstring) to an item,
                                # contains a list of items for each mapping

    alive = False               # flag if plugin is running
    _cycle = 60                 # default cycle for cyclic scheduler
    _schedulers = []            # all created schedulers for this plugin

    _add_translation = None

    _pause_item = None          # pause item
    _pause_item_path = ''       # path of pause item

    _asyncio_loop = None        # eventloop of the plugin
    _asyncio_state = 'unused'   # stored state of the asyncio use of the plugin
    _used_plugin_coro = None    # plugin coro used when calling start_asyncio (to be able to used by a generic 'restart asyncio' method
    _run_queue = None           # queue to send commends to the main-coro/plugin-coro

#
# the following methods need to be overwritten / implemented
#

    def run(self):
        """
        This method of the plugin is called to start the plugin

        :note: This method needs to be overwritten by the plugin implementation. Otherwise an error will be raised
        """
        raise NotImplementedError("'Plugin' subclasses should have a 'run()' method")

    def stop(self):
        """
        This method of the plugin is called to stop the plugin when SmartHomeNG shuts down

        :note: This method needs to be overwritten by the plugin implementation. Otherwise an error will be raised
        """
        raise NotImplementedError("'Plugin' subclasses should have a 'stop()' method")

#
# the following methods should be overwritten, but also called via super().<method>()
#

    def __init__(self, **kwargs) -> None:
        """
        Initialization of SmartPlugin instance

        Should be called by super().__init__() from the plugin's __init__() method
        """
        self.logger = logging.getLogger(__name__)

        # initialize instance members; for mutable types make sure these are "instance-specific"

        self._plg_item_dict = {}        # dict to hold the items assigned to the plugin and their plugin specific information
        self._item_lookup_dict = {}     # dict for the reverse lookup from a mapping (device-command or matchstring) to an item,
                                        # contains a list of items for each mapping

        self._schedulers = []           # all created schedulers for this plugin

        # initialize plugin variables

        self._plg_item_dict = {}        # dict to hold the items assigned to the plugin and their plugin specific information
        self._item_lookup_dict = {}     # dict for the reverse lookup from a mapping (device-command or matchstring) to an item,
                                        # contains a list of items for each mapping

        self.alive = False              # flag if plugin is running
        self._cycle = 60                # default cycle for cyclic scheduler
        self._schedulers = []           # all created schedulers for this plugin

        self._add_translation = None

        self._pause_item = None         # pause item
        self._pause_item_path = ''      # pause item path

        self._asyncio_loop = None       # eventloop of the plugin
        self._asyncio_state = 'unused'  # stored state of the asyncio use of the plugin
        self._used_plugin_coro = None   # plugin coro used when calling start_asyncio (to be able to used by a generic 'restart asyncio' method
        self._run_queue = None          # queue to send commends to the main-coro/plugin-coro

#
# the following methods should be overwritten
#

    def update_item(self, item, caller=None, source=None, dest=None) -> None:
        """
        Item has been updated

        This method is called, if the value of an item has been updated by
        SmartHomeNG. It should write the changed value out to the device
        (hardware/interface) that is managed by this plugin.

        Method must be overwritten for the plugin to be able to react to
        item changes.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        # check for pause item
        if item is self._pause_item:
            if caller != self.get_shortname():
                self.logger.debug(f'pause item changed to {item()}')
                if item() and self.alive:
                    self.stop()
                elif not item() and not self.alive:
                    self.run()
            return

        if not self.alive:
            self.logger.warning(f'Received item update for item {item.property.path}, but plugin is not running. Ignoring...')
            return

    def parse_item(self, item) -> Any:
        """
        This method is used to parse the configuration of an item for this plugin. It is
        called for each item before the plugins are started (calling all run methods).
        Copy code to own function; calling via super() does not work without bending three arms...

        :note: This method should be overwritten by the plugin implementation.
        """
        # check for pause item
        if item.property.path == self._pause_item_path:
            self.logger.debug(f'pause item {item.property.path} registered')
            self._pause_item = item
            self.add_item(item, updating=True)
            return self.update_item

#
# the following methods can be overwritten
#

    def poll_device(self) -> None:
        """
        periodically poll device (or do other things periodically)

        :note: This method can be overwritten by plugin implementation.
        """
        pass

    def parse_logic(self, logic) -> None:
        """
        This method is used to parse the configuration of a logic for this plugin. It is
        called for all plugins before the plugins are started (calling all run methods).

        :note: This method should to be overwritten by the plugin implementation.
        """
        pass

    def deinit(self, items=[]) -> None:
        """
        This method "deinitializes" the plugin, i.e. prepares for unloading.
        The plugin is stopped and all (or all provided) items are un-registered.

        If the Plugin needs special code to be executed before it is unloaded, this method
        has to be overwritten with the code needed for de-initialization. Keep the
        original code or call super().deinit()...

        If called without parameters, all registered items are unregistered.
        items is a list of items (or a single Item() object).
        """
        if self.alive:
            self.stop()

        if not items:
            items = self.get_item_list()
        elif not isinstance(items, list):
            items = [items]

        for item in items:
            self.remove_item(item)

###############################################################################
#
#
# the following methods should NOT be overwritten
#
#

    def add_item(self, item, config_data_dict: dict = {}, mapping=None, updating: bool = False) -> bool:
        """
        For items that are used/handled by a plugin, this method stores the configuration information
        that is individual for the plugin. The configuration information is/has to be stored in a dictionary

        The configuration information can be retrieved later by a call to the method get_item_configdata(<item_path>)

        If data is being received by the plugin, a mapping ( a 'device-command' or matchstring) has to be specified
        as an optional 3rd parameter. This allows a reverse lookup. The method get_itemlist_for_mapping(<mapping>)
        returns a list of items for the items that have defined the <mapping>. In most cases, the list will have
        only one entry, but if multiple items should receive data from the same device (or command), the list can
        have more than one entry.

        Calling this method for an item already stored in `self._plg_item_dict` can be used to change the "is_updating"
        key to True, if it was False before and the `updating` parameter is True. Otherwise, nothing happens.

        This method should be called from parse_item to register the item. If parse_item returns a reference to `update_item`,
        this method is called again by the Item instance itself to change the `is_updating` key.

        Only available in SmartHomeNG versions **v1.9.4 and up**.

        :param item: item
        :param config_data_dict: Dictionary with the plugin-specific configuration information for the item
        :param mapping: String identifing the origin (source/kind) of received data (e.g. the address on a bus)
        :param updating: Show if item updates from shng should be sent to the plugin
        :type item: Item
        :type config_data_dict: dict
        :type mapping: str
        :type updating: bool

        :return: True, if the information has been added
        :rtype: bool
        """
        if item.property.path in self._plg_item_dict:

            # if called again (e.g. from lib/item/item.py) with updating == True,
            # update "is_updating" key...
            if updating:
                self.logger.debug(f"add_item called with existing item {item.property.path}, updating stored data: is_updating enabled")
                self.register_updating(item)
                return True

            # otherwise return error
            self.logger.warning(f"Trying to add an existing item: {item.property.path}")
            return False

        self._plg_item_dict[item.property.path] = {
            'item': item,
            'is_updating': updating,
            'mapping': mapping,
            'config_data': dict(config_data_dict)
        }

        if mapping:
            if mapping not in self._item_lookup_dict:
                self._item_lookup_dict[mapping] = []
            self._item_lookup_dict[mapping].append(item)

        return True

    def remove_item(self, item) -> bool:
        """
        Remove configuration data for an item (and remove the item from the mapping's list

        :param item: item to remove
        :type item: Item

        :return: True, if the information has been removed
        :rtype: bool
        """
        if item.property.path not in self._plg_item_dict:
            # There is no information stored for that item
            self.logger.debug(f'item {item.property.path} not associated to this plugin, doing nothing')
            return False

        # check if plugin is running
        if self.alive:
            if self.STOP_ON_ITEM_CHANGE:
                self.logger.debug(f'stopping plugin for removal of item {item.property.path}')
                self.stop()
            else:
                self.logger.debug(f'not stopping plugin for removal of item {item.property.path}')

        if item.property.path == self._pause_item_path:
            self.logger.warning(f'trying to remove pause item {item}. Disabling pause item function')
            self._pause_item = None
            self._pause_item_path = ''

        # remove data from item_dict early in case of concurrent actions
        data = self._plg_item_dict[item.property.path]
        del self._plg_item_dict[item.property.path]

        # remove item from self._item_lookup_dict if present
        mapping = data.get('mapping')
        if mapping:
            # if a mapping was given for the item, the item is being removed from the list of the mapping
            if item in self._item_lookup_dict[mapping]:
                self._item_lookup_dict[mapping].remove(item)

        # unregister item update method
        self.unparse_item(item)

        return True

    def callerinfo(self, caller: str, source: str) -> str:

        if source is None:
            return caller
        else:
            return caller + ':' + source

    def register_updating(self, item) -> None:
        """
        Mark item in self._plg_item_dict as registered in shng for updating
        (usually done by returning self.update_item from self.parse_item)

        NOTE: Items are added to _plg_item_dict by the item class as updating
              by default. This could only be used if items were added manually
              as non-updating first. Registering them as updating usually only
              occurs via parse_item(), which in turn makes the item class
              add the item as updating.

        :param item: item object
        :type item: item
        """
        if item.property.path not in self._plg_item_dict:
            self.add_item(item)
        self._plg_item_dict[item.property.path]['is_updating'] = True

    def get_item_config(self, item) -> dict:
        """
        Returns the plugin-specific configuration information (config_data_dict) for the given item

        :param item: item or item_path (str) to get config info for
        :type item: item object or str

        :return: dict with the configuration information for the given item
        :rtype: dict
        """
        if isinstance(item, str):
            item_path = item
        else:
            item_path = item.property.path
        return self._plg_item_dict[item_path].get('config_data')

    def get_item_mapping(self, item) -> str:
        """
        Returns the plugin-specific mapping that was defined by add_item()

        Only available in SmartHomeNG versions **v1.9.4 and up**.

        :param item: item or item_path (str) to get config info for
        :type item: item object or str

        :return: mapping string for that item
        :rtype: str
        """
        if isinstance(item, str):
            item_path = item
        else:
            item_path = item.property.path
        return self._plg_item_dict[item_path].get('mapping')

    def get_item_mapping_list(self) -> list:
        """
        Returns the plugin-specific mapping that was defined by add_item()

        This method is implemented to support plugin development
        to be used with the eval syntax checker or the executor plugin

        Only available in SmartHomeNG versions **v1.10.0 and up**.

        :return: mapping string for that item
        :rtype: list
        """
        result = []
        for item_path in list(self._plg_item_dict.keys()):
            result.append([item_path, self._plg_item_dict[item_path].get('mapping')])
        return result

    def _string_compare(self, s1: str, s2: str, mode: str='') -> bool:
        """
        Compare strings of different length

        This method compares strings only up to the length of the shorter string.
        - mode 'start' compares the shorter string with the beginning of longer string
        - mode 'end' compares the shorter string with the end of longer string

        :param s1: First string to compare
        :param s2: Second string to compare
        :param mode: Compare mode ('start', 'end') for comparing strings of different length
        :return: True if strings match, False otherwise
        :rtype: bool
        """
        if mode == 'end':
            if len(s1) > len(s2):
                return s1.endswith(s2)
            else:
                return s2.endswith(s1)
        elif mode == 'start':
            if len(s1) > len(s2):
                return s1.startswith(s2)
            else:
                return s2.startswith(s1)
        else:
            return s1 == s2

    def get_item_path_list(self, filter_key: str='', filter_value: str='', mode: str='') -> list:
        """
        Return list of stored item paths used by this plugin

        Only available in SmartHomeNG versions **v1.9.4 and up**.
        Parameter 'mode' only available in SmartHomeNG versions **v1.10.0 and up**.

        :param filter_key: key of the configdata dict used to filter
        :param filter_value: value for filtering item_path_list
        :param mode: Compare mode ('start', 'end') for comparing strings of different length, None oder ommitting does a standard compare

        :return: List of item pathes
        """
        if filter_key == '' or filter_value == '':
            return self._plg_item_dict.keys()

        if mode == '':
            return [item_path for item_path in list(self._plg_item_dict.keys()) if self._plg_item_dict[item_path]['config_data'].get(filter_key, None) == filter_value]

        return [item_path for item_path in list(self._plg_item_dict.keys()) if self._string_compare(self._plg_item_dict[item_path]['config_data'].get(filter_key, None), filter_value, mode)]

    def get_item_list(self, filter_key: str='', filter_value: str='', mode: str='') -> list:
        """
        Return list of stored items used by this plugin

        Only available in SmartHomeNG versions **v1.9.4 and up**.
        Parameter 'mode' only available in SmartHomeNG versions **v1.10.0 and up**.

        :param filter_key: key of the configdata dict used to filter
        :param filter_value: value for filtering item_path_list
        :param mode: Compare mode ('start', 'end') for comparing strings of different length, None oder ommitting does a standard compare

        :return: List of item objects
        """
        if filter_key == '' or filter_value == '':
            return [self._plg_item_dict[item_path]['item'] for item_path in list(self._plg_item_dict.keys())]

        if mode == '':
            return [self._plg_item_dict[item_path]['item'] for item_path in list(self._plg_item_dict.keys()) if self._plg_item_dict[item_path]['config_data'].get(filter_key, None) == filter_value]

        return [self._plg_item_dict[item_path]['item'] for item_path in list(self._plg_item_dict.keys()) if self._string_compare(self._plg_item_dict[item_path]['config_data'].get(filter_key, None), filter_value, mode)]

    def get_trigger_items(self) -> list:
        """
        Return list of stored items which were marked as updating

        Only available in SmartHomeNG versions **v1.9.4 and up**.
        """
        return [self._plg_item_dict[item_path]['item'] for item_path in self._plg_item_dict if self._plg_item_dict[item_path]['is_updating']]

    def get_items_for_mapping(self, mapping: str) -> list:
        """
        Returns a list of items that should receive data for the given mapping

        Only available in SmartHomeNG versions **v1.9.4 and up**.

        :param mapping: mapping, for which the receiving items should be returned
        :type mapping: str

        :return: List of items
        :rtype: list
        """
        return self._item_lookup_dict.get(mapping, [])

    def get_mappings(self) -> list:
        """
        Returns a list containing all mappings, which have items associated with it

        Only available in SmartHomeNG versions **v1.9.4 and up**.

        :return: List of mappings
        :rtype: list
        """
        return list(self._item_lookup_dict.keys())

    def unparse_item(self, item) -> bool:
        """
        Ensure that changes to <item> are no longer propagated to this plugin

        :param item: item to unparse
        :type item: class Item
        """
        try:
            item.remove_method_trigger(self.update_item)
            return True
        except Exception:
            return False

    def get_configname(self) -> str:
        """
        return the name of the plugin instance as defined in plugin.yaml (section name)

        :return: name of the plugin instance as defined in plugin.yaml
        :rtype: str
        """
        return self._configname


    def _set_configname(self, configname: str) -> None:
        """
        set the name of the plugin instance as defined in plugin.yaml (section name)

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :param configname: name of the plugin instance as defined in plugin.yaml
        :type configname: str
        """
        self._configname = configname


    def get_shortname(self) -> str:
        """
        return the shortname of the plugin (name of it's directory)

        :return: shortname of the plugin
        :rtype: str
        """
        return self._shortname


    def _set_shortname(self, shortname: str) -> None:
        """
        ...

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :param shortname: short name of the plugin (name of it's directory)
        :type shortname: str
        """
        self._shortname = shortname


    def get_instance_name(self) -> str:
        """
        Returns the name of this instance of the plugin

        :return: instance name
        :rtype: str
        """
        return self.__instance


    def _set_instance_name(self, instance: str) -> None:
        """
        set instance name of the plugin

        :Note: Usually **you don't need to call this method**, since the instance name is set during startup from the plugin configuration in etc/plugin.yaml

        :param instance: Name of this instance of the plugin
        :type instance: str
        """
        if hasattr(self, 'ALLOW_MULTIINSTANCE') and self.ALLOW_MULTIINSTANCE:
            self.__instance = instance
        elif hasattr(self, 'ALLOW_MULTIINSTANCE') and not self.ALLOW_MULTIINSTANCE:
            self.logger.warning(f"Plugin '{self.get_shortname()}': Only multi-instance capable plugins allow setting a name for an instance")


    def get_fullname(self) -> str:
        """
        return the full name of the plugin (shortname & instancename)

        :return: full name of the plugin
        :rtype: str
        """
        if self.get_instance_name() == '':
            return self.get_shortname()
        else:
            return self.get_shortname() + '_' + self.get_instance_name()


    def get_classname(self) -> str:
        """
        return the classname of the plugin

        :return: classname of the plugin
        :rtype: str
        """
        return self._classname


    def _set_classname(self, classname: str) -> None:
        """
        ...

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :param classname: name of the plugin's class
        :type classname: str
        """
        self._classname = classname


    def get_version(self, extended: bool=False) -> str:
        """
        Return plugin version

        :param extended: If True, returned version string contains (pv) if not the latest version is loaded
        :type extended: bool

        :return: plugin version
        :rtype: str
        """
        if extended and ('_pv_' in self._plugin_dir):
            return self.PLUGIN_VERSION + ' (pv)'
        else:
            return self.PLUGIN_VERSION


    def _set_multi_instance_capable(self, mi: bool) -> bool:
        """
        Sets information if plugin is capable of multi instance handling (derived from metadate),
        but only, if ALLOW_MULTIINSTANCE is not set in source code

        :param mi: True, if plugin is multiinstance capable
        :type mi: bool
        :return: True, if success or ALLOW_MULTIINSTANCE == mi
        :rtype: bool
        """
        if hasattr(self, 'ALLOW_MULTIINSTANCE') and (self.ALLOW_MULTIINSTANCE is not None):
            return (self.ALLOW_MULTIINSTANCE == mi)
        else:
            self.ALLOW_MULTIINSTANCE = mi
        return True


    def is_multi_instance_capable(self) -> bool:
        """
        Returns information if plugin is capable of multi instance handling

        :return: True: If multiinstance capable
        :rtype: bool
        """
        if not hasattr(self, 'ALLOW_MULTIINSTANCE') or self.ALLOW_MULTIINSTANCE is None:
            return False
        return self.ALLOW_MULTIINSTANCE


    def get_plugin_dir(self) -> str:
        """
        return the directory where the pluing files are stored in

        :return: name of the directory
        :rtype: str
        """
        return self._plugin_dir


    def _set_plugin_dir(self, dir: str) -> None:
        """
        Set the object's local variable `_plugin_dir` to root directory of the plugins.
        You can reference the main object of SmartHmeNG by using self._plugin_dir.

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin by PluginWrapper

        :param dir: name of the directory where the plugin resides in
        :type dir: str
        """
        self._plugin_dir = dir


    def get_info(self) -> str:
        """
        Returns a small plugin info like: class, version and instance name

        :return: plugin Info
        :rtype: str
        """
        return f"Plugin: '{self.get_shortname()}.{self.__class__.__name__}', Version: '{self.get_version()}', Instance: '{self.get_instance_name()}'"


    def get_parameter_value(self, parameter_name: str) -> Any:
        """
        Returns the configured value for the given parameter name

        If the parameter is not defined, None is returned

        :param parameter_name: Name of the parameter for which the value should be retrieved
        :type parameter_name: str

        :return: Configured value
        :rtype: depends on the type of the parameter definition
        """
        return self._parameters.get(parameter_name, None)


    def get_parameter_value_for_display(self, parameter_name: str) -> Any:
        """
        Returns the configured value for the given parameter name

        If the parameter is not defined, None is returned
        If the parameter is marked as 'hide', only '*'s are returned

        :param parameter_name: Name of the parameter for which the value should be retrieved
        :type parameter_name: str

        :return: Configured value
        :rtype: depends on the type of the parameter definition
        """
        param = self._parameters.get(parameter_name, None)
        if param == '' or param is None:
            return ''
        if self._hide_parameters.get(parameter_name, False):
            return '******'
        else:
            return param

    def update_config_section(self, param_dict: dict) -> None:
        """
        Update the config section of ../etc/plugin.yaml

        :param param_dict: dict with the parameters that should be updated

        :return:
        """
        param_names = list(self.metadata.parameters.keys())
        self.logger.debug(f"update_config_section: Beginning to update section '{self._configname}' of ../etc/plugin.yaml")
        self.logger.debug(f"update_config_section: valid parameter names to update = {param_names}")
        self.logger.info(f"update_config_section: Config file = '{self._configfilename}', update data = {param_dict}")

        # read plugin.yaml
        plugin_conf = shyaml.yaml_load_roundtrip(self._configfilename)
        sect = plugin_conf.get(self._configname)
        if sect is None:
            self.logger.error(f"update_config_section: Config section '{self._configname}' not found in ../etc/plugin.yaml")
            return

        parameters_changed = False
        for param in param_dict:
            if param in param_names:
                if self.metadata.parameters[param]['type'] == 'num':
                    if param_dict[param] == '':
                        this_param = ''
                    else:
                        this_param = float(param_dict[param])
                elif self.metadata.parameters[param]['type'] == 'int':
                    if param_dict[param] == '':
                        this_param = ''
                    else:
                        try:
                            this_param = int(float(param_dict[param]))
                        except ValueError:
                            self.logger.error(f"update_config_section: Parameter {param} -> Cannot convert '{param_dict[param]}' to type 'int'")
                else:
                    this_param = param_dict[param]
                self.logger.info(f"update_config_section: Changing Parameter '{param}' -> type = '{self.metadata.parameters[param]['type']}' from '{sect.get(param, None)}' to '{this_param}'")
                if param_dict[param] == '' or param_dict[param] == {} or param_dict[param] == []:
                    try:
                        del sect[param]
                    except KeyError:
                        pass
                else:
                    sect[param] = this_param
                parameters_changed = True
            else:
                self.logger.error(f"update_config_section: Invalid parameter '{param}' specified for update")

        self.logger.debug(f"update_config_section: Config section content = '{sect}'")
        # write plugin.yaml
        if parameters_changed:
            shyaml.yaml_save_roundtrip(self._configfilename, plugin_conf, True)
        self.logger.debug(f"update_config_section: Finished updating section '{self._configname}' of ../etc/plugin.yaml")

    def get_loginstance(self) -> str:
        """
        Returns a prefix for logmessages of multi instance capable plugins.

        The result is an empty string, if the instancename is empty. Otherwise the result
        is a string containing the instance name preseeded by a '@' and traild by ': '.

        This way it is easy to show the instance name in log messages. Just write

        self.logger.info(self.get_loginstance()+"Your text")

        and the logmessage is preseeded by the instance name, if needed.

        :return: instance name for logstring
        :rtype: str
        """
        if self.__instance == '':
            return ''
        else:
            return self.__instance + '@: '


    def __get_iattr(self, attr: str) -> str:
        """
        Returns the given item attribute name for this plugin instance
        (by adding the instance to the attribute name)

        :param attr: name of attribute
        :type attr: str

        :return: attributr
        :rtype: str
        """
        if self.__instance == '':
            return attr
        else:
            return f"{attr}@{self.__instance}"


    def __get_iattr_conf(self, conf: str, attr: str) -> Any:
        """
        returns item attribute name including instance if required and found
        in item configuration

        :param conf: item configuration
        :param attr: attribute name
        :type conf: str
        :type attr: str

        :return: name of item attribute (including instance) or None (if not found)
        :rtype: str
        """
        __attr = self.__get_iattr(attr)
        if __attr in conf:
            return __attr
        elif f"{attr}@*" in conf:
            return f"{attr}@*"
        return None


    def has_iattr(self, conf: str, attr: str) -> bool:
        """
        checks item configuration for an attribute

        :param conf: item configuration
        :param attr: attribute name

        :return: True, if attribute is in item configuration
        """
        __attr = self.__get_iattr_conf(conf, attr)
        return __attr is not None


    def get_iattr_value(self, conf: str, attr: str, default=None) -> str:
        """
        Returns value for an attribute from item config

        Parameter default is only available in SmartHomeNG versions **v1.10.0 and up**.

        :param conf: item configuration
        :param attr: attribute name
        :param default: Return-value, if attribute is not found

        :return: value of an attribute
        """
        __attr = self.__get_iattr_conf(conf, attr)
        return default if __attr is None else conf[__attr]


    def set_attr_value(self, conf: str, attr: str, value: str) -> None:
        """
        Set value for an attribute in item configuration

        :param conf: item configuration
        :param attr: attribute name
        :param value: value to set the atteibute to
        :type conf: str
        :type attr: str
        :type value: str
        """
        __attr = self.__get_iattr_conf(conf, attr)
        if __attr is not None:
            conf[self.__get_iattr(attr)] = value


    def __new__(cls, *args, **kargs) -> Any:
        """
        This method ic called during the creation of an object of the class SmartPlugin.

        It tests, if PLUGIN_VERSION is defined.
        """
        if not hasattr(cls, 'PLUGIN_VERSION'):
            raise NotImplementedError("'Plugin' subclasses should have a 'PLUGIN_VERSION' attribute")
        return SmartObject.__new__(cls, *args, **kargs)


    def get_sh(self) -> object:
        """
        Return the main object of smarthomeNG (usually refered to as **smarthome** or **sh**)
        You can reference the main object of SmartHomeNG by using self.get_sh() in your plugin

        :return: the main object of smarthomeNG (usually refered to as **smarthome** or **sh**)
        :rtype: object
        """
        return self._sh


    def _set_sh(self, smarthome: object) -> None:
        """
        Set the object's local variable `_sh` to the main smarthomeNG object.
        You can reference the main object of SmartHomeNG by using self._sh.

        :Note: **Usually you don't need to call this method**, since it is called during loading of the plugin

        :param smarthome: the main object of smarthomeNG
        :type smarthome: object
        """
        self._sh = smarthome

        if self.shtime is None:
            self.shtime = Shtime.get_instance()


    def get_module(self, modulename: str) -> object:
        """
        Test if module http is loaded and if loaded, return a handle to the module
        """
        try:
            mymod = Modules.get_instance().get_module(modulename)
        except Exception:
            mymod = None
        if mymod is None:
            self.logger.error(f"Module '{modulename}' not loaded")
        else:
            self.logger.info(f"Using module '{str(mymod._shortname)}'")
        return mymod


    def path_join(self, path, dir):
        """
        Join an existing path and a directory
        """
        return os.path.join(path, dir)

    def now(self):
        """
        Returns SmartHomeNGs current time (timezone aware)
        """
        return self.shtime.now()

    def scheduler_return_next(self, name: str) -> Any:
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        self.logger.debug(f"scheduler_return_next: name = {name}")
        return self._sh.scheduler.return_next(name, from_smartplugin=True)

    def scheduler_trigger(self, name, obj=None, by=None, source=None, value=None, dest=None, prio=3, dt=None) -> None:
        """
        This methods triggers the scheduler entry for a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.trigger method from lib.scheduler
        """
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        if by is None:
            by = f'Plugin {name}'
        parameters = ', '.join([f'{k}={v!r}' for k, v in locals().items()
                                if v and k not in ['name', 'self', 'obj']])
        self.logger.debug(f"scheduler_trigger: name = {name}, parameters: {parameters}")
        self._sh.scheduler.trigger(name, obj, by, source, value, dest, prio, dt, from_smartplugin=True)

    def scheduler_add(self, name: str, obj: object, prio: int=3, cron=None, cycle=None, value=None, offset=None, next=None) -> None:
        """
        This methods adds a scheduler entry for a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.add method from lib.scheduler
        """
        self._schedulers.append(name)
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        parameters = ', '.join([f'{k}={v!r}' for k, v in locals().items()
                                if v and k not in ['name', 'self', 'obj']])
        self.logger.debug(f"scheduler_add: name = {name}, parameters: {parameters}")
        self._sh.scheduler.add(name, obj, prio, cron, cycle, value, offset, next, from_smartplugin=True)

    def scheduler_change(self, name: str, **kwargs) -> None:
        """
        This methods changes a scheduler entry of a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.change method from lib.scheduler
        """
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        kwargs['from_smartplugin'] = True
        parameters = ', '.join([f'{k}={v!r}' for k, v in kwargs.items()])
        self.logger.debug(f"scheduler_change: name = {name}, parameters: {parameters}")
        self._sh.scheduler.change(name, **kwargs)

    def scheduler_remove(self, name: str) -> None:
        """
        This methods removes a scheduler entry of a plugin-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.remove method from lib.scheduler
        """
        try:
            self._schedulers.remove(name)
        except ValueError:
            self.logger.warning(f'tried to remove scheduler {name} but scheduler not in list')
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        self.logger.debug(f"scheduler_remove: name = {name}")
        self._sh.scheduler.remove(name, from_smartplugin=True)

    def scheduler_get(self, name: str) -> dict:
        """
        This methods gets a scheduler entry of a plugin-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.get method from lib.scheduler
        """
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        self.logger.debug(f"scheduler_get: name = {name}")
        return self._sh.scheduler.get(name, from_smartplugin=True)

    def scheduler_get_all(self):
        """ This method returns a list of all added schedulers """
        return self._schedulers

    def scheduler_remove_all(self):
        """ This method removes all schedulers added by the plugin """
        for sched in self._schedulers:
            try:
                self.scheduler_remove(sched)
            except Exception:
                pass

    # ----------------------------------------------------------------------------------
    #   Ascyncio handling
    # ----------------------------------------------------------------------------------

    def asyncio_state(self) -> str:
        """
        Returns the state of asyncio for the plugin
         - 'unused'  - If the plugin does not use asyncio (the start_asyncio method has not been successfully executed)
         - 'running' - An active eventloop is beeing processed
         - 'stopped' - There is no active eventloop

        :return: 'unused' | 'running' | 'stopped'
        """
        return self._asyncio_state

    def start_asyncio(self, plugin_coro: Coroutine) -> None:
        """
        Start the thread for the asyncio loop

        The started asyncio thread sets up the asyncio environment and starts the eventloop.
        The given plugin_coro is added as the main task to the eventloop.

        This routine is to be called from the plugin's run() method

        :param plugin_coro: The asyncio coroutine which implements the async part of the plugin
        """
        self._used_plugin_coro = plugin_coro
        self._start_known_asyncio_coro()

    def _start_known_asyncio_coro(self) -> None:
        """
        Start the thread for the asyncio loop, when plugin_coro is already known

        The started asyncio thread sets up the asyncio environment and starts the evemtloop.
        This routine is to be called from the plugin's run() method.
        """
        if self._used_plugin_coro is None:
            self.logger.error("Called '_start_known_asyncio_coro()' without known plugin_coro")
            return

        threadname = 'plugins.'+self.get_fullname()+'.asyncio'
        try:
            self.pluginThread = threading.Thread(target=self._asyncio_loop_thread, name=threadname, daemon=False, kwargs={'plugin_coro': self._used_plugin_coro})
            self.logger.info(f"Starting thread {threadname} for asyncio loop...")
            self.pluginThread.start()
        except Exception as e:
            self.logger.error(f"Cannot start thread '{threadname}' - Error: {e}")

    def stop_asyncio(self) -> None:
        """
        stop the eventloop and the thread it is running in

        This routine is to be called from the plugin's stop() method.

        """
        self.logger.info("Shutting down asyncio loop and thread...")

        self.put_command_to_run_queue('STOP')
        time.sleep(3)
        try:
            self.pluginThread.join()
            self.logger.debug("_asyncio_loop_thread of plugin stopped")
        except Exception as err:
            self.logger.notice(f"Error stopping _asyncio_loop_thread: {err}")
            pass
        self._asyncio_state = 'stopped'

    def _asyncio_loop_thread(self, plugin_coro: Coroutine) -> None:
        """
        Thread to start and execute the asyncio event loop

        It starts the main task, which starts the plugin coroutine as a task

        :param plugin_coro: Coroutine that should be started in the eventloop of the asyncio-thread
        """
        self.logger.debug("_asyncio_loop_thread of plugin started")

        asyncio.run(self._asyncio_main(plugin_coro))

    async def _asyncio_main(self, plugin_coro: Coroutine) -> None:
        """
        main coroutine to set up the environment for the coroutine of the specific plugin

        :param plugin_coro: Coroutine that should be started in the eventloop of the asyncio-thread
        """
        self.logger.debug("_asyncio main task of plugin started")
        self._asyncio_loop = asyncio.get_event_loop()
        task = asyncio.current_task()
        task.set_name('MainTask')
        # Create queue to send termination command to plugin_coro when the plugin should be stopped
        self._run_queue = asyncio.Queue()

        # Create the main task of the plugin and await it
        self.task = asyncio.create_task(plugin_coro, name='PluginTask')
        self._asyncio_state = 'running'
        try:
            await self.task
        except Exception as ex:
            self.logger.exception(f"Exception raised in PluginTask: {ex}")

        self._asyncio_state = 'stopped'
        self._asyncio_loop = None
        self.logger.debug("_asyncio main task of plugin finished")

    def run_asyncio_coro(self, coro: Coroutine, return_exeption: bool = False) -> Any:
        """
        Run a coroutine in the eventloop of the plugin

        When the asyncio eventloop of the plugin is running, this method can be used to add a coroutine
        to the eventloop from the part of the plugin which is thread operated.
        E.g.: This can be used in the plugins update_item() method to send data to the device through an asyncio package.

        This method waits for the coroutine to be finished, to be able to return the result of the coroutine.

        :param coro: A coroutine that should be run in the eventloop of the asyncio-thread
        :param return_exeption: If set to True, run_asyncio_coro returns exceptions instead of handling (logging) them itself

        return: The result of the coroutine
        """
        if self._asyncio_loop is None:
            self.logger.error(f"run_asyncio_coro: Cannot run coro '{coro}' because no eventloop is active")
            return
        try:
            future = asyncio.run_coroutine_threadsafe(coro, self._asyncio_loop)
            result = future.result(timeout=60)
        except Exception as ex:
            result = None
            if return_exeption:
                raise Exception( ex )
            else:
                self.logger.exception(f"run_asyncio_coro: Exception {ex} ({coro=}, loop={self._asyncio_loop})")
        return result

    async def wait_for_asyncio_termination(self) -> None:
        """
        Wait for the command to stop the plugin_coro

        This is used to block the plugin_coro until the plugin should be stopped.

        When the plugin should be stopped, a string 'STOP' is written into the queue
        """
        queue_command = ''
        while queue_command != 'STOP':
            queue_command = await self._run_queue.get()
            if queue_command != 'STOP':
                # put command back to queue?
                await asyncio.sleep(0.1)

    def put_command_to_run_queue(self, command: str) -> None:
        """
        Put an entry to the run-queue (if implemented in the plugin_coro)

        :param command: command to be executed by the plugin_coro
        """
        if self._asyncio_loop is not None:
            self.logger.info(f"Writing command '{command}' to run-queue")
            try:
                # Send a command to plugin_coro
                asyncio.run_coroutine_threadsafe(self._run_queue.put(command), self._asyncio_loop)
            except Exception as e:
                self.logger.warning(f"put_command_to_run_queue: Exception '{e}' in _run_queue.put ({self._asyncio_loop=})")
            time.sleep(3)
        else:
            self.logger.warning(f"put_command_to_run_queue: Cannot write command '{command}' to run-queue, no active event-loop")

    async def get_command_from_run_queue(self) -> str:
        """
        Get an entry from the run-queue

        When the plugin should be stopped, a string 'STOP' is written into the queue and the plugin_coro can check for
        the string 'STOP' and terminate itself.

        :return: First command from the queue
        """
        queue_item = await self._run_queue.get()
        return queue_item

    async def list_asyncio_tasks(self) -> None:
        """
        Log a list of the tasks that are in the eventloop

        The intention of this method is to support the plugin development/debugging. It can be called
        from the executor plugin or from the eval-syntax-checker of the admin gui
        """
        self.logger.notice("list_asyncio_tasks: Task list")
        tasks = asyncio.all_tasks()
        for task in tasks:
            if task.get_coro().__name__ == 'list_asyncio_tasks':
                task.set_name('ListTasks')
            self.logger.notice(f" - {task}")

    def translate(self, txt, vars=None, block=None):
        """
        Returns translated text for class SmartPlugin
        """
        txt = str(txt)
        if block:
            self.logger.warning(f"unsuported 3. parameter '{block}' used in translation function _( ... )")

        if self._add_translation is None:
            # test initially, if plugin has additional translations
            translation_fn = os.path.join(self._plugin_dir, 'locale.yaml')
            self._add_translation = os.path.isfile(translation_fn)

        if self._add_translation:
            return lib_translate(txt, vars, plugin_translations='plugin/'+self.get_shortname())
        else:
            return lib_translate(txt, vars)


    def init_webinterface(self, WebInterface=None) -> bool:
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        if WebInterface is None:
            return False

        try:
            # try/except to handle running in a core version that does not support modules
            self.mod_http = Modules.get_instance().get_module('http')
        except:
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

#
# deprecated methods, kept in place in case anybody still uses them
#

    def _get_itemlist(self):
        self._sh._deprecated_warning('SmartPlugin.get_items()')
        return self.get_items()

    def _append_to_itemlist(self, item):
        self._sh._deprecated_warning('SmartPlugin.add_item()')
        self.add_item(item)



#from lib.module import Modules


class SmartPluginWebIf():

    def __init__(self, **kwargs):
        pass

    def init_template_environment(self):
        """
        Initialize the Jinja2 template engine environment

        :return: Jinja2 template engine environment
        :rtype: object
        """
        try:
            from jinja2 import Environment, FileSystemLoader
        except:
            pass

        mytemplates = self.plugin.path_join(self.webif_dir, 'templates')
        globaltemplates = self.plugin.mod_http.gtemplates_dir
        tplenv = Environment(loader=FileSystemLoader([mytemplates, globaltemplates]))

        tplenv.globals['isfile'] = self.is_staticfile
        tplenv.globals['_'] = self.translate        # use translate method of webinterface class
        tplenv.globals['len'] = len
        return tplenv


    def is_staticfile(self, path):
        """
        Method tests, if the given pathname points to an existing file in the webif's static
        directory or the global static directory gstatic in the http module

        This method extends the jinja2 template engine

        :param path: path to test
        :param type: str

        :return: True if the file exists
        :rtype: bool
        """
        if path.startswith('/gstatic/'):
            complete_path = self.plugin.path_join(self.plugin.mod_http.gstatic_dir, path[len('/gstatic/'):])
        else:
            complete_path = self.plugin.path_join(self.webif_dir, path)
        from os.path import isfile as isfile
        return isfile(complete_path)


    def translate(self, txt, vars=None):
        """
        Returns translated text for class SmartPluginWebIf

        This method extends the jinja2 template engine _( ... ) -> translate( ... )
        """
        txt = str(txt)

        if self.plugin._add_translation is None:
            # test initially, if plugin has additional translations
            translation_fn = os.path.join(self.plugin._plugin_dir, 'locale.yaml')
            self.plugin._add_translation = os.path.isfile(translation_fn)

        if self.plugin._add_translation:
            return lib_translate(txt, vars, plugin_translations='plugin/' + self.plugin.get_shortname(), module_translations='module/http')
        else:
            return lib_translate(txt, vars, module_translations='module/http')


