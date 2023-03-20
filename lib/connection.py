#!/usr/bin/env python3
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
#  Copyright 2018 Bernd Meiners                     Bernd.Meiners@Mail.de
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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
#########################################################################

"""

This library is on its way out. Network classes for SmartHomeNG are provided by
lib.network. Creating lib.connection Server and Client class object will
create an appropriate WARNING log entry.

The following modules use an import lib.connection as of December 2021:
smarthome.py for an object of Connections()
Plugins:
visu_websocket

"""
import logging
import socket
import collections
import threading
import select
import time
import sys
from iowait import IOWait

logger = logging.getLogger(__name__)


class Base():
    """
    provides same base class for class Connections(), class Server(),
    class Stream() and thus also to class Client() which inherits from Stream()

    some lookup dicts for protocol family like TCP or UDP flavours and the like for protocol type
    """

    _poller = None
    _family = {'UDP': socket.AF_INET, 'UDP6': socket.AF_INET6, 'TCP': socket.AF_INET, 'TCP6': socket.AF_INET6}
    _type = {'UDP': socket.SOCK_DGRAM, 'UDP6': socket.SOCK_DGRAM, 'TCP': socket.SOCK_STREAM, 'TCP6': socket.SOCK_STREAM}
    _monitor = []
    _deprecated_wanings = True

    def __init__(self, monitor=False):
        self._name = self.__class__.__name__
        if monitor:
            self._monitor.append(self)

    def _create_socket(self, flags=None):
        family, type, proto, canonname, sockaddr = socket.getaddrinfo(self._host, self._port, family=self._family[self._proto], type=self._type[self._proto])[0]
        self.socket = socket.socket(family, type, proto)
        return sockaddr

    def _deprecated_warning(self, n_func=''):
        """
        Display function deprecated warning
        """
        if hasattr(self, '_deprecated_warnings'):
            if lib.utils.Utils.to_bool(self._deprecated_warnings) == False:
                return
        else:
            return # if parameter is not defined

        d_func = 'sh.'+str(sys._getframe(1).f_code.co_name)+'()'
        if n_func != '':
            n_func = '- use the '+n_func+' instead'
        try:
            d_test = ' (' + str(sys._getframe(2).f_locals['self'].__module__) + ')'
        except:
            d_test = ''

        called_by = str(sys._getframe(2).f_code.co_name)
        in_class = ''
        try:
            in_class = 'class ' + str(sys._getframe(2).f_locals['self'].__class__.__name__) + d_test
        except:
            in_class = 'a logic?' + d_test
        if called_by == '<module>':
            called_by = str(sys._getframe(3).f_code.co_name)
            level = 3
            while True:
                level += 1
                try:
                    c_b = str(sys._getframe(level).f_code.co_name)
                except ValueError:
                    c_b = ''
                if c_b == '':
                    break
                called_by += ' -> ' + c_b

#            called_by = str(sys._getframe(3).f_code.co_name)

        if not hasattr(self, 'dep_id_list'):
            self.dep_id_list = []
        id_str = d_func + '|' + in_class + '|' + called_by
        if not id_str in self.dep_id_list:
            self.logger.warning("DEPRECATED: Used function '{}', called in '{}' by '{}' {}".format(d_func, in_class, called_by, n_func))
            self.dep_id_list.append(id_str)
        return


