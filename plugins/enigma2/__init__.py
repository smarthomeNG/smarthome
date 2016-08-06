#!/usr/bin/env python3
#
#########################################################################
#  Copyright 2016 René Frieß                        rene.friess(a)gmail.com
#  Version 1.1.11
#########################################################################
#  Free for non-commercial use
#
#  Plugin for the software SmartHomeNG, which allows to control and read
#  enigma2 compatible devices such as the VUSolo4k. For the API, the openwebif
#  needs to be installed.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import logging
import time
from xml.dom import minidom
import requests
from requests.packages import urllib3
from requests.auth import HTTPDigestAuth
from lib.model.smartplugin import SmartPlugin


class Enigma2Device():
    """
    This class encapsulates information related to a specific Enigma2Device, such has host, port, ssl, username, password, or related items
    """
    def __init__(self, host, port, ssl, username, password):
        self.logger = logging.getLogger(__name__)
        self._host = host
        self._port = port
        self._ssl = ssl
        self._username = username
        self._password = password
        self._items = []
        self._items_fast = []

    def get_identifier(self):
        """
        Returns the internal identifier of the Enigma2Device

        :return: identifier of the device, as set in plugin.conf
        """
        return self._identifier

    def get_host(self):
        """
        Returns the hostname / IP of the Enigma2Device

        :return: hostname of the device, as set in plugin.conf
        """
        return self._host

    def get_port(self):
        """
        Returns the port of the Enigma2Device

        :return: port of the device, as set in plugin.conf
        """
        return self._port

    def get_items(self):
        """
        Returns added items

        :return: array of items hold by the device
        """
        return self._items

    def get_fast_items(self):
        """
        Returns added items

        :return: array of items hold by the device
        """
        return self._items_fast

    def get_item_count(self):
        """
        Returns number of added items

        :return: number of items hold by the device
        """
        return (len(self._items)+len(self._items_fast))

    def is_ssl(self):
        """
        Returns information if SSL is enabled

        :return: is ssl enabled, as set in plugin.conf
        """
        return self._ssl

    def get_user(self):
        """
        Returns the user for the Enigma2Device

        :return: user, as set in plugin.conf
        """
        return self._username

    def get_password(self):
        """
        Returns the password for the Enigma2Device

        :return: password, as set in plugin.conf
        """
        return self._password

