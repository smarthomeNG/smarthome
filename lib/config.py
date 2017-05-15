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

import logging
import collections
import keyword
import os
import lib.shyaml as shyaml
from lib.constants import (YAML_FILE, CONF_FILE)
logger = logging.getLogger(__name__)

valid_item_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
valid_attr_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@*'
digits = '0123456789'
reserved = ['set', 'get']

def parse_basename(basename, configtype=''):
    '''
    Load and parse a single configuration and merge it to the configuration tree
    The configuration is only specified by the basename.
    At the moment it looks for a .yaml file or a .conf file
    .yaml files take preference
    
    :param basename: Name of the configuration
    :param configtype: Optional string with config type (only used for log output)
    :return: The resulting merged OrderedDict tree
    '''
    config = parse(basename+YAML_FILE)
    if config == {}:
        config = parse(basename+CONF_FILE)
    if config == {}:
        logger.critical("No file '{}.*' found with {} configuration".format(basename, configtype))
    return config
        

def parse_itemsdir(itemsdir, item_conf):
    '''
    Load and parse item configurations and merge it to the configuration tree
    The configuration is only specified by the name of the directory.
    At the moment it looks for .yaml files and a .conf files
    Both filetypes are read, even if they have the same basename
    
    :param itemsdir: Name of folder containing the configuration files
    :param item_conf: Optional OrderedDict tree, into which the configuration should be merged
    :return: The resulting merged OrderedDict tree
    '''
    for item_file in sorted(os.listdir(itemsdir)):
        if item_file.endswith(CONF_FILE) or item_file.endswith(YAML_FILE):
            try:
                item_conf = parse(itemsdir + item_file, item_conf)
            except UnicodeDecodeError as e:
                logger.error("item file ({}) is not in UTF-8 format, please check character encoding at position {}! => ignoring config".format(item_file, e.start))
                continue
            except Exception as e:
                logger.exception("Problem reading {0}: {1}".format(item_file, e))
                continue
    return item_conf


def parse(filename, config=None):
    '''
    Load and parse a configuration file and merge it to the configuration tree
    Depending on the extension of the filename, the apropriate parser is called
    
    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :return: The resulting merged OrderedDict tree
    '''
    if filename.endswith(YAML_FILE) and os.path.isfile(filename):
         return parse_yaml(filename, config)
    elif filename.endswith(CONF_FILE) and os.path.isfile(filename):
        return parse_conf(filename, config)
    return {}


# --------------------------------------------------------------------------------------

def remove_keys(ydata, func, level=0):
    '''
    Removes given keys from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :param func: the function to call to check for removal
    :param level: optional subtree level (used for recursion)
    '''
    try:
        level_keys = list(ydata.keys())
        for key in level_keys:
            if type(ydata[key]).__name__ in ['dict','OrderedDict']:
                remove_keys(ydata[key], func, level+1)
            else:
                if func(str(key)):
                    ydata.pop(key)
    except:
        logger.error("Problem removing key from '{}', probably invalid YAML file".format(str(ydata)))



def remove_comments(ydata):
    '''
    Removes comments from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    '''
    remove_keys(ydata, lambda k: k.startswith('comment'))


def remove_digits(ydata):
    '''
    Removes digit keys from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    '''
    remove_keys(ydata, lambda k: k[0] in digits)


def remove_reserved(ydata):
    '''
    Removes reserved keywords from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    '''
    remove_keys(ydata, lambda k: k in reserved)


def remove_keyword(ydata):
    '''
    Removes reserved Python keywords from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    '''
    remove_keys(ydata, lambda k: keyword.iskeyword(k))


def remove_invalid(ydata):
    '''
    Removes invalid chars in item from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    '''
    valid_chars = valid_item_chars + valid_attr_chars
    remove_keys(ydata, lambda k: True if True in [True for i in range(len(k)) if k[i] not in valid_chars] else False)


def merge(source, destination):
    '''
    Merges an OrderedDict Tree into another one
    
    Run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    
    
    :param source: OrderedDict tree to be merged into another one
    :param destination: OrderedDict tree, into which the other OrderedDict tree is merged
    :return: The resulting merged OrderedDict tree
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
    
    
def parse_yaml(filename, config=None):
    '''
    Load and parse a yaml configuration file and merge it to the configuration tree

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :return: The resulting merged OrderedDict tree
    '''
    if config is None:
        config = collections.OrderedDict()

    items = shyaml.yaml_load(filename, ordered=True)
    remove_comments(items)
    remove_digits(items)
    remove_reserved(items)
    remove_keyword(items)
    remove_invalid(items)
    
    config = merge(items, config)
    return config
    

# --------------------------------------------------------------------------------------


def strip_quotes(string):
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
    
    The config file should stick to the following setup:
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
            attribute1 = andsoon
            
    where firstlevel, secondlevel, thirdlevel and anothersecondlevel are defined as items and attribute are their respective attribute - value pairs
    
    Valid characters for the items are a-z and A-Z plus any digit and underscore as second or further characters.
    Valid characters for the attributes are the same as for an item plus @ and *

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :return: The resulting merged OrderedDict tree
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
                if '|' in value:
                    item[attr] = [strip_quotes(x) for x in value.split('|')]
                else:
                    item[attr] = strip_quotes(value)
        return config

