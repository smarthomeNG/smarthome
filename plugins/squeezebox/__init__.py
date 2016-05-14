#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  Squeezebox-Plugin for SmartHome.py.  http://mknx.github.com/smarthome/
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import urllib.request
import urllib.error
import urllib.parse
import lib.connection
import re

logger = logging.getLogger('Squeezebox')


class Squeezebox(lib.connection.Client):

    def __init__(self, smarthome, host='127.0.0.1', port=9090):
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self._sh = smarthome
        self._val = {}
        self._obj = {}
        self._init_cmds = []

    def _check_mac(self, mac):
        return re.match("[0-9a-fA-F]{2}([:][0-9a-fA-F]{2}){5}", mac)

    def _resolv_full_cmd(self, item, attr):
        # check if PlayerID wildcard is used
        if '<playerid>' in item.conf[attr]:
            # try to get from parent object
            parent_item = item.return_parent()
            if (parent_item is not None) and ('squeezebox_playerid' in parent_item.conf) and self._check_mac(parent_item.conf['squeezebox_playerid']):
                item.conf[attr] = item.conf[attr].replace('<playerid>', parent_item.conf['squeezebox_playerid'])
            else:
                logger.warning("squeezebox: could not resolve playerid for {0} from parent item {1}".format(item, parent_item))
                return None
        return item.conf[attr]

    def parse_item(self, item):
        if 'squeezebox_recv' in item.conf:
            cmd = self._resolv_full_cmd(item, 'squeezebox_recv')
            if (cmd is None):
                return None

            logger.debug("squeezebox: {0} receives updates by \"{1}\"".format(item, cmd))
            if not cmd in self._val:
                self._val[cmd] = {'items': [item], 'logics': []}
            else:
                if not item in self._val[cmd]['items']:
                    self._val[cmd]['items'].append(item)

            if ('squeezebox_init' in item.conf):
                cmd = self._resolv_full_cmd(item, 'squeezebox_init')
                if (cmd is None):
                    return None

                logger.debug("squeezebox: {0} is initialized by \"{1}\"".format(item, cmd))
                if not cmd in self._val:
                    self._val[cmd] = {'items': [item], 'logics': []}
                else:
                    if not item in self._val[cmd]['items']:
                        self._val[cmd]['items'].append(item)

            if not cmd in self._init_cmds:
                self._init_cmds.append(cmd)

        if 'squeezebox_send' in item.conf:
            cmd = self._resolv_full_cmd(item, 'squeezebox_send')
            if (cmd is None):
                return None
            logger.debug("squeezebox: {0} is send to \"{1}\"".format(item, cmd))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        if 'squeezebox_playerid' in logic.conf:
            playerid = logic.conf['squeezebox_playerid'];
            if not self._check_mac(playerid):
                logger.warning("squeezebox: invalid playerid for {0}".format(logic.name))
                return None
        else:
            playerid = 'playerid_not_set'
        if 'squeezebox_recv' in logic.conf:
            cmds = logic.conf['squeezebox_recv']
            if isinstance(cmds, str):
                cmds = [cmds, ]
            for cmd in cmds:
                cmd = cmd.replace('<playerid>', playerid)
                if not self._check_mac(cmd.split(maxsplit=1)[0]):
                    logger.warning("squeezebox: no valid playerid in \"{}\"".format(cmd))
                    continue
                logger.debug("squeezebox: {} will be triggered by \"{}\"".format(logic.name, cmd))
                if not cmd in self._val:
                    self._val[cmd] = {'items': [], 'logics': [logic]}
                else:
                    if not logic in self._val[cmd]['logics']:
                        self._val[cmd]['logics'].append(logic)
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        # be careful: as the server echoes ALL comands not using this will
        # result in a loop
        if caller != 'LMS':
            cmd = self._resolv_full_cmd(item, 'squeezebox_send').split()
            if not self._check_mac(cmd[0]):
                return
            value = item()
            if isinstance(value, bool):
                # convert to get '0'/'1' instead of 'True'/'False'
                value = int(value)

            # special handling for bool-types who need other comands or values
            # to behave intuitively
            if (len(cmd) >= 2) and not item():
                if (cmd[1] == 'play'):
                    # if 'play' was set to false, send 'stop' to allow
                    # single-item-operation
                    cmd[1] = 'stop'
                    value = 1
                if (cmd[1] == 'playlist') and (cmd[2] in ['shuffle', 'repeat']):
                    # if a boolean item of [...] was set to false, send '0' to disable the option whatsoever
                    # replace cmd[3], as there are fixed values given and
                    # filling in 'value' is pointless
                    cmd[3] = '0'
            self._send(' '.join(urllib.parse.quote(cmd_str.format(value), encoding='iso-8859-1')
                       for cmd_str in cmd))

    def _send(self, cmd):
        logger.debug("squeezebox: Sending request: {0}".format(cmd))
        self.send(bytes(cmd + '\r\n', 'utf-8'))

    def found_terminator(self, response):
        # logger.debug("squeezebox: #####################################")
        # print(type(response))
        # print(response.decode('iso-8859-1').encode('utf-8').decode('unicode-escape'))
        # print(urllib.parse.unquote(response.decode('iso-8859-1')))
        # print(urllib.parse.unquote(response.decode('unicode-escape')))
        #response = response.decode('iso-8859-1')
        # print(type(response))
        #logger.debug("squeezebox: Raw: {0}".format(response))
        data = [urllib.parse.unquote(data_str)
                for data_str in response.decode().split()]
        logger.debug("squeezebox: Got: {0}".format(data))

        try:
            if (data[0].lower() == 'listen'):
                value = int(data[1])
                if (value == 1):
                    logger.info("squeezebox: Listen-mode enabled")
                else:
                    logger.info("squeezebox: Listen-mode disabled")

            if self._check_mac(data[0]):
                if (data[1] == 'play'):
                    self._update_items_with_data([data[0], 'play', '1'])
                    self._update_items_with_data([data[0], 'stop', '0'])
                    self._update_items_with_data([data[0], 'pause', '0'])
                    # play also overrules mute
                    self._update_items_with_data(
                        [data[0], 'prefset server mute', '0'])
                    return
                elif (data[1] == 'stop'):
                    self._update_items_with_data([data[0], 'play', '0'])
                    self._update_items_with_data([data[0], 'stop', '1'])
                    self._update_items_with_data([data[0], 'pause', '0'])
                    return
                elif (data[1] == 'pause'):
                    self._send(data[0] + ' mode ?')
                    self._send(data[0] + ' mixer muting ?')
                    return
                elif (data[1] == 'mode'):
                    self._update_items_with_data(
                        [data[0], 'play', str(data[2] == 'play')])
                    self._update_items_with_data(
                        [data[0], 'stop', str(data[2] == 'stop')])
                    self._update_items_with_data(
                        [data[0], 'pause', str(data[2] == 'pause')])
                    # play also overrules mute
                    if (data[2] == 'play'):
                        self._update_items_with_data(
                            [data[0], 'prefset server mute', '0'])
                    return
                elif ((((data[1] == 'prefset') and (data[2] == 'server')) or (data[1] == 'mixer'))
                      and (data[-2] == 'volume') and data[-1].startswith('-')):
                    # make sure value is always positive - also if muted!
                    self._update_items_with_data(
                        [data[0], 'prefset server mute', '1'])
                    data[-1] = data[-1][1:]
                elif (data[1] == 'playlist'):
                    if (data[2] == 'jump') and (len(data) == 4):
                        self._update_items_with_data(
                            [data[0], 'playlist index', data[3]])
                    elif (data[2] == 'newsong'):
                        if (len(data) >= 4):
                            self._update_items_with_data(
                                [data[0], 'title', data[3]])
                        else:
                            self._send(data[0] + ' title ?')
                        if (len(data) >= 5):
                            self._update_items_with_data(
                                [data[0], 'playlist index', data[4]])
                        # trigger reading of other song fields
                        for field in ['genre', 'artist', 'album', 'duration']:
                            self._send(data[0] + ' ' + field + ' ?')
                elif (data[1] in ['genre', 'artist', 'album', 'title']) and (len(data) == 2):
                    # these fields are returned empty so update fails - append
                    # '' to allow update
                    data.append('')
                elif (data[1] in ['duration']) and (len(data) == 2):
                    # these fields are returned empty so update fails - append
                    # '0' to allow update
                    data.append('0')
            # finally check for '?'
            if (data[-1] == '?'):
                return
            self._update_items_with_data(data)
        except Exception as e:
            logger.error(
                "squeezebox: exception while parsing \'{0}\'".format(data))
            logger.error("squeezebox: exception: {}".format(e))

    def _update_items_with_data(self, data):
        cmd = ' '.join(data_str for data_str in data[:-1])
        if (cmd in self._val):
            for item in self._val[cmd]['items']:
                if re.match("[+-][0-9]+$", data[-1]) and not isinstance(item(), str):
                    data[-1] = int(data[-1]) + item()
                item(data[-1], 'LMS', self.address)
            for logic in self._val[cmd]['logics']:
                logic.trigger('squeezebox', cmd, data[-1])

    def handle_connect(self):
        self.discard_buffers()
        # enable listen-mode to get notified of changes
        self._send('listen 1')
        if self._init_cmds != []:
            if self.connected:
                logger.debug('squeezebox: init read')
                for cmd in self._init_cmds:
                    self._send(cmd + ' ?')

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.close()
