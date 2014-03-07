#!/usr/bin/env python3
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
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
import socket
import collections
import threading
import select
import time

logger = logging.getLogger('')


class Base():

    _poller = None
    _family = {'UDP': socket.AF_INET, 'UDP6': socket.AF_INET6, 'TCP': socket.AF_INET, 'TCP6': socket.AF_INET6}
    _type = {'UDP': socket.SOCK_DGRAM, 'UDP6': socket.SOCK_DGRAM, 'TCP': socket.SOCK_STREAM, 'TCP6': socket.SOCK_STREAM}
    _monitor = []

    def __init__(self, monitor=False):
        self._name = self.__class__.__name__
        if monitor:
            self._monitor.append(self)

    def _create_socket(self, flags=None):
        family, type, proto, canonname, sockaddr = socket.getaddrinfo(self._host, self._port, family=self._family[self._proto], type=self._type[self._proto])[0]
        self.socket = socket.socket(family, type, proto)
        return sockaddr


class Connections(Base):

    _connections = {}
    _servers = {}
    _ro = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
    _rw = _ro | select.EPOLLOUT

    def __init__(self):
        Base.__init__(self)
        Base._poller = self
        self._epoll = select.epoll()

    def register_server(self, fileno, obj):
        self._servers[fileno] = obj
        self._connections[fileno] = obj
        self._epoll.register(fileno, self._ro)

    def register_connection(self, fileno, obj):
        self._connections[fileno] = obj
        self._epoll.register(fileno, self._ro)

    def unregister_connection(self, fileno):
        try:
            self._epoll.unregister(fileno)
            del(self._connections[fileno])
            del(self._servers[fileno])
        except:
            pass

    def monitor(self, obj):
        self._monitor.append(obj)

    def check(self):
        for obj in self._monitor:
            if not obj.connected:
                obj.connect()

    def trigger(self, fileno):
        if self._connections[fileno].outbuffer:
            self._epoll.modify(fileno, self._rw)

    def poll(self):
        time.sleep(0.0000000001)  # give epoll.modify a chance
        if not self._connections:
            time.sleep(1)
            return
        for fileno in self._connections:
            if fileno not in self._servers:
                if self._connections[fileno].outbuffer:
                    self._epoll.modify(fileno, self._rw)
                else:
                    self._epoll.modify(fileno, self._ro)
        for fileno, event in self._epoll.poll(timeout=1):
            if fileno in self._servers:
                server = self._servers[fileno]
                server.handle_connection()
            else:
                if event & select.EPOLLIN:
                    try:
                        con = self._connections[fileno]
                        con._in()
                    except Exception as e:  # noqa
#                       logger.exception("{}: {}".format(self._name, e))
                        con.close()
                        continue
                if event & select.EPOLLOUT:
                    try:
                        con = self._connections[fileno]
                        con._out()
                    except Exception as e:  # noqa
                        con.close()
                        continue
                if event & (select.EPOLLHUP | select.EPOLLERR):
                    try:
                        con = self._connections[fileno]
                        con.close()
                        continue
                    except:
                        pass

    def close(self):
        for fileno in self._connections:
            try:
                self._connections[fileno].close()
            except:
                pass


class Server(Base):

    def __init__(self, host, port, proto='TCP'):
        Base.__init__(self, monitor=True)
        self._host = host
        self._port = port
        self._proto = proto
        self.address = "{}:{}".format(host, port)
        self.connected = False

    def connect(self):
        try:
            sockaddr = self._create_socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(sockaddr)
            if self._proto.startswith('TCP'):
                self.socket.listen(5)
            self.socket.setblocking(0)
        except Exception as e:
            logger.error("{}: problem binding {} ({}): {}".format(self._name, self.address, self._proto, e))
            self.close()
        else:
            self.connected = True
            logger.debug("{}: binding to {} ({})".format(self._name, self.address, self._proto))
            self._poller.register_server(self.socket.fileno(), self)

    def close(self):
        self.connected = False
        try:
            self._poller.unregister_connection(self.socket.fileno())
        except:
            pass
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
        try:
            del(self.socket)
        except:
            pass

    def accept(self):
        try:
            sock, addr = self.socket.accept()
            sock.setblocking(0)
            addr = "{}:{}".format(addr[0], addr[1])
            logger.debug("{}: incoming connection from {} to {}".format(self._name, addr, self.address))
            return sock, addr
        except:
            return None, None

    def handle_connection(self):
        pass


