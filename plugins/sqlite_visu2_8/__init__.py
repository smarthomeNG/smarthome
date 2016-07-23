#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013-2014 Marcus Popp                          marcus@popp.mx
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
import sqlite3
import datetime
import functools
import time
import threading
from lib.model.smartplugin import SmartPlugin

class SQL(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.1"
    _version = 3
    _buffer_time = 60 * 1000
    # (period days, granularity hours)
    periods = [(1900, 168), (400, 24), (32, 1), (7, 0.5), (1, 0.1)]
    # _start, _item, _dur, _avg, _min, _max, _on
    _pack_query = """
        SELECT
        group_concat(rowid),
        MIN(_start),
        _item,
        SUM(_dur),
        SUM(_avg * _dur) / SUM(_dur),
        MIN(_min),
        MAX(_max),
        SUM(_on * _dur) / SUM(_dur)
        FROM num
        WHERE (_start < {})
        GROUP by CAST((_start / {}) AS INTEGER), _item
        ORDER BY _start DESC;"""

    def __init__(self, smarthome, cycle=300, path=None, dumpfile=False):
        self.logger = logging.getLogger(__name__)
#       sqlite3.register_adapter(datetime.datetime, self._timestamp)
        self._sh = smarthome
        self.connected = False
        self._buffer = {}
        self._buffer_lock = threading.Lock()
        self.logger.debug("SQLite {0}".format(sqlite3.sqlite_version))
        self._fdb_lock = threading.Lock()
        self._fdb_lock.acquire()
        self._dumpfile = dumpfile
        if path is None:
            self.path = smarthome.base_dir + '/var/db/smarthome.db'
        else:
            self.path = path + '/smarthome.db'
        try:
            self._fdb = sqlite3.connect(self.path, check_same_thread=False)
        except Exception as e:
            self.logger.error("SQLite: Could not connect to the database {}: {}".format(self.path, e))
            self._fdb_lock.release()
            return
        self.connected = True
        integrity = self._fdb.execute("PRAGMA integrity_check(10);").fetchone()[0]
        if integrity == 'ok':
            self.logger.debug("SQLite: database integrity ok")
        else:
            self.logger.error("SQLite: database corrupt. Seek help.")
            self._fdb_lock.release()
            return
        self._fdb.execute("CREATE TABLE IF NOT EXISTS num (_start INTEGER, _item TEXT, _dur INTEGER, _avg REAL, _min REAL, _max REAL, _on REAL);")
        self._fdb.execute("CREATE TABLE IF NOT EXISTS cache (_item TEXT PRIMARY KEY, _start INTEGER, _value REAL);")
        self._fdb.execute("CREATE INDEX IF NOT EXISTS idx ON num (_item);")
        common = self._fdb.execute("SELECT * FROM sqlite_master WHERE name='common' and type='table';").fetchone()
        if common is None:
            self._fdb.execute("CREATE TABLE common (version INTEGER);")
            self._fdb.execute("INSERT INTO common VALUES (:version);", {'version': self._version})
        else:
            version = int(self._fdb.execute("SELECT version FROM common;").fetchone()[0])
            if version < self._version:
                import plugins.sqlite.upgrade
                self.logger.info("SQLite: upgrading database. Please wait!")
                plugins.sqlite.upgrade.Upgrade(self._fdb, version)
                self._fdb.execute("UPDATE common SET version=:version;", {'version': self._version})
        self._fdb.commit()
        self._fdb_lock.release()
        minute = 60 * 1000
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        month = 30 * day
        year = 365 * day
        self._frames = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}
        self._times = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}
        smarthome.scheduler.add('SQLite Maintain', self._maintain, cron='2 3 * *', prio=5)

    def remove_orphans(self):
        current_items = [item.id() for item in self._buffer]
        db_items = self._fetchall("SELECT _item FROM num GROUP BY _item;")
        if db_items:
            for item in db_items:
                if item[0] not in current_items:
                    self.logger.info("SQLite: deleting entries for {}".format(item[0]))
                    self._execute("DELETE FROM num WHERE _item='{}';".format(item[0]))

    def dump(self, dumpfile):
        self.logger.info("SQLite: dumping database to {}".format(dumpfile))
        self._fdb_lock.acquire()
        try:
            with open(dumpfile, 'w') as f:
                for line in self._fdb.iterdump():
                    f.write('{}\n'.format(line))
        except Exception as e:
            self.logger.warning("SQLite: Problem dumping to '{0}': {1}".format(dumpfile, e))
        finally:
            self._fdb_lock.release()

    def move(self, old, new):
        self._execute("UPDATE OR IGNORE num SET _item={} WHERE _item='{}';".format(new, old))

    def parse_item(self, item):
        if 'sqlite' in item.conf:
            if item.type() not in ['num', 'bool']:
                self.logger.warning("SQLite: only supports 'num' and 'bool' as types. Item: {} ".format(item.id()))
                return
            cache = self._fetchone("SELECT _start,_value from cache WHERE _item = '{}'".format(item.id()))
            if cache is not None:
                last_change, value = cache
                item._sqlite_last = last_change
                last_change = self._datetime(last_change)
                prev_change = self._fetchone("SELECT _start from num WHERE _item = '{}' ORDER BY _start DESC LIMIT 1".format(item.id()))
                if prev_change is not None:
                    prev_change = self._datetime(prev_change[0])
                    item.set(value, 'SQLite', prev_change=prev_change, last_change=last_change)
            else:
                last_change = self._timestamp(self._sh.now())
                item._sqlite_last = last_change
                self._execute("INSERT OR IGNORE INTO cache VALUES('{}',{},{})".format(item.id(), last_change, float(item())))
            self._buffer[item] = []
            item.series = functools.partial(self._series, item=item.id())
            item.db = functools.partial(self._single, item=item.id())
            return self.update_item
        else:
            return None

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        for item in self._buffer:
            if self._buffer[item] != []:
                self._insert(item)
        self._fdb_lock.acquire()
        try:
            self._fdb.close()
        except Exception:
            pass
        finally:
            self.connected = False
            self._fdb_lock.release()

    def update_item(self, item, caller=None, source=None, dest=None):
        _start = self._timestamp(item.prev_change())
        _end = self._timestamp(item.last_change())
        _dur = _end - _start
        _avg = float(item.prev_value())
        _on = int(bool(_avg))
        self._buffer[item].append((_start, _dur, _avg, _on))
        if _end - item._sqlite_last > self._buffer_time:
            self._insert(item)
        # update cache with current value
        self._execute("UPDATE OR IGNORE cache SET _start={}, _value={} WHERE _item='{}';".format(_end, float(item()), item.id()))

    def _datetime(self, ts):
        return datetime.datetime.fromtimestamp(ts / 1000, self._sh.tzinfo())

    def _execute(self, *query):
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            if not self.connected:
                return
            self._fdb.execute(*query)
            self._fdb.commit()
        except Exception as e:
            self.logger.warning("SQLite: Problem with '{0}': {1}".format(query, e))
        finally:
            self._fdb_lock.release()

    def _fetchone(self, *query):
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            if not self.connected:
                return
            reply = self._fdb.execute(*query).fetchone()
        except Exception as e:
            self.logger.warning("SQLite: Problem with '{0}': {1}".format(query, e))
            reply = None
        finally:
            self._fdb_lock.release()
        return reply

    def _fetchall(self, *query):
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            if not self.connected:
                return
            reply = self._fdb.execute(*query).fetchall()
        except Exception as e:
            self.logger.warning("SQLite: Problem with '{0}': {1}".format(query, e))
            reply = None
        finally:
            self._fdb_lock.release()
        return reply

    def _get_timestamp(self, frame='now'):
        try:
            return int(frame)
        except:
            pass
        dt = self._sh.now()
        ts = int(time.mktime(dt.timetuple()) * 1000 + dt.microsecond / 1000)
        if frame == 'now':
            fac = 0
            frame = 0
        elif frame[-1] in self._frames:
            fac = self._frames[frame[-1]]
            frame = frame[:-1]
        else:
            return frame
        try:
            ts = ts - int(float(frame) * fac)
        except:
            self.logger.warning("SQLite: unkown time frame '{0}'".format(frame))
        return ts

    def _insert(self, item):
        if not self._fdb_lock.acquire(timeout=2):
            return
        tuples = sorted(self._buffer[item])
        tlen = len(tuples)
        self._buffer[item] = self._buffer[item][tlen:]
        item._sqlite_last = self._timestamp(item.last_change())
        try:
            if tlen == 1:
                _start, _dur, _avg, _on = tuples[0]
                insert = (_start, item.id(), _dur, _avg, _avg, _avg, _on)
            elif tlen > 1:
                _vals = []
                _dur = 0
                _avg = 0.0
                _on = 0.0
                _start = tuples[0][0]
                for __start, __dur, __avg, __on in tuples:
                    _vals.append(__avg)
                    _avg += __dur * __avg
                    _on += __dur * __on
                    _dur += __dur
                insert = (_start, item.id(), _dur, _avg / _dur, min(_vals), max(_vals), _on / _dur)
            else:  # no tuples
                return
            self._fdb.execute("INSERT INTO num VALUES (?,?,?,?,?,?,?);", insert)
            self._fdb.commit()
        except Exception as e:
            self.logger.warning("SQLite: problem updating {}: {}".format(item.id(), e))
        finally:
            self._fdb_lock.release()

    def _maintain(self):
        for item in self._buffer:
            if self._buffer[item] != []:
                self._insert(item)
        self._pack()
        if self._dumpfile:
            self.dump(self._dumpfile)

    def _pack(self):
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            self.logger.debug("SQLite: pack database")
            for entry in self.periods:
                now = self._timestamp(self._sh.now())
                period, granularity = entry
                period = int(now - period * 24 * 3600 * 1000)
                granularity = int(granularity * 3600 * 1000)
                for row in self._fdb.execute(self._pack_query.format(period, granularity)):
                    gid, _start, _item, _dur, _avg, _min, _max, _on = row
                    if gid.count(',') == 0:  # ignore
                        continue
                    insert = (_start, _item, _dur, _avg, _min, _max, _on)
                    self._fdb.execute("INSERT INTO num VALUES (?,?,?,?,?,?,?);", insert)
                    self._fdb.execute("DELETE FROM num WHERE rowid in ({0});".format(gid))
                    self._fdb.commit()
            self._fdb.execute("VACUUM;")
            self._fdb.execute("PRAGMA shrink_memory;")
        except Exception as e:
            self.logger.exception("problem packing sqlite database: {} period: {} type: {}".format(e, period, type(period)))
            self._fdb.rollback()
        finally:
            self._fdb_lock.release()

    def _series(self, func, start, end='now', count=100, ratio=1, update=False, step=None, sid=None, item=None):
        init = not update
        if sid is None:
            sid = item + '|' + func + '|' + start + '|' + end + '|' + str(count)
        istart = self._get_timestamp(start)
        iend = self._get_timestamp(end)
        if step is None:
            if count != 0:
                step = int((iend - istart) / int(count))
            else:
                step = iend - istart
        reply = {'cmd': 'series', 'series': None, 'sid': sid}
        reply['params'] = {'update': True, 'item': item, 'func': func, 'start': iend, 'end': end, 'step': step, 'sid': sid}
        reply['update'] = self._sh.now() + datetime.timedelta(seconds=int(step / 1000))
        where = " from num WHERE _item='{0}' AND _start + _dur >= {1} AND _start <= {2} GROUP by CAST((_start / {3}) AS INTEGER)".format(item, istart, iend, step)
        if func == 'avg':
            query = "SELECT MIN(_start), ROUND(SUM(_avg * _dur) / SUM(_dur), 2)" + where + " ORDER BY _start ASC"
        elif func == 'min':
            query = "SELECT MIN(_start), MIN(_min)" + where
        elif func == 'max':
            query = "SELECT MIN(_start), MAX(_max)" + where
        elif func == 'on':
            query = "SELECT MIN(_start), ROUND(SUM(_on * _dur) / SUM(_dur), 2)" + where + " ORDER BY _start ASC"
        else:
            raise NotImplementedError
        _item = self._sh.return_item(item)
        if self._buffer[_item] != [] and end == 'now':
            self._insert(_item)
        tuples = self._fetchall(query)
        if tuples:
            if istart > tuples[0][0]:
                tuples[0] = (istart, tuples[0][1])
            if end != 'now':
                tuples.append((iend, tuples[-1][1]))
        else:
            tuples = []
        item_change = self._timestamp(_item.last_change())
        if item_change < iend:
            value = float(_item())
            if item_change < istart:
                tuples.append((istart, value))
            elif init:
                tuples.append((item_change, value))
            if init:
                tuples.append((iend, value))
        if tuples:
            reply['series'] = tuples
        return reply

    def _single(self, func, start, end='now', item=None):
        start = self._get_timestamp(start)
        end = self._get_timestamp(end)
        where = " from num WHERE _item='{0}' AND _start + _dur >= {1} AND _start <= {2};".format(item, start, end)
        if func == 'avg':
            query = "SELECT ROUND(SUM(_avg * _dur) / SUM(_dur), 2)" + where
        elif func == 'min':
            query = "SELECT MIN(_min)" + where
        elif func == 'max':
            query = "SELECT MAX(_max)" + where
        elif func == 'on':
            query = "SELECT ROUND(SUM(_on * _dur) / SUM(_dur), 2)" + where
        else:
            self.logger.warning("Unknown export function: {0}".format(func))
            return
        _item = self._sh.return_item(item)
        if self._buffer[_item] != [] and end == 'now':
            self._insert(_item)
        tuples = self._fetchall(query)
        if tuples is None:
            return
        return tuples[0][0]

    def _timestamp(self, dt):
        return int(time.mktime(dt.timetuple())) * 1000 + int(dt.microsecond / 1000)
