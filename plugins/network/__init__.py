#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2014 Marcus Popp                         marcus@popp.mx
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
import urllib.request
import urllib.parse
import urllib.error
import lib.connection

logger = logging.getLogger('')


class TCPHandler(lib.connection.Stream):

    def __init__(self, parser, dest, sock, source):
        lib.connection.Stream.__init__(self, sock, source)
        self.terminator = b'\n'
        self.parser = parser
        self.dest = dest
        self.source = source

    def found_terminator(self, data):
        self.parser(self.source, self.dest, data.decode().strip())
        self.close()


class TCPDispatcher(lib.connection.Server):

    def __init__(self, parser, ip, port):
        lib.connection.Server.__init__(self, ip, port)
        self.parser = parser
        self.dest = 'tcp:' + ip + ':' + port
        self.connect()

    def handle_connection(self):
        sock, address = self.accept()
        if sock is None:
            return
        TCPHandler(self.parser, self.dest, sock, address)


class HTTPHandler(lib.connection.Stream):

    def __init__(self, parser, dest, sock, source):
        lib.connection.Stream.__init__(self, sock, source)
        self.terminator = b"\r\n\r\n"
        self.parser = parser
        self.dest = dest
        self.source = source

    def found_terminator(self, data):
        for line in data.decode().splitlines():
            if line.startswith('GET'):
                request = line.split(' ')[1].strip('/')
                if self.parser(self.source, self.dest, urllib.parse.unquote(request)) is not False:
                    self.send(b'HTTP/1.1 200 OK\r\n\r\n', close=True)
                else:
                    self.send(b'HTTP/1.1 400 Bad Request\r\n\r\n', close=True)
                break


class HTTPDispatcher(lib.connection.Server):

    def __init__(self, parser, ip, port):
        lib.connection.Server.__init__(self, ip, port)
        self.parser = parser
        self.dest = 'http:' + ip + ':' + port
        self.connect()

    def handle_connection(self):
        sock, address = self.accept()
        if sock is None:
            return
        HTTPHandler(self.parser, self.dest, sock, address)


class UDPDispatcher(lib.connection.Server):

    def __init__(self, parser, ip, port):
        lib.connection.Server.__init__(self, ip, port, proto='UDP')
        self.dest = 'udp:' + ip + ':' + port
        self.parser = parser
        self.connect()

    def handle_connection(self):
        try:
            data, addr = self.socket.recvfrom(4096)
            ip = addr[0]
            addr = "{}:{}".format(addr[0], addr[1])
            logger.debug("{}: incoming connection from {} to {}".format(self._name, addr, self.address))
        except Exception as e:
            logger.exception("{}: {}".format(self._name, e))
            return
        self.parser(ip, self.dest, data.decode().strip())


