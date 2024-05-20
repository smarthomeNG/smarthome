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

  - Umrechnungen der folgenden Maßeinheiten für Längen / Entfernungenn:

    - meter   - Meter
    - miles   - Meilen
    - nm      - Nautische Meilen

  - Umrechnungen der folgenden Maßeinheiten für Temperaturen:

    - °F   - Grad Fahrenheit
    - °C   - Grad Celsius

  - weitere Umrechnungen

    - Grad zu Himmelsrichtung

"""

import logging

from lib.translation import translate

_logger = logging.getLogger('lib.env')


_mile = 1609.344       # 1 mile is 1609.344 meters long
_nautical_mile = 1852  # 1 nm is 1852 meters long


"""
Umrechnungen von Geschwindigkeiten  (m/s, km/h, mph, Knoten, mps, Bft)

  https://www.einheiten-umrechnen.de
"""

def kn_to_kmh(speed: float) -> float:
    """
    Umrechnung Knoten (nautische Meilen pro Stunde) in Kilometer pro Stunde

    :param speed: Geschwindigkeit in Knoten
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error("kn_to_kmh: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed * _nautical_mile


def kmh_to_kn(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Knoten (nautische Meilen pro Stunde)

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in Knoten
    """
    if not isinstance(speed,(int, float)):
        _logger.error("kmh_to_kn: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed / _nautical_mile


def ms_to_kmh(speed: float) -> float:
    """
    Umrechnung Meter pro Sekunde in Kilometer pro Stunde

    :param speed: Geschwindigkeit in m/s
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error("ms_to_kmh: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed * 3.6


def kmh_to_ms(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Meter pro Sekunde

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in m/s
    """
    if not isinstance(speed,(int, float)):
        _logger.error("kmh_to_ms: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed / 3.6


def mps_to_kmh(speed: float) -> float:
    """
    Umrechnung Miles per Second in Kilometer pro Stunde

    :param speed: Geschwindigkeit in mps
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error("mps_to_kmh: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed * 3.6 * _mile


def kmh_to_mps(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Miles per Second

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in mps
    """
    if not isinstance(speed,(int, float)):
        _logger.error("kmh_to_mps: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed / 3.6 / _mile


def mph_to_kmh(speed: float) -> float:
    """
    Umrechnung Miles per Hour in Kilometer pro Stunde

    :param speed: Geschwindigkeit in mph
    :return: Geschwindigkeit in km/h
    """
    if not isinstance(speed,(int, float)):
        _logger.error("mph_to_kmh: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed * _mile / 1000


def kmh_to_mph(speed: float) -> float:
    """
    Umrechnung Kilometer pro Stunde in Miles per Hour

    :param speed: Geschwindigkeit in km/h
    :return: Geschwindigkeit in mph
    """
    if not isinstance(speed,(int, float)):
        _logger.error("kmh_to_mph: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return speed / _mile * 1000


def ms_to_bft(speed: float) -> int:
    """
    Umrechnung Windgeschwindigkeit von Meter pro Sekunde in Beaufort

    Beaufort gibt die Windgeschwindigkeit durch eine Zahl zwischen 0 und 12 an

    :param speed: Windgeschwindigkeit in m/s
    :return: Windgeschwindigkeit in bft
    """
    if not isinstance(speed,(int, float)):
        _logger.error("ms_to_bft: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
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
        _logger.error("kmh_to_bft: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(speed)}))
        return -1

    return ms_to_bft(kmh_to_ms(speed))


def bft_to_text(bft: int, language: str='de') -> str:
    """
    Umwandlung Windgeschwindigkeit in bft in beschreibenden Text

    :param bft: Wind speed in beaufort (bft)
    :return: Text Beschreibung der Windgeschwindigkeit
    """

    if not isinstance(bft,(int, float)):
        _logger.error("bft_to_text: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(bft)}))
        return ''

    bft = int(bft)
    if (bft < 0) or (bft > 12):
        _logger.error("bft_to_text: " + translate("Beaufort is out of scale: '{bft}'", {'bft': bft}))
        return ''

    return translate("bft_"+str(bft))


"""
Umrechnung von Längen / Entfernungen
"""

def miles_to_meter(distance):
    """
    Umterchnung Meilen zu Metern

    :param distance: Strecke in Meilen
    :return: Strecke in Metern
    """
    if not isinstance(distance,(int, float)):
        _logger.error("miles_to_meter: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(distance)}))
        return -1

    return miles * _mile


def nauticalmiles_to_meter(distance):
    """
    Umterchnung nautische Meilen zu Metern

    :param distance: Strecke in nautischen Meilen
    :return: Strecke in Metern
    """
    if not isinstance(distance,(int, float)):
        _logger.error("nauticalmiles_to_meter: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(distance)}))
        return -1

    return miles * _nautical_mile


def meter_to_miles(distance):
    """
    Umterchnung Meter zu Meilen

    :param distance: Strecke in Metern
    :return: Strecke in Meilen
    """
    if not isinstance(distance,(int, float)):
        _logger.error("meter_to_miles: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(distance)}))
        return -1

    return meter / _mile


def meter_to_nauticalmiles(distance):
    """
    Umterchnung Meter zu nautische Meilen

    :param distance: Strecke in Metern
    :return: Strecke in nautischen Meilen
    """
    if not isinstance(distance,(int, float)):
        _logger.error("meter_to_nauticalmiles: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(distance)}))
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
        _logger.error("f_to_c: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(grad)}))
        return -999

    return (grad - 32) * 5 / 9


def c_to_f(grad: float) -> float:
    """
    Umrechnung von Grad Celsius in Grad Fahrenheit

    :param grad: Temperatur in °C
    :return: Temperatur in °F
    """
    if not isinstance(grad,(int, float)):
        _logger.error("c_to_f: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(grad)}))
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
    if deg is None:
        return '?'

    if not isinstance(deg,(int, float)):
        _logger.error("degrees_to_direction_8: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(deg)}))
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
    if deg is None:
        return '?'

    if not isinstance(deg,(int, float)):
        _logger.error("degrees_to_direction_16: " + translate("Parameter must be of type float or int but is of type {typ}", {'typ': type(deg)}))
        return ''

    direction_array = ['N', 'NNO', 'NO', 'ONO', 'O', 'OSO', 'SO', 'SSO', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

    index = int( (deg % 360 + 11.25) / 22.5)
    return direction_array[index]


from typing import Union

# Ab Python 3.10 auch: def location_name(lat: float | str, lon: float | str) -> str:
def location_name(lat: Union[float, str], lon: Union[float, str]) -> str:
    """
    Lokationsname (Stadt, Stadtteil oder Ort) einer Lokation, die über Latitude und Longitude gewählt wird.
    Die Informationen werden von OpenWeatherMap abgerufen.

    :param lat: Latitude
    :param lon: Longitude
    :return: Lokationsname
    """

    import requests

    # api documentation: https://nominatim.org/release-docs/develop/api/Reverse/
    request_str = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"

    try:
        response = requests.get(request_str)
    except Exception as e:
        _logger.warning("location_name: " + translate("Exception when sending GET request: {e}", {'e': e}))
        return ''

    if response.ok:
        try:
            json_obj = response.json()
        except Exception as e:
            _logger.warning("location_name: " + translate("Response '{response}' is not in valid json format: {e}", {'response': response, 'e': e}))
            return ''
    else:
        _logger.warning(f"location_name: openstreetmap.org responded with '{response.status_code}'")
        return ''

#    if response.status_code >= 500:
#        _logger.warning(f"location_name: {location_name(response.status_code)}")
#        return ''

    if json_obj.get('address', None) is None:
        result = ''
        _logger.notice(f"No 'address' in json response '{json_obj}' for request '{request_str}'")
    else:
        if json_obj['address'].get('city', None) is not None:
            result = json_obj['address']['city']
        elif json_obj['address'].get('town', None) is not None:
            result = json_obj['address']['town']
        elif json_obj['address'].get('village', None) is not None:
            result = json_obj['address']['village']
        else:
            result = ''

    if  json_obj['address'].get('suburb', None) is not None:
        if result != '':
            result += ', '
        result += json_obj['address']['suburb']

    return result


def location_address(lat: Union[float, str], lon: Union[float, str]) -> dict:
    """
    Address-Information einer Lokation, die über Latitude und Longitude gewählt wird.
    Die Informationen werden von OpenWeatherMap abgerufen.

    :param lat: Latitude
    :param lon: Longitude
    :return: Address Information
    """

    import requests

    # api documentation: https://nominatim.org/release-docs/develop/api/Reverse/
    request_str = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=jsonv2"

    try:
        response = requests.get(request_str)
    except Exception as e:
        _logger.warning("location_name: " + translate("Exception when sending GET request: {e}", {'e': e}))
        return ''

    try:
        json_obj = response.json()
    except Exception as e:
        _logger.warning("location_name: " + translate("Response '{response}' is not in valid json format: {e}", {'response': response, 'e': e}))
        return ''

    if response.status_code >= 500:
        _logger.warning(f"location_name: {location_name(response.status_code)}")
        return ''

    #self._logger.notice(f"{json_obj['display_name']}")

    return json_obj['address']


