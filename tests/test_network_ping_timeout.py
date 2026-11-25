#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the timeout of lib/network.py's Network.ping().

The tests put a fake ``ping`` executable first on PATH, so the real
subprocess handling of Network.ping() is exercised.
"""

import os
import stat
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.network import Network


class TestNetworkPingTimeout(unittest.TestCase):
    def fake_ping(self, script: str):
        """Install a fake ``ping`` running *script* at the front of PATH."""
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = os.path.join(directory.name, 'ping')
        with open(path, 'w') as f:
            f.write('#!/bin/sh\n' + script + '\n')
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
        patcher = patch.dict(os.environ, {'PATH': directory.name + os.pathsep + os.environ['PATH']})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_hanging_ping_is_a_failure_after_the_timeout(self):
        self.fake_ping('sleep 10')

        start = time.monotonic()
        result = Network.ping('192.0.2.1', timeout=0.3)

        self.assertFalse(result)
        self.assertLess(time.monotonic() - start, 5)

    def test_answering_ping_is_a_success(self):
        self.fake_ping('exit 0')

        self.assertTrue(Network.ping('192.0.2.1', timeout=2))

    def test_failing_ping_is_a_failure(self):
        self.fake_ping('exit 1')

        self.assertFalse(Network.ping('192.0.2.1'))

    def test_default_timeout_ends_a_hanging_ping(self):
        self.fake_ping('sleep 30')

        start = time.monotonic()
        self.assertFalse(Network.ping('192.0.2.1'))
        self.assertLess(time.monotonic() - start, 10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