class Stream(Base):

    def __init__(self, sock=None, address=None, monitor=False):
        Base.__init__(self, monitor=monitor)
        self.connected = False
        self.address = address
        self.inbuffer = bytearray()
        self.outbuffer = collections.deque()
        self.__olock = threading.Lock()
        self._frame_size_in = 4096
        self._frame_size_out = 4096
        self.terminator = b'\r\n'
        self._balance_open = False
        self._balance_close = False
        self._close_after_send = False
        if sock is not None:
            self.socket = sock
            self._connected()

    def _connected(self):
            self._poller.register_connection(self.socket.fileno(), self)
            self.connected = True
            self.handle_connect()

    def _in(self):
        max_size = self._frame_size_in
        try:
            data = self.socket.recv(max_size)
        except Exception as e:  # noqa
#           logger.warning("{}: {}".format(self._name, e))
            self.close()
            return
        if data == b'':
            self.close()
            return
        self.inbuffer.extend(data)
        while True:
            terminator = self.terminator
            buffer_len = len(self.inbuffer)
            if not terminator:
                if not self._balance_open:
                    break
                index = self._is_balanced()
                if index:
                    data = self.inbuffer[:index]
                    self.inbuffer = self.inbuffer[index:]
                    self.found_balance(data)
                else:
                    break
            elif isinstance(terminator, int):
                if buffer_len < terminator:
                    break
                else:
                    data = self.inbuffer[:terminator]
                    self.inbuffer = self.inbuffer[terminator:]
                    self.terminator = 0
                    self.found_terminator(data)
            else:
                if terminator not in self.inbuffer:
                    break
                index = self.inbuffer.find(terminator)
                data = self.inbuffer[:index]
                cut = index + len(terminator)
                self.inbuffer = self.inbuffer[cut:]
                self.found_terminator(data)

    def _is_balanced(self):
        stack = []
        for index, char in enumerate(self.inbuffer):
            if char == self._balance_open:
                stack.append(char)
            elif char == self._balance_close:
                stack.append(char)
                if stack.count(self._balance_open) < stack.count(self._balance_close):
                    logger.warning("{}: unbalanced input!".format(self._name))
                    logger.close()
                    return False
                if stack.count(self._balance_open) == stack.count(self._balance_close):
                    return index + 1
        return False

    def _out(self):
        if not self.__olock.acquire(timeout=1):
            return
        try:
            while self.connected:
                frame = self.outbuffer.pop()
                if not frame:
                    if frame is None:
                        self.close()
                        return
                    continue  # ignore empty frames
                sent = self.socket.send(frame)
                if sent < len(frame):
                    self.outbuffer.append(frame[sent:])
            if self._close_after_send:
                self.close()
        except IndexError:  # buffer empty
            return
        except socket.error:
            self.outbuffer.append(frame)
        except Exception as e:  # noqa
            logger.exception("{}: {}".format(self._name, e))
            self.close()
        finally:
            self.__olock.release()

    def balance(self, bopen, bclose):
        self._balance_open = ord(bopen)
        self._balance_close = ord(bclose)

    def close(self):
        if self.connected:
            logger.debug("{}: closing socket {}".format(self._name, self.address))
        self.connected = False
        try:
            self._poller.unregister_connection(self.socket.fileno())
        except:
            pass
        try:
            self.handle_close()
        except:
            pass
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass
        try:
            del(self.socket)
        except:
            pass

    def discard_buffers(self):
        self.inbuffer = bytearray()
        self.outbuffer.clear()

    def found_terminator(self, data):
        pass

    def found_balance(self, data):
        pass

    def handle_close(self):
        pass

    def handle_connect(self):
        pass

    def send(self, data, close=False):
        self._close_after_send = close
        if not self.connected:
            return False
        frame_size = self._frame_size_out
        if len(data) > frame_size:
            for i in range(0, len(data), frame_size):
                self.outbuffer.appendleft(data[i:i + frame_size])
        else:
            self.outbuffer.appendleft(data)
        self._out()
        return True


class Client(Stream):

    def __init__(self, host, port, proto='TCP', monitor=False):
        Stream.__init__(self, monitor=monitor)
        self._host = host
        self._port = port
        self._proto = proto
        self.address = "{}:{}".format(host, port)
        self._connection_attempts = 0
        self._connection_errorlog = 60
        self._connection_lock = threading.Lock()

    def connect(self):
        self._connection_lock.acquire()
        if self.connected:
            self._connection_lock.release()
            return
        try:
            sockaddr = self._create_socket()
            self.socket.settimeout(2)
            self.socket.connect(sockaddr)
            self.socket.setblocking(0)
#           self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                logger.error("{}: could not connect to {} ({}): {}".format(self._name, self.address, self._proto, e))
                self._connection_attempts = self._connection_errorlog
            self.close()
        else:
            logger.debug("{}: connected to {}".format(self._name, self.address))
            self._connected()
        finally:
            self._connection_lock.release()
