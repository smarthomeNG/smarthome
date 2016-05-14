#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.   http://smarthome.sourceforge.net/
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
import socket
import threading
import struct

import lib.my_asynchat

logger = logging.getLogger('')

REQ_DELIMITER = '\r\n'
RESP_DELIMITER = '\n'

class IrTrans(lib.my_asynchat.AsynChat):

    def __init__(self, smarthome, host, port=21000):
        lib.my_asynchat.AsynChat.__init__(self, smarthome, host, port)
        self._sh = smarthome
        self._recv_off = {}
        self._recv_on = {}
        self._recv_l = {}
        self._send_off = {}
        self._send_on = {}
        smarthome.monitor_connection(self)

    def send(self, remote, command, led=None, bus=None, mask=None)
        self._snd(remote, command, led, bus, mask)

    def send_repeat(self, remote, command, led=None, bus=None, mask=None)
        self._snd(remote, command, led, bus, mask, True)

    def _snd(self, remote, command, led=None, bus=None, mask=None, repeat=False):
        if repeat:
            data = 'sndr {}, {}'.format(remote, command)
        else:
            data = 'snd {}, {}'.format(remote, command)

        if led is not None:
            data += ', l{}'.format(led)
        if bus is not None:
            data += ', b{}'.format(bus)
        if mask is not None:
            data += ', m{}'.format(mask)
        
        self._send(data)
    
    def _send(self, data):
        self.push('A' + data + REQ_DELIMITER)

    def handle_connect(self):
        self.push('ASCI')
        self.terminator = RESP_DELIMITER

    def found_terminator(self):
        data = self.buffer
        self.buffer = ''
        
        data = data[8:].split(' ', 2)
        cmd = data[0]
        msg = data[1]

        if cmd == 'RESULT':
            if msg == 'OK':
                pass
            elif msg.startswith('Error'):
                logger.error(msg)
        elif cmd == 'RCV_COM':
            params = msg.split(',')
            key = params[0] + '.' + params[1]
           
            for item in self._recv_on[key]:
                item(True)
            for item in self._recv_off[key]:
                item(False)
            for logic in self._recv_l[key]:
                logic.trigger('IrTrans')

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'ir_remote' in item.conf:
            r = item.conf['ir_remote']
        else:
            return None

        if 'ir_on' in item.conf:
            c_on = item.conf['ir_on']
        if 'ir_off' in item.conf:
            c_off = item.conf['ir_off']

        if not item._type is 'bool':
            logger.warning('Remote {} specified for neither boolean nor numeric item {}'.format(r, item))
            return None

        if c_on is None and c_off is None:
            logger.warning('No on or off command for remote {} specified for item {}'.format(r, item))
            return None

        if not c_on is None:
            key = r + '.' + c_on
            if key in self._recv_on:
                self._recv_on[key].append(item)
            else:
                self._recv_on[key] = [item]
            self._send_on[item] = {'remote': r, 'command': c_on}
        if not c_off is None:
            key = r + '.' + c_off
            if key in self._recv_off:
                self._recv_off[key].append(item)
            else:
                self._recv_off[key] = [item]
            self._send_off[item] = {'remote': r, 'command': c_off }

        return self.update_item

    def parse_logic(self, logic):
        if 'ir_remote' in logic.conf:
            r = logic.conf['ir_remote']
        else:
            return None

        if 'ir_command' in logic.conf:
            c = logic.conf['ir_command']
        else:
            logger.warning('No command for remote {} specified on logic {}'.format(r, logic))
            return None

        key = r + '.' + c
        if key in self._recv_l:
            self._recv_l[key].append(logic)
        else:
            self._recv_l[key] = [logic]

    def update_item(self, item, caller=None, source=None):
        if caller != 'IrTrans':
            if item in self._send_on:
                on = self._send_on[item]
                self.send(on['remote'], on['command'])

            if item in self._send_off:
                off = self._send_off[item]
                self.send(off['remote'], off['command'])

