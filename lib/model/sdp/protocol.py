#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SDPProtocol and derived classes for SmartDevicePlugin class
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
#
#########################################################################

import logging

from lib.model.sdp.globals import (
    CONN_NET_TCP_CLI, JSON_MOVE_KEYS, PLUGIN_ATTR_CB_ON_CONNECT,
    PLUGIN_ATTR_CB_ON_DISCONNECT, PLUGIN_ATTR_CONNECTION,
    PLUGIN_ATTR_CONN_AUTO_CONN, PLUGIN_ATTR_CONN_CYCLE, PLUGIN_ATTR_CONN_RETRIES,
    PLUGIN_ATTR_CONN_TIMEOUT, PLUGIN_ATTR_MSG_REPEAT, PLUGIN_ATTR_MSG_TIMEOUT,
    PLUGIN_ATTR_NET_HOST, PLUGIN_ATTR_NET_PORT)
from lib.model.sdp.connection import SDPConnection

from collections import OrderedDict
from time import time
import threading
import queue
import json


#############################################################################################################################################################################################################################################
#
# class SDPProtocol and subclasses
#
#############################################################################################################################################################################################################################################

class SDPProtocol(SDPConnection):
    """ SDPProtocol class to provide protocol support for SmartDevicePlugin

    This class implements a basic protocol layer to act as a standin between
    the plugin class and the SDPConnection-class. Its purpose is to enable
    establishing a control layer, so the connection only has to care for the
    'physical' connection and the device only needs to operate on commmand basis.

    This implementation can also be seen as a 'NULL' protocol, it only passes
    along everything.

    By overwriting this class, different protocols can be implemented independent
    of the device and the connection classes.
    """

    def __init__(self, data_received_callback, name=None, **kwargs):

        self.logger = logging.getLogger(__name__)

        if SDP_standalone:
            self.logger = logging.getLogger('__main__')

        self.logger.debug(f'protocol initializing from {self.__class__.__name__} with arguments {kwargs}')

        # set class properties
        self._is_connected = False
        self._data_received_callback = data_received_callback

        # make sure we have a basic set of parameters
        self._params = {PLUGIN_ATTR_CB_ON_DISCONNECT: None,
                        PLUGIN_ATTR_CB_ON_CONNECT: None,
                        PLUGIN_ATTR_MSG_TIMEOUT: 3,
                        PLUGIN_ATTR_MSG_REPEAT: 3,
                        PLUGIN_ATTR_CONNECTION: SDPConnection}
        self._params.update(kwargs)

        # check if some of the arguments are usable
        self._set_connection_params()

        # initialize connection
        conn_params = self._params.copy()
        conn_params.update({PLUGIN_ATTR_CB_ON_CONNECT: self.on_connect, PLUGIN_ATTR_CB_ON_DISCONNECT: self.on_disconnect})
        self._connection = self._params[PLUGIN_ATTR_CONNECTION](self.on_data_received, name=name, **conn_params)

        # tell someone about our actual class
        self.logger.debug(f'protocol initialized from {self.__class__.__name__}')

    def _open(self):
        self.logger.debug(f'{self.__class__.__name__} _open called, opening protocol with params {self._params}')
        if not self._connection.connected():
            self._connection.open()

        self._is_connected = self._connection.connected()
        return self._is_connected

    def _close(self):
        self.logger.debug(f'{self.__class__.__name__} _close called, closing protocol')
        self._connection.close()
        self._is_connected = False

    def _send(self, data_dict):
        self.logger.debug(f'{self.__class__.__name__} _send called with {data_dict}')
        return self._connection.send(data_dict)

    def _get_connection(self, use_callbacks=False, name=None):
        conn_params = self._params.copy()

        cb_data = self.on_data_received if use_callbacks else None
        cb_connect = self.on_connect if use_callbacks else None
        cb_disconnect = self.on_disconnect if use_callbacks else None
        conn_params.update({PLUGIN_ATTR_CB_ON_CONNECT: cb_connect, PLUGIN_ATTR_CB_ON_DISCONNECT: cb_disconnect})

        conn_cls = self._get_connection_class(**conn_params)
        self._connection = conn_cls(cb_data, name=name, **conn_params)


