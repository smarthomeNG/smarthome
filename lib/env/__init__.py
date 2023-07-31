#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2023-       Martin Sinn                         m.sinn@gmx.de
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


"""
This library implements functions to handle environmental data in SmartHomeNG.
"""


class Env:

    _sh = None
    _logger = None

    # source for german descriptions https://www.smarthomeng.de/vom-winde-verweht
    _beaufort_descriptions_de = ["Windstille",
                                 "leiser Zug",
                                 "leichte Brise",
                                 "schwacher Wind",
                                 "mäßiger Wind",
                                 "frischer Wind",
                                 "starker Wind",
                                 "steifer Wind",
                                 "stürmischer Wind",
                                 "Sturm",
                                 "schwerer Sturm",
                                 "orkanartiger Sturm",
                                 "Orkan"]
    # source for english descriptions https://simple.wikipedia.org/wiki/Beaufort_scale
    _beaufort_descriptions_en = ["Calm",
                                 "Light air",
                                 "Light breeze",
                                 "Gentle breeze",
                                 "Moderate breeze",
                                 "Fresh breeze",
                                 "Strong breeze",
                                 "High wind",
                                 "Fresh Gale",
                                 "Strong Gale",
                                 "Storm",
                                 "Violent storm",
                                 "Hurricane-force"]



    def __init__(self, smarthome):

        self._sh = smarthome
        self._logger = smarthome._logger


    def mps_to_beaufort(self, speed_in_mps):
        """
        Convert wind speed from meters per second to beaufort

        :param speed_in_mps: wind speed in miles per second

        :return: Wind speed in beauford (Bft) - range from 0 - 12
        """
        try:
            # Origin of table: https://www.smarthomeng.de/vom-winde-verweht
            table = [
                (0.3, 0),
                (1.6, 1),
                (3.4, 2),
                (5.5, 3),
                (8.0, 4),
                (10.8, 5),
                (13.9, 6),
                (17.2, 7),
                (20.8, 8),
                (24.5, 9),
                (28.5, 10),
                (32.7, 11),
                (999, 12)]
            return min(filter(lambda x: x[0] >= speed_in_mps, table))[1]
        except ValueError:
            self._logger.error(f"Cannot translate wind-speed to beaufort-number, received: '{speed_in_mps}'")
            return None


    @staticmethod
    def kmh_to_beaufort(speed_in_kmh):
        """
        Convert wind speed from kilometers per hour to beaufort

        :param speed_in_kmh: wind speed in kilometers per hour
        :return: Wind speed in beauford (Bft) - range from 0 - 12
        """

        return mps_to_beaufort(kmh_to_mps(speed_in_kmh))


    def get_beaufort_description(self, speed_in_bft, sh=None):
        """
        Get description for windspeed in beaufort

        :param speed_in_bft: Wind speed in beauford (Bft) - range from 0 - 12
        :param sh:
        :return:
        """
        if speed_in_bft is None:
            self._logger.warning(f"speed_in_bft is given as None")
            return None
        if type(speed_in_bft) is not int:
            self._logger.error(
                f"speed_in_bft is not given as int: '{speed_in_bft}'")
            return None
        if (speed_in_bft < 0) or (speed_in_bft > 12):
            self._logger.error(
                f"speed_in_bft is out of scale: '{speed_in_bft}'")
            return None

        if sh is None or sh.get_defaultlanguage() == 'de':
            return self._beaufort_descriptions_de[speed_in_bft]
        return self._beaufort_descriptions_en[speed_in_bft]


    @staticmethod
    def mps_to_kmh(speed_in_mps):
        """
        Umterchnung m/s in km/h

        :param speed_in_mps:
        :return:
        """
        return speed_in_mps * 3.6


    @staticmethod
    def kmh_to_mps(speed_in_kmh):
        """
        Umterchnung km/h in m/s

        :param speed_in_mps:
        :return:
        """
        return speed_in_kmh / 3.6


    @staticmethod
    def kn_to_kmh(speed_in_kn):
        """
        Umrechnung Knoten (nm/h) in km/h

        :param speed_in_kn:
        :return:
        """
        return speed_in_kn * 1.852


    @staticmethod
    def kmh_to_kn(speed_in_kmh):
        """
        Umrechnung km/h in Knoten (nm/h)

        :param speed_in_kmh:
        :return:
        """
        return speed_in_kmh / 1.852





    @staticmethod
    def get_wind_direction8(deg):

        direction_array = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW', 'N']

        index = int( (deg % 360 + 22.5) / 45)
        return direction_array[index]


    @staticmethod
    def get_wind_direction16(deg):

        direction_array = ['N', 'NNO', 'NO', 'ONO', 'O', 'OSO', 'SO', 'SSO', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

        index = int( (deg % 360 + 11.25) / 22.5)
        return direction_array[index]





    def get_location_name(self, lat=None, lon=None):

        import requests

        if lat is None:
            lat = self._sh._lat
        if lon is None:
            lon = self._sh._lon

        if lat == 0 or lon == 0:
            self._logger.debug(f"lat or lon are zero, not sending request: {lat=}, {lon=}")
            return

        # api documentation: https://nominatim.org/release-docs/develop/api/Reverse/
        request_str = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"

        try:
            response = requests.get(request_str)
        except Exception as e:
            self._logger.warning(f"get_location_name: Exception when sending GET request: {e}")
            return

        try:
            json_obj = response.json()
        except Exception as e:
            self._logger.warning(f"get_location_name: Response '{response}' is no valid json format: {e}")
            return ''

        if response.status_code >= 500:
            self._logger.warning(f"get_location_name: {self.get_location_name(response.status_code)}")
            return ''

        #self._logger.notice(f"{json_obj['display_name']}")
        #self._logger.notice(f"{json_obj['address']}")
        return json_obj['address']['suburb']


