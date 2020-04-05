#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  MQTT is a machine-to-machine (M2M)/"Internet of Things" connectivity
#  protocol. It was designed as an extremely lightweight publish/subscribe
#  messaging transport.
#
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
#########################################################################


import threading
import logging
import json
import os
import socket    # for gethostbyname
import inspect

import paho.mqtt.client as mqtt

from lib.model.module import Module
from lib.module import Modules
from lib.shtime import Shtime
from lib.utils import Utils


class Mqtt(Module):
    version = '1.7.0'
    longname = 'MQTT module for SmartHomeNG'

    __plugif_CallbackTopics = {}         # for plugin interface
    __plugif_Sub = None

    _broker_version = '?'
    _broker = {}

    def __init__(self, sh):
        """
        Initialization Routine for the module
        """
        # TO DO: Shortname anders setzen (oder warten bis der Modul Loader es beim Laden setzt)
        self._shortname = self.__class__.__name__
        self._shortname = self._shortname.lower()

        self.logger = logging.getLogger(__name__)
        self._sh = sh
        self.shtime = Shtime.get_instance()
        self.logger.debug("Module '{}': Initializing".format(self._shortname))


        # get the parameters for the plugin (as defined in metadata plugin.yaml):
        self.logger.debug("Module '{}': Parameters = '{}'".format(self._shortname, dict(self._parameters)))
        try:
            self.broker_hostname = self._parameters['broker_host']
            self.broker_port = self._parameters['broker_port']
            self.broker_monitoring = self._parameters['broker_monitoring']
            self.qos = self._parameters['qos']
            self.last_will_topic = self._parameters['last_will_topic']
            self.last_will_payload = self._parameters['last_will_payload']
            self.birth_topic = self._parameters['birth_topic']
            self.birth_payload = self._parameters['birth_payload']
            self.bool_values = self._parameters['bool_values']
            # self.publish_items = self._parameters['publish_items']
            # self.items_topic_prefix = self._parameters['items_topic_prefix']
            self.username = self._parameters['user']
            self.password = self._parameters['password']

            # self.tls = self._parameters['tls']
            # self.ca_certs = self._parameters['ca_certs']
            # self.acl = self._parameters['acl'].lower()
        except KeyError as e:
            self.logger.critical(
                "Module '{}': Inconsistent module (invalid metadata definition: {} not defined)".format(self._shortname, e))
            self._init_complete = False
            return

        # resolve broker name, is no ip address is specified
        try:
            self.broker_ip = socket.gethostbyname(self.broker_hostname)
        except Exception as e:
            self.logger.error("Error resolving '{}': {}".format(self.broker_hostname, e))
            self._init_complete = False
            return
        if self.broker_ip == self.broker_hostname:
            self.broker_hostname = ''

        # handle last_will and birth topic configuration
        if (self.last_will_topic != '') and (self.last_will_topic [-1] == '/'):
            self.last_will_topic = self.last_will_topic[:-1]
        if self.birth_topic == '':
            self.birth_topic = self.last_will_topic
        else:
            if self.birth_topic [-1] == '/':
                self.birth_topic = self.birth_topic[:-1]

        # if self.items_topic_prefix [-1] != '/':
        #     self.items_topic_prefix = self.items_topic_prefix + '/'


        if self.password == '':
            self.password = None

        # tls ...
        # ca_certs ...

        # _subscribed_topics is a datastructure to keep track of subscribed topics
        # and the needed additional information
        #  - who subscribed to the topic
        #  - kind of subscriber (logic, plugin, ...)
        #  - datatype of payload
        #
        # <topic1>:
        #     <subscriber1_name>:
        #         subsciber_type: 'logic'
        #         callback: 'logic1name'
        #         payload_type: 'str'
        #     <subscriber2_name>:
        #         subsciber_type: 'logic'
        #         callback: 'logic2name'
        #         payload_type: 'dict'
        # <topic2>:
        #     <subscriber3_name>:
        #         subsciber_type: 'plugin'
        #         callback: obj_callback3
        #         payload_type: 'str'
        #     <subscriber4_name>:
        #

        self._subscribed_topics_lock = threading.Lock()
        self._subscribed_topics = {}


        self.topics = {}  # subscribed topics
        self.logicpayloadtypes = {}  # payload types for subscribed topics for triggering logics


        # ONLY used for multiinstance handling of plugins?
        # # needed because self.set_attr_value() can only set but not add attributes
        # self.at_instance_name = self.get_instance_name()
        # if self.at_instance_name != '':
        #     self.at_instance_name = '@' + self.at_instance_name


        self._connected = False
        self._connect_result = ''

        # tls ...
        # ca_certs ...

        if not self._connect_to_broker():
            self._init_complete = False
            return


        ip = _get_local_ipv4_address()


    def start(self):
        """
        This method starts the mqtt module

        It is called by lib.module and should not be called otherwise.
        """
        # self.alive = True
        if (self.birth_topic != '') and (self.birth_payload != ''):
            self._client.publish(self.birth_topic, self.birth_payload, self.qos, retain=True)
        self._client.loop_start()
        self.logger.debug("MQTT client loop started")
        # set the name of the paho thread for this plugin instance
        try:
            self._client._thread.name = "paho_" + self.longname
        except:
            self.logger.warning("Unable to set name for paho thread")


    def stop(self):
        """
        This method stops the mqtt module

        It is called by lib.module and should not be called otherwise.
        """
        #        self.logger.debug("Module '{}': Shutting down".format(self.shortname))
        self._client.loop_stop()
        self.logger.debug("MQTT client loop stopped")
        self._disconnect_from_broker()
        # self.alive = False


    # ----------------------------------------------------------------------------------------
    #  methods to handle the broker connection
    # ----------------------------------------------------------------------------------------

    def _connect_to_broker(self):
        """
        Establish connection to MQTT broker
        """
        clientname = os.uname()[1] + '.MQTT-module'
        self.logger.info("Connecting to broker '{}:{}'. Starting mqtt client '{}'".format(self.broker_ip, self.broker_port, clientname))
        self._client = mqtt.Client(client_id=clientname)


        # set testament, if configured
        if (self.last_will_topic != '') and (self.last_will_payload != ''):
            retain = False
            if (self.birth_topic != '') and (self.birth_payload != ''):
                retain = True
            self._client.will_set(self.last_will_topic, self.last_will_payload, self.qos, retain=retain)
            self.logger.debug("- Last will set to topic '{}' and payload '{}' with retain set to '{}'".format(self.last_will_topic,self.last_will_payload, retain))

        if self.username != '':
            self._client.username_pw_set(self.username, self.password)
            self.logger.debug("- Using broker login information user '{}' and password".format(self.username))
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_log = self._on_mqtt_log
        self._client.on_message = self._on_mqtt_message
        try:
            self._client.connect(self.broker_ip, self.broker_port, 60)
            self.logger.debug("- Sending connect request to broker")
        except Exception as e:
            self.logger.error('Connection error: {0}'.format(e))
            return False
        return True


    def _disconnect_from_broker(self):
        """
        Stop all communication with MQTT broker
        """
        self._unsubscribe_broker_infos()

        for topic in self.topics:
            item = self.topics[topic]
            self.logger.debug("Unsubscribing topic '{}' for item '{}'".format(str(topic), str(item.id())))
            self._client.unsubscribe(topic)

        self.logger.info("Stopping mqtt client '{}'. Disconnecting from broker.".format(self._client._client_id.decode('utf-8')))
        if (self.last_will_topic != '') and (self.last_will_payload != ''):
            if (self.birth_topic != '') and (self.birth_payload != ''):
                self._client.publish(self.last_will_topic, self.last_will_payload + ' (shutdown)', self.qos, retain=True)
                self.logger.debug("- Disconnect: Last will sent with topic '{}' and payload '{}' and retain set to '{}'".format(self.last_will_topic,self.last_will_payload, True))

        self._client.loop_stop()
        self._connected = False
        self._client.disconnect()


    def _log_brokerinfo(self, payload):
        """
        Log info about broker connection
        """
        payload = self.cast_from_mqtt('str', payload)
        if self.broker_hostname == '':
            address = str(self.broker_ip)+':'+str(self.broker_port)
        else:
            address = self.broker_hostname + ' (' + str(self.broker_ip)+':'+str(self.broker_port) + ')'
        self.logger.info("Connected to broker '{}' at address {}".format( str(payload), address ))


    def broker_uptime(self):
        """
        Return formatted uptime of broker
        """
        try:
            return self.shtime.seconds_to_displaysting(int(self._broker['uptime']))
        except:
            return '-'


    def get_broker_info(self):
        """
        Return the collected broker information

        :return: Broker information
        :rtype: dict
        """
        return (self._broker, self.broker_monitoring)


    def get_broker_config(self):
        """
        Return the configuration of the broker connection

        :return: Broker configuration
        :rtype: dict
        """
        broker_config = {}
        if self.broker_hostname:
            broker_config['host'] = self.broker_hostname
        elif self.broker_ip == '127.0.0.1':
            broker_config['host'] = 'localhost'
        else:
            broker_config['host'] = self.broker_ip
        broker_config['port'] = self.broker_port
        broker_config['user'] = self.username
        broker_config['password'] = '-'
        broker_config['qos'] = self.qos
        # broker_config['acl'] = self.acl
        return broker_config


    # ----------------------------------------------------------------------------------------
    #  methods to handle mqtt
    # ----------------------------------------------------------------------------------------

    def _add_subscription_definition(self, topic, subscription_source, subscriber_type, callback, payload_type, bool_values):
        """
        Add a subscription definition to a defined topic in the _subscribed_topics data

        :param topic:
        :param subscription_source:
        :param subscriber_type:
        :param callback:
        :param payload_type:
        """
        if self._subscribed_topics[topic].get(subscription_source, None):
            self.logger.info("_add_subscription_definition: Subscription to topic '{}' for logic '{}' already exists, overwriting it".format(topic, subscription_source))
        self._subscribed_topics[topic][subscription_source] = {}
        self._subscribed_topics[topic][subscription_source]['subscriber_type'] = subscriber_type.lower()
        self._subscribed_topics[topic][subscription_source]['callback'] = callback
        self._subscribed_topics[topic][subscription_source]['payload_type'] = payload_type
        self._subscribed_topics[topic][subscription_source]['bool_values'] = bool_values
        self.logger.info("_add_subscription_definition: {} '{}' is subscribing to topic '{}'".format(subscriber_type, subscription_source, topic))
        return


    def subscribe_topic(self, source, topic, callback=None, qos=None, payload_type='str', bool_values=None):
        """
        method to subscribe to a topic

        this function is to be called from plugins, which are utilizing the mqtt module

        :param source:       name of plugin or logic which want's to publish a topic
        :param topic:        topic to subscribe to
        :param qos:          Optional: quality of service (0-2) otherwise the default of the mqtt plugin will be used
        :param payload_type: Optional: 'str', 'num', 'bool', 'list', 'dict', 'scene', 'bytes'
        :param callback:     plugin callback function or name of logic for logics-callbacks
        :type source:        str
        :type topic:         str
        :type qos:           int
        :type payload_type:  str
        :type callback:      str (if logic) or function (if called from MqttPlugin class)
        """
        if bool_values is None:
            bool_values = self.bool_values

        source_type = self._get_caller_type()
        self.logger.info("'{}()' - called from {} by '{}()'".format(inspect.stack()[0][3], source_type, inspect.stack()[1][3]))
        #self.logger.debug("subscribe_topic: inspect.stack()[2][3] = '{}', inspect.stack()[3][3] = '{}'".format(inspect.stack()[2][3], inspect.stack()[3][3]))

        if qos == None:
            qos = self.qos

        if bool_values:
            if not (isinstance(bool_values, list) and len(bool_values)==2):
                self.logger.warning("subscribe_topic: topic '{}', source '{}': Invalid bool_values specified ('{}') - Ignoring bool_values".format( topic, source, bool_values))

        if not payload_type.lower() in ['str', 'num', 'bool', 'list', 'dict', 'scene', 'bytes']:
            payload_type = 'str'
            self.logger.warning("Invalid payload-datatype specified for {} '{}', ignored".format(source_type, callback))

        if not self._subscribed_topics.get(topic, None):
            self.logger.info("subscribe_topic: NO MQTT Subscription to topic '{}' exists yet, adding topic".format(topic))
            # lock
            self._subscribed_topics_lock.acquire()
            try:
                # add topic
                self._subscribed_topics[topic] = {}
                # add subscription definition
                self._add_subscription_definition(topic, source, source_type, callback, payload_type, bool_values)
            finally:
                # unlock
                self._subscribed_topics_lock.release()

            # subscribe to topic
            result, mid = self._client.subscribe(topic, qos=qos)
            self.logger.info("subscribe_topic: mqtt module is subscribing to topic '{}' with qos={} at broker (result={}, mid={})".format(topic, qos, result, mid))
        else:
            self.logger.info("subscribe_topic: A MQTT Subscription to topic '{}' already exists".format(topic))
            # lock
            self._subscribed_topics_lock.acquire()
            try:
                # add subscription definition
                self._add_subscription_definition(topic, source, source_type, callback, payload_type, bool_values)
            finally:
                # unlock
                self._subscribed_topics_lock.release()
        return


    def unsubscribe_topic(self, source, topic):
        """
        method to unsubscribe from a topic

        this function is to be called from plugins, which are utilizing the mqtt module

        :param source:       name of logic which want's to publish a topic
        :param topic:        topic to unsubscribe from
        """
        source_type = self._get_caller_type()
        self.logger.info("'{}()' - called from {} by '{}()'".format(inspect.stack()[0][3], source_type, inspect.stack()[1][3]))

        if not self._subscribed_topics.get(topic, None):
            # the topic is not subscribed
            self.logger.info("unsubscribe_topic: NO MQTT Subscription to topic '{}' exists".format(topic))
            return

        if not self._subscribed_topics[topic].get(source, None):
            # the topic is not subscribed by this source
            self.logger.info("unsubscribe_topic: Topic '{}' is not subscribed by '{}'".format(topic, source))
            return

        self.logger.debug("unsubscribe_topic: Subscription to topic '{}' for '{}' is removed".format(topic, source))
        # lock
        self._subscribed_topics_lock.acquire()
        try:
            # delete subscription-source for this topic
            del self._subscribed_topics[topic][source]
            if self._subscribed_topics[topic] == {}:
                # unsubscribe on broker, if no source is subscribing the topic any more
                del self._subscribed_topics[topic]
                self._client.unsubscribe(topic)
        finally:
            # unlock
            self._subscribed_topics_lock.release()

        return


    def _trigger_logic(self, subscription_dict, topic, payload):
        """
        This method is called by on_mqtt_message to trigger the right logic

        :param subscription_dict:
        :param topic:             Topic of message received via mqtt
        :param payload:           Payload of message received via mqtt

        :return:
        :rtype: bool
        """
        datatype = subscription_dict.get('payload_type', 'foo')
        bool_values = subscription_dict.get('bool_values', None)
        payload = self.cast_from_mqtt(datatype, payload, bool_values)
        logic = subscription_dict.get('callback', None)

        subscription_found = False
        if logic:
            self.logger.info("_trigger_logic: Using topic '{}', payload '{} (type {})' for triggering logic '{}'".format(topic, payload, datatype, logic))
            self._sh.logics.trigger_logic(logic, source='mqtt', by=topic, value=payload)
            subscription_found = True

        return subscription_found


    def _callback_to_plugin(self, plugin_name, subscription_dict, topic, payload, qos, retain):
        """
        This method is called by on_mqtt_message to callback the rigth plugin

        :param plugin_name:       Name of the plugin with the callback function
        :param subscription_dict:
        :param topic:             Topic of message received via mqtt
        :param payload:           Payload of message received via mqtt
        :param qos:
        :param retain:

        :return:
        :rtype: bool
        """
        datatype = subscription_dict.get('payload_type', 'foo')
        bool_values = subscription_dict.get('bool_values', None)
        payload = self.cast_from_mqtt(datatype, payload, bool_values)
        plugin = subscription_dict.get('callback', None)

        try:
            subscription_found = False
            if plugin:
                self.logger.info("_callback_to_plugin: Using topic '{}', payload '{}' (type {}) for callback to plugin '{}' {}".format(topic, payload, datatype, plugin_name, plugin))
                #self._sh.logics.trigger_logic(logic, source='mqtt', by=topic, value=payload)
                plugin(topic, payload, qos, retain)
                subscription_found = True
            else:
                self.logger.error("_callback_to_plugin: callback for plugin '{}' not defined".format(plugin_name))
        except Exception as e:
            self.logger.error("_callback_to_plugin Exception {}".format(e))

        return subscription_found


    def _on_mqtt_message(self, client, userdata, message):
        """
        Callback function to handle received messages for items and logics

        :param client:    the client instance for this callback
        :param userdata:  the private user data as set in Client() or userdata_set()
        :param message:   an instance of MQTTMessage.
                          This is a class with members topic, payload, qos, retain.
        """
        self.logger.debug( "_on_mqtt_message: RECEIVED topic '{}', payload '{}, QoS '{}', retain '{}'".format(message.topic, message.payload, message.qos, message.retain))

        # lock
        self._subscribed_topics_lock.acquire()
        try:
            # look for subscriptions to the received topic
            subscription_found = False
            for topic in self._subscribed_topics:
                if topic == message.topic:
                    topic_dict = self._subscribed_topics[topic]

                    for subscription in topic_dict:
                        self.logger.info("_on_mqtt_message: subscription '{}': {}".format(subscription, topic_dict[subscription]))
                        subscriber_type = topic_dict[subscription].get('subscriber_type', None)
                        if subscriber_type == 'plugin':
                            subscription_found = self._callback_to_plugin(subscription, topic_dict[subscription], message.topic, message.payload, message.qos, message.retain)
                        elif subscriber_type == 'logic':
                            subscription_found = self._trigger_logic(topic_dict[subscription], message.topic, message.payload)
                        else:
                            self.logger.error("_on_mqtt_message: received topic for unknown subscriber_type '{}'".format(subscriber_type))
        finally:
            # unlock
            self._subscribed_topics_lock.release()

        item = self.topics.get(message.topic, None)
        if item != None:
            payload = self.cast_from_mqtt(item.type(), message.payload)
            self.logger.info(
                "Received topic '{}', payload '{}' (type {}), QoS '{}', retain '{}' for item '{}'".format(message.topic, payload, item.type(), message.qos, message.retain, item.id()))
            item(payload, 'MQTT')

        if (not subscription_found) and (item == None):
            if not self._handle_broker_infos(message):
                self.logger.error("_on_mqtt_message: Received topic '{}', payload '{}', QoS '{}', retain '{}' WITHOUT matching item/logic".format( message.topic, message.payload, message.qos, message.retain))


    # ----------------------------------------------------------------------------------------

    def _get_qos_forTopic(self, item):
        """
        Return the configured QoS for a topic/item as an integer

        :param item:      item to get the QoS for
        :return:          Quality of Service (0..2)
        """
        qos = self.get_iattr_value(item.conf, 'mqtt_qos')
        if qos == None:
            qos = self.qos
        return int(qos)


    def _on_mqtt_log(self, client, userdata, level, buf):
        # self.logger.info("_on_log: {}".format(buf))
        return


    def _subscribe_broker_infos(self):
        """
        Subscribe to broker's infos

        This method is called from on_connect
        """
        self._client.subscribe('$SYS/broker/version', qos=0)
        self._client.subscribe('$SYS/broker/clients/active', qos=0)
        self._client.subscribe('$SYS/broker/subscriptions/count', qos=0)
        self._client.subscribe('$SYS/broker/messages/stored', qos=0)

        if self.broker_monitoring:
            self._client.subscribe('$SYS/broker/uptime', qos=0)
            self._client.subscribe('$SYS/broker/retained messages/count', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/received/1min', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/received/5min', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/received/15min', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/sent/1min', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/sent/5min', qos=0)
            self._client.subscribe('$SYS/broker/load/messages/sent/15min', qos=0)
        return


    def _handle_broker_infos(self, message):

        if message.topic == '$SYS/broker/clients/active':
            self._broker['active_clients'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/subscriptions/count':
            self._broker['subscriptions'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/messages/stored':
            self._broker['stored_messages'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/retained messages/count':
            self._broker['retained_messages'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/uptime':
            self._broker['uptime'] = message.payload.decode('utf-8').split(' ')[0]
        elif message.topic == '$SYS/broker/load/messages/received/1min':
            self._broker['msg_rcv_1min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/load/messages/received/5min':
            self._broker['msg_rcv_5min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/load/messages/received/15min':
            self._broker['msg_rcv_15min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/load/messages/sent/1min':
            self._broker['msg_snt_1min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/load/messages/sent/5min':
            self._broker['msg_snt_5min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/load/messages/sent/15min':
            self._broker['msg_snt_15min'] = message.payload.decode('utf-8')
        elif message.topic == '$SYS/broker/version':
            self._log_brokerinfo(message.payload)
            self._broker['version'] = message.payload.decode('utf-8')
            # self._client.unsubscribe('$SYS/broker/version')
        else:
            return False

        self.logger.debug("_handle_broker_infos: $SYS/broker info = '{}'".format(self._broker))
        return True

    def _unsubscribe_broker_infos(self):
        """
        Unsubscribe from broker's infos

        This method is called from DisconnectFromBroker
        """
        self._client.unsubscribe('$SYS/broker/version')
        self._client.unsubscribe('$SYS/broker/clients/active')
        self._client.unsubscribe('$SYS/broker/subscriptions/count')
        self._client.unsubscribe('$SYS/broker/messages/stored')

        if self.broker_monitoring:
            self._client.unsubscribe('$SYS/broker/uptime')
            self._client.unsubscribe('$SYS/broker/retained messages/count')
            self._client.unsubscribe('$SYS/broker/load/messages/received/1min')
            self._client.unsubscribe('$SYS/broker/load/messages/received/5min')
            self._client.unsubscribe('$SYS/broker/load/messages/received/15min')
            self._client.unsubscribe('$SYS/broker/load/messages/sent/1min')
            self._client.unsubscribe('$SYS/broker/load/messages/sent/5min')
            self._client.unsubscribe('$SYS/broker/load/messages/sent/15min')
        return


    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback function called on connect
        """
        self._connect_result = mqtt.connack_string(rc)

        if rc == 0:
            self.logger.info("Connection returned result '{}' (userdata={}) ".format(mqtt.connack_string(rc), userdata))
            self._connected = True

            self._subscribe_broker_infos()

            # subscribe to topics to listen for items
            for topic in self.topics:
                item = self.topics[topic]
                self._client.subscribe(topic, qos=self._get_qos_forTopic(item) )
                self.logger.info("Listening on topic '{}' for item '{}'".format( topic, item.id() ))

            self.logger.info("self.topics = {}".format(self.topics))

            return

        msg = "Connection returned result '{}': {} (client={}, userdata={}, self._client={})".format( str(rc), mqtt.connack_string(rc), client, userdata, self._client )
        if rc == 5:
            self.logger.error(msg)
            self._disconnect_from_broker()
        else:
            self.logger.warning(msg)

    def _on_disconnect(self, client, userdata, rc):
        """
        Callback function called on disconnect
        """
        self.logger.info("Disconnection returned result '{}' ".format(rc))
        return



    # ---------------------------------------------------------------------------------
    # Following functions build the interface for other plugins which want to use MQTT
    #

    def _get_caller_type(self):
        """
        determine if called from logic or plugin

        :return: caller type ('Plugin' | 'Logic' | 'Unknown')
        :rtype: str
        """
        self.logger.debug("_get_caller_type: inspect.stack()[2][1] = '{}', split = {}".format(inspect.stack()[2][1], inspect.stack()[2][1].split('/')))
        if inspect.stack()[2][1].split('/')[4] == 'lib' and inspect.stack()[2][1].split('/')[5] == 'model':
            source_type = 'Plugin'
        elif inspect.stack()[2][1].split('/')[4] == 'plugins':
            source_type = 'Plugin'
        elif inspect.stack()[2][1].split('/')[4] == 'logics':
            source_type = 'Logic'
        else:
            source_type = 'Unknown'
            self.logger.info("_get_caller_type: inspect.stack()[2][1] = '{}', split = {}".format(inspect.stack()[2][1],
                                                                                                  inspect.stack()[2][
                                                                                                      1].split('/')))

        return source_type


    def publish_topic(self, source, topic, payload, qos=None, retain=False, bool_values=None):
        """
        method to publish a topic

        this method is to be called from plugins or logics

        :param source:     name of plugin or logic which want's to publish a topic
        :param topic:      topic to publish to
        :param payload:    payload to publish
        :param qos:        quality of service (optional) otherwise the default of the mqtt plugin will be used
        :param retain:     retain flag (optional)
        """
        if bool_values is None:
            bool_values = self.bool_values

        source_type = self._get_caller_type()
        self.logger.info("'{}()' - called from {} by '{}()'".format(inspect.stack()[0][3], source_type, inspect.stack()[1][3]))
        #self.logger.info("inspect.stack()[1][1] = '{}', split = {}".format(inspect.stack()[1][1], inspect.stack()[1][1].split('/')))

        if not self._connected:
            return False

        if qos == None:
            qos = self.qos
        self.logger.info("{} '{}' is publishing topic '{}' with payload '{}' (qos={}, retain={})".format(source_type, source, topic, payload, qos, retain ))
        payload = self.cast_to_mqtt(payload, bool_values)
        try:
            self._client.publish(topic=topic, payload=payload, qos=qos, retain=retain)
            self.logger.info("{} '{}' has published topic '{}' with payload '{}'".format(source_type, source, topic, payload))
        except Exception as e:
            self.logger.error("{}: Publish exception '{}'".format(inspect.stack()[0][3], e))
            return False
        return True


    # ----------------------------------------------------------------------------------------
    #  casting methods
    # ----------------------------------------------------------------------------------------

    def cast_from_mqtt(self, datatype, raw_data, bool_values=None):
        """
        Cast payload data to SmartHomeNG datatypes

        :param datatype:  datatype to which the data should be casted to
        :param raw_data:  data as received from the mqtt broker
        :type datatype:   str
        :type raw_data:   str

        :return:          data casted to the datatype of the item it should be written to
        :rtype:           str | bool | list | dict
        """
        if bool_values is None:
            bool_values = self.bool_values
        str_data = raw_data.decode('utf-8')
        if datatype == 'bytes':
            data = raw_data
        if datatype == 'str':
            data = str(str_data)
        elif datatype == 'num':
            data = str_data
        elif datatype == 'bool':
            self.logger.debug("cast_from_mqtt: datatype 'bool', str_data = '{}', bool_values = ‘{}‘".format(str_data, bool_values))
            if bool_values:
                try:
                    data = bool(bool_values.index(str_data.strip()))
                except:
                    data = Utils.to_bool(str_data, default=False)
            else:
                data = Utils.to_bool(str_data, default=False)
        elif datatype == 'list':
            if not ((len(str_data) > 0) and (str_data[0] == '[')):
                str_data = '[' + str_data + ']'
            try:
                data = json.loads(str_data)
            except Exception as e:
                self.logger.error("cast_from_mqtt: datatype 'list', error '{}', data = ‘{}‘".format(e, str_data))
                data = str_data
        elif datatype == 'dict':
            try:
                data = json.loads(str_data)
            except Exception as e:
                self.logger.error("cast_from_mqtt: datatype 'dict', error '{}', data = ‘{}‘".format(e, str_data))
                data = str_data
        elif datatype == 'scene':
            data = '0'
            if Utils.is_int(str_data):
                if (int(str_data) >= 0) and (int(str_data) < 0):
                    data = str_data
        elif datatype == 'foo':
            data = raw_data
        else:
            self.logger.warning("cast_from_mqtt: Casting '{}' to '{}' is not implemented".format(raw_data, datatype))
            data = raw_data
        return data


    def cast_to_mqtt(self, data, bool_values=None):
        """
        Cast SmartHomeNG datatypes to payload data

        :param data:  data which should be casted to a payload compatible format
        :type data:   str | bool | int | float | list | dict | bytes

        :return:      data casted from the SmartHomeNG datatype to str to be written to payload
        :rtype:       str
        """
        if bool_values is None:
            bool_values = self.bool_values
        try:
            self.logger.debug("cast_to_mqtt: data = '{}', type(data) = '{}', bool_values ='{}'".format(data, type(data), bool_values))
            if isinstance(data, bytes):
                payload_data = data
            elif isinstance(data, str):
                payload_data = data
            elif isinstance(data, bool):
                self.logger.info("            : data = '{}', type(data) = '{}', bool_values ='{}'".format(data, type(data), bool_values))
                if bool_values:
                    payload_data = str(bool_values[data])
                else:
                    payload_data = 'true' if data else 'false'
                self.logger.info("            : payload_data = '{}', type(payload_data) = '{}', bool_values ='{}'".format(payload_data, type(payload_data), bool_values))
            elif isinstance(data, int):
                payload_data = str(data)
            elif isinstance(data, float):
                payload_data = str(data)
            elif isinstance(data, list):
                payload_data = json.dumps(data)
            elif isinstance(data, dict):
                payload_data = json.dumps(data)
            else:
                self.logger.warning("cast_from_mqtt: Casting '{}' type = '{}' to payload fat is not implemented".format(data, type(data)))
                payload_data = str(data)
        except Exception as e:
            self.logger.error("cast_to_mqtt: Cast exception'{}'".format(e))
        return payload_data



# ----------------------------------------------------------------------------------------

def _get_local_ipv4_address():
    """
    Get's local ipv4 address of the interface with the default gateway.
    Return '127.0.0.1' if no suitable interface is found

    :return: IPv4 address as a string
    :rtype: string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
