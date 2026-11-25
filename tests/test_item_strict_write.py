#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Item writes with ``strict=True`` raise ``ItemWriteRejected`` where a regular write is dropped silently."""

import os
import sys
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.errors import ItemWriteRejected, WriteRejectReason
from lib.item.helpers import fadejob
from lib.item._internal._hysteresis import run_hysteresis
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


class _Base(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()

    def tearDown(self):
        _reset()

    def _item(self, path='target', itype='num', value=None, **conf):
        item = lib.item.item.Item(self.sh, self.sh, path, {'type': itype, **conf})
        self.sh.items.add_item(path, item)
        if value is not None:
            item(value)
        return item


class TestTypeMismatch(_Base):
    def test_strict_write_of_a_wrong_type_raises_and_keeps_the_value(self):
        item = self._item(value=1)

        with self.assertRaises(ItemWriteRejected) as ctx:
            item('not a number', strict=True)

        self.assertIs(WriteRejectReason.TYPE, ctx.exception.reason)
        self.assertEqual('target', ctx.exception.item_path)
        self.assertEqual('not a number', ctx.exception.value)
        self.assertEqual(1, item())

    def test_regular_write_of_a_wrong_type_logs_a_warning_and_keeps_the_value(self):
        item = self._item(value=1)

        with self.assertLogs('lib.item', level='WARNING') as logs:
            result = item('not a number')

        self.assertIsNone(result)
        self.assertEqual(1, item())
        self.assertIn('does not match type num', logs.output[0])

    def test_strict_write_of_a_castable_value_stores_the_cast_value(self):
        item = self._item(value=1)

        item('5', strict=True)

        self.assertEqual(5, item())


class TestEvalItem(_Base):
    def test_strict_write_to_an_eval_item_raises_nothing(self):
        item = self._item(eval='value * 2')

        item('not a number', strict=True)


class TestSet(_Base):
    def test_strict_set_of_a_wrong_type_raises_and_keeps_the_value(self):
        item = self._item(value=1)

        with self.assertRaises(ItemWriteRejected) as ctx:
            item.set('not a number', strict=True)

        self.assertIs(WriteRejectReason.TYPE, ctx.exception.reason)
        self.assertEqual(1, item())

    def test_regular_set_of_a_wrong_type_logs_a_warning_and_keeps_the_value(self):
        item = self._item(value=1)

        with self.assertLogs('lib.item', level='WARNING') as logs:
            item.set('not a number')

        self.assertEqual(1, item())
        self.assertIn('does not match type num', logs.output[0])


class TestHysteresisItem(_Base):
    """A hysteresis output whose upper timer runs: the input is above the threshold, the delay not yet over."""

    def setUp(self):
        super().setUp()
        self.sensor = self._item('sensor', value=25)
        self.output = self._item(
            'output',
            'bool',
            hysteresis_input='sensor',
            hysteresis_upper_threshold='22 ; 60',
            hysteresis_lower_threshold='18',
        )
        self.output(False)
        run_hysteresis(self.output, value=25)
        self.assertTrue(self.output.hysteresis_data()['upper_timer_active'])

    def test_regular_write_of_a_wrong_type_keeps_the_running_timer(self):
        self.output('maybe')

        self.assertTrue(self.output.hysteresis_data()['upper_timer_active'])
        self.assertFalse(self.output())

    def test_strict_write_of_a_wrong_type_raises_and_keeps_the_running_timer(self):
        with self.assertRaises(ItemWriteRejected) as ctx:
            self.output('maybe', strict=True)

        self.assertIs(WriteRejectReason.TYPE, ctx.exception.reason)
        self.assertTrue(self.output.hysteresis_data()['upper_timer_active'])

    def test_write_of_a_valid_value_stops_the_running_timer(self):
        self.output(True)

        self.assertFalse(self.output.hysteresis_data()['upper_timer_active'])
        self.assertTrue(self.output())


class TestFading(_Base):
    """A running fade with ``stop_fade=['admin']``: only the admin may interrupt it."""

    def setUp(self):
        super().setUp()
        self.item = self._item(value=0)
        self.item.fade(10, step=1, delta=5, stop_fade=['admin'])
        self.fader = threading.Thread(target=fadejob, args=(self.item,), daemon=True)
        self.fader.start()
        self.addCleanup(self._stop_fade)
        deadline = time.monotonic() + 2
        while self.item() != 1 and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertEqual(1, self.item(), 'fade did not take its first step')

    def _stop_fade(self):
        self.item(0, caller='admin')
        self.fader.join(2)

    def test_strict_write_ignored_by_the_fade_raises_and_keeps_the_value(self):
        with self.assertRaises(ItemWriteRejected) as ctx:
            self.item(7, caller='Logic', strict=True)

        self.assertIs(WriteRejectReason.FADING, ctx.exception.reason)
        self.assertEqual(1, self.item())

    def test_regular_write_ignored_by_the_fade_raises_nothing(self):
        self.item(7, caller='Logic')

        self.assertEqual(1, self.item())

    def test_strict_write_by_a_caller_that_stops_the_fade_is_stored(self):
        self.item(7, caller='admin', strict=True)

        self.assertEqual(7, self.item())


if __name__ == '__main__':
    unittest.main()
