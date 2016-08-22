#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# Parts Copyright 2013  Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
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
import lib.shyaml as shyaml

logger = logging.getLogger(__name__)



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
    config = parse(basename+'.yaml')
    if config == {}:
        config = parse(basename+'.conf')
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
        if item_file.endswith('.conf') or item_file.endswith('.yaml'):
            try:
                item_conf = parse(itemsdir + item_file, item_conf)
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
    if filename.endswith('.yaml') and os.path.isfile(filename):
         return parse_yaml(filename, config)
    elif filename.endswith('.conf') and os.path.isfile(filename):
        return parse_conf(filename, config)
    return {}


# --------------------------------------------------------------------------------------


def remove_comments(ydata, level=0):
    '''
    Removes comments from a dict or OrderedDict structure

    :param ydata: configuration (sub)tree to work on
    :param level: optional subtree level (used for recursion)
    '''
    level_keys = list(ydata.keys())
    for key in level_keys:
        if type(ydata[key]).__name__ in ['dict','OrderedDict']:
            remove_comments(ydata[key], level+1)
        else:
            if key.startswith('comment'):
                ydata.pop(key)


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
    
    config = merge(items, config)
    return config
    

# --------------------------------------------------------------------------------------


def strip_quotes(string):
    string = string.strip()
    if string[0] in ['"', "'"]:  # check if string starts with ' or "
        if string[0] == string[-1]:  # and end with it
            if string.count(string[0]) == 2:  # if they are the only one
                string = string[1:-1]  # remove them
    return string


def parse_conf(filename, config=None):
    '''
    Load and parse a configuration file which is in the old .conf format of smarthome.py
    and merge it to the configuration tree

    :param filename: Name of the configuration file
    :param config: Optional OrderedDict tree, into which the configuration should be merged
    :return: The resulting merged OrderedDict tree
    '''
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@*'
    valid_set = set(valid_chars)
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
                        if line[index] not in valid_chars + "'":
                            logger.error("Problem parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, line, valid_chars))
                            return config
                if brackets != 0:
                    logger.error("Problem parsing '{}' unbalanced brackets in line {}: {}".format(filename, linenu, line))
                    return config
                name = line.strip("[]")
                name = strip_quotes(name)
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
                    logger.error("Problem parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, attr, valid_chars))
                    continue
                if '|' in value:
                    item[attr] = [strip_quotes(x) for x in value.split('|')]
                else:
                    item[attr] = strip_quotes(value)
        return config

