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
import re

logger = logging.getLogger('netio230b')


class NetIO230B():

    def __init__(self, smarthome, address, user, password, netio_id=1):
        self._sh = smarthome
        self._cycle = 10
        self._ports = dict()
        self._error = []
        self._timeout = 2
        self._address = address
        self._user = user
        self._password = password
        self._netio_id = int(netio_id)

    def run(self):
        self._sh.scheduler.add(
            'NetIO230B' + str(self._netio_id),
            self.update_status,
            cycle=self._cycle)
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):

        if 'netio_id' in item.conf:
            netio_id = int(item.conf['netio_id'])
        else:
            netio_id = 1

        if netio_id != self._netio_id:
            return None

        if 'netio_port' in item.conf:
            self._ports[item.conf['netio_port']] = item
            return self.update_item
        else:
            if 'netio_id' in item.conf:
                self._error.append(item)
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'netio230b':
            if 'netio_port' in item.conf:
                self.set_port(item.conf['netio_port'], item())

    def update_status(self):
        url = 'http://' + self._address + '/tgi/control.cgi?login=p:' \
            + self._user + ':' + self._password + '&p=l'

        # read html response of format '<html>1 0 1 0 </html>'
        html = self._sh.tools.fetch_url(url, timeout=2)

        if (html):
            r = re.compile('[^0^1]')
            cur_state = [_f for _f in r.split(html.decode("utf-8")) if _f]

            # reset error state to False
            for key in self._error:
                key(False)

            # assign values to items
            for key in list(self._ports.keys()):
                try:
                    if cur_state[int(key)] == '0':
                        self._ports[key](False, caller='netio230b')
                    else:
                        if cur_state[int(key)] == '1':
                            self._ports[key](True, caller='netio230b')
                except IndexError as e:
                    logger.error("no state for port: %s", str(e))

        else:
            # set error state to True
            for key in self._error:
                key(True)

    def set_port(self, port, state):
        req = list('uuuu')

        if int(port) in range(0, 4):
            req[int(port)] = '%d' % state

        url = 'http://' + self._address + '/tgi/control.cgi?login=p:' \
            + self._user + ':' + self._password + '&p=' + ''.join(req)
        self._sh.tools.fetch_url(url, timeout=2)
