#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the pip command line built by lib/shpypi.py for requirements installs.

Coverage
--------
- inside a virtualenv the install command has no ``--user``
- outside a virtualenv the install command has ``--user``
- ``--no-warn-script-location`` is present in both cases
- virtualenv detection follows ``sys.prefix != sys.base_prefix``
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib import shpypi
from lib.shpypi import Shpypi

PIP = '/opt/venv/bin/pip3'
REQ_FILE = '/opt/shng/requirements/base.txt'


class TestBuildInstallCommand(unittest.TestCase):
    def test_virtualenv_has_no_user_flag(self):
        cmd = Shpypi.build_install_command(PIP, REQ_FILE, in_virtualenv=True)
        self.assertNotIn('--user', cmd.split())

    def test_system_python_has_user_flag(self):
        cmd = Shpypi.build_install_command(PIP, REQ_FILE, in_virtualenv=False)
        self.assertIn('--user', cmd.split())

    def test_common_parts_in_both_cases(self):
        for in_venv in (True, False):
            with self.subTest(in_virtualenv=in_venv):
                cmd = Shpypi.build_install_command(PIP, REQ_FILE, in_virtualenv=in_venv)
                self.assertEqual(cmd.split()[:4], [PIP, 'install', '-r', REQ_FILE])
                self.assertIn('--no-warn-script-location', cmd.split())


class TestIsVirtualenv(unittest.TestCase):
    def test_prefix_differs_from_base_prefix(self):
        with mock.patch.object(sys, 'prefix', '/opt/venv'), mock.patch.object(sys, 'base_prefix', '/usr'):
            self.assertTrue(shpypi.is_virtualenv())

    def test_prefix_equals_base_prefix(self):
        with mock.patch.object(sys, 'prefix', '/usr'), mock.patch.object(sys, 'base_prefix', '/usr'):
            self.assertFalse(shpypi.is_virtualenv())


if __name__ == '__main__':
    unittest.main()
