#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SDPConnection and derived classes for SmartDevicePlugin class
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
import sys
from time import sleep, time
import requests
import socket
from threading import Lock, Thread
from contextlib import contextmanager
import json

from lib.network import Tcp_client

from lib.model.sdp.globals import (sanitize_param, CONN_NET_TCP_REQ, CONN_NULL, CONN_SER_DIR, CONNECTION_TYPES,
                                   PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_ON_DISCONNECT, PLUGIN_ATTR_CONNECTION,
                                   PLUGIN_ATTR_CONN_AUTO_CONN, PLUGIN_ATTR_CONN_AUTO_RECONN, PLUGIN_ATTR_CONN_BINARY,
                                   PLUGIN_ATTR_CONN_CYCLE, PLUGIN_ATTR_CONN_RETRIES, PLUGIN_ATTR_CONN_TERMINATOR,
                                   PLUGIN_ATTR_CONN_TIMEOUT, PLUGIN_ATTR_NET_HOST, PLUGIN_ATTR_NET_PORT,
                                   PLUGIN_ATTR_PROTOCOL, PLUGIN_ATTR_SERIAL_BAUD, PLUGIN_ATTR_SERIAL_BSIZE,
                                   PLUGIN_ATTR_SERIAL_PARITY, PLUGIN_ATTR_SERIAL_PORT, PLUGIN_ATTR_SERIAL_STOP,
                                   PLUGIN_ATTRS, PROTO_NULL, PROTOCOL_TYPES, REQUEST_DICT_ARGS)


#############################################################################################################################################################################################################################################
#
# class SDPConnection and subclasses
#
#############################################################################################################################################################################################################################################

