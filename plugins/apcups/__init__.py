#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import subprocess # we scrape apcaccess output

logger = logging.getLogger('')

class APCUPS():

    def __init__(self, smarthome, host='127.0.0.1', port=3551):
        self._sh = smarthome
        self._host = host
        self._port = port
        self._cycle = 300
        self._items = {}

    def run(self):
        self.alive = True
        self._sh.scheduler.add('Apcups', self.update_status, cycle=self._cycle)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'apcups' in item.conf:
            apcups_key = (item.conf['apcups']).lower()
            self._items[apcups_key]=item
            logger.debug("item {0} added with apcupd_key {1}".format(item,apcups_key))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'plugin':
            logger.info("update item: {0}".format(item.id()))

    def update_status(self):
        # go and grab
        command = '/sbin/apcaccess status {0}:{1}'.format(self._host, self._port)   # the command goes here
        output = subprocess.check_output(command.split(), shell=False)
        # decode byte string to string
        output = output.decode()
        for line in output.split('\n'):
            (key,spl,val) = line.partition(': ')
            key = key.rstrip().lower()
            val = val.strip()
            val = val.split(' ',1)[0] # ignore anything after 1st space
 
            if key in self._items:
                 logger.debug("update item {0} with {1}".format(self._items[key],val))
                 item = self._items[key]
                 logger.debug("Item type {0}".format(item.type()))
                 if item.type() == 'str':
                     item (val, 'apcups')
                 else:
                     item (float(val), 'apcups')
        return

