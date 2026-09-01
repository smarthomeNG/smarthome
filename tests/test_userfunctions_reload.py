#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib.userfunctions.reload().

reload() must resolve the module the same way import_user_module() does -
via a dict-style globals()['{m}'] lookup, not
exec(f'importlib.reload({userlib})') with the module name spliced in as a
bare identifier. Any userfunctions filename that isn't a valid Python
identifier (e.g. contains a hyphen, a common and legal filename character)
breaks the bare-identifier form (a hyphenated name like 'my-functions'
parses as the subtraction `my - functions`), so the "module not loaded,
try importing it" fallback must still trigger correctly.
"""

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
        # lib.userfunctions is a module-global-state library (not a class) --
        # save everything reload()/init_lib() touch so tests don't leak into
        # each other or into any other test file that happens to import it.
        self._saved = {
            '_uf_subdir': uf._uf_subdir,
            '_func_dir': uf._func_dir,
            '_sh': uf._sh,
            '_user_modules': list(uf._user_modules),
        }

        self._tmpdir = tempfile.TemporaryDirectory()
        base_dir = self._tmpdir.name
        functions_dir = os.path.join(base_dir, 'functions')
        os.makedirs(functions_dir)
        with open(os.path.join(functions_dir, 'hyphen-mod.py'), 'w') as f:
            f.write("_VERSION = '1.0'\n_DESCRIPTION = 'test'\nVALUE = 1\n")

        sys.path.insert(0, base_dir)
        self._sys_path_entry = base_dir

        uf.init_lib(shng_base_dir=base_dir)

    def tearDown(self):
        for key, value in self._saved.items():
            setattr(uf, key, value)
        sys.path.remove(self._sys_path_entry)
        for modname in ('functions.hyphen-mod', 'functions'):
            sys.modules.pop(modname, None)
        self._tmpdir.cleanup()

    def test_reload_hyphenated_module_name_succeeds(self):
        self.assertIn('hyphen-mod', uf._user_modules)
        self.assertTrue(uf.reload('hyphen-mod'))

    def test_reload_hyphenated_module_actually_reimports(self):
        # bump VALUE on disk, reload, confirm the module object was really
        # re-executed (not just reporting success without doing anything).
        # Force the mtime forward: importlib's source cache validates by
        # mtime+size, and a same-tick rewrite (write, immediately reload,
        # both within one filesystem mtime-granularity window) can leave it
        # not noticing the file changed at all - a general reload() timing
        # quirk, unrelated to hyphenated names, not something under test
        # here.
        functions_dir = os.path.join(self._tmpdir.name, 'functions')
        path = os.path.join(functions_dir, 'hyphen-mod.py')
        with open(path, 'w') as f:
            f.write("_VERSION = '1.0'\n_DESCRIPTION = 'test'\nVALUE = 2\n")
        future = os.path.getmtime(path) + 5
        os.utime(path, (future, future))

        self.assertTrue(uf.reload('hyphen-mod'))
        mod = importlib.import_module('functions.hyphen-mod')
        self.assertEqual(mod.VALUE, 2)

    def test_reload_falls_back_to_import_when_not_actually_loaded(self):
        # simulate "known to _user_modules but never actually imported"
        # (e.g. a prior import failure) -- must fall back to import, not
        # silently do nothing / crash. uf.__dict__ is the same dict
        # globals() returns from code running inside lib.userfunctions.
        del uf.__dict__['hyphen-mod']
        self.assertTrue(uf.reload('hyphen-mod'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