class SDPProtocolJsonrpc(SDPProtocol):
    """ Protocol support for JSON-RPC 2.0

    This class implements a protocol to send JSONRPC 2.0  compatible messages
    As JSONRPC includes message-ids, replies can be associated to their respective
    queries and reply tracing and command repeat functions are implemented.

    Fragmented packets need to be collected and assembled;
    multiple received json packets neet to be split;
    processed packets will then be returned as received data.

    Data received is dispatched via callback, thus the send()-method does not
    return any response data.

    Callback syntax is:
        def connected_callback(by=None)
        def disconnected_callback(by=None)
        def data_received_callback(by, message, command=None)
    If callbacks are class members, they need the additional first parameter 'self'

    """
    def __init__(self, data_received_callback, name=None, **kwargs):

        self.logger = logging.getLogger(__name__)

        if SDP_standalone:
            self.logger = logging.getLogger('__main__')

        self.logger.debug(f'protocol initializing from {self.__class__.__name__} with arguments {kwargs}')

        # set class properties
        self._is_connected = False
        self._shutdown_active = False

        self._message_id = 0
        self._msgid_lock = threading.Lock()
        self._send_queue = queue.Queue()
        self._stale_lock = threading.Lock()

        self._receive_buffer = b''

        # make sure we have a basic set of parameters for the TCP connection
        self._params = {PLUGIN_ATTR_NET_HOST: '',
                        PLUGIN_ATTR_NET_PORT: 9090,
                        PLUGIN_ATTR_CONN_AUTO_CONN: True,
                        PLUGIN_ATTR_CONN_RETRIES: 1,
                        PLUGIN_ATTR_CONN_CYCLE: 3,
                        PLUGIN_ATTR_CONN_TIMEOUT: 3,
                        PLUGIN_ATTR_MSG_REPEAT: 3,
                        PLUGIN_ATTR_MSG_TIMEOUT: 5,
                        PLUGIN_ATTR_CB_ON_DISCONNECT: None,
                        PLUGIN_ATTR_CB_ON_CONNECT: None,
                        PLUGIN_ATTR_CONNECTION: CONN_NET_TCP_CLI,
                        JSON_MOVE_KEYS: []}
        self._params.update(kwargs)

        # check if some of the arguments are usable
        self._set_connection_params()

        # self._message_archive[str message_id] = [time() sendtime, str method, str params or None, int repeat]
        self._message_archive = {}

        self._check_stale_cycle = float(self._params[PLUGIN_ATTR_MSG_TIMEOUT]) / 2
        self._next_stale_check = 0
        self._last_stale_check = 0

        self._data_received_callback = data_received_callback

        # initialize connection
        self._get_connection(True, name=name)

        # tell someone about our actual class
        self.logger.debug(f'protocol initialized from {self.__class__.__name__}')

    def on_connect(self, by=None):
        self.logger.info(f'onconnect called by {by}, send queue contains {self._send_queue.qsize()} commands')
        super().on_connect(by)

    def on_disconnect(self, by=None):
        super().on_disconnect(by)

        # did we power down? then clear queues
        if self._shutdown_active:
            self._send_queue = queue.Queue()
            self._stale_lock.acquire()
            self._message_archive = {}
            self._stale_lock.release()
            self._shutdown_active = False

    def on_data_received(self, connection, response):
        """
        Handle received data

        Data is handed over as byte/bytearray and needs to be converted to 
        utf8 strings. As packets can be fragmented, all data is written into
        a buffer and then checked for complete json expressions. Those are
        separated, converted to dict and processed with respect to saved
        message-ids. Processed data packets are dispatched one by one via
        callback.
        """

        def check_chunk(data: str):
            print(f'I 0000 000000 lib.model.sdp.protocol | checking chunk {data}')
            try:
                json.loads(data)
                print('W 0000 000000 lib.model.sdp.protocol | chunk checked ok')
                return True
            except Exception:
                print('E 0000 000000 lib.model.sdp.protocol | chunk not valid json')
                return False

        self.logger.debug(f'data received before encode: {response}')

        if isinstance(response, (bytes, bytearray)):
            response = str(response, 'utf-8').strip()

        self.logger.debug(f'adding response to buffer: {response}')
        self._receive_buffer += response

        datalist = []
        if '}{' in self._receive_buffer:

            # split multi-response data into list items
            try:
                self.logger.debug(f'attempting to split buffer')
                tmplist = self._receive_buffer.replace('}{', '}-#-{').split('-#-')
                datalist = list(OrderedDict((x, True) for x in tmplist).keys())
                self._receive_buffer = ''
            except Exception:
                pass
        elif self._receive_buffer[0] == '{' and self._receive_buffer[-1] == '}' and check_chunk(self._receive_buffer):
            datalist = [self._receive_buffer]
            self._receive_buffer = ''
        elif self._receive_buffer:
            self.logger.debug(f'Buffer with incomplete response: {self._receive_buffer}')

        if datalist:
            self.logger.debug(f'received {len(datalist)} data items')

        # process all response items
        for data in datalist:
            self.logger.debug(f'Processing received data item #{datalist.index(data)}: {data}')

            try:
                jdata = json.loads(data)
            except Exception as err:
                if data == datalist[-1]:
                    self.logger.debug(f'returning incomplete data to buffer: {data}')
                    self._receive_buffer = data
                else:
                    self.logger.warning(f'Could not json.load data item {data} with error {err}')
                continue

            command = None

            # check messageid for replies
            if 'id' in jdata:
                response_id = jdata['id']

                # reply or error received, remove command
                if response_id in self._message_archive:
                    # possibly the command was resent and removed before processing the reply
                    # so let's 'try' at least...
                    try:
                        command = self._message_archive[response_id][1]
                        del self._message_archive[response_id]
                    except KeyError:
                        command = '(deleted)' if '_' not in response_id else response_id[response_id.find('_') + 1:]
                else:
                    command = None

                # log possible errors
                if 'error' in jdata:
                    self.logger.error(f'received error {jdata} in response to command {command}')
                elif command:
                    self.logger.debug(f'command {command} sent successfully')

            # process data
            if self._data_received_callback:
                self._data_received_callback(connection, jdata, command)

        # check _message_archive for old commands - check time reached?
        if self._next_stale_check < time():

            # try to lock check routine, fail quickly if already locked = running
            if self._stale_lock.acquire(False):

                # we cannot deny access to self._message_archive as this would block sending
                # instead, copy it and check the copy
                stale_messages = self._message_archive.copy()
                remove_ids = []
                requeue_cmds = []

                # self._message_archive[message_id] = [time(), command, params, repeat]
                self.logger.debug(f'Checking for unanswered commands, last check was {int(time()) - self._last_stale_check} seconds ago, {len(self._message_archive)} commands saved')
                # !! self.logger.debug('Stale commands: {}'.format(stale_messages))
                for (message_id, (send_time, command, params, repeat)) in stale_messages.items():

                    if send_time + self._params[PLUGIN_ATTR_MSG_TIMEOUT] < time():

                        # reply timeout reached, check repeat count
                        if repeat <= self._params[PLUGIN_ATTR_MSG_REPEAT]:

                            # send again, increase counter
                            self.logger.info(f'Repeating unanswered command {command} ({params}), try {repeat + 1}')
                            requeue_cmds.append([command, params, message_id, repeat + 1])
                        else:
                            self.logger.info(f'Unanswered command {command} ({params}) repeated {repeat} times, giving up.')
                            remove_ids.append(message_id)

                for msgid in remove_ids:
                    # it is possible that while processing stale commands, a reply arrived
                    # and the command was removed. So just to be sure, 'try' and delete...
                    self.logger.debug(f'Removing stale msgid {msgid} from archive')
                    try:
                        del self._message_archive[msgid]
                    except KeyError:
                        pass

                # resend pending repeats - after original
                for (command, params, message_id, repeat) in requeue_cmds:
                    self._send_rpc_message(command, params, message_id, repeat)

                # set next stale check time
                self._last_stale_check = time()
                self._next_stale_check = self._last_stale_check + self._check_stale_cycle

                del stale_messages
                del requeue_cmds
                del remove_ids
                self._stale_lock.release()

            else:
                self.logger.debug(f'Skipping stale check {time() - self._last_stale_check} seconds after last check')

    def _send(self, data_dict):
        """
        wrapper to prepare json rpc message to send. extracts command, id, repeat and
        params (data) from data_dict and call send_rpc_message(command, params, id, repeat)
        """
        command = data_dict.get('command', data_dict.get('method', data_dict.get('payload')))
        message_id = data_dict.get('message_id', None)
        repeat = data_dict.get('repeat', 0)

        self._send_rpc_message(command, data_dict, message_id, repeat)

        # we don't return a response (this goes via on_data_received)
        return None

    def _send_rpc_message(self, command, ddict=None, message_id=None, repeat=0):
        """
        Send a JSON RPC message.
        The JSON string is extracted from the supplied command and the given parameters.

        :param command: the command to be triggered
        :param ddict: dictionary with command data, e.g. keys 'params', 'data', 'headers', 'request_method'...
        :param message_id: the message ID to be used. If none, use the internal counter
        :param repeat: counter for how often the message has been repeated
        """
        self.logger.debug(f'preparing message to send command {command} with data {ddict}, try #{repeat}')

        if message_id is None:
            # safely acquire next message_id
            # !! self.logger.debug('Locking message id access ({})'.format(self._message_id))
            self._msgid_lock.acquire()
            self._message_id += 1
            new_msgid = self._message_id
            self._msgid_lock.release()
            message_id = str(new_msgid) + '_' + command
            # !! self.logger.debug('Releasing message id access ({})'.format(self._message_id))

        if not ddict:
            ddict = {}

        method = ddict.get('method', command)

        # create message packet
        new_data = {'jsonrpc': '2.0', 'id': message_id, 'method': method}

        if 'data' in ddict and ddict['data']:

            # ddict already contains 'data', we either have an old "ready" packet or new data
            if 'jsonrpc' not in ddict['data']:

                # we don't have a jsonrpc header, add new data to new header
                new_data['params'] = ddict['data']
            else:
                # jsonrpc header present, keep packet as is
                new_data = ddict['data']

        # set packet data
        ddict['data'] = new_data

        for key in self._params[JSON_MOVE_KEYS]:
            if key in ddict:
                if 'params' not in ddict['data']:
                    ddict['data']['params'] = {}
                ddict['data']['params'][key] = ddict[key]
                del ddict[key]

        # convert data if not using HTTP connections
        if 'request_method' not in ddict:

            try:
                # if 'payload' in ddict:
                #     ddict['payload'] += json.dumps(ddict['data'])
                # else:
                ddict['payload'] = json.dumps(ddict['data'])
            except Exception as e:
                raise ValueError(f'data {ddict["data"]} not convertible to JSON, aborting. Error was: {e}')

        # push message in queue
        self._send_queue.put([message_id, command, ddict, repeat])

        # try to actually send all queued messages
        self.logger.debug(f'processing queue - {self._send_queue.qsize()} elements')
        while not self._send_queue.empty():
            (message_id, command, ddict, repeat) = self._send_queue.get()

            self._message_archive[message_id] = [time(), command, ddict, repeat]

            self.logger.debug(f'sending queued msg {message_id} - {command} (#{repeat})')
            response = self._connection.send(ddict)
            if response:
                self.on_data_received('request', response)
