#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#########################################################################

"""
Standalone database migration tool for the `database` plugin's schema -
converts an item/log dataset between any two of the three supported
backends (sqlite3, MySQL/MariaDB via pymysql, PostgreSQL/TimescaleDB via
psycopg2), in either direction.

Must be run with SmartHomeNG stopped. Source and destination connection
details are either read from a locally-checked-out etc/plugin.yaml,
or entered/selected manually.
"""

import argparse
import getpass
import json
import os
import shutil
import sys
import time as time_module
import types
from typing import TextIO

sh_basedir: str = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

import lib.daemon
import lib.db
import lib.shyaml
from plugins.database import Database as DatabasePlugin
from plugins.database.constants import COL_ITEM, COL_ITEM_ID, COL_ITEM_NAME, COL_LOG
from plugins.database.store import ItemStore, LogStore
from plugins.database.utils import apply_table_names

# A driver connect spec - plugin.yaml's 'key:value' list form, or a dict from CLI/interactive input.
ConnectParams = dict[str, str | int] | list[str]

PIDFILE: str = os.path.join(sh_basedir, 'var', 'run', 'smarthome.pid')

# Matches max_delete_logentries' "safe batch size" precedent - see plugins/database/plugin.yaml.
DEFAULT_BATCH_SIZE: int = 20000


class MigrationError(Exception):
    """A fatal, unrecoverable migration error - stops the whole run."""

    pass


class ShngRunningError(MigrationError):
    """SmartHomeNG is currently running - refuses to proceed."""

    pass


def assert_shng_not_running() -> None:
    """Raise ShngRunningError if a live SmartHomeNG instance is detected.

    Reuses lib.daemon.check_sh_is_running() directly - the exact function
    bin/smarthome.py's own double-launch guard uses (PID-file +
    psutil.pid_exists() + an actual portalocker exclusive-lock probe on
    the file, not just file existence). A live instance writing to either
    side of the migration while this tool runs would corrupt or silently
    miss data.
    """
    if lib.daemon.check_sh_is_running(PIDFILE):
        pid = lib.daemon.read_pidfile(PIDFILE)
        raise ShngRunningError(
            f'SmartHomeNG is currently running (pid {pid}). Stop it first '
            "('smarthome.py -s') - this tool must never run against a live instance."
        )


# ── connection discovery / selection ────────────────────────────────────────


def discover_database_instances(etc_dir: str) -> dict[str, dict]:
    """Return {instance_label: config_dict} for every plugin.yaml entry with
    plugin_name: database.

    Plain YAML parsing, not lib.plugin.Plugins - that framework machinery is
    tied to a running SmartHomeNG instance (item registration, metadata,
    ...), none of which this tool needs just to read connection config.
    Each entry's label is its plugin.yaml section key (e.g. 'database',
    'database_test') - already unique by construction, since it's a YAML
    mapping key.

    :param etc_dir: Path to the etc/ directory containing plugin.yaml.
    :returns: dict of section_name -> raw plugin.yaml config dict.
    """
    plugin_yaml: str = os.path.join(etc_dir, 'plugin.yaml')
    if not os.path.isfile(plugin_yaml):
        return {}
    conf: dict = lib.shyaml.yaml_load(plugin_yaml, ordered=True) or {}
    return {
        name: section
        for name, section in conf.items()
        if isinstance(section, dict) and section.get('plugin_name') == 'database'
    }


def format_instance_summary(config: dict) -> str:
    driver: str = config.get('driver', '?')
    connect: ConnectParams | str = config.get('connect', '?')
    prefix: str = config.get('prefix', '')
    return f'driver={driver} connect={connect} prefix={prefix!r}'


def prompt_choice(prompt: str, options: list[tuple[str, str | None]]) -> str | None:
    """Print a numbered list of options, prompt until a valid index is chosen.

    :param options: list of (label, value) tuples. Index 0 in the printed
                    list is always '0. manual' by convention of the caller.
    :returns: the value of the chosen option.
    """
    print(prompt)
    for i, (label, _value) in enumerate(options):
        print(f'  {i}. {label}')
    while True:
        raw: str = input('> ').strip()
        try:
            idx = int(raw)
            if 0 <= idx < len(options):
                return options[idx][1]
        except ValueError:
            pass
        print(f'Enter a number from 0 to {len(options) - 1}.')


