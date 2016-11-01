#!/usr/bin/env python3
#
#########################################################################
#  Copyright 2016 René Frieß                        rene.friess(a)gmail.com
#  Version 1.1.2
#########################################################################
#  Free for non-commercial use
#  
#  Plugin for the software SmartHome.py (NG), which allows to control and read 
#  devices such as the FritzBox. 
#  For all functionality, the TR-064 interface is used.
#
#  Service implementation is mainly based on the information found on:
#  - http://avm.de/service/schnittstellen/
#  - http://www.fhemwiki.de/wiki/FRITZBOX
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
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
#  along with SmartHome.py (NG). If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import datetime
import logging
import socket
import time
import threading
from xml.dom import minidom
import requests
from requests.packages import urllib3
from requests.auth import HTTPDigestAuth
from lib.model.smartplugin import SmartPlugin


class MonitoringService():
    """
    Class which connects to the FritzBox service of the Callmonitor: http://www.wehavemorefun.de/fritzbox/Callmonitor

    | Can currently handle three items:
    | - avm_data_type = is_call_incoming, type = bool
    | - avm_data_type = last_caller, type = str
    | - avm_data_type = last_call_date, type = str
    """

    def __init__(self, host, port, callback, call_monitor_incoming_filter, plugin_instance):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("starting monitoring service")
        self._host = host
        self._port = port
        self._plugin_instance = plugin_instance
        self._callback = callback
        self._trigger_items = []  # items which can be used to trigger sth, e.g. a logic
        self._items = []  # more general items for the call monitor
        self._items_incoming = []  # items for incoming calls
        self._items_outgoing = []  # items for outgoing calls
        self._duration_item = dict()  # 2 items, on for counting the incoming, one for counting the outgoing call duration
        self._call_active = dict()
        self._call_active['incoming'] = False
        self._call_active['outgoing'] = False
        self._call_incoming_cid = dict()
        self._call_outgoing_cid = dict()
        self._call_monitor_incoming_filter = call_monitor_incoming_filter
        self.conn = None

    def connect(self):
        """
        Connects to the call monitor of the AVM device
        """
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((self._host, self._port))
            self._listen_thread = threading.Thread(target=self._listen,
                                                   name="MonitoringService_%s" % self._plugin_instance.get_instance_name()).start()
        except Exception as e:
            self.conn = None
            self.logger.error("MonitoringService: Cannot connect to " + self._host + " on port: " + str(
                self._port) + ", CallMonitor activated by #96*5*? - Error: " + str(e))
            return

    def disconnect(self):
        """
        Disconnects from the call monitor of the AVM device
        """
        self._listen_active = False
        self._stop_counter('incoming')
        self._stop_counter('outgoing')
        try:
            self._listen_thread.join(1)
        except:
            pass
        self.conn.shutdown(2)

    def reconnect(self):
        """
        Reconnects to the call monitor of the AVM device
        """
        self.disconnect()
        self.connect()

    def register_item(self, item):
        """
        Registers an item to the MonitoringService

        :param item: item to register
        """
        if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['is_call_incoming',
                                                                                 'last_caller_incoming',
                                                                                 'last_number_incoming',
                                                                                 'last_called_number_incoming',
                                                                                 'last_call_date_incoming',
                                                                                 'call_event_incoming']:
            self._items_incoming.append(item)
        elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['is_call_outgoing',
                                                                                   'last_caller_outgoing',
                                                                                   'last_number_outgoing',
                                                                                   'last_called_number_outgoing',
                                                                                   'last_call_date_outgoing',
                                                                                   'call_event_outgoing']:
            self._items_outgoing.append(item)
        elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'monitor_trigger':
            self._trigger_items.append(item)
        else:
            self._items.append(item)

    def set_duration_item(self, item):
        """
        Sets specific items which count the duration of an incoming or outgoing call
        """
        self._duration_item[self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type').split("@")[0]] = item

    def _listen(self, recv_buffer=4096):
        """
        Function which listens to the established connection.
        """
        self._listen_active = True
        buffer = ""
        data = True
        while self._listen_active == True:
            data = self.conn.recv(recv_buffer)
            buffer += data.decode("utf-8")
            while buffer.find("\n") != -1:
                line, buffer = buffer.split("\n", 1)
                self._parse_line(line)

            time.sleep(1)
        return

    def _start_counter(self, timestamp, direction):
        if direction == 'incoming':
            self._call_connect_timestamp = time.mktime(
                datetime.datetime.strptime((timestamp), "%d.%m.%y %H:%M:%S").timetuple())
            self._duration_counter_thread_incoming = threading.Thread(target=self._count_duration_incoming,
                                                                      name="MonitoringService_Duration_Incoming_%s" % self._plugin_instance.get_instance_name()).start()
            self.logger.debug('Counter incoming - STARTED')
        elif direction == 'outgoing':
            self._call_connect_timestamp = time.mktime(
                datetime.datetime.strptime((timestamp), "%d.%m.%y %H:%M:%S").timetuple())
            self._duration_counter_thread_outgoing = threading.Thread(target=self._count_duration_outgoing,
                                                                      name="MonitoringService_Duration_Outgoing_%s" % self._plugin_instance.get_instance_name()).start()
            self.logger.debug('Counter outgoing - STARTED')

    def _stop_counter(self, direction):
        # only stop of thread is active

        if self._call_active[direction]:
            self._call_active[direction] = False
            self.logger.debug('STOPPING ' + direction)
            try:
                if direction == 'incoming':
                    self._duration_counter_thread_incoming.join(1)
                elif direction == 'outgoing':
                    self._duration_counter_thread_outgoing.join(1)
            except:
                pass

    def _count_duration_incoming(self):
        self._call_active['incoming'] = True
        while (self._call_active['incoming']):
            if not self._duration_item['call_duration_incoming'] is None:
                duration = time.time() - self._call_connect_timestamp
                self._duration_item['call_duration_incoming'](int(duration))
            time.sleep(1)

    def _count_duration_outgoing(self):
        self._call_active['outgoing'] = True
        while (self._call_active['outgoing']):
            if not self._duration_item['call_duration_outgoing'] is None:
                duration = time.time() - self._call_connect_timestamp
                self._duration_item['call_duration_outgoing'](int(duration))
            time.sleep(1)

    def _parse_line(self, line):
        """
        Parses a data set in the form of a line.

        Data Format:
        Ausgehende Anrufe: datum;CALL;ConnectionID;Nebenstelle;GenutzteNummer;AngerufeneNummer;SIP+Nummer
        Eingehende Anrufe: datum;RING;ConnectionID;Anrufer-Nr;Angerufene-Nummer;SIP+Nummer
        Zustandegekommene Verbindung: datum;CONNECT;ConnectionID;Nebenstelle;Nummer;
        Ende der Verbindung: datum;DISCONNECT;ConnectionID;dauerInSekunden;

        :param line: data line which is parsed
        """
        self.logger.debug(line)
        line = line.split(";")

        if (line[1] == "RING"):
            call_from = line[3]
            call_to = line[4]
            self._trigger(call_from, call_to, line[0], line[2], line[1], '')
        elif (line[1] == "CALL"):
            call_from = line[4]
            call_to = line[5]
            self._trigger(call_from, call_to, line[0], line[2], line[1], line[3])
        elif (line[1] == "CONNECT"):
            self._trigger('', '', line[0], line[2], line[1], line[3])
        elif (line[1] == "DISCONNECT"):
            self._trigger('', '', '', line[2], line[1], '')

    def _trigger(self, call_from, call_to, time, callid, event, branch):
        """
        Triggers the event: sets item values and looks up numbers in the phone book.
        """

        # in each case set current call event and direction
        for item in self._items:
            if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'call_event':
                item(event.lower())
            if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'call_direction':
                if event == 'RING':
                    item("incoming")
                else:
                    item("outgoing")

        # call is incoming
        if event == 'RING':
            # process "trigger items"
            for trigger_item in self._trigger_items:
                if self._plugin_instance.get_iattr_value(trigger_item.conf, 'avm_data_type') == 'monitor_trigger':
                    trigger_item(0)
                    # self.logger.debug(self._plugin_instance.get_iattr_value(trigger_item.conf, 'avm_data_type') + " " +trigger_item.conf['avm_incoming_allowed']+" "+trigger_item.conf['avm_target_number'])
                    if 'avm_incoming_allowed' not in trigger_item.conf or 'avm_target_number' not in trigger_item.conf:
                        self.logger.error(
                            "both 'avm_incoming_allowed' and 'avm_target_number' must be specified as attributes in a trigger item.")
                    elif trigger_item.conf['avm_incoming_allowed'] == call_from and trigger_item.conf[
                        'avm_target_number'] == call_to:
                        trigger_item(1)

            if self._call_monitor_incoming_filter in call_to:
                # set call id for incoming call
                self._call_incoming_cid = callid

                # reset duration for incoming calls
                self._duration_item['call_duration_incoming'](0)

                # process items specific to incoming calls
                for item in self._items_incoming:  # update items for incoming calls
                    if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['is_call_incoming']:
                        item(1)
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['last_caller_incoming']:
                        if call_from != '' and call_from is not None:
                            name = self._callback(call_from)
                            if name != '' and not name is None:
                                item(name)
                            else:
                                item(call_from)
                        else:
                            item("Unbekannt")
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in [
                        'last_call_date_incoming']:
                        item(time)
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['call_event_incoming']:
                        item(event.lower())
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['last_number_incoming']:
                        item(call_from)
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in [
                        'last_called_number_incoming']:
                        item(call_to)

        # call is outgoing
        elif event == 'CALL':
            # set call id for outgoing call
            self._call_outgoing_cid = callid

            # reset duration for outgoing calls
            self._duration_item['call_duration_outgoing'](0)

            # process items specific to outgoing calls
            for item in self._items_outgoing:
                if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['is_call_outgoing']:
                    item(1)
                elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['last_caller_outgoing']:
                    name = self._callback(call_to)
                    if name != '' and not name is None:
                        item(name)
                    else:
                        item(call_to)
                elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['last_call_date_outgoing']:
                    item(time)
                elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['call_event_outgoing']:
                    item(event.lower())
                elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['last_number_outgoing']:
                    item(call_from)
                elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in [
                    'last_called_number_outgoing']:
                    item(call_to)

        # connection established
        elif event == 'CONNECT':
            # handle OUTGOING calls
            if callid == self._call_outgoing_cid:
                if not self._duration_item[
                    'call_duration_outgoing'] is None:  # start counter thread only if duration item set and call is outgoing
                    self._stop_counter('outgoing')  # stop potential running counter for parallel (older) outgoing call
                    self._start_counter(time, 'outgoing')
                for item in self._items_outgoing:
                    if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['call_event_outgoing']:
                        item(event.lower())

            # handle INCOMING calls
            elif callid == self._call_incoming_cid:
                if not self._duration_item[
                    'call_duration_incoming'] is None:  # start counter thread only if duration item set and call is incoming
                    self._stop_counter('incoming')  # stop potential running counter for parallel (older) incoming call
                    self._start_counter(time, 'incoming')
                for item in self._items_incoming:
                    if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') in ['call_event_incoming']:
                        item(event.lower())

        # connection ended
        elif event == 'DISCONNECT':
            # handle OUTGOING calls
            if callid == self._call_outgoing_cid:
                for item in self._items_outgoing:
                    if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'call_event_outgoing':
                        item(event.lower())
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'is_call_outgoing':
                        item(0)
                if not self._duration_item['call_duration_outgoing'] is None:  # stop counter threads
                    self._stop_counter('outgoing')
                self._call_outgoing_cid = None

            # handle INCOMING calls
            elif callid == self._call_incoming_cid:
                for item in self._items_incoming:
                    if self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'call_event_incoming':
                        item(event.lower())
                    elif self._plugin_instance.get_iattr_value(item.conf, 'avm_data_type') == 'is_call_incoming':
                        item(0)
                if not self._duration_item['call_duration_incoming'] is None:  # stop counter threads
                    self._stop_counter('incoming')
                self._call_incoming_cid = None


class FritzDevice():
    """
    This class encapsulates information related to a specific FritzDevice, such has host, port, ssl, username, password, or related items
    """

    def __init__(self, host, port, ssl, username, password, identifier='default'):
        self.logger = logging.getLogger(__name__)
        self._host = host
        self._port = port
        self._ssl = ssl
        self._username = username
        self._password = password
        self._identifier = identifier
        self._items = []

    def get_identifier(self):
        """
        Returns the internal identifier of the FritzDevice

        :return: identifier of the device, as set in plugin.conf
        """
        return self._identifier

    def get_host(self):
        """
        Returns the hostname / IP of the FritzDevice

        :return: hostname of the device, as set in plugin.conf
        """
        return self._host

    def get_port(self):
        """
        Returns the port of the FritzDevice

        :return: port of the device, as set in plugin.conf
        """
        return self._port

    def get_items(self):
        """
        Returns added items

        :return: array of items hold by the device
        """
        return self._items

    def get_item_count(self):
        """
        Returns number of added items

        :return: number of items hold by the device
        """
        return len(self._items)

    def is_ssl(self):
        """
        Returns information if SSL is enabled

        :return: is ssl enabled, as set in plugin.conf
        """
        return self._ssl

    def get_user(self):
        """
        Returns the user for the FritzDevice

        :return: user, as set in plugin.conf
        """
        return self._username

    def get_password(self):
        """
        Returns the password for the FritzDevice

        :return: password, as set in plugin.conf
        """
        return self._password


class AVM(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides the update functions for the different TR-064 services on the FritzDevice
    """
    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION = "1.1.2"

    _header = {'SOAPACTION': '', 'CONTENT-TYPE': 'text/xml; charset="utf-8"'}
    _envelope = """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
            xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">%s
        </s:Envelope>
        """
    _body = """
        <s:Body>
        <u:%(action)s xmlns:u="%(service)s">%(arguments)s
        </u:%(action)s>
        </s:Body>
        """
    _argument = """
        <s:%(name)s>%(value)s</s:%(name)s>"""

    _urn_map = dict([('WLANConfiguration', 'urn:dslforum-org:service:WLANConfiguration:%s'),
                     # index needs to be adjusted from 1 to 3
                     ('WANCommonInterfaceConfig', 'urn:dslforum-org:service:WANCommonInterfaceConfig:1'),
                     ('WANIPConnection', 'urn:schemas-upnp-org:service:WANIPConnection:1'),
                     ('TAM', 'urn:dslforum-org:service:X_AVM-DE_TAM:1'),
                     ('OnTel', 'urn:dslforum-org:service:X_AVM-DE_OnTel:1'),
                     ('Homeauto', 'urn:dslforum-org:service:X_AVM-DE_Homeauto:1'),
                     ('Hosts', 'urn:dslforum-org:service:Hosts:1'),
                     ('X_VoIP', 'urn:dslforum-org:service:X_VoIP:1'),
                     ('DeviceConfig', 'urn:dslforum-org:service:DeviceConfig:1'),
                     ('DeviceInfo', 'urn:dslforum-org:service:DeviceInfo:1'),
                     ('WANDSLInterfaceConfig', 'urn:dslforum-org:service:WANDSLInterfaceConfig:1'),
                     ('MyFritz', 'urn:dslforum-org:service:X_AVM-DE_MyFritz:1')])

    def __init__(self, smarthome, username='', password='', host='fritz.box', port='49443', ssl='True', verify='False',
                 cycle=300, call_monitor='False', call_monitor_incoming_filter=''):
        """
        Initalizes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

        :param username:           Login name of user, cptional for devices which only support passwords
        :param password:           Password for the FritzDevice
        :param host:               IP or host name of FritzDevice
        :param port:               Port of the FritzDevice (https: 49443, http: 49000)
        :param ssl:                True or False => https or http in URLs
        :param verify:             True or False => verification of SSL certificate
        :param cycle:              Update cycle in seconds
        :param call_monitor:       bool: Shall the MonitoringService for the CallMonitor be started?
        :param call_monitor_incoming_filter:    Filter only specific numbers to be watched by call monitor
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info('Init AVM Plugin')

        self._session = requests.Session()
        self._timeout = 10

        self._verify = self.to_bool(verify)
        ssl = self.to_bool(ssl)

        if ssl and not self._verify:
            urllib3.disable_warnings()

        self._fritz_device = FritzDevice(host, port, ssl, username, password, self.get_instance_name())

        self._call_monitor = self.to_bool(call_monitor)
        if self._call_monitor:
            self._monitoring_service = MonitoringService(self._fritz_device.get_host(), 1012,
                                                         self.get_contact_name_by_phone_number,
                                                         call_monitor_incoming_filter, self)
            self._monitoring_service.connect()

        self._call_monitor_incoming_filter = call_monitor_incoming_filter

        self._cycle = int(cycle)
        self._sh = smarthome
        # Response Cache: Dictionary for storing the result of requests which is used for several different items, refreshed each update cycle. Please use distinct keys!
        self._response_cache = dict()
        self._calllist_cache = []

    def run(self):
        """
        Run method for the plugin
        """
        self._sh.scheduler.add(__name__, self._update_loop, prio=5, cycle=self._cycle, offset=2)
        self.alive = True

    def stop(self):
        """
        Stop method for the plugin
        """
        if self._call_monitor:
            self._monitoring_service.disconnect()
        self.alive = False

    def _assemble_soap_data(self, action, service, argument=''):
        """
        Builds the soap data set (from body and envelope templates for a given request.

        :param action: string of the action
        :param service: string of the service
        :param argument: dictionary (name : value) of arguments
        :return: string of the soap data
        """
        argument_string = ''
        if argument:
            arguments = [
                self._argument % {'name': name, 'value': value}
                for name, value in argument.items()
                ]
            argument_string = argument_string.join(arguments)
        body = self._body.strip() % {'action': action, 'service': service, 'arguments': argument_string}
        soap_data = self._envelope.strip() % body
        return soap_data

    def _build_url(self, suffix):
        """
        Builds a request url

        :param suffix: url suffix, e.g. "/upnp/control/x_tam"
        :return: string of the url, dependent on settings of the FritzDevice
        """
        if self._fritz_device.is_ssl():
            url_prefix = "https"
        else:
            url_prefix = "http"
        url = "%s://%s:%s%s" % (url_prefix, self._fritz_device.get_host(), self._fritz_device.get_port(), suffix)
        return url

    def _update_loop(self):
        """
        Starts the update loop for all known items.
        """
        self.logger.debug('Starting update loop for instance %s' % self._fritz_device.get_identifier())
        for item in self._fritz_device.get_items():
            if not self.alive:
                return
            if self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_connection_status', 'wan_connection_error',
                                                                    'wan_is_connected', 'wan_uptime', 'wan_ip']:
                self._update_wan_ip_connection(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['tam', 'tam_name', 'tam_new_message_number',
                                                                      'tam_total_message_number']:
                self._update_tam(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
                self._update_home_automation(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['wlanconfig', 'wlanconfig_ssid',
                                                                      'wlan_guest_time_remaining']:
                self._update_wlan_config(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_total_packets_sent',
                                                                      'wan_total_packets_received',
                                                                      'wan_total_bytes_sent',
                                                                      'wan_total_bytes_received', 'wan_link']:
                self._update_wan_common_interface_configuration(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['network_device']:
                self._update_host(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['uptime', 'software_version', 'hardware_version',
                                                                      'serial_number']:
                self._update_fritz_device_info(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_upstream', 'wan_downstream']:
                self._update_wan_dsl_interface_config(item)
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'myfritz_status':
                self._update_myfritz(item)
        # empty response cache
        self._response_cache = dict()

    def get_calllist_from_cache(self):
        """
        returns the cached calllist when all items are initialized. The filter set by plugin.conf is applied.

        :return: Array of calllist entries
        """
        # request and cache calllist
        if (self._calllist_cache is None):
            self._calllist_cache = self.get_calllist(self._call_monitor_incoming_filter)
        elif len(self._calllist_cache) == 0:
            self._calllist_cache = self.get_calllist(self._call_monitor_incoming_filter)
        return self._calllist_cache

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized. Selects each item corresponding to the AVM identifier and adds it to an internal array

        :param item: The item to process.
        """
        # items specific to call monitor
        if self.get_iattr_value(item.conf, 'avm_data_type') in ['is_call_incoming', 'last_caller_incoming',
                                                                'last_call_date_incoming',
                                                                'call_event_incoming', 'last_number_incoming',
                                                                'last_called_number_incoming',
                                                                'is_call_outgoing', 'last_caller_outgoing',
                                                                'last_call_date_outgoing',
                                                                'call_event_outgoing', 'last_number_outgoing',
                                                                'last_called_number_outgoing',
                                                                'call_event', 'call_direction', 'monitor_trigger']:
            # initally - if item empty - get data from calllist
            if self.get_iattr_value(item.conf, 'avm_data_type') == 'last_caller_incoming' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            if 'Name' in element:
                                item(element['Name'])
                            else:
                                item(element['Caller'])
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_number_incoming' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            if 'Caller' in element:
                                item(element['Caller'])
                            else:
                                item("")
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_called_number_incoming' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            item(element['CalledNumber'])
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_call_date_incoming' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            date = str(element['Date'])
                            date = date[8:10] + "." + date[5:7] + "." + date[2:4] + " " + date[11:19]
                            item(date)
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'call_event_incoming' and item() == '':
                item('disconnect')
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'is_call_incoming' and item() == '':
                item(0)
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_caller_outgoing' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['3', '4']:
                            if 'Name' in element:
                                item(element['Name'])
                            else:
                                item(element['Called'])
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_number_outgoing' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['3', '4']:
                            if 'Caller' in element:
                                item(''.join(filter(lambda x: x.isdigit(), element['Caller'])))
                            else:
                                item("")
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_called_number_outgoing' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['3', '4']:
                            item(element['Called'])
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'last_call_date_outgoing' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['3', '4']:
                            date = str(element['Date'])
                            date = date[8:10] + "." + date[5:7] + "." + date[2:4] + " " + date[11:19]
                            item(date)
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'call_event_outgoing' and item() == '':
                item('disconnect')
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'is_call_outgoing' and item() == '':
                item(0)
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'call_event' and item() == '':
                item('disconnect')
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'call_direction' and item() == '':
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            item('incoming')
                            break
                        if element['Type'] in ['3', '4']:
                            item('outgoing')
                            break
            if self._monitoring_service is not None:
                self._monitoring_service.register_item(item)
        elif self.get_iattr_value(item.conf, 'avm_data_type') in ['call_duration_incoming', 'call_duration_outgoing']:
            # items specific to call monitor duration calculation
            # initally get data from calllist
            if self.get_iattr_value(item.conf, 'avm_data_type') == 'call_duration_incoming' and item() == 0:
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['1', '2']:
                            duration = element['Duration']
                            duration = int(duration[0:1]) * 3600 + int(duration[2:4]) * 60
                            item(duration)
                            break
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'call_duration_outgoing' and item() == 0:
                if not self.get_calllist_from_cache() is None:
                    for element in self.get_calllist_from_cache():
                        if element['Type'] in ['3', '4']:
                            duration = element['Duration']
                            duration = int(duration[0:1]) * 3600 + int(duration[2:4]) * 60
                            item(duration)
                            break
            if not self._monitoring_service is None:
                self._monitoring_service.set_duration_item(item)
        else:
            # normal items
            self._fritz_device._items.append(item)
        if self.get_iattr_value(item.conf, 'avm_data_type') in ['wlanconfig', 'tam', 'aha_device']:
            # special items which can be changed outside the plugin context and need to be submitted to the FritzDevice
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        | Write items values - in case they were changed from somewhere else than the AVM plugin (=the FritzDevice) to the FritzDevice.

        | Uses:
        | - http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_tam.pdf
        | - http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wlanconfigSCPD.pdf
        | - http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_homeauto.pdf

        :param item: item to be updated towards the FritzDevice (Supported item avm_data_types: wlanconfig, tam, aha_device)
        """
        if caller != 'AVM':
            if self.get_iattr_value(item.conf, 'avm_data_type') in ['wlanconfig', 'tam']:
                action = 'SetEnable'
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
                action = 'SetSwitch'
            else:
                self.logger.error("%s is not defined to be updated." % self.get_iattr_value(item.conf, 'avm_data_type'))
                return

            headers = self._header.copy()
            if self.get_iattr_value(item.conf, 'avm_data_type') == 'wlanconfig':
                if int(item.conf['avm_wlan_index']) > 0:
                    headers['SOAPACTION'] = "%s#%s" % (
                    self._urn_map['WLANConfiguration'] % str(item.conf['avm_wlan_index']), action)
                    soap_data = self._assemble_soap_data(action, self._urn_map['WLANConfiguration'] % str(
                        item.conf['avm_wlan_index']), {'NewEnable': int(item())})
                else:
                    self.logger.error(
                        'No wlan_index attribute provided: %s' % self.get_iattr_value(item.conf, 'avm_data_type'))
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'tam':
                headers['SOAPACTION'] = "%s#%s" % (self._urn_map['TAM'], action)
                soap_data = self._assemble_soap_data(action, self._urn_map['TAM'],
                                                     {'NewIndex': 0, 'NewEnable': int(item())})
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
                headers['SOAPACTION'] = "%s#%s" % (self._urn_map['Homeauto'], action)
                # SwitchState: OFF, ON, TOGGLE, UNDEFINED
                if int(item()) == 1:
                    switch_state = "ON"
                else:
                    switch_state = "OFF"
                soap_data = self._assemble_soap_data(action, self._urn_map['Homeauto'],
                                                     {'NewAIN': item.conf['ain'].strip(),
                                                      'NewSwitchState': switch_state})

            if self.get_iattr_value(item.conf, 'avm_data_type') == 'wlanconfig':
                param = "%s%s%s" % (
                "/upnp/control/", self.get_iattr_value(item.conf, 'avm_data_type'), item.conf['avm_wlan_index'])
                url = self._build_url(param)

            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'tam':
                url = self._build_url("/upnp/control/x_tam")
            elif self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
                url = self._build_url("/upnp/control/x_homeauto")

            try:
                self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                   auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                       self._fritz_device.get_password()), verify=self._verify)
            except Exception as e:
                self.logger.error(
                    "Exception when sending POST request for updating item towards the FritzDevice: %s" % str(e))
                return

            if self.get_iattr_value(item.conf,
                                    'avm_data_type') == 'wlanconfig':  # check if item was guest wifi item and remaining time is set as item..
                for citem in self._fritz_device.get_items():  # search for guest time remaining item.
                    if self.get_iattr_value(citem.conf,
                                            'avm_data_type') == 'wlan_guest_time_remaining' and self.get_iattr_value(
                            citem.conf, 'avm_wlan_index') == item.conf['avm_wlan_index']:
                        self._response_cache.pop("wlanconfig_%s_%s" % (
                        self.get_iattr_value(citem.conf, 'avm_wlan_index'), "X_AVM-DE_GetWLANExtInfo"),
                                                 None)  # reset response cache
                        self._update_wlan_config(citem)  # immediately update remaining guest time

    def get_contact_name_by_phone_number(self, phone_number=''):
        """
        Searches the phonebook for a contact by a given (complete) phone number

        | Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_contactSCPD.pdf
        | Implementation of this method used information from https://www.symcon.de/forum/threads/25745-FritzBox-mit-SOAP-auslesen-und-steuern

        :param phone_number: full phone number of contact
        :return: string of the contact's real name
        """
        url = self._build_url("/upnp/control/x_contact")
        headers = self._header.copy()
        action = "GetPhonebook"
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['OnTel'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['OnTel'], {'NewPhonebookID': 0})

        try:
            response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                          auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                              self._fritz_device.get_password()), verify=self._verify)
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when sending POST request or parsing response: %s" % str(e))
            return

        pb_url_xml = xml.getElementsByTagName('NewPhonebookURL')
        if (len(pb_url_xml) > 0):
            pb_url = pb_url_xml[0].firstChild.data
            try:
                pb_result = self._session.get(pb_url, timeout=self._timeout, verify=self._verify)
                pb_xml = minidom.parseString(pb_result.content)
            except Exception as e:
                self.logger.error("Exception when sending GET request or parsing response: %s" % str(e))
                return
            contacts = pb_xml.getElementsByTagName('contact')
            if (len(contacts) > 0):
                for contact in contacts:
                    phone_numbers = contact.getElementsByTagName('number')
                    if (phone_numbers.length > 0):
                        i = phone_numbers.length
                        while (i >= 0):
                            i -= 1
                            if phone_number in phone_numbers[i].firstChild.data:
                                return contact.getElementsByTagName('realName')[0].firstChild.data.strip()
                                # no contact with phone number found, return number only
            return phone_number
        else:
            self.logger.error("Phonebook not available on the FritzDevice")

        return phone_number

    def get_calllist(self, filter_incoming=''):
        """
        Returns an array of all calllist entries

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_contactSCPD.pdf

        :param: Filter to filter incoming calls to a specific destination phone number
        :return: Array of calllist entries with the attributes 'Id','Type','Caller','Called','CalledNumber','Name','Numbertype','Device','Port','Date','Duration' (some optional)
        """

        url = self._build_url("/upnp/control/x_contact")
        headers = self._header.copy()
        action = "GetCallList"
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['OnTel'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['OnTel'], {'NewPhonebookID': 0})
        try:
            response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                          auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                              self._fritz_device.get_password()), verify=self._verify)
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when sending POST request or parsing response: %s" % str(e))
            return

        calllist_url_xml = xml.getElementsByTagName('NewCallListURL')
        if (len(calllist_url_xml) > 0):
            calllist_url = calllist_url_xml[0].firstChild.data

            try:
                calllist_result = self._session.get(calllist_url, timeout=self._timeout, verify=self._verify)
                calllist_xml = minidom.parseString(calllist_result.content)
            except Exception as e:
                self.logger.error("Exception when sending GET request or parsing response: %s" % str(e))
                return

            calllist_entries = calllist_xml.getElementsByTagName('Call')
            result_entries = []
            if (len(calllist_entries) > 0):
                for calllist_entry in calllist_entries:
                    result_entry = {}

                    progress = True

                    if len(filter_incoming) > 0:
                        type_element = calllist_entry.getElementsByTagName("Type")
                        if len(type_element) > 0:
                            if type_element[0].hasChildNodes():
                                type = int(type_element[0].firstChild.data)

                                if type == 1 or type == 2:
                                    called_number_element = calllist_entry.getElementsByTagName("CalledNumber")
                                    if len(called_number_element) > 0:
                                        if called_number_element[0].hasChildNodes():
                                            called_number = called_number_element[0].firstChild.data
                                            # self.logger.debug(called_number+" "+filter_incoming)
                                            if not filter_incoming in called_number:
                                                progress = False
                    if progress:
                        attributes = ['Id', 'Type', 'Caller', 'Called', 'CalledNumber', 'Name', 'Numbertype', 'Device',
                                      'Port', 'Date', 'Duration']
                        for attribute in attributes:
                            attribute_value = calllist_entry.getElementsByTagName(attribute)
                            if len(attribute_value) > 0:
                                if attribute_value[0].hasChildNodes():
                                    if attribute != 'Date':
                                        result_entry[attribute] = attribute_value[0].firstChild.data
                                    else:
                                        result_entry[attribute] = datetime.datetime.strptime(
                                            attribute_value[0].firstChild.data, '%d.%m.%y %H:%M')

                        result_entries.append(result_entry)
                return result_entries
            else:
                self.logger.debug("No calllist entries on the FritzDevice")
        else:
            self.logger.error("Calllist not available on the FritzDevice")

        return

    def reboot(self):
        """
        Reboots the FritzDevice

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/deviceconfigSCPD.pdf
        """
        url = self._build_url("/upnp/control/deviceconfig")
        action = 'Reboot'
        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['DeviceConfig'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['DeviceConfig'])
        try:
            self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                               auth=HTTPDigestAuth(self._fritz_device.get_user(), self._fritz_device.get_password()),
                               verify=self._verify)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

    def wol(self, mac_address):
        """
        Sends a WOL (WakeOnLAN) command to a MAC address

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/hostsSCPD.pdf

        :param mac_address: MAC address of the device to wake up
        """
        url = self._build_url("/upnp/control/hosts")
        headers = self._header.copy()
        action = 'X_AVM-DE_WakeOnLANByMACAddress'
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['Hosts'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['Hosts'], {'NewMACAddress': mac_address})
        self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                           auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                               self._fritz_device.get_password()), verify=self._verify)
        return

    def reconnect(self):
        """
        Reconnects the FritzDevice to the WAN

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wanipconnSCPD.pdf
        """
        url = self._build_url("/igdupnp/control/WANIPConn1")
        action = 'ForceTermination'
        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['WANIPConnection'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['WANIPConnection'])
        try:
            self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                               auth=HTTPDigestAuth(self._fritz_device.get_user(), self._fritz_device.get_password()),
                               verify=self._verify)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

    def set_call_origin(self, phone_name):
        """
        Sets the call origin, e.g. before running 'start_call'

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_voipSCPD.pdf

        :param phone_name: full phone identifier, could be e.g. '\*\*610' for an internal device
        """
        url = self._build_url("/upnp/control/x_voip")
        action = 'X_AVM-DE_DialSetConfig'
        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['X_VoIP'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['X_VoIP'],
                                             {'NewX_AVM-DE_PhoneName': phone_name.strip()})
        try:
            self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                               auth=HTTPDigestAuth(self._fritz_device.get_user(), self._fritz_device.get_password()),
                               verify=self._verify)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

    def start_call(self, phone_number):
        """
        Triggers a call for a given phone number

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_voipSCPD.pdf

        :param phone_number: full phone number to call
        """
        url = self._build_url("/upnp/control/x_voip")
        action = 'X_AVM-DE_DialNumber'
        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['X_VoIP'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['X_VoIP'],
                                             {'NewX_AVM-DE_PhoneNumber': phone_number.strip()})
        try:
            self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                               auth=HTTPDigestAuth(self._fritz_device.get_user(), self._fritz_device.get_password()),
                               verify=self._verify)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

    def cancel_call(self):
        """
        Cancels an active call

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_voipSCPD.pdf
        """
        url = self._build_url("/upnp/control/x_voip")
        action = 'X_AVM-DE_DialHangup'
        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['X_VoIP'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['X_VoIP'])
        try:
            self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                               auth=HTTPDigestAuth(self._fritz_device.get_user(), self._fritz_device.get_password()),
                               verify=self._verify)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

    def is_host_active(self, mac_address):
        """
        Checks if a MAC address is active on the FritzDevice, e.g. the status can be used for simple presence detection

        | Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/hostsSCPD.pdf
        | Also reference: https://blog.pregos.info/2015/11/07/anwesenheitserkennung-fuer-smarthome-mit-der-fritzbox-via-tr-064/

        :param: MAC address of the host
        :return: True or False, depending if the host is active on the FritzDevice
        """
        url = self._build_url("/upnp/control/hosts")
        headers = self._header.copy()
        action = 'GetSpecificHostEntry'
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['Hosts'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['Hosts'], {'NewMACAddress': mac_address})
        response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                      auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                          self._fritz_device.get_password()), verify=self._verify)

        xml = minidom.parseString(response.content)
        tag_content = xml.getElementsByTagName('NewActive')
        if (len(tag_content) > 0):
            if (tag_content[0].firstChild.data == "1"):
                is_active = True
            else:
                is_active = False
        else:
            is_active = False
            self.logger.debug("MAC Address %s not available on the FritzDevice - ID: %s" % (
            mac_address, self._fritz_device.get_identifier()))
        return bool(is_active)

    def _update_myfritz(self, item):
        """
        Retrieves information related to myfritz status of the FritzDevice

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_myfritzSCPD.pdf

        :param item: item to be updated (Supported item avm_data_types: myfritz_status)
        """
        url = self._build_url("/upnp/control/x_myfritz")
        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'myfritz_status':
            action = 'GetInfo'
            headers['SOAPACTION'] = "%s#%s" % (self._urn_map['MyFritz'], action)
            soap_data = self._assemble_soap_data(action, self._urn_map['MyFritz'])
        else:
            self.logger.error(
                "Attribute %s not supported by plugin method" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        try:
            response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                          auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                              self._fritz_device.get_password()), verify=self._verify)
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when sending POST request or parsing response: %s" % str(e))
            return

        tag_content = xml.getElementsByTagName('NewEnabled')
        if len(tag_content) > 0:
            item(tag_content[0].firstChild.data)

    def _update_host(self, item):
        """
        Retrieves information related to a network_device represented by its MAC address, e.g. the status of the network_device can be used for simple presence detection

        | Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/hostsSCPD.pdf
        | Also reference: https://blog.pregos.info/2015/11/07/anwesenheitserkennung-fuer-smarthome-mit-der-fritzbox-via-tr-064/

        :param item: item to be updated (Supported item avm_data_types: network_device, child item avm_data_types: device_ip, device_connection_type, device_hostname)
        """
        url = self._build_url("/upnp/control/hosts")
        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'network_device':
            if 'mac' not in item.conf:
                self.logger.error("No mac attribute provided in network_device item")
                return
            action = 'GetSpecificHostEntry'
            headers['SOAPACTION'] = "%s#%s" % (self._urn_map['Hosts'], action)
            soap_data = self._assemble_soap_data(action, self._urn_map['Hosts'], {'NewMACAddress': item.conf['mac']})
        else:
            self.logger.error(
                "Attribute %s not supported by plugin method" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        try:
            response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                          auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                              self._fritz_device.get_password()), verify=self._verify)
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when sending POST request: %s" % str(e))
            return

        tag_content = xml.getElementsByTagName('NewActive')
        if len(tag_content) > 0:
            item(tag_content[0].firstChild.data)
            for child in item.return_children():
                if 'avm_data_type' in child.conf:
                    if child.conf['avm_data_type'] == 'device_ip':
                        device_ip = xml.getElementsByTagName('NewIPAddress')
                        if len(device_ip) > 0:
                            if not device_ip[0].firstChild is None:
                                child(device_ip[0].firstChild.data)
                            else:
                                child('')
                        else:
                            self.logger.error(
                                "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                       'avm_data_type'))
                    elif child.conf['avm_data_type'] == 'device_connection_type':
                        device_connection_type = xml.getElementsByTagName('NewInterfaceType')
                        if len(device_connection_type) > 0:
                            if not device_connection_type[0].firstChild is None:
                                child(device_connection_type[0].firstChild.data)
                            else:
                                child('')
                        else:
                            self.logger.error(
                                "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                       'avm_data_type'))
                    elif child.conf['avm_data_type'] == 'device_hostname':
                        data = self._get_value_from_xml_node(xml, 'NewHostName')
                        if not data is None:
                            child(data)
                        else:
                            self.logger.error(
                                "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                       'avm_data_type'))
        else:
            item(0)
            self.logger.debug(
                "MAC Address not available on the FritzDevice - ID: %s" % self._fritz_device.get_identifier())

    def _update_home_automation(self, item):
        """
        Updates AVM home automation device related information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_homeauto.pdf

        :param item: item to be updated (Supported item avm_data_types: aha_device)
        """
        url = self._build_url("/upnp/control/x_homeauto")
        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
            action = 'GetSpecificDeviceInfos'
            headers['SOAPACTION'] = "%s#%s" % (self._urn_map['Homeauto'], action)
            soap_data = self._assemble_soap_data(action, self._urn_map['Homeauto'],
                                                 {'NewAIN': item.conf['ain'].strip()})
        else:
            self.logger.error(
                "Attribute %s not supported by plugin method" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        try:
            response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                          auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                              self._fritz_device.get_password()), verify=self._verify)
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when sending POST request or parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'aha_device':
            element_xml = xml.getElementsByTagName('NewSwitchState')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
                for child in item.return_children():
                    if 'avm_data_type' in child.conf:
                        if child.conf['avm_data_type'] == 'temperature':
                            temp = xml.getElementsByTagName('NewTemperatureCelsius')
                            if len(temp) > 0:
                                child(int(temp[0].firstChild.data))
                            else:
                                self.logger.error(
                                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                           'avm_data_type'))
                        elif child.conf['avm_data_type'] == 'power':
                            power = xml.getElementsByTagName('NewMultimeterPower')
                            if len(power) > 0:
                                child(int(power[0].firstChild.data))
                            else:
                                self.logger.error(
                                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                           'avm_data_type'))
                        elif child.conf['avm_data_type'] == 'energy':
                            energy = xml.getElementsByTagName('NewMultimeterEnergy')
                            if len(energy) > 0:
                                child(int(energy[0].firstChild.data))
                            else:
                                self.logger.error(
                                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf,
                                                                                                           'avm_data_type'))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_fritz_device_info(self, item):
        """
        Updates FritzDevice specific information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/deviceinfoSCPD.pdf

        :param item: Item to be updated (Supported item avm_data_types: uptime, software_version, hardware_version,serial_number, description)
        """
        url = self._build_url("/upnp/control/deviceinfo")
        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') in ['uptime', 'software_version', 'hardware_version',
                                                                'serial_number']:
            action = 'GetInfo'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['DeviceInfo'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['DeviceInfo'])

        if "dev_info_" + action not in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)
            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
                return
            self._response_cache["dev_info_" + action] = response.content
        else:
            self.logger.debug("Accessing DeviceInfo reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["dev_info_" + action])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'uptime':
            element_xml = xml.getElementsByTagName('NewUpTime')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'software_version':
            element_xml = xml.getElementsByTagName('NewSoftwareVersion')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'hardware_version':
            element_xml = xml.getElementsByTagName('NewHardwareVersion')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'serial_number':
            element_xml = xml.getElementsByTagName('NewSerialNumber')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_tam(self, item):
        """
        Updates telephone answering machine (TAM) related information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_tam.pdf

        :param item: item to be updated (Supported item avm_data_types: tam, child item avm_data_types: tam_name)
        """
        url = self._build_url("/upnp/control/x_tam")
        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') in ['tam', 'tam_name']:
            action = 'GetInfo'
        elif self.get_iattr_value(item.conf, 'avm_data_type') in ['tam_new_message_number', 'tam_total_message_number']:
            action = 'GetMessageList'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['TAM'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['TAM'], {'NewIndex': 0})

        if "tam_" + action not in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)
            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
                return
            self._response_cache["tam_" + action] = response.content
        else:
            self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["tam_" + action])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'tam':
            element_xml = xml.getElementsByTagName('NewEnable')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'tam_name':
            element_xml = xml.getElementsByTagName('NewName')
            if len(element_xml) > 0:
                item(element_xml[0].firstChild.data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') in ['tam_new_message_number', 'tam_total_message_number']:
            message_url_xml = xml.getElementsByTagName('NewURL')
            if len(message_url_xml) > 0:
                message_url = message_url_xml[0].firstChild.data

                if not "tam_messages" in self._response_cache:
                    try:
                        message_result = self._session.get(message_url, timeout=self._timeout, verify=self._verify)
                    except Exception as e:
                        self.logger.error("Exception when sending GET request: %s" % str(e))
                        return
                    self._response_cache["tam_messages"] = message_result.content
                else:
                    self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

                try:
                    message_xml = minidom.parseString(self._response_cache["tam_messages"])
                except Exception as e:
                    self.logger.error("Exception when parsing response: %s" % str(e))
                    return

                messages = message_xml.getElementsByTagName('Message')
                message_count = 0
                if len(messages) > 0:
                    if self.get_iattr_value(item.conf, 'avm_data_type') == 'tam_total_message_number':
                        message_count = len(messages)
                    elif self.get_iattr_value(item.conf, 'avm_data_type') == 'tam_new_message_number':
                        for message in messages:
                            is_new = message.getElementsByTagName('New')
                            if int(is_new[0].firstChild.data) == 1:
                                message_count = message_count + 1
                item(message_count)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_wlan_config(self, item):
        """
        Updates wlan related information, all items of this method need an numeric avm_wlan_index (typically 1-3)

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wlanconfigSCPD.pdf

        :param item: item to be updated (Supported item avm_data_types: wlanconfig, wlan_guest_time_remaining
        """
        if item.conf['avm_wlan_index']:
            if int(item.conf['avm_wlan_index']) > 0:
                url = self._build_url("/upnp/control/wlanconfig%s" % item.conf['avm_wlan_index'])
            else:
                self.logger.error('No wlan_index attribute provided')
        else:
            self.logger.error('No wlan_index attribute provided')

        headers = self._header.copy()

        if self.get_iattr_value(item.conf, 'avm_data_type') in ['wlanconfig', 'wlanconfig_ssid']:
            action = 'GetInfo'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wlan_guest_time_remaining':
            action = 'X_AVM-DE_GetWLANExtInfo'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        headers['SOAPACTION'] = "%s#%s" % (
        self._urn_map['WLANConfiguration'] % str(item.conf['avm_wlan_index']), action)
        soap_data = self._assemble_soap_data(action,
                                             self._urn_map['WLANConfiguration'] % str(item.conf['avm_wlan_index']))

        if not "wlanconfig_%s_%s" % (item.conf['avm_wlan_index'], action) in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)

            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
                return
            self._response_cache["wlanconfig_%s_%s" % (item.conf['avm_wlan_index'], action)] = response.content
        else:
            self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["wlanconfig_%s_%s" % (item.conf['avm_wlan_index'], action)])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'wlanconfig':
            newEnable = self._get_value_from_xml_node(xml, 'NewEnable')
            if newEnable is not None:
                item(newEnable)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wlanconfig_ssid':
            newSSID = self._get_value_from_xml_node(xml, 'NewSSID')
            if newSSID is not None:
                item(newSSID)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wlan_guest_time_remaining':
            element_xml = xml.getElementsByTagName('NewX_AVM-DE_TimeRemain')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_wan_dsl_interface_config(self, item):
        """
        Updates wide area network (WAN) speed related information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wandslifconfigSCPD.pdf

        :param item: item to be updated (Supported item avm_data_types: wan_upstream, wan_downstream)
        """
        if self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_upstream', 'wan_downstream']:
            action = 'GetInfo'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        url = self._build_url("/upnp/control/wandslifconfig1")

        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['WANDSLInterfaceConfig'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['WANDSLInterfaceConfig'])

        # if action has not been called in a cycle so far, request it and cache response
        if "wan_dsl_interface_config_" + action not in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)
            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
                return
            self._response_cache["wan_dsl_interface_config_" + action] = response.content
        else:
            self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["wan_dsl_interface_config_" + action])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_upstream':
            element_xml = xml.getElementsByTagName('NewUpstreamCurrRate')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_downstream':
            element_xml = xml.getElementsByTagName('NewDownstreamCurrRate')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_wan_common_interface_configuration(self, item):
        """
        Updates wide area network (WAN) related information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wancommonifconfigSCPD.pdf

        :param item: item to be updated (Supported item avm_data_types: wan_total_packets_sent, wan_total_packets_received, wan_total_bytes_sent, wan_total_bytes_received)
        """
        url = self._build_url("/upnp/control/wancommonifconfig1")

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_packets_sent':
            action = 'GetTotalPacketsSent'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_packets_received':
            action = 'GetTotalPacketsReceived'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_bytes_sent':
            action = 'GetTotalBytesSent'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_bytes_received':
            action = 'GetTotalBytesReceived'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_link':
            action = 'GetCommonLinkProperties'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['WANCommonInterfaceConfig'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['WANCommonInterfaceConfig'])

        # if action has not been called in a cycle so far, request it and cache response
        if "wan_common_interface_configuration_" + action not in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)
            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
                return
            self._response_cache["wan_common_interface_configuration_" + action] = response.content
        else:
            self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["wan_common_interface_configuration_" + action])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_packets_sent':
            element_xml = xml.getElementsByTagName('NewTotalPacketsSent')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_packets_received':
            element_xml = xml.getElementsByTagName('NewTotalPacketsReceived')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_bytes_sent':
            element_xml = xml.getElementsByTagName('NewTotalBytesSent')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_total_bytes_received':
            element_xml = xml.getElementsByTagName('NewTotalBytesReceived')
            if len(element_xml) > 0:
                item(int(element_xml[0].firstChild.data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_link':
            element_xml = xml.getElementsByTagName('NewPhysicalLinkStatus')
            if len(element_xml) > 0:
                if element_xml[0].firstChild.data == 'Up':
                    item(True)
                else:
                    item(False)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _update_wan_ip_connection(self, item):
        """
        Updates wide area network (WAN) IP related information

        Uses: http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wanipconnSCPD.pdf

        :param item: item to be updated (Supported item avm_data_types: wan_connection_status, wan_is_connected, wan_uptime, wan_ip)
        """
        url = self._build_url("/igdupnp/control/WANIPConn1")

        if self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_connection_status', 'wan_is_connected',
                                                                'wan_uptime', 'wan_connection_error']:
            action = 'GetStatusInfo'
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_ip':
            action = 'GetExternalIPAddress'
        else:
            self.logger.error("Attribute %s not supported by plugin" % self.get_iattr_value(item.conf, 'avm_data_type'))
            return

        headers = self._header.copy()
        headers['SOAPACTION'] = "%s#%s" % (self._urn_map['WANIPConnection'], action)
        soap_data = self._assemble_soap_data(action, self._urn_map['WANIPConnection'])

        # if action has not been called in a cycle so far, request it and cache response
        if "wan_ip_connection_" + action not in self._response_cache:
            try:
                response = self._session.post(url, data=soap_data, timeout=self._timeout, headers=headers,
                                              auth=HTTPDigestAuth(self._fritz_device.get_user(),
                                                                  self._fritz_device.get_password()),
                                              verify=self._verify)
            except Exception as e:
                self.logger.error("Exception when sending POST request: %s" % str(e))
            self._response_cache["wan_ip_connection_" + action] = response.content
        else:
            self.logger.debug("Accessing TAM reponse cache for action %s!" % action)

        try:
            xml = minidom.parseString(self._response_cache["wan_ip_connection_" + action])
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            return

        if self.get_iattr_value(item.conf, 'avm_data_type') in ['wan_connection_status', 'wan_is_connected']:
            data = self._get_value_from_xml_node(xml, 'NewConnectionStatus')
            if data is not None:
                if self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_connection_status':
                    item(data)
                elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_is_connected':
                    if data == 'Connected':
                        item(True)
                    else:
                        item(False)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_uptime':
            data = self._get_value_from_xml_node(xml, 'NewUptime')
            if data is not None:
                item(int(data))
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_connection_error':
            data = self._get_value_from_xml_node(xml, 'NewLastConnectionError')
            if data is not None:
                item(data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))
        elif self.get_iattr_value(item.conf, 'avm_data_type') == 'wan_ip':
            data = self._get_value_from_xml_node(xml, 'NewExternalIPAddress')
            if data is not None:
                item(data)
            else:
                self.logger.error(
                    "Attribute %s not available on the FritzDevice" % self.get_iattr_value(item.conf, 'avm_data_type'))

    def _get_value_from_xml_node(self, node, tag_name):
        data = None
        xml = node.getElementsByTagName(tag_name)
        if len(xml) > 0:
            if not xml[0].firstChild is None:
                data = xml[0].firstChild.data
        return data