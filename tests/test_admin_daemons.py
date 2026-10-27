#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for modules/admin/daemons.py: detection of the KNX, 1-Wire, MQTT and Node-RED daemons."""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.admin import daemons


def fake_shell(outputs):
    """Return a shell_output replacement answering each command from ``outputs`` (default '')."""

    def shell_output(command, include_stderr=False):
        return outputs.get(command, '')

    return shell_output


class TestDaemonDetection(unittest.TestCase):
    def detect(self, func, outputs):
        with patch.object(daemons, 'shell_output', fake_shell(outputs)), patch.object(daemons.os, 'name', 'posix'):
            return func()

    def test_nothing_running(self):
        for func in (daemons.knx_daemon, daemons.onewire_daemon, daemons.mqtt_daemon, daemons.node_red_daemon):
            self.assertEqual('SERVICES.INACTIVE', self.detect(func, {}))

    def test_knxd_with_version(self):
        outputs = {'ps cax|grep knxd': '123 ? knxd', 'knxd -l?V|grep knxd': 'knxd 0.14.30:abc'}
        self.assertEqual('knxd v0.14.30', self.detect(daemons.knx_daemon, outputs))

    def test_knxd_without_version_output(self):
        self.assertEqual('knxd', self.detect(daemons.knx_daemon, {'ps cax|grep knxd': '123 ? knxd'}))

    def test_eibd_and_knxd(self):
        outputs = {'ps cax|grep eibd': '1 ? eibd', 'ps cax|grep knxd': '2 ? knxd'}
        self.assertEqual('eibd and knxd', self.detect(daemons.knx_daemon, outputs))

    def test_mosquitto_with_version(self):
        outputs = {
            'ps cax|grep mosquitto': '1 ? mosquitto',
            '/usr/sbin/mosquitto -h|grep version': 'mosquitto version 2.0.18',
        }
        self.assertEqual('mosquitto v2.0.18', self.detect(daemons.mqtt_daemon, outputs))

    def test_shell_output_returns_stdout(self):
        self.assertEqual('hi\n', daemons.shell_output('echo hi'))

    def test_shell_output_can_include_stderr(self):
        self.assertIn('err', daemons.shell_output('echo err 1>&2', include_stderr=True))


if __name__ == '__main__':
    unittest.main(verbosity=2)
