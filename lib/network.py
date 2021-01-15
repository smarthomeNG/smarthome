#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Parts Copyright 2016 C. Strassburg (lib.utils)     c.strassburg@gmx.de
#  Copyright 2017- Serge Wagener                     serge@wagener.family
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

|  *** ATTENTION: This is early work in progress. Interfaces are subject to change. ***
|  *** DO NOT USE IN PRODUCTION until you know what you are doing ***
|

This library contains the future network classes for SmartHomeNG.

New network functions and utilities are going to be implemented in this library.
This classes, functions and methods are mainly meant to be used by plugin developers

"""

import asyncio
import ipaddress
import logging
import queue
import re
import requests
from iowait import IOWait   ### BMX
import select               ### should not be needed
import socket
import struct
import subprocess
import threading
import time

# Turn off ssl warnings
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class Network(object):
    """ This Class has some usefull static methods that you can use in your projects """

    @staticmethod
    def is_mac(mac):
        """
        Validates a MAC address

        :param mac: MAC address
        :type string: str

        :return: True if value is a MAC
        :rtype: bool
        """

        mac = str(mac)
        if len(mac) == 12:
            for c in mac:
                try:
                    if int(c, 16) > 15:
                        return False
                except:
                    return False
            return True

        octets = re.split('[\:\-\ ]', mac)
        if len(octets) != 6:
            return False
        for i in octets:
            try:
                if int(i, 16) > 255:
                    return False
            except:
                return False
        return True

    @staticmethod
    def is_ip(string):
        """
        Checks if a string is a valid ip-address (v4 or v6)

        :param string: String to check
        :type string: str

        :return: True if an ip, false otherwise.
        :rtype: bool
        """

        return (Network.is_ipv4(string) or Network.is_ipv6(string))

    @staticmethod
    def is_ipv4(string):
        """
        Checks if a string is a valid ip-address (v4)

        :param string: String to check
        :type string: str

        :return: True if an ip, false otherwise.
        :rtype: bool
        """

        try:
            ipaddress.IPv4Address(string)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_ipv6(string):
        """
        Checks if a string is a valid ip-address (v6)

        :param string: String to check
        :type string: str

        :return: True if an ipv6, false otherwise.
        :rtype: bool
        """

        try:
            ipaddress.IPv6Address(string)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_hostname(string):
        """
        Checks if a string is a valid hostname

        The hostname has is checked to have a valid format

        :param string: String to check
        :type string: str

        :return: True if a hostname, false otherwise.
        :rtype: bool
        """

        try:
            return bool(re.match("^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$", string))
        except TypeError:
            return False

    @staticmethod
    def get_local_ipv4_address():
        """
        Get's local ipv4 address of the interface with the default gateway.
        Return '127.0.0.1' if no suitable interface is found

        :return: IPv4 address as a string
        :rtype: string
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    @staticmethod
    def get_local_ipv6_address():
        """
        Get's local ipv6 address of the interface with the default gateway.
        Return '::1' if no suitable interface is found

        :return: IPv6 address as a string
        :rtype: string
        """
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        try:
            s.connect(('2001:4860:4860::8888', 1))
            IP = s.getsockname()[0]
        except:
            IP = '::1'
        finally:
            s.close()
        return IP

    @staticmethod
    def ip_port_to_socket(ip, port):
        """
        Returns an ip address plus port to a socket string.
        Format is 'ip:port' for IPv4 or '[ip]:port' for IPv6

        :return: Socket address / IPEndPoint as string
        :rtype: string
        """
        if Network.is_ipv6(ip):
            ip = '[{}]'.format(ip)
        return '{}:{}'.format(ip, port)

    @staticmethod
    def ipver_to_string(ipver):
        """
        Converts a socket address family to an ip version string 'IPv4' or 'IPv6'

        :param ipver: Socket family
        :type ipver: socket.AF_INET or socket.AF_INET6

        :return: 'IPv4' or 'IPv6'
        :rtype: string
        """
        return 'IPv6' if ipver == socket.AF_INET6 else 'IPv4'

    @staticmethod
    def ping(ip):
        """
        Tries to ICMP ping a host using external OS utilities. Currently IPv4 only.

        :param ip: IPv4 address as a string
        :type ip: string

        :return: True if a reachable, false otherwise.
        :rtype: bool
        """
        logger = logging.getLogger(__name__)
        if subprocess.call("ping -c 1 %s" % ip, shell=True, stdout=open('/dev/null', 'w'), stderr=subprocess.STDOUT) == 0:
            logger.debug('Ping: {} is online'.format(ip))
            return True
        else:
            logger.debug('Ping: {} is offline'.format(ip))
            return False

    @staticmethod
    def ping_port(ip, port=80):
        """
        Tries to reach a given TCP port. Currently IPv4 only.

        :param ip: IPv4 address
        :param port: Port number

        :type ip: string
        :type port: int

        :return: True if a reachable, false otherwise.
        :rtype: bool
        """
        logger = logging.getLogger(__name__)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        if sock.connect_ex((ip, int(port))) == 0:
            logger.debug('Ping: port {} on {} is reachable'.format(port, ip))
            sock.close()
            return True
        else:
            logger.debug('Ping: port {} on {} is offline or not reachable'.format(port, ip))
            sock.close()
            return False

    @staticmethod
    def send_wol(mac, ip='255.255.255.255'):
        """
        Sends a wake on lan packet to the given mac address using ipv4 broadcast (or directed to specific ip)

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
        logger.debug('Sent WOL packet to {}'.format(mac))


class Http(object):
    """
    Creates an instance of the Http class.

    :param baseurl: base URL used everywhere in this instance (example: http://www.myserver.tld)
    :param timeout: Set a maximum amount of seconds the class should try to establish a connection

    :type baseurl: str
    :type timeout: int
    """
    def __init__(self, baseurl='', timeout=10):
        self.logger = logging.getLogger(__name__)

        self.baseurl = baseurl
        self._response = None
        self.timeout = timeout
        self._session = requests.Session()

    def HTTPDigestAuth(self, user=None, password=None):
        """
        Creates a HTTPDigestAuth instance and returns it to the caller.

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
        Launches a POST request and returns JSON answer as a dict or None on error.

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
            except:
                self.logger.warning("Invalid JSON received from {} !".format(url if url else self.baseurl))
            return json
        return None

    def get_json(self, url=None, params=None, verify=True, auth=None):
        """
        Launches a GET request and returns JSON answer as a dict or None on error.

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
            except:
                self.logger.warning("Invalid JSON received from {} !".format(url if url else self.baseurl))
            return json
        return None

    def get_text(self, url=None, params=None, encoding=None, timeout=None):
        """
        Launches a GET request and returns answer as string or None on error.

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
            except:
                self.logger.error("Successfull GET, but decoding response failed. This should never happen !")
        return _text

    def download(self, url=None, local=None, params=None, verify=True, auth=None):
        """
        Downloads a binary file to a local path

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
            self.logger.debug("Download of {} successfully completed, saving to {}".format(url, local))
            with open(str(local), 'wb') as f:
                for chunk in self._response:
                    f.write(chunk)
            return True
        else:
            self.logger.warning("Download error: {}".format(url))
            return False

    def get_binary(self, url=None, params=None):
        """
        Launches a GET request and returns answer as raw binary data or None on error.
        This is usefull for downloading binary objects / files.

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
        Returns the status code (200, 404, ...) of the last executed request.
        If GET request was not possible and thus no HTTP statuscode is available the returned status code = 0.

        :return: Status code and text of last request
        :rtype: (int, str)
        """
        try:
            (code, reason) = (self._response.status_code, self._response.reason)
        except:
            code = 0
            reason = 'Unable to complete GET request'
        return (code, reason)

    def response_headers(self):
        """
        Returns a dictionary with the server return headers of the last executed request

        :return: Headers returned by server
        :rtype: dict
        """
        return self._response.headers

    def response_cookies(self):
        """
        Returns a dictionary with the cookies the server may have sent on the last executed request

        :return: Cookies returned by server
        :rtype: dict
        """
        return self._response.cookies

    def response_object(self):
        """
        Returns the raw response object for advanced ussage. Use if you know what you are doing.
        Maybe this lib can be extented to your needs instead ?

        :return: Reponse object as returned by underlying requests library
        :rtype: `requests.Response <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
        """
        return self._response

    def __post(self, url=None, params=None, timeout=None, verify=True, auth=None, json=None, data=None, files={}):
        url = self.baseurl + url if url else self.baseurl
        timeout = timeout if timeout else self.timeout
        data = json if json else data
        self.logger.info("Sending POST request {} to {}".format(json, url))
        try:
            self._response = self._session.post(url, params=params, timeout=timeout, verify=verify, auth=auth, data=data, files=files)
            self.logger.debug("{} Posted to URL {}".format(self.response_status(), self._response.url))
        except Exception as e:
            self.logger.warning("Error sending POST request to {}: {}".format(url, e))
            return False
        return True

    def __get(self, url=None, params=None, timeout=None, verify=True, auth=None, stream=False):
        url = self.baseurl + url if url else self.baseurl
        timeout = timeout if timeout else self.timeout
        self.logger.info("Sending GET request to {}".format(url))
        try:
            self._response = self._session.get(url, params=params, timeout=timeout, verify=verify, auth=auth, stream=stream)
            self.logger.debug("{} Fetched URL {}".format(self.response_status(), self._response.url))
        except Exception as e:
            self.logger.warning("Error sending GET request to {}: {}".format(url, e))
            self._response = None
            return False
        return True


class Tcp_client(object):
    """ Creates a new instance of the Tcp_client class

    :param host: Remote host name or ip address (v4 or v6)
    :param port: Remote host port to connect to
    :param name: Name of this connection (mainly for logging purposes). Try to keep the name short.
    :param autoreconnect: Should the socket try to reconnect on lost connection (or finished connect cycle)
    :param connect_retries: Number of connect retries per cycle
    :param connect_cycle: Time between retries inside a connect cycle
    :param retry_cycle: Time between cycles if :param:autoreconnect is True
    :param binary: Switch between binary and text mode. Text will be encoded / decoded using encoding parameter.
    :param terminator: Terminator to use to split received data into chunks (split lines <cr> for example). If integer then split into n bytes. Default is None means process chunks as received.

    :type host: str
    :type port: int
    :type name: str
    :type autoreconnect: bool
    :type connect_retries: int
    :type connect_cycle: int
    :type retry_cycle: int
    :type binary: bool
    :type terminator: int | bytes | str
    """

    def __init__(self, host, port, name=None, autoreconnect=True, connect_retries=5, connect_cycle=5, retry_cycle=30, binary=False, terminator=False):
        self.logger = logging.getLogger(__name__)

        # Public properties
        self.name = name
        self.terminator = terminator

        # "Private" properties
        self._host = host
        self._port = port
        self._autoreconnect = autoreconnect
        self._is_connected = False
        self._is_receiving = False
        self._connect_retries = connect_retries
        self._connect_cycle = connect_cycle
        self._retry_cycle = retry_cycle
        self._timeout = 1

        self._hostip = None
        self._ipver = socket.AF_INET
        self._socket = None
        self._connect_counter = 0
        self._binary = binary

        self._connected_callback = None
        self._receiving_callback = None
        self._disconnected_callback = None
        self._data_received_callback = None

        # "Secret" properties
        self.__connect_thread = None
        self.__connect_threadlock = threading.Lock()
        self.__receive_thread = None
        self.__receive_threadlock = threading.Lock()
        self.__running = True

        self.logger.setLevel(logging.DEBUG)
        self.logger.info("Initializing a connection to {} on TCP port {} {} autoreconnect".format(self._host, self._port, ('with' if self._autoreconnect else 'without')))

        # Test if host is an ip address or a host name
        if Network.is_ip(self._host):
            # host is a valid ip address (v4 or v6)
            self.logger.debug("{} is a valid IP address".format(host))
            self._hostip = self._host
            if Network.is_ipv6(self._host):
                self._ipver = socket.AF_INET6
            else:
                self._ipver = socket.AF_INET
        else:
            # host is a hostname, trying to resolve to an ip address (v4 or v6)
            self.logger.debug("{} is not a valid IP address, trying to resolve it as hostname".format(host))
            try:
                self._ipver, sockettype, proto, canonname, socketaddr = socket.getaddrinfo(host, None)[0]
                # Check if resolved address is IPv4 or IPv6
                if self._ipver == socket.AF_INET:  # is IPv4
                    self._hostip, port = socketaddr
                elif self._ipver == socket.AF_INET6:  # is IPv6
                    self._hostip, port, flow_info, scope_id = socketaddr
                else:
                    # This should never happen
                    self.logger.error("Unknown ip address family {}".format(self._ipver))
                    self._hostip = None
                # Print ip address on successfull resolve
                if self._hostip is not None:
                    self.logger.info("Resolved {} to {} address {}".format(self._host, 'IPv6' if self._ipver == socket.AF_INET6 else 'IPv4', self._hostip))
            except:
                # Unable to resolve hostname
                self.logger.error("Cannot resolve {} to a valid ip address (v4 or v6)".format(self._host))
                self._hostip = None

    def set_callbacks(self, connected=None, receiving=None, data_received=None, disconnected=None):
        """ Set callbacks to caller for different socket events

        :param connected: Called whenever a connection is established successfully
        :param data_received: Called when data is received
        :param disconnected: Called when a connection has been dropped for whatever reason

        :type connected: function
        :type data_received: function
        :type disconnected: function
        """
        self._connected_callback = connected
        self._receiving_callback = receiving
        self._disconnected_callback = disconnected
        self._data_received_callback = data_received

    def connect(self):
        """ Connects the socket

        :return: False if an error prevented us from launching a connection thread. True if a connection thread has been started.
        :rtype: bool
        """
        if self._hostip is None:  # return False if no valid ip to connect to
            self.logger.error("No valid IP address to connect to {}".format(self._host))
            self._is_connected = False
            return False
        if self._is_connected:  # return false if already connected
            self.logger.error("Already connected to {}, ignoring new request".format(self._host))
            return False

        self.__connect_thread = threading.Thread(target=self._connect_thread_worker, name='TCP_Connect')
        self.__connect_thread.daemon = True
        self.__connect_thread.start()
        return True

    def connected(self):
        """ Returns the current connection state

        :return: True if an active connection exists,else False.
        :rtype: bool
        """
        return self._is_connected

    def send(self, message):
        """ Sends a message to the server. Can be a string, bytes or a bytes array.

        :return: True if message has been successfully sent, else False.
        :rtype: bool
        """
        if not isinstance(message, (bytes, bytearray)):
            try:
                message = message.encode('utf-8')
            except:
                self.logger.warning("Error encoding message for client {}".format(self.name))
                return False
        try:
            if self._is_connected:
                self._socket.send(message)
            else:
                return False
        except Exception as e:
            self.logger.warning("No connection to {}, cannot send data {}. Error: {}".format(self._host, message, e))
            return False
        return True

    def _connect_thread_worker(self):
        if not self.__connect_threadlock.acquire(blocking=False):
            self.logger.warning("Connection attempt already in progress for {}, ignoring new request".format(self._host))
            return
        if self._is_connected:
            self.logger.error("Already connected to {}, ignoring new request".format(self._host))
            return
        self.logger.debug("Starting connection cycle for {}".format(self._host))
        self._connect_counter = 0
        while self.__running and not self._is_connected:
            # Try a full connect cycle
            while not self._is_connected and self._connect_counter < self._connect_retries and self.__running:
                self._connect()
                if self._is_connected:
                    try:
                        self.__connect_threadlock.release()
                        self._connected_callback and self._connected_callback(self)
                        _name='TCP_Client'
                        if self.name is not None:
                            _name = self.name + '.' + _name
                        self.__receive_thread = threading.Thread(target=self.__receive_thread_worker, name=_name)
                        self.__receive_thread.daemon = True
                        self.__receive_thread.start()
                    except:
                        raise
                    return True
                self._sleep(self._connect_cycle)

            if self._autoreconnect:
                self._sleep(self._retry_cycle)
                self._connect_counter = 0
            else:
                break
        try:
            self.__connect_threadlock.release()
        except:
            pass

    def _connect(self):
        self.logger.debug("Connecting to {} using {} {} on TCP port {} {} autoreconnect".format(self._host, 'IPv6' if self._ipver == socket.AF_INET6 else 'IPv4', self._hostip, self._port, ('with' if self._autoreconnect else 'without')))
        # Try to connect to remote host using ip (v4 or v6)
        try:
            self._socket = socket.socket(self._ipver, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self._socket.settimeout(5)
            self._socket.connect(('{}'.format(self._hostip), int(self._port)))
            self._socket.settimeout(self._timeout)
            self._is_connected = True
            self.logger.info("Connected to {} on TCP port {}".format(self._host, self._port))
        # Connection error
        except Exception as err:
            self._is_connected = False
            self._connect_counter += 1
            self.logger.warning("TCP connection to {}:{} failed with error {}. Counter: {}/{}".format(self._host, self._port, err, self._connect_counter, self._connect_retries))

    def __receive_thread_worker(self):
        waitobj = IOWait()
        waitobj.watch( self._socket, read=True)
        ### BMX poller = select.poll()
        ### BMX poller.register(self._socket, select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR)
        __buffer = b''

        self._is_receiving = True
        self._receiving_callback and self._receiving_callback(self)
        while self._is_connected and self.__running:
            ### BMX events = poller.poll(1000)
            events = waitobj.wait(1000)     ### BMX
            ### BMX for fd, event in events:
            for fileno, read, write in events:  ### BMX
                ### BMX if event & select.POLLHUP:
                ### BMX     self.logger.warning("Client socket closed")
                # Check if POLLIN event triggered
                ### BMX if event & (select.POLLIN | select.POLLPRI):
                if read:
                    msg = self._socket.recv(4096)
                    # Check if incoming message is not empty
                    if msg:
                        # If we transfer in text mode decode message to string
                        if not self._binary:
                            msg = str.rstrip(str(msg, 'utf-8'))
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
                                    self._data_received_callback(self, line)
                        # If not in terminator mode just forward what we received
                        else:
                            if self._data_received_callback is not None:
                                self._data_received_callback(self, msg)
                    # If empty peer has closed the connection
                    else:
                        # Peer connection closed
                        self.logger.warning("Connection closed by peer {}".format(self._host))
                        self._is_connected = False
                        ### BMX poller.unregister()
                        waitobj.unwatch(self._socket)
                        self._disconnected_callback and self._disconnected_callback(self)
                        if self._autoreconnect:
                            self.logger.debug("Autoreconnect enabled for {}".format(self._host))
                            self.connect()
        self._is_receiving = False

    def _sleep(self, time_lapse):
        time_start = time.time()
        time_end = (time_start + time_lapse)
        while self.__running and time_end > time.time():
            pass

    def close(self):
        """ Closes the current client socket """
        self.logger.info("Closing connection to {} on TCP port {}".format(self._host, self._port))
        self.__running = False
        if self.__connect_thread is not None and self.__connect_thread.isAlive():
            self.__connect_thread.join()
        if self.__receive_thread is not None and self.__receive_thread.isAlive():
            self.__receive_thread.join()


class _Client(object):
    """ Client object that represents a connected client of tcp_server

    :param server: The tcp_server passes a reference to itself to access parent methods
    :param socket: socket.Socket class used by the Client object
    :param fd: File descriptor of socket used by the Client object

    :type server: tcp_server
    :type socket: function
    :type fd: int
    """
    def __init__(self, server=None, socket=None, ip=None, port=None):
        self.logger = logging.getLogger(__name__)
        self.name = None
        self.ip = ip
        self.port = port
        self.ipver = None
        self.writer = None
        self.process_iac = True

        self._data_received_callback = None
        self._will_close_callback = None
        self.__server = server
        self.__socket = socket

    @property
    def socket(self):
        return self.__socket

    def set_callbacks(self, data_received=None, will_close=None):
        """ Set callbacks for different socket events (client based)

        :param data_received: Called when data is received
        :type data_received: function
        """
        self._data_received_callback = data_received
        self._will_close_callback = will_close

    def send(self, message):
        """ Send a string to connected client

        :param msg: Message to send
        :type msg: string | bytes | bytearray

        :return: True if message has been queued successfully.
        :rtype: bool
        """
        if not isinstance(message, (bytes, bytearray)):
            try:
                message = message.encode('utf-8')
            except:
                self.logger.warning("Error encoding data for client {}".format(self.name))
                return False
        try:

            self.writer.write(message)
            self.writer.drain()
        except:
            self.logger.warning("Error sending data to client {}".format(self.name))
            return False
        return True

    def send_echo_off(self):
        """ Sends an IAC telnet command to ask client to turn it's echo off """
        command = bytearray([0xFF, 0xFB, 0x01])
        string = self._iac_to_string(command)
        self.logger.debug("Sending IAC telnet command: '{}'".format(string))
        self.send(command)

    def send_echo_on(self):
        """ Sends an IAC telnet command to ask client to turn it's echo on again """
        command = bytearray([0xFF, 0xFC, 0x01])
        string = self._iac_to_string(command)
        self.logger.debug("Sending IAC telnet command: '{}'".format(string))
        self.send(command)

    def _process_IAC(self, msg):
        """ Processes incomming IAC messages. Does nothing for now except logging them in clear text """
        if len(msg) >= 3:
            string = self._iac_to_string(msg[:3])
            self.logger.debug("Received IAC telnet command: '{}'".format(string))
            msg = msg[3:]
        return msg

    def close(self):
        """ Client socket closes itself """
        self._will_close_callback and self._will_close_callback(self)
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
                #string += '<UNKNOWN> '
                string += chr(char)
        return string.rstrip()


class Tcp_server(object):
    """ Creates a new instance of the Tcp_server class

    :param interface: Remote interface name or ip address (v4 or v6). Default is '::' which listens on all IPv4 and all IPv6 addresses available.
    :param port: Remote interface port to connect to
    :param name: Name of this connection (mainly for logging purposes)

    :type interface: str
    :type port: int
    :type name: str
    """

    MODE_TEXT = 1
    MODE_TEXT_LINE = 2
    MODE_BINARY = 3
    MODE_FIXED_LENGTH = 4

    def __init__(self, port, interface='', name=None, mode=MODE_BINARY, terminator=None):
        self.logger = logging.getLogger(__name__)

        # Public properties
        self.name = name
        self.mode = mode
        self.terminator = terminator

        # "Private" properties
        self._interface = interface
        self._port = port
        self._is_listening = False
        self._timeout = 1

        self._interfaceip = None
        self._ipver = socket.AF_INET
        self._socket = None

        self._listening_callback = None
        self._incoming_connection_callback = None
        self._data_received_callback = None

        # "Secret" properties
        self.__loop = None
        self.__coroutine = None
        self.__server = None
        self.__listening_thread = None
        self.__listening_threadlock = threading.Lock()
        self.__running = True

        # Test if host is an ip address or a host name
        if self._interface == '' or Network.is_ip(self._interface):
            # host is a valid ip address (v4 or v6)
            self._interfaceip = self._interface
            if self._interface == '':
                self._interface = 'All Ipv4/Ipv6'
            self.logger.debug("'{}' is a valid IP address".format(self._interface))
            if Network.is_ipv6(self._interfaceip):
                self._ipver = socket.AF_INET6
            else:
                self._ipver = socket.AF_INET
        else:
            # host is a hostname, trying to resolve to an ip address (v4 or v6)
            self.logger.debug("{} is not a valid IP address, trying to resolve it as hostname".format(self._interface))
            try:
                self._ipver, sockettype, proto, canonname, socketaddr = socket.getaddrinfo(self._interface, None)[0]
                # Check if resolved address is IPv4 or IPv6
                if self._ipver == socket.AF_INET:
                    self._interfaceip, port = socketaddr
                elif self._ipver == socket.AF_INET6:
                    self._interfaceip, port, flow_info, scope_id = socketaddr
                else:
                    self.logger.error("Unknown ip address family {}".format(self._ipver))
                    self._interfaceip = None
                if self._interfaceip is not None:
                    self.logger.info("Resolved {} to {} address {}".format(self._interface, ipver_to_string(self._ipver), self._hostip))
            except:
                # Unable to resolve hostname
                self.logger.error("Cannot resolve {} to a valid ip address (v4 or v6)".format(self._interface))
                self._interfaceip = None

        self.__our_socket = Network.ip_port_to_socket(self._interfaceip, self._port)
        if not self.name:
            self.name = self.__our_socket

    def set_callbacks(self, listening=None, incoming_connection=None, disconnected=None, data_received=None):
        """ Set callbacks to caller for different socket events

        :param connected: Called whenever a connection is established successfully
        :param data_received: Called when data is received
        :param disconnected: Called when a connection has been dropped for whatever reason

        :type connected: function
        :type data_received: function
        :type disconnected: function
        """
        self._listening_callback = listening
        self._incoming_connection_callback = incoming_connection
        self._data_received_callback = data_received
        self._disconnected_callback = disconnected

    def start(self):
        """ Start the server socket

        :return: False if an error prevented us from launching a connection thread. True if a connection thread has been started.
        :rtype: bool
        """
        if self._is_listening:
            return False
        try:
            self.logger.info("Starting up TCP server socket {}".format(self.__our_socket))
            self.__loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.__loop)
            self.__coroutine = asyncio.start_server(self.__handle_connection, self._interfaceip, self._port)
            self.__server = self.__loop.run_until_complete(self.__coroutine)

            _name = 'TCP_Server'
            if self.name is not None:
                _name = self.name + '.' + _name

            self.__listening_thread = threading.Thread(target=self.__listening_thread_worker, name=_name)
            self.__listening_thread.daemon = True
            self.__listening_thread.start()
        except:
            return False
        return True

    def __listening_thread_worker(self):
        """ Runs the asyncio loop in a separate thread to not block the Tcp_server.start() method """
        asyncio.set_event_loop(self.__loop)
        self._is_listening = True
        try:
            self.__loop.run_forever()
        except:
            self.logger.debug('*** Error in loop.run_forever()')
        finally:

            for task in asyncio.Task.all_tasks():
                task.cancel()
            self.__server.close()
            self.__loop.run_until_complete(self.__server.wait_closed())
            self.__loop.close()
        self._is_listening = False
        return True

    async def __handle_connection(self, reader, writer):
        """ Handles incoming connection. One handler per client """
        peer = writer.get_extra_info('peername')
        socket_object = writer.get_extra_info('socket')
        peer_socket = Network.ip_port_to_socket(peer[0], peer[1])

        client = _Client(server=self, socket=socket_object, ip=peer[0], port=peer[1])
        client.ipver = socket.AF_INET6 if Network.is_ipv6(client.ip) else socket.AF_INET
        client.name = Network.ip_port_to_socket(client.ip, client.port)
        client.writer = writer

        self.logger.info("Incoming connection from {} on socket {}".format(peer_socket, self.__our_socket))
        self._incoming_connection_callback and self._incoming_connection_callback(self, client)

        while True:
            try:
                if self.mode == self.MODE_TEXT_LINE:
                    # self.logger.debug("***")
                    data = await reader.readline()
                else:
                    data = await reader.read(4096)
            except:
                data = None

            if data and data[0] == 0xFF and client.process_iac:
                data = client._process_IAC(data)
            if data:
                try:
                    string = str.rstrip(str(data, 'utf-8'))
                    self.logger.debug("Received '{}' from {}".format(string, client.name))
                    self._data_received_callback and self._data_received_callback(self, client, string)
                    client._data_received_callback and client._data_received_callback(self, client, string)
                except:
                    self.logger.debug("Received undecodable bytes from {}".format(client.name))
            else:
                try:
                    self.__close_client(client)
                    pass
                finally:
                    del client
                return

    def __close_client(self, client):
        self.logger.info("Lost connection to client {}".format(client.name))
        self._disconnected_callback and self._disconnected_callback(self, client)
        client.writer.close()

    def listening(self):
        """ Returns the current listening state

        :return: True if the server socket is actually listening, else False.
        :rtype: bool
        """
        return self._is_listening

    def send(self, client, msg):
        """ Send a string to connected client

        :param client: Client Object to send message to
        :param msg: Message to send

        :type client: network.Client
        :type msg: string | bytes | bytearray

        :return: True if message has been queued successfully.
        :rtype: bool
        """
        client.send(msg)
        return True

    def disconnect(self, client):
        """ Disconnects a specific client

        :param client: Client Object to disconnect
        :type client: network.Client
        """
        client.close()
        return True

    def close(self):
        """ Closes running listening socket """
        self.logger.info("Shutting down listening socket on interface {} port {}".format(self._interface, self._port))
        asyncio.set_event_loop(self.__loop)
        try:
            active_connections = len([task for task in asyncio.Task.all_tasks() if not task.done()])
        except:
            active_connections = 0
        if active_connections > 0:
            self.logger.info('Tcp_server still has {} active connection(s), cleaning up'.format(active_connections))
        self.__running = False
        self.__loop.call_soon_threadsafe(self.__loop.stop)
        while self.__loop.is_running():
            pass
        if self.__listening_thread and self.__listening_thread.isAlive():
            self.__listening_thread.join()
        self.__loop.close()
