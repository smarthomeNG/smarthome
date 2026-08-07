from . import common
import unittest
import sqlite3
import threading
import logging
import time
from unittest.mock import patch
import lib.db


class TestDbBase:
    def api(self, paramstyle='qmark'):
        return MockDbApi(paramstyle)

    def db(self, connect='', paramstyle='qmark', format_input='qmark'):
        return lib.db.Database('test', self.api(paramstyle=paramstyle), connect, format_input)


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
        # Every connect value used to be guessed via int/float/str fallback
        # typing, so a numeric-looking value for ANY key (e.g. a numeric
        # password) silently became an int. 'port' genuinely needs to be an
        # int for drivers like pymysql; everything else must stay the exact
        # string from config.
        db = self.db(connect='passwd:123456 | port:3306 | host:myhost')
        self.assertEqual('123456', db._params['passwd'])
        self.assertEqual(3306, db._params['port'])
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
        db = self.db()
        db.lock()
        self.assertFalse(db.lock(0))

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
        db = self.db()
        db.connect()
        db.setup({1: ['ROLLOUT 1', 'ROLLBACK 1'], 2: ['ROLLOUT 2', 'ROLLBACK 2']})

        # Statement 0: SELECT version - ignore
        # Statement 1: Rollout statment 1 - check:
        self.assertEqual('ROLLOUT 1', db._conn.cursor_return.execute_kwargs[1][0])
        # Statement 2: INSERT version - ignore
        # Statement 3: Rollout statment 2 - check:
        self.assertEqual('ROLLOUT 2', db._conn.cursor_return.execute_kwargs[3][0])
        # Statement 4: INSERT version - check
        self.assertEqual('INSERT INTO test_version', db._conn.cursor_return.execute_kwargs[4][0][0:24])
        self.assertEqual(2, db._conn.cursor_return.execute_kwargs[4][1][0])

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

    # -- reconnect-on-stale-connection (cur=None path) -----------------------
    #
    # execute()/fetchone()/fetchall() manage their own cursor when called
    # with cur=None - this is the path store.py's ItemStore/LogStore CRUD
    # layer always uses, and it never calls verify() itself. A connection
    # that goes stale between calls (network blip, server-side disconnect)
    # used to wedge every subsequent cur=None call identically until
    # something unrelated called verify() or the process restarted - see
    # plugins/database's "Lost connection to MySQL server during query" /
    # "read of closed file" incident. These tests cover the fix directly on
    # lib.db.Database rather than through the plugin.

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

    def test_fetchall_not_connected_returns_empty_without_reconnect_attempt(self):
        # never connected at all - must preserve today's behaviour exactly
        # (empty result, no attempted reconnect / no connection storm).
        # Initial connect() throttling is _initialize_db()'s job, not this
        # retry's.
        db = self.db()
        self.assertEqual([], db.fetchall('SELECT 1'))
        self.assertIsNone(db._conn)

    def test_cursor_op_lock_wait_tracks_configured_timeout_not_hardcoded_300(self):
        # Regression: _cursor_op_with_reconnect used to call self.lock(300),
        # a value hardcoded independent of db_query_timeout - meaning a
        # hung server could stall this specific path (the cur=None path
        # store.py's ItemStore/LogStore always use) for up to 5 minutes
        # regardless of what the user configured. Prove the lock wait now
        # actually respects the configured value by holding the lock in a
        # background thread and using a tiny configured timeout.
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


class MockDbApi:
    def __init__(self, paramstyle):
        self.paramstyle = paramstyle
        self.connected_kwargs = None

    def connect(self, **kwargs):
        self.connect_kwargs = kwargs if kwargs is not None else True
        return MockDbApiConnection()


class MockPymysqlApi(MockDbApi):
    __name__ = 'pymysql'


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
        db = self.db()
        db.lock()
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.05):
                with self.assertRaises(TimeoutError):
                    db.connect()
        finally:
            db.release()

    def test_logs_early_watchdog_warning_before_timeout(self):
        # The watchdog should warn partway through the wait (b), not just
        # after it - so a wedged connect() is visible in the log before it
        # eventually raises, not only in the final error line.
        db = self.db()
        db.lock()
        try:
            with patch('lib.db._sh_db_query_timeout', return_value=0.1):
                with self.assertLogs('lib.db', level='WARNING') as cm:
                    with self.assertRaises(TimeoutError):
                        db.connect()
            self.assertTrue(any('still running' in msg and 'connect()' in msg for msg in cm.output))
        finally:
            db.release()

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

    def _hold_lock_in_thread(self, db):
        """Acquire the lock in a daemon thread; return (release_event, thread)."""
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

    Regression context: a failed commit/rollback (e.g. the underlying
    driver tore its own socket down after a protocol error or a client-side
    timeout) used to leave self._connected/self._conn untouched. The next
    thing to touch the connection - verify()'s probe, the next dump item,
    an unrelated later call - would inherit the same broken connection
    object and fail with a confusing, unrelated-looking error (pymysql
    leaves attributes like _sock/_rfile as None, so callers see
    AttributeError instead of a clear "not connected").
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
    path must roll back after a successful read. Writes must be unaffected:
    execute()'s cur=None path never auto-rolls-back (a write's caller owns
    its own commit), and an explicit cur (an outer caller already managing
    its own transaction, e.g. _dump()) must never trigger an internal
    rollback either.
    """

    def test_verify_rolls_back_after_successful_probe(self):
        db = self.db()
        db.connect()
        db.verify()
        self.assertIsNotNone(db._conn.rollback_kwargs, "verify()'s probe must roll back its own transaction")

    def test_verify_probe_rollback_failure_does_not_fail_verify(self):
        db = self.db()
        db.connect()
        db._conn.rollback = lambda **kw: (_ for _ in ()).throw(Exception('simulated rollback failure'))
        # must not raise - connectivity was already confirmed by the probe
        result = db.verify()
        self.assertEqual(-1, result)

    def test_fetchall_cur_none_rolls_back_after_success(self):
        db = self.db()
        db.connect()
        db.fetchall('SELECT 1')
        self.assertIsNotNone(db._conn.rollback_kwargs, 'fetchall() with cur=None must close its own read transaction')

    def test_fetchone_cur_none_rolls_back_after_success(self):
        db = self.db()
        db.connect()
        db.fetchone('SELECT 1')
        self.assertIsNotNone(db._conn.rollback_kwargs, 'fetchone() with cur=None must close its own read transaction')

    def test_fetchall_explicit_cur_does_not_auto_rollback(self):
        # An explicit cur means the caller (e.g. _dump()) is managing its
        # own transaction across multiple statements - an internal rollback
        # here would corrupt whatever the outer caller is building up.
        db = self.db()
        db.connect()
        cur = db.cursor()
        db.fetchall('SELECT 1', cur=cur)
        self.assertIsNone(db._conn.rollback_kwargs)

    def test_execute_cur_none_does_not_auto_rollback(self):
        # A write's caller owns its own commit - execute()'s cur=None path
        # must never auto-rollback, or a write would be silently discarded.
        db = self.db()
        db.connect()
        db.execute('INSERT INTO x VALUES (1)')
        self.assertIsNone(db._conn.rollback_kwargs)

    def test_readonly_rollback_failure_does_not_mask_successful_read_result(self):
        db = self.db()
        db.connect()
        db._conn.rollback = lambda **kw: (_ for _ in ()).throw(Exception('simulated rollback failure'))
        with self.assertLogs('lib.db', level='WARNING'):
            result = db.fetchall('SELECT 1')
        self.assertEqual([[0]], result, 'a cleanup-only failure must not turn a successful read into an error')


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
