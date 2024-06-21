#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
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
#########################################################################


import os
import logging
import json
import cherrypy

import lib.shyaml as shyaml

from .rest import RESTResource


class ConfigController(RESTResource):
    """
    Support for reading and writing the core's configuration (including modules)
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.etc_dir = self._sh._etc_dir
        self.modules_dir = os.path.join(self.base_dir, 'modules')

        self.core_conf = shyaml.yaml_load(os.path.join(self.modules_dir, 'core', 'module.yaml'))
        self.http_conf = shyaml.yaml_load(os.path.join(self.modules_dir, 'http', 'module.yaml'))
        self.websocket_conf = shyaml.yaml_load(os.path.join(self.modules_dir, 'websocket', 'module.yaml'))
        self.admin_conf = shyaml.yaml_load(os.path.join(self.modules_dir, 'admin', 'module.yaml'))
        self.mqtt_conf = shyaml.yaml_load(os.path.join(self.modules_dir, 'mqtt', 'module.yaml'))

        return


    def update_configdict(self, config_dict, data, section='unknown'):
        """
        Update loaded config dict from data received from the admin frontend
        """
        update_data = data.get(section, {}).get('data', {})
        for key in update_data:
            # self.logger.info("  - update: {}: {} = {}".format(section, key, update_data[key]))
            if update_data[key] is None:
                config_dict.pop(key, None)
            else:
                config_dict[key] = update_data[key]
        return


    # ======================================================================
    #  Read holidays
    #
    def read_holidays(self):
        self.holidays_confdata = shyaml.yaml_load(os.path.join(self.etc_dir, 'holidays.yaml'))
        if self.holidays_confdata.get('location', None) is not None:
            self.core_confdata['holidays_country'] = self.holidays_confdata['location'].get('country', '')
            self.core_confdata['holidays_province'] = self.holidays_confdata['location'].get('province', '')
            self.core_confdata['holidays_state'] = self.holidays_confdata['location'].get('state', '')

        for i in range(1,6):
            self.core_confdata['holidays_custom'+str(i)] = ''
        try:
            for i in range(1, 6):
                if isinstance(self.holidays_confdata['custom'][i-1], dict):
                    self.core_confdata['holidays_custom'+str(i)] = json.dumps(self.holidays_confdata['custom'][i-1])
                else:
                    self.core_confdata['holidays_custom' + str(i)] = self.holidays_confdata['custom'][i - 1]
        except:
            pass
        return


    # ======================================================================
    #  Update holidays
    #
    def update_holidays(self, data):
        filename = os.path.join(self.etc_dir, 'holidays.yaml')
        self.holidays_confdata = shyaml.yaml_load_roundtrip(filename)
        self.logger.info("update_holidays: self.holidays_confdata = '{}'".format(self.holidays_confdata))
        self.logger.info("update_holidays: data['common']['data'] = '{}'".format(data['common']['data']))

        if self.holidays_confdata.get('location', None) is None:
            self.holidays_confdata['location'] = {}

        self.holidays_confdata['location']['country'] = data['common']['data']['holidays_country']
        self.holidays_confdata['location']['province'] = data['common']['data']['holidays_province']
        self.holidays_confdata['location']['state'] = data['common']['data']['holidays_state']
        del data['common']['data']['holidays_country']
        del data['common']['data']['holidays_province']
        del data['common']['data']['holidays_state']

        if self.holidays_confdata.get('custom', None) is None:
            self.holidays_confdata['custom'] = []

        try:
            if len(self.holidays_confdata['custom']) > 5:
                for i in range(1, 6):
                    custom = data['common']['data']['holidays_custom' + str(i)]
                    if custom is not None and custom != '':
                        self.holidays_confdata['custom'][i-1] = custom
            else:
                self.holidays_confdata['custom'] = []
                for i in range(1, 6):
                    custom = data['common']['data']['holidays_custom' + str(i)]
                    if custom is not None and custom != '':
                        self.holidays_confdata['custom'].append(custom)

            for i in range(1, 6):
                del data['common']['data']['holidays_custom' + str(i)]
        except Exception as e:
            self.logger.critical("update_holidays: Exception {}".format(e))

        if self.holidays_confdata['custom'] == []:
            #self.holidays_confdata['custom'] = None
            del self.holidays_confdata['custom']

        if self.holidays_confdata['location']['state'] is None:
            del self.holidays_confdata['location']['state']

        self.logger.info("update_holidays: self.holidays_confdata = '{}'".format(self.holidays_confdata))
        shyaml.yaml_save_roundtrip(filename, self.holidays_confdata, create_backup=True)
        return


    # ======================================================================
    #  Handling of http REST requests
    #
    def read(self, id=None):
        """
        Handle GET requests
        """
        self.logger.info("ConfigController.read(): config = {}".format(id))

        self.core_confdata = shyaml.yaml_load(os.path.join(self.etc_dir, 'smarthome.yaml'))
        self.read_holidays()

        self.module_confdata = shyaml.yaml_load(os.path.join(self.etc_dir, 'module.yaml'))

        result = {}
        if (not id) or id == 'core':
            result['common'] = {}
            result['common']['data'] = self.core_confdata
            result['common']['meta'] = self.core_conf
            result['http'] = {}
            result['http']['data'] = self.module_confdata.get('http', {})
            result['http']['meta'] = self.http_conf
            result['websocket'] = {}
            result['websocket']['data'] = self.module_confdata.get('websocket', {})
            result['websocket']['meta'] = self.websocket_conf
            if result['websocket']['data'].get('enabled', None) is None:
                result['websocket']['data']['enabled'] = True
            result['admin'] = {}
            result['admin']['data'] = self.module_confdata.get('admin', {})
            result['admin']['meta'] = self.admin_conf
            result['mqtt'] = {}
            result['mqtt']['data'] = self.module_confdata.get('mqtt', {})
            if result['mqtt']['data'].get('enabled', None) is None:
                result['mqtt']['data']['enabled'] = True
            result['mqtt']['meta'] = self.mqtt_conf
            self.logger.info("  - index: core = {}".format(result))
            return json.dumps(result)

        if id == 'common':
            result['data'] = self.core_confdata
            result['meta'] = self.core_conf
            self.logger.info("  - index: common = {}".format(result))
            return json.dumps(result)

        if id == 'http':
            result['data'] = self.module_confdata.get('http', {})
            result['meta'] = self.http_conf
            self.logger.info("  - index: http = {}".format(result))
            return json.dumps(result)

        if id == 'websocket':
            result['data'] = self.module_confdata.get('websocket', {})
            result['meta'] = self.websocket_conf
            self.logger.info("  - index: http = {}".format(result))
            return json.dumps(result)

        if id == 'admin':
            result['data'] = self.module_confdata.get('admin', {})
            result['meta'] = self.admin_conf
            self.logger.info("  - index: admin = {}".format(result))
            return json.dumps(result)

        if id == 'mqtt':
            result['data'] = self.module_confdata.get('mqtt', {})
            if result['mqtt']['data'].get('enabled', None) is None:
                result['mqtt']['data']['enabled'] = True
            result['meta'] = self.mqtt_conf
            self.logger.info("  - index: admin = {}".format(result))
            return json.dumps(result)

        raise cherrypy.NotFound

    read.expose_resource = True
    read.authentication_needed = True


    @cherrypy.expose
    def update(self, id=None):
        """
        Handle PUT requests
        """
        self.logger.info("ConfigController() update: config {}".format(id))
        if id in ['common', 'http', 'admin', 'mqtt', 'core']:

            # get http headers
            cl = cherrypy.request.headers.get('Content-Length', 0)
            if cl == 0:
                raise cherrypy.HTTPError(status=411)
            rawbody = cherrypy.request.body.read(int(cl))
            data = json.loads(rawbody.decode('utf-8'))
            self.logger.info("  - update: data = {}".format(data))

            # update holidays and remove keys from self.core_confdata
            self.update_holidays(data)

            # update etc/smarthome.yaml with data from admin frontend
            self.core_confdata = shyaml.yaml_load_roundtrip(os.path.join(self.etc_dir, 'smarthome.yaml'))
            self.update_configdict(self.core_confdata, data, 'common')
            shyaml.yaml_save_roundtrip(os.path.join(self.etc_dir, 'smarthome.yaml'), self.core_confdata, create_backup=True)

            # update etc/module.yaml with data from admin frontend
            self.module_confdata = shyaml.yaml_load_roundtrip(os.path.join(self.etc_dir, 'module.yaml'))
            self.update_configdict(self.module_confdata['http'], data, 'http')
            self.update_configdict(self.module_confdata['admin'], data, 'admin')

            if self.module_confdata.get('websocket', None) is None:
                self.module_confdata['websocket'] = {}
                self.module_confdata['websocket']['module_name'] = 'websocket'
            self.update_configdict(self.module_confdata['websocket'], data, 'websocket')
            self.logger.info("Update: self.websocket_conf = {}".format(self.websocket_conf))
            if self.module_confdata['websocket'].get('enabled', None) is None:
                self.module_confdata['websocket']['enabled'] = True
            if self.module_confdata['websocket']['enabled']:
                self.module_confdata['websocket'].pop('enabled', None)
            #self.logger.warning("Update: ['websocket'] = {}".format(self.module_confdata['websocket']))
            #self.logger.warning("Update: - enabled = {}".format(self.module_confdata['websocket'].get('enabled', None)))

            if self.module_confdata.get('mqtt', None) is None:
                self.module_confdata['mqtt'] = {}
                self.module_confdata['mqtt']['module_name'] = 'mqtt'
            self.update_configdict(self.module_confdata['mqtt'], data, 'mqtt')
            self.logger.info("Update: self.mqtt_conf = {}".format(self.mqtt_conf))
            if self.module_confdata['mqtt'].get('enabled', None) is None:
                self.module_confdata['mqtt']['enabled'] = False
            if self.module_confdata['mqtt']['enabled']:
                self.module_confdata['mqtt'].pop('enabled', None)
            self.logger.info("Update: ['mqtt'] = {}".format(self.module_confdata['mqtt']))
            self.logger.info("Update: - enabled = {}".format(self.module_confdata['mqtt'].get('enabled', None)))
            shyaml.yaml_save_roundtrip(os.path.join(self.etc_dir, 'module.yaml'), self.module_confdata, create_backup=True)

            result = {"result": "ok"}
            return json.dumps(result)

        result = {"result": "error"}
        return json.dumps(result)

    update.expose_resource = True
    update.authentication_needed = True


    def REST_instantiate(self,param):
        """
        instantiate a REST resource based on the id

        this method MUST be overridden in your class. it will be passed
        the id (from the url fragment) and should return a model object
        corresponding to the resource.

        if the object doesn't exist, it should return None rather than throwing
        an error. if this method returns None and it is a PUT request,
        REST_create() will be called so you can actually create the resource.
        """
        return param

