#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the logic group definitions in etc/logic_groups.yaml (Logics._load_groups())

Coverage
--------
- a new installation gets etc/logic_groups.yaml from templates/logic_groups.yaml
- the groups of an etc/admin.yaml are migrated and admin.yaml is renamed to admin.yaml.bak
- an existing etc/logic_groups.yaml is loaded unchanged
- SmartHome.checkConfigFiles() does not create an etc/admin.yaml any more
"""

import os
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.shyaml as shyaml
from lib.constants import DIR_TPL
from lib.logic import Logics
from lib.smarthome import SmartHome

BASE_DIR = os.path.join(os.path.dirname(__file__), '..')


class _ShStub:
    def __init__(self, etc_dir, templates_dir):
        self._etc_dir = etc_dir
        self._templates_dir = templates_dir

    def get_config_file(self, config, extension='.yaml'):
        return os.path.join(self._etc_dir, config + extension)

    def get_config_dir(self, config):
        return self._templates_dir if config == DIR_TPL else self._etc_dir


class TestLoadGroups(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.etc_dir = os.path.join(self._tmp.name, 'etc')
        self.templates_dir = os.path.join(self._tmp.name, 'templates')
        os.makedirs(self.etc_dir)
        os.makedirs(self.templates_dir)
        shutil.copy2(os.path.join(BASE_DIR, 'templates', 'logic_groups.yaml'), self.templates_dir)
        self.logics = SimpleNamespace(_sh=_ShStub(self.etc_dir, self.templates_dir))

    def etc(self, name):
        return os.path.join(self.etc_dir, name)

    def test_new_installation_gets_groups_of_template(self):
        groups = Logics._load_groups(self.logics)

        self.assertIn('Beispiele', groups)
        self.assertTrue(os.path.isfile(self.etc('logic_groups.yaml')))
        self.assertFalse(os.path.exists(self.etc('admin.yaml.bak')))

    def test_groups_of_admin_yaml_are_migrated(self):
        shyaml.yaml_save(self.etc('admin.yaml'), {'logics': {'groups': {'Mine': {'title': 'my logics'}}}})

        groups = Logics._load_groups(self.logics)

        self.assertEqual(['Mine'], list(groups))
        self.assertFalse(os.path.exists(self.etc('admin.yaml')))
        self.assertTrue(os.path.isfile(self.etc('admin.yaml.bak')))

    def test_existing_logic_groups_yaml_is_loaded(self):
        shyaml.yaml_save(self.etc('logic_groups.yaml'), {'Own': {'title': 'own group'}})

        groups = Logics._load_groups(self.logics)

        self.assertEqual(['Own'], list(groups))


class TestCheckConfigFiles(unittest.TestCase):
    def test_no_admin_yaml_is_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = SimpleNamespace(_templates_dir=os.path.join(BASE_DIR, 'templates'), _etc_dir=tmp)

            SmartHome.checkConfigFiles(stub)

            self.assertTrue(os.path.isfile(os.path.join(tmp, 'smarthome.yaml')))
            self.assertFalse(os.path.exists(os.path.join(tmp, 'admin.yaml')))


if __name__ == '__main__':
    unittest.main()
