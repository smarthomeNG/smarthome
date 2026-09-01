from . import common
import unittest
import sqlite3
import threading
import logging
import time
import importlib
import os
import tempfile
from collections import OrderedDict
from unittest.mock import patch
import lib.db


class TestDbBase:
    def api(self, paramstyle='qmark'):
        return MockDbApi(paramstyle)

    def db(self, connect='', paramstyle='qmark', format_input='qmark'):
        return lib.db.Database('test', self.api(paramstyle=paramstyle), connect, format_input)

    def _hold_lock_in_thread(self, db):
        """Acquire the lock in a daemon thread; return (release_event, thread).

        For simulating genuine cross-thread contention - a different
        thread's Thread object never matches the reentrancy guard's owner
        check, so this exercises real timeout/blocking behaviour rather
        than the same-thread RuntimeError path.
        """
        locked = threading.Event()
        release = threading.Event()

        def _worker():
            db.lock()
            locked.set()
            release.wait()
            db.release()

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        locked.wait()
        return release, t


class TestDbTests(unittest.TestCase, TestDbBase):
    def test_paramstyle_supported(self):
        self.db(paramstyle='qmark')
        self.db(paramstyle='format')
        self.db(paramstyle='numeric')
        self.db(paramstyle='pyformat')

    def test_paramstyle_not_supported(self):
        #        with self.assertRaisesRegex(Exception, 'driver format style .* not supported'):
        #            self.db(paramstyle='wrongformat')
        test_db = self.db(paramstyle='wrongformat')  # 'driver format style .* not supported'
        self.assertFalse(test_db.api_initialized)

    def test_lock_release_safe_on_failed_init(self):
        # self._fdb_lock must exist even on __init__'s three early-return
        # failure paths (bad dbapi import, unsupported format_input,
        # unsupported format_output), so generic cleanup code (e.g. a
        # defensive `finally: db.release()`) can call lock()/release() on
        # a half-built object without hitting AttributeError.
        test_db = self.db(paramstyle='wrongformat')
        self.assertFalse(test_db.api_initialized)
        self.assertTrue(test_db.lock(timeout=0))
        test_db.release()

    def test_connect(self):
        db = self.db(connect='host:server | user:username | password:secret')
        db.connect()
        args = db._dbapi.connect_kwargs
        self.assertTrue('host' in args)
        self.assertEqual('server', args['host'])
        self.assertTrue('user' in args)
        self.assertEqual('username', args['user'])
        self.assertTrue('password' in args)
        self.assertEqual('secret', args['password'])

    def test_connect_only_port_is_coerced_to_int(self):
        # 'port' must be coerced to int (drivers like pymysql require it);
        # every other connect value must stay the exact string from config,
        # not be guessed via int/float/str fallback typing.
        db = self.db(connect='passwd:123456 | port:3306 | host:myhost')
        self.assertEqual('123456', db._params['passwd'])
        self.assertEqual(3306, db._params['port'])
        self.assertEqual('myhost', db._params['host'])

    def test_connect_ordered_dict_list_preserves_native_yaml_types(self):
        # This shape (a list of single-key OrderedDicts) is exactly what
        # shyaml.yaml_load(..., ordered=True) produces for a real
        # etc/plugin.yaml connect: list written as multi-line YAML entries
        # (config.py loads plugin instance config with ordered=True). Each
        # value must keep its native YAML type (port: 3307 -> int,
        # check_same_thread: false -> bool); pymysql.connect() requires an
        # int port, not a string.
        connect = [
            OrderedDict([('port', 3307)]),
            OrderedDict([('check_same_thread', False)]),
            OrderedDict([('host', 'myhost')]),
        ]
        db = self.db(connect=connect)
        self.assertEqual(3307, db._params['port'])
        self.assertIsInstance(db._params['port'], int)
        self.assertIs(False, db._params['check_same_thread'])
        self.assertEqual('myhost', db._params['host'])

    def test_connect_set_connected(self):
        db = self.db()
        self.assertFalse(db.connected())

        db.connect()
        self.assertTrue(db.connected())

    def test_close(self):
        db = self.db()
        db.connect()
        conn = db._conn
        db.close()
        self.assertTrue(conn.close_kwargs is not None)

    def test_close_set_connected(self):
        db = self.db()
        db.connect()
        db.close()
        self.assertFalse(db.connected())

    def test_lock(self):
        db = self.db()
        self.assertTrue(db.lock())

    def test_lock_already_locked(self):
        # Genuine cross-thread contention - a same-thread double lock() is
        # a different case now (see test_lock_reentrant_same_thread_raises).
        db = self.db()
        release, t = self._hold_lock_in_thread(db)
        try:
            self.assertFalse(db.lock(0))
        finally:
            release.set()
            t.join(timeout=1)

    def test_lock_reentrant_same_thread_raises_immediately(self):
        db = self.db()
        db.lock()
        try:
            with self.assertRaisesRegex(RuntimeError, r'lock\(\) called re-entrantly'):
                db.lock()
        finally:
            db.release()

    def test_release(self):
        db = self.db()
        db.lock()
        db.release()

    def test_release_not_locked(self):
        db = self.db()
        with self.assertRaisesRegex(Exception, 'release unlocked lock'):
            db.release()

    def test_commit(self):
        db = self.db()
        db.connect()
        db.commit()
        self.assertTrue(db._conn.commit_kwargs is not None)

    def test_rollback(self):
        db = self.db()
        db.connect()
        db.rollback()
        self.assertTrue(db._conn.rollback_kwargs is not None)

    def test_cursor(self):
        db = self.db()
        db.connect()
        self.assertTrue(db.cursor() is not None)
        self.assertTrue(db._conn.cursor_kwargs is not None)

    def test_setup(self):
        # Each version commits its own transaction() (see setup()'s
        # docstring - MySQL/MariaDB DDL commits implicitly regardless, so
        # one end-of-loop commit couldn't make the whole migration atomic
        # there anyway; per-step commits narrow a crash's blast radius to
        # one step instead of the whole remaining migration). That means a
        # fresh cursor per transaction() - track cursor creation order to
        # inspect each step's own statements, rather than relying on one
        # shared cursor across the whole call the way a single-transaction
        # setup() would have.
        db = self.db()
        db.connect()
        cursors = []
        orig_cursor_method = db._conn.cursor

        def spy_cursor(**kwargs):
            c = orig_cursor_method(**kwargs)
            cursors.append(c)
            return c

        db._conn.cursor = spy_cursor
        db.setup({1: ['ROLLOUT 1', 'ROLLBACK 1'], 2: ['ROLLOUT 2', 'ROLLBACK 2']})

        self.assertEqual(3, len(cursors), 'bootstrap check + one transaction() per version step')
        # cursors[0]: bootstrap check (SELECT version) - not asserted here
        self.assertEqual('ROLLOUT 1', cursors[1].execute_kwargs[0][0])
        self.assertEqual('INSERT INTO test_version', cursors[1].execute_kwargs[1][0][0:24])
        self.assertEqual(1, cursors[1].execute_kwargs[1][1][0])
        self.assertEqual('ROLLOUT 2', cursors[2].execute_kwargs[0][0])
        self.assertEqual('INSERT INTO test_version', cursors[2].execute_kwargs[1][0][0:24])
        self.assertEqual(2, cursors[2].execute_kwargs[1][1][0])

    def test_setup_releases_lock_even_if_upgrade_fails(self):
        db = self.db()
        db.connect()

        original_execute = db.execute

        def failing_execute(stmt, *a, **kw):
            if stmt == 'ROLLOUT 1':
                raise RuntimeError('simulated bad SQL for this driver')
            return original_execute(stmt, *a, **kw)

        with patch.object(db, 'execute', side_effect=failing_execute):
            with self.assertRaises(RuntimeError):
                db.setup({1: ['ROLLOUT 1', 'ROLLBACK 1']})

        # a failed upgrade statement must not leave self._fdb_lock held -
        # every future connect()/close()/setup()/verify() call would hang
        self.assertTrue(db.lock(0), 'self._fdb_lock was left held after setup() raised')
        db.release()

    def test_setup_step_failure_does_not_undo_earlier_committed_steps(self):
        # setup() must commit each version step independently - a crash
        # between steps must not lose an already-applied step's version
        # row, and re-running must retry only the step that failed, not
        # re-apply already-committed DDL. Uses a real sqlite3 file (not the
        # mock) so version persistence across the failure is genuinely
        # checked, not just call counts.
        db = lib.db.Database('setup_step_test', 'sqlite3', {'database': ':memory:'}, 'qmark')
        db.connect()

        orig_execute = db.execute

        def fail_on_step_2(stmt, *a, **kw):
            if stmt == 'SELECT 2':
                raise RuntimeError('simulated failure applying step 2')
            return orig_execute(stmt, *a, **kw)

        db.execute = fail_on_step_2
        with self.assertRaises(RuntimeError):
            db.setup({1: ['SELECT 1', 'SELECT 1'], 2: ['SELECT 2', 'SELECT 2']})
        db.execute = orig_execute

        (version,) = db.fetchone('SELECT MAX(version) FROM setup_step_test_version')
        self.assertEqual(1, version, "step 1's commit must survive step 2's failure")

    def test_setup_applies_string_version_keys_in_numeric_not_lexicographic_order(self):
        # setup() must apply string version keys ('1'..'8'-style, per the
        # database plugin's real schema) in numeric order, not
        # lexicographic - a plain string sort puts '10' before '2' once a
        # caller reaches double digits, which would apply step 10's DDL
        # before steps 2-9 it may depend on.
        db = lib.db.Database('setup_order_test', 'sqlite3', {'database': ':memory:'}, 'qmark')
        db.connect()

        applied = []
        orig_execute = db.execute

        def spy_execute(stmt, *a, **kw):
            if stmt.startswith('SELECT ') and stmt != 'SELECT MAX(version) FROM setup_order_test_version;':
                applied.append(stmt)
            return orig_execute(stmt, *a, **kw)

        db.execute = spy_execute
        db.setup({'2': ['SELECT 2', ''], '9': ['SELECT 9', ''], '10': ['SELECT 10', '']})
        db.execute = orig_execute

        self.assertEqual(['SELECT 2', 'SELECT 9', 'SELECT 10'], applied)

    def test_execute_internal_cursor(self):
        db = self.db()
        db.connect()
        db.execute('select 1')
        self.assertEqual('select 1', db._conn.cursor_return.execute_kwargs[0][0])

    def test_execute_custom_cursor(self):
        db = self.db()
        db.connect()
        cur = db.cursor()
        db.execute('select 1', cur=cur)
        self.assertEqual('select 1', cur.execute_kwargs[0][0])

    def test_verify(self):
        db = self.db()
        db.connect()
        db.verify()
        self.assertEqual('SELECT 1', db._conn.cursor_return.execute_kwargs[0][0])

    def test_verify_gives_up_after_retries_on_lock_contention(self):
        # Lock contention (lock() returning False without raising) must count
        # against the retry budget just like a connection exception does,
        # otherwise verify() loops forever whenever the lock is held elsewhere.
        db = self.db()
        db.connect()
        calls = []

        def fake_lock(timeout=-1):
            calls.append(timeout)
            if len(calls) > 10:
                raise AssertionError('verify() did not respect the retry limit on lock contention')
            return False

        db.lock = fake_lock
        result = db.verify(retry=3, delay=0)
        self.assertEqual(0, result)
        self.assertEqual(3, len(calls))

    def test_verify_names_lock_holder_on_contention(self):
        db = self.db()
        db.connect()
        release, holder_thread = self._hold_lock_in_thread(db)
        try:
            with self.assertLogs('lib.db', level='WARNING') as cm:
                db.verify(retry=1, delay=0)
            self.assertTrue(any(holder_thread.name in msg and 'held by thread' in msg for msg in cm.output), cm.output)
        finally:
            release.set()
            holder_thread.join()

    def test_verify_survives_connection_closed_between_connect_and_lock(self):
        # connect() acquires/releases self._fdb_lock internally before
        # returning; verify() then separately re-acquires it via its own
        # self.lock(2). A connection closed by another thread in that gap
        # must be treated like any other failed-verification retry, not
        # crash verify() with AttributeError ('NoneType' object has no
        # attribute 'close') from probe_cur.close().
        db = self.db()
        db.connect()

        real_lock = db.lock

        def fake_lock(timeout=-1):
            acquired = real_lock(timeout)
            if acquired:
                # simulate a concurrent close() landing in the window
                # between connect()'s internal lock release and this
                # lock() call succeeding
                db._conn = None
                db._connected = False
            return acquired

        db.lock = fake_lock

        with self.assertLogs('lib.db', level='WARNING') as cm:
            result = db.verify(retry=1, delay=0)
        self.assertEqual(0, result)
        self.assertTrue(any('closed between connect() and lock()' in msg for msg in cm.output), cm.output)

    def test_execute_error_logs_by_default(self):
        db = self.db()
        db.connect()
        cur = db.cursor()
        cur.execute = lambda *a, **kw: (_ for _ in ()).throw(Exception('no such table: foo_version'))
        with self.assertRaisesRegex(Exception, 'no such table: foo_version'):
            with self.assertLogs('lib.db', level='ERROR'):
                db.execute('SELECT 1', cur=cur)

    def test_execute_quiet_suppresses_log_but_still_raises(self):
        # quiet=True must silence the ERROR log for an expected "table
        # missing" probe (e.g. setup()'s first-run version check) without
        # ever swallowing the exception itself - callers still need to catch
        # it to react (e.g. create the table).
        db = self.db()
        db.connect()
        cur = db.cursor()
        cur.execute = lambda *a, **kw: (_ for _ in ()).throw(Exception('no such table: foo_version'))
        with self.assertRaisesRegex(Exception, 'no such table: foo_version'):
            with self.assertNoLogs('lib.db', level='ERROR'):
                db.execute('SELECT 1', cur=cur, quiet=True)

    def test_fetchone(self):
        db = self.db()
        db.connect()
        db.fetchone('SELECT 1')

    def test_fetchall(self):
        db = self.db()
        db.connect()
        db.fetchall('SELECT 1')

    # -- NO_CURSOR sentinel: cur omitted vs. cur=None must be distinguishable -

    def test_execute_cur_omitted_uses_no_cursor_path(self):
        # Omitting 'cur' entirely must behave exactly as before - it's the
        # NO_CURSOR sentinel default, not a literal None.
        db = self.db()
        db.connect()
        db.execute('SELECT 1')

    def test_execute_explicit_cur_none_raises(self):
        # A literal cur=None is a caller bug (something expected to hand in
        # a real cursor but got None instead) - it must not be silently
        # treated the same as "omitted".
        db = self.db()
        db.connect()
        with self.assertRaisesRegex(TypeError, 'received cur=None'):
            db.execute('SELECT 1', cur=None)

    def test_fetchone_explicit_cur_none_raises(self):
        db = self.db()
        db.connect()
        with self.assertRaisesRegex(TypeError, 'received cur=None'):
            db.fetchone('SELECT 1', cur=None)

    def test_fetchall_explicit_cur_none_raises(self):
        db = self.db()
        db.connect()
        with self.assertRaisesRegex(TypeError, 'received cur=None'):
            db.fetchall('SELECT 1', cur=None)

    def test_fetchone_real_cursor_still_works(self):
        # A genuine cursor (e.g. from transaction()) must still take the
        # "use my cursor" branch unchanged.
        db = self.db()
        db.connect()
        with db.transaction() as cur:
            db.fetchone('SELECT 1', cur=cur)

    # -- reconnect-on-stale-connection (cur=None path) -----------------------
    #
    # execute()/fetchone()/fetchall() manage their own cursor when called
    # with cur=None - this is the path store.py's ItemStore/LogStore CRUD
    # layer always uses, and it never calls verify() itself. A connection
    # that goes stale between calls (network blip, server-side disconnect)
    # must reconnect and retry rather than wedge every subsequent cur=None
    # call until something unrelated calls verify() or the process
    # restarts. These tests cover lib.db.Database directly rather than
    # through the plugin.

    def _break_connection_once(self, db, where='cursor'):
        """Make the *current* connection's cursor()/execute() raise exactly
        once, then behave normally again on the connection that's active
        for that attempt (mirrors both failure shapes noted in
        _cursor_op_with_reconnect: sqlite3 raises immediately from
        .cursor() on an already-closed connection, pymysql instead tends to
        return a cursor that only fails on first use)."""
        conn = db._conn
        calls = {'n': 0}
        if where == 'cursor':
            original = conn.cursor

            def failing(**kwargs):
                calls['n'] += 1
                if calls['n'] == 1:
                    raise Exception('simulated stale connection')
                return original(**kwargs)

            conn.cursor = failing
        else:  # 'execute' - cursor() itself succeeds, first .execute() call fails
            original_cursor = conn.cursor

            def wrapped_cursor(**kwargs):
                cur = original_cursor(**kwargs)
                original_execute = cur.execute

                def failing_execute(*a, **kw):
                    calls['n'] += 1
                    if calls['n'] == 1:
                        raise Exception('simulated stale connection')
                    return original_execute(*a, **kw)

                cur.execute = failing_execute
                return cur

            conn.cursor = wrapped_cursor
        return calls

    def test_fetchall_reconnects_after_stale_connection_cursor_failure(self):
        db = self.db()
        db.connect()
        first_conn = db._conn
        self._break_connection_once(db, where='cursor')

        result = db.fetchall('SELECT 1')

        self.assertEqual([[0]], result)
        self.assertIsNot(first_conn, db._conn, 'must have reconnected to a new connection object')

    def test_fetchone_reconnects_after_stale_connection_execute_failure(self):
        db = self.db()
        db.connect()
        first_conn = db._conn
        self._break_connection_once(db, where='execute')

        result = db.fetchone('SELECT 1')

        self.assertEqual([0], result)
        self.assertIsNot(first_conn, db._conn, 'must have reconnected to a new connection object')

    def test_execute_reconnects_after_stale_connection(self):
        db = self.db()
        db.connect()
        first_conn = db._conn
        self._break_connection_once(db, where='cursor')

        db.execute('INSERT INTO x VALUES (1)')

        self.assertIsNot(first_conn, db._conn, 'must have reconnected to a new connection object')

    def test_reconnect_gives_up_and_logs_after_second_failure(self):
        # a genuinely broken destination, not a transient blip: the first
        # attempt fails (stale connection), and the reconnect attempt
        # itself also fails (server really is unreachable) - must still
        # raise the original error, and must still log exactly once.
        db = self.db()
        db.connect()

        def always_failing_cursor(**kwargs):
            raise Exception('simulated persistent connection failure')

        db._conn.cursor = always_failing_cursor

        def failing_connect(**kwargs):
            raise Exception('simulated reconnect also fails')

        db._dbapi.connect = failing_connect

        with self.assertRaisesRegex(Exception, 'simulated persistent connection failure'):
            with self.assertLogs('lib.db', level='ERROR'):
                db.fetchall('SELECT 1')

    def test_operational_error_from_statement_still_reconnects(self):
        # A driver exposing the PEP 249 exception hierarchy: connection-
        # level errors (OperationalError - lost connection, server gone)
        # raised by the statement itself must keep the close/reconnect/
        # retry behavior.
        db = lib.db.Database('test', MockClassifiedDbApi('qmark'), '', 'qmark')
        db.connect()
        first_conn = db._conn
        original_cursor = first_conn.cursor
        calls = {'n': 0}

        def wrapped_cursor(**kwargs):
            cur = original_cursor(**kwargs)
            original_execute = cur.execute

            def failing_execute(*a, **kw):
                calls['n'] += 1
                if calls['n'] == 1:
                    raise MockClassifiedDbApi.OperationalError('simulated lost connection')
                return original_execute(*a, **kw)

            cur.execute = failing_execute
            return cur

        first_conn.cursor = wrapped_cursor

        result = db.fetchall('SELECT 1')

        self.assertEqual([[0]], result)
        self.assertIsNot(first_conn, db._conn, 'must have reconnected to a new connection object')

    def test_statement_error_does_not_tear_down_healthy_connection(self):
        # A statement-level failure (IntegrityError, ProgrammingError -
        # duplicate key, SQL typo) on a live connection is permanent:
        # retrying it fails identically, and the close/reconnect teardown
        # would discard whatever else is pending on the connection. It must
        # raise immediately and leave the connection untouched.
        db = lib.db.Database('test', MockClassifiedDbApi('qmark'), '', 'qmark')
        db.connect()
        first_conn = db._conn
        original_cursor = first_conn.cursor

        def wrapped_cursor(**kwargs):
            cur = original_cursor(**kwargs)

            def failing_execute(*a, **kw):
                raise MockClassifiedDbApi.IntegrityError('simulated duplicate key')

            cur.execute = failing_execute
            return cur

        first_conn.cursor = wrapped_cursor

        with self.assertRaisesRegex(MockClassifiedDbApi.IntegrityError, 'simulated duplicate key'):
            db.execute('INSERT INTO x VALUES (1)')

        self.assertIs(first_conn, db._conn, 'a statement error must not tear down the connection')
        self.assertTrue(db.connected())

    def test_cursor_level_failure_still_reconnects_regardless_of_class(self):
        # cursor() raising at all means the connection object itself is
        # unusable (sqlite3 raises ProgrammingError on a closed
        # connection) - always reconnect-worthy, whatever the class.
        db = lib.db.Database('test', MockClassifiedDbApi('qmark'), '', 'qmark')
        db.connect()
        first_conn = db._conn
        original_cursor = first_conn.cursor
        calls = {'n': 0}

        def failing_cursor(**kwargs):
            calls['n'] += 1
            if calls['n'] == 1:
                raise MockClassifiedDbApi.ProgrammingError('Cannot operate on a closed database.')
            return original_cursor(**kwargs)

        first_conn.cursor = failing_cursor

        result = db.fetchall('SELECT 1')

        self.assertEqual([[0]], result)
        self.assertIsNot(first_conn, db._conn, 'must have reconnected to a new connection object')

    def test_fetchall_not_connected_returns_empty_without_reconnect_attempt(self):
        # never connected at all - must preserve today's behaviour exactly
        # (empty result, no attempted reconnect / no connection storm).
        # Initial connect() throttling is _initialize_db()'s job, not this
        # retry's.
        db = self.db()
        self.assertEqual([], db.fetchall('SELECT 1'))
        self.assertIsNone(db._conn)

    def test_fetchone_not_connected_returns_none_not_empty_string(self):
        # fetchone()'s disconnect sentinel must be None, not '' - a caller
        # checking `if row is None` (the normal DB-API2 "no row" check)
        # must catch it; `row[0]` on '' raises IndexError instead of the
        # TypeError a None check would cleanly catch.
        db = self.db()
        self.assertIsNone(db.fetchone('SELECT 1'))
        self.assertIsNone(db._conn)

    def test_not_connected_logs_visibly_instead_of_silent(self):
        # A not-connected fetchone() must log visibly, not just return an
        # empty result indistinguishable from a real no-rows result to
        # callers that don't null-check (e.g. plugins/db_addon's
        # self._fetchone(query)[0]).
        db = self.db()
        with self.assertLogs('lib.db', level='INFO') as cm:
            self.assertIsNone(db.fetchone('SELECT 1'))
        self.assertTrue(any('not connected' in msg for msg in cm.output), cm.output)

    def test_cursor_op_lock_wait_tracks_configured_timeout_not_hardcoded_300(self):
        # _cursor_op_with_reconnect's lock wait must respect the configured
        # db_query_timeout, not a hardcoded value - this is the cur=None
        # path store.py's ItemStore/LogStore always use, so a hung server
        # must not stall it regardless of what the user configured.
        db = self.db()
        db.connect()

        locked_evt = threading.Event()
        release_evt = threading.Event()

        def _worker():
            db.lock()
            locked_evt.set()
            release_evt.wait()
            db.release()

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        locked_evt.wait()
        try:
            start = time.monotonic()
            with patch('lib.db._sh_db_query_timeout', return_value=0.1):
                with self.assertRaisesRegex(TimeoutError, 'could not acquire lock within 0.1s'):
                    db.fetchall('SELECT 1', quiet=True)
            elapsed = time.monotonic() - start
            self.assertLess(elapsed, 5, 'lock wait took much longer than the configured 0.1s timeout')
        finally:
            release_evt.set()
            t.join(timeout=1)


