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

import jwt
from .rest import RESTResource


class LoggersController(RESTResource):

    logging_config = None

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.etc_dir = self._sh._etc_dir
        # self.log_dir = os.path.join(self.base_dir, 'var', 'log')

        self.logging_levels = {}
        self.logging_levels[50] = 'CRITICAL'
        self.logging_levels[40] = 'ERROR'
        self.logging_levels[30] = 'WARNING'
        self.logging_levels[29] = 'NOTICE'
        self.logging_levels[20] = 'INFO'
        self.logging_levels[10] = 'DEBUG'
        self.logging_levels[0] = 'NOTSET'

        return


    def save_logging_config(self):
        """
        Save dict to logging.yaml
        """
        if self.logging_config is not None:
            conf_filename = os.path.join(self.etc_dir, 'logging')
            shyaml.yaml_save_roundtrip(conf_filename, self.logging_config, create_backup=False)
        return


    def load_logging_config(self):
        """
        Load config from logging.yaml to a dict

        If logging.yaml does not contain a 'shng_version' key, a backup is created
        """
        conf_filename = os.path.join(self.etc_dir, 'logging')
        result = shyaml.yaml_load(conf_filename + '.yaml')

        return result


    def load_logging_config_for_edit(self):
        """
        Load config from logging.yaml to a dict

        If logging.yaml does not contain a 'shng_version' key, a backup is created
        """
        conf_filename = os.path.join(self.etc_dir, 'logging')
        self.logging_config = shyaml.yaml_load_roundtrip(conf_filename)
        self.logger.warning(
            "load_logging_config: shng_version={}".format(self.logging_config.get('shng_version', None)))

        if self.logging_config.get('shng_version', None) is None:
            self.create_backupfile(conf_filename)
            self.logging_config['shng_version'] = 'x'
            self.save_logging_config()

        return


    def get_active_loggers(self):

        loggerlist = []
        try:
            for l in logging.Logger.manager.loggerDict:
                lg = logging.Logger.manager.loggerDict[l]

                try:
                    h = lg.handlers
                except:
                    h = []
                if len(h) > 0:
                    if (len(h) > 1) or (len(h) == 1 and str(h[0]) != '<NullHandler (NOTSET)>'):
                        loggerlist.append(l)
                        # self.logger.info("ld Handler = {} h = {} -> {}".format(l, h, lg))
                else:
                    try:
                        lv = lg.level
                    except:
                        lv = 0
                    if lv > 0:
                        loggerlist.append(l)
                        # self.logger.info("ld Level   = {}, lv = {} -> {}".format(l, lv, lg))
        except Exception as e:
            self.logger.exception("Logger Exception: {}".format(e))

        return sorted(loggerlist)


    def set_active_logger_level(self, logger, level):

        if level is not None:
            self.logger.warning("set_active_logger_level(): logger={}, level={}".format(logger, level))
            lg = logging.getLogger(logger)
            lglevel = logging.getLevelName(level)
            self.logger.warning("set_active_logger_level(): lg={}, lglevel={}".format(lg, lglevel))
            lg.setLevel(lglevel)

            self.load_logging_config_for_edit()
            try:
                oldlevel = self.logging_config['loggers'][logger]['level']
            except:
                oldlevel = None
            if oldlevel != None:
                self.logger.warning(" - old level={}".format(oldlevel))
                self.logging_config['loggers'][logger]['level'] = level
                self.save_logging_config()
                return True
        return False

    # -----------------------------------------------------------------------------------


    def get_logger_active_configuration(self, loggername=None):

        active = {}
        active_logger = logging.getLogger(loggername)
        active['disabled'] = active_logger.disabled
        #active['level'] = self.logging_levels[active_logger.level]
        active['level'] = self.logging_levels.get(active_logger.level, 'UNKNOWN_'+str(active_logger.level))
        active['filters'] = active_logger.filters

        hl = []
        bl = []
        for h in active_logger.handlers:
            hl.append(h.__class__.__name__)
            try:
                bl.append(h.baseFilename)
            except:
                bl.append('')

        active['handlers'] = hl
        active['logfiles'] = bl

        return active


    # ======================================================================
    #  GET /api/loggers
    #
    def read(self, id=None):
        """
        Handle GET requests for loggers API
        """
        self.logger.info("LoggersController.read()")

        config = self.load_logging_config()
        loggers = config['loggers']
        loggers['root'] = config['root']
        loggers['root']['active'] = self.get_logger_active_configuration()

        loggerlist = self.get_active_loggers()
        self.logger.info("loggerlist = {}".format(loggerlist))

        for logger in loggerlist:
            if loggers.get(logger, None) == None:
                # self.logger.info("active but not configured logger = {}".format(logger))
                loggers[logger] = {}
                loggers[logger]['not_conf'] = True

            loggers[logger]['active'] = self.get_logger_active_configuration(logger)

        self.logger.info("logger = {} -> {}".format(logger, loggers[logger]))

        self.logger.info("loggers = {}".format(loggers))

        return json.dumps(loggers)

    read.expose_resource = True
    read.authentication_needed = False


    def update(self, id=None, level=None):
        self.logger.info("LoggersController.update('{}'), level='{}'".format(id, level))

        if self.set_active_logger_level(id, level):
            response = {'result': 'ok'}
        else:
            response = {'result': 'error', 'description': 'unable to set logger level'}

        return json.dumps(response)

    update.expose_resource = True
    update.authentication_needed = True
