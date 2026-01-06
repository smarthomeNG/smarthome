#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2017   Martin Sinn                         m.sinn@gmx.de
# -Parts (from the parser) Copyright 2013 Marcus Pop       marcus@popp.mx
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

"""
This file is a special version of the configuration loader. It has been modified to
support the conversion from CONF to YAML format. This configuration loader is only called
by the converter tools/conf_to_yaml_converter.py.
"""

import os

RUAMEL_YAML_INSTALLED = False
try:
    import ruamel.yaml as yaml
    RUAMEL_YAML_INSTALLED = True
except:
    print('ERROR: module ruamel.yaml not found')
    print('')
    print('Please install ruamel.yaml using the command:')
    print('sudo pip3 install ruamel.yaml')
    print('')
    RUAMEL_YAML_INSTALLED = False
    import yaml


import collections
from collections import OrderedDict


yaml_version = '1.1'
indent_spaces = 4
store_raw_output = False			# Only for testing, otherwise False


def is_ruamelyaml_installed():

    return RUAMEL_YAML_INSTALLED


# ==================================================================================
#   config loader from config.py modified for parsing to yaml
#


def _strip_quotes(string):
    string = string.strip()
    # check if string starts with ' or ", and end with it, if they are the only one
    if len(string) >= 2 and string[0] in ['"', "'"] and string[0] == string[-1] and string.count(string[0]) == 2:
        string = string[1:-1]  # remove them
    return string


def _handle_multiline_string(string):
    if len(string) > 0 and string.find('\n') > -1 and string[0] != '|':
        string = '|\n' + string
    return string


def parse_for_convert(filename=None, conf_code=None, config=None):
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@*'
    valid_set = set(valid_chars)
    if config is None:
        config = collections.OrderedDict()
    item = config
    offset = 0
    lastline_was_comment = False
    last_comment_nr = 0

    if filename != None:
        print("- parsing '{}'".format(os.path.basename(filename)), end="")
        with open(filename, 'r', encoding='UTF-8') as f:
            lines = iter(f.readlines())
    elif isinstance(conf_code, str):
        lines = conf_code.splitlines()
    else:
        return config

    linenu = 0
    parents = collections.OrderedDict()
    parent = collections.OrderedDict()
    if 1 == 1:
        for raw in lines:
            linenu += 1
            line = raw.lstrip('\ufeff')  # remove BOM

            multiline = []
            if line.rstrip().endswith('\\'):
                i = 0
                while line.rstrip().endswith('\\'):
                    multiline.append( line.rstrip().rstrip('\\').strip() )
                    i += 1
                    linenu += 1
                    line = next(lines, '').lstrip()
                line = '\n'.join(multiline) + '\n'+line.strip()
                lastline_was_comment = False

            if (len(multiline) == 0) or (line[0] == '#'):
                if len(multiline) == 0:
                    comment_in_line = line.find('#')
                    comment = line.partition('#')[2].strip()
                    if comment_in_line > -1 and comment == '':
                        comment = '>**<'
                    line = line.partition('#')[0].strip()
                    # inline comment
                    if (line != '') and (comment != '') and line.find('[') == -1:
                        attr, __, value = line.partition('=')
                        if ("'" in line) or ("|" in line):
                            comment = attr.strip() + ': ' + comment
                        else:
                            line = line + '    ## ' + comment
                            comment = ''
                else:
                    comment = line
                    line = ''
                if comment != '':
                    while (comment != '') and (comment[0] == '#'):
                        comment = comment[1:].strip()
                if comment != '':
                    comment = comment.replace('\t', ' ')
                    if 'comment' in item.keys():
                        if lastline_was_comment:
                            if last_comment_nr > 0:
                                item['comment'+str(last_comment_nr)] = _handle_multiline_string(item['comment'+str(last_comment_nr)] + '\n' + _strip_quotes(comment))
                            else:
                                item['comment'] = _handle_multiline_string(item['comment'] + '\n' + _strip_quotes(comment))
                        else:
                            i = 1
                            while 'comment'+str(i) in item.keys():
                                i += 1
                            item['comment'+str(i)] = _handle_multiline_string(_strip_quotes(comment))
                            last_comment_nr = i
                    else:
