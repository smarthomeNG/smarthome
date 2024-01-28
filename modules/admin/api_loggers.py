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
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])
        self.etc_dir = self._sh._etc_dir

        return


    def get_active_loggers(self):

        loggerlist = []
        try:
            wrk_loggerDict = logging.Logger.manager.loggerDict
            for l in dict(wrk_loggerDict):
                lg = logging.Logger.manager.loggerDict[l]
                try:
                    not_conf = lg.not_conf
                except:
                    not_conf = False
                if not_conf:
                    self.logger.info(f"get_active_loggers: not_conf {l=} - {lg=}")
                else:
                    try:
                        h = lg.handlers
                    except:
                        h = []
                    if len(h) > 0:
                        # handlers do exist
                        if (len(h) > 1) or (len(h) == 1 and str(h[0]) != '<NullHandler (NOTSET)>'):
                            loggerlist.append(l)
                            # self.logger.info("ld Handler = {} h = {} -> {}".format(l, h, lg))
                        else:
                            pass
                            #self.logger.info(f"get_active_loggers: {l} - Not len(h) > 1) or (len(h) == 1 and str(h[0])")
                    else:
                        # no handlers exist
                        try:
                            lv = lg.level
                        except:
                            lv = 0
                        if lv > 0:
                            loggerlist.append(l)
                            # self.logger.info("ld Level   = {}, lv = {} -> {}".format(l, lv, lg))
                        else:
                            pass
                            loggerlist.append(l)
                            #self.logger.info(f"get_active_loggers: {l} - {lv=} - {wrk_loggerDict[l]}")
        except Exception as e:
            self.logger.exception("Logger Exception: {}".format(e))

        return sorted(loggerlist)


    def set_active_logger_level(self, logger, level):

        if level is not None:
            lg = logging.getLogger(logger)
            lglevel = logging.getLevelName(level)
            oldlevel = logging.getLevelName(lg.level)

            lg.setLevel(lglevel)
            self.logger.notice(f"Logger '{logger}' changed from {oldlevel} to {level}")

            logging_config = self._sh.logs.load_logging_config_for_edit()
            try:
                oldlevel = logging_config['loggers'][logger]['level']
            except:
                oldlevel = None
            if oldlevel != None:
                logging_config['loggers'][logger]['level'] = level
                self._sh.logs.save_logging_config(logging_config)
                #self.logger.info("Saved changed logger configuration to ../etc/logging.yaml}")
                return True
        return False


    def get_active_logger_handler_names(self, logger_name):

        logger = logging.getLogger(logger_name)
        handlers = logger.handlers
        handler_names = []
        for h in handlers:
            handler_names.append(h.name)
        return handler_names


    def set_handlers(self, logger_name, handler_names):

        handlerlist = handler_names.split(',')

        logger = logging.getLogger(logger_name)
        self.logger.info(f"set_handlers: logger='{logger_name}', new handlers={handlerlist})")

        # remove existing handlers from logger, which are not in the list of handlers to configure
        handlers = list(logger.handlers)
        for h in handlers:
            if not h.name in handlerlist:
                self.logger.info(f"set_handlers: - Remove handler '{h.name}' from logger '{logger_name}'")
                logger.removeHandler(h)

        # add handlers to logger, which are not in the list of existing handlers of the logger
        for hn in handlerlist:
            hn_found = False
            for h in logger.handlers:
                if h.name == hn:
                    hn_found = True
            if not hn_found:
                self.logger.info(f"set_handlers: - Add handler '{hn}' to logger '{logger_name}'")
                logger.addHandler(self._sh.logs.get_handler_by_name(hn))

        new_handler_names = sorted(self.get_active_logger_handler_names(logger_name))

        # Change configuration of logger in logging.yaml
        logging_config = self._sh.logs.load_logging_config_for_edit()
        logging_config['loggers'][logger_name]['handlers'] = new_handler_names
        self._sh.logs.save_logging_config(logging_config)

        return True


    # -----------------------------------------------------------------------------------


    def get_parent_handler_names(self, logger, handlernames):

        hl = []
        try:
            for h in logger.parent.handlers:
                try:
                    hl.append(h.name)
                except Exception as e:
                    self.logger.notice(f"get_logger_active_configuration: Exception {h=} - {h.__class__.__name__=} - {e}")
        except:
            return handlernames

        return list(set(handlernames + hl))


    def get_logger_active_configuration(self, loggername=None):

        active = {}
        active_logger = logging.getLogger(loggername)
        active['disabled'] = active_logger.disabled
        active['level'] = self._sh.logs.get_shng_logging_levels().get(active_logger.level, 'UNKNOWN_'+str(active_logger.level))
        filters = list(active_logger.filters)
        active['filters'] = []
        for filter in filters:
            active['filters'].append(str(filter))
        active['parent_handlers_names'] = []

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

        if loggername is not None:
            active['parent_handlers_names'] = self.get_parent_handler_names(active_logger, [] )
            active['parent_handlers_names'] = self.get_parent_handler_names(active_logger.parent, active['parent_handlers_names'])
            active['parent_handlers_names'] = self.get_parent_handler_names(active_logger.parent.parent, active['parent_handlers_names'])

        return active


    # ======================================================================
    #  GET /api/loggers
    #
    def read(self, id=None):
        """
        Handle GET requests for loggers API
        """
        self.logger.info(f"LoggersController.read('{id}')")

        config = self._sh.logs.load_logging_config()
        loggers = config['loggers']
        loggers['root'] = config['root']
        loggers['root']['active'] = self.get_logger_active_configuration()
        loggers['root']['logger_name'] = 'root'
        handlers = config['handlers']

        loggerlist = self.get_active_loggers()
        self.logger.info("loggerlist = {}".format(loggerlist))

        for logger in loggerlist:
            if loggers.get(logger, None) == None:
                # self.logger.info("active but not configured logger = {}".format(logger))
                loggers[logger] = {}
                loggers[logger]['logger_name'] = logger
                loggers[logger]['not_conf'] = True

            loggers[logger]['active'] = self.get_logger_active_configuration(logger)

        self.logger.info("read: logger = {} -> {}".format(logger, loggers[logger]))

        self.logger.info("read: loggers = {}".format(loggers))

        response = {}
        response['loggers'] = loggers
        response['active_plugins'] = self._sh.plugins.get_loaded_plugins()
        response['active_logics'] = self._sh.logics.get_loaded_logics()
        response['defined_handlers'] = handlers
        return json.dumps(response)

    read.expose_resource = True
    read.authentication_needed = False


    def update(self, id=None, level=None, handlers=None):
        """
        Handle PUT requests for loggers API
        """
        self.logger.info(f"LoggersController.update('{id}'), level='{level}', handlers='{handlers}'")

        if level is not None:
            if self.set_active_logger_level(id, level):
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'unable to set logger level'}

        if handlers is not None:
            if self.set_handlers(id, handlers):
                response = {'result': 'ok'}
            else:
                response = {'result': 'error', 'description': 'unable to set handlers for logger'}

        return json.dumps(response)

    update.expose_resource = True
    update.authentication_needed = True


    def add(self, id=None, level=None):
        """
        Handle DELETE requests for loggers API
        """
        self.logger.info(f"LoggersController.add('{id}', level='{level}'")

        response = {'result': 'ok', 'description': ''}
        # add logger to active loggers
        lg = logging.getLogger(id)
        default_level = logging.getLevelName(lg.parent.level)
        lg.setLevel(default_level)

        # add logger definition to logging.yaml
        logging_config = self._sh.logs.load_logging_config_for_edit()
        logging_config['loggers'][id] = {'level': default_level}
        self._sh.logs.save_logging_config(logging_config)

        self.logger.notice(f"Logger '{id}' added")

        return json.dumps(response)

    add.expose_resource = True
    add.authentication_needed = True


    def delete(self, id=None, level=None):
        """
        Handle DELETE requests for loggers API
        """
        self.logger.info("LoggersController.delete('{}', level='{}'".format(id, level))

        response = {'result': 'ok', 'description': ''}
        # delete active logger
        active_logger = logging.root.manager.loggerDict.get(id, None)
        if active_logger is None:
             response = {'result': 'error', 'description': 'active logger not found'}
        else:
            active_logger.setLevel(active_logger.parent.level)
            for hdlr in active_logger.handlers:
                active_logger.removeHandler(hdlr)

        # delete logger definition from logging.yaml
        logging_config = self._sh.logs.load_logging_config_for_edit()
        del logging_config['loggers'][id]
        self._sh.logs.save_logging_config(logging_config)

        self.logger.notice(f"Logger '{id}' removed")

        return json.dumps(response)

    delete.expose_resource = True
    delete.authentication_needed = True

