#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_threads.py's ThreadsController: running scheduler tasks in the
thread list (GET /api/threads) and a task's stack (GET /api/threads/<ident>).
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

from modules.admin.api_threads import ThreadsController
from tests.test_scheduler_runtime import BUSY_LOGIC_CODE, JOIN_TIMEOUT, _TaskTestCase


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh


class TestThreadsApi(_TaskTestCase):
    def setUp(self):
        super().setUp()
        self.sched._sh.scheduler = self.sched
        self.controller = ThreadsController(_FakeModule(self.sched._sh))

    def test_thread_list_includes_running_task_info(self):
        _, t = self._run_hanging_method('plugins.foo.poll')

        count, threads = json.loads(self.controller.read())
        [entry] = [th for th in threads if th['id'] == t.ident]

        self.assertEqual(entry['name'], 'plugins.foo.poll')
        self.assertEqual(entry['task']['type'], 'method')
        self.assertEqual(entry['task']['name'], 'plugins.foo.poll')
        self.assertEqual(entry['task']['runtime_warn'], 120)
        self.assertFalse(entry['task']['overdue'])
        self.assertGreaterEqual(entry['task']['runtime'], 0)

    def test_threads_without_task_have_no_task_info(self):
        count, threads = json.loads(self.controller.read())

        main = [th for th in threads if th['name'] == 'MainThread']
        self.assertEqual(len(main), 1)
        self.assertNotIn('task', main[0])

    def test_read_by_ident_returns_task_and_stack(self):
        _, t = self._run_hanging_method('plugins.foo.poll')

        result = json.loads(self.controller.read(id=str(t.ident)))

        self.assertEqual(result['id'], t.ident)
        self.assertEqual(result['task']['name'], 'plugins.foo.poll')
        self.assertIn('self.release.wait(JOIN_TIMEOUT)', ''.join(result['stack']))

    def test_read_by_ident_without_running_task_is_not_found(self):
        with self.assertRaises(cherrypy.NotFound):
            self.controller.read(id='1')

    def test_read_by_non_numeric_ident_is_not_found(self):
        with self.assertRaises(cherrypy.NotFound):
            self.controller.read(id='abc')

    def test_thread_list_task_info_carries_cancel_state(self):
        _, t = self._run_hanging_logic('slow')

        count, threads = json.loads(self.controller.read())
        [entry] = [th for th in threads if th['id'] == t.ident]

        self.assertTrue(entry['task']['cancellable'])
        self.assertIsNone(entry['task']['cancel_requested'])
        self.assertEqual(entry['task']['cancel_requests'], 0)
        self.assertIsInstance(entry['task']['task_id'], int)


class TestCancelApi(_TaskTestCase):
    def setUp(self):
        super().setUp()
        self.sched._sh.scheduler = self.sched
        self.controller = ThreadsController(_FakeModule(self.sched._sh))
        request = MagicMock()
        request.method = 'POST'
        self._patch = patch.object(cherrypy, 'request', request)
        self._patch.start()
        self.addCleanup(self._patch.stop)

    def _post_cancel(self, ident, task_id):
        cherrypy.request.body.read.return_value = json.dumps({'task_id': task_id}).encode()
        return self.controller.cancel(str(ident))

    def test_cancel_running_logic(self):
        logic, t = self._run_hanging_logic('busy', BUSY_LOGIC_CODE)
        [running] = self.sched.get_running_tasks()

        result = json.loads(self._post_cancel(t.ident, running.task_id))
        t.join(JOIN_TIMEOUT)

        self.assertEqual(result, {'result': 'ok', 'state': 'requested'})
        self.assertFalse(t.is_alive())

    def test_cancel_finished_or_other_task_is_404(self):
        _, t = self._run_hanging_logic('slow')
        [running] = self.sched.get_running_tasks()

        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self._post_cancel(t.ident, running.task_id + 1)
        self.assertEqual(ctx.exception.status, 404)

    def test_cancel_method_task_is_409(self):
        _, t = self._run_hanging_method('plugins.foo.poll')
        [running] = self.sched.get_running_tasks()

        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self._post_cancel(t.ident, running.task_id)
        self.assertEqual(ctx.exception.status, 409)

    def test_cancel_with_get_is_405(self):
        cherrypy.request.method = 'GET'
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.cancel('1')
        self.assertEqual(ctx.exception.status, 405)

    def test_cancel_without_task_id_is_400(self):
        cherrypy.request.body.read.return_value = b'{}'
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.cancel('1')
        self.assertEqual(ctx.exception.status, 400)


if __name__ == '__main__':
    unittest.main()
