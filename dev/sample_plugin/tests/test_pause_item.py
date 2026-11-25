#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Pause item of the sample plugin, with the pause_item line in __init__ enabled."""

import tempfile
import unittest

from tests.sdp_harness import load_plugin

ITEMS = """
dev:
    pause:
        type: bool
"""


class TestSamplePauseItem(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_plugin(
            self._tmp.name,
            'dev.sample_plugin',
            'SamplePlugin',
            ITEMS,
            params={'pause_item': 'dev.pause', 'param3': 'x'},
            before_items=self.enable_pause_item,
        )
        self.plugin = self.rig.plugin
        self.pause = self.rig.item('dev.pause')
        self.requests: list[bool] = []
        on_pause_item_change = self.plugin.on_pause_item_change

        def record(paused):
            self.requests.append(paused)
            on_pause_item_change(paused)

        self.plugin.on_pause_item_change = record
        self.plugin.run()

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    @staticmethod
    def enable_pause_item(plugin):
        plugin._pause_item_path = plugin.get_parameter_value('pause_item')

    def test_external_pause_and_resume_go_through_seam(self):
        self.pause(True, 'test')
        stopped = not self.plugin.alive
        self.pause(False, 'test')

        self.assertEqual([True, False], self.requests)
        self.assertTrue(stopped)
        self.assertTrue(self.plugin.alive)

    def test_own_write_backs_are_ignored(self):
        self.plugin.stop()
        self.plugin.run()

        self.assertEqual([], self.requests)


if __name__ == '__main__':
    unittest.main(verbosity=2)