class TestDbWalMode(unittest.TestCase):
    """wal_mode needs a real, file-backed sqlite3 database - WAL is not
    supported for ':memory:' databases, and verifying it actually took
    effect means reading back PRAGMA journal_mode, not just call counts."""

    def setUp(self):
        fd, self._db_path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        self.addCleanup(os.unlink, self._db_path)

    def _journal_mode(self, db):
        (mode,) = db.fetchone('PRAGMA journal_mode;')
        return str(mode).lower()

    def test_wal_mode_false_by_default(self):
        db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark')
        db.connect()
        self.assertNotEqual('wal', self._journal_mode(db))

    def test_wal_mode_true_activates_wal(self):
        db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark', wal_mode=True)
        db.connect()
        self.assertEqual('wal', self._journal_mode(db))

    def test_wal_mode_persists_across_reconnect(self):
        # WAL is a property of the database file, not the connection - a
        # later connect() (even with wal_mode not explicitly requested
        # again) must see it still active once the file has it.
        db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark', wal_mode=True)
        db.connect()
        db.close()

        db2 = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark')
        db2.connect()
        self.assertEqual('wal', self._journal_mode(db2), 'WAL, once set on the file, must survive a plain reconnect')

    def test_wal_mode_idempotent_on_second_connect(self):
        db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark', wal_mode=True)
        db.connect()
        db.close()
        db.connect()  # must not raise or warn on an already-WAL file
        self.assertEqual('wal', self._journal_mode(db))

    def test_wal_mode_warns_for_non_sqlite3_driver(self):
        with self.assertLogs('lib.db', level='WARNING') as log:
            lib.db.Database('wal_test', MockPymysqlApi('qmark'), {}, 'qmark', wal_mode=True)
        self.assertTrue(any('wal_mode' in m and 'not sqlite3' in m for m in log.output))

    def test_wal_mode_no_warning_for_sqlite3(self):
        with self.assertNoLogs('lib.db', level='WARNING'):
            db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark', wal_mode=True)
            db.connect()

    def test_reports_wal_left_active_when_not_requested(self):
        # A prior run (or another tool) left the file in WAL mode; this
        # instance never asked for wal_mode - read-only check, must still
        # surface that the file itself disagrees with the current setting.
        db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark', wal_mode=True)
        db.connect()
        db.close()

        with self.assertLogs('lib.db', level='INFO') as log:
            db2 = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark')
            db2.connect()
        self.assertTrue(
            any('WAL' in m and 'not requested' in m for m in log.output),
            f'expected a WAL-left-active notice, got: {log.output}',
        )
        # Read-only: must not have (re-)issued the setting PRAGMA itself.
        self.assertEqual('wal', self._journal_mode(db2))

    def test_no_report_when_file_is_not_wal_and_not_requested(self):
        # connect() itself always logs one INFO line ("Connected with...") -
        # asserting on content, not blanket absence of any INFO log.
        with self.assertLogs('lib.db', level='INFO') as log:
            db = lib.db.Database('wal_test', 'sqlite3', {'database': self._db_path}, 'qmark')
            db.connect()
        self.assertFalse(any('WAL' in m and 'not requested' in m for m in log.output))


