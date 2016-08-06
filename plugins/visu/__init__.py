#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
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

import base64
import datetime
import hashlib
import json
import logging
import struct
import ssl
import struct
import threading

import lib.connection

logger = logging.getLogger()


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return int(obj.total_seconds())
        return json.JSONEncoder.default(self, obj)


class WebSocket(lib.connection.Server):
    
    def __init__(self, smarthome, visu_dir=False, generator_dir=False, ip='0.0.0.0', port=2424, tls='no', smartvisu_dir=False, acl='ro'):
        lib.connection.Server.__init__(self, ip, port)
        self._sh = smarthome
        self.__acl = acl
        smarthome.add_event_listener(['log'], self._send_event)
        self.clients = []
        self.visu_items = {}
        self.visu_logics = {}
        if tls == 'no':
            self.tls = False
        else:
            self.tls = True
        self.tls_crt = '/usr/local/smarthome/etc/home.crt'
        self.tls_key = '/usr/local/smarthome/etc/home.key'
        self.tls_ca = '/usr/local/smarthome/etc/ca.crt'
        self.generator_dir = visu_dir
        if generator_dir:  # transition feature
            self.generator_dir = generator_dir
        self.smartvisu_dir = smartvisu_dir
        logger.warning("")
        logger.warning("+============================================================================+")
        logger.warning("! The VISU plugin is deprecated                                              !")
        logger.warning("! - Please switch to the VISU_WEBSOCKET and VISU_SMARTVISU plugins           !")
        logger.warning("! - The old VISU plugin will be removed in the upcoming smarthomeNG v1.3     !")
        logger.warning("!                                                                            !")
        logger.warning("! Please read:                                                               !")
        logger.warning("!   https://github.com/smarthomeNG/smarthome/wiki/Visu_Unterstützung_in_v1.2 !")
        logger.warning("+============================================================================+")
        logger.warning("")


    def _smartvisu_pages(self, directory):
        from . import smartvisu
        smartvisu.pages(self._sh, directory)

    def _generate_pages(self, directory):
        from . import generator
        header_file = directory + '/tpl/header.html'
        footer_file = directory + '/tpl/footer.html'
        try:
            with open(header_file, 'r') as f:
                header = f.read()
        except IOError:
            logger.error("Could not find header file: {0}".format(header_file))
            return
        try:
            with open(footer_file, 'r') as f:
                footer = f.read()
        except IOError:
            logger.error("Could not find footer file: {0}".format(footer_file))
            return
        index = header.replace(': ', '').replace('TITLE', '')
        index += '<div data-role="page" id="index">\n'
        index += '    <div data-role="header"><h3>SmartHome</h3></div>\n'
        index += '    <div data-role="content">\n\n'
        index += '<ul data-role="listview" data-inset="true">\n'
        for item in self._sh:
            html = generator.return_tree(self._sh, item)
            item_file = "/gen/{0}.html".format(item.id())
            if 'data-sh' in html or 'data-rrd' in html:
                index += '<li><a href="{0}" data-ajax="false">{1}</a></li>\n'.format(item_file, item)
                page = header.replace('TITLE', str(item))
                page += '<div data-role="page" id="{0}">\n'.format(item.id())
                page += '    <div data-role="header"><h3>{0}</h3></div>\n'.format(item)
                page += '    <div data-role="content">\n\n'
                page += html
                page += footer
                with open(directory + item_file, 'w') as f:
                    f.write(page)
        index += '</ul>\n' + footer
        with open(directory + '/gen/index.html', 'w') as f:
            f.write(index)

    def handle_connection(self):
        sock, address = self.accept()
        if sock is None:
            return
        if self.tls:
            try:
                # cert_reqs=ssl.CERT_REQUIRED
                sock = ssl.wrap_socket(sock, server_side=True, cert_reqs=ssl.CERT_OPTIONAL, certfile=self.tls_crt, ca_certs=self.tls_ca, keyfile=self.tls_key, ssl_version=ssl.PROTOCOL_TLSv1)
                logger.debug('Client cert: {0}'.format(sock.getpeercert()))
                logger.debug('Cipher: {0}'.format(sock.cipher()))
