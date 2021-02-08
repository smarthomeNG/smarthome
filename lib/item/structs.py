#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2018-2020   Martin Sinn                         m.sinn@gmx.de
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
import collections
import os
import copy

import lib.shyaml as shyaml

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
#   Following methods handle structs
# -----------------------------------------------------------------------------------------

struct_merge_lists = True


class Structs():

    struct_merge_lists = True

    _struct_definitions = collections.OrderedDict()    # definitions of item structures

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def merge_structlists(self, l1, l2, key=''):
        if not self.struct_merge_lists:
            self.logger.warning("merge_structlists: Not merging lists, key '{}' value '{}' is ignored'".format(key, l2))
            return l1       # First wins
        else:
            if not isinstance(l1, list):
                l1 = [l1]
            if not isinstance(l2, list):
                l2 = [l2]
            return l1 + l2


    def add_struct_definition(self, plugin_name, struct_name, struct):
        """
        Add a struct definition

        called when reading in item structs from ../etc/struct.yaml
        or from lib.plugin when reading in plugin-metadata

        :param plugin_name:
        :param struct_name:
        :param struct:
        :return:
        """
        if plugin_name == '':
            name = struct_name
        else:
            name = plugin_name + '.' + struct_name

        self.logger.info("add_struct_definition: struct '{}' = {}".format(name, struct))
        self._struct_definitions[name] = struct
        return


    def merge(self, source, destination, source_name='', dest_name=''):
        '''
        Merges an OrderedDict Tree into another one

        :param source: source tree to merge into another one
        :param destination: destination tree to merge into
        :type source: OrderedDict
        :type destination: OrderedDict

        :return: Merged configuration tree
        :rtype: OrderedDict

        :Example: Run me with nosetests --with-doctest file.py

        .. code-block:: python

            >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
            >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
            >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
            True

        '''
        #self.logger.warning("merge: source_name='{}', dest_name='{}'".format(source_name, dest_name))
        for key, value in source.items():
            if isinstance(value, collections.OrderedDict):
                # get node or create one
                node = destination.setdefault(key, collections.OrderedDict())
                if node == 'None':
                    destination[key] = value
                else:
                    self.merge(value, node, source_name, dest_name)
            else:
                if isinstance(value, list) or isinstance(destination.get(key, None), list):
                    if destination.get(key, None) is None:
                        destination[key] = value
                    else:
                        destination[key] = self.merge_structlists(destination[key], value, key)
                else:
                    # convert to string and remove newlines from multiline attributes
                    if destination.get(key, None) is None:
                        destination[key] = str(value).replace('\n', '')
        return destination


    def resolve_structs(self, struct, struct_name, substruct_names):
        """
        Resolve a struct reference within a struct

        if the struct definition that is to be inserted contains a struct reference, it is resolved first

        :param struct:          struct that contains a struct reference
        :param substruct:       sub-struct definition that shall be inserted
        :param struct_name:     name of the struct that contains a struct reference
        :param substruct_name:  name of the sub-struct definition that shall be inserted
        """

        self.logger.info("resolve_structs: struct_name='{}', substruct_names='{}'".format(struct_name, substruct_names))

        new_struct = collections.OrderedDict()
        structentry_list = list(struct.keys())
        for structentry in structentry_list:
            # copy all existing attributes and sub-entrys of the struct
            if new_struct.get(structentry, None) is None:
                self.logger.debug("resolve_struct: - copy attribute structentry='{}', value='{}'".format(structentry, struct[structentry]))
                new_struct[structentry] = copy.deepcopy(struct[structentry])
            else:
                self.logger.debug("resolve_struct: - key='{}', value is ignored'".format(structentry))
            if structentry == 'struct':
                for substruct_name in substruct_names:
                    # for every substruct
                    self.merge_substruct_to_struct(new_struct, substruct_name, struct_name)
                    # self.logger.info("resolve_struct: ->substruct_name='{}'".format(substruct_name))
                    # substruct = self._struct_definitions.get(substruct_name, None)
                    # # merge in the sub-struct
                    # for key in substruct:
                    #     if new_struct.get(key, None) is None:
                    #         self.logger.info \
                    #             ("resolve_struct: - key='{}', value='{}' -> new_struct='{}'".format(key, substruct[key], new_struct))
                    #         new_struct[key] = copy.deepcopy(substruct[key])
                    #     elif isinstance(new_struct.get(key, None), dict):
                    #         self.logger.info("resolve_struct: - merge key='{}', value='{}' -> new_struct='{}'".format(key, substruct
                    #                                                                                                  [key], new_struct))
                    #         self.merge(substruct[key], new_struct[key], key, struct_name +'. ' +key)
                    #     elif isinstance(new_struct.get(key, None), list) or isinstance(substruct.get(key, None), list):
                    #         new_struct[key] = self.merge_structlists(new_struct[key], substruct[key], key)
                    #     else:
                    #         self.logger.debug("resolve_struct: - key='{}', value '{}' is ignored'".format(key, substruct[key]))

        return new_struct


    def merge_substruct_to_struct(self, main_struct, substruct_name, main_struct_name='?'):

        if substruct_name.startswith('test_'):
            self.logger.info("merge_substruct_to_struct: ->substruct_name='{}'".format(substruct_name))
        substruct = self._struct_definitions.get(substruct_name, None)
        if substruct is None:
            self.logger.error("struct '{}' not found in structdefinitions (used in '{}')".format(substruct_name, main_struct_name))
        else:
            # merge in the sub-struct
            for key in substruct:
                if main_struct.get(key, None) is None:
                    if substruct_name.startswith('test_'):
                        self.logger.info("merge_substruct_to_struct: - key='{}', value='{}' -> new_struct='{}'".format(key, substruct[key], main_struct))
                    main_struct[key] = copy.deepcopy(substruct[key])
                elif isinstance(main_struct.get(key, None), dict):
                    if substruct_name.startswith('test_'):
                        self.logger.info("merge_substruct_to_struct: - merge key='{}', value='{}' -> new_struct='{}'".format(key, substruct
                    [key], main_struct))
                    self.merge(substruct[key], main_struct[key], substruct_name + '.' + key, main_struct_name + '.' + key)
                elif isinstance(main_struct.get(key, None), list) or isinstance(substruct.get(key, None), list):
                    main_struct[key] = self.merge_structlists(main_struct[key], substruct[key], key)
                else:
                    self.logger.debug("merge_substruct_to_struct: - key='{}', value '{}' is ignored'".format(key, substruct[key]))
        return


    def fill_nested_structs(self):
        """
        Resolve struct references in structs and fill in the content of the struct

        :return:
        """
        for struct_name in self._struct_definitions:
            # for every defined struct
            struct = self._struct_definitions[struct_name]
            substruct_names = struct.get('struct', None)
            if substruct_names is not None:
                # stuct has a sub-struct
                if isinstance(substruct_names, str):
                    substruct_names = [substruct_names]
                struct = self.resolve_structs(struct, struct_name, substruct_names)
                self._struct_definitions[struct_name] = struct


    def return_struct_definitions(self, all=True):
        """
        Return all loaded structure template definitions

        :return:
        :rtype: dict
        """
        result = {}
        for struct in self._struct_definitions:
            try:
                plg_name, struct_name = struct.split('.')
            except:
                plg_name = ''
                struct_name = struct
            if struct_name.startswith('_'):
                self.logger.info(f"return_struct_definitions: Internal struct {struct}")
                if all:
                    result[struct] = self._struct_definitions[struct]
            else:
                result[struct] = self._struct_definitions[struct]

        return result


    def load_struct_definitions(self, etc_dir):

        # --------------------------------------------------------------------
        # Read in all struct definitions before reading item definitions
        #
        # structs are merged into the item tree in lib.config
        #
        # structs are read in from metadata file of plugins while loading plugins
        # and from ../etc/struct.yaml
        #
        # Read in item structs from ../etc/struct.yaml
        struct_definitions = shyaml.yaml_load(os.path.join(etc_dir, 'struct.yaml'), ordered=True, ignore_notfound=True)
        if struct_definitions is not None:
            if isinstance(struct_definitions, collections.OrderedDict):
                for key in struct_definitions:
                    self.add_struct_definition('', key, struct_definitions[key])
            else:
                self.logger.error("load_itemdefinitions(): Invalid content in struct.yaml: struct_definitions = '{}'".format(struct_definitions))

        self.fill_nested_structs()

        # for Testing: Save structure of joined item structs
        self.logger.info("load_itemdefinitions(): For testing the joined item structs are saved to {}".format(os.path.join(etc_dir, 'structs_joined.yaml')))
        shyaml.yaml_save(os.path.join(etc_dir, 'structs_joined.yaml'), self._struct_definitions)

