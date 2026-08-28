#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-     Oliver Hinckel                   github@ollisnet.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import datetime
import time
import threading
import collections
import re
import contextlib
import importlib

from typing import OrderedDict

from lib.shtime import Shtime

_DB_QUERY_TIMEOUT_DEFAULT = 60


def _sh_db_query_timeout() -> int:
    """Return db_query_timeout from the running SmartHomeNG instance.

    Falls back to _DB_QUERY_TIMEOUT_DEFAULT when called before SmartHomeNG
    is initialised (tests, early startup) or when the config key is absent.
    Lazy import avoids a circular dependency (lib.smarthome -> many libs,
    but none of them import lib.db at module level).
    """
    try:
        from lib.smarthome import SmartHome

        sh = SmartHome.get_instance()
        if sh is not None:
            return int(getattr(sh, '_db_query_timeout', _DB_QUERY_TIMEOUT_DEFAULT))
    except Exception:
        pass
    return _DB_QUERY_TIMEOUT_DEFAULT


@contextlib.contextmanager
def _hang_watchdog(logger, name, label, timeout):
    """Log a single WARNING partway through a bounded wait if it's still
    running, so a genuinely wedged connection is visible in the log before
    (not just after) the eventual timeout/error fires.

    Not shutdown-specific - wraps any bounded wait in this module, including
    live query execution while SmartHomeNG is running normally. A blocked
    worker thread doesn't hold the GIL (it's parked in a socket read), so
    this timer thread runs and logs regardless of what the blocked thread
    is doing.

    Fires once, at half of *timeout*. Cancelled harmlessly if the
    operation finishes first - the normal/fast path never logs anything.
    """
    warn_after = timeout / 2

    def _warn():
        logger.warning(
            'Database [{}]: {} still running after {:.0f}s - will give up in ~{:.0f}s if unresponsive'.format(
                name, label, warn_after, max(timeout - warn_after, 0)
            )
        )

    timer = threading.Timer(warn_after, _warn)
    timer.daemon = True
    timer.start()
    try:
        yield
    finally:
        timer.cancel()


