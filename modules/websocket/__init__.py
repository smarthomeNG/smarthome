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
import ssl
import threading
import websockets

import time

import os
import sys
import socket
import logging

from lib.model.module import Module

from lib.shtime import Shtime
from lib.utils import Utils


class Websocket(Module):
    version = '1.0.9'
    longname = 'Websocket module for SmartHomeNG'
    port = 0

    def __init__(self, sh, testparam=''):
        """
        Initialization Routine for the module
        """
        # TO DO: Shortname anders setzen (oder warten bis der Plugin Loader es beim Laden setzt
        self._shortname = self.__class__.__name__
        self._shortname = self._shortname.lower()

        self.logger = logging.getLogger(__name__)
        self._sh = sh
        self.etc_dir = sh._etc_dir
        #self.shtime = Shtime.get_instance()

        self.logger.debug(f"Module '{self._shortname}': Initializing")

        # get the parameters for the module (as defined in metadata module.yaml):
        self.logger.debug(f"Module '{self._shortname}': Parameters = '{dict(self._parameters)}'")
        self.ip = self.get_parameter_value('ip')
        # if self.ip == '0.0.0.0':
        #    self.ip = Utils.get_local_ipv4_address()
        self.port = self.get_parameter_value('port')
        self.tls_port = self.get_parameter_value('tls_port')
        self.use_tls = self.get_parameter_value('use_tls')
        self.tls_cert = self.get_parameter_value('tls_cert')
        self.tls_key = self.get_parameter_value('tls_key')

        self.ssl_context = None
        if self.use_tls:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            pem_file = os.path.join(self.etc_dir, self.tls_cert)
            key_file = os.path.join(self.etc_dir, self.tls_key)
            try:
                self.ssl_context.load_cert_chain(pem_file, key_file)
            except Exception as e:
                self.logger.error(f"Secure websocket port not opened because the following error ocured while initilizing tls: {e}")
                self.ssl_context = None
                self.use_tls = False

        if self.use_tls and self.port == self.tls_port:
            self.logger.error("Secure websocket port not opened because it cannnot be the same port as the ws:// port:")
            self.ssl_context = None
            self.use_tls = False

        if self.ip == '0.0.0.0':
            self.logger.info(f"Listening on IP .: all local IPs")
        else:
            self.logger.info(f"Listening on IP .: {self.ip}")
        self.logger.info(f"port / tls_port .: {self.port} / {self.tls_port}")
        self.logger.info(f"use_tls .........: {self.use_tls}")
        self.logger.info(f"certificate .....: key: ../etc/{self.tls_cert} / ../etc/{self.tls_key}")

        self.loop = None    # Var to hold the event loop for asyncio

        self.initialize_payload_protocols()
        return

    def start(self):
        """
        If the module needs to startup threads or uses python modules that create threads,
        put thread creation code or the module startup code here.

        Otherwise don't enter code here
        """
        _name = 'modules.' + self.get_fullname() + '.websocket_server'
        try:
            self._server_thread = threading.Thread(target=self._ws_server_thread, name=_name)
            self._server_thread.start()
            self.logger.dbghigh("Starting websocket server(s)...")
        except Exception as e:
            self.conn = None
            self.logger.error(f"Websocket Server: Cannot start server - Error: {e}")
        return

    def stop(self):
        """
        If the module has started threads or uses python modules that created threads,
        put cleanup code here.

        Otherwise don't enter code here
        """
        self.logger.info("Shutting down websocket server(s)...")
        self.loop.call_soon_threadsafe(self.loop.stop)
        time.sleep(5)

        try:
            self._server_thread.join()
            self.logger.info("Websocket Server(s): Stopped")
        except Exception as err:
            self.logger.info(f"Stopping websocket error: {err}")
            pass
        return


    def initialize_payload_protocols(self):
        """
        Initialize the supported payload protocols

        :return:
        """
        self.protocols = {}

        # parameters and class instance for sync_example protocol
        from . import sync_example
        self.initialize_payload_protocol(sync_example.Protocol)

        # parameters and class instance for smartVISU protocol
        from . import smartvisu
        self.initialize_payload_protocol(smartvisu.Protocol)

        return


    def initialize_payload_protocol(self, Protocol):

        # hand the websocket module instance (self) to protocol object
        id = Protocol.protocol_id
        prot = Protocol(self, self.logger.name+'.'+id)
        self.protocols[prot.protocol_path] = {}
        self.protocols[prot.protocol_path]['id'] = id
        self.protocols[prot.protocol_path]['name'] = prot.protocol_name
        self.protocols[prot.protocol_path]['protocol'] = prot
        self.logger.info(f"Payload protocol '{ prot.protocol_name}' initialized ({'enabled' if prot.protocol_enabled else 'disabled'})")
        return


    def get_payload_protocol_by_id(self, id):

        result = None
        for path in self.protocols:
            if self.protocols[path]['id'] == id:
                result = self.protocols[path]['protocol']
                break
        return result


    def get_port(self):
        """
        Returns the port used for the ws:// protocol

        :return: port number
        """

        return self.port


    def get_tls_port(self):
        """
        Returns the port used for the secure wss:// protocol

        :return: port number
        """

        return self.tls_port


    def get_use_tls(self):
        """
        Returns True, if secure websocket protocol (wss://) is enabled

        :return: True, if secure websocket protocol is enabled
        """

        return self.use_tls


    # ===============================================================================
    # Module specific code
    #

    def _ws_server_thread(self):
        """
        Thread that runs the websocket server

        The websocket server itself is using asyncio
        """
        self.loop = asyncio.new_event_loop()
        python_version = str(sys.version_info[0]) + '.' + str(sys.version_info[1])

        if python_version == '3.6':
            self.loop.ensure_future(self.ws_server(self.ip, self.port))
        elif python_version == '3.7':
            self.loop.create_task(self.ws_server(self.ip, self.port))
        else:
            self.loop.create_task(self.ws_server(self.ip, self.port), name='ws_server')
        # self.loop.ensure_future(self.ws_server(self.ip, self.port))
        if self.ssl_context is not None:
            if python_version == '3.7':
                self.loop.create_task(self.ws_server(self.ip, self.tls_port, self.ssl_context))
            else:
                self.loop.create_task(self.ws_server(self.ip, self.tls_port, self.ssl_context), name='wss_server')

            # self.loop.ensure_future(self.ws_server(self.ip, self.tls_port, self.ssl_context))

        # start tasks, that are global for a payload protocol
        for path in self.protocols:
            self.protocols[path]['protocol'].start_global_tasks(self.loop)

        try:
            self.loop.run_forever()
        finally:
            #self.logger.warning("_ws_server_thread: finally")
            try:
                self.loop.shutdown_asyncgens()
                #if python_version >= '3.9':
                #    self.loop.shutdown_default_executor()
                #time.sleep(3)
                #self.logger.notice(f"all_tasks: {self.loop.Task.all_tasks()}")
                #self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            except Exception as e:
                self.logger.warning(f"_ws_server_thread: finally - Exception on loop.shutdown_asyncgens(): {e}")
            try:
                self.loop.close()
            except Exception as e:
                self.logger.warning(f"_ws_server_thread: finally - Exception on loop.close(): {e}")

    USERS = set()

    async def ws_server(self, ip, port, ssl_context=None):
        while self._sh.shng_status['code'] != 20:
            await asyncio.sleep(1)

        if ssl_context:
            self.logger.info("Secure websocket server started")
            try:
                await websockets.serve(self.handle_new_connection, ip, port, ssl=ssl_context)
            except OSError as e:
                self.logger.error(f"Cannot start secure websocket server - error: {e}")
        else:
            self.logger.info("Websocket server started")
            try:
                await websockets.serve(self.handle_new_connection, ip, port)
            except OSError as e:
                self.logger.error(f"Cannot start websocket server - error: {e}")

        return


    """
    ===============================================================================
    =
    =  The following method(s) implement the handling of new connections (users)
    =  and the disconnections after the websocket connection terminates
    =
    """

    async def handle_new_connection(self, websocket, path):
        """
        Wait for incoming connection and handle the request
        """
