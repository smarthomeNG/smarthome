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
import collections
import requests
import time
import threading
from random import randrange

import lib.shyaml as shyaml
import lib.config
from lib.module import Modules
from lib.plugin import Plugins
from lib.metadata import Metadata
from lib.model.smartplugin import SmartPlugin
from lib.constants import (KEY_CLASS_PATH, YAML_FILE, DIR_PLUGINS)

from .rest import RESTResource


class PluginsController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugin_data = {}
        return


    # ======================================================================
    #  GET /api/plugins
    #
    def read(self, id=None):
        """
        Handle GET requests for threads API

        return an object with type info about all installed plugins
        """
        self.logger.info("PluginsController(): read")

        default_language = self._sh.get_defaultlanguage()

        if self.plugin_data == {}:
            plugins_list = sorted(os.listdir(self.plugins_dir))

            self.logger.info("- plugins_list_sorted = {}".format(plugins_list))
            for p in plugins_list:
                if not (p[0] in ['.', '_']):
                    if os.path.isfile(os.path.join(self.plugins_dir, p, 'plugin.yaml')):
                        plg_yaml = shyaml.yaml_load(os.path.join(os.path.join(self.plugins_dir, p, 'plugin.yaml')))
                        if plg_yaml is None:
                            self.logger.warning("- no valid plugin.yaml found for plugin {}".format(p))
                        else:
                            plg_data = plg_yaml.get('plugin', None)
                            if plg_data is None:
                                self.logger.info("- plugin.yaml has no section 'plugin': {}".format(p))
                            else:
                                self.plugin_data[p] = plg_data.get('type', '')
                    else:
                        self.logger.info("- no plugin.yaml: {}".format(p))

        return json.dumps(self.plugin_data)

    read.expose_resource = True
    read.authentication_needed = True


class PluginsInstalledController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugin_data = {}
        return


    # ======================================================================
    #  GET /api/plugins/installed
    #
    def read(self, id=None):
        """
        return an object with data about all installed plugins
        """
        self.logger.info("PluginsInstalledController(): index")
        if self._sh.shng_status['code'] < 20:
            self.logger.error("PluginsInstalledController.read(): SmartHomeNG has not yet finished initialization")
            return json.dumps({})

        default_language = self._sh.get_defaultlanguage()

        if self.plugin_data == {}:
            plugins_list = sorted(os.listdir(self.plugins_dir))
            self.logger.info("PluginsInstalledController.read(): plugin_list (sollte sortiert sein) = '{}'".format(plugins_list))

            self.logger.info("- plugins_list_sorted = {}".format(plugins_list))
            for p in plugins_list:
                if not (p[0] in ['.', '_']):
                    if os.path.isfile(os.path.join(self.plugins_dir, p, 'plugin.yaml')):
                        plg_yaml = shyaml.yaml_load(os.path.join(os.path.join(self.plugins_dir, p, 'plugin.yaml')))
                        if plg_yaml == None:
                            self.logger.warning("PluginsInstalledController.read(): Plugin '{}': plugin.yaml cannot be read".format(p))
                        else:
                            plg_data = plg_yaml.get('plugin', None)
                            if plg_data is None:
                                self.logger.info("- plugin.yaml has no section 'plugin': {}".format(p))
                            else:
                                # self.plugin_data[p] = {}
                                self.plugin_data[p] = collections.OrderedDict()
                                self.plugin_data[p]['type'] = plg_data.get('type', '')
                                description = plg_data.get('description', {'de': '', 'en': ''})

                                # self.plugin_data[p]['description'] = description.get(default_language, '')
                                # if self.plugin_data[p]['description'] == '':
                                #     self.plugin_data[p]['description'] = description[self.fallback_language_order[0]]
                                # if self.plugin_data[p]['description'] == '':
                                #     self.plugin_data[p]['description'] = description[self.fallback_language_order[1]]

                                self.plugin_data[p]['description'] = description

                                self.plugin_data[p]['version'] = plg_data.get('version', '')
                                self.plugin_data[p]['state'] = plg_data.get('state', '')
                                self.plugin_data[p]['documentation'] = plg_data.get('documentation', '')
                                self.plugin_data[p]['multi_instance'] = plg_data.get('multi_instance', '')
                                self.plugin_data[p]['configuration_needed'] = plg_data.get('configuration_needed', True)
                    else:
                        self.logger.info("- no plugin.yaml: {}".format(p))
        self.logger.info("PluginsInstalledController.read(): Plugin Liste (sollte sortiert sein), json.dumps(self.plugin_data) = '{}'".format(json.dumps(self.plugin_data)))
        return json.dumps(self.plugin_data, sort_keys=True)

    read.expose_resource = True
    read.authentication_needed = True