class Database:
    """A database abstraction layer based on DB-API2 specification.

    It provides basic functionality to access databases using Python driver
    implementations based on the DB-API2 specification (PEP 249).

    The following methods are provided:
    '__init__()' - create a new database object
    'connect()' - establish the connection to the database
    'close()' - close the connection to the database
    'setup()' - check/update/upgrade database structure
    'execute()' - execute statement (no result returned)
    'fetchone()' - execute statement and return first row from result
    'fetchall()' - execute statement and reeturn all rows from result
    'cursor()' - create a cursor object to execute multiple statements
    'commit()' - commit a transaction (if the selcted database supports it)
    'rollback()' - rollback a transaction (if the selcted database supports it)
    'lock()' - acquire the database lock (prevent simultaneous reads/writes)
    'release()' - release the database lock
    'transaction()' - context manager: run several statements as one
        commit/rollback unit, using lock()/release() internally
    'verify()' - check database connection and reconnect if required
    'connected()' - check if database is connected


    The SQL statements executed may have placeholders and parameters which
    are passed to the execution methods listed above. The following DB-API
    driver implementations are supported:
    - qmark: Specify placeholders as "?" and parameters as list
    - format: Specify placeholders as "%s" and parameters as list
    - numeric: Specify placeholders as ":1" and parameters as list
    - named: Specify placeholders as ":name" and parameters as dict
    - pyformat: Specify placeholders as "%(arg)s" and parameters as dict

    Further you can choose a different formatting style in your code when
    using this class. Specify one of the formatting listed above or use
    the default - which is named.

    In case the driver implementation uses a different formatting it
    will be converted transparently!
    """

    # Supported formatting styles
    _styles = ('qmark', 'format', 'numeric', 'named', 'pyformat')

    # Supported formatting translations:
    # - input_token: The token in source query to replace with output token
    # - output_token: The token to use in output query
    # - input_name: The name of parameter lookup in input parameter list
    # - output_name: The name of parameter to put in output parameter list
    # You can use placeholders in the output_token, input_name and output_name:
    # - {0}: Number of parameter (counting from 1 for first parameter)
    # - {1}: First match of input_token regex (use 2 for second, 3 for third, etc)
    _translations = {
        'qmark': {
            'qmark': {},
            'format': {'input_token': '?', 'output_token': '%s'},
            'numeric': {'input_token': '?', 'output_token': ':{0}'},
            'named': {'input_token': '?', 'output_token': ':arg{0}', 'output_name': 'arg{0}'},
            'pyformat': {'input_token': '?', 'output_token': '%(arg{0})s', 'output_name': 'arg{0}'},
        },
        'format': {
            'qmark': {'input_token': re.compile(r'%\w+'), 'output_token': '?'},
            'format': {},
            'numeric': {'input_token': re.compile(r'%\w+'), 'output_token': ':{0}'},
            'named': {'input_token': re.compile(r'%\w+'), 'output_token': ':arg{0}', 'output_name': 'arg{0}'},
            'pyformat': {'input_token': re.compile(r'%\w+'), 'output_token': '%(arg{0})s', 'output_name': 'arg{0}'},
        },
        'numeric': {
            'qmark': {'input_token': re.compile(r':(\d+)'), 'output_token': '?', 'input_name': '{1}'},
            'format': {'input_token': re.compile(r':(\d+)'), 'output_token': '%s', 'input_name': '{1}'},
            'numeric': {},
            'named': {
                'input_token': re.compile(r':(\d+)'),
                'output_token': ':arg{1}',
                'input_name': '{1}',
                'output_name': 'arg{1}',
            },
            'pyformat': {'input_token': re.compile(r':(\d+)'), 'output_token': '%(arg{1})s', 'output_name': 'arg{1}'},
        },
        'named': {
            'qmark': {'input_token': re.compile(r':(\w+)'), 'output_token': '?', 'input_name': '{1}'},
            'format': {'input_token': re.compile(r':(\w+)'), 'output_token': '%s', 'input_name': '{1}'},
            'numeric': {'input_token': re.compile(r':(\w+)'), 'output_token': ':{0}', 'input_name': '{1}'},
            'named': {},
            'pyformat': {
                'input_token': re.compile(r':(\w+)'),
                'output_token': '%({1})s',
                'input_name': '{1}',
                'output_name': '{1}',
            },
        },
        'pyformat': {
            'qmark': {'input_token': re.compile(r'%\((\w+)\)\w+'), 'output_token': '?', 'input_name': '{1}'},
            'format': {'input_token': re.compile(r'%\((\w+)\)\w+'), 'output_token': '%s', 'input_name': '{1}'},
            'numeric': {'input_token': re.compile(r'%\((\w+)\)\w+'), 'output_token': ':{0}', 'input_name': '{1}'},
            'named': {
                'input_token': re.compile(r'%\((\w+)\)\w+'),
                'output_token': ':{1}',
                'input_name': '{1}',
                'output_name': '{1}',
            },
            'pyformat': {},
        },
    }
    _translation_param_types = {'qmark': list, 'format': list, 'numeric': list, 'named': dict, 'pyformat': dict}

    # connect() kwargs whose values must be type int
    _numeric_connect_keys = {'port', 'connect_timeout', 'read_timeout', 'write_timeout', 'timeout'}

    # DB-API driver __name__ values that accept pymysql-style timeout kwargs
    # (connect_timeout/read_timeout/write_timeout). These are injected as
    # defaults in __init__ when not already in _params. mysql.connector is
    # deliberately absent: it rejects unknown connect() kwargs and uses
    # connection_timeout instead - its users set that in the connect config
    # themselves.
    _pymysql_driver_names = frozenset({'pymysql', 'MySQLdb'})

    # connect() kwargs whose values must be a real bool, not the literal
    # config string.
    _bool_connect_keys = {'check_same_thread'}

    def __init__(self, name, dbapi, connect, formatting='named'):
        """Create a new database instance

        The 'name' parameter identifies the name for the database access .
        It is also used internally to create versions table (to keep track
        if the database structure is up to date) and logging.

        Use the 'dbapi' parameter to specify the DB-API2 module of the
        database type to use (e.g. import the sqlite3 module and pass it
        directly as parameter or as name 'sqlite3').

        How the database is accessed is specified by the 'connect' parameter
        which supports key/value pairs specified as dict. These named
        parameters will be used as 'connect()' parameters of the DB-API driver
        implementation.

        The 'formatting' parameter can be used to specify a different type
        of formatting (see DB-API spec) which defaults to 'named'.
        """
        self.logger = logging.getLogger(__name__)
        self.shtime = Shtime.get_instance()

        # this should not happen in normal operations, but is needed for testing
        if self.shtime is None:
            self.shtime = Shtime(None)

        self._name = name
        self._dbapi = dbapi
        self._dbapi_name = dbapi
        self._format_input = formatting
        self._connected = False
        self._conn = None

        self.api_initialized = False

        # Set up-front, before any of the three failure paths below can
        # return early: lock()/release() are generic enough that cleanup
        # code (e.g. a defensive `finally: db.release()`) could reach them
        # on a half-built object without checking api_initialized first -
        # AttributeError on self._fdb_lock would be a confusing way to
        # discover that, versus lock() simply working (harmlessly) on an
        # object nothing else will use.
        self._fdb_lock = threading.Lock()
        self._fdb_lock_owner = None

        if type(dbapi) is str:
            try:
                # importlib.import_module, not __import__: for a dotted
                # name like 'mysql.connector', __import__ returns the
                # top-level 'mysql' package, not the submodule - it has
                # no paramstyle/no __name__ match in _pymysql_driver_names,
                # so that driver could never actually work.
                self._dbapi = importlib.import_module(dbapi)
            except ImportError as e:
                self.logger.error('DB-API import failed for "{}": {} - module installed?'.format(dbapi, e))
                return

        if self._format_input not in self._styles:
            self.logger.error(
                'Database [{}]: SQL format style {} not supported (only {})'.format(
                    self._name, self._format_input, self._styles
                )
            )
            return

        self._params = {}

        # Deprecated, remove with 1.7 or 1.8
        if type(connect) is str:
            connect = [p.strip() for p in connect.split('|')]

        # -> but keep list of ordered dict as "default" returned by yaml parser!
        if type(connect) is list:
            if isinstance(connect[0], str):
                for arg in connect:
                    key, sep, value = arg.partition(':')
                    if key in self._numeric_connect_keys:
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                    elif key in self._bool_connect_keys:
                        value = value.strip().lower() not in ('false', '0', 'no', '')
                    self._params[key] = value
            elif isinstance(connect[0], OrderedDict):
                # No str() coercion here (unlike the 'key:value' pipe-string
                # branch above, which genuinely starts with everything as
                # text) - shyaml.yaml_load(..., ordered=True) (used for the
                # real etc/plugin.yaml this comes from) already gives each
                # value its correct native YAML type (port: 3307 -> int,
                # check_same_thread: false -> bool). Blanket str()'ing here
                # was actively destroying that - e.g. pymysql.connect()
                # rejects a string port with "ValueError: port should be of
                # type int" (verified against a real pymysql connection).
                self._params = {k: v for item in connect for k, v in item.items()}

        elif type(connect) in [dict, collections.OrderedDict]:
            self._params = connect

        if getattr(self._dbapi, '__name__', '') == 'sqlite3' and 'check_same_thread' not in self._params:
            # sqlite3 defaults check_same_thread to True, rejecting
            # cross-thread use - but self._fdb_lock below already
            # serializes all access, and callers legitimately connect() on
            # one thread then use the connection from another. Only
            # applied as a default; an explicit check_same_thread in the
            # connect config always wins.
            self._params['check_same_thread'] = False

        if getattr(self._dbapi, '__name__', '') in self._pymysql_driver_names:
            # Without explicit timeouts pymysql blocks indefinitely on a
            # hung server, holding _fdb_lock and preventing shutdown.
            # connect_timeout covers the TCP handshake; read/write_timeout
            # cover query execution.  All three are user-overridable via the
            # connect config; db_query_timeout in smarthome.yaml sets the
            # read/write default (falls back to _DB_QUERY_TIMEOUT_DEFAULT).
            _qt = _sh_db_query_timeout()
            self._params.setdefault('connect_timeout', 10)
            self._params.setdefault('read_timeout', _qt)
            self._params.setdefault('write_timeout', _qt)

        self._format_output = self._dbapi.paramstyle
        if self._format_output not in self._styles:
            self.logger.error(
                'Database [{}]: DB-API driver format style {} not supported (only {})'.format(
                    self._name, self._format_output, self._styles
                )
            )
            return

        self._translation = self._translations[self._format_input][self._format_output]
        self._translation_param_type = self._translation_param_types[self._format_output]

        # PEP 249 connection-trouble classes for _cursor_op_with_reconnect's
        # error classification: only these justify the close/reconnect/retry
        # cycle. A driver exposing none of them (minimal test doubles) falls
        # back to retrying everything rather than retrying nothing -
        # is_connection_error() below uses the raw tuple instead, so that
        # fallback can't hide a real bug's log entry.
        classes = tuple(
            cls
            for cls in (getattr(self._dbapi, n, None) for n in ('InterfaceError', 'OperationalError', 'InternalError'))
            if isinstance(cls, type)
        )
        self._connection_error_classes = classes
        self._reconnect_exceptions = classes or (Exception,)

        self.api_initialized = True
        return

    def connect(self):
        """Connects to the database"""
        timeout = _sh_db_query_timeout()
        with _hang_watchdog(self.logger, self._name, 'connect() waiting for db lock', timeout):
            locked = self.lock(timeout=timeout)
        if not locked:
            raise TimeoutError(
                'Database [{}]: could not acquire lock within {}s in connect()'.format(self._name, timeout)
            )
        try:
            self._conn = self._dbapi.connect(**self._params)
        except Exception as e:
            self.logger.error(
                "Database [{}]: Could not connect to the database using '{}': {}".format(
                    self._name, self._dbapi_name, e
                )
            )
            raise
        finally:
            self.release()
        self._connected = True
        self.logger.info(
            'Database [{}]: Connected with {} using "{}" style'.format(self._name, self._conn, self._format_output)
        )

    def close(self):
        """Closes the database connection"""
        timeout = _sh_db_query_timeout()
        with _hang_watchdog(self.logger, self._name, 'close() waiting for db lock', timeout):
            acquired = self.lock(timeout=timeout)
        if not acquired:
            # A worker thread is holding the lock while blocked on a query
            # (e.g. waiting on a hung MySQL server).  We cannot wait forever
            # during shutdown, so close the underlying connection anyway.
            # The blocked thread will receive a broken-connection error,
            # exit its except branch, and release the lock in its finally
            # block.  _conn=None / _connected=False are written here so
            # anything the worker tries after recovering fails gracefully.
            self.logger.warning(
                'Database [{}]: could not acquire lock within {}s in close(); '
                'force-closing connection to unblock hung thread'.format(self._name, timeout)
            )
        try:
            self._reset_connection_locked()
        finally:
            if acquired:
                self.release()

    def _reset_connection_locked(self):
        """Discard the current connection and mark disconnected.

        Callers must already hold self._fdb_lock (or, for the commit()/
        rollback() failure path below, be the sole owner of a connection
        that's already provably broken) - this method never acquires the
        lock itself. commit()/rollback() are always called by code that
        already holds the lock via its own lock()...release() block (see
        _dump()/_compact_maxage() in the database plugin) - self._fdb_lock
        is a plain, non-reentrant threading.Lock, so routing the failure
        path through close()'s own lock() call here would deadlock a
        thread against itself.
        """
        try:
            if self._conn is not None:
                self._conn.close()
        except Exception:
            pass
        self._conn = None
        self._connected = False

    def connected(self):
        """Return the connected status"""
        return self._connected

    def is_connection_error(self, exc):
        """True if *exc* is a PEP 249 connection-trouble class for this driver.

        Uses the raw classes tuple, not _reconnect_exceptions' (Exception,)
        fallback - an unclassifiable driver must never downgrade an
        unrelated bug's log level just because it can't be classified.
        """
        return isinstance(exc, self._connection_error_classes)

    def setup(self, queries):
        """Setup or update the database structure.

        This method can be used to setup the database structure by providing
        the SQL statements to this method. Additionally it will check if the
        structure is already up to date by checking the data of the version
        table (which will also be created by this method if it does not exist
        already).

        To setup the database you need to specify the required SQL statements
        (e.g. 'CREATE TABLE', 'CREATE INDEX' etc.) in the 'queries' parameter.
        This will be a dictionary where the keys are simple version numbers
        and values are a two-item list for a rollout and rollback statement.

        E.g.::
           db.setup({1: ['CREATE TABLE xyz (...)', 'DROP TABLE xyz'], 2: [...]})

        For an extended example take a look into the 'database' plugin.

        Each version's rollout statement and its version-row bookkeeping
        commit as their own transaction(), not one commit for the whole
        migration - MySQL/MariaDB DDL (CREATE TABLE/ALTER TABLE/...)
        commits implicitly as a side effect regardless of any wrapping
        transaction, so a single end-of-loop commit couldn't make a
        multi-step migration atomic there anyway; on a crash between one
        step's DDL and its own version-row commit, only that one step
        needs to be figured out by hand on restart (the DDL re-running
        and failing with "already exists"), not the whole remaining
        migration. On sqlite, Python's sqlite3 module autocommits DDL
        anyway under its default (legacy) isolation handling - an implicit
        BEGIN is only issued before DML - so per-step commits match what
        actually happens there too; neither backend gets multi-step
        atomicity.
        """
        version_table = re.sub('[^a-z0-9_]', '', self._name.lower()) + '_version'
        with self.transaction() as cur:
            try:
                (version,) = self.fetchone('SELECT MAX(version) FROM ' + version_table + ';', cur=cur, quiet=True)
                if version is None:
                    version = 0
            except Exception:
                self.logger.info('Missing table ' + version_table + ' error can be ignored, will be created now!')
                self.execute(
                    'CREATE TABLE ' + version_table + '(version NUMERIC, updated BIGINT, rollout TEXT, rollback TEXT)',
                    cur=cur,
                )
                version = 0
        self.logger.info('Database [{}]: Version {} found'.format(self._name, version))
        # sort by numeric value, not string - version keys are strings (the
        # database plugin's _setup uses '1'..'8'), and plain sorted() would
        # put '10' before '2' once a caller reaches a double-digit version,
        # applying that step's DDL before earlier steps it may depend on.
        for v in sorted(queries.keys(), key=float):
            if float(v) > version:
                self.logger.info('Database [{}]: Upgrading to version {}'.format(self._name, v))
                with self.transaction() as cur:
                    self.execute(queries[v][0], cur=cur)

                    dt = self.shtime.utcnow()  # type: ignore (shtime is set dynamically)
                    ts = int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)
                    self.execute(
                        'INSERT INTO ' + version_table + '(version, updated, rollout, rollback) VALUES(?, ?, ?, ?);',
                        (v, ts, queries[v][0], queries[v][1]),
                        formatting='qmark',
                        cur=cur,
                    )

    def lock(self, timeout=-1):
        """Acquire a database lock

        Raises RuntimeError immediately - never waits out timeout - if the
        calling thread already holds this lock. self._fdb_lock is a plain,
        non-reentrant threading.Lock: without this check a same-thread
        re-entry would just block until timeout, indistinguishable from
        genuine cross-thread contention. This is what makes transaction()'s
        non-reentrancy hazard (see its docstring for what triggers it) fail
        loud and immediately instead of silently hanging.

        Tracks threading.current_thread() (the Thread object), not
        threading.get_ident() (a small OS-recyclable int) - an owner marker
        holding a live reference to the actual Thread object can't collide
        with an unrelated later thread the way a recycled ident could once
        the original owner had already exited without releasing.

        A stale read of the owner marker (benign: plain attribute read
        under the GIL, no separate synchronization) can only cause a false
        negative here - falling through to the real self._fdb_lock.acquire()
        call, which then behaves exactly as it did before this check
        existed. It can never falsely raise for a thread that doesn't
        actually hold the lock.
        """
        if self._fdb_lock_owner is threading.current_thread():
            raise RuntimeError(
                f'Database [{self._name}]: lock() called re-entrantly by the thread that already holds it - '
                "see transaction()'s docstring for the non-reentrancy hazard this guards against"
            )
        acquired = self._fdb_lock.acquire(timeout=timeout)
        if acquired:
            self._fdb_lock_owner = threading.current_thread()
        return acquired

    def release(self):
        """Release the database lock"""
        self._fdb_lock_owner = None
        self._fdb_lock.release()

    @contextlib.contextmanager
    def transaction(self, timeout=None):
        """Run a block of statements as one transaction.

        Acquires self._fdb_lock, yields a cursor for the caller to run
        multiple statements against, commits on clean exit, rolls back
        (best-effort) on any exception and re-raises it, always releases
        the lock. Use this instead of hand-rolling
        lock()/cursor()/commit()/rollback()/release() at each call site -
        a hand-rolled block that omits cleanup on failure leaves a
        corrupted connection for the next caller to inherit.

        Rolling back unconditionally on any exception is always safe here
        - no DB-API2 exception-class distinction needed. If the connection
        is genuinely dead, the rollback attempt itself fails, which
        triggers the existing self-healing reset in rollback() and
        re-raises - so this gets "reset on real connection failure" for
        free, without a fragile classification heuristic.

        Usage::

           with self._db.transaction() as cur:
               self._log_store.insert(item_id, entry, item_type, now_ms, cur=cur)

        IMPORTANT - non-reentrancy: self._fdb_lock is a plain,
        non-reentrant threading.Lock, held for the entire block. Two
        hazards follow from this, both enforced by lock() itself raising
        RuntimeError immediately on a same-thread re-entry (see lock())
        rather than deadlocking/timing out:

        - transaction() cannot be nested.
        - Any call from inside the block that acquires the lock
          internally - a cur=None execute()/fetchone()/fetchall() call, or
          connect()/close()/verify()/setup() - hits the same wall. Always
          pass the yielded cur through explicitly to statements run inside
          the block.

        :param timeout: Seconds to wait for the lock; defaults to the
                         configured db_query_timeout.
        """
        if timeout is None:
            timeout = _sh_db_query_timeout()

        with _hang_watchdog(self.logger, self._name, 'transaction() waiting for db lock', timeout):
            locked = self.lock(timeout=timeout)
        if not locked:
            raise TimeoutError(
                'Database [{}]: could not acquire lock within {}s in transaction()'.format(self._name, timeout)
            )

        cur = self.cursor()
        if cur is None:
            self.release()
            raise ConnectionError(f'Database [{self._name}]: not connected, cannot start transaction()')

        try:
            with _hang_watchdog(self.logger, self._name, 'transaction() block', timeout):
                yield cur
        except Exception as original_exc:
            try:
                cur.close()
            except Exception:
                pass
            try:
                self.rollback()
            except Exception as rollback_error:
                # Expected shape of a dead connection - only a rollback
                # failure after some *other* kind of original error is
                # actually surprising and worth a WARNING.
                level = self.logger.info if self.is_connection_error(original_exc) else self.logger.warning
                level(f'Database [{self._name}]: rollback after failed transaction() also failed: {rollback_error}')
            raise
        else:
            try:
                cur.close()
            except Exception:
                pass
            self.commit()
        finally:
            self.release()

    def commit(self):
        """Commit the current transaction"""
        try:
            self._conn.commit()
        except Exception:
            # A failed commit means the underlying connection is dead (the
            # driver already tore down its own socket/buffers internally -
            # this is what turns one query's failure into confusing,
            # unrelated-looking errors on whatever touches self._conn next:
            # pymysql leaves attributes like _sock/_rfile set to None, so a
            # later call fails with AttributeError instead of a clear
            # "not connected"). Reset state immediately so the next caller
            # (verify(), the next dump item, the next scheduled task) sees
            # connected() == False right away instead of inheriting a
            # corrupted connection object.
            self._reset_connection_locked()
            raise

    def rollback(self):
        """Rollback the current transaction"""
        try:
            self._conn.rollback()
        except Exception:
            self._reset_connection_locked()
            raise

    def cursor(self):
        """Create a new cursor for executing statements"""
        if self._conn is not None:
            return self._conn.cursor()

    def _cursor_op_with_reconnect(self, op, quiet=False, empty=None, error_prefix=None, readonly=False):
        """Run *op(cursor)* against a fresh cursor of our own (the ``cur is
        None`` case in execute()/fetchone()/fetchall()), retrying exactly
        once after a reconnect if the connection has gone stale.

        ``verify()`` is the dedicated, actively-called health check for a
        connection - but callers that go through the newer ItemStore/
        LogStore CRUD layer (store.py) always call execute()/fetchone()/
        fetchall() with ``cur=None`` and never call verify() themselves.
        Without this, a single dropped connection (network blip, MySQL
        restarting, "Lost connection to MySQL server during query") leaves
        ``self._conn`` in a broken-but-not-None state that nothing ever
        resets - every subsequent cur=None call fails identically until
        something unrelated happens to call verify() or the process
        restarts. This mirrors verify()'s own close-then-reconnect recovery,
        scoped to the one statement actually being run instead of a
        separate probe query.

        :param op:        Callable taking a cursor, returning the result.
        :param quiet:     Suppress the error-level log entry on final failure.
        :param empty:     Value to return if no cursor could be obtained at
                          all (mirrors execute()'s ``result = []`` /
                          fetchone()'s ``result = ''`` no-cursor fallbacks).
        :param error_prefix: Message prefix to log on final failure (the
                          final exception is appended); falls back to a
                          generic message if omitted.
        :param readonly:  If True, commit after a successful op() while
                          still holding the lock (see fetchone()/
                          fetchall()). On MySQL-family drivers autocommit
                          is off, so even a bare SELECT opens a real
                          transaction that would otherwise sit open
                          indefinitely, holding back InnoDB purge (on
                          sqlite3 a SELECT opens no transaction and this
                          commit is a no-op). Uses commit(), not rollback():
                          self._fdb_lock already serializes every caller, so
                          any write still pending on this connection already
                          finished its own critical section before this
                          read could acquire the lock - rollback() here
                          would destroy a not-yet-committed write still
                          pending on the shared connection instead of
                          completing it. execute() does not set this - a
                          write commits explicitly; this only closes out
                          what a read leaves behind.

        This path is exactly what ItemStore/LogStore always use with
        cur=None. It holds self._fdb_lock for the duration - concurrent
        threads (scheduler-driven maxage/orphan cleanup, live item writes,
        WebIf/logic reads) would otherwise hit the same self._conn/cursor
        with no serialization at all. Released again before close()/
        connect() run: both lock internally, and self._fdb_lock is a
        plain, non-reentrant Lock - holding it across those calls would
        deadlock.
        """
        last_error = None
        timeout = _sh_db_query_timeout()
        # Tracks db_query_timeout like every other bounded wait in this
        # file - a hardcoded value here would let a hung server stall this
        # path longer than the user configured elsewhere.
        label = error_prefix or f'Database [{self._name}]: query'
        for attempt in (1, 2):
            if self._conn is None:
                # Never connected, or a previous attempt already gave up
                # and closed us - not "stale", just not connected right
                # now. No reconnect storm here; that's _initialize_db()'s
                # throttled job. Only an existing-but-broken connection
                # gets retried.
                return empty

            with _hang_watchdog(self.logger, self._name, f'{label} - waiting for db lock', timeout):
                locked = self.lock(timeout)
            if not locked:
                last_error = TimeoutError(f'Database [{self._name}]: could not acquire lock within {timeout}s')
                break

            c = None
            retryable = True
            try:
                # sqlite3 raises immediately on .cursor() against an
                # already-closed connection; pymysql instead tends to
                # return a cursor that only fails on first use. Either way
                # it's the same "connection object present but unusable"
                # condition this retry exists for.
                c = self.cursor()
                with _hang_watchdog(self.logger, self._name, label, timeout):
                    result = op(c)
                c.close()
                if readonly:
                    # commit(), not rollback() - see the readonly= docstring
                    # above. Best-effort: a cleanup failure here shouldn't
                    # turn an already-successful read into an error for the
                    # caller.
                    try:
                        self.commit()
                    except Exception as e:
                        self.logger.warning(f'Database [{self._name}]: could not close read-only transaction: {e}')
                return result
            except Exception as e:
                last_error = e
                if c is not None:
                    try:
                        c.close()
                    except Exception:
                        pass
                    # Statement-level error on a live connection (c is None
                    # would mean cursor() itself failed - the connection
                    # object is unusable, always reconnect-worthy): only
                    # connection-trouble classes justify tearing down and
                    # retrying; anything else (IntegrityError, SQL typo)
                    # fails identically on retry and the teardown would
                    # needlessly discard the healthy connection.
                    retryable = isinstance(e, self._reconnect_exceptions)
            finally:
                self.release()

            if not retryable:
                break

            if attempt == 1:
                self.close()
                try:
                    self.connect()
                except Exception:
                    break
        if not quiet:
            prefix = error_prefix or f'Database [{self._name}]: query failed after reconnect attempt'
            # Same reasoning as execute()'s cur-provided branch below.
            level = self.logger.info if self.is_connection_error(last_error) else self.logger.error
            level(f'{prefix}: {last_error}')
        raise last_error

    def execute(self, stmt, params=(), formatting=None, cur=None, quiet=False):
        """Execute the given statement

        This will execute the statement specified in the 'stmt' parameter
        which may contain parameter placeholders (depending on selected
        formatting style given in constructor).

        The parameters can be specified in 'params' parameter as list or
        dict depending on selected formatting style.

        To overwrite the global formatting style given in constructor, the
        parameter 'formatting' can be used to change the style for the
        given statement.

        If already aqcuired a cursor you can use this cursor by using the
        'cur' parameter. If omitted a new cursor will be aqcuire for this
        statement and released afterwards.

        Set 'quiet' to True to suppress the error-level log entry for an
        expected failure (e.g. a first-run "table does not exist yet" probe).
        The exception is always raised regardless of 'quiet' - only the log
        entry is conditional.
        """
        try:
            stmt, args = self._prepare(stmt, params, formatting)
        except Exception as e:
            self.logger.error('Can not prepare query: {} (args {}): {}'.format(stmt, params, e))
            raise

        if cur is not None:
            try:
                return cur.execute(stmt, args)
            except Exception as e:
                if not quiet:
                    # Connection trouble is what transaction() exists to
                    # survive - ERROR would overstate it; the caller logs
                    # its own line if the failure matters to report.
                    level = self.logger.info if self.is_connection_error(e) else self.logger.error
                    level(f'Can not execute query: {stmt} (args {args}): {e}')
                raise

        return self._cursor_op_with_reconnect(
            lambda c: c.execute(stmt, args),
            quiet=quiet,
            empty=[],
            error_prefix=f'Can not execute query: {stmt} (args {args})',
        )

    def verify(self, retry=5, delay=5, probe_timeout=5):
        """Verifies the connection status and reconnets if required

        The connected status of the connection will be checked by executing
        a simple SQL statement. If this fails or the connection is not
        established already a new connection will be opened.

        In case the reconnect fails you can specify how many times a
        reconnect will be executed until it will give up. This can be
        specified by the 'retry' parameter.

        To specify the delay between retries use the `delay` parameter,
        which defaults to 5 seconds.

        Cost note: each attempt can cost up to `probe_timeout` (see
        below) even against a completely unresponsive server, and retry
        multiplies that. A caller whose own failure path already gets
        retried on its own cadence (e.g. a scheduled cycle) should still
        pass a low `retry` here rather than relying on this loop alone.

        probe_timeout (pymysql only, default 5s): a "SELECT 1" probe
        doesn't need the full db_query_timeout (60s default) a real query
        gets. Overrides pymysql's read_timeout/write_timeout for the
        duration of this call, then restores them (finally block below) -
        including on an already-open connection, since pymysql applies
        these fresh on every read/write rather than caching them at
        connect time. hasattr-guarded: read_timeout is not part of
        pymysql's public API and could be renamed in a future version, in
        which case this silently no-ops instead of raising. Scoped to the
        'pymysql' driver name, not the wider _pymysql_driver_names set -
        MySQLdb/mysql.connector may name this attribute differently.
        """
        is_pymysql = getattr(self._dbapi, '__name__', '') == 'pymysql'
        saved_read_timeout = self._params.get('read_timeout') if is_pymysql else None
        saved_write_timeout = self._params.get('write_timeout') if is_pymysql else None
        if is_pymysql:
            self._params['read_timeout'] = probe_timeout
            self._params['write_timeout'] = probe_timeout

        try:
            while retry > 0:
                locked = False

                try:
                    if not self.connected():
                        self.connect()
                    elif is_pymysql:
                        # Already-open connection: connect() won't run again
                        # this time round, so the live socket's timeout (set
                        # when it was originally opened) needs overriding
                        # directly - see probe_timeout note above.
                        if hasattr(self._conn, '_read_timeout'):
                            self._conn._read_timeout = probe_timeout
                        if hasattr(self._conn, '_write_timeout'):
                            self._conn._write_timeout = probe_timeout

                    locked = self.lock(2)

                    if locked:
                        # explicit cursor: fetchone(cur=None) now locks
                        # internally too (see _cursor_op_with_reconnect) - we
                        # already hold self._fdb_lock here, and it's a plain
                        # non-reentrant Lock, so a cur=None call from the same
                        # thread would deadlock against itself.
                        probe_cur = self.cursor()
                        self.fetchone('SELECT 1', cur=probe_cur)
                        probe_cur.close()
                        try:
                            # On MySQL-family drivers autocommit is off - the
                            # probe above opened a real transaction that would
                            # otherwise sit idle indefinitely between verify()
                            # calls, holding back InnoDB purge (no-op on
                            # sqlite3, where a SELECT opens no transaction).
                            # commit(), not rollback() - see
                            # _cursor_op_with_reconnect's readonly= docstring:
                            # self._fdb_lock already serializes every caller, so
                            # rollback() here could silently discard an
                            # unrelated write still pending on this connection
                            # from an earlier cur=None caller that never
                            # explicitly committed (e.g. insertLog()). Best-
                            # effort: a failure here shouldn't turn a successful
                            # verify() into a reported failure, since
                            # connectivity IS confirmed.
                            self.commit()
                        except Exception as e:
                            self.logger.warning(
                                f'Database [{self._name}]: could not close verify() probe transaction: {e}'
                            )
                        retry = -1
                        self.release()
                    else:
                        self.logger.warning(
                            'Database [{}]: Could not acquire lock to verify connection'.format(self._name)
                        )
                        retry = retry - 1

                except Exception as e:
                    self.logger.warning('Database [{}]: Connection error {}'.format(self._name, e))
                    if locked:
                        self.release()
                    self.close()
                    retry = retry - 1

                if retry > 0:
                    time.sleep(delay)
        finally:
            if is_pymysql:
                self._params['read_timeout'] = saved_read_timeout
                self._params['write_timeout'] = saved_write_timeout
                # Whatever connection exists now (reused, or freshly opened
                # mid-loop with probe_timeout baked in via self._params
                # above) must have the real timeout restored too - future
                # real queries on it must not inherit the short probe value.
                if self._conn is not None:
                    if hasattr(self._conn, '_read_timeout'):
                        self._conn._read_timeout = saved_read_timeout
                    if hasattr(self._conn, '_write_timeout'):
                        self._conn._write_timeout = saved_write_timeout

        return retry

    def fetchone(self, stmt, params=(), formatting=None, cur=None, quiet=False):
        """Execute given statement and fetch one row from result

        This method can be used in case you only want to fetch one row from
        the result. It accepts the same arguments as mentioned in the
        'execute()' method.
        """
        if cur is not None:
            self.execute(stmt, params, formatting=formatting, cur=cur, quiet=quiet)
            return cur.fetchone()

        def op(c):
            self.execute(stmt, params, formatting=formatting, cur=c, quiet=True)
            return c.fetchone()

        return self._cursor_op_with_reconnect(
            op,
            quiet=quiet,
            empty=None,
            error_prefix=f'fetchone failed for stmt {stmt} with params {params}',
            readonly=True,
        )

    def fetchall(self, stmt, params=(), formatting=None, cur=None, quiet=False):
        """Execute given statement and fetch all rows from result

        This method can be used to fetch all rows from the result. It accepts
        the same arguments as mentioned in the 'execute()' method.
        """
        if cur is not None:
            self.execute(stmt, params, formatting=formatting, cur=cur, quiet=quiet)
            return cur.fetchall()

        def op(c):
            self.execute(stmt, params, formatting=formatting, cur=c, quiet=True)
            return c.fetchall()

        return self._cursor_op_with_reconnect(
            op,
            quiet=quiet,
            empty=[],
            error_prefix=f'fetchall failed for stmt {stmt} with params {params}',
            readonly=True,
        )

    def _prepare(self, stmt, params, formatting=None):
        """Internal helper method to convert the statement and parameter list"""

        if isinstance(params, dict):
            param_dict = params
        else:
            param_dict = collections.OrderedDict()
            for key, value in enumerate(params):
                param_dict[str(key + 1)] = value

        input_format = self._format_input if formatting is None else formatting
        if formatting is None:
            translation = self._translation
        else:
            translation = self._translations[formatting][self._format_output]

        if self._format_output in ('format', 'pyformat') and input_format not in ('format', 'pyformat'):
            # format/pyformat drivers (e.g. pymysql) substitute parameters via
            # Python's own '%' string formatting (query % args) - a literal
            # '%' anywhere in the SQL text (e.g. the modulo operator) is
            # otherwise misread as the start of another format spec and
            # raises "not enough arguments for format string" or similar,
            # even though the query has nothing to do with that parameter.
            # '%%' is '%' string-formatting's own escape for a literal '%',
            # so doubling it here survives untouched through to the driver.
            # Only when neither side already uses '%' for its own
            # placeholder syntax - a 'format'/'pyformat' *source* stmt's
            # existing %s/%(name)s placeholders must not be double-escaped.
            stmt = stmt.replace('%', '%%')

        stmt_result, param_result = self._translate(stmt, param_dict, **translation)

        if self._translation_param_type is list:
            return (stmt_result, [param_result[name] for name in param_result])
        elif self._translation_param_type is dict:
            return (stmt_result, param_result)

    def _translate(self, stmt, params, input_token=None, output_token=None, input_name='{0}', output_name='{0}'):
        """Internal helper method to convert the statement from input format to output format"""

        if input_token is None or output_token is None:
            return (stmt, params)

        cnt = 1
        param_result = collections.OrderedDict()
        if isinstance(input_token, str):
            while input_token in stmt:
                stmt = stmt.replace(input_token, output_token.format(cnt), 1)
                args = [cnt]
                param_result[output_name.format(*args)] = params[input_name.format(*args)]
                cnt = cnt + 1
        else:
            for match in input_token.finditer(stmt):
                args = [cnt]
                args.extend(match.groups())
                stmt = stmt.replace(match.group(0), output_token.format(*args), 1)
                param_result[output_name.format(*args)] = params[input_name.format(*args)]
                cnt = cnt + 1

        return (stmt, param_result)
