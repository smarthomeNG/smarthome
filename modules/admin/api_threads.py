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
import time
import cherrypy

from lib.scheduler import RunningTask

from .rest import ApiDoc, ApiParam, RESTResource


class ThreadsController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

    @staticmethod
    def _parse_ident(id) -> int:
        """Thread ident from a URL path segment; raises cherrypy.NotFound if it is not an integer."""
        try:
            return int(id)
        except ValueError:
            raise cherrypy.NotFound

    def _running_tasks(self) -> dict:
        """Running scheduler tasks keyed by thread ident; empty while no scheduler exists."""
        scheduler = getattr(self._sh, 'scheduler', None)
        if scheduler is None:
            return {}
        return {task.thread_ident: task for task in scheduler.get_running_tasks()}

    @staticmethod
    def _task_info(task: RunningTask) -> dict:
        """JSON-serializable view of a running scheduler task."""
        return {
            'type': task.task_type,
            'name': task.name,
            'started_at': task.started_at.isoformat(),
            'runtime': round(task.runtime, 1),
            'runtime_warn': task.runtime_warn,
            'overdue': task.overdue,
            'trigger': task.trigger,
            'task_id': task.task_id,
            'cancellable': task.cancellable,
            'cancel_requested': (
                None if task.cancel_requested_at is None else round(time.monotonic() - task.cancel_requested_at, 1)
            ),
            'cancel_requests': task.cancel_requests,
        }

    def get_thread_list(self):
        """
        get a list of all threads; threads running a scheduler task carry its info in 'task'
        """
        running = self._running_tasks()
        threads_count = 0
        cp_threads = 0
        http_threads = 0
        pool_threads = 0
        idle_threads = 0
        for thread in threading.enumerate():
            if thread.name.find('CP Server') == 0:
                cp_threads += 1
            if thread.name.find('HTTPServer') == 0:
                http_threads += 1
            if thread.name.find('ThreadPoolExecutor') == 0:
                pool_threads += 1
            if thread.name.find('idle') == 0:
                idle_threads += 1

        threads = []
        for t in threading.enumerate():
            # create thread list for admin gui
            if (
                t.name.find('CP Server') != 0
                and t.name.find('HTTPServer') != 0
                and t.name.find('ThreadPoolExecutor') != 0
                and t.name.find('idle') != 0
            ):
                thread = dict()
                thread['name'] = t.name
                thread['sort'] = str(t.name).lower()
                thread['id'] = t.ident
                try:
                    # get_native_id() is supported for Python 3.8 and newer
                    thread['native_id'] = t.native_id
                except AttributeError:
                    thread['native_id'] = ''
                try:
                    if t.is_alive():
                        thread['alive'] = 'True'
                    else:
                        thread['alive'] = 'False'
                except AssertionError:
                    thread['alive'] = 'AssertionError'
                if t.ident in running:
                    thread['task'] = self._task_info(running[t.ident])

                # self.logger.warning("get_thread_list: {}".format(thread))
                threads.append(thread)
                threads_count += 1

        if cp_threads > 0:
            threads.append(self.thread_sum('modules.http.cherrypy_server', cp_threads))
            threads_count += cp_threads
        if http_threads > 0:
            threads.append(self.thread_sum('modules.http.http_server', http_threads))
            threads_count += http_threads
        if pool_threads > 0:
            threads.append(self.thread_sum('asyncio.ThreadPoolExecutor', http_threads))
            threads_count += pool_threads
        if idle_threads > 0:
            threads.append(self.thread_sum('idle', idle_threads))
            threads_count += idle_threads

        threads_sorted = sorted(threads, key=lambda k: k['sort'])
        return json.dumps([threads_count, threads_sorted], default=str)

    def get_task_details(self, id):
        """
        get the running scheduler task and its current stack for the thread with ident ``id``

        :raises cherrypy.NotFound: if ``id`` is no thread ident or no scheduler task runs on that thread
        """
        ident = self._parse_ident(id)
        task = self._running_tasks().get(ident)
        stack = None if task is None else self._sh.scheduler.get_task_stack(ident)
        if stack is None:
            raise cherrypy.NotFound
        return json.dumps({'id': ident, 'task': self._task_info(task), 'stack': stack}, default=str)

    def thread_sum(self, name, count):
        thread = dict()
        if count > 0:
            thread['name'] = name
            thread['sort'] = str(thread['name']).lower()
            thread['id'] = '(' + str(count) + ' threads' + ')'
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
        self.logger.info('ThreadsController.read()')

        if id:
            return self.get_task_details(id)
        return self.get_thread_list()

    read.expose_resource = True
    read.authentication_needed = True
    read.api_doc = [
        ApiDoc(summary='List of running threads', method='get', path='/threads/', tags=['threads']),
        ApiDoc(
            summary='Scheduler task running on a thread, with its current call stack',
            method='get',
            path='/threads/{ident}',
            tags=['threads'],
            params=[ApiParam(name='ident', location='path', type='integer', required=True)],
        ),
    ]

    #  POST /api/threads/{ident}/cancel
    def cancel(self, id, *vpath, **params):
        """
        Handle POST requests for the /cancel sub-resource - request cancellation of the logic
        running on thread ``id``.

        Request body: JSON object with the "task_id" of the task run to cancel (from GET /api/threads),
        so a later task on the same worker thread is never hit. See ``Scheduler.cancel_task()`` for
        when the cancellation takes effect.

        Sub-resource methods reached via vpath aren't verb-gated by RESTResource's dispatcher -
        checked explicitly here.
        """
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, 'Method not allowed')
        try:
            task_id = int(json.loads(cherrypy.request.body.read())['task_id'])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body - expected {"task_id": <int>}')
        ident = self._parse_ident(id)

        result = self._sh.scheduler.cancel_task(ident, task_id)
        if result == 'not_found':
            raise cherrypy.HTTPError(404, f'No task {task_id} running on thread {ident}')
        if result == 'not_cancellable':
            raise cherrypy.HTTPError(409, f'Task {task_id} on thread {ident} is not a logic and cannot be cancelled')
        return json.dumps({'result': 'ok', 'state': result})

    cancel.expose_resource = True
    cancel.authentication_needed = True
    cancel.api_doc = [
        ApiDoc(
            summary=(
                'Request cancellation of the logic running on a thread. Takes effect at the next bytecode '
                'boundary: a blocking call (sleep, wait, socket) is interrupted only when it returns.'
            ),
            method='post',
            path='/threads/{ident}/cancel',
            tags=['threads'],
            params=[ApiParam(name='ident', location='path', type='integer', required=True)],
            request_body='application/json',
            request_example='{"task_id": 42}',
        )
    ]