class SDPConnection(object):
    """ SDPConnection class to provide actual connection support

    This class is the base class for further connection classes. It can - well,
    not much. Opening and closing of connections and writing and receiving data
    is something to implement in the interface-specific derived classes.
    """
    def __init__(self, data_received_callback, name=None, **kwargs):

        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)

        if SDP_standalone:
            self.logger = logging.getLogger('__main__')

        self.logger.debug(f'connection initializing from {self.__class__.__name__} with arguments {kwargs}')

        # set class properties
        self._is_connected = False
        self._data_received_callback = data_received_callback
        self.dummy = None   # dummy response for testing

        # we set defaults for all possible connection parameters, so we don't
        # need to care later if a parameter is set or not
        # these will be overwritten by all parameters set in plugin.yaml
        self._params = {PLUGIN_ATTR_SERIAL_PORT: '',
                        PLUGIN_ATTR_SERIAL_BAUD: 9600,
                        PLUGIN_ATTR_SERIAL_BSIZE: 8,
                        PLUGIN_ATTR_SERIAL_PARITY: 'N',
                        PLUGIN_ATTR_SERIAL_STOP: 1,
                        PLUGIN_ATTR_PROTOCOL: None,
                        PLUGIN_ATTR_NET_HOST: '',
                        PLUGIN_ATTR_NET_PORT: 0,
                        PLUGIN_ATTR_CONN_BINARY: False,
                        PLUGIN_ATTR_CONN_TIMEOUT: 1.0,
                        PLUGIN_ATTR_CONN_AUTO_RECONN: True,
                        PLUGIN_ATTR_CONN_AUTO_CONN: True,
                        PLUGIN_ATTR_CONN_RETRIES: 1,
                        PLUGIN_ATTR_CONN_CYCLE: 3,
                        PLUGIN_ATTR_CONN_TERMINATOR: '',
                        PLUGIN_ATTR_CB_ON_CONNECT: None,
                        PLUGIN_ATTR_CB_ON_DISCONNECT: None}
        self._params.update(kwargs)

        # check if some of the arguments are usable
        self._set_connection_params()

        # tell someone about our actual class
        if not kwargs.get('done', True):
            self.logger.debug(f'connection initialized from {self.__class__.__name__}')

    def open(self):
        """ wrapper method provides stable interface and allows overwriting """
        self.logger.debug('open method called for connection')
        if self._open():
            self._is_connected = True
            self._send_init_on_open()

        return self._is_connected

    def close(self):
        """ wrapper method provides stable interface and allows overwriting """
        self.logger.debug('close method called for connection')
        self._close()
        self._is_connected = False

    def send(self, data_dict):
        """
        Send data, possibly return response

        :param data: dict with raw data and possible additional parameters to send
        :type data_dict: dict
        :return: raw response data if applicable, None otherwise. Errors need to raise exceptions
        """
        if not self._is_connected:
            if self._params[PLUGIN_ATTR_CONN_AUTO_CONN]:
                self._open()
            if not self._is_connected:
                raise RuntimeError('trying to send, but not connected')

        data = data_dict.get('payload', None)
        if not data:
            raise ValueError('send provided with empty data_dict["payload"], aborting')

        response = None

        if self._send_init_on_send():
            response = self._send(data_dict)

        return response

    def connected(self):
        """ getter for self._is_connected """
        return self._is_connected

    def on_data_received(self, by, data):
        """ callback for on_data_received event """
        if data:
            self.logger.debug(f'received raw data "{data}" from "{by}"')
            if self._data_received_callback:
                self._data_received_callback(by, data)

    def on_connect(self, by=None):
        """ callback for on_connect event """
        self._is_connected = True
        self.logger.info(f'on_connect called by {by}')
        if self._params[PLUGIN_ATTR_CB_ON_CONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_CONNECT](by)

    def on_disconnect(self, by=None):
        """ callback for on_disconnect event """
        self.logger.debug(f'on_disconnect called by {by}')
        self._is_connected = False
        if self._params[PLUGIN_ATTR_CB_ON_DISCONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_DISCONNECT](by)

    #
    #
    # overwriting needed for at least some of the following methods...
    #
    #

    def _open(self):
        """
        overwrite with opening of connection

        :return: True if successful
        :rtype: bool
        """
        self.logger.debug(f'simulating opening connection as {__name__} with params {self._params}')
        return True

    def _close(self):
        """
        overwrite with closing of connection
        """
        self.logger.debug(f'simulating closing connection as {__name__} with params {self._params}')

    def _send(self, data_dict):
        """
        overwrite with sending of data and - possibly - returning response data
        Return None if no response is received or expected.
        """
        self.logger.debug(f'simulating to send data {data_dict}...')
        return self.dummy

    def _send_init_on_open(self):
        """
        This class can be overwritten if anything special is needed to make the
        other side talk after opening the connection... ;)

        Using class properties instead of arguments makes overwriting easy.

        It is routinely called by self.open()
        """
        pass

    def _send_init_on_send(self):
        """
        This class can be overwritten if anything special is needed to make the
        other side talk before sending commands... ;)

        Cancel sending if it returns False...

        It is routinely called by self.send()
        """
        return True

    #
    #
    # private utility methods
    #
    #

    def _set_connection_params(self):
        """
        Try to set some of the common parameters.
        Might need to be overwritten...
        """
        for arg in PLUGIN_ATTRS:
            if arg in self._params:
                self._params[arg] = sanitize_param(self._params[arg])

    def __str__(self):
        return self.__class__.__name__

    def _get_connection_class(self, connection_type=None, connection_classname=None, connection_cls=None, **params):

        if not params:
            params = self._params

        connection_module = sys.modules.get('lib.model.sdp.connection', '')
        if not connection_module:
            self.logger.error('unable to get object handle of SDPConnection module')
            return None

        try:

            # class not set
            if not connection_cls:

                # do we have a class type from parameters?
                if PLUGIN_ATTR_CONNECTION in params and type(params[PLUGIN_ATTR_CONNECTION]) is type and issubclass(params[PLUGIN_ATTR_CONNECTION], SDPConnection):

                    # directly assign class
                    connection_cls = params[PLUGIN_ATTR_CONNECTION]
                    connection_classname = connection_cls.__name__

                else:
                    # classname not known
                    if not connection_classname:

                        # do we have an unknown connection type from parameters?
                        if PLUGIN_ATTR_CONNECTION in params and params[PLUGIN_ATTR_CONNECTION] not in CONNECTION_TYPES:

                            # assume name of unknown class
                            connection_classname = params[PLUGIN_ATTR_CONNECTION]
                            connection_type = 'manual'

                        # wanted connection type not known yet
                        if not connection_type:

                            # known connection type given in parameters?
                            if PLUGIN_ATTR_CONNECTION in params and params[PLUGIN_ATTR_CONNECTION] in CONNECTION_TYPES:

                                # user given connection type
                                connection_type = params[PLUGIN_ATTR_CONNECTION]

                            # host given in parameters?
                            elif PLUGIN_ATTR_NET_HOST in params and params[PLUGIN_ATTR_NET_HOST]:

                                # no further information on network specifics, use basic HTTP TCP client
                                connection_type = CONN_NET_TCP_REQ

                            # serial port given in parameters?
                            elif PLUGIN_ATTR_SERIAL_PORT in params and params[PLUGIN_ATTR_SERIAL_PORT]:

                                # this seems to be a serial killer application
                                connection_type = CONN_SER_DIR

                            if not connection_type:
                                # if not preset and not identified, use "empty" connection, e.g. for testing
                                # when physical device is not present
                                connection_type = CONN_NULL

                        # build classname from type
                        connection_classname = 'SDPConnection' + ''.join([tok.capitalize() for tok in connection_type.split('_')])

                    # get class from classname -> only for predefined classes, not for custom plugin classes!
                    connection_cls = getattr(connection_module, connection_classname, getattr(connection_module, 'SDPConnection'))

        except (TypeError, AttributeError):
            self.logger.warning(f'could not identify wanted connection class from {connection_cls}, {connection_classname}, {connection_type}. Using default connection.')
            connection_cls = SDPConnection

        return connection_cls

    def _get_protocol_class(self, protocol_cls=None, protocol_classname=None, protocol_type=None, **params):

        if not params:
            params = self._params

        protocol_module = sys.modules.get('lib.model.sdp.protocol', '')
        if not protocol_module:
            self.logger.error('unable to get object handle of SDPProtocol module')
            return None

        # class not set
        if not protocol_cls:

            # do we have a class type from params?
            if PLUGIN_ATTR_PROTOCOL in params and type(params[PLUGIN_ATTR_PROTOCOL]) is type and issubclass(params[PLUGIN_ATTR_PROTOCOL], SDPConnection):

                # directly use given class
                protocol_cls = params[PLUGIN_ATTR_PROTOCOL]
                protocol_classname = protocol_cls.__name__

            else:
                # classname not known
                if not protocol_classname:

                    # do we have a protocol name
                    if PLUGIN_ATTR_PROTOCOL in params and isinstance(params[PLUGIN_ATTR_PROTOCOL], str):
                        if params[PLUGIN_ATTR_PROTOCOL] not in PROTOCOL_TYPES:
                            protocol_classname = params[PLUGIN_ATTR_PROTOCOL]
                            protocol_type = 'manual'

                    # wanted connection type not known
                    if not protocol_type:

                        if PLUGIN_ATTR_PROTOCOL in params and params[PLUGIN_ATTR_PROTOCOL] in PROTOCOL_TYPES:
                            protocol_type = params[PLUGIN_ATTR_PROTOCOL]
                        else:
                            protocol_type = PROTO_NULL

                    # got unknown protocol type
                    if protocol_type not in PROTOCOL_TYPES:
                        self.logger.error(f'protocol "{protocol_type}" specified, but unknown and not class type or class name. Using default protocol')
                        protocol_type = PROTO_NULL

                    # get classname from type
                    protocol_classname = 'SDPProtocol' + ''.join([tok.capitalize() for tok in protocol_type.split('_')])

                # get class from classname
                protocol_cls = getattr(protocol_module, protocol_classname, None)

        if not protocol_cls:
            self.logger.error(f'protocol {self._parameters[PLUGIN_ATTR_PROTOCOL]} specified, but not loadable.')
            return None

        return protocol_cls