#               print ssl.OPENSSL_VERSION
            except Exception as e:
                logger.exception(e)
                return
        client = WebSocketHandler(self._sh, self, sock, address, self.visu_items, self.visu_logics)
        self.clients.append(client)

    def run(self):
        self.alive = True
        if self.generator_dir:
            self._generate_pages(self.generator_dir)
        if self.smartvisu_dir:
            self._smartvisu_pages(self.smartvisu_dir)
        self._sh.scheduler.add('series', self._update_series, cycle=10, prio=5)

    def stop(self):
        self.alive = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.close()

    def parse_item(self, item):
        acl = self.__acl
        if 'visu_acl' in item.conf:
            if item.conf['visu_acl'] in ('yes', 'rw'):
                acl = 'rw'
            elif item.conf['visu_acl'] in ('deny', 'no'):
                return
            else:
                acl = 'ro'
        self.visu_items[item.id()] = {'acl': acl, 'item': item}
        return self.update_item

    def parse_logic(self, logic):
        if hasattr(logic, 'visu_acl'):
            self.visu_logics[logic.name] = logic

    def update_item(self, item, caller=None, source=None, dest=None):
        data = {'cmd': 'item', 'items': [[item.id(), item()]]}
        for client in list(self.clients):
            try:
                client.update(item.id(), data, source)
            except:
                pass

    def remove_client(self, client):
        self.clients.remove(client)

    def _send_event(self, event, data):
        for client in list(self.clients):
            try:
                client.send_event(event, data)
            except:
                pass

    def _update_series(self):
        for client in list(self.clients):
            try:
                client.update_series()
            except:
                pass

    def dialog(self, header, content):
        for client in list(self.clients):
            try:
                client.json_send({'cmd': 'dialog', 'header': header, 'content': content})
            except:
                pass

    def url(self, url):
        for client in list(self.clients):
            try:
                client.json_send({'cmd': 'url', 'url': url})
            except:
                pass


class WebSocketHandler(lib.connection.Stream):

    def __init__(self, smarthome, dispatcher, sock, addr, items, logics):
        lib.connection.Stream.__init__(self, sock, addr)
        self.terminator = b"\r\n\r\n"
        self._sh = smarthome
        self._dp = dispatcher
        self.found_terminator = self.parse_header
        self.addr = addr
        self.header = {}
        self.monitor = {'item': [], 'rrd': [], 'log': []}
        self.monitor_id = {'item': 'item', 'rrd': 'item', 'log': 'name'}
        self._update_series = {}
        self.items = items
        self.rrd = False
        self.log = False
        self.logs = smarthome.return_logs()
        self._series_lock = threading.Lock()
        self.logics = logics
        self.proto = 3

    def send_event(self, event, data):
        data = data.copy()  # don't filter the orignal data dict
        if event not in self.monitor:
            return
        if data[self.monitor_id[event]] in self.monitor[event]:
            data['cmd'] = event
            self.json_send(data)

    def json_send(self, data):
        logger.debug("Visu: DUMMY send to {0}: {1}".format(self.addr, data))

    def handle_close(self):
        # remove circular references
        self._dp.remove_client(self)
        try:
            del(self.json_send, self.found_terminator)
        except:
            pass

    def update(self, path, data, source):
        if path in self.monitor['item']:
            if self.addr != source:
                self.json_send(data)

    def update_series(self):
        now = self._sh.now()
        self._series_lock.acquire()
        remove = []
        for sid, series in self._update_series.items():
            if series['update'] < now:
                try:
                    reply = self.items[series['params']['item']]['item'].series(**series['params'])
                except Exception as e:
                    logger.exception("Problem updating series for {0}: {1}".format(series['params'], e))
                    remove.append(sid)
                    continue
                self._update_series[reply['sid']] = {'update': reply['update'], 'params': reply['params']}
                del(reply['update'])
                del(reply['params'])
                if reply['series'] is not None:
                    self.json_send(reply)
        for sid in remove:
            del(self._update_series[sid])
        self._series_lock.release()

    def difference(self, a, b):
        return list(set(b).difference(set(a)))

    def json_parse(self, data):
        logger.debug("{0} sent {1}".format(self.addr, repr(data)))
        try:
            data = json.loads(data)
        except Exception as e:
            logger.debug("Problem decoding {0} from {1}: {2}".format(repr(data), self.addr, e))
            return
        command = data['cmd']
        if command == 'item':
            path = data['id']
            value = data['val']
            if path in self.items:
                if not self.items[path]['acl'] == 'ro':
                    self.items[path]['item'](value, 'Visu', self.addr)
                else:
                    logger.warning("Client {0} want to update read only item: {1}".format(self.addr, path))
            else:
                logger.warning("Client {0} want to update invalid item: {1}".format(self.addr, path))
        elif command == 'monitor':
            if data['items'] == [None]:
                return
            items = []
