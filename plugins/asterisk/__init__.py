#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
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

import threading
import logging
import datetime

import lib.connection
import lib.log

logger = logging.getLogger('')


class Asterisk(lib.connection.Client):

    def __init__(self, smarthome, username, password, host='127.0.0.1', port=5038):
        lib.connection.Client.__init__(self, host, port, monitor=True)
        self.terminator = b'\r\n\r\n'
        self._init_cmd = {'Action': 'Login', 'Username': username, 'Secret': password, 'Events': 'call,user,cdr'}
        self._sh = smarthome
        self._reply_lock = threading.Condition()
        self._cmd_lock = threading.Lock()
        self._aid = 0
        self._devices = {}
        self._mailboxes = {}
        self._trigger_logics = {}
        self._log_in = lib.log.Log(smarthome, 'env.asterisk.log.in', ['start', 'name', 'number', 'duration', 'direction'])

    def _command(self, d, reply=True):
        if not self.connected:
            return
        self._cmd_lock.acquire()
        if self._aid > 100:
            self._aid = 0
        self._aid += 1
        self._reply = None
        self._error = False
        if reply:
            d['ActionID'] = self._aid
        #logger.debug("Request {0} - sending: {1}".format(self._aid, d))
        self._reply_lock.acquire()
        self.send(('\r\n'.join(['{0}: {1}'.format(key, value) for (key, value) in list(d.items())]) + '\r\n\r\n').encode())
        if reply:
            self._reply_lock.wait(2)
        self._reply_lock.release()
        reply = self._reply
        #logger.debug("Request {0} - reply: {1}".format(self._aid, reply))
        error = self._error
        self._cmd_lock.release()
        if error:
            raise Exception(error)
        return reply

    def db_read(self, key):
        fam, sep, key = key.partition('/')
        try:
            return self._command({'Action': 'DBGet', 'Family': fam, 'Key': key})
        except Exception:
            logger.warning("Asterisk: Problem reading {0}/{1}.".format(fam, key))

    def db_write(self, key, value):
        fam, sep, key = key.partition('/')
        try:
            return self._command({'Action': 'DBPut', 'Family': fam, 'Key': key, 'Val': value})
        except Exception as e:
            logger.warning("Asterisk: Problem updating {0}/{1} to {2}: {3}.".format(fam, key, value, e))

    def mailbox_count(self, mailbox, context='default'):
        try:
            return self._command({'Action': 'MailboxCount', 'Mailbox': mailbox + '@' + context})
        except Exception as e:
            logger.warning("Asterisk: Problem reading mailbox count {0}@{1}: {2}.".format(mailbox, context, e))
            return (0, 0)

    def call(self, source, dest, context, callerid=None):
        cmd = {'Action': 'Originate', 'Channel': source, 'Exten': dest, 'Context': context, 'Priority': '1', 'Async': 'true'}
        if callerid:
            cmd['Callerid'] = callerid
        try:
            self._command(cmd, reply=False)
        except Exception as e:
            logger.warning("Asterisk: Problem calling {0} from {1} with context {2}: {3}.".format(dest, source, context, e))

    def hangup(self, hang):
        active_channels = self._command({'Action': 'CoreShowChannels'})
        if active_channels is None:
            active_channels = []
        for channel in active_channels:
            device = self._get_device(channel)
            if device == hang:
                self._command({'Action': 'Hangup', 'Channel': channel}, reply=False)

    def found_terminator(self, data):
        data = data.decode()
        event = {}
        for line in data.splitlines():
            key, sep, value = line.partition(': ')
            event[key] = value
        if 'ActionID' in event:
            aid = int(event['ActionID'])
            if aid != self._aid:
                return  # old request
            if 'Response' in event:
                if event['Response'] == 'Error':
                    self._error = event['Message']
                    self._reply_lock.acquire()
                    self._reply_lock.notify()
                    self._reply_lock.release()
                elif event['Message'] == 'Updated database successfully':
                    self._reply_lock.acquire()
                    self._reply_lock.notify()
                    self._reply_lock.release()
                elif event['Message'] == 'Mailbox Message Count':
                    self._reply = [int(event['OldMessages']), int(event['NewMessages'])]
                    self._reply_lock.acquire()
                    self._reply_lock.notify()
                    self._reply_lock.release()
        if not 'Event' in event:  # ignore
            return
        if event['Event'] == 'Newchannel':  # or data.startswith('Event: Newstate') ) and 'ChannelStateDesc: Ring' in data:
            device = self._get_device(event['Channel'])
            if device in self._devices:
                self._devices[device](True, 'Asterisk')
        elif event['Event'] == 'Hangup':
            self._sh.scheduler.trigger('Ast.UpDev', self._update_devices, by='Asterisk')
        elif event['Event'] == 'CoreShowChannel':
            if self._reply is None:
                self._reply = [event['Channel']]
            else:
                self._reply.append(event['Channel'])
        elif event['Event'] == 'CoreShowChannelsComplete':
            self._reply_lock.acquire()
            self._reply_lock.notify()
            self._reply_lock.release()
        elif event['Event'] == 'UserEvent':
            if 'Source' in event:
                source = event['Source']
            else:
                source = None
            if 'Value' in data:
                value = event['Value']
            else:
                value = None
            if 'Destination' in data:
                destination = event['Destination']
            else:
                destination = None
            if event['UserEvent'] in self._trigger_logics:
                for logic in self._trigger_logics[event['UserEvent']]:
                    logic.trigger('Asterisk', source, value, destination)
        elif event['Event'] == 'DBGetResponse':
            self._reply = event['Val']
            self._reply_lock.acquire()
            self._reply_lock.notify()
            self._reply_lock.release()
        elif event['Event'] == 'MessageWaiting':
            mb = event['Mailbox'].split('@')[0]
            if mb in self._mailboxes:
                if 'New' in event:
                    self._mailboxes[mb](event['New'])
                else:
                    self._mailboxes[mb](0)
        elif event['Event'] == 'Cdr':
            end = self._sh.now()
            start = end - datetime.timedelta(seconds=int(event['Duration']))
            duration = event['BillableSeconds']
            if len(event['Source']) <= 4:
                direction = '=>'
                number = event['Destination']
            else:
                direction = '<='
                number = event['Source']
                name = event['CallerID'].split('<')[0].strip('" ')
                self._log_in.add([start, name, number, duration, direction])

    def _update_devices(self):
        active_channels = self._command({'Action': 'CoreShowChannels'})
        if active_channels is None:
            active_channels = []
        active_devices = list(map(self._get_device, active_channels))
        for device in self._devices:
            if device not in active_devices:
                self._devices[device](False, 'Asterisk')

    def _get_device(self, channel):
        channel, s, d = channel.rpartition('-')
        a, b, channel = channel.partition('/')
        return channel

    def parse_item(self, item):
        if 'ast_dev' in item.conf:
            self._devices[item.conf['ast_dev']] = item
        if 'ast_box' in item.conf:
            self._mailboxes[item.conf['ast_box']] = item
        if 'ast_db' in item.conf:
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if 'ast_db' in item.conf:
            value = item()
            if isinstance(value, bool):
                value = int(item())
            self.db_write(item.conf['ast_db'], value)

    def parse_logic(self, logic):
        if 'ast_userevent' in logic.conf:
            event = logic.conf['ast_userevent']
            if event not in self._trigger_logics:
                self._trigger_logics[event] = [logic]
            else:
                self._trigger_logics[event].append(logic)

    def run(self):
        self.alive = True

    def handle_connect(self):
        self._command(self._init_cmd, reply=False)
        for mb in self._mailboxes:
            mbc = self.mailbox_count(mb)
            if mbc is not None:
                self._mailboxes[mb](mbc[1])

    def stop(self):
        self.alive = False
        self._reply_lock.acquire()
        self._reply_lock.notify()
        self._reply_lock.release()
        self.close()
