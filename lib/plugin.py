#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2013 Marcus Popp                          marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import logging
import threading

import lib.config

logger = logging.getLogger('')


class Plugins():
    _plugins = []
    _threads = []

    def __init__(self, smarthome, configfile):
        try:
            _conf = lib.config.parse(configfile)
        except IOError as e:
            logger.critical(e)
            return

        for plugin in _conf:
            args = ''
            logger.debug("Plugin: {0}".format(plugin))
            for arg in _conf[plugin]:
                if arg != 'class_name' and arg != 'class_path':
                    value = _conf[plugin][arg]
                    if isinstance(value, str):
                        value = "'{0}'".format(value)
                    args = args + ", {0}={1}".format(arg, value)
            classname = _conf[plugin]['class_name']
            classpath = _conf[plugin]['class_path']
            try:
                plugin_thread = Plugin(smarthome, plugin, classname, classpath, args)
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


class Plugin(threading.Thread):

    def __init__(self, smarthome, name, classname, classpath, args):
        threading.Thread.__init__(self, name=name)
        exec("import {0}".format(classpath))
        exec("self.plugin = {0}.{1}(smarthome{2})".format(classpath, classname, args))
        setattr(smarthome, self.name, self.plugin)

    def run(self):
        self.plugin.run()

    def stop(self):
        self.plugin.stop()
