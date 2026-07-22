#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/scheduler.py

Strategy
--------
The Scheduler is a threading.Thread that drives a full SmartHomeNG runtime.
We test two independently useful units without starting threads:

1. _PriorityQueue  — no external dependencies; tests priority ordering, FIFO
   within same priority, concurrent-safe insert/get, and size/dump.

2. Scheduler job-registration API (add / remove / get / return_next) with a
   minimal mock of the shtime, items, and crontabs dependencies.  We exercise
   the _next_time() calculation for cycle-based and cron-based jobs.

The Scheduler thread is never started — we only call the synchronous API.
"""

import collections
import datetime
import sys
import os
import threading
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.scheduler import _PriorityQueue, Scheduler
import lib.scheduler as _scheduler_module


# ===========================================================================
# _PriorityQueue
# ===========================================================================


class TestPriorityQueue(unittest.TestCase):
    """_PriorityQueue maintains a sorted list; lower priority number = higher urgency."""

    def test_empty_queue_size_is_zero(self):
        q = _PriorityQueue()
        self.assertEqual(q.qsize(), 0)

    def test_insert_increases_size(self):
        q = _PriorityQueue()
        q.insert(1, 'a')
        self.assertEqual(q.qsize(), 1)
        q.insert(2, 'b')
        self.assertEqual(q.qsize(), 2)

    def test_get_returns_lowest_priority_first(self):
        q = _PriorityQueue()
        q.insert(3, 'low')
        q.insert(1, 'high')
        q.insert(2, 'mid')
        prio, data = q.get()
        self.assertEqual(prio, 1)
        self.assertEqual(data, 'high')

    def test_get_second_item_has_next_priority(self):
        q = _PriorityQueue()
        q.insert(5, 'five')
        q.insert(2, 'two')
        q.insert(8, 'eight')
        q.get()  # removes 'two' (priority 2)
        prio, data = q.get()
        self.assertEqual(prio, 5)
        self.assertEqual(data, 'five')

    def test_fifo_within_same_priority(self):
        q = _PriorityQueue()
        q.insert(1, 'first')
        q.insert(1, 'second')
        q.insert(1, 'third')
        _, d1 = q.get()
        _, d2 = q.get()
        _, d3 = q.get()
        self.assertEqual(d1, 'first')
        self.assertEqual(d2, 'second')
        self.assertEqual(d3, 'third')

    def test_get_on_empty_raises_index_error(self):
        q = _PriorityQueue()
        with self.assertRaises(IndexError):
            q.get()

    def test_dump_returns_all_entries_sorted(self):
        q = _PriorityQueue()
        q.insert(3, 'c')
        q.insert(1, 'a')
        q.insert(2, 'b')
        entries = q.dump()
        priorities = [e[0] for e in entries]
        self.assertEqual(priorities, [1, 2, 3])

    def test_dump_does_not_consume_entries(self):
        q = _PriorityQueue()
        q.insert(1, 'x')
        q.dump()
        self.assertEqual(q.qsize(), 1)

    def test_priority_tuple_ordering(self):
        # Scheduler uses (next_time, prio) tuples as priority
        q = _PriorityQueue()
        t1 = datetime.datetime(2024, 1, 1, 10, 0)
        t2 = datetime.datetime(2024, 1, 1, 9, 0)  # earlier
        q.insert((t1, 3), 'later_job')
        q.insert((t2, 3), 'earlier_job')
        _, data = q.get()
        self.assertEqual(data, 'earlier_job')

    def test_concurrent_inserts_maintain_order(self):
        """Basic thread-safety: concurrent inserts should not corrupt the queue."""
        q = _PriorityQueue()
        errors = []

        def producer(start_prio):
            try:
                for i in range(50):
                    q.insert(start_prio + i, f'item-{start_prio}-{i}')
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=producer, args=(p * 100,)) for p in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        self.assertEqual(q.qsize(), 200)

        # Verify sorted order
        prev_prio = -1
        for _ in range(200):
            prio, _ = q.get()
            self.assertGreaterEqual(prio, prev_prio)
            prev_prio = prio


# ===========================================================================
# Scheduler — job registration and _next_time calculation
# ===========================================================================


def _make_scheduler():
    """
    Create a Scheduler with mocked dependencies, without starting its thread.

    Returns the Scheduler instance.  The Scheduler thread is *not* started.
    """
    # Reset the singleton so we can create a fresh one
    _scheduler_module._scheduler_instance = None

    sh = MagicMock()

    # Mock shtime with a fixed "now"
    now = datetime.datetime(2024, 6, 21, 12, 0, 0, tzinfo=datetime.timezone.utc)
    shtime = MagicMock()
    shtime.now.return_value = now

    # Mock items
    items = MagicMock()

    # Mock crontabs (TriggerTimes)
    crontabs = MagicMock()
    # Default: get_next returns now + 1 hour
    crontabs.get_next.return_value = now + datetime.timedelta(hours=1)

    with (
        patch('lib.scheduler.Shtime') as mock_st,
        patch('lib.scheduler.Items') as mock_items,
        patch('lib.scheduler.TriggerTimes') as mock_tt,
    ):
        mock_st.get_instance.return_value = shtime
        mock_items.get_instance.return_value = items
        mock_tt.get_instance.return_value = crontabs

        sched = Scheduler(sh)
        sched.shtime = shtime
        sched.items = items
        sched.crontabs = crontabs

    return sched, now


class _DummyCallable:
    """Minimal callable that is not a Logic, Item, or SmartPlugin."""

    class_name = 'function'
    __class__ = type('function', (), {})()

    def __call__(self):
        pass


class TestSchedulerJobRegistration(unittest.TestCase):
    def setUp(self):
        self.sched, self.now = _make_scheduler()

    # --- add with cycle ---

    def test_add_cycle_int_stores_job(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('test_job', obj, cycle=60)
        self.assertIn('test_job', self.sched._scheduler)

    def test_add_cycle_sets_next_within_cycle(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('cycle_job', obj, cycle=60, offset=60)
        job = self.sched._scheduler['cycle_job']
        expected = self.now + datetime.timedelta(seconds=60)
        self.assertEqual(job['next'], expected)

    def test_add_cycle_dict_format(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('dict_cycle', obj, cycle={30: None})
        job = self.sched._scheduler['dict_cycle']
        self.assertIsNotNone(job['next'])

    def test_add_multiple_cycles_both_stored(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('job_a', obj, cycle=60)
        self.sched.add('job_b', obj, cycle=120)
        self.assertIn('job_a', self.sched._scheduler)
        self.assertIn('job_b', self.sched._scheduler)

    def test_add_with_explicit_next_uses_that_time(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        explicit_next = self.now + datetime.timedelta(hours=2)
        self.sched.add('explicit', obj, next=explicit_next)
        job = self.sched._scheduler['explicit']
        self.assertEqual(job['next'], explicit_next)

    # --- add with cron ---

    def test_add_cron_string_stored_as_dict(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('cron_job', obj, cron='0 * * * *')
        job = self.sched._scheduler['cron_job']
        # cron should be a dict with the entry as key
        self.assertIsInstance(job['cron'], dict)
        self.assertIn('0 * * * *', job['cron'])

    def test_add_cron_list_all_entries_stored(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('multi_cron', obj, cron=['0 * * * *', '30 * * * *'])
        job = self.sched._scheduler['multi_cron']
        self.assertIn('0 * * * *', job['cron'])
        self.assertIn('30 * * * *', job['cron'])

    def test_add_cron_calls_get_next(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('cron_time', obj, cron='0 * * * *')
        # _next_time should have asked crontabs for the next time
        self.sched.crontabs.get_next.assert_called()

    # --- priority ---

    def test_add_default_priority_is_3(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('prio_job', obj, cycle=60)
        self.assertEqual(self.sched._scheduler['prio_job']['prio'], 3)

    def test_add_custom_priority_stored(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('urgent', obj, cycle=60, prio=1)
        self.assertEqual(self.sched._scheduler['urgent']['prio'], 1)

    # --- active flag ---

    def test_add_job_is_active_by_default(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('active_job', obj, cycle=60)
        self.assertTrue(self.sched._scheduler['active_job']['active'])

    # --- remove ---

    def test_remove_deletes_job(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('to_remove', obj, cycle=60)
        self.assertIn('to_remove', self.sched._scheduler)
        self.sched.remove('to_remove')
        self.assertNotIn('to_remove', self.sched._scheduler)

    def test_remove_nonexistent_does_not_raise(self):
        # removing a job that doesn't exist should be silent
        try:
            self.sched.remove('ghost_job')
        except Exception as e:
            self.fail(f'remove() raised unexpectedly: {e}')

    # --- get ---

    def test_get_returns_job_dict(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched.add('get_job', obj, cycle=60)
        result = self.sched.get('get_job')
        self.assertIsNotNone(result)
        self.assertIn('next', result)
        self.assertIn('prio', result)

    def test_get_nonexistent_returns_none(self):
        result = self.sched.get('nonexistent_job')
        self.assertIsNone(result)

    # --- return_next ---

    def test_return_next_returns_datetime(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        explicit_next = self.now + datetime.timedelta(minutes=5)
        self.sched.add('timed_job', obj, next=explicit_next)
        result = self.sched.return_next('timed_job')
        self.assertEqual(result, explicit_next)

    def test_return_next_nonexistent_returns_none(self):
        result = self.sched.return_next('ghost')
        self.assertIsNone(result)


class TestSchedulerNextTimeCalculation(unittest.TestCase):
    """Verify _next_time() computes correct fire times for cycle-based jobs."""

    def setUp(self):
        self.sched, self.now = _make_scheduler()

    def _add_raw(self, name, cron=None, cycle=None, offset=None):
        """Directly insert a job dict and call _next_time, bypassing add()'s transformation."""
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched._scheduler[name] = {
            'prio': 3,
            'obj': obj,
            'source': '??',
            'cron': cron,
            'cycle': cycle,
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._next_time(name, offset=offset)

    def test_cycle_next_equals_now_plus_offset(self):
        self._add_raw('c30', cycle={30: None}, offset=30)
        expected = self.now + datetime.timedelta(seconds=30)
        self.assertEqual(self.sched._scheduler['c30']['next'], expected)

    def test_cycle_60_with_60_offset(self):
        self._add_raw('c60', cycle={60: None}, offset=60)
        expected = self.now + datetime.timedelta(seconds=60)
        self.assertEqual(self.sched._scheduler['c60']['next'], expected)

    def test_no_cron_no_cycle_next_is_none(self):
        obj = MagicMock()
        obj.__class__.__name__ = 'function'
        self.sched._scheduler['empty'] = {
            'prio': 3,
            'obj': obj,
            'source': '??',
            'cron': None,
            'cycle': None,
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._next_time('empty')
        self.assertIsNone(self.sched._scheduler['empty']['next'])

    def test_cron_uses_get_next_result(self):
        cron_next = self.now + datetime.timedelta(hours=2)
        self.sched.crontabs.get_next.return_value = cron_next
        self._add_raw('cron_only', cron={'0 10 * * *': None})
        self.assertEqual(self.sched._scheduler['cron_only']['next'], cron_next)

    def test_cycle_wins_over_later_cron(self):
        # cycle offset 30s; cron returns now + 1h → cycle wins
        cron_next = self.now + datetime.timedelta(hours=1)
        self.sched.crontabs.get_next.return_value = cron_next
        self.sched._scheduler['both'] = {
            'prio': 3,
            'obj': MagicMock(),
            'source': '??',
            'cron': {'* * * * *': None},
            'cycle': {30: None},
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._scheduler['both']['obj'].__class__.__name__ = 'function'
        self.sched._next_time('both', offset=30)
        expected = self.now + datetime.timedelta(seconds=30)
        self.assertEqual(self.sched._scheduler['both']['next'], expected)

    def test_cron_wins_over_later_cycle(self):
        # cron returns now + 5s; cycle offset 3600s → cron wins
        cron_next = self.now + datetime.timedelta(seconds=5)
        self.sched.crontabs.get_next.return_value = cron_next
        self.sched._scheduler['cron_wins'] = {
            'prio': 3,
            'obj': MagicMock(),
            'source': '??',
            'cron': {'* * * * *': None},
            'cycle': {3600: None},
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._scheduler['cron_wins']['obj'].__class__.__name__ = 'function'
        self.sched._next_time('cron_wins', offset=3600)
        self.assertEqual(self.sched._scheduler['cron_wins']['next'], cron_next)

    def test_multiple_cron_entries_takes_earliest(self):
        soon = self.now + datetime.timedelta(minutes=5)
        later = self.now + datetime.timedelta(hours=3)

        call_count = [0]

        def get_next_side(entry, now):
            call_count[0] += 1
            return soon if call_count[0] == 1 else later

        self.sched.crontabs.get_next.side_effect = get_next_side
        self.sched._scheduler['multi_cron'] = {
            'prio': 3,
            'obj': MagicMock(),
            'source': '??',
            'cron': {'entry1': None, 'entry2': None},
            'cycle': None,
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._scheduler['multi_cron']['obj'].__class__.__name__ = 'function'
        self.sched._next_time('multi_cron')
        self.assertEqual(self.sched._scheduler['multi_cron']['next'], soon)


class TestUpdateItemLocking(unittest.TestCase):
    """
    Regression test: update_item() is registered as an item method-trigger,
    so it runs synchronously on whatever thread changes the watched item -
    not the scheduler's own thread. It used to mutate self._scheduler[name]
    ('cycle', 'value', and via _next_time() also 'next') without taking
    self._lock, unlike add()/remove()/change() and run()'s own iteration -
    a concurrent run() iteration or another update_item() call for the same
    entry could interleave with it. Verifies the whole method (including
    the trailing _next_time() call) now runs under self._lock.
    """

    def setUp(self):
        self.sched, self.now = _make_scheduler()

        job_obj = MagicMock()
        job_obj.__class__.__name__ = 'function'
        job_obj.get_attr_time.return_value = 10
        job_obj.get_attr_value.return_value = 'A'
        self.sched._scheduler['job1'] = {
            'prio': 3,
            'obj': job_obj,
            'source': '??',
            'cron': None,
            'cycle': 5,
            'value': None,
            'next': None,
            'active': True,
        }
        self.sched._cycle_items['watched'] = {'job1'}

        self.watched_item = MagicMock()
        self.watched_item.property.path = 'watched'

    def test_update_item_holds_lock_for_its_duration(self):
        lock_was_held = threading.Event()
        proceed = threading.Event()
        original_next_time = self.sched._next_time

        def slow_next_time(name, offset=None):
            # by the time _next_time() runs, update_item() should already
            # hold self._lock - pause here (still "inside" update_item()'s
            # call) and let the main thread try to acquire it meanwhile
            lock_was_held.set()
            proceed.wait(timeout=2)
            return original_next_time(name, offset)

        with patch.object(self.sched, '_next_time', side_effect=slow_next_time):
            t = threading.Thread(target=self.sched.update_item, args=(self.watched_item,))
            t.start()
            self.assertTrue(lock_was_held.wait(timeout=2), 'update_item() never reached _next_time()')

            # update_item() should still be running (and, if fixed, holding
            # self._lock) at this point - a short-timeout acquire from this
            # thread must fail while it does
            acquired = self.sched._lock.acquire(timeout=0.2)
            if acquired:
                self.sched._lock.release()

            proceed.set()
            t.join(timeout=2)

        self.assertFalse(acquired, 'update_item() must hold self._lock for its entire duration')


if __name__ == '__main__':
    unittest.main()
