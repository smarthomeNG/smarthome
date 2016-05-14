#!/usr/bin/env python3
#
###############################################################################
# Copyright (c) 2013 Marcus Popp
###############################################################################
#
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################
"""
==========================
 Wake On Lan
==========================

.. codeauthor:: Marcus Popp

This plugin awakes computers by a network message. A magic Wake-on-LAN packet.

Requirements
============

This plugin has no requirements or dependencies.

Configuration
=============

plugin.conf
-----------
::

    [wol]
        class_name = WOL
        class_path = plugins.wol

items.conf
----------
::

    [test]
        [[wol]]
            type = bool
            wol_mac = 03:06:a0:87:22:33


Methods
=======

.. autoclass:: WOL()
   :members:

"""

import logging
import socket

logger = logging.getLogger('')


class WOL():
    def __init__(self, smarthome):
        self._sh = smarthome

    def __call__(self, mac):
        self.wol(mac)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'wol_mac' in item.conf:
            return self.update_item

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if item():
            if 'wol_mac' in item.conf:
                self.wol(item.conf['wol_mac'])

    def wol(self, mac):
        """
        :param mac: MAC address to wake up
        """
        logger.debug("WOL: sending packet to {}".format(mac))
        mac = ''.join([p.zfill(2) for p in mac.replace(':', ' ').split()])

        mac = bytearray.fromhex(mac)
        if len(mac) != 6:
            logger.warning("WOL: invalid mac address {}!".format(mac))
            return

        magic = bytearray([255] * 6)
        magic.extend(mac * 16)
        try:
            _s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            _s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            _s.sendto(magic, ('<broadcast>', 9))
        except:
            pass
        finally:
            try:
                _s.close()
            except:
                pass
