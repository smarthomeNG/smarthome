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
from lib.constants import DIR_ETC, BASE_LOG
import jwt
from .rest import ApiDoc, ApiParam, RESTResource


class LogsController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)
        self.log_dir = os.path.join(self.base_dir, 'var', 'log')

        self.logging_conf = shyaml.yaml_load(self._sh.get_config_file(BASE_LOG))

        self.chunksize = self.module.log_chunksize

        try:
            roothandler = self.logging_conf['root']['handlers'][0]
            self.root_logname = os.path.splitext(
                os.path.basename(self.logging_conf['handlers'][roothandler]['filename'])
            )[0]
        except (KeyError, IndexError):
            self.root_logname = ''
        self.logger.info('logging_conf: self.root_logname = {}'.format(self.root_logname))

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
            fnl = fn.split('.')
            if (len(fnl) == 2) and (fnl[1] == 'log'):
                log_name = fnl[0]

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
            # if fn.startswith(log_name+'.log'):
            if (fn.startswith(log_name + '.') and fn.endswith('.log')) or fn.startswith(log_name + '.log'):
                size = round(os.path.getsize(os.path.join(self.log_dir, fn)) / 1024, 1)
                logfiles.append([fn, size])
        return logfiles

    @staticmethod
    def _iter_log_entries(path):
        """
        Yield ``(raw_line_no, entry_text)`` for every logical log entry in the
        file at *path*, merging traceback continuation lines into the entry
        they belong to: a line starting with ``'Traceback'``, and every
        following indented (``'  '``-prefixed) line up to and including the
        first non-indented line after it, is appended to the *previous*
        entry rather than starting a new one - same convention the reader
        has always used, just applied consistently across the whole file in
        one pass instead of being re-derived per chunk request.

        *raw_line_no* is the 1-based physical file line number of the last
        raw line consumed by that entry (a running total, not an index) -
        this is what lets callers compute true chunk/line offsets without
        assuming a fixed number of raw lines per logical entry, which breaks
        as soon as any entry spans more than one physical line.

        :param path: Path of the logfile to read
        :type path: str

        :return: generator of (raw_line_no, entry_text) pairs, in file order
        :rtype: Iterator[tuple[int, str]]
        """
        with open(path, 'r', encoding='UTF-8') as lfile:
            raw_line_no = 0
            entry_text = None
            entry_end_line = 0
            appending = False
            for line in lfile:
                raw_line_no += 1
                if line.startswith('Traceback'):
                    appending = True
                if appending and entry_text is not None:
                    entry_text += '> ' + line.replace(' ', chr(160))
                    entry_end_line = raw_line_no
                    if (not line.startswith('Traceback')) and (not line.startswith('  ')):
                        appending = False
                    continue
                if entry_text is not None:
                    yield entry_end_line, entry_text
                entry_text = line.replace(' ', chr(160))
                entry_end_line = raw_line_no
            if entry_text is not None:
                yield entry_end_line, entry_text

    # ======================================================================
    #  GET /api/logs
    #
    def read(self, id=None, chunk='1', count='10'):
        """
        Handle GET requests for logs API
        """
        self.logger.info('LogsController.read({}, chunk={})'.format(id, chunk))

        if Utils.is_int(chunk):
            chunk = int(chunk)
        else:
            chunk = 1

        # id may name an in-memory log (e.g. 'env.core.log', the root
        # WARNING+ buffer from lib.log.ShngMemLogHandler) instead of a file
        # on disk. These are already maintained incrementally at log-emit
        # time, so serving them is just a deque read, no file I/O - checked
        # before the file-directory scan below, which touches disk (and on
        # a bare checkout with no var/log/ yet, e.g. a fresh CI runner,
        # would raise before ever reaching this branch otherwise).
        if id is not None:
            memlogs = self._sh.logs.return_logs()
            if id in memlogs:
                if Utils.is_int(count):
                    count = int(count)
                else:
                    count = 10
                return json.dumps({'name': id, 'entries': memlogs[id].export(count)}, default=str)

        # get names of files in log directory
        wrkl = sorted(os.listdir(self.log_dir))
        self.files = []
        for fn in wrkl:
            if not (fn.startswith('.')):
                if os.path.isfile(os.path.join(self.log_dir, fn)):
                    self.files.append(fn)
        # get names of logs (from filenames enting with '.log')
        logs = self.get_logs()
        if id is None:
            # get list of existing logs and name of default log
            logs = self.get_logs_with_files()
            return json.dumps({'logs': logs, 'default': self.root_logname})

        # Deactivated 2026-07-20 to check whether anything still depends on it: shngadmin's
        # log-display.component.ts already gets each log's rotated-file list from the bulk
        # GET /api/logs/ response (get_logs_with_files() above embeds it) and never calls
        # this branch separately. If nothing breaks, remove for good.
        # if id in logs:
        #     # get filenames available for the specified log (if log is specified without extension)
        #     logfiles = self.get_files_of_log(id)
        #     return json.dumps(sorted(logfiles))

        logfile_path = os.path.join(self.log_dir, id)
        if os.path.isfile(logfile_path):
            # return content of the logfile specified in id, if file is found

            # Full-file scan, every request: entries[i] = (raw_line_no, text)
            # for the i-th logical entry, raw_line_no being that entry's last
            # physical line. This is what makes 'chunks' (total page count)
            # and true raw-line offsets possible - a chunk's raw line span
            # can no longer be derived from chunksize*index once any entry
            # in an earlier chunk spanned more than one physical line (a
            # traceback), so counting is done directly instead of assumed.
            entries = list(self._iter_log_entries(logfile_path))
            total_entries = len(entries)
            chunks_total = max(1, -(-total_entries // self.chunksize))  # ceil div

            if chunk == 0:
                # sentinel: caller wants the last (possibly partial) chunk
                chunk_no = chunks_total
            elif chunk < 1:
                chunk_no = 1
            else:
                chunk_no = chunk

            start_index = (chunk_no - 1) * self.chunksize
            end_index = start_index + self.chunksize
            window = entries[start_index:end_index]
            loglines = [text for _raw_line_no, text in window]

            # Raw line the previous chunk ended on, clamped to the file's
            # actual last entry for an out-of-range chunk request (avoids
            # indexing past the end instead of mirroring it).
            prev_entry_index = min(start_index, total_entries)
            prev_end_raw_line = entries[prev_entry_index - 1][0] if prev_entry_index > 0 else 0
            last_raw_line = window[-1][0] if window else prev_end_raw_line

            result = {}
            result['file'] = id
            result['filesize'] = round(os.path.getsize(logfile_path) / 1024, 1)
            result['chunk'] = chunk_no
            result['chunksize'] = self.chunksize
            result['chunks'] = chunks_total
            result['lastchunk'] = chunk_no >= chunks_total
            result['lines'] = [prev_end_raw_line + 1, last_raw_line]
            result['loglines'] = loglines
            return json.dumps(result)

        raise cherrypy.NotFound

    read.expose_resource = True
    read.authentication_needed = True
    read.api_doc = [
        ApiDoc(summary='List of available log files', method='get', path='/logs/', tags=['logs']),
        ApiDoc(
            summary=(
                "One chunk of a log file's content. The per-log-name rotated-file-list "
                'variant of this path was deactivated 2026-07-20 (see the commented-out '
                'branch above) - only real filenames on disk are served now.'
            ),
            method='get',
            path='/logs/{filename}',
            tags=['logs'],
            params=[
                ApiParam(name='filename', location='path', required=True),
                ApiParam(
                    name='chunk',
                    type='integer',
                    default=1,
                    description='1 = first chunk; 0 is the server convention for "last chunk".',
                ),
            ],
        ),
        ApiDoc(
            summary=(
                "Tail of an in-memory log (e.g. 'env.core.log', the root WARNING+ buffer). "
                'Matched by name against registered memory logs before falling back to the '
                'file lookup above.'
            ),
            method='get',
            path='/logs/{name}',
            tags=['logs'],
            params=[
                ApiParam(name='name', location='path', required=True),
                ApiParam(name='count', type='integer', default=10, description='Number of newest entries to return.'),
            ],
        ),
    ]
