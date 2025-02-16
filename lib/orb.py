#!/usr/bin/env python3
#
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2014 Marcus Popp                          marcus@popp.mx
# Copyright 2021-2025 Bernd Meiners                 Bernd.Meiners@mail.de
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import logging
import datetime
import math

logger = logging.getLogger(__name__)

try:
    import ephem
except ImportError as e:
    ephem = None  # noqa

import dateutil.relativedelta
from dateutil.tz import tzutc

"""
This library contains a class Orb for calculating sun or moon related events.
Currently it uses ephem for calculation of the sky bound events.
"""

class Orb():
    """
    Save an observers location and the name of a celestial body for future use
    
    The Methods internally use PyEphem for computation
    
    An `Observer` instance allows  to compute the positions of
    celestial bodies as seen from a particular position on the Earth's surface.
    Following attributes can be set after creation (used defaults are given):

        `date` - the moment the `Observer` is created
        `lat` - zero degrees latitude
        `lon` - zero degrees longitude
        `elevation` - 0 meters above sea level
        `horizon` - 0 degrees
        `epoch` - J2000
        `temp` - 15 degrees Celsius
        `pressure` - 1010 mBar
    """

    def __init__(self, orb, lon, lat, elev=False, neverup_delta=0.00001):
        """
        Save location and celestial body
        
        :param orb: either 'sun' or 'moon'
        :param lon: longitude of observer in degrees
        :param lat: latitude of observer in degrees
        :param elev: elevation of observer in meters
        """
        if ephem is None:
            logger.warning("Could not find/use ephem!")
            return
        
        self.orb = orb
        self.lat = lat
        self.lon = lon
        self.elev = elev
        if self.orb == 'sun':
            self.neverup_delta = neverup_delta
            if not neverup_delta == 0.00001:
                logger.warning(f"neverup_delta was adjusted to {neverup_delta} for sun calculations")
        else:
            self.neverup_delta = None

    def get_observer_and_orb(self):
        """
        Return a tuple of an instance of an observer with location information
        and a celestial body
        Both returned objects are uniquely created to prevent errors in computation

        See also this thread at `Stackoverflow <https://stackoverflow.com/questions/26428904/pyephem-advances-observer-date-on-neveruperror>`_
        dated back to 2015 where the creator of pyephem writes:
        
        > Second answer: As long as each thread has its own Moon and Observer objects, 
          it should be able to do its own computations without ruining those of any other threads.

        :return: tuple of observer and celestial body
        """

        observer = ephem.Observer()
        # ephem expects lat and lon as strings
        observer.long = str(self.lon)
        observer.lat = str(self.lat)
        if self.elev:
            observer.elevation = float(self.elev)

        if self.orb == 'sun':
            orb = ephem.Sun()
        elif self.orb == 'moon':
            orb = ephem.Moon()
            self.phase = self._phase
            self.light = self._light
            
        return observer,orb

    def _avoid_neverup(self, dt, date_utc, doff):
        """
        When specifying an offset for e.g. a sunset or a sunrise it might well be that the
        offset is too high to be ever reached for a specific location and time
        Therefore this function will limit this offset and return it to the calling function

        :param dt: starting point for calculation
        :type dt: datetime
        :param date_utc: a datetime with utc time
        :type date_utc: datetime
        :param doff: offset in degrees
        :type doff: float
        :return: corrected offset in degrees
        :rtype: float
        """
        originaldoff = doff

        # Get times for noon and midnight
        midnight = self.midnight(0, 0, dt=dt)
        noon = self.noon(0, 0, dt=dt)
        
        # If the altitudes are calculated from previous or next day, set the correct day for the observer query
        noon = noon if noon >= date_utc else \
            self.noon(0, 0, dt=date_utc + dateutil.relativedelta.relativedelta(days=1))
        midnight = midnight if midnight >= date_utc else \
            self.midnight(0, 0, dt=date_utc - dateutil.relativedelta.relativedelta(days=1))
        # Get lowest and highest altitudes of the relevant day/night
        max_altitude = self.pos(offset=None, degree=True, dt=midnight)[1] if doff <= 0 else \
                                self.pos(offset=None, degree=True, dt=noon)[1]

        # Limit degree offset to the highest or lowest possible for the given date
        doff = max(doff, max_altitude + self.neverup_delta) if doff < 0 else min(doff, max_altitude - self.neverup_delta) if doff > 0 else doff
        if not originaldoff == doff:
            logger.notice(f"offset {originaldoff} truncated to {doff}")
        return doff

    def noon(self, doff=0, moff=0, dt=None):
        observer, orb = self.get_observer_and_orb()
        if dt is not None:
            observer.date = dt - dt.utcoffset() - dateutil.relativedelta.relativedelta(minutes=moff)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        else:
            observer.date = datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(minutes=moff) + dateutil.relativedelta.relativedelta(seconds=2)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        if not doff == 0:
            doff = self._avoid_neverup(dt, date_utc, doff)
        observer.horizon = str(doff)
        next_transit = observer.next_transit(orb).datetime()
        next_transit = next_transit + dateutil.relativedelta.relativedelta(minutes=moff)
        next_transit = next_transit.replace(tzinfo=tzutc())
        logger.debug(f"ephem: noon for {self.orb} with doff={doff}, moff={moff}, dt={dt} will be {next_transit}")
        return next_transit

    def midnight(self, doff=0, moff=0, dt=None):
        observer, orb = self.get_observer_and_orb()
        if dt is not None:
            observer.date = dt - dt.utcoffset() - dateutil.relativedelta.relativedelta(minutes=moff)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        else:
            observer.date = datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(minutes=moff) + dateutil.relativedelta.relativedelta(seconds=2)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        if not doff == 0:
            doff = self._avoid_neverup(dt, date_utc, doff)
        observer.horizon = str(doff)
        next_antitransit = observer.next_antitransit(orb).datetime()
        next_antitransit = next_antitransit + dateutil.relativedelta.relativedelta(minutes=moff)
        next_antitransit = next_antitransit.replace(tzinfo=tzutc())
        logger.debug(f"ephem: midnight for {self.orb} with doff={doff}, moff={moff}, dt={dt} will be {next_antitransit}")
        return next_antitransit

    def rise(self, doff=0, moff=0, center=True, dt=None):
        """
        Computes the rise of either sun or moon
        :param doff:    degrees offset for the observers horizon
        :param moff:    minutes offset from time of rise (either before or after)
        :param center:  if True then the centerpoint of either sun or moon will be considered to make the transit otherwise the upper limb will be considered
        :param dt:      start time for the search for a rise, if not given the current time will be used
        :return:
        """
        observer, orb = self.get_observer_and_orb()
        # workaround if rise is 0.001 seconds in the past
        if dt is not None:
            observer.date = dt - dt.utcoffset() - dateutil.relativedelta.relativedelta(minutes=moff)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        else:
            observer.date = datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(minutes=moff) + dateutil.relativedelta.relativedelta(seconds=2)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        if not doff == 0:
            doff = self._avoid_neverup(dt, date_utc, doff)
        observer.horizon = str(doff)
        if not doff == 0:
            next_rising = observer.next_rising(orb, use_center=center).datetime()
        else:
            next_rising = observer.next_rising(orb).datetime()
        next_rising = next_rising + dateutil.relativedelta.relativedelta(minutes=moff)
        next_rising = next_rising.replace(tzinfo=tzutc())
        logger.debug(f"ephem: next_rising for {self.orb} with doff={doff}, moff={moff}, center={center}, dt={dt} will be {next_rising}")
        return next_rising

    def set(self, doff=0, moff=0, center=True, dt=None):
        """
        Computes the setting of either sun or moon
        :param doff:    degrees offset for the observers horizon
        :param moff:    minutes offset from time of setting (either before or after)
        :param center:  if True then the centerpoint of either sun or moon will be considered to make the transit otherwise the upper limb will be considered
        :param dt:      start time for the search for a setting, if not given the current time will be used
        :return:
        """
        observer, orb = self.get_observer_and_orb()
        # workaround if set is 0.001 seconds in the past
        if dt is not None:
            observer.date = dt - dt.utcoffset() - dateutil.relativedelta.relativedelta(minutes=moff)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        else:
            observer.date = datetime.datetime.utcnow() - dateutil.relativedelta.relativedelta(minutes=moff) + dateutil.relativedelta.relativedelta(seconds=2)
            date_utc = (observer.date.datetime()).replace(tzinfo=tzutc())
        # avoid NeverUp error
        if not doff == 0:
            doff = self._avoid_neverup(dt, date_utc, doff)
        observer.horizon = str(doff)
        if not doff == 0:
            next_setting = observer.next_setting(orb, use_center=center).datetime()
        else:
            next_setting = observer.next_setting(orb).datetime()
        next_setting = next_setting + dateutil.relativedelta.relativedelta(minutes=moff)
        next_setting = next_setting.replace(tzinfo=tzutc())
        logger.debug(f"ephem: next_setting for {self.orb} with doff={doff}, moff={moff}, center={center}, dt={dt} will be {next_setting}")
        return next_setting

    def pos(self, offset=None, degree=False, dt=None):
        """
        Calculates the position of either sun or moon
        :param offset:  given in minutes, shifts the time of calculation by some minutes back or forth
        :param degree:  if True: return the position of either sun or moon from the observer as degrees, otherwise as radians
        :param dt:      time for which the position needs to be calculated
        :return:        a tuple with azimuth and elevation
        """
        observer, orb = self.get_observer_and_orb()
        if dt is None:
            date = datetime.datetime.utcnow()
        else:
            date = dt.replace(tzinfo=tzutc())
        if offset:
            date += dateutil.relativedelta.relativedelta(minutes=offset)
        observer.date = date
        orb.compute(observer)
        if degree:
            return (math.degrees(orb.az), math.degrees(orb.alt))
        else:
            return (orb.az, orb.alt)

    def _light(self, offset=None):
        """
        Applies only for moon, returns fraction of lunar surface illuminated when viewed from earth
        for the current time plus an offset
        :param offset: an offset given in minutes
        """
        observer, orb = self.get_observer_and_orb()
        date = datetime.datetime.utcnow()
        if offset:
            date += dateutil.relativedelta.relativedelta(minutes=offset)
        observer.date = date
        orb.compute(observer)
        light = int(round(orb.moon_phase * 100))
        return light

    def _phase(self, offset=None):
        """
        Applies only for moon, returns the moon phase related to a cycle of approx. 29.5 days
        for the current time plus an offset
        :param offset: an offset given in minutes
        """
        observer, orb = self.get_observer_and_orb()
        date = datetime.datetime.utcnow()
        cycle = 29.530588861
        if offset:
            date += dateutil.relativedelta.relativedelta(minutes=offset)
        observer.date = date
        orb.compute(observer)
        last = ephem.previous_new_moon(observer.date)
        frac = (observer.date - last) / cycle
        phase = int(round(frac * 8))
        return phase