class SDPConnectionNetTcpRequest(SDPConnection):
    """ Connection via TCP / HTTP requests

    This class implements TCP connections in the query-reply matter using
    the requests library, e.g. for HTTP communication.

    The data_dict['payload']-Data needs to be the full query URL. Additional
    parameter dicts can be added to be given to requests.request, as
    - request_method: get (default) or post
    - headers, data, cookies, files: passed thru to request()
    - data is encoded in the url for GET or sent as dict for POST

    Response data is returned as text. Errors raise HTTPException
    """
    def _open(self):
        self.logger.debug(f'{self.__class__.__name__} opening connection as {__name__} with params {self._params}')
        return True

    def _close(self):
        self.logger.debug(f'{self.__class__.__name__} closing connection as {__name__} with params {self._params}')

    def _send(self, data_dict):
        url = data_dict.get('payload', None)
        if not url:
            self.logger.error(f'can not send without url parameter from data_dict {data_dict}, aborting')
            return False

        # default to get if not 'post' specified
        request_method = data_dict.get('request_method', 'get')

        # check for additional data
        par = {}
        for arg in (REQUEST_DICT_ARGS):
            par[arg] = data_dict.get(arg, {})

        if request_method == 'get':
            par['params'] = par['data']
            par['data'] = {}
        else:
            par['params'] = {}

        # needed for LMS, Requests does funny things converting data dict to json...
        par['data'] = json.dumps(par['data'])

        # send data
        response = requests.request(request_method, url,
                                    params=par['params'],
                                    headers=par['headers'],
                                    data=par['data'],
                                    cookies=par['cookies'],
                                    files=par['files'])

        self.logger.debug(f'{self.__class__.__name__} received response {response.text} with code {response.status_code}')

        if 200 <= response.status_code < 400:
            return response.text
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                raise requests.HTTPError(f'TCP request returned code {response.status_code}, error was: {e}')
        return None


