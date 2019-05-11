#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 Marcus Popp                          marcus@popp.mx
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################
# Anpassungen 2016 Michael Würtenberger
# Error Item für Verbindungsfehler bei fetch_url

"""
This library contains the Tools-class from the original smarthome.py

:Note: These functions **should be concidered deprecated**. New helper-functions are going to be implemented in the utils.lib.

"""

import base64
import datetime
import http.client
import logging
import math
import subprocess
import time

logger = logging.getLogger(__name__)


class Tools():

    def __init__(self):
        self._start = datetime.datetime.now()

    def ping(self, host):
        try:
            retcode = subprocess.call("ping -W 1 -c 1 " + host + " > /dev/null", shell=True)
            if retcode == 0:
                return True
            else:
                return False
        except OSError:
            return False

    def dewpoint(self, t, rf):
        log = math.log((rf + 0.01) / 100)  # + 0.01 to 'cast' float
        return round((241.2 * log + 4222.03716 * t / (241.2 + t)) / (17.5043 - log - 17.5043 * t / (241.2 + t)), 2)

    def dt2js(self, dt):
        return time.mktime(dt.timetuple()) * 1000 + int(dt.microsecond / 1000)

    def dt2ts(self, dt):
        return time.mktime(dt.timetuple())

    def fetch_url(self, url, username=None, password=None, timeout=2, warn_no_connect=1, method = 'GET', body=None, errorItem = None):
        connErrors = ['Host is down', 'timed out', '[Errno 113] No route to host']
        headers = {'Accept': 'text/plain'}
        plain = True
        if url.startswith('https'):
            plain = False
        lurl = url.split('/')
        host = lurl[2]
        purl = '/' + '/'.join(lurl[3:])
        if plain:
            conn = http.client.HTTPConnection(host, timeout=timeout)
        else:
            conn = http.client.HTTPSConnection(host, timeout=timeout)
        if username and password:
            headers['Authorization'] = ('Basic '.encode() + base64.b64encode((username + ':' + password).encode()))
        try:
            conn.request(method, purl, body, headers)
        except Exception as e:
            if format(e) in connErrors:
                # diese fehler bekommen einen status, der in der visu oder sonst genutzt werden kann
                if errorItem != None:
                    errorItem(True,'_fetch_url')
            if warn_no_connect == 1:
                logger.warning("Problem fetching {0}: {1}".format(url, e))
            conn.close()
            return False
        resp = conn.getresponse()
        if resp.status == 200:
            content = resp.read()
        else:
            logger.warning("Problem fetching {0}: {1} {2}".format(url, resp.status, resp.reason))
            content = False
        conn.close()
        return content

    def rel2abs(self, t, rf):
        t += 273.15
        if rf > 1:
            rf /= 100
        sat = 611.0 * math.exp(-2.5e6 * 18.0160 / 8.31432E3 * (1.0 / t - 1.0 / 273.16))
        mix = 18.0160 / 28.9660 * rf * sat / (100000 - rf * sat)
        rhov = 100000 / (287.0 * (1 - mix) + 462.0 * mix) / t
        return mix * rhov * 1000
    
    def abs2rel(self,t,ah):
        """
        Return the relative humidity from the absolute humidity (g/cm3) and temperature (Celsius)
        
        :param t: temperature in celsius
        :type t: float
        :param ah: absolute humidity (g/cm3)
        :type t: float
        
        :return: val = relative humidity (in percent)
        :rtype: dict
        """
        T=t+273.15
        ah=ah/1000
        sat_p=math.exp(77.3450 + 0.0057* T - 7235 / T) / math.pow(T,8.2   )
        sat_density=0.0022*sat_p/T
        rel=ah/sat_density*100
        return rel

    def runtime(self):
        return datetime.datetime.now() - self._start
