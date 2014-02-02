#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
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
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import time
import threading

logger = logging.getLogger('')


class DataLog():
    filepatterns = {}
    logpatterns = {}
    cycle = 0
    _items = {}
    _buffer = {}
    _buffer_lock = None

    def __init__(self, smarthome, path="var/log/data", filepatterns={ "default" : "{log}-{year}-{month}-{day}.csv" }, logpatterns={ "csv" : "{time};{item};{value}\n" }, cycle=10):
        self._sh = smarthome
        self.path = path

        if type(filepatterns) is list:
            for pattern in filepatterns:
                key, value = pattern.split(':')
                self.filepatterns[key] = value
        else:
            self.filepatterns = filepatterns

        if type(logpatterns) is list:
            newlogpatterns = {}
            for pattern in logpatterns:
                key, value = pattern.split(':')
                newlogpatterns[key] = value
            logpatterns = newlogpatterns

        for log in self.filepatterns:
            ext = self.filepatterns[log].split('.')[-1]
            if ext in logpatterns:
                self.logpatterns[log] = logpatterns[ext]

        self.cycle = int(cycle)
        self._items = {}
        self._buffer = {}
        self._buffer_lock = threading.Lock()
        
        logger.info('DataLog: Initialized, logging to "{}"'.format(self.path))
        for log in self.filepatterns:
            logger.info('DataLog: Registered log "{}", file="{}", format="{}"'.format(log, self.filepatterns[log], self.logpatterns[log]))

    def run(self):
        self.alive = True
        self._sh.scheduler.add('DataLog', self._dump, cycle=self.cycle)

    def stop(self):
        self.alive = False
        self._dump()

    def parse_item(self, item):
        if 'datalog' in item.conf:
            if type(item.conf['datalog']) is list:
                logs = item.conf['datalog']
            else:
                logs = [item.conf['datalog']]

            found = False
            for log in logs:
                if log not in self.filepatterns:
                    logger.debug('Unknown log "{}" for item {}'.format(log, item.id()))
                    return None

                if log not in self._buffer:
                    self._buffer[log] = []

                if item.id() not in self._items:
                    self._items[item.id()] = []

                if log not in self._items[item.id()]:
                   self._items[item.id()].append(log)
                   found = True

            if found:
                return self.update_item

        return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'DataLog':
            pass

        if item.id() in self._items:
            for log in self._items[item.id()]:
                self._buffer[log].append({ 'time' : self._sh.now(), 'item' : item.id(), 'value' : item() })

    def _dump(self):
        data = {}
        now = self._sh.now()
        handles = {}

        for log in self._buffer:
            self._buffer_lock.acquire()
            logger.debug('Dumping log "{}" with {} entries ...'.format(log, len(self._buffer[log])))
            entries = self._buffer[log]
            self._buffer[log] = []
            self._buffer_lock.release()

            if len(entries):
                logpattern = self.logpatterns[log]

                try:
                    for entry in entries:
                        filename = self.filepatterns[log].format(**{ 'log' : log, 'year' : entry['time'].year, 'month' : entry['time'].month, 'day' : entry['time'].day })

                        if filename not in handles:
                            handles[filename] = open(self.path + '/' + filename, 'a')

                        data = entry
                        data['stamp'] = data['time'].time();
                        handles[filename].write(logpattern.format(**data))

                except Exception as e:
                    logger.error('Error while writing to {}: {}'.format(filename, e))

        for filename in handles:
            handles[filename].close()

        logger.debug('Dump done!')

