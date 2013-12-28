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

logger = logging.getLogger('')


class SQL():

    _version = 2
    # (period days, granularity hours)
    periods = [(1900, 168), (400, 24), (32, 1), (7, 0.5), (1, 0.1)]
    # SQL queries
    # time, item, avg, vmin, vmax, power
    _create_db = "CREATE TABLE IF NOT EXISTS history (time INTEGER, item TEXT, avg REAL, vmin REAL, vmax REAL, power REAL);"
    _create_index = "CREATE INDEX IF NOT EXISTS idy ON history (item);"
    _pack_query = """
        SELECT
        group_concat(rowid),
        group_concat(time),
        group_concat(avg),
        group_concat(power),
        item,
        MIN(vmin),
        MAX(vmax)
        FROM history
        WHERE (time < {})
        GROUP by CAST((time / {}) AS INTEGER), item
        ORDER BY time DESC;"""

    def __init__(self, smarthome, cycle=300, path=None):
        self._sh = smarthome
        self.connected = False
        self._dump_cycle = int(cycle)
        self._buffer = {}
        self._buffer_lock = threading.Lock()
        sqlite3 = self._sh.dbapi('sqlite')
#       sqlite3.register_adapter(datetime.datetime, self._timestamp)
        logger.debug("SQLite {0}".format(sqlite3.sqlite_version))
        self._fdb_lock = threading.Lock()
        self._fdb_lock.acquire()
        if path is None:
            self.path = smarthome.base_dir + '/var/db/smarthome.db'
        else:
            self.path = path + '/smarthome.db'
        try:
            self._fdb = sqlite3.connect(self.path, check_same_thread=False)
        except Exception as e:
            logger.error("SQLite: Could not connect to the database {}: {}".format(self.path, e))
            self._fdb_lock.release()
            return
        self.connected = True
        integrity = self._fdb.execute("PRAGMA integrity_check(10);").fetchone()[0]
        if integrity == 'ok':
            logger.debug("SQLite: database integrity ok")
        else:
            logger.error("SQLite: database corrupt. Seek help.")
            self._fdb_lock.release()
            return
        common = self._fdb.execute("SELECT * FROM sqlite_master WHERE name='common' and type='table';").fetchone()
        if common is None:
            self._fdb.execute("CREATE TABLE common (version INTEGER);")
            self._fdb.execute("INSERT INTO common VALUES (:version);", {'version': self._version})
            version = self._version
        else:
            version = int(self._fdb.execute("SELECT version FROM common;").fetchone()[0])
            if version == 1:
                logger.warning("SQLite: dropping history!")
                self._fdb.execute("DROP TABLE history;")
        self._fdb.execute("DROP INDEX IF EXISTS idx;")
        self._fdb.execute(self._create_db)
        self._fdb.execute(self._create_index)
        if version < self._version:
            self._fdb.execute("UPDATE common SET version=:version;", {'version': self._version})
            # self.query("alter table history add column power INTEGER;")
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
        smarthome.scheduler.add('SQLite pack', self._pack, cron='2 3 * *', prio=5)
        smarthome.scheduler.add('SQLite dump', self._dump, cycle=self._dump_cycle, prio=5)

    def parse_item(self, item):
        if 'history' in item.conf:  # XXX legacy history option remove sometime
            logger.warning("{} deprecated history attribute. Use sqlite as keyword instead.".format(item.id()))
            item.conf['sqlite'] = item.conf['history']
        if 'sqlite' in item.conf:
            if item.type() not in ['num', 'bool']:
                logger.warning("SQLite: only supports 'num' and 'bool' as types. Item: {} ".format(item.id()))
                return
            item.series = functools.partial(self._series, item=item.id())
            item.db = functools.partial(self._single, item=item.id())
            if item.conf['sqlite'] == 'init':
                last = self._fetchone("SELECT avg from history WHERE item = '{0}' ORDER BY time DESC LIMIT 1".format(item.id()))
                if last is not None:
                    last = last[0]
                    item.set(last, 'SQLite')
            self._buffer[item] = []
            self.update_item(item)
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
        now = self._timestamp(self._sh.now())
        val = float(item())
        power = int(bool(val))
        self._buffer[item].append((now, val, power))

    def _datetime(self, ts):
        return datetime.datetime.fromtimestamp(ts / 1000, self._sh.tzinfo())

    def _dump(self):
        for item in self._buffer:
            self._buffer_lock.acquire()
            tuples = self._buffer[item]
            self._buffer[item] = []
            self._buffer_lock.release()
            self.update_item(item)
            _now = self._timestamp(self._sh.now())
            try:
                _insert = self.__dump(item.id(), tuples, _now)
            except:
                continue
            if not self._fdb_lock.acquire(timeout=10):
                continue
            try:
                # time, item, avg, vmin, vmax, power
                self._fdb.execute("INSERT INTO history VALUES (?,?,?,?,?,?);", _insert)
                self._fdb.commit()
            except Exception as e:
                logger.warning("SQLite: problem updating {}: {}".format(item.id(), e))
            finally:
                self._fdb_lock.release()

    def __dump(self, item, tuples, end):
        vsum = 0.0
        psum = 0.0
        prev = end
        if len(tuples) == 1:
            return (tuples[0][0], item, tuples[0][1], tuples[0][1], tuples[0][1], tuples[0][2])
        vals = []
        for _time, val, power in sorted(tuples, reverse=True):
            vals.append(val)
            vsum += (prev - _time) * val
            psum += (prev - _time) * power
            prev = _time
        span = end - _time
        if span != 0:
            return (_time, item, vsum / span, min(vals), max(vals), psum / span)
        else:
            return (_time, item, val, min(vals), max(vals), power)

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
            logger.warning("DB select: unkown time frame '{0}'".format(frame))
        return ts

    def _fetchone(self, *query):
        if not self._fdb_lock.acquire(timeout=2):
            return
        if not self.connected:
            self._fdb_lock.release()
            return
        try:
            reply = self._fdb.execute(*query).fetchone()
        except Exception as e:
            logger.warning("SQLite: Problem with '{0}': {1}".format(query, e))
            reply = None
        finally:
            self._fdb_lock.release()
        return reply

    def _fetchall(self, *query):
        if not self._fdb_lock.acquire(timeout=2):
            return
        if not self.connected:
            self._fdb_lock.release()
            return
        try:
            reply = self._fdb.execute(*query).fetchall()
        except Exception as e:
            logger.warning("SQLite: Problem with '{0}': {1}".format(query, e))
            reply = None
        finally:
            self._fdb_lock.release()
        return reply

    def _pack(self):
        insert = []
        delete = []
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            logger.debug("SQLite: pack database")
            for entry in self.periods:
                now = self._timestamp(self._sh.now())
                prev = {}
                period, granularity = entry
                period = int(now - period * 24 * 3600 * 1000)
                granularity = int(granularity * 3600 * 1000)
                for row in self._fdb.execute(self._pack_query.format(period, granularity)):
                    gid, gtime, gavg, gpower, item, vmin, vmax = row
                    gtime = gtime.split(',')
                    if len(gtime) == 1:  # ignore
                        prev[item] = gtime[0]
                        continue
                    if item not in prev:
                        upper = now
                    else:
                        upper = prev[item]
                    # pack !!!
                    delete = gid
                    gavg = gavg.split(',')
                    gpower = gpower.split(',')
                    _time, _avg, _power = self.__pack(gtime, gavg, gpower, upper)
                    insert = (_time, item, _avg, vmin, vmax, _power)
                    self._fdb.execute("INSERT INTO history VALUES (?,?,?,?,?,?);", insert)
                    self._fdb.execute("DELETE FROM history WHERE rowid in ({0});".format(delete))
                    self._fdb.commit()
                    prev[item] = gtime[0]
            self._fdb.execute("VACUUM;")
            self._fdb.execute("PRAGMA shrink_memory;")
        except Exception as e:
            logger.exception("problem packing sqlite database: {} period: {} type: {}".format(e, period, type(period)))
            self._fdb.rollback()
        finally:
            self._fdb_lock.release()

    def __pack(self, gtime, gavg, gpower, end):
        asum = 0.0
        psum = 0.0
        end = int(end)
        prev = end
        tuples = []
        for i, _time in enumerate(gtime):
            tuples.append((int(_time), float(gavg[i]), float(gpower[i])))
        for _time, _avg, _power in sorted(tuples, reverse=True):
            asum += (prev - _time) * _avg
            psum += (prev - _time) * _power
            prev = _time
        span = end - _time
        if span != 0:
            return (_time, asum / span, psum / span)
        else:
            return (_time, _avg, _power)

    def _series(self, func, start, end='now', count=100, ratio=1, update=False, step=None, sid=None, item=None):
        if sid is None:
            sid = item + '|' + func + '|' + start + '|' + end
        istart = self._get_timestamp(start)
        iend = self._get_timestamp(end)
        prev = self._fetchone("SELECT time from history WHERE item='{0}' AND time <= {1} ORDER BY time DESC LIMIT 1".format(item, istart))
        if not prev:
            first = istart
        else:
            first = prev[0]
        where = " from history WHERE item='{0}' AND time >= {1} AND time <= {2}".format(item, first, iend)
        if step is None:
            if count != 0:
                step = (iend - istart) / count
            else:
                step = (iend - istart)
        reply = {'cmd': 'series', 'series': None, 'sid': sid}
        reply['params'] = {'update': True, 'item': item, 'func': func, 'start': iend, 'end': end, 'step': step, 'sid': sid}
        reply['update'] = self._sh.now() + datetime.timedelta(seconds=int(step / 1000))
        where += " GROUP by CAST((time / {0}) AS INTEGER)".format(step)
        if func == 'avg':
            query = "SELECT CAST(AVG(time) AS INTEGER), ROUND(AVG(avg), 2)" + where + " ORDER BY time DESC"
        elif func == 'min':
            query = "SELECT CAST(AVG(time) AS INTEGER), MIN(vmin)" + where
        elif func == 'max':
            query = "SELECT CAST(AVG(time) AS INTEGER), MAX(vmax)" + where
        elif func == 'on':
            query = "SELECT CAST(AVG(time) AS INTEGER), ROUND(AVG(power), 2)" + where + " ORDER BY time DESC"
        else:
            raise NotImplementedError
        tuples = self._fetchall(query)
        if not tuples:
            if not update:
                reply['series'] = [(iend, 0)]
            return reply
        tuples = [(istart, t[1]) if first == t[0] else t for t in tuples]  # replace 'first' time with 'start' time
        tuples = sorted(tuples)
        lval = tuples[-1][1]
        tuples.append((iend, lval))  # add end entry with last valid entry
        if update:  # remove first entry
            tuples = tuples[1:]
        reply['series'] = tuples
        return reply

    def _single(self, func, start, end='now', item=None):
        start = self._get_timestamp(start)
        end = self._get_timestamp(end)
        prev = self._fetchone("SELECT time from history WHERE item = '{0}' AND time <= {1} ORDER BY time DESC LIMIT 1".format(item, start))
        if prev is None:
            first = start
        else:
            first = prev[0]
        where = " from history WHERE item='{0}' AND time >= {1} AND time < {2}".format(item, first, end)
        if func == 'avg':
            query = "SELECT AVG(avg)" + where
        elif func == 'min':
            query = "SELECT MIN(vmin)" + where
        elif func == 'max':
            query = "SELECT MAX(vmax)" + where
        elif func == 'on':
            query = "SELECT AVG(power)" + where
        else:
            logger.warning("Unknown export function: {0}".format(func))
            return
        tuples = self._fetchall(query)
        if tuples is None:
            return
        return tuples[0][0]

    def _timestamp(self, dt):
        return int(time.mktime(dt.timetuple())) * 1000 + int(dt.microsecond / 1000)
