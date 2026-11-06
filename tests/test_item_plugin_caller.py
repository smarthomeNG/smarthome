#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Caller that plugins receive in update_item() for items with an eval.

Plugins compare it with their own name to skip echoes of what they wrote themselves:

- A plugin's write to an item with an eval is such an echo: the plugin gets its own name.
- An eval triggered by another item derives a new value: the plugin gets ``Eval:<origin>``, so
  the value is sent even if the plugin also wrote the triggering item.
"""

import collections
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from lib.scheduler import Scheduler
from tests.mock.core import MockSmartHome


class PluginCallerTestCase(unittest.TestCase):
    """Real items whose scheduler triggers run through the real task dispatch."""

    def setUp(self):
        lib.item.items._items_instance = None
        lib.item.item._items_instance = None
        Items._Items__items = []
        Items._Items__item_dict = {}
        Items._children = []
        Items.plugin_attributes = {}
        Items.plugin_attribute_prefixes = {}
        Items.plugin_prefixes_tuple = None
        self.sh = MockSmartHome()
        self.tasks = collections.deque()
        self.sh.trigger = self._queue
        self.updates = []

    def _queue(self, name, obj=None, by='Logic', source=None, value=None, dest=None, prio=3, dt=None):
        self.tasks.append((name, obj, by, source, dest, value))

    def run_tasks(self):
        while self.tasks:
            Scheduler._dispatch_task(None, *self.tasks.popleft())

    def item(self, path, itype='bool', **conf):
        item = lib.item.item.Item(self.sh, self.sh.items, path, {'type': itype, **conf})
        self.sh.items.add_item(path, item)
        vars(self.sh)[path] = item
        return item

    def update_item(self, item, caller=None, source=None, dest=None):
        """Stands in for a plugin's update_item()."""
        self.updates.append(caller)


class TestTriggeredEval(PluginCallerTestCase):
    def test_eval_triggered_by_another_item_keeps_the_eval_prefix(self):
        origin = self.item('origin')
        derived = self.item('derived', eval='sh.origin()', eval_trigger='origin')
        derived._init_prerun()
        derived.add_method_trigger(self.update_item)

        origin(True, 'knx', '1.1.27:ga=4/0/1', '4/0/1')
        self.run_tasks()

        self.assertTrue(derived())
        self.assertEqual(['Eval:knx'], self.updates)

    def test_plugin_that_wrote_the_triggering_item_is_not_named_as_caller(self):
        origin = self.item('origin')
        derived = self.item('derived', eval='sh.origin()', eval_trigger='origin')
        derived._init_prerun()
        derived.add_method_trigger(self.update_item)

        origin(True, 'knx')
        self.run_tasks()

        self.assertNotIn('knx', self.updates)


class TestOwnWrite(PluginCallerTestCase):
    def test_write_to_an_item_with_eval_reports_the_plugin_itself(self):
        item = self.item('calculated', eval='value')
        item.add_method_trigger(self.update_item)

        item(True, 'knx', '1.1.27:ga=4/0/1', '4/0/1')
        self.run_tasks()

        self.assertTrue(item())
        self.assertEqual(['knx'], self.updates)


class TestAutotimer(PluginCallerTestCase):
    def test_autotimer_of_a_triggered_item_is_not_restarted_by_an_autotimer_chain(self):
        origin = self.item('origin')
        derived = self.item('derived', eval='sh.origin()', eval_trigger='origin', autotimer='60 = False')
        derived._init_prerun()
        timers = []
        self.sh.scheduler.add = lambda name, *args, **kwargs: timers.append(name)

        origin(True, 'Autotimer')
        self.run_tasks()

        self.assertTrue(derived())
        self.assertEqual([], timers)

    def test_autotimer_of_a_triggered_item_starts_on_any_other_origin(self):
        origin = self.item('origin')
        derived = self.item('derived', eval='sh.origin()', eval_trigger='origin', autotimer='60 = False')
        derived._init_prerun()
        timers = []
        self.sh.scheduler.add = lambda name, *args, **kwargs: timers.append(name)

        origin(True, 'knx')
        self.run_tasks()

        self.assertEqual(1, len(timers))


if __name__ == '__main__':
    unittest.main()
