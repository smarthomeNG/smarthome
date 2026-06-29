#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for item deletion (lib/item/_lifecycle.py).

Coverage
--------
remove():
  cycle/crontab scheduler job removed
  autotimer/threshold '-Timer' scheduler job removed
  hysteresis '-UpTimer' scheduler job removed
  hysteresis '-LoTimer' scheduler job removed
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from tests.mock.core import MockSmartHome


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _make_sh():
    _reset()
    return MockSmartHome()


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh, path, c)
    sh.items.add_item(path, i)
    return i


class RecordingScheduler:
    """Drop-in replacement for MockScheduler that records calls."""

    def __init__(self):
        self.calls = []

    def add(self, name, obj=None, prio=3, cron=None, cycle=None, value=None, offset=None, next=None, items=None):
        self.calls.append({'action': 'add', 'name': name, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next})

    def remove(self, name):
        self.calls.append({'action': 'remove', 'name': name})

    def removes(self):
        return [c for c in self.calls if c['action'] == 'remove']

    def removed_names(self):
        return [c['name'] for c in self.removes()]


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()


class TestRemoveSchedulerCleanup(_Base):
    def test_remove_clears_cycle_job(self):
        item = _item(self.sh, 'cy', cycle='30')
        item._init_start_scheduler()

        item.remove()

        self.assertIn('items.cy', self.recorder.removed_names())

    def test_remove_clears_timer_job(self):
        item = _item(self.sh, 'at', autotimer='5m = 42')

        item.remove()

        self.assertIn('items.at-Timer', self.recorder.removed_names())

    def test_remove_clears_hysteresis_up_timer_job(self):
        item = _item(self.sh, 'hu')

        item.remove()

        self.assertIn('items.hu-UpTimer', self.recorder.removed_names())

    def test_remove_clears_hysteresis_lo_timer_job(self):
        item = _item(self.sh, 'hl')

        item.remove()

        self.assertIn('items.hl-LoTimer', self.recorder.removed_names())


class TestRemoveStopsFading(_Base):
    def test_remove_stops_in_progress_fade(self):
        item = _item(self.sh, 'fd')
        item._fading = True

        item.remove()

        self.assertFalse(item._fading)

    def test_remove_without_active_fade_does_not_crash(self):
        item = _item(self.sh, 'nf')
        self.assertFalse(item._fading)

        item.remove()  # must not raise


class TestRemoveDetachesFromParent(_Base):
    def test_remove_detaches_child_from_parent(self):
        parent = lib.item.item.Item(self.sh, self.sh, 'parent', {'sub': {'type': 'num'}})
        child = parent.return_children().__next__()

        child.remove()

        self.assertNotIn(child, parent.return_children())

    def test_remove_detaches_toplevel_item_from_items(self):
        items_instance = self.sh.items
        toplevel = lib.item.item.Item(self.sh, items_instance, 'top', {'type': 'num'}, items_instance=items_instance)
        items_instance._children.append(toplevel)

        toplevel.remove()

        self.assertNotIn(toplevel, items_instance._children)


class TestRemoveDetachesShAttribute(_Base):
    def _make_toplevel(self, name):
        items_instance = self.sh.items
        item = lib.item.item.Item(self.sh, items_instance, name, {'type': 'num'}, items_instance=items_instance)
        # mirrors Items.load_itemdefinitions()'s install side
        setattr(items_instance, name, item)
        setattr(self.sh, name, item)
        return item, items_instance

    def test_remove_clears_sh_and_items_attribute(self):
        item, items_instance = self._make_toplevel('top')

        item.remove()

        self.assertFalse(hasattr(items_instance, 'top'))
        self.assertFalse(hasattr(self.sh, 'top'))

    def test_remove_does_not_clear_attribute_reassigned_to_something_else(self):
        item, items_instance = self._make_toplevel('top')

        # name got reassigned (e.g. to another item, or a plugin) before removal
        sentinel = object()
        setattr(items_instance, 'top', sentinel)
        setattr(self.sh, 'top', sentinel)

        item.remove()

        self.assertIs(items_instance.top, sentinel)
        self.assertIs(self.sh.top, sentinel)

    def test_remove_of_nested_item_does_not_touch_sh(self):
        parent = lib.item.item.Item(self.sh, self.sh, 'parent', {'sub': {'type': 'num'}})
        child = parent.return_children().__next__()

        child.remove()  # must not raise, must not touch unrelated sh attributes

        self.assertFalse(hasattr(self.sh, 'parent.sub'))

    def test_remove_of_nested_item_clears_parents_attribute(self):
        parent = lib.item.item.Item(self.sh, self.sh, 'parent', {'sub': {'type': 'num'}})
        child = parent.return_children().__next__()
        self.assertIs(parent.sub, child)

        child.remove()

        self.assertFalse(hasattr(parent, 'sub'))


class TestRemoveDetachesFromOtherItemsTriggerLists(_Base):
    def test_remove_clears_item_from_other_items_items_to_trigger(self):
        target = _item(self.sh, 'target', eval='1')
        source = _item(self.sh, 'source', eval='sh.target()', eval_trigger='target')
        target._init_prerun()
        source._init_prerun()
        self.assertIn(source, target.get_item_triggers())

        source.remove()

        self.assertNotIn(source, target.get_item_triggers())

    def test_remove_clears_item_from_other_items_hysteresis_triggers(self):
        sensor = _item(self.sh, 'sensor', 'num')
        output = _item(
            self.sh,
            'output',
            'bool',
            hysteresis_input='sensor',
            hysteresis_upper_threshold='22',
            hysteresis_lower_threshold='18',
        )
        sensor._init_prerun()
        output._init_prerun()
        self.assertIn(output, sensor.get_hysteresis_item_triggers())

        output.remove()

        self.assertNotIn(output, sensor.get_hysteresis_item_triggers())


if __name__ == '__main__':
    unittest.main(verbosity=2)
