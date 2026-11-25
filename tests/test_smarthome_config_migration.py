import logging
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import lib.smarthome
from lib import shyaml


class TestCheckMigrateConfig(unittest.TestCase):
    """SmartHome.check_migrate_config() moves the user config directories below etc/."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='SHNG_migrate.')
        self.addCleanup(self._tmp.cleanup)
        self.base = self._tmp.name
        self.etc = os.path.join(self.base, 'etc')
        os.makedirs(self.etc)
        self.smarthome_yaml = os.path.join(self.etc, 'smarthome.yaml')
        with open(self.smarthome_yaml, 'w') as f:
            f.write('default_language: de\n')
        self.sh = SimpleNamespace(
            _config_etc=True,
            _etc_dir=self.etc,
            _logger=logging.getLogger('test.migrate'),
            get_config_file=lambda name: self.smarthome_yaml,
        )

    def _write(self, *parts, text='x'):
        path = os.path.join(self.base, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(text)
        return path

    def _migrate(self):
        with patch('lib.smarthome.BASE', self.base):
            lib.smarthome.SmartHome.check_migrate_config(self.sh)

    def test_moves_files_of_all_config_directories(self):
        for directory in ('items', 'logics', 'structs', 'scenes', 'functions'):
            self._write(directory, 'a.yaml')

        self._migrate()

        for directory in ('items', 'logics', 'structs', 'scenes', 'functions'):
            self.assertTrue(os.path.isfile(os.path.join(self.etc, directory, 'a.yaml')), directory)
            self.assertFalse(os.path.exists(os.path.join(self.base, directory)), directory)

    def test_records_config_etc_in_smarthome_yaml(self):
        self._write('items', 'a.yaml')

        self._migrate()

        self.assertIs(True, shyaml.yaml_load_roundtrip(self.smarthome_yaml)['config_etc'])

    def test_conflicting_file_aborts_and_keeps_both_files(self):
        old = self._write('items', 'a.yaml', text='old')
        new = self._write('etc', 'items', 'a.yaml', text='new')

        with self.assertRaises(SystemExit) as raised:
            self._migrate()

        self.assertEqual(255, raised.exception.code)
        self.assertEqual('old', open(old).read())
        self.assertEqual('new', open(new).read())

    def test_nothing_happens_when_config_etc_is_off(self):
        old = self._write('items', 'a.yaml')
        self.sh._config_etc = False

        self._migrate()

        self.assertTrue(os.path.isfile(old))
        self.assertFalse(os.path.exists(os.path.join(self.etc, 'items')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
