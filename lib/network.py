#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Parts Copyright 2016 C. Strassburg (lib.utils)     c.strassburg@gmx.de
#  Copyright 2017- Serge Wagener                     serge@wagener.family
#  Copyright 2020- Sebastian Helms                  morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
This library contains the network classes for SmartHomeNG.

New network functions and utilities are going to be implemented in this library.
These classes, functions and methods are mainly meant to be used by plugin developers

- class Network provides utility methods for network-related tasks
- class Html provides methods for communication with resp. requests to a HTTP server
- class Tcp_client provides a two-way TCP client implementation
- class Tcp_server provides a TCP listener with connection / data callbacks
- class Udp_server provides a UDP listener with data callbacks
"""

from lib.utils import Utils
import sys
import traceback
from inspect import signature
import re
import asyncio
import logging
import requests
from iowait import IOWait
import socket
import struct
import subprocess
import threading
import time
from contextlib import suppress
from . import aioudp


# Turn off ssl warnings from urllib
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
logging.getLogger('urllib3').setLevel(logging.WARNING)


class Network(object):
    """
    Provide useful static methods that you can use in your projects.

    NOTE: Some format check routines were duplicate with lib.utils. As these primarily check string formats and are used for metadata parsing, they were removed here to prevent duplicates.
    """

    @staticmethod
    def ip_port_to_socket(ip, port):
        """
        Return an ip address plus port to a socket string.

        Format is 'ip:port' for IPv4 or '[ip]:port' for IPv6

        :return: Socket address / IP endpoint as string
        :rtype: string
        """
        if Utils.is_ipv6(ip):
            ip = f'[{ip}]'
        return f'{ip}:{port}'

    @staticmethod
    def family_to_string(family):
        """
        Convert a socket address family to an ip version string 'IPv4' or 'IPv6'.

        :param family: Socket family
        :type family: socket.AF_INET or socket.AF_INET6

        :return: 'IPv4' or 'IPv6'
        :rtype: string
        """
        return 'IPv6' if family == socket.AF_INET6 else 'IPv4'

    @staticmethod
    def ping(ip):
        """
        Try to ICMP ping a host using external OS utilities. IPv4 only.

        :param ip: IPv4 address as a string
        :type ip: string

        :return: True if a reachable, false otherwise.
        :rtype: bool
        """
        logger = logging.getLogger(__name__)
        if subprocess.call(f'ping -c 1 {ip}', shell=True, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT) == 0:
            logger.debug(f'Ping: {ip} is online')
            return True
        else:
            logger.debug(f'Ping: {ip} is offline')
            return False

    @staticmethod
    def ping_port(ip, port=80):
        """
        Try to reach a given TCP port. IPv4 only.

        :param ip: IPv4 address
        :param port: Port number

        :type ip: string
        :type port: int

        :return: True if reachable, false otherwise.
        :rtype: bool
        """
        logger = logging.getLogger(__name__)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        if sock.connect_ex((ip, int(port))) == 0:
            logger.debug(f'Ping: port {port} on {ip} is reachable')
            sock.close()
            return True
        else:
            logger.debug(f'Ping: port {port} on {ip} is offline or not reachable')
            sock.close()
            return False

    @staticmethod
    def send_wol(mac, ip='255.255.255.255'):
        """
        Send a wake on lan packet to the given mac address using ipv4 broadcast (or directed to specific ip).

        :param mac: Mac address to wake up (pure numbers or with any separator)
        :type mac: string
        """
        logger = logging.getLogger(__name__)
        if len(mac) == 12:
            pass
        elif len(mac) == 12 + 5:
            mac = mac.replace(mac[2], '')
        else:
            logger.error('Incorrect MAC address format')
            return

        data = ''.join(['FFFFFFFFFFFF', mac * 16])
        send_data = b''
        for i in range(0, len(data), 2):
            send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

        for _ in range(15):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(send_data, (ip, 9))
        logger.debug(f'Sent WOL packet to {mac}')

    @staticmethod
    def validate_inet_addr(addr, port):
        """
        Validate that addr:port resolve properly and return resolved IP address and port.

        :param addr: hostname or ip address under test
        :type addr: str
        :param port: port number under test
        :type port: num
        :return: (ip_address, port, family) or (None, 0, None) if error occurs
        :rtype: tuple
        """
        logger = logging.getLogger(__name__)
        # Test if host is empty
        if addr == '':
            return ('', port, socket.AF_INET)
        else:
            # try to resolve addr to get more info
            logger.debug(f'trying to resolve addr {addr} with port {port}')
            try:
                family, sockettype, proto, canonname, socketaddr = socket.getaddrinfo(addr, None)[0]
                # Check if resolved address is IPv4 or IPv6
                if family == socket.AF_INET:
                    ip, _ = socketaddr
                elif family == socket.AF_INET6:
                    ip, _, flow_info, scope_id = socketaddr
                else:
                    # might be AF_UNIX or something esoteric?
                    logger.error(f'Unsupported address family {family}')
                    ip = None
                if ip is not None:
                    logger.info(f'Resolved {addr} to {Network.family_to_string(family)} address {ip}')
            except socket.gaierror as e:
                # Unable to resolve hostname
                logger.error(f'Cannot resolve {addr} to a valid ip address (v4 or v6): {e}')
                ip = None
                port = 0
                family = None

        return (ip, port, family)

    @staticmethod
    def clean_uri(uri, mode='show'):
        """
        Check URIs for embedded http/https login data (http://user:pass@domain.tld...) and clean it.

        Possible modes are:

        - 'show': don't change URI (default) -> ``http://user:pass@domain.tld...``
        - 'mask': replace login data with ``***`` -> ``http://***:***@domain.tld...``
        - 'strip': remove login data part -> ``http://domain.tld...``

        :param uri: full URI to check and process
        :param mode: handling mode, one of 'show', 'strip', 'mask'
        :return: resulting URI string

        :type uri: str
        :type mode: str
        :rtype: str
        """
        # find login data
        pattern = re.compile('http([s]?)://([^:]+:[^@]+@)')
        # possible replacement modes
        replacement = {
            'strip': 'http\\g<1>://',
            'mask': 'http\\g<1>://***:***@'
        }

        # if no change requested or no login data found, return unchanged
        if mode not in replacement or not pattern.match(uri):
            return uri

        # return appropriately changed URI
        return pattern.sub(replacement[mode], uri)


class Connections(object):
    """
    Within SmartHome.py there is one instance of this class

    The monitoring feature enables autoconnecting and auto-
    reconnecting by checking <plugin>.connected and calling
    <plugin>.connect()
    """

    _monitor = []

    def __init__(self):
        self._name = self.__class__.__name__

    def monitor(self, obj):
        if obj not in self._monitor:
            self._monitor.append(obj)

    def unmonitor(self, obj):
        if obj in self._monitor:
            self._monitor.remove(obj)

    def check(self):
        for obj in self._monitor:
            if obj.alive and not obj.connected:
                obj.connect()


class Http(object):
    """
    Provide methods to simplify HTTP connections, especially to talk to HTTP servers.

    :param baseurl: base URL used everywhere in this instance (example: http://www.myserver.tld)
    :param timeout: Set a maximum amount of seconds the class should try to establish a connection
    :param hide_login: Hide or mask login data in logged http(s) requests (see ``Network.clean_uri()``)

    :type baseurl: str
    :type timeout: int
    :type hide_login: str
    """

    def __init__(self, baseurl='', timeout=10, hide_login='show', name=None):
        self.logger = logging.getLogger(__name__)

        self.baseurl = baseurl
        self._response = None
        self.timeout = timeout
        self._session = requests.Session()
        self._hide_login = hide_login

        self._id = f'({name if name else "HTTP"}_{self.baseurl})'

    def HTTPDigestAuth(self, user=None, password=None):
        """
        Create a HTTPDigestAuth instance and returns it to the caller.

        :param user: Username
        :param password: Password

        :type user: str
        :type password: str

        :return: HTTPDigestAuth object
        :rtype: HTTPDigestAuth
        """
        return requests.auth.HTTPDigestAuth(user, password)

    def post_json(self, url=None, params=None, verify=True, auth=None, json=None, files={}):
        """
        Launch a POST request and return JSON answer as a dict or None on error.

        :param url: Optional URL to fetch from. If None (default) use baseurl given on init.
        :param params: Optional dict of parameters to add to URL query string.
        :param verify: Set to false to ignore SSL certificate verification errors (for self-signed for example)
        :param auth: Optional authentication object

        :type url: str
        :type params: dict
        :type verify: bool
        :type auth: HTTPBasicAuth | HTTPDigestAuth | ...

        :return: JSON answer decoded into a dict or None on whatever error occured
        :rtype: dict | None
        """
        if self.__post(url=url, params=params, verify=verify, auth=auth, json=json, files=files):
            json = None
            try:
                json = self._response.json()
            except Exception:
                self.logger.warning(f'{self._id} invalid JSON received from {Network.clean_uri(url, self._hide_login) if url else self.baseurl}')
            return json
        return None

    def get_json(self, url=None, params=None, verify=True, auth=None):
        """
        Launch a GET request and return JSON answer as a dict or None on error.

        :param url: Optional URL to fetch from. If None (default) use baseurl given on init.
        :param params: Optional dict of parameters to add to URL query string.
        :param verify: Set to false to ignore SSL certificate verification errors (for self-signed for example)
        :param auth: Optional authentication object

        :type url: str
        :type params: dict
        :type verify: bool
        :type auth: HTTPBasicAuth | HTTPDigestAuth | ...

        :return: JSON answer decoded into a dict or None on whatever error occured
        :rtype: dict | None
        """
        if self.__get(url=url, params=params, verify=verify, auth=auth):
            json = None
            try:
                json = self._response.json()
            except Exception:
                self.logger.warning(f'{self._id} invalid JSON received from {Network.clean_uri(url if url else self.baseurl, self._hide_login) }')
            return json
        return None

    def get_text(self, url=None, params=None, encoding=None, timeout=None):
        """
        Launch a GET request and return answer as string or None on error.

        :param url: Optional URL to fetch from. Default is to use baseurl given to constructor.
        :param params: Optional dict of parameters to add to URL query string.
        :param encoding: Optional encoding of the received text. Default is to let the lib try to figure out the right encoding.

        :type url: str
        :type params: dict
        :type encoding: str

        :return: Answer decoded into a string or None on whatever error occured
        :rtype: str | None
        """
        _text = None
        if self.__get(url=url, params=params, timeout=timeout):
            try:
                if encoding:
                    self._response.encoding = encoding
                _text = self._response.text
            except Exception as e:
                self.logger.error(f'{self._id} successful GET, but decoding response failed. This should never happen...error was: {e}')
        return _text

    def download(self, url=None, local=None, params=None, verify=True, auth=None):
        """
        Download a binary file to a local path.

        :param url: Remote file to download. Attention: Must be full url. 'baseurl' is NOT prefixed here.
        :param local: Local file to save
        :param params: Optional dict of parameters to add to URL query string.
        :param verify: Set to false to ignore SSL certificate verification errors (for self-signed for example)
        :param auth: Optional authentication object

        :type url: str
        :type local: str
        :type params: dict
        :type verify: bool
        :type auth: HTTPBasicAuth | HTTPDigestAuth | ...

        :return: Returns true on success, else false
        :rtype: bool
        """
        if self.__get(url=url, params=params, verify=verify, auth=auth, stream=True):
            self.logger.debug(f'{self._id} download of {Network.clean_uri(url, self._hide_login)} successfully completed, saving to {local}')
            with open(str(local), 'wb') as f:
                for chunk in self._response:
                    f.write(chunk)
            return True
        else:
            self.logger.warning(f'{self._id} download error: {Network.clean_uri(url, self._hide_login)}')
            return False

    def get_binary(self, url=None, params=None):
        """
        Launch a GET request and return answer as raw binary data or None on error.

        This is useful for downloading binary objects / files.

        :param url: Optional URL to fetch from. Default is to use baseurl given to constructor.
        :param params: Optional dict of parameters to add to URL query string.

        :type url: str
        :type params: dict

        :return: Answer as raw binary objector None on whatever error occured
        :rtype: bytes | None
        """
        self.__get(url=url, params=params)
        return self._response.content

    def response_status(self):
        """
        Return the status code (200, 404, ...) of the last executed request.

        If GET request was not possible and thus no HTTP statuscode is available,
        the returned status code is 0.

        :return: Status code and text of last request
        :rtype: tuple(int, str)
        """
        try:
            (code, reason) = (self._response.status_code, self._response.reason)
        except Exception:
            code = 0
            reason = 'Unable to complete GET request'
        return (code, reason)

    def response_headers(self):
        """
        Return a dictionary with the server return headers of the last executed request.

        :return: Headers returned by server
        :rtype: dict
        """
        return self._response.headers

    def response_cookies(self):
        """
        Return a dictionary with the cookies the server may have sent on the last executed request.

        :return: Cookies returned by server
        :rtype: dict
        """
        return self._response.cookies

    def response_object(self):
        """
        Return the raw response object for advanced ussage.

        :return: Reponse object as returned by underlying requests library
        :rtype: `requests.Response <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
        """
        return self._response

    def __post(self, url=None, params=None, timeout=None, verify=True, auth=None, json=None, data=None, files={}):
        """
        Send POST request. Non-documented arguments are passed on to requests.request().

        :param url: URL to which to POST
        :type url: str
        :param data: data to submit to POST
        :type data: dict or bytes or file

        :return: True if POST was successful
        :rtype: bool
        """
        url = self.baseurl + url if url else self.baseurl
        timeout = timeout if timeout else self.timeout
        data = json if json else data
        self.logger.info(f'{self._id} sending POST request {json} to {Network.clean_uri(url, self._hide_login)}')
        try:
            self._response = self._session.post(url, params=params, timeout=timeout, verify=verify, auth=auth, data=data, files=files)
            self.logger.debug(f'{self.response_status()} Posted to URL {Network.clean_uri(self._response.url, self._hide_login)}')
        except Exception as e:
            self.logger.warning(f'{self._id} error sending POST request to {Network.clean_uri(url, self._hide_login)}: {e}')
            return False
        return True

    def __get(self, url=None, params=None, timeout=None, verify=True, auth=None, stream=False):
        """
        Send POST request. Non-documented arguments are passed on to requests.request().

        :param url: URL to which to GET
        :type url: str

        :return: True if GET was successful
        :rtype: bool
        """
        url = self.baseurl + url if url else self.baseurl
        timeout = timeout if timeout else self.timeout
        self.logger.info(f'{self._id} sending GET request to {Network.clean_uri(url, self._hide_login)}')
        try:
            self._response = self._session.get(url, params=params, timeout=timeout, verify=verify, auth=auth, stream=stream)
            self.logger.debug(f'{self._id} {self.response_status()} fetched URL {Network.clean_uri(self._response.url, self._hide_login)}')
        except Exception as e:
            self.logger.warning(f'{self._id} error sending GET request to {Network.clean_uri(url, self._hide_login)}: {e}')
            self._response = None
            return False
        return True


class Tcp_client(object):
    """
    Structured class to handle locally initiated TCP connections with two-way communication.

    The callbacks need to be defined as follows:

    def connected_callback(Tcp_client_instance)
    def receiving_callback(Tcp_client_instance)
    def disconnected_callback(Tcp_client_instance)
    def data_received_callback(Tcp_client_instance, message)

    (Class members need the additional first `self` parameter)


    :param host: Remote host name or ip address (v4 or v6)
    :param port: Remote host port to connect to
    :param name: Name of this connection (mainly for logging purposes). Try to keep the name short.
    :param autoreconnect: Should the socket try to reconnect on lost connection (or finished connect cycle)
    :param autoconnect: automatically connect on send. Copies autoreconnect if None
    :param connect_retries: Number of connect retries per connect round
    :param connect_cycle: Time between retries inside a connect round
    :param retry_cycle: Time between connect rounds if autoreconnect is True
    :param retry_abort: abort connecting after this many failed connect rounds and call abort_callback, no action if set to 0 or callback not set
    :param abort_callback: callback function to be run on connection abort 
    :param binary: Switch between binary and text mode. Text will be encoded / decoded using encoding parameter.
    :param terminator: Terminator to use to split received data into chunks (split lines <cr> for example). If integer then split into n bytes. Default is None means process chunks as received.
    :param timeout: Timeout to set for connected socket. Don't change without reason

    :type host: str
    :type port: int
    :type name: str
    :type autoreconnect: bool
    :type autoconnect: bool
    :type connect_retries: int
    :type connect_cycle: int
    :type retry_cycle: int
    :type retry_abort: int
    :type abort_callback: function
    :type binary: bool
    :type terminator: int | bytes | str
    :type timeout: int
    """

    def __init__(self, host, port, name=None, autoreconnect=True, autoconnect=None, connect_retries=5, connect_cycle=5, retry_cycle=30, retry_abort=0, abort_callback=None, binary=False, terminator=False, timeout=1):
        self.logger = logging.getLogger(__name__)

        # public properties
        self.name = name
        self.terminator = terminator

        # protected properties
        self._host = host
        self._port = port
        self._autoreconnect = autoreconnect
        self._autoconnect = autoconnect
        if self._autoconnect is None:
            self._autoconnect = self._autoreconnect
        self._is_connected = False
        self._is_receiving = False
        self._connect_retries = connect_retries
        self._connect_cycle = connect_cycle
        self._retry_cycle = int(retry_cycle)
        self._retry_abort = retry_abort
        self._abort_callback = abort_callback
        self._timeout = timeout

        self._hostip = None
        self._family = socket.AF_INET
        self._socket = None
        self._connect_counter = 0
        self._retry_round_counter = 0
        self._binary = binary

        self._connected_callback = None
        self._receiving_callback = None
        self._disconnected_callback = None
        self._data_received_callback = None

        # private properties
        self.__connect_thread = None
        self.__connect_threadlock = threading.Lock()
        self.__receive_thread = None
        self.__receive_threadlock = threading.Lock()
        self.__running = False

        # self.logger.setLevel(logging.DEBUG)   # Das sollte hier NICHT gesetzt werden, sondern in etc/logging.yaml im Logger lib.network konfiguriert werden!

        self._host = host
        self._port = port
        self._id = f'({self.name if self.name else "TCP_Client"}_{self._host}:{self._port})'
        (self._hostip, self._port, self._family) = Network.validate_inet_addr(host, port)
        if self._hostip is not None:
            self._id = f'({self.name if self.name else "TCP_Client"}_{self._hostip}:{self._port})'
            self.logger.info(f'{self._id} Initializing a connection to {self._host} on TCP port {self._port} {"with" if self._autoreconnect else "without"} autoreconnect')
        else:
            self.logger.error(f'{self._id} Connection to {self._host} not possible, invalid address')

    def set_callbacks(self, connected=None, receiving=None, data_received=None, disconnected=None):
        """
        Set callbacks to caller for different socket events.

        :param connected: Called whenever a connection is established successfully
        :param data_received: Called when data is received
        :param disconnected: Called when a connection has been dropped for whatever reason

        :type connected: function
        :type data_received: function
        :type disconnected: function
        """
        if connected:
            params = len(signature(connected).parameters)
            self.logger.debug(f"connected_callback for {self._id} is {connected.__qualname__} and it expects {params} arguments")
            self._connected_callback = connected
        if receiving:
            params = len(signature(receiving).parameters)
            self.logger.debug(f"connected_callback for {self._id} is {receiving.__qualname__} and it expects {params} arguments")
            self._receiving_callback = receiving
        if disconnected:
            params = len(signature(disconnected).parameters)
            self.logger.debug(f"connected_callback for {self._id} is {disconnected.__qualname__} and it expects {params} arguments")
            self._disconnected_callback = disconnected
        if data_received:
            params = len(signature(data_received).parameters)
            self.logger.debug(f"connected_callback for {self._id} is {data_received.__qualname__} and it expects {params} arguments")
            self._data_received_callback = data_received

    def connect(self):
        """
        Connect the socket.

        :return: False if an error prevented us from launching a connection thread. True if a connection thread has been started.
        :rtype: bool
        """
        if self._is_connected:  # return false if already connected
            self.logger.debug(f'{self._id} already connected, ignoring new request')
            return False

        if self._hostip is None:  # return False if no valid ip to connect to
            self.logger.error(f'{self._id} no valid IP address to connect')
            self._is_connected = False
            return False

        self.logger.debug(f'Starting connect to {self._host}:{self._port}')
        if not self.__connect_thread or not self.__connect_thread.is_alive():
            self.__connect_thread = threading.Thread(target=self._connect_thread_worker, name=f'TCP_Connect {self._id}')
            self.__connect_thread.daemon = True
        self.logger.debug(f'connect() to {self._host}:{self._port}: self.__running={self.__running}, self.__connect_thread.is_alive()={self.__connect_thread.is_alive()}')
        if not self.__running or not self.__connect_thread.is_alive():
            self.logger.debug(f'connect() to {self._host}:{self._port}: calling __connect_thread.start()')
            self.__connect_thread.start()
        self.logger.debug(f'leaving connect() to {self._host}:{self._port}')
        return True

    def connected(self):
        """
        Return the current connection state.

        :return: True if an active connection exists,else False.
        :rtype: bool
        """
        return self._is_connected

    def send(self, message):
        """
        Send a message to the server. Can be a string, bytes or a bytes array.

        :return: True if message has been successfully sent, else False.
        :rtype: bool
        """
        if not isinstance(message, (bytes, bytearray)):
            try:
                message = message.encode('utf-8')
            except Exception:
                self.logger.warning(f'{self._id} error encoding message for client')
                return False

        # automatically (re)connect on send attempt
        if not self._is_connected:
            if self._autoconnect:
                self.logger.debug(f'{self._id} autoconnecting on send attempt, message is {message}')
                self.connect()
            else:
                self.logger.warning(f'{self._id} trying to send {message}, but not connected and autoconnect not active. Aborting.')
                return False

        try:
            if self._is_connected:
                bytes_sent = self._socket.send(message)
                if bytes_sent != len(message):
                    self.logger.warning(f'{self._id} error sending message {message}: message truncated, sent {bytes_sent} of {len(message)} bytes')
            else:
                return False

        except (BrokenPipeError, TimeoutError) as e:
            if e.errno == 60:
                # timeout
                self.logger.warning(f'{self._id} detected timeout, disconnecting, send failed.')
            else:
                self.logger.warning(f'{self._id} detected disconnect, send failed.')
            self._is_connected = False
            try:
                self._socket.shutdown()
            except Exception:
                pass
            if self._disconnected_callback:
                self._disconnected_callback(self)
            if self._autoreconnect:
                self.logger.debug(f'{self._id} autoreconnect enabled')
                self.connect()
            return False

        except Exception as e:  # log errors we are not prepared to handle and raise exception for further debugging
            self.logger.warning(f'{self._id} unhandleded error on sending, cannot send data {message}. Error: {e}')
            raise

        return True

    def _connect_thread_worker(self):
        """
        Thread worker to handle connection.
        """
        if not self.__connect_threadlock.acquire(blocking=False):
            self.logger.info(f'{self._id} connection attempt already in progress, ignoring new request')
            return
        if self._is_connected:
            self.logger.info(f'{self._id} already connected, ignoring new request')
            return
        self.logger.debug(f'{self._id} starting connection cycle')
        self._connect_counter = 0
        self._retry_round_counter = 0
        self.__running = True
        while self.__running and not self._is_connected:
            # Try a full connect round
            while not self._is_connected and self._connect_counter < self._connect_retries and (self._retry_round_counter < self._retry_abort or not self._retry_abort) and self.__running:
                self._connect()
                if self._is_connected:
                    try:
                        self.__connect_threadlock.release()
                        if self._connected_callback:
                            self._connected_callback(self)
                        name = f'TCP_Client {self._id}'
                        self.__receive_thread = threading.Thread(target=self.__receive_thread_worker, name=name)
                        self.__receive_thread.daemon = True
                        self.__receive_thread.start()
                    except Exception:
                        self.logger.error(f"could not start __receive_thread_worker for {self.name}")
                        raise
                    return True
                else:
                    self.logger.warning(f"self._connect() for {self.name} did not work")
                if self.__running and self._connect_counter < self._connect_retries:
                    self._sleep(self._connect_cycle)

            if self._autoreconnect and self.__running:
                self._retry_round_counter += 1
                if self._retry_abort and self._retry_round_counter == self._retry_abort and self._abort_callback:
                    self._abort_callback()
                    break
                self.logger.debug(f'waiting {self._retry_cycle} seconds before next connection attempt')
                self._sleep(self._retry_cycle)
                self._connect_counter = 0
            else:
                break
        try:
            self.__connect_threadlock.release()
        except Exception:
            # self.logger.debug(f'{self._id} exception while trying self.__connect_threadlock.release()')
            pass

    def _connect(self):
        """
        Initiate connection.
        """
        self.logger.debug(f'{self._id} connecting using TCP/{"IPv6" if self._family == socket.AF_INET6 else "IPv4"} {"with" if self._autoreconnect else "without"} autoreconnect')
        # Try to connect to remote host using ip (v4 or v6)
        try:
            self._socket = socket.socket(self._family, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.settimeout(5)
            self._socket.connect((f'{self._hostip}', int(self._port)))
            self._socket.settimeout(self._timeout)
            self._is_connected = True
            self.logger.info(f'{self._id} connected')
        # Connection error
        except Exception as err:
            self._is_connected = False
            self._connect_counter += 1
            self.logger.warning(f'{self._id} TCP connection failed {self._connect_counter}/{int(self._connect_retries)} times, last error was: {err}')

    def __receive_thread_worker(self):
        """
        Thread worker to handle receiving.
        """
        self.logger.debug(f'{self._id} started receive thread')
        waitobj = IOWait()
        waitobj.watch(self._socket, read=True)
        __buffer = b''

        self._is_receiving = True
        if self._receiving_callback:
            self._receiving_callback(self)
        # try to find possible "hidden" errors
        try:
            while self._is_connected and self.__running:
                events = waitobj.wait(1000)     # BMX
                for fileno, read, write in events:  # BMX
                    if read:
                        timeout = False
                        try:
                            msg = self._socket.recv(4096)
                        except (TimeoutError, OSError) as e:
                            if isinstance(e, OSError) and e.errno not in (60, 65):
                                raise
                            msg = None
                            timeout = True

                        # Check if incoming message is not empty
                        if msg:
                            # TODO: doing this breaks line separation if multiple lines
                            #       are read at a time, the next loop can't split it
                            #       because line endings are missing
                            #       find out reason for this operation...

                            # # If we transfer in text mode decode message to string
                            # # if not self._binary:
                            # #     msg = str.rstrip(str(msg, 'utf-8')).encode('utf-8')

                            # If we work in line mode (with a terminator) slice buffer into single chunks based on terminator
                            if self.terminator:
                                __buffer += msg
                                while True:
                                    # terminator = int means fixed size chunks
                                    if isinstance(self.terminator, int):
                                        i = self.terminator
                                        if i > len(__buffer):
                                            break
                                    # terminator is str or bytes means search for it
                                    else:
                                        i = __buffer.find(self.terminator)
                                        if i == -1:
                                            break
                                        i += len(self.terminator)
                                    line = __buffer[:i]
                                    __buffer = __buffer[i:]
                                    if self._data_received_callback is not None:
                                        try:
                                            self._data_received_callback(self, line if self._binary else str(line, 'utf-8').strip())
                                        except Exception as iex:
                                            self._log_exception(iex, f'lib.network {self._id} receive in terminator mode calling data_received_callback {self._data_received_callback} failed: {iex}')
                            # If not in terminator mode just forward what we received
                            else:
                                if self._data_received_callback is not None:
                                    try:
                                        self._data_received_callback(self, msg)
                                    except Exception as iex:
                                        self._log_exception(iex, f'lib.network {self._id} calling data_received_callback {self._data_received_callback} failed: {iex}')
                        # If empty peer has closed the connection
                        else:
                            if self.__running:
                                self._is_receiving = False
                                self._is_connected = False
                                try:
                                    self._socket.shutdown()
                                except Exception:
                                    pass
                                if timeout:
                                    # TimeoutError exception caught
                                    self.logger.warning(f'{self._id} connection timed out, disconnecting.')
                                else:
                                    # default state, peer closed connection
                                    self.logger.warning(f'{self._id} connection closed by peer')
                                waitobj.unwatch(self._socket)
                                if self._disconnected_callback is not None:
                                    try:
                                        self._disconnected_callback(self)
                                    except Exception as iex:
                                        self._log_exception(iex, f'lib.network {self._id} calling disconnected_callback {self._disconnected_callback} failed: {iex}')
                                if self._autoreconnect:
                                    self.logger.debug(f'{self._id} autoreconnect enabled')
                                    self.connect()
                                if self._is_connected:
                                    self.logger.debug(f'{self._id} set read watch on socket again')
                                    waitobj.watch(self._socket, read=True)
                            else:
                                # socket shut down by self.close, no error
                                self.logger.debug(f'{self._id} connection shut down by call to close method')
                                self._is_receiving = False
                                self._is_connected = False
                                return
        except Exception as ex:
            if not self.__running:
                self.logger.debug(f'{self._id} receive thread shutting down')
            else:
                self._log_exception(ex, f'lib.network {self._id} receive thread died with unexpected error: {ex}. Go tell...')
        self._is_receiving = False

    def _log_exception(self, ex, msg):
        self.logger.error(msg + ' -- If stack trace is necessary, enable/check debug log')

        if self.logger.isEnabledFor(logging.DEBUG):

            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

            self.logger.debug("Exception type : %s " % ex_type.__name__)
            self.logger.debug("Exception message : %s" % ex_value)
            self.logger.debug("Stack trace : %s" % stack_trace)

    def _sleep(self, time_lapse):
        """
        Sleep (at least) <time_lapse> seconds, but abort if self.__running changes to False.

        :param time_lapse: wait time in seconds
        :type time: int
        """
        time_start = time.time()
        time_end = (time_start + time_lapse)
        while self.__running and time_end > time.time():
            # modified from 'pass' - this way intervals of 1 second are given up to other threads
            # but the abort loop stays intact with a maximum of 1 second delay
            time.sleep(1)

    def close(self):
        """
        Close the current client socket.
        """
        self.__running = False
        self.logger.info(f'{self._id} closing connection')
        if self._is_connected:
            try:
                self._socket.shutdown(socket.SHUT_RD)
            except Exception as e:
                self.logger.info(f"socket no longer connected on disconnect, exception is {e}")
        if self.__connect_thread is not None and self.__connect_thread.is_alive():
            try:
                self.__connect_thread.join()
            except Exception:
                pass
        if self.__receive_thread is not None and self.__receive_thread.is_alive():
            try:
                self.__receive_thread.join()
            except Exception:
                pass

        self.__connect_thread = None
        self.__receive_thread = None
        self.__connect_threadlock = threading.Lock()
        self.__receive_threadlock = threading.Lock()
        self._is_connected = False

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()


class ConnectionClient(object):
    """
    Client object that represents a connected client returned by a Tcp_server instance on incoming connection.

    This class should normally **not be instantiated manually**, but is provided by the Tcp_server via the callbacks

    :param server: The tcp_server passes a reference to itself to access parent methods
    :param socket: socket.Socket class used by the Client object
    :param fd: File descriptor of socket used by the Client object

    :type server: tcp_server
    :type socket: function
    :type fd: int
    """

    def __init__(self, server=None, socket=None, ip=None, port=None, name=None):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.ip = ip
        self.port = port
        self.family = None
        self.writer = None
        self.process_iac = True

        self._data_received_callback = None
        self._will_close_callback = None
        self.__server = server
        self.__socket = socket

        self._id = f'({self.name if self.name else "Connection"}_{self.ip}:{self.port})'

    @property
    def socket(self):
        """
        Socket getter.
        """
        return self.__socket

    def set_callbacks(self, data_received=None, will_close=None):
        """
        Set callbacks for different socket events (client based).

        :param data_received: Called when data is received
        :type data_received: function
        """
        self._data_received_callback = data_received
        self._will_close_callback = will_close

    async def __drain_writer(self):
        """
        Ensure drain() is called.
        """
        with suppress(ConnectionResetError):
            await self.writer.drain()

    def send(self, message):
        """
        Send a string to connected client.

        :param msg: Message to send
        :type msg: string | bytes | bytearray

        :return: True if message has been queued successfully.
        :rtype: bool
        """
        if not isinstance(message, (bytes, bytearray)):
            try:
                message = message.encode('utf-8')
            except Exception:
                self.logger.warning(f'{self._id} error encoding data')
                return False
        try:

            self.writer.write(message)
            asyncio.ensure_future(self.__drain_writer())
        except Exception as e:
            self.logger.warning(f'{self._id} error sending data: {e}')
            return False
        return True

    def send_echo_off(self):
        """
        Send an IAC telnet command to ask client to turn its echo off.
        """
        command = bytearray([0xFF, 0xFB, 0x01])
        string = self._iac_to_string(command)
        self.logger.debug(f'{self._id} sending IAC telnet command: {string}')
        self.send(command)

    def send_echo_on(self):
        """
        Send an IAC telnet command to ask client to turn its echo on again.
        """
        command = bytearray([0xFF, 0xFC, 0x01])
        string = self._iac_to_string(command)
        self.logger.debug(f'{self._id} sending IAC telnet command: {string}')
        self.send(command)

    def _process_IAC(self, msg):
        """
        Process incomming IAC messages.

        NOTE: Does nothing for now except logging them in clear text
        """
        if len(msg) >= 3:
            string = self._iac_to_string(msg[:3])
            self.logger.debug(f'{self._id} received IAC telnet command: {string}')
            msg = msg[3:]
        return msg

    def close(self):
        """
        Close client socket.
        """
        if self._will_close_callback:
            self._will_close_callback(self)
        self.set_callbacks(data_received=None, will_close=None)
        self.writer.close()
        return True

    def _iac_to_string(self, msg):
        iac = {1: 'ECHO', 251: 'WILL', 252: 'WON\'T', 253: 'DO', 254: 'DON\'T', 255: 'IAC'}
        string = ''
        for char in msg:
            if char in iac:
                string += iac[char] + ' '
            else:
                string += chr(char)
        return string.rstrip()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()


class Tcp_server(object):
    """
    Threaded TCP listener which dispatches connections (and possibly received data) via callbacks.

    NOTE: The callbacks need to expect the following arguments:

    - ``incoming_connection(server, client)`` where ``server`` ist the ``Tcp_server`` instance and ``client`` is a ``ConnectionClient`` for the current connection
    - ``data_received(server, client, data)`` where ``server`` ist the ``Tcp_server`` instance, ``client`` is a ``ConnectionClient`` for the current connection, and ``data`` is a string containing received data
    - ``disconnected(server, client)`` where ``server`` ist the ``Tcp_server`` instance and ``client`` is a ``ConnectionClient`` for the closed connection

    :param host: Local host name or ip address (v4 or v6). Default is '::' which listens on all IPv4 and all IPv6 addresses available.
    :param port: Local port to connect to
    :param name: Name of this connection (mainly for logging purposes)

    :type host: str
    :type port: int
    :type name: str
    """

    MODE_TEXT = 1
    MODE_TEXT_LINE = 2
    MODE_BINARY = 3
    MODE_FIXED_LENGTH = 4

    def __init__(self, port, host='', name=None, mode=MODE_BINARY, terminator=None):
        self.logger = logging.getLogger(__name__)

        # public properties
        self.name = name
        self.mode = mode
        self.terminator = terminator

        # private properties
        self._host = host
        self._port = port
        self._is_listening = False
        self._timeout = 1

        self._ipaddr = None
        self._family = socket.AF_INET
        self._socket = None

        self._incoming_connection_callback = None
        self._data_received_callback = None

        # protected properties
        self.__loop = None
        self.__coroutine = None
        self.__server = None
        self.__listening_thread = None
        self.__running = True

        # Test if host is an ip address or a host name
        self._id = f'({self.name if self.name else "TCP_Server"}_{self._host}:{self._port})'

        (self._ipaddr, self._port, self._family) = Network.validate_inet_addr(host, port)

        if self._ipaddr is not None:
            self._id = f'({self.name if self.name else "TCP_Server"}_{self._ipaddr}:{self._port})'
            self.__our_socket = Network.ip_port_to_socket(self._ipaddr, self._port)
            if not self.name:
                self.name = self.__our_socket

    def set_callbacks(self, incoming_connection=None, disconnected=None, data_received=None):
        """
        Set callbacks to caller for different socket events.

        :param connected: Called whenever a connection is established successfully
        :param data_received: Called when data is received
        :param disconnected: Called when a connection has been dropped for whatever reason

        :type connected: function
        :type data_received: function
        :type disconnected: function
        """
        self._incoming_connection_callback = incoming_connection
        self._data_received_callback = data_received
        self._disconnected_callback = disconnected

    def start(self):
        """
        Start the server socket.

        :return: False if an error prevented us from launching a connection thread. True if a connection thread has been started.
        :rtype: bool
        """
        if self._is_listening:
            return False
        try:
            self.logger.info(f'{self._id} starting up TCP server socket')
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)
            self.__coroutine = asyncio.start_server(self.__handle_connection, self._ipaddr, self._port)
            self.__server = self.__loop.run_until_complete(self.__coroutine)

            self.__listening_thread = threading.Thread(target=self.__listening_thread_worker, name=f'TCPServer {self._id}')
            self.__listening_thread.daemon = True
            self.__listening_thread.start()
        except Exception as e:
            self.logger.error(f'{self._id} error starting server: {e}')
            return False
        return True

    def __listening_thread_worker(self):
        """
        Run the asyncio loop in a separate thread to not block the Tcp_server.start() method.
        """
        asyncio.set_event_loop(self.__loop)
        self._is_listening = True
        try:
            self.__loop.run_forever()
        except Exception:
            self.logger.debug(f'{self._id} error in loop.run_forever()')
        finally:
            for task in asyncio.all_tasks(self.__loop):
                task.cancel()
            self.__server.close()
            self.__loop.run_until_complete(self.__server.wait_closed())
            try:
                self.__loop.close()
            except Exception:
                pass
        self._is_listening = False

    async def __handle_connection(self, reader, writer):
        """
        Handle incoming connection.

        Each client gets its own handler.
        """
        peer = writer.get_extra_info('peername')
        socket_object = writer.get_extra_info('socket')
        peer_socket = Network.ip_port_to_socket(peer[0], peer[1])

        client = ConnectionClient(server=self, socket=socket_object, ip=peer[0], port=peer[1])
        client.family = socket.AF_INET6 if Utils.is_ipv6(client.ip) else socket.AF_INET
        client.name = Network.ip_port_to_socket(client.ip, client.port)
        client.writer = writer

        self.logger.info(f'{self._id} incoming connection from {peer_socket}')
        if self._incoming_connection_callback:
            self._incoming_connection_callback(self, client)

        while True:
            try:
                if self.mode == self.MODE_TEXT_LINE:
                    # self.logger.debug("***")
                    data = await reader.readline()
                else:
                    data = await reader.read(4096)
            except Exception:
                data = None

            if data and data[0] == 0xFF and client.process_iac:
                data = client._process_IAC(data)
            if data:
                try:
                    string = str.rstrip(str(data, 'utf-8'))
                    self.logger.debug(f'{self._id} received "{string}" from {client.name}')
                    if self._data_received_callback:
                        self._data_received_callback(self, client, string)
                    if client._data_received_callback:
                        client._data_received_callback(self, client, string)
                except Exception as e:
                    self.logger.debug(f'{self._id} received undecodable bytes from {client.name}: {data}, resulting in error: {e}')
            else:
                try:
                    self.__close_client(client)
                    pass
                finally:
                    del client
                return

    def __close_client(self, client):
        """
        Close client connection.

        :param client: client object
        :type client: lib.network.ConnectionClient
        """
        self.logger.info(f'{self._id} connection to client {client.name} closed')
        if self._disconnected_callback:
            self._disconnected_callback(self, client)
        client.writer.close()

    def listening(self):
        """
        Return the current listening state.

        :return: True if the server socket is actually listening, else False.
        :rtype: bool
        """
        return self._is_listening

    def send(self, client, msg):
        """
        Send a string to connected client.

        :param client: Client Object to send message to
        :param msg: Message to send

        :type client: lib.network.ConnectionClient
        :type msg: string | bytes | bytearray

        :return: True if message has been queued successfully.
        :rtype: bool
        """
        client.send(msg)
        return True

    def disconnect(self, client):
        """
        Disconnect a specific client.

        :param client: Client Object to disconnect
        :type client: lib.network.ConnectionClient
        """
        client.close()
        return True

    def close(self):
        """
        Close running listening socket.
        """
        self.logger.info(f'{self._id} shutting down listening socket')
        asyncio.set_event_loop(self.__loop)
        try:
            active_connections = len([task for task in asyncio.all_tasks(self.__loop) if not task.done()])
        except Exception:
            active_connections = 0
        if active_connections > 0:
            self.logger.info(f'{self._id} still has {active_connections} active connection(s), cleaning up')
        self.__running = False
        self.__loop.call_soon_threadsafe(self.__loop.stop)
        while self.__loop.is_running():
            pass
        with suppress(AttributeError):  # thread can disappear between first and second condition test
            if self.__listening_thread and self.__listening_thread.is_alive():
                self.__listening_thread.join()
        self.__listening_thread = None
        self.__loop.close()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()


class Udp_server(object):
    """
    Threaded UDP listener which dispatches received data via callbacks.

    NOTE: The callbacks need to expect the following arguments:

    - ``data_received(addr, data)`` where ``addr`` is a tuple with ``('<remote_ip>', remote_port)`` and ``data`` is the received data as string

    :param host: Local hostname or ip address (v4 or v6). Default is '' which listens on all IPv4 addresses available.
    :param port: Local port to connect to
    :param name: Name of this connection (mainly for logging purposes)

    :type host: str
    :type port: int
    :type name: str
    """

    def __init__(self, port, host='', name=None):
        self.logger = logging.getLogger(__name__)

        # Public properties
        self.name = name

        # protected properties
        self._host = host
        self._port = port
        self._is_listening = False

        self._ipaddr = None
        self._family = socket.AF_INET
        self._socket = None

        self._data_received_callback = None

        # provide a shutdown timeout for the server loop. emergency fallback only
        self._close_timeout = 2

        # private properties
        self.__coroutine = None
        self.__loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__loop)

        self.__server = aioudp.aioUDPServer()
        self.__listening_thread = None
        self.__running = True

        self._id = f'({self.name if self.name else "UDP_Server"}_{self._host}:{self._port})'

        # create sensible ipaddr (resolve host, handle protocol family)
        (self._ipaddr, self._port, self._family) = Network.validate_inet_addr(host, port)

        if self._ipaddr is not None:
            self._id = f'({self.name if self.name else "UDP_Server"}_{self._ipaddr}:{self._port})'
            self.__our_socket = Network.ip_port_to_socket(self._ipaddr, self._port)
            if not self.name:
                self.name = self.__our_socket
        else:
            self.__running = False

    def start(self):
        """
        Start the server socket.

        :return: False if an error prevented us from launching a connection thread. True if a connection thread has been started.
        :rtype: bool
        """
        if not self.__running:
            self.logger.error(f'{self._id} UDP server not initialized, can not start.')
            return False
        if self._is_listening:
            self.logger.warning(f'{self._id} already listening, not starting again')
            return False
        try:
            self.logger.info(f'{self._id} starting up UDP server socket')
            self.__coroutine = self.__start_server()
            self.__loop.run_until_complete(self.__coroutine)

            self.__listening_thread = threading.Thread(target=self.__listening_thread_worker, name=f'UDP_Server {self._id}')
            self.__listening_thread.daemon = True
            self.__listening_thread.start()
        except Exception as e:
            self.logger.error(f'{self._id} error {e} setting up udp server')
            return False
        return True

    def set_callbacks(self, data_received=None):
        """
        Set callbacks to caller for different socket events.

        :param data_received: Called when data is received

        :type data_received: function
        """
        self._data_received_callback = data_received

    def listening(self):
        """
        Return the current listening state.

        :return: True if the server socket is actually listening, else False.
        :rtype: bool
        """
        return self._is_listening

    def close(self):
        """
        Close running listening socket.
        """
        self.logger.info(f'{self._id} shutting down listening socket')
        asyncio.set_event_loop(self.__loop)
        self.__running = False
        self.__server.stop()

        # cancel pending tasks
        tasks = [t for t in asyncio.all_tasks(self.__loop) if t is not asyncio.current_task(self.__loop)]
        [task.cancel() for task in tasks]

        # close loop gracefully
        self.__loop.call_soon_threadsafe(self.__loop.stop)

        # this code shouldn't be needed, but include it with timeout just to be sure...
        starttime = time.time()
        while self.__loop.is_running() and time.time() < starttime + self._close_timeout:
            pass
        if self.__loop.is_running():
            self.__loop.stop()
        time.sleep(0.5)

        with suppress(AttributeError):  # thread can disappear between first and second condition test
            if self.__listening_thread and self.__listening_thread.is_alive():
                self.__listening_thread.join()
        self.__listening_thread = None        
        self.__loop.close()

    async def __start_server(self):
        """
        Start the actual server class.
        """
        self.__server.run(self._ipaddr, self._port, self.__loop)
        self.__server.subscribe(self.__handle_connection)

    def __listening_thread_worker(self):
        """
        Run the asyncio loop in a separate thread to not block the Udp_server.start() method.
        """
        self._is_listening = True
        self.logger.debug('{self._id} listening thread set is_listening to True')
        asyncio.set_event_loop(self.__loop)
        try:
            self.__loop.run_forever()
        except Exception as e:
            self.logger.debug(f'{self._id} error in loop.run_forever(): {e}')
        finally:
            self.__server.stop()
            self.__loop.close()
        self._is_listening = False
        return True

    async def __handle_connection(self, data, addr):
        """
        Handle incoming connection.

        As UDP is stateless, each datagram creates a new handler.

        :param data: data received from socket
        :type data: bytes
        :param addr: address info ('addr', port)
        :type addr: tuple
        """
        if addr:
            host, port = addr
        else:
            self.logger.debug(f'{self._id} address info {addr} not in format "(host, port)"')
            host = '0.0.0.0'
            port = 0

        self.logger.info(f'{self._id} incoming datagram from {host}:{port}')

        if data:
            try:
                string = str.rstrip(str(data, 'utf-8'))
                self.logger.debug(f'{self._id} received "{string}" from {host}:{port}')
                if self._data_received_callback:
                    self._data_received_callback(addr, string)
            except UnicodeError:
                self.logger.debug(f'{self._id} received undecodable bytes from {host}:{port}')
        else:
            self.logger.debug(f'{self._id} received empty datagram from {host}:{port}')

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()
