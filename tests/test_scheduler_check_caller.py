#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Scheduler.check_caller() appends the instance name of a calling multi-instance plugin to scheduler names,
so that the plugin's instances do not share scheduler entries.
"""

import unittest
from unittest.mock import patch

from tests import common

common.register_shng_log_levels()

from lib.model.smartplugin import SmartPlugin
from lib.scheduler import Scheduler


class _Scheduler:
    """Stands in for the Scheduler methods (get, change, trigger, remove) that call check_caller()."""

    check_caller = Scheduler.check_caller

    def get(self, name, from_smartplugin=False):
        return self.check_caller(name, from_smartplugin)


class _Plugin(SmartPlugin):
    def __init__(self, instance):
        self._instance = instance

    def get_instance_name(self):
        return self._instance

    def ask(self, scheduler, name, from_smartplugin=False):
        return scheduler.get(name, from_smartplugin)


class TestCheckCaller(unittest.TestCase):
    def setUp(self):
        self.scheduler = _Scheduler()

    def test_instance_name_is_appended_for_a_plugin_caller(self):
        self.assertEqual('poll_bad', _Plugin('bad').ask(self.scheduler, 'poll'))

    def test_name_with_instance_suffix_is_kept(self):
        self.assertEqual('poll_bad', _Plugin('bad').ask(self.scheduler, 'poll_bad'))

    def test_plugin_without_instance_name(self):
        self.assertEqual('poll', _Plugin('').ask(self.scheduler, 'poll'))

    def test_from_smartplugin_keeps_the_name(self):
        self.assertEqual('poll', _Plugin('bad').ask(self.scheduler, 'poll', from_smartplugin=True))

    def test_other_callers_keep_the_name(self):
        self.assertEqual('poll', self.scheduler.get('poll'))

    def test_the_call_stack_is_not_collected(self):
        with patch('inspect.stack', side_effect=AssertionError('inspect.stack() called')):
            self.assertEqual('poll_bad', _Plugin('bad').ask(self.scheduler, 'poll'))


if __name__ == '__main__':
    unittest.main()
