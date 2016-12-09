#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2011 KNX-User-Forum e.V.           http://knx-user-forum.de/
#########################################################################
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
#########################################################################

import logging
import urllib.parse
import http.client

logger = logging.getLogger('NMA')


class NMA():
    _host = 'www.notifymyandroid.com'
    _api = '/publicapi/notify'

    def __init__(self, smarthome, apikey=None):
        self._apikey = apikey
        self._sh = smarthome

    def run(self):
        pass

    def stop(self):
        pass

    def __call__(self, event='', description='', priority=None, url=None, apikey=None, application='SmartHome'):
        data = {}
        headers = {'User-Agent': "SmartHomeNG", 'Content-Type': "application/x-www-form-urlencoded"}
        data['event'] = event[:1000].encode()
        data['description'] = description[:1000].encode()
        data['application'] = application[:256].encode()
        if apikey:
            data['apikey'] = apikey
        else:
            data['apikey'] = self._apikey
        if priority:
            data['priority'] = priority
        if url:
            data['url'] = url[:2000]
        try:
            conn = http.client.HTTPSConnection(self._host, timeout=4)
            conn.request("POST", self._api, urllib.parse.urlencode(data), headers)
            resp = conn.getresponse()
            conn.close()
            if (resp.status == 200):
                logger.debug("NMA returns: Notification submitted.")
            elif (resp.status == 400):
                logger.warning("NMA returns: The data supplied is in the wrong format, invalid length or null.")
            elif (resp.status == 401):
                logger.warning("NMA returns: None of the API keys provided were valid.")
            elif (resp.status == 402):
                logger.warning("NMA returns: Maximum number of API calls per hour exceeded.")
            elif (resp.status == 500):
                logger.warning("NMA returns: Internal server error. Please contact our support if the problem persists.")
            else:
                logger.error("NAME returns unknown HTTP status code = {0}".format(resp.status))
        except Exception as e:
            logger.warning("Could not send NMA notification: {0}. Error: {1}".format(event, e))
