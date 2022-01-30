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
import sys
import traceback
import threading
import random
import inspect
import copy

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
import lib.userfunctions as uf

import types
import subprocess

try:
    from lib.module import Modules
    _lib_modules_found = True
except:
    _lib_modules_found = False


logger = logging.getLogger(__name__)

_scheduler_instance = None    # Pointer to the initialized instance of the scheduler class  (for use by static methods)

from lib.triggertimes import TriggerTimes

class LeaveLogic(Exception): pass  # declare a label for 'raise LeaveLogic'

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
        """
        Returns the actual size of the queue
        :return: Size of the queue
        """
        return len(self.queue)

    def dump(self):
        """
        Returns all entries of the queue as a list
        :return: list of all queue entries
        """
        queue_list = []
        self.lock.acquire()
        for entry in self.queue:
            queue_list.append(entry)
        self.lock.release()
        return queue_list


class Scheduler(threading.Thread):

    _workers = []
    _worker_num = 5
    _worker_max = 20
    _worker_delta = 60  # wait 60 seconds before adding another worker thread
    _scheduler = {}                     # holder schedulers, key is the scheduler name. Each scheduler is stored in a dict
                                        # (keys are 'obj', 'active', 'prio', 'next', 'value', 'cycle', 'cron')
    _runq = _PriorityQueue()            # holds priority and a tuple of (name, obj, by, source, dest, value) for immediate execution
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
        self.crontabs = TriggerTimes.get_instance()
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
            try:
                for name in self._scheduler:
                    task = self._scheduler[name]
                    if task['next'] is not None:
                        if task['next'] < now:
                            self._runc.acquire()
                            # insert priority and a tuple of (name, obj, by, source, dest, value) # ms
                            self._runq.insert(task['prio'], (name, task['obj'], 'Scheduler', task.get('source', None), None, task['value']))
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
            finally:
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
        try:
            name = self.check_caller(name, from_smartplugin)
            logger.debug("remove scheduler entry with name:{0}".format(name))
            if name in self._scheduler:
                del(self._scheduler[name])
        except:
            logger.error("Could not remove scheduler entry for {}".format(name))
        finally:
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
        try:
            stack = inspect.stack()
        except Exception as e:
            logger.exception(f"check_caller('{name}'): Exception in inspect.stack(): {e}")

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
        :param value: Value that an item should be set to or to be handed to a logic, otherwise: None
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
        try:
            source = '??'
            if isinstance(cron, str):
                cron = [cron, ]
            if isinstance(cron, list):
                details = None
                _cron = {}
                for entry in cron:
                    desc, __, _value = entry.partition('=')
                    desc = desc.strip()
                    if _value == '':
                        _value = None
                    else:
                        _value = _value.strip()
                    if desc.lower().startswith('init'):
                        details = desc
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
                    source = {'source': 'cron', 'details': details}
                if _cron == {}:
                    cron = None
                else:
                    cron = _cron

            if isinstance(cycle, int):
                source = {'source': 'cycle1', 'details': cycle}
                cycle = {cycle: cycle}
            elif isinstance(cycle, str):
                cycle, __, _value = cycle.partition('=')
                try:
                    cycle = int(cycle.strip())
                except Exception:
                    logger.warning("Scheduler: Invalid cycle entry for {0} {1}".format(name, cycle))
                    return
                if _value != '':
                    _value = _value.strip()
                else:
                    _value = cycle
                cycle = {cycle: _value}
                source = {'source': 'cycle', 'details': _value}
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
            #if name.startswith('items.test.test_trigger.'):
            #    logger.warning(f"ms: add: name={name}, cycle={cycle}, value={value}")
            self._scheduler[name] = {'prio': prio, 'obj': obj, 'source': source, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next, 'active': True}
            if next is None:
                self._next_time(name, offset)
        finally:
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
                    elif key == 'cycle':
                        _cycle = kwargs[key]
                        if isinstance(kwargs[key], dict):
                            _cycle = kwargs[key]
                        elif isinstance(kwargs[key], int):
                            _cycle = {kwargs[key]: None}
                        elif isinstance(kwargs[key], str):
                            _param = kwargs[key].strip()
                            if _param[0] == '{' and _param[-1] == '}':
                                _param = _param[1:-1]
                            _cycle, __, _value = _param.partition(':')
                            try:
                                _cycle = int(_cycle.strip())
                            except Exception:
                                logger.warning("scheduler.change: Invalid cycle entry for {} {}".format(name, _cycle))
                                return
                            if _value != '':
                                _value = _value.strip()
                            else:
                                _value = None
                            _cycle = {_cycle: _value}
                        #logger.warning("scheduler.change: {}: {}, type = type(kwargs[key])={}".format(name, kwargs[key], type(kwargs[key])))
                        kwargs[key] = _cycle
                        #logger.warning("scheduler.change: {}: cycle entry {}".format(name, _cycle))
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
            #value = job['cycle'][cycle]
            # set value only, if it is an item scheduler
            if job['obj'].__class__.__name__ == 'Item':
                value = job['cycle'][cycle]
            #if name.startswith('items.test.test_trigger'):
            #    logger.warning(f"_next_time ms: (cycle) value={value}, job['cycle']={job['cycle']}, job={job}")
            if offset is None:
                offset = cycle
            next_time = now + datetime.timedelta(seconds=offset)
            #job['source'] = 'cycle'
            job['source'] = {'source': 'cycle', 'details': str(cycle)}
        if job['cron'] is not None:
            for entry in job['cron']:
                if entry == 'None':
                    continue
                ct = self.crontabs.get_next(entry, now)
                if next_time is not None:
                    if ct < next_time:
                        next_time = ct
                        #job['source'] = 'cron'    # ms
                        job['source'] = {'source': 'cron', 'details': str(entry)}
                        value = job['cron'][entry]
                else:
                    next_time = ct
                    job['source'] = {'source': 'cron', 'details': str(entry)}
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
            self._execute_logic_task(obj, by, source, dest, value)

        elif obj.__class__.__name__ == 'Item':
            try:
                scheduler_source = source.get('source', '')
                #if name.startswith('items.test.test_trigger.'):
                #    logger.warning(f"ms: _task: name={name}, obj={str(obj)}, by={by}, source={source}, dest={dest}, value={value}")
                if scheduler_source != '':
                    scheduler_source = ' ('+scheduler_source+')'
                if value is not None:
                    obj(value, caller=("Scheduler"+scheduler_source))
            except Exception as e:
                logger.exception(f"Item {name} exception: {e}")

        else:  # method
            try:
                if value is None:
                    obj()
                else:
                    obj(**value)
            except Exception as e:
                logger.exception(f"Method {name} exception: {e}")

        threading.current_thread().name = 'idle'


    def _execute_logic_task(self, logic, by, source, dest, value):
        """
        Execute a logic from _task method

        :param logic:
        :return:
        """
        name = 'logics.' + logic.name
        logger = logging.getLogger(name)
        source_details = None
        if isinstance(source, dict):
            source_details = source.get('details', '')
            src = source.get('item', '')
            if src == '':
                # get source ('cron' or 'cycle')
                src = source.get('source', '')
            source = src
        trigger = {'by': by, 'source': source, 'source_details': source_details, 'dest': dest, 'value': value}  # noqa

        # following variables are assigned to be available during logic execution
        sh = self._sh  # noqa
        shtime = self.shtime
        items = self.items

        # set the logic environment here (for use within functions in logics):
        #logic = obj  # noqa
        logic.sh = sh
        logic.logger = logger
        logic.shtime = shtime
        logic.items = items
        logic.trigger_dict = trigger  # logic.trigger has naming conflict with method logic.trigger of lib.item

        logics = logic._logics

        if not self.mqtt:
            if _lib_modules_found:
                self.mqtt = Modules.get_instance().get_module('mqtt')
        mqtt = self.mqtt
        logic.mqtt = mqtt

        try:
            if logic.enabled:
                if sh.shng_status['code'] < 20:
                    logger.warning(f"Logik ignoriert, SmartHomeNG ist noch nicht vollständig initialisiert - Logik wurde getriggert durch {trigger}")
                else:
                    logger.debug(f"Getriggert durch: {trigger}")
                    exec(logic.bytecode)
                    # store timestamp of last run
                    logic.set_last_run()
                    for method in logic.get_method_triggers():
                        try:
                            method(logic, by, source, dest)
                        except Exception as e:
                            logger.exception("Logic: Trigger {} for {} failed: {}".format(method, logic.name, e))
        except LeaveLogic as e:
            # 'LeaveLogic' is no error
            if str(e) != '':
                logger.info(f"Die Logik '{logic.name}' wurde verlassen. Grund: {e}")
        except SystemExit:
            # ignore exit() call from logic.
            pass
        except Exception as e:
            tb = sys.exc_info()[2]
            tb = traceback.extract_tb(tb)[-1]
            if tb[2] == '<module>':
                logic_method = 'Hauptroutine der Logik'
            else:
                logic_method = 'function ' + tb[2] + '()'
            logger.error(f"In der Logik ist ein Fehler aufgetreten:\n   Logik '{logic.name}', Datei '{tb[0]}', Zeile {tb[1]}\n   {logic_method}, Exception: {e}")
            #logger.exception(f"In der Logik ist ein Fehler aufgetreten:\n   Logik '{logic.name}', Datei '{tb[0]}', Zeile {tb[1]}\n   {logic_method}, Exception: '{e}'\n ")

        return


