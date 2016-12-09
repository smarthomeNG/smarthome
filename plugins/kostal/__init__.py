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
import time
import re

logger = logging.getLogger('')


class Kostal():
    _key2td = {
        'power_current': 9,
        'power_total': 12,
        'power_day': 21,
        'status': 27,
        'string1_volt': 45,
        'string2_volt': 69,
        'string3_volt': 93,
        'string1_ampere': 54,
        'string2_ampere': 78,
        'string3_ampere': 102,
        'l1_volt': 48,
        'l2_volt': 72,
        'l3_volt': 96,
        'l1_watt': 57,
        'l2_watt': 81,
        'l3_watt': 105
    }

    def __init__(self, smarthome, ip, user="pvserver", passwd="pvwr", cycle=300):
        self._sh = smarthome
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.cycle = int(cycle)
        self._items = []
        self._values = {}

    def run(self):
        self.alive = True
        self._sh.scheduler.add('Kostal', self._refresh, cycle=self.cycle)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'kostal' in item.conf:
            kostal_key = item.conf['kostal']
            if kostal_key in self._key2td:
                self._items.append([item, kostal_key])
                return self.update_item
            else:
                logger.warn('invalid key {0} configured', kostal_key)
        return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Kostal':
            pass

    def _refresh(self):
        start = time.time()
        try:
            data = self._sh.tools.fetch_url(
                'http://' + self.ip + '/', self.user, self.passwd, timeout=2).decode()
            # remove all attributes for easy findall()
            data = re.sub(r'<([a-zA-Z0-9]+)(\s+[^>]*)>', r'<\1>', data)
            # search all TD elements
            table = re.findall(r'<td>([^<>]*)</td>', data, re.M | re.I | re.S)
            for kostal_key in self._key2td:
                value = table[self._key2td[kostal_key]].strip()
                if 'x x x' not in value:
                    logger.debug('set {0} = {1}'.format(kostal_key, value))
                    self._values[kostal_key] = value
            for item_cfg in self._items:
                if item_cfg[1] in self._values:
                    item_cfg[0](self._values[item_cfg[1]], 'Kostal')
        except Exception as e:
            logger.error(
                'could not retrieve data from {0}: {1}'.format(self.ip, e))
            return

        cycletime = time.time() - start
        logger.debug("cycle takes {0} seconds".format(cycletime))
