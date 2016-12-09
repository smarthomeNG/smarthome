#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
#  This file is part of SmartHomeNG.   https://github.com/smarthomeNG/
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
#

import base64
import http.client
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from lib.model.smartplugin import SmartPlugin

__ETA_PU__ = 'eta_pu'
__ETA_ERROR__ = 'eta_pu_error'
__ETA_URI__ = 'eta_pu_uri'
__ETA_TYPE__ = 'eta_pu_type'

class EtaValue():
    def __init__(self, xml_item):
        self.logger = logging.getLogger(__name__)
        self.value = xml_item.text
        self.str_value = xml_item.attrib['strValue']
        self.unit = xml_item.attrib['unit']
        self.dec_places = int(xml_item.attrib['decPlaces'])
        self.scale_factor = int(xml_item.attrib['scaleFactor'])
        self.adv_text_offset = int(xml_item.attrib['advTextOffset'])

    def valueFromString(self, str_value):
        value = str_value.lower()
        if value in ('off', 'false'):
            return 0
        elif value in ('on', 'true'):
            return 1
        return None

    def get_data(self, uri, str_value):
        value = 0
        try:
            value = int(str_value) # FIXME
        except:
            value = self.valueFromString(str_value)
            if value is None:
                self.logger.error("unhandled strValue {0} for {1}".format(str_value, uri))
                return None
        data = value * self.scale_factor + self.adv_text_offset
        return data
'''
Little helper for PUT, DELETE, POST and GET request
'''
class Request():
    def __init__(self, address, port):
        self.address = address
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.timeout = 2

    def __request__(self, req_type, url, username=None, password=None, value=None):
        lurl = url.split('/')
        # extract HOST http(s)://HOST/path/...
        host = lurl[2]
        # rebuild path from parts
        purl = '/' + '/'.join(lurl[3:])
        # select protocol: http or https
        if url.startswith('https'):
            conn = http.client.HTTPSConnection(host, timeout=self.timeout)
        else:
            conn = http.client.HTTPConnection(host, timeout=self.timeout)
        # add headers
        hdrs = {'Accept': 'text/plain'}
        if username and password:
            hdrs['Authorization'] = 'Basic ' + base64.b64encode(username + ':' + password)

        if 'POST' == req_type:
            data = urllib.parse.urlencode({'value': value})
            data = data.encode('utf-8')
            request = urllib.request.Request(url)
            # adding charset parameter to the Content-Type header.
            request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
            f = urllib.request.urlopen(request, data)
            if f.status in (http.client.OK, http.client.CREATED):
                return f.read().decode('utf-8')
                self.logger.warning("request failed: {0}: ".format(url))
                # self.logger.debug("{0} response: {1} {2}".format(req_type, f.status, f.reason))
            return None
        elif 'PUT' == req_type:
            conn.request(req_type, purl, body=value, headers=hdrs)
        else:  # 'GET' or 'DELETE'
            conn.request(req_type, purl, headers=hdrs)
        resp = conn.getresponse()
        conn.close()
        # success status: 201/Created for PUT request, else 200/Ok
        if resp.status in (http.client.OK, http.client.CREATED):
            return resp.read()
        self.logger.warning("request failed for: {0}: ".format(url))
        # self.logger.debug("{0} response: {1} {2}".format(req_type, resp.status, resp.reason))
        return None

    def send(self, req_type, path, uri='', value=''):
        url = 'http://{0}:{1}{2}'.format(self.address, self.port, path)
        if uri:
            url += uri
        return self.__request__(req_type, url, value=value)

