#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  Backend plugin for SmartHomeNG
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

import os
import shutil
import json

import cherrypy

import lib.shyaml as shyaml
import lib.config
from lib.plugin import Plugins
from lib.metadata import Metadata
from lib.model.smartplugin import SmartPlugin
from lib.constants import (KEY_CLASS_PATH, YAML_FILE)


class PluginData:

    def __init__(self):

        self.plugins = Plugins.get_instance()

        return


    # -----------------------------------------------------------------------------------
    #    PLUGINS  -  Interface methods (for admin frontend)
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def plugin_set_config_html(self, plugin_section='', config=''):
        """
        Is called by items.html when an item value has been changed

        plugin_set_config.html?plugin_section=' + pluginsection + '&config=' + configstr;
        """
        if config == '':
            self.logger.error("plugin_set_config_html: 'config' not specified")
            return 'false'
        if plugin_section == '':
            self.logger.error("plugin_set_config_html: 'plugin_section' not specified")
            return 'false'

        self.logger.warning("plugin_set_config_html: pluginconfig '{}' set to '{}'".format(plugin_section, config))

        # to do:
        # - load etc/plugin.yaml for round-trip
        config_filename = self.plugins._get_plugin_conf_filename()
        self.logger.warning('Loading config_filename: {}'.format(config_filename))
        plugin_yaml = shyaml.yaml_load_roundtrip(config_filename)
        self.logger.warning('plugin_yaml: {}'.format(plugin_yaml))

        # - remove all entries of the section that don't start with plugin_ (all beside plugin_name)
        self.logger.warning('1: plugin_yaml[{}]: {}'.format(plugin_section, dict(plugin_yaml[plugin_section])))
        key_list = list(plugin_yaml[plugin_section].keys())
        for key in key_list:
            if key != 'plugin_name':
                del plugin_yaml[plugin_section][key]
        self.logger.warning('2: plugin_yaml[{}]: {}'.format(plugin_section, dict(plugin_yaml[plugin_section])))

        # - add all entries to the section which just were received from the admin backend
        self.logger.warning('- {}:'.format(plugin_section))
        config_dict = json.loads(config)

        # change class_path to plugin_name
        if 'class_path' in config_dict.keys():
            if config_dict['class_path'].startswith('plugins.'):
                plugin_yaml[plugin_section]['plugin_name'] = config_dict['class_path'][8:]
                del config_dict['class_path']

        # handle plugin_enabled
        if 'plugin_enabled' in config_dict.keys():
            if str(config_dict['plugin_enabled']).lower() == 'false':
                plugin_yaml[plugin_section]['plugin_enabled'] = False
            else:
                del config_dict['plugin_enabled']

        # save the rest of the parameters to plugin.yaml
        for key in config_dict:
            self.logger.warning('-     {}: {}'.format(key, config_dict[key]))
            plugin_yaml[plugin_section][key] = config_dict[key]
        self.logger.warning('3: plugin_yaml[{}]: {}'.format(plugin_section, dict(plugin_yaml[plugin_section])))

        # - save etc/plugin.yaml
        self.logger.warning('Saving config_filename: {}'.format(config_filename))
        shyaml.yaml_save_roundtrip(config_filename, plugin_yaml, create_backup=True)
        # self.logger.warning("Config-Information not saved to etc/plugin.yaml")


        # item_data = []
        # item = self.items.return_item(item_path)
        # if 'num' in item.type():
        #     if "." in value or "," in value:
        #         value = float(value)
        #     else:
        #         value = int(value)
        # item(value, caller='admin')

        return '{"result": "true"}'

