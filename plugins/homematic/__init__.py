#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.           https://knx-user-forum.de/
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

import logging
import sys
import xmlrpc
import xmlrpc.server
import xmlrpc.client

logger = logging.getLogger(__name__)

class Homematic():

    def __init__(self, smarthome, host='0.0.0.0', port='2001'):
        self.sh = smarthome
        self.host = host
        self.port = port
        self.korrektur = 0
    
    def run(self):
        server_url = 'http://' + self.host + ':' + self.port + '/'
        self.server = xmlrpc.client.ServerProxy(server_url)
        self.load_status()
        self.alive = True

    def load_status(self):
        for hm_devices in self.sh.find_items('hm_type'):
            if hm_devices.conf['hm_type'] == 'pos':
                try:
                    result = self.server.getValue(hm_devices.conf['hm_address'] + ':1', 'LEVEL')
                    value = 1 - float(result)
                    hm_devices(int(255 * float(value)))
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: " + hm_devices.conf['hm_address'])
            elif hm_devices.conf['hm_type'] == 'switch':
                try:
                    result = self.server.getValue(hm_devices.conf['hm_address'] + ':1', 'STATE')
                    hm_devices(bool(result))
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: " + hm_devices.conf['hm_address'])
            elif hm_devices.conf['hm_type'] == '2ch_switch':
                try:
                    result = self.server.getValue(hm_devices.conf['hm_address'] + ':' + hm_devices.conf['hm_channel'], 'STATE')
                    hm_devices(bool(result))
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: " + hm_devices.conf['hm_address'])

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'hm_address' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Homematic':
            if item.conf['hm_type'] == 'pos':
                new_value = float(item()) / 255
                conv_value = 1 - float(new_value)
                try:
                    result = self.server.setValue(item.conf['hm_address'] + ':1', 'LEVEL', str(conv_value)) 
                    logger.debug('Homematic: Rollo auf ' + str(conv_value))
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: ".format(e))
            elif item.conf['hm_type'] == 'stop':
                item(0)
                try:
                    result = self.server.setValue(item.conf['hm_address'] + ':1', 'STOP', bool('true'))
                    result2 = self.server.getValue(item.conf['hm_address'] + ':1', 'LEVEL')
                    for shutter_items in self.sh.find_items('hm_type'):
                        if shutter_items.conf['hm_type'] == 'pos':
                            if shutter_items.conf['hm_address'] == item.conf['hm_address']:
                                akt_value = 1 - float(result2)
                                shutter_items(int(255 * float(akt_value)))
                    logger.debug('Homematic: Rollo stop...')
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: ".format(e))
            elif item.conf['hm_type'] == 'move':
                direction = item()
                item(2)
                if direction == 0:
                    try:
                        result = self.server.setValue(item.conf['hm_address'] + ':1', 'LEVEL', '1')
                    except Exception as e:
                        logger.error("Could not connect to Homematic Device: ".format(e))
                elif direction == 1:
                    try:
                        result = self.server.setValue(item.conf['hm_address'] + ':1', 'LEVEL', '0') 
                        result2 = self.server.getValue(item.conf['hm_address'] + ':1', 'LEVEL')
                    except Exception as e:
                        logger.error("Could not connect to Homematic Device: ".format(e))
                    for shutter_items in self.sh.find_items('hm_type'):
                        if shutter_items.conf['hm_type'] == 'pos':
                            if shutter_items.conf['hm_address'] == item.conf['hm_address']:
                                akt_value = 1 - float(result2)
                                shutter_items(int(255 * float(akt_value)))
            elif item.conf['hm_type'] == 'switch':
                try:
                    result = self.server.setValue(item.conf['hm_address'] + ':1', 'STATE', item())
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: ".format(e))
            elif item.conf['hm_type'] == '2ch_switch':
                try:
                    result = self.server.setValue(item.conf['hm_address'] + ':' + item.conf['hm_channel'], 'STATE', item()) 
                except Exception as e:
                    logger.error("Could not connect to Homematic Device: ".format(e))
                    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = Homematic('homematic')
    myplugin.run()
