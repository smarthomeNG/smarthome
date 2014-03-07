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

import logging
from datetime import datetime, timedelta

from dateutil.rrule import rrulestr
from dateutil import parser

logger = logging.getLogger('')


class UZSU():

    _items = {}         # item buffer for all uzsu enabled items

    def __init__(self, smarthome, path=None):
        logger.info('Init UZSU')
        self._sh = smarthome

    def parse_item(self, item):
        if 'uzsu_item' in item.conf:
            self._items[item] = item()
            return self.update_item

    def run(self):
        self.alive = True
        for item in self._items:
            if 'active' in self._items[item]:
                if self._items[item]['active']:
                    self._schedule(item)

    def stop(self):
        self.alive = False

    def update_item(self, item, caller=None, source=None, dest=None):
        self._items[item] = item()
        self._schedule(item)

    def _schedule(self, item):
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
                    except:
                        rrule = rrulestr(entry['rrule'], dtstart=datetime.combine(yesterday, datetime.min.time()))
                dt = now
                while self.alive:
                    dt = rrule.after(dt)
                    if dt is None:
                        return None, None
                    if 'sun' in time:
                        next = self._sun(datetime.combine(dt.date(), datetime.min.time()).replace(tzinfo=self._sh.tzinfo()), time)
                    else:
                        next = datetime.combine(dt.date(), parser.parse(time.strip()).time()).replace(tzinfo=self._sh.tzinfo())
                    if next and next.date() == dt.date() and next > datetime.now(self._sh.tzinfo()):
                        return next, value
            if 'sun' in time:
                next = self.sun(datetime.combine(today, datetime.min.time()).replace(tzinfo=self._sh.tzinfo()), time)
            else:
                next = datetime.combine(today, parser.parse(time.strip()).time()).replace(tzinfo=self._sh.tzinfo())
            if next and next.date() == today and next > datetime.now(self._sh.tzinfo()):
                return next, value
        except Exception as e:
            logger.error("Error parsing time {}: {}".format(time, e))
        return None, None

    def _sun(self, dt, tstr):
        if not self._sh.sun:  # no sun object created
            logger.warning('No latitude/longitude specified. You could not use sunrise/sunset as UZSU entry.')
            return
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
            logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
            return

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

        if cron.startswith('sunrise'):
            next_time = self._sh.sun.rise(doff, moff, dt=dt)
        elif cron.startswith('sunset'):
            next_time = self._sh.sun.set(doff, moff, dt=dt)
        else:
            logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
            return

        if smin is not None:
            h, sep, m = smin.partition(':')
            try:
                dmin = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self._sh.tzinfo())
            except Exception:
                logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
                return
            if dmin > next_time:
                next_time = dmin
        if smax is not None:
            h, sep, m = smax.partition(':')
            try:
                dmax = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self._sh.tzinfo())
            except Exception:
                logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(tstr))
                return
            if dmax < next_time:
                next_time = dmax
        return next_time
