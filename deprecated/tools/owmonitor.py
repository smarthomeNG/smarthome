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

import time
import sys
import logging
sys.path.append("/usr/smarthome")

import plugins.onewire

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('')

host = '127.0.0.1'
port = 4304

ow = plugins.onewire.OwBase(host, port)
ow.connect()

old = []
while 1:
    try:
        new = ow.dir('/uncached')
    except Exception as e:
        logger.error(e)
        sys.exit()
    dif = list(set(new) - set(old))
    for sensor in dif:
        try:
            sensor = sensor.replace('/uncached', '')
            typ = ow.read(sensor + 'type')
            sensors = ow.identify_sensor(sensor)
            print("new sensor {0} ({1}) provides: {2}".format(sensor, typ, sensors))
        except Exception as e:
            pass
    old += dif
    time.sleep(1)
