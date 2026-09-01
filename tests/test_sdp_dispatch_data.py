#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for SmartDevicePlugin.dispatch_data()'s command-list build.

dispatch_data() must not mutate self._commands_read[command] in place:
dict.get() returns the actual stored list (not a copy) when the key
exists, and `+=` on a list mutates in place (list.__iadd__). Building the
combined read+pseudo command list must copy first - otherwise, for any
command present in both self._commands_read and self._commands_pseudo,
every call would permanently append the pseudo items onto the real,
persistent self._commands_read[command] list (unbounded growth, with the
pseudo item(s) updated more times each call as the growing list is walked
in full every time).
"""

import builtins

builtins.SDP_standalone = False

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartdeviceplugin import SmartDevicePlugin


class _FakeItem:
    def __init__(self, name):
        self.property = type('P', (), {'path': name})()
        self.calls = []

    def __call__(self, value, by=None):
        self.calls.append(value)


def _make_sdp(commands_read, commands_pseudo):
    sdp = object.__new__(SmartDevicePlugin)
    sdp.logger = logging.getLogger('test.dispatch_data')
    sdp.alive = True
    sdp.suspended = False
    sdp._commands_read = commands_read
    sdp._commands_pseudo = commands_pseudo
    return sdp


class TestDispatchDataDoesNotMutateStoredLists(unittest.TestCase):
    def setUp(self):
        self.item_real = _FakeItem('real')
        self.item_pseudo = _FakeItem('pseudo')
        self.commands_read = {'cmd1': [self.item_real]}
        self.commands_pseudo = {'cmd1': [self.item_pseudo]}
        self.sdp = _make_sdp(self.commands_read, self.commands_pseudo)

    def test_commands_read_list_does_not_grow_across_calls(self):
        for _ in range(4):
            self.sdp.dispatch_data('cmd1', 'value')

        self.assertEqual(1, len(self.commands_read['cmd1']), '_commands_read[cmd1] must not accumulate pseudo items')
        self.assertEqual(1, len(self.commands_pseudo['cmd1']))

    def test_pseudo_item_is_updated_exactly_once_per_call(self):
        for i in range(4):
            self.sdp.dispatch_data('cmd1', f'value{i}')

        self.assertEqual(['value0', 'value1', 'value2', 'value3'], self.item_pseudo.calls)

    def test_real_item_is_updated_exactly_once_per_call(self):
        for i in range(4):
            self.sdp.dispatch_data('cmd1', f'value{i}')

        self.assertEqual(['value0', 'value1', 'value2', 'value3'], self.item_real.calls)


if __name__ == '__main__':
    unittest.main(verbosity=2)