#                        logger.info("comment: '{}'".format(comment))
                        item['comment'] = _handle_multiline_string(_strip_quotes(comment))
                        last_comment_nr = 0
                    lastline_was_comment = True

            if line == '':
                continue
            if line[0] == '[':  # item
                lastline_was_comment = False
                #
                comment_in_line = line.find('#')
                comment = line.partition('#')[2].strip()
                if comment_in_line > -1 and comment == '':
                    comment = '>**<'
                line = line.partition('#')[0].strip()
                #
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
                            print()
                            print("ERROR: Problem (1) parsing '{}' invalid character in \nline {}: {}. \nValid chars: {}".format(os.path.basename(filename), linenu, line, valid_chars))
                            return config
                if brackets != 0:
                    print()
                    print("ERROR: Problem parsing '{}' unbalanced brackets in line {}: {}".format(filename, linenu, line))
                    return config
                #
                if comment_in_line > -1:
                    print()
                    print("ERROR: Problem parsing '{}' \nunhandled comment {} in \nline {}: {}. \nValid chars: {}".format(os.path.basename(filename), comment, linenu, line, valid_chars))
                #
                name = line.strip("[]")
                name = _strip_quotes(name)
                if level - offset == 1:
                    if name not in config:
                        config[name] = collections.OrderedDict()
                    item = config[name]
                    parents = collections.OrderedDict()
                    parents[level] = item
                else:
                    if level - 1 not in parents:
                        offset = level - 1
                        if name not in config:
                            config[name] = collections.OrderedDict()
                        item = config[name]
                        parents = collections.OrderedDict()
                        parents[level] = item
                    else:
                        parent = parents[level - 1]
                        if name not in parent:
                            parent[name] = collections.OrderedDict()
                        item = parent[name]
                        parents[level] = item

            else:  # attribute
                lastline_was_comment = False
                attr, __, value = line.partition('=')
                comm = ''
                if '##' in value:
                    value, __, comm  = value.partition('##')
                    value = _strip_quotes(value)
                    value = value + '    ## ' + comm.strip()
