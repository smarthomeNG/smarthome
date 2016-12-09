#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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
#

import logging
import serial
import re
import time

logger = logging.getLogger('easymeter')


class easymeter():

    def __init__(self, smarthome):
        self._sh = smarthome
        self._cycle = 10
        self._timeout = 2
        self._codes = dict()

    def run(self):
        self._sh.scheduler.add(
            'easymeter', self.update_status, cycle=self._cycle)
        self.alive = True

    def stop(self):
        self.alive = False

    # parse items, if item has parameter netio_port
    # add item to local list
    def parse_item(self, item):
        if 'easymeter_code' in item.conf:

            if item.conf['device'] not in self._codes:
                self._codes[item.conf['device']] = dict()

            self._codes[item.conf['device']][
                item.conf['easymeter_code']] = item

        return None

    def update_status(self):

        for curr_port in self._codes.keys():
            ser = serial.Serial(
                port=curr_port,
                timeout=2,
                baudrate=9600,
                bytesize=serial.SEVENBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE)

            start = time.time()
            ser.flushInput()

            # wait for start of next datablock
            while True:
                line = ser.readline().decode("utf-8")
                if line.find('!') >= 0:
                    break

            # read next datablock
            datablock = []

            while True:
                line = ser.readline().decode("utf-8")
                datablock.append(line)
                if line.find('!') >= 0:
                    break

            # close serial connection
            ser.close()

            for code in self._codes[curr_port].keys():
                r = re.compile('[()]+')
                for line in datablock:
                    line = line.split(code)
                    if len(line) > 1:
                        self._codes[curr_port][code](
                            r.split(line[1])[1].split('*')[0])

            cycletime = time.time() - start
            logger.debug("cycle takes %d seconds", cycletime)