class Enigma2(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides the update functions for the Enigma2Device
    """
    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION = "1.1.11"

    _url_suffix_map = dict([('about','/web/about'),
                            ('deviceinfo', '/web/deviceinfo'),
                            ('epgservice', '/web/epgservice'),
                            ('getaudiotracks', '/web/getaudiotracks'),
                            ('getcurrent', '/web/getcurrent'),
                            ('message', '/web/message'),
                            ('messageanswer','/web/messageanswer'),
                            ('powerstate', '/web/powerstate'),
                            ('remotecontrol', '/web/remotecontrol'),
                            ('subservices', '/web/subservices'),
                            ('zap', '/web/zap'),
                            ('vol', '/web/vol')])

    _keys_fast_refresh = ['current_eventtitle','current_eventdescription','current_eventdescriptionextended',
                          'current_volume','e2servicename','e2videoheight','e2videowidth','e2apid','e2vpid',
                          'e2instandby','e2servicereference']
    _key_event_information = ['current_eventtitle','current_eventdescription','current_eventdescriptionextended','e2servicereference', 'e2servicename']

    def __init__(self, smarthome, username='', password='', host='dreambox', port='80', ssl='True', verify='False', cycle=300, fast_cycle=10): #, device_id='enigma2'
        """
        Initalizes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

        :param username:           Login name of user, cptional for devices which only support passwords
        :param password:           Password for the Enigma2Device
        :param host:               IP or host name of Enigma2Device
        :param port:               Port of the Enigma2Device (https: 49443, http: 49000)
        :param ssl:                True or False => https or http in URLs
        :param verify:             True or False => verification of SSL certificate
        :param cycle:              Update cycle in seconds
        """
        self.logger = logging.getLogger(__name__)
        #self.logger.info('Init Enigma2 Plugin with device_id %s' % )

        self._session = requests.Session()
        self._timeout = 10
        self._verify = self.to_bool(verify)

        ssl = self.to_bool(ssl)
        if ssl and not self._verify:
            urllib3.disable_warnings()

        self._enigma2_device = Enigma2Device(host, port, ssl, username, password)

        self._cycle = int(cycle)
        self._fast_cycle = int(fast_cycle)
        self._sh = smarthome

        # Response Cache: Dictionary for storing the result of requests which is used for several different items, refreshed each update cycle. Please use distinct keys!
        self._response_cache = dict()
        self._response_cache_fast = dict()

    def run(self):
        """
        Run method for the plugin
        """
        self._sh.scheduler.add(__name__ , self._update_loop, cycle=self._cycle)
        self._sh.scheduler.add(__name__ + "_fast", self._update_loop_fast, cycle=self._fast_cycle)
        self.alive = True

    def stop(self):
        """
        Stop method for the plugin
        """
        self.alive = False


    def _update_loop(self):
        """
        Starts the update loop for all known items.
        """
        self.logger.debug('Starting update loop for instance %s' % self.get_instance_name())
        for item in self._enigma2_device.get_items():
            if not self.alive:
                return
            self._update(item, cache = True, fast = False)

    def _update_loop_fast(self, cache = True, fast = True):
        """
        Starts the fast update loop for all known items.
        """
        self.logger.debug('Starting fast update loop for instance %s' % self.get_instance_name())
        for item in self._enigma2_device.get_fast_items():
            if not self.alive:
                return
            if self.get_iattr_value(item.conf, 'enigma2_data_type') in self._key_event_information:
                self._update_event_items(cache, fast)
            elif not self.get_iattr_value(item.conf, 'enigma2_page') is None:
                self._update(item, fast)
            elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'current_volume':
                self._update_volume(item, cache, fast)

        # empty response cache
        self._response_cache_fast = dict()

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized. Selects each item corresponding to
        the Enigma2 device id and adds it to an internal array

        :param item: The item to process.
        """

        # normal items
        if self.has_iattr(item.conf, "enigma2_page"):
            if self.get_iattr_value(item.conf, 'enigma2_page') in ['about', 'powerstate', 'subservices', 'deviceinfo']:
                if self.get_iattr_value(item.conf, 'enigma2_data_type') in self._keys_fast_refresh:
                    self._enigma2_device._items_fast.append(item)
                else:
                    self._enigma2_device._items.append(item)
        elif self.has_iattr(item.conf, "enigma2_data_type"):
            if self.get_iattr_value(item.conf, 'enigma2_data_type') in self._keys_fast_refresh:
                self._enigma2_device._items_fast.append(item)
            else:
                self._enigma2_device._items.append(item)
            if self.get_iattr_value(item.conf, 'enigma2_data_type') in ['current_volume', 'e2servicereference']:
                return self.execute_item
        elif self.has_iattr(item.conf, "enigma2_remote_command_id") or self.has_iattr(item.conf, "sref"):
            return self.execute_item

    def execute_item(self, item, caller=None, source=None, dest=None):
        """
        | Write items values - in case they were changed from somewhere else than the Enigma2 plugin
        | (=the Enigma2Device) to the Enigma2Device.

        :param item: item to be updated towards the Enigma2Device
        """
        if caller != 'Enigma2':
            # enigma2 remote control
            if self.has_iattr(item.conf, 'enigma2_remote_command_id'):
                self.remote_control_command(self.get_iattr_value(item.conf, 'enigma2_remote_command_id'))
                if self.get_iattr_value(item.conf, 'enigma2_remote_command_id') in ['105','106','116']:
                    self._update_event_items(cache = False)
            elif self.has_iattr(item.conf, 'sref'):
                self.zap(self.get_iattr_value(item.conf, 'sref'))
                self._update_event_items(cache = False)
            elif self.has_iattr(item.conf, 'enigma2_data_type'):
                if self.get_iattr_value(item.conf, 'enigma2_data_type') == 'current_volume':
                    self.set_volume(item())
                elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'e2servicereference':
                    self.zap(item())

    def box_request(self, suffix, parameter=''):
        """
        Send request to Enigma2 box, ret the answer and parse it

        :param suffix: url suffix, e.g. "/upnp/control/x_tam"
        :param parameter: optional parameter for the url
        :return: parsed xml result string
        """
        if self._enigma2_device.is_ssl():
            url = "https"
        else:
            url = "http"
        url += "://%s:%s%s?%s" % (self._enigma2_device.get_host(), self._enigma2_device.get_port(), suffix, parameter)

        try:
            response = self._session.get(url, timeout=self._timeout,
                                         auth=HTTPDigestAuth(self._enigma2_device.get_user(),
                                                             self._enigma2_device.get_password()), verify=self._verify)

        except Exception as e:
            self.logger.error("Exception when sending GET request: {0}".format(str(e)))
            return minidom.parseString('<noanswer/>')

        try:
            xml = minidom.parseString(response.content)
        except Exception as e:
            self.logger.error("Exception when parsing response: %s" % str(e))
            xml = minidom.parseString('<noanswer/>')
        return xml
    
    def remote_control_command(self, command_id):
        xml = self.box_request(self._url_suffix_map['remotecontrol'], 'command=%s' % command_id)

        e2result_xml = xml.getElementsByTagName('e2result')
        e2resulttext_xml = xml.getElementsByTagName('e2resulttext')
        if (len(e2resulttext_xml) > 0 and len(e2result_xml) > 0):
            if not e2resulttext_xml[0].firstChild is None and not e2result_xml[0].firstChild is None:
                if e2result_xml[0].firstChild.data == 'True':
                    self.logger.debug(e2resulttext_xml[0].firstChild.data)

    def get_audio_tracks(self):
        """
        Retrieves an array of all available audio tracks
        
        :param result: Array of audiotracks with keys: 'e2audiotrackdescription', 'e2audiotrackid', 'e2audiotrackpid', 'e2audiotrackactive'
        """
        result = []
        xml = self.box_request(self._url_suffix_map['getaudiotracks'])

        e2audiotrack_xml = xml.getElementsByTagName('e2audiotrack')
        if (len(e2audiotrack_xml)) > 0:
            for audiotrack_entry_xml in e2audiotrack_xml:
                result_entry = {}
                e2audiotrackdescription_xml = audiotrack_entry_xml.getElementsByTagName('e2audiotrackdescription')

                if (len(e2audiotrackdescription_xml)) > 0:
                    result_entry['e2audiotrackdescription'] = e2audiotrackdescription_xml[0].firstChild.data

                e2audiotrackid_xml = audiotrack_entry_xml.getElementsByTagName('e2audiotrackid')
                if (len(e2audiotrackid_xml)) > 0:
                    result_entry['e2audiotrackid'] = int(e2audiotrackid_xml[0].firstChild.data)

                e2audiotrackpid_xml = audiotrack_entry_xml.getElementsByTagName('e2audiotrackpid')
                if (len(e2audiotrackpid_xml)) > 0:
                    result_entry['e2audiotrackpid'] = int(e2audiotrackpid_xml[0].firstChild.data)

                e2audiotrackactive_xml = audiotrack_entry_xml.getElementsByTagName('e2audiotrackactive')
                if (len(e2audiotrackactive_xml)) > 0:
                    if e2audiotrackactive_xml[0].firstChild.data in 'True':
                        result_entry['e2audiotrackactive'] = True
                    else:
                        result_entry['e2audiotrackactive'] = False

                result.append(result_entry)

        return result

    def zap(self, e2servicereference, title=''):
        """
        Zaps to another service by a given e2servicereference

        :param e2servicereference: reference to the service
        :param title: optional title of "zap" action
        """
        xml = self.box_request(self._url_suffix_map['zap'], 'sRef=%s&title=%s' % (e2servicereference, title))

        e2state_xml = xml.getElementsByTagName('e2state')
        e2statetext_xml = xml.getElementsByTagName('e2statetext')
        if (len(e2statetext_xml) > 0 and len(e2state_xml) > 0):
            if not e2statetext_xml[0].firstChild is None and not e2state_xml[0].firstChild is None:
                if e2state_xml[0].firstChild.data == 'True':
                    self.logger.debug(e2statetext_xml[0].firstChild.data)

    def set_volume(self, value):
        """
        Sets the volume to a specific value

        :param value: value of the volume (int from 0 to 100)
        """
        xml = self.box_request(self._url_suffix_map['vol'], 'set=set%s' % (value))

        e2result_xml = xml.getElementsByTagName('e2result')
        e2resulttext_xml = xml.getElementsByTagName('e2resulttext')
        if len(e2resulttext_xml) > 0 and len(e2result_xml) > 0:
            if not e2resulttext_xml[0].firstChild is None and not e2result_xml[0].firstChild is None:
                if e2result_xml[0].firstChild.data == 'True':
                    self.logger.debug(e2resulttext_xml[0].firstChild.data)

    def send_message(self, messagetext, messagetype=1, timeout=10):
        """
        Sends a message to the Enigma2 Device
        
        messagetext=Text of Message
        messagetype=Number from 0 to 3, 0= Yes/No, 1= Info, 2=Message, 3=Attention
        timeout=Can be empty or the Number of seconds the Message should disappear after.
        """
        xml = self.box_request(self._url_suffix_map['message'],'text=%s&type=%s&timeout=%s' % (messagetext, messagetype, timeout))

        e2result_xml = xml.getElementsByTagName('e2result')
        e2resulttext_xml = xml.getElementsByTagName('e2resulttext')
        if len(e2resulttext_xml) > 0 and len(e2result_xml) >0:
            if not e2resulttext_xml[0].firstChild is None and not e2result_xml[0].firstChild is None:
                if e2result_xml[0].firstChild.data == 'True':
                    self.logger.debug(e2resulttext_xml[0].firstChild.data)
                    
    def get_answer(self):
        """
        Retrieves the answer to a currently sent message, take care to take the timeout into account in which the answer can be given and start a thread which is polling the answer for that period.
        """
        xml = self.box_request(self._url_suffix_map['message'],'getanswer=now')

        e2result_xml = xml.getElementsByTagName('e2state')
        e2resulttext_xml = xml.getElementsByTagName('e2statetext')
        if (len(e2resulttext_xml) > 0 and len(e2result_xml) >0):
            if not e2resulttext_xml[0].firstChild is None and not e2result_xml[0].firstChild is None:
                self.logger.debug(e2resulttext_xml[0].firstChild.data)
                if e2result_xml[0].firstChild.data == 'True':                    
                    return e2resulttext_xml[0].firstChild.data

    def _update_event_items(self, cache = True, fast = False):
        for item in self._enigma2_device.get_fast_items():
            if self.get_iattr_value(item.conf, 'enigma2_data_type') in self._key_event_information:
                self._update_current_event(item, cache, fast)

    def _update_volume(self, item, cache = True, fast = False): #todo add cache
        """
        Retrieves the current volume value and sets it to an item.
        
        :param item: item to be updated
        """
        xml = self.box_request(self._url_suffix_map['getcurrent'])

        volume = self._get_value_from_xml_node(xml, 'e2current')
        #self.logger.debug("Volume "+volume)
        item(volume)

    def _update_current_event(self, item, cache = True, fast = False):
        """
        Updates information on the current event

        :param item: item to be updated
        """
        if self.get_iattr_value(item.conf, 'enigma2_data_type') is None:
            self.logger.error("No enigma2_data_type set in item!")
            return

        xml = self._cached_get_request('subservices', self._url_suffix_map['subservices'], '', cache, fast)

        e2servicereference = 'N/A'
        test_xml = xml.getElementsByTagName('noanswer')
        if len(test_xml) == 0:
            element_xml = xml.getElementsByTagName('e2servicereference')
            if len(element_xml) > 0:
                e2servicereference = element_xml[0].firstChild.data
            else:
                e2servicereference = ''
                self.logger.error("Attribute %s not available on the Enigma2Device" % self.get_iattr_value(item.conf, 'enigma2_data_type'))

        if not e2servicereference == 'N/A' and '1:0:0:0:0:0:0:0:0:0' not in e2servicereference:
            current_epgservice = self.get_current_epgservice_for_service_reference(e2servicereference, cache, fast)
        else:
            current_epgservice = {}

        if self.get_iattr_value(item.conf, 'enigma2_data_type') == 'e2servicename':
            e2servicename = self._get_value_from_xml_node(xml, 'e2servicename')
            if e2servicename is None or e2servicename == 'N/A':
                e2servicename = '-'
            item(e2servicename)
        elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'e2servicereference':
            if e2servicereference is None or e2servicereference == 'N/A':
                servicereference = '-'
            else:
                servicereference = e2servicereference
            item(servicereference)
        elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'current_eventtitle':
            if 'e2eventtitle' in current_epgservice:
               item(current_epgservice['e2eventtitle'])
            else:
                item('-')
        elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'current_eventdescription':
            if 'e2eventdescription' in current_epgservice:
                item(current_epgservice['e2eventdescription'])
            else:
                item('-')
        elif self.get_iattr_value(item.conf, 'enigma2_data_type') == 'current_eventdescriptionextended':
            if 'e2eventdescriptionextended' in current_epgservice:
                item(current_epgservice['e2eventdescriptionextended'])
            else:
                item('-')

    def get_current_epgservice_for_service_reference(self, service_reference, cache=True, fast=False):
        """
        Retrieves event information for a given service reference id

        :param referece of the service to retrieve data for:
        :return: dict of result data
        """
        xml = self._cached_get_request('epgservice', self._url_suffix_map['epgservice'], 'sRef=%s' % service_reference, cache, fast)
            
        e2event_list_xml = xml.getElementsByTagName('e2event')
        result_entry = {}
        if (len(e2event_list_xml) > 0):
            e2eventdescription = self._get_value_from_xml_node(e2event_list_xml[0], 'e2eventdescription')
            if e2eventdescription is None:
                e2eventdescription = '-'
            result_entry['e2eventdescription'] = e2eventdescription

            e2eventdescriptionextended = self._get_value_from_xml_node(e2event_list_xml[0], 'e2eventdescriptionextended')
            if e2eventdescriptionextended is None:
                e2eventdescriptionextended = '-'
            result_entry['e2eventdescriptionextended'] = e2eventdescriptionextended

            e2eventtitle = self._get_value_from_xml_node(e2event_list_xml[0], 'e2eventtitle')
            if e2eventtitle is None:
                e2eventtitle = '-'
            result_entry['e2eventtitle'] = e2eventtitle

        return result_entry

    def _update(self, item, cache = True, fast = True):
        """
        Updates information on diverse items

        :param item: item to be updated
        :param cache: cache for request true or false
        """

        if self.get_iattr_value(item.conf, 'enigma2_data_type') is None:
            self.logger.error("No enigma2_data_type set in item!")
            return

        xml = self._cached_get_request(self.get_iattr_value(item.conf, 'enigma2_page'), self._url_suffix_map[self.get_iattr_value(item.conf, 'enigma2_page')], '', cache, fast)

        if "/" in self.get_iattr_value(item.conf, 'enigma2_data_type'):
            strings = self.get_iattr_value(item.conf, 'enigma2_data_type').split('/')
            parent_element_xml = xml.getElementsByTagName(strings[0])
            if len(parent_element_xml) > 0:
                element_xml = parent_element_xml[0].getElementsByTagName(strings[1])
            else:
                self.logger.info("Attribute %s not available on the Enigma2Device" % self.get_iattr_value(item.conf, 'enigma2_data_type'))
                return
        else:
            element_xml = xml.getElementsByTagName(self.get_iattr_value(item.conf, 'enigma2_data_type'))

        if (len(element_xml) > 0):
            # self.logger.debug(element_xml[0].firstChild.data)
            if item.type() == 'bool':
                if not element_xml[0].firstChild is None:
                    if element_xml[0].firstChild.data == 'true' or element_xml[0].firstChild.data == 'True':
                        item(1)
                    else:
                        item(0)
            elif item.type() == 'num':
                if not element_xml[0].firstChild is None:
                    if self.is_int(element_xml[0].firstChild.data):
                        item(int(element_xml[0].firstChild.data))
                    elif self.is_float(element_xml[0].firstChild.data):
                        item(float(element_xml[0].firstChild.data))
                    elif self.get_iattr_value(item.conf, 'enigma2_data_type') in ['e2capacity', 'e2free']:
                        #self.logger.debug(element_xml[0].firstChild.data)
                        item(int(''.join(filter(lambda s: s.isdigit() or (s.startswith('-') and s[1:].isdigit()), element_xml[0].firstChild.data))))  # remove "GB" String and convert to int
                else:
                    item(0) # 0 if no value is provided
            else:
                if not element_xml[0].firstChild is None:
                    if element_xml[0].firstChild.data == "N/A":
                        item("-")
                    else:
                        item(element_xml[0].firstChild.data)
                else:
                    item("-")
        else:
            self.logger.info("Attribute %s not available on the Enigma2Device" % self.get_iattr_value(item.conf, 'enigma2_data_type'))

    #helper functions below

    def _cached_get_request(self, cache_key, urlpart, parameter='', cache=True, fast=False):
        if not fast:
            response_cache = self._response_cache
        else:
            response_cache = self._response_cache_fast

        if cache_key not in response_cache or not cache:
            xml = self.box_request(urlpart, parameter)

            if not fast:
                self.logger.debug("Filling reponse cache for %s!" % urlpart)
            else:
                self.logger.debug("Filling fast reponse cache for %s!" % urlpart)

            response_cache[cache_key] = xml
            return xml
        else:
            if not fast:
                self.logger.debug("Accessing reponse cache for %s!" % urlpart)
            else:
                self.logger.debug("Accessing fast reponse cache for %s!" % urlpart)
            return response_cache[cache_key]

    def _get_value_from_xml_node(self, node, tag_name):
        data = None
        xml = node.getElementsByTagName(tag_name)
        if (len(xml) > 0):
            if not xml[0].firstChild is None:
                data = xml[0].firstChild.data
        return data
