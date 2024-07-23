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
import shutil
import logging
import json
import cherrypy

import lib.shyaml as shyaml
import lib.config
from lib.module import Modules
from lib.plugin import Plugins
from lib.metadata import Metadata
from lib.model.smartplugin import SmartPlugin
from lib.constants import (KEY_CLASS_PATH, YAML_FILE, DIR_PLUGINS)

from .rest import RESTResource


class PluginController(RESTResource):

    def __init__(self, module, jwt_secret=False):
        self._sh = module._sh
        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])
        self.logger.info("PluginController(): __init__")
        self.plugins = Plugins.get_instance()

        self.plugin_data = {}
        self.jwt_secret = jwt_secret
        return


    def get_body(self):
        """
        Get content body of received request header

        :return:
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            # cherrypy.reponse.headers["Status"] = "400"
            # return 'Bad request'
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.debug("PluginController(): ___(): rawbody = {}".format(rawbody))
        try:
            params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning("PluginController(): ___(): Exception {}".format(e))
            return None
        return params


    def test_for_old_config(self, config_filename):
        # make it 'readonly', if plugin.conf is used
        result = not(os.path.splitext(config_filename)[1].lower() == '.yaml')

        _etc_dir = os.path.dirname(config_filename)
        if not result:
            # for beta-testing: create a backup of ../etc/plugin.yaml
            if not os.path.isfile(os.path.join(_etc_dir, 'plugin_before_admin_config.yaml')):
                shutil.copy2(config_filename, os.path.join(_etc_dir, 'plugin_before_admin_config.yaml'))
                self.logger.warning('Created a backup copy of plugin.yaml ({})'.format(os.path.join(_etc_dir, 'plugin_before_admin_config.yaml')))

        return result


    def get_config_filename(self):

        if self.plugins is None:
            self.plugins = Plugins.get_instance()

        return self.plugins._get_plugin_conf_filename()



    # ======================================================================
    #  GET /api/plugin
    #
    def read(self, id=None):
        """
        return an object with type info about all installed plugins
        """
        self.logger.info("PluginController(): index('{}')".format(id))

        config_filename = self.get_config_filename()

        info = {}
        info['_readonly'] = self.test_for_old_config(config_filename)

        # get path to plugin configuration file, without extension
        _conf = lib.config.parse_basename(os.path.splitext(config_filename)[0], configtype='plugin')

        plg_found = False
        if id is not None:
            for confplg in _conf:
                if (confplg == id) or (id == None):
                    self.logger.info(f"PluginController(): index('{id}') - confplg {confplg}")
                    info['config'] = _conf[confplg]
                    plg_found = True

            if plg_found:
                return json.dumps(info)

        raise cherrypy.NotFound

    read.expose_resource = True
    read.authentication_needed = True


    def add(self, id=None):
        self.logger.info("PluginController(): add('{}')".format(id))

        params = self.get_body()
        if params is None:
            self.logger.warning("PluginController(): add(): section '{}': Bad, add request".format(id))
            raise cherrypy.HTTPError(status=411)
        self.logger.info("PluginController(): add(): section '{}' = {}".format(id, params))

        config_filename = self.get_config_filename()

        if self.test_for_old_config(config_filename):
            # make it 'readonly', if plugin.conf is used
            response = {'result': 'error', 'description': 'Updateing .CONF files is not supported'}
        else:
            response = {}
            plugin_conf = shyaml.yaml_load_roundtrip(config_filename)
            sect = plugin_conf.get(id)
            if sect is not None:
                response = {'result': 'error', 'description': "Configuration section '{}' already exists".format(id)}
            else:
                plugin_conf[id] = params.get('config', {})
                shyaml.yaml_save_roundtrip(config_filename, plugin_conf, False)
                response = {'result': 'ok'}

        self.logger.info("PluginController(): add(): response = {}".format(response))
        return json.dumps(response)

    add.expose_resource = True
    add.authentication_needed = True


    def handle_plugin_action(self, id, action):

        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        plugin = self.plugins.return_plugin(id)
        if plugin is None:
            response = {'result': 'error', 'description': "No running plugin instance found for '{}'".format(id)}
            return response

        response = {}
        if action == 'start':
            self.logger.info("PluginController.handle_plugin_action(): Starting plugin '{}'".format(id))
            plugin.run()
            response = {'result': 'ok'}

        elif action == 'stop':
            self.logger.info("PluginController.handle_plugin_action(): Stopping plugin '{}'".format(id))
            plugin.stop()
            response = {'result': 'ok'}

        return response


    def update(self, id='', action=''):
        self.logger.info("PluginController.update(id='{}', action='{}')".format(id, action))

        if action == '':
            # Update section for plugin in etc/plugin.yaml
            params = self.get_body()
            if params is None:
                self.logger.warning("PluginController.update(): section '{}': Bad, add request".format(id))
                raise cherrypy.HTTPError(status=411)
            self.logger.info("PluginController.update(): section '{}' = {}".format(id, params))

            config_filename = self.get_config_filename()

            if self.test_for_old_config(config_filename):
                # make it 'readonly', if plugin.conf is used
                response = {'result': 'error', 'description': 'Updateing .CONF files is not supported'}
            else:
                response = {}
                plugin_conf = shyaml.yaml_load_roundtrip(config_filename)
                sect = plugin_conf.get(id)
                if sect is None:
                    response = {'result': 'error', 'description': "Configuration section '{}' does not exist".format(id)}
                else:
                    self.logger.debug("update: params = {}".format(params))
                    if params.get('config', {}).get('plugin_enabled', None) == True:
                        del params['config']['plugin_enabled']
                    plugin_conf[id] = params.get('config', {})
                    shyaml.yaml_save_roundtrip(config_filename, plugin_conf, False)
                    response = {'result': 'ok'}
        elif action in ['start','stop']:
            response = self.handle_plugin_action(id, action)
        else:
            response = {'result': 'error', 'description': "Plugin '{}': unknown action '{}'".format(id, action)}
            self.logger.warning("PluginController.update(): " + response['description'])

        self.logger.info("PluginController.update(): response = {}".format(response))
        return json.dumps(response)

    update.expose_resource = True
    update.authentication_needed = True


    @cherrypy.expose
    def delete(self, id=None):
        self.logger.info("PluginController(): delete('{}')".format(id))

        config_filename = self.get_config_filename()

        if self.test_for_old_config(config_filename):
            # make it 'readonly', if plugin.conf is used
            response = {'result': 'error', 'description': 'Updateing .CONF files is not supported'}
        else:
            response = {}
            plugin_conf = shyaml.yaml_load_roundtrip(config_filename)
            sect = plugin_conf.pop(id, None)
            if sect is None:
                response = {'result': 'error', 'description': "Configuration section '{}' does not exist".format(id)}
            else:
                shyaml.yaml_save_roundtrip(config_filename, plugin_conf, False)
                response = {'result': 'ok'}

        self.logger.info("PluginController(): delete(): response = {}".format(response))
        return json.dumps(response)

    delete.expose_resource = True
    delete.authentication_needed = True