class DbQueryBaseTests(TestDbBase):
    format = None
    query = None
    args = (1, 'test')

    def execute(self, sql, args, format_input='qmark', paramstyle='pyformat'):
        db = self.db(paramstyle=paramstyle, format_input=format_input)
        db.connect()
        db.execute(sql, args)
        return db._conn.cursor_return.execute_kwargs[0]

    def test_execute_qmark(self):
        args = self.execute(self.query, self.args, self.format, 'qmark')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = ? AND Name = ?', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_format(self):
        args = self.execute(self.query, self.args, self.format, 'format')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %s AND Name = %s', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_numeric(self):
        args = self.execute(self.query, self.args, self.format, 'numeric')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = :1 AND Name = :2', args[0])
        self.assertEqual([1, 'test'], args[1])

    def test_execute_pyformat(self):
        args = self.execute(self.query, self.args, self.format, 'pyformat')
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %(arg1)s AND Name = %(arg2)s', args[0])
        self.assertEqual({'arg1': 1, 'arg2': 'test'}, args[1])

    def test_execute_same_format_input_is_output(self):
        args = self.execute(self.query_formatter, self.args, self.format, self.format)
        self.assertEqual(self.query_formatter, args[0])

    def _assert_argument_reuse(self, args, output_format):
        if self.format == output_format:
            args_list = list(self.args)
            args_dict = self.args
        else:
            args_list = self.expect_args_argsreuse_list
            args_dict = self.expect_args_argsreuse_dict
        if isinstance(args[1], list):
            self.assertEqual(args_list, args[1])
        else:
            self.assertEqual(args_dict, dict(args[1]))

    def test_execute_argument_reuse_qmark(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'qmark')
        self._assert_argument_reuse(args, 'qmark')

    def test_execute_argument_reuse_format(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'format')
        self._assert_argument_reuse(args, 'format')

    def test_execute_argument_reuse_numeric(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'numeric')
        self._assert_argument_reuse(args, 'numeric')

    def test_execute_argument_reuse_named(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'named')
        self._assert_argument_reuse(args, 'named')

    def test_execute_argument_reuse_pyformat(self):
        args = self.execute(self.query_argsreuse, self.args, self.format, 'pyformat')
        self._assert_argument_reuse(args, 'pyformat')


