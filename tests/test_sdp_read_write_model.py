#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""read/write declare device operations; every item bound to a command receives its values."""

import tempfile
import unittest

from lib.model.sdp.globals import SDPError
from tests.sdp_harness import load_sdp_plugin

ITEMS = """
dev:
    mode:
        type: str
        fx_command: status.mode
        fx_write: true
    mode_read_requested:
        type: str
        fx_command: status.mode
        fx_read: true
    info:
        type: str
        fx_command: status.info
    power:
        type: bool
        fx_command: status.power
        fx_read: true
        fx_write: true
"""


class TestReadWriteModel(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDP', ITEMS)
        self.plugin = self.rig.plugin
        self.plugin.run()
        self.rig.connection.sent.clear()

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    def test_write_only_item_receives_values(self):
        self.plugin.dispatch_data('status.mode', 'eco', 'test')

        self.assertEqual('eco', self.rig.item('dev.mode')())

    def test_item_with_ignored_read_receives_values(self):
        self.plugin.dispatch_data('status.mode', 'eco', 'test')

        self.assertEqual('eco', self.rig.item('dev.mode_read_requested')())

    def test_pseudo_command_item_receives_values(self):
        self.plugin.dispatch_data('status.info', 'hello', 'test')

        self.assertEqual('hello', self.rig.item('dev.info')())

    def test_non_readable_command_is_not_requested(self):
        self.assertFalse(self.plugin.send_command('status.mode'))
        self.assertFalse(self.plugin.send_command('status.info'))

        self.assertEqual([], self.rig.connection.payloads)

    def test_non_readable_request_raises_on_request(self):
        with self.assertRaises(SDPError):
            self.plugin.send_command('status.mode', raise_on_error=True)

    def test_read_all_requests_only_readable_commands(self):
        self.plugin.read_all_commands()

        self.assertEqual(['PW'], self.rig.connection.payloads)

    def test_write_only_command_is_written(self):
        self.rig.item('dev.mode')('eco', 'test')

        self.assertEqual(['MO'], self.rig.connection.payloads)


if __name__ == '__main__':
    unittest.main(verbosity=2)
