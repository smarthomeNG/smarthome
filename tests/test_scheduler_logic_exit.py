#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for leaving a logic with ``exit()`` / ``quit()``.

The builtins of the site module close ``sys.stdin`` before raising SystemExit, which blocks while another
thread reads stdin and closes the stdin of the whole process. A logic must leave it alone.
"""

import io
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from tests.test_scheduler_runtime import _TaskTestCase

DAILY_LOGIC = os.path.join(os.path.dirname(__file__), '..', 'lib', 'env', 'daily.py')


class TestLogicExit(_TaskTestCase):
    def _run_logic(self, name, code):
        """Run a logic synchronously through ``Scheduler._task()``; returns the logic."""
        logic = self._make_logic(name, code)
        logic.ran = []
        self.sched._task(f'logics.{name}', logic, 'Test', None, None, None)
        return logic

    def _assert_exit_leaves_stdin_open(self, leave):
        stdin = io.StringIO()
        with patch.object(sys, 'stdin', stdin):
            logic = self._run_logic('leaver', f'logic.ran.append(1)\n{leave}\nlogic.ran.append(2)\n')
        self.assertEqual(logic.ran, [1])
        self.assertFalse(stdin.closed)

    def test_exit_stops_the_logic_and_leaves_stdin_open(self):
        self._assert_exit_leaves_stdin_open('exit()')

    def test_quit_stops_the_logic_and_leaves_stdin_open(self):
        self._assert_exit_leaves_stdin_open('quit()')

    def test_exit_inside_a_function_of_the_logic(self):
        stdin = io.StringIO()
        with patch.object(sys, 'stdin', stdin):
            logic = self._run_logic('leaver', 'def f():\n    exit()\nf()\nlogic.ran.append(2)\n')
        self.assertEqual(logic.ran, [])
        self.assertFalse(stdin.closed)

    def test_exit_does_not_disturb_the_next_run_of_a_logic(self):
        logic = self._run_logic('leaver', 'logic.ran.append(1)\nexit()\n')
        self.sched._task('logics.leaver', logic, 'Test', None, None, None)
        self.assertEqual(logic.ran, [1, 1])

    def test_daily_logic_schedules_a_random_night_time_on_init(self):
        with open(DAILY_LOGIC, encoding='UTF-8') as f:
            code = f.read()
        logic = self._make_logic('env_daily', code)
        stdin = io.StringIO()
        with patch.object(sys, 'stdin', stdin):
            self.sched._task('logics.env_daily', logic, 'Init', None, None, 'init')
        self.assertFalse(stdin.closed)
        (name,), kwargs = self.sched._sh.scheduler.change.call_args
        minute, hour = kwargs['cron'].split()[:2]
        self.assertEqual(name, 'logics.env_daily')
        self.assertIn(int(hour), range(2, 5))
        self.assertIn(int(minute), range(0, 59))


if __name__ == '__main__':
    unittest.main()