class TestDbQueryQmark(unittest.TestCase, DbQueryBaseTests):
    format = 'qmark'
    query = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = ? AND Name = ?'
    expect_args_argsreuse_list = [1, 'test']
    expect_args_argsreuse_dict = {'arg1': 1, 'arg2': 'test'}


class TestDbQueryFormat(unittest.TestCase, DbQueryBaseTests):
    format = 'format'
    query = 'SELECT * FROM TABLE WHERE ID = %s AND Name = %s'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = %d AND Name = %s'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = %s AND Name = %s'
    expect_args_argsreuse_list = [1, 'test']
    expect_args_argsreuse_dict = {'arg1': 1, 'arg2': 'test'}


class TestDbQueryNumeric(unittest.TestCase, DbQueryBaseTests):
    format = 'numeric'
    query = 'SELECT * FROM TABLE WHERE ID = :1 AND Name = :2'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = :1 AND Name = :2'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = :2 AND Name = :2'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2': 'test'}


class TestDbQueryNamed(unittest.TestCase, DbQueryBaseTests):
    format = 'named'
    args = {'arg1': 1, 'arg2': 'test'}
    query = 'SELECT * FROM TABLE WHERE ID = :arg1 AND Name = :arg2'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = :arg1 AND Name = :arg2'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = :arg2 AND Name = :arg2'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2': 'test'}


