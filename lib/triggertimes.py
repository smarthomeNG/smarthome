#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2020   Martin Sinn                         m.sinn@gmx.de
# Copyright 2016        Christian Straßburg           c.strassburg@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
# Copyright 2019-2022   Bernd Meiners               Bernd.Meiners@mail.de
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
import calendar
import threading
import time

import dateutil.relativedelta
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import tzutc

from lib.shtime import Shtime
shtime = Shtime.get_instance()

logger = logging.getLogger(__name__)

"""
This library implements TriggerTimes in SmartHomeNG.

The main class ``TriggerTimes`` implements the handling for 
Linux like crontab and sky event bound times

This class has a static method to get a handle to the instance of the TriggerTimes class, 
that is created during initialization of SmartHomeNG.
This method implements a way to access the API for handling TriggerTimes without having 
to juggle through the object hierarchy of the running SmartHomeNG.

This API enables plugins and logics to access the details of the TriggerTimes initialized in SmartHomeNG.

The methods of the class TriggerTimes implement the API for trigger times.
They can be used the following way: To call eg. **get_toplevel_items()**, use the following syntax:

.. code-block:: python

    from lib.triggertimes import TriggerTimes
    sh_triggertimes = TriggerTimes.get_instance()

:Note: Do not use the functions or variables of the main smarthome object any more. They are deprecated.
    Use the methods of the class **TriggerTimes** instead.

:Note: This library is part of the core of SmartHomeNG. Regular plugins should not need to use this API. 
    It is mainly implemented for plugins near to the core like **scheduler** and the core itself!
"""

_triggertimes_instance = None    # Pointer to the initialized instance of the TriggerTimes class (for use by static methods)

def get_invalid_time():
    return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)

class TriggerTimes():
    """
    TriggerTimes loader class. (TriggerTimes-methods from lib/scheduler.py are moved here.)

    - An instance is created during initialization by bin/smarthome.py
    - There should be only one instance of this class. So: Don't create another instance
    """
    # dict with all the items that are defined in the form: 
    # {"*/5 6-19/1 * * *":  crontab object, "* * 6 * : crontab object, ..."}

    def __init__(self, smarthome):
        """
        :param smarthome: Instance of the smarthome master-object
        :type smarthome: object
        """
        self._sh = smarthome
        Skytime.set_smarthome_reference(smarthome)
        self.logger = logging.getLogger(__name__)
        
        # a list with objects containing trigger times
        self.__known_triggertimes = [] 

        global _triggertimes_instance
        if _triggertimes_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            self.logger.critical(f"A second 'TriggerTimes' object has been created. There should only be ONE instance of class 'TriggerTimes'!!! Called from: {calframe[1][1]} ({calframe[1][3]})")

        _triggertimes_instance = self

    def get_next(self, triggertime: str, starttime: datetime, location = None):
        """
        Find the next point in time starting from start for a given location
        Location is important if there is sunrise/set or moonrise/set included
        If location ist not given then the location of SmartHomeNG is used


        :param triggertime: a user defined time description when to trigger
        :type triggertime: str
        :param start: starttime and date for the beginning of the search
        :type start: datetime
        :param location: Location information (not implemented yet), defaults to None
        :type location: tupel with (lat,lon,elev), optional
        :return: the time and date of next event
        :rtype: datetime
        """
        triggertime = TriggerTimes.normalize(triggertime)
        #self.logger.debug(f"get next triggertime for '{triggertime}' start search at '{starttime}'")
        for tt in self.__known_triggertimes:
            if tt.get_triggertime() == triggertime:
                #self.logger.debug(f"Element found in list for {triggertime}")
                break
        else:
            if any(substring in triggertime for substring in Skytime.get_skyevents() ):
                self.logger.debug(f"create new Skytime('{triggertime}') object")
                tt = Skytime(triggertime)
            else:
                self.logger.debug(f"create new Crontab('{triggertime}') object")
                tt = Crontab(triggertime)
            self.__known_triggertimes.append(tt)
        self.logger.debug(tt)
        return tt.get_next(starttime)

    @staticmethod
    def normalize(triggertime):
        """
        this removes unnecessary spaces from a triggertime definition

        :param triggertime: definition of the triggertime
        :type triggertime: str
        :return: cleaned up triggertime
        :rtype: str
        """#
        if not isinstance( triggertime, str):
            triggertime = str(triggertime)
        triggertime = triggertime.strip()           # remove spaces in front and at end
        triggertime = re.sub(' +', ' ',triggertime) # replace multiple spaces by a single one
        return triggertime

    # --------------------------------------------------------------------------------------------------------
    #   Following (static) method of the class TriggerTimes implement the API for trigger times in SmartHomeNG
    # --------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the TriggerTimes class, to be used to access the trigger times API

        Use it the following way to access the API:

        .. code-block:: python

            from lib.triggertimes import TriggerTimes
            sh_triggertimes = TriggerTimes.get_instance()

            # to access a method (eg. get_next()):
            sh_triggertimes.get_next(triggertime)


        :return: Triggertimes instance
        :rtype: object
        """
        return _triggertimes_instance


"""
Events for SmartHomeNG can be scheduled by a parameter to attribute ``crontab`` which essentially describe a triggertime.
This attribute parameter may be one of:

    * init optional with timeshift, the init keyword is handled by the scheduler itself and will never show up here
        * crontab: init+1  --> 1 second after initialisation
        * crontab: init+5m --> 5 minutes after initialisation

    * sun- or moonbound time instruction 
        * crontab: 17:00<sunset<20:00 --> means sunset but a time at least equal or later than 17:00 and earlier or latest at 20:00
        * crontab: 6:00<sunrise<10:00 --> means sunrise but a time at least equal or later than 6:00 and earlier or latest at 10:00

    * parameter which is similar but not equal to linux *crontab*
        * crontab: */5 6-19/1 * * * ==> every 5 minutes between 6 and 19 at any day of any month or any weekday
