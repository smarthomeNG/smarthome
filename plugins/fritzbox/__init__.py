#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2012-2013 KNX-User-Forum e.V.       http://knx-user-forum.de/
#
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import logging
import http.client
import urllib.request
import urllib.parse
import urllib.error
import hashlib
from xml.dom.minidom import parseString

logger = logging.getLogger('')


class fbex(Exception):
    pass


class FritzBoxBase():

    def __init__(self, host='fritz.box', username=None, password=None):
        self._host = host
        self._username = username
        self._password = password
        self._sid = 0

    def createResponse(self, challenge):
        text = "%s-%s" % (challenge, self._password)
        text = text.encode("utf-16le")
        res = "%s-%s" % (challenge, hashlib.md5(text).hexdigest())
        return res

    def _login(self):

        params = urllib.parse.urlencode(
            {'getpage': '../html/login_sid.xml', 'sid': self._sid})
        headers = {"Content-type":
                   "application/x-www-form-urlencoded", "Accept": "text/plain"}
        con = http.client.HTTPConnection(self._host)
        con.request("POST", "/cgi-bin/webcm", params, headers)
        resp = con.getresponse()
        con.close()
        if resp.status != 200:
            raise fbex("no connection to fritzbox.")
        data = resp.read().decode('iso-8859-1')
        logger.debug("data = {0}".format(data))
        sid = re.search('<SID>(.*?)</SID>', data).group(1)
        logger.debug("sid = {0}".format(sid))
        if sid == '0000000000000000':
            logger.debug("invalid sid, starting challenge/response")
            challenge = re.search('<Challenge>(.*?)</Challenge>', data).group(1)
            challenge_resp = challenge + '-' + self._password
            m = hashlib.md5()
            m.update(challenge_resp)
            challenge_resp = challenge + '-' + m.hexdigest().lower()
            params = urllib.parse.urlencode(
                {'login:command/response': challenge_resp, 'getpage': '../html/login_sid.xml'})
            con = http.client.HTTPConnection(self._host)
            con.request("POST", "/cgi-bin/webcm", params, headers)
            resp = con.getresponse()
            con.close()
            if resp.status != 200:
                raise fbex("challenge/response failed")
            data = resp.read().decode('iso-8859-1')
            self._sid = re.search('<SID>(.*?)</SID>', data).group(1)
            logger.debug('session id = {0}'.format(self._sid))

    def execute(self, cmd_dict, return_resp=False):
        logger.debug("execute command: {0}".format(cmd_dict))
        self._login()
        cmd_dict['getpage'] = '../html/login_sid.lua'
        cmd_dict['sid'] = self._sid
        params = urllib.parse.urlencode(cmd_dict)
        headers = {"Content-type":
                   "application/x-www-form-urlencoded", "Accept": "text/plain"}
        con = http.client.HTTPConnection(self._host)
        con.request("POST", "/cgi-bin/webcm", params, headers)
        resp = con.getresponse()
        con.close()
        if resp.status != 200:
            raise fbex("execution failed: {0}".format(cmd_dict))
        if return_resp:
            return resp

    def call(self, call_from, call_to):
        logger.debug(
            "initiate call from {0} to {1}".format(call_from, call_to))
        self.execute({
            'telcfg:settings/UseClickToDial': 1,
            'telcfg:command/Dial': call_to,
            'telcfg:settings/DialPort': call_from
        })


class FritzBox(FritzBoxBase):

    def __init__(self, smarthome, host='fritz.box', username=None, password=None):
        FritzBoxBase.__init__(self, host, username, password)
        self._sh = smarthome

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'fritzbox' in item.conf:
            return self.update_item
        fb = {}
        for attr in item.conf:
            if attr.startswith('fritzbox'):
                fb['telcfg{0}'.format(attr[8:])] = item.conf[attr]
        if len(fb) > 0:
            item.conf['fritzbox'] = fb
            print(fb)
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Fritzbox' and item():
            attr = item.conf['fritzbox']
            if isinstance(attr, dict):
                self.execute(attr)
                return
            if isinstance(attr, str):
                match = re.search(
                    r'\s*call\s(?P<from>[^\s]+)\s+(?P<to>[^\s]+)\s*', attr)
                if match:
                    self.call(match.group('from'), match.group('to'))
                    return
            logger.debug(
                "fritzbox attribute value {0} on item {1} not recognized".format(attr, item))


def main():
    if len(sys.argv) != 4:
        print("usage: {0} password from to".format(sys.argv[0]))
        return 1

    handler = logging.StreamHandler(sys.stdout)
    frm = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s", "%d.%m.%Y %H:%M:%S")
    handler.setFormatter(frm)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    fb = FritzBoxBase(password=sys.argv[1])
    fb.call(sys.argv[2], sys.argv[3])

if __name__ == '__main__':
    sys.exit(main())
