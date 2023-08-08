#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2021   Martin Sinn                         m.sinn@gmx.de
# Parts Copyright 2013  Marcus Popp                        marcus@popp.mx
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import time
import logging
import logging.handlers
import logging.config
import os
import datetime

import collections

import lib.shyaml as shyaml

logs_instance = None


class Logs():

    _logs = {}
    logging_levels = {}
    root_handler_name = ''

    NOTICE_level = 29
    DBGHIGH_level = 13
    DBGMED_level = 12
    DBGLOW_level = 11

    _all_handlers_logger_name = '_shng_all_handlers_logger'
    _all_handlers = {}


    def __init__(self, sh):

        self.logger = logging.getLogger(__name__)

        global logs_instance
        if logs_instance is None:
            logs_instance = self
        else:
            self.logger.error(f"Another instance of Logs class already exists: {logs_instance}")

        self._sh = sh
        self.etc_dir = self._sh.get_etcdir()
        return


    def configure_logging(self, config_filename='logging.yaml'):

        config_dict = self.load_logging_config(config_filename, ignore_notfound=True)

        if config_dict == None:
            print()
            print(f"ERROR: Invalid logging configuration in file '{os.path.join(self.etc_dir, config_filename)}'")
            print()
            exit(1)

        config_dict = self.add_all_handlers_logger(config_dict)

        # Default loglevels are:
        #  - CRITICAL     50
        #  - ERROR        40
        #  - WARNING      30
        #  - INFO         20
        #  - DEBUG        10

        # Additionally SmartHomeNG defines the following log levels_
        #  - NOTICE       29   (31, if logging.yaml has not been adjusted)
        #  - DBGHIGH      13   Debug high level
        #  - DBGMED       12   Debug medium level
        #  - DBGLOW       11   Debug low level

        self.logging_levels = {}
        self.logging_levels[50] = 'CRITICAL'
        self.logging_levels[40] = 'ERROR'
        self.logging_levels[30] = 'WARNING'
        self.logging_levels[20] = 'INFO'
        self.logging_levels[10] = 'DEBUG'
        self.logging_levels[0]  = 'NOTSET'

        # # self.logging_levels[31] = 'NOTICE'
        # self.logging_levels[29] = 'NOTICE'
        # self.logging_levels[13] = 'DBGHIGH'
        # self.logging_levels[12] = 'DBGMED'
        # self.logging_levels[11] = 'DBGLOW'

        # adjust config dict from logging.yaml:
        # if logger 'lib.smarthome' is not defined or no level is defined for it,
        # define logger with level 'NOTICE'
        if config_dict['loggers'].get('lib.smarthome', None) is None:
            config_dict['loggers']['lib.smarthome'] = {}
        if config_dict['loggers']['lib.smarthome'].get('level', None) is None:
            config_dict['loggers']['lib.smarthome']['level'] = 'NOTICE'

        try:
            root_handler_name = config_dict['root']['handlers'][0]
            root_handler = config_dict['handlers'][ root_handler_name ]
            root_handler_level = root_handler.get('level', '?')
            self.root_handler_name = root_handler_name
        except:
            root_handler_level = '?'

        if root_handler_level.upper() in ['NOTICE', 'INFO', 'DEBUG']:
            self.NOTICE_level = 29
        else:
            self.NOTICE_level = 31
        self.DBGHIGH_level = 13
        self.DBGMED_level = 12
        self.DBGLOW_level = 11

        # add SmartHomeNG specific loglevels
        self.add_logging_level('NOTICE', self.NOTICE_level)
        self.add_logging_level('DBGHIGH', self.DBGHIGH_level)
        self.add_logging_level('DBGMED', self.DBGMED_level)
        self.add_logging_level('DBGLOW', self.DBGLOW_level)

        try:
            logging.config.dictConfig(config_dict)
        except Exception as e:
            #self._logger_main.error(f"Invalid logging configuration in file 'logging.yaml' - Exception: {e}")
            print()
            print(f"ERROR: dictConfig: Invalid logging configuration in file '{os.path.join(self.etc_dir, config_filename)}'")
            print(f"       Exception: {e}")
            print()
            return False

        #self.logger.notice(f"Logs.configure_logging: Level NOTICE = {notice_level} / root_handler_level={root_handler_level}")

        # Initialize MemLog Handler to output root log entries to smartVISU
        self.initMemLog()

        return True


    def add_logging_level(self, description, value):
        """
        Adds a new Logging level to the standard python logging

        :param description: appearance within logs SYSINFO
        :type description: string
        :param value: numeric value for the logging level
        :type value: int
        :param tocall: function name to call for a log with the given level
        :type tocall: String, optional, if not given  description will be used with lower case

        no error checking is performed here for typos, already existing levels or functions
        """

        def logForLevel(self, message, *args, **kwargs):
            if self.isEnabledFor(value):
                self._log(value, message, args, **kwargs)

        def logToRoot(message, *args, **kwargs):
            logging.log(value, message, *args, **kwargs)

        logging.addLevelName(value, description)
        setattr(logging, description, value)
        setattr(logging.getLoggerClass(), description.lower(), logForLevel)
        setattr(logging, description.lower(), logToRoot)
        self.logging_levels[value] = description
        return


    def get_shng_logging_levels(self):
        """
        Returns a dict of the logging levels, that are defined in SmartHomeNG (key=numeric log level, value=name od loa level)

        It is used e.g. by the admin module

        :return: dict
        """
        return self.logging_levels


    def initMemLog(self):
        """
        This function initializes all needed datastructures to use the 'env.core.log' mem-logger and
        the (old) memlog plugin

        It adds the handler log_mem (based on the custom lib.log.ShngMemLogHandler) to the root logger
        It logs all WARNINGS from all (old) mem-loggers to the root Logger
        """
        log_mem = ShngMemLogHandler('env.core.log', maxlen=50, level=logging.WARNING)

        # define formatter for 'env.core.log' log
        _logdate = "%Y-%m-%d %H:%M:%S"
        _logformat = "%(asctime)s %(levelname)-8s %(threadName)-12s %(message)s"
        formatter = logging.Formatter(_logformat, _logdate)
        log_mem.setFormatter(formatter)

        # add handler to root logger
        logging.getLogger('').addHandler(log_mem)
        return




    def add_log(self, name, log):
        """
        Adds a log (object) to the list of memory logs

        :param name: Name of log
        :param log: Log object
        """
        self._logs[name] = log


    def return_logs(self):
        """
        Function to the list of memory logs

        :return: List of logs
        :rtype: list
        """
        return self._logs

    # ---------------------------------------------------------------------------

    def load_logging_config(self, filename='logging', ignore_notfound=False):
        """
        Load config from logging.yaml to a dict

        If logging.yaml does not contain a 'shng_version' key, a backup is created
        """
        conf_filename = os.path.join(self.etc_dir, filename)
        if not conf_filename.endswith('.yaml') and not conf_filename.endswith('.default'):
            conf_filename += '.yaml'
        result = shyaml.yaml_load(conf_filename, ignore_notfound)

        return result


    def save_logging_config(self, logging_config, create_backup=False):
        """
        Save dict to logging.yaml
        """
        if logging_config is not None:
            logging_config['shng_version'] = self._sh.version.split('-')[0][1:]
            conf_filename = os.path.join(self.etc_dir, 'logging')
            shyaml.yaml_save_roundtrip(conf_filename, logging_config, create_backup=create_backup)
        return


    def load_logging_config_for_edit(self):
        """
        Load config from logging.yaml to a dict

        If logging.yaml does not contain a 'shng_version' key, a backup is created
        """
        #self.etc_dir = self._sh.get_etcdir()
        conf_filename = os.path.join(self.etc_dir, 'logging')
        logging_config = shyaml.yaml_load_roundtrip(conf_filename)
        self.logger.info("load_logging_config_for_edit: shng_version={}".format(logging_config.get('shng_version', None)))

        if logging_config.get('shng_version', None) is None:
            logging_config['shng_version'] = self._sh.version.split('-')[0][1:]
            self.save_logging_config(logging_config, create_backup=True)

        return logging_config


    def add_all_handlers_logger(self, logging_config):

        lg = logging_config['loggers'].get(self._all_handlers_logger_name, None)
        if lg is None:
            logging_config['loggers'][self._all_handlers_logger_name] = {}
            lg = logging_config['loggers'].get(self._all_handlers_logger_name, None)

        hd = logging_config['loggers'][self._all_handlers_logger_name].get('handlers', None)
        if hd is None:
            logging_config['loggers'][self._all_handlers_logger_name]['handlers'] = []
            hd = logging_config['loggers'][self._all_handlers_logger_name].get('handlers', None)

        all_hdlrs = sorted(logging_config['handlers'].keys())
        logging_config['loggers'][self._all_handlers_logger_name]['handlers'] = all_hdlrs

        return logging_config


    def get_all_handlernames(self):
        if self._all_handlers == {}:
            l = logging.getLogger(self._all_handlers_logger_name)
            for h in l.handlers:
                self._all_handlers[h.name] = h

        return sorted(self._all_handlers.keys())


    def get_handler_by_name(self, handlername):

        if self._all_handlers == {}:
            self.get_all_handlernames()
        return self._all_handlers[handlername]


