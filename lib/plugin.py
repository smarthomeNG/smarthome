#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# Copyright 2016        Christian Strassburg
# Copyright 2018        Stefan Widmer (smailee)
# Copyright 2011-2013   Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

# TO DO
# - consolidate with module.py


"""
This library implements loading and starting of plugins of SmartHomeNG.

The methods of the class Plugins implement the API for plugins.
They can be used the following way: To call eg. **xxx()**, use the following syntax:

.. code-block:: python

        from lib.plugin import Plugins
        plugins = Plugins.get_instance()

        # to access a method (eg. xxx()):
        plugins.xxx()


:Warning: This library is part of the core of SmartHomeNG. It **should not be called directly** from plugins!

"""
import gc
import ctypes
import inspect
import sys

import json
import logging
import threading
import collections
import os.path		# until Backend is modified

from importlib import import_module

import lib.config
import lib.translation as translation
from lib.model.smartplugin import SmartPlugin
from lib.constants import (KEY_CLASS_NAME, KEY_CLASS_PATH, KEY_INSTANCE, YAML_FILE, CONF_FILE, DIR_PLUGINS)
from lib.metadata import Metadata

logger = logging.getLogger(__name__)


_plugins_instance = None    # Pointer to the initialized instance of the Plugins class (for use by static methods)
_SH = None


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


class PyObject(ctypes.Structure):
    _fields_ = [("refcnt", ctypes.c_long)]


class Plugins():
    """
    Plugin loader Class. Parses config file and creates a worker thread for each plugin

    :param smarthome: Instance of the smarthome master-object
    :param configfile: Basename of the plugin configuration file
    :type samrthome: object
    :type configfile: str

    """

    _plugins = []
    _threads = []

    _plugindict = {}

    def __init__(self, smarthome, configfile: str):
        self._sh = smarthome
        self._configfile = configfile

        global _plugins_instance
        if _plugins_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical(f"A second 'plugins' object has been created. There should only be ONE instance of class 'Plugins'!!! Called from: {calframe[1][1]} ({calframe[1][3]})")

        _plugins_instance = self

        # until Backend plugin is modified
        if os.path.isfile(configfile + YAML_FILE):
            self._plugin_conf_filename = configfile + YAML_FILE
        else:
            self._plugin_conf_filename = configfile + CONF_FILE
        smarthome._plugin_conf = self._plugin_conf_filename  # type: ignore

        # read plugin configuration (from etc/plugin.yaml)
        _conf = lib.config.parse_basename(configfile, configtype='plugin')
        if _conf == {}:
            return

        logger.info('Load plugins')
        self.threads_early = []
        self.threads_late = []

        # for every section (plugin) in the plugin.yaml file
        for plugin in _conf:
            logger.debug(f'Plugins, section: {plugin}')
            self.load_plugin(plugin, _conf[plugin])

        # join the start_early and start_late lists with the main thread list
        self._threads = self.threads_early + self._threads + self.threads_late

        # cleanup early/late startup
        self.threads_early = self.threads_late = []

        logger.info('Load of plugins finished')
        del _conf  # clean up
        os.chdir((self._sh._base_dir))

        # Tests für logic-Parameter Metadaten
        self.logic_parameters = {}

        for i in range(0, len(self._plugins) - 1):

            if self._plugins[i]._metadata.logic_parameters is not None:
                for param in self._plugins[i]._metadata.logic_parameters:
                    logger.debug(f"Plugins.__init__: Plugin '{self._plugins[i]._shortname}' logic_param '{param}' = {json.loads(json.dumps(self._plugins[i]._metadata.logic_parameters[param]))}")
                    self.logic_parameters[param] = json.loads(json.dumps(self._plugins[i]._metadata.logic_parameters[param]))
                    self.logic_parameters[param]['plugin'] = self._plugins[i]._shortname


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
                logger.debug(f"Plugins __init__: pluginname = '{plugin_name}', classpath '{classpath}'")
                meta = Metadata(self._sh, plugin_name, 'plugin', (classpath + plugin_version).replace('.', os.sep))
            else:
                logger.error(f"Plugin configuration section '{plg_section}': Neither 'plugin_name' nor '{KEY_CLASS_PATH}' are defined.")
                meta = Metadata(self._sh, plugin_name, 'plugin', classpath)
        return (plugin_name + plugin_version, meta)


    def _get_conf_args(self, plg_conf):
        """
        Return the parameters/values for the actual plugin as args-dict

        :param plg_conf: loaded section of the plugin.yaml for the actual plugin
        :type plg_conf: dict

        :return: args = specified parameters and their values
        :rtype: dict
        """
        args = {}
        for arg in plg_conf:
            # ignore class_name, class_path and instance - those parameters ar not handed to the PluginWrapper
            if arg != KEY_CLASS_NAME and arg != KEY_CLASS_PATH and arg != KEY_INSTANCE:
                value = plg_conf[arg]
                if isinstance(value, str):
                    value = f"'{value}'"
                args[arg] = value
        return args


    def _get_classname_and_classpath(self, plg_conf, plugin_name):
        """
        Returns the classname and the classpath for the actual plugin

        :param plg_conf: loaded section of the plugin.yaml for the actual plugin
        :param plugin_name: Plugin name (to be used, for building classpass, if it is not specified in the configuration
        :type plg_conf: dict
        :type plugin_name: str

        :return: classname, classpass
        :rtype: str, str
        """
        classname = plg_conf.get(KEY_CLASS_NAME, '')
        plugin_version = ''
        if plugin_name == '':
            plugin_version = plg_conf.get('plugin_version', '').lower()
            if plugin_version != '':
                plugin_version = '._pv_' + plugin_version.replace('.', '_')

        if classname == '':
            classname = self.meta.get_string('classname')
        try:
            classpath = plg_conf[KEY_CLASS_PATH]
        except Exception:
            if plugin_name == '':
                classpath = ''
            else:
                classpath = DIR_PLUGINS + '.' + plugin_name
