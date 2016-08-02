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
import base64
import json
import binascii
import urllib.request, urllib.error, urllib.parse
from io import StringIO
from Crypto.Cipher import AES
from lib.model.smartplugin import SmartPlugin

logger = logging.getLogger('')


class Buderus(SmartPlugin):
    PLUGIN_VERSION = "1.0.0"
    ALLOW_MULTIINSTANCE = False
    BS = AES.block_size
    INTERRUPT = '\u0001'
    PAD = '\u0000'

    def __init__(self, smarthome, host, key, cycle=900):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Init Buderus")
        self.__ua = "TeleHeater/2.2.3"
        self.__content_type = "application/json"
        self._sh = smarthome
        self._host = host
        self._key = binascii.unhexlify(key)
        self._ids = {}
        self.opener = urllib.request.build_opener()
        self.opener.addheaders = [('User-agent', self.__ua), ('Accept', self.__content_type)]
        self._sh.scheduler.add('Buderus', self._cycle, cycle=int(cycle))

    def _decrypt(self, enc):
        decobj = AES.new(self._key, AES.MODE_ECB)
        data = decobj.decrypt(base64.b64decode(enc))
        data = data.rstrip(self.PAD.encode()).rstrip(self.INTERRUPT.encode())
        return data

    def _encrypt(self, plain):
        plain = plain + (AES.block_size - len(plain) % self.BS) * self.PAD
        encobj = AES.new(self._key, AES.MODE_ECB)
        data = encobj.encrypt(plain)
        self.logger.debug("Buderus encrypted data: {} -- Base64 encoded: {}".format(data, base64.b64encode(data)))
        return base64.b64encode(data)

    def _get_data(self, path):
        try:
            url = 'http://' + self._host + path
            self.logger.debug("Buderus fetching data from {}".format(path))
            resp = self.opener.open(url)
            plain = self._decrypt(resp.read())
            self.logger.debug("Buderus data received from {}: {}".format(url, plain))
            return plain
        except Exception as e:
            self.logger.error("Buderus error happened at {}: {}".format(url, e))
            return None

    def _set_data(self, path, data):
        try:
            url = 'http://' + self._host + path
            self.logger.info("Buderus setting value for {}".format(path))
            headers = {"User-Agent": self.__ua, "Content-Type": self.__content_type}
            request = urllib.request.Request(url, data=data, headers=headers, method='PUT')
            req = urllib.request.urlopen(request)
            self.logger.info("Buderus returned {}: {}".format(req.status, req.reason))
            if not req.status == 204:
                self.logger.debug(req.read())
        except Exception as e:
            self.logger.error("Buderus error happened at {}: {}".format(url, e))
            return None

    def _get_json(self, data):
        try:
            j = json.load(StringIO(data.decode()))
            return j
        except Exception as e:
            self.logger.error("Buderus error happened while reading JSON data {}: {}".format(data, e))
            return False

    def _json_encode(self, value):
        d = {"value": value}
        return json.dumps([d])

    def _get_value(self, j):
        return j['value']

    def _get_type(self, j):
        return j['type']

    def _get_writeable(self, j):
        if j['writeable'] == 1:
            return True
        else:
            return False

    def _get_allowed_values(self, j, value_type):
        if value_type == "stringValue":
            try:
                return j['allowedValues']
            except:
                return None
        elif value_type == "floatValue":
            return {"minValue": j['minValue'], "maxValue": j['maxValue']}

    def _submit_data(self, item, id):
        self.logger.info("Buderus SETTING {} to {}".format(item, item()))
        payload = self._json_encode(item())
        self.logger.debug(payload)
        req = self._set_data(id, self._encrypt(str(payload)))

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def _cycle(self):
        self.logger.info("Buderus fetching data...")
        for id, item in self._ids.items():
            plain = self._get_data(id)
            data = self._get_json(plain)
            item(self._get_value(data), "Buderus")
        self.logger.info("Buderus fetching data done.")

    def parse_item(self, item):
        if "km_id" in item.conf:
            id = item.conf['km_id']
            self._ids[id] = item
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != "Buderus":
            id = item.conf['km_id']
            plain = self._get_data(id)
            data = self._get_json(plain)
            if self._get_writeable(data):
                value_type = self._get_type(data)
                allowed_values = self._get_allowed_values(data, value_type)
                if value_type == "stringValue" and item() in allowed_values or not allowed_values:
                    self._submit_data(item, id)
                    return
                elif value_type == "floatValue" and item() >= allowed_values['minValue'] and item() <= allowed_values[
                    'maxValue']:
                    self._submit_data(item, id)
                    return
                else:
                    self.logger.error("Buderus value {} not allowed [{}]".format(item(), allowed_values))
                    item(item.prev_value(), "Buderus")
            else:
                self.logger.error("Buderus item {} not writeable!".format(item))
                item(item.prev_value(), "Buderus")
