#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Serge Wagener (Foxi352)
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
#  along with SmartHomeNG If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import threading
import time
import datetime
import functools
import json

from importlib.util import find_spec

from lib.model.smartplugin import SmartPlugin

from sqlalchemy import create_engine, __version__, Column, BigInteger, Integer, String, Numeric, Float, cast
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.serializer import dumps, loads
from sqlalchemy.orm import sessionmaker, class_mapper
from sqlalchemy.pool import StaticPool


class Database(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.2"
    _buffer_time = 60 * 1000

    # Declare classes to store data
    Base = declarative_base()

    class ItemStore(Base):
        __tablename__ = "num"
        __table_args__ = {'mysql_collate': 'utf8_general_ci'}
        # id = Column(BigInteger, primary_key=True)
        _start = Column(BigInteger)
        _item = Column(String(255), index=True)
        _dur = Column(BigInteger)
        _avg = Column(Float)
        _min = Column(Float)
        _max = Column(Float)
        _on = Column(Float)
        __mapper_args__ = {'primary_key': [_start, _item]}

    class ItemCache(Base):
        __tablename__ = "cache"
        __table_args__ = {'mysql_collate': 'utf8_general_ci'}
        _item = Column(String(255), primary_key=True)
        _start = Column(BigInteger)
        _value = Column(Float)

    def __init__(self, smarthome, engine="sqlite", database="var/db/smarthome.db", host=None, port=None, username=None, password=None):
        self._sh = smarthome
        self.connected = False
        self._buffer = {}
        self._buffer_lock = threading.Lock()
        self._fdb_lock = threading.Lock()
        self._fdb_lock.acquire()
        self._engine = engine
        self._database = database
        self.logger = logging.getLogger(__name__)

        # if engine = mysql then force use of PyMySql driver. If module does not exist instruct user to install it.
        if self._engine == 'mysql':
            if find_spec('pymysql') is None:
                self.logger.error("Database: PyMySql not found. run 'pip3 install pymysql' if you plan to use MySQL or MariaDB !")
            self._engine += '+pymysql'
        # If credentials in config concatenate them for URI use
        if (username is not None) and (password is not None):
            self._credentials = username + ":" + password
        else:
            self._credentials = ""
        # If host and port in config concatenate them for URI use, ignore them if engine = sqlite
        if (host is not None) and (self._engine != 'sqlite'):
            self._host = "@" + host
            if (port is not None):
                self._host += ":" + port
        else:
            self._host = ""
        # Assemble URI
        self._uri = self._engine + "://" + self._credentials + self._host + "/" + self._database
        if self._engine == 'sqlite':
            self._uri += '?check_same_thread=False'
        self.logger.info("Database: SqlAlchemy {0} using {1} database '{2}'".format(__version__, self._engine, self._database))
        self.logger.debug("Database: URI " + self._uri)
        try:
            # db = create_engine(self._uri, poolclass=StaticPool)
            db = create_engine(self._uri, pool_recycle=14400)
            Session = sessionmaker(bind=db)
            self.session = Session()
            self.connected = True
            # For debugging purposes, disable in production version. Prints out all DB sql queries.
            # db.echo = True
            self.Base.metadata.bind = db
            self.Base.metadata.create_all()
        except Exception as e:
            self.logger.error("Database: Error while establishing database connection: {}".format(e))
            self.connected = False
        finally:
            self._fdb_lock.release()
        minute = 60 * 1000
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        month = 30 * day
        year = 365 * day
        self._frames = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}
        self._times = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}

    def cleanup(self):
        """
        Clean history and cache from items that do no longer exist
        """
        current_items = [item.id() for item in self._buffer]
        db_items = self.session.query(self.ItemStore).group_by(self.ItemStore._item).all()
        # Clear orphans from num table
        if db_items:
            for item in db_items:
                if item._item not in current_items:
                    self.logger.info("Database: deleting value entries for {}".format(item._item))
                    self.session.query(self.ItemStore).filter(self.ItemStore._item == item._item).delete()
                    self.session.commit()
        # Clear orphans from cache table
        db_items = self.session.query(self.ItemCache).group_by(self.ItemCache._item).all()
        if db_items:
            for item in db_items:
                if item._item not in current_items:
                    self.logger.info("Database: deleting cache entries for {}".format(item._item))
                    self.session.query(self.ItemCache).filter(self.ItemCache._item == item._item).delete()
                    self.session.commit()

    def serialize(self, model):
        """Transforms a model into a dictionary which can be dumped to JSON."""
        columns = [c.key for c in class_mapper(model.__class__).columns]
        return dict((c, getattr(model, c)) for c in columns)

    def dump(self, path):
        """
        dump database into file (TODO)
        """
        if not self._fdb_lock.acquire(timeout=2):
            return

        self.logger.info("Database: Dumping 'cache' table".format(path))
        serialized_cache = [
            self.serialize(item)
            for item in self.session.query(self.ItemCache)
        ]

        self.logger.info("Database: Dumping 'nums' table".format(path))
        serialized_store = [
            self.serialize(item)
            for item in self.session.query(self.ItemStore)
        ]

        path = path.rstrip('//') + '/'
        with open(path + 'dump_cache.json', 'w') as outfile:
            json.dump(serialized_cache, outfile)
        with open(path + 'dump_num.json', 'w') as outfile:
            json.dump(serialized_store, outfile)
        self.logger.info("Database: Dumping done. Find your files in path '{0}'".format(path))
        self._fdb_lock.release()

    def move(self, old, new):
        """
        rename / move item including history and cache
        """
        self.logger.info("Database: renaming {0} to {1}".format(old, new))
        self.session.query(self.ItemStore).filter(self.ItemStore._item == old).update({self.ItemStore._item: new})
        self.session.query(self.ItemCache).filter(self.ItemCache._item == old).update({self.ItemCache._item: new})
        self.session.commit()

    def parse_item(self, item):
        if 'database' in item.conf:
            # ignore items with database parameter if no database connected
            if not self.connected:
                return None
            # Check if item type is supported by this plugin
            if item.type() not in ['num', 'bool']:
                self.logger.warning("Database: only 'num' and 'bool' currently supported. Item: {} ".format(item.id()))
                return
            # If item exists in cache load last value, if not create it
            start = time.time()  # REMOVE
            cache = self.session.query(self.ItemCache).filter_by(_item=item.id()).first()
            self.logger.debug('1 - Execution time: ' + str((time.time() - start) * 1000) + ' milliseconds')  # REMOVE
            if cache is None:
                self.logger.debug("Database: Items {0} does not exist in cache, creating it".format(item.id()))
                last_change = self._timestamp(self._sh.now())
                item._database_last = last_change
                newItem = self.ItemCache(_item=item.id(), _start=last_change, _value=float(item()))
                self.session.add(newItem)
                self.session.commit()
            else:
                self.logger.debug("Database: Loading last value for item {0} from cache".format(item.id()))
                last_change = cache._start
                value = cache._value
                item._database_last = last_change
                last_change = self._datetime(last_change)
                self.logger.debug('2 - Execution time: ' + str((time.time() - start) * 1000) + ' milliseconds')  # REMOVE
                storedItem = self.session.query(self.ItemStore).filter_by(_item=item.id()).order_by(self.ItemStore._start.desc()).first()

                self.logger.debug('3 - Execution time: ' + str((time.time() - start) * 1000) + ' milliseconds')  # REMOVE
                if storedItem is not None:
                    prev_change = self._datetime(storedItem._start)
                    item.set(value, 'Database', prev_change=prev_change, last_change=last_change)
            self._buffer[item] = []
            item.series = functools.partial(self._series, item=item.id())
            item.db = functools.partial(self._single, item=item.id())
            end = time.time()  # REMOVE
            self.logger.debug('Execution time: ' + str((end - start) * 1000) + ' milliseconds')  # REMOVE
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
            self.session.commit()
            self.session.close()
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
        if _end - item._database_last > self._buffer_time:
            self._insert(item)
        if not self._fdb_lock.acquire(timeout=2):
            return
        # update cache with current value
        itemForUpdate = self.session.query(self.ItemCache).filter_by(_item=item.id()).first()
        if itemForUpdate is not None:
            try:
                itemForUpdate._start = _end
                itemForUpdate._value = float(item())
                self.session.commit()
            except Exception as e:
                self.logger.debug("Database: Error updating cache for item {}: {}".format(item.id(), e))
                self.session.rollback()
        self._fdb_lock.release()

    def _datetime(self, ts):
        return datetime.datetime.fromtimestamp(ts / 1000, self._sh.tzinfo())

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
            self.logger.warning("Database: unkown time frame '{0}'".format(frame))
        return ts

    def _insert(self, item):
        if not self._fdb_lock.acquire(timeout=2):
            return
        tuples = sorted(self._buffer[item])
        tlen = len(tuples)
        self._buffer[item] = self._buffer[item][tlen:]
        item._database_last = self._timestamp(item.last_change())
        try:
            if tlen == 1:
                _start, _dur, _avg, _on = tuples[0]
                insert = (_start, item.id(), _dur, _avg, _avg, _avg, _on)
                newItem = self.ItemStore(_start=_start, _item=item.id(), _dur=_dur, _avg=_avg, _min=_avg, _max=_avg, _on=_on / _dur)
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
                newItem = self.ItemStore(_start=_start, _item=item.id(), _dur=_dur, _avg=_avg / _dur, _min=min(_vals), _max=max(_vals), _on=_on / _dur)
            else:  # no tuples
                return
            self.session.add(newItem)
            self.session.commit()
        except Exception as e:
            self.logger.warning("Database: problem updating {}: {}".format(item.id(), e))
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
        if not self._fdb_lock.acquire(timeout=2):
            return
        try:
            if not self.connected:
                return
            if func == 'avg':
                items = self.session.query(sqlfunc.min(self.ItemStore._start), sqlfunc.round(sqlfunc.sum(self.ItemStore._avg * self.ItemStore._dur) / sqlfunc.sum(self.ItemStore._dur), 2)) \
                    .filter(self.ItemStore._item == item) \
                    .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                    .filter(self.ItemStore._start <= iend) \
                    .group_by(cast(self.ItemStore._start / 864000, Integer)) \
                    .order_by(self.ItemStore._start.asc()) \
                    .all()
            elif func == 'min':
                items = self.session.query(sqlfunc.min(self.ItemStore._start), sqlfunc.min(self.ItemStore._min)) \
                    .filter(self.ItemStore._item == item) \
                    .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                    .filter(self.ItemStore._start <= iend) \
                    .group_by(cast(self.ItemStore._start / 864000, Integer)) \
                    .all()
            elif func == 'max':
                items = self.session.query(sqlfunc.min(self.ItemStore._start), sqlfunc.max(self.ItemStore._max)) \
                    .filter(self.ItemStore._item == item) \
                    .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                    .filter(self.ItemStore._start <= iend) \
                    .group_by(cast(self.ItemStore._start / 864000, Integer)) \
                    .all()
            elif func == 'on':
                items = self.session.query(sqlfunc.min(self.ItemStore._start), sqlfunc.round(sqlfunc.sum(self.ItemStore._on * self.ItemStore._dur) / sqlfunc.sum(self.ItemStore._dur), 2)) \
                    .filter(self.ItemStore._item == item) \
                    .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                    .filter(self.ItemStore._start <= iend) \
                    .group_by(cast(self.ItemStore._start / 864000, Integer)) \
                    .order_by(self.ItemStore._start.asc()) \
                    .all()
            else:
                raise NotImplementedError
        except Exception as e:
            self.logger.error("Database: Error {0}".format(e))
            reply = None
            return reply
        finally:
            self._fdb_lock.release()

        _item = self._sh.return_item(item)
        if self._buffer[_item] != [] and end == 'now':
            self._insert(_item)
        if items:
            if istart > items[0][0]:
                items[0] = (istart, items[0][1])
            if end != 'now':
                items.append((iend, items[-1][1]))
        else:
            items = []
        item_change = self._timestamp(_item.last_change())
        if item_change < iend:
            value = float(_item())
            if item_change < istart:
                items.append((istart, value))
            elif init:
                items.append((item_change, value))
            if init:
                items.append((iend, value))
        if items:
            reply['series'] = items
        return reply

    def _single(self, func, start, end='now', item=None):
        istart = self._get_timestamp(start)
        iend = self._get_timestamp(end)
        if func == 'avg':
            items = self.session.query(sqlfunc.round(sqlfunc.sum(self.ItemStore._avg * self.ItemStore._dur) / sqlfunc.sum(self.ItemStore._dur), 2)) \
                .filter(self.ItemStore._item == item) \
                .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                .filter(self.ItemStore._start <= iend) \
                .all()
        elif func == 'min':
            items = self.session.query(sqlfunc.min(self.ItemStore._min)) \
                .filter(self.ItemStore._item == item) \
                .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                .filter(self.ItemStore._start <= iend) \
                .all()
        elif func == 'max':
            items = self.session.query(sqlfunc.max(self.ItemStore._max)) \
                .filter(self.ItemStore._item == item) \
                .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                .filter(self.ItemStore._start <= iend) \
                .all()
        elif func == 'on':
            items = self.session.query(sqlfunc.round(sqlfunc.sum(self.ItemStore._on * self.ItemStore._dur) / sqlfunc.sum(self.ItemStore._dur), 2)) \
                .filter(self.ItemStore._item == item) \
                .filter(self.ItemStore._start + self.ItemStore._dur >= istart) \
                .filter(self.ItemStore._start <= iend) \
                .all()
        else:
            self.logger.warning("Database: Unknown export function: {0}".format(func))
            return
        _item = self._sh.return_item(item)
        if self._buffer[_item] != [] and end == 'now':
            self._insert(_item)
        tuples = items
        if tuples is None:
            return
        return tuples[0][0]

    def _timestamp(self, dt):
        return int(time.mktime(dt.timetuple())) * 1000 + int(dt.microsecond / 1000)
