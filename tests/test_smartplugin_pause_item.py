#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Pause item handling of SmartPlugin."""

import tempfile
import unittest

from tests.sdp_harness import load_plugin

ITEMS = """
dev:
    pause:
        type: bool
    other:
        type: num
"""


class _PauseTestBase(unittest.TestCase):
    class_name = 'FixturePause'
    other_sections: dict = {}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_plugin(
            self._tmp.name,
            'tests.fixture_pause_plugin',
            self.class_name,
            ITEMS,
            params={'pause_item': 'dev.pause'},
            other_sections=self.other_sections,
        )
        self.plugin = self.rig.plugin
        self.pause = self.rig.item('dev.pause')
        self.plugin.run()
        self.plugin.lifecycle.clear()

    def tearDown(self):
        self._tmp.cleanup()


class TestBasePauseHandling(_PauseTestBase):
    def test_external_pause_stops_and_resume_runs(self):
        self.pause(True, 'test')
        self.pause(False, 'test')

        self.assertEqual(['stop', 'run'], self.plugin.lifecycle)

    def test_own_write_back_does_not_stop(self):
        self.pause(True, self.plugin.get_fullname())

        self.assertEqual([], self.plugin.lifecycle)


class TestMultiInstancePauseHandling(_PauseTestBase):
    other_sections = {'second': {'pause_item': 'dev.other'}}

    def test_instance_name_differs_from_short_name(self):
        self.assertNotEqual(self.plugin.get_shortname(), self.plugin.get_fullname())

    def test_own_write_back_does_not_stop(self):
        self.pause(True, self.plugin.get_fullname())

        self.assertEqual([], self.plugin.lifecycle)

    def test_external_pause_stops(self):
        self.pause(True, 'test')

        self.assertEqual(['stop'], self.plugin.lifecycle)


class TestPauseSeam(_PauseTestBase):
    class_name = 'FixturePauseSeam'

    def test_seam_receives_pause_states_instead_of_stop_run(self):
        self.pause(True, 'test')
        self.pause(False, 'test')

        self.assertEqual([True, False], self.plugin.pause_requests)
        self.assertEqual([], self.plugin.lifecycle)


class TestOwnUpdateItemDelegatesPause(_PauseTestBase):
    class_name = 'FixturePauseOwnUpdate'

    def test_pause_item_is_handled_by_base(self):
        self.pause(True, 'test')

        self.assertEqual(['stop'], self.plugin.lifecycle)
        self.assertEqual([], self.plugin.other_updates)

    def test_other_items_reach_own_update_item(self):
        self.rig.item('dev.other')(42, 'test')

        self.assertEqual(['dev.other'], self.plugin.other_updates)


if __name__ == '__main__':
    unittest.main(verbosity=2)
