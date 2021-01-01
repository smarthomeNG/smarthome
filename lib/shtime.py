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

try:
    import holidays
    HOLIDAYS_imported = True
except:
    HOLIDAYS_imported = False


import datetime
import dateutil
import pytz
from dateutil.tz import tzlocal
from dateutil import parser
import json
import logging
import os

import lib.shyaml as shyaml
from lib.constants import (YAML_FILE)
#from lib.translation import translate
from lib.translation import translate as lib_translate



_shtime_instance = None    # Pointer to the initialized instance of the shtime class (for use by static methods)

class Shtime:

    _tzinfo = None
    _timezone = None
    _utctz = None
    _starttime = None
    _tz = ''
    holidays = None
    public_holidays = None


    def __init__(self, smarthome):
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)

        global _shtime_instance
        if _shtime_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            self.logger.critical(self.translate("A second 'shtime' object has been created. There should only be ONE instance of class 'Shtime'!!! Called from: {callframe1} ({callframe3})").format(callframe1=calframe[1][1], callframe3=calframe[1][3]))

        _shtime_instance = self

        self._starttime = datetime.datetime.now()

        # set default timezone to UTC
#        global TZ
        self._tz = 'UTC'
        os.environ['TZ'] = self._tz
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


    def translate(self, txt, vars=None):
        """
        Returns translated text

        :param txt: text to translate
        :type txt: str

        :return: translated text
        :rtype: str
        """
        txt = str(txt)

        return lib_translate(txt, vars, additional_translations='lib/shtime')


    def set_tz(self, tz):
        """
        set timezone info from name of timezone
        """
        tzinfo = dateutil.tz.gettz(tz)
        if tzinfo is not None:
#            TZ = tzinfo
            self._tz = tz
            os.environ['TZ'] = self._tz
