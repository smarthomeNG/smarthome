#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2014 Marcus Popp                          marcus@popp.mx
# Copyright 2016- Christian Straßburg
# Copyright 2017 Bernd Meiners                      Bernd.Meiners@mail.de
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

import logging
import time
import datetime
import calendar
import sys
import traceback
import threading
import random
import inspect
import re

from lib.shtime import Shtime
from lib.item import Items
from lib.model.smartplugin import SmartPlugin

import dateutil.relativedelta
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import tzutc


# following modules) are imported to have those functions available during logic execution
import gc  # noqa
import os
import math
import types
import subprocess

try:
    from lib.module import Modules
    _lib_modules_found = True
except:
    _lib_modules_found = False


logger = logging.getLogger(__name__)

_scheduler_instance = None    # Pointer to the initialized instance of the scheduler class (for use by static methods)


class _PriorityQueue:
    """
    Implements a queue which contain tuples of priority and data sorted by priority.
    Lowest priority given will be the first candidate for a get from the queue, data can be anything
    """
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def insert(self, priority, data):
        """
        Add a tuple with priority and data into the queue
        :param priority: a positive integer or a tuple where lowest indicates the highest priority
        :param data: anything to be associated with the given priority
        """
        self.lock.acquire()
        lo = 0
        hi = len(self.queue)
        while lo < hi:
            mid = (lo + hi) // 2
            if priority < self.queue[mid][0]:
                hi = mid
            else:
                lo = mid + 1
        self.queue.insert(lo, (priority, data))
        self.lock.release()

    def get(self):
        """
        Returns the first tuple of the queue
        :return: tuple with priority and data or None if no entry is available in the queue
        """
        self.lock.acquire()
        try:
            return self.queue.pop(0)
        except IndexError:
            raise
        finally:
            self.lock.release()

    def qsize(self):
        return len(self.queue)


