#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Straßburg
# Copyright 2018 Bernd Meiners                      Bernd.Meiners@mail.de
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
import re
import datetime

"""
This module contains utils to be used in logging
"""

class Filter(logging.Filter):
    """
    This class builds a filter to be used in logging.yaml to configure logging
    name: name of the logger object (regex)
    module: logger module (regex)
    msg: logger message (regex)
    invert: defines whether the filter suppresses the entries matching the above parameters or suppresses everything else (bool)
    returns: bool

    Returning True tells logging to suppress this logentry,
    whereas False will include the record into further processing and eventual output
    """
    def __init__(self, name='', module='', msg='', timestamp='', invert=False):
        self.logger = logging.getLogger(__name__)
        self.name = name if isinstance(name, list) else [] if len(name) == 0 else [name]
        self.module = module if isinstance(module, list) else [] if len(module) == 0 else [module]
        self.msg = msg if isinstance(msg, list) else [] if len(msg) == 0 else [msg]
        self.timestamp = timestamp if isinstance(timestamp, list) else [] if len(timestamp) == 0 else [timestamp]
        compiled_name = []
        compiled_module = []
        compiled_msg = []
        compiled_timestamp = []
        for n in self.name:
            try:
                compiled_name.append(re.compile(n))
            except Exception as err:
                self.logger.error("There is a problem with filter {}. Error: {}".format(n, err))
        for m in self.module:
            try:
                compiled_module.append(re.compile(m))
            except Exception as err:
                self.logger.error("There is a problem with filter {}. Error: {}".format(m, err))
        for msg in self.msg:
            try:
                compiled_msg.append(re.compile(msg))
            except Exception as err:
                self.logger.error("There is a problem with filter {}. Error: {}".format(msg, err))
        for stamp in self.timestamp:
            try:
                compiled_timestamp.append(re.compile(stamp))
            except Exception as err:
                self.logger.error("There is a problem with filter {}. Error: {}".format(stamp, err))
        self.name = compiled_name
        self.module = compiled_module
        self.msg = compiled_msg
        self.timestamp = compiled_timestamp
        self.invert = invert

    def filter(self, record):
        hits = 0
        total = 4
        hits = hits + 1 if len(self.name) == 0 else hits
        hits = hits + 1 if len(self.module) == 0 else hits
        hits = hits + 1 if len(self.msg) == 0 else hits
        hits = hits + 1 if len(self.timestamp) == 0 else hits
        if len(self.timestamp) > 0:
            compare = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            for t in self.timestamp:
                if t.match(compare):
                    hits += 1
        if isinstance(record.msg, dict):
            record.msg = ['{}: {}'.format(i, record.msg[i]) for i in record.msg]
        if isinstance(record.msg, list):
            record.msg = ', '.join(record.msg)
        for n in self.name:
            if n.match(record.name):
                hits += 1
        for m in self.module:
            if m.match(record.module):
                hits += 1
        for msg in self.msg:
            if msg.match(record.msg):
                hits += 1
        #invert is False: hide record if all of the given parameters match
        #invert is True: show record if all of the given parameters match
        return True if hits < total and not self.invert else True if hits >= total and self.invert else False

class DuplicateFilter(object):
    """
    This class builds a filter to be used in logging.yaml to configure logging
    Since Python 3.2 it only needs to provide a filter function taking a
    LogRecord object as argument.
    The filter function here will remember module, levelno and msg of the
    current record until next call. If a record immediately following provides
    the same entries, then it won't be displayed.
    It is useful to suppress the generation of huge logs due to a non captured
    error that is only of time limited nature such as connection problems to
    other devices.
    This will however not work if there are two interchanging records.
    The size of a logfile should then be limited as a seconds measurement
    Returning True tells logging to suppress this logentry,
    whereas False will include the record into further processing and eventual output
    """
    def __init__(self):
        self.last_log = None

    def filter(self, record):
        current_log = (record.module, record.levelno, record.msg, record.created)
        if current_log != self.last_log:
            self.last_log = current_log
            return True
        return False
