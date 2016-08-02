#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#  Copyright 2016- Christian Strassburg               c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.py.  
#  Visit:  https://github.com/smarthomeNG/
#          https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SmartHomeNG.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import threading
import struct
import binascii

import lib.connection
from . import dpts

KNXREAD = 0x00
KNXRESP = 0x40
KNXWRITE = 0x80


class KNX(lib.connection.Client):

    def __init__(self, smarthome, time_ga=None, date_ga=None, send_time=False, busmonitor=False, host='127.0.0.1', port=6720, readonly=False, instance='default'):
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self.gal = {}
        self.gar = {}
        self._init_ga = []
        self._cache_ga = []
        self.time_ga = time_ga
        self.date_ga = date_ga
        self.instance = instance
        self._lock = threading.Lock()
        if smarthome.string2bool(busmonitor):
            self._busmonitor = self.logger.info
        else:
            self._busmonitor = self.logger.debug
        if send_time:
            self._sh.scheduler.add('KNX[{0}] time'.format(self.instance), self._send_time, prio=5, cycle=int(send_time))
        if readonly: 
            self.logger.warning("!!! KNX Plugin in READONLY mode !!! ")
        self.readonly = readonly

    def _send(self, data):
        if len(data) < 2 or len(data) > 0xffff:
            self.logger.debug('KNX[{0}]: Illegal data size: {1}'.format(self.instance, repr(data)))
            return False
        # prepend data length
        send = bytearray(len(data).to_bytes(2, byteorder='big'))
        send.extend(data)
        self.send(send)

    def groupwrite(self, ga, payload, dpt, flag='write'):
        pkt = bytearray([0, 39])
        try:
            pkt.extend(self.encode(ga, 'ga'))
        except:
            self.logger.warning('KNX[{0}]: problem encoding ga: {1}'.format(self.instance, ga))
            return
        pkt.extend([0])
        pkt.extend(self.encode(payload, dpt))
        if flag == 'write':
            flag = KNXWRITE
        elif flag == 'response':
            flag = KNXRESP
        else:
            self.logger.warning("KNX[{0}]: groupwrite telegram for {1} with unknown flag: {2}. Please choose beetween write and response.".format(self.instance, ga, flag))
            return
        pkt[5] = flag | pkt[5]
        if self.readonly:
            self.logger.info("KNX: groupwrite telegram for: {0} - Value: {1} not send. Plugin in READONLY mode. ".format(ga,payload))
        else:
            self._send(pkt)

    def _cacheread(self, ga):
        pkt = bytearray([0, 116])
        try:
            pkt.extend(self.encode(ga, 'ga'))
        except:
            self.logger.warning('KNX[{0}]: problem encoding ga: {1}'.format(self.instance, ga))
            return
        pkt.extend([0, 0])
        self._send(pkt)

    def groupread(self, ga):
        pkt = bytearray([0, 39])
        try:
            pkt.extend(self.encode(ga, 'ga'))
        except:
            self.logger.warning('KNX[{0}]: problem encoding ga: {1}'.format(self.instance, ga))
            return
        pkt.extend([0, KNXREAD])
        self._send(pkt)

    def _send_time(self):
        self.send_time(self.time_ga, self.date_ga)

    def send_time(self, time_ga=None, date_ga=None):
        now = self._sh.now()
        if time_ga:
            self.groupwrite(time_ga, now, '10')
        if date_ga:
            self.groupwrite(date_ga, now.date(), '11')

    def handle_connect(self):
        self.discard_buffers()
        enable_cache = bytearray([0, 112])
        self._send(enable_cache)
        self.found_terminator = self.parse_length
        if self._cache_ga != []:
            if self.connected:
                self.logger.debug('KNX[{0}]: reading eibd cache'.format(self.instance))
                for ga in self._cache_ga:
                    self._cacheread(ga)
                self._cache_ga = []
        self.logger.debug('KNX[{0}]: enable group monitor'.format(self.instance))
        init = bytearray([0, 38, 0, 0, 0])
        self._send(init)
        self.terminator = 2
        if self._init_ga != []:
            if self.connected:
                self.logger.debug('KNX[{0}]: init read'.format(self.instance))
                for ga in self._init_ga:
                    self.groupread(ga)
                self._init_ga = []

