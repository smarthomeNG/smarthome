#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  VR100/Neato plugin for SmartHomeNG. https://github.com/smarthomeNG//
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

import logging
import socket
import sys

logger = logging.getLogger('VR100')


class VR100():

    def __init__(self, smarthome, bt_addr, update_cycle="300"):
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._query_items = {}
        self._bt_addr = bt_addr
        self._terminator = bytes('\r\n\x1a\r\n\x1a', 'utf-8')

    def _update_values(self):
        #logger.debug("vr100: update")
        for query_cmd, fields in self._query_items.items():
            #logger.debug("vr100: requesting \'{}\'".format(query_cmd))
            self._send(query_cmd)
            for line in self._recv().splitlines():
                field, _, value = line.partition(',')
                #logger.debug("vr100: {}={}".format(field, value))
                field = field.upper()
                if field in self._query_items[query_cmd]:
                    for item in self._query_items[query_cmd][field]['items']:
                        item(value, 'VR100', "field \'{}\'".format(field))

    def run(self):
        self.alive = True
        if True:
            try:
                self._btsocket = socket.socket(
                    socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                self._btsocket.connect((self._bt_addr, 1))
                logger.info(
                    "vr100: via bluetooth connected to {}".format(self._bt_addr))
            except:
                logger.error(
                    "vr100: establishing connection to robot failed - {}".format(sys.exc_info()))
                return
        self._sh.scheduler.add('VR100', self._update_values,
                               prio=5, cycle=self._update_cycle)

    def stop(self):
        self.alive = False
        try:
            self._sh.scheduler.remove('VR100')
        except:
            logger.error(
                "vr100: removing VR100 from scheduler failed - {}".format(sys.exc_info()))
        try:
            self._btsocket.close()
        except:
            logger.error(
                "vr100: closing connection to robot failed - {}".format(sys.exc_info()))

    def parse_item(self, item):
        if 'vr100_cmd' in item.conf:
            cmd = item.conf['vr100_cmd']
            logger.debug("vr100: {0} will send cmd \'{1}\'".format(item, cmd))
            return self.update_item
        if 'vr100_info' in item.conf:
            info = item.conf['vr100_info'].rsplit(' ', 1)
            query_cmd = info[0]
            field = info[1].upper()
            if not query_cmd in self._query_items:
                self._query_items[query_cmd] = {}
            if not field in self._query_items[query_cmd]:
                self._query_items[query_cmd][field] = {
                    'items': [], 'logics': []}
            if not item in self._query_items[query_cmd][field]['items']:
                self._query_items[query_cmd][field]['items'].append(item)
            logger.debug("vr100: {0} will be updated by querying \'{1}\' and extracting \'{2}\'".format(
                item, query_cmd, field))
        return None

    def update_item(self, item, caller=None, source=None, dest=None):
        try:
            cmd = item.conf['vr100_cmd']
            value = item()
            if isinstance(value, bool):
                value = 'on' if value else 'off'
            if cmd.lower().startswith('clean') and not value:
                # allow stopping cleaning by setting item to false
                cmd = 'clean stop'
            self._send(cmd.format(value))
        except:
            pass

    def _recv(self, timeout=1.0):
        try:
            msg = bytearray()
            self._btsocket.settimeout(timeout)
            while ((len(msg) < len(self._terminator)) or (msg[-len(self._terminator):] != self._terminator)):
                msg += self._btsocket.recv(1000)
        except socket.timeout:
            logger.warning("vr100: rx: timeout after {}s".format(timeout))
            return ''
        except:
            logger.warning("vr100: rx: exception - {}".format(sys.exc_info()))
            return ''
        try:
            msg = msg[:-len(self._terminator)].decode()
        except:
            msg = ''
        #logger.debug("vr100: rx: msg: len={} / str={}".format(len(msg), msg))
        return msg

    def _send(self, msg):
        #logger.debug("vr100: tx: len={} / str={}".format(len(msg), msg))
        try:
            self._btsocket.send(bytes(msg + '\r\n', 'utf-8'))
        except OSError as e:
            if e.errno == 107:  # Der Socket ist nicht verbunden
                self.run()
        except:
            logger.warning("vr100: rx: exception - {}".format(sys.exc_info()))
