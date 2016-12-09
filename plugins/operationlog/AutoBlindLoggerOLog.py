#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2014-2016 Thomas Ernst                       offline@gmx.net
#########################################################################
#
#  Modified version used as parent class for OperationLogger
#  2016 Jan Troelsen
#
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
#
# AutoBlindLoggerOLog
#
# Extended logging functionality for debugging AutoBlind plugin
# Enables to log into different files (e.g. depending on item, room or
# similar)
#########################################################################
import logging
import datetime
import os

logger = logging.getLogger("")


class AbLogger:
    # Log-Level: (0=off 1=Info, 2=Debug)
    __loglevel = 2

    # Target directory for log files
    __logdirectory = "/usr/local/smarthome/var/log/AutoBlind/"

    # Max age for log files (days)
    __logmaxage = 0

    # Set log level
    # loglevel: current loglevel
    @staticmethod
    def set_loglevel(loglevel):
        try:
            AbLogger.__loglevel = int(loglevel)
        except ValueError:
            AbLogger.__loglevel = 2
            logger.error("Das Log-Level muss numerisch angegeben werden.")

    # Set log directory
    # logdirectory: Target directory for AutoBlind log files
    @staticmethod
    def set_logdirectory(logdirectory):
        AbLogger.__logdirectory = logdirectory

    # Set max age for log files
    # logmaxage: Maximum age for log files (days)
    @staticmethod
    def set_logmaxage(logmaxage):
        try:
            AbLogger.__logmaxage = int(logmaxage)
        except ValueError:
            AbLogger.__logmaxage = 0
            logger.error("Das maximale Alter der Logdateien muss numerisch angegeben werden.")

    @staticmethod
    def remove_old_logfiles():
        if AbLogger.__logmaxage == 0:
            return
        logger.info("Removing logfiles older than {0} days".format(AbLogger.__logmaxage))
        count_success = 0
        count_error = 0
        now = datetime.datetime.now()
        for file in os.listdir(AbLogger.__logdirectory):
            if file.endswith(".log"):
                try:
                    abs_file = os.path.join(AbLogger.__logdirectory, file)
                    stat = os.stat(abs_file)
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                    age_in_days = (now - mtime).total_seconds() / 86400.0
                    if age_in_days > AbLogger.__logmaxage:
                        os.unlink(abs_file)
                        count_success += 1
                except Exception as ex:
                    logger.error(str(ex))
                    count_error += 1
        logger.info("{0} files removed, {1} errors occured".format(count_success, count_error))

    # Return AbLogger instance for given item
    # item: item for which the detailed log is
    @staticmethod
    def create(item):
        return AbLogger(item)

    # Constructor
    # item: item for which the detailed log is (used as part of file name)
    def __init__(self, item):
        try:
            self.__section = item.id().replace(".", "_").replace("/", "")
        except (AttributeError, TypeError):
            # parameter is no item, use as text instead
            self.__section = str(item).replace(".", "_").replace("/", "")
        self.__indentlevel = 0
        self.__date = None
        self.__filename = ""

    # Update name logfile if required
    def update_logfile(self, name=None):
        if isinstance(name, type(None)):
            if self.__date == datetime.datetime.today() and self.__filename is not None:
                return
            self.__date = str(datetime.date.today())
            self.__filename = str(AbLogger.__logdirectory + self.__date + '-' + self.__section + ".log")
        else:
            self.__filename = str(AbLogger.__logdirectory + name)

    # Increase indentation level
    # by: number of levels to increase
    def increase_indent(self, by=1):
        self.__indentlevel += by

    # Decrease indentation level
    # by: number of levels to decrease
    def decrease_indent(self, by=1):
        if self.__indentlevel > by:
            self.__indentlevel -= by
        else:
            self.__indentlevel = 0

    # log text something
    # level: required loglevel
    # text: text to log
    def log(self, level, text, *args):
        # Section givn: Check level
        if level <= AbLogger.__loglevel:
            indent = "\t" * self.__indentlevel
            text = text.format(*args)
            logtext = "{0}{1} {2}\r\n".format(datetime.datetime.now(), indent, text)
            with open(self.__filename, mode="a", encoding="utf-8") as f:
                f.write(logtext)
            # JT
            logger.debug("Writing: {} to logfile: {}".format(logtext, self.__filename))

    # log header line (as info)
    # text: header text
    def header(self, text):
        self.__indentlevel = 0
        text += " "
        self.log(1, text.ljust(80, "="))

    # log with level=info
    # @param text text to log
    # @param *args parameters for text
    def info(self, text, *args):
        self.log(1, text, *args)

    # log with lebel=debug
    # text: text to log
    # *args: parameters for text
    def debug(self, text, *args):
        self.log(2, text, *args)

    # log warning (always to main smarthome.py log)
    # text: text to log
    # *args: parameters for text
    # noinspection PyMethodMayBeStatic
    def warning(self, text, *args):
        self.log(1, "WARNING: " + text, *args)
        logger.warning(text.format(*args))

    # log error (always to main smarthome.py log)
    # text: text to log
    # *args: parameters for text
    # noinspection PyMethodMayBeStatic
    def error(self, text, *args):
        self.log(1, "ERROR: " + text, *args)
        logger.error(text.format(*args))

    # log exception (always to main smarthome.py log'
    # msg: message to log
    # *args: arguments for message
    # **kwargs: known arguments for message
    # noinspection PyMethodMayBeStatic
    def exception(self, msg, *args, **kwargs):
        self.log(1, "EXCEPTION: " + msg, *args)
        logger.exception(msg, *args, **kwargs)
