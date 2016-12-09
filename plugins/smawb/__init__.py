#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2014 Brootux (https://github.com/Brootux) as GNU-GPL
#
# This file is part of SmartHomeNG. https://github.com/smarthomeNG//
#
# SmartHomeNG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SmartHomeNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import re
import socket

from .SunnyWebBox import SunnyWebBoxHTTP
from .SunnyWebBox import SunnyWebBoxUDPStream


logger = logging.getLogger('smawb')


class SMAWB():
    def __init__(self, smarthome, smawb_polling_cycle=10):
        self._sh = smarthome
        self._polling_cycle = int(smawb_polling_cycle)
        self._items = dict()

    def run(self):
        self._alive = True

        # Register updating of items at the smarthome sheduler.
        self._sh.scheduler.add('SMAWB', self._update_values, prio=5, cycle=self._polling_cycle)

    def stop(self):
        self._alive = False

    def _update_values(self):
        # Iterate over all SunnyWebBoxes
        for host in self._items.keys():
            # Initialize Connection to SunnyWebBox
            swb = None

            # Setup connection to SunnyWebBox
            if self._items[host]['udp']:
                swb = SunnyWebBoxUDPStream(host, self._items[host]['password'])
            else:
                swb = SunnyWebBoxHTTP(host, self._items[host]['password'])

            # Iterate over all inverters in a SunnyWebBox
            for key in self._items[host].keys():

                # Check which key is iterating
                if key == 'udp' or key == 'password':
                    continue

                elif key == 'OVERVIEW':
                    # Get the overview data from SunnyWebBox
                    overviewData = swb.getPlantOverview()

                    for date in overviewData:
                        # Check if date is needed
                        if date['name'] in self._items[host][key].keys():
                            # Get the item
                            item = self._items[host][key][date['name']]
                            # Parse value to type of the item
                            value = self._parseItemValue(date['value'], item)
                            # Send values to receiver (i.e. a visualisation)
                            item(value, 'SMAWB', host, key)

                else:
                    # Get processdata-channels from SunnyWebBox
                    channels = swb.getProcessDataChannels(key)
                    # Get processdata from SunnyWebBox
                    data = swb.getProcessData([{'key': key, 'channels': channels}])

                    # Get parameter-channels from SunnyWebBox
                    channels = swb.getParameterChannels(key)
                    # Get parameters from SunnyWebBox and merge result with process data
                    data[key] = data[key] + swb.getParameter([{'key': key, 'channels': channels}])[key]

                    for date in data[key]:
                        # Check if date is needed
                        if date['name'] in self._items[host][key].keys():
                            # Get the item
                            item = self._items[host][key][date['name']]
                            # Parse value to type of the item
                            value = self._parseItemValue(date['value'], item)
                            # Send values to receiver (i.e. a visualisation)
                            item(value, 'SMAWB', host, key)

    def _parseItemValue(self, parseValue, item):
        value = None

        if item._type == 'num':
            value = float(parseValue)
        elif item._type == 'bool':
            value = bool(parseValue)
        else:
            value = str(parseValue)

        return value

    def parse_item(self, item):
        # Build the following structure from informations out of the
        # items configuration file:
        #
        # [web-box-ip]
        #     [inverter-of-webbox]
        #         [data-field-of-inverter]
        #             item
        #         [data-field-of-inverter]
        #             item
        # [web-box-ip]
        #     ...

        # Parse just the parent-items wich define the 'smawb_host'
        # and/or 'smawb_password' attribute
        if 'smawb_host' in item.conf:

            # Get the host-name/ip value from SunnyWebBox
            host = item.conf['smawb_host']

            logger.debug("WebBox %s (%s) in items.conf found!" % (item, host))

            # Create new inverter dictionary if this SunnyWebBox was
            # not found before
            if host not in self._items.keys():
                self._items[host] = dict()

            # Try to get the password from parent-item
            # (else no password will be used)
            if 'smawb_password' in item.conf:
                self._items[host]['password'] = int(item.conf['smawb_password'])
            else:
                self._items[host]['password'] = ""

            # Try to get the UDP-flag from parent-item
            # (else HTTP will be used)
            if 'smawb_udp' in item.conf:
                self._items[host]['udp'] = bool(item.conf['smawb_udp'])
            else:
                self._items[host]['udp'] = False

            # Try to get a list of inverters wich are managed from a SunnyWebBox
            inverterList = self._sh.find_children(item, 'smawb_key')

            # Iterate over all found inverters
            for inverter in inverterList:

                # Get the key value (i.e. serial number) of the inverter
                key = inverter.conf['smawb_key']

                logger.debug("Inverter %s (%s) in items.conf found!" % (inverter, key))

                # Save all items of an inverter if this inverter was not found before
                if key not in self._items[host].keys():

                    # Try to get a list of all data-fields of the inverter
                    self._items[host][key] = dict()
                    fields = self._sh.find_children(inverter, 'smawb_data')

                    for field in fields:

                        # Get the data field name (channel) of the data field
                        channel = field.conf['smawb_data']

                        # Save the item wich corresponds to a field
                        self._items[host][key][channel] = field

                        logger.debug("    %s of is field in %s" % (channel, inverter))

        return None