def prompt_manual_config(role: str) -> tuple[str, dict[str, str | int], str]:
    """Interactively prompt for driver/connect/prefix, password via getpass.

    :param role: 'source' or 'destination' - only used in prompt text.
    :returns: (driver, connect_dict, prefix) tuple.
    """
    print(f'\nManual {role} configuration:')
    driver: str = input('  driver (sqlite3 / pymysql / psycopg2): ').strip()
    connect: dict[str, str | int] = {}
    if driver == 'sqlite3':
        connect['database'] = input('  database file path: ').strip()
    else:
        connect['host'] = input('  host: ').strip()
        port: str = input('  port (blank for default): ').strip()
        if port:
            connect['port'] = int(port)
        connect['user'] = input('  user: ').strip()
        connect['passwd' if driver == 'pymysql' else 'password'] = getpass.getpass('  password: ')
        connect['db' if driver == 'pymysql' else 'database'] = input('  database name: ').strip()
    prefix: str = input('  table prefix (blank for none): ').strip()
    return driver, connect, prefix


def resolve_role(
    role: str, args_prefix_attr: str, instances: dict[str, dict], args: argparse.Namespace
) -> tuple[str, ConnectParams, str]:
    """Resolve one side (source/destination) to (driver, connect, prefix),
    either from a named plugin.yaml instance, explicit CLI flags, or an
    interactive prompt - whichever the caller actually supplied.

    :param role: 'source' or 'destination'.
    :param args: parsed argparse.Namespace.
    """
    instance_flag: str | None = getattr(args, f'{role}_instance', None)
    driver_flag: str | None = getattr(args, f'{role}_driver', None)
    prefix_flag: str = getattr(args, args_prefix_attr, None) or ''

    if instance_flag:
        if instance_flag not in instances:
            raise MigrationError(f"No such {role} instance '{instance_flag}' in plugin.yaml. Found: {list(instances)}")
        cfg = instances[instance_flag]
        cfg_driver: str | None = cfg.get('driver')
        cfg_connect: ConnectParams | None = cfg.get('connect')
        if cfg_driver is None or cfg_connect is None:
            raise MigrationError(f"Instance '{instance_flag}' in plugin.yaml is missing 'driver' or 'connect'.")
        return cfg_driver, cfg_connect, cfg.get('prefix', '') or prefix_flag

    if driver_flag:
        connect_flag: ConnectParams | None = getattr(args, f'{role}_connect', None)
        if not connect_flag:
            raise MigrationError(f'--{role}-driver given without --{role}-connect')
        return driver_flag, connect_flag, prefix_flag

    if not args.interactive:
        raise MigrationError(
            f'No {role} configured - pass --{role}-instance, --{role}-driver/--{role}-connect, or run with --interactive.'
        )

    options: list[tuple[str, str | None]] = [
        (f'{name} ({format_instance_summary(cfg)})', name) for name, cfg in instances.items()
    ]
    options.append(('manual entry', None))
    chosen: str | None = prompt_choice(f'\nSelect {role} database:', options)
    driver: str | None
    connect: ConnectParams | None
    prefix: str
    if chosen is None:
        driver, connect, prefix = prompt_manual_config(role)
    else:
        cfg = instances[chosen]
        driver, connect, prefix = cfg.get('driver'), cfg.get('connect'), cfg.get('prefix', '')
    if driver is None or connect is None:
        raise MigrationError(f"Instance '{chosen}' in plugin.yaml is missing 'driver' or 'connect'.")
    return driver, connect, prefix or prefix_flag


def connect_params_with_password_prompt(
    role: str, driver: str, connect: ConnectParams, password_flag: str | None
) -> ConnectParams:
    """Fill in a missing password via getpass rather than ever requiring it
    as a bare CLI argument (shell history / `ps aux` visibility)."""
    if password_flag:
        key: str = 'passwd' if driver == 'pymysql' else 'password'
        connect = dict(connect) if isinstance(connect, dict) else connect
        if isinstance(connect, dict) and key not in connect:
            connect[key] = password_flag
    elif isinstance(connect, dict) and driver != 'sqlite3':
        key = 'passwd' if driver == 'pymysql' else 'password'
        if key not in connect or not connect[key]:
            connect[key] = getpass.getpass(f'{role} database password: ')
    return connect