# -------------------------------------------------------------------------------

class Log(collections.deque):

    def __init__(self, smarthome, name, mapping, maxlen=40, handler=None):
        """
        Class to implement a memory log

        As of shng version 1.7a develop this is used in core at bin/smarthome.py and
        in plugins memlog, operationlog and visu_websocket

        :param smarthome: Dummy, for backwart compatibility
        :param name: name of the the log (used in cli plugin and smartVISU)
        :param mapping: Kind of a headline for the entry which can be anything
            e.g. mappings can be [time, thread, level, message ] and log entry is a

        :param maxlen: maximum length of the memory log, defaults to 40
        :param handler: Python LoggingHandler that created this instance of a memory log
        """
        collections.deque.__init__(self, maxlen=maxlen)
        if (mapping is None) or (mapping == []):
            self.mapping = ['time', 'thread', 'level', 'message']
        else:
            self.mapping = mapping

        self._sh = logs_instance._sh
        self._name = name
        self.handler = handler
        # Add this log to dict of defined memory logs
        logs_instance.add_log(name, self)

    def add(self, entry):
        """
        Adds a log entry to the memory log. If the log already has reached the maximum length, the oldest
        entry is removed from the log automatically.
        """
        self.appendleft(entry)
        for listener in self._sh.return_event_listeners('log'):
            listener('log', {'name': self._name, 'log': [dict(zip(self.mapping, entry))]})

    def last(self, number):
        """
        Returns the newest entries of the log

        :param number: Number of entries to return

        :return: List of log entries
        """
        return(list(self)[-number:])

    def export(self, number):
        """
        Returns the newest entries of the log and prepares them with the mapping

        :param number: Number of entries to return

        :return: List of log entries
        """
        return [dict(zip(self.mapping, x)) for x in list(self)[:number]]

    def clean(self, dt):
        """
        Assuming dt to be a datetime: remove all entries that are smaller or equal
        to this given datetime from the right side of the queue
        """
        while True:
            try:
                entry = self.pop()
            except Exception:
                return
            if entry[0] > dt:
                self.append(entry)
                return


