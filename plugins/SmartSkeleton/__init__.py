#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
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
from lib.model.smartplugin import SmartPlugin


logger = logging.getLogger(__name__)


class PluginName(SmartPlugin, PluginSensor, PluginAktor):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides the update functions for the service
    """
    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION = "0.0.1"

    def __init__(self, smarthome, cycle=300):
	    """
        Initalizes the plugin. The parameters for this method are pulled from the entry in plugin.conf.

        :param cycle:              Update cycle in seconds

        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Init ... Plugin')

        self._cycle = int(cycle)
        self._sh = smarthome

    def run(self):
        """
        Run method for the plugin
        """
        self._sh.scheduler.add(__name__, self._update_loop, prio=5, cycle=self._cycle, offset=2)
        self.alive = True
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        """
        Stop method for the plugin
        """
        self.alive = False

    def _update_loop(self):
        """
        Starts the update loop for all known items.
        """
		pass

    def parse_item(self, item):
    	"""
        Default plugin parse_item method. Is called when the plugin is initialized. 
        Selects each item corresponding to the device id and adds it to an internal array.
        
        :param item: The item to process.
        """
        plugin_attr = 'plugin_attr'
        if self.has_iattr(item.conf, plugin_attr):
        	attr_value = self.get_iattr_value(item.conf, plugin_attr)
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

	def update_item(self, item, caller=None, source=None, dest=None):
        """
        Write items values - in case they were changed from somewhere else than this plugin to the Device.

        :param item: item to be updated towards the Device
        """
        if caller != self.__class__.__name__:
            logger.info("update item: {0}".format(item.id()))

class PluginNameSensor():
    """
    The Item represents a sensor. I.e. some external device provides data to update the item. Data gets polled any cycle seconds.
    """
    _sensor_items = {}
    _logics_to_trigger = {}
        
    
    def __init__(self, smarthome, cycle=300):
	    """
        Initalizes the plugin. The parameters for this method are pulled from the entry in plugin.conf.
        :param cycle:              Update cycle in seconds
        """
        self._cycle = int(cycle)
        self._sh = smarthome

    def run(self):
        """
        Run method for the plugin
        """
        self._sh.scheduler.add(__name__, self._update_loop, prio=5, cycle=self._cycle, offset=2)
        self.alive = True

    def stop(self):
        """
        Stop method for the plugin
        """
        self.alive = False

    def parse_item(self, item):
    	"""
        Default plugin parse_item method. Is called when the plugin is initialized. 
        Selects each item corresponding to the device id and adds it to an internal array.
        :param item: 	The item to process.
        """
        plugin_sensor_attr = 'my_sensor_attr'
        if self.has_iattr(item.conf, plugin_sensor_attr):
        	sensor_identifier = self.get_iattr_value(item.conf, plugin_sensor_attr)
            logger.debug("Sensor item [{0}] is listening to device sensor: {1}".format(item, sensor_identifier))
            self._sensor_items[sensor_identifier] = item

    def parse_logic(self, logic):
        plugin_sensor_attr = 'my_sensor_attr'
		if plugin_sensor_attr in logic.conf:
            sensor_identifier = logic.conf[plugin_sensor_attr]
            logger.debug('Logic [{0}] is listening to device sensor: {1}'.format(logic.name, sensor_identifier))
            self._logics_to_trigger[sensor_identifier] = logic
			

    def _update_loop(self):
        """
        Starts the update loop for all items and logics under attention of this plugin.
        """
        self.logger.debug('Starting update loop for instance %s' % self._identifier )
        for item in self._sensor_items:
            if not self.alive:
                return
            _update(item)
        for logic in self._logics_to_trigger:
            if not self.alive:
                return
            logic.trigger('MQTT', msg.topic, msg.payload)

	def _update(self, item):
        """
        Updates information on diverse items

        :param item: item to be updated
        """
        
		item(value, 'MQTT')
			
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = PluginName('smarthome-dummy')
    myplugin.run()