class TestDbQueryPyformat(unittest.TestCase, DbQueryBaseTests):
    format = 'pyformat'
    args = {'arg1': 1, 'arg2': 'test'}
    query = 'SELECT * FROM TABLE WHERE ID = %(arg1)s AND Name = %(arg2)s'
    query_formatter = 'SELECT * FROM TABLE WHERE ID = %(arg1)d AND Name = %(arg2)s'
    query_argsreuse = 'SELECT * FROM TABLE WHERE ID = %(arg2)d AND Name = %(arg2)s'
    expect_args_argsreuse_list = ['test', 'test']
    expect_args_argsreuse_dict = {'arg2': 'test'}

    def test_execute_format_always_uses_strings(self):
        """Converting pyformat to format should always use %s
        See also: https://github.com/smarthomeNG/smarthome/pull/131/commits/bcaa491f91251e2129fa40958bad09cc623d9732
        """
        args = self.execute(
            'SELECT * FROM TABLE WHERE ID = %(arg1)d AND Name = %(arg2)s', self.args, self.format, 'format'
        )
        self.assertEqual('SELECT * FROM TABLE WHERE ID = %s AND Name = %s', args[0])


class TestDbLiteralPercentEscaping(unittest.TestCase, TestDbBase):
    # pymysql (paramstyle 'pyformat') substitutes parameters via Python's
    # own '%' string formatting (query % args) - a literal '%' anywhere in
    # the SQL text (e.g. the modulo operator, as used by the database
    # plugin's bucket-boundary GROUP BY expression) is otherwise misread as
    # the start of another format spec, raising "not enough arguments for
    # format string" even though the query has nothing to do with that
    # parameter. Requires a real MariaDB/pymysql target - sqlite3
    # (paramstyle 'qmark') does real positional binding, not string
    # substitution, so this can't be exercised there.
    #
    # Deliberately not built on DbQueryBaseTests - that mixin's own
    # test_execute_* methods would also get collected here, and rely on
    # class attributes (query_formatter, query_argsreuse, ...) this test
    # doesn't set. Only its execute() helper's pattern is reused, inline.

    def _prepared(self, sql, args, format_input, paramstyle):
        db = self.db(paramstyle=paramstyle, format_input=format_input)
        db.connect()
        db.execute(sql, args)
        return db._conn.cursor_return.execute_kwargs[0]

    def test_literal_percent_survives_named_to_pyformat_translation(self):
        stmt, params = self._prepared('SELECT time - (time % :step) FROM log', {'step': 5}, 'named', 'pyformat')
        self.assertEqual('SELECT time - (time %% %(step)s) FROM log', stmt)

        # the actual failure mode: pymysql's real substitution step is
        # query % args - prove the translated statement survives it (the
        # untranslated statement raises TypeError: not enough arguments
        # for format string on exactly this query).
        stmt % params

    def test_literal_percent_not_double_escaped_when_source_already_pyformat(self):
        # pyformat -> pyformat is a no-op translation (empty dict in
        # _translations) - a source statement already written with real
        # %(name)s placeholders must not have its own '%' doubled.
        stmt, params = self._prepared('SELECT * FROM t WHERE id = %(arg1)s', {'arg1': 1}, 'pyformat', 'pyformat')
        self.assertEqual('SELECT * FROM t WHERE id = %(arg1)s', stmt)
        stmt % params


class MockDbApi:
    def __init__(self, paramstyle):
        self.paramstyle = paramstyle
        self.connected_kwargs = None

    def connect(self, **kwargs):
        self.connect_kwargs = kwargs if kwargs is not None else True
        return MockDbApiConnection()


class MockPymysqlApi(MockDbApi):
    __name__ = 'pymysql'


class MockClassifiedDbApi(MockDbApi):
    """Mock driver exposing the PEP 249 exception hierarchy, so
    _cursor_op_with_reconnect's error classification is active (drivers
    without these attributes fall back to legacy retry-everything)."""

    __name__ = 'classified'

    class InterfaceError(Exception):
        pass

    class OperationalError(Exception):
        pass

    class InternalError(Exception):
        pass

    class IntegrityError(Exception):
        pass

    class ProgrammingError(Exception):
        pass


class MockDbApiConnection:
    def __init__(self):
        self.close_kwargs = None
        self.commit_kwargs = None
        self.rollback_kwargs = None
        self.cursor_kwargs = None
        self.cursor_return = None

    def close(self, **kwargs):
        self.close_kwargs = kwargs if kwargs is not None else True

    def commit(self, **kwargs):
        self.commit_kwargs = kwargs if kwargs is not None else True

    def rollback(self, **kwargs):
        self.rollback_kwargs = kwargs if kwargs is not None else True

    def cursor(self, **kwargs):
        self.cursor_kwargs = kwargs if kwargs is not None else True
        self.cursor_return = MockDbApiCursor()
        return self.cursor_return


class MockDbApiCursor:
    def __init__(self):
        self.execute_kwargs = []
        self.close_kwargs = None

    def execute(self, *kwargs):
        self.execute_kwargs.append(kwargs if kwargs is not None else True)
        return {}

    def close(self, **kwargs):
        self.close_kwargs = kwargs if kwargs is not None else True

    def fetchone(self, **kwargs):
        return [0]

    def fetchall(self, **kwargs):
        return [[0]]


class TestHangWatchdog(unittest.TestCase):
    """_hang_watchdog logs a WARNING partway through a slow bounded wait,
    and stays silent when the wrapped operation finishes quickly."""

    def test_fires_warning_when_operation_outlasts_half_timeout(self):
        with self.assertLogs('test.watchdog', level='WARNING') as cm:
            with lib.db._hang_watchdog(logging.getLogger('test.watchdog'), 'mydb', 'doing stuff', timeout=0.1):
                time.sleep(0.15)
        self.assertTrue(any('doing stuff' in msg and 'mydb' in msg for msg in cm.output))
        self.assertTrue(any('still running' in msg for msg in cm.output))

    def test_silent_when_operation_completes_before_half_timeout(self):
        logger = logging.getLogger('test.watchdog.quiet')
        with self.assertNoLogs(logger, level='WARNING'):
            with lib.db._hang_watchdog(logger, 'mydb', 'doing stuff', timeout=1.0):
                pass  # returns instantly - timer must be cancelled, not fired
        # give a cancelled timer a chance to (wrongly) fire, to make the
        # negative assertion meaningful rather than just "didn't wait long enough"
        time.sleep(0.05)

    def test_message_includes_deadline_countdown(self):
        with self.assertLogs('test.watchdog2', level='WARNING') as cm:
            with lib.db._hang_watchdog(logging.getLogger('test.watchdog2'), 'mydb', 'q', timeout=0.1):
                time.sleep(0.15)
        # timeout=0.1 -> warn_after=0.05, remaining=0.05 -> "0s"/"0s" after rounding
        self.assertTrue(any('will give up in' in msg for msg in cm.output))


class TestDbConnectHungLock(unittest.TestCase, TestDbBase):
    """connect() must raise instead of blocking indefinitely when lock is held."""

    def test_raises_timeout_error_when_lock_held(self):
        # Genuine cross-thread contention - a same-thread double lock() now
        # hits the reentrancy guard instead (see TestDbTests), so this must
        # use a background thread to hold the lock, not a direct db.lock().
        db = self.db()
        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.05):
                with self.assertRaises(TimeoutError):
                    db.connect()
        finally:
            release.set()
            t.join(timeout=1)

    def test_logs_early_watchdog_warning_before_timeout(self):
        # The watchdog should warn partway through the wait (b), not just
        # after it - so a wedged connect() is visible in the log before it
        # eventually raises, not only in the final error line.
        db = self.db()
        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.1):
                with self.assertLogs('lib.db', level='WARNING') as cm:
                    with self.assertRaises(TimeoutError):
                        db.connect()
            self.assertTrue(any('still running' in msg and 'connect()' in msg for msg in cm.output))
        finally:
            release.set()
            t.join(timeout=1)

    def test_lock_released_after_failed_connect(self):
        # If dbapi.connect() raises, the lock must still be released.
        db = self.db()
        db._dbapi.connect = lambda **kw: (_ for _ in ()).throw(Exception('host unreachable'))
        with patch('lib.db._sh_db_query_timeout', return_value=1):
            with self.assertRaises(Exception):
                db.connect()
        self.assertTrue(db.lock(0), '_fdb_lock left held after connect() failure')
        db.release()


