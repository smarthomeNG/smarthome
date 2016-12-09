#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
#  Copyright 2014 Brootux (https://github.com/Brootux) as GNU-GPL
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
import re
import socket

logger = logging.getLogger('elro')


class Elro():

    def __init__(self, smarthome):
        self._sh = smarthome
        self._host = "localhost"
        self._port = 6700

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):

        # Parse just the parent-items wich define the 'elro_host'
        # and/or 'elro_port' attribute
        if 'elro_host' in item.conf:

            # Get the host-name/ip from parent-item
            self._host = item.conf['elro_host']

            # Try to get the port from parent-item
            # (else the default value will be uesed)
            if 'elro_port' in item.conf:
                self._port = int(item.conf['elro_port'])

            # Get all child-item-lists for the given fields (parse to set)
            escSet = set(self._sh.find_children(item, 'elro_system_code'))
            eucSet = set(self._sh.find_children(item, 'elro_unit_code'))
            esSet = set(self._sh.find_children(item, 'elro_send'))

            # Just get those child-items which have all mandatory fields
            # set (elro_system_code and elro_unit_code and elro_send)
            validItems = list(escSet & eucSet & esSet)

            # Iterate over all valid child-items
            for item in validItems:
                # Add fields of parent-item to all valid child-items
                item.conf['elro_host'] = self._host
                item.conf['elro_port'] = self._port

                # Add method trigger to all valid child-items
                item.add_method_trigger(self._send)

    def _send(self, item, caller=None, source=None, dest=None):

        # Just let calls from outside pass
        if (caller != 'Elro'):
            # Send informations to server (e.g. "0.0.0.0.1;2;0")
            self.send("%s;%s;%s" % (
                                    item.conf['elro_system_code'],
                                    item.conf['elro_unit_code'],
                                    int(item())
                                   ),
                      item.conf['elro_host'],
                      item.conf['elro_port'])

    def send(self, payload="0.0.0.0.1;1;0", host="localhost", port=6700):

        # Print what will be send as a debug-message
        logger.debug("ELRO: Sending %s to %s:%s" % (payload, host, port))

        # Create socket
        s = socket.socket()

        # Connect to server
        s.connect((host, port))

        # Write payload to server
        s = s.makefile(mode="rw")
        s.write(payload)
        s.flush()

        # Close server-connection
        s.close()
