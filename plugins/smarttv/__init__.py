#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
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
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
import socket
import time
import base64

from uuid import getnode as getmac

logger = logging.getLogger('')


class SmartTV():

    def __init__(self, smarthome, host, port=55000, tvid=1):
        self._sh = smarthome
        self._host = host
        self._port = port
        self._tvid = int(tvid)

    def push(self, key):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._host, int(self._port)))
            logger.debug("Connected to {0}:{1}".format(self._host, self._port))
        except Exception:
            logger.warning("Could not connect to %s:%s, to send key: %s." %
                           (self._host, self._port, key))
            return

        src = s.getsockname()[0]            # ip of remote
        mac = self._int_to_str(getmac())    # mac of remote
        remote = 'sh.py remote'             # remote name
        dst = self._host                    # ip of tv
        app = b'python'                      # iphone..iapp.samsung
        tv = b'UE32ES6300'                   # iphone.UE32ES6300.iapp.samsung

        logger.debug("src = {0}, mac = {1}, remote = {2}, dst = {3}, app = {4}, tv = {5}".format(
            src, mac, remote, dst, app, tv))

        src = base64.b64encode(src.encode())
        mac = base64.b64encode(mac.encode())
        cmd = base64.b64encode(key.encode())
        rem = base64.b64encode(remote.encode())

        msg = bytearray([0x64, 0])
        msg.extend([len(src), 0])
        msg.extend(src)
        msg.extend([len(mac), 0])
        msg.extend(mac)
        msg.extend([len(rem), 0])
        msg.extend(rem)

        pkt = bytearray([0])
        pkt.extend([len(app), 0])
        pkt.extend(app)
        pkt.extend([len(msg), 0])
        pkt.extend(msg)

        try:
            s.send(pkt)
        except:
            try:
                s.close()
            except:
                pass
            return

        msg = bytearray([0, 0, 0])
        msg.extend([len(cmd), 0])
        msg.extend(cmd)

        pkt = bytearray([0])
        pkt.extend([len(tv), 0])
        pkt.extend(tv)
        pkt.extend([len(msg), 0])
        pkt.extend(msg)

        try:
            s.send(pkt)
        except:
            return
        finally:
            try:
                s.close()
            except:
                pass
        logger.debug("Send {0} to Smart TV".format(key))
        time.sleep(0.1)

    def parse_item(self, item):
        if 'smarttv_id' in item.conf:
            tvid = int(item.conf['smarttv_id'])
        else:
            tvid = 1

        if tvid != self._tvid:
            return None

        if 'smarttv' in item.conf:
            logger.debug("Smart TV Item {0} with value {1} for TV ID {2} found!".format(
                item, item.conf['smarttv'], tvid))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        val = item()
        if isinstance(val, str):
            if val.startswith('KEY_'):
                self.push(val)
            return
        if val:
            keys = item.conf['smarttv']
            if isinstance(keys, str):
                keys = [keys]
            for key in keys:
                if isinstance(key, str) and key.startswith('KEY_'):
                    self.push(key)

    def parse_logic(self, logic):
        pass

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def _int_to_words(self, int_val, word_size, num_words):
        max_int = 2 ** (num_words * word_size) - 1

        if not 0 <= int_val <= max_int:
            raise IndexError('integer out of bounds: %r!' % hex(int_val))

        max_word = 2 ** word_size - 1

        words = []
        for _ in range(num_words):
            word = int_val & max_word
            words.append(int(word))
            int_val >>= word_size

        return tuple(reversed(words))

    def _int_to_str(self, int_val):
        words = self._int_to_words(int_val, 8, 6)
        tokens = ['%.2X' % i for i in words]
        addr = '-'.join(tokens)

        return addr
