#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import time
import socket
import re
import serial
import threading
import struct

logger = logging.getLogger('')


class Sml():
    _serial = None
    _sock = None
    _lock = None
    _target = None
    _connection_attempts = 0
    _dataoffset = 0
    _items = {}
    connected = False

    def __init__(self, smarthome, host=None, port=0, serialport=None, cycle=300):
        self._sh = smarthome
        self.host = host
        self.port = port
        self.serialport = serialport
        self.cycle = cycle
        self._lock = threading.Lock()
        smarthome.connections.monitor(self)

    def run(self):
        self.alive = True
        self._sh.scheduler.add('Sml', self._refresh, cycle=self.cycle)

    def stop(self):
        self.alive = False
        self.disconnect()

    def parse_item(self, item):
        if 'sml_obis' in item.conf:
            obis = item.conf['sml_obis']
            if obis not in self._items:
                self._items[obis] = []
            self._items[obis].append(item)
            return self.update_item
        return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Sml':
            pass

    def connect(self):
        self._lock.acquire()
        target = None
        try:
            if self.serialport is not None:
                self._target = 'serial://{}'.format(self.serialport)
                self._serial = serial.Serial(
                    self.serialport, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=2)
            elif self.host is not None:
                self._target = 'tcp://{}:{}'.format(self.host, self.port)
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(2)
                self._sock.connect((self.host, self.port))
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                self.log_err('Sml: Could not connect to {}: {}'.format(self._target, e))
                self._connection_attempts = self._connection_errorlog
            self._lock.release()
            return
        else:
            logger.info('Sml: Connected to {}'.format(self._target))
            self.connected = True
            self._connection_attempts = 0
            self._lock.release()

    def disconnect(self):
        if self.connected:
            try:
                if self._serial is not None:
                    self._serial.close()
                    self._serial = None
                elif self._sock is not None:
                    self._sock.shutdown(socket.SHUT_RDWR)
                    self._sock = None
            except:
                pass
            logger.info('Sml: Disconnected!')
            self.connected = False
            self._target = None
            self._connection_attempts = 0

    def _read(self, length):
        if self._serial is not None:
            return self._serial.read(length)
        elif self._sock is not None:
            return self._sock.recv(length)
        
    def _refresh(self):
        if self.connected:
            start = time.time()
            try:
                self._dataoffset = 0
                data = self._read(512)
            except Exception as e:
                logger.error(
                    'could not retrieve data from {0}: {1}'.format(self._target, e))
                return

            # Search SML List Entry sequences like:
            # "77 07 81 81 c7 82 03 ff 01 01 01 01 04 xx xx xx xx" - manufactor
            # "77 07 01 00 00 00 09 ff 01 01 01 01 0b xx xx xx xx xx xx xx xx xx xx 01" - server id
            # "77 07 01 00 01 08 00 ff 63 01 80 01 62 1e 52 ff 56 00 00 00 29 85 01"
            # Details see http://wiki.volkszaehler.org/software/sml
            values = {}
            logger.debug('Data: {}'.format(''.join(' {:02x}'.format(x) for x in data)))
            try:
                while self._dataoffset < len(data):

                    # Find SML_ListEntry starting with 0x77 0x07 and OBIS code end with 0xFF
                    if data[self._dataoffset] == 0x77 and data[self._dataoffset+1] == 0x07 and data[self._dataoffset+7] == 0xff:
                        self._dataoffset += 1
                        entry = {
                          'objName'   : self._read_entity(data),
                          'status'    : self._read_entity(data),
                          'valTime'   : self._read_entity(data),
                          'unit'      : self._read_entity(data),
                          'scaler'    : self._read_entity(data),
                          'value'     : self._read_entity(data),
                          'signature' : self._read_entity(data)
                        }

                        obis = '{}-{}:{}.{}.{}*{}'.format(entry['objName'][0], entry['objName'][1], entry['objName'][2], entry['objName'][3], entry['objName'][4], entry['objName'][5])
                        logger.debug('Entry {} = {}'.format(obis, entry))

                        if entry['scaler'] is not None:
                            values[obis] = entry['value'] * 10 ** entry['scaler']
                        else:
                            values[obis] = entry['value']
                    else:
                        self._dataoffset += 1
            except IndexError:
                pass

            for obis in values:
                if obis in self._items:
                    for item in self._items[obis]:
                        item(values[obis])

            cycletime = time.time() - start
            logger.debug("cycle takes {0} seconds".format(cycletime))

    def _read_entity(self, data):
        upack = {
          5 : { 1 : '>b', 2 : '>h', 3: '>i', 4 : '>i', 8 : '>q' },
          6 : { 1 : '>B', 2 : '>H', 3: '>I', 4 : '>I', 8 : '>Q' }
        }

        result = None

        tlf = data[self._dataoffset]
        type = (tlf & 112) >> 4
        more = tlf & 128
        len = tlf & 15
        self._dataoffset += 1

        if more > 0:
            tlf = data[self._dataoffset]
            len = len << 4 + (tlf & 15)
            self._dataoffset += 1

        len -= 1

        if len == 0:     # skip empty optional value
            return result

        if type == 0:    # octet string
            result = data[self._dataoffset:self._dataoffset+len]

        elif type == 5 or type == 6:  # signed int or unsigned int
            d = data[self._dataoffset:self._dataoffset+len]

            if len == 3:  # extend 3-byte value to 4-byte value for unpack()
                d = b'\x00' + d

            result = struct.unpack(upack[type][len], d)[0]

        elif type == 7:  # list
            result = []
            self._dataoffset += 1
            for i in range(0, len + 1):
                result.append(self._read_entity(data))
            return result

        else:
            logger.warning('Skipping unkown field {}'.format(hex(tlf)))

        self._dataoffset += len

        return result