# ── connection identity (for the source != destination guard) ──────────────


def connection_identity(driver: str, connect: ConnectParams, prefix: str) -> tuple:
    """A hashable tuple identifying "the same underlying table set" -
    resolved absolute file path for sqlite3, else (driver, host, port,
    database, prefix). Used only for the safety guard below; not a real
    connection.
    """
    if driver == 'sqlite3':
        db_path: str | int | None = connect.get('database') if isinstance(connect, dict) else None
        return ('sqlite3', os.path.realpath(str(db_path)) if db_path else None, prefix)
    if isinstance(connect, dict):
        host: str | int | None = connect.get('host')
        port: str | int | None = connect.get('port')
        dbname: str | int | None = connect.get('db') or connect.get('database')
    else:
        host = port = dbname = None
    return (driver, host, port, dbname, prefix)


def source_has_native_cagg(source: lib.db.Database, source_driver: str, source_tn: dict[str, str]) -> bool:
    """True if source is TimescaleDB and at least one continuous aggregate
    exists on its {log} hypertable (plugins/database's
    timescale_aggregation_mode: native - see ~/.claude/handoff/
    handoff-shng-timescaledb.md). This tool only ever reads raw {log}; a
    cagg-covered source may already have raw chunks dropped by native
    retention, for buckets only the cagg still covers - a raw-only
    migration would silently be incomplete there.
    """
    if source_driver not in lib.db.Database._psycopg_driver_names:
        return False
    result = source.fetchall(
        'SELECT 1 FROM timescaledb_information.continuous_aggregates WHERE hypertable_name = :table LIMIT 1;',
        {'table': source_tn['log']},
    )
    return bool(result)


def assert_source_not_destination(
    source_driver: str,
    source_connect: ConnectParams,
    source_prefix: str,
    dest_driver: str,
    dest_connect: ConnectParams,
    dest_prefix: str,
) -> None:
    """Hard refusal, no override - a typo'd flag pointing both sides at the
    same table set would otherwise silently self-migrate/corrupt data."""
    src_id = connection_identity(source_driver, source_connect, source_prefix)
    dst_id = connection_identity(dest_driver, dest_connect, dest_prefix)
    if src_id == dst_id:
        raise MigrationError(f'Source and destination resolve to the same database/table set ({src_id}) - refusing.')


# ── progress display ────────────────────────────────────────────────────────


