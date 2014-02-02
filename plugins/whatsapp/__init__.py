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
from plugins.whatsapp.ListenerClient import WhatsappListenerClient
import base64
import subprocess

logger = logging.getLogger('Whatsapp')

class Whatsapp():

    def __init__(self, smarthome, account, password, trusted = None, logic = 'Whatsapp'):
        self._sh = smarthome
        self._account = account
        self._trusted = trusted

        self._password = base64.b64decode(bytes(password.encode('utf-8')))
        wa = WhatsappListenerClient(smarthome, True, True, trusted, logic)
        self._wa = wa
        self.createListener()

    def createListener(self):
        self._wa.login(self._account, self._password)
    
    def run(self):
        pass

    def stop(self):
        self._wa.autoreconnect = False
        self._wa.cm.disconnect("Shutting SH down....")

    def parse_item(self, item):
        return None

    def parse_logic(self, logic):
        pass

    def __call__(self, message, phoneNumber = None):
        if phoneNumber == None:
            if self._wa._absender == None:
                phoneNumber = self._trusted[0]
            else:
                phoneNumber = self._wa._absender

        jid = "%s@s.whatsapp.net" % phoneNumber
        self._wa.methodsInterface.call("message_send", (jid, message))

    def sendPicture (self, url, username=None, password=None, phoneNumber = None):
        self._wa.sendPicture (url, username, password, phoneNumber)