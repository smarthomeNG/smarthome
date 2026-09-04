#!/usr/bin/env python3
"""Tests for tools/db_migrate.py - the standalone item/log migration tool
between sqlite3/MySQL-MariaDB/PostgreSQL backends.

Uses real sqlite3-backed lib.db.Database instances (in-memory) for source
and destination - fast, no external dependency, exercises the actual
schema/insert/read code paths rather than mocks.
"""

import io
import os
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import lib.db
import db_migrate
from plugins.database.store import ItemStore, LogStore
from plugins.database.constants import BufferEntry, QUALITY_VALID


def make_db(name='test'):
    db = lib.db.Database(name, 'sqlite3', {'database': ':memory:'}, 'named')
    db.connect()
    return db


def seed_source(db, prefix=''):
    """Sets up a source database with schema + a couple of items/log rows,
    via the migrator's own schema-setup path (dogfooding the real code)."""
    migrator = db_migrate.DbMigrator(db, db, 'sqlite3', source_prefix=prefix, dest_prefix=prefix, stream=io.StringIO())
    migrator.ensure_destination_schema()
    tn = db_migrate.build_table_names(prefix)
    item_store = ItemStore(db, tn)
    log_store = LogStore(db, tn)
    id1 = item_store.insert('solar.power')
    id2 = item_store.insert('outside.temp')
    log_store.insert(id1, BufferEntry(time=1000, duration=500, value=42.5, quality=QUALITY_VALID), 'num', 1500)
    log_store.insert(id1, BufferEntry(time=1500, duration=300, value=43.0, quality=QUALITY_VALID), 'num', 1800)
    log_store.insert(id2, BufferEntry(time=1000, duration=1000, value=-2.5, quality=QUALITY_VALID), 'num', 2000)
    # {item}'s cached-last-value columns come from ItemStore.update() (as the plugin's own updateItem() does), not log_store.insert() alone.
    item_store.update(id1, time=1500, val=43.0, item_type='num', changed=1800)
    item_store.update(id2, time=1000, val=-2.5, item_type='num', changed=2000)
    return {'solar.power': id1, 'outside.temp': id2}


class TestBuildTableNames(unittest.TestCase):
    def test_no_prefix(self):
        tn = db_migrate.build_table_names('')
        self.assertEqual('item', tn['item'])
        self.assertEqual('log', tn['log'])

    def test_with_prefix(self):
        tn = db_migrate.build_table_names('shng')
        self.assertEqual('shng_item', tn['item'])
        self.assertEqual('shng_log', tn['log'])


