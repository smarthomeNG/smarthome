#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for shell injection in lib/tools.py's Tools.ping() and
lib/network.py's Network.ping().

Both must build the ping command as an argv list with no shell, so a host
value containing shell metacharacters (e.g. from an item fed by an
external, less-trusted source) is always exactly one literal argument to
the ping binary, never interpolated into a shell=True command string.
"""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.tools import Tools
from lib.network import Network

MALICIOUS_HOST = '1.1.1.1; touch /tmp/shng_test_pwned'


class TestToolsPingNoShellInjection(unittest.TestCase):
    def setUp(self):
        self.tools = Tools()

    @unittest.skipIf(os.name == 'nt', 'posix-only code path')
    def test_ping_does_not_use_a_shell(self):
        with patch('subprocess.call', return_value=1) as mock_call:
            self.tools.ping(MALICIOUS_HOST)

        args, kwargs = mock_call.call_args
        self.assertFalse(kwargs.get('shell', False), 'ping() must not invoke a shell')

    @unittest.skipIf(os.name == 'nt', 'posix-only code path')
    def test_malicious_host_is_a_single_argv_element(self):
        with patch('subprocess.call', return_value=1) as mock_call:
            self.tools.ping(MALICIOUS_HOST)

        (command,), kwargs = mock_call.call_args
        self.assertIsInstance(command, list)
        self.assertIn(MALICIOUS_HOST, command)
        # every element must be a separate argv token, not a shell-joined string
        self.assertTrue(all(';' not in part for part in command if part != MALICIOUS_HOST))


class TestNetworkPingNoShellInjection(unittest.TestCase):
    def test_ping_does_not_use_a_shell(self):
        with patch('subprocess.call', return_value=1) as mock_call:
            Network.ping(MALICIOUS_HOST)

        args, kwargs = mock_call.call_args
        self.assertFalse(kwargs.get('shell', False), 'ping() must not invoke a shell')

    def test_malicious_host_is_a_single_argv_element(self):
        with patch('subprocess.call', return_value=1) as mock_call:
            Network.ping(MALICIOUS_HOST)

        (command,), kwargs = mock_call.call_args
        self.assertIsInstance(command, list)
        self.assertIn(MALICIOUS_HOST, command)


if __name__ == '__main__':
    unittest.main(verbosity=2)
