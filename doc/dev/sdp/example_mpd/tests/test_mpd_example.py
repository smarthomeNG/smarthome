#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Behaviour of the MPD tutorial example on the real SDP stack.

The transport is a RecordingConnection; device lines are fed in through the
plugin's data hook as the TCP client would deliver them, one line per call.
Run from the shng base directory: ``pytest doc/dev/sdp/example_mpd/tests``.
"""

import os
import tempfile
import unittest

from tests.plugin_contract.base import BasePluginContractTest
from tests.plugin_contract.sdp import SdpPluginContractTest
from tests.sdp_harness import PluginNotLoaded, load_sdp_plugin
from tests.sdp_harness.characterize import items_yaml_from_struct

from doc.dev.sdp import example_mpd
from doc.dev.sdp.example_mpd import MpdSdp

CLASS_PATH = 'doc.dev.sdp.example_mpd'

ITEMS = """
mpd:
    state:
        type: str
        mpds_command: status.state
        mpds_read: true
        mpds_read_initial: true
    volume:
        type: num
        mpds_command: status.volume
        mpds_write: true
    random:
        type: bool
        mpds_command: status.random
        mpds_write: true
    elapsed:
        type: num
        mpds_command: status.elapsed
    title:
        type: str
        mpds_command: currentsong.title
        mpds_read: true
        mpds_read_initial: true
    artist:
        type: str
        mpds_command: currentsong.artist
    next:
        type: bool
        enforce_updates: true
        mpds_command: control.next
        mpds_write: true
"""


class TestMpdExample(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(self._tmp.name, CLASS_PATH, 'MpdSdp', ITEMS, params={'host': '127.0.0.1'})
        self.plugin = self.rig.plugin
        self.plugin.run()

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    def receive(self, *lines: str) -> None:
        for line in lines:
            self.plugin.on_data_received('127.0.0.1', line)

    def test_initial_read_requests_status_and_currentsong(self):
        self.rig.plugin_jobs()['read_initial_values'].fire()

        self.assertEqual(['status\n', 'currentsong\n'], self.rig.connection.payloads)

    def test_status_block_fills_all_status_items(self):
        self.receive('volume: 42', 'repeat: 0', 'random: 1', 'state: pause', 'elapsed: 12.5', 'OK')

        self.assertEqual(42, self.rig.item('mpd.volume')())
        self.assertIs(True, self.rig.item('mpd.random')())
        self.assertEqual('paused', self.rig.item('mpd.state')())
        self.assertEqual(12.5, self.rig.item('mpd.elapsed')())

    def test_flag_zero_is_false(self):
        self.receive('random: 1', 'random: 0')

        self.assertIs(False, self.rig.item('mpd.random')())

    def test_currentsong_block_fills_song_items(self):
        self.receive('file: a.flac', 'Artist: Nina Simone', 'Title: Sinnerman', 'OK')

        self.assertEqual('Sinnerman', self.rig.item('mpd.title')())
        self.assertEqual('Nina Simone', self.rig.item('mpd.artist')())

    def test_volume_write_is_clamped(self):
        self.rig.item('mpd.volume')(150, 'test')

        self.assertEqual(['setvol 100\n'], self.rig.connection.payloads)

    def test_flag_write_sends_one_or_zero(self):
        self.rig.item('mpd.random')(True, 'test')

        self.assertEqual(['random 1\n'], self.rig.connection.payloads)

    def test_action_runs_on_true_only(self):
        self.rig.item('mpd.next')(False, 'test')
        self.rig.item('mpd.next')(True, 'test')

        self.assertEqual(['next\n'], self.rig.connection.payloads)

    def test_receive_only_command_is_not_requested(self):
        self.assertFalse(self.plugin.send_command('status.volume'))

        self.assertEqual([], self.rig.connection.payloads)

    def test_error_reply_is_logged_and_changes_nothing(self):
        self.receive('volume: 42', 'ACK [50@0] {play} No such song')

        self.assertEqual(42, self.rig.item('mpd.volume')())
        self.assertTrue(any('No such song' in m for m in self.rig.logs.messages()))


class TestMpdExampleStructs(unittest.TestCase):
    def test_generated_struct_binds_items(self):
        items = items_yaml_from_struct(os.path.dirname(example_mpd.__file__), 'ALL', root='mpd')
        with tempfile.TemporaryDirectory() as tmp:
            rig = load_sdp_plugin(tmp, CLASS_PATH, 'MpdSdp', items, params={'host': '127.0.0.1'})
            rig.plugin.run()
            rig.plugin_jobs()['read_initial_values'].fire()
            rig.plugin.on_data_received('127.0.0.1', 'volume: 7')
            rig.item('mpd.control.next')(True, 'test')
            rig.plugin.stop()

        self.assertEqual(7, rig.item('mpd.status.volume')())
        self.assertEqual(['status\n', 'currentsong\n', 'next\n'], rig.connection.payloads)


class TestMpdExampleWithoutHost(unittest.TestCase):
    def test_plugin_is_not_loaded_without_host(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(PluginNotLoaded):
            load_sdp_plugin(tmp, CLASS_PATH, 'MpdSdp', '', record=False)


class TestMpdExampleContract(BasePluginContractTest, SdpPluginContractTest):
    PLUGIN_CLASS = MpdSdp
    PLUGIN_INIT_PARAMS = {}
    SDP_ITEM_ATTR_SETS = [
        {'mpds_command': 'status.state', 'mpds_read': True},
        {'mpds_command': 'status.volume', 'mpds_write': True},
        {'mpds_command': 'status.elapsed'},
    ]


if __name__ == '__main__':
    unittest.main(verbosity=2)
