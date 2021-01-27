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
import janus
import ssl
import threading
import decimal
import websockets

import time

import os
import sys
import logging
import json
import collections
from datetime import date, datetime


from lib.model.module import Module
from lib.item import Items
from lib.logic import Logics

from lib.shtime import Shtime


class Websocket(Module):
    version = '1.0.1'
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
        self.shtime = Shtime.get_instance()

        self.logger.debug("Module '{}': Initializing".format(self._shortname))

        # get the parameters for the module (as defined in metadata module.yaml):
        self.logger.debug("Module '{}': Parameters = '{}'".format(self._shortname, dict(self._parameters)))
        self.ip = self.get_parameter_value('ip')
        # ip == '0.0.0.0' means "all network interfaces"
        # if self.ip == '0.0.0.0':
        #     self.ip = Utils.get_local_ipv4_address()
        self.port = self.get_parameter_value('port')
        self.tls_port = self.get_parameter_value('tls_port')
        self.use_tls = self.get_parameter_value('use_tls')
        self.tls_cert = self.get_parameter_value('tls_cert')
        self.tls_key = self.get_parameter_value('tls_key')

        # parameters for smartVISU handling are initialized by the smartvisu plugin
        # self.sv_enabled = self.get_parameter_value('sv_enabled')
        # self.sv_acl = self.get_parameter_value('sv_acl')
        # self.sv_querydef = self.get_parameter_value('sv_querydef')
        # self.sv_ser_upd_cycle = self.get_parameter_value('sv_ser_upd_cycle')
        self.sv_enabled = False
        self.sv_acl = 'deny'
        self.sv_querydef = False
        self.sv_ser_upd_cycle = 0

        self.ssl_context = None
        if self.use_tls:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            pem_file = os.path.join(self.etc_dir, self.tls_cert)
            key_file = os.path.join(self.etc_dir, self.tls_key)
            try:
                self.ssl_context.load_cert_chain(pem_file, key_file)
            except Exception as e:
                self.logger.error("Secure websocket port not opened because the following error ocured while initilizing tls: {}".format(e))
                self.ssl_context = None
                self.use_tls = False

        if self.use_tls and self.port == self.tls_port:
            self.logger.error("Secure websocket port not opened because it cannnot be the same port as the ws:// port:")
            self.ssl_context = None
            self.use_tls = False

        self.logger.info("ip         : {}".format(self.ip))
        self.logger.info("port       : {}".format(self.port))
        self.logger.info("tls_port   : {}".format(self.tls_port))
        self.logger.info("use_tls    : {}".format(self.use_tls))
        self.logger.info("tls_cert   : {}".format(self.tls_cert))
        self.logger.info("tls_key    : {}".format(self.tls_key))

        # try to get API handles
        self.items = Items.get_instance()
        self.logics = Logics.get_instance()

        self.loop = None    # Var to hold the event loop for asyncio

        # For Release 1.8 only: Enable smartVISU protocol support even if smartvisu plugin is not loaded
        self.set_smartvisu_support(protocol_enabled=True)

    def start(self):
        """
        If the module needs to startup threads or uses python modules that create threads,
        put thread creation code or the module startup code here.

        Otherwise don't enter code here
        """
        _name = 'modules.' + self.get_fullname() + '.websocket_server'
        try:
            self._server_thread = threading.Thread(target=self._ws_server_thread, name=_name).start()
            self.logger.info("Starting websocket server(s)...")
        except Exception as e:
            self.conn = None
            self.logger.error("Websocket Server: Cannot start server - Error: {}".format(e))
        return

    def stop(self):
        """
        If the module has started threads or uses python modules that created threads,
        put cleanup code here.

        Otherwise don't enter code here
        """
        self.logger.info("Shutting down websoocket server(s)...")
#        self.stop_async = True

        #self.loop.call_soon_threadsafe(self.loop.stop)

        try:
            self._server_thread.join()
            self.logger.info("Websocket Server(s): Stopped")
        except:
            pass
        time.sleep(10)
        return

    def set_smartvisu_support(self, protocol_enabled=False, default_acl='ro', query_definitions=False, series_updatecycle=0):
        """
        Set state of smartvisu support

        :param protocol_enabled:    enable or disable the payload protocol for smartVISU
        :param query_definitions:   enable or disable the query of item definitions over websocket protocol
        :param series_updatecycle:  update cycle for smartVISU series requests (if 0, timing from database plugin is used)
        """
        self.sv_enabled = protocol_enabled
        self.sv_acl = default_acl
        self.sv_querydef = query_definitions
        self.sv_ser_upd_cycle = series_updatecycle
        self.logger.info(f"set_smartvisu_support: Set to protocol_enabled={protocol_enabled}, default_acl={default_acl}, query_definitions={query_definitions}, series_updatecycle={series_updatecycle}")
        # self.sv_config = {'enabled': self.sv_enabled, 'acl': self.sv_acl, 'query_def': self.sv_querydef, 'upd_cycle': self.sv_ser_upd_cycle}
        # self.logger.warning(f"sv_config {self.sv_config}")

        # self.stop()
        # self.start()
        return

    def get_port(self):

        return self.port

    def get_tls_port(self):

        return self.tls_port

    def get_use_tls(self):

        return self.use_tls

    # ===============================================================================
    # Module specific code
    #