"""

class TriggerTime():
    """
    This provides a base class for all trigger times like crontabs, or sun/moonbound trigger times
    It is mainly to share the same basics and static methods
    """
    named_days = { 
        'mon':'0', 'tue':'1','wed':'2','thu':'3','fri':'4','sat':'5','sun':'6',
        'mo':'0', 'di':'1','mi':'2','do':'3','fr':'4','sa':'5','so':'6' 
        }

    named_months = { 
        'jan':'1', 'feb':'2','mar':'3','apr':'4','may':'5','jun':'6','jul':'7',
        'aug': '8', 'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12'
        }

    def __init__(self, triggertime):
        self._lock = threading.Lock()
        # save the original given triggertime
        self._triggertime = triggertime
        #if TriggerTime.shtime is None:
        #    TriggerTime.shtime = Shtime.get_instance()

    def get_triggertime( self):
        return self._triggertime

    @staticmethod
    def integer_range(entry, low, high):
        """
        Inspects a string containing 
        * intervals ('*/2' --> ['2','4','6', ... high]
        * ranges ('9-11' --> ['9','10','11']), 
        * single values ('1,2,5,9' --> ['1','2','5','9'])
        * or a combination of those and 
        returns a sorted and distinct list of found integers

        :param entry: a string with single entries of intervals, numeric ranges or single values
        :param low: lower limit as integer
        :param high: higher limit as integer
        :return: a list of found integers formatted as string
        """
        result = []
        item_range = []

        # Check for multiple items and process each item recursively
        if ',' in entry:
            for item in entry.split(','):
                result.extend(Crontab.integer_range(item, low, high))

        # Check for intervals, e.g. "*/2", "9-17/2"
        elif '/' in entry:
            spec_range, interval = entry.split('/')
            logger.debug(f'Cron spec interval {entry} -> {spec_range},{interval}')
            result = Crontab.integer_range(spec_range, low, high)[::int(interval)]

        # Check for numeric ranges, e.g. "9-17"
        elif '-' in entry:
            spec_low, spec_high = entry.split('-')
            result = Crontab.integer_range('*', int(spec_low), int(spec_high))

        # Process single item
        else:
            if entry == '*':
                item_range = list(range(low, high + 1))
            else:
                item = int(entry)
                if item > high:  # entry above range
                    item = high  # truncate value to highest possible
                item_range.append(item)
            for entry in item_range:
                result.append(entry)
        result = sorted(list(set(result)))
        # logger.debug('Crontab.integer_range {}[{},{}] results in {}'.format(entry, low, high, result))
        return result

    @staticmethod
    def get_next_in_sorted_list( entry, items, minentry, maxentry):
        newlist = sorted([i for i in items if i >= minentry and i <= maxentry])
        if entry in newlist: return entry, True
        result = [i for i in newlist if i > entry]
        if len(result) == 0: return None, False
        return min(result), False


class Crontab(TriggerTime):
    """One space or more spaces separate the time pieces from each other.
    Currently sets of 4,5 or 6 parts are allowed.

    Distinction with count of parameters
    If 4 parts specified (normal case in SmartHomeNG up to version 1.8):

    * * * *
    │ │ │ │
    │ │ │ └───────────── weekday (0 - 6)
    │ │ └───────────── day of month (1 - 31)
    │ └───────────── hour (0 - 23)
    └───────────── minute (0 - 59)

    If 5 parts specified:
    
    * * * * *
    │ │ │ │ │
    │ │ │ │ └───────────── weekday (0 - 6)
    │ │ │ └───────────── month (1 - 12)           new 5th part
    │ │ └───────────── day of month (1 - 31)
    │ └───────────── hour (0 - 23)
    └───────────── minute (0 - 59)

    If 6 parts specified:
    
    * * * * * *
    │ │ │ │ │ │
    │ │ │ │ │ └───────────── weekday (0 - 6)
    │ │ │ │ └───────────── month (1 - 12)
    │ │ │ └───────────── day of month (1 - 31)    optional
    │ │ └───────────── hour (0 - 23)
    │ └───────────── minute (0 - 59)
    └───────────── seconds (0 - 60)               optional, only valid if month is present (which can be a range of 1-12 of course)

    So the parameter count is the distinction which flavour is to be used for examination

    There are predefined names to abbreviate certain recurrent time sets like **@midnight** which equals ``0 0 * * *``

    * named presets like:
        @yearly     equals  0 0 1 1 *
        @annually   equals  0 0 1 1 *
        @monthly    equals  0 0 1 * *
        @weekly     equals  0 0 * * 0
        @daily      equals  0 0 * * *
        @midnight   equals  0 0 * * *
        @hourly     equals  0 * * * *

    """
    crontab_presets = {
        "@yearly": "0 0 1 1 *",
        "@annually": "0 0 1 1 *",
        "@monthly": "0 0 1 * *",
        "@weekly": "0 0 * * 0",
        "@daily": "0 0 * * *",
        "@midnight": "0 0 * * *",
        "@hourly": "0 * * * *"
        }

    def __init__(self, triggertime):
        super().__init__(triggertime)

        self.next_event = None  # store last result
        self.max_calc_time = 0  # keep track of maximum calculation time
        # prevent
        self.hour = None
        self.hour_range = None
        self.minute = None
        self.minute_range = None
        self.second = None
        self.second_range = None
        self.day = None
        self.day_range = None
        self.wday = None
        self.weekday_range = None
        self.month = None
        self.month_range = None
        self.parameter_count = 0
        self._is_valid = False

        self.parse_triggertime()

    def parse_triggertime(self):
        """parse the crontab string for details and store them to the class variables for later use"""
        logger.debug(f'Enter Crontab.parse_triggertime({self._triggertime})')

        with self._lock:
            triggertime = self._triggertime
            # replace @yearly etc. with correct preset
            if triggertime in Crontab.crontab_presets:
                triggertime = Crontab.crontab_presets[triggertime]

            # find our how many parameters are given with this crontab and save them to the class variables
            try:
                parameter_set = triggertime.strip().split()
            except:
                logger.error(f"crontab entry '{triggertime}' can not be split up into parts")
                return False
            
            self.parameter_count = len(parameter_set)
            if self.parameter_count < 4:
                logger.error(f"crontab entry '{triggertime}' has fewer than 4 parts and is invalid")
                return False
            elif self.parameter_count == 4:
                logger.debug(f'old smarthome.py style parameter set {triggertime} given')
                self.minute, self.hour, self.day, self.wday = parameter_set[0],parameter_set[1],parameter_set[2],parameter_set[3]
                self.month='*'
                self.second = '0'
            elif self.parameter_count == 5:
                logger.debug(f'new SmartHomeNG style parameter set {triggertime} given')
                self.minute, self.hour, self.day, self.month, self.wday = parameter_set[0],parameter_set[1],parameter_set[2],parameter_set[3], parameter_set[4]
                self.second = '0'
            elif self.parameter_count == 6:
                logger.debug(f'new SmartHomeNG style parameter set {triggertime} given')
                self.second, self.minute, self.hour, self.day, self.month, self.wday = parameter_set[0],parameter_set[1],parameter_set[2],parameter_set[3], parameter_set[4], parameter_set[5]
            else:
                logger.error(f"crontab entry '{triggertime}' has more than 6 parts and is invalid")
                return False

            if self.parameter_count > 4:
                # replace abbreviated months like 'jan' with their number like '1'
                self.month = self.month.lower()
                for search in sorted(Crontab.named_months, key=len, reverse=True): # Through keys sorted by length
                    self.month = self.month.replace(search, Crontab.named_months[search])

            # replace abbreviated days like 'sun' for sunday with their number like '6'
            self.wday = self.wday.lower()
            for search in sorted(Crontab.named_days, key=len, reverse=True): # Through keys sorted by length
                self.wday = self.wday.replace(search, Crontab.named_days[search])

            # evaluate the crontab parameter string to some lists of allowed points as integers
            self.second_range = Crontab.integer_range(self.second, 0, 59)
            self.minute_range = Crontab.integer_range(self.minute, 0, 59)
            self.hour_range = Crontab.integer_range(self.hour, 0, 23)
            self.day_range = Crontab.integer_range(self.day, 1, 31)       # not zero based, limited to 1..31 days, needs to be clipped for actual month
            self.month_range = Crontab.integer_range(self.month, 1, 12)
            self.weekday_range = Crontab.integer_range(self.wday, 0, 6)
            self._is_valid = True

        logger.debug(f'Leave Crontab.parse_triggertime()')

    def __str__(self):
        r = f"""{self._triggertime} is {'' if self._is_valid else 'not'} valid, parameter count {self.parameter_count}:
        Hours:   {self.hour} -> {self.hour_range}
        Minutes: {self.minute} -> {self.minute_range}
        Seconds: {self.second} -> {self.second_range}
        Days:   {self.day} -> {self.day_range}
        Weekday: {self.wday} -> {self.weekday_range}
        Months: {self.month} -> {self.month_range}
        """
        return(r)


    def get_next(self, starttime: datetime):
        """
        Calculates the next crontab triggertime

        :param starttime: the datetime to start the search from
        :type starttime: datetime
        :return: found date and time of next occurence or a time way up in the future
        :rtype: datetime
        """
        if not self._is_valid:
            return get_invalid_time()

        with self._lock:
            tik = time.perf_counter()
            if self.next_event is None:
                self.next_event = datetime.datetime.min
                self.next_event = self.next_event.replace(tzinfo=starttime.tzinfo)
            if starttime < self.next_event:
                logger.debug(f'looking for the next event after {starttime} was already calculated as {self.next_event}')
                return self.next_event
            days_max_count = 365*25
            days = 0
            searchtime = starttime
            #logger.debug(f'looking for the next event after {starttime}')
            searchtime = searchtime.replace(microsecond=0) + datetime.timedelta(seconds=1)   # smallest amount higher than given time
            while True:
                #logger.warning(f"{searchtime}")
                days = abs((starttime-searchtime).days)
                if days > days_max_count:
                    logger.error(f'No matches after {days} examined days, giving up')
                    return get_invalid_time()
                # preset current searcher
                year = searchtime.year
                month, em = Crontab.get_next_in_sorted_list(searchtime.month, self.month_range, 1, 12)
                if month is not None:
                    if not em:
                        # if not an exact match for month then set starttime to earliest of next month
                        searchtime = searchtime.replace(month=month, day=1, hour=0, minute=0, second=0)
                    day, em = Crontab.get_next_in_sorted_list(searchtime.day, self.day_range, 1, calendar.monthrange(year, month)[1])
                    if day is not None:
                        if not em:
                            searchtime = searchtime.replace(day=day,hour=0, minute=0, second=0)
                        weekday = searchtime.weekday()
                        if weekday in self.weekday_range:
                            hour, em = Crontab.get_next_in_sorted_list(searchtime.hour, self.hour_range, 0, 23)
                            if hour is not None:
                                if not em:
                                    searchtime = searchtime.replace(hour=hour, minute=0, second=0)
                                minute, em = Crontab.get_next_in_sorted_list(searchtime.minute, self.minute_range, 0, 59)
                                if minute is not None:
                                    if not em:
                                        searchtime = searchtime.replace(minute=minute, second=0)
                                    second, em = Crontab.get_next_in_sorted_list(searchtime.second, self.second_range, 0, 59)
                                    if second is not None:
                                        if not em:
                                            searchtime = searchtime.replace(second=second)
                                        # we found the next event, so leave the while loop here
                                        break
                                    else:
                                        searchtime = searchtime.replace(second=0) + datetime.timedelta(minutes=1)
                                        continue
                                else:
                                    searchtime = searchtime.replace(minute=0,second=0) + datetime.timedelta(minutes=60)
                                    continue
                            else: # hour not found, goto next day at early morning
                                searchtime = searchtime.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
                                continue
                        else: # weekday not found, proceed at next day early morning
                            searchtime = searchtime.replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
                            continue
                    else: # day not found, start at beginning of next month
                        advance_days = calendar.monthrange(year, searchtime.month)[1]
                        searchtime = searchtime.replace(day=1, hour=0, minute=0, second=0) + datetime.timedelta(days=advance_days)
                        continue
                else:
                    # goto next month, set hour, minute and second to 0, set day to 1
                    searchtime = searchtime.replace(year=searchtime.year+1, month=1, day=1, hour=0, minute=0, second=0)
                    continue

            self.next_event = searchtime
            tok = time.perf_counter()-tik
            self.max_calc_time = max(self.max_calc_time, tok)
            logger.debug(f'next event is at {searchtime}, calc took {tok:0.4f} sec, max: {self.max_calc_time:0.4f} sec')

            # find out how the new function compares to old implementation
            if self.parameter_count == 4:
                tik = time.perf_counter()
                foo = self.get_next_old( starttime)
                tok = time.perf_counter()-tik
                logger.debug(f'OLD: next event is at {foo}, calc took {tok:0.4f} sec')
                if searchtime != foo:
                    logger.error(f'NEW gives {searchtime} but OLD gives {foo}')

            return searchtime


    def get_next_old(self, starttime: datetime):
        """
        a crontab entry is expected the correct form as documented above
        Part of the old implementation

        :param crontab: a string containing an enhanced crontab entry
        :return: a timezone aware datetime with the next event time or an error datetime object that lies 10 years in the future
        """
        try:
            next_event = self._parse_month(starttime)  # this month
            if not next_event:
                next_event = self._parse_month(starttime, next_month=True)  # next month
            #logger.debug(f'next event after {starttime} is {next_event}')
            return next_event
        except Exception as e:
            logger.error(f'Error parsing crontab "{self._triggertime}": {e}')
            return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)

    def _parse_month(self, starttime, next_month=False):
        """
        Inspects a given string with classic crontab information to calculate the next point in time that matches
        Part of the old implementation

        :param crontab: a string with crontab entries. It is expected to have the form of ``minute hour day weekday``
        :param next_month: inspect the current month or the next following month
        :return: false or datetime
        """
        # evaluate the crontab strings
        minute_range = self._range(self.minute, 00, 59)
        hour_range = self._range(self.hour, 00, 23)
        if not next_month:
            mdays = calendar.monthrange(starttime.year, starttime.month)[1]
        elif starttime.month == 12:
            mdays = calendar.monthrange(starttime.year + 1, 1)[1]
        else:
            mdays = calendar.monthrange(starttime.year, starttime.month + 1)[1]

        if self.wday == '*' and self.day == '*':
            day_range = self._day_range('0, 1, 2, 3, 4, 5, 6')
        elif self.wday != '*' and self.day == '*':
            day_range = self._range(self.wday,0,6)
            day_range = self._day_range(','.join(day_range))
        elif self.wday != '*' and self.day != '*':
            day_range = self._range(self.wday,0,6)
            day_range = self._day_range(','.join(day_range))
            day_range = day_range + self._range(self.day, 0o1, mdays)
        else:
            day_range = self._range(self.day, 0o1, mdays)

        # combine the different ranges
        event_range = sorted([str(day) + '-' + str(hour) + '-' + str(minute) for minute in minute_range for hour in hour_range for day in day_range])
        if next_month:  # next month
            next_event = event_range[0]
            next_time = starttime + dateutil.relativedelta.relativedelta(months=+1)
        else:  # this month
            now_str = starttime.strftime("%d-%H-%M")
            next_event = self._next(lambda event: event > now_str, event_range)
            if not next_event:
                return False
            next_time = starttime
        day, hour, minute = next_event.split('-')
        return next_time.replace(day=int(day), hour=int(hour), minute=int(minute), second=0, microsecond=0)

    def _next(self, f, seq):
        """Part of the old implementation"""
        for item in seq:
            if f(item):
                return item
        return False


    def _range(self, entry, low, high):
        """
        inspects a single crontab entry for minutes our hours
        Part of the old implementation

        :param entry: a string with single entries of intervals, numeric ranges or single values
        :param low: lower limit as integer
        :param high: higher limit as integer
        :return:
        """
        result = []
        item_range = []

        # Check for multiple comma separated values and process each of them recursively
        if ',' in entry:
            for item in entry.split(','):
                result.extend(self._range(item, low, high))

        # Check for intervals, e.g. "*/2", "9-17/2"
        elif '/' in entry:
             spec_range, interval = entry.split('/')
             #logger.debug('Cron spec interval {} {}'.format(entry, interval))
             result = self._range(spec_range, low, high)[::int(interval)]

        # Check for numeric ranges, e.g. "9-17"
        elif '-' in entry:
             spec_low, spec_high = entry.split('-')
             result = self._range('*', int(spec_low), int(spec_high))

        # Process single value
        else:
            if entry == '*':
                item_range = list(range(low, high + 1))
            else:
                item = int(entry)
                if item > high:  # entry above range
                    item = high  # truncate value to highest possible
                item_range.append(item)
            for entry in item_range:
                result.append('{:02d}'.format(entry))

        return result

    def _day_range(self, days):
        """
        inspect a given string with days given as integer numbers separated by ","
        Part of the old implementation
        :param days:
        :return: an array with strings containing the days of month
        """
        now = datetime.date.today()
        wdays = [MO, TU, WE, TH, FR, SA, SU]
        result = []
        for day in days.split(','):
            wday = wdays[int(day)]
            # add next weekday occurrence
            day = now + dateutil.relativedelta.relativedelta(weekday=wday)
            result.append(day.strftime("%d"))
            # safety add-on if weekday equals todays weekday
            day = now + dateutil.relativedelta.relativedelta(weekday=wday(+2))
            result.append(day.strftime("%d"))
        return result


class Skytime(TriggerTime):
    """
    Implement sunrise/sunset/moonrise/moonset oriented triggertimes
    """
    sh = None
    skyevents = ["sunrise","sunset","moonrise","moonset"]

    def __init__(self, triggertime, location = None):
        super().__init__(triggertime)

        self.h_min = None   # Either None or an int in range 0..23
        self.m_min = None   # Either None or an int in range 0..59
        self.h_max = None   # Either None or an int in range 0..23
        self.m_max = None   # Either None or an int in range 0..59
        self.event = None   # must be one of sunrise, sunset, moonrise, moonset
        self.doff = None    # Either None or a float in range -90.0 ... 90.0 (although the extreme values are nonsense)
        self.moff = None    # Either None or an int

        # extended syntax that allows day, month and weekday as well
        self.day = '*'
        self.wday = '*'
        self.month = '*'
        self.day_range = Skytime.integer_range(self.day, 1, 31)       # not zero based, limited to 1..31 days, needs to be clipped for actual month
        self.month_range = Skytime.integer_range(self.month, 1, 12)
        self.weekday_range = Skytime.integer_range(self.wday, 0, 6)

        self.next_event = None
        self.max_calc_time = 0

        self._is_valid = False

        self.parse_triggertime()

    @staticmethod
    def set_smarthome_reference(sh):
        Skytime.sh = sh

    @staticmethod
    def get_skyevents():
        return Skytime.skyevents

    @staticmethod
    def split_skyevents(triggertime: str):
        """
        Splits the triggertime into parts at '<'

        :param triggertime: contains a trigger time like ``[H:M<](sunrise|sunset)[+|-][offset][<H:M]``
        :type triggertime: str
        :raises SyntaxError: will be raised if triggertime does not match
        :return: a tuple of the parts
        :rtype: tuple
        """
        assert isinstance(triggertime, str), 'triggerime must be a string'
        tabs = triggertime.split('<')
        if len(tabs) == 1:
            smin = None
            cron = tabs[0].strip()
            smax = None
        elif len(tabs) == 2:
            if any(substring in tabs[0].strip() for substring in Skytime.skyevents ):
                smin = None
                cron = tabs[0].strip()
                smax = tabs[1].strip()
            else:
                smin = tabs[0].strip()
                cron = tabs[1].strip()
                smax = None
        elif len(tabs) == 3:
            smin = tabs[0].strip()
            cron = tabs[1].strip()
            smax = tabs[2].strip()
        else:
            raise SyntaxError(f"Wrong syntax: {triggertime}. Should be [H:M<](sunrise|sunset)[+|-][offset][unit][<H:M]")
        return (smin, cron, smax)

    @staticmethod
    def split_offset(skyevent):
        """
        This parses offsets from a sky event. It is expected for the offset to be 
        a float when indicating degrees or 
        an integer when unit ``m`` is appended

        :param skyevent: (skyevent)[+|-][offset][unit]
        :type skyevent: str
        :return: a tuple of a skyevent and offsets for degree and time (in minutes)
        :rtype: tuple 
        """
        doff = 0.0  # degree offset
        moff = 0  # minute offset
        tmp, op, offs = skyevent.rpartition('+')
        revent = ""
        if op:
            if offs.endswith('m'):
                moff = int(offs.strip('m'))
            else:
                doff = float(offs)
            revent = tmp
        else:
            tmp, op, offs = skyevent.rpartition('-')
            if op:
                if offs.endswith('m'):
                    moff = -int(offs.strip('m'))
                else:
                    doff = -float(offs)
                revent = tmp
            else:
                revent = offs

        return (revent, doff, moff)

    @staticmethod
    def keep_in_range(value, minvalue, maxvalue):
        if minvalue > maxvalue:
            logger.error(f"minvalue={minvalue} is greater than maxvalue={maxvalue}")
        if value < minvalue:
            value = minvalue
            logger.warning(f"{value}<{minvalue} --> {value}={minvalue}")
        if value > maxvalue:
            value = maxvalue
            logger.warning(f"{value}>{maxvalue} --> {value}={maxvalue}")
        return value

    @staticmethod
    def split_times(timepoint: str):
        if timepoint is None:
            return None
        timepoint = timepoint.strip()
        if timepoint == "":
            return None

        h, sep, m = timepoint.partition(':')
        try:
            h = int(h)
            h = Skytime.keep_in_range(h,0,23)
            m = int(m)
            m= Skytime.keep_in_range(m,0,59)
        except ValueError:
            pass
        return(h, m)

    def __str__(self):
        r = f"""{self._triggertime} is {'' if self._is_valid else 'not '}valid and evaluates to:
        min:   {self.h_min}:{self.m_min}
        event:  {self.event}
        degree offset: {self.doff}
        time offset: {self.moff} min
        max:   {self.h_max}:{self.m_max}
        Days:   {self.day} -> {self.day_range}
        Weekday: {self.wday} -> {self.weekday_range}
        Months: {self.month} -> {self.month_range}
        """
        return(r)

    def parse_triggertime(self):
        """parses internal set triggertime into parts"""
        logger.debug(f'Enter Skytime.parse_triggertime({self._triggertime})')
        try:
            with self._lock:
                triggertime = self._triggertime
                # find out how many parameters are given with this triggertime and save them to the class variables
                try:
                    parameter_set = triggertime.strip().split()
                except:
                    logger.error(f"skytime entry '{triggertime}' can not be split up into 1 or 4 parts")
                    return False

                self.parameter_count = len(parameter_set)
                if self.parameter_count == 1:
                    logger.debug(f'old smarthome.py style parameter set {triggertime} given')
                    self.timeset = parameter_set[0]    # this contains something like 'mm:hh<skyevent+offset<mm:hh'
                    self.day = '*'
                    self.wday = '*'
                    self.month='*'
                elif self.parameter_count == 4:
                    logger.debug(f'new SmartHomeNG style parameter set {triggertime} given')
                    self.timeset, self.day, self.month, self.wday = parameter_set[0],parameter_set[1],parameter_set[2],parameter_set[3]
                else:
                    logger.debug(f'wrong parameter set {triggertime} given')

                if self.parameter_count == 4:
                    self.month = self.month.lower()
                    for search in sorted(Skytime.named_months, key=len, reverse=True): # Through keys sorted by length
                        self.month = self.month.replace(search, Skytime.named_months[search])

                # replace abbreviated days like 'sun' for sunday with their number like '6'
                self.wday = self.wday.lower()
                for search in sorted(Skytime.named_days, key=len, reverse=True): # Through keys sorted by length
                    self.wday = self.wday.replace(search, Skytime.named_days[search])

                # evaluate the crontab parameter string to some lists of allowed points as integers
                self.day_range = Skytime.integer_range(self.day, 1, 31)       # not zero based, limited to 1..31 days, needs to be clipped for actual month
                self.month_range = Skytime.integer_range(self.month, 1, 12)
                self.weekday_range = Skytime.integer_range(self.wday, 0, 6)

                smin, cron, smax = Skytime.split_skyevents(self.timeset)
                logger.debug(cron)
                self.event, self.doff, self.moff = Skytime.split_offset(cron)
                logger.debug(self.event)
                if smin is not None:
                    self.h_min,self.m_min = Skytime.split_times(smin)
                if smax is not None:
                    self.h_max,self.m_max = Skytime.split_times(smax)
                if self.event in Skytime.skyevents:
                    self._is_valid = True
        except Exception as e:
            logger.debug(f'Error in Skytime.parse_triggertime({self._triggertime}): {e}')
        finally:
            logger.debug(f'Leave Skytime.parse_triggertime({self._triggertime})')

    def get_next(self, starttime: datetime):
        """
        Calculates the next skyevent bound triggertime

        :param starttime: point from which to start the search.
        :type starttime: datetime
        :return: found date and time of next occurence or a time way up in the future
        :rtype: datetime
        """
        mappings = {"sunrise": Skytime.sh.sun.rise, "sunset": Skytime.sh.sun.set, "moonrise": Skytime.sh.moon.rise, "moonset": Skytime.sh.moon.set}
        if not self._is_valid:
            raise ValueError(f"definition of {self._triggertime} was not successfully parsed!")
        with self._lock:
            tik = time.perf_counter()
            if self.next_event is None:
                self.next_event = datetime.datetime.min
                self.next_event = self.next_event.replace(tzinfo=starttime.tzinfo)
            if starttime < self.next_event:
                logger.debug(f'looking for the next event after {starttime} was already calculated as {self.next_event}')
                return self.next_event
            days_max_count = 365*25
            days = 0
            searchtime = starttime
            #logger.debug(f'looking for the next event after {starttime}')
            searchtime = searchtime + datetime.timedelta(microseconds=1)   # smallest amount higher than given time
            while True:
                #logger.warning(f"searchtime: {searchtime}")
                #logger.warning(f"difference {searchtime-starttime}")
                days = abs((searchtime-starttime).days)
                if days > days_max_count:
                    logger.error(f'No matches after {days} examined days, giving up')
                    return get_invalid_time()
                # preset current searcher
                year = searchtime.year
                month, em = Crontab.get_next_in_sorted_list(searchtime.month, self.month_range, 1, 12)
                if month is not None:
                    if not em:
                        # if not an exact match for month then set starttime to earliest of next month
                        searchtime = searchtime.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
                    day, em = Crontab.get_next_in_sorted_list(searchtime.day, self.day_range, 1, calendar.monthrange(year, month)[1])
                    if day is not None:
                        if not em:
                            searchtime = searchtime.replace(day=day,hour=0, minute=0, second=0)
                        weekday = searchtime.weekday()
                        if weekday in self.weekday_range:
                            # the day, month and weekday is correct with searchtime
                            # now get the skyevent time and see if it fits for this day.
                            if self.event in mappings:
                                eventtime = mappings[self.event](self.doff, self.moff, dt=searchtime)
                                # time in next_time will be in utctime. So we need to adjust it
                                if eventtime.tzinfo == tzutc():
                                    eventtime = eventtime.astimezone(Skytime.sh.shtime.tzinfo())
                                else:
                                    logger.error("searchtime.tzinfo was not given as utc!")
                            else:
                                logger.error(f'No function found to get next skyevent time for {self._triggertime}')
                                return get_invalid_time()
                            
                            # eventtime will contain the next time e.g. a sunset will take place
                            # thus 
                            #  - searchtime must be smaller than eventtime and 
                            #  - eventtime might be one or more day(s) later

                            logger.debug(f"starting with {starttime} the next {self.event}({self.doff},{self.moff}) is {eventtime}")

                            # if the dates differ then it must be certain that the new date adheres to the
                            # constraints of the day range.
                            if eventtime.date() > searchtime.date():
                                logger.debug(f"eventtime ({eventtime.date()}) is at least a day later than current searchtime ({searchtime}), skip to eventtime's early morning")
                                searchtime = eventtime.replace(hour=0, minute=0, second=0, microsecond=0)
                                continue # need to start over for a matching date

                            if eventtime.date() < searchtime.date():
                                logger.debug(f"eventtime ({eventtime.date()}) is at least a day earlier than current searchtime ({searchtime}), skip to searchtime's early morning")
                                searchtime = searchtime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                                continue

                            # eventtime and searchtime have the same day
                            # now check time limits if given
                            if self.h_min is not None and self.m_min is not None:
                                try:
                                    dmin = eventtime.replace(hour=self.h_min, minute=self.m_min, second=0, microsecond=0)
                                except Exception:
                                    logger.error('Wrong syntax: {self._triggertime}. Should be [H:M<](skyevent)[+|-][offset][<H:M]')
                                    return get_invalid_time()
                                if dmin > eventtime:
                                    eventtime = dmin

                            if self.h_max is not None and self.m_max is not None:
                                try:
                                    dmax = eventtime.replace(hour=self.h_max, minute=self.m_max, second=0, microsecond=0)
                                    logger.debug(f"searchtime={searchtime}, eventtime={eventtime}, dmax={dmax}")
                                except Exception:
                                    logger.error('Wrong syntax: {self._triggertime}. Should be [H:M<](skyevent)[+|-][offset][<H:M]')
                                    return get_invalid_time()

                                # the time offset for the event might be a higher negative number
                                # in this case it could be that dmax is way below the searchtime
                                if dmax < searchtime:
                                    # in this case we need to look the next day again
                                    searchtime = searchtime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                                    continue

                                if dmax < eventtime:
                                    eventtime = dmax
                            if eventtime < searchtime:
                                logger.debug(f"eventtime ({eventtime}) is still earlier than current searchtime ({searchtime}), skip to searchtime's early morning")
                                searchtime = searchtime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                                continue

                            #logger.debug(f"next trigger time found: {eventtime}")
                            searchtime = eventtime
                            break
                            #------------------------------
                        else: # weekday not found, proceed at next day early morning
                            searchtime = searchtime.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                            continue
                    else: # day not found, start at beginning of next month
                        advance_days = calendar.monthrange(year, searchtime.month)[1]
                        searchtime = searchtime.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=advance_days)
                        continue
                else:
                    # goto next month, set hour, minute and second to 0, set day to 1
                    searchtime = searchtime.replace(year=searchtime.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                    continue

            # successful
            self.next_event = searchtime
            tok = time.perf_counter()-tik
            self.max_calc_time = max(self.max_calc_time, tok)
            logger.debug(f'next event is at {searchtime}, calc took {tok:0.4f} seconds, maximum was {self.max_calc_time:0.4f}')
            return searchtime