class TestConnectionIdentity(unittest.TestCase):
    def test_sqlite_resolves_absolute_path(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            id1 = db_migrate.connection_identity('sqlite3', {'database': f.name}, '')
            id2 = db_migrate.connection_identity('sqlite3', {'database': f.name}, '')
            self.assertEqual(id1, id2)

    def test_sqlite_relative_vs_absolute_same_file_match(self):
        with tempfile.NamedTemporaryFile(suffix='.db', dir='.') as f:
            rel = os.path.basename(f.name)
            id_abs = db_migrate.connection_identity('sqlite3', {'database': f.name}, '')
            id_rel = db_migrate.connection_identity('sqlite3', {'database': rel}, '')
            self.assertEqual(id_abs, id_rel)

    def test_network_driver_identity(self):
        cfg = {'host': 'narya', 'port': 5436, 'database': 'shng_test'}
        self.assertEqual(
            db_migrate.connection_identity('psycopg2', cfg, 'p'),
            db_migrate.connection_identity('psycopg2', dict(cfg), 'p'),
        )

    def test_different_prefix_is_different_identity(self):
        cfg = {'host': 'narya', 'port': 5436, 'database': 'shng_test'}
        self.assertNotEqual(
            db_migrate.connection_identity('psycopg2', cfg, 'a'), db_migrate.connection_identity('psycopg2', cfg, 'b')
        )


class TestSourceNotDestinationGuard(unittest.TestCase):
    def test_same_sqlite_file_refused(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            with self.assertRaises(db_migrate.MigrationError):
                db_migrate.assert_source_not_destination(
                    'sqlite3', {'database': f.name}, '', 'sqlite3', {'database': f.name}, ''
                )

    def test_different_sqlite_files_allowed(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f1, tempfile.NamedTemporaryFile(suffix='.db') as f2:
            db_migrate.assert_source_not_destination(
                'sqlite3', {'database': f1.name}, '', 'sqlite3', {'database': f2.name}, ''
            )  # must not raise

    def test_same_network_db_different_prefix_allowed(self):
        cfg = {'host': 'h', 'port': 1, 'database': 'd'}
        db_migrate.assert_source_not_destination('pymysql', cfg, 'a', 'pymysql', cfg, 'b')  # must not raise


class TestSourceHasNativeCagg(unittest.TestCase):
    def test_non_psycopg_driver_skips_query_entirely(self):
        db = mock.Mock()
        self.assertFalse(db_migrate.source_has_native_cagg(db, 'sqlite3', {'log': 'log'}))
        db.fetchall.assert_not_called()

    def test_psycopg2_driver_with_cagg_present(self):
        db = mock.Mock()
        db.fetchall.return_value = [(1,)]
        self.assertTrue(db_migrate.source_has_native_cagg(db, 'psycopg2', {'log': 'log'}))

    def test_psycopg_driver_with_cagg_present(self):
        db = mock.Mock()
        db.fetchall.return_value = [(1,)]
        self.assertTrue(db_migrate.source_has_native_cagg(db, 'psycopg', {'log': 'log'}))

    def test_psycopg2_driver_without_cagg(self):
        db = mock.Mock()
        db.fetchall.return_value = []
        self.assertFalse(db_migrate.source_has_native_cagg(db, 'psycopg2', {'log': 'log'}))

    def test_queries_the_prefixed_log_table_name(self):
        db = mock.Mock()
        db.fetchall.return_value = []
        db_migrate.source_has_native_cagg(db, 'psycopg2', {'log': 'shng_log'})
        _sql, params = db.fetchall.call_args[0]
        self.assertEqual('shng_log', params['table'])


class TestBuildDatabaseNaming(unittest.TestCase):
    """build_database()'s Database name must match plugins/database/
    __init__.py's own naming scheme exactly - lib.db.Database.setup()
    derives its version-bookkeeping table name from it, and a mismatch
    means the real plugin, started later against an already-migrated
    database, finds no rows in its own version table and reruns 'CREATE
    TABLE' against tables this tool already created."""

    def test_name_matches_plugin_convention_no_prefix(self):
        db = db_migrate.build_database('sqlite3', {'database': ':memory:'}, 'destination')
        self.assertEqual('Database', db._name)
        db.close()

    def test_name_matches_plugin_convention_with_prefix(self):
        db = db_migrate.build_database('sqlite3', {'database': ':memory:'}, 'destination', 'shng')
        self.assertEqual('ShngDatabase', db._name)
        db.close()

    def test_version_table_survives_a_later_plugin_style_reconnect(self):
        with tempfile.NamedTemporaryFile(suffix='.db') as f:
            source = make_db('source')
            dest = db_migrate.build_database('sqlite3', {'database': f.name}, 'destination')
            migrator = db_migrate.DbMigrator(source, dest, 'sqlite3', stream=io.StringIO())
            migrator.ensure_destination_schema()
            dest.close()

            plugin_style = lib.db.Database('Database', 'sqlite3', {'database': f.name}, 'named')
            plugin_style.connect()
            (version,) = plugin_style.fetchone('SELECT MAX(version) FROM database_version;')
            self.assertIsNotNone(version)
            self.assertGreaterEqual(float(version), 1)
            plugin_style.close()


class TestDotProgress(unittest.TestCase):
    def test_emits_roughly_one_dot_per_percent(self):
        stream = io.StringIO()
        progress = db_migrate.DotProgress(1000, stream=stream)
        for _ in range(1000):
            progress.advance(1)
        progress.finish()
        self.assertEqual(100, stream.getvalue().count('.'))

    def test_wraps_at_terminal_width(self):
        stream = io.StringIO()
        progress = db_migrate.DotProgress(1000, stream=stream)
        progress.width = 20  # force an early wrap for the test
        for _ in range(1000):
            progress.advance(1)
        progress.finish()
        lines = [line for line in stream.getvalue().split('\n') if line]
        self.assertGreater(len(lines), 1, 'expected more than one wrapped line at a narrow width')
        for line in lines:
            self.assertLessEqual(len(line), 20)

    def test_ends_with_100_percent(self):
        stream = io.StringIO()
        progress = db_migrate.DotProgress(50, stream=stream)
        for _ in range(50):
            progress.advance(1)
        progress.finish()
        self.assertIn('100%', stream.getvalue())

    def test_explicit_tick_overrides_percent_based_default(self):
        stream = io.StringIO()
        progress = db_migrate.DotProgress(1_000_000, stream=stream, tick=20_000)
        progress.advance(1_000_000)
        progress.finish()
        # 1_000_000 // 20_000 = 50 dots, not the ~100 a percent-based default would give regardless of size.
        self.assertEqual(50, stream.getvalue().count('.'))

    def test_item_smaller_than_tick_still_confirms_completion(self):
        stream = io.StringIO()
        progress = db_migrate.DotProgress(5, stream=stream, tick=20_000)
        progress.advance(5)
        progress.finish()
        output = stream.getvalue()
        self.assertNotIn('.', output)
        self.assertIn('100%', output)


class TestMigrationEndToEnd(unittest.TestCase):
    def setUp(self):
        self.source = make_db('source')
        self.dest = make_db('dest')
        self.source_ids = seed_source(self.source)
        self.stream = io.StringIO()

    def _migrator(self, **kw):
        kw.setdefault('stream', self.stream)
        return db_migrate.DbMigrator(self.source, self.dest, 'sqlite3', **kw)

    def test_items_migrated_with_remapped_ids(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()

        dest_store = ItemStore(self.dest, db_migrate.build_table_names(''))
        for source_id, dest_id in id_map.items():
            source_name = names[source_id]
            dest_row = dest_store.find(dest_id)
            self.assertEqual(source_name, dest_row[1], 'destination row must have the same item name')
        # IDs need not match (destination assigns its own), but the map must be complete.
        self.assertEqual(set(self.source_ids.values()), set(id_map.keys()))

    def test_item_cached_value_copied(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, _names = migrator.migrate_items()
        dest_store = ItemStore(self.dest, db_migrate.build_table_names(''))
        dest_row = dest_store.find(id_map[self.source_ids['outside.temp']])
        self.assertEqual(-2.5, dest_row[4])  # val_num column

    def test_log_rows_migrated_with_remapped_item_id(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        total, summary = migrator.migrate_logs(id_map, names)

        self.assertEqual(3, total)
        dest_log_store = LogStore(self.dest, db_migrate.build_table_names(''))
        dest_solar_id = id_map[self.source_ids['solar.power']]
        rows = dest_log_store.find_range(dest_solar_id)
        self.assertEqual(2, len(rows))
        self.assertEqual({1000, 1500}, {r[0] for r in rows})  # time column

    def test_row_counts_match_after_migration(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        migrator.migrate_logs(id_map, names)  # must not raise MigrationError (its own count check)

    def test_progress_output_prefixed_with_item_position(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        migrator.migrate_logs(id_map, names)

        output = self.stream.getvalue()
        self.assertIn('[1/2]', output)
        self.assertIn('[2/2]', output)

    def test_summary_and_force_lookup_use_bare_name_not_display_text(self):
        # The [i/N] prefix is display-only - summary entries and --force matching still key on the plain item name.
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        _total, summary = migrator.migrate_logs(id_map, names)

        summary_names = {name for name, _count, _status in summary}
        self.assertEqual({'solar.power', 'outside.temp'}, summary_names)

    def test_resumed_run_skips_already_migrated_items(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        migrator.migrate_logs(id_map, names)

        second_stream = io.StringIO()
        migrator2 = self._migrator(stream=second_stream)
        id_map2, names2 = migrator2.migrate_items()  # item migration itself is idempotent by name
        total2, summary2 = migrator2.migrate_logs(id_map2, names2)

        self.assertEqual(0, total2, 'a fully resumed run must not re-migrate any rows')
        statuses = {name: status for name, _count, status in summary2}
        self.assertTrue(all(s == 'skipped-resume' for s in statuses.values()))

    def test_force_redoes_a_specific_item(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        migrator.migrate_logs(id_map, names)

        forced = self._migrator(force_items=['solar.power'])
        id_map2, names2 = forced.migrate_items()
        total2, summary2 = forced.migrate_logs(id_map2, names2)

        self.assertEqual(2, total2, "forcing 'solar.power' must redo its 2 rows, not skip them")
        statuses = {name: status for name, _count, status in summary2}
        self.assertEqual('migrated', statuses['solar.power'])
        self.assertEqual('skipped-resume', statuses['outside.temp'])

    def test_dry_run_writes_nothing(self):
        migrator = self._migrator(dry_run=True)
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        total, summary = migrator.migrate_logs(id_map, names)

        self.assertEqual(3, total, 'dry-run must still report what it would migrate')
        # dry-run never really ran ensure_destination_schema(), so a missing destination table just means "no rows created".
        dest_store = ItemStore(self.dest, db_migrate.build_table_names(''))
        try:
            rows = dest_store.find_all()
        except Exception:
            rows = []
        self.assertEqual([], rows, 'dry-run must not create any destination rows')

    def test_bulk_path_produces_identical_result_to_row_by_row(self):
        bulk_dest = make_db('bulk-dest')
        migrator = db_migrate.DbMigrator(self.source, bulk_dest, 'sqlite3', use_bulk=True, stream=self.stream)
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        total, _summary = migrator.migrate_logs(id_map, names)
        self.assertEqual(3, total)

        dest_log_store = LogStore(bulk_dest, db_migrate.build_table_names(''))
        dest_solar_id = id_map[self.source_ids['solar.power']]
        rows = dest_log_store.find_range(dest_solar_id)
        self.assertEqual(2, len(rows))

    def test_independent_prefixes(self):
        prefixed_source = make_db('prefixed-source')
        seed_source(prefixed_source, prefix='src')
        dest = make_db('prefixed-dest')

        migrator = db_migrate.DbMigrator(
            prefixed_source, dest, 'sqlite3', source_prefix='src', dest_prefix='dst', stream=self.stream
        )
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()
        total, _summary = migrator.migrate_logs(id_map, names)

        self.assertEqual(3, total)
        dest_store = ItemStore(dest, db_migrate.build_table_names('dst'))
        self.assertEqual(2, len(dest_store.find_all()))

    def test_strict_error_does_not_mark_item_complete(self):
        migrator = self._migrator()
        migrator.ensure_destination_schema()
        id_map, names = migrator.migrate_items()

        real_execute = self.dest.execute
        call_count = {'n': 0}

        def failing_execute(*a, **kw):
            call_count['n'] += 1
            if call_count['n'] > 2:  # let the item-table setup/copy through, fail on log inserts
                raise RuntimeError('simulated failure')
            return real_execute(*a, **kw)

        self.dest.execute = failing_execute
        with self.assertRaises(db_migrate.MigrationError):
            migrator.migrate_logs(id_map, names)


class TestDiscoverDatabaseInstances(unittest.TestCase):
    def test_finds_database_plugin_sections_only(self):
        with tempfile.TemporaryDirectory() as etc_dir:
            with open(os.path.join(etc_dir, 'plugin.yaml'), 'w') as f:
                f.write(
                    textwrap.dedent("""\
                    database:
                        plugin_name: database
                        driver: pymysql
                        connect:
                        -   host:127.0.0.1
                    other_plugin:
                        plugin_name: not_database
                    """)
                )
            instances = db_migrate.discover_database_instances(etc_dir)
        self.assertEqual(['database'], list(instances.keys()))

    def test_missing_plugin_yaml_returns_empty(self):
        with tempfile.TemporaryDirectory() as etc_dir:
            self.assertEqual({}, db_migrate.discover_database_instances(etc_dir))


if __name__ == '__main__':
    unittest.main(verbosity=2)
