#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the ``--var_dir`` command line option of bin/smarthome.py.

Coverage
--------
- ``-u`` and ``--var_dir`` are accepted and default to None
- without the option, the var dir and the pidfile are the defaults below <base>/var
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import bin.smarthome as smarthome_cli
from lib import vardir


class TestVarDirOption(unittest.TestCase):
    def test_default_is_none(self):
        self.assertIsNone(smarthome_cli.argparser.parse_args([]).var_dir)

    def test_long_option(self):
        self.assertEqual(smarthome_cli.argparser.parse_args(['--var_dir', '/srv/ctx/var']).var_dir, '/srv/ctx/var')

    def test_short_option(self):
        self.assertEqual(smarthome_cli.argparser.parse_args(['-u', '/srv/ctx/var']).var_dir, '/srv/ctx/var')

    def test_combines_with_config_dir(self):
        args = smarthome_cli.argparser.parse_args(['-c', '/srv/ctx/etc', '-u', '/srv/ctx/var'])
        self.assertEqual((args.config_dir, args.var_dir), ('/srv/ctx/etc', '/srv/ctx/var'))

    def test_pidfile_defaults_to_run_dir_of_default_var_dir(self):
        self.assertEqual(smarthome_cli.PIDFILE, os.path.join(vardir.BASE_DIR, 'var', 'run', 'smarthome.pid'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