#        logger.warning("_get_classname_and_classpath: plugin_name = {}, classpath = {}, classname = {}".format(plugin_name, classpath, classname))
        return (classname, classpath + plugin_version)


    def _get_instancename(self, plg_conf):
        """
        Returns the instancename for the actual plugin

        :param plg_conf: loaded section of the plugin.yaml for the actual plugin
        :type plg_conf: dict

        :return: instance name
        :rtype: str
        """
        instance = ''
        if KEY_INSTANCE in plg_conf:
            instance = plg_conf[KEY_INSTANCE].strip()
            if instance == 'default':
                instance = ''
        return instance


    def _test_duplicate_pluginconfiguration(self, plugin, classname, instance):
        """
        Returns True, if a plugin instance of the classname is already loaded by another configuration section

        :param plugin: Name of the configuration
        :param classname: Name of the class to check
        :type plugin: str
        :type classname: str

        :return: True, if plugin is already loaded
        :rtype: bool
        """
        # give a warning if either a classic plugin uses the same class twice
        # or if a SmartPlugin uses the same class and instance twice (due to a copy & paste error)
        duplicate = False
        for p in self._plugins:
            if isinstance(p, SmartPlugin):
                if p.get_instance_name() == instance:
                    for t in self._threads:
                        if t.plugin == p:
                            if t.plugin.__class__.__name__ == classname:
                                duplicate = True
                                prev_plugin = t._name
                                logger.warning(f"Plugin section '{plugin}' uses same class '{p.__class__.__name__}' and instance '{'default' if instance == '' else instance}' as plugin section '{prev_plugin}'")
                                break

            elif p.__class__.__name__ == classname:
                logger.warning(f'Multiple classic plugin instances of class "{classname}" detected')
        return duplicate


    def __iter__(self):
        for plugin in self._plugins:
            yield plugin


    def get_loaded_plugins(self):
        """
        Returns a list with the names of all loaded plugins

        if multiple instances of a plugin are loaded, the plugin name is returned only once

        :return: list of plugin names
        :rtype: list
        """
        plgs = []
        for plugin in self._plugins:
            plgname = plugin.get_shortname()
            if plgname not in plgs:
                plgs.append(plgname)
        return sorted(plgs)


    def get_loaded_plugin_instances(self):
        """
        Returns a list of tuples of all loaded plugins with the plugin name and the instance name

        :return: list of (plugin name, instance name)
        :rtype: list of tuples
        """
        plgs = []
        for plugin in self._plugins:
            plgname = plugin.get_shortname()
            insname = plugin.get_instance_name()
            plgs.append((plgname, insname))
        return sorted(plgs)


    def _get_plugin_conf_filename(self):
        """
        Returns the name of the logic configuration file
        """
        return self._plugin_conf_filename


    # ------------------------------------------------------------------------------------
    #   Following (static) methods of the class Plugins implement the API for plugins in shNG
    # ------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Plugins class, to be used to access the plugin-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.plugin import Plugins
            plugins = Plugins.get_instance()

            # to access a method (eg. xxx()):
            plugins.xxx()


        :return: logics instance
        :rtype: object of None
        """
        return _plugins_instance


    def __call__(self, plugin_name, instance=None):
        """ get plugin object by name """
        return self.get(plugin_name, instance)


    def get(self, plugin_name, instance=None):
        """
        Get plugin object by plugin name and instance (optional)

        :param plugin_name: name of the plugin (not the plugin configuration)
        :param instance: name of the instance of the plugin (optional)

        :return: plugin object
        """
        if instance is None:
            return self._plugindict.get(plugin_name)
        return self._plugindict.get(plugin_name + '#' + instance)


    def return_plugin(self, configname):
        """
        Returns (the object of) one loaded smartplugin with given configname

        :param name: name of the plugin to get
        :type name: str

        :return: object of the plugin
        :rtype: object
        """
        for plugin in self._plugins:
            try:
                if plugin.get_configname() == configname:
                    return plugin
            except Exception:
                pass


    def return_plugins(self):
        """
        Returns each of all loaded plugins (including instances)

        :return: list of plugin names
        :rtype: list
        """

        for plugin in self._plugins:
            yield plugin


    def get_logic_parameters(self):
        """
        Returns the list of all logic parameter definitions of all configured/loaded plugins

        :return:
        """
        paramdict = collections.OrderedDict(sorted(self.logic_parameters.items()))
        for p in paramdict:
            logger.debug(f"Plugins.get_logic_parameters(): {p} = {paramdict[p]}")

        return paramdict


    def load_plugin(self, plg_section: str, conf: dict) -> bool:
        """
        load plugin for given section with given config

        return True if plugin was loaded successfully, False if not (even if disabled)
        """
        logger.debug(f'Attempting to load plugin "{conf.get("plugin_name", "(unknown)")}" from section {plg_section}')
        plugin_name, self.meta = self._get_pluginname_and_metadata(plg_section, conf)
        self._sh.shng_status['details'] = plugin_name   # Namen des Plugins übertragen

        # test if plugin defines item attributes
        item_attributes = self.meta.itemdefinitions
        if item_attributes is not None:
            attribute_keys = list(item_attributes.keys())
            for attribute_name in attribute_keys:
                self._sh.items.add_plugin_attribute(plugin_name, attribute_name, item_attributes[attribute_name])

        # test if plugin defines item attribute prefixes (e.g. stateengine)
        item_attribute_prefixes = self.meta.itemprefixdefinitions
        if item_attribute_prefixes is not None:
            attribute_prefixes_keys = list(item_attribute_prefixes.keys())
            for attribute_prefix in attribute_prefixes_keys:
                self._sh.items.add_plugin_attribute_prefix(plugin_name, attribute_prefix, item_attribute_prefixes[attribute_prefix])

        # Test if plugin defines item structs
        item_structs = self.meta.itemstructs
        if item_structs is not None:
            struct_keys = list(item_structs.keys())
            for struct_name in struct_keys:
                self._sh.items.add_struct_definition(plugin_name, struct_name, item_structs[struct_name])

        # Test if plugin is disabled
        if str(conf.get('plugin_enabled', None)).lower() == 'false':
            logger.info(f'Section {plg_section} (plugin_name {conf.get("plugin_name", "unknown")}) is disabled - plugin not loaded')
        elif self.meta.test_shngcompatibility() and self.meta.test_pythoncompatibility() and self.meta.test_sdpcompatibility():
            classname, classpath = self._get_classname_and_classpath(conf, plugin_name)
            if (classname == '') and (classpath == ''):
                logger.error(f'Plugins, section {plg_section}: plugin_name is not defined')
            elif classname == '':
                logger.error(f'Plugins, section {plg_section}: class_name is not defined')
            elif classpath == '':
                logger.error(f'Plugins, section {plg_section}: class_path is not defined')
            else:
                args = self._get_conf_args(conf)
                instance = self._get_instancename(conf).lower()
                try:
                    plugin_version = self.meta.pluginsettings.get('version', 'ersion unknown')
                    plugin_version = 'v' + plugin_version
                except Exception:
                    plugin_version = 'version unknown'
                self._test_duplicate_pluginconfiguration(plg_section, classname, instance)
                os.chdir((self._sh._base_dir))
                try:
                    plugin_thread = PluginWrapper(self._sh, plg_section, classname, classpath, args, instance, self.meta, self._configfile)
                    if plugin_thread._init_complete:
                        try:
                            try:
                                startorder = self.meta.pluginsettings.get('startorder', 'normal').lower()
                            except Exception as e:
                                logger.warning(f'Plugin {str(classpath).split(".")[1]} error on getting startorder: {e}')
                                startorder = 'normal'
                            self._plugins.append(plugin_thread.plugin)  # type: ignore (plugin is set via eval)
                            # dict to get a handle to the plugin code by plugin name:
                            if self._plugindict.get(classpath.split('.')[1], None) is None:
                                self._plugindict[classpath.split('.')[1]] = plugin_thread.plugin  # type: ignore
                            self._plugindict[classpath.split('.')[1] + '#' + instance] = plugin_thread.plugin  # type: ignore
                            if startorder == 'early':
                                self.threads_early.append(plugin_thread)
                            elif startorder == 'late':
                                self.threads_late.append(plugin_thread)
                            else:
                                self._threads.append(plugin_thread)
                            if instance == '':
                                logger.info(f"Initialized plugin '{str(classpath).split('.')[1]}' from section '{plg_section}'")
                            else:
                                logger.info(f"Initialized plugin '{str(classpath).split('.')[1]}' instance '{instance}' from section '{plg_section}'")
                            return True
                        except Exception as e:
                            logger.warning(f"Plugin '{str(classpath).split('.')[1]}' from section '{plg_section}' not loaded - exception {e}")
                except Exception as e:
                    logger.exception(f"Plugin '{str(classpath).split('.')[1]}' {plugin_version} from section '{plg_section}'\nException: {e}\nrunning SmartHomeNG {self._sh.version} / plugins {self._sh.plugins_version}")

        return False


    def unload_plugin(self, configname: str) -> bool:
        """
        Unloads (the object of) one loaded plugin with given configname

        :param name: name of the plugin to unload
        :type name: str

        :return: success or failure
        :rtype: bool
        """
        logger.info("unload_plugin -------------------------------------------------")

        myplugin = self.return_plugin(configname)
        if not myplugin:
            logger.warning(f'Plugin {configname} not found, aborting')
            return
        mythread = self.get_pluginthread(configname)
        if myplugin.alive:
            myplugin.stop()

        logger.info("unload_plugin: configname = {}, myplugin = {}".format(configname, myplugin))

        logger.debug("Plugins._plugins ({}) = {}".format(len(self._plugins), self._plugins))
        logger.debug("Plugins._threads ({}) = {}".format(len(self._threads), self._threads))

        # execute de-initialization code of the plugin
        myplugin.deinit()

        self._threads.remove(mythread)
        self._plugins.remove(myplugin)
        logger.debug("Plugins._plugins nach remove ({}) = {}".format(len(self._plugins), self._plugins))
        logger.debug("Plugins._threads nach remove ({}) = {}".format(len(self._threads), self._threads))

        myplugin_address = id(myplugin)
        logger.debug(f'myplugin sizeof       = {sys.getsizeof(myplugin)}')
        logger.debug(f'myplugin refcnt       = {PyObject.from_address(myplugin_address).refcnt}')
        logger.debug(f'myplugin referrer     = {gc.get_referrers(myplugin)}')
        logger.debug(f'myplugin referrer cnt = {len(gc.get_referrers(myplugin))}')
        for r in gc.get_referrers(myplugin):
            logger.debug("myplugin referrer     = {} / {} / {}".format(r, namestr(r, globals()), namestr(r, locals())))
        gc.collect()
        logger.debug(f'myplugin referrer cnt2= {len(gc.get_referrers(myplugin))}')

        del mythread
        del myplugin
        try:
            logger.warning(f"myplugin refcnt nach del    = {PyObject.from_address(myplugin_address).refcnt}")
        except Exception:
            pass

        # 'myplugin' was deleted above, so this will always raise an exception. Might as well skip it outright...
        # try:
        #     logger.info(f'myplugin referrer cnt = {len(gc.get_referrers(myplugin))}')
        #     for r in gc.get_referrers(myplugin):
        #         logger.info(f'myplugin referrer     = {r}')
        # except Exception:
        #     pass

        logger.debug(f"Plugins._plugins nach del ({len(self._plugins)}) = {self._plugins}")
        logger.debug(f"Plugins._threads nach del ({len(self._threads)}) = {self._threads}")

        # TODO: find proper point to return True on success...?!
        return False


    def start(self):
        logger.info('Start plugins')
        for plugin in self._threads:
            try:
                instance = plugin.get_implementation().get_instance_name()
                if instance != '':
                    instance = ", instance '" + instance + "'"
                logger.debug(f"Starting plugin '{plugin.get_implementation().get_shortname()}'{instance}")
            except Exception:
                logger.debug(f"Starting classic-plugin from section '{plugin.name}'")
            plugin.start()
        logger.info('Start of plugins finished')


    def stop(self):
        logger.info('Stop plugins')
        for plugin in list(reversed(self._threads)):
            instance = ''
            try:
                instance = plugin.get_implementation().get_instance_name()
                if instance != '':
                    instance = ", instance '" + instance + "'"
                logger.debug(f"Stopping plugin '{plugin.get_implementation().get_shortname()}'{instance}")
            except Exception:
                logger.debug(f"Stopping classic-plugin from section '{plugin.name}'")
            try:
                plugin.stop()
            except Exception as e:
                logger.warning(f"Error while stopping plugin '{plugin.get_implementation().get_shortname()}'{instance}': {e}")
        logger.info('Stop of plugins finished')


    def get_pluginthread(self, configname):
        """
        Returns one plugin with given name

        :return: Thread object for the given plugin name
        :rtype: object
        """
        for thread in self._threads:
            if thread.name == configname:
               return thread


class PluginWrapper(threading.Thread):
    """
    Wrapper class for loading plugins

    :param smarthome: Instance of the smarthome master-object
    :param plg_section: Section name in plugin configuration file (etc/plugin.yaml)
    :param classname: Name of the (main) class in the plugin
    :param classpath: Path to the Python file containing the class
    :param args: Parameter as specified in the configuration file (etc/plugin.yaml)
    :param instance: Name of the instance of the plugin
    :param meta:
    :type samrthome: object
    :type plg_section: str
    :type classname: str
    :type classpath: str
    :type args: dict
    :type instance: str
    :type meta: object
    """

    def __init__(self, smarthome, plg_section: str, classname: str, classpath: str, args: dict, instance: str, meta: Metadata, configfile: str):
        """
        Initialization of wrapper class
        """
        logger.debug(f"PluginWrapper __init__: Section {plg_section}, classname {classname}, classpath {classpath}")
        threading.Thread.__init__(self, name=plg_section)

        self._sh = smarthome
        self._init_complete = False
        self.meta = meta
        # Load an instance of the plugin

        module = None

        try:
            # exec("import {0}".format(classpath))
            module = import_module(classpath)
        except ImportError as e:
            logger.error(f"Plugin '{plg_section}' error importing Python package: {e}")
            logger.error(f"Plugin '{plg_section}' initialization failed, plugin not loaded")
            return
        except Exception as e:
            logger.exception(f"Plugin '{plg_section}' exception during import: {e}")
            logger.error(f"Plugin '{plg_section}' initialization failed, plugin not loaded")
            return
        if not module:
            logger.error(f"Plugin '{plg_section}' import didn't return a module.")
            logger.error(f"Plugin '{plg_section}' initialization failed, plugin not loaded")
            return
        cls = getattr(module, classname)
        if not cls:
            logger.error(f"Plugin '{plg_section}' errorclass name '{classname}' defined in metadata, but not found in plugin code")
            return

        try:
            # exec("self.plugin = {0}.{1}.__new__({0}.{1})".format(classpath, classname))
            self.plugin = cls.__new__(cls)
        except Exception as e:
            logger.error(f"Plugin '{plg_section}' initialization failed: {e}")
            logger.error(f"Plugin '{plg_section}' not loaded")
            return

        # load plugin-specific translations
        self._ptrans = translation.load_translations('plugin', classpath.replace('.', '/'), 'plugin/' + classpath.split('.')[1])

        if self.meta.get_string('state') == 'deprecated':
            logger.warning(f"Plugin '{classpath.split('.')[1]}' (section '{plg_section}') is deprecated. Consider to use a replacement instead")

        # initialize attributes of the newly created plugin object instance
        if isinstance(self.get_implementation(), SmartPlugin):

            # SmartPlugin
            self.get_implementation()._configfilename = configfile
            self.get_implementation()._set_configname(plg_section)
            self.get_implementation()._set_shortname(str(classpath).split('.')[1])
            self.get_implementation()._classpath = classpath
            self.get_implementation()._set_classname(classname)
            if self.get_implementation().ALLOW_MULTIINSTANCE is None:
                self.get_implementation().ALLOW_MULTIINSTANCE = self.meta.get_bool('multi_instance')
            if instance != '':
                logger.debug(f"set plugin {plg_section} instance to {instance}")
                self.get_implementation()._set_instance_name(instance)

            # Customized logger instance for plugin to append name of plugin instance to log text
            global _SH
            _SH = self._sh
            self.get_implementation().logger = PluginLoggingAdapter(logging.getLogger(classpath), {'plugininstance': self.get_implementation().get_loginstance()})
            self.get_implementation()._set_sh(smarthome)
            self.get_implementation()._set_plugin_dir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), classpath.replace('.', os.sep)))
            self.get_implementation()._plgtype = self.meta.get_string('type')
            self.get_implementation().metadata = self.meta
        else:

            # classic plugin
            self.get_implementation()._configfilename = configfile
            self.get_implementation()._configname = plg_section
            self.get_implementation()._shortname = str(classpath).split('.')[1]
            self.get_implementation()._classpath = classpath
            self.get_implementation()._classname = classname
            self.get_implementation()._plgtype = ''

        self.get_implementation()._itemlist = []

        # get arguments defined in __init__ of plugin's class to self.args
        # exec("self.args = inspect.getfullargspec({0}.{1}.__init__)[0][1:]".format(classpath, classname))
        plg_class_args = inspect.getfullargspec(getattr(module, classname).__init__)[0][1:]

        # get list of argument used names, if they are defined in the plugin's class
        logger.debug(f"Plugin '{classname}': args = '{str(args)}'")

        # make kwargs dict for all args which are arguments to __init__
        kwargs = {name: args[name] for name in [name for name in plg_class_args if name in args]}

        self.get_implementation()._init_complete = False
        plugin_params, params_ok, hide_params = self.meta.check_parameters(args)
        if params_ok:
            # initialize parameters the new way: Define a dict within the instance
            self.get_implementation()._parameters = plugin_params
            self.get_implementation()._hide_parameters = hide_params
            self.get_implementation()._metadata = self.meta

            # initialize the loaded instance of the plugin
            self.get_implementation()._init_complete = True   # set to false by plugin, if an initalization error occurs

            # initialize the loaded instance of the plugin
            # exec("self.plugin.__init__(smarthome{0}{1})".format("," if len(arglist) else "", argstring))
            self.plugin.__init__(smarthome, **kwargs)

            # set level to make logger appear in internal list of loggers (if not configured by logging.yaml)
            try:  # skip classic plugins
                if self.get_implementation().logger.level == 0:
                    self.get_implementation().logger.setLevel('WARNING')
            except Exception:
                pass

        # set the initialization complete status for the wrapper instance
        self._init_complete = self.get_implementation()._init_complete
        if self.get_implementation()._init_complete:
            # make the plugin a method/function of the main smarthome object
            setattr(smarthome, self.name, self.plugin)
            try:
                code_version = self.get_implementation().PLUGIN_VERSION
            except Exception:
                code_version = None    # if plugin code without version
            if isinstance(self.get_implementation(), SmartPlugin):
                if self.meta.test_version(code_version):
                    # set version in plugin instance (if not defined in code)
                    if code_version is None:
                        self.get_implementation().PLUGIN_VERSION = self.meta.get_version()
                    # set multiinstance in plugin instance (if not defined in code)
                    try:
                        self.get_implementation().ALLOW_MULTIINSTANCE
                    except Exception:
                        # logger.warning(f'self.meta.get_bool('multi_instance') = {self.meta.get_bool('multi_instance')}')
                        self.get_implementation().ALLOW_MULTIINSTANCE = self.meta.get_bool('multi_instance')
                        # logger.warning(f'get_implementation().ALLOW_MULTIINSTANCE = {self.get_implementation().ALLOW_MULTIINSTANCE}')
                    if not self.get_implementation()._set_multi_instance_capable(self.meta.get_bool('multi_instance')):
                        logger.error(f"Plugins: Loaded plugin '{plg_section}' ALLOW_MULTIINSTANCE differs between metadata ({self.meta.get_bool('multi_instance')}) and Python code ({self.get_implementation().ALLOW_MULTIINSTANCE})")
                    logger.debug(f"Plugins: Loaded plugin '{plg_section}' (class '{str(self.get_implementation().__class__.__name__)}') v{self.meta.get_version()}: {self.meta.get_mlstring('description')}")
            else:
                logger.debug(f"Plugins: Loaded classic-plugin '{plg_section}' (class '{str(self.get_implementation().__class__.__name__)}')")
            if instance != '':
                logger.debug(f"set plugin {plg_section} instance to {instance}")
                self.get_implementation()._set_instance_name(instance)
        else:
            logger.error(f"Plugin '{classpath.split('.')[1]}' initialization failed, plugin not loaded")


    def run(self):
        """
        Starts this plugin instance
        """
        try:
            self.plugin.run()
        except Exception as e:
            logger.exception(f"Plugin '{self.plugin.get_shortname()}' exception in run() method: {e}")

    def stop(self):
        """
        Stops this plugin instance
        """
        try:
            self.plugin.stop()
        except Exception as e:
            logger.exception(f"Plugin '{self.plugin.get_shortname()}' exception in stop() method: {e}")


    def get_name(self):
        """
        Returns the name of current plugin instance

        :return: name of the current plugin instance
        :rtype: str
        """
        return self.name


    def get_ident(self):
        """
        Returns the thread ident of current plugin instance

        :return: Thread identifier of current plugin instance
        :rtype: int
        """
        return self.ident


    def get_implementation(self):
        """
        Returns the implementation of current plugin instance

        :return: the current plugin instance
        :rtype: object
        """
        return self.plugin


# addition von smai:
class PluginLoggingAdapter(logging.LoggerAdapter):
    """
    Class to append name of plugin instance to log text

    This class is used by PluginWrapper to set up a logger for the SmartPlugin class
    """
    from lib.log import Logs

    def __init__(self, logger, extra):
        logging.LoggerAdapter.__init__(self, logger, extra)
        self.logger = logger

        logging.addLevelName(_SH.logs.NOTICE_level, "NOTICE")
        logging.addLevelName(_SH.logs.DBGHIGH_level, "DBGHIGH")
        logging.addLevelName(_SH.logs.DBGMED_level, "DBGMED")
        logging.addLevelName(_SH.logs.DBGLOW_level, "DBGLOW")
        return

    def notice(self, msg, *args, **kwargs):
        self.logger.log(_SH.logs.NOTICE_level, f"{self.extra['plugininstance']}{msg}", *args, **kwargs)
        return

    def dbghigh(self, msg, *args, **kwargs):
        self.logger.log(_SH.logs.DBGHIGH_level, f"{self.extra['plugininstance']}{msg}", *args, **kwargs)
        return

    def dbgmed(self, msg, *args, **kwargs):
        self.logger.log(_SH.logs.DBGMED_level, f"{self.extra['plugininstance']}{msg}", *args, **kwargs)
        return

    def dbglow(self, msg, *args, **kwargs):
        self.logger.log(_SH.logs.DBGLOW_level, f"{self.extra['plugininstance']}{msg}", *args, **kwargs)
        return

    def process(self, msg, kwargs):
        kwargs['extra'] = self.extra
        return f"{self.extra['plugininstance']}{msg}", kwargs
# end addition von smai
