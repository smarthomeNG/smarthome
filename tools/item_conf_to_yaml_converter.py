#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# -Parts Copyright 2013 Marcus Popp                        marcus@popp.mx
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

import sys
sys.path.insert(0, '../lib')
import shyaml

import logging
import collections
import os


# ==================================================================================
#   config loader from config.py modified for parsing to yaml
#

logger = logging.getLogger(__name__)


def strip_quotes(string):
    string = string.strip()
    if string[0] in ['"', "'"]:  # check if string starts with ' or "
        if string[0] == string[-1]:  # and end with it
            if string.count(string[0]) == 2:  # if they are the only one
                string = string[1:-1]  # remove them
    return string


def parse_for_convert(filename, config=None):
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_@*'
    valid_set = set(valid_chars)
    if config is None:
        config = collections.OrderedDict()
    item = config
    lastline_was_comment = False
    last_comment_nr = 0
    logging.info("parsing '{}' to '{}'".format(filename, type(config).__name__))
    with open(filename, 'r', encoding='UTF-8') as f:
        linenu = 0
        parent = collections.OrderedDict()
        lines = iter(f.readlines())
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
                    comment = line.partition('#')[2].strip()
                    line = line.partition('#')[0].strip()
                    # inline comment
                    if (line != '') and (comment != ''):
                        attr, __, value = line.partition('=')
                        comment = attr.strip() + ': ' + comment
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
                                item['comment'+str(last_comment_nr)] = item['comment'+str(last_comment_nr)] + '\n' + strip_quotes(comment)
                            else:
                                item['comment'] = item['comment'] + '\n' + strip_quotes(comment)
                        else:
                            i = 1
                            while 'comment'+str(i) in item.keys():
                                i += 1
                            item['comment'+str(i)] = strip_quotes(comment)
                            last_comment_nr = i
                    else:
#                        logger.info("comment: '{}'".format(comment))
                        item['comment'] = strip_quotes(comment)
                        last_comment_nr = 0
                    lastline_was_comment = True
                
            if line is '':
                continue
            if line[0] == '[':  # item
                lastline_was_comment = False
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
                            logger.error("Problem (1) parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, line, valid_chars))
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
                lastline_was_comment = False
                attr, __, value = line.partition('=')
                if not value:
                    continue
                attr = attr.strip()
                if not set(attr).issubset(valid_set):
                    logger.info("line: '{}'".format(line))
                    logger.error("Problem (2) parsing '{}' invalid character in line {}: {}. Valid characters are: {}".format(filename, linenu, attr, valid_chars))
                    continue
                if '|' in value:
                    item[attr] = [strip_quotes(x) for x in value.split('|')]
                else:
                    svalue = strip_quotes(value)
                    try:
                        ivalue = int(svalue)
                        item[attr] = ivalue
                    except:
                        item[attr] = svalue.replace('\t', ' ')

        return config


# ==================================================================================
#   Main Converter Routine
#

if __name__ == '__main__':
    _logdate = "%Y-%m-%d %H:%M:%S"
#    _logformat = "%(levelname)-8s %(message)s"
    _logformat = "%(message)s"
    logging.basicConfig(level='INFO', format=_logformat, datefmt=_logdate)

    directory = '../items'

    for item_file in sorted(os.listdir(directory)):
        if item_file.endswith('.conf'):
            # Remove path and extension
            item_file = os.path.basename(item_file)
            item_file = os.path.splitext(item_file)[0]
            configurationfile = directory+'/'+item_file

            try:
                logger.info('')
                ydata = parse_for_convert(configurationfile+'.conf')
                if ydata != None:
                    shyaml.yaml_save(configurationfile+'.yaml', ydata)
            except Exception as e:
                logger.error("Problem reading {0}: {1}".format(directory+'/'+conffile, e))

    logger.info('')
