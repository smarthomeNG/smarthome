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
import collections
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

    The SQL statments executed may have placeholders and parameters which
    are passed to the execution methods listed above. The following DB-API
    driver implementations are supported:
    - qmark: Specify placeholders as "?" and parameters as list
    - format: Specify placeholders as "%s" and parameters as list
    - numeric: Specify placeholders as ":1" and parameters as list
    - pyformat: Specify placeholders as "%(arg)s" and parameters as dict

    Further you can choose a different formatting style in your code when
    using this class. Specify one of the formatting listed above or use
    the default - which is pyformat.

    In case the driver implementation uses a different formatting it
    will be converted transparently!
    """

    # Supported formatting styles
    _styles = ('qmark', 'format', 'numeric', 'pyformat')

    # Supported formatting translations
    _translations = {
      'qmark' : {
        'qmark'    : {},
        'format'   : {'input_token' : '?', 'output_token' : '%s'},
        'numeric'  : {'input_token' : '?', 'output_token' : ':{0}'},
        'pyformat' : {'input_token' : '?', 'output_token' : '%(arg{0})s', 'output_name' : 'arg{0}'}
      },
      'format' : {
        'qmark'    : {'input_token' : re.compile('%[\w\d]+'), 'output_token' : '?'},
        'format'   : {},
        'numeric'  : {'input_token' : re.compile('%[\w\d]+'), 'output_token' : ':{0}'},
        'pyformat' : {'input_token' : re.compile('%[\w\d]+'), 'output_token' : '%(arg{0})s', 'output_name' : 'arg{0}'}
      },
      'numeric' : {
        'qmark'    : {'input_token' : re.compile(':(\d+)'), 'output_token' : '?', 'input_name' : '{1}'},
        'format'   : {'input_token' : re.compile(':(\d+)'), 'output_token' : '%s', 'input_name' : '{1}'},
        'numeric'  : {},
        'pyformat' : {'input_token' : re.compile(':(\d+)'), 'output_token' : '%(arg{1})s', 'output_name' : 'arg{1}'}
      },
      'pyformat' : {
        'qmark'    : {'input_token' : re.compile('%\(([\w\d]+)\)\w+'), 'output_token' : '?', 'input_name' : '{1}'},
        'format'   : {'input_token' : re.compile('%\(([\w\d]+)\)\w+'), 'output_token' : '%s', 'input_name' : '{1}'},
        'numeric'  : {'input_token' : re.compile('%\(([\w\d]+)\)\w+'), 'output_token' : ':{0}', 'input_name' : '{1}'},
        'pyformat' : {}
      },
    }
    _translation_param_types = {
      'qmark'    : list,
      'format'   : list,
      'numeric'  : list,
      'pyformat' : dict
    }

    def __init__(self, name, dbapi, connect, formatting='pyformat'):
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

        The 'formatting' parameter can be used to specify a different type
        of formatting (see DB-API spec) which defaults to 'pyformat'.
        """
        self._name = name
        self._dbapi = dbapi
        self._format_input = formatting
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

        self._translation = self._translations[self._format_input][self._format_output]
        self._translation_param_type = self._translation_param_types[self._format_output]

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
                self.execute("INSERT INTO " + version_table + "(version, updated, rollout, rollback) VALUES(?, ?, ?, ?);", (v, ts, queries[v][0], queries[v][1]), formatting='qmark', cur=cur)

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

    def execute(self, stmt, params=(), formatting=None, cur=None):
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
        """
        try:
            stmt, args = self._prepare(stmt, params, formatting)
        except Exception as e:
            logger.error("Can not prepare query: {} (args {}): {}".format(stmt, params, e))
            raise

        c = None
        try:
            if cur == None:
                c = self.cursor()
                result = c.execute(stmt, args)
                c.close()
                c = None
            else:
                result = cur.execute(stmt, args)
            return result
        except Exception as e:
            logger.error("Can not execute query: {} (args {}): {}".format(stmt, args, e))
            raise
        finally:
            if c is not None:
                c.close()

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

    def fetchone(self, stmt, params=(), formatting=None, cur=None):
        """Execute given statement and fetch one row from result

        This method can be used in case you only want to fetch one row from
        the result. It accepts the same arguments as mentioned in the
        'execute()' method.
        """
        if cur == None:
            c = self.cursor()
            self.execute(stmt, params, formatting=formatting, cur=c)
            result = c.fetchone()
            c.close()
        else:
            self.execute(stmt, params, formatting=formatting, cur=cur)
            result = cur.fetchone()
        return result

    def fetchall(self, stmt, params=(), formatting=None, cur=None):
        """Execute given statement and fetch all rows from result

        This method can be used to fetch all rows from the result. It accepts
        the same arguments as mentioned in the 'execute()' method.
        """
        if cur == None:
            c = self.cursor()
            self.execute(stmt, params, formatting=formatting, cur=c)
            result = c.fetchall()
            c.close()
        else:
            self.execute(stmt, params, formatting=formatting, cur=cur)
            result = cur.fetchall()
        return result

    def _prepare(self, stmt, params, formatting=None):
        """Internal helper method to convert the statement and parameter list"""

        if isinstance(params, dict):
            param_dict = params
        else:
            param_dict = {str(key+1): value for key, value in enumerate(params)}

        if formatting is None:
            translation = self._translation
            translation_param_type = self._translation_param_type
        else:
            translation = self._translations[formatting][self._format_output]
            translation_param_type = self._translation_param_types[formatting]

        stmt_result, param_result = self._translate(stmt, param_dict, **translation)

        if translation_param_type is list:
            return (stmt_result, [param_result[name] for name in param_result])
        elif translation_param_type is dict:
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
            match = True
            while match is not None:
                match = input_token.search(stmt)
                if match is not None:
                    args = [cnt]
                    args.extend(match.groups())
                    stmt = stmt.replace(match.group(0), output_token.format(*args), 1)
                    param_result[output_name.format(*args)] = params[input_name.format(*args)]
                    cnt = cnt + 1

        return (stmt,  param_result)

