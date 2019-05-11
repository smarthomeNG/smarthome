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
from lib.utils import Utils

import jwt
from .rest import RESTResource


class LogsController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.etc_dir = self._sh._etc_dir
        self.log_dir = os.path.join(self.base_dir, 'var', 'log')

        self.logging_conf = shyaml.yaml_load(os.path.join(self.etc_dir, 'logging.yaml'))

        self.chunksize = self.module.log_chunksize

        try:
            roothandler = self.logging_conf['root']['handlers'][0]
            self.root_logname = os.path.splitext(os.path.basename(self.logging_conf['handlers'][roothandler]['filename']))[0]
        except:
            self.root_logname = ''
        self.logger.info("logging_conf: self.root_logname = {}".format(self.root_logname))

        return


    def get_logs(self):
        """
        Return the names of logs (names of .log-files without the extension)

        :return: names of logs
        :rtype: list
        """
        logs = []
        for fn in self.files:
            if os.path.splitext(fn)[1] == '.log':
                log_name = os.path.splitext(fn)[0]
                logs.append(log_name)
        return logs


    def get_logs_with_files(self):
        """
        Return the names of logs (names of .log-files without the extension)

        :return: names of logs
        :rtype: list
        """
        logs = {}
        for fn in self.files:
            if os.path.splitext(fn)[1] == '.log':
                log_name = os.path.splitext(fn)[0]

                logfiles = self.get_files_of_log(log_name)
                logs[log_name] = sorted(logfiles)
        return logs


    def get_files_of_log(self, log_name):
        """
        Return the files (actual and passed days) of a log

        :param log_name: name of the log
        :type log_name: str
        :return: filenames
        :rtype: list
        """
        logfiles = []
        for fn in self.files:
            if fn.startswith(log_name+'.log'):
                size = round(os.path.getsize(os.path.join(self.log_dir, fn)) / 1024, 1)
                logfiles.append([fn,size])
        return logfiles


    # ======================================================================
    #  GET /api/logs
    #
    def read(self, id=None, chunk='1'):
        """
        Handle GET requests for logs API
        """
        self.logger.info("LogsController.read({}, chunk={})".format(id, chunk))

        if Utils.is_int(chunk):
            chunk = int(chunk)
        else:
            chunk = 1

        # get names of files in log directory
        self.files = sorted(os.listdir(self.log_dir))
        # get names of logs (from filenames enting with '.log')
        logs = self.get_logs()

        if id is None:
            # get list of existing logs and name of default log
            logs = self.get_logs_with_files()
            return json.dumps({'logs':logs, 'default': self.root_logname})

        if id in logs:
            # get filenames available for the specified log (if log is specified without extension)
            logfiles = self.get_files_of_log(id)
            return json.dumps(sorted(logfiles))

        if os.path.isfile(os.path.join(self.log_dir, id)):
            # return content of the logfile specified in id, if file is found
            chunk_read = 0
            if chunk > 0:
                chunk_read = chunk-1
            skiplines = self.chunksize * (chunk-1)
            if skiplines < 0:
                skiplines = 0
            skipcount = 0

            # read logfile
            with open(os.path.join(self.log_dir, id), 'r') as lfile:
                append_to_previous_line = False
                loglines = []
                lastchunk = True
                # read lines of logfile
                for line in lfile:
                    if (skiplines > 0) and (skipcount < skiplines):
                        # skip line, if not reading first chunk
                        skipcount += 1
                    else:
                        if len(loglines) < self.chunksize:
                            if line.startswith('Traceback'):
                                append_to_previous_line = True
                            if append_to_previous_line:
                                # append to previous log line
                                loglines[len(loglines)-1] += '> ' + line.replace(" ", chr(160))
                                if (not line.startswith('Traceback')) and (not line.startswith('  ')):
                                    # last line of multiline traceback reached
                                    append_to_previous_line = False
                            else:
                                # append new log line
                                loglines.append(line.replace(" ", chr(160)))
                        else:
                            # chunk length reached, but there is another line
                            lastchunk = False
                            if chunk != 0:
                                break
                            else:
                                chunk_read += 1
                                # skip forward till last chunk is read
                                loglines = []
                                loglines.append(line.replace(" ", chr(160)))
                                if chunk == 0:
                                    lastchunk = True

                chunk_read += 1
            # return content
            first_chunk_line = (chunk_read-1)*self.chunksize   # zero based
            result = {}
            result['file'] = id
            result['filesize'] = round(os.path.getsize(os.path.join(self.log_dir, id)) / 1024, 1)
            result['chunk'] = chunk_read
            result['chunksize'] = self.chunksize
            result['lastchunk'] = lastchunk
            result['lines'] = [first_chunk_line + 1, first_chunk_line + len(loglines)]
            result['loglines'] = loglines
            return json.dumps(result)

        raise cherrypy.NotFound

    read.expose_resource = True
    read.authentication_needed = True

