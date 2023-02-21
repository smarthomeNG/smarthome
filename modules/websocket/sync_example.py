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

from functools import partial

import asyncio
import logging

import json

"""
===============================================================================
=
=  The following method(s) implement the webmethods protocol for sync example
=
"""

class Protocol():

    version = '1.0.0'

    protocol_id = 'ex'
    protocol_name = 'sync_example'
    protocol_path = '/sync'
    protocol_enabled = True


    def __init__(self, ws_server, logger_name):

        self.logger = logging.getLogger(logger_name)

        self.client_address = ws_server.client_address
        self.get_users = partial(ws_server.get_payload_users, self.protocol_path)

        return


    def start_global_tasks(self, loop):

        self.loop = loop

        self.logger.dbghigh("start_global_tasks: Nothing to start")
        return


    async def handle_protocol(self, websocket):

        await self.counter_sync(websocket)
        return


    async def cleanup_connection(self, websocket):

        # Nothing to clean up for this protocol
        return


#--------------

    STATE = {"value": 0}

    def state_event(self):
        return json.dumps({"type": "state", **self.STATE})

    def users_event(self):
        sync_USERS = self.get_users()
        return json.dumps({"type": "users", "count": len(sync_USERS)})

    async def notify_state(self):
        sync_USERS = self.get_users()
        if sync_USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in sync_USERS])

    async def notify_users(self):
        try:
            sync_USERS = self.get_users()

            if sync_USERS:  # asyncio.wait doesn't accept an empty list
                message = self.users_event()
                done, pending = await asyncio.wait([user.send(message) for user in sync_USERS])

                for task in done:
                    name = task.get_name()
                    exception = task.exception()
                    if isinstance(exception, Exception):
                        if not str(exception).startswith('received 1000'):
                            self.logger.info(f"notify_users: Finished task {name} threw {exception}")

                for task in pending:
                    name = task.get_name()
                    exception = task.exception()
                    if isinstance(exception, Exception):
                        self.logger.info(f"notify_users: Pending task {name} threw {exception}")
        except Exception as e:
            self.logger.exception(f"Exception: {e}")

    async def counter_sync(self, websocket):
        await self.notify_users()
        await websocket.send(self.state_event())

        try:
            async for message in websocket:
                data = json.loads(message)
                if data.get("cmd", ''):
                    self.logger.info(f"CMD: {data}")
                elif data.get("action", '') == "minus":
                    self.STATE["value"] -= 1
                    self.logger.info(f"Decremented value to {self.STATE['value']}")
                    await self.notify_state()
                elif data.get("action", '') == "plus":
                    self.STATE["value"] += 1
                    self.logger.info(f"Incremented value to {self.STATE['value']}")
                    await self.notify_state()
                else:
                    self.logging.error(f"Sync-protocol: unsupported event: {data}")

            await self.notify_users()

        except Exception as e:
            #logmsg = f"counter_sync error: Client {self.build_log_info(client_addr)} - {e}"
            logmsg = f"counter_sync error: Client {self.client_address(websocket)} - {e}"
            if str(e).startswith(('no close frame received or sent', 'received 1005')):
                self.logger.info(logmsg)
            elif str(e).startswith(('code = 1005', 'code = 1006')) or str(e).endswith('keepalive ping timeout; no close frame received'):
                self.logger.warning(logmsg)
            else:
                self.logger.error(logmsg)

        return


