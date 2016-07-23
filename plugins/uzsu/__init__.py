#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2013 Niko Will
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
##########################################################################


# Item Data Format
# 
# Each UZSU item is of type list. Each list entry has to be a dict with specific key and value pairs. Here are the possible keys and what their for:
# 
#     dtstart: a datetime object. Exact datetime as start value for the rrule algorithm. Important e.g. for FREQ=MINUTELY rrules (optional).
# 
#     value: the value which will be set to the item.
# 
#     active: True if the entry is activated, False if not. A deactivated entry is stored to the database but doesn't trigger the setting of the value. It can be enabled later with the update method.
# 
#     time: time as string to use sunrise/sunset arithmetics like in the crontab eg. 17:00<sunset, sunrise>8:00, 17:00<sunset. You also can set the time with 17:00.
# 
#     rrule: You can use the recurrence rules documented in the iCalendar RFC for recurrence use of a switching entry.
# 
# Example
# 
# Activates the light every other day at 16:30 and deactivates it at 17:30 for five times:
# 
# sh.eg.wohnen.kugellampe.uzsu({'active':True, 'list':[
# {'value':1, 'active':True, 'rrule':'FREQ=DAILY;INTERVAL=2;COUNT=5', 'time': '16:30'},
# {'value':0, 'active':True, 'rrule':'FREQ=DAILY;INTERVAL=2;COUNT=5', 'time': '17:30'}
# ]})



import logging
from datetime import datetime, timedelta

from dateutil.rrule import rrulestr
from dateutil import parser

import lib.orb

