#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 Dirk Wallmeier                      dirk@wallmeier.info
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#########################################################################


import logging
import socket
import threading
import time

logger = logging.getLogger('')


class owex(Exception):
    pass


class ECMD1wireBase():

    def __init__(self, host='127.0.0.1', port=2701):
        self.host = host
        self.port = int(port)
        self._lock = threading.Lock()
        self.connected = False
        self._connection_attempts = 0
        self._connection_errorlog = 60

    def connect(self):
        self._lock.acquire()
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            self._sock.connect((self.host, self.port))
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                logger.error('ecmd1wire: could not connect to {0}:{1}: {2}'.format(self.host, self.port, e))
                self._connection_attempts = self._connection_errorlog
            return
        else:
            self.connected = True
            logger.info('ecmd1wire: connected to {0}:{1}'.format(self.host, self.port))
            self._connection_attempts = 0
        finally:
            self._lock.release()

    def request(self):
        #  name: request
        #  get a table of all DS1820 sensors and their names and values,
        #  separated by '\t' and terminated by 'OK\n':
        #     10f01929020800dc  sensor1 26.4
        #     100834290208001b  sensor2 25.4
        #     OK
        #  @return dict {'addr' : value}
        #
        if not self.connected:
            raise owex("ecmd1wire: No connection to ethersex server {0}:{1}.".format(self.host, self.port))
        self._lock.acquire()
        try:
            self._sock.send("1w list\n")
        except Exception as e:
            self._lock.release()
            raise owex("error sending request: {0}".format(e))
        table = {}
        while 1:
            try:
                response = self._sock.recv(1024)
            except socket.timeout:
                self.close()
                break
            if not response:
                self.close()
                break
            if response != "OK":
                for r in response.split("\n"):
                    if r and len(r.split("\t")) == 3:
                        addr, name, value = r.split("\t")
                        table[addr] = float(value)
                        logger.debug('ecmd1wire: append Sensor {0} = {1}\n'.format(addr, table[addr]))
        self._lock.release()
        return table

    def close(self):
        self.connected = False
        try:
            self._sock.close()
        except:
            pass


class ECMD(ECMD1wireBase):
    _sensors = {}
    alive = True

    def __init__(self, smarthome, cycle=120, host='192.168.178.10', port=2701):
        ECMD1wireBase.__init__(self, host, port)
        self._sh = smarthome
        self._cycle = int(cycle)
        smarthome.connections.monitor(self)

    def _refresh(self):
        start = time.time()
        table = self.request()
        for addr in self._sensors:
            if not self.alive:
                break
            if addr not in table:
                logger.debug("ecmd1wire: {0} not in sensors watched".format(addr))
            else:
                try:
                    value = table[addr]
                except Exception:
                    logger.info("ecmd1wire: problem reading {0}".format(addr))
                    continue
                else:
                    logger.info("ecmd1wire: sensor {0} has {1}°".format(addr, value))
                if value == '85':
                    logger.info("ecmd1wire: problem reading {0}. Wiring problem?".format(addr))
                    continue
                item = self._sensors[addr]
                item(value, 'ECMD1Wire')
        cycletime = time.time() - start
        logger.debug("cycle takes {0} seconds".format(cycletime))

    def run(self):
        self.alive = True
        self._sh.scheduler.add('ecmd1wire', self._refresh, cycle=self._cycle, prio=5, offset=0)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'ecmd1wire_addr' not in item.conf:
            return
        addr = item.conf['ecmd1wire_addr']
        self._sensors[addr] = item
        logger.info("ecmd1wire: Sensor {0} added.".format(addr))