class SDPConnectionNetTcpClient(SDPConnection):
    """ Connection via direct TCP connection with listener

    This class implements a TCP connection using a single persistent connection
    to send data and an anynchronous listener with callback for receiving data.

    Data received is dispatched via callback, thus the send()-method does not
    return any response data.

    Callback syntax is:
        def disconnected_callback()
        def data_received_callback(command, message)
    If callbacks are class members, they need the additional first parameter 'self'
    """
    def __init__(self, data_received_callback, name=None, **kwargs):

        super().__init__(data_received_callback, done=False, **kwargs)

        if isinstance(self._params[PLUGIN_ATTR_CONN_TERMINATOR], str):
            self._params[PLUGIN_ATTR_CONN_TERMINATOR] = bytes(self._params[PLUGIN_ATTR_CONN_TERMINATOR], 'utf-8')

        # initialize connection
        self._tcp = Tcp_client(host=self._params[PLUGIN_ATTR_NET_HOST],
                               port=self._params[PLUGIN_ATTR_NET_PORT],
                               name=name,
                               autoreconnect=self._params[PLUGIN_ATTR_CONN_AUTO_CONN],
                               connect_retries=self._params[PLUGIN_ATTR_CONN_RETRIES],
                               connect_cycle=self._params[PLUGIN_ATTR_CONN_CYCLE],
                               terminator=self._params[PLUGIN_ATTR_CONN_TERMINATOR])
        self._tcp.set_callbacks(data_received=self.on_data_received,
                                disconnected=self.on_disconnect,
                                connected=self.on_connect)

        # tell someone about our actual class
        self.logger.debug(f'connection initialized from {self.__class__.__name__}')

    def _open(self):
        self.logger.debug(f'{self.__class__.__name__} opening connection with params {self._params}')
        if not self._tcp.connected():
            self._tcp.connect()
            # give a moment to establish connection (threaded call).
            # immediate return would always fail
            # "proper" control can be exercised by using on_connect callback
            sleep(2)
        return self._tcp.connected()

    def _close(self):
        self.logger.debug(f'{self.__class__.__name__} closing connection')
        self._tcp.close()

    def _send(self, data_dict):
        self._tcp.send(data_dict['payload'])

        # we receive only via callback, so we return "no reply".
        return None


class UDPServer(socket.socket):
    """
    This class sets up a UDP unicast socket listener on local_port
    """
    def __init__(self, local_port):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.bind(('0.0.0.0', local_port))


