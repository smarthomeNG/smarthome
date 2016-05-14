#!/usr/bin/env python3
#
#########################################################################
#  Copyright 2014 Marcus Popp                              marcus@popp.mx
#########################################################################
#  Free for non-commercial use
#########################################################################

import datetime
import logging
import hashlib
import urllib.parse
import xml.etree.cElementTree

import lib.connection
import lib.www

logger = logging.getLogger('')

services = {'WANIPConnection': ('/upnp/control/wanipconnection1', 'urn:dslforum-org:service:WANIPConnection:1'),
            'WLANConfiguration1': ('/upnp/control/wlanconfig1', 'urn:dslforum-org:service:WLANConfiguration:1'),
            'WLANConfiguration2': ('/upnp/control/wlanconfig2', 'urn:dslforum-org:service:WLANConfiguration:2'),
            'WLANConfiguration3': ('/upnp/control/wlanconfig3', 'urn:dslforum-org:service:WLANConfiguration:3'),
            'X_AVM-DE_OnTel': ('/upnp/control/x_contact', 'urn:dslforum-org:service:X_AVM-DE_OnTel:1'),
            'DeviceConfig': ('/upnp/control/deviceconfig', 'urn:dslforum-org:service:DeviceConfig:1'),
            'TAM': ('/upnp/control/x_tam', 'urn:dslforum-org:service:X_AVM-DE_TAM:1'),
            'Hosts': ('/upnp/control/hosts', 'urn:dslforum-org:service:Hosts:1'),
            'VoIP': ('/upnp/control/x_voip', 'urn:dslforum-org:service:X_VoIP:1'),
            'WANCommonInterfaceConfig': ('/upnp/control/wancommonifconfig1', 'urn:dslforum-org:service:WANCommonInterfaceConfig:1')}

values = {'external_ip': ('WANIPConnection', 'GetExternalIPAddress', 'NewExternalIPAddress', None),
          'connected': ('WANIPConnection', 'GetStatusInfo', 'NewConnectionStatus', 'Connected'),
          'packets_sent': ('WANCommonInterfaceConfig', 'GetTotalPacketsSent', 'NewTotalPacketsSent', None),
          'packets_received': ('WANCommonInterfaceConfig', 'GetTotalPacketsReceived', 'NewTotalPacketsReceived', None),
          'bytes_sent': ('WANCommonInterfaceConfig', 'GetTotalBytesSent', 'NewTotalBytesSent', None),
          'bytes_received': ('WANCommonInterfaceConfig', 'GetTotalBytesReceived', 'NewTotalBytesReceived', None),
          'tam': ('TAM', 'GetInfo', 'NewEnable', '1'),
          'host': ('Hosts', 'GetSpecificHostEntry', 'NewActive', '1'),
          'wlan': ('WLANConfiguration1', 'GetInfo', 'NewEnable', '1'),
          'wlan_1': ('WLANConfiguration1', 'GetInfo', 'NewEnable', '1'),
          'wlan_2': ('WLANConfiguration2', 'GetInfo', 'NewEnable', '1'),
          'wlan_3': ('WLANConfiguration3', 'GetInfo', 'NewEnable', '1'),
          'link': ('WANCommonInterfaceConfig', 'GetCommonLinkProperties', 'NewPhysicalLinkStatus', 'Up')
          }
#         'calls': ('VoIP', 'X_AVM-DE_DialGetConfig', 'NewX_AVM-DE_PhoneName', None),
#         'phonebook': ('X_AVM-DE_OnTel', 'GetCallList', '', None)
#         'port': ('VoIP', 'X_AVM-DE_GetPhonePort', 'NewX_AVM-DE_PhoneName', None),
#         'clients': ('VoIP', 'X_AVM-DE_GetClients', 'NewX_AVM-DE_ClientList', None),

commands = {'reconnect': ('WANIPConnection', 'ForceTermination', None),
            'reboot': ('DeviceConfig', 'Reboot', None),
            'tam': ('TAM', 'SetEnable', 'NewEnable'),
            'setport': ('VoIP', 'X_AVM-DE_DialSetConfig', 'NewX_AVM-DE_PhoneName'),
            'call': ('VoIP', 'X_AVM-DE_DialNumber', 'NewX_AVM-DE_PhoneNumber'),
            'hangup': ('VoIP', 'X_AVM-DE_DialHangup', None),
            'wlan': ('WLANConfiguration1', 'SetEnable', 'NewEnable'),
            'wlan_1': ('WLANConfiguration1', 'SetEnable', 'NewEnable'),
            'wlan_2': ('WLANConfiguration2', 'SetEnable', 'NewEnable'),
            'wlan_3': ('WLANConfiguration3', 'SetEnable', 'NewEnable')}

