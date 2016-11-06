#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2013   Marcus Popp                        marcus@popp.mx
# Copyright 2016-       Christian Strassburg 
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
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

import logging
import threading
import inspect
import os.path		# until Backend is modified

import lib.config
from lib.model.smartplugin import SmartPlugin
logger = logging.getLogger(__name__)


class Plugins():
    """
    Plugin loader Class. Parses config file and creates a worker thread for each plugin
    """
    _plugins = []
    _threads = []
    
    def __init__(self, smarthome, configfile):

        # until Backend plugin is modified
        if os.path.isfile(configfile+'.yaml'):
            smarthome._plugin_conf = configfile+'.yaml'
        else:
            smarthome._plugin_conf = configfile+'.conf'


        _conf = lib.config.parse_basename(configfile, configtype='plugin')
        if _conf == {}:
            return
            
        for plugin in _conf:
            args = {}
            logger.debug("Plugin: {0}".format(plugin))
            for arg in _conf[plugin]:
                if arg != 'class_name' and arg != 'class_path' and arg != 'instance':
                    value = _conf[plugin][arg]
                    if isinstance(value, str):
                        value = "'{0}'".format(value)
                    args[arg] = value
            classname = _conf[plugin]['class_name']
            classpath = _conf[plugin]['class_path']
            
            instance = ''
            if 'instance' in _conf[plugin]:
                instance = _conf[plugin]['instance'].strip()
                if instance == 'default': 
                    instance = ''

            # issue a warning if there is already a plugin that has the same classname
            # and does not have another instance
            for p in self._plugins:
                if isinstance(p, SmartPlugin):
                    if p.get_instance_name() == instance:
                        for t in self._threads:
                            if t.plugin == p:
                                prev_plugin = t.name
                                break
                        logger.warning("Plugin '{}' uses same class '{}' and instance '{}' as plugin '{}'".format(plugin, p.__class__.__name__, 'default' if instance == '' else instance, prev_plugin))
                elif hasattr(p, '_name'):
                    if p._name == classname:
                        # if already a plugin uses this class, we need to check for instance only if plugin is a smartplugin
                        # otherwise
                       logger.warning("Multiple classic plugin instances of class '{}' detected".format(classname))
                else:
                    logger.error("Plugin '{}' does not have a name!".format(p))

            try:
                plugin_thread = PluginWrapper(smarthome, plugin, classname, classpath, args, instance)
                self._threads.append(plugin_thread)
                self._plugins.append(plugin_thread.plugin)
            except Exception as e:
                logger.exception("Plugin {0} exception: {1}".format(plugin, e))
        del(_conf)  # clean up

    def __iter__(self):
        for plugin in self._plugins:
            yield plugin

    def start(self):
        logger.info('Start Plugins')
        for plugin in self._threads:
            logger.debug('Starting {} Plugin'.format(plugin.name))
            plugin.start()

    def stop(self):
        logger.info('Stop Plugins')
        for plugin in self._threads:
            logger.debug('Stopping {} Plugin'.format(plugin.name))
            plugin.stop()
    
    def get_plugin(self, name):
        """
           returns one plugin with given name 
        """
        for thread in self._threads:
            if thread.name == name:
               return thread
        return None


class PluginWrapper(threading.Thread):
    def __init__(self, smarthome, name, classname, classpath, args, instance):
        threading.Thread.__init__(self, name=name)

        exec("import {0}".format(classpath))

        #exec("self.plugin = {0}.{1}(smarthome{2})".format(classpath, classname, args))
        exec("self.plugin = {0}.{1}.__new__({0}.{1})".format(classpath, classname))
        setattr(smarthome, self.name, self.plugin)
        if isinstance(self.get_implementation(), SmartPlugin):
            if instance != '':
                logger.debug("set plugin {0} instance to {1}".format(name, instance ))
                self.get_implementation().set_instance_name(instance)
            self.get_implementation().set_sh(smarthome)

        exec("self.args = inspect.getargspec({0}.{1}.__init__)[0][1:]".format(classpath, classname))

        arglist = [name for name in self.args if name in args]
        argstring = ",".join(["{}={}".format(name, args[name]) for name in arglist])
        logger.debug("Using arguments {}".format(arglist))

        exec("self.plugin.__init__(smarthome{0}{1})".format("," if len(arglist) else "", argstring))

    def run(self):
        """
            starts this plugin instance
        """
        self.plugin.run()

    def stop(self):
        """
            stops this plugin instance
        """
        self.plugin.stop()
    
    def get_name(self):
        """
            returns the name of current plugin instance
            :rtype: str 
        """
        return self.name

    def get_ident(self):
        """
            returns the thread ident of current plugin instance
            :rtype: int
        """
        return self.ident
    
    def get_implementation(self):
        """
            returns the implementation of current plugin instance
            :rtype: object of plugin
        """
        return self.plugin