#        if path == '/sync' and not sync_enabled:
#            return

        await self.register(websocket)
        try:
            # Determine payload protocol and start it if found and enabled
            payload = self.protocols.get(path, None)
            if payload is None:
                self.logger.warning(f"Unsupported websocket path '{path}' used by {self.client_address(websocket)}. Cannot determine payload protocol - terminating connection")
            else:
                if payload['protocol'].protocol_enabled:
                    self.logger.info(f"Starting '{payload['name']}' payload protocol")
                    await payload['protocol'].handle_protocol(websocket)
                else:
                    self.logger.notice(f"Payload protocol '{payload['name']}' is disabled - terminating connection")

        except Exception as e:
            # connection has been ended or not established in payload protocol
            self.logger.info(f"handle_new_connection: Connection to {e} has been terminated in payload protocol")
        finally:
            await self.unregister(websocket)
        return

    async def register(self, websocket):
        """
        Register a new incoming connection
        """
        self.USERS.add(websocket)
        await self.log_connection_event('added', websocket)
        return

    async def unregister(self, websocket):
        """
        Unregister an incoming connection
        """
        payload = self.protocols.get(websocket.path, None)
        if payload is not None:
            await payload['protocol'].cleanup_connection(websocket)

        self.USERS.remove(websocket)
        await self.log_connection_event('removed', websocket)
        return

    async def log_connection_event(self, action, websocket):
        """
        Log info about connection/disconnection of users
        """
        if not websocket.remote_address:
            self.logger.info(f"USER {action}: {'with SSL connection'} - local port: {websocket.port} - path: {websocket.path}")
        else:
            self.logger.info(f"USER {action}: {self.client_address(websocket)} - local port: {websocket.port} - path: {websocket.path}")

        self.logger.dbghigh(f"Connected USERS: {len(self.USERS)}")
        for u in self.USERS:
            self.logger.dbghigh(f"- user: {self.client_address(u)}    path: {u.path}    secure: {u.secure}    port: {u.port}")
        return




    def client_address(self, websocket):
        return websocket.remote_address[0] + ':' + str(websocket.remote_address[1])


    def get_payload_users(self, protocol_path):
        # get USERS, that use this protocol
        payload_USERS = set()
        for user in self.USERS:
            if user.path == protocol_path:
                payload_USERS.add(user)
        return payload_USERS
