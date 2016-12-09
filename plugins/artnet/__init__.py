#!/usr/bin/env python3
# coding=utf-8
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
# Author    mode@gmx.co.uk
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
import socket
import struct

logger = logging.getLogger('Artnet')


class ArtNet():
    packet_counter = 1
    dmxdata = [0, 0]

    def __init__(self, smarthome, artnet_net, artnet_subnet, artnet_universe, ip, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.net = int(artnet_net)
        self.subnet = int(artnet_subnet)
        self.universe = int(artnet_universe)
        self.ip = ip
        self.port = int(port)
        logger.debug("Init ArtNet Plugin done")

    def run(self):
        pass

    def stop(self):
        self.close()

    def __call__(self, var1=None, var2=None):
        if type(var1) == int and type(var2) == int:
            self.send_single_value(var1, var2)
        if type(var1) == int and type(var2) == list:
            self.send_frame_starting_at(var1, var2)
        if type(var1) == list and type(var2) == type(None):
            self.send_frame(var1)

    def send_single_value(self, adr, value):
        if adr < 1 or adr > 512:
            logger.error("DMX address %s invalid" % adr)
            return

        while len(self.dmxdata) < adr:
            self.dmxdata.append(0)
        self.dmxdata[adr - 1] = value
        self.__ArtDMX_broadcast()

    def send_frame_starting_at(self, adr, values):
        if adr < 1 or adr > (512 - len(values) + 1):
            logger.error("DMX address %s with length %s invalid" %
                         (adr, len(values)))
            return

        while len(self.dmxdata) < (adr + len(values) - 1):
            self.dmxdata.append(0)
        cnt = 0
        for value in values:
            self.dmxdata[adr - 1 + cnt] = value
            cnt += 1
        self.__ArtDMX_broadcast()

    def send_frame(self, dmxframe):
        if len(dmxframe) < 2:
            logger.error("Send at least 2 channels")
            return
        self.dmxdata = dmxframe
        self.__ArtDMX_broadcast()

    def __ArtDMX_broadcast(self):
#       logger.info("Incomming DMX: %s"%self.dmxdata)
        # New Array
        data = []
        # Fix ID 7byte + 0x00
        data.append("Art-Net\x00")
        # OpCode = OpOutput / OpDmx -> 0x5000, Low Byte first
        data.append(struct.pack('<H', 0x5000))
        # ProtVerHi and ProtVerLo -> Protocol Version 14, High Byte first
        data.append(struct.pack('>H', 14))
        # Order 1 to 255
        data.append(struct.pack('B', self.packet_counter))
        self.packet_counter += 1
        if self.packet_counter > 255:
            self.packet_counter = 1
        # Physical Input Port
        data.append(struct.pack('B', 0))
        # Artnet source address
        data.append(
            struct.pack('<H', self.net << 8 | self.subnet << 4 | self.universe))
        # Length of DMX Data, High Byte First
        data.append(struct.pack('>H', len(self.dmxdata)))
        # DMX Data
        for d in self.dmxdata:
            data.append(struct.pack('B', d))
        # convert from list to string
        result = bytes()
        for token in data:
            try:  # Handels all strings
                result = result + token.encode('utf-8', 'ignore')
            except:  # Handels all bytes
                result = result + token
#       data = "".join(data)
        # debug
#       logger.info("Outgoing Artnet:%s"%(':'.join(x.encode('hex') for x in data)))
        # send over ethernet
        self.s.sendto(result, (self.ip, self.port))

    def close(self):
        self.s.close()