'''
The ETA_PU plugin class.
'''
class ETA_PU(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.1"

    def __init__(self, smarthome, address, port, setpath, setname):
        self._sh = smarthome
        self._cycle = 30
        self.logger = logging.getLogger(__name__)
        self._uri = dict()
        self._error = None
        self._objects = dict()
        self._request = Request(address, port)
        self._request.timeout = 2
        self._setpath = setpath
        self._setname = setname

    def run(self):
        self.rebuild_set()
        self._sh.scheduler.add(__ETA_PU__, self.update_status, cycle=self._cycle)
        self.alive = True


    def rebuild_set(self):
        try:
            self.del_set(self._setname)
            self.add_set(self._setname)
            self.fill_set(self._setname)
        except:
            self.logger.error('Failed to rebuild.. ETA offline?')
 
    '''
    add the list of URIs to an existing varset
    '''
    def fill_set(self, var_set):
        for uri in self._uri:
            path = '/'.join((self._setpath, var_set, uri))
            rc = 'OK'
            if None is self._request.send('PUT', path):
                rc = 'FAILED'
            self.logger.info('adding to ETA var_set {0}: {1}'.format(path, rc))

    def stop(self):
        self.alive = False

    '''
    delete the default uri-set
    '''
    def del_set(self, name):
        rc = 'OK'
        if None is self._request.send('DELETE', '{0}/{1}'.format(self._setpath, name)):
            rc = 'FAILED'
        self.logger.info("deleting ETA var_set {0}: {1}".format(name, rc))

    '''
    add an empty uri-set
    '''
    def add_set(self, name):
        rc = 'OK'
        if None is self._request.send('PUT', '{0}/{1}'.format(self._setpath, name)):
            rc = 'FAILED'
        self.logger.info("adding gew var_set {0}: {1}".format(name, rc))

    '''
    read uri from parent item
    '''
    def _get_uri(self, item):
        parent_item = item.return_parent()
        if parent_item is None:
            self.logger.error("skipping item: no parent with 'eta_pu_uri' found")
            return None
        if False == (__ETA_URI__ in parent_item.conf):
            return self._get_uri(parent_item)
        return parent_item.conf[__ETA_URI__]

    '''
    parse conf file
    '''
    def parse_item(self, item):
        if __ETA_TYPE__ in item.conf:
            return self.parse_type(item)
        if __ETA_ERROR__ in item.conf:
            self.parse_error(item)
        return None

    '''
    parse variables to observe:
        looking for eta_pu_type with parent having eta_pu_uri set
        returning a function that can be used to set the value of the variable
    '''
    def parse_type(self, item):
        uri = self._get_uri(item).strip('/')
        if uri:
            if uri not in self._uri:
                self._uri[uri] = []
            self._uri[uri].append(item)
        return self.update_var_item

    '''
    parse fub_uris of the subsystems to observe:
        to obtain the errors of a subsystem
        entries containing eta_pu_fub = <fub_uri_of_the_subsystem>
    '''
    def parse_error(self, item):
        self._error = item

    '''
    update function for variables
    '''
    def update_var_item(self, item, caller=None, source=None, dest=None):
        if caller == __ETA_PU__:
            return
        if item.conf[__ETA_TYPE__] == 'calc':
            # self.logger.debug('Write to ETA_PU...{} {} {}'.format(caller,source,dest))
            uri = self._get_uri(item)
            if uri:
                data = self._objects[uri].get_data(uri,item())
                self.logger.debug('write to ETA_PU: {}'.format(data))
                self._request.send('POST', '/user/var/', uri, data)

    '''
    request an uri and return the xml response
    '''
    def fetch_xml(self, uri):
        url = 'http://{0}:{1}{2}'.format(self._request.address, self._request.port, uri)
        xml = self._sh.tools.fetch_url(url, timeout=2)
        try:
                return ET.fromstring(xml)
        except:
                self.logger.error('can not parse response from ETA')
        return None

    '''
    helper function called by update status
    called periodically to update the var_items
    '''

    def update_var_status(self):
        try:
            self._objects.clear()
            # fetch response
            response = self.fetch_xml('{0}/{1}'.format(self._setpath, self._setname))
            if response is None:
                return
            for uri in self._uri.keys():
                element = response.find(".//*[@uri='%s']" % uri)
                if element is None:
                     self.logger.error('element not found: {}'.format(uri))
                     continue
                # store parameters needed when update_var_item is called
                self._objects[uri] = EtaValue(element)
                self.logger.debug('looking for {} in respones'.format(uri))
                for item in self._uri[uri]:
                    self.logger.debug('update item {}'.format(uri))
                    # update item value
                    # self.logger.debug(str(item.conf))
                    if item.conf[__ETA_TYPE__] == 'calc':
                        value = int(element.text) / int(element.attrib['scaleFactor'])- int(element.attrib['advTextOffset'])
                    else:
                        value = element.attrib[item.conf[__ETA_TYPE__]]
                    if isinstance(item, str):
                        value = value.replace(',', '.')
                    item(value, caller=__ETA_PU__)
        except:
            self.logger.error('Update var failed, trying to rebuild varset...')
            self.rebuild_set()

    '''
    helper function called by update status
    called periodically to retrieve the list of errors
    '''
    def update_errors(self):
        response = self.fetch_xml('/user/errors')
        if response is None:
            return
        text = ''
        for errors in response:
            for fub in errors:
                # self.logger.info("Suche Fehlermeldung in Subsys: {}".format(fub.attrib['name']))
                for error in fub:
                    # concatenate error strings
                    text = '{0}{1} {2} {3} {4}\n'.format(
                            text, error.attrib['time'], error.attrib['priority'],
                            error.attrib['msg'], error.text)
            self.logger.info("Error Message from ETA: {}".format(text))
        # update the item
        if self._error is not None:
            self._error(text, caller=__ETA_PU__)

        # for all fub_/subsystem_URIs
        #for fub in self._errors.keys():
        #    # find element with that fub_URI
        #    element = response.find(".//*[@uri='%s']" % fub)
        #    self.logger.debug('looking for {} in respones'.format(fub))
        #    if element is None:
        #        return
        #    # extract errors
        #    text = ''
        #    for error in element:
        #        # concatenate error strings
        #        text = '{0}{1} {2} {3} {4}\n'.format(
        #                text, error.attrib['time'], error.attrib['priority'],
        #                error.attrib['msg'], error.text)
        #    self.logger.info("Fehlermeldung: {}".format(text))
        #    # update the item
        #    self._errors[fub](text, caller=__ETA_PU__)

    '''
    called periodically to update the items
    '''
    def update_status(self):
        self.update_var_status()
        self.update_errors()

