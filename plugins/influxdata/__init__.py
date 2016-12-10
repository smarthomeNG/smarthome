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
import socket
from lib.model.smartplugin import SmartPlugin


class InfluxData(SmartPlugin):
    PLUGIN_VERSION = "1.0.0"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, smarthome, influx_host='localhost', influx_port=8089, influx_keyword='influx'):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Init InfluxData')
        self._sh = smarthome
        self.influx_host = influx_host
        self.influx_port = influx_port
        self.influx_keyword = influx_keyword
        self._items = []

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def udp(self, data):
        try:
            family, type, proto, canonname, sockaddr = socket.getaddrinfo(self.influx_host, self.influx_port)[0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data.encode(), (sockaddr[0], sockaddr[1]))
            sock.close()
            del sock
        except Exception as e:
            self.logger.warning(
                "InfluxData: Problem sending data to {}:{}: {}".format(self.influx_host, self.influx_port, e))
            pass
        else:
            self.logger.debug("InfluxData: Sending data to {}:{}: {}".format(self.influx_host, self.influx_port, data))

    def parse_item(self, item):
        if self.influx_keyword in item.conf:
            if item.type() not in ['num', 'bool']:
                self.logger.debug("InfluxData: only supports 'num' and 'bool' as types. Item: {} ".format(item.id()))
                return
            self._items.append(item)
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        message = "{},caller={},source={},dest={} value={}".format(item.id(), caller, source, dest, float(item()))
        self.udp(message)
        return None

    def _update_values(self):
        return None
