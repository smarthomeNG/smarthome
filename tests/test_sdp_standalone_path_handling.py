#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Standalone.__init__()'s path/module-path computation
(lib.model.smartdeviceplugin):

- self.plugin_path: the plugin's directory
- self.plugin_mod_path: the same directory, as a dotted import path
- self.plugin_name: the plugin's directory name

Exercised via the '-h' early-exit path (usage text is built - which
requires plugin_path/plugin_mod_path/plugin_name and a working Metadata()
call - then printed, then __init__ returns before touching anything
struct/device-related), since that's the cheapest way to reach this code
for real without a full commands.py/device fixture.
"""

import builtins
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

builtins.SDP_standalone = False  # noqa

from lib.model.smartdeviceplugin import Standalone


class _DummyPlugin:
    STANDALONE_HELP_OPTIONS = ''
    STANDALONE_HELP_EXTRA = ''


class _StandaloneInitTestCase(unittest.TestCase):
    """Sets up a throwaway fake shng base dir (just bin/smarthome.py, so
    the '__init__ must run from the shng base dir' check passes) with a
    plugin subdirectory under it, and chdir's there for the test."""

    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._orig_argv = sys.argv
        self._tmp = tempfile.TemporaryDirectory()
        # resolve() - macOS puts tempdirs under /var, itself a symlink to
        # /private/var; os.getcwd() always returns the resolved form, so
        # comparing an unresolved tempdir path against it would make
        # os.path.relpath() see two different absolute prefixes and
        # compute a bogus '../../...'-laden result. Not what this test is
        # about, so resolve up front to keep that confound out of it.
        self.base = Path(self._tmp.name).resolve()
        (self.base / 'bin').mkdir(parents=True)
        (self.base / 'bin' / 'smarthome.py').write_text('')
        os.chdir(self.base)

    def tearDown(self):
        os.chdir(self._orig_cwd)
        sys.argv = self._orig_argv
        self._tmp.cleanup()

    def _make_plugin_dir(self, *rel_parts):
        plugin_dir = self.base.joinpath(*rel_parts)
        plugin_dir.mkdir(parents=True)
        (plugin_dir / '__init__.py').write_text('')
        return plugin_dir

    def _run(self, plugin_file):
        sys.argv = [str(plugin_file), '-h']
        return Standalone(_DummyPlugin, str(plugin_file))


class TestNormalRelativeInvocation(_StandaloneInitTestCase):
    def test_plugin_path_is_the_plugin_directory(self):
        self._make_plugin_dir('plugins', 'viessmann')
        standalone = self._run(Path('plugins', 'viessmann', '__init__.py'))
        self.assertEqual(Path(standalone.plugin_path), Path('plugins', 'viessmann'))

    def test_plugin_mod_path_is_dotted(self):
        self._make_plugin_dir('plugins', 'viessmann')
        standalone = self._run(Path('plugins', 'viessmann', '__init__.py'))
        self.assertEqual(standalone.plugin_mod_path, 'plugins.viessmann')

    def test_plugin_name_is_the_directory_name(self):
        self._make_plugin_dir('plugins', 'viessmann')
        standalone = self._run(Path('plugins', 'viessmann', '__init__.py'))
        self.assertEqual(standalone.plugin_name, 'viessmann')


class TestAbsolutePathInvocation(_StandaloneInitTestCase):
    """plugin_file given as an absolute path while cwd is still the shng
    base dir - e.g. a user pastes the full path on the command line.

    plugin_mod_path must resolve to the same dotted form as a relative
    invocation ('plugins.viessmann'), not leak the absolute filesystem
    prefix as bogus package segments (e.g.
    '.private.var.folders.xx.tmpXXXX.plugins.viessmann') - that value
    feeds importlib.import_module() in create_struct_yaml(), so a leaked
    prefix would make struct generation invoked with an absolute path fail
    outright."""

    def test_plugin_path_matches_relative_invocation(self):
        plugin_dir = self._make_plugin_dir('plugins', 'viessmann')
        standalone = self._run(plugin_dir / '__init__.py')
        self.assertEqual(Path(standalone.plugin_path), Path('plugins', 'viessmann'))

    def test_plugin_mod_path_has_no_leading_dot(self):
        plugin_dir = self._make_plugin_dir('plugins', 'viessmann')
        standalone = self._run(plugin_dir / '__init__.py')
        self.assertEqual(standalone.plugin_mod_path, 'plugins.viessmann')


class TestNestedPluginDirectory(_StandaloneInitTestCase):
    """commands.py-style plugins can be nested more than one level deep."""

    def test_multi_level_path_is_fully_dotted(self):
        self._make_plugin_dir('plugins', 'foo', 'bar')
        standalone = self._run(Path('plugins', 'foo', 'bar', '__init__.py'))
        self.assertEqual(standalone.plugin_mod_path, 'plugins.foo.bar')
        self.assertEqual(standalone.plugin_name, 'bar')


class TestRejectsPathOutsideCwd(_StandaloneInitTestCase):
    def test_climbing_above_cwd_is_rejected_without_crashing(self):
        # plugin lives OUTSIDE the fake base dir entirely
        outside = Path(tempfile.mkdtemp()).resolve()
        try:
            plugin_dir = outside / 'plugins' / 'elsewhere'
            plugin_dir.mkdir(parents=True)
            (plugin_dir / '__init__.py').write_text('')
            standalone = self._run(os.path.relpath(plugin_dir / '__init__.py', self.base))
            self.assertFalse(hasattr(standalone, 'plugin_path'))
        finally:
            import shutil

            shutil.rmtree(outside)


class TestRejectsMissingBaseDir(unittest.TestCase):
    def test_returns_without_crashing_when_not_run_from_base_dir(self):
        orig_cwd = os.getcwd()
        tmp = tempfile.TemporaryDirectory()
        try:
            os.chdir(tmp.name)  # no bin/smarthome.py here
            standalone = Standalone(_DummyPlugin, 'plugins/whatever/__init__.py')
            self.assertFalse(hasattr(standalone, 'plugin_path'))
        finally:
            os.chdir(orig_cwd)
            tmp.cleanup()


if __name__ == '__main__':
    unittest.main(verbosity=2)
