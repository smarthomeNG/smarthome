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
Diese lib implementiert Funktionen zum Umgang mit Environment Daten in SmartHomeNG.

Hierzu gehören

  - Umrechnungen der folgenden Maßeinheiten für Geschwindigkeiten:

    - mps  - Miles Per Second
    - mph
    - km/h - Kilometer pro Stunde (kmh)
    - m/s  - Meter je Sekunde (ms)
    - nm/h - Nautical Miles per Hour
    - kn   - Knoten (1 nm pro Stunde)
    - bft  - Beaufort

  - Umrechnungen der folgenden Maßeinheiten für Temperaturen:

    - °F   - Grad Fahrenheit
    - °C   - Grad Celsius


  https://www.einheiten-umrechnen.de

"""

import logging

_logger = logging.getLogger('lib.env')


_mile = 1609.344       # 1 mile is 1609.344 meters long
_nautical_mile = 1852  # 1 nm is 1852 meters long


"""
Umrechnungen von Geschwindigkeiten  (m/s, km/h, mph, Knoten, mps, Bft)
"""

def kn_to_kmh(speed: float) -> float:
    """
    Umrechnung Knoten (nautische Meilen pro Stunde) in Kilometer pro Stunde

    :param speed: Geschwindigkeit in Knoten
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"kn_to_kmh: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed * _nautical_mile


def kmh_to_kn(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Knoten (nautische Meilen pro Stunde)

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in Knoten
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"kmh_to_kn: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed / _nautical_mile


def ms_to_kmh(speed: float) -> float:
    """
    Umrechnung Meter pro Sekunde in Kilometer pro Stunde

    :param speed: Geschwindigkeit in m/s
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"ms_to_kmh: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed * 3.6


def kmh_to_ms(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Meter pro Sekunde

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in m/s
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"kmh_to_ms: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed / 3.6


def mps_to_kmh(speed: float) -> float:
    """
    Umrechnung Miles per Second in Kilometer pro Stunde

    :param speed: Geschwindigkeit in mps
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"mps_to_kmh: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed * 3.6 * _mile


def kmh_to_mps(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Miles per Second

    :param speed:
    :return:
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"kmh_to_mps: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return speed / 3.6 / _mile


def ms_to_bft(speed: float) -> int:
    """
    Umrechnung Windgeschwindigkeit von Meter pro Sekunde in Beaufort

    Beaufort gibt die Windgeschwindigkeit durch eine Zahl zwischen 0 und 12 an

    :param speed: Windgeschwindigkeit in m/s
    :return: Windgeschwindigkeit in bft
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"ms_to_bft: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

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
    return min(filter(lambda x: x[0] >= speed, table))[1]


def kmh_to_bft(speed: float) -> int:
    """
    Umrechnung Windgeschwindigkeit von Kilometer pro Stunde in Beaufort

    Beaufort gibt die Windgeschwindigkeit durch eine Zahl zwischen 0 und 12 an

    :param speed: Windgeschwindigkeit in km/h
    :return: Windgeschwindigkeit in bft
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"kmh_to_bft: Parameter must be of type float or int but is of type {type(speed)}")
        return -1

    return ms_to_bft(kmh_to_ms(speed))


def bft_to_text(bft: int, language: str='de') -> str:
    """
    Umwandlung Windgeschwindigkeit in bft in beschreibenden Text

    :param bft: Wind speed in beaufort (bft)
    :return: Text Beschreibung der Windgeschwindigkeit
    """

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

    if not isinstance(bft,(int)):
        _logger.error(f"bft_to_text: Parameter must be of type int but is of type {type(bft)}")
        return ''

    if (bft < 0) or (bft > 12):
        _logger.error(f"speed_in_bft is out of scale: '{bft}'")
        return ''

    if language.lower() == 'de':
        return _beaufort_descriptions_de[bft]
    return _beaufort_descriptions_en[bft]


"""
Umrechnung von Längen / Entfernungen
"""

def miles_to_meter(miles):
    """
    Umterchnung Meilen zu Metern

    :param miles:
    :return:
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"miles_to_meter: Parameter must be of type float or int but is of type {type(miles)}")
        return -1

    return miles * _mile


def nauticalmiles_to_meter(miles):
    """
    Umterchnung nautische Meilen zu Metern

    :param miles:
    :return:
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"nauticalmiles_to_meter: Parameter must be of type float or int but is of type {type(miles)}")
        return -1

    return miles * _nautical_mile