#   def collect_incoming_data(self, data):
#       print('#  bin   h  d')
#       for i in data:
#           print("{0:08b} {0:02x} {0:02d}".format(i))
#       self.buffer.extend(data)

    def parse_length(self, length):
        self.found_terminator = self.parse_telegram
        try:
            self.terminator = struct.unpack(">H", length)[0]
        except:
            self.logger.error("KNX[{0}]: problem unpacking length: {1}".format(self.instance, length))
            self.close()

    def encode(self, data, dpt):
        return dpts.encode[str(dpt)](data)

    def decode(self, data, dpt):
        return dpts.decode[str(dpt)](data)

    def parse_telegram(self, data):
        self.found_terminator = self.parse_length  # reset parser and terminator
        self.terminator = 2
        # 2 byte type
        # 2 byte src
        # 2 byte dst
        # 2 byte command/data
        # x byte data
        typ = struct.unpack(">H", data[0:2])[0]
        if (typ != 39 and typ != 116) or len(data) < 8:
#           self.logger.debug("Ignore telegram.")
            return
        if (data[6] & 0x03 or (data[7] & 0xC0) == 0xC0):
            self.logger.debug("KNX[{0}]: Unknown APDU".format(self.instance))
            return
        src = self.decode(data[2:4], 'pa')
        dst = self.decode(data[4:6], 'ga')
        flg = data[7] & 0xC0
        if flg == KNXWRITE:
            flg = 'write'
        elif flg == KNXREAD:
            flg = 'read'
        elif flg == KNXRESP:
            flg = 'response'
        else:
            self.logger.warning("KNX[{0}]: Unknown flag: {1:02x} src: {2} dest: {3}".format(self.instance, flg, src, dst))
            return
        if len(data) == 8:
            payload = bytearray([data[7] & 0x3f])
        else:
            payload = data[8:]
        if flg == 'write' or flg == 'response':
            if dst not in self.gal:  # update item/logic
                self._busmonitor("KNX[{0}]: {1} set {2} to {3}".format(self.instance, src, dst, binascii.hexlify(payload).decode()))
                return
            dpt = self.gal[dst]['dpt']
            try:
                val = self.decode(payload, dpt)
            except Exception as e:
                self.logger.exception("KNX[{0}]: Problem decoding frame from {1} to {2} with '{3}' and DPT {4}. Exception: {5}".format(self.instance, src, dst, binascii.hexlify(payload).decode(), dpt, e))
                return
            if val is not None:
                self._busmonitor("KNX[{0}]: {1} set {2} to {3}".format(self.instance, src, dst, val))
                #print "in:  {0}".format(self.decode(payload, 'hex'))
                #out = ''
                #for i in self.encode(val, dpt):
                #    out += " {0:x}".format(i)
                #print "out:{0}".format(out)
                for item in self.gal[dst]['items']:
                    item(val, 'KNX', src, dst)
                for logic in self.gal[dst]['logics']:
                    logic.trigger('KNX', src, val, dst)
            else:
                self.logger.warning("KNX[{0}]: Wrong payload '{3}' for ga '{2}' with dpt '{1}'.".format(self.instance, dpt, dst, binascii.hexlify(payload).decode()))
        elif flg == 'read':
            self.logger.debug("KNX[{0}]: {1} read {2}".format(self.instance, src, dst))
            if dst in self.gar:  # read item
                if self.gar[dst]['item'] is not None:
                    item = self.gar[dst]['item']
                    self.groupwrite(dst, item(), item.conf['knx_dpt'], 'response')
                if self.gar[dst]['logic'] is not None:
                    self.gar[dst]['logic'].trigger('KNX', src, None, dst)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.handle_close()

    def parse_item(self, item):
        if 'knx_dtp' in item.conf:
            self.logger.warning("KNX[{0}]: Ignoring {1}: please change knx_dtp to knx_dpt.".format(self.instance, item))
            return None
        if 'knx_dpt' in item.conf:
            dpt = item.conf['knx_dpt']
            if dpt not in dpts.decode:
                self.logger.warning("KNX[{0}]: Ignoring {1} unknown dpt: {2}".format(self.instance, item, dpt))
                return None
        else:
            return None

        if 'knx_instance' in item.conf:
            if not item.conf['knx_instance'] == self.instance:
                return None
        else:
            if not self.instance == 'default':
                return None
        self.logger.debug("KNX[{1}]: Item {0} is mapped to KNX Instance {1}".format(item, self.instance))

        if 'knx_listen' in item.conf:
            knx_listen = item.conf['knx_listen']
            if isinstance(knx_listen, str):
                knx_listen = [knx_listen, ]
            for ga in knx_listen:
                self.logger.debug("KNX[{0}]: {1} listen on {2}".format(self.instance, item, ga))
                if not ga in self.gal:
                    self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}
                else:
                    if not item in self.gal[ga]['items']:
                        self.gal[ga]['items'].append(item)

        if 'knx_init' in item.conf:
            ga = item.conf['knx_init']
            self.logger.debug("KNX[{0}]: {1} listen on and init with {2}".format(self.instance, item, ga))
            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}
            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._init_ga.append(ga)

        if 'knx_cache' in item.conf:
            ga = item.conf['knx_cache']
            self.logger.debug("KNX[{0}]: {1} listen on and init with cache {2}".format(self.instance, item, ga))
            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}
            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._cache_ga.append(ga)

        if 'knx_reply' in item.conf:
            knx_reply = item.conf['knx_reply']
            if isinstance(knx_reply, str):
                knx_reply = [knx_reply, ]
            for ga in knx_reply:
                self.logger.debug("KNX[{0}]: {1} reply to {2}".format(self.instance, item, ga))
                if ga not in self.gar:
                    self.gar[ga] = {'dpt': dpt, 'item': item, 'logic': None}
                else:
                    self.logger.warning("KNX[{0}]: {1} knx_reply ({2}) already defined for {3}".format(self.instance, item.id(), ga, self.gar[ga]['item']))

        if 'knx_send' in item.conf:
            if isinstance(item.conf['knx_send'], str):
                item.conf['knx_send'] = [item.conf['knx_send'], ]

        if 'knx_status' in item.conf:
            if isinstance(item.conf['knx_status'], str):
                item.conf['knx_status'] = [item.conf['knx_status'], ]

        if 'knx_status' in item.conf or 'knx_send' in item.conf:
            return self.update_item

        return None

    def parse_logic(self, logic):
        if 'knx_dpt' in logic.conf:
            dpt = logic.conf['knx_dpt']
            if dpt not in dpts.decode:
                self.logger.warning("KNX[{0}]: Ignoring {1} unknown dpt: {2}".format(self.instance, logic, dpt))
                return None
        else:
            return None

        if 'knx_instance' in logic.conf:
            if not logic.conf['knx_instance'] == self.instance:
                return None
        else:
            if not self.instance == 'default':
                return None
        self.logger.debug("KNX[{1}]: Logic {0} is mapped to KNX Instance {1}".format(logic, self.instance))

        if 'knx_listen' in logic.conf:
            knx_listen = logic.conf['knx_listen']
            if isinstance(knx_listen, str):
                knx_listen = [knx_listen, ]
            for ga in knx_listen:
                self.logger.debug("KNX[{0}]: {1} listen on {2}".format(self.instance, logic, ga))
                if not ga in self.gal:
                    self.gal[ga] = {'dpt': dpt, 'items': [], 'logics': [logic]}
                else:
                    self.gal[ga]['logics'].append(logic)

        if 'knx_reply' in logic.conf:
            knx_reply = logic.conf['knx_reply']
            if isinstance(knx_reply, str):
                knx_reply = [knx_reply, ]
            for ga in knx_reply:
                self.logger.debug("KNX[{0}]: {1} reply to {2}".format(self.instance, logic, ga))
                if ga in self.gar:
                    if self.gar[ga]['logic'] is False:
                        obj = self.gar[ga]['item']
                    else:
                        obj = self.gar[ga]['logic']
                    self.logger.warning("KNX[{0}]: {1} knx_reply ({2}) already defined for {3}".format(self.instance, logic, ga, obj))
                else:
                    self.gar[ga] = {'dpt': dpt, 'item': None, 'logic': logic}

    def update_item(self, item, caller=None, source=None, dest=None):
        if 'knx_send' in item.conf:
            if caller != 'KNX':
                for ga in item.conf['knx_send']:
                    self.groupwrite(ga, item(), item.conf['knx_dpt'])
        if 'knx_status' in item.conf:
            for ga in item.conf['knx_status']:  # send status update
                if ga != dest:
                    self.groupwrite(ga, item(), item.conf['knx_dpt'])