class DotProgress:
    """pytest-style dot progress, reset per item: one dot per *tick* rows
    processed, wrapped at terminal width (or 80 cols when stdout isn't a
    TTY - e.g. piped to a log file over SSH), each wrapped line ending in
    the running percentage. *tick* is a fixed row count (e.g. the
    migration's batch_size) rather than a percentage of *total*, so an
    item's dot count reflects real work done - large and small items are
    visually distinguishable - instead of every item normalizing to the
    same ~100 dots regardless of size."""

    def __init__(self, total: int, stream: TextIO = sys.stdout, tick: int | None = None) -> None:
        self.total: int = max(total, 1)
        self.stream: TextIO = stream
        self.done: int = 0
        self.dots_on_line: int = 0
        self.width: int = shutil.get_terminal_size(fallback=(80, 24)).columns if stream.isatty() else 80
        self.tick: int = max(tick, 1) if tick else max(self.total // 100, 1)
        self._last_dot_at: int = 0

    def advance(self, n: int) -> None:
        self.done += n
        while self.done - self._last_dot_at >= self.tick:
            self._last_dot_at += self.tick
            self._emit_dot()

    def _emit_dot(self) -> None:
        self.stream.write('.')
        self.dots_on_line += 1
        # reserve room for ' [100%]'
        if self.dots_on_line >= self.width - 8:
            pct: int = min(100, int(100 * self.done / self.total))
            self.stream.write(f' [{pct:>3}%]\n')
            self.dots_on_line = 0
        self.stream.flush()

    def finish(self) -> None:
        pct: int = min(100, int(100 * self.done / self.total))
        if self.dots_on_line > 0:
            self.stream.write(' ' * (self.width - 8 - self.dots_on_line) + f' [{pct:>3}%]\n')
        elif self._last_dot_at == 0:
            # Item smaller than tick - confirm completion since no dot ever printed.
            self.stream.write(f'[{pct:>3}%]\n')
        self.stream.flush()


# ── migration ────────────────────────────────────────────────────────────────

# Well under PostgreSQL's 65535-bound-param limit (8 params/row -> ~8191 rows max).
BULK_SUBCHUNK_ROWS = 1000


def build_table_names(prefix: str) -> dict[str, str]:
    """Mirrors plugins/database/__init__.py's own self._replace construction
    exactly (trailing underscore only when a prefix is given)."""
    p: str = (prefix + '_') if prefix else ''
    return {
        'item': p + 'item',
        'log': p + 'log',
        'item_columns': ', '.join(COL_ITEM),
        'log_columns': ', '.join(COL_LOG + ('val_quality',)),
    }


class DbMigrator:
    def __init__(
        self,
        source: lib.db.Database,
        dest: lib.db.Database,
        dest_driver: str,
        source_prefix: str = '',
        dest_prefix: str = '',
        batch_size: int = DEFAULT_BATCH_SIZE,
        use_bulk: bool = False,
        dry_run: bool = False,
        force_items: list[str] | set[str] | None = None,
        stream: TextIO = sys.stdout,
    ) -> None:
        self.source: lib.db.Database = source
        self.dest: lib.db.Database = dest
        self.dest_driver: str = dest_driver
        self.source_tn: dict[str, str] = build_table_names(source_prefix)
        self.dest_tn: dict[str, str] = build_table_names(dest_prefix)
        self.batch_size: int = batch_size
        self.use_bulk: bool = use_bulk
        self.dry_run: bool = dry_run
        self.force_items: set[str] = set(force_items or [])
        self.stream: TextIO = stream

    def ensure_destination_schema(self) -> None:
        """Reuses plugins/database/__init__.py's own _setup DDL dict - the
        exact schema-migration code the plugin itself runs on a fresh
        install, accessed via the class (no full plugin/SmartHomeNG
        instance needed - _setup only reads self.driver)."""
        fake_plugin = types.SimpleNamespace(driver=self.dest_driver)
        assert DatabasePlugin._setup.fget is not None
        setup_dict: dict[str, list[str]] = DatabasePlugin._setup.fget(fake_plugin)
        resolved: dict[str, list[str]] = {
            version: [apply_table_names(up, self.dest_tn), apply_table_names(down, self.dest_tn)]
            for version, (up, down) in setup_dict.items()
        }
        if self.dry_run:
            self.stream.write('[dry-run] would run schema setup on destination (creates {item}/{log} if missing)\n')
            return
        self.dest.setup(resolved)

    def migrate_items(self) -> tuple[dict[int, int | None], dict[int, str]]:
        """Returns dict source_item_id -> dest_item_id, and source_item_id
        -> name. Idempotent by item name - an item already present on the
        destination is reused, not re-inserted, so a resumed run is safe
        to call this again."""
        dest_store = ItemStore(self.dest, self.dest_tn)
        source_rows: list[tuple] = (
            self.source.fetchall(apply_table_names('SELECT {item_columns} FROM {item};', self.source_tn)) or []
        )
        id_map: dict[int, int | None] = {}
        names: dict[int, str] = {}
        for row in source_rows:
            source_id, name = row[COL_ITEM_ID], row[COL_ITEM_NAME]
            names[source_id] = name
            if self.dry_run:
                # dry-run: destination table may not exist yet, so a query failure here means "not found", not a real error.
                try:
                    existing = dest_store.find(name)
                except Exception:
                    existing = None
                id_map[source_id] = existing[COL_ITEM_ID] if existing else None
                continue
            existing = dest_store.find(name)
            if existing:
                dest_id = existing[COL_ITEM_ID]
            else:
                dest_id = dest_store.insert(name)
                self._copy_item_cached_value(row, dest_id)
            id_map[source_id] = dest_id
        return id_map, names

    def _copy_item_cached_value(self, source_row: tuple, dest_id: int) -> None:
        """Copy {item}'s own cached last-value columns (time/val_*/changed)
        directly - already in the encoded 3-column form, so this is a raw
        column copy, not something to route through ItemStore.update()
        (which expects one decoded value + item_type, not pre-encoded
        columns, and would need a pointless decode-then-re-encode round trip)."""
        _, _, item_time, val_str, val_num, val_bool, changed = source_row
        with self.dest.transaction() as cur:
            self.dest.execute(
                apply_table_names(
                    'UPDATE {item} SET time=:time, val_str=:val_str, val_num=:val_num,'
                    ' val_bool=:val_bool, changed=:changed WHERE id=:id;',
                    self.dest_tn,
                ),
                {
                    'time': item_time,
                    'val_str': val_str,
                    'val_num': val_num,
                    'val_bool': val_bool,
                    'changed': changed,
                    'id': dest_id,
                },
                cur=cur,
            )

    def migrate_logs(
        self, id_map: dict[int, int | None], names: dict[int, str]
    ) -> tuple[int, list[tuple[str, int, str]]]:
        """id_map/names as returned by migrate_items(). Per-item, strict:
        a failure on one item aborts that item immediately (see
        _copy_log_rows) rather than silently skipping the bad row."""
        dest_log_store = LogStore(self.dest, self.dest_tn)
        total_migrated: int = 0
        summary: list[tuple[str, int, str]] = []
        total_items: int = len(id_map)
        for item_num, (source_id, dest_id) in enumerate(id_map.items(), start=1):
            name: str = names[source_id]
            # Display-only progress prefix - name (not display_name) stays the identity for summary/--force lookups.
            display_name: str = f'[{item_num}/{total_items}] {name}'
            forced: bool = name in self.force_items
            existing_count: int
            if dest_id is None:
                # dry-run against a not-yet-created item (see migrate_items())
                existing_count = 0
            elif self.dry_run:
                # dry-run still checks real destination state; falls back to 0 only if the table doesn't exist yet.
                try:
                    existing_count = dest_log_store.count(dest_id)
                except Exception:
                    existing_count = 0
            else:
                existing_count = dest_log_store.count(dest_id)

            if existing_count > 0 and not forced:
                self.stream.write(
                    f'{display_name}: already has {existing_count} rows on destination, skipping (resume)\n'
                )
                summary.append((name, 0, 'skipped-resume'))
                continue

            if forced and existing_count > 0:
                if self.dry_run:
                    self.stream.write(
                        f'{display_name}: [dry-run] would delete {existing_count} existing rows and redo (--force)\n'
                    )
                else:
                    # dest_id is None only for a dry-run's not-yet-created item (see migrate_items()); guaranteed real here.
                    assert dest_id is not None
                    self._delete_dest_log_rows(dest_id)

            source_count: int = LogStore(self.source, self.source_tn).count(source_id)
            self.stream.write(f'{display_name}: migrating {source_count} rows...\n')

            if self.dry_run:
                summary.append((name, source_count, 'would-migrate'))
                total_migrated += source_count
                continue

            # dest_id is None only for a dry-run item (see migrate_items()); the dry-run branch above always continues.
            assert dest_id is not None
            migrated: int = self._copy_log_rows(source_id, dest_id, source_count, display_name)
            total_migrated += migrated

            dest_count: int = dest_log_store.count(dest_id)
            if dest_count != source_count:
                raise MigrationError(
                    f'{display_name}: row count mismatch after migration - source had {source_count}, destination has {dest_count}'
                )
            summary.append((name, migrated, 'migrated'))
        return total_migrated, summary

    def _delete_dest_log_rows(self, dest_id: int) -> None:
        with self.dest.transaction() as cur:
            self.dest.execute(
                apply_table_names('DELETE FROM {log} WHERE item_id=:id;', self.dest_tn), {'id': dest_id}, cur=cur
            )

    def _copy_log_rows(self, source_id: int, dest_id: int, total_rows: int, name: str) -> int:
        progress = DotProgress(total_rows, stream=self.stream, tick=self.batch_size)
        migrated: int = 0
        last_time: int | None = None
        select_sql: str = apply_table_names(
            'SELECT time, duration, val_str, val_num, val_bool, changed, val_quality FROM {log} '
            'WHERE item_id=:id AND (:last_time_null = 1 OR time > :last_time) ORDER BY time LIMIT :row_limit;',
            self.source_tn,
        )
        while True:
            rows: list[tuple] | None = self.source.fetchall(
                select_sql,
                {
                    'id': source_id,
                    'last_time_null': 1 if last_time is None else 0,
                    'last_time': last_time,
                    'row_limit': self.batch_size,
                },
            )
            if not rows:
                break
            try:
                if self.use_bulk:
                    self._insert_batch_bulk(dest_id, rows)
                else:
                    self._insert_batch_row_by_row(dest_id, rows)
            except Exception as e:
                raise MigrationError(f'{name}: failed migrating a batch starting after time={last_time}: {e}') from e
            migrated += len(rows)
            progress.advance(len(rows))
            last_time = rows[-1][0]
            if len(rows) < self.batch_size:
                break
        progress.finish()
        return migrated

    def _insert_batch_row_by_row(self, dest_id: int, rows: list[tuple]) -> None:
        insert_sql: str = apply_table_names(
            'INSERT INTO {log}(item_id, time, duration, val_str, val_num, val_bool, changed, val_quality) '
            'VALUES(:item_id, :time, :duration, :val_str, :val_num, :val_bool, :changed, :val_quality);',
            self.dest_tn,
        )
        with self.dest.transaction() as cur:
            for row_time, duration, val_str, val_num, val_bool, changed, val_quality in rows:
                self.dest.execute(
                    insert_sql,
                    {
                        'item_id': dest_id,
                        'time': row_time,
                        'duration': duration,
                        'val_str': val_str,
                        'val_num': val_num,
                        'val_bool': val_bool,
                        'changed': changed,
                        'val_quality': val_quality,
                    },
                    cur=cur,
                )

    def _insert_batch_bulk(self, dest_id: int, rows: list[tuple]) -> None:
        """Multi-row VALUES insert, sub-chunked to BULK_SUBCHUNK_ROWS to
        stay well under PostgreSQL's 65535-bound-parameter limit. Still a
        generic multi-row INSERT, not a driver-native bulk-load call
        (psycopg2.extras.execute_values() etc.) - a further speed step if
        this isn't fast enough, not implemented here."""
        insert_prefix: str = apply_table_names(
            'INSERT INTO {log}(item_id, time, duration, val_str, val_num, val_bool, changed, val_quality) VALUES ',
            self.dest_tn,
        )
        for start in range(0, len(rows), BULK_SUBCHUNK_ROWS):
            chunk: list[tuple] = rows[start : start + BULK_SUBCHUNK_ROWS]
            placeholders: list[str] = []
            params: dict[str, object] = {}
            for i, (row_time, duration, val_str, val_num, val_bool, changed, val_quality) in enumerate(chunk):
                placeholders.append(
                    f'(:item_id{i}, :time{i}, :duration{i}, :val_str{i}, :val_num{i}, :val_bool{i}, :changed{i}, :val_quality{i})'
                )
                params.update(
                    {
                        f'item_id{i}': dest_id,
                        f'time{i}': row_time,
                        f'duration{i}': duration,
                        f'val_str{i}': val_str,
                        f'val_num{i}': val_num,
                        f'val_bool{i}': val_bool,
                        f'changed{i}': changed,
                        f'val_quality{i}': val_quality,
                    }
                )
            with self.dest.transaction() as cur:
                self.dest.execute(insert_prefix + ', '.join(placeholders) + ';', params, cur=cur)


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description='Migrate the database plugin schema (item/log tables) between sqlite3/MySQL-MariaDB/PostgreSQL. '
        'Must be run with SmartHomeNG stopped.'
    )
    p.add_argument('--etc-dir', default=os.path.join(sh_basedir, 'etc'), help='etc/ directory to read plugin.yaml from')
    p.add_argument('--interactive', action='store_true', help='prompt for any side not fully specified via flags')
    p.add_argument('--dry-run', action='store_true', help='report what would happen, write nothing')
    p.add_argument('--bulk', action='store_true', help='use multi-row bulk inserts instead of row-by-row (default)')
    p.add_argument(
        '--batch-size', type=int, default=DEFAULT_BATCH_SIZE, help=f'rows per commit (default {DEFAULT_BATCH_SIZE})'
    )
    p.add_argument(
        '--force',
        nargs='+',
        default=[],
        metavar='ITEM',
        help='redo these items even if already migrated; also the required override to proceed when the source '
        'has native continuous aggregates (see source_has_native_cagg)',
    )

    for role in ('source', 'dest'):
        label: str = 'source' if role == 'source' else 'destination'
        p.add_argument(f'--{role}-instance', metavar='NAME', help=f'{label}: plugin.yaml instance name')
        p.add_argument(f'--{role}-driver', help=f'{label}: driver (sqlite3/pymysql/psycopg2), manual config')
        p.add_argument(
            f'--{role}-connect', type=json.loads, metavar='JSON', help=f'{label}: connect params as a JSON object'
        )
        p.add_argument(f'--{role}-password', help=f'{label}: password (prompted via getpass if omitted and needed)')
        p.add_argument(f'--{role}-prefix', default='', help=f'{label}: table prefix')

    return p


