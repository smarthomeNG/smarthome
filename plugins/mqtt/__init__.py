#!/usr/bin/env python

# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHomeNG.   https://github.com/smarthomeNG/
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
#  Skender Haxhimolla
#########################################################################

import logging
import paho.mqtt.client as paho
import paho.mqtt.publish as pahopub
import os

logger = logging.getLogger()


class Mqtt():

    def __init__(self, smarthome, host, port):
        self._sh = smarthome
        self.broker_ip = host
        self.broker_port = int(port)
        self.clients = []
        self.items = {}
        self.logics = {}
        self.publisher = self.create_client('main')

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        for client in self.clients:
            logger.debug('Stopping mqtt client {0}'.format(client._client_id))
            client.loop_stop()

    def parse_item(self, item):
        if 'mqtt_topic' in item.conf:
            item.conf['mqtt_topic_in'] = item.conf['mqtt_topic']
            item.conf['mqtt_topic_out'] = item.conf['mqtt_topic']
            logger.debug("parse item: {0}".format(item))

        if 'mqtt_topic_in' in item.conf:
            client = self.create_client(item.id())
            client.on_message = lambda client, obj, msg: self.items[msg.topic](msg.payload, 'MQTT')
            client.on_connect = lambda client, obj, rc: client.subscribe(item.conf['mqtt_topic_in'], 2)
            client.loop_start()
            self.items[item.conf['mqtt_topic_in']] = item
            logger.debug('Item [{0}] is listening for messages on topic [{1}]'.format(item, item.conf['mqtt_topic_in']))

        if 'mqtt_topic_out' in item.conf:
            return self.update_item

    def parse_logic(self, logic):
        if 'mqtt_topic' in logic.conf:
            client = self.create_client(logic.name)
            client.on_message = lambda client, obj, msg: self.logics[msg.topic].trigger('MQTT', msg.topic, msg.payload)
            client.subscribe(logic.conf['mqtt_topic'], 2)
            client.loop_start()
            self.logics[logic.conf['mqtt_topic']] = logic
            logger.debug('Logic [{0}] is listening for messages on topic [{1}]'.format(logic.name, logic.conf['mqtt_topic']))

    def update_item(self, item, caller=None, source=None, dest=None):
        pahopub.single(topic=item.conf['mqtt_topic_out'], payload=str(item()), qos=2, hostname=self.broker_ip)
        logger.info("update item: {0}".format(item.id()))
        logger.debug("Mqtt caller item: {0} \t Source: {1} \t Destination:{2}".format(caller, source, dest))
        logger.info("update topic: {0}\t{1}".format(item.conf['mqtt_topic_out'], str(item())))

    def create_client(self, name):
        client = paho.Client('{0}.{1}'.format(os.uname()[1], name))
        client.connect(self.broker_ip, self.broker_port, 60)
        self.clients.append(client)
        return client