class TestDbCloseHungLock(unittest.TestCase, TestDbBase):
    """close() must not block forever when a worker holds _fdb_lock."""

    def test_force_closes_conn_when_lock_held(self):
        """Lock held by worker → close() times out, force-closes conn, marks disconnected."""
        db = self.db()
        db.connect()
        conn = db._conn

        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.05):
                with self.assertLogs('lib.db', level='WARNING') as cm:
                    db.close()

            self.assertIsNotNone(conn.close_kwargs, '_conn.close() must be called even without the lock')
            self.assertIsNone(db._conn)
            self.assertFalse(db.connected())
            self.assertTrue(any('force-closing' in msg for msg in cm.output))
            # (b): an early "still running" warning must precede the final
            # "force-closing" one - visible proof the timeout is about to
            # strike, not just a post-hoc note that it already did.
            self.assertTrue(any('still running' in msg and 'close()' in msg for msg in cm.output))
        finally:
            release.set()
            t.join(timeout=1)
        self.assertFalse(t.is_alive())

    def test_does_not_release_unacquired_lock(self):
        """close() must not call release() when it never got the lock (would RuntimeError)."""
        db = self.db()
        db.connect()

        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.05):
                with self.assertLogs('lib.db', level='WARNING'):
                    db.close()  # would raise RuntimeError if it tried release() on unowned lock
        finally:
            release.set()
            t.join(timeout=1)

    def test_normal_path_releases_lock(self):
        """When no contention, lock is acquired and released cleanly."""
        db = self.db()
        db.connect()
        db.close()
        # lock must be free so a subsequent acquire succeeds immediately
        self.assertTrue(db.lock(0), '_fdb_lock not released after normal close()')
        db.release()


class TestDbConnectionSelfHealing(unittest.TestCase, TestDbBase):
    """commit()/rollback() reset connection state on failure instead of
    leaving a corrupted connection object for the next caller to inherit.

    A failed commit/rollback (e.g. the underlying driver tore its own
    socket down after a protocol error or a client-side timeout) must not
    leave self._connected/self._conn untouched - the next thing to touch
    the connection (verify()'s probe, the next dump item, an unrelated
    later call) would otherwise inherit the same broken connection object
    and fail with a confusing, unrelated-looking error (pymysql leaves
    attributes like _sock/_rfile as None, so callers see AttributeError
    instead of a clear "not connected").
    """

    def test_commit_failure_resets_connection_state(self):
        db = self.db()
        db.connect()
        conn = db._conn
        conn.commit = lambda **kw: (_ for _ in ()).throw(Exception('simulated dead connection'))

        with self.assertRaisesRegex(Exception, 'simulated dead connection'):
            db.commit()

        self.assertIsNone(db._conn)
        self.assertFalse(db.connected())
        self.assertIsNotNone(conn.close_kwargs, 'the dead connection object must still be closed')

    def test_rollback_failure_resets_connection_state(self):
        db = self.db()
        db.connect()
        conn = db._conn
        conn.rollback = lambda **kw: (_ for _ in ()).throw(Exception('simulated dead connection'))

        with self.assertRaisesRegex(Exception, 'simulated dead connection'):
            db.rollback()

        self.assertIsNone(db._conn)
        self.assertFalse(db.connected())
        self.assertIsNotNone(conn.close_kwargs)

    def test_commit_success_does_not_touch_connection_state(self):
        db = self.db()
        db.connect()
        db.commit()
        self.assertIsNotNone(db._conn)
        self.assertTrue(db.connected())

    def test_commit_failure_while_caller_holds_lock_does_not_deadlock(self):
        # _dump()/_compact_maxage()'s actual pattern: lock() ... commit()/
        # rollback() ... release(), all on the same thread. self._fdb_lock
        # is a plain, non-reentrant threading.Lock - if the failure path
        # inside commit()/rollback() tried to re-acquire it (e.g. by
        # routing through close()'s own lock() call), this would hang
        # forever instead of raising. Must complete promptly.
        db = self.db()
        db.connect()
        db._conn.commit = lambda **kw: (_ for _ in ()).throw(Exception('simulated dead connection'))

        self.assertTrue(db.lock())
        try:
            with self.assertRaisesRegex(Exception, 'simulated dead connection'):
                db.commit()
        finally:
            db.release()

        # lock must be genuinely free afterward - proves no self-deadlock occurred
        self.assertTrue(db.lock(0), '_fdb_lock not released after commit() failure under held lock')
        db.release()

    def test_rollback_failure_while_caller_holds_lock_does_not_deadlock(self):
        db = self.db()
        db.connect()
        db._conn.rollback = lambda **kw: (_ for _ in ()).throw(Exception('simulated dead connection'))

        self.assertTrue(db.lock())
        try:
            with self.assertRaisesRegex(Exception, 'simulated dead connection'):
                db.rollback()
        finally:
            db.release()

        self.assertTrue(db.lock(0), '_fdb_lock not released after rollback() failure under held lock')
        db.release()


class TestDbReadOnlyTransactionCleanup(unittest.TestCase, TestDbBase):
    """Reads must not leave an idle transaction open (autocommit is off,
    see __init__) - verify()'s probe and fetchone()/fetchall()'s cur=None
    path must close it after a successful read. Writes must be unaffected:
    execute()'s cur=None path never auto-closes anything (a write's caller
    owns its own commit), and an explicit cur (an outer caller already
    managing its own transaction, e.g. _dump()) must never trigger internal
    cleanup either.

    Must commit, not rollback, for that cleanup: self._fdb_lock serializes
    every caller, so any other write still pending on the same connection
    already finished its own critical section before this read could
    acquire the lock. A rollback here would silently destroy not-yet-
    committed writes made via the same cur=None convenience path (e.g.
    insertLog()'s own cur=None default, which never self-commits) the
    moment an unrelated later cur=None read ran. The mock harness here
    can't model pending transactional state, only which method got called
    - plugins/database's real (sqlite3) test suite covers that.
    """

    def test_verify_commits_after_successful_probe(self):
        db = self.db()
        db.connect()
        db.verify()
        self.assertIsNotNone(db._conn.commit_kwargs, "verify()'s probe must close its own transaction")
        self.assertIsNone(db._conn.rollback_kwargs, 'must commit, not roll back - see class docstring')

    def test_verify_probe_commit_failure_does_not_fail_verify(self):
        db = self.db()
        db.connect()
        db._conn.commit = lambda **kw: (_ for _ in ()).throw(Exception('simulated commit failure'))
        # must not raise - connectivity was already confirmed by the probe
        result = db.verify()
        self.assertEqual(-1, result)

    def test_fetchall_cur_none_commits_after_success(self):
        db = self.db()
        db.connect()
        db.fetchall('SELECT 1')
        self.assertIsNotNone(db._conn.commit_kwargs, 'fetchall() with cur=None must close its own read transaction')
        self.assertIsNone(db._conn.rollback_kwargs, 'must commit, not roll back - see class docstring')

    def test_fetchone_cur_none_commits_after_success(self):
        db = self.db()
        db.connect()
        db.fetchone('SELECT 1')
        self.assertIsNotNone(db._conn.commit_kwargs, 'fetchone() with cur=None must close its own read transaction')
        self.assertIsNone(db._conn.rollback_kwargs, 'must commit, not roll back - see class docstring')

    def test_fetchall_explicit_cur_does_not_auto_cleanup(self):
        # An explicit cur means the caller (e.g. _dump()) is managing its
        # own transaction across multiple statements - internal cleanup
        # here would corrupt whatever the outer caller is building up.
        db = self.db()
        db.connect()
        cur = db.cursor()
        db.fetchall('SELECT 1', cur=cur)
        self.assertIsNone(db._conn.commit_kwargs)
        self.assertIsNone(db._conn.rollback_kwargs)

    def test_execute_cur_none_does_not_auto_cleanup(self):
        # A write's caller owns its own commit - execute()'s cur=None path
        # must never auto-commit or auto-rollback on its own.
        db = self.db()
        db.connect()
        db.execute('INSERT INTO x VALUES (1)')
        self.assertIsNone(db._conn.commit_kwargs)
        self.assertIsNone(db._conn.rollback_kwargs)

    def test_readonly_commit_failure_does_not_mask_successful_read_result(self):
        db = self.db()
        db.connect()
        db._conn.commit = lambda **kw: (_ for _ in ()).throw(Exception('simulated commit failure'))
        with self.assertLogs('lib.db', level='WARNING'):
            result = db.fetchall('SELECT 1')
        self.assertEqual([[0]], result, 'a cleanup-only failure must not turn a successful read into an error')

    def test_uncommitted_cur_none_write_survives_a_later_cur_none_read(self):
        # insertLog()'s cur=None default never self-commits
        # (plugins/database/__init__.py) - a later, unrelated cur=None read
        # must not roll that write back via this exact code path. Simulate
        # the same shape here: write, then read, then confirm the write's
        # own commit()/rollback state was never touched by the read's
        # cleanup.
        db = self.db()
        db.connect()
        db.execute('INSERT INTO x VALUES (1)')  # cur=None, not yet committed by caller
        self.assertIsNone(db._conn.commit_kwargs, 'sanity: write must not have self-committed')
        db.fetchall('SELECT 1')  # unrelated later read on the same connection
        self.assertIsNotNone(
            db._conn.commit_kwargs, "the read's cleanup must commit (preserving the pending write), not roll it back"
        )
        self.assertIsNone(db._conn.rollback_kwargs, 'the pending write must never be rolled back by an unrelated read')


