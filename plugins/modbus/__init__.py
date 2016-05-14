#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  Modbus plugin for SmartHome.py.       http://mknx.github.io/smarthome/
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

import serial
import logging
import struct
import time
import datetime

# Table of CRC values for high–order byte
FCSTABHI = [
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40
]

# Table of CRC values for low–order byte
FCSTABLO = [
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
    0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
    0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
    0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
    0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
    0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
    0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
    0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
    0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
    0x40
]

logger = logging.getLogger('Modbus')


class Modbus():

    def __init__(self, smarthome, serialport, slave_address="1", update_cycle="30"):
        self._sh = smarthome
        self.slave_address = int(slave_address)
        self._holding_registers = {}
        self._update = {}
        self._serial = serial.Serial(serialport, 9600, timeout=2)
        self._sh.scheduler.add('Modbus', self._update_values, prio=5, cycle=int(update_cycle))

    def _update_values(self):
        self._read_holding_registers(0xFDFE, 26)
        time.sleep(0.2)
        self._read_holding_registers(0x0001, 125)
        time.sleep(0.2)
        self._read_holding_registers(0x07D1, 125)
        time.sleep(0.2)
        self._read_holding_registers(0x0FA1, 113)

        for regaddr in self._update:
            if not (regaddr in self._holding_registers):
                continue
            for item in self._update[regaddr]['items']:
                try:
                    datatype = item.conf['modbus_datatype']
                    if (datatype == 'VT_R4'):
                        value = round(self._decode_vt_r4(regaddr), 1)
                    elif (datatype == 'VT_UI1'):
                        value = (self._decode_vt_array_ui1(regaddr, 0x0001) == 0x0001)
                    elif (datatype == 'VT_ARRAY_UI1') and ('modbus_datamask' in item.conf):
                        mask = int(item.conf['modbus_datamask'], 0)
                        value = self._decode_vt_array_ui1(regaddr, mask)
                        if (item.type() == 'bool'):
                            value = (value == mask)
                    elif (datatype == 'VT_BSTR'):
                        value = self._decode_vt_bstr(regaddr)
                    elif (datatype == 'VT_TIME'):
                        value = self._decode_vt_time(regaddr)
                        if (item.type() == 'str'):
                            value = str(value)
                    elif (datatype == 'VT_DATE'):
                        value = self._decode_vt_date(regaddr)
                        if (item.type() == 'str'):
                            value = str(value)
                    else:
                        logger.warning("Modbus: DataType unknown: {}".format(datatype))
                        continue
                    item(value, 'Modbus', "Reg {}".format(regaddr))
                except Exception as e:
                    logger.error("Modbus: Exception when updating {} {}".format(item, e))

    def _decode_vt_r4(self, addr):
        return struct.unpack('f', bytes([self._holding_registers[addr] & 0xFF, self._holding_registers[addr] >> 8, self._holding_registers[addr + 16] & 0xFF, self._holding_registers[addr + 16] >> 8]))[0]

    def _decode_vt_array_ui1(self, addr, mask):
        return (self._holding_registers[addr] & mask)

    def _decode_vt_bstr(self, addr):
        bstr = bytearray()
        for i in range(8):
            bstr += bytes([self._holding_registers[addr + i * 16] & 0xFF, self._holding_registers[addr + i * 16] >> 8])
        return bstr.decode('cp850')

    def _decode_vt_time(self, addr):
        return datetime.time(self._holding_registers[addr] >> 8, self._holding_registers[addr] & 0xFF)

    def _decode_vt_date(self, addr):
#        return datetime.datetime((self._holding_registers[addr+5*16] & 0xFF) + 1900, (self._holding_registers[addr+4*16] & 0xFF) + 1, (self._holding_registers[addr+3*16] & 0xFF),
#                                  (self._holding_registers[addr+2*16] & 0xFF), (self._holding_registers[addr+1*16] & 0xFF), (self._holding_registers[addr] & 0xFF))
        return datetime.datetime.utcfromtimestamp((self._holding_registers[1 + (12 * 16)] << 16) + self._holding_registers[1 + (11 * 16)])

    def run(self):
        self.alive = True
        self.connect()

    def stop(self):
        self.alive = False

    def connect(self):
        logger.debug("Modbus: connect")
        self._serial.write(b'AT\r')
        time.sleep(4)
        self._serial.write(b'AT\r')

    def parse_item(self, item):
        if ('modbus_regaddr' in item.conf) and ('modbus_datatype' in item.conf):
            modbus_regaddr = int(item.conf['modbus_regaddr'])
            logger.debug("modbus: {0} connected to register {1:#04x} with datatype {2}".format(item, modbus_regaddr, item.conf['modbus_datatype']))
            if not modbus_regaddr in self._update:
                self._update[modbus_regaddr] = {'items': [item], 'logics': []}
            else:
                if not item in self._update[modbus_regaddr]['items']:
                    self._update[modbus_regaddr]['items'].append(item)
        return None

    def _calc_crc16(self, msg):
        crchi = 0xFF
        crclo = 0xFF
        for i in msg:
            index = crclo ^ i
            crclo = crchi ^ FCSTABHI[index]
            crchi = FCSTABLO[index]
        return bytes([crclo, crchi])

    def _send(self, msg):
        self._serial.write(msg + self._calc_crc16(msg))

    def _receive(self):
        msg = bytearray()
        while self.alive:
            try:
                msg += self._serial.read(1000)
            except:
                logger.debug("Modbus: read timeout")
                return None
            # check if msg is complete and ok
            if (len(msg) >= 3) and (msg[0] == 0x01) and (msg[1] == 0x03) and (len(msg) == (msg[2] + 5)) and (self._calc_crc16(msg[:-2]) == msg[-2:]):
                return msg

    def _transfer(self, msg):
        self._send(msg)
        self._serial.drainOutput()
        return self._receive()

    def _read_holding_registers(self, start_address, quantity):
        msg = bytes([self.slave_address, 0x03]) + start_address.to_bytes(2, byteorder='big') + quantity.to_bytes(2, byteorder='big')
        response = self._transfer(msg)
        if response is None:
            logger.warning("Modbus: no response when reading holding registers")
        elif (response[2] != (2 * quantity)):
            logger.warning("Modbus: wrong response length when reading holding registers")
        else:
            for i in range(0, 2 * quantity - 2, 2):
                self._holding_registers[start_address + (i * 8)] = int.from_bytes(response[3 + i:5 + i], byteorder='big')
