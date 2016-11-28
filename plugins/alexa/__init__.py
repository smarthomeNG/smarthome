#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016 Kai Meder <kai@meder.info>
#########################################################################
#  This file is part of SmartHomeNG.
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
#########################################################################

import logging
import socket
import json
from lib.model.smartplugin import SmartPlugin

from .devices import AlexaDevices
from .device import AlexaDevice
from .actions import AlexaActions
from .service import AlexaService

from . import actions_turn
from . import actions_temperature
from . import actions_percentage

class Alexa(SmartPlugin):
    PLUGIN_VERSION = "1.0.0"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, sh, service_host='0.0.0.0', service_port=9000):
        self.logger = logging.getLogger(__name__)
        self.sh = sh
        self.devices = AlexaDevices()
        self.actions = AlexaActions(self.sh, self.logger, self.devices)
        self.service = AlexaService(self.sh, self.logger, self.PLUGIN_VERSION, self.devices, self.actions, service_host, service_port)

    def run(self):
        self.service.start()
        self.alive = True

    def stop(self):
        self.service.stop()
        self.alive = False

    def parse_item(self, item):
        # item's supported alexa-actions, space-separated
        if 'alexa_actions' in item.conf:
            action_names = map(str.strip, item.conf['alexa_actions'].split(' '))
            self.logger.debug("Alexa: {}-actions = {}".format(item.id(), action_names))
            for action_name in action_names:
                if self.actions.by_name(action_name) is None:
                    self.logger.error("Alexa: invalid alexa action '{}' specified in item {}, ignoring item".format(action_name, item.id()))
                    return None
        else:
            return None

        # item's friendly name for alexa, fallback to normal item.name
        if 'alexa_name' in item.conf:
            name = item.conf['alexa_name']
        elif actions and name in item.conf and item.conf['name']:
            name = item.conf['name']
        elif actions:
            self.logger.error("Alexa: neither `alexa_name` nor `name` specified for item {}, ignoring item".format(item.id()))
            return None
        else:
            return None
        self.logger.debug("Alexa: {}-name = {}".format(item.id(), name))

        # optional explicit device-identifier (instead of deducing it from above alexa-name)
        if 'alexa_device' in item.conf:
            device_id = item.conf['alexa_device']
        else:
            device_id = AlexaDevice.create_id_from_name(name)
        self.logger.debug("Alexa: {}-device = {}".format(item.id(), device_id))

        # create device if not yet existing
        if not self.devices.exists(device_id):
            self.devices.put( AlexaDevice(device_id, name) )

        # register all supported actions of this item with the device
        device = self.devices.get(device_id)
        for action_name in action_names:
            device.add_action(action_name, item)

        # item's optional friendly description for alexa
        if 'alexa_description' in item.conf:
            device.set_description( item.conf['alexa_description'].strip() )

        self.logger.info("Alexa: item {} supports actions {} as device {}".format(item.id(), action_names, device_id))
        return None

    def _update_values(self):
        return None