class SDPConnectionNetUdpRequest(SDPConnectionNetTcpRequest):
    """ Connection via TCP / HTTP requests and listens for UDP messages

    This class implements TCP connections in the query-reply matter using
    the requests library, e.g. for HTTP communication.

    The data_dict['payload']-Data needs to be the full query URL. Additional
    parameter dicts can be added to be given to requests.request, as
    - method: get (default) or post
    - headers, data, cookies, files, params: passed thru to request()

    Response data is returned as text. Errors raise HTTPException
    """
    def __init__(self, data_received_callback, name=None, **kwargs):

        super().__init__(data_received_callback, name, **kwargs)

        self.alive = False
        self._sock = None
        self._srv_buffer = 1024
        self.__receive_thread = None
        self._connected = True

    def _open(self):
        self.logger.debug(f'{self.__class__.__name__} opening connection with params {self._params}')
        self.alive = True
        self.__receive_thread = Thread(target=self._receive_thread_worker, name='UDP_Listener')
        self.__receive_thread.daemon = True
        self.__receive_thread.start()

        return True

    def _close(self):
        self.logger.debug(f'{self.__class__.__name__} closing connection')
        self.alive = False
        try:
            self._sock.close()
        except Exception:
            pass

    def _receive_thread_worker(self):
        self.sock = UDPServer(self._params[PLUGIN_ATTR_NET_PORT])
        if self._params[PLUGIN_ATTR_CB_ON_CONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_CONNECT](self.__str__() + ' UDP_listener')
        while self.alive:
            data, addr = self.sock.recvfrom(self._srv_buffer)
            try:
                host, port = addr
            except Exception as e:
                self.logger.warning(f'error receiving data - host/port not readable. Error was: {e}')
                return
            else:
                # connected device sends updates every second for
                # about 10 minutes without further interaction
                if self._data_received_callback:
                    self._data_received_callback(host, data.decode('utf-8'))

        self.sock.close()
        if self._params[PLUGIN_ATTR_CB_ON_DISCONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_DISCONNECT](self.__str__() + ' UDP_listener')


