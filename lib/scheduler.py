#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2014 Marcus Popp                          marcus@popp.mx
# Copyright 2016-2017 Christian Straßburg
# Copyright 2017-2023 Martin Sinn                           m.sinn@gmx.de
# Copyright 2017-2022 Bernd Meiners                 Bernd.Meiners@mail.de
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
import dataclasses
import typing
import ctypes
import itertools

import lib.env

from lib.shtime import Shtime
from lib.item import Items
from lib.model.smartplugin import SmartPlugin
from lib.triggertimes import TriggerTimes

# following modules) are imported to have those functions available during logic execution
import gc  # noqa
import os  # noqa
import math  # noqa
import lib.userfunctions as uf  # noqa

import types  # noqa
import subprocess  # noqa

try:
    from lib.module import Modules

    _lib_modules_found = True
except ImportError:
    _lib_modules_found = False


logger = logging.getLogger(__name__)
tasks_logger = logging.getLogger(__name__ + '.tasks')

_scheduler_instance = None  # Pointer to the initialized instance of the scheduler class  (for use by static methods)


class LeaveLogic(Exception):
    pass  # declare a label for 'raise LeaveLogic'


def _leave_logic(code=None):
    """
    ``exit()`` / ``quit()`` inside a logic: end the current run of the logic.

    Replaces the builtins of the site module, which close ``sys.stdin`` of the whole process before they
    raise SystemExit. Closing blocks while another thread reads stdin.
    """
    raise SystemExit(code)


class TaskCancelled(BaseException):
    """
    Raised inside a running logic whose cancellation was requested.

    Derives from BaseException, so ``except Exception`` in logic code does not swallow it;
    ``try/finally`` blocks still run.
    """


TaskType = typing.Literal['logic', 'item', 'method']

CancelResult = typing.Literal['requested', 'not_found', 'not_cancellable']

DEFAULT_RUNTIME_WARN = 120  # seconds a scheduler task may run before a warning is logged; 0 disables


def _parse_seconds(value) -> float | None:
    """``value`` as a threshold in seconds (a number >= 0), None if invalid."""
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return seconds if seconds >= 0 else None


def _set_async_exc(thread_ident: int, exc: type[BaseException] | None) -> None:
    """
    Raise ``exc`` in thread ``thread_ident`` at its next bytecode boundary; None clears a pending one.

    A thread blocked in a C call (sleep, lock, socket, ...) gets the exception only when that call returns.
    """
    ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread_ident), None if exc is None else ctypes.py_object(exc)
    )


@dataclasses.dataclass
class RunningTask:
    """
    A scheduler task currently executing on a worker thread.

    :ivar thread_ident: ``threading.get_ident()`` of the worker thread running the task
    :ivar task_type: kind of task object - logic, item (cycle/cron/autotimer) or method
    :ivar name: scheduler name of the task
    :ivar started: ``time.monotonic()`` at task start, basis for runtime calculation
    :ivar started_at: wall-clock time at task start, for display
    :ivar runtime_warn: seconds after which a runtime warning is logged; 0 disables warnings
    :ivar trigger: trigger dict of a logic (by, source, source_details, dest, value), None for other types
    :ivar warnings_logged: number of runtime warnings logged so far
    :ivar task_id: unique id of this task run, assigned by the registry; distinguishes runs on the same thread
    :ivar runtime_cancel: seconds after which cancellation is requested automatically; 0 disables
    :ivar cancel_requested_at: ``time.monotonic()`` of the first cancellation request, None if never requested
    :ivar cancel_requests: number of cancellation requests so far
    """

    thread_ident: int
    task_type: TaskType
    name: str
    started: float
    started_at: datetime.datetime
    runtime_warn: float = 0
    trigger: dict | None = None
    warnings_logged: int = 0
    task_id: int = 0
    runtime_cancel: float = 0
    cancel_requested_at: float | None = None
    cancel_requests: int = 0

    @property
    def runtime(self) -> float:
        """Seconds since the task started."""
        return time.monotonic() - self.started

    @property
    def cancellable(self) -> bool:
        """True if the task may be cancelled; only logics are."""
        return self.task_type == 'logic'

    @property
    def next_warn_after(self) -> float | None:
        """Runtime in seconds at which the next warning is due (runtime_warn, then each doubling); None if disabled."""
        if self.runtime_warn <= 0:
            return None
        return self.runtime_warn * 2**self.warnings_logged

    @property
    def overdue(self) -> bool:
        """True once the task has exceeded its runtime_warn threshold."""
        return self.runtime_warn > 0 and self.runtime >= self.runtime_warn


