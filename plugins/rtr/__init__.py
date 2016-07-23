#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 TCr82 @ KNX-User-Forum         http://knx-user-forum.de/
# Version 0.2
#########################################################################
#  This file is part of SmartHome.py.   http://smarthome.sourceforge.net/
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

# Some useful docs:
# http://www.rn-wissen.de/index.php/Regelungstechnik#PI-Regler
# http://de.wikipedia.org/wiki/Regler#PI-Regler
# http://www.honeywell.de/fp/regler/Reglerparametrierung.pdf

import logging
import threading
#import serial
import time
#from inspect import getmembers
#from pprint import pprint

logger = logging.getLogger('')

def dump(obj):
  '''return a printable representation of an object for debugging'''
  newobj=obj
  if '__dict__' in dir(obj):
    newobj=obj.__dict__
    if ' object at ' in str(obj) and not newobj.has_key('__type__'):
      newobj['__type__']=str(obj)
    for attr in newobj:
      newobj[attr]=dump(newobj[attr])
  return newobj

# 
# Room Temperatur Regulator Class
#
class RTR():

    _controller = {}
    _defaults = {'currentItem' : None,
                'setpointItem' : None,
                'actuatorItem' : None,
                'stopItem' : None,
                'eSum' : 0,
                'Kp' : 0,
                'Ki' : 0,
                'Ta' : 60,
                'Tlast' : 0,
                'validated' : False}

    def __init__(self, smarthome, default_Kp = 5, default_Ki = 240):
        self._sh = smarthome
        self._default_Kp = default_Kp
        self._default_Ki = default_Ki

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.alive = False

    def parse_item(self, item):

        if 'rtr_current' in item.conf and not item.conf['rtr_current'].isdigit():
            logger.error("rtr: error in {0}, rtr_current need to be the controller number" . format(item.id()))
            return
        elif 'rtr_current' in item.conf:
            c = 'c' + item.conf['rtr_current']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self._controller[c] = self._defaults

            # store curstrentItem into controller
            self._controller[c]['currentItem'] = item.id()

            if 'rtr_Kp' not in item.conf:
                logger.info("rtr: missing rtr_Kp in {0}, setting to default: {1}" . format(item.id(), self._default_Kp))
                self._controller[c]['Kp'] = self._default_Kp
            else:
                self._controller[c]['Kp'] = item.conf['rtr_Kp']

            if 'rtr_Ki' not in item.conf:
                logger.info("rtr: missing rtr_Ki in {0}, setting to default: {1}" . format(item.id(), self._default_Ki))
                self._controller[c]['Ki'] = self._default_Ki
            else:
                self._controller[c]['Ki'] = item.conf['rtr_Ki']

            if 'rtr.scheduler' not in self._sh.scheduler:
                self._sh.scheduler.add('rtr.scheduler', self.update_items, prio=5, cycle=int(60))

            if not self._controller[c]['validated']:
                self.validate_controller(c)

            return

        if 'rtr_setpoint' in item.conf and not item.conf['rtr_setpoint'].isdigit():
            logger.error("rtr: error in {0}, rtr_setpoint need to be the controller number" . format(item.id()))
            return
        elif 'rtr_setpoint' in item.conf:
            c = 'c' + item.conf['rtr_setpoint']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self._controller[c] = self._defaults

            # store setpointItem into controller
            self._controller[c]['setpointItem'] = item.id()

            if not self._controller[c]['validated']:
                self.validate_controller(c)

            return self.update_item

        if 'rtr_actuator' in item.conf and not item.conf['rtr_actuator'].isdigit():
            logger.error("rtr: error in {0}, rtr_actuator need to be the controller number" . format(item.id()))
            return
        elif 'rtr_actuator' in item.conf:
            c = 'c' + item.conf['rtr_actuator']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self._controller[c] = self._defaults

            # store actuatorItem into controller
            self._controller[c]['actuatorItem'] = item.id()

            if not self._controller[c]['validated']:
                self.validate_controller(c)

            return

        if 'rtr_stop' in item.conf and not item.conf['rtr_stop'].isdigit():
            logger.error("rtr: error in {0}, rtr_stop need to be the controller number" . format(item.id()))
            return
        elif 'rtr_stop' in item.conf:

            # validate this optional Item
            if item._type is not 'bool':
                logger.error("rtr: error in {0}, rtr_stop Item need to be bool" . format(item.id()))
                return

            c = 'c' + item.conf['rtr_stop']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self._controller[c] = self._defaults

            # store stopItem into controller
            self._controller[c]['stopItem'] = item.id()

            return

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'plugin':
            if 'rtr_setpoint' in item.conf:
                c = 'c' + item.conf['rtr_setpoint']
                if self._controller[c]['validated'] \
                and ( self._controller[c]['stopItem'] is None or self._sh.return_item(self._controller[c]['stopItem'])() is True ):
                    self.pi_controller(c)

            if 'rtr_current' in item.conf:
                c = 'c' + item.conf['rtr_current']
                if self._controller[c]['validated'] \
                and ( self._controller[c]['stopItem'] is None or self._sh.return_item(self._controller[c]['stopItem'])() is True ):
                    self.pi_controller(c)

    def update_items(self):
        for c in self._controller.keys():
            if self._controller[c]['validated'] \
            and ( self._controller[c]['stopItem'] is None or self._sh.return_item(self._controller[c]['stopItem'])() is True ):
                self.pi_controller(c)

    def validate_controller(self, c):
        if self._controller[c]['setpointItem'] is None:
            return

        if self._controller[c]['currentItem'] is None:
            return

        if self._controller[c]['actuatorItem'] is None:
            return

        logger.info("rtr: all needed params are set, controller {0} validated" . format(c))
        self._controller[c]['validated'] = True

    def pi_controller(self, c):
        # w    = Führungsgröße (Sollwert) / command variable (setpoint)
        # x    = Regelgröße (Istwert) / controlled variable (current)
        # e    = Regelabweichung / control error
        # eSum = Summe der Regelabweichungen
        # y    = Stellgröße / manipulated variable
        # z    = Störgröße / disturbance variable
        # Kp   = Verstärkungsfaktor / proportional gain
        # Ki   = Integralfaktor / integral gain
        # Ta   = Abtastzeit in ms / scanning time
        # 
        # esum = esum + e
        # y = Kp * e + Ki * Ta * esum
        # 
        # p_anteil = error * p_gain;
        # error_integral = error_integral + error
        # i_anteil = error_integral * i_gain

        # calculate scanning time
        Ta = int(time.time()) - self._controller[c]['Tlast']
        logger.debug("rtr: {0} | Ta = Time() - Tlast | {1} = {2} - {3}" . format(c, Ta, (Ta + self._controller[c]['Tlast']), self._controller[c]['Tlast']))
        self._controller[c]['Tlast'] = int(time.time())

        # calculate control error
        w = self._sh.return_item(self._controller[c]['setpointItem'])
        x = self._sh.return_item(self._controller[c]['currentItem'])
        e = w() - x()
        logger.debug("rtr: {0} | e = w - x | {1} = {2} - {3}" . format(c, e, w(), x()))

        Kp = 1.0 / self._controller[c]['Kp']
        self._controller[c]['eSum'] = self._controller[c]['eSum'] + e * Ta
        i = self._controller[c]['eSum'] / (60.0 * self._controller[c]['Ki'])
        y = 100.0 * Kp * (e + i);

        if y > 100:
            y = 100
            self._controller[c]['eSum'] = (1.0 / Kp) * 60.0 * self._controller[c]['Ki']

        if y < 0 or self._controller[c]['eSum'] < 0:
            if y < 0:
                y = 0
            self._controller[c]['eSum'] = 0

        #self._controller[c]['eSum'] = self._controller[c]['eSum'] + e
        #y = self._controller[c]['Kp'] * e + self._controller[c]['Ki'] * (self._controller[c]['Ta']*1000) * self._controller[c]['eSum']

        logger.debug("rtr: {0} | eSum = {1}" . format(c, self._controller[c]['eSum']))
        logger.debug("rtr: {0} | y = {1}" . format(c, y))

        self._sh.return_item(self._controller[c]['actuatorItem'])(y)
        #logger.debug("rtr: _controller = {}" . format(dump(self._controller)))
