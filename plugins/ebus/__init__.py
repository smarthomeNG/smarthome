#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012-2013 KNX-User-Forum e.V.       http://knx-user-forum.de/
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import socket
import threading
import time

logger = logging.getLogger('eBus')


class eBus():
    _items = []

    def __init__(self, smarthome, host, port, cycle=240):
        self._sh = smarthome
        self._cycle = int(cycle)
        self._sock = False
        self.connected = False
        self.host = host
        self.port = int(port)
        self._connection_attempts = 0
        self._connection_errorlog = 60
        smarthome.connections.monitor(self)
        self._lock = threading.Lock()
        self.refresh_cycle = self._cycle

    def parse_item(self, item):
        # Attribute und Parameter werden regelmäßig ausgelesen
        if 'ebus_type' in item.conf and 'ebus_cmd' in item.conf:
            self._items.append(item)
            return self.update_item

    def run(self):
        self.alive = True
        self._sh.scheduler.add('eBusd', self.refresh, prio=5, cycle=self._cycle, offset=2)

    def refresh(self):
        for item in self._items:
            time.sleep(1)
            ebus_type = item.conf['ebus_type']
            ebus_cmd = item.conf['ebus_cmd']
            if ebus_cmd == "cycle":
                request = ebus_type + " " + ebus_cmd  # build command
            else:
                request = "get" + " " + ebus_cmd  # build command
            value = self.request(request)
            #if reading fails (i.e. at broadcast-commands) the value will not be updated
            if 'command not found' not in str(value) and value is not None:
                item(value, 'eBus', 'refresh')
            if not self.alive:
                break

    def request(self, request):
        if not self.connected:
            logger.info("eBusd not connected")
            return
        self._lock.acquire()
        try:
            self._sock.send(request.encode())
            logger.debug("REQUEST: {0}".format(request))
        except Exception as e:
            self._lock.release()
            self.close()
            logger.warning("error sending request: {0} => {1}".format(request, e))
            return
        try:
            answer = self._sock.recv(256).decode()[:-2]
            logger.debug("ANSWER: {0}".format(answer))
        except socket.timeout:
            self._lock.release()
            logger.warning("error receiving answer: timeout")
            return
        except Exception as e:
            self._lock.release()
            self.close()
            logger.warning("error receiving answer: {0}".format(e))
            return
        self._lock.release()
        return answer

    def connect(self):
        self._lock.acquire()
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            self._sock.connect((self.host, self.port))
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                logger.error('eBus:	could not connect to {0}:{1}: {2}'.format(self.host, self.port, e))
                self._connection_attempts = self._connection_errorlog
            self._lock.release()
            return
        logger.info('Connected to {0}:{1}'.format(self.host, self.port))
        self.connected = True
        self._connection_attempts = 0
        self._lock.release()

    def close(self):
        self.connected = False
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self._sock.close()
            self._sock = False
            logger.info('Connection closed to {0}:{1}'.format(self.host, self.port))
        except:
            pass

    def stop(self):
        self.close()
        self.alive = False

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'eBus':
            value = str(int(item()))
            cmd = item.conf['ebus_cmd']
            request = "set " + cmd + " " + value
            set_answer = self.request(request)
            #just check if set was no broadcast-message
            if 'broadcast done' not in set_answer:
                request = "get " + cmd
                answer = self.request(request)
                #transfer value and answer to float for better comparsion
                if float(answer) != float(value) or answer is None:
                    logger.warning("Failed to set parameter: value: {0} cmd: {1} answer {2}".format(value, request, answer))