class SDPConnectionSerial(SDPConnection):
    """ Connection for serial connectivity

    This class implements a serial connection using a single persistent connection
    to send data and receive immediate answers.

    The data_dict provided to send() need the data to send in data_dict['payload']
    and the required response read mode in data_dict['data']['response']:


    If callbacks are provided, they are utilized; data_received_callback will be
    called in addition to returning the result to send() calls.

    Callback syntax is:
        def connected_callback(by=None)
        def disconnected_callback(by=None)
        def data_received_callback(by, message)
    If callbacks are class members, they need the additional first parameter 'self'
    """
    def __init__(self, data_received_callback, name=None, **kwargs):

        class TimeoutLock(object):
            def __init__(self):
                self._lock = Lock()

            def acquire(self, blocking=True, timeout=-1):
                return self._lock.acquire(blocking, timeout)

            @contextmanager
            def acquire_timeout(self, timeout):
                result = self._lock.acquire(timeout=timeout)
                yield result
                if result:
                    self._lock.release()

            def release(self):
                self._lock.release()

        # only import serial now we know we need it -> reduce requirements for non-serial setups
        import serial

        super().__init__(data_received_callback, done=False, name=name, **kwargs)

        # set class properties
        self._lock = TimeoutLock()
        self.__lock_timeout = 2
        self._timeout_mult = 3
        self._lastbyte = b''
        self._lastbytetime = 0
        self._connection_attempts = 0
        self._read_buffer = b''
        self.__use_read_buffer = True
        self._listener_active = False

        # initialize connection
        self._connection = serial.Serial()
        self._connection.baudrate = self._params[PLUGIN_ATTR_SERIAL_BAUD]
        self._connection.parity = self._params[PLUGIN_ATTR_SERIAL_PARITY]
        self._connection.bytesize = self._params[PLUGIN_ATTR_SERIAL_BSIZE]
        self._connection.stopbits = self._params[PLUGIN_ATTR_SERIAL_STOP]
        self._connection.port = self._params[PLUGIN_ATTR_SERIAL_PORT]
        self._connection.timeout = self._params[PLUGIN_ATTR_CONN_TIMEOUT]

        # tell someone about our actual class
        self.logger.debug(f'connection initialized from {self.__class__.__name__}')

    def _open(self):
        if self._is_connected:
            return True
        self.logger.debug(f'{self.__class__.__name__} _open called with params {self._params}')

        while not self._is_connected and self._connection_attempts <= self._params[PLUGIN_ATTR_CONN_RETRIES]:

            self._connection_attempts += 1
            self._lock.acquire()
            try:
                self._connection.open()
                self._is_connected = True
                self.logger.info(f'connected to {self._params[PLUGIN_ATTR_SERIAL_PORT]}')
                self._connection_attempts = 0
                if self._params[PLUGIN_ATTR_CB_ON_CONNECT]:
                    self._params[PLUGIN_ATTR_CB_ON_CONNECT](self)
                self._setup_listener()
                return True
            except (serial.SerialException, ValueError) as e:
                self.logger.error(f'error on connection to {self._params[PLUGIN_ATTR_SERIAL_PORT]}. Error was: {e}')
                self._connection_attempts = 0
                return False
            finally:
                self._lock.release()

            if not self._is_connected:
                sleep(self._params[PLUGIN_ATTR_CONN_CYCLE])

        self.logger.error(f'error on connection to {self._params[PLUGIN_ATTR_SERIAL_PORT]}, max number of connection attempts reached')
        self._connection_attempts = 0
        return False

    def _close(self):
        self.logger.debug(f'{self.__class__.__name__} _close called')
        self._is_connected = False
        try:
            self._connection.close()
        except Exception:
            pass
        self.logger.info(f'connection to {self._params[PLUGIN_ATTR_SERIAL_PORT]} closed')
        if self._params[PLUGIN_ATTR_CB_ON_DISCONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_DISCONNECT](self)

    def _send(self, data_dict):
        """
        send data. data_dict needs to contain the following information:

        data_dict['payload']: data to send
        data_dict['limit_response']: expected response type/length:
                                     - number of bytes to read as response
                                     - terminator to recognize end of reply
                                     - 0 to read till timeout

        On errors, exceptions are raised

        :param data_dict: data_dict to send (used value is data_dict['payload'])
        :type data_dict: dict
        :return: response as bytes() or None if no response is received or limit_response is None
        """
        self.logger.debug(f'{self.__class__.__name__} _send called with {data_dict}')

        data = data_dict['payload']
        if not type(data) in (bytes, bytearray, str):
            try:
                data = str(data)
            except Exception as e:
                raise ValueError(f'provided payload {data} could not be converted to string. Error was: {e}')
        if isinstance(data, str):
            data = data.encode('utf-8')

        if self._params[PLUGIN_ATTR_CONN_AUTO_CONN]:
            self._open()

        if not self._is_connected:
            raise serial.SerialException(f'trying to send {data}, but connection can\'t be opened.')

        if not self._send_bytes(data):
            self.is_connected = False
            raise serial.SerialException(f'data {data} could not be sent')

        # don't try to read response if listener is active
        if self._listener_active:
            return None

        rlen = data_dict.get('limit_response', None)
        if rlen is None:
            return None
        else:
            res = self._read_bytes(rlen)
            if not self.params[PLUGIN_ATTR_CONN_BINARY]:
                res = str(res, 'utf-8').strip()

            if self._data_received_callback:
                self._data_received_callback(self, res, None)

            return res

    def _send_bytes(self, packet):
        """
        Send data to device

        :param packet: Data to be sent
        :type packet: bytearray|bytes
        :return: Returns False, if no connection is established or write failed; number of written bytes otherwise
        """
        # self.logger.debug(f'{self.__class__.__name__} _send_bytes called with {packet}')

        if not self._is_connected:
            self.logger.debug('_send_bytes not connected, aborting')
            return False

        try:
            numbytes = self._connection.write(packet)
        except serial.SerialTimeoutException:
            return False

        # self.logger.debug(f'_send_bytes: sent {packet} with {numbytes} bytes')
        return numbytes

    def _read_bytes(self, limit_response, clear_buffer=False):
        """
        Try to read bytes from device, return read bytes
        if limit_response is int > 0, try to read at least <limit_response> bytes
        if limit_response is bytes() or bytearray(), try to read till receiving <limit_response>
        if limit_response is 0, read until timeout (use with care...)

        :param limit_response: Number of bytes to read, b'<terminator> for terminated read, 0 for unrestricted read (timeout)
        :return: read bytes
        :rtype: bytes
        """
        # self.logger.debug(f'{self.__class__.__name__} _read_bytes called with limit {limit_response}')

        if not self._is_connected:
            return 0

        maxlen = 0
        term_bytes = None
        if isinstance(limit_response, int):
            maxlen = limit_response
        elif isinstance(limit_response, (bytes, bytearray, str)):
            term_bytes = bytes(limit_response)

        # take care of "overflow" from last read
        if clear_buffer:
            totalreadbytes = b''
        else:
            totalreadbytes = self._read_buffer
        self._read_buffer = b''

        # self.logger.debug('_read_bytes: start read')
        starttime = time()

        # prevent concurrent read attempts;
        with self._lock.acquire_timeout(self.__lock_timeout) as locked:

            if locked:
                # don't wait for input indefinitely, stop after 3 * self._params[PLUGIN_ATTR_CONN_TIMEOUT] seconds
                while time() <= starttime + self._timeout_mult * self._params[PLUGIN_ATTR_CONN_TIMEOUT]:
                    readbyte = self._connection.read()
                    self._lastbyte = readbyte
                    # self.logger.debug(f'_read_bytes: read {readbyte}')
                    if readbyte != b'':
                        self._lastbytetime = time()
                    else:
                        return totalreadbytes
                    totalreadbytes += readbyte

                    # limit_response reached?
                    if maxlen and len(totalreadbytes) >= maxlen:
                        return totalreadbytes

                    if term_bytes and term_bytes in totalreadbytes:
                        if self.__use_read_buffer:
                            pos = totalreadbytes.find(term_bytes)
                            self._read_buffer += totalreadbytes[pos + len(term_bytes):]
                            return totalreadbytes[:pos + len(term_bytes)]
                        else:
                            return totalreadbytes
            else:
                self.logger.warning('read_bytes couldn\'t get lock on serial. Ths is unintended...')

        # timeout reached, did we read anything?
        if not totalreadbytes and not self._listener_active:

            # just in case, force plugin to reconnect
            self._is_connected = False

        # return what we got so far, might be b''
        return totalreadbytes

    def reset_input_buffer(self):
        if self._connection:
            self._connection.reset_input_buffer()

    def _setup_listener(self):
        """ empty, for subclass use """
        pass


