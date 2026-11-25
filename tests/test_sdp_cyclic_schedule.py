#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""CyclicSchedule due times."""

import unittest

from lib.model.sdp.binding import CyclicSchedule


class TestCyclicSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = CyclicSchedule()
        self.schedule.sync(commands={'a': 10, 'b': 30}, groups={'g': 20})

    def test_everything_due_initially(self):
        self.assertEqual(['a', 'b'], self.schedule.due_commands(now=0))
        self.assertEqual(['g'], self.schedule.due_groups(now=0))

    def test_read_entry_due_again_after_its_cycle(self):
        self.schedule.mark_command_read('a', now=100)

        self.assertEqual(['b'], self.schedule.due_commands(now=109))
        self.assertEqual(['a', 'b'], self.schedule.due_commands(now=110))

    def test_shortest_cycle_spans_commands_and_groups(self):
        self.assertEqual(10, self.schedule.shortest_cycle())
        self.assertIsNone(CyclicSchedule().shortest_cycle())

    def test_resync_keeps_due_times_of_kept_entries(self):
        self.schedule.mark_command_read('a', now=100)
        self.schedule.sync(commands={'a': 10, 'c': 5}, groups={})

        self.assertEqual(['c'], self.schedule.due_commands(now=105))
        self.assertEqual([], self.schedule.due_groups(now=105))

    def test_resync_applies_changed_cycle_from_next_read(self):
        self.schedule.mark_command_read('a', now=100)
        self.schedule.sync(commands={'a': 50}, groups={})
        self.schedule.mark_command_read('a', now=110)

        self.assertEqual([], self.schedule.due_commands(now=159))
        self.assertEqual(['a'], self.schedule.due_commands(now=160))


if __name__ == '__main__':
    unittest.main(verbosity=2)
