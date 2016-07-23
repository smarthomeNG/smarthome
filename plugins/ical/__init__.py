#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
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
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import datetime

import dateutil.tz
import dateutil.rrule
import dateutil.relativedelta

logger = logging.getLogger('')


class iCal():
    DAYS = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")
    FREQ = ("YEARLY", "MONTHLY", "WEEKLY", "DAILY", "HOURLY", "MINUTELY", "SECONDLY")
    PROPERTIES = ("SUMMARY", "DESCRIPTION", "LOCATION", "CATEGORIES", "CLASS")

    def __init__(self, smarthome):
        self._sh = smarthome

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        pass

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        pass

    def __call__(self, ics, delta=1, offset=0, username=None, password=None, timeout=2):
        if ics.startswith('http'):
            ical = self._sh.tools.fetch_url(ics, username=username, password=password, timeout=timeout)
            if ical is False:
                return {}
            ical = ical.decode()
        else:
            try:
                with open(ics, 'r') as f:
                    ical = f.read()
            except IOError as e:
                logger.error('Could not open ics file {0}: {1}'.format(ics, e))
                return {}
        now = self._sh.now()
        offset = offset - 1  # start at 23:59:59 the day before
        delta += 1  # extend delta for negetiv offset
        start = now.replace(hour=23, minute=59, second=59, microsecond=0) + datetime.timedelta(days=offset)
        end = start + datetime.timedelta(days=delta)
        events = self._parse_ical(ical, ics)
        revents = {}
        for event in events:
            event = events[event]
            e_start = event['DTSTART']
            e_end = event['DTEND']
            if 'RRULE' in event:
                e_duration = e_end - e_start
                for e_rstart in event['RRULE'].between(start, end, inc=True):
                    if e_rstart not in event['EXDATES']:
                        date = e_rstart.date()
                        revent = {'Start': e_rstart, 'End': e_rstart + e_duration}
                        for prop in self.PROPERTIES:
                            if prop in event:
                                revent[prop.capitalize()] = event[prop]
                        if date not in revents:
                            revents[date] = [revent]
                        else:
                            revents[date].append(revent)
            else:
                if (e_start > start and e_start < end) or (e_start < start and e_end > start):
                    date = e_start.date()
                    revent = {'Start': e_start, 'End': e_end}
                    for prop in self.PROPERTIES:
                        if prop in event:
                            revent[prop.capitalize()] = event[prop]
                    if date not in revents:
                        revents[date] = [revent]
                    else:
                        revents[date].append(revent)
        return revents

    def _parse_date(self, val, dtzinfo, par=''):
        if par.startswith('TZID='):
            tmp, par, timezone = par.partition('=')
        if 'T' in val:  # ISO datetime
            val, sep, off = val.partition('Z')
            dt = datetime.datetime.strptime(val, "%Y%m%dT%H%M%S")
        else:  # date
            y = int(val[0:4])
            m = int(val[4:6])
            d = int(val[6:8])
            dt = datetime.datetime(y, m, d)
        dt = dt.replace(tzinfo=dtzinfo)
        return dt

    def _parse_ical(self, ical, ics):
        #skip = False
        events = {}
        tzinfo = self._sh.tzinfo()
        ical = ical.replace('\n', '')
        for line in ical.splitlines():
            #if line == 'BEGIN:VTIMEZONE':
            #    skip = True
            #elif line == 'END:VTIMEZONE':
            #    skip = False
            if line == 'BEGIN:VEVENT':
                event = {'EXDATES': []}
            elif line == 'END:VEVENT':
                if 'UID' not in event:
                    logger.warning("iCal: problem parsing {0} no UID for event: {1}".format(ics, event))
                    continue
                if 'SUMMARY' not in event:
                    logger.warning("iCal: problem parsing {0} no SUMMARY for UID: {1}".format(ics, event['UID']))
                    continue
                if 'DTSTART' not in event:
                    logger.warning("iCal: problem parsing {0} no DTSTART for UID: {1}".format(ics, event['UID']))
                    continue
                if 'DTEND' not in event:
                    logger.warning("iCal: Warning in parsing {0} no DTEND for UID: {1}. Setting DTEND from DTSTART".format(ics, event['UID']))
                    #Set end to start time:
                    event['DTEND'] = event['DTEND']
                    continue
                if 'RRULE' in event:
                    event['RRULE'] = self._parse_rrule(event, tzinfo)
                if event['UID'] in events:
                    if 'RECURRENCE-ID' in event:
                        events[event['UID']]['EXDATES'].append(event['RECURRENCE-ID'])
                        events[event['UID'] + event['DTSTART'].isoformat()] = event
                    else:
                        logger.warning("iCal: problem parsing {0} duplicate UID: {1}".format(ics, event['UID']))
                        continue
                else:
                    events[event['UID']] = event
                del(event)
            elif 'event' in locals():
                key, sep, val = line.partition(':')
                key, sep, par = key.partition(';')
                key = key.upper()
                if key == 'TZID':
                    tzinfo = dateutil.tz.gettz(val)
                elif key in ['UID', 'SUMMARY', 'SEQUENCE', 'RRULE', 'CLASS']:
                    event[key] = val  # noqa
                elif key in ['DTSTART', 'DTEND', 'EXDATE', 'RECURRENCE-ID']:
                    try:
                        date = self._parse_date(val, tzinfo, par)
                    except Exception as e:
                        logger.warning("Problem parsing: {0}: {1}".format(ics, e))
                        continue
                    if key == 'EXDATE':
                        event['EXDATES'].append(date)  # noqa
                    else:
                        event[key] = date  # noqa
                else:
                    event[key] = val  # noqa
        return events

    def _parse_rrule(self, event, tzinfo):
        rrule = dict(a.split('=') for a in event['RRULE'].upper().split(';'))
        args = {}
        if 'FREQ' not in rrule:
            return
        freq = self.FREQ.index(rrule['FREQ'])
        #logger.debug("iCal: Frequency: {0}".format(freq))
        del(rrule['FREQ'])
        if 'DTSTART' not in rrule:
            rrule['DTSTART'] = event['DTSTART']
        if 'WKST' in rrule:
            if rrule['WKST'] in self.DAYS:
                rrule['WKST'] = self.DAYS.index(rrule['WKST'])
            else:
                rrule['WKST'] = int(rrule['WKST'])
        if 'BYDAY' in rrule:
            day = rrule['BYDAY']
            if day.isalpha():
                if day in self.DAYS:
                    day = self.DAYS.index(day)
            else:
                n = int(day[0:-2])
                day = self.DAYS.index(day[-2:])
                day = dateutil.rrule.weekday(day, n)
            rrule['BYWEEKDAY'] = day
            del(rrule['BYDAY'])
        if 'COUNT' in rrule:
            rrule['COUNT'] = int(rrule['COUNT'])
        if 'INTERVAL' in rrule:
            rrule['INTERVAL'] = int(rrule['INTERVAL'])
        if 'UNTIL' in rrule:
            try:
                rrule['UNTIL'] = self._parse_date(rrule['UNTIL'], tzinfo)
            except Exception as e:
                logger.warning("Problem parsing UNTIL: {1} --- {0} ".format(event, e))
                return
        for par in rrule:
            args[par.lower()] = rrule[par]
        return dateutil.rrule.rrule(freq, **args)
