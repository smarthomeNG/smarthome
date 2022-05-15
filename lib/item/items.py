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


"""
This library implements items in SmartHomeNG.

The main class ``Items`` implements the handling for all items. This class has a  static method to get a handle to the
instance of the Items class, that is created during initialization of SmartHomeNG. This method implements a way to
access the API for handling items without having to juggle through the object hierarchy of the running SmartHomeNG.

This API enables plugins and logics to access the details of the items initialized in SmartHomeNG.

Each item is represented by an instance of the class ``Item``.

The methods of the class Items implement the API for items.
They can be used the following way: To call eg. **get_toplevel_items()**, use the following syntax:

.. code-block:: python

    from lib.item import Items
    sh_items = Items.get_instance()

    # to access a method (eg. get_toplevel_items()):
    tl_items = sh_items.get_toplevel_items()


:Note: Do not use the functions or variables of the main smarthome object any more. They are deprecated. Use the methods of the class **Items** instead.

:Note: This library is part of the core of SmartHomeNG. Regular plugins should not need to use this API.  It is manily implemented for plugins near to the core like **backend** and the core itself!

"""
import logging
import re

import lib.utils

from .item import Item
from .structs import Structs


_items_instance = None    # Pointer to the initialized instance of the Items class (for use by static methods)


class Items():
    """
    Items loader class. (Item-methods from bin/smarthome.py are moved here.)

    - An instance is created during initialization by bin/smarthome.py
    - There should be only one instance of this class. So: Don't create another instance

    :param smarthome: Instance of the smarthome master-object
    :type smarthome: object
    """

    __items = []                     # list with the paths of all items that are defined
    __item_dict = {}                 # dict with all the items that are defined in the form: {"<item-path>": "<item-object>", ...}

    _children = []                   # List of top level items

    plugin_attributes = {}           # dict with all item attributes, that are defined by plugins
    plugin_attribute_prefixes = {}   # dict with all item attribute-prefixes, that are defined by plugins
    plugin_prefixes_tuple = None     # tuple for finding if an attribute name starts with one of the prefixes

    structs = None

    def __init__(self, smarthome):
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)

        global _items_instance
        if _items_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            self.logger.critical("A second 'items' object has been created. There should only be ONE instance of class 'Items'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _items_instance = self
        self.structs = Structs()


    # -----------------------------------------------------------------------------------------
    #   Following (static) method of the class Items implement the API for Items in SmartHomeNG
    # -----------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Items class, to be used to access the items-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.item import Items
            items = Items.get_instance()

            # to access a method (eg. return_items()):
            items.return_items()


        :return: items instance
        :rtype: object
        """
        return _items_instance


    # -----------------------------------------------------------------------------------------
    #   Following methods handle structs
    # -----------------------------------------------------------------------------------------

    def add_struct_definition(self, plugin_name, struct_name, struct):
        self.structs.add_struct_definition(plugin_name, struct_name, struct)


    def return_struct_definitions(self, all=True):
        """
        Return all loaded structure template definitions

        :return:
        :rtype: dict
        """
        return self.structs.return_struct_definitions(all)


    def load_itemdefinitions(self, env_dir, items_dir, etc_dir, plugins_dir):
        """
        Load item definitions

        This method is called during initialization of SmartHomeNG to initialize the item tree.
        For that, it loads the item definitions from **../items** directory through calling the function **parse_itemsdir()**
        from **lib.config**

        :param env_dir: path to the directory containing the core's environment item definition files
        :param items_dir: path to the directory containing the user's item definition files
        :param etc_dir: path to the directory containing the user's configuration files (only used for 'struct' support)
        :param plugins_dir: path to the directory containing the plugins (only used for 'struct' support)
        :type env_dir: str
        :type items_dir: str
        :type etc_dir: str
        :type plugins_dir: str
        """

        # --------------------------------------------------------------------
        # Read in all struct definitions before reading item definitions
        #
        # structs are merged into the item tree in lib.config
        #
        # structs are read in from metadata file of plugins while loading plugins
        # and from ../etc/struct.yaml
        #
        # Read in item structs from ../etc/struct.yaml
        self._sh.shng_status['details'] = 'Structs'
        self.structs.load_struct_definitions(etc_dir)


        # --------------------------------------------------------------------
        # Read in item definitions
        #
        self._sh.shng_status['details'] = 'Items'
        item_conf = None
        item_conf = lib.config.parse_itemsdir(env_dir, item_conf)
        item_conf = lib.config.parse_itemsdir(items_dir, item_conf, addfilenames=True, struct_dict=self.structs._struct_definitions)

        for attr, value in item_conf.items():
            if isinstance(value, dict):
                child_path = attr
                try:
                    # (smarthome, parent, path, config):
                    child = Item(self._sh, self, child_path, value, items_instance=_items_instance)
                except Exception as e:
                    self.logger.error("load_itemdefinitions: Item {}: problem creating: {}".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    vars(self._sh)[attr] = child
                    self.add_item(child_path, child)
                    self._children.append(child)
        del(item_conf)  # clean up

        # Test if all used attributes are defined in configuread plugins
        #feature moved to lib.metadata
        #for item in self.return_items():
        #    item._test_attribute_existance()


        # --------------------------------------------------------------------
        # prepare loaded items for run phase of SmartHomeNG
        #
        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'prerun'}

        # Build eval expressions from special functions and triggers before first run
        for item in self.return_items():
            item._init_prerun()

        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'start scheduler'}
        # Start schedulers of the items which have a crontab or a cycle attribute
        for item in self.return_items():
            item._init_start_scheduler()
        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'eval-run'}
        # Run initial eval to set an initial value for the item
        #import time
        #gstart = time.time()
        #gduration = 0.0
        #gcount = 0
        for item in self.return_items():
            item._init_run()
            #start = time.time()
            #calculated = item._init_run()
            #end = time.time()
            #if calculated:
            #    duration = end - start
            #    self.logger.warning(f"_init_run: {item._path}, execution time = {duration}")
            #    gduration += duration
            #    gcount += 1
        #gend = time.time()
        #self.logger.warning(f"_init_run: Totals: duration {gend-gstart}, eval execution time = {gduration} for {gcount} items")

        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items'}
#        self.item_count = len(self.__items)
#        self._sh.item_count = self.item_count()

        # here goes debug output (if needed) after the initialization of all items
        #import lib.metadata as metadata
        #self.logger.notice(f"metadata.all_itemprefixdefinitions: {metadata.all_itemprefixdefinitions.keys()}")



    def add_item(self, path, item):
        """
        Function to to add an item to the dictionary of items.
        If the path does not exist, it is created

        :param path: Path of the item
        :param item: The item itself
        :type path: str
        :type item: object
        """

        if path not in self.__items:
            self.__items.append(path)
        self.__item_dict[path] = item

    # aus bin/smarthome.py
    #    def __iter__(self):
    #        for child in self.__children:
    #            yield child

    def get_toplevel_items(self):
        """
        Returns a list with all items defined at the top level

        :return: items defined at the top level
        :rtype: list
        """
        for child in self._children:
            yield child

    # aus lib.logic.py
    #    def __iter__(self):
    #        for logic in self._logics:
    #            yield logic



    def return_item(self, string):
        """
        Function to return the item for a given path

        :param string: Path of the item to return
        :type string: str

        :return: Item
        :rtype: object
        """

        if string in self.__items:
            return self.__item_dict[string]


    def return_items(self, sorted=False):
        """
        Function to return a list with all defined items

        :param sorted: return list sorted alphabetically, defaults to False
        :type sorted: bool

        :return: List of all items
        :rtype: list
        """

        if sorted:
            for item in sorted(self.__items):
                yield self.__item_dict[item]
        else:
            for item in self.__items:
                yield self.__item_dict[item]


    def match_items(self, regex):
        """
        Function to match items against a regular expression

        :param regex: Regular expression to match items against
        :type regex: str

        :return: List of matching items
        :rtype: list
        """

        regex, __, attr = regex.partition(':')
        #regex = regex.replace('.', '\.').replace('*', '.*') + '$'
        regex = regex.replace(r'.', '\.').replace('*', '.*') + '$'
        regex = re.compile(regex)1
        attr, __, val = attr.partition('[')
        val = val.rstrip(']')
        if attr != '' and val != '':
            return [self.__item_dict[item] for item in self.__items if regex.match(item) and attr in self.__item_dict[item].conf and ((type(self.__item_dict[item].conf[attr]) in [list,dict] and val in self.__item_dict[item].conf[attr]) or (val == self.__item_dict[item].conf[attr]))]
        elif attr != '':
            return [self.__item_dict[item] for item in self.__items if regex.match(item) and attr in self.__item_dict[item].conf]
        else:
            return [self.__item_dict[item] for item in self.__items if regex.match(item)]


    def _attribute_find(self, attr, attr_list):
        """
        Find an attribute in an attribute list

        :param attr:
        :param attr_list:
        :return:

        examples:
            attr_list = ['avm_identifier' , 'avm_data_type@willy_tel', 'avm_wlan_index', 'visu_acl']

            attr                          result
            ---_                          ------
            'willy_tel'                -> False
            '@willy_tel'               -> True
            '@fritz_wz'                -> False

            'avm_data_type@willy_tel'  -> True
            'avm_data_type@fritz_wz'   -> False
            'avm_data_type'            -> False
            'avm_data_type@'           -> True

            'avm_wlan_index'           -> True
            'avm_wlan_index@'          -> True

            'visu_acl'                 -> True
            '@visu_acl'                -> False

        """
        result = False
        if attr.endswith('@'):
            result = any(s for s in attr_list if s.startswith(attr))
            if not result:
                result = attr[:-1] in attr_list
        elif attr.startswith('@'):
            result = any(s for s in attr_list if s.endswith(attr))
        else:
            result = attr in attr_list
        return result


    def find_items(self, conf):
        """
        Function to find items that match the specified configuration

        :param conf: Configuration to look for
        :type conf: str

        :return: list of matching items
        :rtype: list
        """

        for item in self.__items:
            # if conf in self.__item_dict[item].conf:
            #     yield self.__item_dict[item]
            if self._attribute_find(conf, self.return_item(item).property.attributes):
                yield self.__item_dict[item]


    def find_children(self, parent, conf):
        """
        Function to find children with the specified configuration

        :param parent: parent item on which to start the search
        :param conf: Configuration to look for
        :type parent: str
        :type conf: str

        :return: list or matching child-items
        :rtype: list
        """

        children = []
        for item in parent:
            # if conf in item.conf:
            #     children.append(item)
            if self._attribute_find(conf, item.property.attributes):
                children.append(item)
            children += self.find_children(item, conf)
        return children


    def item_count(self):
        """
        Return the number of defined items

        :return: number of items
        :rtype: int
        """
        return len(self.__items)


    def stop(self, signum=None, frame=None):
        """
        Stop what all items are doing

        At the moment, it stops fading of all items
        """
        for item in self.__items:
            self.__item_dict[item]._fading = False


    def add_plugin_attribute(self, plugin_name, attribute_name, attribute):
        """
        Add an attribute definition to the dict of plugin specific item-attributes

        :param plugin_name:    Name of the plugin that defines the attribute
        :param attribute_name: Name of the attribute
        :param attribute:      Metadata that defines the attribute
        :return:
        """
        attribute_name = attribute_name.lower()
        if self.plugin_attributes.get(attribute_name, None) is None:
            self.plugin_attributes[attribute_name] = {}
            self.plugin_attributes[attribute_name]['plugin'] = plugin_name
            self.plugin_attributes[attribute_name]['meta'] = dict(attribute)
            self.logger.info("add_plugin_attribute: {} ({}) -> {}".format(attribute_name, plugin_name, dict(attribute)))
        else:
            if plugin_name != self.plugin_attributes[attribute_name]['plugin']:
                if self.plugin_attributes[attribute_name]['meta']['type'] != attribute['type']:
                    self.logger.error(f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}' with different type definitions {self.plugin_attributes[attribute_name]['meta']['type']}/{attribute['type']}")
                elif not self.plugin_attributes[attribute_name]['meta'].get('duplicate_use', False):
                    self.logger.warning(f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}'")
                else:
                    self.logger.info(f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}'")

    def add_plugin_attribute_prefix(self, plugin_name, prefix_name, prefix):
        """
        Add an attribute-prefix definition to the dict of plugin specific item-attribute prefixes

        :param plugin_name: Name of the plugin that defines the attribute
        :param prefix_name: Name of the attribute-prefix
        :param prefix:      Metadata that defines the attribute-prefix
        :return:
        """
        prefix_name = prefix_name.lower()
        if self.plugin_attribute_prefixes.get(prefix_name, None) is None:
            self.plugin_attribute_prefixes[prefix_name] = {}
            self.plugin_attribute_prefixes[prefix_name]['plugin'] = plugin_name
            self.plugin_attribute_prefixes[prefix_name]['meta'] = dict(prefix)
            self.logger.info("add_plugin_attribute_prefix: {} ({}) -> {}".format(prefix_name, plugin_name, dict(prefix)))
        else:
            if plugin_name != self.plugin_attribute_prefixes[prefix_name]['plugin']:
                self.logger.error("Plugins '{}' and '{}' define the same item-attribute-prefix '{}'".format(self.plugin_attribute_prefixes[prefix_name]['plugin'], plugin_name, prefix_name))


    def plugin_attribute_exists(self, attribute_name):
        """
        Returns the type of the attribute's value

        :param attribute_name: Name of the attribute
        :return:               Type of the attribute's value or None
        """
        meta = self.plugin_attributes.get(attribute_name.lower(), None)
        if meta is not None:
            return True

        if self.plugin_prefixes_tuple is None:
            # Generate tuple on first call to this method
            self.plugin_prefixes_tuple = tuple(self.plugin_attribute_prefixes.keys())
        if attribute_name.startswith(self.plugin_prefixes_tuple):
            return True

        return False


    def get_plugin_attribute_type(self, attribute_name):
        """
        Returns the type of the attribute's value

        :param attribute_name: Name of the attribute
        :return:               Type of the attribute's value or None
        """
        meta = self.plugin_attributes.get(attribute_name.lower, None)
        if meta is None:
            return None
        else:
            return meta['type']
