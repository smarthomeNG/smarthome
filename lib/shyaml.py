#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
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
import yaml
from collections import OrderedDict


logger = logging.getLogger(__name__)

# ==================================================================================
#   Routines to handle yaml files
#

def yaml_load(filename, ordered=False):
    """
    Load contents of a yaml file into an dict/OrderedDict structure

    :param filename: name of the yaml file to load
    :return: Dict/OrderedDict structure or None, if an error occured
    """

    dict_type = 'dict'
    if ordered:
        dict_type = 'OrderedDict'
    logger.info("Loading '{}' to '{}'".format(filename, dict_type))
    y = None

    try:
        with open(filename, 'r') as stream:
            sdata = stream.read()
        sdata = sdata.replace('\n', '\n\n')
        if ordered:
            y = _ordered_load(sdata, yaml.SafeLoader)
        else:
            y = yaml.load(sdata, yaml.SafeLoader)
    except Exception as e:
        logger.error("YAML-file load error:  \n'%s'" % (e))

    return y


def yaml_save(filename, data):
    """
    Save contents of an OrderedDict structure to a yaml file

    :param filename: name of the yaml file to save to
    :param data: OrderedDict to save
    """

    ordered = (type(data).__name__ == 'OrderedDict')
    dict_type = 'dict'
    if ordered:
        dict_type = 'OrderedDict'
    logger.info("Saving '{}' to '{}'".format(dict_type, filename))
    if ordered:
        sdata = _ordered_dump(data, Dumper=yaml.SafeDumper, indent=4, width=768, allow_unicode=True, default_flow_style=False)
    else:
        sdata = yaml.dump(data, Dumper=yaml.SafeDumper, indent=4, width=768, allow_unicode=True, default_flow_style=False)
    sdata = _format_yaml_dump( sdata )
    with open(filename, 'w') as outfile:
        outfile.write( sdata )

# ==================================================================================

def _format_yaml_load(data):
    """
    Reinsert '\n's that have been removed fom comments to make file more readable

    :param data: string to format
    
    :return: formatted string
    """

#    ptr = 0
#    cptr = data[ptr:].find('comment: ')
    
    data = data.replace('\n', '\n\n')
    return data
    

def _ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Ordered yaml loader
    Use this instead ot yaml.loader/yaml.saveloader to get an Ordereddict

    :param stream: stream to read from
    :param Loader: yaml-loader to use
    :object_pairs_hook: ...
    
    :return: OrderedDict structure
    """

    # usage example: ordered_load(stream, yaml.SafeLoader)
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def _format_yaml_dump(data):
    """
    Format yaml-dump to make file more readable
    (yaml structure must be dumped to a stream before using this function)
    | Currently does the following:
    | - Add an empty line before a new item

    :param data: string to format
    
    :return: formatted string
    """

    data = data.replace('\n\n', '\n')
    ldata = data.split('\n')
    rdata = []
    for index, line in enumerate(ldata):
        if line[-1:] == ':':
            # no empty line before list attributes
            if ldata[index+1].strip()[0] != '-':
                rdata.append('')
            rdata.append(line)
        else:
            rdata.append(line)
    fdata = '\n'.join(rdata)
    return fdata
        

def _ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    """
    Ordered yaml dumper
    Use this instead ot yaml.Dumper/yaml.SaveDumper to get an Ordereddict

    :param stream: stream to write to
    :param Dumper: yaml-dumper to use
    :**kwds: Additional keywords
    
    :return: OrderedDict structure
    """

    # usage example: ordered_dump(data, Dumper=yaml.SafeDumper)
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

