#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
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

import asyncio
import logging

import json

"""
===============================================================================
=
=  The following method(s) implement the webmethods protocol for sync example
=
"""

class Sync_example():

    version = '1.0.0'

    STATE = {"value": 0}

    protocol_name = 'sync_example'
    protocol_path = '/sync'
    protocol_enabled = True


    def __init__(self, ws_modul):

        self.logger = logging.getLogger(__name__)

        self.ws_modul = ws_modul


    def state_event(self):
        return json.dumps({"type": "state", **self.STATE})

    def users_event(self):
        return json.dumps({"type": "users", "count": len(self.ws_modul.USERS)})

    async def notify_state(self):
        if self.ws_modul.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in self.ws_modul.USERS])

    async def notify_users(self):
        if self.ws_modul.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await asyncio.wait([user.send(message) for user in self.ws_modul.USERS])

    async def counter_sync(self, websocket):
        await self.notify_users()
        await websocket.send(self.state_event())

        async for message in websocket:
            data = json.loads(message)
            if data.get("cmd", ''):
                self.ws_modul.logger.info(f"Sync-protocol: CMD: {data}")
            elif data.get("action", '') == "minus":
                self.STATE["value"] -= 1
                self.ws_modul.logger.info(f"Sync-protocol: Decremented value to {self.STATE['value']}")
                await self.notify_state()
            elif data.get("action", '') == "plus":
                self.STATE["value"] += 1
                self.ws_modul.logger.info(f"Sync-protocol: Incremented value to {self.STATE['value']}")
                await self.notify_state()
            else:
                self.ws_modul.logging.error(f"Sync-protocol: unsupported event: {data}")

        await self.notify_users()
        return
