#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 Marcus Popp                               marcus@popp.mx
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

import logging
import threading
import time

logger = logging.getLogger('')

import lib.connection


class MPD():

    def __init__(self, smarthome, cycle=2):
        self._sh = smarthome
        self._mpds = []
        self._cycle = float(cycle)

    def run(self):
        self.alive = True
        while self.alive:
            for d in self._mpds:
                try:
                    d.update_status()
                except Exception as e:
                    logger.warning("exception: {0}".format(e))
            time.sleep(self._cycle)

    def stop(self):
        self.alive = False
        for d in self._mpds:
            d.close()

    def parse_item(self, item):
        if 'mpd_host' in item.conf:
            self._mpds.append(mpd(self._sh, item))


class mpd(lib.connection.Client):

    _listen_keys = ['state', 'volume', 'repeat', 'random', 'single', 'time', 'total', 'percent', 'play', 'pause', 'stop', 'song', 'playlistlength', 'nextsongid']
    _current_keys = {'title': 'Title', 'name': 'Name', 'album': 'Album', 'artist': 'Artist', 'albumartist': 'AlbumArtist', 'track': 'Track', 'disc': 'Disc', 'file': 'file'}
    _bool_keys = ['repeat', 'random', 'single', 'consume']

    def __init__(self, smarthome, item):
        if 'mpd_port' in item.conf:
            port = int(item.conf['mpd_port'])
        else:
            port = 6600
        host = item.conf['mpd_host']
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self._sh = smarthome
        self._cmd_lock = threading.Lock()
        self._reply_lock = threading.Condition()
        self._reply = {}
        self._items = {}
        self.terminator = b'\n'
        self.found_terminator = self.handshake
        for child in self._sh.find_children(item, 'mpd_listen'):
            listen_to = child.conf['mpd_listen']
            if listen_to in self._listen_keys:
                self._items[listen_to] = child
            if listen_to in self._current_keys:
                self._items[self._current_keys[listen_to]] = child
        for child in self._sh.find_children(item, 'mpd_send'):
            send_to = child.conf['mpd_send']
            if send_to in self._bool_keys:
                child.add_method_trigger(self._send_bool)
            elif send_to == 'volume':
                child.add_method_trigger(self._send_volume)
            elif send_to == 'value':
                child.add_method_trigger(self._send_value)
            else:
                child.add_method_trigger(self._send_command)
        for child in self._sh.find_children(item, 'mpd_file'):
            child.add_method_trigger(self._play_file)
        # adding item methods
        item.command = self.command
        item.play_file = self.play_file
        item.add_file = self.add_file

    def command(self, command, wait=True):
        return self._send(command, wait)

    def play_file(self, url):
        play = self._parse_url(url)
        if play == []:
            return
        self._send('clear', False)
        for url in play:
            self._send("add {0}".format(url), False)
        self._send('play', False)

    def add_file(self, url):
        play = self._parse_url(url)
        if play != []:
            self._send("add {0}".format(play[0]), False)

    def _play_file(self, item, caller=None, source=None, dest=None):
        if caller != 'MPD':
            if item.conf['mpd_file'] == 'value':
                self.play_file(item())
            else:
                self.play_file(item.conf['mpd_file'])

    def _parse_url(self, url):
        name, sep, ext = url.rpartition('.')
        ext = ext.lower()
        play = []
        if ext in ('m3u', 'pls'):
            content = self._sh.tools.fetch_url(url, timeout=4)
            if content is False:
                return play
            content = content.decode()
            if ext == 'pls':
                for line in content.splitlines():
                    if line.startswith('File'):
                        num, tmp, url = line.partition('=')
                        play.append(url)
            else:
                for line in content.splitlines():
                    if line.startswith('http://'):
                        play.append(line)
        else:
            play.append(url)
        return play

    def _send_volume(self, item, caller=None, source=None, dest=None):
        if caller != 'MPD':
            self._send('setvol {0}'.format(int(item())), False)

    def _send_bool(self, item, caller=None, source=None, dest=None):
        if caller != 'MPD':
            key = item.conf['mpd_send']
            self._send("{0} {1}".format(key, int(item())), False)

    def _send_command(self, item, caller=None, source=None, dest=None):
        if caller != 'MPD':
            self._send("{0}".format(item.conf['mpd_send']), False)

    def _send_value(self, item, caller=None, source=None, dest=None):
        if caller != 'MPD':
            self._send("{0}".format(item()), False)

    def _send(self, command, wait=True):
        self._cmd_lock.acquire()
        self._reply = {}
        self._reply_lock.acquire()
        self.send((command + '\n').encode())
        if wait:
            self._reply_lock.wait(1)
        self._reply_lock.release()
        reply = self._reply
        self._reply = {}
        self._cmd_lock.release()
        return reply

    def update_status(self):
        if not self.connected:
            return
        status = self._send('status')
        if 'state' not in status:
            return
        status.update({'Album': '', 'Name': '', 'Artist': '', 'AlbumArtist': '', 'Disc': '', 'Track': '', 'Title': '', 'play': False, 'pause': False, 'stop': False})
        status[status['state']] = True  # set only the current state to True
        if 'time' in status:
            status['time'], sep, status['total'] = status['time'].partition(':')
            if 'percent' in self._items:
                if status['total'] != '0':
                    status['percent'] = int(int(status['time']) / (int(status['total']) / 100.0))
                else:
                    status['percent'] = 0
        else:
            status.update({'time': 0, 'total': 0, 'percent': 0})
        if status['state'] != 'stop':
            status.update(self._send('currentsong'))  # append current song information to status
        for attr in self._items:
            if attr in status:
                try:
                    self._items[attr](str(status[attr]), 'MPD')
                except Exception as e:
                    logger.warning("Error processing attr '{0}' value '{1}'".format(attr, str(status[attr])))
                    logger.warning("Exception: {0}".format(e))

    def handle_connect(self):
        self.found_terminator = self.handshake

    def handshake(self, data):
        data = data.decode()
        if data.startswith('OK MPD'):
            self.found_terminator = self.parse_reply

    def parse_reply(self, data):
        data = data.decode()
        if data.startswith('OK'):
            self._reply_lock.acquire()
            self._reply_lock.notify()
            self._reply_lock.release()
        elif data.startswith('ACK'):
            logger.warning(data)
        else:
            key, sep, value = data.partition(': ')
            self._reply[key] = value
