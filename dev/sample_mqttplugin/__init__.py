#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      <AUTHOR>                                  <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins using MQTT to run with SmartHomeNG
#  version 1.7 and upwards.
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
#
#########################################################################

from lib.model.mqttplugin import MqttPlugin
from lib.item import Items

from .webif import WebInterface


# If a needed package is imported, which might be not installed in the Python environment,
# add it to a requirements.txt file within the plugin's directory


class SampleMqttPlugin(MqttPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """

    PLUGIN_VERSION = '1.0.0'    # (must match the version specified in plugin.yaml), use '1.0.0' for your initial plugin Release

    def __init__(self, sh):
        """
        Initalizes the plugin.

        If you need the sh object at all, use the method self.get_sh() to get it. There should be almost no need for
        a reference to the sh object any more.

        Plugins have to use the new way of getting parameter values:
        use the SmartPlugin method get_parameter_value(parameter_name). Anywhere within the Plugin you can get
        the configured (and checked) value for a parameter by calling self.get_parameter_value(parameter_name). It
        returns the value in the datatype that is defined in the metadata.
        """

        # Call init code of parent class (MqttPlugin)
        super().__init__()

        # if you want to use an item to toggle plugin execution, enable the
        # definition in plugin.yaml and uncomment the following line
        #self._pause_item_path = self.get_parameter_value('pause_item')

        # Initialization code goes here

        # On initialization error use:
        #   self._init_complete = False
        #   return

        # if plugin should start even without web interface
        self.init_webinterface(WebInterface)

        return

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'run()'}))

        self.alive = True

        # let the plugin change the state of pause_item
        if self._pause_item:
            self._pause_item(False, self.get_fullname())

        # start subscription to all topics
        self.start_subscriptions()

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'stop()'}))
        self.alive = False

        # let the plugin change the state of pause_item
        if self._pause_item:
            self._pause_item(True, self.get_fullname())

        # this stops all schedulers the plugin has started.
        # you can disable/delete the line if you don't use schedulers
        self.scheduler_remove_all()

        # stop subscription to all topics
        self.stop_subscriptions()

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """
        # check for alive item
        if item.property.path == self._pause_item_path:
            self.logger.debug(f'alive item {item.property.path} registered')
            self._pause_item = item
            self.add_item(item, updating=True)
            return self.update_item

        if self.has_iattr(item.conf, 'foo_itemid'):
            self.logger.debug(f"parse item: {item.property.path}")

            # subscribe to topic for relay state
            # mqtt_id = self.get_iattr_value(item.conf, 'foo_itemid').upper()
            # payload_type = item.property.type
            # topic = 'shellies/shellyplug-' + mqtt_id + '/relay/0'
            # bool_values = ['off','on']
            # self.add_subscription(topic, payload_type, bool_values, item=item)

            # alternative:
            #   self.add_subscription(topic, payload_type, bool_values, callback=self.on_mqtt_message)
            # and implement callback:
            #   def on_mqtt_message(self, topic, payload, qos=None, retain=None):

            # todo
            # if interesting item for sending values:
            #   return self.update_item

            # if the item is changed in SmartHomeNG and shall update the mqtt device, enable:
            # return self.update_item


    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by SmartHomeNG.
        It should write the changed value out to the device (hardware/interface) that
        is managed by this plugin.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        # check for pause item
        if item is self._pause_item:
            if caller != self.get_shortname():
                self.logger.debug(f'pause item changed to {item()}')
                if item() and self.alive:
                    self.stop()
                elif not item() and not self.alive:
                    self.run()
            return

        if self.alive and caller != self.get_shortname():
            # code to execute if the plugin is not stopped
            # and only, if the item has not been changed by this this plugin:
            self.logger.info(f"Update item: {item.property.path}, item has been changed outside this plugin")

            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger.debug(
                    f"update_item was called with item {item.property.path} from caller {caller}, source {source} and dest {dest}")
            pass