class Connections(Base):
    """
    Within SmartHome.py there is one instance of this class

    The filenumber of a connection is the key to the contained dicts of
    _connections and _servers
    Additionally the filenumber is used for either epoll or kqueue depending
    on the environment found for select.
    A filenumber of value -1 is an error value.
    """

    _connections = {}
    _servers = {}
    if hasattr(select, 'epoll'):
        _ro = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        _rw = _ro | select.EPOLLOUT

    def __init__(self):
        Base.__init__(self)
        Base._poller = self
        if hasattr(select, 'epoll'):
            self._epoll = select.epoll()
        elif hasattr(select, 'kqueue'):
            self._kqueue = select.kqueue()
        else:
            logger.debug("Init connections using IOWait")
            self._connections_found = 0
            self._waitobj = IOWait()

    def register_server(self, fileno, obj):
        if fileno == -1:
            logger.error("{} tried to register a server with filenumber == -1".format(obj))
            return
        self._servers[fileno] = obj
        self._connections[fileno] = obj
        if hasattr(select, 'epoll'):
            self._epoll.register(fileno, self._ro)
        elif hasattr(select, 'kqueue'):
            event = [
                select.kevent(fileno,
                       filter=select.KQ_FILTER_READ,
                       flags=select.KQ_EV_ADD)
            ]
            self._kqueue.control(event, 0, 0)
        else:
            logger.debug("register_server: put watch on fileno {}".format(fileno))
            self._waitobj.watch(fileno, read=True)

    def register_connection(self, fileno, obj):
        if fileno == -1:
            logger.error("tried to register a connection with filenumber == -1")
            return
        self._connections[fileno] = obj
        if hasattr(select, 'epoll'):
            self._epoll.register(fileno, self._ro)
        elif hasattr(select, 'kqueue'):
            event = [
                select.kevent(fileno,
                       filter=select.KQ_FILTER_READ,
                       flags=select.KQ_EV_ADD)
            ]
            self._kqueue.control(event, 0, 0)
        else:
            logger.debug("register_connection: put watch on fileno {}".format(fileno))
            self._waitobj.watch(fileno, read=True)

    def unregister_connection(self, fileno):
        if fileno == -1:
            logger.error("tried to unregister a connection with filenumber == -1")
            return
        try:
            if hasattr(select, 'epoll'):
                self._epoll.unregister(fileno)
            elif hasattr(select, 'kqueue'):
                pass
            else:
                logger.debug("unregister_connection: unwatch fileno {}".format(fileno))
                self._waitobj.unwatch(fileno)
        except Exception as e:
            logger.error("unregister a connection with filenumber == {} for epoll failed".format(fileno))

        try:
            del(self._connections[fileno])
        except:
            pass

        try:
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
        if fileno == -1:
            logger.error("tried to trigger a connection with filenumber == -1")
            return
        if self._connections[fileno].outbuffer:
            if hasattr(select, 'epoll'):
                self._epoll.modify(fileno, self._rw)
            elif hasattr(select, 'kqueue'):
                event = [
                    select.kevent(fileno,
                           filter=select.KQ_FILTER_WRITE,
                           flags=select.KQ_EV_ADD | KQ_EV_ONESHOT)
                ]
                self._kqueue.control(event, 0, 0)
            else:
                logger.error("trigger: Operating System without epoll or kqueue is currently not supported, please report this error")

    def poll(self):
        time.sleep(0.0000000001)  # give epoll.modify a chance
        if not self._connections:
            time.sleep(1)
            return

        if -1 in self._connections:
            logger.error("fileno -1 was found, please report to SmartHomeNG team")
            del( self._connections[-1])

        if hasattr(select, 'epoll') or hasattr(select, 'kqueue'):
            for fileno in self._connections:
            # Fix for: "RuntimeError: dictionary changed size during iteration"
            #connections_keys = self._connections.keys()
            #for fileno in connections_keys:
                if fileno not in self._servers:
                    if hasattr(select, 'epoll'):
                        if self._connections[fileno].outbuffer:
                            try:
                                self._epoll.modify(fileno, self._rw)
                            except OSError as e:
                                # as with python 3.6 an OSError will be raised when a socket is already closed like with a settimeout
                                # the socket will need to be recreated then
                                logger.error("OSError {} for epoll.modify(RW) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache
                            except PermissionError as e:
                                logger.error("PermissionError {} for epoll.modify(RW) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache
                            except FileNotFoundError as e:
                                logger.error("FileNotFoundError {} for epoll.modify(RW) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache
                        else:
                            try:
                                self._epoll.modify(fileno, self._ro)
                            except OSError as e:
                                # as with python 3.6 an OSError will be raised when a socket is already closed like with a settimeout
                                # the socket will need to be recreated then
                                logger.error("OSError {} for epoll.modify(RO) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache
                            except PermissionError as e:
                                logger.error("PermissionError {} for epoll.modify(RO) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache
                            except FileNotFoundError as e:
                                logger.error("FileNotFoundError {} for epoll.modify(RO) with fileno {} for object {}, please report to SmartHomeNG team".format(e, fileno, self._connections[fileno]))
                                # here we could try to get rid of the connection that causes the headache

                    elif hasattr(select, 'kqueue'):
                        event = []
                        if self._connections[fileno].outbuffer:
                            event.append(select.kevent(fileno,
                                                filter=select.KQ_FILTER_WRITE,
                                                flags=select.KQ_EV_ADD | KQ_EV_ONESHOT))
                        else:
                            event.append(select.kevent(fileno,
                                                filter=select.KQ_FILTER_READ,
                                                flags=select.KQ_EV_ADD))
                        self._kqueue.control(event, 0, 0)

            if hasattr(select, 'epoll'):
                for fileno, event in self._epoll.poll(timeout=1):
                    if fileno in self._servers:
                        server = self._servers[fileno]
                        server.handle_connection()
                    else:
                        if event & select.EPOLLIN:
                            try:
                                con = self._connections[fileno]
                                con._in()
                            except Exception as e:
                                con.close()
                                continue
                            if event & select.EPOLLOUT:
                                try:
                                    con = self._connections[fileno]
                                    con._out()
                                except Exception as e:
                                    con.close()
                                    continue
                            if event & (select.EPOLLHUP | select.EPOLLERR):
                                try:
                                    con = self._connections[fileno]
                                    con.close()
                                    continue
                                except:
                                    pass
            elif hasattr(select, 'kqueue'):
                for event in self._kqueue.control(None, 1):
                    fileno = event.ident
                    if fileno in self._servers:
                        server = self._servers[fileno]
                        server.handle_connection()
                    else:
                        if event.filter == select.KQ_FILTER_READ:
                            try:
                                con = self._connections[fileno]
                                con._in()
                            except Exception as e:  # noqa
                                con.close()
                                continue
                            if event.filter == select.KQ_FILTER_WRITE:
                                try:
                                    con = self._connections[fileno]
                                    con._out()
                                except Exception as e:  # noqa
                                    con.close()
                                    continue
                            if event.flags & select.KQ_EV_EOF:
                                try:
                                    con = self._connections[fileno]
                                    con.close()
                                    continue
                                except:
                                    pass
        else:
            # not using  epoll or kqueue
            n_connections = len(self._connections)
            if self._connections_found != n_connections:
                logger.debug("lib/connection.py poll() for len(self._connections)={}".format(n_connections))
                self._connections_found = n_connections

            watched = self._waitobj.get_watched()
            nwatched = len(watched)
            logger.debug("iowait in alpha status with {} watched connections".format(nwatched))
            events = self._waitobj.wait()
            nevents = len(events)
            logger.debug("iowait reports {} events".format(nevents))
            for fileno, read, write in events:
                logger.debug("event for fileno={}, read={}, write={}".format(fileno, read, write))
                if fileno in self._servers:
                    server = self._servers[fileno]
                    server.handle_connection()
                else:
                    logger.debug("fileno {} not in self._servers".format(fileno))
                    if read:
                        try:
                            con = self._connections[fileno]
                            con._in()
                        except Exception as e:  # noqa
                            con.close()
                            continue
                        if write:
                            try:
                                con = self._connections[fileno]
                                con._out()
                            except Exception as e:  # noqa
                                con.close()
                                continue


    def close(self):
        if -1 in self._connections:
            logger.error("Connections.close() tried to close a filenumber == -1")

        try:
            for fileno in self._connections:
                try:
                    self._connections[fileno].close()
                except:
                    pass
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
        self._deprecated_warning('lib.network.Tcp_server() class')

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
        except IndexError:  # buffer empty
            return
        except socket.error:
            self.outbuffer.append(frame)
        except Exception as e:  # noqa
            logger.exception("{}: {}".format(self._name, e))
            self.close()
        finally:
            if self._close_after_send:
                logger.debug("close after send")
                self.close()
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
        self._deprecated_warning('lib.network.Tcp_client() class')

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
            # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