def build_database(driver: str, connect: ConnectParams, role: str, prefix: str = '') -> lib.db.Database:
    """*name* must match plugins/database/__init__.py's own naming scheme
    (('' if prefix == '' else prefix.capitalize()) + 'Database') exactly -
    lib.db.Database.setup()'s version-bookkeeping table name is derived
    from it (re.sub-sanitized name + '_version'). A mismatch here means the
    real plugin, started later against this same database with this same
    prefix, finds no rows in ITS version table, treats the DB as fresh, and
    reruns 'CREATE TABLE' against tables this tool already created."""
    name: str = ('' if prefix == '' else prefix.capitalize()) + 'Database'
    db = lib.db.Database(name, driver, connect, 'named')
    if not db.api_initialized:
        raise MigrationError(f'{role}: could not initialize DB-API driver {driver!r} - module installed?')
    db.connect()
    if not db.connected():
        raise MigrationError(f'{role}: could not connect')
    return db


def main(argv: list[str] | None = None) -> None:
    args = build_arg_parser().parse_args(argv)

    assert_shng_not_running()

    instances = discover_database_instances(args.etc_dir)

    source_driver, source_connect, source_prefix = resolve_role('source', 'source_prefix', instances, args)
    dest_driver, dest_connect, dest_prefix = resolve_role('dest', 'dest_prefix', instances, args)

    source_connect = connect_params_with_password_prompt('source', source_driver, source_connect, args.source_password)
    dest_connect = connect_params_with_password_prompt('destination', dest_driver, dest_connect, args.dest_password)

    assert_source_not_destination(source_driver, source_connect, source_prefix, dest_driver, dest_connect, dest_prefix)

    source_db = build_database(source_driver, source_connect, 'source', source_prefix)
    source_tn = build_table_names(source_prefix)
    log_table: str = source_tn['log']
    if source_has_native_cagg(source_db, source_driver, source_tn):
        if not args.force:
            raise MigrationError(
                f"Source's {log_table} hypertable has continuous aggregates (native aggregation mode) - this "
                f'tool only migrates raw {log_table}, not cagg-only data for buckets whose raw chunks are '
                f'already gone. Re-run with --force <item...> to migrate {log_table} only anyway, accepting '
                'that gap.'
            )
        print(
            f"WARNING: source's {log_table} hypertable has continuous aggregates - migrating raw {log_table} "
            'only (--force). Any bucket already covered only by a cagg (raw chunk dropped by native retention) '
            'will NOT be migrated.'
        )

    dest_db = build_database(dest_driver, dest_connect, 'destination', dest_prefix)

    migrator = DbMigrator(
        source_db,
        dest_db,
        dest_driver,
        source_prefix=source_prefix,
        dest_prefix=dest_prefix,
        batch_size=args.batch_size,
        use_bulk=args.bulk,
        dry_run=args.dry_run,
        force_items=args.force,
    )

    start: float = time_module.monotonic()
    migrator.ensure_destination_schema()
    id_map, names = migrator.migrate_items()
    total_rows, summary = migrator.migrate_logs(id_map, names)
    elapsed: float = time_module.monotonic() - start

    print(f'\n{"[dry-run] " if args.dry_run else ""}Summary:')
    print(f'  items: {len(id_map)}')
    print(f'  rows migrated: {total_rows}')
    skipped: int = sum(1 for _n, _c, status in summary if status == 'skipped-resume')
    if skipped:
        print(f'  items skipped (already on destination): {skipped}')
    print(f'  elapsed: {elapsed:.1f}s')

    source_db.close()
    dest_db.close()


if __name__ == '__main__':
    try:
        main()
    except MigrationError as e:
        print(f'\nERROR: {e}')
        sys.exit(1)