class Scheduler(threading.Thread):

    _workers = []
    _worker_num = 5
    _worker_max = 20
    _worker_delta = 60  # wait 60 seconds before adding another worker thread
    _scheduler = {}
    _runq = _PriorityQueue()            # holds tuples of priority and (name, obj, by, source, dest, value) for immediate execution
    _triggerq = _PriorityQueue()        # holds tuples of (datetime, priority) and (name, obj, by, source, dest, value)
                                        # to be put in the run queue when time is due

    _pluginname_prefix = 'plugins.'     # prefix for scheduler names

    def __init__(self, smarthome):
        threading.Thread.__init__(self, name='Scheduler')
        logger.info('Init Scheduler')
        self._sh = smarthome
        self._lock = threading.Lock()
        self._runc = threading.Condition()

        global _scheduler_instance
        if _scheduler_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical("A second 'scheduler' object has been created. There should only be ONE instance of class 'Scheduler'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _scheduler_instance = self

        self.shtime = Shtime.get_instance()
        self.items = Items.get_instance()
        self.mqtt = None


    # --------------------------------------------------------------------------------------------------
    #   Following (static) method of the class Scheduler implement the API for schedulers in SmartHomeNG
    # --------------------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the scheduler class, to be used to access the scheduler-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.scheduler import Scheduler
            scheduler = Scheduler.get_instance()

            # to access a method (eg. to trigger a logic):
            scheduler.trigger(...)


        :return: scheduler instance
        :rtype: object or None
        """
        if _scheduler_instance == None:
            return None
        else:
            return _scheduler_instance


    def get_worker_count(self):
        """
        Get number of worker threads initialized by scheduler

        :return: number of worker threads
        """
        return len(self._workers)


    def get_idle_worker_count(self):
        """
        Get number of idle worker threads

        :return: number of worker threads
        """
        idle_count = 0
        for w in self._workers:
            if w.name == 'idle':
                idle_count +=1
        return idle_count


    def get_worker_names(self):
        """
        Get names on non-idle worker threads

        :return: list with names of worker threads
        """
        worker_names = []
        for w in self._workers:
            if w.name != 'idle':
                worker_names.append(w.name)
        return worker_names


    def run(self):
        self.alive = True
        logger.debug("creating {0} workers".format(self._worker_num))
        for i in range(self._worker_num):
            self._add_worker()
        while self.alive:
            now = self.shtime.now()
            if self._runq.qsize() > len(self._workers):
                delta = now - self._last_worker
                if delta.seconds > self._worker_delta:
                    if len(self._workers) < self._worker_max:
                        self._add_worker()
                    else:
                        logger.error("Needing more worker threads than the specified maximum of {}!  ({} worker threads active)".format(self._worker_max, len(self._workers)))
                        tn = {}
                        # for t in threading.enumerate():
                        for t in self._workers:
                            tn[t.name] = tn.get(t.name, 0) + 1
                        logger.info('Worker-Threads: ' + ', '.join("{0}: {1}".format(k, v) for (k, v) in list(tn.items())))

                        if int(self._sh._restart_on_num_workers) < self._worker_max:
                            # do no restart
                            self._add_worker()
                        else:
                            if len(self._workers) < int(self._sh._restart_on_num_workers):
                                self._add_worker()
                            else:
                                logger.warning('Worker-Threads: ' + ', '.join("{0}: {1}".format(k, v) for (k, v) in list(tn.items())))
                                self._sh.restart('SmartHomeNG (scheduler started too many worker threads ({}))'.format(len(self._workers)))

            while self._triggerq.qsize() > 0:
                try:
                    (dt, prio), (name, obj, by, source, dest, value) = self._triggerq.get()
                except Exception as e:
                    logger.warning("Trigger queue exception: {0}".format(e))
                    break

                if dt < now:  # run it
                    self._runc.acquire()
                    self._runq.insert(prio, (name, obj, by, source, dest, value))
                    self._runc.notify()
                    self._runc.release()
                else:  # put last entry back and break while loop
                    self._triggerq.insert((dt, prio), (name, obj, by, source, dest, value))
                    break
            # For debugging
            # task_count = 0
            # for name in self._scheduler:
            #     task = self._scheduler[name]
            #     if task['next'] is not None:
            #         task_count += 1
            # End for debugging
            if not self._lock.acquire(timeout=1):
            #     logger.critical("Scheduler: Deadlock! - Task Count to enter run queue: {}".format(task_count))
                logger.critical("Scheduler: Deadlock!")
                continue
            for name in self._scheduler:
                task = self._scheduler[name]
                if task['next'] is not None:
                    if task['next'] < now:
                        self._runc.acquire()
                        self._runq.insert(task['prio'], (name, task['obj'], 'Scheduler', None, None, task['value']))
                        self._runc.notify()
                        self._runc.release()
                        task['next'] = None
                    else:
                        continue
                elif not task['active']:
                    continue
                else:
                    if task['cron'] is None and task['cycle'] is None:
                        continue
                    else:
                        self._next_time(name)
            self._lock.release()
            time.sleep(0.5)

    def stop(self):
        self.alive = False

    def trigger(self, name, obj=None, by='Logic', source=None, value=None, dest=None, prio=3, dt=None, from_smartplugin=False):
        """
        triggers the execution of a logic optional at a certain datetime given with dt

        :param name:
        :param obj:
        :param by:
        :param source:
        :param value:
        :param dest:
        :param prio:
        :param dt: a certain datetime
        :return: always None
        """
        name = self.check_caller(name, from_smartplugin)
        if obj is None:
            if name in self._scheduler:
                obj = self._scheduler[name]['obj']
            else:
                logger.warning("Logic name not found: {0}".format(name))
                return
        if name in self._scheduler:
            if not self._scheduler[name]['active']:
                logger.debug("Logic '{0}' deactivated. Ignoring trigger from {1} {2}".format(name, by, source))
                return
        if dt is None:
            logger.debug("Triggering {0} - by: {1} source: {2} dest: {3} value: {4}".format(name, by, source, dest, str(value)[:40]))
            self._runc.acquire()
            self._runq.insert(prio, (name, obj, by, source, dest, value))
            self._runc.notify()
            self._runc.release()
        else:
            if not isinstance(dt, datetime.datetime):
                logger.warning("Trigger: Not a valid timezone aware datetime for {0}. Ignoring.".format(name))
                return
            if dt.tzinfo is None:
                logger.warning("Trigger: Not a valid timezone aware datetime for {0}. Ignoring.".format(name))
                return
            logger.debug("Triggering {0} - by: {1} source: {2} dest: {3} value: {4} at: {5}".format(name, by, source, dest, str(value)[:40], dt))
            self._triggerq.insert((dt, prio), (name, obj, by, source, dest, value))

    def remove(self, name, from_smartplugin=False):
        """
        Remove a scheduler entry with given name. If a call is made from a SmartPlugin with an instance configuration
        the instance name is added to the name to be able to distinguish scheduler entries from different instances

        :param name: scheduler entry name to remove
        :param from_smartplugin:
        """
        self._lock.acquire()
        name = self.check_caller(name, from_smartplugin)
        logger.debug("remove scheduler entry with name:{0}".format(name))
        if name in self._scheduler:
            del(self._scheduler[name])
        self._lock.release()

    def check_caller(self, name, from_smartplugin=False):
        """
        Checks the calling stack if the calling function (one of get, change, remove, trigger) itself was called by
        a smartplugin instance. If there is an instance name of the calling smartplugin then the instance name of that
        calling smartplugin is appended to the name

        :param name: the name of a scheduler entry
        :param from_smartplugin:
        :return: returns either the name or name combined with instance name
        """
        stack = inspect.stack()
        try:
            obj = stack[2][0].f_locals["self"]
            if isinstance(obj, SmartPlugin):
                iname = obj.get_instance_name()
                if iname != '':
#                    if not (iname).startswith(self._pluginname_prefix):
                    if not from_smartplugin:
                        if not str(name).endswith('_' + iname):
                            name = name + '_' + obj.get_instance_name()
        except:
            pass
        return name

    def return_next(self, name, from_smartplugin=False):
        # name = self.check_caller(name, from_smartplugin)   # ms
        if name in self._scheduler:
            return self._scheduler[name]['next']

    def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None, from_smartplugin=False):
        """
        Adds an entry to the scheduler.

        :param name: Name of the scheduler
        :param obj: Method to call by the scheduler
        :param prio: a priority with default of 3 having 1 as most important and higher numbers less important
        :param cron: a crontab entry of type string or a list of entries
        :param cycle: a time given as integer in seconds or a string with a time given in seconds and a value after an equal sign
        :param value:
        :param offset: an optional offset for cycle. If not given, cycle start point will be varied between 10..15 seconds to prevent too many scheduler entries with the same starting times
        :param next:
        :param from_smartplugin: Only to set to True, if called from the internal method in SmartPlugin class
        """
        # set shtime and items if they were initialized to None in __init__  (potenital timing problem in init of shng)
        if self.shtime == None:
            self.shtime = Shtime.get_instance()
        if self.items == None:
            self.items = Items.get_instance()
        self._lock.acquire()
        if isinstance(cron, str):
            cron = [cron, ]
        if isinstance(cron, list):
            _cron = {}
            for entry in cron:
                desc, __, _value = entry.partition('=')
                desc = desc.strip()
                if _value == '':
                    _value = None
                else:
                    _value = _value.strip()
                if desc.startswith('init'):
                    offset = 5  # default init offset
                    desc, op, seconds = desc.partition('+')
                    if op:
                        offset += int(seconds)
                    else:
                        desc, op, seconds = desc.partition('-')
                        if op:
                            offset -= int(seconds)
                    value = _value
                    next = self.shtime.now() + datetime.timedelta(seconds=offset)
                else:
                    _cron[desc] = _value
            if _cron == {}:
                cron = None
            else:
                cron = _cron
        if isinstance(cycle, int):
            cycle = {cycle: None}
        elif isinstance(cycle, str):
            cycle, __, _value = cycle.partition('=')
            try:
                cycle = int(cycle.strip())
            except Exception:
                logger.warning("Scheduler: invalid cycle entry for {0} {1}".format(name, cycle))
                return
            if _value != '':
                _value = _value.strip()
            else:
                _value = None
            cycle = {cycle: _value}
        if cycle is not None and offset is None:  # spread cycle jobs
                offset = random.randint(10, 15)
        # change name for multi instance plugins
        if obj.__class__.__name__ == 'method':
            if isinstance(obj.__self__, SmartPlugin):
                if obj.__self__.get_instance_name() != '':
                    #if not (name).startswith(self._pluginname_prefix):
                    if not from_smartplugin:
                        name = name +'_'+ obj.__self__.get_instance_name()
                    logger.debug("Scheduler: Name changed by adding plugin instance name to: " + name)
        self._scheduler[name] = {'prio': prio, 'obj': obj, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next, 'active': True}
        if next is None:
            self._next_time(name, offset)
        self._lock.release()

    def get(self, name, from_smartplugin=False):
        """
        takes a given name for a scheduler and returns either the matching scheduler or None
        """
        name = self.check_caller(name, from_smartplugin)
        if name in self._scheduler:
            return self._scheduler[name]
        else:
            return None

    def change(self, name, from_smartplugin=False, **kwargs):
        name = self.check_caller(name, from_smartplugin)
        if name in self._scheduler:
            for key in kwargs:
                if key in self._scheduler[name]:
                    if key == 'cron':
                        if isinstance(kwargs[key], str):
                            _cron = {}
                            for entry in kwargs[key].split('|'):
                                desc, __, _value = entry.partition('=')
                                desc = desc.strip()
                                if _value == '':
                                    _value = None
                                else:
                                    _value = _value.strip()
                                _cron[desc] = _value
                            if _cron == {}:
                                kwargs[key] = None
                            else:
                                kwargs[key] = _cron
                    elif key == 'active':
                        if kwargs['active'] and not self._scheduler[name]['active']:
                            logger.info("Activating logic: {0}".format(name))
                        elif not kwargs['active'] and self._scheduler[name]['active']:
                            logger.info("Deactivating logic: {0}".format(name))
                    self._scheduler[name][key] = kwargs[key]
                else:
                    logger.warning("Attribute {0} for {1} not specified. Could not change it.".format(key, name))
            if self._scheduler[name]['active'] is True:
                if 'cycle' in kwargs or 'cron' in kwargs:
                    self._next_time(name)
            else:
                self._scheduler[name]['next'] = None
        else:
            logger.warning("Could not change {0}. No logic/method with this name found.".format(name))

    def _next_time(self, name, offset=None):
        """
        Looks at the cycle and crontab attributes of job with name to find the next time
        for them and puts this and the value to the job.

        :param name: the name of the job
        :param offset: if a cycle attribute is present, then this value offsets the next execution time of a cycle
        """
        job = self._scheduler[name]
        if None == job['cron'] == job['cycle']:
            self._scheduler[name]['next'] = None
            return
        next_time = None
        value = None
        now = self.shtime.now()
        now = now.replace(microsecond=0)
        if job['cycle'] is not None:
            cycle = list(job['cycle'].keys())[0]
            value = job['cycle'][cycle]
            if offset is None:
                offset = cycle
            next_time = now + datetime.timedelta(seconds=offset)
        if job['cron'] is not None:
            for entry in job['cron']:
                ct = self._crontab(entry)
                if next_time is not None:
                    if ct < next_time:
                        next_time = ct
                        value = job['cron'][entry]
                else:
                    next_time = ct
                    value = job['cron'][entry]
        self._scheduler[name]['next'] = next_time
        self._scheduler[name]['value'] = value
        if name not in ['Connections', 'series', 'SQLite dump']:
            logger.debug("{0} next time: {1}".format(name, next_time))

    def __iter__(self):
        for job in self._scheduler:
            yield job

    def _add_worker(self):
        self._last_worker = self.shtime.now()
        t = threading.Thread(target=self._worker)
        t.start()
        self._workers.append(t)
        if len(self._workers) > self._worker_num:
            logger.info("Adding worker thread. Total: {0}".format(len(self._workers)))
            tn = {}
            for t in threading.enumerate():
                tn[t.name] = tn.get(t.name, 0) + 1
            logger.info('Threads: ' + ', '.join("{0}: {1}".format(k, v) for (k, v) in list(tn.items())))

    def _worker(self):
        while self.alive:
            self._runc.acquire()
            self._runc.wait(timeout=1)
            try:
                prio, (name, obj, by, source, dest, value) = self._runq.get()
            except IndexError:
                continue
            finally:
                self._runc.release()
            self._task(name, obj, by, source, dest, value)

    def _task(self, name, obj, by, source, dest, value):
        threading.current_thread().name = name
        logger = logging.getLogger(name)
        if obj.__class__.__name__ == 'Logic':
            source_details = None
            if isinstance(source, dict):
                source_details = source.get('details', '')
                source = source.get('item', '')
            trigger = {'by': by, 'source': source, 'source_details': source_details, 'dest': dest, 'value': value}  # noqa

            #following variables are assigned to be available during logic execution
            sh = self._sh  # noqa
            shtime = self.shtime
            items = self.items

            # set the logic environment here (for use within functions in logics):
            logic = obj  # noqa
            logic.sh = sh
            logic.logger = logger
            logic.shtime = shtime
            logic.items = items
            logic.trigger_dict = trigger    # logic.trigger has naming conflict with method logic.trigger of lib.item

            logics = obj._logics

            if not self.mqtt:
                if _lib_modules_found:
                    self.mqtt = Modules.get_instance().get_module('mqtt')
            mqtt = self.mqtt
            logic.mqtt = mqtt

            try:
                if logic.enabled:
                    exec(obj.bytecode)
                    # store timestamp of last run
                    obj.set_last_run()
                    for method in logic.get_method_triggers():
                        try:
                            method(logic, by, source, dest)
                        except Exception as e:
                            logger.exception("Logic: Trigger {} for {} failed: {}".format(method, logic.name, e))
            except SystemExit:
                # ignore exit() call from logic.
                pass
            except Exception as e:
                tb = sys.exc_info()[2]
                tb = traceback.extract_tb(tb)[-1]
                logger.exception("Logic: {0}, File: {1}, Line: {2}, Method: {3}, Exception: {4}".format(name, tb[0], tb[1], tb[2], e))
        elif obj.__class__.__name__ == 'Item':
            try:
                if value is not None:
                    obj(value, caller="Scheduler")
            except Exception as e:
                logger.exception("Item {0} exception: {1}".format(name, e))
        else:  # method
            try:
                if value is None:
                    obj()
                else:
                    obj(**value)
            except Exception as e:
                logger.exception("Method {0} exception: {1}".format(name, e))
        threading.current_thread().name = 'idle'

    def _crontab(self, crontab):
        """
        inspects if a crontab entry contains a sunbound time instruction (e.g. "17:00<sunset<20:00") or
        if it contains a normal crontab entry (e.g. "*/5 6-19/1 * * *")

        :param crontab: a string containing an enhanced crontab entry that may include a sunset/sunrise
        :return: a timezone aware datetime with the next event time or an error datetime object that lies 10 years in the future
        """
        try:
            # process sunrise/sunset
            for entry in crontab.split('<'):
                if entry.startswith('sun'):
                    return self._sun(crontab)
            next_event = self._parse_month(crontab)  # this month
            if not next_event:
                next_event = self._parse_month(crontab, next_month=True)  # next month
            return next_event
        except Exception as e:
            logger.error('Error parsing crontab "{}": {}'.format(crontab, e))
            return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)

    def _parse_month(self, crontab, next_month=False):
        """
        Inspects a given string with classic crontab information to calculate the next point in time that matches
        The function depends on the function now() of SmartHomeNG core

        :param crontab: a string with crontab entries. It is expected to have the form of ``minute hour day weekday``
        :param next_month: inspect the current month or the next following month
        :return: false or datetime
        """
        now = self.shtime.now()
        crontab_list = re.split(r'\s+(?![^()]*\))', crontab.strip())
        try:
            if len(crontab_list) > 4:
                second, minute, hour, day, wday = [i.strip() for i in crontab_list]
            else:
                minute, hour, day, wday = [i.strip() for i in crontab_list]
                second = '0'
        except:
            logger.warning("crontab entry '{}' can not be split up into 4 parts for minute, hour, day and weekday".format(crontab))
            return False
        # evaluate the crontab strings
        minute_range = self._range(minute, 00, 59)
        hour_range = self._range(hour, 00, 23)
        if not next_month:
            mdays = calendar.monthrange(now.year, now.month)[1]
        elif now.month == 12:
            mdays = calendar.monthrange(now.year + 1, 1)[1]
        else:
            mdays = calendar.monthrange(now.year, now.month + 1)[1]

        if wday == '*' and day == '*':
            day_range = self._day_range('0, 1, 2, 3, 4, 5, 6')
        elif wday != '*' and day == '*':
            day_range = self._range(wday,0,6)
            day_range = self._day_range(','.join(day_range))
        elif wday != '*' and day != '*':
            day_range = self._range(wday,0,6)
            day_range = self._day_range(','.join(day_range))
            day_range = day_range + self._range(day, 0o1, mdays)
        else:
            day_range = self._range(day, 0o1, mdays)

        # combine the different ranges
        event_range = sorted([str(day) + '-' + str(hour) + '-' + str(minute) for minute in minute_range for hour in hour_range for day in day_range])
        if next_month:  # next month
            next_event = event_range[0]
            next_time = now + dateutil.relativedelta.relativedelta(months=+1)
        else:  # this month
            now_str = now.strftime("%d-%H-%M")
            next_event = self._next(lambda event: event > now_str, event_range)
            if not next_event:
                return False
            next_time = now
        day, hour, minute = next_event.split('-')
        return next_time.replace(day=int(day), hour=int(hour), minute=int(minute), second=int(second), microsecond=0)

    def _next(self, f, seq):
        for item in seq:
            if f(item):
                return item
        return False

    def _sun(self, crontab):
        """
        parses a given string with a time range to determine it's timely boundaries and
        returns a time

        :param: crontab contains a string with '[H:M<](sunrise|sunset)[+|-][offset][<H:M]' like e.g. '6:00<sunrise<8:00'

        """
        # checking preconditions from configuration:
        if not self._sh.sun:  # no sun object created
            logger.warning('No latitude/longitude specified. You could not use sunrise/sunset as crontab entry.')
            return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)
        # find min/max times
        tabs = crontab.split('<')
        if len(tabs) == 1:
            smin = None
            cron = tabs[0].strip()
            smax = None
        elif len(tabs) == 2:
            if tabs[0].startswith('sun'):
                smin = None
                cron = tabs[0].strip()
                smax = tabs[1].strip()
            else:
                smin = tabs[0].strip()
                cron = tabs[1].strip()
                smax = None
        elif len(tabs) == 3:
            smin = tabs[0].strip()
            cron = tabs[1].strip()
            smax = tabs[2].strip()
        else:
            logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(crontab))
            return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)

        doff = 0  # degree offset
        moff = 0  # minute offset
        tmp, op, offs = cron.rpartition('+')
        if op:
            if offs.endswith('m'):
                moff = int(offs.strip('m'))
            else:
                doff = float(offs)
        else:
            tmp, op, offs = cron.rpartition('-')
            if op:
                if offs.endswith('m'):
                    moff = -int(offs.strip('m'))
                else:
                    doff = -float(offs)

        if cron.startswith('sunrise'):
            next_time = self._sh.sun.rise(doff, moff)
            # time in next_time will be in utctime. So we need to adjust it
            if next_time.tzinfo == tzutc():
                next_time = next_time.astimezone(self.shtime.tzinfo())
            else:
                self.logger.warning("next_time.tzinfo was not given as utc!")
        elif cron.startswith('sunset'):
            next_time = self._sh.sun.set(doff, moff)
            # time in next_time will be in utctime. So we need to adjust it
            if next_time.tzinfo == tzutc():
                next_time = next_time.astimezone(self.shtime.tzinfo())
            else:
                self.logger.warning("next_time.tzinfo was not given as utc!")
        else:
            logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(crontab))
            return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)

        now = self.shtime.now()
        if smin is not None:
            h, sep, m = smin.partition(':')
            try:
                dmin = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self.shtime.tzinfo())
            except Exception:
                logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(crontab))
                return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)
            if dmin > next_time:
                next_time = dmin
        if smax is not None:
            h, sep, m = smax.partition(':')
            try:
                dmax = next_time.replace(hour=int(h), minute=int(m), second=0, tzinfo=self.shtime.tzinfo())
            except Exception:
                logger.error('Wrong syntax: {0}. Should be [H:M<](sunrise|sunset)[+|-][offset][<H:M]'.format(crontab))
                return datetime.datetime.now(tzutc()) + dateutil.relativedelta.relativedelta(years=+10)
            if dmax < next_time:
                if dmax < now:
                    dmax = dmax + datetime.timedelta(days=1)
                next_time = dmax
        return next_time

    def _range(self, entry, low, high):
        """
        inspects a single crontab entry for minutes our hours

        :param entry: a string with single entries of intervals, numeric ranges or single values
        :param low: lower limit as integer
        :param high: higher limit as integer
        :return:
        """
        result = []
        item_range = []

        # Check for multiple comma separated values and process each of them recursively
        if ',' in entry:
            for item in entry.split(','):
                result.extend(self._range(item, low, high))

        # Check for intervals, e.g. "*/2", "9-17/2"
        elif '/' in entry:
             spec_range, interval = entry.split('/')
             logger.debug('Cron spec interval {} {}'.format(entry, interval))
             result = self._range(spec_range, low, high)[::int(interval)]

        # Check for numeric ranges, e.g. "9-17"
        elif '-' in entry:
             spec_low, spec_high = entry.split('-')
             result = self._range('*', int(spec_low), int(spec_high))

        # Process single value
        else:
            if entry == '*':
                item_range = list(range(low, high + 1))
            else:
                item = int(entry)
                if item > high:  # entry above range
                    item = high  # truncate value to highest possible
                item_range.append(item)
            for entry in item_range:
                result.append('{:02d}'.format(entry))

        return result

    def _day_range(self, days):
        """
        inspect a given string with days given as integer numbers separated by ","

        :param days:
        :return: an array with strings containing the days of month
        """
        now = datetime.date.today()
        wdays = [MO, TU, WE, TH, FR, SA, SU]
        result = []
        for day in days.split(','):
            wday = wdays[int(day)]
            # add next weekday occurrence
            day = now + dateutil.relativedelta.relativedelta(weekday=wday)
            result.append(day.strftime("%d"))
            # safety add-on if weekday equals todays weekday
            day = now + dateutil.relativedelta.relativedelta(weekday=wday(+2))
            result.append(day.strftime("%d"))
        return result