class PluginsConfigController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugins = Plugins.get_instance()

        self.plugin_data = {}
        return


    def _get_pluginname_and_metadata(self, plg_section, plg_conf):
        """
        Return the actual plugin name and the metadata instance

        :param plg_conf: loaded section of the plugin.yaml for the actual plugin
        :type plg_conf: dict

        :return: plugin_name and metadata_instance
        :rtype: string, object
        """
        plugin_name = plg_conf.get('plugin_name', '').lower()
        plugin_version = plg_conf.get('plugin_version', '').lower()
        if plugin_version != '':
            plugin_version = '._pv_' + plugin_version.replace('.', '_')
        if plugin_name != '':
            meta = Metadata(self._sh, (plugin_name + plugin_version).replace('.', os.sep), 'plugin')
        else:
            classpath = plg_conf.get(KEY_CLASS_PATH, '')
            if classpath != '':
                plugin_name = classpath.split('.')[len(classpath.split('.')) - 1].lower()
                if plugin_name.startswith('_pv'):
                    plugin_name = classpath.split('.')[len(classpath.split('.')) - 2].lower()
                self.logger.debug("Plugins __init__: pluginname = '{}', classpath '{}'".format(plugin_name, classpath))
                meta = Metadata(self._sh, plugin_name, 'plugin', (classpath + plugin_version).replace('.', os.sep))
            else:
                self.logger.error(
                    "Plugin configuration section '{}': Neither 'plugin_name' nor '{}' are defined.".format(plg_section,
                                                                                                            KEY_CLASS_PATH))
                meta = Metadata(self._sh, plugin_name, 'plugin', classpath)
        return (plugin_name + plugin_version, meta)


    # ======================================================================
    #  GET /api/plugins/config
    #
    def read(self, id=None):
        """
        return an object with data about all configured plugins
        """
        if self.plugins is None:
            self.plugins = Plugins.get_instance()

        config_filename = self.plugins._get_plugin_conf_filename()
        _etc_dir = os.path.dirname(config_filename)

        info = {}
        # make it 'readonly', if plugin.conf is used
        info['readonly'] = not(os.path.splitext(config_filename)[1].lower() == '.yaml')

        if not info['readonly']:
            # for beta-testing: create a backup of ../etc/plugin.yaml
            if not os.path.isfile(os.path.join(_etc_dir, 'plugin_before_admin_config.yaml')):
                shutil.copy2(config_filename, os.path.join(_etc_dir, 'plugin_before_admin_config.yaml'))
                self.logger.warning('Created a backup copy of plugin.yaml ({})'.format(os.path.join(_etc_dir, 'plugin_before_admin_config.yaml')))

        # get path to plugin configuration file, withou extension
        _conf = lib.config.parse_basename(os.path.splitext(config_filename)[0], configtype='plugin')

        for confplg in _conf:
            plg = _conf[confplg].get('plugin_name', '?')
            if plg == '?':
                plg = _conf[confplg].get('class_path', '?')
            plginstance = self.plugins.return_plugin(confplg)
            typ = '?'
            if plginstance != None:
                # self.logger.warning("confplg {}: type(plginstance) = {}".format(confplg, type(plginstance)))
                # self.logger.warning("confplg {}: type(plginstance.metadata) = {}".format(confplg, type(plginstance.metadata)))
                try:
                    typ = plginstance.metadata.get_string('type')
                    _conf[confplg]['_meta'] = plginstance.metadata.meta
                    _conf[confplg]['_description'] = plginstance.metadata.meta['plugin']['description']
                except:
                    self.logger.warning('confplg {}: Passed for plginstance = {}'.format(confplg, plginstance))
            else:
                # nicht geladene Plugins
                # self.logger.warning("confplg {}: type(plginstance) = None".format(confplg))
                plugin_name, metadata = self._get_pluginname_and_metadata(confplg, _conf[confplg])
                # self.logger.warning("plugin_name = {}, meta = {}".format(plugin_name, metadata.meta))

                typ = metadata.get_string('type')
                _conf[confplg]['_meta'] = metadata.meta
                try:
                    _conf[confplg]['_description'] = metadata.meta['plugin']['description']
                except:
                    _conf[confplg]['_description'] = {}
                    _conf[confplg]['_description']['de'] = ''
                    _conf[confplg]['_description']['en'] = ''


        info['plugin_config'] = _conf

        return json.dumps(info)

    read.expose_resource = True
    read.authentication_needed = True