#             self._tzinfo = TZ
            self.set_tzinfo(tzinfo)
            self._timezone = pytz.timezone(tz)
        else:
            self.logger.warning(self.translate("Problem parsing timezone '{tz}' - Using UTC").format(tz=tz))
            self._timezone = pytz.timezone("UTC")
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
        :rtype: datetime.datetime
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

        return self._tz


    def tzinfo(self):
        """
        Returns the info about the actual local timezone

        :return: Timezone info
        :rtype: dateutil.tz.tz.tzfile
        """

        return self._tzinfo


    def tzname(self):
        """
        Returns the name about the actual local timezone (e.g. CET)

        :return: Timezone info
        :rtype: str
        """

        return datetime.datetime.now(tzlocal()).tzname()


    def tznameST(self):
        """
        Returns the name for Standard Time in the local timezone (e.g. CET)

        :return: Timezone info
        :rtype: str
        """

        jan = datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime(2020, 1, 1)), tzlocal())
        return jan.strftime("%Z")


    def tznameDST(self):
        """
        Returns the name for Daylight Saving Time (DST) in the local timezone (e.g. CEST)

        :return: Timezone info
        :rtype: str
        """

        jul = datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime.datetime(2020, 7, 1)), tzlocal())
        return jul.strftime("%Z")


    def utcnow(self):
        """
        Returns the actual time in GMT

        :return: Actual time in GMT
        :rtype: datetime.datetime
        """

        # tz aware utc time
        if self._utctz is None:
            self._utctz = dateutil.tz.gettz('UTC')
        return datetime.datetime.now(self._utctz)


    def utcinfo(self):
        """
        Returns the info about the GMT timezone

        :return: Timezone info
        :rtype: dateutil.tz.tz.tzfile
        """

        return self._utctz


    def runtime(self):
        """
        Returns the uptime of SmartHomeNG

        :return: Uptime in days, hours, minutes and seconds
        :rtype: datetime.timedelta
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


    # -----------------------------------------------------------------------------------------------------
    #   Following methods implement some time handling
    # -----------------------------------------------------------------------------------------------------

    def _build_timediff_resulttype(self, delta, resulttype):
        if resulttype == 's':
            return delta.days * 24 * 3600 + delta.seconds
        if resulttype == 'm':
            return delta.days * 24 * 60 + delta.seconds / 60
        if resulttype == 'h':
            return delta.days * 24 + delta.seconds / 3600
        if resulttype == 'd':
            return delta.days + delta.seconds / (3600 * 24)
        if resulttype == 'im':
            return delta.days * 24 * 60 + delta.seconds // 60
        if resulttype == 'ih':
            return delta.days * 24 + delta.seconds // 3600
        if resulttype == 'id':
            return delta.days
        if resulttype == 'dhms':
            return delta.days, delta.seconds // 3600, (delta.seconds // 60 - (delta.seconds // 3600) * 60), (
                    delta.seconds % 60)
        if resulttype == 'dhms2':
            return delta.days, delta.seconds // 3600, (delta.seconds // 60), (delta.seconds % 60)
        if resulttype == 'ds':
            return delta.days, delta.seconds
        self.logger.error("_build_timediff_resulttype: Called with invalid resulttype parameter: {resulttype}".format(resulttype=resulttype))
        return -1


    def time_since(self, dt, resulttype='s'):
        """
        Calculates the time that has elapsed since the given datetime parameter

        :param dt: point in time (in the past)
        :param resulttype: type in which the result should be returned (s, m, h, d, im, ih, id, dhms, ds)
        :type: dt: str | datetime.datetime | datetime.date | int | float
        :type resulttype: str

        :return: Elapsed time
        :rtype: int|float|tuple
        """
        dt = self.datetime_transform(dt)
        if type(dt) is datetime.datetime:
            delta = self.now() - dt
            if delta.days < 0:
                self.logger.error("time_since: "+self.translate("Called with point in time that is later than now: {dt}").format(dt=dt))
                return (0, 0)
            return self._build_timediff_resulttype(delta, resulttype)
        else:
            self.logger.error("time_since: "+self.translate("Called with parameter that is not of type 'datetime': {dt}").format(dt=dt))
            return -1


    def time_until(self, dt, resulttype='s'):
        """
        Calculates the time that will elapse from now to the given datetime parameter

        :param dt: point in time (in the past)
        :param resulttype: type in which the result should be returned (s, m, h, d, im, ih, id, dhms, ds)
        :type: dt: str|datetime.datetime|datetime.date|int|float
        :type resulttype: str

        :return: Elapsed time
        :rtype: int|float|tuple
        """
        dt = self.datetime_transform(dt)
        if type(dt) is datetime:
            delta = dt - self.now()
            if delta.days < 0:
                self.logger.error("time_until: "+self.translate("Called with point in time that is earlier than now: {dt}").format(dt=dt))
                return (0, 0)
            return self._build_timediff_resulttype(delta, resulttype)
        else:
            self.logger.error("time_since: "+self.translate("Called with parameter that is not of type 'datetime': {dt}").format(dt=dt))
            return -1


    def time_diff(self, dt1, dt2, resulttype='s'):
        """
        Calculates the time between the two given datetime parameters

        :param dt1: first point in time
        :param dt2: second point in time
        :param resulttype: type in which the result should be returned (s, m, h, d, im, ih, id, dhms, ds)
        :type: dt1: str|datetime.datetime|datetime.date|int|float
        :type: dt2: str|datetime.datetime|datetime.date|int|float
        :type resulttype: str

        :return: Elapsed time
        :rtype: int|float|tuple
        """
        dt1 = self.datetime_transform(dt1)
        dt2 = self.datetime_transform(dt2)
        if type(dt1) is datetime.datetime and type(dt2) is datetime.datetime:
            delta = dt2 - dt1
            if delta.days < 0:
                delta = dt1 - dt2
            return self._build_timediff_resulttype(delta, resulttype)
        else:
            self.logger.error("time_since: "+self.translate("Called with parameter that is not of type 'datetime': {dt1}, {dt2}").format(dt1=dt2, dt2=dt2))
            return -1


    def seconds_to_displaystring(self, sec):
        """
        Convert number of seconds to time display-string

        :param sec: Number of seconds to convert
        :type sec: int

        :return: Display-string (in the form x days, y hours, z minutes, s seconds)
        :rtype: str
        """
        min = sec // 60
        sec = sec - min * 60
        std = min // 60
        min = min - std * 60
        days = std // 24
        std = std - days * 24

        result = ''
        if days == 1:
            result += str(days) + ' ' + self.translate('Tag')
        elif days > 0:
            result += str(days) + ' ' + self.translate('Tage')

        if result and std > 0:
            result += ', '
        if std == 1:
            result += str(std) + ' ' + self.translate('Stunde')
        elif std > 0:
            result += str(std) + ' ' + self.translate('Stunden')

        if result and min > 0:
            result += ', '
        if min == 1:
            result += str(min) + ' ' + self.translate('Minute')
        elif min > 0:
            result += str(min) + ' ' + self.translate('Minuten')

        if result and sec > 0:
            result += ', '
        if sec == 1:
            result += str(sec) + ' ' + self.translate('Sekunde')
        elif sec > 0:
            result += str(sec) + ' ' + self.translate('Sekunden')
        return result


    # -----------------------------------------------------------------------------------------------------
    #   Following methods implement some date handling
    # -----------------------------------------------------------------------------------------------------

    def datetime_transform(self, key):
        """
        Converts Date/Time parameter from various formats to a datetime.datetime format

        :param key: date/time
        :type key: str|datetime.datetime|datetime.date|int|float

        :return: Date/Time
        :rtype: datetime.datetime
        """
        if isinstance(key, datetime.datetime):
            key = key
        elif isinstance(key, datetime.date):
            key = datetime.datetime(key.year, key.month, key.day, 0, 0, 0)
        elif isinstance(key, int) or isinstance(key, float):
            key = datetime.datetime.utcfromtimestamp(key)
        elif isinstance(key, str):
            dayfirst = True
            yearfirst = False
            if key.count('/') > 1:
                dayfirst = False
            if key.count('-') > 1:
                yearfirst = True
                dayfirst = False
            try:
                key = dateutil.parser.parse(key, dayfirst=dayfirst, yearfirst=yearfirst)
            except (ValueError, OverflowError):
                raise ValueError(self.translate("Cannot parse datetime from string '{key}'").format(key=key))
        else:
            raise TypeError(self.translate("Cannot convert type '{key}' to datetime").format(key=type(key)))
        if isinstance(key, datetime.datetime) and key.tzinfo is None:
            key =  self._timezone.localize(key)
        return key


    def date_transform(self, key):
        """
        Converts Date parameter from various formats to a datetime.date format

        :param key: date/time
        :type key: str|datetime.datetime|datetime.date|int|float

        :return: Date
        :rtype: datetime.date
        """
        try:
            key = self.datetime_transform(key).date()
        except (ValueError, OverflowError):
            raise ValueError(self.translate("Cannot parse date from string '{key}'").format(key=key))
        return key


    def beginning_of_week(self, week=None, year=None):
        """
        Calculates the date of the beginning of a given week

        If no week and no year are specified, the beginning of the current week is calculated

        :param week: week to use for calculation
        :param year: year to use for calculation
        :type week: int
        :type year: int

        :return: date the monday of given week
        :rtype: datetime.date
        """
        if week is None and year is None:
            week = self.calendar_week(self.today())
            year = self.current_year()
            month = self.current_month()
            if month == 1 and week > 50:
                year -= 1
            week -= 1
        else:
            if year is None:
                year = self.current_year()
            if week is None:
                self.logger.error("beginning_of_week: "+self.translate("Week not specified"))
                return self.today()
        #monday = datetime.datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w")  # geht erst ab Python 3.6
        monday = datetime.datetime.strptime('{year}-{week}-1'.format(year=year, week=week), "%Y-%W-%w")

        return monday.date()


    def beginning_of_month(self, month=None, year=None):
        """
        Calculates the date of the beginning of a given month

        This method is used to make code more readable

        If no month is specified, the current month is used
        If no year is specified, the current year is used

        :param month: month to use for calculation
        :param year: year to use for calculation
        :type month: int
        :type year: int

        :return: date the first day of given month
        :rtype: datetime.date
        """
        if month is None:
            month = self.current_month()
        if year is None:
            year = self.current_year()
        return datetime.date(year, month, 1)


    def beginning_of_year(self, year=None):
        """
         Calculates the date of the beginning of a given year

         This method is used to make code more readable

         If no year is specified, the current year is used

         :param year: year to use for calculation
         :type year: int

         :return: date the first day of given year
         :rtype: datetime.date
         """
        return self.beginning_of_month(1, year)


    def today(self):
        """
        Return today's date

        :return: date of today
        :rtype: datetime.date
        """
        return datetime.datetime.now().date()


    def tomorrow(self):
        """
        Return tomorrow's date

        :return: date of tomorrow
        :rtype: datetime.date
        """
        return self.today() + datetime.timedelta(days=1)


    def yesterday(self):
        """
        Return yesterday's date

        :return: date of yesterday
        :rtype: datetime.date
        """
        return self.today() + datetime.timedelta(days=-1)


    def current_year(self):
        """
        Return the current year

        :return: year
        :rtype: int
        """
        return self.today().year


    def current_month(self):
        """
        Return the current month

        :return: month
        :rtype: int
        """
        return self.today().month


    def current_day(self):
        """
        Return the current day

        :return: day
        :rtype: int
        """
        return self.today().day


    def length_of_year(self, year=None):
        """
        Returns the length of a given year

        :param year: year to use for calculation
        :type year: int

        :return: Length of year in days
        :rtype: int
        """
        return self.length_of_month(1, year)


    def length_of_month(self, month=None, year=None):
        """
        Returns the length of a given month for a given year

        :param month: month to use for calculation
        :param year: year to use for calculation
        :type month: int
        :type year: int

        :return: Length of month in days
        :rtype: int
        """
        if month is None:
            month = self.current_month()
        if year is None:
            year = self.current_year()

        next_month = month
        next_year = year
        if next_month == 12:
            next_year += 1
            next_month = 0
        return (datetime.datetime(next_year, next_month+1, 1) - datetime.datetime(year, month, 1)).days


    def day_of_year(self, date=None):
        """
        Calculate which day of the year the given date is

        :param date: date
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: day of year
        :rtype: int
        """
        if date:
            date = self.date_transform(date)
        else:
            date = self.today()
        return (date - datetime.date(date.year, 1, 1)).days + 1


    def weekday(self, date=None):
        """
        Returns the ISO weekday of a given date (or of today, if date is None)

        Return the day of the week as an integer, where Monday is 1 and Sunday is 7. (ISO weekday)

        :param date: date
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: weekday (1=Monday .... 7=Sunday)
        :rtype: int
        """

        if date:
            dt = self.date_transform(date)
            return dt.isoweekday()
        else:
            return datetime.datetime.now().isoweekday()


    def calendar_week(self, date=None):
        """
        Returns the calendar week (according to ISO)

        :param date: date
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: week (ISO)
        :rtype: int
        """
        if date:
            dt = self.date_transform(date)
            return dt.isocalendar()[1]
        else:
            return datetime.datetime.now().isocalendar()[1]


    def weekday_name(self, date=None):
        """
        Returns the name of the weekday for a given date

        :param date: date
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: weekday name
        :rtype: str
        """
        if date:
            dt = self.date_transform(date)
        else:
            dt = self.today()

        wday = self.weekday(dt)
        if wday == 1:
            day = "Montag"
        elif wday == 2:
            day = "Dienstag"
        elif wday == 3:
            day = "Mittwoch"
        elif wday == 4:
            day = "Donnerstag"
        elif wday == 5:
            day = "Freitag"
        elif wday == 6:
            day = "Samstag"
        elif wday == 7:
            day = "Sonntag"
        else:
            day = "?"

        return self.translate(day)


    def _get_nth_dow_in_month(self, dow, dow_week, year, month):
        """
        get nth day of week for given month and year

        :param dow:  day of week (1-7)
        :param dow_week: n for nth week (1-4)
        :param year: year to look into
        :param month: month to look into

        :return: date
        """
        day_1st = datetime.date(year, month, 1)
        dow_1st = self.weekday(datetime.date(year, month, 1))
        week = int(dow_week)

        if dow_1st <= dow:
            d_diff = dow - dow_1st
        else:
            d_diff = 7 - dow_1st + dow
        d_diff += (week - 1) * 7
        date = day_1st + datetime.timedelta(days=d_diff)
        self.logger.debug('dow_1st: d_diff {} -> {}'.format(d_diff, date))
        return date


    def _get_last_dow_in_month(self, dow, year, month):
        """
        get last day of week for given month and year

        :param dow: day of week (1-7)
        :param year: year to look into
        :param month: month to look into

        :return: date
        """
        day_last = datetime.date(year, month + 1, 1) + datetime.timedelta(days=-1)
        dow_last = self.weekday(datetime.date(year, month + 1, 1) + datetime.timedelta(days=-1))

        if dow_last >= dow:
            d_diff = dow_last - dow
        else:
            d_diff = dow_last + 7 - dow
        date = day_last - datetime.timedelta(days=d_diff)
        self.logger.debug('dow_last: d_diff {} -> {}'.format(d_diff, date))
        return date


    # -----------------------------------------------------------------------------------------------------
    #   Following methods implement some holiday handling
    # -----------------------------------------------------------------------------------------------------


    def _add_holiday_by_date(self, cust_date, gen_for_years):
        """
        Add a custom holiday for given day and month (and optionally year)

        :param cust_date:

        """
        cust_dict = {}
        self.logger.info(self.translate('custom holiday')+' (date): {}'.format(cust_date))

        for year in gen_for_years:
            d = datetime.date(year, cust_date['month'], cust_date['day'])

            cust_dict[d] = cust_date.get('name', '')

        self.holidays.append(cust_dict)
        return


    def _add_holiday_by_dow(self, cust_date, gen_for_years):
        """
        Add a custom holiday for given day-of-week

        :param cust_date:

        """
        cust_dict = {}
        self.logger.info(self.translate('custom holiday')+' (dow): {}'.format(cust_date))
        month = cust_date.get('month', None)
        try:
            dow_week = int(cust_date.get('dow_week', 0))
            if dow_week < 1:
                return
        except ValueError:
            if str(cust_date.get('dow_week', None)).lower() == 'last':
                dow_week = str(cust_date.get('dow_week', None)).lower()
            else:
                return

        try:
            dow_start_week = int(cust_date.get('dow_start_week', dow_week))
        except ValueError:
            dow_start_week = dow_week

        for year in gen_for_years:
            if month is None:
                # get every nth day-of-week in a year
                date = self._get_nth_dow_in_month(cust_date.get('dow', None), dow_start_week, year, 1)
                while date.year == year:
                    cust_dict[date] = cust_date.get('name', '')
                    date = date + datetime.timedelta(7*dow_week)
            else:
                # get a day-of-week in a given month
                if str(cust_date.get('dow_week', None)).lower() == 'last':
                    date = self._get_last_dow_in_month(cust_date.get('dow', None), year, month)
                else:
                    date = self._get_nth_dow_in_month(cust_date.get('dow', None), cust_date.get('dow_week', None), year, month)

                cust_dict[date] = cust_date.get('name', '')

        self.holidays.append(cust_dict)
        return


    def _add_custom_holidays(self):
        """
        Add custom holidays from etc/holidays.yaml to the initialized list of holidays

        :return: Number of valid custom holiday definitions
        """
        if self.holidays is None:
            self.logger.info("_add_custom_holidays: "+self.translate("Holidays are not initialized, cannot add custom holidays"))
            return 0

        custom = self.config.get('custom', [])
        count = 0
        if len(custom) > 0:
            for entry in custom:
                if isinstance(entry, str):
                    cust_date = json.loads(entry)
                else:
                    cust_date = entry
                # generate for range of years or a given year
                if cust_date.get('year', None) is None:
                    gen_for_years = self.years
                else:
                    gen_for_years = [cust_date['year']]

                # {'day': 2, 'month': 12, 'name': "Martin's Geburtstag"}
                if cust_date.get('month', None) and cust_date.get('day', None):
                    # generate holiday(s) for a given date (day/month)
                    self._add_holiday_by_date(cust_date, gen_for_years)
                    count += 1
                elif cust_date.get('dow', None) and cust_date.get('dow_week', None) and (0 < cust_date.get('dow', None) < 8):
                    # generate holiday(s) for a given weekday (dow/dowweek/month)
                    self._add_holiday_by_dow(cust_date, gen_for_years)
                    count += 1

        return count


    def add_custom_holiday(self, cust_date):
        """
        Add a custom holiday from etc/holidays.yaml to the initialized list of holidays

        :param cust_date: Dictionary with holiday definition (see: /etc/holidays.yaml.default)
        :type cust_date: dict
        """
        if self.holidays is None:
            self.logger.info("add_custom_holiday: "+self.translate("Holidays are not initialized, cannot add custom holidays"))
            return

        # generate for range of years or a given year
        if cust_date.get('year', None) is None:
            gen_for_years = self.years
        else:
            gen_for_years = [cust_date['year']]

        # {'day': 2, 'month': 12, 'name': "Martin's Geburtstag"}
        if cust_date.get('month', None) and cust_date.get('day', None):
            # generate holiday(s) for a given date (day/month)
            self._add_holiday_by_date(cust_date, gen_for_years)
        elif cust_date.get('dow', None) and cust_date.get('dow_week', None) and (0 < cust_date.get('dow', None) < 8):
            # generate holiday(s) for a given weekday (dow/dowweek/month)
            self._add_holiday_by_dow(cust_date, gen_for_years)

        log_msg = self.translate("Custom holiday definitions defined during runtime: {cust_date}")
        self.logger.warning(log_msg.format(cust_date=cust_date))

        return


    def add_custom_holiday_range(self, from_date, to_date=None, holiday_name=''):
        """
        Add a range of dates to the custom holidays

        :param from_date: First date to add
        :param to_date: Last date to add
        :param holiday_name: Name of the holidays
        :type from_date: str|datetime.datetime|datetime.date|int|float
        :type to_date: str|datetime.datetime|datetime.date|int|float
        :type holiday_name: str
        """
        from_date = self.date_transform(from_date)
        if to_date is None:
            to_date = from_date
        else:
            to_date = self.date_transform(to_date)

        num_days = (to_date-from_date).days + 1
        holiday_list = [from_date+datetime.timedelta(days=x) for x in range(num_days)]

        cust_dict = {}
        for holiday in holiday_list:
            cust_dict[holiday] = holiday_name
        self.holidays.append(cust_dict)
        return


    def _initialize_holidays(self):
        """
        Initialize the holidays according to etc/holidays.yaml for the current year and the two years to come
        """

        if self.holidays is None:
            self._etc_dir = self._sh._etc_dir
            conf_filename = os.path.join(self._sh._etc_dir, 'holidays'+YAML_FILE)
            self.config = shyaml.yaml_load(conf_filename)
            location = self.config.get('location', None)

            # prepopulate holidays for following years
            this_year=self.today().year
            self.years=[this_year, this_year+1, this_year+2]

            if location:
                country=location.get('country', 'DE')
                prov=location.get('province', None)
                state=location.get('state', None)
                try:
                    self.holidays = holidays.CountryHoliday(country, years=self.years, prov=prov, state=state)
                except KeyError as e:
                    self.logger.error("Error initializing self.holidays: {}".format(e))
                try:
                    self.public_holidays = holidays.CountryHoliday(country, years=self.years, prov=prov, state=state)
                except KeyError as e:
                    self.logger.error("Error initializing self.public_holidays: {}".format(e))
            else:
                self.holidays = holidays.CountryHoliday('US', years=self.years, prov=None, state=None)
                self.public_holidays = holidays.CountryHoliday('US', years=self.years, prov=None, state=None)

            if self.holidays is not None:
                c_logtext = self.translate('not defined')
                c_logcount = ''
                count = self._add_custom_holidays()
                if count > 0:
                    c_logcount = ' ' + str(count)
                    c_logtext = self.translate('defined')
                defined_state = ''
                if self.holidays.state is not None:
                    defined_state = ", state'" + self.holidays.state + "'"
                self.log_msg = self.translate("Using holidays for country '{country}', province '{province}'{state},{count} custom holiday(s) {defined}")
                self.log_msg = self.log_msg.format(country=self.holidays.country, province=self.holidays.prov, state=defined_state, count=c_logcount, defined=c_logtext)
                self.logger.info(self.log_msg)

                self.logger.info(self.translate('Defined holidays') + ':')
                for ft in sorted(self.holidays):
                    self.logger.info(' - {}: {}'.format(ft, self.holidays[ft]))

        return


    def is_weekend(self, date=None):
        """
        Returns True, if the date is on a weekend

        Note: Easter sunday is not considered a holiday (since it is a sunday already)!

        :param date: date for which the weekday should be returned. If not specified, today is used
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: True, if date is on a weekend
        :rtype: bool
        """

        if date:
            dt = self.date_transform(date)
        else:
            dt = self.today()

        self._initialize_holidays()

        return self.weekday(dt) in [6,7]


    def is_holiday(self, date=None):
        """
        Returns True, if the date is a holiday (custom or public)

        Note: Easter sunday is not concidered a holiday (since it is a sunday already)!

        :param date: date for which the weekday should be returned. If not specified, today is used
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: True, if date is on a holiday
        :rtype: bool
        """

        if date:
            dt = self.date_transform(date)
        else:
            dt = self.today()

        self._initialize_holidays()

        return (dt in self.holidays)


    def is_public_holiday(self, date=None):
        """
        Returns True, if the date is a public holiday

        Note: Easter sunday is not concidered a public holiday (since it is a sunday already)!

        :param date: date for which the weekday should be returned. If not specified, today is used
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: True, if date is on a holiday
        :rtype: bool
        """

        if date:
            dt = self.date_transform(date)
        else:
            dt = self.today()

        self._initialize_holidays()

        return (dt in self.public_holidays)


    def holiday_name(self, date=None, as_list=False):
        """
        Returns the name of the holiday, if date is a holiday

        If there are multiple holidays on that date, all are returned

        :param date: date for which the holiday-name should be returned. If not specified, today is used
        :param as_list: If True, result is a list and not a str (comma delimited)
        :type date: str|datetime.datetime|datetime.date|int|float

        :return: name of the holiday(s)
        :rtype: str|list
        """
        if date:
            dt = self.date_transform(date)
        else:
            dt = self.today()

        self._initialize_holidays()

        if as_list:
            if self.holidays.get_list(dt):
                return self.holidays.get(dt)
        else:
            if self.holidays.get(dt):
                return self.holidays.get(dt)
        return ''


    def holiday_list(self, year=None):
        """
        Returns a list with the defined holidays

        :param year: Year for which the holiday list sould be returned
        :type year: int

        :return: List with holiday information
        :rtpye: list
        """
        hl = []
        for h in self.holidays:
            if year is None or h.year == year:
                hl.append({h, self.holidays[h]})
        return hl


    def public_holiday_list(self, year=None):
        """
        Returns a list with the defined public holidays

        :param year: Year for which the holiday list sould be returned
        :type year: int

        :return: List with holiday information
        :rtpye: list
        """
        hl = []
        for h in self.public_holidays:
            if year is None or h.year == year:
                hl.append({h, self.public_holidays[h]})
        return hl
