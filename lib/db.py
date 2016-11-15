#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-     Christian Strassburg            c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/

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
import re

logger = logging.getLogger('')


class Database():
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
    'lock()' - acquire the database lock (prevent simultaneous reads/writes)
    'release()' - release the database lock
    'verify()' - check database connection and reconnect if required
    """

    # Supported formatting styles
    _styles = ('qmark', 'format', 'numeric', 'pyformat')

    def __init__(self, name, dbapi, connect, format='pyformat'):
        """Create a new database instance

        The 'name' parameter identifies the name for the database access.
        It is also used internally to create versions table (to keep track
        if the database structure is up to date) and logging.

        Use the 'dbapi' parameter to specify the name of the database type
        to use (registered in the common configuration, e.g. 'sqlite').

        How the database is accessed is specified by the 'connect' parameter
        which supports key/value pairs separated by '|'. These named
        parameters will be used as 'connect()' parameters of the DB-API driver
        implementation.

        The 'pyformat' parameter can be used to specify a different type
        of formatting (see DB-API spec) which defaults to 'pyformat'.
        """
        self._name = name
        self._dbapi = dbapi
        self._format_input = format
        self._connected = False
        self._conn = None

        if self._format_input not in self._styles:
            raise Exception("Database [{}]: SQL format style {} not supported (only {})".format(self._name, self._format_input, self._styles))

        self._params = {}
        if type(connect) is str:
            connect = [p.strip() for p in connect.split('|')]

        if type(connect) is list:
            for arg in connect:
               key, sep, value = arg.partition(':')
               for t in int, float, str:
                 try:
                   v = t(value)
                   break
                 except:
                   pass
               self._params[key] = v

        elif type(connect) is dict:
            self._params = connect

        self._format_output = self._dbapi.paramstyle
        if self._format_output not in self._styles:
            raise Exception("Database [{}]: DB-API driver format style {} not supported (only {})".format(self._name, self._format_output, self._styles))

        self._fdb_lock = threading.Lock()

    def connect(self):
        """Connects to the database"""
        self.lock()
        try:
            self._conn = self._dbapi.connect(**self._params)
        except Exception as e:
            logger.error("Database [{}]: Could not connect to the database: {}".format(self._name, e))
            raise
        finally:
            self.release()
        self._connected = True
        logger.info("Database [{}]: Connected with {} using \"{}\" style".format(self._name, self._conn, self._format_output))

    def close(self):
        """Closes the database connection"""
        self.lock()
        try:
            self._conn.close()
        except Exception:
            pass
        finally:
            self.release()
        self._conn = None
        self._connected = False

    def connected(self):
        """Return the connected status"""
        return self._connected

    def setup(self, queries):
        """Setup or update the database structure.

        This method can be used to setup the database structure by providing
        the SQL statements to this method. Additionally it will check if the
        structure is already up to date by checking the data of the version
        table (which will also be created by this method if it does not exist
        already).

        To setup the database you need to specify the required SQL statments
        (e.g. 'CREATE TABLE', 'CREATE INDEX' etc.) in the 'queries' parameter.
        This will be a dictionary where the keys are simple version numbers
        and values are a two-item list for a rollout and rollback statement.

        E.g.::
           db.setup({1:['CREATE TABLE xyz (...)', 'DROP TABLE xyz'], 2:[...]})

        For an extended example take a look into the 'dblog' plugin.
        """
        self.lock()
        cur = self.cursor()
        version_table = re.sub('[^a-z0-9_]', '', self._name.lower()) + "_version";
        try:
            version, = self.fetchone("SELECT MAX(version) FROM " + version_table + ";", cur=cur)
        except Exception as e:
            self.execute("CREATE TABLE " + version_table + "(version NUMERIC, updated BIGINT, rollout TEXT, rollback TEXT)", cur=cur)
            version, = self.fetchone("SELECT MAX(version) FROM " + version_table + ";", cur=cur)
        if version == None:
            version = 0
        logger.info("Database [{}]: Version {} found".format(self._name, version))
        for v in sorted(queries.keys()):
            if float(v) > version:
                logger.info("Database [{}]: Upgrading to version {}".format(self._name, v))
                self.execute(queries[v][0], cur=cur)

                dt = datetime.datetime.utcnow()
                ts = int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)
                self.execute("INSERT INTO " + version_table + "(version, updated, rollout, rollback) VALUES(?, ?, ?, ?);", (v, ts, queries[v][0], queries[v][1]), cur)

        self.commit()
        cur.close()
        self.release()

    def lock(self, timeout=-1):
        """Acquire a database lock"""
        return self._fdb_lock.acquire(timeout=timeout)

    def release(self):
        """Release the database lock"""
        self._fdb_lock.release()

    def commit(self):
        """Commit the current transaction"""
        self._conn.commit()

    def rollback(self):
        """Rollback the current transaction"""
        self._conn.rollback()

    def cursor(self):
        """Create a new cursor for executing statements"""
        return self._conn.cursor()

    def execute(self, stmt, params=(), cur=None):
        """Execute the given statement

        This will execute the statement specified in the 'stmt' parameter
        which may contain '?' for parameter placeholders.

        The parameters can be specified as tuple in the 'params' parameters
        where the first '?' in statement will be replaced by first value from
        the parameter tuple.

        If already aqcuired a cursor you can use this cursor by using the
        'cur' parameter. If omitted a new cursor will be aqcuire for this
        statement and released afterwards.
        """
        args = self._parameters(params)
        stmt = self._format(stmt)
        if cur == None:
            c = self.cursor()
            result = c.execute(stmt, args)
            c.close()
        else:
            result = cur.execute(stmt, args)
        return result

    def verify(self, retry=5):
        """Verifies the connection status and reconnets if required

        The connected status of the connection will be checked by executing
        a simple SQL statement. If this fails or the connection is not
        established already a new connection will be opened.

        In case the reconnect fails you can specify how many times a
        reconnect will be executed until it will give up. This can be
        specified by the 'retry' parameter.
        """
        while retry > 0:
            locked = False

            try:
                if self.connected() == False:
                    self.connect()

                locked = self.lock(2)

                if locked:
                    self.fetchone("SELECT 1")
                    retry = -1
                    self.release()

            except Exception as e:
                logger.warning("Database [{}]: Connection error {}".format(self._name, e))
                if locked:
                    self.release()
                self.close()
                retry = retry - 1

        return retry

    def fetchone(self, stmt, params=(), cur=None):
        """Execute given statement and fetch one row from result

        This method can be used in case you only want to fetch one row from
        the result. It accepts the same arguments as mentioned in the
        'execute()' method.
        """
        if cur == None:
            c = self.cursor()
            self.execute(stmt, params, c)
            result = c.fetchone()
            c.close()
        else:
            self.execute(stmt, params, cur)
            result = cur.fetchone()
        return result

    def fetchall(self, stmt, params=(), cur=None):
        """Execute given statement and fetch all rows from result

        This method can be used to fetch all rows from the result. It accepts
        the same arguments as mentioned in the 'execute()' method.
        """
        if cur == None:
            c = self.cursor()
            self.execute(stmt, params, c)
            result = c.fetchall()
            c.close()
        else:
            self.execute(stmt, params, cur)
            result = cur.fetchall()
        return result

    def _parameters(self, params):
        """Internal helper method to convert the parameter list"""

        if isinstance(params, dict):
            param_list = list(params.values())
            param_dict = params
        else:
            param_list = list(params)
            param_dict = {'arg' + str(1+i) : params[i] for i in range(0, len(list(params)))}

        if self._format_output == 'qmark':
            return param_list
        elif self._format_output == 'format':
            return param_list
        elif self._format_output == 'numeric':
            return param_list
        elif self._format_output == 'pyformat':
            return param_dict

    def _format(self, stmt):
        """Internal helper method to convert the statement"""

        stmts = {}
        if self._format_input == 'qmark':
            stmts['qmark'] = stmt
            stmts['format'] = self._format_replace(stmt, '?', '%s')
            stmts['numeric'] = self._format_numbered(stmt, '?', ':{0}')
            stmts['pyformat'] = self._format_numbered(stmt, '?', '%(arg{0})s')

        elif self._format_input == 'format':
            format_token = re.compile('%[\w\d]+')
            stmts['qmark'] = self._format_numbered(stmt, format_token, '?')
            stmts['format'] = stmt
            stmts['numeric'] = self._format_numbered(stmt, format_token, ':{0}')
            stmts['pyformat'] = self._format_numbered(stmt, format_token, '%(arg{0})s')

        elif self._format_input == 'numeric':
            format_token = re.compile(':(\d+)')
            stmts['qmark'] = self._format_numbered(stmt, format_token, '?')
            stmts['format'] = self._format_numbered(stmt, format_token, '%s')
            stmts['numeric'] = stmt
            stmts['pyformat'] = self._format_numbered(stmt, format_token, '%(arg{1})s')

        elif self._format_input == 'pyformat':
            format_token = re.compile('%\([\w\d]+\)\w+')
            stmts['qmark'] = self._format_numbered(stmt, format_token, '?')
            stmts['format'] = self._format_numbered(stmt, format_token, '%s')
            stmts['numeric'] = self._format_numbered(stmt, format_token, ':{0}')
            stmts['pyformat'] = stmt

        return stmts[self._format_output]

    def _format_replace(self, stmt, search, replace):
        return stmt.replace(search, replace)

    def _format_numbered(self, stmt, search, replace, cnt=1):
        if isinstance(search, str):
            while search in stmt:
                stmt = stmt.replace(search, replace.format(cnt), 1)
                cnt = cnt + 1
        else:
            match = True
            while match is not None:
                match = search.search(stmt)
                if match is not None:
                    args = [cnt]
                    args.extend(match.groups())
                    stmt = stmt.replace(match.group(0), replace.format(*args), 1)
                    cnt = cnt + 1
        return stmt