class PluginsInfoController(RESTResource):

    blog_urls = {}
    _update_bloglinks_active = False


    def __init__(self, module, shng_url_root):
        self._sh = module._sh
        self.module = module
        self.shng_url_root = shng_url_root

        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugins = Plugins.get_instance()

        self.plugin_data = {}

        self.blog_urls = {}
        self._update_bloglinks_active = True

        # Start scheduler
        self._blog_task_name = 'modules.admin.update_blog_links'
        self._sh.scheduler.add(self._blog_task_name, self._test_for_blog_articles_task, cycle=60, offset=0)
        try:
            module.add_stop_method(self.stop, self.__class__.__name__)
        except Exception as e:
            self.logger.exception("__init__: Exception {}".format(e))
        return


    def stop(self):
        """
        If the Controller has started threads or uses python modules that created threads,
        put cleanup code here.
        """
        self.logger.info("PluginsInfoController: Shutting down")
        self._update_bloglinks_active = False
        # Stop scheduler
        self._sh.scheduler.remove(self._blog_task_name)

        return


    def _test_for_blog_articles_task(self):
        """
        Scheduler task to test if blog articles for the loaded plugins exist
        :return:
        """

        if self.plugins == None:
            self.plugins = Plugins.get_instance()
        if self.plugins != None and self._sh.shng_status.get('code', 0) == 20:   # Running
            self._sh.scheduler._scheduler[self._blog_task_name]['cycle'] = {120 * 60 + randrange(60) : None}  # set scheduler cycle to test every 2 hours
            start = time.time()
            temp_blog_urls = {}

            try:
                for plugin in self.plugins.return_plugins():
                    if not self._update_bloglinks_active:
                        break
                    if isinstance(plugin, SmartPlugin):
                        plugin_name = plugin.get_shortname()
                        if temp_blog_urls.get(plugin_name, None) is None:
                            # Link to Blog:
                            #   add link to blog, if articles exist, that have the pluginname as a tag
                            #   example: Blog articles with tag 'backend'
                            #   - https://www.smarthomeng.de/tag/backend
                            #   alternative example: Blog articles with category 'plugins' and tag 'backend'
                            #   - https://www.smarthomeng.de/category/plugins?tag=backend
                            temp_blog_urls[plugin_name] = 'https://www.smarthomeng.de/tag/' + plugin_name
                            r = requests.get(temp_blog_urls[plugin_name])
                            if r.status_code == 404:
                                temp_blog_urls[plugin_name] = ''
                            elif r.status_code != 200:
                                if r.status_code in [500, 503]:
                                    self.logger.info("www.smarthomeng.de sent status_code {} for get-request to {}".format(r.status_code, temp_blog_urls[plugin_name]))
                                else:
                                    self.logger.notice("www.smarthomeng.de sent status_code {} for get-request to {}".format(r.status_code, temp_blog_urls[plugin_name]))
                                temp_blog_urls[plugin_name] = ''
                        else:
                            pass
                        time.sleep(1)
            except OSError as e:
                if str(e).find('[Errno 101]') > -1:     # [Errno 101] Das Netzwerk ist nicht erreichbar
                    pass
                else:
                    self.logger.error("_test_for_blog_articles: OSError {}".format(e))
            except Exception as e:
                self.logger.error("_test_for_blog_articles: Exception {}".format(e))
            self.blog_urls = temp_blog_urls
            end = time.time()
            self.logger.info("_test_for_blog_articles_task: Used time: {} - blog_urls = {}".format(end - start, self.blog_urls))
        else:
            self.logger.debug("_test_for_blog_articles: Plugin initialization not finished")
        return


    # ======================================================================
    #  GET /api/plugins/info
    #
    def read(self, id=None):
        """
        return a list of all configured plugin instances
        """
        self.logger.info("PluginsInfoController (index)")
        if self.plugins == None:
            self.plugins = Plugins.get_instance()

        # get data for display of page
        conf_plugins = {}
        _conf = lib.config.parse(self.plugins._get_plugin_conf_filename())

        for plugin in _conf:
            conf_plugins[plugin] = {}
            conf_plugins[plugin] = _conf[plugin]

        # Determine the base url for documentation (config and user_doc)
        if self._sh.branch == 'develop':
            documentation_base_url = 'https://smarthomeng.github.io/dev_doc/'
        else:
            documentation_base_url = 'https://smarthomeng.github.io/smarthome/'

        #self._test_for_blog_articles()
        plugin_list = []
        for x in self.plugins.return_plugins():
            plugin = dict()
            plugin['metadata'] = {}

            plugin['stopped'] = False
            # Update(s) triggered by < strong > {{p.instance._itemlist | length}} < / strong > items
            plugin['triggers'] = []
            for it in x._itemlist:
                plugin['triggers'].append(it._path)
            #self.logger.warning("{} items={}, itemlist={}".format(x.get_shortname(), len(plugin['triggers']), plugin['triggers']))

            if isinstance(x, SmartPlugin):
                plugin['pluginname'] = x.get_shortname()
                plugin['configname'] = x.get_configname()
                plugin['version'] = x.get_version()
                plugin['smartplugin'] = True
                plugin['multiinstance'] = x.is_multi_instance_capable()
                plugin['instancename'] = x.get_instance_name()

                plugin['webif_url'] = ''
                if self.module.mod_http.get_webifs_for_plugin(x.get_shortname()) != []:
                    for webif in self.module.mod_http.get_webifs_for_plugin(x.get_shortname()):
                        if webif['Instance'] == plugin['instancename']:
                            # plugin['webif_url'] = self.shng_url_root + webif['Mount']  # don't specify full path (for docker installations reletive path is needed)
                            plugin['webif_url'] = webif['Mount']

                plugin['blog_url'] = self.blog_urls.get(plugin['pluginname'], '')

                plugin['parameters'] = []
                if bool(x._parameters):
                    #                    for p in x._parameters:
                    for p in x._metadata.get_parameterlist():
                        p_dict = {}
                        p_dict['name'] = str(p)
                        p_dict['type'] = x._metadata.get_parameter_type_with_subtype(p)
                        p_dict['value'] = str(x._parameters[p])
                        p_dict['default'] = x._metadata.get_parameter_defaultvalue(p)
                        plugin['parameters'].append(p_dict)

                plugin['attributes'] = []
                for a in x._metadata.get_itemdefinitionlist():
                    a_dict = {}
                    a_dict['name'] = str(a)
                    a_dict['type'] = x._metadata.get_itemdefinition_type_with_subtype(a)
                    plugin['attributes'].append(a_dict)

                plugin['metadata']['classpath'] = x._classpath  # str
                plugin['metadata']['classname'] = x.get_classname()
            else:
                plugin['pluginname'] = x._shortname
                plugin['configname'] = x._configname
                plugin['version'] = ''
                plugin['smartplugin'] = False
                plugin['multiinstance'] = False
                plugin['instancename'] = ''
                plugin['webif_url'] = ''
                plugin['parameters'] = []
                plugin['attributes'] = []

                plugin['metadata']['classpath'] = str(x._classpath)  # str
                plugin['metadata']['classname'] = str(x._classname)  # str
                plugin['stopped'] = False

            plugin['metadata']['type'] = x._metadata.get_string('type')
            plugin['metadata']['state'] = x._metadata.get_string('state')
            plugin['metadata']['description'] = x._metadata.get_mlstring('description')
            plugin['metadata']['description_long'] = x._metadata.get_mlstring('description_long')
            plugin['metadata']['keywords'] = x._metadata.get_string('keywords')
            # documentation link from metadata
            plugin['metadata']['documentation'] = x._metadata.get_string('documentation')
            if plugin['metadata']['documentation'] is None:
                plugin['metadata']['documentation'] = ''
            if plugin['metadata']['documentation'].endswith(f"plugins/{plugin['pluginname']}/user_doc.html"):
                plugin['metadata']['documentation'] = ''
            elif plugin['metadata']['documentation'].endswith(f"plugins_doc/config/{plugin['pluginname']}.html"):
                plugin['metadata']['documentation'] = ''
            plugin['metadata']['support'] = x._metadata.get_string('support')
            plugin['metadata']['maintainer'] = x._metadata.get_string('maintainer')
            plugin['metadata']['tester'] = x._metadata.get_string('tester')

            # construct urls to config page and user_doc page
            plugin['documentation_config_doc'] = ''
            plugin['documentation_user_doc'] = ''
            if plugin['smartplugin'] and not(plugin['pluginname'].startswith('priv_')):
                plugin['documentation_config_doc'] = documentation_base_url + f"plugins_doc/config/{plugin['pluginname']}.html"
                if os.path.isfile(os.path.join(self.plugins_dir, plugin['pluginname'], 'user_doc.rst')):
                    plugin['documentation_user_doc'] = documentation_base_url + f"plugins/{plugin['pluginname']}/user_doc.html"

            try:
                plugin['stopped'] = not x.alive
                plugin['stoppable'] = True
            except:
                plugin['stopped'] = False
                plugin['stoppable'] = False
            if plugin['pluginname'] == 'backend':
                plugin['stoppable'] = False

            plugin_list.append(plugin)
        #        plugins_sorted = sorted(plugin_list, key=lambda k: k['classpath'])
        plugins_sorted = sorted(plugin_list, key=lambda k: k['pluginname'] + k['instancename'])

        return json.dumps(plugins_sorted)

    read.expose_resource = True
    read.authentication_needed = True


