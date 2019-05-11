#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 Marcus Popp                               marcus@popp.mx
# Copyright 2016 The SmartHomeNG team
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
This library does the handling and parsing of the configuration of SmartHomeNG.


:Warning: This library is part of the core of SmartHomeNG. It **should not be called directly** from plugins!

"""

import copy
import logging
import collections
import keyword
import os

from lib.utils import Utils
import lib.shyaml as shyaml
from lib.constants import (YAML_FILE, CONF_FILE)
logger = logging.getLogger(__name__)

valid_item_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
valid_attr_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@*'
digits = '0123456789'
reserved = ['set', 'get', 'property']

REMOVE_ATTR = 'attr'
REMOVE_PATH = 'path'

def parse_basename(basename, configtype=''):
    '''
    Load and parse a single configuration and merge it to the configuration tree
    The configuration is only specified by the basename.
    At the moment it looks for a .yaml file or a .conf file
    .yaml files take preference

    :param basename: Name of the configuration
    :param configtype: Optional string with config type (only used for log output)
    :type basename: str
    :type configtype: str

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict

    '''
    config = parse(basename+YAML_FILE)
    if config == {}:
        config = parse(basename+CONF_FILE)
    if config == {}:
        if not (configtype == 'logics'):
            logger.critical("No file '{}.*' found with {} configuration".format(basename, configtype))
    return config


def parse_itemsdir(itemsdir, item_conf, addfilenames=False, struct_dict={}):
    '''
    Load and parse item configurations and merge it to the configuration tree
    The configuration is only specified by the name of the directory.
    At the moment it looks for .yaml files and a .conf files
    Both filetypes are read, even if they have the same basename

    :param itemsdir: Name of folder containing the configuration files
    :param item_conf: Optional OrderedDict tree, into which the configuration should be merged
    :type itemsdir: str
    :type item_conf: OrderedDict

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict

    '''
    logger.info("parse_itemsdir: Beginning to parse items directory {}".format(itemsdir))
    for item_file in sorted(os.listdir(itemsdir)):
        if item_file.endswith(CONF_FILE) or item_file.endswith(YAML_FILE):
            if item_file == 'logic'+YAML_FILE and itemsdir.find('lib/env/') > -1:
                logger.info("parse_itemsdir: skipping logic definition file = {}".format( itemsdir+item_file ))
            else:
                try:
                    item_conf = parse(itemsdir + item_file, item_conf, addfilenames, parseitems=True, struct_dict=struct_dict)
                except Exception as e:
                    logger.exception("Problem reading {0}: {1}".format(item_file, e))
                    continue
    logger.info("parse_itemsdir: Finished parsing items directory {}".format(itemsdir))
    return item_conf


def parse(filename, config=None, addfilenames=False, parseitems=False, struct_dict={}):
    '''
    Load and parse a configuration file and merge it to the configuration tree
    Depending on the extension of the filename, the apropriate parser is called

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :type filename: str
    :type config: OrderedDict

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict

    '''
    if filename.endswith(YAML_FILE) and os.path.isfile(filename):
         return parse_yaml(filename, config, addfilenames, parseitems, struct_dict)
    elif filename.endswith(CONF_FILE) and os.path.isfile(filename):
        return parse_conf(filename, config)
    return {}


# --------------------------------------------------------------------------------------

def remove_keys(ydata, func, remove=[REMOVE_ATTR], level=0, msg=None, key_prefix=''):
    '''
    Removes given keys from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :param func: the function to call to check for removal (Example: lambda k: k.startswith('comment'))
    :param level: optional subtree level (used for recursion)
    :type ydata: OrderedDict
    :type func: function
    :type level: int

    '''
    try:
        level_keys = list(ydata.keys())
        for key in level_keys:
            key_str = str(key)
            key_dict = type(ydata[key]).__name__ in ['dict','OrderedDict']
            if  not key_dict:
                key_remove = REMOVE_ATTR in remove and func(key_str)
            else:
                key_remove = REMOVE_PATH in remove and func(key_str)
            if key_remove:
                if msg:
                    logger.warn(msg.format(key_prefix+key_str))
                ydata.pop(key)
            elif key_dict:
                remove_keys(ydata[key], func, remove, level+1, msg, key_prefix+key_str+'.')
    except Exception as e:
        logger.error("Problem removing key from '{}', probably invalid YAML file: {}".format(str(ydata), e))



def remove_comments(ydata, filename=''):
    '''
    Removes comments from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :type ydata: OrderedDict

    '''
    remove_keys(ydata, lambda k: k.startswith('comment'), [REMOVE_ATTR])


def remove_digits(ydata, filename=''):
    '''
    Removes keys starting with digits from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :type ydata: OrderedDict

    '''
    remove_keys(ydata, lambda k: k[0] in digits, [REMOVE_ATTR, REMOVE_PATH], msg="Problem parsing '{}' in file '"+filename+"': item starts with digits")


def remove_reserved(ydata, filename=''):
    '''
    Removes keys that are reserved keywords from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :type ydata: OrderedDict

    '''
    remove_keys(ydata, lambda k: k in reserved, [REMOVE_PATH], msg="Problem parsing '{}' in file '"+filename+"': item using reserved word set/get")


def remove_keyword(ydata, filename=''):
    '''
    Removes keys that are reserved Python keywords from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :type ydata: OrderedDict

    '''
    remove_keys(ydata, lambda k: keyword.iskeyword(k), [REMOVE_PATH], msg="Problem parsing '{}' in file '"+filename+"': item using reserved Python keyword")


def remove_invalid(ydata, filename=''):
    '''
    Removes invalid chars in item from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :type ydata: OrderedDict

    '''
    valid_chars = valid_item_chars + valid_attr_chars
    remove_keys(ydata, lambda k: True if True in [True for i in range(len(k)) if k[i] not in valid_chars] else False, [REMOVE_ATTR, REMOVE_PATH], msg="Problem parsing '{}' in file '"+filename+"': Invalid character. Valid characters are: " + str(valid_chars))


def merge(source, destination):
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
    try:
        for key, value in source.items():
            if isinstance(value, collections.OrderedDict):
                # get node or create one
                node = destination.setdefault(key, collections.OrderedDict())
                merge(value, node)
            else:
                if type(value).__name__ == 'list':
                    destination[key] = value
                else:
                    # convert to string and remove newlines from multiline attributes
                    destination[key] = str(value).replace('\n','')
    except:
        logger.error("Problem merging subtrees, probably invalid YAML file")

    return destination


#-------------------------------------------------------------------------------------
# Handling of structs while loading item tree from yaml files
#

def nested_get(input_dict, path):
    internal_dict_value = input_dict
    nested_key = path.split('.')
    for k in nested_key:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value


def nested_put(output_dict, path, value):
    '''

    :param output_dict: dict structure to write to
    :param path: path to write to
    :param value: value to write to the nested key
    :return:
    '''
    internal_dict_value = output_dict
    nested_key = path.split('.')
    for k in nested_key:
        if internal_dict_value.get(k, None) is None:
            if isinstance(output_dict, collections.OrderedDict):
                internal_dict_value[k] = collections.OrderedDict()
            else:
                internal_dict_value[k] = {}
        internal_last_dict_value = internal_dict_value
        internal_dict_value = internal_dict_value.get(k, None)
    internal_last_dict_value[nested_key[len(nested_key)-1]] = value
    return


def search_for_struct_in_items(items, template, struct_dict, config, nestlevel=0, parent=''):
    '''
    Test if the loaded file contains items with 'struct' attribute.

    This function is (recursively) called before merging the loaded file into the item tree

    :param config: OrderedDict tree, into which the configuration should be merged

    :return:
    '''

    result = False
    template = collections.OrderedDict()
    for key in items:
        value = items[key]
        if key == 'struct':
            # item is a struct
            struct_names = value
            # ensure, struct_names is a list
            if isinstance(struct_names, str):
                struct_names = [struct_names]

            instance = items.get('instance', '')
            for struct_name in struct_names:
                wrk = struct_name.find('@')
                if wrk > -1:
                    add_struct_to_template(parent, struct_name[:wrk], template, struct_dict, struct_name[wrk+1:])
                else:
                    add_struct_to_template(parent, struct_name, template, struct_dict, instance)
                if template != {}:
                    config = merge(template, config)
                    template = collections.OrderedDict()
            result = True
        else:
            #item is no struct
            if isinstance(value, collections.OrderedDict):
                # treat value as node
                if parent == '':
                    path = key
                else:
                    path = parent+'.'+key
                # test if a aub-item is a struct
                if search_for_struct_in_items(value, template, struct_dict, config, nestlevel+1, parent=path):
                    result = True

#        if nestlevel == 0:
#            if template != {}:
#                config = merge(template, config)
    return result


def set_attr_for_subtree(subtree, attr, value, indent=0):
    '''

    :param subtree: dict (subtree) to operate on
    :param attr: Attribute to set for every item
    :param value: Value to set the attribute to
    :param indent: indent level (only for debug-logging)

    :return:
    '''
    for k, v in subtree.items():
        if isinstance(v, dict):
            v[attr] = value
            spc = " " * 2 * indent
            logger.debug("set_attr_for_subtree:{} node: {} => {}".format(spc, k, v))
            set_attr_for_subtree(v, attr, value, indent+1)
    return


def add_struct_to_template(path, struct_name, template, struct_dict, instance):
    '''
    Add the referenced struct to the items_template subtree

    :param path: Path of the item which references a struct (template)
    :param struct_name: Name of the to use for the item
    :param template: Template dict to be merged into the item tree
    :param struct_dict: struct to be inserted
    :param instance: For multi instance plugins: instance for which the items work (is derived from item with struct attribute)

    :return:
    '''
    logger.info("add_struct_to_template: 'struct' '{}' reference found in item '{}', instance '{}'".format(struct_name, path, instance))

    struct = struct_dict.get(struct_name, None)
    if struct is None:
        # no struct/template with this name
        nf = collections.OrderedDict()
        nf['name'] = "ERROR: struct '" + struct_name+"' not found!"
        nf['value'] = nf['name']
        nested_put(template, path, nf)
        logger.warning("add_struct_to_template: 'struct' definition for '{}' not found (referenced in item {})".format(struct_name, path))
    else:
        # add struct/template to temporary item(template) tree
        nested_put(template, path, copy.deepcopy(struct))
        if instance != '' or True:
            # add instance to items added by template struct
            subtree = nested_get(template, path)
            # logger.info("add_struct_to_template: Adding 'instance: {}' to template for subtree '{}'".format(instance, path))
            # add instance name to attributes which carry '@instance'
            replace_struct_instance(path, subtree, instance)
        logger.debug("add_struct_to_template: struct_dict = {}".format(struct_dict))

    return


def replace_struct_instance(path, subtree, instance):
    """
    Replace the constant string '@instance' in attribute names with the real instance
    (or remove the constant string '@instance', if the struct has no instace reference)

    :param path:
    :param subtree:
    :param instance:
    :return:
    """
    keys = list(subtree.keys())
    # logger.info("replace_struct_instance: Setting  instance to {} for subtree {}".format(instance, subtree))
    for key in keys:
        # replace recursively
        if Utils.get_type(subtree[key]) == 'collections.OrderedDict':
            replace_struct_instance(path, subtree[key], instance)
        if key.endswith('@instance'):
            if instance == '':
                newkey = key[:-9]
            else:
                newkey = key[:-9] + '@' + instance
            logger.info("- path {}: key '{}' --> newkey '{}'".format(path, key, newkey))
            subtree[newkey] = subtree.pop(key)
    # logger.info("replace_struct_instance: Done set instance to {} for subtree {}".format(instance, subtree))
    return


def parse_yaml(filename, config=None, addfilenames=False, parseitems=False, struct_dict={}):
    """
    Load and parse a yaml configuration file and merge it to the configuration tree

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :param addfilenames: x
    :param parseitems: x
    :param struct_dict: dictionary with stuct definitions (templates) for reading item tree
    :type filename: str
    :type config: bool
    :type addfilenames: bool
    :type parseitems: bool
    :type struct_dict: dict

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict


    The config file should stick to the following setup:

    .. code-block:: yaml

       firstlevel:
           attribute1: xyz
           attribute2: foo
           attribute3: bar

           secondlevel:
               attribute1: abc
               attribute2: bar
               attribute3: foo

               thirdlevel:
                   attribute1: def
                   attribute2: barfoo
                   attribute3: foobar

           anothersecondlevel:
               attribute1: and so on

    where firstlevel, secondlevel, thirdlevel and anothersecondlevel are defined as items and attribute are their respective attribute - value pairs

    Valid characters for the items are a-z and A-Z plus any digit and underscore as second or further characters.
    Valid characters for the attributes are the same as for an item plus @ and *

    """
    logger.debug("parse_yaml: Parsing file {}".format(os.path.basename(filename)))
    if config is None:
        config = collections.OrderedDict()

    items = shyaml.yaml_load(filename, ordered=True)
    if items is not None:
        remove_comments(items, filename)
        remove_digits(items, filename)
        remove_reserved(items, filename)
        remove_keyword(items, filename)
        remove_invalid(items, filename)

        if parseitems:
            # test if file contains 'struct' attribute
            logger.debug("parse_yaml: Checking if file {} contains 'struct' attribute".format(os.path.basename(filename)))
            items_template = collections.OrderedDict()
            if search_for_struct_in_items(items, items_template, struct_dict, config):
                pass
#                if items_template != {}:
#                    config = merge(items_template, config)

        if addfilenames:
            logger.debug("parse_yaml: Add filename = {} to items".format(os.path.basename(filename)))
            _add_filenames_to_config(items, os.path.basename(filename))

        config = merge(items, config)
    return config


def _add_filenames_to_config(items, filename, level=0):
    """
    Adds the name of the config file to the config items

    This routine is used to add the source filename to:
    - be able to display the file an item is defined in (backend page items)
    - to enable editing and storing back of item definitions

    This function calls itself recurselively

    """
    for attr, value in items.items():
        if isinstance(value, dict):
            child_path = dict(value)
            if filename != '':
                value['_filename'] = filename
            _add_filenames_to_config(child_path, filename, level+1)
    return


# --------------------------------------------------------------------------------------


def strip_quotes(string):
    """
    Strip single-quotes or double-quotes from string beggining and end

    :param string: String to strip the quotes from
    :type string: str

    :return: Stripped string
    :rtype: str

    """
    string = string.strip()
    if len(string) > 0:
        if string[0] in ['"', "'"]:  # check if string starts with ' or "
            if string[0] == string[-1]:  # and end with it
                if string.count(string[0]) == 2:  # if they are the only one
                    string = string[1:-1]  # remove them
    return string


def parse_conf(filename, config=None):
    """
    Load and parse a configuration file which is in the old .conf format of smarthome.py
    and merge it to the configuration tree

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :type filename: str
    :type config: bool

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict


    The config file should stick to the following setup:

    .. code-block:: ini

       [firstlevel]
           attribute1 = xyz
           attribute2 = foo
           attribute3 = bar

           [[secondlevel]]
               attribute1 = abc
               attribute2 = bar
               attribute3 = foo

               [[[thirdlevel]]]
                   attribute1 = def
                   attribute2 = barfoo
                   attribute3 = foobar

           [[anothersecondlevel]]
               attribute1 = and so on

    where firstlevel, secondlevel, thirdlevel and anothersecondlevel are defined as items and attribute are their respective attribute - value pairs

    Valid characters for the items are a-z and A-Z plus any digit and underscore as second or further characters.
    Valid characters for the attributes are the same as for an item plus @ and *

    """

    valid_set = set(valid_attr_chars)
    if config is None:
        config = collections.OrderedDict()
    item = config
    with open(filename, 'r', encoding='UTF-8') as f:
        linenu = 0
        parent = collections.OrderedDict()
        lines = iter(f.readlines())
        for raw in lines:
            linenu += 1
            line = raw.lstrip('\ufeff')  # remove BOM
            while line.rstrip().endswith('\\'):
                linenu += 1
                line = line.rstrip().rstrip('\\') + next(lines, '').lstrip()
            line = line.partition('#')[0].strip()
            if line is '':
                continue
            if line[0] == '[':  # item
                brackets = 0
                level = 0
                closing = False
                for index in range(len(line)):
                    if line[index] == '[' and not closing:
                        brackets += 1
                        level += 1
                    elif line[index] == ']':
                        closing = True
                        brackets -= 1
                    else:
                        closing = True
                        if line[index] not in valid_item_chars + "'":
                            logger.error("Problem parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, line, valid_item_chars))
                            return config
                if brackets != 0:
                    logger.error("Problem parsing '{}' unbalanced brackets in line {}: {}".format(filename, linenu, line))
                    return config
                name = line.strip("[]")
                name = strip_quotes(name)

                if len(name) == 0:
                    logger.error("Problem parsing '{}' tried to use an empty item name in line {}: {}".format(filename, linenu, line))
                    return config
                elif name[0] in digits:
                    logger.error("Problem parsing '{}': item starts with digit '{}' in line {}: {}".format(filename, name[0], linenu, line))
                    return config
                elif name in reserved:
                    logger.error("Problem parsing '{}': item using reserved word set/get in line {}: {}".format(filename, linenu, line))
                    return config
                elif keyword.iskeyword(name):
                    logger.error("Problem parsing '{}': item using reserved Python keyword {} in line {}: {}".format(filename, name, linenu, line))
                    return config

                if level == 1:
                    if name not in config:
                        config[name] = collections.OrderedDict()
                    item = config[name]
                    parents = collections.OrderedDict()
                    parents[level] = item
                else:
                    if level - 1 not in parents:
                        logger.error("Problem parsing '{}' no parent item defined for item in line {}: {}".format(filename, linenu, line))
                        return config
                    parent = parents[level - 1]
                    if name not in parent:
                        parent[name] = collections.OrderedDict()
                    item = parent[name]
                    parents[level] = item

            else:  # attribute
                attr, __, value = line.partition('=')
                if not value:
                    continue
                attr = attr.strip()
                if not set(attr).issubset(valid_set):
                    logger.error("Problem parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, attr, valid_attr_chars))
                    continue

                if len(attr) > 0:
                    if attr[0] in digits:
                        logger.error("Problem parsing '{}' attrib starts with a digit '{}' in line {}: {}.".format(filename, attr[0], linenu, attr ))
                        continue
                if '|' in value:
                    item[attr] = [strip_quotes(x) for x in value.split('|')]
                else:
                    item[attr] = strip_quotes(value)
        return config
