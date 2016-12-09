#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#

import logging

import lib.connection

logger = logging.getLogger('')

REQ_DELIMITER = b'\r'
RESP_DELIMITER = b'\r\n'


class Russound(lib.connection.Client):

    def __init__(self, smarthome, host, port=9621):
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.terminator = RESP_DELIMITER
        self._sh = smarthome
        self.params = {}
        self.sources = {}

    def parse_item(self, item):
#        if 'rus_src' in item.conf:
#            s = int(item.conf['rus_src'])
#            self.sources[s] = {'s': s, 'item':item}
#            logger.debug("Source {0} added".format(s))
#            return None

        if 'rus_path' in item.conf:
            path = item.conf['rus_path']
            parts = path.split('.', 2)

            if len(parts) is not 3:
                logger.warning(
                    "Invalid Russound path with value {0}, format should be 'c.z.p' c = controller, z = zone, p = parameter name.".format(path))
                return None

            c = parts[0]
            z = parts[1]
            param = parts[2]

        else:
            if 'rus_controller' in item.conf:
                c = item.conf['rus_controller']
                path = c + '.'
            else:
                return None

            if 'rus_zone' in item.conf:
                z = item.conf['rus_zone']
                path += z + '.'
            else:
                logger.warning(
                    "No zone specified for controller {0} in config of item {1}".format(c, item))
                return None

            if 'rus_parameter' in item.conf:
                param = item.conf['rus_parameter']
                path += param
            else:
                logger.warning(
                    "No parameter specified for zone {0} on controller {1} in config of item {2}".format(z, c, item))
                return None

            if param == 'relativevolume':
                item._enforce_updates = True

            item.conf['rus_path'] = path

        param = param.lower()
        self.params[path] = {'c':
                             int(c), 'z': int(z), 'param': param, 'item': item}
        logger.debug("Parameter {0} with path {1} added".format(item, path))

        return self.update_item

    def parse_logic(self, logic):
        pass

    def _restrict(self, val, minval, maxval):
        if val < minval:
            return minval
        if val > maxval:
            return maxval
        return val

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Russound':
            path = item.conf['rus_path']
            p = self.params[path]
            cmd = p['param']
            c = p['c']
            z = p['z']

            if cmd == 'bass':
                self.send_set(c, z, cmd, self._restrict(item(), -10, 10))
            elif cmd == 'treble':
                self.send_set(c, z, cmd, self._restrict(item(), -10, 10))
            elif cmd == 'balance':
                self.send_set(c, z, cmd, self._restrict(item(), -10, 10))
            elif cmd == 'loudness':
                self.send_set(c, z, cmd, 'ON' if item() else 'OFF')
            elif cmd == 'turnonvolume':
                self.send_set(c, z, cmd, self._restrict(item(), 0, 50))
            elif cmd == 'status':
                self.send_event(c, z, 'ZoneOn' if item() else 'ZoneOff')
            elif cmd == 'partymode':
                self.send_event(c, z, cmd, item().lower())
            elif cmd == 'donotdisturb':
                self.send_event(c, z, cmd, 'on' if item() else 'off')
            elif cmd == 'volume':
                self.send_event(c, z, 'KeyPress', 'Volume',
                                self._restrict(item(), 0, 50))
            elif cmd == 'currentsource':
                self.send_event(c, z, 'SelectSource', item())
            elif cmd == 'relativevolume':
                self.send_event(c, z, 'KeyPress',
                                'VolumeUp' if item() else 'VolumeDown')
            elif cmd == 'name':
                return
            else:
                self.key_release(c, z, cmd)

    def send_set(self, c, z, cmd, value):
        self._send_cmd(
            'SET C[{0}].Z[{1}].{2}="{3}"\r'.format(c, z, cmd, value))

    def send_event(self, c, z, cmd, value1=None, value2=None):
        if value1 is None and value2 is None:
            self._send_cmd('EVENT C[{0}].Z[{1}]!{2}\r'.format(c, z, cmd))
        elif value2 is None:
            self._send_cmd(
                'EVENT C[{0}].Z[{1}]!{2} {3}\r'.format(c, z, cmd, value1))
        else:
            self._send_cmd(
                'EVENT C[{0}].Z[{1}]!{2} {3} {4}\r'.format(c, z, cmd, value1, value2))

    def key_release(self, c, z, key_code):
        self.send_event(c, z, 'KeyRelease', key_code)

    def key_hold(self, c, z, key_code, hold_time):
        self.send_event(c, z, 'KeyHold', key_code, hold_time)

    def _watch_zone(self, controller, zone):
        self._send_cmd('WATCH C[{0}].Z[{1}] ON\r'.format(controller, zone))

    def _watch_source(self, source):
        self._send_cmd('WATCH S[{0}] ON\r'.format(source))

    def _watch_system(self):
        self._send_cmd('WATCH System ON\r')

    def _send_cmd(self, cmd):
        logger.debug("Sending request: {0}".format(cmd))

        # if connection is closed we don't wait for sh.con to reopen it
        # instead we reconnect immediatly
        if not self.connected:
            self.connect()

        self.send(cmd.encode())

    def found_terminator(self, resp):
        resp = resp.decode()
        try:
            logger.debug("Parse response: {0}".format(resp))
            if resp[0] == 'S':
                return
            if resp[0] == 'E':
                logger.debug("Received response error: {0}".format(resp))
            elif resp[0] == 'N':
                resp = resp[2:]

                if resp[0] == 'C':
                    resp = resp.split('.', 2)
                    c = int(resp[0][2])
                    z = int(resp[1][2])
                    resp = resp[2]
                    cmd = resp.split('=')[0].lower()
                    value = resp.split('"')[1]

                    path = '{0}.{1}.{2}'.format(c, z, cmd)
                    if path in list(self.params.keys()):
                        self.params[path]['item'](
                            self._decode(cmd, value), 'Russound')
                elif resp.startswith('System.status'):
                    return
                elif resp[0] == 'S':
                    resp = resp.split('.', 1)
#                   s = int(resp[0][2])
                    resp = resp[1]
                    cmd = resp.split('=')[0].lower()
                    value = resp.split('"')[1]

#                    if s in self.sources.keys():
#                        for child in self.sources[s]['item'].return_children():
#                            if str(child).lower() == cmd.lower():
#                                child(unicode(value, 'utf-8'), 'Russound')
                    return
        except Exception as e:
            logger.error(e)

    def _decode(self, cmd, value):
        cmd = cmd.lower()

        if cmd == 'bass' or cmd == 'treble' or cmd == 'balance' or cmd == 'turnonvolume' or cmd == 'volume':
            return int(value)
        elif cmd == 'loudness' or cmd == 'status' or cmd == 'mute':
            return value == 'ON'
        elif cmd == 'partymode' or cmd == 'donotdisturb':
            return value.lower()
        elif cmd == 'currentsource':
            return value
        elif cmd == 'name':
            return str(value, 'utf-8')

    def handle_connect(self):
        self.discard_buffers()
        self.terminator = RESP_DELIMITER
        self._watch_system()

        zones = []
        for path in self.params:
            p = self.params[path]
            key = '{0}.{1}'.format(p['c'], p['z'])
            if not key in zones:
                zones.append(key)
                self._watch_zone(p['c'], p['z'])

        for s in self.sources:
            self._watch_source(s)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.close()
