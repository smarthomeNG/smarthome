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

"""
This module contains utils to be used in logging
"""

class Filter(logging.Filter):
    """
    This class builds a filter to be used in logging.yaml to configure logging
    
    Returning True tells logging to suppress this logentry,
    whereas False will include the record into further processing and eventual output
    """
    def __init__(self, name=''):
        if isinstance(name, list):
            self.name = name
        elif len(name) == 0:
            self.name = []
        else:
            self.name = [name]

    def filter(self, record):
        for n in self.name:
            if n == record.name:
                return False
        return True

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
        current_log = (record.module, record.levelno, record.msg)
        if current_log != self.last_log:
            self.last_log = current_log
            return True
        return False
