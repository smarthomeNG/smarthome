#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2019-      Martin Sinn                       m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import threading

from lib.module import Modules
from lib.model.smartplugin import SmartPlugin
from lib.shtime import Shtime
from lib.translation import translate as lib_translate

import os


class MqttPlugin(SmartPlugin):

    _item_values = {}                    # dict of dicts


    # Initialization of SmartPlugin class called by super().__init__() from the plugin's __init__() method
    def __init__(self):

        """
        Initialization Routine for the mqtt extension class to SmartPlugin
        """
        SmartPlugin.__init__(self)

        # get instance of MQTT module
        try:
            self.mod_mqtt = Modules.get_instance().get_module('mqtt')  # try/except to handle running in a core version that does not support modules
        except:
            self.mod_mqtt = None
        if self.mod_mqtt == None:
            self.logger.error("Module 'mqtt' not loaded. The plugin is not starting")
            self._init_complete = False
            return False

        self._subscribed_topics_lock = threading.Lock()
        self._subscribed_topics = {}  # subscribed topics (a dict of dicts)
        self._subscribe_current_number = 0  # current number of the subscription entry
        self._subscriptions_started = False

        # get broker configuration (for display in web interface)
        self.broker_config = self.mod_mqtt.get_broker_config()

        return True


    def translate(self, txt, vars=None, block=None):
        """
        Returns translated text for class SmartPlugin
        """
        txt = str(txt)
        if block:
            self.logger.warning(f"unsuported 3. parameter '{block}' used in translation function _( ... )")

        if self._add_translation is None:
            # test initially, if plugin has additional translations
            translation_fn = os.path.join(self._plugin_dir, 'locale.yaml')
            self._add_translation = os.path.isfile(translation_fn)

        if self._add_translation:
            return lib_translate(txt, vars, plugin_translations='plugin/'+self.get_shortname(), additional_translations='module/mqtt')
        else:
            return lib_translate(txt, vars, additional_translations='module/mqtt')


    def start_subscriptions(self):
        """
        Start subscription to all topics

        Should be called from the run method of a plugin
        """
        if self.mod_mqtt:
            with self._subscribed_topics_lock:
                for topic in self._subscribed_topics:
                    # start subscription to all items for this topic
                    for item_path in self._subscribed_topics[topic]:
                        self._start_subscription(topic, item_path)

            self._subscriptions_started = True
        return

    def stop_subscriptions(self):
        """
        Stop subscription to all topics

        Should be called from the stop method of a plugin
        """
        if self.mod_mqtt:
            with self._subscribed_topics_lock:
                for topic in self._subscribed_topics:
                    # stop subscription to all items for this topic
                    for item_path in self._subscribed_topics[topic]:
                        current = str(self._subscribed_topics[topic][item_path]['current'])
                        if item_path == '*no_item*':
                            self.logger.info(f"Unsubscribing from topic {topic}")
                        else:
                            self.logger.info(f"Unsubscribing from topic {topic} for item {item_path}")
                        self.mod_mqtt.unsubscribe_topic(self.get_shortname() + '-' + current, topic)
            self._subscriptions_started = False
        return

    def _start_subscription(self, topic, item_path):

        current = str(self._subscribed_topics[topic][item_path]['current'])
        qos = self._subscribed_topics[topic][item_path].get('qos', None)
        payload_type = self._subscribed_topics[topic][item_path].get('payload_type', None)
        callback = self._subscribed_topics[topic][item_path].get('callback', None)
        bool_values = self._subscribed_topics[topic][item_path].get('bool_values', None)
        if item_path == '*no_item*':
            self.logger.info(f"Subscribing to topic {topic}, payload_type '{payload_type}' - callback={callback}")
        else:
            self.logger.info(f"Subscribing to topic {topic}, payload_type '{payload_type}' - for item '{item_path}'")
        self.mod_mqtt.subscribe_topic(self.get_shortname() + '-' + current, topic, callback=callback,
                                      qos=qos, payload_type=payload_type, bool_values=bool_values)
        return

    def add_subscription(self, topic, payload_type, bool_values=None, item=None, callback=None):
        """
        Add mqtt subscription to subscribed_topics list

        subscribing is done directly, if subscriptions have been started by self.start_subscriptions()

        :param topic:        topic to subscribe to
        :param payload_type: payload type of the topic (for this subscription to the topic)
        :param bool_values:  bool values (for this subscription to the topic)
        :param item:         item that should receive the payload as value. Used by the standard handler (if no callback function is specified)
        :param callback:     a plugin can provide an own callback function, if special handling of the payload is needed
        :return:
        """

        with self._subscribed_topics_lock:

            # test if topic is new
            if not self._subscribed_topics.get(topic, None):
                self._subscribed_topics[topic] = {}
            # add this item to topic
            if item is None:
                item_path = '*no_item*'
            else:
                item_path = item.property.path
            self._subscribed_topics[topic][item_path] = {}
            self._subscribe_current_number += 1
            self._subscribed_topics[topic][item_path]['current'] = self._subscribe_current_number
            self._subscribed_topics[topic][item_path]['item'] = item
            self._subscribed_topics[topic][item_path]['qos'] = None
            self._subscribed_topics[topic][item_path]['payload_type'] = payload_type
            if callback:
                self._subscribed_topics[topic][item_path]['callback'] = callback
            else:
                self._subscribed_topics[topic][item_path]['callback'] = self._on_mqtt_message
            self._subscribed_topics[topic][item_path]['bool_values'] = bool_values

        if self._subscriptions_started:
            # directly subscribe to added subscription, if subscribtions are started
            self._start_subscription(topic, item_path)
        return


    def publish_topic(self, topic, payload, item=None, qos=None, retain=False, bool_values=None):
        """
        Publish a topic to mqtt

        :param topic:        topic to publish
        :param payload:      payload to publish
        :param item:         item (if relevant)
        :param qos:          qos for this message (optional)
        :param retain:       retain flag for this message (optional)
        :param bool_values:  bool values (for publishing this topic, optional)
        :return:
        """
        self.mod_mqtt.publish_topic(self.get_shortname(), topic, payload, qos, retain, bool_values)
        if item is not None:
            self.logger.dbghigh(f"publish_topic: Item '{item.id()}' -> topic '{topic}', payload '{payload}', QoS '{qos}', retain '{retain}'")
            # Update dict for periodic updates of the web interface
            self._update_item_values(item, payload)
        else:
            self.logger.dbghigh(f"publish_topic: topic '{topic}', payload '{payload}', QoS '{qos}', retain '{retain}'")
        return


    # ----------------------------------------------------------------------------------------
    #  methods to handle the broker connection
    # ----------------------------------------------------------------------------------------

    _broker_version = '?'
    _broker = {}
    broker_config = {}
    broker_monitoring = False


    def get_broker_info(self):
        if self.mod_mqtt:
            (self._broker, self.broker_monitoring) = self.mod_mqtt.get_broker_info()


    def broker_uptime(self):
        """
        Return formatted uptime of broker
        """
        if self.shtime is None:
            self.shtime = Shtime.get_instance()
        try:
            return self.shtime.seconds_to_displaystring(int(self._broker['uptime']))
        except Exception as e:
            return '-'


    def mqtt_init(self):
        """
        Dummy method - should not be called any more
        :return: Bool value True
        :rtype: bool
        """
        self.logger.warning("'mqtt_init()' method called. it is not used anymore. The Plugin should remove the call to mqtt_init(), use 'super.__init__()' instead")
        pass
        return True

    # -----------------------------------------------------------------------

    def _on_mqtt_message(self, topic, payload, qos=None, retain=None):
        """
        Callback function to handle received messages

        :param topic:
        :param payload:
        :param qos:
        :param retain:
        """
        self.logger.debug(f"_on_mqtt_message: Received topic '{topic}', payload '{payload} (type {type(payload)})', QoS '{qos}', retain '{retain}' ")

        # get item for topic
        if self._subscribed_topics.get(topic, None):
            # at least 1 item has subscribed to this topic
            for item_path in self._subscribed_topics[topic]:
                item = self._subscribed_topics[topic][item_path].get('item', None)
                if item != None:
                    try:
                        log_info = (float(payload) != float(item()))
                    except:
                        log_info = (str(payload) != str(item()))
                    if log_info:
                        self.logger.dbghigh(f"_on_mqtt_message: Received topic '{topic}', payload '{payload}' (item-type {item.type()}), QoS '{qos}', retain '{retain}' for item '{item.id()}' (value={item()})")
                    else:
                        self.logger.debug(f"_on_mqtt_message: Received topic '{topic}', payload '{payload}' (item-type {item.type()}), QoS '{qos}', retain '{retain}' for item '{item.id()}' (value={item()})")
                    item(payload, self.get_shortname())
                    # Update dict for periodic updates of the web interface
                    self._update_item_values(item, payload)
        else:
            self.logger.error(f"_on_mqtt_message: No definition found for subscribed topic '{topic}'")
        return


    def _update_item_values(self, item, payload):
        """
        Update dict for periodic updates of the web interface

        :param item:
        :param payload:
        """
        if not self._item_values.get(item.id()):
            self._item_values[item.id()] = {}
        if isinstance(payload, bool):
            self._item_values[item.id()]['value'] = str(payload)
        else:
            self._item_values[item.id()]['value'] = payload
        self._item_values[item.id()]['last_update'] = item.last_update().strftime('%d.%m.%Y %H:%M:%S')
        self._item_values[item.id()]['last_change'] = item.last_change().strftime('%d.%m.%Y %H:%M:%S')
        return


from lib.model.smartplugin import SmartPluginWebIf
# try:
#     from jinja2 import Environment, FileSystemLoader
# except:
#     pass
# from lib.module import Modules


class MqttPluginWebIf(SmartPluginWebIf):


    def translate(self, txt, vars=None):
        """
        Returns translated text for class SmartPluginWebIf

        This method extends the jinja2 template engine _( ... ) -> translate( ... )
        """
        txt = str(txt)

        if self.plugin._add_translation is None:
            # test initially, if plugin has additional translations
            translation_fn = os.path.join(self.plugin._plugin_dir, 'locale.yaml')
            self.plugin._add_translation = os.path.isfile(translation_fn)

        if self.plugin._add_translation:
            return lib_translate(txt, vars, plugin_translations='plugin/' + self.plugin.get_shortname(), module_translations='module/http', additional_translations='module/mqtt')
        else:
            return lib_translate(txt, vars, module_translations='module/http', additional_translations='module/mqtt')


