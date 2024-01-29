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
            if configtype == 'module':
                logger.warning("No valid file '{}.yaml' found with {} configuration".format(basename, configtype))
            else:
                logger.error("No valid file '{}.*' found with {} configuration".format(basename, configtype))
    return config


def parse_itemsdir(itemsdir, item_conf, addfilenames=False, struct_dict={}):
    '''
    Load and parse item configurations and merge it to the configuration tree
    The configuration is only specified by the name of the directory.
    At the moment it looks for .yaml files and a .conf files
    Both filetypes are read, even if they have the same basename

    :param itemsdir:      Name of folder containing the configuration files
    :param item_conf:     Optional OrderedDict tree, into which the configuration should be merged
    :param addfilenames:
    :param struct_dict:   dict with all defined structs (from /etc/structs.yaml and from loaded plugins)
    :type itemsdir:       str
    :type item_conf:      OrderedDict
    :type addfilenames:
    :type struct_dict:    dict / OrderedDict

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict

    '''
    logger.info("parse_itemsdir: Beginning to parse items directory {}".format(itemsdir))
    for item_file in sorted(os.listdir(itemsdir)):
        if not item_file.startswith('.'):
            if item_file.endswith(CONF_FILE) or item_file.endswith(YAML_FILE):
                if item_file == 'logic'+YAML_FILE and itemsdir.find(os.path.join('lib','env')) > -1:
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

    :param struct_dict:   dict with all defined structs (from /etc/structs.yaml and from loaded plugins)
    :type filename: str
    :type config: OrderedDict

    :return: The resulting merged OrderedDict tree
    :rtype: OrderedDict

    '''
    if not filename.startswith('.'):
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
                    logger.warning(msg.format(key_prefix+key_str))
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


struct_merging_active = False
struct_merge_lists = True
special_listentry_found = False


def merge_structlists(l1, l2, key=''):

    if not struct_merging_active:
        global special_listentry_found
        # merge* or merge_unique*
        if (len(l1) > 0 and l1[0] == 'merge_unique*') and (len(l2) > 0 and l2[0] == 'merge_unique*'):
            logger.debug("merge_structlists: merge_unique* l1={}, l2={}".format(l1,l2))
            logger.debug("merge_structlists: both lists contains 'merge_unique*' - l1={}, l2={}, key={}".format(l1, l2, key))
            special_listentry_found = True
            l1 = list(collections.OrderedDict.fromkeys(l1))
            return l1

        if (len(l1) > 0 and l1[0] == 'merge*') and (len(l2) > 0 and l2[0] == 'merge*'):
            logger.debug("merge_structlists: merge* l1={}, l2={}".format(l1,l2))
            logger.debug("merge_structlists: both lists contains 'merge*' - l1={}, l2={}, key={}".format(l1, l2, key))
            special_listentry_found = True
            return l1

        if (len(l2) > 0 and l2[0] == 'merge*'):
            logger.debug("merge_structlists: l2 contains merge* l1={}, l2={}".format(l1,l2))
            logger.debug("merge_structlists: list l2 contains 'merge*' - l1={}, l2={}, key={}".format(l1, l2, key))
            del l2[0]
            l1 = ['merge*'] + l1 + l2
            l2 = ['merge*'] + l2
            return l1

        if (len(l1) > 0 and l1[0] == 'merge*') or (len(l2) > 0 and l2[0] == 'merge*'):
            logger.debug("merge_structlists: l1 or l2 contain merge* l1={}, l2={}".format(l1,l2))
            #logger.warning("merge_structlists: a list contains 'merge*' - l1={}, l2={}, key={}".format(l1, l2, key))
            pass
        return l2       # Last wins

    if not struct_merge_lists:
        #logger.warning("merge_structlists: Not merging lists, key '{}' value '{}' is ignored'".format(key, l2))
        return l1       # First wins
    else:
        if not isinstance(l1, list):
            l1 = [l1]
        if not isinstance(l2, list):
            l2 = [l2]
        return l1 + l2


def merge(source, destination, source_name='', dest_name='', filename=''):
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

#    if struct_merging_active:
    if source.get('_filename', '') == 'test_struct.yaml':
        logger.info("merge {}: source={}, destination={}, source_name={}, dest_name={}".format(source.get('_filename', ''), dict(source), dict(destination), source_name, dest_name))
        ext_logging = True
    else:
        ext_logging = False
    for key, value in source.items():
        try:
            if isinstance(value, collections.OrderedDict):
                # get node or create one
                node = destination.setdefault(key, collections.OrderedDict())
                if node == 'None':
                    destination[key] = value
                else:
                    merge(value, node, source_name, dest_name)
            else:
#                if struct_merging_active:
#                    logger.warning("merge: - value={}, destination.get(key, None)={}".format(value, destination.get(key, None)))
                if isinstance(value, list) or isinstance(destination.get(key, None), list):
                    if destination.get(key, None) is None:
                        destination[key] = value
                    else:
                        if ext_logging:
                            logger.info("merge: call merge_structlists - key={}, value={}, destination.get(key, None)={}".format(key, value, destination.get(key, None)))
                        destination[key] = merge_structlists(destination[key], value, key)
                else:
                    # convert to string and remove newlines from multiline attributes
                    destination[key] = str(value).replace('\n', '')
                    # if destination.get(key, None) is None:
                    #     destination[key] = str(value).replace('\n', '')

                # if type(value).__name__ == 'list':
                #     destination[key] = value
                # else:
                #     # convert to string and remove newlines from multiline attributes
                #     destination[key] = str(value).replace('\n','')
#                if struct_merging_active:
#                    logger.warning("merge: - destination={}".format(dict(destination)))
        except Exception as e:
            logger.error("Problem merging subtrees (key={}), probably invalid YAML file '{}' with entry '{}'. Error: {}".format(key, source_name, destination, e))

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
    internal_last_dict_value = None
    # if struct_merging_active:
    #     logger.warning("nested_put: path = {}, value = {}  -  nested_key = {}".format(path, value, nested_key))
    #     logger.warning("nested_put: - output_dict = {}".format(dict(output_dict)))
    for k in nested_key:
        if internal_dict_value.get(k, None) is None:
            if isinstance(output_dict, collections.OrderedDict):
                internal_dict_value[k] = collections.OrderedDict()
            else:
                internal_dict_value[k] = {}
        internal_last_dict_value = internal_dict_value
        internal_dict_value = internal_dict_value.get(k, None)

    if internal_last_dict_value is not None:
        # if struct_merging_active:
        #     logger.warning("nested_put: - dest subtree = {}".format(dict(internal_last_dict_value[nested_key[len(nested_key)-1]])))
        #     logger.warning("nested_put: - merge struct = {}".format(dict(value)))

        #internal_last_dict_value[nested_key[len(nested_key)-1]] = value
        merge(value, internal_last_dict_value[nested_key[len(nested_key)-1]], 'struct-tree', 'sub-tree')

        # if struct_merging_active:
        #     logger.warning("nested_put: - dest result  = {}".format(dict(internal_last_dict_value[nested_key[len(nested_key)-1]])))

    # if struct_merging_active:
    #     logger.warning("nested_put: - internal_last_dict_value = {}".format(internal_last_dict_value))
    return


def search_for_struct_in_items(items, struct_dict, config, source_name='', parent='', level=0):
    """
    Test if the loaded file contains items with 'struct' attribute.

    This function is (recursively) called before merging the loaded file into the item tree

    :param items:        tree content of a single items.yaml file (or part of it during recursion)
    :param struct_dict:  dict with all defined structs (from /etc/structs.yaml and from loaded plugins)
    :param config:       tree, into which the configuration should be merged
    :param parent:
    :type items:         OrderedDict
    :type config:        OrderedDict
    :return: True, if a struct attribute was expanded
    """

    if source_name.startswith('test_struct'):
        logger.info("search_for_struct_in_items: items.keys()={}, source_name={}, parent={}".format(list(dict(items).keys()), source_name, parent))

    for key in items:
        value = items[key]
        if source_name.startswith('test_struct'):
            if isinstance(value, collections.OrderedDict):
                logger.info("search_for_struct_in_items: - items[{}]={}".format(key, dict(value)))
            else:
                logger.info("search_for_struct_in_items: - items[{}]={}".format(key, value))

        if key == 'struct':
            # item is a struct
            struct_names = value
            # ensure, struct_names is a list
            if isinstance(struct_names, str):
                struct_names = [struct_names]

            instance = items.get('instance', '')
            template = collections.OrderedDict()

            global struct_merging_active
            struct_merging_active = True
            for struct_name in struct_names:
                wrk = struct_name.find('@')
                if wrk > -1:
                    add_struct_to_item_template(parent, struct_name[:wrk], template, struct_dict, struct_name[wrk+1:])
                else:
                    add_struct_to_item_template(parent, struct_name, template, struct_dict, instance)
            if template != {}:
                config = merge(template, config, source_name, 'Item-Tree')
            struct_merging_active = False

        else:
            #item is no struct
            if isinstance(value, collections.OrderedDict):
                # treat value as node
                if parent == '':
                    path = key
                else:
                    path = parent+'.'+key
                # test if a aub-item is a struct
                search_for_struct_in_items(value, struct_dict, config, source_name, parent=path, level=level+1)
                template = collections.OrderedDict()
                nested_put(template, path, value)
                config = merge(template, config, source_name, 'Item-Tree')

    return


def remove_special_listentries(config, filename=''):
    for k, v in config.items():
        if isinstance(v, dict):
            remove_special_listentries(v, filename)
        else:
            if isinstance(v, list):
                if len(v) > 0 and v[0] in ['merge*','merge_unique*']:
                    #logger.warning("remove_special_listentries: a list={} -> {} - {}".format(k, v, filename))
                    del v[0]

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


def add_struct_to_item_template(path, struct_name, template, struct_dict, instance):
    '''
    Add the referenced struct to the items_template subtree

    :param path: Path of the item which references a struct (template)
    :param struct_name: Name of the to use for the item
    :param template: Template dict to be merged into the item tree
    :param struct_dict: dict with all defined structs (from /etc/structs.yaml and from loaded plugins)
    :param instance: For multi instance plugins: instance for which the items work (is derived from item with struct attribute)

    :return:
    '''
    logger.info("add_struct_to_item_template: path (parent)={}, struct_name={}, template={}".format(path, struct_name, dict(template)))
    struct = struct_dict.get(struct_name, None)
    if struct is None:
        # no struct/template with this name
        nf = collections.OrderedDict()
        nf['name'] = "ERROR: struct '" + struct_name+"' not found!"
        # nf['value'] = nf['name']
        nested_put(template, path, nf)
        logger.error("add_struct_to_item_template: Struct definition for '{}' not found (referenced in item {})".format(struct_name, path))
    else:
        # add struct/template to temporary item(template) tree
        #logger.debug("- add_struct_to_item_template: struct_dict = {}".format(dict(struct_dict)))
        #logger.debug("- add_struct_to_item_template: struct '{}' to item '{}'".format(struct_name, path))
        tmp_struct = copy.deepcopy(struct)
        if 'name' in tmp_struct and isinstance(struct["name"], str):
            from lib.smarthome import SmartHome
            _sh = SmartHome.get_instance()
            if Utils.to_bool(getattr(_sh, '_struct_strip_name', False)):
                del tmp_struct['name']
                logger.debug(f'removed "name" attribute from struct {struct_name}')
        nested_put(template, path, tmp_struct)
        if instance != '' or True:
            # add instance to items added by template struct
            subtree = nested_get(template, path)
            # logger.info("add_struct_to_item_template: Adding 'instance: {}' to template for subtree '{}'".format(instance, path))
            # add instance name to attributes which carry '@instance'
            logger.debug("- add_struct_to_item_template: Add instance={} to subtree={}".format(instance, subtree))
            replace_struct_instance(path, subtree, instance)

    logger.info("- add_struct_to_item_template: - after add - template={}".format(dict(template)))
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
    #logger.info("replace_struct_instance: Setting  instance to {} for subtree {}".format(instance, subtree))
    for key in keys:
        # replace recursively
        if Utils.get_type(subtree[key]) == 'collections.OrderedDict':
            replace_struct_instance(path, subtree[key], instance)
        if key.endswith('@instance'):
            if instance == '':
                newkey = key[:-9]
            else:
                newkey = key[:-9] + '@' + instance
            #logger.debug("replace_struct_instance: - path {}: key '{}' --> newkey '{}'".format(path, key, newkey))
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
    if os.path.basename(filename).startswith('test_'):
        logger.info("parse_yaml: Parsing file {}".format(os.path.basename(filename)))
    if config is None:
        config = collections.OrderedDict()

    items = shyaml.yaml_load(filename, ordered=True)
    if items is not None:
        remove_comments(items, filename)
        remove_digits(items, filename)
        remove_reserved(items, filename)
        remove_keyword(items, filename)
        remove_invalid(items, filename)

        if addfilenames:
            #logger.debug("parse_yaml: Add filename = {} to items".format(os.path.basename(filename)))
            _add_filenames_to_config(items, os.path.basename(filename))

        if parseitems:
            # test if file contains 'struct' attribute and merge all items into config
            #logger.debug("parse_yaml: Checking if file {} contains 'struct' attribute".format(os.path.basename(filename)))

            search_for_struct_in_items(items, struct_dict, config, os.path.basename(filename))

            global special_listentry_found
            if special_listentry_found:
                remove_special_listentries(config, os.path.basename(filename))
            special_listentry_found = False

        if not parseitems:
            # if not parsing items
            config = merge(items, config, os.path.basename(filename), 'Config-Tree')
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
            if (filename != ''):
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
            if line == '':
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
