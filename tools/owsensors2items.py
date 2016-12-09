#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 KNX-User-Forum e.V.       http://knx-user-forum.de/
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


import ConfigParser, io, sys

conf = ''
# read conf and skip header entries (no section)
try:

    with open(sys.argv[1], 'r') as cfg:
        found_section = False
        for l in cfg.readlines():
            if len(l.strip()) == 0: 
                continue
            if l[0] != '[' and found_section == False:
                continue
            found_section = True
            conf += l

    with open(sys.argv[2], 'w') as out:
        config = ConfigParser.ConfigParser()
        config.readfp(io.BytesIO(conf))
        for section in config.sections():
            try:
                name = config.get(section, 'name')
                typ = config.get(section, 'type')
            except ConfigParser.NoOptionError:
                continue
            if typ == 'DS1820':
                sensor = 'T' + config.get(section, 'resolution')
                typ = 'num'
                knx_send = config.get(section, 'eib_ga_temp')
            elif typ == 'DS2438Hum' or typ == 'DS2438Datanab':
                sensor = 'H'
                typ = 'num'
            elif typ == 'DS1990':
                sensor = 'B'
                typ = 'bool'
                knx_send = config.get(section, 'eib_ga_present')
            elif typ == 'DS2401':
                sensor = 'B'
                typ = 'bool'
                knx_send = config.get(section, 'eib_ga_present')
            elif typ == 'DS9490':
                sensor = 'BM'
                typ = 'bool'
            else:
                continue

            out.write('''
[[{0}]]
    name = {0}
    type = {1}
    ow_addr = {2}
    ow_sensor = {3}
    #knx_send = {4}
    #knx_reply = {4}
        '''.format(name, typ, section, sensor,knx_send))

except:
    print "usage: owsensors2item.py <input_file> <output_file>"
    sys.exit()