# ================================================================================

""" 
In the following part of the code, logging handlers are defined
"""

class ShngTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    TimedRotatingFilehandler with a different naming scheme for rotated files
    """

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        # for changed naming scheme
        fName, fExt = os.path.splitext(baseName)
        fileNames = os.listdir(dirName)
        result = []
        # for changed naming scheme
        #prefix = baseName + "."
        prefix = fName + "."
        plen = len(prefix)
        # for changed naming scheme
        # for fileName in fileNames:
        #     if fileName[:plen] == prefix:
        #         suffix = fileName[plen:]
        #         if self.extMatch.match(suffix):
        #             result.append(os.path.join(dirName, fileName))
        elen = len(fExt)
        for fileName in fileNames:
            if fileName[:plen] == prefix and fileName[-elen:] == fExt:
                if plen + elen < len(fileName):
                    # ...
                    suffix = fileName[plen:]
                    if self.extMatch.match(suffix):
                        result.append(os.path.join(dirName, fileName))
                    # ...
                    #result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)

        # from logging.handlers.TimedRotatingFileHandler
        #dfn = self.rotation_filename(self.baseFilename + "." +
        #                             time.strftime(self.suffix, timeTuple))

        # for shng: splitext -> tuple ( path+fn , ext )
        bfn = os.path.splitext(self.baseFilename)[0]
        ext = os.path.splitext(self.baseFilename)[1]
        dfn = self.rotation_filename(bfn + "." + time.strftime(self.suffix, timeTuple) + ext)

        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class ShngMemLogHandler(logging.StreamHandler):
    """
    LogHandler used by MemLog
    """
    def __init__(self, logname='undefined', maxlen=35, level=logging.NOTSET):
        super().__init__()
        self.setLevel(level)

        if self.get_name() is None:
            # for 'env.core.log' memory logger
            self.set_name('_shng_root_memory')

        #logs_instance.logger.info(f"ShngMemLogHandler.__init__(): logname={logname}, self={self}, handlername={self.get_name()}, level={self.level}, levelname={logging.getLevelName(self.level)}, maxlen={maxlen}")

        self._log = Log(self, logname, ['time', 'thread', 'level', 'message'], maxlen=maxlen, handler=self)

        self._shtime = logs_instance._sh.shtime
        # Dummy baseFileName for output in shngadmin (and priv_develop plugin)
        self.baseFilename = "'" + self._log._name + "'"

    def emit(self, record):
        #logs_instance.logger.info(f"ShngMemLogHandler.emit() #1: logname={self._log._name}, handlername={self.get_name()}, level={self.level}, record.levelno={record.levelno}, record.levelname={record.levelname}, record={record}")
        #logs_instance.logger.info(f"ShngMemLogHandler.emit() #2: self={self}, handlers={logging._handlers.data}")
        try:
            self.format(record)
            timestamp = datetime.datetime.fromtimestamp(record.created, self._shtime.tzinfo())
            self._log.add([timestamp, record.threadName, record.levelname, record.message])
        except Exception:
            self.handleError(record)


