#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016 Raoul Thill                       raoul.thill@gmail.com
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
import json
import requests
import random
from lib.model.smartplugin import SmartPlugin


class Plex(SmartPlugin):
    PLUGIN_VERSION = "1.0.0"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, smarthome, displaytime=6000):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Init Plex notifications")
        self._sh = smarthome
        self._displayTime = int(displaytime)
        self._images = ["info", "error", "warning"]
        self._clients = []

    def run(self):
        pass

    def stop(self):
        pass

    def _push(self, host, data):
        try:
            res = requests.post(host,
                                headers={
                                    "User-Agent": "sh.py",
                                    "Content-Type": "application/json"},
                                timeout=4,
                                data=json.dumps(data),
                                )
            self.logger.debug(res)
            response = res.text
            del res
            self.logger.debug(response)
        except Exception as e:
            self.logger.exception(e)

    def notify(self, title, message, image="info"):
        if not image in self._images:
            self.logger.warn("Plex image must be: {}".format(", ".join(self._images)))
        else:
            data = {"jsonrpc": "2.0",
                    "id": random.randint(1, 99),
                    "method": "GUI.ShowNotification",
                    "params": {"title": title, "message": message, "image": image},
                    "displayTime": self._displayTime
                    }
            for host in self._clients:
                self.logger.debug("Plex sending push notification to host {}: {}".format(host, data))
                self._push(host, data)

    def parse_item(self, item):
        if 'plex_host' in item.conf:
            host = item.conf['plex_host']
            if 'plex_port' in item.conf:
                port = item.conf['plex_port']
            else:
                port = 3005
            self.logger.info("Plex found client {}".format(item))
            self._clients.append('http://' + host + ':' + str(port) + '/jsonrpc')
