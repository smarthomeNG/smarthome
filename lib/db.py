#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 Marcus Popp                          marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import datetime
import time
import threading
import re

logger = logging.getLogger('')


class Database():

    # Supported formatting styles
    _styles = ('qmark', 'format', 'numeric')

    def __init__(self, name, dbapi, connect):
        self._name = name
        self._dbapi = dbapi
        self._connected = False
        self._conn = None

        self._params = {}
        if type(connect) is str:
            connect = [trim(p) for p in connect.split('|')]

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

        self._style = self._dbapi.paramstyle
        if self._style not in self._styles:
            raise Exception("Database [{}]: Format style {} not supported (only {})".format(self._name, self._style, self._styles))

        self._fdb_lock = threading.Lock()

    def connect(self):
        self.lock()
        try:
            self._conn = self._dbapi.connect(**self._params)
        except Exception as e:
            logger.error("Database [{}]: Could not connect to the database: {}".format(self._name, e))
            raise
        finally:
            self.release()
        self._connected = True
        logger.info("Database [{}]: Connected with {} using \"{}\" style".format(self._name, self._conn, self._style))

    def close(self):
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
        return self._connected

    def setup(self, queries):
        self.lock()
        cur = self.cursor()
        version_table = re.sub('[^a-z0-9]', '', self._name.lower()) + "_version";
        try:
            version, = self.fetchone("SELECT MAX(version) FROM " + version_table + ";", cur=cur)
        except Exception as e:
            self.execute("CREATE TABLE " + version_table + "(version NUMERIC, updated BIGINT)", cur=cur)
            version, = self.fetchone("SELECT MAX(version) FROM " + version_table + ";", cur=cur)
        if version == None:
            version = 0
        logger.info("Database [{}]: Version {} found".format(self._name, version))
        for v in sorted(queries.keys()):
            if float(v) > version:
                logger.info("Database [{}]: Upgrading to version {}".format(self._name, v))
                self.execute(queries[v], cur=cur)

                dt = datetime.datetime.utcnow()
                ts = int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)
                self.execute("INSERT INTO " + version_table + "(version, updated) VALUES(?, ?);", (v, ts), cur)

        self.commit()
        cur.close()
        self.release()

    def lock(self, timeout=-1):
        return self._fdb_lock.acquire(timeout=timeout)

    def release(self):
        self._fdb_lock.release()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def cursor(self):
        return self._conn.cursor()

    def execute(self, stmt, params=(), cur=None):
        stmt = self._format(stmt)
        if cur == None:
            c = self.cursor()
            result = c.execute(stmt, params)
            c.close()
        else:
            result = cur.execute(stmt, params)
        return result

    def verify(self, retry=5):
        while retry > 0:
            locked = False

            try:
                if self.connected() == False:
                    self.connect()

                locked = self.lock(2)

                if locked:
                    self.fetchone("SELECT 1")
                    retry = -1

            except Exception as e:
                logger.warning("Database [{}]: Connection error {}".format(self._name, e))
                self.close()
                retry = retry - 1

            finally:
                if locked:
                    self.release()

        return retry

    def fetchone(self, stmt, params=(), cur=None):
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
        if cur == None:
            c = self.cursor()
            self.execute(stmt, params, c)
            result = c.fetchall()
            c.close()
        else:
            self.execute(stmt, params, cur)
            result = cur.fetchall()
        return result

    def _format(self, stmt):
        if self._style == 'qmark':
            return stmt
        elif self._style == 'format':
            return stmt.replace('?', '%s')
        elif self._style == 'numeric':
            cnt = 1
            while '?' in stmt:
                stmt = stmt.replace('?', ':' + str(cnt), 1)
                cnt = cnt + 1
            return stmt


