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

        self.assertFalse(item._fading)


if __name__ == '__main__':
    unittest.main(verbosity=2)
