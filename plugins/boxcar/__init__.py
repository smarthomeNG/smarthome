#!/usr/bin/env python3
# coding=utf-8
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
# Author    mode@gmx.co.uk
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
import urllib.request
import urllib.parse
import urllib.error
import http.client

# boxcar notifications
logger = logging.getLogger('Boxcar')


class Boxcar():
    _apiurl = 'boxcar.io'
    _headers = {"Content-type":
                "application/x-www-form-urlencoded", "Accept": "text/plain"}

    def __init__(self, smarthome, apikey=None, email=None, url=None):
        self.__set_path(apikey)
        self._email = email
        if url:
            self._apiurl = url

    def run(self):
        pass

    def stop(self):
        pass

    def __set_path(self, apikey):
        self._path = '/devices/providers/' + apikey + '/notifications'

    def __call__(self, sender='', message='', link_url=None, icon=None, email=None, apikey=None):
        data = {}
        if email:
            data['email'] = email[:1024]
        else:
            data['email'] = self._email[:1024]
        data['notification[from_screen_name]'] = sender[:1024]
        data['notification[message]'] = message[:1024]
        if link_url:
            data['notification[source_url]'] = link_url[:1024]
        if icon:
            data['notification[icon_url]'] = icon[:1024]
        if apikey:
            self.__set_path(apikey)

        try:
            conn = http.client.HTTPSConnection(self._apiurl)
            conn.request("POST", self._path,
                         urllib.parse.urlencode(data), self._headers)
            response = conn.getresponse()
            if response.status == 200:
                logger.info("Boxcar: Message %s %s successfully sent - %s %s" %
                            (sender, message, response.status, response.reason))
            else:
                logger.warning("Boxcar: Could not send message %s %s - %s %s" %
                               (sender, message, response.status, response.reason))
            conn.close()
            del(conn)
        except Exception as e:
            logger.warning(
                "Could not send boxcar notification: {0}. Error: {1}".format(message, e))
