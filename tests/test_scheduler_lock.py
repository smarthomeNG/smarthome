#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the scheduler lock: diagnostics when run() cannot acquire it, and what runs while it is held.

run() executes on a real thread against a lock held by another real thread; log records are
collected by a handler on the ``lib.scheduler`` logger.
"""

import logging
import os
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.scheduler import _PriorityQueue
from tests.test_scheduler import _make_scheduler

JOIN_TIMEOUT = 5


class _RecordingHandler(logging.Handler):
    """Collects the formatted messages of the records it receives; wait_for() blocks until enough arrived."""

    def __init__(self, level: int):
        super().__init__(level)
        self.messages: list[str] = []
        self._received = threading.Condition()

    def emit(self, record: logging.LogRecord) -> None:
        with self._received:
            self.messages.append(record.getMessage())
            self._received.notify_all()

    def wait_for(self, count: int, timeout: float) -> bool:
        """True once ``count`` messages arrived, False if ``timeout`` seconds passed first."""
        with self._received:
            return self._received.wait_for(lambda: len(self.messages) >= count, timeout)


class TestLockTimeoutDiagnostics(unittest.TestCase):
    """run() names the thread holding the scheduler lock when it cannot acquire the lock within its timeout."""

    def setUp(self):
        self.sched, _ = _make_scheduler()
        self.sched._worker_num = 0
        self.sched._workers = []
        self.sched._runq = _PriorityQueue()
        self.sched._triggerq = _PriorityQueue()
        self.sched._sh.shng_status = {'code': 20, 'text': 'Running'}
        self.handler = _RecordingHandler(logging.CRITICAL)
        logging.getLogger('lib.scheduler').addHandler(self.handler)
        self.held = threading.Event()
        self.release = threading.Event()
        self.holder = threading.Thread(target=self._hold_scheduler_lock, name='lock-holder')
        self.runner = threading.Thread(target=self.sched.run, name='Scheduler')

    def tearDown(self):
        self.sched.alive = False
        self.release.set()
        for t in (self.holder, self.runner):
            if t.is_alive():
                t.join(JOIN_TIMEOUT)
        logging.getLogger('lib.scheduler').removeHandler(self.handler)

    def _hold_scheduler_lock(self):
        with self.sched._lock:
            self.held.set()
            self.release.wait(JOIN_TIMEOUT)

    def _timeout_messages(self, count: int) -> list[str]:
        """Hold the lock on another thread, run the scheduler until it logged ``count`` timeouts, stop it."""
        self.holder.start()
        self.assertTrue(self.held.wait(JOIN_TIMEOUT))
        self.runner.start()
        self.assertTrue(self.handler.wait_for(count, timeout=count + JOIN_TIMEOUT), 'no lock timeout logged')
        self.sched.alive = False
        return self.handler.messages[:count]

    def test_timeout_names_holder_thread_and_acquiring_function(self):
        (message,) = self._timeout_messages(1)
        self.assertIn('lock-holder', message)
        self.assertIn('_hold_scheduler_lock', message)

    def test_holder_stack_is_logged_once_per_acquisition(self):
        first, second = self._timeout_messages(2)
        self.assertIn('self.release.wait(JOIN_TIMEOUT)', first)
        self.assertNotIn('self.release.wait(JOIN_TIMEOUT)', second)
        self.assertIn('lock-holder', second)


class TestRemoveLocking(unittest.TestCase):
    """remove() resolves the caller-dependent entry name before it takes the scheduler lock."""

    def setUp(self):
        self.sched, _ = _make_scheduler()
        self.sched._scheduler['job1'] = {'obj': None, 'next': None, 'active': True}

    def test_caller_resolution_runs_without_lock(self):
        holders_during_resolution = []
        resolve = self.sched.check_caller

        def recording_check_caller(name, from_smartplugin=False):
            holders_during_resolution.append(self.sched._lock.holder)
            return resolve(name, from_smartplugin)

        with patch.object(self.sched, 'check_caller', side_effect=recording_check_caller):
            self.sched.remove('job1')

        self.assertEqual([None], holders_during_resolution)
        self.assertNotIn('job1', self.sched._scheduler)


if __name__ == '__main__':
    unittest.main()
