#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 Marcus Popp                               marcus@popp.mx
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
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import datetime
import functools
import time
import threading
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger('')


class DbLog():

    _version = 2
    # SQL queries
    # time, item_id, val_str, val_num, val_bool
    _create_db_log = "CREATE TABLE IF NOT EXISTS log (time INTEGER, item_id INTEGER, val_str TEXT, val_num REAL, val_bool BOOLEAN);"
    _create_db_item = "CREATE TABLE IF NOT EXISTS item (id INTEGER, name TEXT, time INTEGER, val_str TEXT, val_num REAL, val_bool BOOLEAN);"
    _create_index_log = "CREATE INDEX IF NOT EXISTS log_item_id ON log (item_id);"
    _create_index_item = "CREATE INDEX IF NOT EXISTS item_name ON item (name);"

    def __init__(self, smarthome, db, connect, cycle=10):
        self._sh = smarthome
        self.connected = False
        self._dump_cycle = int(cycle)
        self._buffer = {}
        self._buffer_lock = threading.Lock()

        if type(connect) is not list:
            connect = [connect]

        self._params = {}
        for arg in connect:
           key, sep, value = arg.partition(':')
           for t in int, float, str:
             try:
               v = t(value)
               break
             except:
               pass
           self._params[key] = v

        dbapi = self._sh.dbapi(db)
        self._fdb_lock = threading.Lock()
        self._fdb_lock.acquire()
        try:
            self._fdb = dbapi.connect(**self._params)
        except Exception as e:
            logger.error("DbLog: Could not connect to the database: {}".format(e))
            self._fdb_lock.release()
            return
        self.connected = True
        logger.info("DbLog: Connected using {}!".format(db))

        self._fdb.execute(self._create_db_log)
        self._fdb.execute(self._create_db_item)
        self._fdb.execute(self._create_index_log)
        self._fdb.execute(self._create_index_item)
        self._fdb_lock.release()
        smarthome.scheduler.add('DbLog dump', self._dump, cycle=self._dump_cycle, prio=5)

    def parse_item(self, item):
        if 'dblog' in item.conf:
            self._buffer[item] = []
            return self.update_item
        else:
            return None

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self._dump()
        self._fdb_lock.acquire()
        try:
            self._fdb.close()
        except Exception:
            pass
        finally:
            self.connected = False
            self._fdb_lock.release()

    def update_item(self, item, caller=None, source=None, dest=None):
        if item.type() == 'num':
           val_str = None
           val_num = float(item())
           val_bool = None
        elif item.type() == 'bool':
           val_str = None
           val_num = None
           val_bool = bool(item())
        else:
           val_str = str(item())
           val_num = None
           val_bool = None

        self._buffer[item].append((self._timestamp(self._sh.now()), val_str, val_num, val_bool))

    def _datetime(self, ts):
        return datetime.datetime.fromtimestamp(ts / 1000, self._sh.tzinfo())

    def _dump(self):
        logger.debug('Starting dump')
        for item in self._buffer:
            self._buffer_lock.acquire()
            tuples = self._buffer[item]
            self._buffer[item] = []
            self._buffer_lock.release()

            if len(tuples):
                try:
                    self._fdb_lock.acquire()

                    # Create new item ID
                    id = self._fdb.execute("SELECT id FROM item where name = ?;", (item.id(),)).fetchone()
                    if id == None:
                        id = self._fdb.execute("SELECT MAX(id) FROM item;").fetchone()
                        self._fdb.execute("INSERT INTO item(id, name) VALUES(?,?);", (1 if id[0] == None else id[0]+1, item.id()))
                        id = self._fdb.execute("SELECT id FROM item where name = ?;", (item.id(),)).fetchone()

                    id = id[0]
                    logger.debug('Dumping {} (id {}) with {} values'.format(item.id(), id, len(tuples)))

                    for t in tuples:
                        _insert = ( t[0], id, t[1], t[2], t[3] )

                        # time, item_id, val_str, val_num, val_bool
                        self._fdb.execute("INSERT INTO log VALUES (?,?,?,?,?);", _insert)

                    t = tuples[-1]
                    _update = ( t[0], t[1], t[2], t[3], id )

                    # time, item_id, val_str, val_num, val_bool
                    self._fdb.execute("UPDATE item SET time = ?, val_str = ?, val_num = ?, val_bool = ? WHERE id = ?;", _update)

                    self._fdb.commit()
                except Exception as e:
                    logger.warning("DbLog: problem updating {}: {}".format(item.id(), e))
                finally:
                    self._fdb_lock.release()

    def _timestamp(self, dt):
        return int(time.mktime(dt.timetuple())) * 1000 + int(dt.microsecond / 1000)
