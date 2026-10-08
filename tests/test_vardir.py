#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/vardir.py - the process-wide resolver for SmartHomeNG's var directory.

Coverage
--------
get_var_dir()/set_var_dir(): default is <base>/var; an override is normalised to an
absolute path; None restores the default.

rebase_var_prefix(): re-roots a relative path whose first segment is 'var' under the
configured var dir and leaves every other path untouched; no-op for the default var dir.

resolve_var_path(): always returns an absolute path - relative 'var/...' paths follow
the var dir, other relative paths resolve against the base dir, absolute paths are kept.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib import vardir


class _VarDirTestCase(unittest.TestCase):
    def setUp(self):
        vardir.set_var_dir(None)
        self.addCleanup(vardir.set_var_dir, None)


class TestGetSetVarDir(_VarDirTestCase):
    def test_default_is_var_below_base(self):
        self.assertEqual(vardir.get_var_dir(), os.path.join(vardir.BASE_DIR, 'var'))

    def test_override_is_used(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.get_var_dir(), '/srv/other/var')

    def test_override_is_made_absolute_and_normalised(self):
        vardir.set_var_dir('some/rel/../var/')
        self.assertEqual(vardir.get_var_dir(), os.path.abspath('some/var'))

    def test_override_expands_user(self):
        vardir.set_var_dir('~/shng-var')
        self.assertEqual(vardir.get_var_dir(), os.path.expanduser('~/shng-var'))

    def test_none_and_empty_restore_default(self):
        vardir.set_var_dir('/srv/other/var')
        vardir.set_var_dir(None)
        self.assertEqual(vardir.get_var_dir(), os.path.join(vardir.BASE_DIR, 'var'))
        vardir.set_var_dir('/srv/other/var')
        vardir.set_var_dir('')
        self.assertEqual(vardir.get_var_dir(), os.path.join(vardir.BASE_DIR, 'var'))


class TestRebaseVarPrefix(_VarDirTestCase):
    def test_unchanged_with_default_var_dir(self):
        self.assertEqual(vardir.rebase_var_prefix('./var/log/x.log'), './var/log/x.log')

    def test_var_prefix_is_rerooted(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.rebase_var_prefix('./var/log/x.log'), '/srv/other/var/log/x.log')
        self.assertEqual(vardir.rebase_var_prefix('var/log/x.log'), '/srv/other/var/log/x.log')

    def test_bare_var_is_rerooted(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.rebase_var_prefix('var'), '/srv/other/var')

    def test_other_paths_untouched(self):
        vardir.set_var_dir('/srv/other/var')
        for path in ('/var/log/x.log', 'plugins/foo/var/x', 'variable/x', './logs/x.log', '../var/x'):
            with self.subTest(path=path):
                self.assertEqual(vardir.rebase_var_prefix(path), path)


class TestResolveVarPath(_VarDirTestCase):
    def test_var_relative_default(self):
        self.assertEqual(vardir.resolve_var_path('var/knx'), os.path.join(vardir.BASE_DIR, 'var', 'knx'))

    def test_var_relative_follows_override(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.resolve_var_path('var/knx'), '/srv/other/var/knx')
        self.assertEqual(vardir.resolve_var_path('./var/knx/'), '/srv/other/var/knx')

    def test_other_relative_resolves_against_base(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.resolve_var_path('plugins/foo/data'), os.path.join(vardir.BASE_DIR, 'plugins/foo/data'))

    def test_absolute_kept(self):
        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(vardir.resolve_var_path('/data/knx'), '/data/knx')


class TestSmartHomeResolveVarPath(_VarDirTestCase):
    def test_follows_var_dir(self):
        from lib.smarthome import SmartHome

        vardir.set_var_dir('/srv/other/var')
        self.assertEqual(SmartHome.resolve_var_path(None, 'var/knx'), '/srv/other/var/knx')


if __name__ == '__main__':
    unittest.main(verbosity=2)