#           for path in list(set(data['items']).difference(set(self.monitor['item']))):
            for path in list(data['items']):
                if path in self.items:
                    items.append([path, self.items[path]['item']()])
                else:
                    logger.warning("Client {0} requested invalid item: {1}".format(self.addr, path))
            self.json_send({'cmd': 'item', 'items': items})
            self.monitor['item'] = data['items']
        elif command == 'ping':
            self.json_send({'cmd': 'pong'})
        elif command == 'logic':
            if 'name' not in data or 'val' not in data:
                return
            name = data['name']
            value = data['val']
            if name in self.logics:
                logger.info("Client {0} triggerd logic {1} with '{2}'".format(self.addr, name, value))
                self.logics[name].trigger(by='Visu', value=value, source=self.addr)
            else:
                logger.warning("Client {0} requested invalid logic: {1}".format(self.addr, name))
        elif command == 'series':
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
            if path in self.items:
                if hasattr(self.items[path]['item'], 'series'):
                    try:
                        reply = self.items[path]['item'].series(series, start, end, count)
                    except Exception as e:
                        logger.exception("Problem fetching series for {0}: {1}".format(path, e))
                    else:
                        if 'update' in reply:
                            self._series_lock.acquire()
                            self._update_series[reply['sid']] = {'update': reply['update'], 'params': reply['params']}
                            self._series_lock.release()
                            del(reply['update'])
                            del(reply['params'])
                        if reply['series'] is not None:
                            self.json_send(reply)
                        else:
                            logger.info("WebSocket: no entries for series {} {}".format(path, series))
                else:
                    logger.warning("Client {0} requested invalid series: {1}.".format(self.addr, path))
        elif command == 'log':
            self.log = True
            name = data['name']
            num = 10
            if 'max' in data:
                num = int(data['max'])
            if name in self.logs:
                self.json_send({'cmd': 'log', 'name': name, 'log': self.logs[name].export(num), 'init': 'y'})
            else:
                logger.warning("Client {0} requested invalid log: {1}".format(self.addr, name))
            if name not in self.monitor['log']:
                self.monitor['log'].append(name)
        elif command == 'proto':  # protocol version
            proto = data['ver']
            if proto > self.proto:
                logger.warning("WebSocket: protocol mismatch. Update SmartHome.py")
            elif proto < self.proto:
                logger.warning("WebSocket: protocol mismatch. Update your client: {0}".format(self.addr))
            self.json_send({'cmd': 'proto', 'ver': self.proto, 'time': self._sh.now()})

    def parse_header(self, data):
        data = bytes(data)
        for line in data.splitlines():
            key, sep, value = line.partition(b': ')
            self.header[key] = value
        if b'Sec-WebSocket-Version' in self.header:
            if self.header[b'Sec-WebSocket-Version'] == b'13':
                self.rfc6455_handshake()
            else:
                self.handshake_failed()
        elif b'Sec-WebSocket-Key2' in self.header:
            self.found_terminator = self.hixie76_handshake
            self.terminator = 8
        else:
            self.handshake_failed()

    def handshake_failed(self):
        logger.debug("Handshake for {0} with the following header failed! {1}".format(self.addr, repr(self.header)))
        self.close()

    def set_bit(self, byte, bit):
        return byte | (1 << bit)

    def bit_set(self, byte, bit):
        return not 0 == (byte & (1 << bit))

    def rfc6455_handshake(self):
        logger.debug("rfc6455 Handshake")
        self.terminator = 8
        self.found_terminator = self.rfc6455_parse
        self.json_send = self.rfc6455_send
        key = self.header[b'Sec-WebSocket-Key'] + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        key = base64.b64encode(hashlib.sha1(key).digest()).decode()
        self.send('HTTP/1.1 101 Switching Protocols\r\n'.encode())
        self.send('Upgrade: websocket\r\n'.encode())
        self.send('Connection: Upgrade\r\n'.encode())
        self.send('Sec-WebSocket-Accept: {0}\r\n'.format(key).encode())
        self.send('\r\n'.encode())

    def rfc6455_parse(self, data):
        # fin = bit_set(data[0], 7)
        # rsv1 = bit_set(data[0], 6)
        # rsv2 = bit_set(data[0], 5)
        # rsv1 = bit_set(data[0], 4)
        opcode = data[0] & 0x0f
        if opcode == 8:
            logger.debug("WebSocket: closing connection to {0}.".format(self.addr))
            self.close()
            return
        header = 2
        masked = self.bit_set(data[1], 7)
        if masked:
            header += 4
        length = data[1] & 0x7f
        if length == 126:
            header += 2
            length = int.from_bytes(data[2:4], byteorder='big')
        elif length == 127:
            header += 8
            length = int.from_bytes(data[2:10], byteorder='big')
        read = header + length
        if len(data) < read:  # data too short, read more
            self.inbuffer = data + self.inbuffer
            self.terminator = read
            return
        if masked:
            key = data[header - 4:header]
            payload = bytearray(data[header:])
            for i in range(length):
                payload[i] ^= key[i % 4]
        else:
            payload = data[header:]
        self.json_parse(payload.decode())
        self.terminator = 8

    def rfc6455_send(self, data):
        data = json.dumps(data, cls=JSONEncoder, separators=(',', ':'))
        header = bytearray(2)
        header[0] = self.set_bit(header[0], 0)  # opcode text
        header[0] = self.set_bit(header[0], 7)  # final
        length = len(data)
        if length < 126:
            header[1] = length
        elif length < ((1 << 16) - 1):
            header[1] = 126
            header += bytearray(length.to_bytes(2, byteorder='big'))
        elif length < ((1 << 64) - 1):
            header[1] = 127
            header += bytearray(length.to_bytes(8, byteorder='big'))
        else:
            logger.warning("data to big: {0}".format(data))
            return
        self.send(header + data.encode())

    def hixie76_send(self, data):
        data = json.dumps(data, cls=JSONEncoder, separators=(',', ':'))
        packet = bytearray()
        packet.append(0x00)
        packet.extend(data.encode())
        packet.append(0xff)
        self.send(packet)

    def hixie76_parse(self, data):
        self.json_parse(data.decode().lstrip('\x00'))

    def hixie76_handshake(self, key3):
        logger.debug("Hixie76 Handshake")
        key1 = self.header[b'Sec-WebSocket-Key1'].decode()
        key2 = self.header[b'Sec-WebSocket-Key2'].decode()
        spaces1 = key1.count(" ")
        spaces2 = key2.count(" ")
        num1 = int("".join([c for c in key1 if c.isdigit()])) // spaces1
        num2 = int("".join([c for c in key2 if c.isdigit()])) // spaces2
        key = hashlib.md5()
        key.update(struct.pack('>II', num1, num2))
        key.update(key3)
        # send header
        self.send(b'HTTP/1.1 101 Web Socket Protocol Handshake\r\n')
        self.send(b'Upgrade: WebSocket\r\n')
        self.send(b'Connection: Upgrade\r\n')
        self.send(b"Sec-WebSocket-Origin: " + self.header[b'Origin'] + b"\r\n")
        self.send(b"Sec-WebSocket-Location: ws://" + self.header[b'Host'] + b"/\r\n\r\n")
        self.send(key.digest())
        self.found_terminator = self.hixie76_parse
        self.json_send = self.hixie76_send
        self.terminator = b"\xff"
