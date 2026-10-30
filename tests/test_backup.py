import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import lib.backup
import lib.vardir
from lib.configdirs import resolve_config_etc, user_conf_dir
from lib.shpypi import Shpypi


class TestBackupConfigDirs(unittest.TestCase):
    """create_backup()/restore_backup() find the user config where SmartHome reads it."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='SHNG_backup.')
        self.addCleanup(self._tmp.cleanup)
        self.base = self._tmp.name
        os.makedirs(os.path.join(self.base, 'plugins'))
        lib.vardir.set_var_dir(os.path.join(self.base, 'var'))
        self.addCleanup(lib.vardir.set_var_dir, None)
        if Shpypi.get_instance() is None:
            Shpypi(base=self.base, for_tests=True)
        pip_list = patch.object(Shpypi, 'create_pip_list', lambda self, dest: None)
        pip_list.start()
        self.addCleanup(pip_list.stop)

    def _write(self, *parts, text='x'):
        path = os.path.join(self.base, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(text)
        return path

    def _backup_names(self, **kwargs):
        filename = lib.backup.create_backup(self.base, self.base, **kwargs)
        with zipfile.ZipFile(filename) as z:
            return set(z.namelist())

    def _restore(self, zip_path, **kwargs):
        restore_dir = os.path.join(self.base, 'var', 'restore')
        os.makedirs(restore_dir, exist_ok=True)
        os.rename(zip_path, os.path.join(restore_dir, 'b.zip'))
        lib.backup.restore_backup(self.base, self.base, **kwargs)

    def test_config_below_etc_is_backed_up_by_default(self):
        self._write('etc', 'smarthome.yaml', text='default_language: de\n')
        self._write('etc', 'items', 'a.yaml')
        self._write('etc', 'logics', 'l.py')

        names = self._backup_names()

        self.assertIn('items/a.yaml', names)
        self.assertIn('logics/l.py', names)

    def test_config_etc_false_in_smarthome_yaml_backs_up_base_dirs(self):
        self._write('etc', 'smarthome.yaml', text='config_etc: false\n')
        self._write('items', 'a.yaml')
        self._write('etc', 'items', 'stale.yaml')

        names = self._backup_names()

        self.assertIn('items/a.yaml', names)
        self.assertNotIn('items/stale.yaml', names)

    def test_explicit_config_etc_overrides_smarthome_yaml(self):
        self._write('etc', 'smarthome.yaml', text='config_etc: false\n')
        self._write('etc', 'items', 'a.yaml')

        names = self._backup_names(config_etc=True)

        self.assertIn('items/a.yaml', names)

    def test_logic_groups_are_backed_up(self):
        self._write('etc', 'logic_groups.yaml', text='Mine:\n    title: my logics\n')

        names = self._backup_names()

        self.assertIn('etc/logic_groups.yaml', names)

    def test_private_plugins_are_backed_up(self):
        self._write('plugins', 'priv_x', '__init__.py')

        names = self._backup_names()

        self.assertIn('plugins/priv_x/__init__.py', names)

    def test_restore_writes_config_below_etc_by_default(self):
        self._write('etc', 'smarthome.yaml', text='default_language: de\n')
        self._write('etc', 'items', 'a.yaml', text='saved')
        zip_path = lib.backup.create_backup(self.base, self.base)
        self._write('etc', 'items', 'a.yaml', text='changed')

        self._restore(zip_path)

        with open(os.path.join(self.base, 'etc', 'items', 'a.yaml')) as f:
            self.assertEqual('saved', f.read())
        self.assertFalse(os.path.exists(os.path.join(self.base, 'items')))


class TestConfigDirs(unittest.TestCase):
    """lib.configdirs resolves the config_etc setting and the user config directory."""

    def test_cmdline_flag_wins_over_configured_value(self):
        self.assertTrue(resolve_config_etc(True, False))

    def test_configured_value_is_used_without_cmdline_flag(self):
        self.assertFalse(resolve_config_etc(False, 'false'))
        self.assertTrue(resolve_config_etc(False, None))

    def test_user_conf_dir(self):
        self.assertEqual(os.path.join('/c', 'etc'), user_conf_dir('/c', True))
        self.assertEqual('/c', user_conf_dir('/c', False))


if __name__ == '__main__':
    unittest.main()