class _TaskRegistry:
    """Thread-safe registry of the tasks currently running on scheduler worker threads, keyed by thread ident."""

    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: dict[int, RunningTask] = {}
        self._task_ids = itertools.count(1)

    def start(self, task: RunningTask) -> None:
        """Register ``task`` as running on its worker thread and assign its ``task_id``."""
        with self._lock:
            task.task_id = next(self._task_ids)
            self._tasks[task.thread_ident] = task

    def finish(self, thread_ident: int) -> RunningTask | None:
        """
        Remove and return the task running on ``thread_ident``, None if there is none.

        A cancellation requested but not yet delivered is withdrawn, so it cannot hit the
        worker's next task. Must be called from the worker thread itself; a TaskCancelled
        raised while this runs means it has to be called again (see ``Scheduler._finish_task()``).
        """
        with self._lock:
            task = self._tasks.get(thread_ident)
            if task is not None and task.cancel_requested_at is not None:
                _set_async_exc(thread_ident, None)
            return self._tasks.pop(thread_ident, None)

    def request_cancel(self, thread_ident: int, task_id: int, now: float) -> tuple[CancelResult, RunningTask | None]:
        """
        Raise TaskCancelled in the task ``task_id`` running on ``thread_ident``.

        Every call raises it again, since a delivered exception may have been swallowed by the task.

        :return: result and a copy of the task (None if not found)
        """
        with self._lock:
            task = self._tasks.get(thread_ident)
            if task is None or task.task_id != task_id:
                return 'not_found', None
            if not task.cancellable:
                return 'not_cancellable', dataclasses.replace(task)
            _set_async_exc(thread_ident, TaskCancelled)
            if task.cancel_requested_at is None:
                task.cancel_requested_at = now
            task.cancel_requests += 1
            return 'requested', dataclasses.replace(task)

    def due_cancels(self, now: float) -> list[RunningTask]:
        """Copies of the tasks that passed their runtime_cancel at monotonic time ``now`` and were not cancelled yet."""
        with self._lock:
            return [
                dataclasses.replace(t)
                for t in self._tasks.values()
                if t.runtime_cancel > 0 and t.cancel_requested_at is None and now - t.started >= t.runtime_cancel
            ]

    def snapshot(self) -> list[RunningTask]:
        """Copies of all running tasks."""
        with self._lock:
            return [dataclasses.replace(t) for t in self._tasks.values()]

    def get(self, thread_ident: int) -> RunningTask | None:
        """Copy of the task running on ``thread_ident``, None if there is none."""
        with self._lock:
            task = self._tasks.get(thread_ident)
            return None if task is None else dataclasses.replace(task)

    def due_warnings(self, now: float) -> list[RunningTask]:
        """
        Tasks whose next runtime warning is due at monotonic time ``now``, marked as warned.

        A task is returned at most once per call; if several thresholds have passed since the last
        call, ``warnings_logged`` skips to the highest one passed.
        """
        due = []
        with self._lock:
            for task in self._tasks.values():
                threshold = task.next_warn_after
                if threshold is None or now - task.started < threshold:
                    continue
                while threshold <= now - task.started:
                    task.warnings_logged += 1
                    threshold = task.next_warn_after
                due.append(dataclasses.replace(task))
        return due


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

    _scheduler = {}  # holder schedulers, key is the scheduler name. Each scheduler is stored in a dict
    # (keys are 'obj', 'active', 'prio', 'next', 'value', 'cycle', 'cron')
    _runq = (
        _PriorityQueue()
    )  # holds priority and a tuple of (name, obj, by, source, dest, value) for immediate execution
    _triggerq = _PriorityQueue()  # holds tuples of (datetime, priority) and (name, obj, by, source, dest, value)
    # to be put in the run queue when time is due

    _pluginname_prefix = 'plugins.'  # prefix for scheduler names

    def __init__(self, smarthome):
        threading.Thread.__init__(self, name='Scheduler')
        logger.info('Init Scheduler')
        self._sh = smarthome
        self._lock = threading.Lock()
        self._runc = threading.Condition()
        self._cycle_items = {}  # store items for dynamic cycles {'item2.property.path': {name1, name2, ...}}
        self._running = _TaskRegistry()
        self._reported_invalid_runtime_warn = None

        global _scheduler_instance
        if _scheduler_instance is not None:
            import inspect

            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical(
                "A second 'scheduler' object has been created. There should only be ONE instance of class 'Scheduler'!!! Called from: {} ({})".format(
                    calframe[1][1], calframe[1][3]
                )
            )

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
        if _scheduler_instance is None:
            return None
        else:
            return _scheduler_instance

    def set_worker_warn_count(self, count):

        self._worker_max = count
        logger.info(f'Warn Level for maximum number of workers set to {self._worker_max}')

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
                idle_count += 1
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

    def get_running_tasks(self) -> list[RunningTask]:
        """
        Get the tasks currently executing on worker threads

        :return: copies of the running tasks, in no particular order
        """
        return self._running.snapshot()

    def get_task_stack(self, thread_ident: int) -> list[str] | None:
        """
        Get the current call stack of a running task

        :param thread_ident: thread ident of the worker thread running the task
        :return: stack as formatted by ``traceback.format_stack()``, None if no task runs on that thread
        """
        if self._running.get(thread_ident) is None:
            return None
        frame = sys._current_frames().get(thread_ident)
        if frame is None:
            return None
        return traceback.format_stack(frame)

    def cancel_task(self, thread_ident: int, task_id: int) -> CancelResult:
        """
        Request cancellation of a running logic by raising TaskCancelled in it

        The exception arrives at the logic's next bytecode boundary: immediately in a busy loop,
        but only after a blocking call (sleep, wait, lock, socket, subprocess) returns. A logic
        swallowing it (bare ``except:``) keeps running; repeated requests raise it again.

        :param thread_ident: thread ident of the worker thread running the task
        :param task_id: ``task_id`` of the task run to cancel; a different run on that thread is not touched
        :return: 'requested', 'not_found' (no such task run) or 'not_cancellable' (not a logic)
        """
        result, task = self._running.request_cancel(thread_ident, task_id, time.monotonic())
        if result == 'requested':
            self._task_logger(task).notice(
                f'{task.name} ({task.task_type}) cancellation requested after {task.runtime:.0f} s '
                f'(request {task.cancel_requests})'
            )
        return result

    @staticmethod
    def _task_logger(task: RunningTask) -> logging.Logger:
        """Logger for messages about ``task``: the logic's own logger for logics, the scheduler logger otherwise."""
        if task.task_type == 'logic':
            return logging.getLogger(task.name)
        return logger

    def _check_task_runtimes(self, now: float | None = None) -> None:
        """
        Check running tasks against their runtime thresholds.

        Logs a warning with the current stack for each task that passed its next runtime_warn
        threshold, and requests cancellation of each logic that passed its runtime_cancel.

        :param now: ``time.monotonic()`` value to check against, defaults to the current one
        """
        if now is None:
            now = time.monotonic()
        for task in self._running.due_warnings(now):
            stack = ''.join(self.get_task_stack(task.thread_ident) or ['(not available)\n'])
            self._task_logger(task).warning(
                f'{task.name} ({task.task_type}) running for {now - task.started:.0f} s '
                f'(runtime_warn {task.runtime_warn:g} s, thread {task.thread_ident}), current stack:\n{stack}'
            )
        for task in self._running.due_cancels(now):
            self._task_logger(task).warning(
                f'{task.name} ({task.task_type}) exceeded runtime_cancel {task.runtime_cancel:g} s, cancelling'
            )
            self.cancel_task(task.thread_ident, task.task_id)

    def run(self):
        self.alive = True
        logger.debug(f'creating {self._worker_num} workers')
        for i in range(self._worker_num):
            self._add_worker()
        while self.alive:
            now = self.shtime.now()
            if self._runq.qsize() > len(self._workers):
                # .timestamp() avoids the same-tzinfo fold bug - see Shtime.add_seconds()'s docstring
                delta_seconds = now.timestamp() - self._last_worker.timestamp()
                if delta_seconds > self._worker_delta:
                    if len(self._workers) < self._worker_max:
                        self._add_worker()
                    else:
                        logger.error(
                            f'Needing more worker threads than the specified maximum of {self._worker_max}!  ({len(self._workers)} worker threads active)'
                        )
                        tn = {}
                        # for t in threading.enumerate():
                        for t in self._workers:
                            tn[t.name] = tn.get(t.name, 0) + 1
                        logger.info(
                            'Worker-Threads: ' + ', '.join('{0}: {1}'.format(k, v) for (k, v) in list(tn.items()))
                        )

                        if int(self._sh._restart_on_num_workers) < self._worker_max:
                            # do no restart
                            self._add_worker()
                        else:
                            if len(self._workers) < int(self._sh._restart_on_num_workers):
                                self._add_worker()
                            else:
                                logger.warning(
                                    'Worker-Threads: '
                                    + ', '.join('{0}: {1}'.format(k, v) for (k, v) in list(tn.items()))
                                )
                                self._sh.restart(
                                    'SmartHomeNG (scheduler started too many worker threads ({}))'.format(
                                        len(self._workers)
                                    )
                                )

            while self._triggerq.qsize() > 0:
                try:
                    (dt, prio), (name, obj, by, source, dest, value) = self._triggerq.get()
                except Exception as e:
                    logger.warning(f'Trigger queue exception: {e}')
                    break

                # .timestamp() avoids the same-tzinfo fold bug - see Shtime.add_seconds()'s docstring
                if dt.timestamp() < now.timestamp():  # run it
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
                logger.critical('Scheduler: Deadlock!')
                continue
            try:
                for name in self._scheduler:
                    task = self._scheduler[name]
                    if task['next'] is not None:
                        # .timestamp() avoids the same-tzinfo fold bug - see Shtime.add_seconds()'s docstring
                        if task['next'].timestamp() <= now.timestamp():
                            self._runc.acquire()
                            # insert priority and a tuple of (name, obj, by, source, dest, value) # ms
                            self._runq.insert(
                                task['prio'],
                                (name, task['obj'], 'Scheduler', task.get('source', None), None, task['value']),
                            )
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
            except Exception as e:
                tb_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
                logger.warning(f'Exception: {e} while searching scheduler for due tasks. Traceback: {tb_str}')
            finally:
                self._lock.release()
            try:
                self._check_task_runtimes()
            except Exception as e:
                logger.exception(f'Exception: {e} while checking task runtimes')
            time.sleep(0.5)

        if self._sh.shng_status['code'] > 20:
            logger.info('scheduler leaves run method')
        else:
            logger.warning('scheduler leaves run method')
        return

    def stop(self):
        self.alive = False
        logger.debug('scheduler leaves stop method')

    def trigger(
        self, name, obj=None, by='Logic', source=None, value=None, dest=None, prio=3, dt=None, from_smartplugin=False
    ):
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
                logger.warning(f'Logic name not found: {name}')
                return
        if name in self._scheduler:
            if not self._scheduler[name]['active']:
                logger.debug(f"Logic '{name}' deactivated. Ignoring trigger from {by} {source}")
                return
        if dt is None:
            logger.debug(f'Triggering {name} - by: {by} source: {source} dest: {dest} value: {value}')
            self._runc.acquire()
            self._runq.insert(prio, (name, obj, by, source, dest, value))
            self._runc.notify()
            self._runc.release()
        else:
            if not isinstance(dt, datetime.datetime):
                logger.warning(f'Trigger: Not a valid timezone aware datetime for {name}. Ignoring.')
                return
            if dt.tzinfo is None:
                logger.warning(f'Trigger: Not a valid timezone aware datetime for {name}. Ignoring.')
                return
            logger.debug(f'Triggering {name} - by: {by} source: {source} dest: {dest} value: {value} at: {dt}')
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
            logger.debug(f'remove scheduler entry with name: {name}')
            if name in self._scheduler:
                del self._scheduler[name]
        except Exception as e:
            logger.error(f'Exception {e}: Could not remove scheduler entry for {name}')
        finally:
            self._lock.release()

    def check_caller(self, name, from_smartplugin=False):
        """
        Checks the calling stack if the calling function (one of get, change, remove, trigger) itself was called by
        a smartplugin instance. If there is an instance name of the calling smartplugin then the instance name of that
        calling smartplugin is appended to the name

        Only the frame of that caller is looked at (``sys._getframe(2)``), since this runs on every trigger, i.e. on
        every item change that triggers a logic or an eval.

        :param name: the name of a scheduler entry
        :param from_smartplugin: True if the call comes from a SmartPlugin method that has added the instance name
        :return: returns either the name or name combined with instance name
        """
        if from_smartplugin:
            return name
        try:
            caller = sys._getframe(2).f_locals.get('self')
        except ValueError:
            return name
        if isinstance(caller, SmartPlugin):
            iname = caller.get_instance_name()
            if iname != '' and not str(name).endswith('_' + iname):
                name = name + '_' + iname
        return name

    def return_next(self, name, from_smartplugin=False):
        # name = self.check_caller(name, from_smartplugin)   # ms
        if name in self._scheduler:
            return self._scheduler[name]['next']

    @staticmethod
    def __get_first(d):
        """return first k, v pair from dict"""
        try:
            for k, v in d.items():
                return (k, v)
        except Exception:
            pass
        return (False, None)

    def add(
        self,
        name,
        obj,
        prio=3,
        cron=None,
        cycle=None,
        value=None,
        offset=None,
        next=None,
        from_smartplugin=False,
        items=None,
    ):
        """
        Adds an entry to the scheduler.

        :param name: Name of the scheduler
        :param obj: Method to call by the scheduler
        :param prio: a priority with default of 3 having 1 as most important and higher numbers less important
        :param cron: a crontab entry of type string or a list of entries
        :param cycle: a time given as integer in seconds or a string with a time given in seconds and a value after an equal sign or
        :param value: Value that an item should be set to or to be handed to a logic, otherwise: None
        :param offset: an optional offset for cycle. If not given, cycle start point will be varied between 10..15 seconds to prevent too many scheduler entries with the same starting times
        :param next:
        :param from_smartplugin: Only to set to True, if called from the internal method in SmartPlugin class
        :param items: None or list of items to register for update_item calls (if cycle time is calculated from expression containing item(s))
        """
        # set shtime and items if they were initialized to None in __init__  (potenital timing problem in init of shng)
        if self.shtime is None:
            self.shtime = Shtime.get_instance()
        if self.items is None:
            self.items = Items.get_instance()
        if self._lock.acquire():
            try:
                source = '??'
                if isinstance(cron, str):
                    cron = [cron]
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
                            if obj.__class__.__name__ == 'Item':
                                _value = obj.get_stringwithabsolutepathes(_value, 'sh.', '(')
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

                # NOTE: moved up so the full name is present for registering cycle items
                # change name for multi instance plugins
                if obj.__class__.__name__ == 'method':
                    if isinstance(obj.__self__, SmartPlugin):
                        if obj.__self__.get_instance_name() != '':
                            if not from_smartplugin:
                                name = name + '_' + obj.__self__.get_instance_name()
                            logger.debug('Scheduler: Name changed by adding plugin instance name to: ' + name)

                item = None
                if isinstance(cycle, (int, float)):
                    source = {'source': 'cycle1', 'details': cycle}
                    cycle = {cycle: value}

                # this should not occur anymore, as it should have been done in lib.item.item
                # just in case, and only for static values...
                elif isinstance(cycle, str):
                    # TODO: could be ; instead of = according to the docs!
                    if '=' in cycle:
                        cycle, __, _value = cycle.partition('=')
                    elif ';' in cycle:
                        cycle, __, _value = cycle.partition(';')
                    elif ':' in cycle:
                        cycle, __, _value = cycle.partition(':')
                    else:
                        _value = ''
                    try:
                        cycle = int(cycle.strip())
                    except Exception as e:
                        logger.warning(f'Scheduler: Exception {e}: Invalid cycle entry for {name} {cycle}')
                        return
                    if _value != '':
                        _value = _value.strip()
                    else:
                        _value = None
                    cycle = {cycle: _value}
                    source = {'source': 'cycle', 'details': _value}

                elif isinstance(cycle, dict) and False in cycle:
                    logger.warning(
                        f"scheduler {name}: can't add cycle with length False, check cycle assignment (obj {obj}, source {source})."
                    )
                    return

                # check if lib.item found an item reference for duration
                if items:
                    for item in items:
                        if item is None:
                            logger.warning(
                                f'Item {item} for scheduler {name} not found, check cycle assignment, skipping item'
                            )
                            continue

                        # store item for callback
                        if name not in self._cycle_items.get(item.property.path, []):
                            self._cycle_items.setdefault(item.property.path, set()).add(name)
                            item.add_method_trigger(self.update_item)

                if cycle is not None and offset is None:  # spread cycle jobs
                    offset = random.randint(10, 15)

                # TODO: remove debug code later
                # if cycle is not None and not isinstance(cycle, dict):
                #     logger.error(f'cycle not in dict format: {cycle} ({type(cycle)}) for scheduler {name}')
                #     return

                self._scheduler[name] = {
                    'prio': prio,
                    'obj': obj,
                    'source': source,
                    'cron': cron,
                    'cycle': cycle,
                    'value': value,
                    'next': next,
                    'active': True,
                }
                if next is None:
                    self._next_time(name, offset)
            except Exception:
                raise
                # logger.error(f"Exception: {e} while trying to add a new entry to scheduler")
            finally:
                self._lock.release()
        else:
            logger.error('Could not aquire lock to add a new entry to scheduler')

    def update_item(self, item, caller=None, source=None, dest=None):
        """provide a mechanism to handle changes of cycle item references"""
        # called synchronously on whatever thread changes the watched item
        # (item.add_method_trigger), so this must not touch _scheduler/
        # _cycle_items without the lock run() and the other mutators use -
        # otherwise a concurrent run() iteration and this method can read/
        # write the same job entry's 'cycle'/'value'/'next' interleaved
        with self._lock:
            if item.property.path not in self._cycle_items:
                logger.warning(f'item {item} not registered for cycle update, ignoring.')
                return

            for name in self._cycle_items[item.property.path]:
                cycle_item = self._scheduler[name]['obj']
                cycle = cycle_item.get_attr_time('cycle')
                if cycle is None:
                    logger.warning(f'item {cycle_item} for cycle update return invalid cycle data {cycle}, ignoring.')
                    return

                value = cycle_item.get_attr_value('cycle')

                c = self._scheduler[name]['cycle']
                if isinstance(c, int):
                    self._scheduler[name]['cycle'] = cycle
                    self._scheduler[name]['value'] = value
                else:
                    self._scheduler[name]['cycle'] = {cycle: value}

                # as we don't know the last execution time, we start anew from now
                self._next_time(name)

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
        """changes a scheduler entry for a given name to settings given in kwargs"""
        name = self.check_caller(name, from_smartplugin)
        if self._lock.acquire():
            try:
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
                                if isinstance(kwargs[key], int):
                                    _cycle = {kwargs[key]: None}
                                elif isinstance(kwargs[key], str):
                                    _param = kwargs[key].strip()
                                    if _param[0] == '{' and _param[-1] == '}':
                                        _param = _param[1:-1]
                                    _cycle, __, _value = _param.partition(':')
                                    try:
                                        _cycle = int(_cycle.strip())
                                    except Exception:
                                        logger.warning(
                                            'scheduler.change: Invalid cycle entry for {} {}'.format(name, _cycle)
                                        )
                                        return
                                    if _value != '':
                                        _value = _value.strip()
                                    else:
                                        _value = None
                                    _cycle = {_cycle: _value}
                                # logger.warning("scheduler.change: {}: {}, type = type(kwargs[key])={}".format(name, kwargs[key], type(kwargs[key])))
                                kwargs[key] = _cycle
                                # logger.warning("scheduler.change: {}: cycle entry {}".format(name, _cycle))
                            elif key == 'active':
                                if kwargs['active'] and not self._scheduler[name]['active']:
                                    logger.info('Activating logic: {0}'.format(name))
                                elif not kwargs['active'] and self._scheduler[name]['active']:
                                    logger.info('Deactivating logic: {0}'.format(name))
                            self._scheduler[name][key] = kwargs[key]
                        else:
                            logger.warning(f'Attribute {key} for {name} not specified. Could not change it.')
                    if self._scheduler[name]['active'] is True:
                        if 'cycle' in kwargs or 'cron' in kwargs:
                            self._next_time(name)
                    else:
                        self._scheduler[name]['next'] = None
                else:
                    logger.warning(f'Could not change {name}. No logic/method with this name found.')
            except Exception as e:
                logger.error(f'Exception: {e} while trying to change entry for {name}')
            finally:
                self._lock.release()
        else:
            logger.error(f'Could not aquire lock to change entry for {name}')

    def _next_time(self, name, offset=None):
        """
        Looks at the cycle and crontab attributes of job with name to find the next time
        for them and puts this and the value to the job.

        :param name: the name of the job
        :param offset: if a cycle attribute is present, then this value offsets the next execution time of a cycle
        """
        job = self._scheduler[name]

        # don't warn for logics as these get schedulers even without crontab or cycle
        if job['obj'].__class__.__name__ != 'Logic' and job['cron'] is None and job['cycle'] is None:
            logger.warning(f'for {job["obj"]}, neither cron or cycle is given, not setting next trigger time')
            self._scheduler[name]['next'] = None
            return
        next_time = None
        value = None
        now = self.shtime.now()
        if job['cycle'] is not None:
            cycle, v = self.__get_first(job['cycle'])

            # set value only if it is an item scheduler
            if job['obj'].__class__.__name__ == 'Item':
                value = v

                # check if item is stored in cycle_items
                item = job['obj']
                if item.property.path in self._cycle_items:
                    cycle = item.get_attr_time('cycle')
                    value = item.get_attr_value('cycle')

                    # update dynamic cycle value
                    self._scheduler[name]['cycle'] = cycle

            # TODO: if offset is not None: will cycle be completely ignored?
            if offset is None:
                offset = cycle

            next_time = self.shtime.add_seconds(now, offset)
            job['source'] = {'source': 'cycle', 'details': str(cycle)}
        if job['cron'] is not None:
            for entry in job['cron']:
                if entry == 'None':
                    continue
                ct = self.crontabs.get_next(entry, now)
                if next_time is not None:
                    # .timestamp() avoids the same-tzinfo fold bug - see Shtime.add_seconds()'s docstring
                    if ct.timestamp() < next_time.timestamp():
                        next_time = ct
                        job['source'] = {'source': 'cron', 'details': str(entry)}
                        value = job['cron'][entry]
                else:
                    next_time = ct
                    job['source'] = {'source': 'cron', 'details': str(entry)}
                    value = job['cron'][entry]

        self._scheduler[name]['next'] = next_time

        if value is not None:
            self._scheduler[name]['value'] = value

    def __iter__(self):
        for job in self._scheduler:
            yield job

    def _add_worker(self):
        self._last_worker = self.shtime.now()
        t = threading.Thread(target=self._worker)
        t.start()
        self._workers.append(t)
        if len(self._workers) > self._worker_num:
            logger.info('Adding worker thread. Total: {0}'.format(len(self._workers)))
            tn = {}
            for t in threading.enumerate():
                tn[t.name] = tn.get(t.name, 0) + 1
            logger.info('Threads: ' + ', '.join('{0}: {1}'.format(k, v) for (k, v) in list(tn.items())))

    def _worker(self):
        while self.alive:
            self._runc.acquire()
            if self._runq.qsize() == 0:
                self._runc.wait(timeout=1)
            try:
                prio, (name, obj, by, source, dest, value) = self._runq.get()
            except IndexError:
                continue
            finally:
                self._runc.release()
            try:
                self._task(name, obj, by, source, dest, value)
            except TaskCancelled:
                # cancellation delivered after _task() caught the first one; the task is already finished
                threading.current_thread().name = 'idle'

    @staticmethod
    def _task_type(obj) -> TaskType:
        """Classify a scheduler task object the way ``_dispatch_task()`` executes it."""
        class_name = obj.__class__.__name__
        if class_name == 'Logic':
            return 'logic'
        if class_name == 'Item':
            return 'item'
        return 'method'

    @staticmethod
    def _logic_trigger(by, source, dest, value) -> dict:
        """
        Build the ``trigger`` dict handed to a logic.

        A dict ``source`` (item/cron/cycle trigger) is flattened: ``source`` becomes its item path,
        or its 'source' entry ('cron'/'cycle') if no item is given; its 'details' go to ``source_details``.
        """
        source_details = None
        if isinstance(source, dict):
            source_details = source.get('details', '')
            src = source.get('item', '')
            if src == '':
                src = source.get('source', '')
            source = src
        return {'by': by, 'source': source, 'source_details': source_details, 'dest': dest, 'value': value}

    def _global_runtime_warn(self) -> float:
        """
        Global runtime warning threshold in seconds (``runtime_warn`` in smarthome.yaml, changeable live).

        An invalid value is replaced by ``DEFAULT_RUNTIME_WARN`` and logged once per distinct invalid value.
        """
        value = self._sh._runtime_warn
        runtime_warn = _parse_seconds(value)
        if runtime_warn is not None:
            return runtime_warn
        if value != self._reported_invalid_runtime_warn:
            self._reported_invalid_runtime_warn = value
            logger.warning(
                f"smarthome.yaml: invalid runtime_warn '{value}' (must be a number >= 0), using {DEFAULT_RUNTIME_WARN}"
            )
        return DEFAULT_RUNTIME_WARN

    @staticmethod
    def _logic_seconds(name, obj, task_type: TaskType, attr: str, default: float) -> float:
        """
        A logic's threshold attribute ``attr`` (logic.yaml) in seconds.

        ``default`` applies to other task types, to logics without the attribute, and replaces an
        invalid value, which is logged.
        """
        value = getattr(obj, attr, None) if task_type == 'logic' else None
        if value is None:
            return default
        seconds = _parse_seconds(value)
        if seconds is None:
            logger.warning(f"{name}: invalid {attr} '{value}' (must be a number >= 0), using {default:g}")
            return default
        return seconds

    @staticmethod
    def _task_frames(tb) -> traceback.StackSummary:
        """Frames of traceback ``tb`` inside the task code, i.e. below the last frame of this module."""
        frames = traceback.extract_tb(tb)
        own = [i for i, frame in enumerate(frames) if frame.filename == __file__]
        return traceback.StackSummary.from_list(frames[own[-1] + 1 :] if own else frames)

    def _finish_task(self, thread_ident: int) -> RunningTask | None:
        """
        Remove the task of ``thread_ident`` from the registry, withdrawing an undelivered cancellation.

        A cancellation delivered while the registry is being updated is absorbed and the update
        retried; once the task is removed, no new cancellation can target it.
        """
        while True:
            try:
                return self._running.finish(thread_ident)
            except TaskCancelled:
                continue

    def _task(self, name, obj, by, source, dest, value):
        """
        Execute a task on the current worker thread, tracking it as running for its duration.

        The worker thread carries the task name while the task runs and 'idle' afterwards.
        A cancelled task (TaskCancelled) is logged with the task code frames it was interrupted in.
        """
        thread = threading.current_thread()
        thread.name = name
        task_type = self._task_type(obj)
        self._running.start(
            RunningTask(
                thread_ident=thread.ident,
                task_type=task_type,
                name=name,
                started=time.monotonic(),
                started_at=self.shtime.now(),
                runtime_warn=self._logic_seconds(name, obj, task_type, 'runtime_warn', self._global_runtime_warn()),
                runtime_cancel=self._logic_seconds(name, obj, task_type, 'runtime_cancel', 0),
                trigger=self._logic_trigger(by, source, dest, value) if task_type == 'logic' else None,
            )
        )
        cancelled_in = None
        try:
            self._dispatch_task(name, obj, by, source, dest, value)
        except TaskCancelled as e:
            cancelled_in = self._task_frames(e.__traceback__)
        finally:
            task = self._finish_task(thread.ident)
            if task is not None and cancelled_in is not None:
                self._task_logger(task).warning(
                    f'{task.name} ({task.task_type}) cancelled after {task.runtime:.0f} s, interrupted in:\n'
                    + ''.join(cancelled_in.format())
                )
            elif task is not None and task.warnings_logged:
                self._task_logger(task).notice(f'{task.name} ({task.task_type}) finished after {task.runtime:.0f} s')
            thread.name = 'idle'

    def _dispatch_task(self, name, obj, by, source, dest, value):
        """Execute a task according to its type (logic, item or method)."""
        # logger.warning(f'task {obj} ({obj.__class__.__name__}) with {value} by {by} source {source}')
        if obj.__class__.__name__ == 'Logic':
            self._execute_logic_task(obj, by, source, dest, value)

        elif obj.__class__.__name__ == 'Item':
            try:
                if isinstance(source, str):
                    scheduler_source = source
                else:
                    scheduler_source = str(source.get('source', ''))
                    if scheduler_source != '':
                        scheduler_source = ':' + scheduler_source + ':' + str(source.get('details', ''))
                src = 'cycle'
                if isinstance(value, dict) and value.get('caller') == 'Autotimer':
                    src = 'autotimer'
                    value = obj.get_attr_value(src)
                elif isinstance(source, dict) and source.get('source', '') == 'cron':
                    src = 'cron'

                if value is None:
                    # re-set current item value. needs enforce_updates to work properly
                    value = obj()
                else:
                    # get current (static or evaluated) value from item itself
                    value = obj.get_attr_value(src, value)

                # logger.debug(f'item {obj}: src = {src}, value = {value}')
                if src != 'autotimer':
                    src = f'Scheduler{scheduler_source}'
                obj(value, caller=src.capitalize())
            except Exception as e:
                tasks_logger.exception(f'Item {name} exception: {e}')

        else:  # method
            try:
                if value is None:
                    obj()
                else:
                    if ('caller' in inspect.getfullargspec(obj).args) and isinstance(value, dict):
                        caller = value.get('caller', None)
                        if caller is None:
                            value['caller'] = by
                    obj(**value)
            except Exception as e:
                tasks_logger.exception(f'Method {name} exception: {e}')

    def _execute_logic_task(self, logic, by, source, dest, value):
        """
        Execute a logic from _task method

        :param logic:
        :return:
        """
        # get logger for the logic
        name = 'logics.' + logic.name
        logger = logging.getLogger(name)

        trigger = self._logic_trigger(by, source, dest, value)
        source = trigger['source']

        # TODO: remove comment block? or move to docstring

        # following variables are assigned to be available during logic execution
        # sh = self._sh  # noqa
        # shtime = self.shtime
        # items = self.items

        # set the logic environment here (for use within functions in logics):
        # logic = obj  # noqa
        # logic.sh = self._sh           # not needed (because of being set in logic_globals dict
        # logic.logger = logger         # not needed (because of being set in logic_globals dict
        # logic.shtime = self.shtime    # not needed (because of being set in logic_globals dict
        # logic.items = self.items      # not needed (because of being set in logic_globals dict
        # logic.env = lib.env           # not needed (because of being set in logic_globals dict
        # logic.trigger_dict = trigger  # logic.trigger has naming conflict with method logic.trigger of lib.item
        # logics = logic._logics

        if not self.mqtt:
            if _lib_modules_found:
                self.mqtt = Modules.get_instance().get_module('mqtt')
        # mqtt = self.mqtt
        logic.mqtt = self.mqtt

        try:
            if logic._enabled:
                if self._sh.shng_status['code'] < 20:
                    logger.warning(
                        f'Logik ignoriert, SmartHomeNG ist noch nicht vollständig initialisiert - Logik wurde getriggert durch {trigger}'
                    )
                else:
                    # set up "globals" environment for the logic
                    logic_globals = dict(globals())
                    logic_globals['sh'] = self._sh
                    logic_globals['logger'] = logger
                    logic_globals['mqtt'] = self.mqtt
                    logic_globals['shtime'] = self.shtime
                    logic_globals['env'] = lib.env
                    logic_globals['items'] = self.items
                    logic_globals['trigger'] = trigger  # logic.trigger_dict
                    logic_globals['logic'] = logic
                    logic_globals['logics'] = logic._logics
                    logic_globals['exit'] = logic_globals['quit'] = _leave_logic

                    # execute logic
                    logger.debug(f'Getriggert durch: {trigger}')
                    exec(logic._bytecode, logic_globals)
                    # store timestamp of last run
                    logic.set_last_run()
                    for method in logic.get_method_triggers():
                        try:
                            method(logic, by, source, dest)
                        except Exception as e:
                            logger.exception(f'Logic: Trigger {method} for {logic.name} failed: {e}')
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
            logger.error(
                f"In der Logik ist ein Fehler aufgetreten:\n   Logik '{logic.name}', Datei '{tb[0]}', Zeile {tb[1]}\n   {logic_method}, Exception: {e}"
            )
            # logger.exception(f"In der Logik ist ein Fehler aufgetreten:\n   Logik '{logic.name}', Datei '{tb[0]}', Zeile {tb[1]}\n   {logic_method}, Exception: '{e}'\n ")

        return
