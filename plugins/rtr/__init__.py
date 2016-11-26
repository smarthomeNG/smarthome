#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 TCr82 @ KNX-User-Forum        http://knx-user-forum.de/
#  Copyright 2016 Bernd Meiners                     Bernd.Meiners@mail.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
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
#  along with SmartHomeNG If not, see <http://www.gnu.org/licenses/>.
#########################################################################

# Some useful docs:
# http://www.rn-wissen.de/index.php/Regelungstechnik#PI-Regler
# http://de.wikipedia.org/wiki/Regler#PI-Regler
# http://www.honeywell.de/fp/regler/Reglerparametrierung.pdf

import logging
from lib.model.smartplugin import SmartPlugin
import time


class RTR(SmartPlugin):
    """
    Main class of the rtr plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.2.3"

    _controller = {}
    _defaults = {'currentItem' : None,
                'setpointItem' : None,
                'actuatorItem' : None,
                'stopItem' : None,
                'eSum' : 0,
                'Kp' : 0,
                'Ki' : 0,
                'Tlast' : time.time(),
                'validated' : False}

    def __init__(self, sh, default_Kp = 5, default_Ki = 240):
        """
        Initalizes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

        :param sh:  The instance of the smarthome object, save it for later references
        """
        self._sh = sh
        # get a unique logger for the plugin and provide it internally
        self.logger = logging.getLogger(__name__) 
        
        self.logger.debug("init method called")
        
        # preset the controller defaults
        self._default_Kp = default_Kp
        self._default_Ki = default_Ki
        self._calc_interval = 60

        self._defaults['Tlast'] = time.time()
        self._defaults['Kp'] = default_Kp
        self._defaults['Ki'] = default_Ki
        
    def run(self):
        """
        Run method for the plugin
        """        
        self.logger.debug("run method called")
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug("stop method called")
        self.alive = False

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.

        :param item: The item to process.
        """
        if self.has_iattr(item.conf, 'rtr_current'):
            if not item.conf['rtr_current'].isdigit():
                self.logger.error("rtr: error in {0}, rtr_current need to be the controller number" . format(item.id()))
                return
            c = 'c' + item.conf['rtr_current']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self.logger.debug("rtr: controller '{0}' does not exist yet. Init with default values" . format(c))
                self._controller[c] = self._defaults.copy()

            # store curstrentItem into controller
            self._controller[c]['currentItem'] = item.id()
            self.logger.info("rtr: controller '{}' was set to {}". format(c, self._controller[c]['currentItem']))

            if not self.has_iattr(item.conf, 'rtr_Kp'):
                self.logger.info("rtr: missing rtr_Kp in {0}, setting to default: {1}" . format(item.id(), self._default_Kp))
                self._controller[c]['Kp'] = self._default_Kp
            else:
                self._controller[c]['Kp'] = float(item.conf['rtr_Kp'])

            if not self.has_iattr(item.conf, 'rtr_Ki'):
                self.logger.info("rtr: missing rtr_Ki in {0}, setting to default: {1}" . format(item.id(), self._default_Ki))
                self._controller[c]['Ki'] = self._default_Ki
            else:
                self._controller[c]['Ki'] = float(item.conf['rtr_Ki'])

            if 'rtr.scheduler' not in self._sh.scheduler:
                self._sh.scheduler.add('rtr.scheduler', self.update_items, prio=5, cycle=int(self._calc_interval))

            if not self._controller[c]['validated']:
                self.validate_controller(c)
            
            return

        if self.has_iattr(item.conf, 'rtr_setpoint'):
            if not item.conf['rtr_setpoint'].isdigit():
                self.logger.error("rtr: error in {0}, rtr_setpoint need to be the controller number" . format(item.id()))
                return

            c = 'c' + item.conf['rtr_setpoint']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self.logger.debug("rtr: controller '{0}' does not exist yet. Init with default values" . format(c))
                self._controller[c] = self._defaults.copy()

            # store setpointItem into controller
            self._controller[c]['setpointItem'] = item.id()

            if not self._controller[c]['validated']:
                self.validate_controller(c)

            return self.update_item

        if self.has_iattr(item.conf, 'rtr_actuator'):
            if not item.conf['rtr_actuator'].isdigit():
                self.logger.error("rtr: error in {0}, rtr_actuator need to be the controller number" . format(item.id()))
                return

            c = 'c' + item.conf['rtr_actuator']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self.logger.debug("rtr: controller '{0}' does not exist yet. Init with default values" . format(c))
                self._controller[c] = self._defaults.copy()

            # store actuatorItem into controller
            self._controller[c]['actuatorItem'] = item.id()

            if not self._controller[c]['validated']:
                self.validate_controller(c)

            return

        if self.has_iattr(item.conf, 'rtr_stop'):
            if not item.conf['rtr_stop'].isdigit():
                self.logger.error("rtr: error in {0}, rtr_stop need to be the controller number" . format(item.id()))
                return

            # validate this optional Item
            if item._type is not 'bool':
                self.logger.error("rtr: error in {0}, rtr_stop Item need to be bool" . format(item.id()))
                return

            c = 'c' + item.conf['rtr_stop']

            # init controller with defaults when it not exist
            if c not in self._controller:
                self.logger.debug("rtr: controller '{0}' does not exist yet. Init with default values" . format(c))
                self._controller[c] = self._defaults.copy()

            # store stopItem into controller
            self._controller[c]['stopItem'] = item.id()

            return

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        write item's values

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
    
        self.logger.debug("rtr: update item {}, from caller = {}, with source={} and dest={}" . format(item.id(), caller, source, dest))
        if item() and caller != 'plugin':
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
        """ this is the callback function for the scheduler """
        for c in self._controller.keys():
            if self._controller[c]['validated'] \
            and ( self._controller[c]['stopItem'] is None or self._sh.return_item(self._controller[c]['stopItem'])() is True ):
                self.pi_controller(c)

    def validate_controller(self, c):
        """ this function checks wether the needed parameters are set for a given controller 
        :param c: controller to be checked
        """
        if self._controller[c]['setpointItem'] is None:
            return

        if self._controller[c]['currentItem'] is None:
            return

        if self._controller[c]['actuatorItem'] is None:
            return

        self.logger.info("rtr: all needed params are set, controller {0} validated" . format(c))
        self._controller[c]['validated'] = True

    def pi_controller(self, c):
        """ 
        this function calculates a new actuator value for a given controller
        
        w    = setpoint value / Führungsgröße (Sollwert)
        x    = current value / Regelgröße (Istwert)
        e    = control error / Regelabweichung
        eSum = sum of error values / Summe der Regelabweichungen
        y    = output to actuator / Stellgröße
        z    = disturbance variable / Störgröße
        Kp   = proportional gain / Verstärkungsfaktor
        Ki   = integral gain / Integralfaktor
        Ta   = scanning time (given in seconds)/ Abtastzeit
         
        esum = esum + e
        y = Kp * e + Ki * Ta * esum
        
        p_anteil = error * p_gain;
        error_integral = error_integral + error
        i_anteil = error_integral * i_gain

        :param c: controller for the calculation
        """

        # calculate scanning time
        Ta = int(time.time()) - self._controller[c]['Tlast']
        self.logger.debug("rtr: {0} | Ta = Time() - Tlast | {1} = {2} - {3}" . format(c, Ta, (Ta + self._controller[c]['Tlast']), self._controller[c]['Tlast']))
        self._controller[c]['Tlast'] = int(time.time())

        # calculate control error
        w = self._sh.return_item(self._controller[c]['setpointItem'])
        x = self._sh.return_item(self._controller[c]['currentItem'])
        e = w() - x()
        self.logger.debug("rtr: {0} | e = w - x | {1} = {2} - {3}" . format(c, e, w(), x()))

        Kp = 1.0 / self._controller[c]['Kp']
        self._controller[c]['eSum'] = self._controller[c]['eSum'] + e * Ta
        i = self._controller[c]['eSum'] / (60.0 * self._controller[c]['Ki'])
        y = 100.0 * Kp * (e + i);

        # limit the new actuator value to [0 ... 100]
        if y > 100:
            y = 100
            self._controller[c]['eSum'] = (1.0 / Kp) * 60.0 * self._controller[c]['Ki']

        if y < 0 or self._controller[c]['eSum'] < 0:
            if y < 0:
                y = 0
            self._controller[c]['eSum'] = 0

        self.logger.debug("rtr: {0} | eSum = {1}" . format(c, self._controller[c]['eSum']))
        self.logger.debug("rtr: {0} | y = {1}" . format(c, y))

        self._sh.return_item(self._controller[c]['actuatorItem'])(y)
