#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
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


import datetime
import dateutil
from dateutil.tz import tzlocal
import logging
import os


logger = logging.getLogger(__name__)

_shtime_instance = None    # Pointer to the initialized instance of the shtime class (for use by static methods)


class Shtime:

    _tzinfo = None
    _utctz = None
    _starttime = None
    tz = ''
    
    
    def __init__(self, smarthome):
        global _shtime_instance
        if _shtime_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical("A second 'shtime' object has been created. There should only be ONE instance of class 'Shtime'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _shtime_instance = self
        
        self._starttime = datetime.datetime.now()

        # set default timezone to UTC
#        global TZ
        self.tz = 'UTC'
        os.environ['TZ'] = self.tz
        self.set_tzinfo(dateutil.tz.gettz('UTC'))


    # -----------------------------------------------------------------------------------------------------
    #   Following (static) method of the class Shtime implement the API for date and time handling in shNG
    # -----------------------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Shtime class, to be used to access the shtime-API

       .. code-block:: python

           from lib.shtime import Shtime
           shtime = Shtime.get_instance()

           # to access a method (eg. to get timezone info):
           shtime.tzinfo()


        :return: shinfo instance
        :rtype: object or None
        """
        if _shtime_instance == None:
            return None
        else:
            return _shtime_instance


    def set_tz(self, tz):
        """
        set timezone info from name of timezone
        """
        tzinfo = dateutil.tz.gettz(tz)
        if tzinfo is not None:
#            TZ = tzinfo
            self.tz = tz
            os.environ['TZ'] = self.tz
#             self._tzinfo = TZ
            self.set_tzinfo(tzinfo)
        else:
            logger.warning("Problem parsing timezone: {}. Using UTC.".format(tz))
        return
        
        
    def set_tzinfo(self, tzinfo):
        """
        Set the timezone info
        """
        self._tzinfo = tzinfo
        return
        
        
    #################################################################
    # Time Methods
    #################################################################
    def now(self):
        """
        Returns the actual time in a timezone aware format
        
        :return: Actual time for the local timezone
        :rtype: datetime
        """
        
        if self._tzinfo is None:
            self._tzinfo = dateutil.tz.gettz('UTC')
        # tz aware 'localtime'
        return datetime.datetime.now(self._tzinfo)


    def tz(self):
        """
        Returns the the actual local timezone

        :return: Timezone
        :rtype: str
        """

        return self.tz


    def tzinfo(self):
        """
        Returns the info about the actual local timezone

        :return: Timezone info
        :rtype: object
        """

        return self._tzinfo


    def tzname(self):
        """
        Returns the name about the actual local timezone (e.g. CET)

        :return: Timezone info
        :rtype: object
        """

        return datetime.datetime.now(tzlocal()).tzname()


    def utcnow(self):
        """
        Returns the actual time in GMT

        :return: Actual time in GMT
        :rtype: datetime
        """

        # tz aware utc time
        if self._utctz is None:
            self._utctz = dateutil.tz.gettz('UTC')
        return datetime.datetime.now(self._utctz)


    def utcinfo(self):
        """
        Returns the info about the GMT timezone

        :return: Timezone info
        :rtype: str
        """

        return self._utctz


    def runtime(self):
        """
        Returns the uptime of SmartHomeNG

        :return: Uptime in days, hours, minutes and seconds
        :rtype: str
        """

        return datetime.datetime.now() - self._starttime


    def runtime_as_dict(self):
        """
        Returns the uptime of SmartHomeNG as a dict of integers

        :return: {days, hours, minutes, seconds}
        :rtype: dict
        """

        # return SmarthomeNG runtime
        rt = str(self.runtime())
        daytest = rt.split(' ')
        if len(daytest) == 3:
            days = int(daytest[0])
            hours, minutes, seconds = [float(val) for val in str(daytest[2]).split(':')]
        else:
            days = 0
            hours, minutes, seconds = [float(val) for val in str(daytest[0]).split(':')]
        total_seconds = days * 24 * 3600 + hours * 3600 + minutes * 60 + seconds

        return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds, 'total_seconds': total_seconds}
