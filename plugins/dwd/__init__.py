#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import csv
import ftplib
import socket
import re
import datetime
import dateutil.parser
import dateutil.tz
import dateutil.relativedelta
import xml.etree.cElementTree
import threading
from lib.model.smartplugin import SmartPlugin


class DWD(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.1"

    _dwd_host = 'ftp-outgoing2.dwd.de'
    _warning_cat = {}

    def __init__(self, smarthome, username, password=True):
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self._warnings_csv = smarthome.base_dir + '/plugins/dwd/warnings.csv'
        self._dwd_user = username
        self._dwd_password = password
        self.lock = threading.Lock()
        self.tz = dateutil.tz.gettz('Europe/Berlin')
        try:
            warnings = csv.reader(open(self._warnings_csv, "r", encoding='utf_8'), delimiter=';')
        except IOError as e:
            self.logger.error('Could not open warning catalog {}: {}'.format(self._warnings_csv, e))
        for row in warnings:
            self._warning_cat[int(row[0])] = {'summary': row[1], 'kind': row[2]}

    def _connect(self):
        # open ftp connection to dwd
        if not hasattr(self, '_ftp'):
            try:
                self._ftp = ftplib.FTP(self._dwd_host, self._dwd_user, self._dwd_password, timeout=1)
            except (socket.error, socket.gaierror) as e:
                self.logger.error('Could not connect to {}: {}'.format(self._dwd_host, e))
                self.ftp_quit()
            except ftplib.error_perm as e:
                self.logger.error('Could not login: {}'.format(e))
                self.ftp_quit()

    def run(self):
        self.alive = True

    def stop(self):
        self.ftp_quit()
        self.alive = False

    def ftp_quit(self):
        try:
            self._ftp.close()
        except Exception:
            pass
        if hasattr(self, '_ftp'):
            del(self._ftp)

    def parse_item(self, item):
        return None

    def parse_logic(self, logic):
        return None

    def _buffer_file(self, data):
        self._buffer.extend(data)

    def _retr_file(self, filename):
        self.lock.acquire()
        self._connect()
        self._buffer = bytearray()
        try:
            self._ftp.retrbinary("RETR {}".format(filename), self._buffer_file)
        except Exception as e:
            self.logger.info("problem fetching {0}: {1}".format(filename, e))
            del(self._buffer)
            self._buffer = bytearray()
            self.ftp_quit()
        self.lock.release()
        return self._buffer.decode('iso-8859-1')

    def _retr_list(self, dirname):
        self.lock.acquire()
        self._connect()
        try:
            filelist = self._ftp.nlst(dirname)
        except Exception:
            filelist = []
        finally:
            self.lock.release()
        return filelist

    def warnings(self, region, location):
        directory = 'gds/specials/alerts/txt'
        warnings = []
        filepath = "{0}/{1}/W*_{2}_*".format(directory, region, location)
        files = self._retr_list(filepath)
        for filename in files:
            fb = self._retr_file(filename)
            if fb == '':
                continue
            dates = re.findall(r"\d\d\.\d\d\.\d\d\d\d \d\d:\d\d", fb)
            now = datetime.datetime.now(self.tz)
            if len(dates) > 1:  # Entwarnungen haben nur ein Datum
                start = dateutil.parser.parse(dates[0], dayfirst=True)
                start = start.replace(tzinfo=self.tz)
                end = dateutil.parser.parse(dates[1], dayfirst=True)
                end = end.replace(tzinfo=self.tz)
                notice = dateutil.parser.parse(dates[2])
                notice = notice.replace(tzinfo=self.tz)
                if end > now:
                    area_splitter = re.compile(r'^\r\r\n', re.M)
                    area = area_splitter.split(fb)
                    code = int(re.findall(r"\d\d", area[0])[0])
                    desc = area[5].replace('\r\r\n', '').strip()
                    kind = self._warning_cat[code]['kind']
                    warnings.append({'start': start, 'end': end, 'kind': kind, 'notice': notice, 'desc': desc})
        return warnings

    def current(self, location):
        directory = 'gds/specials/observations/tables/germany'
        cleanr =re.compile('<.*?>') #clean html tags
        files = self._retr_list(directory)
        if files == []:
            return {}
        last = sorted(files)[-1]
        fb = self._retr_file(last)

        matchObj = re.findall(r'<tr>(.*?)</tr>', fb, re.M|re.I|re.S)
        if not matchObj is None:
            if len(matchObj) > 0:
                legend = re.sub(cleanr,'', matchObj[0])
                legend = list(filter(None, [s.strip() for s in legend.splitlines()]))  #filter empty lines

                fb = fb.splitlines()
                if len(fb) < 8:
                    self.logger.info("problem fetching {0}".format(last))
                    return {}
                header = fb[3] # index angepasst
                if "Messwerte" in header:
                    return {}
                date = re.findall(r"\d\d\.\d\d\.\d\d\d\d", header)[0].split('.')
                date = "{}-{}-{}".format(date[2], date[1], date[0])

                for element in matchObj:
                    if element.count(location):
                        data_string = re.sub(cleanr,'', element)
                        data = list(filter(None, [s.strip() for s in data_string.splitlines()]))   #filter empty lines
                        if len(data) == len(legend):
                            return dict(zip(legend, data))
                        else:
                            self.logger.error('Number of elements in legend does not match data {} : {}'.format(str(len(legend)), str(len(data))))
                
        return {}

    def forecast(self, region, location):
        path = 'gds/specials/forecasts/tables/germany/Daten_'
        frames = ['frueh', 'mittag', 'spaet', 'nacht', 'morgen_frueh', 'morgen_spaet', 'uebermorgen_frueh', 'uebermorgen_spaet', 'Tag4_frueh', 'Tag4_spaet']
        forecast = {}
        for frame in frames:
            filepath = "{0}{1}_{2}".format(path, region, frame)
            fb = self._retr_file(filepath)
            if fb == '':
                continue
            minute = 0
            if frame.count('frueh'):
                hour = 6
            elif frame == 'mittag':
                hour = 12
            elif frame == 'nacht':
                hour = 23
                minute = 59
            else:
                hour = 18
            for line in fb.splitlines():
                if line.count('Termin ist nicht mehr'):  # already past
                    date = self._sh.now().replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=self.tz)
                    forecast[date] = ['', '', '']
                    continue
                elif line.startswith('Vorhersage'):
                    header = line
                elif line.count(location):
                    if frame == 'nacht':
                        #header = re.sub(r"/\d\d?", '', header)
                        day, month, year = re.findall(r"\d\d\D\d\d\.\d\d\.\d\d\d\d", header)[0].split('.')  #31/01.06.2016
                        day1, day2 = day.split("/")
                        if day2 == "01":
                            if 1 < int(month) < 10:
                                month = "0%s"%str(int(month)-1)
                            elif int(month) == 1: #next day of night in new year, reset to last year
                                month = "12"
                                year = str(int(year)-1)
                            else:
                                month = str(int(month)-1)
                        day = day1
                    else:
                        header = re.sub(r"/\d\d?", '', header)
                        day, month, year = re.findall(r"\d\d\.\d\d\.\d\d\d\d", header)[0].split('.')
                    #self.logger.debug(day+" "+month+" "+year)
                    date = datetime.datetime(int(year), int(month), int(day), hour, tzinfo=self.tz)
                    if re.search("\d\d\/\d\d", header):
                        date = date + datetime.timedelta(days=-1)
                    space = re.compile(r'  +')
                    fc = space.split(line)
                    forecast[date] = fc[1:]
        return forecast

    def uvi(self, location):
        directory = 'gds/specials/alerts/health'
        forecast = {}
        for frame in ['12', '36', '60']:
            filename = "{0}/u_vindex{1}.xml".format(directory, frame)
            fb = self._retr_file(filename)
            try:
                year, month, day = re.findall(r"\d\d\d\d\-\d\d\-\d\d", fb)[0].split('-')
            except:
                continue
            date = datetime.datetime(int(year), int(month), int(day), 12, 0, 0, 0, tzinfo=self.tz)
            uv = re.findall(r"{}<\/tns:Ort>\n *<tns:Wert>([^<]+)".format(location), fb)
            if len(uv) == 1:
                forecast[date] = int(uv[0])
        return forecast

    def pollen(self, region):
        filename = 'gds/specials/alerts/health/s_b31fg.xml'
        filexml = self._retr_file(filename)
        if filexml == '':
            return {}
        fxp = xml.etree.cElementTree.fromstring(filexml)
        date = fxp.attrib['last_update'].split()[0].split('-')
        day0 = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), 12, 0, 0, 0, tzinfo=self.tz)
        day1 = day0 + dateutil.relativedelta.relativedelta(days=1)
        day2 = day0 + dateutil.relativedelta.relativedelta(days=2)
        forecast = {day0: {}, day1: {}, day2: {}}
        for reg in fxp.findall('region'):
            for preg in reg.findall('partregion'):
                if preg.attrib['name'] == region:
                    for kind in preg:
                        for day in kind:
                            value = day.text.replace('/', '')
                            if day.tag == 'today':
                                forecast[day0][kind.tag] = value
                            elif day.tag == 'tomorrow':
                                forecast[day1][kind.tag] = value
                            elif day.tag == 'dayafter_to':
                                forecast[day2][kind.tag] = value
                            else:
                                self.logger.debug("unknown day: {0}".format(day.tag))
        fxp.clear()
        return forecast