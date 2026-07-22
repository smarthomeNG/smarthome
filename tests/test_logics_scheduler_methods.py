#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib/logic.py's Logics.scheduler_add/scheduler_change/
scheduler_remove.

All three used to call self.get_fullname(), a method that only exists on
SmartPlugin, not Logics - guaranteed AttributeError on every call, despite
being documented public API (logics.scheduler_add() etc. in
doc/user/source/referenz/logiken/logiken_logic_objekt.rst). scheduler_change
also passed its kwargs dict positionally instead of expanding it with **,
landing it in Scheduler.change()'s from_smartplugin parameter instead of
being applied as the actual settings to change.
"""

import logging
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.logic import Logics


def _make_logics():
    logics = object.__new__(Logics)
    logics._logicname_prefix = 'logics.'
    logics.scheduler = MagicMock()
    return logics


class TestLogicsSchedulerMethods(unittest.TestCase):
    def test_scheduler_add_does_not_raise_and_prefixes_name(self):
        logics = _make_logics()
        obj = MagicMock()

        logics.scheduler_add('myjob', obj, prio=5, cron='* * * * *')

        logics.scheduler.add.assert_called_once_with(
            'logics.myjob', obj, 5, '* * * * *', None, None, None, None, from_smartplugin=True
        )

    def test_scheduler_remove_does_not_raise_and_prefixes_name(self):
        logics = _make_logics()

        logics.scheduler_remove('myjob')

        logics.scheduler.remove.assert_called_once_with('logics.myjob', from_smartplugin=False)

    def test_scheduler_change_does_not_raise_and_expands_kwargs(self):
        logics = _make_logics()

        logics.scheduler_change('myjob', cron='0 * * * *', value=42)

        logics.scheduler.change.assert_called_once_with('logics.myjob', cron='0 * * * *', value=42)


if __name__ == '__main__':
    unittest.main(verbosity=2)
