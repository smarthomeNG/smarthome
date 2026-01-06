#!/usr/bin/env python
#
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHomeNG.   https://github.com/smarthomeNG/
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
##########################################################################

import os
import sys
import re
from collections import namedtuple
import xml.etree.ElementTree as ET

NS_URL = '{http://knx.org/xml/project/11}'  # ETS4
FIND_GA = NS_URL + 'GroupAddress'

def write_dpt(dpt, depth, f):
	if dpt == 1:
		write_param("type=bool", depth, f)
		write_param("visu=toggle", depth, f)
	elif dpt == 2 or dpt == 3 or dpt == 10 or dpt == 11:
		write_param("type=foo", depth, f)
	elif dpt == 4 or dpt == 24:
		write_param("type=str", depth, f)
		write_param("visu=div", depth, f)
	else:
		write_param("type=num", depth, f)
		write_param("visu=slider", depth, f)
		write_param("knx_dpt=5001", depth, f)
		return

	write_param("knx_dpt=" + str(dpt), depth, f)

def write_dict(a, depth, f):
    if 'sh_attributes' in a.keys():
        if a['sh_attributes']['knx_dpt']:
           write_dpt(int(a['sh_attributes']['knx_dpt'][0]), depth, f)   
           del(a['sh_attributes']['type'])
           del(a['sh_attributes']['visu'])
           del(a['sh_attributes']['knx_dpt'])
        write_attributes(a['sh_attributes'], depth, f)

    for k in a.keys():
        if k == 'sh_attributes':
            continue

        write_item(k, depth, f)
        write_dict(a[k], depth+1, f)

def write_attributes(attr, depth, f):
    attr_str = ""
    for k in attr.keys():
        val = ""
        attr[k] = list(set(attr[k]))
        for v in attr[k]:
            if len(val) > 0:
                val += ", "
            val += v
        write_param(u"{0} = {1}".format(k, val), depth, f)    

def write_param(string, depth, f):
	for i in range(depth):
		f.write('    ')

	f.write(string + '\n')

def write_item(string, depth, f):
	for i in range(depth):
		f.write('    ')

	for i in range(depth + 1):
		f.write('[')

	f.write("'" + string.encode('UTF-8').lower() + "'")

	for i in range(depth + 1):
		f.write(']')

	f.write('\n')

def ga2str(ga):
	return "%d/%d/%d" % ((ga >> 11) & 0xf, (ga >> 8) & 0x7, ga & 0xff)

def pa2str(pa):
	return "%d.%d.%d" % (pa >> 12, (pa >> 8) & 0xf, pa & 0xff)

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

##############################################################
# Main
##############################################################

if __name__ == '__main__':
    PROJECTFILE = sys.argv[1]

    print("Project: " + PROJECTFILE)
    project = ET.parse(PROJECTFILE)
    root = project.getroot()
    a = AutoVivification()

    for ga in root.findall('.//' + FIND_GA):
        if 'Description' in ga.attrib.keys() and 'Name' in ga.attrib.keys():
            desc = ga.attrib['Description']
            name = ga.attrib['Name']

            match = re.match(r".*\s*sh\((?P<sh_str>[^)]*)\).*", desc)
            if match:
                parts = name.split(' ')
                item = a
                for part in parts:
                    item = item[part]
                
                parts = match.group('sh_str').split('|',1)
                ga_str = ga2str(int(ga.attrib['Address']))
                ga_attributes = parts[0].split(',')

                for ga_attribute in ga_attributes:
                    if not ga_attribute in item['sh_attributes'].keys():
                        item['sh_attributes'][ga_attribute] = []
                    item['sh_attributes'][ga_attribute].append(ga_str)
                
                if len(parts) > 1:
                    for part in parts[1].split('|'):
                        p = part.split('=')
                        if len(p) == 2:
                            if not p[0] in item['sh_attributes'].keys():
                                item['sh_attributes'][p[0]] = []
                            item['sh_attributes'][p[0]].append(p[1].strip())
    

    for k in a.keys():
        OUTFILE = u"{0}.conf".format(k)
        print("Create File: {0}".format(OUTFILE))
        
        if (os.path.exists(OUTFILE)):
            os.remove(OUTFILE)

        with open(OUTFILE, 'w') as f:
            write_item(k, 0, f)
            write_dict(a[k], 1, f)