#                print("= attr >{}<, value >{}<, comment >{}<".format(attr, value, comm))
                if not value:
                    continue
                attr = attr.strip()
                if not set(attr).issubset(valid_set):
                    print()
                    print("line: '{}'".format(line))
                    print("ERROR: Problem (2) parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, attr, valid_chars))
                    continue
                if '|' in value:
                    item[attr] = [_strip_quotes(x) for x in value.split('|')]
                else:
                    svalue = _handle_multiline_string(_strip_quotes(value))
                    try:
                        ivalue = int(svalue)
                        item[attr] = ivalue
                    except:
                        item[attr] = svalue.replace('\t', ' ')

        return config


# ##################################################################################
#   YAML handling routines
#

def _yaml_save_roundtrip(filename, data):
    """
    Dump yaml using the RoundtripDumper and correct linespacing in output file
    """

    sdata = yaml.dump(data, Dumper=yaml.RoundTripDumper, version=yaml_version, indent=indent_spaces, block_seq_indent=2, width=32768, allow_unicode=True)

    ldata = sdata.split('\n')
    rdata = []
    for index, line in enumerate(ldata):
        # Fix for ruamel.yaml handling: Reinsert empty line before comment of next section
        if len(line.lstrip()) > 0 and line.lstrip()[0] == '#':
            indentcomment = len(line) - len(line.lstrip(' '))
            indentprevline = len(ldata[index-1]) - len(ldata[index-1].lstrip(' '))
            if indentprevline - indentcomment >= 2*indent_spaces:
                rdata.append('')
            rdata.append(line)
        # Fix for ruamel.yaml handling: Remove empty line with spaces that have been inserted
        elif line.strip() == '' and line != '':
            if ldata[index-1] != '':
                rdata.append(line)
        else:
            rdata.append(line)

    sdata = '\n'.join(rdata)
    if sdata[0] == '\n':
        sdata =sdata[1:]

    with open(filename+'.yaml', 'w', encoding='utf8') as outfile:
        outfile.write( sdata )



def yaml_save(filename, data):
    """
    ***Converter Special ***

    Save contents of an OrderedDict structure to a yaml file

    :param filename: name of the yaml file to save to
    :param data: OrderedDict to save
    """

    sdata = convert_yaml(data)

    print(", saving to '{}'".format(os.path.basename(filename)+'.yaml'))
    if store_raw_output == True:
        with open(filename+'_raw.yaml', 'w', encoding='UTF-8') as outfile:
            outfile.write( sdata )

    # Test if roundtrip gives the same result
    data = yaml.load(sdata, yaml.RoundTripLoader)
    _yaml_save_roundtrip(filename, data)


def convert_yaml(data):
    """
    ***Converter Special ***

    Convert data structure to yaml format

    :param data: OrderedDict to convert
    :return: yaml formated data
    """

    ordered = (type(data).__name__ == 'OrderedDict')
    if ordered:
        sdata = _ordered_dump(data, Dumper=yaml.SafeDumper, version=yaml_version, indent=indent_spaces, block_seq_indent=2, width=32768, allow_unicode=True, default_flow_style=False)
    else:
        sdata = yaml.dump(data, Dumper=yaml.SafeDumper, indent=indent_spaces, block_seq_indent=2, width=32768, allow_unicode=True, default_flow_style=False)
    sdata = _format_yaml_dump(sdata)

    return sdata


def _format_yaml_dump(data):
    """
    ***Converter Special ***

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
        if len(line) > 0:
            # Handle inline-comments from converter
            if line.find('##') > -1 and line.find(": '") > -1 and line[-1:] == "'":
                line = line.replace('##', '#')
                line = line.replace(": '", ": ")
                line = line[:-1]

            # Handle comments from converter
            if line.find('comment') > -1 and line.find(':') > line.find('comment'):
#                print('comment-line>', line, '<')
                indent = len(line) - len(line.lstrip(' '))
                if ldata[index+1][-1:] == ':':
                    indent = len(ldata[index+1]) - len(ldata[index+1].lstrip(' '))
                if line.find(': "|') > -1:
                    line = line[:-1]
                    line = line.replace(': "|', ': |')
                else:
                    line = line.replace(': ', ': |\\n', 1)
#                print('# ' + line[line.find("|\\n")+3:])
                line = " "*indent + '# ' + line[line.find("|\\n")+3:]
                line = line.replace('>**<', '')
                line = line.replace('\\n', '\n'+" "*indent + '# ')

            # Handle newlines for multiline string-attributes ruamel.yaml
            if line.find(': "|') > -1 and line[-1:] == '"' and line.find('\\n') > -1:
                indent = len(line) - len(line.lstrip(' ')) + indent_spaces
                line = line[:-1]
                line = line.replace(': "|', ': |')
                line = line.replace('\\n', '\n'+" "*indent)

        rdata.append(line)


    ldata = rdata
    rdata = []
    for index, line in enumerate(ldata):
        if len(line.lstrip()) > 0 and  line.lstrip()[0] == '#' and ldata[index+1][-1:] == ':':
            rdata.append('')
            rdata.append(line)

        # Insert empty line before section (key w/o a value)
        elif line[-1:] == ':':
            if not (len(ldata[index-1].lstrip()) > 0 and ldata[index-1].lstrip()[0] == '#'):
                # no empty line before list attributes
                if ldata[index+1].strip()[0] != '-':
                    rdata.append('')
                rdata.append(line)
            else:
                rdata.append(line)
        else:
            rdata.append(line)

    fdata = '\n'.join(rdata)
    if fdata[0] == '\n':
        fdata = fdata[1:]
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