#    stop_async = False

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
            if python_version == '3.6':
                self.loop.ensure_future(self.ws_server(self.ip, self.tls_port, self.ssl_context))
            elif python_version == '3.7':
                self.loop.create_task(self.ws_server(self.ip, self.tls_port, self.ssl_context))
            else:
                self.loop.create_task(self.ws_server(self.ip, self.tls_port, self.ssl_context), name='wss_server')

            # self.loop.ensure_future(self.ws_server(self.ip, self.tls_port, self.ssl_context))

        if python_version == '3.6':
            self.loop.ensure_future(self.update_visu())
            self.loop.ensure_future(self.update_all_series())
        elif python_version == '3.7':
            self.loop.create_task(self.update_visu())
            self.loop.create_task(self.update_all_series())
        else:
            self.loop.create_task(self.update_visu(), name='update_visu')
            self.loop.create_task(self.update_all_series(), name='update_all_series')

        # self.loop.ensure_future(self.update_visu())
        # self.loop.ensure_future(self.update_all_series())

        try:
            self.loop.run_forever()
        finally:
            self.logger.warning("_ws_server_thread: finally")
            try:
                self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            except:
                self.logger.warning("_ws_server_thread: finally *1")
            self.logger.warning("_ws_server_thread: finally *1x")
            try:
                self.loop.close()
            except:
                self.logger.warning("_ws_server_thread: finally *2")
            self.logger.warning("_ws_server_thread: finally *2x")

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
#        if self.stop_async:
#            await websockets.close()

        return

    async def handle_new_connection(self, websocket, path):
        """
        Wait for incoming connection and handle the request
        """
