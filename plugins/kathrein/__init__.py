#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
#########################################################################
# Copyright 2014 Johannes Mayr                         joh.mayr@gmail.com
#########################################################################
# Kathrein UFSControl-Plugin for SmartHomeNG.   
#                                        https://github.com/smarthomeNG//
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import time
import urllib.request

logger = logging.getLogger('')

class Kathrein():

    def __init__(self, smarthome, host, port=9000, kathreinid=1):
        self._sh = smarthome
        self._host = host
        self._port = port
        self._kathreinid = int(kathreinid)

    def push(self, key):
        urllib.request.urlopen("http://" + self._host + ":" + str(self._port) + "/HandleKey/" + key).read()
        logger.debug("Send {0} to Kathrein with IP {1} at Port {2}".format(key, self._host, self._port))
        time.sleep(0.1)

    def parse_item(self, item):
        if 'kathreinid' in item.conf:
            kathreinid = int(item.conf['kathreinid'])
        else:
            kathreinid = 1

        if kathreinid != self._kathreinid:
            return None

        if 'kathrein' in item.conf:
            logger.debug("Kathrein Item {0} with value {1} for Kathrein ID {2} found!".format(
                item, item.conf['kathrein'], kathreinid))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        val = item()
        if isinstance(val, str):
            self.push(val)
            return
        if val:
            keys = item.conf['kathrein']
            if isinstance(keys, str):
                keys = [keys]
            for key in keys:
                self.push(key)

    def parse_logic(self, logic):
        pass

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

