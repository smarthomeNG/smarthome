#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2014 Oliver Hinckel                  github@ollisnet.de
#########################################################################
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
#########################################################################

import logging
import time
import re
import serial
import threading
import struct
import socket
import errno

from lib.model.smartplugin import SmartPlugin

class Sml(SmartPlugin):

    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION = '1.0.0'

    _units = {  # Blue book @ http://www.dlms.com/documentation/overviewexcerptsofthedlmsuacolouredbooks/index.html
       1 : 'a',    2 : 'mo',    3 : 'wk',  4 : 'd',    5 : 'h',     6 : 'min.',  7 : 's',     8 : '°',     9 : '°C',    10 : 'currency',
      11 : 'm',   12 : 'm/s',  13 : 'm³', 14 : 'm³',  15 : 'm³/h', 16 : 'm³/h', 17 : 'm³/d', 18 : 'm³/d', 19 : 'l',     20 : 'kg',
      21 : 'N',   22 : 'Nm',   23 : 'Pa', 24 : 'bar', 25 : 'J',    26 : 'J/h',  27 : 'W',    28 : 'VA',   29 : 'var',   30 : 'Wh',
      31 : 'WAh', 32 : 'varh', 33 : 'A',  34 : 'C',   35 : 'V',    36 : 'V/m',  37 : 'F',    38 : 'Ω',    39 : 'Ωm²/h', 40 : 'Wb',
      41 : 'T',   42 : 'A/m',  43 : 'H',  44 : 'Hz',  45 : 'Rac',  46 : 'Rre',  47 : 'Rap',  48 : 'V²h',  49 : 'A²h',   50 : 'kg/s',
      51 : 'Smho'
    }
    _devices = {
      'smart-meter-gateway-com-1' : 'hex'
    }

    def __init__(self, smarthome, host=None, port=0, serialport=None, device="raw", cycle=300):
        self._sh = smarthome
        self.host = host
        self.port = int(port)
        self.serialport = serialport
        self.cycle = cycle
        self.connected = False
        self._serial = None
        self._sock = None
        self._target = None
        self._dataoffset = 0
        self._items = {}
        self._lock = threading.Lock()

        if device in self._devices:
          device = self._devices[device]

        if device == "hex":
            self._prepare = self._prepareHex
        elif device == "raw":
            self._prepare = self._prepareRaw
        else:
            self.logger.warning("Device type \"{}\" not supported - defaulting to \"raw\"".format(device))
            self._prepare = self._prepareRaw

        smarthome.connections.monitor(self)

    def run(self):
        self.alive = True
        self._sh.scheduler.add('Sml', self._refresh, cycle=self.cycle)

    def stop(self):
        self.alive = False
        self.disconnect()

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'sml_obis'):
            obis = self.get_iattr_value(item.conf, 'sml_obis')
            prop = self.get_iattr_value(item.conf, 'sml_prop') if self.has_iattr(item.conf, 'sml_prop') else 'valueReal'
            if obis not in self._items:
                self._items[obis] = {}
            if prop not in self._items[obis]:
                self._items[obis][prop] = []
            self._items[obis][prop].append(item)
            self.logger.debug('attach {} {} {}'.format(item.id(), obis, prop))
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
                    self.serialport, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=0)
            elif self.host is not None:
                self._target = 'tcp://{}:{}'.format(self.host, self.port)
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(2)
                self._sock.connect((self.host, self.port))
                self._sock.setblocking(False)
        except Exception as e:
            self.logger.error('Sml: Could not connect to {}: {}'.format(self._target, e))
            self._lock.release()
            return
        else:
            self.logger.info('Sml: Connected to {}'.format(self._target))
            self.connected = True
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
            self.logger.info('Sml: Disconnected!')
            self.connected = False
            self._target = None

    def _read(self, length):
        total = []
        while 1:
            if self._serial is not None:
                data = self._serial.read(length)
                if data:
                    total.append(data)
                else:
                    break
            elif self._sock is not None:
                try:
                    data = self._sock.recv(length)
                    if data:
                        total.append(data)
                except socket.error as e:
                    if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                        break
                    else:
                        raise e

        return b''.join(total)
        
    def _refresh(self):
        if self.connected:
            start = time.time()
            retry = 5
            while retry > 0:
                try:
                    data = self._read(512)

                    retry = 0
                    values = self._parse(self._prepare(data))

                    for obis in values:
                        self.logger.debug('Entry {}'.format(values[obis]))

                        if obis in self._items:
                            for prop in self._items[obis]:
                                for item in self._items[obis][prop]:
                                    item(values[obis][prop], 'Sml')

                except Exception as e:
                    self.logger.error('Reading data from {0} failed: {1} - reconnecting!'.format(self._target, e))

                    self.disconnect()
                    time.sleep(1)
                    self.connect()

                    retry = retry - 1
                    if retry == 0:
                        self.logger.warn('Trying to read data in next cycle due to connection errors!')


            cycletime = time.time() - start
            self.logger.debug("cycle takes {0} seconds".format(cycletime))

    def _parse(self, data):
        # Search SML List Entry sequences like:
        # "77 07 81 81 c7 82 03 ff 01 01 01 01 04 xx xx xx xx" - manufactor
        # "77 07 01 00 00 00 09 ff 01 01 01 01 0b xx xx xx xx xx xx xx xx xx xx 01" - server id
        # "77 07 01 00 01 08 00 ff 63 01 80 01 62 1e 52 ff 56 00 00 00 29 85 01"
        # Details see http://wiki.volkszaehler.org/software/sml
        values = {}
        packetsize = 7
        self.logger.debug('Data:{}'.format(''.join(' {:02x}'.format(x) for x in data)))
        self._dataoffset = 0
        while self._dataoffset < len(data)-packetsize:

            # Find SML_ListEntry starting with 0x77 0x07 and OBIS code end with 0xFF
            if data[self._dataoffset] == 0x77 and data[self._dataoffset+1] == 0x07 and data[self._dataoffset+packetsize] == 0xff:
                packetstart = self._dataoffset
                self._dataoffset += 1
                try:
                    entry = {
                      'objName'   : self._read_entity(data),
                      'status'    : self._read_entity(data),
                      'valTime'   : self._read_entity(data),
                      'unit'      : self._read_entity(data),
                      'scaler'    : self._read_entity(data),
                      'value'     : self._read_entity(data),
                      'signature' : self._read_entity(data)
                    }

                    # add additional calculated fields
                    entry['obis'] = '{}-{}:{}.{}.{}*{}'.format(entry['objName'][0], entry['objName'][1], entry['objName'][2], entry['objName'][3], entry['objName'][4], entry['objName'][5])
                    entry['valueReal'] = entry['value'] * 10 ** entry['scaler'] if entry['scaler'] is not None else entry['value']
                    entry['unitName'] = self._units[entry['unit']] if entry['unit'] != None and entry['unit'] in self._units else None

                    values[entry['obis']] = entry
                except Exception as e:
                    if self._dataoffset < len(data) - 1:
                        self.logger.warning('Can not parse entity at position {}, byte {}: {}:{}...'.format(self._dataoffset, self._dataoffset - packetstart, e, ''.join(' {:02x}'.format(x) for x in data[packetstart:packetstart+64])))
                        self._dataoffset = packetstart + packetsize - 1
            else:
                self._dataoffset += 1

        return values

    def _read_entity(self, data):
        import builtins
        upack = {
          5 : { 1 : '>b', 2 : '>h', 4 : '>i', 8 : '>q' },  # int
          6 : { 1 : '>B', 2 : '>H', 4 : '>I', 8 : '>Q' }   # uint
        }

        result = None

        tlf = data[self._dataoffset]
        type = (tlf & 112) >> 4
        more = tlf & 128
        len = tlf & 15
        self._dataoffset += 1

        if more > 0:
            tlf = data[self._dataoffset]
            len = (len << 4) + (tlf & 15)
            self._dataoffset += 1

        len -= 1

        if len == 0:     # skip empty optional value
            return result

        if self._dataoffset + len >= builtins.len(data):
            raise Exception("Try to read {} bytes, but only have {}".format(len, builtins.len(data) - self._dataoffset))

        if type == 0:    # octet string
            result = data[self._dataoffset:self._dataoffset+len]

        elif type == 5 or type == 6:  # int or uint
            d = data[self._dataoffset:self._dataoffset+len]

            ulen = len
            if ulen not in upack[type]:  # extend to next greather unpack unit
              while ulen not in upack[type]:
                d = b'\x00' + d
                ulen += 1

            result = struct.unpack(upack[type][ulen], d)[0]

        elif type == 7:  # list
            result = []
            self._dataoffset += 1
            for i in range(0, len + 1):
                result.append(self._read_entity(data))
            return result

        else:
            self.logger.warning('Skipping unkown field {}'.format(hex(tlf)))

        self._dataoffset += len

        return result

    def _prepareRaw(self, data):
        return data

    def _prepareHex(self, data):
        data = data.decode("iso-8859-1").lower();
        data = re.sub("[^a-f0-9]", " ", data)
        data = re.sub("( +[a-f0-9]|[a-f0-9] +)", "", data)
        data = data.encode()
        return bytes(''.join(chr(int(data[i:i+2], 16)) for i in range(0, len(data), 2)), "iso8859-1")