class Network():

    generic_listeners = {}
    special_listeners = {}
    input_seperator = '|'
    socket_warning = 10
    socket_warning = 2

    def __init__(self, smarthome, ip='0.0.0.0', port='2727', udp='no', tcp='no', http='no', udp_acl='*', tcp_acl='*', http_acl='*'):
        self._sh = smarthome
        self.tcp_acl = self.parse_acl(tcp_acl)
        self.udp_acl = self.parse_acl(udp_acl)
        self.http_acl = self.parse_acl(http_acl)
        if tcp == 'yes':
            self.add_listener('tcp', ip, port, tcp_acl, generic=True)
        if udp == 'yes':
            self.add_listener('udp', ip, port, udp_acl, generic=True)
        if http != 'no':
            self.add_listener('http', ip, http, http_acl, generic=True)

    def udp(self, host, port, data):
        try:
            family, type, proto, canonname, sockaddr = socket.getaddrinfo(host, port)[0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data.encode(), (sockaddr[0], sockaddr[1]))
            sock.close()
            del(sock)
        except Exception as e:
            logger.warning("UDP: Problem sending data to {}:{}: {}".format(host, port, e))
            pass
        else:
            logger.debug("UDP: Sending data to {}:{}: {}".format(host, port, data))

    def add_listener(self, proto, ip, port, acl='*', generic=False):
        dest = proto + ':' + ip + ':' + port
        logger.debug("Adding listener on: {}".format(dest))
        if proto == 'tcp':
            dispatcher = TCPDispatcher(self.parse_input, ip, port)
        elif proto == 'udp':
            dispatcher = UDPDispatcher(self.parse_input, ip, port)
        elif proto == 'http':
            dispatcher = HTTPDispatcher(self.parse_input, ip, port)
        else:
            return
        if not dispatcher.connected:
            return False
        acl = self.parse_acl(acl)
        if generic:
            self.generic_listeners[dest] = {'items': {}, 'logics': {}, 'acl': acl}
        else:
            self.special_listeners[dest] = {'items': {}, 'logics': {}, 'acl': acl}
        return True

    def parse_acl(self, acl):
        if acl == '*':
            return False
        if isinstance(acl, str):
            return [acl]
        return acl

    def parse_input(self, source, dest, data):
        if dest in self.generic_listeners:
            inp = data.split(self.input_seperator, 2)  # max 3 elements
            if len(inp) < 3:
                logger.info("Ignoring input {}. Format not recognized.".format(data))
                return False
            typ, name, value = inp
            proto = dest.split(':')[0].upper()
            source, __, port = source.partition(':')
            gacl = self.generic_listeners[dest]['acl']
            if typ == 'item':
                if name not in self.generic_listeners[dest]['items']:
                    logger.error("Item '{}' not available in the generic listener.".format(name))
                    return False
                iacl = self.generic_listeners[dest]['items'][name]['acl']
                if iacl:
                    if source not in iacl:
                        logger.error("Item '{}' acl doesn't permit updates from {}.".format(name, source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("Generic network acl doesn't permit updates from {}.".format(source))
                        return False
                item = self.generic_listeners[dest]['items'][name]['item']
                item(value, proto, source)

            elif typ == 'logic':
                if name not in self.generic_listeners[dest]['logics']:
                    logger.error("Logic '{}' not available in the generic listener.".format(name))
                    return False
                lacl = self.generic_listeners[dest]['logics'][name]['acl']
                if lacl:
                    if source not in lacl:
                        logger.error("Logic '{}' acl doesn't permit triggering from {}.".format(name, source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("Generic network acl doesn't permit triggering from {}.".format(source))
                        return False
                logic = self.generic_listeners[dest]['logics'][name]['logic']
                logic.trigger(proto, source, value)

            elif typ == 'log':
                if gacl:
                    if source not in gacl:
                        logger.error("Generic network acl doesn't permit log entries from {}".format(source))
                        return False
                if name == 'info':
                    logger.info(value)
                elif name == 'warning':
                    logger.warning(value)
                elif name == 'error':
                    logger.error(value)
                else:
                    logger.warning("Unknown logging priority '{}'. Data: '{}'".format(name, data))
            else:
                logger.error("Unsupporter key element {}. Data: {}".format(typ, data))
                return False
        elif dest in self.special_listeners:
            proto, t1, t2 = dest.partition(':')
            if proto == 'udp':
                gacl = self.udp_acl
            elif proto == 'tcp':
                gacl = self.tcp_acl
            else:
                return
            for entry in self.special_listeners[dest]['logics']:
                lacl = self.special_listeners[dest]['logics'][entry]['acl']
                logic = self.special_listeners[dest]['logics'][entry]['logic']
                if lacl:
                    if source not in lacl:
                        logger.error("Logic '{}' acl doesn't permit triggering from {}.".format(logic.name, source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("Generic network acl doesn't permit triggering from {}.".format(source))
                        return False
                logic.trigger('network', source, data)
            for entry in self.special_listeners[dest]['items']:
                lacl = self.special_listeners[dest]['items'][entry]['acl']
                item = self.special_listeners[dest]['items'][entry]['item']
                if lacl:
                    if source not in lacl:
                        logger.error("Item {0} acl doesn't permit triggering from {1}.".format(item.id(), source))
                        return False
                elif gacl:
                    if source not in gacl:
                        logger.error("Generic network acl doesn't permit triggering from {0}.".format(source))
                        return False
                item(data, 'network', source)
        else:
            logger.error("Destination {}, not in listeners!".format(dest))
            return False
        return True

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_logic(self, logic):
        self.parse_obj(logic, 'logic')

    def parse_item(self, item):
        self.parse_obj(item, 'item')
        if 'nw_udp_send' in item.conf:
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if 'nw_udp_send' in item.conf:
            addr, __, message = item.conf['nw_udp_send'].partition('=')
            if message is None:
                message = str(item())
            else:
                message = message.replace('itemvalue', str(item()))
            host, __, port = addr.partition(':')
            self.udp(host, port, message)

    def parse_obj(self, obj, obj_type):
        # nw_acl, nw_udp, nw_tcp
        if obj_type == 'item':
            oid = obj.id()
        elif obj_type == 'logic':
            oid = obj.id()
        else:
            return

        if 'nw_acl' in obj.conf:
            acl = obj.conf['nw_acl']
        else:
            acl = False

        if 'nw' in obj.conf:  # adding object to generic listeners
            if self._sh.string2bool(obj.conf['nw']):
                for dest in self.generic_listeners:
                    self.generic_listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}

        if 'nw_udp_listen' in obj.conf:
            ip, sep, port = obj.conf['nw_udp_listen'].rpartition(':')
            if not ip:
                ip = '0.0.0.0'
            dest = 'udp:' + ip + ':' + port
            if dest not in self.special_listeners:
                if self.add_listener('udp', ip, port):
                    self.special_listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}
                else:
                    logger.warning("Could not add listener {} for {}".format(dest, oid))
            else:
                self.special_listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}

        if 'nw_tcp_listen' in obj.conf:
            ip, sep, port = obj.conf['nw_tcp_listen'].rpartition(':')
            if not ip:
                ip = '0.0.0.0'
            dest = 'tcp:' + ip + ':' + port
            if dest not in self.special_listeners:
                if self.add_listener('tcp', ip, port):
                    self.special_listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}
                else:
                    logger.warning("Could not add listener {} for {}".format(dest, oid))
            else:
                self.special_listeners[dest][obj_type + 's'][oid] = {obj_type: obj, 'acl': acl}
