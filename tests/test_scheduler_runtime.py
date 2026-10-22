#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the scheduler's running-task tracking (runtime, runtime_warn warnings, stack dumps).

Tasks run through the real ``Scheduler._task()`` on real threads; a ``threading.Event``
keeps a task "hanging" until the test (or tearDown) releases it.
"""

import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.logic import Logic
from tests.test_scheduler import _make_scheduler

JOIN_TIMEOUT = 5

HANGING_LOGIC_CODE = 'logic.entered.set()\nlogic.release.wait(5)\n'

BUSY_LOGIC_CODE = 'logic.entered.set()\nwhile not logic.release.is_set():\n    pass\n'

POLLING_LOGIC_CODE = 'logic.entered.set()\nwhile not logic.release.is_set():\n    logic.release.wait(0.05)\n'


class _HangingTask:
    """Scheduler task (method type) that blocks until released."""

    def __init__(self):
        self.entered = threading.Event()
        self.release = threading.Event()

    def __call__(self):
        self.entered.set()
        self.release.wait(JOIN_TIMEOUT)


class _TaskTestCase(unittest.TestCase):
    """Scheduler fixture plus helpers that run hanging tasks on worker threads; tearDown releases and joins them."""

    def setUp(self):
        self.sched, _ = _make_scheduler()
        self.sched._sh._runtime_warn = 120
        self.sched._sh.shng_status = {'code': 20, 'text': 'Running'}
        self.sched.mqtt = MagicMock()
        self.threads = []
        self.releases = []
        self.logic_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        for release in self.releases:
            release.set()
        for t in self.threads:
            t.join(JOIN_TIMEOUT)
        self.logic_dir.cleanup()

    def _make_logic(self, name, code=HANGING_LOGIC_CODE, **attributes):
        """
        Build a real ``Logic`` from ``code``; the default code blocks until ``logic.release`` is set.

        ``logic.entered`` is set once the logic code runs.
        """
        pathname = os.path.join(self.logic_dir.name, f'{name}.py')
        with open(pathname, 'w', encoding='UTF-8') as f:
            f.write(code)
        logics = MagicMock()
        logics.shtime = self.sched.shtime
        with patch('lib.logic.Logics.get_instance'):
            logic = Logic(self.sched._sh, name, {'pathname': pathname, **attributes}, logics)
        logic.entered = threading.Event()
        logic.release = threading.Event()
        self.releases.append(logic.release)
        return logic

    def _run_hanging_logic(self, name, code=HANGING_LOGIC_CODE, **attributes):
        """Start a hanging logic on a worker thread and wait until its code runs; returns (logic, thread)."""
        logic = self._make_logic(name, code, **attributes)
        t = self._run_in_worker(f'logics.{name}', logic)
        self.assertTrue(logic.entered.wait(JOIN_TIMEOUT))
        return logic, t

    def _run_hanging_method(self, name='plugins.foo.poll'):
        """Start a hanging method task on a worker thread and wait until it runs; returns (task, thread)."""
        task = _HangingTask()
        self.releases.append(task.release)
        t = self._run_in_worker(name, task)
        self.assertTrue(task.entered.wait(JOIN_TIMEOUT))
        return task, t

    def _run_in_worker(self, name, obj, value=None):
        """Run ``obj`` via ``Scheduler._task()`` on its own thread, as a worker would."""
        t = threading.Thread(target=self.sched._task, args=(name, obj, 'Test', None, None, value), daemon=True)
        t.start()
        self.threads.append(t)
        return t


class TestRunningTasks(_TaskTestCase):
    def test_running_method_is_listed_and_removed_when_done(self):
        task, t = self._run_hanging_method('plugins.foo.poll')

        [running] = self.sched.get_running_tasks()
        self.assertEqual(running.name, 'plugins.foo.poll')
        self.assertEqual(running.task_type, 'method')
        self.assertEqual(running.thread_ident, t.ident)

        task.release.set()
        t.join(JOIN_TIMEOUT)
        self.assertEqual(self.sched.get_running_tasks(), [])

    def test_task_escaping_with_base_exception_is_removed_and_worker_marked_idle(self):
        class _Abort(BaseException):
            pass

        def abort():
            raise _Abort

        thread_names = []

        def worker():
            try:
                self.sched._task('plugins.foo.abort', abort, 'Test', None, None, None)
            except _Abort:
                thread_names.append(threading.current_thread().name)

        t = threading.Thread(target=worker)
        t.start()
        t.join(JOIN_TIMEOUT)

        self.assertEqual(thread_names, ['idle'])
        self.assertEqual(self.sched.get_running_tasks(), [])

    def test_running_logic_carries_trigger_and_own_runtime_warn(self):
        self._run_hanging_logic('slow', runtime_warn=5)

        [running] = self.sched.get_running_tasks()
        self.assertEqual(running.task_type, 'logic')
        self.assertEqual(running.name, 'logics.slow')
        self.assertEqual(running.runtime_warn, 5)
        self.assertEqual(running.trigger['by'], 'Test')

    def test_logic_without_runtime_warn_uses_global_threshold(self):
        self._run_hanging_logic('plain')

        [running] = self.sched.get_running_tasks()
        self.assertEqual(running.runtime_warn, 120)

    def test_invalid_logic_runtime_warn_is_logged_and_falls_back_to_global(self):
        with self.assertLogs('lib.scheduler', 'WARNING') as logs:
            self._run_hanging_logic('broken', runtime_warn='soon')

        [running] = self.sched.get_running_tasks()
        self.assertEqual(running.runtime_warn, 120)
        self.assertIn("invalid runtime_warn 'soon'", logs.output[0])

    def test_invalid_global_runtime_warn_is_logged_once_and_replaced_by_default(self):
        self.sched._sh._runtime_warn = 'abc'

        with self.assertLogs('lib.scheduler', 'WARNING') as logs:
            self._run_hanging_method('plugins.foo.a')
            self._run_hanging_method('plugins.foo.b')

        self.assertEqual(len(logs.output), 1)
        self.assertIn("invalid runtime_warn 'abc'", logs.output[0])
        self.assertEqual({t.runtime_warn for t in self.sched.get_running_tasks()}, {120})


class TestRuntimeWarnings(_TaskTestCase):
    def test_logic_warns_at_runtime_warn_and_each_doubling_with_stack(self):
        self._run_hanging_logic('slow', runtime_warn=5)
        [running] = self.sched.get_running_tasks()

        with self.assertNoLogs('logics.slow', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 4.9)
        with self.assertLogs('logics.slow', 'WARNING') as logs:
            self.sched._check_task_runtimes(now=running.started + 5)
        self.assertIn('running for 5 s', logs.output[0])
        self.assertIn('logic.release.wait(5)', logs.output[0])
        with self.assertNoLogs('logics.slow', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 9.9)
        with self.assertLogs('logics.slow', 'WARNING') as logs:
            self.sched._check_task_runtimes(now=running.started + 10)
        self.assertIn('running for 10 s', logs.output[0])

    def test_skipped_thresholds_produce_one_warning_and_next_one_after_highest(self):
        self._run_hanging_logic('slow', runtime_warn=5)
        [running] = self.sched.get_running_tasks()

        with self.assertLogs('logics.slow', 'WARNING') as logs:
            self.sched._check_task_runtimes(now=running.started + 25)
        self.assertEqual(len(logs.output), 1)
        with self.assertNoLogs('logics.slow', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 39.9)
        with self.assertLogs('logics.slow', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 40)

    def test_warned_logic_logs_notice_when_it_finishes(self):
        logic, t = self._run_hanging_logic('slow', runtime_warn=5)
        [running] = self.sched.get_running_tasks()
        with self.assertLogs('logics.slow', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 5)

        with self.assertLogs('logics.slow', 'INFO') as logs:
            logic.release.set()
            t.join(JOIN_TIMEOUT)
        self.assertEqual(logs.records[-1].levelname, 'NOTICE')
        self.assertIn('finished after', logs.records[-1].getMessage())

    def test_runtime_warn_zero_disables_warnings(self):
        self._run_hanging_logic('long', runtime_warn=0)
        [running] = self.sched.get_running_tasks()

        with self.assertNoLogs('logics.long', 'WARNING'):
            self.sched._check_task_runtimes(now=running.started + 10_000)

    def test_method_warning_goes_to_scheduler_logger(self):
        self.sched._sh._runtime_warn = 5
        self._run_hanging_method('plugins.foo.poll')
        [running] = self.sched.get_running_tasks()

        with self.assertLogs('lib.scheduler', 'WARNING') as logs:
            self.sched._check_task_runtimes(now=running.started + 5)
        self.assertIn('plugins.foo.poll', logs.output[0])


class TestCancelTask(_TaskTestCase):
    def test_busy_logic_is_cancelled_and_logged(self):
        logic, t = self._run_hanging_logic('busy', BUSY_LOGIC_CODE)
        [running] = self.sched.get_running_tasks()

        with self.assertLogs('logics.busy', 'WARNING') as logs:
            self.assertEqual(self.sched.cancel_task(running.thread_ident, running.task_id), 'requested')
            t.join(JOIN_TIMEOUT)

        self.assertFalse(t.is_alive())
        self.assertIn('cancelled after', logs.output[-1])
        self.assertIn('busy.py', logs.output[-1])
        self.assertEqual(self.sched.get_running_tasks(), [])
        self.assertIsNone(logic.last_run())

    def test_polling_logic_is_cancelled_when_its_wait_returns(self):
        _, t = self._run_hanging_logic('poll', POLLING_LOGIC_CODE)
        [running] = self.sched.get_running_tasks()

        self.sched.cancel_task(running.thread_ident, running.task_id)
        t.join(JOIN_TIMEOUT)

        self.assertFalse(t.is_alive())
        self.assertEqual(self.sched.get_running_tasks(), [])

    def test_method_is_not_cancellable(self):
        self._run_hanging_method('plugins.foo.poll')
        [running] = self.sched.get_running_tasks()

        self.assertFalse(running.cancellable)
        self.assertEqual(self.sched.cancel_task(running.thread_ident, running.task_id), 'not_cancellable')

    def test_other_task_id_on_same_thread_is_not_found(self):
        self._run_hanging_logic('slow')
        [running] = self.sched.get_running_tasks()

        self.assertEqual(self.sched.cancel_task(running.thread_ident, running.task_id + 1), 'not_found')
        [still_running] = self.sched.get_running_tasks()
        self.assertIsNone(still_running.cancel_requested_at)

    def test_repeated_requests_are_counted_and_keep_first_request_time(self):
        self._run_hanging_logic('slow')
        [running] = self.sched.get_running_tasks()

        self.sched.cancel_task(running.thread_ident, running.task_id)
        [first] = self.sched.get_running_tasks()
        self.sched.cancel_task(running.thread_ident, running.task_id)
        [second] = self.sched.get_running_tasks()

        self.assertEqual(second.cancel_requests, 2)
        self.assertEqual(second.cancel_requested_at, first.cancel_requested_at)

    def test_runtime_cancel_requests_cancellation_once_exceeded(self):
        _, t = self._run_hanging_logic('busy', BUSY_LOGIC_CODE, runtime_cancel=8)
        [running] = self.sched.get_running_tasks()

        self.sched._check_task_runtimes(now=running.started + 7.9)
        [still_running] = self.sched.get_running_tasks()
        self.assertIsNone(still_running.cancel_requested_at)

        with self.assertLogs('logics.busy', 'WARNING') as logs:
            self.sched._check_task_runtimes(now=running.started + 8)
            t.join(JOIN_TIMEOUT)
        self.assertFalse(t.is_alive())
        self.assertIn('cancelled after', logs.output[-1])


class TestWorkerLoop(_TaskTestCase):
    """A real ``Scheduler._worker()`` loop serving the run queue."""

    def setUp(self):
        super().setUp()
        self.sched.alive = True
        self.worker = threading.Thread(target=self.sched._worker, daemon=True)

    def tearDown(self):
        self.sched.alive = False
        with self.sched._runc:
            self.sched._runc.notify_all()
        super().tearDown()
        if self.worker.is_alive():
            self.worker.join(JOIN_TIMEOUT)

    def _queue(self, name, obj):
        self.sched.trigger(name, obj, by='Test')

    def test_task_queued_without_waiting_worker_starts_without_wait_timeout(self):
        task = _HangingTask()
        task.release.set()
        self._queue('plugins.foo.queued', task)

        self.worker.start()

        self.assertTrue(task.entered.wait(0.5))

    def test_worker_runs_next_task_after_cancelled_one(self):
        self.worker.start()
        logic = self._make_logic('busy', BUSY_LOGIC_CODE)
        self._queue('logics.busy', logic)
        self.assertTrue(logic.entered.wait(JOIN_TIMEOUT))
        [running] = self.sched.get_running_tasks()
        self.sched.cancel_task(running.thread_ident, running.task_id)

        follow_up = _HangingTask()
        follow_up.release.set()
        self._queue('plugins.foo.next', follow_up)

        self.assertTrue(follow_up.entered.wait(JOIN_TIMEOUT))
        self.assertTrue(self.worker.is_alive())


if __name__ == '__main__':
    unittest.main()
