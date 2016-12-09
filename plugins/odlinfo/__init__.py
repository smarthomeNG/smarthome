#!/usr/bin/env python3
#
#########################################################################
#  Copyright 2016 René Frieß                      rene.friess(a)gmail.com
#  Copyright of data provided by odlinfo.bfs.de API and retrieved by this
#  plugin see README.md
#  Version 1.1.1
#########################################################################
#  Free for non-commercial use
#
#  Plugin for the API of odlinfo.bfs.de, which allows to read values of
#  radioactive radiation within Germany.
#  This plugin only provides access to the API of ODLInfo and does not
#  modify that data, according to the ODLINFO Terms of Service.
#
#  For accessing the ODLINFO API you need a personal username and password.
#  For your own username and password register to the E-Mail provided in
#  https://odlinfo.bfs.de/DE/service/datenschnittstelle.html
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG (NG). If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import logging
import requests
from lib.model.smartplugin import SmartPlugin
from requests.auth import HTTPBasicAuth

class ODLInfo(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.1"
    _base_url = 'https://odlinfo.bfs.de/daten/json/stamm.json'

    def __init__(self, smarthome, user, password):
        """
        Initializes the plugin
        @param user: For accessing the ODLINFO API you need a personal username
        @param password: For accessing the ODLINFO API you need a personal password
        """
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self._user = user
        self._password = password
        self._keys = ['ort', 'kenn', 'plz', 'status', 'kid', 'hoehe', 'lon', 'lat', 'mw']
        self._session = requests.Session()

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def get_radiation_data_for_id(self, odlinfo_id):
        """
        Returns a dict of information for a radiation measurement station
        @param odlinfo_id: internal odlinfo_id
        """
        try:
            response = self._session.get(self._build_url(), auth=HTTPBasicAuth(self._user, self._password))

        except Exception as e:
            self.logger.error(
                "Exception when sending GET request for get_radiation_data_for_id: %s" % str(e))
            return
        json_obj = response.json()

        if json_obj[odlinfo_id]:
            self.logger.debug(json_obj[odlinfo_id])
            result_station = {}
            for key in self._keys:
                result_station[key] = json_obj[odlinfo_id][key]

        return result_station

    def get_radiation_data_for_ids(self, odlinfo_ids):
        """
        Returns an array of dicts of information for a radiation measurement stations
        @param odlinfo_ids: array if internal odlinfo_ids
        """
        result_stations = []
        try:
            response = self._session.get(self._build_url(), auth=HTTPBasicAuth(self._user, self._password))
        except Exception as e:
            self.logger.error(
                "Exception when sending GET request for get_radiation_data_for_ids: %s" % str(e))
            return
        json_obj = response.json()
        for odlinfo_id in odlinfo_ids:
            self.logger.debug(odlinfo_id)
            if json_obj[odlinfo_id]:
                self.logger.debug(json_obj[odlinfo_id])
                result_station = {}
                for key in self._keys:
                    result_station[key] = json_obj[odlinfo_id][key]
            result_stations.append(result_station)
        return result_stations

    def _build_url(self):
        """
        Builds a request url, method included for a later use vs other data files of ODLINFO
        @return: string of the url
        """
        url = (self._base_url)
        return url