class UZSU():

    _items = {}         # item buffer for all uzsu enabled items

    def __init__(self, smarthome, path=None):
        self.logger = logging.getLogger('UZSU')
        self.logger.info('Init UZSU')
        self._sh = smarthome

    def parse_item(self, item):
        if 'uzsu_item' in item.conf:
            self._items[item] = item()
            return self.update_item

    def run(self):
        """This is called once at the beginning after all items are already parsed from smarthome.py
        All active uzsu items are registered to the scheduler
        """
        self.alive = True
        for item in self._items:
            if 'active' in self._items[item]:
                if self._items[item]['active']:
                    self._schedule(item)

    def stop(self):
        self.alive = False

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        This is called by smarthome engine when the item changes, e.g. by Visu or by the command line interface
        The relevant item is put into the internal item list and registered to the scheduler
        """
        self._items[item] = item()
        self._schedule(item)

    def _schedule(self, item):
        """
        This function schedules an item: First the item is removed from the scheduler. If the item is active
        then the list is searched for the nearest next execution time
        """
        self._sh.scheduler.remove('uzsu_{}'.format(item))
        _next = None
        _value = None
        if 'active' in self._items[item]:
            if self._items[item]['active']:
                for entry in self._items[item]['list']:
                    next, value = self._next_time(entry)
                    if _next is None:
                        _next = next
                        _value = value
                    elif next and next < _next:
                        _next = next
                        _value = value
        if _next and not _value is None:
            self._sh.scheduler.add('uzsu_{}'.format(item), self._set, value={'item': item, 'value': _value}, next=_next)

    def _set(self, **kwargs):
        item = kwargs['item']
        value = kwargs['value']
        self._sh.return_item(item.conf['uzsu_item'])(value, caller='UZSU')
        self._schedule(item)

    def _next_time(self, entry):
        """
        Here we examine an entry of the list of points in time and return the next execution time and the next value
        """
        try:
            if not isinstance(entry, dict):
                return None, None
            if not 'value' in entry:
                return None, None
            if not 'active' in entry:
                return None, None
            if not 'time' in entry:
                return None, None
            now = datetime.now()
            value = entry['value']
            active = entry['active']
            today = datetime.today()
            yesterday = today - timedelta(days=1)
            time = entry['time']
            if not active:
                return None, None
            if 'date' in entry:
                date = entry['date']
            if 'rrule' in entry:
                if 'dtstart' in entry:
                    rrule = rrulestr(entry['rrule'], dtstart=entry['dtstart'])
                else:
                    try:
                        rrule = rrulestr(entry['rrule'], dtstart=datetime.combine(yesterday, parser.parse(time.strip()).time()))
                    except Exception as e:
                        self.logger.debug("Tolerated Exception '{}' while examining '{}' with function rrulestr()".format(e,time))
                        if 'sun' in time:
                            self.logger.debug("Looking for next sun-related time with rulestr()")
                            rrule = rrulestr(entry['rrule'], dtstart=datetime.combine(yesterday, self._sun(datetime.combine(yesterday.date(), datetime.min.time()).replace(tzinfo=self._sh.tzinfo()), time).time()))
                        else:
                            self.logger.debug("Looking for next time with rulestr()")
                            rrule = rrulestr(entry['rrule'], dtstart=datetime.combine(yesterday, datetime.min.time()))
                dt = now
                while self.alive:
                    dt = rrule.after(dt)
                    if dt is None:
                        return None, None
                    if 'sun' in time:
                        next = self._sun(datetime.combine(dt.date(), datetime.min.time()).replace(tzinfo=self._sh.tzinfo()), time)
                        self.logger.debug("Result parsing time (rrule){}: {}".format(time, next))                 
                    else:
                        next = datetime.combine(dt.date(), parser.parse(time.strip()).time()).replace(tzinfo=self._sh.tzinfo())
                    if next and next.date() == dt.date() and next > datetime.now(self._sh.tzinfo()):
                        return next, value
            if 'sun' in time:
                next = self.sun(datetime.combine(today, datetime.min.time()).replace(tzinfo=self._sh.tzinfo()), time)
                self.logger.debug("Result parsing time (sun) {}: {}".format(time, next))              
            else:
                next = datetime.combine(today, parser.parse(time.strip()).time()).replace(tzinfo=self._sh.tzinfo())
            if next and next.date() == today and next > datetime.now(self._sh.tzinfo()):
                return next, value
        except Exception as e:
            self.logger.error("Error '{}' parsing time: {}".format(time, e))
        return None, None

    def _sun(self, dt, tstr):
        #dt contains a datetime object, whereas tstr should contain a string like '6:00<sunrise<8:00'
        #syntax is [H:M<](sunrise|sunset)[+|-][offset][<H:M]

        # checking preconditions from configuration:
        if not self._sh.sun:  # no sun object created
            self.logger.error('No latitude/longitude specified. You could not use sunrise/sunset as UZSU entry.')
            return

        # create an own sun object:
        try:
            #longitude = self._sh.sun.long
            #latitude = self._sh.sun.lat
            #elevation = self._sh.sun.elevation
            longitude = self._sh.sun._obs.long
            latitude = self._sh.sun._obs.lat
            elevation = self._sh.sun._obs.elev
            uzsu_sun = lib.orb.Orb('sun', longitude, latitude, elevation)
            self.logger.debug("Created a new sun object with latitude={}, longitude={}, elevation={}".format(latitude, longitude, elevation)) 
        except Exception as e:
            self.logger.error("Error '{}' creating a new sun object. You could not use sunrise/sunset as UZSU entry.".format(e))
            return

        # now start into parsing details
        self.logger.debug('Examine time string: {0}'.format(tstr))
            
        # find min/max times
        tabs = tstr.split('<')
        if len(tabs) == 1:
            smin = None
            cron = tabs[0].strip()
            smax = None
        elif len(tabs) == 2:
            if tabs[0].startswith('sun'):
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
            self.logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
            return

        # calculate the time offset
        doff = 0  # degree offset
        moff = 0  # minute offset
        tmp, op, offs = cron.rpartition('+')
        if op:
            if offs.endswith('m'):
                moff = int(offs.strip('m'))
            else:
                doff = float(offs)
        else:
            tmp, op, offs = cron.rpartition('-')
            if op:
                if offs.endswith('m'):
                    moff = -int(offs.strip('m'))
                else:
                    doff = -float(offs)

        # see if sunset or sunrise are included 
        dmin = None
        dmax = None
        if cron.startswith('sunrise'):
            next_time = uzsu_sun.rise(doff, moff, dt=dt)
            self.logger.debug("Sunrise is included and calculated as {}".format(next_time)) 
        elif cron.startswith('sunset'):
            next_time = uzsu_sun.set(doff, moff, dt=dt)
            self.logger.debug("Sunset is included and calculated as {}".format(next_time)) 
        else:
            self.logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
            return

        if smin is not None:
            h, sep, m = smin.partition(':')
            try:
                dmin = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self._sh.tzinfo())
            except Exception:
                self.logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
                return
            if dmin > next_time:
                next_time = dmin
        if smax is not None:
            h, sep, m = smax.partition(':')
            try:
                dmax = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self._sh.tzinfo())
            except Exception:
                self.logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
                return
            if dmax < next_time:
                next_time = dmax
        
        if dmin is not None and dmax is not None:
            if dmin > dmax:
                self.logger.error('Wrong times: the earliest time should be smaller than the latest time in {}'.format(tstr))
                return
            
        return next_time
