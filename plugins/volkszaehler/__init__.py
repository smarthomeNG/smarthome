#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012-2013 KNX-User-Forum e.V.       http://knx-user-forum.de/
#
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import urllib.parse
import http.client

from datetime import datetime, timedelta

logger = logging.getLogger('Volkszaehler')

class Volkszaehler():
    _host = ''

    def __init__(self, smarthome, host):
        logger.info('Init Volkszaehler Plugin')
        self._sh = smarthome
        self._host = host

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    # if the item has 'vz_uuid' then register the update_item function
    def parse_item(self, item):
        if 'vz_uuid' in item.conf:
            return self.update_item
        else:
            return None

    # this function is executed every time the item changes
    def update_item(self, item, caller=None, source=None, dest=None):
        vz_uuid = item.conf['vz_uuid']
        value = item()

        # check if the value is float (i.e. temperature, humidity...)
        # if not, then it is 1 (i.e. S0 counter for power or other energy meters)
        if isinstance(value, float):
            vz_value = value
        else:
            vz_value = '1'

        url = '/middleware.php/data' + '/' + vz_uuid + '.json'

        logger.info('Volkszaehler Plugin sent to ' + self._host + ' (UUID: ' + vz_uuid + ')')

        data = {}
        headers = {'User-Agent': "SmartHome.py", 'Content-Type': "application/x-www-form-urlencoded"}
        data['operation'] = 'add' 
        data['value'] = vz_value 

        try:
            conn = http.client.HTTPConnection(self._host, timeout=4)
            conn.request("POST", url, urllib.parse.urlencode(data), headers)
            resp = conn.getresponse()
            conn.close()
            if resp.status != 200:
                raise Exception("{} {}".format(resp.status, resp.reason))
        except Exception as e:
            logger.warning("Could not send to " + self._host + ": {0}. Error: {1}".format(event, e))
