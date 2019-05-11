#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# Copyright 2016-       Christian Strassburg
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
import sys

import json
import logging
import threading
import inspect
import collections
import os.path		# until Backend is modified

import lib.config
import lib.shyaml as shyaml
from lib.model.smartplugin import SmartPlugin
from lib.constants import (KEY_CLASS_NAME, KEY_CLASS_PATH, KEY_INSTANCE,YAML_FILE,CONF_FILE)
#from lib.utils import Utils
from lib.metadata import Metadata
#import lib.item

logger = logging.getLogger(__name__)


_plugins_instance = None    # Pointer to the initialized instance of the Plugins class (for use by static methods)

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


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

    def __init__(self, smarthome, configfile):
        self._sh = smarthome

        global _plugins_instance
        if _plugins_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical("A second 'plugins' object has been created. There should only be ONE instance of class 'Plugins'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _plugins_instance = self

        # until Backend plugin is modified
        if os.path.isfile(configfile+ YAML_FILE):
            self._plugin_conf_filename = configfile + YAML_FILE
        else:
            self._plugin_conf_filename = configfile + CONF_FILE
        smarthome._plugin_conf = self._plugin_conf_filename

        # read plugin configuration (from etc/plugin.yaml)
        _conf = lib.config.parse_basename(configfile, configtype='plugin')
        if _conf == {}:
            return

        self._load_translations()

        logger.info('Load plugins')

        # for every section (plugin) in the plugin.yaml file
        for plugin in _conf:
            logger.debug("Plugins, section: {}".format(plugin))
            plugin_name, self.meta = self._get_pluginname_and_metadata(plugin, _conf[plugin])

            # Test if plugin defines item structs
            item_structs = self.meta.itemstructs
            if item_structs is not None:
                struct_keys = list(item_structs.keys())
                for struct_name in struct_keys:
                    self._sh.items.add_struct_definition(plugin_name, struct_name, item_structs[struct_name])

            # Test if plugin is disabled
            if str(_conf[plugin].get('plugin_enabled', None)).lower() == 'false':
                logger.info("Section {} (plugin_name {}) is disabled - Plugin not loaded".format(plugin, _conf[plugin].get('plugin_name', None)))
            elif self.meta.test_shngcompatibility():
                classname, classpath = self._get_classname_and_classpath(_conf[plugin], plugin_name)
                if (classname == '') and (classpath == ''):
                    logger.error("Plugins, section {}: plugin_name is not defined".format(plugin))
                elif classname == '':
                    logger.error("Plugins, section {}: class_name is not defined".format(plugin))
                elif classpath == '':
                    logger.error("Plugins, section {}: class_path is not defined".format(plugin))
                else:
                    args = self._get_conf_args(_conf[plugin])
#                    logger.warning("Plugin '{}' from from section '{}': classname = {}, classpath = {}".format( str(classpath).split('.')[1], plugin, classname, classpath ) )
                    instance = self._get_instancename(_conf[plugin]).lower()
                    dummy = self._test_duplicate_pluginconfiguration(plugin, classname, instance)
                    try:
                        plugin_thread = PluginWrapper(smarthome, plugin, classname, classpath, args, instance, self.meta, self._gtrans)
                        if plugin_thread._init_complete == True:
                            try:
                                self._plugins.append(plugin_thread.plugin)
                                self._threads.append(plugin_thread)
                                if instance == '':
                                    logger.info("Initialized plugin '{}' from from section '{}'".format( str(classpath).split('.')[1], plugin ) )
                                else:
                                    logger.info("Initialized plugin '{}' instance '{}' from from section '{}'".format( str(classpath).split('.')[1], instance, plugin ) )
                            except:
                                logger.warning("Plugin '{}' from from section '{}' not loaded".format( str(classpath).split('.')[1], plugin ) )
                    except Exception as e:
                        logger.exception("Plugin '{}' from section '{}' exception: {}".format(str(classpath).split('.')[1], plugin, e))

        logger.info('Load of plugins finished')
        del(_conf)  # clean up


        # Tests für logic-Parameter Metadaten
        self.logic_parameters = {}

        for i in range(0, len(self._plugins) - 1):

            if self._plugins[i]._metadata.logic_parameters is not None:
                for param in self._plugins[i]._metadata.logic_parameters:
                    logger.debug("Plugins.__init__: Plugin '{}' logic_param '{}' = {}".format(self._plugins[i]._shortname, param, json.loads(json.dumps(self._plugins[i]._metadata.logic_parameters[param]))))
                    self.logic_parameters[param] = json.loads(json.dumps(self._plugins[i]._metadata.logic_parameters[param]))
                    self.logic_parameters[param]['plugin'] = self._plugins[i]._shortname

        return


    def get_logic_parameters(self):
        """
        Returns the list of all logic parameter definitions of all configured/loaded plugins

        :return:
        """
        paramdict = collections.OrderedDict(sorted(self.logic_parameters.items()))
        for p in paramdict:
            logger.debug("Plugins.get_logic_parameters(): {} = {}".format(p, paramdict[p]))

        return paramdict


    def _load_translations(self):
        """
        """
        self._gtrans = {}
        self.relative_filename = os.path.join( 'bin', 'locale'+YAML_FILE )
        filename = os.path.join( self._sh.get_basedir(), self.relative_filename )
        trans = shyaml.yaml_load(filename, ordered=False, ignore_notfound=True)
        if trans != None:
            self._gtrans = trans.get('global_translations', {})
            logger.info("Loaded global translations = {}".format(self._gtrans))


    def _get_pluginname_and_metadata(self, plg_section, plg_conf):
        """
        Return the actual plugin name and the metadata instance

        :param plg_conf: loaded section of the plugin.yaml for the actual plugin
        :type plg_conf: dict

        :return: plugin_name and metadata_instance
        :rtype: string, object
        """
        plugin_name = plg_conf.get('plugin_name','').lower()
        plugin_version = plg_conf.get('plugin_version','').lower()
        if plugin_version != '':
            plugin_version = '._pv_' + plugin_version.replace('.','_')
        if plugin_name != '':
            meta = Metadata(self._sh, (plugin_name+plugin_version).replace('.',os.sep), 'plugin')
        else:
            classpath = plg_conf.get(KEY_CLASS_PATH,'')
            if classpath != '':
                plugin_name = classpath.split('.')[len(classpath.split('.'))-1].lower()
                if plugin_name.startswith('_pv'):
                    plugin_name = classpath.split('.')[len(classpath.split('.'))-2].lower()
                logger.debug("Plugins __init__: pluginname = '{}', classpath '{}'".format(plugin_name, classpath))
                meta = Metadata(self._sh, plugin_name, 'plugin', (classpath+plugin_version).replace('.',os.sep))
            else:
                logger.error("Plugin configuration section '{}': Neither 'plugin_name' nor '{}' are defined.".format( plg_section, KEY_CLASS_PATH ))
                meta = Metadata(self._sh, plugin_name, 'plugin', classpath)
        return (plugin_name+plugin_version, meta)


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
            if arg != KEY_CLASS_NAME and arg != KEY_CLASS_PATH and arg != KEY_INSTANCE:
                value = plg_conf[arg]
                if isinstance(value, str):
                    value = "'{0}'".format(value)
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
        classname = plg_conf.get(KEY_CLASS_NAME,'')
        plugin_version = ''
        if plugin_name == '':
            plugin_version = plg_conf.get('plugin_version','').lower()
            if plugin_version != '':
                plugin_version = '._pv_' + plugin_version.replace('.','_')

        if classname == '':
            classname = self.meta.get_string('classname')
        try:
            classpath = plg_conf[KEY_CLASS_PATH]
        except:
            if plugin_name == '':
                classpath = ''
            else:
                classpath = 'plugins.' + plugin_name
#        logger.warning("_get_classname_and_classpath: plugin_name = {}, classpath = {}, classname = {}".format(plugin_name, classpath, classname))
        return (classname, classpath+plugin_version)


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
                                logger.warning("Plugin section '{}' uses same class '{}' and instance '{}' as plugin section '{}'".format(plugin, p.__class__.__name__, 'default' if instance == '' else instance, prev_plugin))
                                break

            elif p.__class__.__name__ == classname:
                logger.warning("Multiple classic plugin instances of class '{}' detected".format(classname))
        return duplicate



    def __iter__(self):
        for plugin in self._plugins:
            yield plugin

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
        if _plugins_instance == None:
            return None
        else:
            return _plugins_instance


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
            except:
                pass
        return None
#        return self._plugins[name]


    def return_plugins(self):
        """
        Returns a list with the instances of all loaded plugins

        :return: list of plugin names
        :rtype: list
        """

        for plugin in self._plugins:
            yield plugin


    def _get_plugin_conf_filename(self):
        """
        Returns the name of the logic configuration file
        """
        return self._plugin_conf_filename


    class PyObject(ctypes.Structure):
        _fields_ = [("refcnt", ctypes.c_long)]


    def unload_plugin(self, configname):
        """
        Unloads (the object of) one loaded plugin with given configname

        :param name: name of the plugin to unload
        :type name: str

        :return: success or failure
        :rtype: bool
        """
        logger.info("unload_plugin -------------------------------------------------")

        myplugin = self.return_plugin(configname)
        mythread = self.get_pluginthread(configname)
        if myplugin.alive:
            myplugin.stop()

        logger.info("unload_plugin: configname = {}, myplugin = {}".format(configname, myplugin))

        logger.info("Plugins._plugins ({}) = {}".format(len(self._plugins), self._plugins))
        logger.info("Plugins._threads ({}) = {}".format(len(self._threads), self._threads))

        # execute de-initialization code of the plugin
        myplugin.deinit()

        self._threads.remove(mythread)
        self._plugins.remove(myplugin)
        logger.info("Plugins._plugins nach remove ({}) = {}".format(len(self._plugins), self._plugins))
        logger.info("Plugins._threads nach remove ({}) = {}".format(len(self._threads), self._threads))

        myplugin_address = id(myplugin)
        logger.info("myplugin sizeof       = {}".format(sys.getsizeof(myplugin)))
        logger.info("myplugin refcnt       = {}".format(self.PyObject.from_address(myplugin_address).refcnt))
        logger.info("myplugin referrer     = {}".format(gc.get_referrers(myplugin)))
        logger.info("myplugin referrer cnt = {}".format(len(gc.get_referrers(myplugin))))
        for r in gc.get_referrers(myplugin):
            logger.info("myplugin referrer     = {} / {} / {}".format(r, namestr(r, globals()), namestr(r, locals())))
        gc.collect()
        logger.info("myplugin referrer cnt2= {}".format(len(gc.get_referrers(myplugin))))

        del mythread
        del myplugin
        logger.warning("myplugin refcnt nach del    = {}".format(self.PyObject.from_address(myplugin_address).refcnt))
        try:
            logger.info("myplugin referrer cnt = {}".format(len(gc.get_referrers(myplugin))))
            for r in gc.get_referrers(myplugin):
                logger.info("myplugin referrer     = {}".format(r))
        except:
            pass

        logger.info("Plugins._plugins nach del ({}) = {}".format(len(self._plugins), self._plugins))
        logger.info("Plugins._threads nach del ({}) = {}".format(len(self._threads), self._threads))
        return False



    # ------------------------------------------------------------------------------------

    def start(self):
        logger.info('Start plugins')
        for plugin in self._threads:
            try:
                instance = plugin.get_implementation().get_instance_name()
                if instance != '':
                    instance = ", instance '"+instance+"'"
                logger.debug("Starting plugin '{}'{}".format(plugin.get_implementation().get_shortname(), instance))
            except:
                logger.debug("Starting classic-plugin from section '{}'".format(plugin.name))
            plugin.start()
        logger.info('Start of plugins finished')


    def stop(self):
        logger.info('Stop plugins')
        for plugin in self._threads:
            try:
                instance = plugin.get_implementation().get_instance_name()
                if instance != '':
                    instance = ", instance '"+instance+"'"
                logger.debug("Stopping plugin '{}'{}".format(plugin.get_implementation().get_shortname(), instance))
            except:
                logger.debug("Stopping classic-plugin from section '{}'".format(plugin.name))
            try:
                plugin.stop()
            except:
                logger.warning("Error while stopping plugin '{}'{}'".format(plugin.get_implementation().get_shortname(), instance))
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
        return None


class PluginWrapper(threading.Thread):
    """
    Wrapper class for loading plugins

    :param smarthome: Instance of the smarthome master-object
    :param name: Section name in plugin configuration file (etc/plugin.yaml)
    :param classname: Name of the (main) class in the plugin
    :param classpath: Path to the Python file containing the class
    :param args: Parameter as specified in the configuration file (etc/plugin.yaml)
    :param instance: Name of the instance of the plugin
    :param meta:
    :type samrthome: object
    :type name: str
    :type classname: str
    :type classpath: str
    :type args: dict
    :type instance: str
    :type meta: object
    """

    def __init__(self, smarthome, name, classname, classpath, args, instance, meta, gtranslations):
        """
        Initialization of wrapper class
        """
        logger.debug('PluginWrapper __init__: Section {}, classname {}, classpath {}'.format( name, classname, classpath ))

        threading.Thread.__init__(self, name=name)

        self._init_complete = False
        self.meta = meta
        # Load an instance of the plugin
        try:
            exec("import {0}".format(classpath))
        except ImportError as e:
            logger.error("Plugins: Plugin '{}' error importing Python package: {}".format(name, e))
            logger.error("Plugins: Plugin '{}' initialization failed, plugin not loaded".format(name))
            return
        except Exception as e:
            logger.exception("Plugin '{}' exception during import of __init__.py: {}".format(name, e))
            return
        try:
            exec("self.plugin = {0}.{1}.__new__({0}.{1})".format(classpath, classname))
        except Exception as e:
            logger.exception("Plugin '{}' exception during execution of plugin: {}".format(name, e))

        relative_filename = os.path.join( classpath.replace('.', '/'), 'locale'+YAML_FILE )
        filename = os.path.join( smarthome.get_basedir(), relative_filename )
        trans = shyaml.yaml_load(filename, ordered=False, ignore_notfound=True)
        if trans != None:
            self._ptrans = trans.get('plugin_translations', {})
            logger.info("Plugin '{}': Loaded plugin translations = {}".format(name, self._ptrans))
        else:
            self._ptrans = {}

        # make the plugin a method/function of the main smarthome object  (MS: Ist das zu früh? Falls Init fehlschlägt?)
#        setattr(smarthome, self.name, self.plugin)
        if self.meta.get_string('state') == 'deprecated':
            logger.warning("Plugin '{}' (section '{}') is deprecated. Consider to use a replacement instead".format(classpath.split('.')[1], name))
        # initialize attributes of the newly created plugin object instance
        if isinstance(self.get_implementation(), SmartPlugin):
            self.get_implementation()._gtranslations = gtranslations
            self.get_implementation()._ptranslations = self._ptrans
            self.get_implementation()._set_configname(name)
#            self.get_implementation()._config_section = name
            self.get_implementation()._set_shortname(str(classpath).split('.')[1])
            self.get_implementation()._classpath = classpath
            self.get_implementation()._set_classname(classname)
            # if instance != '' war auskommentiert, reaktiviert: 26.01.2018 MS
            if self.get_implementation().ALLOW_MULTIINSTANCE is None:
                self.get_implementation().ALLOW_MULTIINSTANCE = self.meta.get_bool('multi_instance')
            if instance != '':
                logger.debug("set plugin {0} instance to {1}".format(name, instance ))
                self.get_implementation()._set_instance_name(instance)
#           addition von smai
            # Customized logger instance for plugin to append name of plugin instance to log text
            self.get_implementation().logger = PluginLoggingAdapter(logging.getLogger(classpath), {'plugininstance': self.get_implementation().get_loginstance()})
#           end addition von smai
            self.get_implementation()._set_sh(smarthome)
            self.get_implementation()._set_plugin_dir( os.path.join( os.path.dirname( os.path.dirname(os.path.abspath(__file__)) ), classpath.replace('.',os.sep) ) )
            self.get_implementation()._plgtype = self.meta.get_string('type')
            self.get_implementation().metadata = self.meta
        else:
            # classic plugin
#            self.get_implementation()._config_section = name
            self.get_implementation()._configname = name
            self.get_implementation()._shortname = str(classpath).split('.')[1]
            self.get_implementation()._classpath = classpath
            self.get_implementation()._classname = classname
            self.get_implementation()._plgtype = ''
        self.get_implementation()._itemlist = []

        # get arguments defined in __init__ of plugin's class to self.args
        exec("self.args = inspect.getargspec({0}.{1}.__init__)[0][1:]".format(classpath, classname))

        # get list of argument used names, if they are defined in the plugin's class
        logger.debug("Plugin '{}': args = '{}'".format(classname, str(args)))
        arglist = [name for name in self.args if name in args]
        argstring = ",".join(["{}={}".format(name, args[name]) for name in arglist])
#        logger.debug("Plugin '{}' using arguments {}".format(str(classpath).split('.')[1], arglist))

        self.get_implementation()._init_complete = False
        (plugin_params, params_ok, hide_params) = self.meta.check_parameters(args)
        if params_ok == True:
            if plugin_params != {}:
                # initialize parameters the old way
                argstring = ",".join(["{}={}".format(name, '"'+str(plugin_params.get(name,''))+'"') for name in arglist])
            # initialize parameters the new way: Define a dict within the instance
            self.get_implementation()._parameters = plugin_params
            self.get_implementation()._hide_parameters = hide_params
            self.get_implementation()._metadata = self.meta

            # initialize the loaded instance of the plugin
            self.get_implementation()._init_complete = True   # set to false by plugin, if an initalization error occurs

            # initialize the loaded instance of the plugin
            exec("self.plugin.__init__(smarthome{0}{1})".format("," if len(arglist) else "", argstring))

            # set level to make logger appear in internal list of loggers (if not configured by logging.yaml)
            try: # skip classic plugins
                if self.get_implementation().logger.level == 0:
                    self.get_implementation().logger.setLevel('WARNING')
            except:
                pass

        # set the initialization complete status for the wrapper instance
        self._init_complete = self.get_implementation()._init_complete
        if self.get_implementation()._init_complete == True:
            # make the plugin a method/function of the main smarthome object  (MS: Ist das zu früh? Falls Init fehlschlägt?)
            setattr(smarthome, self.name, self.plugin)
            try:
                code_version = self.get_implementation().PLUGIN_VERSION
            except:
                code_version = None    # if plugin code without version
            if isinstance(self.get_implementation(), SmartPlugin):
                if self.meta.test_version(code_version):
                    # set version in plugin instance (if not defined in code)
                    if code_version == None:
                        self.get_implementation().PLUGIN_VERSION = self.meta.get_version()
                    # set multiinstance in plugin instance (if not defined in code)
                    try:
                        dummy = self.get_implementation().ALLOW_MULTIINSTANCE
                    except:
#                        logger.warning("self.meta.get_bool('multi_instance') = {}".format(self.meta.get_bool('multi_instance')))
                        self.get_implementation().ALLOW_MULTIINSTANCE = self.meta.get_bool('multi_instance')
#                        logger.warning("get_implementation().ALLOW_MULTIINSTANCE = {}".format(self.get_implementation().ALLOW_MULTIINSTANCE))
                    if not self.get_implementation()._set_multi_instance_capable(self.meta.get_bool('multi_instance')):
                        logger.error("Plugins: Loaded plugin '{}' ALLOW_MULTIINSTANCE differs between metadata ({}) and Python code ({})".format(name, self.meta.get_bool('multi_instance'), self.get_implementation().ALLOW_MULTIINSTANCE ))
                    logger.debug("Plugins: Loaded plugin '{}' (class '{}') v{}: {}".format( name, str(self.get_implementation().__class__.__name__), self.meta.get_version(), self.meta.get_mlstring('description') ) )
            else:
                logger.debug("Plugins: Loaded classic-plugin '{}' (class '{}')".format( name, str(self.get_implementation().__class__.__name__) ) )
            if instance != '':
                logger.debug("set plugin {0} instance to {1}".format(name, instance ))
                self.get_implementation()._set_instance_name(instance)
        else:
            logger.error("Plugins: Plugin '{}' initialization failed, plugin not loaded".format(classpath.split('.')[1]))


    def run(self):
        """
        Starts this plugin instance
        """
        try:
            self.plugin.run()
        except Exception as e:
            logger.exception("Plugin '{}' exception in run() method: {}".format(self.plugin.get_shortname(), e))

    def stop(self):
        """
        Stops this plugin instance
        """
        try:
            self.plugin.stop()
        except Exception as e:
            logger.exception("Plugin '{}' exception in stop() method: {}".format(self.plugin.get_shortname(), e))


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
    def process(self, msg, kwargs):
        kwargs['extra'] = self.extra
        return '{}{}'.format(self.extra['plugininstance'], msg), kwargs
# end addition von smai
