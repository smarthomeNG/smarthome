
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

from .device import AlexaDevices, AlexaDevice
from .action import AlexaActions
from .service import AlexaService

from . import actions_turn
from . import actions_temperature
from . import actions_percentage

class Alexa(SmartPlugin):
    PLUGIN_VERSION = "0.7.0"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, sh, service_host='0.0.0.0', service_port=9000):
        self.logger = logging.getLogger(__name__)
        self.sh = sh
        self.devices = AlexaDevices()
        self.actions = AlexaActions(self.sh, self.logger, self.devices)
        self.service = AlexaService(self.sh, self.logger, self.PLUGIN_VERSION, self.devices, self.actions, service_host, service_port)

    def run(self):
        self.validate_devices()
        self.service.start()
        self.alive = True

    def stop(self):
        self.service.stop()
        self.alive = False

    def parse_item(self, item):
        # device/appliance
        device_id = None
        if 'alexa_device' in item.conf:
            device_id = item.conf['alexa_device']

        # supported actions/directives
        action_names = None
        if 'alexa_actions' in item.conf:
            action_names = list( map(str.strip, item.conf['alexa_actions'].split(' ')) )
            self.logger.debug("Alexa: {}-actions = {}".format(item.id(), action_names))
            for action_name in action_names:
                if action_name and self.actions.by_name(action_name) is None:
                    self.logger.error("Alexa: invalid alexa action '{}' specified in item {}, ignoring item".format(action_name, item.id()))
                    return None

        # friendly name
        name = None
        name_is_explicit = None
        if 'alexa_name' in item.conf:
            name = item.conf['alexa_name']
            name_is_explicit = True
        elif action_names and 'name' in item.conf:
            name = item.conf['name']
            name_is_explicit = False

        # deduce device-id from name
        if name and not device_id:
            device_id = AlexaDevice.create_id_from_name(name)

        # skip this item if no device could be determined
        if device_id:
            self.logger.debug("Alexa: {}-device = {}".format(item.id(), device_id))
        else:
            return None # skip this item

        # create device if not yet existing
        if not self.devices.exists(device_id):
            self.devices.put( AlexaDevice(device_id) )

        device = self.devices.get(device_id)

        # friendly name
        if name and (not device.name or name_is_explicit):
            self.logger.debug("Alexa: {}-name = {}".format(item.id(), name))
            if device.name and device.name != name:
                self.logger.warning("Alexa: item {} is changing device-name of {} from '{}' to '{}'".format(item.id(), device_id, device.name, name))
            device.name = name

        # friendly description
        if 'alexa_description' in item.conf:
            descr = item.conf['alexa_description']
            self.logger.debug("Alexa: {}-description = {}".format(item.id(), descr))
            if device.description and device.description != descr:
                self.logger.warning("Alexa: item {} is changing device-description of {} from '{}' to '{}'".format(item.id(), device_id, device.description, descr))
            device.description = descr

        # register item-actions with the device
        if action_names:
            for action_name in action_names:
                device.register(action_name, item)
            self.logger.info("Alexa: item {} supports actions {} as device {}".format(item.id(), action_names, device_id, device.supported_actions()))

        return None

    def _update_values(self):
        return None

    def validate_devices(self):
        for device in self.devices.all():
            if not device.validate(self.logger):
                raise ValueError("Alexa: invalid device {}".format(device.id))