def meter_to_miles(meter):
    """
    Umterchnung Meter zu Meilen

    :param meter:
    :return:
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"meter_to_miles: Parameter must be of type float or int but is of type {type(meter)}")
        return -1

    return meter / _mile


def meter_to_nauticalmiles(meter):
    """
    Umterchnung Meter zu nautische Meilen

    :param meter:
    :return:
    """
    if not isinstance(speed,(int, float)):
        _logger.error(f"meter_to_nauticalmiles: Parameter must be of type float or int but is of type {type(meter)}")
        return -1

    return meter / _nautical_mile


"""
Umrechnung von Temperaturen
"""

def f_to_c(grad: float) -> float:
    """
    Umrechnung von Grad Fahrenheit in Grad Celsius
    :param grad: Temperatur in °F
    :return: Temperatur in °C
    """
    if not isinstance(grad,(int, float)):
        _logger.error(f"f_to_c: Parameter must be of type float or int but is of type {type(grad)}")
        return -999

    return (grad - 32) * 5 / 9


def c_to_f(grad: float) -> float:
    """
    Umrechnung von Grad Celsius in Grad Fahrenheit
    :param grad: Temperatur in °C
    :return: Temperatur in °F
    """
    if not isinstance(grad,(int, float)):
        _logger.error(f"c_to_f: Parameter must be of type float or int but is of type {type(grad)}")
        return -999

    return grad * 9 / 5 + 32


"""
Die folgenden Funktionen dienen der Umrechnung einer Himmelsrichtung von Grad in die gebräuchlichen Abkürzungen
"""

def degrees_to_direction_8(deg: float) -> str:
    """
    Umrechnung Gradzahl in Himmelsrichtung (Abkürzung)

    Diese Funktion teilt die Himmelsrichtungen in 8 Sektoren

    :param deg: Kompass Gradzahl
    :return: Himmelsrichtung (Abkürzung)
    """
    if not isinstance(deg,(int, float)):
        _logger.error(f"degrees_to_direction_8: Parameter must be of type float or int but is of type {type(deg)}")
        return ''

    direction_array = ['N', 'NO', 'O', 'SO', 'S', 'SW', 'W', 'NW', 'N']

    index = int( (deg % 360 + 22.5) / 45)
    return direction_array[index]


def degrees_to_direction_16(deg: float) -> str:
    """
    Umrechnung Gradzahl in Himmelsrichtung (Abkürzung)

    Diese Funktion teilt die Himmelsrichtungen in 16 Sektoren

    :param deg: Kompass Gradzahl
    :return: Himmelsrichtung (Abkürzung)
    """
    if not isinstance(deg,(int, float)):
        _logger.error(f"degrees_to_direction_8: Parameter must be of type float or int but is of type {type(deg)}")
        return ''

    direction_array = ['N', 'NNO', 'NO', 'ONO', 'O', 'OSO', 'SO', 'SSO', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

    index = int( (deg % 360 + 11.25) / 22.5)
    return direction_array[index]



def location_name(lat:float, lon:float) -> str:

    import requests

    #if not isinstance(lat,(int, float)) or not isinstance(lon,(int, float)):
    #    _logger.error(f"location_name: Parameters must be of type float or int but are of type {type(lat)} and {type(lon)}")
    #    return ''

    if lat == 0 or lon == 0:
        _logger.warning(f"lat or lon are zero, not sending request: {lat=}, {lon=}")
        return ''

    # api documentation: https://nominatim.org/release-docs/develop/api/Reverse/
    request_str = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"

    try:
        response = requests.get(request_str)
    except Exception as e:
        _logger.warning(f"location_name: Exception when sending GET request: {e}")
        return ''

    try:
        json_obj = response.json()
    except Exception as e:
        _logger.warning(f"location_name: Response '{response}' is no valid json format: {e}")
        return ''

    if response.status_code >= 500:
        _logger.warning(f"get_location_name: {location_name(response.status_code)}")
        return ''

    #self._logger.notice(f"{json_obj['display_name']}")
    #self._logger.notice(f"{json_obj['address']}")
    if  json_obj['address'].get('suberb', None) is None:
        _logger.warning(f"location_name: no suburb information found for location (lat={lat}, lon={lon}) in address data: {json_obj['address']}")
        return ''

    return json_obj['address']['suburb']


