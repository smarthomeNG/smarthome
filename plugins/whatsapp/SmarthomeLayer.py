#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2015 KNX-User-Forum e.V.            http://knx-user-forum.de/
# by mode2k
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import time
from yowsup.layers.interface                          import YowInterfaceLayer
from yowsup.layers.interface                          import ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities     import OutgoingAckProtocolEntity
from yowsup.layers.protocol_iq.protocolentities       import PingIqProtocolEntity
from yowsup.common                                    import YowConstants
from yowsup.layers.network                            import YowNetworkLayer
from yowsup.layers                                    import YowLayerEvent

logger = logging.getLogger('Whatsapp')


class SmarthomeLayer(YowInterfaceLayer):
    _last_ping_snd_id = None
    _last_ping_rcvd_id = None

    def setPlugin(self, plugin):
        self._plugin = plugin

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        #send receipt otherwise we keep receiving the same message over and over
        logger.info("Received Message: ID {}  From {}  Body {}".format(messageProtocolEntity._id, messageProtocolEntity._from, messageProtocolEntity.body))

        logger.info("Sending Receipt")
        receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())
        self.toLower(receipt)
        self._plugin.message_received(messageProtocolEntity.getBody(), messageProtocolEntity.getFrom())

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        logger.info("Received Receipt: ID {}".format(entity._id))
        logger.info("Sending ACK")
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    @ProtocolEntityCallback("ack")
    def onAck(self, entity):
        logger.info("Received ACK: ID {}  Class {}".format(entity._id, entity._class))

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        logger.info("Received Success: Status {}  Kind {}  Creation {}  Expiration {}".format(entity.status, entity.kind, time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(entity.creation)), time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(entity.expiration))))

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        logger.info("Received Failure: {}".format(entity))

    @ProtocolEntityCallback("chatstate")
    def onChatstate(self, entity):
        logger.info("Received Chatstate: {}".format(entity))

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        logger.debug("Received IQ: ID: {} Type: {} XMLNS: {} To: {} From: {}".format(entity._id, entity._type, entity.xmlns, entity.to, entity._from))
        if entity._type == 'result':
            self._last_ping_rcvd_id = entity._id

    @ProtocolEntityCallback("notification")
    def onNotification(self, notification):
        notificationData = notification.__str__()
        logger.info("Received Notification: {}".format(notificationData))

    def sendMsg(self, msg, num):
        outgoingMessageProtocolEntity = TextMessageProtocolEntity(msg, to="%s@%s" % (num, YowConstants.DOMAIN))
        logger.info("Sending Message {0} to {1}".format(msg, num))
        self.toLower(outgoingMessageProtocolEntity)

    def connect(self):
        self.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

    def disconnect(self):
        self.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

    def onEvent(self, yowLayerEvent):
#        logger.info("YS_Event: {}".format(yowLayerEvent.getName()))
        if yowLayerEvent.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logger.info("YOWSUP DISCONNECTED")
            if self._plugin._run == True:
                logger.info("Reconnecting...")
                self.connect()
                
        if yowLayerEvent.getName() == YowNetworkLayer.EVENT_STATE_CONNECTED:
            logger.info("YOWSUP CONNECTED")