# http://www.avm.de/de/News/artikel/schnittstellen_und_entwicklungen.php


class CallMonitor(lib.connection.Client):
    # Ausgehende Anrufe: datum;CALL;ConnectionID;Nebenstelle;GenutzteNummer;AngerufeneNummer;
    # Eingehende Anrufe: datum;RING;ConnectionID;Anrufer-Nr;Angerufene-Nummer;
    # Zustandegekommene Verbindung: datum;CONNECT;ConnectionID;Nebenstelle;Nummer;
    # Ende der Verbindung: datum;DISCONNECT;ConnectionID;dauerInSekunden;
    # enable with "#96*5*"
    # disable with "#96*4*"

    port = 1012

    def __init__(self, logics, host='fritz.box'):
        lib.connection.Client.__init__(self, host, self.port, monitor=True)
        self._logics = logics

    def found_terminator(self, data):
        value = data.decode().split(';')
        source = ''
        destination = ''
        if value[1] == 'CALL':
            source = value[3]
            destination = value[5]
        elif value[1] == 'RING':
            source = value[3]
            destination = value[4]
        for logic in self._logics:
            logic.trigger('FritzBox', source, value, destination)


class FritzBox(lib.www.Client):

    _body = """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:{0} xmlns:u="{1}">{2}</u:{0}>
</s:Body>
</s:Envelope>"""

    def __init__(self, smarthome, username, password, host='fritz.box', cycle=300, timeout=5):
        self._sid = False
        self._sh = smarthome
        self._fritzbox = host
        self._cycle = int(cycle)
        self._username = username
        self._password = password
        self._timeout = int(timeout)
        self._items = []
        self._ahas = []
        self._callmonitor_logics = []

    def run(self):
        self.alive = True
        self._sh.scheduler.add('fb-cycle', self._update_cycle, prio=5, cycle=self._cycle, offset=2)
        content = self._aha_command('getswitchlist')
        if content and 'homeautoswitch' not in content:
            logger.info("FritzBox: found the following AIN: {}".format(content))
        if self._callmonitor_logics != []:
            self.__callmonitor = CallMonitor(self._callmonitor_logics, self._fritzbox)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'fritzbox' in item.conf:
            value = item.conf['fritzbox']
            if value in values:
                if value == 'wlan':
                    if 'fb_wlan' in item.conf:
                        item.conf['fritzbox'] = "wlan_{}".format(item.conf['fb_wlan'])
                elif value == 'tam':
                    if 'fb_tam' not in item.conf:
                        item.conf['fb_tam'] = 0
                elif value == 'host':
                    if 'fb_mac' not in item.conf:
                        logger.warning("FritzBox: please specify fb_mac for {}".format(item.id()))
                        return
                self._items.append(item)
            if value in commands:
                return self.update_item
            if value in ['switch', 'power', 'energy']:
                if 'fb_ain' in item.conf:
                    ain = item.conf['fb_ain']
                elif 'fb_ain' in item.return_parent().conf:
                    ain = item.return_parent().conf['fb_ain']
                else:
                    logger.warning("FritzBox: please specify fb_ain for {}".format(item.id()))
                    return
                item.conf['fb_ain'] = ain.replace(' ', '').strip()
                self._ahas.append(item)
                if value == 'switch':
                    return self.update_aha

    def parse_logic(self, logic):
        if 'fritzbox' in logic.conf:
            if logic.conf['fritzbox'] == 'callmonitor':
                self._callmonitor_logics.append(logic)

    def update_aha(self, item, caller=None, source=None, dest=None):
        if caller != 'FritzBox':
            if item():
                command = 'setswitchon'
            else:
                command = 'setswitchoff'
            self._aha_command(command, item.conf['fb_ain'])

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'FritzBox':
            command = item.conf['fritzbox']
            if command.startswith('wlan'):
                self._set(command, int(item()))
            elif command == 'tam':
                self._set(command, str(item()).lower(), index=item.conf['fb_tam'])
            else:
                self._set(command)

    # Plugin specific public methods

    def call(self, call_from, call_to):
        self._set('setport', call_from)
        self._set('call', "{}".format(call_to))

    def calllist(self):
        content = self.fetch_url("https://{}:49443/calllist.lua?sid={}".format(self._fritzbox, self._get_sid()), timeout=self._timeout)
        if content:
            entries = []
            tree = xml.etree.cElementTree.fromstring(content.decode())
            for call in tree.findall('Call'):
                entry = {}
                for element in call:
                    entry[element.tag] = element.text
                entry['Date'] = datetime.datetime.strptime(entry['Date'], '%d.%m.%y %H:%M')
                entries.append(entry)
            return entries

    def hangup(self):
        self._set('hangup')

    def reboot(self):
        self._set('reboot')

    def reconnect(self):
        self._set('reconnect')

    def webcm(self, command={}):
        # http://www.wehavemorefun.de/fritzbox/Telcfg
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        command['sid'] = self._get_sid()
        command['getpage'] = '../html/login_sid.xml'
        body = urllib.parse.urlencode(command)
        url = "http://{}/cgi-bin/webcm".format(self._fritzbox)
        self.fetch_url(url, headers=headers, body=body, method='POST', timeout=self._timeout)

    # Plugin specific private methods
    def _aha_command(self, command, ain=None):
        # http://www.avm.de/de/Extern/files/session_id/AHA-HTTP-Interface.pdf
        url = "http://{}/webservices/homeautoswitch.lua?switchcmd={}&sid={}".format(self._fritzbox, command, self._get_sid())
        if ain is not None:
            url += "&ain={}".format(ain)
        content = self.fetch_url(url, timeout=self._timeout)
        if content:
            return(content.decode().strip())

    def _get(self, variable, value='', index=None):
        if variable in values:
            service, action, element, check = values[variable]
            url, service = services[service]
        else:
            return
        url = "https://{}:49443{}".format(self._fritzbox, url)
        headers = {'CONTENT-TYPE': 'text/xml; charset="utf-8"'}
        headers['SOAPACTION'] = "{}#{}".format(service, action)
        if index is not None:
            value += "<{0}>{1}</{0}>".format('NewIndex', index)
        body = self._body.format(action, service, value)
        content = self.fetch_url(url, auth='digest', headers=headers, body=body, username=self._username, password=self._password, method='POST', timeout=self._timeout)
        if content and element:
            tree = xml.etree.cElementTree.fromstring(content.decode())
            element = tree.find('.//{}'.format(element))
            if element is None:
                return
            if check is None:
                try:
                    return int(element.text)
                except:
                    return element.text

            else:
                return element.text == check

    def _get_sid(self):
        if self._sid:
            return self._sid
        content = self.fetch_url("http://{}/login_sid.lua".format(self._fritzbox), timeout=self._timeout)
        if content:
            tree = xml.etree.cElementTree.fromstring(content.decode())
            challenge = tree.find('.//Challenge').text
            response = hashlib.md5("{}-{}".format(challenge, self._password).encode('utf-16le')).hexdigest()
            url = "http://{}/login_sid.lua?username={}&response={}-{}".format(self._fritzbox, self._username, challenge, response)
            content = self.fetch_url(url, timeout=self._timeout)
            tree = xml.etree.cElementTree.fromstring(content.decode())
            sid = tree.find('.//SID').text
            if sid != '0000000000000000':
                self._sid = sid
                return sid

    def _set(self, variable, value='', index=None):
        if variable in commands:
            service, action, element = commands[variable]
            url, service = services[service]
        else:
            return
        url = "https://{}:49443{}".format(self._fritzbox, url)
        headers = {'CONTENT-TYPE': 'text/xml; charset="utf-8"'}
        headers['SOAPACTION'] = "{}#{}".format(service, action)
        if element:
            value = "<{0}>{1}</{0}>".format(element, value)
        if index is not None:
            value = "<{0}>{1}</{0}>{2}".format('NewIndex', index, value)  # für tam notwendig
        body = self._body.format(action, service, value)
        self.fetch_url(url, auth='digest', headers=headers, body=body, username=self._username, password=self._password, method='POST', timeout=self._timeout)

    def _update_cycle(self):
        # start = time.time()
        for item in self._items:
            if not self.alive:
                return
            value = item.conf['fritzbox']
            if value == 'host':
                value = self._get('host', "<NewMACAddress>{}</NewMACAddress>".format(item.conf['fb_mac']))
            elif value == 'tam':
                value = self._get(value, index=item.conf['fb_tam'])
            else:
                value = self._get(value)
            if value is not None:
                item(value, 'FritzBox')
        for item in self._ahas:
            if not self.alive:
                return
            value = item.conf['fritzbox']
            if value == 'power':
                command = 'getswitchpower'
            elif value == 'energy':
                command = 'getswitchenergy'
            else:
                command = 'getswitchstate'
            value = self._aha_command(command, item.conf['fb_ain'])
            if value is not None:
                item(int(value), 'FritzBox')
#       cycletime = time.time() - start
#       logger.debug("cycle takes {0} seconds".format(cycletime))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = FritzBox('smarthome-dummy', '192.168.2.1')