class PluginsAPIController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module

        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugins = Plugins.get_instance()

        self.plugin_list = []
        return

    # ======================================================================
    #  GET /api/plugins/plugin_api
    #
    def read(self, id=None):
        """
        return a list of all configured plugin instances
        """
        self.logger.info("PluginsAPIController (index)")

        if self.plugins == None:
            self.plugins = Plugins.get_instance()
        self.plugin_list = []
        for x in self.plugins.return_plugins():
            if isinstance(x, SmartPlugin):
                plugin_config_name = x.get_configname()
                if x.metadata is not None:
                    api = x.metadata.get_plugin_function_defstrings(with_type=True, with_default=True)
                    if api is not None:
                        for function in api:
                            self.plugin_list.append(plugin_config_name + "." + function)

        return json.dumps(self.plugin_list)

    read.expose_resource = True
    read.authentication_needed = True



class PluginsLogicParametersController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module

        self.base_dir = self._sh.get_basedir()
        self.plugins_dir = self._sh.get_config_dir(DIR_PLUGINS)
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.plugins = Plugins.get_instance()

        self.plugin_list = []
        return

    # ======================================================================
    #  GET /api/plugins/logicparameters
    #
    def read(self, id=None):
        """
        return an object with data about the logic parameters of all configured plugins
        """
        self.plugins = Plugins.get_instance()
        return json.dumps(self.plugins.get_logic_parameters())

    read.expose_resource = True
    read.authentication_needed = True
