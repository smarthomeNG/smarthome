#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_database.py's DatabaseController - the backend
for shngadmin dashboard's optional database-properties widget (shown only
when a `database` plugin instance is actually configured).
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.model.smartplugin import SmartPlugin
from modules.admin.api_database import DatabaseController


class _FakeDb:
    def __init__(self, connected=True, params=None, version_row=('10.11.18-MariaDB',), raise_on_fetch=False):
        self._connected_state = connected
        self._params = params or {}
        self._version_row = version_row
        self._raise_on_fetch = raise_on_fetch

    def connected(self):
        return self._connected_state

    def fetchone(self, stmt):
        if self._raise_on_fetch:
            raise OSError('connection reset')
        return self._version_row


class _FakeDatabasePlugin(SmartPlugin):
    def __init__(self, driver, db, shortname='database'):
        self._shortname = shortname
        self.driver = driver
        self._db = db

    def get_shortname(self):
        return self._shortname

    def db(self):
        return self._db


class FakePlugins:
    def __init__(self, plugins):
        self._plugins = plugins

    def return_plugins(self):
        return self._plugins


class FakeSh:
    pass


class FakeModule:
    def __init__(self, sh):
        self._sh = sh


def _make_controller(plugins):
    with patch('modules.admin.api_database.Plugins.get_instance', return_value=None):
        controller = DatabaseController(FakeModule(FakeSh()))
    controller.plugins = FakePlugins(plugins)
    return controller


class TestNoDatabasePluginConfigured(unittest.TestCase):
    def test_reports_not_configured(self):
        controller = _make_controller([])
        result = json.loads(controller.read(id='info'))
        self.assertEqual(result, {'configured': False})

    def test_ignores_non_database_plugins(self):
        other = _FakeDatabasePlugin('sqlite3', _FakeDb(), shortname='knx')
        controller = _make_controller([other])
        result = json.loads(controller.read(id='info'))
        self.assertEqual(result, {'configured': False})


class TestSqliteConfiguration(unittest.TestCase):
    def test_reports_driver_and_database_name_without_host(self):
        db = _FakeDb(connected=True, params={'database': '/opt/shng/var/db/smarthome.db'})
        plugin = _FakeDatabasePlugin('sqlite3', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['configured'], True)
        self.assertEqual(result['driver'], 'sqlite3')
        self.assertEqual(result['database'], 'smarthome')
        self.assertNotIn('host', result)
        self.assertEqual(result['connected'], True)

    def test_version_uses_sqlite_version_function(self):
        db = _FakeDb(connected=True, params={'database': 'x.db'}, version_row=('3.45.1',))
        plugin = _FakeDatabasePlugin('sqlite3', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['version'], '3.45.1')


class TestMysqlFamilyConfiguration(unittest.TestCase):
    def test_reports_database_name_and_host(self):
        db = _FakeDb(connected=True, params={'host': '127.0.0.1', 'db': 'smarthome', 'user': 'db_user'})
        plugin = _FakeDatabasePlugin('pymysql', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['driver'], 'pymysql')
        self.assertEqual(result['database'], 'smarthome')
        self.assertEqual(result['host'], '127.0.0.1')
        # credentials must never leak into the response
        self.assertNotIn('user', result)
        self.assertNotIn('passwd', result)

    def test_version_uses_select_version(self):
        db = _FakeDb(connected=True, params={'host': '127.0.0.1', 'db': 'smarthome'}, version_row=('10.11.18-MariaDB',))
        plugin = _FakeDatabasePlugin('pymysql', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['version'], '10.11.18-MariaDB')


class TestConnectionState(unittest.TestCase):
    def test_disconnected_skips_version_lookup(self):
        db = _FakeDb(connected=False, params={'database': 'x.db'})
        plugin = _FakeDatabasePlugin('sqlite3', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['connected'], False)
        self.assertNotIn('version', result)

    def test_version_lookup_failure_does_not_break_response(self):
        db = _FakeDb(connected=True, params={'database': 'x.db'}, raise_on_fetch=True)
        plugin = _FakeDatabasePlugin('sqlite3', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=60):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['connected'], True)
        self.assertIsNone(result.get('version'))


class TestQueryTimeout(unittest.TestCase):
    def test_reports_configured_query_timeout(self):
        db = _FakeDb(connected=True, params={'database': 'x.db'})
        plugin = _FakeDatabasePlugin('sqlite3', db)
        controller = _make_controller([plugin])

        with patch('lib.db._sh_db_query_timeout', return_value=45):
            result = json.loads(controller.read(id='info'))

        self.assertEqual(result['query_timeout'], 45)


class TestReadDispatch(unittest.TestCase):
    def test_unrecognized_id_returns_none(self):
        controller = _make_controller([])
        self.assertIsNone(controller.read(id='bogus'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