#        if path == '/sync' and not sync_enabled:
#            return

        await self.register(websocket)
        try:

            if path == '/' and self.sv_enabled:
                await self.smartVISU_protocol_v4(websocket)
            elif path == '/sync':
                await self.counter_sync(websocket)

        except Exception as e:
            # connection has been ended or not established in payload protocol
            self.logger.info("handle_new_connection - Connection to {} has been terminated in payload protocol or couldn't be established".format(e))
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
        self.USERS.remove(websocket)
        await self.log_connection_event('removed', websocket)
        return

    async def log_connection_event(self, action, websocket):
        """
        Print info about connection/disconnection of users
        """
        if not websocket.remote_address:
            self.logger.infp("USER {}: {} - local port: {}".format(action, 'with SSL connection', websocket.port))
        else:
            self.logger.info("USER {}: {} - local port: {}".format(action, websocket.remote_address, websocket.port))

        self.logger.debug("Connected USERS: {}".format(len(self.USERS)))
        for u in self.USERS:
            self.logger.debug("- user: {}   path: {}    secure: {}".format(u.remote_address, u.path, u.secure))
        return

    """
    ===============================================================================
    =
    =  The following method(s) implement the webmethods protocol for sync example
    =
    """

    STATE = {"value": 0}

    def state_event(self):
        return json.dumps({"type": "state", **self.STATE})

    def users_event(self):
        return json.dumps({"type": "users", "count": len(self.USERS)})

    async def notify_state(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_users(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def counter_sync(self, websocket):
        await self.notify_users()
        await websocket.send(self.state_event())

        async for message in websocket:
            data = json.loads(message)
            if data.get("cmd", ''):
                self.logger.warning("CMD: {}".format(data))
            elif data.get("action", '') == "minus":
                self.STATE["value"] -= 1
                await self.notify_state()
            elif data.get("action", '') == "plus":
                self.STATE["value"] += 1
                await self.notify_state()
            else:
                logging.error("unsupported event: {}", data)

        await self.notify_users()
        return

    """
    ===============================================================================
    =
    =  The following method(s) implement the webmethods protocol for smartVISU
    =
    =  The protocol implements the version 4 of the protocol as it has been
    =  implemented by the visu_websocket plugin
    =
    """

    # variables for smartVISU protocol
    # monitor = {'item': [], 'rrd': [], 'log': []}
    sv_monitor_items = {}
    sv_monitor_logs = {}
    sv_clients = {}
    sv_update_series = {}
    clients = []
    proto = 4
    _series_lock = threading.Lock()

    janus_queue = None      # var that holds the queue betweed threaded and async

    async def get_shng_class_instances(self):
        """
        Ensure that the instance vars for items and logics are initialized
        """
        while self.items is None:
            self.items = Items.get_instance()
            if self.items is None:
                await asyncio.sleep(1)
        while self.logics is None:
            self.logics = Logics.get_instance()
            if self.logics is None:
                await asyncio.sleep(1)
        return

    def client_address(self, websocket):
        return websocket.remote_address[0] + ':' + str(websocket.remote_address[1])

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        raise TypeError("Type %s not serializable" % type(obj))

    async def smartVISU_protocol_v4(self, websocket):

        # items = []

        self.logs = self._sh.return_logs()
        self._sh.add_event_listener(['log'], self.update_visulog)

        client_addr = self.client_address(websocket)
        client_ip = websocket.remote_address[0]
        self.sv_clients[client_addr] = {}
        self.sv_clients[client_addr]['websocket'] = websocket
        self.sv_clients[client_addr]['sw'] = 'Visu'
        self.logger.info("smartVISU_protocol_v4: Client {} started".format(client_addr))
        # client_addr = websocket.remote_address[0] + ':' + str(websocket.remote_address[1])
        await self.get_shng_class_instances()

        if not self.janus_queue:
            self.janus_queue = janus.Queue()

        try:
            async for message in websocket:
                data = json.loads(message)
                command = data.get("cmd", '')
                protocol = 'wss' if websocket.secure else 'ws '
                # self.logger.warning("{} <CMD  : '{}'   -   from {}".format(protocol, data, client_addr))
                self.logger.info(f"{client_addr} snt '{data}'")
                answer = {"error": "unhandled command"}

                try:
                    if command == 'item':
                        path = data['id']
                        value = data['val']
                        item = self.items.return_item(path)
                        if item is not None:
                            item_acl = item.conf.get('visu_acl', None)
                            if item_acl is None or item_acl == '':
                                item_acl = item.conf.get('acl', None)
                            if item_acl is None:
                                item_acl = self.sv_acl
                            if item_acl != 'ro':
                                item(value, self.sv_clients[client_addr]['sw'], client_ip)
                            else:
                                self.logger.warning("Client {0} want to update read only item: {1}".format(client_addr, path))
                        else:
                            self.logger.warning("Client {0} want to update invalid item: {1}".format(client_addr, path))
                        answer = {}

                    elif command == 'monitor':
                        answer = {}
                        if data['items'] != [None]:
                            answer = await self.prepare_monitor(data, client_addr)
                        else:
                            self.sv_monitor_items[client_addr] = []   # stop monitoring of items

                    elif command == 'logic':
                        answer = {}
                        await self.request_logic(data, client_addr)
                        self.logger.warning("{} <CMD  not yet tested: '{}'   -   from {}".format(protocol, data, client_addr))

                    elif command == 'series':
                        path = data['item']
                        item = self.items.return_item(path)
                        if item is not None:
                            answer = await self.prepare_series(data, client_addr)
                            if answer == {}:
                                self.logger.warning("command 'series' -> No reply from prepare_series() (for request {})".format(data))
                        else:
                            self.logger.warning("Client {} requested a series for an unknown item: {}".format(client_addr, path))

                    elif command == 'series_cancel':
                        answer = await self.cancel_series(data, client_addr)

                    elif command == 'log':
                        answer = {}
                        name = data['name']
                        num = 10
                        if 'max' in data:
                            num = int(data['max'])
                        if name in self.logs:
                            answer = {'cmd': 'log', 'name': name, 'log': self.logs[name].export(num), 'init': 'y'}
                        else:
                            self.logger.warning("Client {0} requested invalid log: {1}".format(self.addr, name))
                        if client_addr not in self.sv_monitor_logs:
                            self.sv_monitor_logs[client_addr] = []
                        if name not in self.sv_monitor_logs[client_addr]:
                            self.sv_monitor_logs[client_addr].append(name)

                    elif command == 'ping':
                        answer = {'cmd': 'pong'}

                    elif command == 'proto':  # protocol version
                        proto = data['ver']
                        if proto > self.proto:
                            self.logger.warning("WebSocket: protocol mismatch. SmartHomeNG protocol version={0}, visu protocol version={1}".format(self.proto, proto))
                        elif proto < self.proto:
                            self.logger.warning("WebSocket: protocol mismatch. Update your client: {0}".format(client_addr))
                        answer = {'cmd': 'proto', 'ver': self.proto, 'server': 'module.websocket', 'time': self.shtime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")}

                    elif command == 'identity':  # identify client
                        client = data.get('sw', 'Visu')
                        self.sv_clients[client_addr]['sw'] = data.get('sw', '')
                        self.sv_clients[client_addr]['ver'] = data.get('ver', '')
                        self.sv_clients[client_addr]['hostname'] = data.get('hostname', '')
                        self.sv_clients[client_addr]['browser'] = data.get('browser', '')
                        self.sv_clients[client_addr]['bver'] = data.get('bver', '')
                        self.logger.info("smartVISU_protocol_v4: Client {} identified as '{} {}' in Browser '{} {}'".format(client_addr, self.sv_clients[client_addr]['sw'], self.sv_clients[client_addr]['ver'], self.sv_clients[client_addr]['browser'], self.sv_clients[client_addr]['bver']))
                        answer = {}

                    elif command == 'list_items':
                        answer = {}
                        if self.sv_querydef:
                            path = data.get('path', '')
                            answer = await self.request_list_items(path, client_addr)
                        self.logger.warning("{} <CMD  not yet tested: '{}'   -   from {}".format(protocol, data, client_addr))

                    elif command == 'list_logics':
                        answer = {}
                        if self.sv_querydef:
                            enabled = data.get('enabled', 0)
                            answer = await self.request_list_logics((enabled == 1), client_addr)
                        self.logger.warning("{} <CMD  not yet tested: '{}'   -   from {}".format(protocol, data, client_addr))

                    else:
                        self.logger.error("unsupported event: '{}'", data)
                    reply = json.dumps(answer, default=self.json_serial)
                except Exception as e:
                    self.logger.exception("visu_protocol Exception {}".format(e))

                if answer != {}:
                    # if an answer should be send, it is done here
                    try:
                        await websocket.send(reply)
                        self.logger.info("visu >REPLY: '{}'   -   to {}".format(answer, websocket.remote_address))
                    #except (asyncio.IncompleteReadError, asyncio.connection_closed) as e:
                    except Exception as e:
                        self.logger.error("smartVISU_protocol_v4: Exception in 'await websocket.send(reply)': {}".format(e))

        except Exception as e:
            if not str(e).startswith(('code = 1005', 'code = 1006')):
                self.logger.error("smartVISU_protocol_v4 exception: {}".format(e))
            else:
                self.logger.info("smartVISU_protocol_v4 error: {}".format(e))

        # Remove client from monitoring dict and from dict of active clients
        del(self.sv_monitor_items[client_addr])
        try:
            del(self.sv_clients[client_addr])
        except Exception as e:
            self.logger.error("smartVISU_protocol_v4 error deleting client session data: {}".format(e))

        self.logger.info("smartVISU_protocol_v4: Client {} stopped".format(client_addr))
        return

    async def prepare_monitor(self, data, client_addr):
        """
        Prepare the return of item monitoring data

        :param data: data of the visu's request
        :param client_addr: address of the client (visu)

        :return: answer to the visu
        """
        answer = {}
        items = []
        newmonitor_items = []
        for path in list(data['items']):
            path_parts = 0 if path is None else path.split('.property.')
            if len(path_parts) == 1:
                self.logger.debug("Client {0} requested to monitor item {1}".format(client_addr, path_parts[0]))
                try:
                    item = self.items.return_item(path)
                    if item is not None:
                        item_acl = item.conf.get('acl', None)
                        if item_acl is None:
                            item_acl = self.sv_acl
                        if item_acl != 'deny':
                            items.append([path, item()])
                        if self.update_visuitem not in item.get_method_triggers():
                            item.add_method_trigger(self.update_visuitem)
                    else:
                        self.logger.error("prepare_monitor: No item '{}' found".format(path))
                except KeyError as e:
                    self.logger.warning(
                        "KeyError: Client {0} requested to monitor item {1} which can not be found".format(
                            client_addr, path_parts[0]))
                else:
                    newmonitor_items.append(path)
            elif len(path_parts) == 2:
                self.logger.debug(
                    "Client {0} requested to monitor item {2} with property {1}".format(client_addr, path_parts[1],
                                                                                        path_parts[0]))
                try:
                    prop = self.items.return_item(path_parts[0]).property
                    prop_attr = getattr(prop, path_parts[1])
                    items.append([path, prop_attr])
                    newmonitor_items.append(path)
                except KeyError as e:
                    self.logger.warning(
                        "Property KeyError: Client {0} requested to monitor item {2} with property {1}".format(
                            client_addr, path_parts[1], path_parts[0]))
                except AttributeError as e:
                    self.logger.warning(
                        "Property AttributeError: Client {0} requested to monitor property {1} of item {2}".format(
                            client_addr, path_parts[1], path_parts[0]))

            else:
                self.logger.warning("Client {0} requested invalid item: {1}".format(client_addr, path))
        self.logger.debug(
            "json_parse: send to {0}: {1}".format(client_addr, ({'cmd': 'item', 'items': items})))  # MSinn
        answer = {'cmd': 'item', 'items': items}
        self.sv_monitor_items[client_addr] = newmonitor_items
        self.logger.info("Client {0} new monitored items are {1}".format(client_addr, newmonitor_items))
        return answer

    async def prepare_series(self, data, client_addr):
        """
        Prepare the return of series data

        :param data: data of the visu's request
        :param client_addr: address of the client (visu)

        :return: answer to the visu
        """
        answer = {}
        path = data['item']
        series = data['series']
        start = data['start']
        if 'end' in data:
            end = data['end']
        else:
            end = 'now'
        if 'count' in data:
            count = data['count']
        else:
            count = 100

        item = self.items.return_item(path)
        if item is not None:
            if hasattr(item, 'series'):
                try:
                    # reply = item.series(series, start, end, count)
                    reply = await self.loop.run_in_executor(None, item.series, series, start, end, count)
                except Exception as e:
                    self.logger.error("Problem fetching series for {0}: {1} - Wrong sqlite/database plugin?".format(path, e))
                else:
                    if 'update' in reply:
                        await self.loop.run_in_executor(None, self.set_periodic_series_updates, reply, client_addr)
                        #     self._series_lock.acquire()
                        #     self.sv_update_series[reply['sid']] = {'update': reply['update'], 'params': reply['params']}
                        #     self._series_lock.release()
                        del (reply['update'])
                        del (reply['params'])
                    if reply['series'] is not None:
                        answer = reply
                    else:
                        self.logger.info("WebSocket: no entries for series {} {}".format(path, series))
            else:
                if path.startswith('env.'):
                    self.logger.warning("Client {0} requested invalid series: {1}. Probably not database plugin is configured".format(client_addr, path))
                else:
                    self.logger.warning("Client {0} requested invalid series: {1}.".format(client_addr, path))
        return answer

    def set_periodic_series_updates(self, reply, client_addr):
        """
        -> blocking method - called via run_in_executor()
        """
        self._series_lock.acquire()
        if self.sv_update_series.get(client_addr, None) is None:
            self.sv_update_series[client_addr] = {}
        self.sv_update_series[client_addr][reply['sid']] = {'update': reply['update'], 'params': reply['params']}
        self._series_lock.release()
        return

    async def update_all_series(self):
        """
        Async task to periodically update the series data for the visu(s)
        """
        while self._sh.shng_status['code'] != 20:
            await asyncio.sleep(1)

        self.logger.info("update_all_series: Started")
        while True:
            remove = []
            series_list = list(self.sv_update_series.keys())
            if series_list != []:
                txt = ''
                if self.sv_ser_upd_cycle > 0:
                    txt = " - Fixed update-cycle time"
                #self.logger.info("update_all_series: series_list={}{}".format(series_list, txt))
            for client_addr in series_list:
                if (client_addr in self.sv_clients) and not (client_addr in remove):
                    self.logger.debug("update_all_series: Updating client {}...".format(client_addr))
                    websocket = self.sv_clients[client_addr]['websocket']
                    replys = await self.loop.run_in_executor(None, self.update_series, client_addr)
                    for reply in replys:
                        if (client_addr in self.sv_clients) and not (client_addr in remove):
                            self.logger.info("update_all_series: reply {} - Replys for client {}: {}".format(reply, client_addr, replys))
                            try:
                                await websocket.send(json.dumps(reply, default=self.json_serial))
                                self.logger.info(">SerUp {}: {}".format(websocket.remote_address, reply))
                            # except (asyncio.IncompleteReadError, asyncio.connection_closed) as e:
                            except Exception as e:
                                self.logger.info("update_all_series: Exception in 'await websocket.send(reply)': {}".format(e))
                                remove.append(client_addr)
                        else:
                            self.logger.info("update_all_series: Client {} is not active any more #1".format(client_addr))
                            pass
                else:
                    self.logger.info("update_all_series: Client {} is not active any more #2".format(client_addr))
                    remove.append(client_addr)

            # Remove series for clients that are not connected any more
            for client_addr in remove:
                del (self.sv_update_series[client_addr])

            await asyncio.sleep(10)
            if self.sv_ser_upd_cycle > 0:
                # wait for sv_ser_upd_cycle seconds before running update loop and update all series
                await asyncio.sleep(self.sv_ser_upd_cycle)
            else:
                # wait for 10 seconds before running update loop again (loop gets update cycle from database plugin)
                await asyncio.sleep(10)

    def update_series(self, client_addr):
        """
        -> blocking method - called via run_in_executor()
        """
        # websocket = self.sv_clients[client_addr]['websocket']
        now = self.shtime.now()
        self._series_lock.acquire()
        remove = []
        series_replys = []

        series_entry = self.sv_update_series.get(client_addr, None)
        if series_entry is not None:
            for sid, series in self.sv_update_series[client_addr].items():
                if (series['update'] < now) or self.sv_ser_upd_cycle > 0:
                    #self.logger.warning("update_series: {} - Processing sid={}, series={}".format(client_addr, sid, series))
                    item = self.items.return_item(series['params']['item'])
                    try:
                        reply = item.series(**series['params'])
                    except Exception as e:
                        self.logger.exception("Problem updating series for {0}: {1}".format(series['params'], e))
                        remove.append(sid)
                        continue
                    self.sv_update_series[client_addr][reply['sid']] = {'update': reply['update'], 'params': reply['params']}
                    del (reply['update'])
                    del (reply['params'])
                    if reply['series'] is not None:
                        series_replys.append(reply)

            for sid in remove:
                del (self.sv_update_series[client_addr][sid])

        self._series_lock.release()
        return series_replys

    async def cancel_series(self, data, client_addr):
        """
        Cancel the update of series data

        :param data: data of the visu's request
        :param client_addr: address of the client (visu)

        :return: answer to the visu
        """
        answer = {}
        path = data['item']
        series = data['series']

        if 'start' in data:
            start = data['start']
        else:
            start = '72h'
        if 'end' in data:
            end = data['end']
        else:
            end = 'now'
        if 'count' in data:
            count = data['count']
        else:
            count = 100

        self.logger.info("Series cancelation: path={}, series={}, start={}, end={}, count={}".format(path, series, start, end, count))
        item = self.items.return_item(path)
        try:
            # reply = item.series(series, start, end, count)
            reply = await self.loop.run_in_executor(None, item.series, series, start, end, count)
            self.logger.info("cancel_series: reply={}".format(reply))
            self.logger.info("cancel_series: self.sv_update_series={}".format(self.sv_update_series))
        except Exception as e:
            self.logger.error("cancel_series: Problem fetching series for {0}: {1} - Wrong sqlite plugin?".format(path, e))
        else:
            answer = await self.loop.run_in_executor(None, self.cancel_periodic_series_updates, reply, path, client_addr)
        return answer

    def cancel_periodic_series_updates(self, reply, path, client_addr):
        """
        -> blocking method - called via run_in_executor()
        """
        self._series_lock.acquire()
        try:
            del (self.sv_update_series[client_addr][reply['sid']])
            if self.sv_update_series[client_addr] == {}:
                del (self.sv_update_series[client_addr])
            self.logger.info("Series cancelation: Series updates for path {} canceled".format(path))
            answer = {'cmd': 'series_cancel', 'result': "Series updates for path {} canceled".format(path)}
        except:
            self.logger.warning("Series cancelation: No series for path {} found in list".format(path))
            answer = {'cmd': 'series_cancel', 'error': "No series for path {} found in list".format(path)}
        self._series_lock.release()
        return answer

    async def update_visu(self):
        """
        Async task to update the visu(s) if items have changed or an url command has been issued
        """
        while not self.janus_queue:
            await asyncio.sleep(1)

        while True:
            if self.janus_queue:
                queue_entry = await self.janus_queue.async_q.get()
                if queue_entry[0] == 'item':
                    item_data = queue_entry[1]
                    # item_data: set (item_name, item_value, caller, source)
                    try:
                        await self.update_item(item_data[0], item_data[1], item_data[3])
                    except Exception as e:
                        self.logger.error("update_visu: Error in 'await self.update_item(...)': {}".format(e))
                elif queue_entry[0] == 'log':
                    log_entry = queue_entry[1]
                    # log_entry: dict {'name', 'log'}
                    #            log is a list and contains dicts: {'time', 'thread', 'level', 'message'}
                    try:
                        await self.update_log(log_entry)
                    except Exception as e:
                        self.logger.error("update_visu: Error in 'await self.update_log(...)': {}".format(e))
                elif queue_entry[0] == 'command':
                    # send command to visu (e.g. url command)
                    command = queue_entry[1]
                    client_addr = queue_entry[2]
                    websocket = self.sv_clients[client_addr]['websocket']
                    try:
                        await websocket.send(command)
                        self.logger.warning(f"visu >command: '{command}'   -   to {client_addr}")
                    # except (asyncio.IncompleteReadError, asyncio.connection_closed) as e:
                    except Exception as e:
                        self.logger.error("smartVISU_protocol_v4: Exception in 'await websocket.send(url-command)': {}".format(e))
                else:
                    self.logger.error("update_visu: Unknown queueentry type '{}'".format(queue_entry[0]))

    async def update_item(self, item_name, item_value, source):
        """
        send JSON data with new value of an item
        """
        items = []
        # self.logger.warning("update_item: self.monitor['item']")
        items_list = list(self.sv_monitor_items.keys())
        for client_addr in items_list:
            websocket = self.sv_clients[client_addr]['websocket']
            for candidate in self.sv_monitor_items[client_addr]:

                try:
                    # self.logger.debug("Send update to Client {0} for candidate {1} and item_name {2}?".format(client_addr, candidate, item_name))
                    path_parts = candidate.split('.property.')
                    if path_parts[0] != item_name:
                        continue

                    if len(path_parts) == 1 and client_addr != source:
                        self.logger.debug("Send update to Client {0} for item {1}".format(client_addr, path_parts[0]))
                        items.append([path_parts[0], item_value])
                        continue

                    if len(path_parts) == 2:
                        self.logger.debug("Send update to Client {0} for item {1} with property {2}".format(client_addr, path_parts[0], path_parts[1]))
                        prop = self.items[path_parts[0]]['item'].property
                        prop_attr = getattr(prop,path_parts[1])
                        items.append([candidate, prop_attr])
                        continue

                    if client_addr == source:
                        self.logger.warning("update_item: client_addr == source - {}".format(client_addr))
                        continue

                    self.logger.warning("Could not send update to Client {0}: something is wrong with item path {1}, value={2}, source={3}".format(client_addr, item_name, item_value, source))
                except:
                    pass

            if len(items):  # only send an update if item/value pairs found to be send
                data = {'cmd': 'item', 'items': items}
                msg = json.dumps(data, default=self.json_serial)
                try:
                    self.logger.info("visu >MONIT: '{}'   -   to {}".format(msg, self.client_address(websocket)))
                    await websocket.send(msg)
                except Exception as e:
                    if not str(e).startswith(('code = 1005', 'code = 1006')):
                        self.logger.exception("update_item - Error in 'await websocket.send(data)': {}".format(e))
                    else:
                        self.logger.info("update_item - Error in 'await websocket.send(data)': {}".format(e))

        return

    async def update_log(self, log_entry):
        """
        send JSON data with update to log
        """
        remove = []
        logs_list = list(self.sv_monitor_logs.keys())
        for client_addr in logs_list:
            if (client_addr in self.sv_clients) and not (client_addr in remove):
                websocket = self.sv_clients[client_addr]['websocket']

                log_entry['cmd'] = 'log'
                msg = json.dumps(log_entry, default=self.json_serial)
                try:
                    self.logger.info(">LogUp {}: {}".format(self.client_address(websocket), msg))
                    await websocket.send(msg)
                except Exception as e:
                    if not str(e).startswith(('code = 1005', 'code = 1006')):
                        self.logger.exception("update_log - Error in 'await websocket.send(data)': {}".format(e))
                    else:
                        self.logger.info("update_log - Error in 'await websocket.send(data)': {}".format(e))
            else:
                self.logger.info("update_log: Client {} is not active any more".format(client_addr))
                remove.append(client_addr)

        # Remove series for clients that are not connected any more
        for client_addr in remove:
            del (self.sv_monitor_logs[client_addr])

        return

    async def request_logic(self, data, client_addr):
        """
        Request logic (trigger, enable, disable)
        """
        if 'name' not in data:
            return
        name = data['name']
        mylogic = self.logics.return_logic(name)
        if mylogic is not None:
            linfo = self.logics.get_logic_info(name)
            if linfo['visu_access']:
                if 'val' in data:
                    value = data['val']
                    self.logger.info("Client {0} triggerd logic {1} with '{2}'".format(client_addr, name, value))
                    mylogic.trigger(by='Visu', value=value, source=client_addr)
                if 'enabled' in data:
                    if data['enabled']:
                        self.logger.info("Client {0} enabled logic {1}".format(client_addr, name))
                        self.logics.enable_logic(name)
                        # non-persistant enable
                        # self.visu_logics[name].enable()
                    else:
                        self.logger.info("Client {0} disabled logic {1}".format(client_addr, name))
                        self.logics.disable_logic(name)
                        # non-persistant disable
                        # self.visu_logics[name].disable()
            else:
                self.logger.warning("Client {0} requested logic without visu-access: {1}".format(client_addr, name))
        else:
            self.logger.warning("Client {0} requested invalid logic: {1}".format(client_addr, name))
        return

    async def request_list_items(self, path, client_addr):
        """
        Build the requested list of logics
        """
        self.logger.info("Client {0} requested a list of defined items.".format(client_addr))
        myitems = []
        for i in self._sh.return_items():
            include = False
            #            if i.get('visu_acl', '').lower() != 'no':
            if (path == '') and ('.' not in i._path):
                include = True
            else:
                if i._path.startswith(path + '.'):
                    p = i._path[len(path + '.'):]
                    if '.' not in p:
                        include = True
            if include:
                myitem = collections.OrderedDict()
                myitem['path'] = i._path
                myitem['name'] = i._name
                myitem['type'] = i.type()
                myitems.append(myitem)

        response = collections.OrderedDict([('cmd', 'list_items'), ('items', myitems)])
        self.logger.info("Requested a list of defined items: {}".format(response))
        return response

    async def request_list_logics(self, enabled, client_addr):
        """
        Build the requested list of logics
        """
        self.logger.info("Client {0} requested a list of defined logics.".format(client_addr))
        logiclist = []
        for l in self.logics.return_loaded_logics():
            linfo = self.logics.get_logic_info(l)
            if linfo['visu_access']:
                if linfo['userlogic']:
                    logic_def = collections.OrderedDict()
                    logic_def['name'] = l
                    logic_def['desc'] = linfo['description']
                    logic_def['enabled'] = 1
                    if not linfo['enabled']:
                        logic_def['enabled'] = 0
                    if (not enabled) or (logic_def['enabled'] == 1):
                        logiclist.append(logic_def)

        response = collections.OrderedDict([('cmd', 'list_logics'), ('logics', logiclist)])
        self.logger.info("Requested a list of defined logics: {}".format(response))
        return response

    # ===============================================================================
    # Thread based (sync) methods of smartVISU support

    def update_visuitem(self, item, caller=None, source=None, dest=None):
        """
        This method gets called when an item value changes

        it is thread based and is called from other threads than the websocket module uses

        :param item: item object that has been changed
        :param caller: Caller that changed the item
        :param source: Source that made the caller change the item
        :param dest: Destination for the change (usually None)
        :return:
        """
        item_data = (item.id(), item(), caller, source)
        if self.janus_queue:
            # if queue has been created from the async side
            self.janus_queue.sync_q.put(['item', item_data])
            # self.logger.warning("update_visuitem: item={}, value={}, caller={}, source={}".format(item_data[0], item_data[1], item_data[2], item_data[3]))

        return

    def update_visulog(self, event, data):
        """
        This method gets called when an item value changes

        it is thread based and is called from other threads than the websocket module uses

        :param event: Type of monitored event (only 'log' is handled)
        :param data: data of log entry
        :return:
        """
        if event != 'log':
            return

        log_data = data.copy()  # don't filter the orignal data dict

        if not log_data['log'][0]['message'].startswith('>LogUp'):
            log_data['cmd'] = 'log'
            if self.janus_queue:
                # if queue has been created from the async side
                self.janus_queue.sync_q.put(['log', log_data])

        return

    def set_visu_url(self, url, clientip=''):
        """
        Tell the websocket client (visu) to load a specific url
        """
        for client_addr in self.sv_clients:
            ip, _, port = client_addr.partition(':')

            if (clientip == '') or (clientip == ip):
                command = json.dumps({'cmd': 'url', 'url': url})
                self.janus_queue.sync_q.put(['command', command, client_addr])

        return True

    def get_visu_client_info(self):
        """
        Get client info for web interface of smartvisu plugin
        :return:
        """
        client_list = []

        for client_addr in self.sv_clients:
            ip, _, port = client_addr.partition(':')

            infos = {}
            infos['ip'] = ip
            infos['port'] = port
            websocket = self.sv_clients[client_addr]['websocket']
            infos['protocol'] = 'wss' if websocket.secure else 'ws'
            infos['sw'] = self.sv_clients[client_addr]['sw']
            infos['swversion'] = self.sv_clients[client_addr].get('ver','')
            infos['hostname'] = self.sv_clients[client_addr]['hostname']
            infos['browser'] = self.sv_clients[client_addr]['browser']
            infos['browserversion'] = self.sv_clients[client_addr]['bver']

            client_list.append(infos)

        return client_list