class TestDbTransaction(unittest.TestCase, TestDbBase):
    """transaction() - the multi-statement primitive. Commits on clean
    exit, rolls back on any exception, always releases the lock, and its
    non-reentrancy is enforced by lock() itself (see TestDbTests'
    reentrancy tests) rather than tested again here in duplicate.
    """

    def test_happy_path_commits_and_releases(self):
        db = self.db()
        db.connect()
        with db.transaction() as cur:
            cur.execute('INSERT INTO x VALUES (1)')
        self.assertIsNotNone(db._conn.commit_kwargs)
        self.assertIsNone(db._conn.rollback_kwargs)
        self.assertIsNotNone(db._conn.cursor_return.close_kwargs, 'cursor must be closed')
        self.assertTrue(db.lock(0), '_fdb_lock not released after a successful transaction()')
        db.release()

    def test_yields_a_usable_cursor(self):
        db = self.db()
        db.connect()
        with db.transaction() as cur:
            cur.execute('SELECT 1')
        self.assertEqual(('SELECT 1',), db._conn.cursor_return.execute_kwargs[0])

    def test_exception_rolls_back_closes_cursor_releases_lock_and_reraises(self):
        db = self.db()
        db.connect()
        with self.assertRaisesRegex(RuntimeError, 'simulated statement failure'):
            with db.transaction() as cur:
                cur.execute('INSERT INTO x VALUES (1)')
                raise RuntimeError('simulated statement failure')
        self.assertIsNotNone(db._conn.rollback_kwargs)
        self.assertIsNone(db._conn.commit_kwargs)
        self.assertIsNotNone(db._conn.cursor_return.close_kwargs)
        self.assertTrue(db.lock(0), '_fdb_lock not released after an exception in transaction()')
        db.release()

    def test_rollback_failure_does_not_mask_original_exception(self):
        db = self.db()
        db.connect()
        db._conn.rollback = lambda **kw: (_ for _ in ()).throw(Exception('simulated rollback failure'))
        with self.assertLogs('lib.db', level='WARNING') as cm:
            with self.assertRaisesRegex(RuntimeError, 'original statement failure'):
                with db.transaction() as cur:
                    cur.execute('INSERT INTO x VALUES (1)')
                    raise RuntimeError('original statement failure')
        self.assertTrue(any('rollback after failed transaction() also failed' in msg for msg in cm.output))
        # rollback()'s own self-healing reset must still fire here, even
        # though this transaction()'s own rollback attempt failed
        self.assertFalse(db.connected(), 'connection state must be reset even when rollback() itself fails')

    def test_commit_failure_propagates_and_still_releases_lock(self):
        db = self.db()
        db.connect()
        db._conn.commit = lambda **kw: (_ for _ in ()).throw(Exception('simulated commit failure'))
        with self.assertRaisesRegex(Exception, 'simulated commit failure'):
            with db.transaction() as cur:
                cur.execute('INSERT INTO x VALUES (1)')
        # commit()'s own self-healing already reset state - transaction()
        # must not double-handle this as a rollback case
        self.assertIsNone(db._conn, 'commit() failure must have reset self._conn via its own self-healing')
        self.assertTrue(db.lock(0), '_fdb_lock not released after a commit() failure')
        db.release()

    def test_lock_timeout_raises_promptly_on_cross_thread_contention(self):
        db = self.db()
        db.connect()
        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.05):
                with self.assertRaisesRegex(TimeoutError, 'could not acquire lock'):
                    with db.transaction():
                        pass  # never reached
        finally:
            release.set()
            t.join(timeout=1)

    def test_logs_early_watchdog_warning_while_waiting_for_lock(self):
        db = self.db()
        db.connect()
        release, t = self._hold_lock_in_thread(db)
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.1):
                with self.assertLogs('lib.db', level='WARNING') as cm:
                    with self.assertRaises(TimeoutError):
                        with db.transaction():
                            pass
            self.assertTrue(any('still running' in msg and 'transaction()' in msg for msg in cm.output))
        finally:
            release.set()
            t.join(timeout=1)

    def test_not_connected_raises_connection_error_and_releases_lock(self):
        db = self.db()  # never connected - db._conn is None
        with self.assertRaisesRegex(ConnectionError, 'not connected'):
            with db.transaction():
                pass
        self.assertTrue(db.lock(0), '_fdb_lock not released when not connected')
        db.release()

    def test_nesting_raises_immediately_not_a_timeout(self):
        db = self.db()
        db.connect()
        start = time.monotonic()
        with patch('lib.db._sh_db_query_timeout', return_value=5):  # would hang 5s if this were a timeout, not a raise
            with self.assertRaisesRegex(RuntimeError, r'lock\(\) called re-entrantly'):
                with db.transaction():
                    with db.transaction():
                        pass
        self.assertLess(time.monotonic() - start, 1, 'nesting must fail immediately, not wait out the lock timeout')

    def test_cur_none_call_from_inside_block_raises_immediately_not_a_timeout(self):
        db = self.db()
        db.connect()
        start = time.monotonic()
        with patch('lib.db._sh_db_query_timeout', return_value=5):
            with self.assertRaisesRegex(RuntimeError, r'lock\(\) called re-entrantly'):
                with db.transaction():
                    db.fetchall('SELECT 1')  # cur=None convenience path - locks internally too
        self.assertLess(time.monotonic() - start, 1)


