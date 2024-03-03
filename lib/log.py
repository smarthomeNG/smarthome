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
import pickle
import re
from pathlib import Path

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
        return


    def configure_logging(self, config_filename='logging.yaml'):

        config_dict = self.load_logging_config(config_filename, ignore_notfound=True)

        if config_dict == None:
            print()
            print(f"ERROR: Invalid logging configuration in file '{os.path.join(self._sh.get_etcdir(), config_filename)}'")
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
            print(f"ERROR: dictConfig: Invalid logging configuration in file '{os.path.join(self._sh.get_etcdir(), config_filename)}'")
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
        conf_filename = os.path.join(self._sh.get_etcdir(), filename)
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
            conf_filename = os.path.join(self._sh.get_etcdir(), 'logging')
            shyaml.yaml_save_roundtrip(conf_filename, logging_config, create_backup=create_backup)
        return


    def load_logging_config_for_edit(self):
        """
        Load config from logging.yaml to a dict

        If logging.yaml does not contain a 'shng_version' key, a backup is created
        """
        #self.etc_dir = self._sh.get_etcdir()
        conf_filename = os.path.join(self._sh.get_etcdir(), 'logging')
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

class DateTimeRotatingFileHandler(logging.StreamHandler):
    """
    Handler for logging to file using current date and time information in
    the filename. Either placeholders can be used or a standard pattern is used.
    Rotating the log file at each `when` beginning.
    If backupCount is > 0, when rollover is done, no more than backupCount
    files are kept - the oldest ones are deleted.
    """

    def __init__(self,
                 filename,
                 when='H',
                 interval=1,
                 backupCount=0,
                 encoding=None,
                 delay=True,
                 utc=False):

        super().__init__()
        self._shtime = logs_instance._sh.shtime
        logging.Handler.__init__(self)
        self._originalname = os.path.basename(filename)
        self._fullname = filename
        self._fn = os.path.splitext(self._originalname)[0]
        self._ext = os.path.splitext(self._originalname)[1]
        self.stream = None
        self.encoding = encoding
        self.delay = delay
        self._when = when.upper()
        self.backup_count = backupCount

        # Current 'when' events supported:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        if self._when == 'S':
            self.time_unit = datetime.timedelta(seconds=1)  # one second
            self.suffix = "%Y-%m-%d-%H.%M.%S"
            self.ext_pat = re.compile(r"^\d{4}\-\d{2}\-\d{2}\-\d{2}\.\d{2}\.\d{2}", re.ASCII)
        if self._when == 'M':
            self.time_unit = datetime.timedelta(minutes=1)  # one minute
            self.suffix = "%Y-%m-%d-%H.%M"
            self.ext_pat = re.compile(r"^\d{4}\-\d{2}\-\d{2}\-\d{2}\.\d{2}", re.ASCII)
        elif self._when == 'H':
            self.time_unit = datetime.timedelta(hours=1)  # one hour
            self.suffix = "%Y-%m-%d-%H"
            self.ext_pat = re.compile(r"^\d{4}\-\d{2}\-\d{2}\-\d{2}", re.ASCII)
        elif self._when == 'D' or self._when == 'MIDNIGHT':
            self.time_unit = datetime.timedelta(days=1)  # one day
            self.suffix = "%Y-%m-%d"
            self.ext_pat = re.compile(r"^\d{4}\-\d{2}\-\d{2}", re.ASCII)
        else:
            raise ValueError(f"Invalid rollover interval specified: {self._when}")

        self.interval = self.time_unit * interval  # multiply by units requested
        self.rollover_at = self.next_rollover_time()
        self.baseFilename = self.get_filename()  # logging to this file

        if not delay:
            self.stream = self._open()

    def parseFilename(self, filename) -> str:
        now = self._shtime.now()
        try:
            # replace placeholders by actual datetime
            return filename.format(**{'year': now.year, 'month': now.month,
                                   'day': now.day, 'hour': now.hour,
                                   'minute': now.minute, 'intstamp': int(now.timestamp()),
                                   'stamp': now.timestamp()})
        except Exception:
            return filename

    def get_filename(self) -> str:
        filename = self.parseFilename(self._fullname)
        if '{' not in self._originalname:
            dirName, _ = os.path.split(filename)
            fn = self._fn + '.' + datetime.datetime.now().strftime(self.suffix) + self._ext
            filename = os.path.join(dirName, fn)
        if self._fullname.startswith("."):
            shng_dir = Path(logs_instance._sh.get_basedir())
            filename = str((shng_dir / filename).resolve())
        dirName, _ = os.path.split(filename)
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
        return filename

    def close(self):
        """
        Closes the stream.
        """
        self.acquire()
        try:
            try:
                if self.stream:
                    try:
                        self.flush()
                    finally:
                        stream = self.stream
                        self.stream = None
                        if hasattr(stream, "close"):
                            stream.close()
            finally:
                logging.StreamHandler.close(self)
        finally:
            self.release()

    def _open(self):
        """
        Open the current base file with encoding.
        Return the resulting stream.
        """
        return open(self.baseFilename, 'a', encoding=self.encoding)

    def next_rollover_time(self):
        """
        Work out the rollover time based on current time.
        """
        t = self._shtime.now()
        if self._when == 'S':
            t = t.replace(microsecond=0)
        elif self._when == 'M':
            t = t.replace(second=0, microsecond=0)
        elif self._when == 'H':
            t = t.replace(minute=0, second=0, microsecond=0)
        elif self._when == 'D' or self._when == 'MIDNIGHT':
            t = t.replace(hour=0, minute=0, second=0, microsecond=0)
        return t + self.interval

    def get_files_to_delete(self):
        """
        Determine the files to delete when rolling over.
        """
        def custom_replace(match):
            # Replace based on different patterns
            if any(match.group(i) for i in (1, 2, 3)):
                return '\d{4}'
            elif any(match.group(i) for i in (4, 7, 10, 13)):
                return '\d{1,2}'
            elif any(match.group(i) for i in (6, 9, 12, 15)):
                return '\d{2}'
            elif any(match.group(i) for i in (5, 8, 11, 14)):
                return '\d{1}'
            elif match.group(16):
                return '\d+'
            else:
                return '[0-9.]'

        dir_name, base_fname = os.path.split(self.baseFilename)
        fileNames = os.listdir(dir_name)
        result = []
        if '{' in self._originalname:
            year = r'{year}'
            year2 = r'{year:02}'
            year4 = r'{year:04}'
            month = r'{month}'
            month1 = r'{month:01}'
            month2 = r'{month:02}'
            day = r'{day}'
            day1 = r'{day:01}'
            day2 = r'{day:02}'
            hour = r'{hour}'
            hour1 = r'{hour:01}'
            hour2 = r'{hour:02}'
            minute = r'{minute}'
            minute1 = r'{minute:01}'
            minute2 = r'{minute:02}'
            intstamp = r'{intstamp}'
            stamp = r'{stamp}'

            combined_pattern = f'({year})|({year2})|({year4})|({month})'\
                f'|({month1})|({month2})|({day})|({day1})|({day2})|({hour})'\
                f'|({hour1})|({hour2})|({minute})|({minute1})|({minute2})|({intstamp})|({stamp})'
            regex_result = re.sub(combined_pattern, custom_replace, self._originalname)
            pattern_regex = re.compile(regex_result)
            for fileName in fileNames:
                if pattern_regex.match(fileName):
                    result.append(os.path.join(dir_name, fileName))
        else:
            prefix = self._fn + "."
            plen = len(prefix)
            elen = len(self._ext) * -1
            for fileName in fileNames:
                cond1 = fileName.startswith(prefix)
                cond2 = self.ext_pat.match(fileName[plen:elen])
                cond3 = fileName.endswith(self._ext)
                if cond1 and cond2 and cond3:
                    result.append(os.path.join(dir_name, fileName))

        if len(result) < self.backup_count:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backup_count]
        return result

    def do_rollover(self):
        """
        Do a rollover. In this case, the current stream will be closed and a new
        filename will be generated when the rollover happens.
        If there is a backup count, then we have to get a list of matching
        filenames, sort them and remove the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        self.rollover_at = self.next_rollover_time()
        self.baseFilename = self.get_filename()

        if self.backup_count > 0:
            for s in self.get_files_to_delete():
                os.remove(s)

        if not self.delay:
            self.stream = self._open()

    def emit(self, record):
        """
        Emit a record.
        Output the record to the file, catering for rollover as described
        in do_rollover().
        """
        try:
            if self._shtime.now() >= self.rollover_at:
                self.do_rollover()
            if self.stream is None:
                self.stream = self._open()
            logging.StreamHandler.emit(self, record)
        except Exception:
            self.handleError(record)

# ================================================================================

"""
In the following part of the code, logging handlers are defined
"""

class ShngTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    TimedRotatingFilehandler with a different naming scheme for rotated files
    """
    def __init__(self, filename, when='MIDNIGHT', interval=0, backupCount=0, encoding=None, delay=False, utc=False):
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        day = datetime.datetime.now().strftime("%d")
        hour = datetime.datetime.now().strftime("%H")
        stamp = datetime.datetime.now().timestamp()
        try:
            filename = eval(f"f'{filename}'")
        except Exception:
            pass
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)

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
    def __init__(self, logname='undefined', maxlen=35, level=logging.NOTSET,
            mapping=['time', 'thread', 'level', 'message'], cache=False):
        super().__init__()
        self.setLevel(level)

        if self.get_name() is None:
            # for 'env.core.log' memory logger
            self.set_name('_shng_root_memory')

        #logs_instance.logger.info(f"ShngMemLogHandler.__init__(): logname={logname}, self={self}, handlername={self.get_name()}, level={self.level}, levelname={logging.getLevelName(self.level)}, maxlen={maxlen}")

        self._log = Log(self, logname, mapping, maxlen=maxlen, handler=self)
        self._shtime = logs_instance._sh.shtime
        # Dummy baseFileName for output in shngadmin (and priv_develop plugin)
        self.baseFilename = "'" + self._log._name + "'"
        self._cache = cache
        self._maxlen = maxlen
        # save cache files in var/log/cache directory
        cache_directory = os.path.join(logs_instance._sh.get_vardir(), 'log'+os.path.sep, 'cache'+os.path.sep)
        if cache is True:
            if not os.path.isdir(cache_directory):
                os.makedirs(cache_directory)
            self._cachefile = cache_directory + self._log._name
            try:
                self.__last_change, self._logcache = self._cache_read(self._cachefile, self._shtime.tzinfo())
                self.load(self._logcache)
                logs_instance.logger.debug(f"Memory Log {self._log._name}: read cache: {self._logcache}")
            except Exception:
                try:
                    self._cache_write(logs_instance.logger, self._cachefile, self._log.export(int(self._maxlen)))
                    self._cache_read(self._cachefile, self._shtime.tzinfo())
                    logs_instance.logger.info(f"Memory Log {self._log._name}: generated cache file")
                except Exception as e:
                    pass
                    logs_instance.logger.warning(f"Memory Log: problem reading cache: {e}")

    def emit(self, record):
        #logs_instance.logger.info(f"ShngMemLogHandler.emit() #1: logname={self._log._name}, handlername={self.get_name()}, level={self.level}, record.levelno={record.levelno}, record.levelname={record.levelname}, record={record}")
        #logs_instance.logger.info(f"ShngMemLogHandler.emit() #2: self={self}, handlers={logging._handlers.data}")
        try:
            self.format(record)
            timestamp = datetime.datetime.fromtimestamp(record.created, self._shtime.tzinfo())
            self._log.add([timestamp, record.threadName, record.levelname, record.message])
        except Exception:
            self.handleError(record)
        if self._cache is True:
            try:
                self._cache_write(logs_instance.logger, self._cachefile, self._log.export(int(self._maxlen)))
            except Exception as e:
                logs_instance.logger.warning(f"Memory Log {self._log._name}: could not update cache {e}")


    ##############################################################################################
    # Cache Methods, taken from operationlog plugin by Jan Troelsen, Oliver Hinckel, Bernd Meiners
    ##############################################################################################
    def load(self, logentries):
        """
        Loads logentries (which were just read from cache) into the log object (see lib.log.Log())
        """
        if len(logentries) != 0:
            for logentry in reversed(logentries):
                log = []
                for name in self._log.mapping:
                    if name == 'time':
                        log.append(logentry['time'])
                    elif name == 'thread':
                        log.append(logentry['thread'])
                    elif name == 'level':
                        log.append(logentry['level'])
                    elif name == 'message':
                        log.append(logentry['message'])
                self._log.add(log)

    def _cache_read(self, filename, tz):
        """
        This loads the cache from a file

        :param filename: file to load from
        :param tz: timezone
        :return: [description]
        :rtype: a tuple with datetime and values from file
        """
        ts = os.path.getmtime(filename)
        dt = datetime.datetime.fromtimestamp(ts, tz)
        value = None
        with open(filename, 'rb') as f:
            value = pickle.load(f)
        return (dt, value)


    def _cache_write(self, logger, filename, value):
        try:
            with open(filename, 'wb') as f:
                pickle.dump(value, f)
        except IOError:
            logger.warning("Could not write to {}".format(filename))
