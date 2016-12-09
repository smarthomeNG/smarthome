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
from plugins.whatsapp.SmarthomeLayer            import SmarthomeLayer
from yowsup.layers.auth                         import YowAuthenticationProtocolLayer
from yowsup.layers.auth                         import AuthError
from yowsup.layers.protocol_messages            import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts            import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks                import YowAckProtocolLayer
from yowsup.layers.protocol_ib                  import YowIbProtocolLayer
from yowsup.layers.protocol_iq                  import YowIqProtocolLayer
from yowsup.layers.protocol_notifications       import YowNotificationsProtocolLayer
from yowsup.layers.protocol_presence            import YowPresenceProtocolLayer
from yowsup.layers.logger                       import YowLoggerLayer
from yowsup.layers.protocol_iq.protocolentities import PingIqProtocolEntity
from yowsup.layers.coder                        import YowCoderLayer
from yowsup.layers.auth                         import YowCryptLayer
from yowsup.layers.stanzaregulator              import YowStanzaRegulator
from yowsup.layers.network                      import YowNetworkLayer
from yowsup.layers                              import YowParallelLayer
from yowsup.stacks                              import YowStack
from yowsup.common                              import YowConstants
from yowsup.layers                              import YowLayerEvent
from yowsup                                     import env
import subprocess
import datetime

logger = logging.getLogger('Whatsapp')


class Whatsapp():
    def __init__(self, smarthome, account, password, trusted=None, logic='Whatsapp', cli_mode='False'):
# Set Plugin Attributes
        self._sh = smarthome
        self._credentials = (account, password.encode('utf-8'))
        self._trusted = trusted
        self._logic = logic
        self._run = False
        if cli_mode == 'True':
            self._cli_mode = True
            return
        else:
            self._cli_mode = False
# Yowsup Layers
        self._layers = (
            SmarthomeLayer,
            YowParallelLayer((YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer, YowIbProtocolLayer, YowIqProtocolLayer, YowNotificationsProtocolLayer, YowPresenceProtocolLayer)),
            YowCoderLayer,
#            YowLoggerLayer,
            YowCryptLayer,
            YowStanzaRegulator,
            YowNetworkLayer)

# Yowsup Properties
        self._stack = YowStack(self._layers)
        self._stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, self._credentials)
        self._stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])
        self._stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        self._stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())

# Connect Yowsup
        self._stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

# Get SmarthomeLayer and set this Plugin
        self._SmarthomeLayer = self._stack.getLayer(len(self._stack._YowStack__stack) - 1)
        self._SmarthomeLayer.setPlugin(self)

    def run(self):
        self._run = True
        if self._cli_mode == True:
            return
        try:
            self._stack.loop(timeout = 0.5, discrete = 0.5)
        except AuthError as e:
            logger.info("Authentication Error!")

    def stop(self):
        self._run = False
        if self._cli_mode == True:
            return
        logger.info("Shutting Down WhatsApp Client")
        disconnectEvent = YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT)
        self._stack.broadcastEvent(disconnectEvent)

    def parse_item(self, item):
        return None

    def parse_logic(self, logic):
        pass

    def __call__(self, message, phoneNumber=None):
        if phoneNumber == None:
            try:
                phoneNumber = self._trusted.split(' ')[0]
            except AttributeError:
                logger.error("Error sending Whatsapp Message")
            except IndentationError:
                logger.error("Error sending Whatsapp Message")
        if self._cli_mode == True:
            subprocess.call(['/usr/local/bin/yowsup-cli', 'demos', '-l', self._credentials[0] + ':' + self._credentials[1].decode(), '-s', phoneNumber, message])
            return
        self._SmarthomeLayer.sendMsg(message, phoneNumber)

    def message_received(self, message, sender):
        try:
            self._sh.trigger(name=self._logic, value=message, source=sender.split('@')[0])
        except AttributeError:
            logger.error("Error receiving Whatsapp Message")
        except IndentationError:
            logger.error("Error receiving Whatsapp Message")
