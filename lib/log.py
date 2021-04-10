#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2021   Martin Sinn                         m.sinn@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
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
import os
import datetime

import collections


logs_instance = None


def listloggers():
    rootlogger = logging.getLogger()
    print(rootlogger)
    for h in rootlogger.handlers:
        print('     %s' % h)

    for nm, lgr in logging.Logger.manager.loggerDict.items():
        print('+ [%-20s] %s ' % (nm, lgr))
        if not isinstance(lgr, logging.PlaceHolder):
            for h in lgr.handlers:
                print('     %s' % h)


class Logs():

    _logs = {}


    def __init__(self, sh):

        self.logger = logging.getLogger(__name__)

        global logs_instance
        if logs_instance is None:
            logs_instance = self
        else:
            self.logger.error(f"Another instance of Logs class already exists: {logs_instance}")

        self._sh = sh

        return


    def addLoggingLevel(self, description, value):
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


class Log(collections.deque):
    #####################################################################
    # Copyright 2012-2013   Marcus Popp                    marcus@popp.mx
    #####################################################################


    def __init__(self, smarthome, name, mapping, maxlen=40, handler=None):
        """
        Class to implement a log
        This is based on a double ended queue. New entries are appended left and old ones are popped right.


        As of version 1.7a develop this is used in core at bin/smarthome.py and
        in plugins memlog, operationlog and visu_websocket

        :param smarthome: the SmartHomeNG main object
        :param name: a descriptive name for the log
        :param mapping: Kind of a headline for the entry which can be anything
            e.g. mappings can be [time, thread, level, message ] and log entry is a

        :param maxlen: maximum length of the log, defaults to 50
        """
        collections.deque.__init__(self, maxlen=maxlen)
        if (mapping is None) or (mapping == []):
            self.mapping = ['time', 'thread', 'level', 'message']
        else:
            self.mapping = mapping
        #self.update_hooks = []     # nowhere else found, maybe not needed any more
        #self._sh = smarthome
        self._sh = logs_instance._sh
        self._name = name
        self._maxlen = maxlen
        self.handler = handler
        # Add this log to dict of defined memory logs
        logs_instance.add_log(name, self)

    def add(self, entry):
        """
        Just adds a log entry to the left side of the queue. If the queue already holds maxlen
        entries, the rightmost will be discarded automatically.
        """
        self.appendleft(entry)
        for listener in self._sh.return_event_listeners('log'):
            listener('log', {'name': self._name, 'log': [dict(zip(self.mapping, entry))]})

    def last(self, number):
        """
        Returns the last ``number`` entries of the log
        """
        return(list(self)[-number:])

    def export(self, number):
        """
        Returns up to ``number`` entries from the log and prepares them together with the mapping
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


