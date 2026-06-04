#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartDevicePlugin loop guard.

The loop guard (_check_loop_guard) is defined in 05_loop_guard.md and
08_impact_on_other_plugins.md but not yet implemented in smartdeviceplugin.py.

These tests act as an executable specification:
  - Tests are skipped automatically if _check_loop_guard is not present.
  - Once the method is implemented, all tests should pass without modification.

Design under test (from .claude/05_loop_guard.md):

    def _check_loop_guard(self, item_path: str, value, caller=None) -> bool:
        if self._loop_guard_source:
            if not caller or not caller.startswith(self._loop_guard_source):
                return False      # source filter: non-matching caller passes freely
        # count identical writes within the window; return True to suppress
"""

import builtins
builtins.SDP_standalone = False

import logging
import time
import unittest
from collections import deque
from unittest.mock import patch

from lib.model.smartdeviceplugin import SmartDevicePlugin


HAS_LOOP_GUARD = hasattr(SmartDevicePlugin, '_check_loop_guard')
skip_if_not_implemented = unittest.skipUnless(
    HAS_LOOP_GUARD,
    '_check_loop_guard not yet implemented in SmartDevicePlugin'
)


# ---------------------------------------------------------------------------
# Helper — build a minimal object with loop guard attributes
# ---------------------------------------------------------------------------

def _make_sdp_with_guard(count=5, window=5.0, source=''):
    sdp = object.__new__(SmartDevicePlugin)
    sdp.logger = logging.getLogger('test.loopguard')
    sdp._loop_guard = {}
    sdp._loop_guard_count = count
    sdp._loop_guard_window = window
    sdp._loop_guard_source = source
    return sdp


# ---------------------------------------------------------------------------
# Basic guard behaviour
# ---------------------------------------------------------------------------

@skip_if_not_implemented
class TestLoopGuardBasic(unittest.TestCase):

    def test_first_write_is_allowed(self):
        sdp = _make_sdp_with_guard()
        self.assertFalse(sdp._check_loop_guard('item.path', True))

    def test_below_threshold_is_allowed(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        for _ in range(4):
            result = sdp._check_loop_guard('item.path', True)
        self.assertFalse(result)

    def test_at_threshold_triggers_guard(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        results = [sdp._check_loop_guard('item.path', True) for _ in range(5)]
        self.assertTrue(results[-1])

    def test_guard_stays_active_on_subsequent_calls(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        for _ in range(5):
            sdp._check_loop_guard('item.path', True)
        # all further calls should also be suppressed
        self.assertTrue(sdp._check_loop_guard('item.path', True))
        self.assertTrue(sdp._check_loop_guard('item.path', True))

    def test_different_value_resets_counter(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        for _ in range(4):
            sdp._check_loop_guard('item.path', True)
        # switch to a different value → counter resets
        result = sdp._check_loop_guard('item.path', False)
        self.assertFalse(result)

    def test_different_items_tracked_independently(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        for _ in range(5):
            sdp._check_loop_guard('item.one', True)
        # item.two has a fresh counter → must pass
        self.assertFalse(sdp._check_loop_guard('item.two', True))

    def test_guard_disabled_when_count_is_zero(self):
        sdp = _make_sdp_with_guard(count=0, window=5.0)
        for _ in range(20):
            result = sdp._check_loop_guard('item.path', True)
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# Time window behaviour
# ---------------------------------------------------------------------------

@skip_if_not_implemented
class TestLoopGuardWindow(unittest.TestCase):

    def test_old_attempts_outside_window_are_pruned(self):
        """Attempts older than window_seconds are not counted."""
        sdp = _make_sdp_with_guard(count=5, window=1.0)
        now = time.time()
        # Manually pre-fill the guard state with 4 old (expired) timestamps
        sdp._loop_guard['item.path'] = {
            'value': True,
            'times': deque([now - 2.0] * 4),   # all expired
            'locked': False,
        }
        # One fresh write → only 1 attempt in window → must pass
        result = sdp._check_loop_guard('item.path', True)
        self.assertFalse(result)

    def test_guard_clears_when_window_expires(self):
        """A locked guard clears itself once all timestamps leave the window."""
        sdp = _make_sdp_with_guard(count=3, window=0.05)
        for _ in range(3):
            sdp._check_loop_guard('item.path', True)
        # guard is now locked
        self.assertTrue(sdp._check_loop_guard('item.path', True))
        # wait for window to expire
        time.sleep(0.1)
        # next call should clear the lock and allow the write
        result = sdp._check_loop_guard('item.path', True)
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# Source filter
# ---------------------------------------------------------------------------

@skip_if_not_implemented
class TestLoopGuardSourceFilter(unittest.TestCase):

    def test_no_filter_counts_all_callers(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='')
        results = [sdp._check_loop_guard('item.path', True, caller='MQTT') for _ in range(5)]
        self.assertTrue(results[-1])

    def test_filter_counts_matching_caller(self):
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        results = [sdp._check_loop_guard('item.path', True, caller='MQTT') for _ in range(5)]
        self.assertTrue(results[-1])

    def test_filter_counts_matching_caller_with_suffix(self):
        """Prefix match: 'MQTT: broker1' matches source='MQTT'."""
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        results = [sdp._check_loop_guard('item.path', True, caller='MQTT: broker1') for _ in range(5)]
        self.assertTrue(results[-1])

    def test_filter_passes_non_matching_caller(self):
        """Caller 'knx' does not match source='MQTT' → always allowed."""
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        results = [sdp._check_loop_guard('item.path', True, caller='knx') for _ in range(20)]
        self.assertFalse(any(results))

    def test_filter_passes_none_caller(self):
        """caller=None should never be blocked by source filter."""
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        results = [sdp._check_loop_guard('item.path', True, caller=None) for _ in range(20)]
        self.assertFalse(any(results))

    def test_filter_is_case_sensitive(self):
        """'mqtt' (lowercase) does not match source='MQTT'."""
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        results = [sdp._check_loop_guard('item.path', True, caller='mqtt') for _ in range(20)]
        self.assertFalse(any(results))

    def test_filter_does_not_affect_different_values(self):
        """Changing value resets the count even through a source filter."""
        sdp = _make_sdp_with_guard(count=5, window=5.0, source='MQTT')
        for _ in range(4):
            sdp._check_loop_guard('item.path', True, caller='MQTT')
        result = sdp._check_loop_guard('item.path', False, caller='MQTT')
        self.assertFalse(result)


# ---------------------------------------------------------------------------
# Integration: update_item() suppression path
# ---------------------------------------------------------------------------

@skip_if_not_implemented
class TestLoopGuardUpdateItemIntegration(unittest.TestCase):
    """
    Verify that update_item() respects the guard result.
    Uses a minimal SDP stub that records whether send_command was called.
    """

    def _make_item_stub(self, value=True):
        item = unittest.mock.MagicMock()
        item.return_value = value
        item.property.path = 'test.item'
        item.property.last_value = not value
        item.conf = {}
        return item

    def test_update_item_calls_send_when_guard_not_triggered(self):
        import unittest.mock as mock
        sdp = _make_sdp_with_guard(count=5, window=5.0)
        sdp.alive = True
        sdp.suspended = False
        sdp._suspend_item = None
        sdp._items_write = {'test.item': 'cmd.test'}
        sdp._items_custom = {'test.item': {1: None, 2: None, 3: None}}
        sdp._items_read_all = []
        sdp._items_read_grp = {}
        sdp._items_lookup = {}
        sdp._items_vlist = {}
        sdp._item_attrs = {
            'ITEM_ATTR_COMMAND': 'viess_command',
            'ITEM_ATTR_READ_GRP': 'viess_read_group_trigger',
            'ITEM_ATTR_LOOKUP': 'viess_lookup',
            'ITEM_ATTR_VALID_LIST': 'viess_valid_list',
            'ITEM_ATTR_WRITE': 'viess_write',
            'ITEM_ATTR_READ': 'viess_read',
            'ITEM_ATTR_READAFTERWRITE': 'viess_readafterwrite',
        }
        sdp.get_fullname = lambda: 'testplugin'
        sdp.has_iattr = SmartDevicePlugin.has_iattr.__get__(sdp)
        sdp.get_iattr_value = SmartDevicePlugin.get_iattr_value.__get__(sdp)
        sdp.send_command = mock.MagicMock(return_value=True)
        sdp._reset_loop_guard = mock.MagicMock()

        item = self._make_item_stub()
        SmartDevicePlugin.update_item(sdp, item, caller='MQTT')
        sdp.send_command.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
