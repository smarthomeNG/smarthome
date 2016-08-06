#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-     Christian Strassburg            c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/

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
#########################################################################
#  Usage:
#
#  1. activate the plugin in etc/plugins.conf
#    [wakeonlan]
#        class_name = WakeOnLan
#        class_path = plugins.wol
#
#  2. add to you items atribute  "wol_mac" with the mac for wake up
#  [wakeonlan_item]
#     type = bool
#     wol_mac = 01:02:03:04:05:06
#
#  type of separators are unimportant. you can use:
#    wol_mac = 01:02:03:04:05:06
#  or:
#    wol_mac = 01-02-03-04-05-06
#  or don't use any separators:
#    wol_mac = 010203040506
#

import logging
import socket
from lib.model.smartplugin import SmartPlugin

ITEM_TAG = ['wol_mac']
class WakeOnLan(SmartPlugin):
    PLUGIN_VERSION = "1.1.2"
    ALLOW_MULTIINSTANCE = True
    def __init__(self, sh,*args, **kwargs):
        self._sh = sh
        self.logger = logging.getLogger(__name__)
        print("###"+self.get_instance_name())

    def __call__(self, mac_adr):
        self.wake_on_lan(mac_adr)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if self.has_iattr(item.conf, ITEM_TAG[0]):
            return self.update_item

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if item():
            if self.has_iattr(item.conf, ITEM_TAG[0]):
                self.wake_on_lan(self.get_iattr_value(item.conf,ITEM_TAG[0]))

    def wake_on_lan(self, mac_adr):
        self.logger.debug("WakeOnLan: send magic paket to {}".format(mac_adr))
        # check length and format 
        if self.is_mac(mac_adr) != True:
            self.logger.warning("WakeOnLan: invalid mac address {}!".format(mac_adr))
            return
        if len(mac_adr) == 12 + 5:
            sep = mac_adr[2]
            mac_adr = mac_adr.replace(sep, '')
        # create magic packet 
        data = ''.join(['FF' * 6, mac_adr * 20])
        # Broadcast
        self.logger.debug("WakeOnLan: send magic paket " + data)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(bytearray.fromhex(data), ('<broadcast>', 7))
    def testprint(self):
        print(self.get_version())
        print(self.get_instance_name())
        print(self.to_bool("yes"))
if __name__ == '__main__':
    myplugin = WakeOnLan('smarthome-dummy')
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    myplugin.wake_on_lan('01:02:03:04:05:06')