class TestDbPymysqlTimeouts(unittest.TestCase, TestDbBase):
    """pymysql-family drivers receive socket timeout defaults via setdefault."""

    def _pymysql_db(self, connect=''):
        return lib.db.Database('test', MockPymysqlApi('qmark'), connect, 'qmark')

    def test_read_and_write_timeout_injected(self):
        db = self._pymysql_db()
        self.assertIn('read_timeout', db._params)
        self.assertIn('write_timeout', db._params)
        self.assertIsInstance(db._params['read_timeout'], int)
        self.assertIsInstance(db._params['write_timeout'], int)

    def test_connect_timeout_fixed_at_10(self):
        db = self._pymysql_db()
        self.assertEqual(10, db._params['connect_timeout'])

    def test_user_read_timeout_not_overridden(self):
        db = self._pymysql_db(connect='read_timeout:120')
        self.assertEqual(120, db._params['read_timeout'])

    def test_user_write_timeout_not_overridden(self):
        db = self._pymysql_db(connect='write_timeout:90')
        self.assertEqual(90, db._params['write_timeout'])

    def test_user_connect_timeout_not_overridden(self):
        db = self._pymysql_db(connect='connect_timeout:5')
        self.assertEqual(5, db._params['connect_timeout'])

    def test_timeout_keys_coerced_to_int_from_string_config(self):
        # Keys in _numeric_connect_keys get int() coercion when the connect
        # param is a pipe-separated string (the common YAML config form).
        db = self._pymysql_db(connect='read_timeout:60 | write_timeout:60')
        self.assertIsInstance(db._params['read_timeout'], int)
        self.assertIsInstance(db._params['write_timeout'], int)

    def test_sqlite_busy_timeout_coerced_to_int_from_string_config(self):
        # 'timeout' (sqlite3.connect()'s busy-timeout kwarg) is coerced the
        # same way - without it in _numeric_connect_keys, string connect
        # config produced sqlite3.connect(timeout='30'), a TypeError against
        # the real driver.
        db = self.db(connect='timeout:30')
        self.assertIsInstance(db._params['timeout'], int)
        self.assertEqual(30, db._params['timeout'])

    def test_non_pymysql_driver_not_affected(self):
        db = self.db()  # MockDbApi has no __name__ → empty string → not in _pymysql_driver_names
        self.assertNotIn('read_timeout', db._params)
        self.assertNotIn('write_timeout', db._params)
        self.assertNotIn('connect_timeout', db._params)

    def test_read_timeout_reflects_sh_config(self):
        """Injected default tracks whatever _sh_db_query_timeout() returns."""
        with patch('lib.db._sh_db_query_timeout', return_value=99):
            db = self._pymysql_db()
        self.assertEqual(99, db._params['read_timeout'])
        self.assertEqual(99, db._params['write_timeout'])

    def test_mysql_connector_gets_no_pymysql_timeout_kwargs(self):
        # mysql.connector rejects unknown connect() kwargs and does not
        # accept read_timeout/write_timeout (its own knob is
        # connection_timeout) - injecting pymysql-style timeouts would make
        # every mysql.connector connect() fail outright.
        api = MockPymysqlApi('pyformat')
        api.__name__ = 'mysql.connector'
        db = lib.db.Database('test', api, '', 'pyformat')
        self.assertNotIn('read_timeout', db._params)
        self.assertNotIn('write_timeout', db._params)
        self.assertNotIn('connect_timeout', db._params)


class TestDbStringDriverImport(unittest.TestCase, TestDbBase):
    """String-driver-name resolution in __init__ (the 'driver: pymysql' style config)."""

    def test_dotted_driver_name_resolves_to_the_submodule_not_the_top_package(self):
        # __import__('mysql.connector') returns the top-level 'mysql'
        # package, not the 'mysql.connector' submodule - it has no
        # paramstyle and its __name__ ('mysql') never matches
        # _pymysql_driver_names ('mysql.connector'), so that driver string
        # would never work. importlib.import_module resolves the dotted
        # name correctly.
        fake_submodule = MockPymysqlApi('pyformat')
        fake_submodule.__name__ = 'mysql.connector'
        real_import_module = importlib.import_module

        def fake_import(name, *a, **kw):
            if name == 'mysql.connector':
                return fake_submodule
            return real_import_module(name, *a, **kw)  # anything else (e.g. stdlib lazy imports) passes through

        with patch('importlib.import_module', side_effect=fake_import) as mock_import:
            db = lib.db.Database('test', 'mysql.connector', '', 'pyformat')
        mock_import.assert_any_call('mysql.connector')
        self.assertEqual('mysql.connector', db._dbapi.__name__)
        self.assertTrue(db.api_initialized)

    def test_single_component_driver_name_still_resolves(self):
        # importlib.import_module and __import__ are equivalent for a
        # plain (non-dotted) name - confirms the switch didn't change
        # behaviour for the drivers that already worked (real sqlite3
        # import here, not mocked - it's always available).
        db = lib.db.Database('test', 'sqlite3', ':memory:', 'qmark')
        self.assertEqual('sqlite3', db._dbapi.__name__)
        self.assertTrue(db.api_initialized)


class TestDbVersion(unittest.TestCase, TestDbBase):
    """version() returns the engine's version string, cached until the
    connection is torn down and reconnected."""

    def test_sqlite_uses_real_sqlite_version(self):
        db = lib.db.Database('version_test', 'sqlite3', {'database': ':memory:'}, 'qmark')
        db.connect()
        self.assertEqual(sqlite3.sqlite_version, db.version())

    def test_mysql_family_driver_queries_select_version(self):
        db = lib.db.Database('test', MockPymysqlApi('qmark'), '', 'qmark')
        db.connect()

        sent = []
        orig_execute = db.execute

        def spy_execute(stmt, *a, **kw):
            sent.append(stmt)
            return orig_execute(stmt, *a, **kw)

        db.execute = spy_execute
        db.version()
        self.assertIn('SELECT VERSION()', sent)

    def test_cached_after_first_successful_lookup(self):
        db = self.db()
        db.connect()

        calls = []
        orig_fetchone = db.fetchone

        def spy_fetchone(*a, **kw):
            calls.append(1)
            return orig_fetchone(*a, **kw)

        db.fetchone = spy_fetchone
        first = db.version()
        second = db.version()

        self.assertEqual(first, second)
        self.assertEqual(1, len(calls), 'second call must use the cache, not re-query')

    def test_cache_invalidated_on_reconnect(self):
        db = self.db()
        db.connect()
        self.assertIsNotNone(db.version())

        db.close()
        db.connect()

        calls = []
        orig_fetchone = db.fetchone

        def spy_fetchone(*a, **kw):
            calls.append(1)
            return orig_fetchone(*a, **kw)

        db.fetchone = spy_fetchone
        db.version()
        self.assertEqual(1, len(calls), 'reconnect must clear the cache and force a fresh lookup')

    def test_failure_returns_none_and_logs_once(self):
        db = self.db()
        db.connect()
        db.fetchone = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('simulated failure'))

        with self.assertLogs('lib.db', level='INFO') as cm:
            result = db.version()

        self.assertIsNone(result)
        self.assertEqual(1, len(cm.output))
        self.assertIn('version lookup failed', cm.output[0])

    def test_failure_not_cached_retries_next_call(self):
        db = self.db()
        db.connect()

        calls = []
        orig_fetchone = db.fetchone

        def failing_once(*a, **kw):
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError('simulated transient failure')
            return orig_fetchone(*a, **kw)

        db.fetchone = failing_once
        self.assertIsNone(db.version())
        self.assertIsNotNone(db.version())
        self.assertEqual(2, len(calls), 'a failed lookup must not be cached')


class TestShDbQueryTimeout(unittest.TestCase):
    """_sh_db_query_timeout() reads sh._db_query_timeout and falls back safely."""

    def _call_with_sh(self, sh_instance):
        """Inject a fake lib.smarthome into sys.modules for one call."""
        import sys

        class _FakeSmartHome:
            @staticmethod
            def get_instance():
                return sh_instance

        fake_module = type(sys)('lib.smarthome')
        fake_module.SmartHome = _FakeSmartHome
        with patch.dict(sys.modules, {'lib.smarthome': fake_module}):
            return lib.db._sh_db_query_timeout()

    def test_returns_default_when_no_instance(self):
        result = self._call_with_sh(None)
        self.assertEqual(lib.db._DB_QUERY_TIMEOUT_DEFAULT, result)

    def test_reads_attribute_from_sh(self):
        class _Sh:
            _db_query_timeout = 60

        result = self._call_with_sh(_Sh())
        self.assertEqual(60, result)

    def test_returns_default_when_attribute_absent(self):
        result = self._call_with_sh(object())  # plain object, no _db_query_timeout
        self.assertEqual(lib.db._DB_QUERY_TIMEOUT_DEFAULT, result)

    def test_returns_default_when_import_fails(self):
        # Simulates early-startup or test environment where lib.smarthome can't load.
        import sys

        with patch.dict(sys.modules, {'lib.smarthome': None}):
            result = lib.db._sh_db_query_timeout()
        self.assertEqual(lib.db._DB_QUERY_TIMEOUT_DEFAULT, result)


if __name__ == '__main__':
    unittest.main(verbosity=2)
