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


import threading
import os
import logging
import json
import cherrypy

from .rest import RESTResource


class ThreadsController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])


    def get_thread_list(self):

        """
        get a list of all threads
        """
        threads_count = 0
        cp_threads = 0
        http_threads = 0
        pool_threads = 0
        idle_threads = 0
        for thread in threading.enumerate():
            if thread.name.find("CP Server") == 0:
                cp_threads += 1
            if thread.name.find("HTTPServer") == 0:
                http_threads += 1
            if thread.name.find("ThreadPoolExecutor") == 0:
                pool_threads += 1
            if thread.name.find("idle") == 0:
                idle_threads += 1

        threads = []
        for t in threading.enumerate():
            # create thread list for admin gui
            if t.name.find("CP Server") != 0 and t.name.find("HTTPServer") != 0 and \
               t.name.find("ThreadPoolExecutor") != 0 and t.name.find("idle") != 0:
                thread = dict()
                thread['name'] = t.name
                thread['sort'] = str(t.name).lower()
                thread['id'] = t.ident
                try:
                    # get_native_id() is supported for Python 3.8 and newer
                    thread['native_id'] = t.native_id
                except:
                    thread['native_id'] = ''
                try:
                    if t.is_alive():
                        thread['alive'] = 'True'
                    else:
                        thread['alive'] = 'False'
                except AssertionError:
                    thread['alive'] = 'AssertionError'

                # self.logger.warning("get_thread_list: {}".format(thread))
                threads.append(thread)
                threads_count += 1

        if cp_threads > 0:
            threads.append(self.thread_sum("modules.http.cherrypy_server", cp_threads))
            threads_count += cp_threads
        if http_threads > 0:
            threads.append(self.thread_sum("modules.http.http_server", http_threads))
            threads_count += http_threads
        if pool_threads > 0:
            threads.append(self.thread_sum("asyncio.ThreadPoolExecutor", http_threads))
            threads_count += pool_threads
        if idle_threads > 0:
            threads.append(self.thread_sum("idle", idle_threads))
            threads_count += idle_threads

        threads_sorted = sorted(threads, key=lambda k: k['sort'])
        return json.dumps([threads_count, threads_sorted])


    def thread_sum(self, name, count):
        thread = dict()
        if count > 0:
            thread['name'] = name
            thread['sort'] = str(thread['name']).lower()
            thread['id'] = "(" + str(count) + " threads" + ")"
            thread['native_id'] = ''
            thread['alive'] = 'True'
        return thread


    # ======================================================================
    #  GET /api/threads
    #
    def read(self, id=None):
        """
        Handle GET requests for threads API
        """
        self.logger.info("ThreadsController.read()")

        return self.get_thread_list()

    read.expose_resource = True
    read.authentication_needed = True

