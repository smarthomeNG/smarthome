#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib.userfunctions: importing, reloading and listing user modules.

User module names need not be Python identifiers (e.g. ``hyphen-mod``), and a
user module whose name collides with a global of lib.userfunctions is refused.
"""

import copy
import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.userfunctions as uf


class TestUserfunctionsReload(unittest.TestCase):
    def setUp(self):
        # state and exported user modules both live in uf's globals: snapshot all of it
        self._saved_globals = {k: copy.copy(v) if isinstance(v, (list, dict)) else v for k, v in vars(uf).items()}

        self._tmpdir = tempfile.TemporaryDirectory()
        base_dir = self._tmpdir.name
        self._functions_dir = os.path.join(base_dir, 'functions')
        os.makedirs(self._functions_dir)
        self._write_uf('hyphen-mod', "_VERSION = '1.0'\n_DESCRIPTION = 'test'\nVALUE = 1\n")

        sys.path.insert(0, base_dir)
        self._sys_path_entry = base_dir

        uf.init_lib(shng_base_dir=base_dir)

    def tearDown(self):
        namespace = vars(uf)
        namespace.clear()
        namespace.update(self._saved_globals)
        sys.path.remove(self._sys_path_entry)
        for modname in [m for m in sys.modules if m == 'functions' or m.startswith('functions.')]:
            sys.modules.pop(modname)
        self._tmpdir.cleanup()

    def _write_uf(self, name, source):
        """Write ``functions/<name>.py`` with *source*, mtime pushed forward so importlib sees the change."""
        path = os.path.join(self._functions_dir, name + '.py')
        exists = os.path.exists(path)
        with open(path, 'w') as f:
            f.write(source)
        if exists:
            future = os.path.getmtime(path) + 5
            os.utime(path, (future, future))
        return path

    def test_get_userlibs_lists_loaded_modules(self):
        self.assertEqual([{'name': 'hyphen-mod', 'version': '1.0', 'description': 'test'}], uf.get_userlibs())

    def test_reload_hyphenated_module_name_succeeds(self):
        self.assertIn('hyphen-mod', uf._user_modules)
        self.assertTrue(uf.reload('hyphen-mod'))

    def test_reload_hyphenated_module_actually_reimports(self):
        # importlib's source cache validates by mtime+size; _write_uf pushes the mtime forward.
        self._write_uf('hyphen-mod', "_VERSION = '1.0'\n_DESCRIPTION = 'test'\nVALUE = 2\n")

        self.assertTrue(uf.reload('hyphen-mod'))
        mod = importlib.import_module('functions.hyphen-mod')
        self.assertEqual(mod.VALUE, 2)

    def test_reload_imports_module_whose_initial_import_failed(self):
        self._write_uf('late', 'VALUE = (\n')
        with self.assertLogs('lib.userfunctions', level='ERROR'):
            uf.init_lib(shng_base_dir=self._tmpdir.name)
        self._write_uf('late', 'VALUE = 1\n')
        self.assertTrue(uf.reload('late'))
        self.assertEqual(uf.late.VALUE, 1)

    def test_reload_imports_module_added_at_runtime(self):
        self._write_uf('added', 'VALUE = 3\n')
        self.assertTrue(uf.reload('added'))
        self.assertEqual(uf.added.VALUE, 3)
        self.assertIn('added', [lib['name'] for lib in uf.get_userlibs()])

    def _write_colliding_uf(self, name):
        """Write a user module named *name* that leaves a marker file when executed; return the marker path."""
        marker = os.path.join(self._tmpdir.name, name + '.executed')
        self._write_uf(name, f"open({marker!r}, 'w').close()\n")
        return marker

    def test_module_shadowing_library_global_is_refused(self):
        marker = self._write_colliding_uf('os')
        with self.assertLogs('lib.userfunctions', level='ERROR'):
            self.assertFalse(uf.import_user_module('os'))
        self.assertIs(uf.os, os)
        self.assertFalse(os.path.exists(marker))

    def test_refused_module_is_neither_listed_nor_reloadable(self):
        self._write_colliding_uf('os')
        with self.assertLogs('lib.userfunctions', level='ERROR'):
            uf.init_lib(shng_base_dir=self._tmpdir.name)
        self.assertEqual(['hyphen-mod'], [lib['name'] for lib in uf.get_userlibs()])
        with self.assertLogs('lib.userfunctions', level='ERROR'):
            self.assertFalse(uf.reload('os'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
