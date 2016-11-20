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
import functools
import time
import threading
import lib.db

from lib.model.smartplugin import SmartPlugin

class DbLog(SmartPlugin):

    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION = '1.3.0'

    # SQL queries: {item} = item table name, {log} = log table name
    # time, item_id, val_str, val_num, val_bool, changed
    _setup = {
      '1' : ["CREATE TABLE {log} (time BIGINT, item_id INTEGER, duration BIGINT, val_str TEXT, val_num REAL, val_bool BOOLEAN, changed BIGINT);", "DROP TABLE {log};"],
      '2' : ["CREATE TABLE {item} (id INTEGER, name varchar(255), time BIGINT, val_str TEXT, val_num REAL, val_bool BOOLEAN, changed BIGINT);", "DROP TABLE {item};"],
      '3' : ["CREATE UNIQUE INDEX {log}_{item}_id_time ON {log} (item_id, time);", "DROP INDEX {log}_{item}_id_time;"],
      '4' : ["CREATE INDEX {log}_{item}_id_changed ON {log} (item_id, changed);", "DROP INDEX {log}_{item}_id_changed;"],
      '5' : ["CREATE UNIQUE INDEX {item}_id ON {item} (id);", "DROP INDEX {item}_id;"],
      '6' : ["CREATE INDEX {item}_name ON {item} (name);", "DROP INDEX {item}_name;"]
    }

    def __init__(self, smarthome, db, connect, prefix="", cycle=60):
        self._sh = smarthome
        self._dump_cycle = int(cycle)
        self._name = self.get_instance_name()
        self._tables = {table: table if prefix == "" else prefix + "_" + table for table in ["log", "item"]}
        self._buffer = {}
        self._buffer_lock = threading.Lock()
        self._dump_lock = threading.Lock()

        self._db = lib.db.Database(("" if prefix == "" else prefix.capitalize() + "_") + "DbLog", self._sh.dbapi(db), connect)
        self._db.connect()
        self._db.setup({i: [self._prepare(query[0]), self._prepare(query[1])] for i, query in self._setup.items()})

        smarthome.scheduler.add('DbLog dump ' + self._name + ("" if prefix == "" else " [" + prefix + "]"), self._dump, cycle=self._dump_cycle, prio=5)

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'dblog'):
            self._buffer[item] = []
            item.series = functools.partial(self._series, item=item.id())
            item.db = functools.partial(self._single, item=item.id())
            item.dblog = self

            cur = self._db.cursor()
            id = self.id(item, create=False, cur=cur)
            cache = None if id is None else self.readItem(id, cur=cur)
            if cache is not None:
                last_change = cache[2]
                value = self._item_value_tuple_rev(item.type(), cache[3:6])
                last_change = self._datetime(last_change)
                prev_change = self._db.fetchone(self._prepare('SELECT time from {log} WHERE item_id = :id ORDER BY time DESC LIMIT 1'), {'id':id})
                if value is not None and prev_change is not None:
                    prev_change = self._datetime(prev_change[0])
                    item.set(value, 'DbLog', prev_change=prev_change, last_change=last_change)
            cur.close()
            return self.update_item
        else:
            return None

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self._dump(True)
        self._db.close()

    def update_item(self, item, caller=None, source=None, dest=None):
        acl = 'rw' if not self.has_iattr(item.conf, 'dblog_acl') else self.get_iattr_value(item.conf, 'dblog_acl')
        if acl is 'rw':
            start = self._timestamp(item.prev_change())
            end = self._timestamp(item.last_change())

            self._buffer[item].append((start, end - start, item.prev_value()))

    def id(self, item, create=True, cur=None):
        id = self._db.fetchone(self._prepare("SELECT id FROM {item} where name = :name;"), {'name':item.id()}, cur=cur)

        if id == None and create == True:
            id = [self.insertItem(item.id(), cur)]

        return None if id == None else int(id[0])

    def insertItem(self, name, cur=None):
        id = self._db.fetchone(self._prepare("SELECT MAX(id) FROM {item};"), {}, cur=cur)
        self._db.execute(self._prepare("INSERT INTO {item}(id, name) VALUES(:id, :name);"), {'id':1 if id[0] == None else id[0]+1, 'name':name}, cur=cur)
        id = self._db.fetchone(self._prepare("SELECT id FROM {item} where name = :name;"), {'name':name}, cur=cur)
        return int(id[0])

    def updateItem(self, id, time, duration=0, val=None, it=None, changed=None, cur=None):
        params = {'id':id, 'time':time, 'changed':changed}
        params.update(self._item_value_tuple(it, val))
        self._db.execute(self._prepare("UPDATE {item} SET time = :time, val_str = :val_str, val_num = :val_num, val_bool = :val_bool, changed = :changed WHERE id = :id;"), params, cur=cur)

    def readItem(self, id, cur=None):
        params = {'id':id}
        return self._db.fetchone(self._prepare("SELECT id, name, time, val_str, val_num, val_bool, changed from {item} WHERE id = :id;"), params, cur=cur)

    def insertLog(self, id, time, duration=0, val=None, it=None, changed=None, cur=None):
        params = {'id':id, 'time':time, 'changed':changed, 'duration':duration}
        params.update(self._item_value_tuple(it, val))
        self._db.execute(self._prepare("INSERT INTO {log}(item_id, time, val_str, val_num, val_bool, duration, changed) VALUES (:id,:time,:val_str,:val_num,:val_bool,:duration,:changed);"), params, cur=cur)

    def updateLog(self, id, time, duration=0, val=None, it=None, changed=None, cur=None):
        params = {'id':id, 'time':time, 'changed':changed, 'duration':duration}
        params.update(self._item_value_tuple(it, val))
        self._db.execute(self._prepare("UPDATE {log} SET duration = :duration, val_str = :val_str, val_num = :val_num, val_bool = :val_bool, changed = :changed WHERE item_id = :id AND time = :time;"), params, cur=cur)

    def readLog(self, id, time, cur = None):
        params = {'id':id, 'time':time}
        return self._db.fetchall(self._prepare("SELECT time, item_id, duration, val_str, val_num, val_bool, changed FROM {log} WHERE item_id = :id AND time = :time;"), params, cur=cur)

    def readLogs(self, id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None):
        condition, params = self._slice_condition(id, time=time, time_start=time_start, time_end=time_end, changed=changed, changed_start=changed_start, changed_end=changed_end)
        self._db.execute(self._prepare("SELECT time, item_id, duration, val_str, val_num, val_bool, changed FROM {log} WHERE " + condition), params, cur=cur)

    def deleteLog(self, id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None, cur = None):
        condition, params = self._slice_condition(id, time=time, time_start=time_start, time_end=time_end, changed=changed, changed_start=changed_start, changed_end=changed_end)
        self._db.execute(self._prepare("DELETE FROM {log} WHERE " + condition), params, cur=cur)

    def _slice_condition(self, id, time = None, time_start = None, time_end = None, changed = None, changed_start = None, changed_end = None):
        params = {
          'id'            : id,
          'time'          : time,          'time_flag'          : 1 if time          == None else 0,
          'time_start'    : time_start,    'time_start_flag'    : 1 if time_start    == None else 0,
          'time_end'      : time_end,      'time_end_flag'      : 1 if time_end      == None else 0,
          'changed'       : changed,       'changed_flag'       : 1 if changed       == None else 0,
          'changed_start' : changed_start, 'changed_start_flag' : 1 if changed_start == None else 0,
          'changed_end'   : changed_end,   'changed_end_flag'   : 1 if changed_end   == None else 0
        }

        condition = "(item_id = :id                                      ) AND " + \
                    "(time    = :time          OR 1 = :time_flag         ) AND " + \
                    "(time    > :time_start    OR 1 = :time_start_flag   ) AND " + \
                    "(time    < :time_end      OR 1 = :time_end_flag     ) AND " + \
                    "(changed = :changed       OR 1 = :changed_flag      ) AND " + \
                    "(changed > :changed_start OR 1 = :changed_start_flag) AND " + \
                    "(changed < :changed_end   OR 1 = :changed_end_flag  );    "
        return (condition, params)

    def db(self):
        return self._db

    def _item_value_tuple(self, item_type, item_val):
        if item_type == 'num':
           val_str = None
           val_num = float(item_val)
           val_bool = int(bool(item_val))
        elif item_type == 'bool':
           val_str = None
           val_num = float(item_val)
           val_bool = int(bool(item_val))
        else:
           val_str = str(item_val)
           val_num = None
           val_bool = int(bool(item_val))

        return {'val_str':val_str, 'val_num':val_num, 'val_bool':val_bool}

    def _item_value_tuple_rev(self, item_type, item_val_tuple):
        if item_type == 'num':
           return None if item_val_tuple[1] is None else float(item_val_tuple[1])
        elif item_type == 'bool':
           return None if item_val_tuple[2] is None else bool(int(item_val_tuple[2]))
        else:
           return None if item_val_tuple[0] is None else str(item_val_tuple[0])

    def _datetime(self, ts):
        return datetime.datetime.fromtimestamp(ts / 1000, self._sh.tzinfo())

    def _prepare(self, query):
        return query.format(**self._tables)

    def _dump(self, finalize=False, items=None):
        if self._dump_lock.acquire(timeout=60) == False:
            self.logger.warning('Skipping dump, since other dump running!')
            return

        self.logger.debug('Starting dump')

        if items == None:
            self._buffer_lock.acquire()
            items = list(self._buffer.keys())
            self._buffer_lock.release()

        for item in items:
            self._buffer_lock.acquire()
            tuples = self._buffer[item]
            self._buffer[item] = self._buffer[item][len(tuples):]
            self._buffer_lock.release()

            if len(tuples) or finalize:

                # Test connectivity
                if self._db.verify(5) == 0:
                    self.logger.error("DbLog: Connection not recovered, skipping dump");
                    self._dump_lock.release()
                    return

                # Can't lock, restore data
                if not self._db.lock(300):
                    self._buffer_lock.acquire()
                    if item in self._buffer:
                        self._buffer[item] = tuples + self._buffer[item]
                    else:
                        self._buffer[item] = tuples
                    self._buffer_lock.release()
                    if finalize:
                        self.logger.error("DbLog: can't dump {} items due to fail to acquire lock!".format(len(self._buffer)))
                    else:
                        self.logger.error("DbLog: can't dump {} items due to fail to acquire lock - will try on next dump".format(len(self._buffer)))
                    self._dump_lock.release()
                    return

                cur = None
                try:
                    changed = self._timestamp(self._sh.now())

                    # Get current values of item
                    start = self._timestamp(item.last_change())
                    end = self._timestamp(self._sh.now())
                    val = item()

                    # When finalizing (e.g. plugin shutdown) add current value to item and log
                    if finalize:
                        _update = (end, val, changed)

                        current = (start, end - start, val)
                        tuples.append(current)

                    else:
                        _update = (start, val, changed)

                    cur = self._db.cursor()
                    id = self.id(item, cur=cur)

                    # Dump tuples
                    self.logger.debug('Dumping {}/{} with {} values'.format(item.id(), id, len(tuples)))

                    for t in tuples:
                        if len(self.readLog(id, t[0], cur)):
                            self.updateLog(id, t[0], t[1], t[2], item.type(), changed, cur)
                        else:
                            self.insertLog(id, t[0], t[1], t[2], item.type(), changed, cur)

                    self.updateItem(id, _update[0], None, _update[1], item.type(), _update[2], cur)

                    cur.close()
                    cur = None

                    self._db.commit()
                except Exception as e:
                    self.logger.warning("DbLog: problem updating {}: {}".format(item.id(), e))
                    self._db.rollback()
                finally:
                    if cur is not None:
                        cur.close()
                self._db.release()
        self.logger.debug('Dump completed')
        self._dump_lock.release()

    def _series(self, func, start, end='now', count=100, ratio=1, update=False, step=None, sid=None, item=None):
        init = not update
        if sid is None:
            sid = item + '|' + func + '|' + start + '|' + end  + '|' + str(count)
        istart = self._parse_ts(start)
        iend = self._parse_ts(end)
        if step is None:
            if count != 0:
                step = int((iend - istart) / int(count))
            else:
                step = iend - istart
        reply = {'cmd': 'series', 'series': None, 'sid': sid}
        reply['params'] = {'update': True, 'item': item, 'func': func, 'start': iend, 'end': end, 'step': step, 'sid': sid}
        reply['update'] = self._sh.now() + datetime.timedelta(seconds=int(step / 1000))
        where = self._prepare(" FROM {log} WHERE item_id = :id AND time > (SELECT COALESCE(MAX(time), 0) FROM {log} WHERE item_id = :id AND time < :time_start) AND time <= :time_end AND time + duration > (SELECT COALESCE(MAX(time), 0) FROM {log} WHERE item_id = :id AND time < :time_start) GROUP BY ROUND(time / :step)")
        if func == 'avg':
            query = "SELECT MIN(time), ROUND(AVG(val_num * duration) / AVG(duration), 2)" + where + " ORDER BY time ASC"
        elif func == 'min':
            query = "SELECT MIN(time), MIN(val_num)" + where
        elif func == 'max':
            query = "SELECT MIN(time), MAX(val_num)" + where
        elif func == 'on':
            query = "SELECT MIN(time), ROUND(SUM(val_bool * duration) / SUM(duration), 2)" + where + " ORDER BY time ASC"
        else:
            raise NotImplementedError
        _item = self._sh.return_item(item)
        if self._buffer[_item] != []:
            self._dump(items=[_item])
        tuples = self._fetch(query, _item, {'id':'<id>', 'time_start':istart, 'time_end':iend, 'step':step})
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
        reply['series'] = tuples
        return reply

    def _single(self, func, start, end='now', item=None):
        start = self._parse_ts(start)
        end = self._parse_ts(end)
        where = self._prepare(" FROM {log} WHERE item_id = :id AND time > (SELECT COALESCE(MAX(time), 0) FROM {log} WHERE item_id = :id AND time < :time_start) AND time <= :time_end AND time + duration > (SELECT COALESCE(MAX(time), 0) FROM {log} WHERE item_id = :id AND time < :time_start)")
        if func == 'avg':
            query = "SELECT ROUND(AVG(val_num * duration) / AVG(duration), 2)" + where
        elif func == 'min':
            query = "SELECT MIN(val_num)" + where
        elif func == 'max':
            query = "SELECT MAX(val_num)" + where
        elif func == 'on':
            query = "SELECT ROUND(SUM(val_bool * duration) / SUM(duration), 2)" + where
        else:
            self.logger.warning("Unknown export function: {0}".format(func))
            return
        _item = self._sh.return_item(item)
        if self._buffer[_item] != []:
            self._dump(items=[_item])
        tuples = self._fetch(query, _item, {'id':'<id>', 'time_start':start, 'time_end':end})
        if tuples is None:
            return
        return tuples[0][0]

    def _fetch(self, query, item, params):
        if self._db.verify(5) == 0:
            self.logger.error("DbLog: Connection not recovered")
            return None
        if not self._db.lock(300):
            self.logger.error("DbLog: can't fetch data due to fail to acquire lock")
            return None
        tuples = None
        try:
            id = self.id(item, create=False)
            params = {n:id if params[n] == '<id>' else params[n] for n in params}
            tuples = self._db.fetchall(query, params)
        except Exception as e:
            self.logger.warning("DbLog: Error fetching data for {}: {}".format(item, e))
        self._db.release()
        self.logger.debug("Fetch {} (args {}): {}".format(query, params, tuples))
        return None if tuples is None else list(tuples)

    def _parse_ts(self, frame):
        minute = 60 * 1000
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        month = 30 * day
        year = 365 * day

        _frames = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}
        try:
            return int(frame)
        except:
            pass
        ts = self._timestamp(self._sh.now())
        if frame == 'now':
            fac = 0
            frame = 0
        elif frame[-1] in _frames:
            fac = _frames[frame[-1]]
            frame = frame[:-1]
        else:
            return frame
        try:
            ts = ts - int(float(frame) * fac)
        except:
            self.logger.warning("DbLog: Unknown time frame '{0}'".format(frame))
        return ts

    def _timestamp(self, dt):
        return int(time.mktime(dt.timetuple())) * 1000 + int(dt.microsecond / 1000)