class SDPConnectionSerialAsync(SDPConnectionSerial):
    """ Connection for serial connectivity with async listener

    This class implements a serial connection for call-based sending and a
    threaded listener for async reading with callbacks.

    As this is derived from ``SDPConnectionSerial``, most of the documentation
    is identical.

    The timeout needs to be set small enough not to block reading for too long.
    Recommended times are between 0.2 and 0.8 seconds.

    The ``data_received_callback`` needs to be set or you won't get data.

    Callback syntax is:
        def connected_callback(by=None)
        def disconnected_callback(by=None)
        def data_received_callback(by, message)
    If callbacks are class members, they need the additional first parameter 'self'
    """
    def __init__(self, data_received_callback, name=None, **kwargs):
        # set additional class members
        self.__receive_thread = None
        self._name = name if name else ''

        super().__init__(data_received_callback, name=name, **kwargs)

    def _setup_listener(self):
        if not self._is_connected:
            return

        self._listener_active = True
        self.__receive_thread = Thread(target=self.__receive_thread_worker, name=self._name + '.Serial')
        self.__receive_thread.daemon = True
        self.__receive_thread.start()

    def _close(self):
        self.logger.debug(f'stopping receive thread {self.__receive_thread.name}')
        self._listener_active = False
        try:
            self.__receive_thread.join()
        except Exception:
            pass

    def __receive_thread_worker(self):
        """ thread worker to handle receiving """
        __buffer = b''

        self._is_receiving = True
        # try to find possible "hidden" errors
        try:
            while self._is_connected and self._listener_active:
                try:
                    msg = self._read_bytes(0)
                except serial.SerialTimeoutException:
                    pass

                if msg:

                    self.logger.debug(f'received raw data {msg}, buffer is {__buffer}')
                    # If we work in line mode (with a terminator) slice buffer into single chunks based on terminator
                    if self._params[PLUGIN_ATTR_CONN_TERMINATOR]:
                        __buffer += msg
                        while True:
                            # terminator = int means fixed size chunks
                            if isinstance(self._params[PLUGIN_ATTR_CONN_TERMINATOR], int):
                                i = self._params[PLUGIN_ATTR_CONN_TERMINATOR]
                                if i > len(__buffer):
                                    break
                            # terminator is str or bytes means search for it
                            else:
                                i = __buffer.find(self._params[PLUGIN_ATTR_CONN_TERMINATOR])
                                if i == -1:
                                    break
                                i += len(self._params[PLUGIN_ATTR_CONN_TERMINATOR])
                            line = __buffer[:i]
                            __buffer = __buffer[i:]
                            if self._data_received_callback:
                                self._data_received_callback(self, line if self._params[PLUGIN_ATTR_CONN_BINARY] else str(line, 'utf-8').strip())
                    # If not in terminator mode just forward what we received

                if not self._listener_active:
                    # socket shut down by self.close, no error
                    self.logger.debug('serial connection shut down by call to close method')
                    return

        except Exception as e:
            if not self._listener_active:
                self.logger.debug(f'serial receive thread {self.__receive_thread.name} shutting down')
                return
            else:
                self.logger.error(f'serial receive thread {self.__receive_thread.name} died with unexpected error: {e}')
