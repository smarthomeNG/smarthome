#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for log_change / log_rules / log_text / log_mapping (lib/item/item.py)

Planned extraction target: lib/item/_logchange.py

Logger name: 'item_changes' in YAML → Python logger 'items.item_changes'
(lib code prefixes with 'items.' unless name starts with '_')

Coverage
--------
Config parsing:
  log_change attr → _log_change_logger set to Logger('items.item_changes')
  log_level attr → resolved level stored
  no log_change → _log_change_logger is None

_log_on_change:
  fires when _log_change_logger set + value changes
  does NOT fire when _log_change_logger is None
  does NOT fire when caller == 'Fader' (handled in _set_value)

log_rules filtering (lowlimit / highlimit / filter / exclude):
  lowlimit: log only when value >= limit
  highlimit: log only when value < limit
  filter: log only values in list
  exclude: suppress values in list
  filter + exclude together → exclude ignored, warning logged
  non-num item with numeric limit → limit ignored, warning logged

_log_build_standardtext:
  contains item path, value, caller
  source/dest included when provided

_log_build_text (custom template):
  {id} substituted with item path
  {value} substituted with current value
  {caller} substituted

log_mapping:
  {mvalue} in template reflects mapped value
  unmapped value uses original
"""

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.config
from lib.item.items import Items
from lib.item._internal._logchange import log_on_change, get_rule, build_standardtext, build_text
from tests.mock.core import MockSmartHome
import tests.common as common


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _make_sh():
    _reset()
    return MockSmartHome()


def _load_items(sh, filename):
    path = os.path.join(common.BASE, 'tests', 'resources', filename + '.yaml')
    conf = lib.config.parse(path, None)
    for attr, value in conf.items():
        if isinstance(value, dict):
            child = lib.item.item.Item(sh, sh.items, attr, value)
            sh.items.add_item(attr, child)
            vars(sh)[attr] = child
    return conf


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    # Use sh.items as parent so _log_build_text sees __parent == _items_instance
    # and doesn't try to access _name/_path on MockSmartHome.
    i = lib.item.item.Item(sh, sh.items, path, c)
    sh.items.add_item(path, i)
    return i


class CapturingHandler(logging.Handler):
    """Records log records emitted to the handler."""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def messages(self):
        return [self.format(r) for r in self.records]

    def clear(self):
        self.records.clear()


class _Base(unittest.TestCase):
    LOGGER_NAME = 'items.item_changes'

    def setUp(self):
        self.sh = _make_sh()
        _load_items(self.sh, 'item_logchange')
        # Attach a capturing handler to the log_change logger
        self.handler = CapturingHandler()
        self.handler.setLevel(logging.DEBUG)
        self.log = logging.getLogger(self.LOGGER_NAME)
        self.log.addHandler(self.handler)
        self.log.setLevel(logging.DEBUG)

    def tearDown(self):
        self.log.removeHandler(self.handler)
        _reset()

    def _records(self):
        return self.handler.records

    def _fired(self):
        return len(self._records()) > 0

    def _last_msg(self):
        return self.handler.format(self._records()[-1]) if self._records() else ''


# ===========================================================================
# Config parsing
# ===========================================================================


class TestLogChangeConfigParsing(_Base):
    def test_log_change_sets_logger(self):
        item = self.sh.items.return_item('logged_basic')
        self.assertIsNotNone(item._log_change_logger)

    def test_logger_name_prefixed_with_items(self):
        item = self.sh.items.return_item('logged_basic')
        self.assertEqual(item._log_change_logger.name, 'items.item_changes')

    def test_no_log_change_leaves_logger_none(self):
        item = self.sh.items.return_item('no_log')
        self.assertIsNone(item._log_change_logger)

    def test_default_log_level_is_info(self):
        item = self.sh.items.return_item('logged_basic')
        self.assertEqual(item._log_level_name, 'INFO')

    def test_custom_log_level_attrib_stored(self):
        # _log_level_attrib stores the raw config value; _log_level_name is
        # resolved lazily inside _log_on_change the first time it fires.
        item = self.sh.items.return_item('logged_warning_level')
        self.assertEqual(item._log_level_attrib, 'WARNING')

    def test_custom_log_level_applied_on_fire(self):
        # After _log_on_change fires, _log_level_name is resolved from attrib
        item = self.sh.items.return_item('logged_warning_level')
        log_on_change(item, 42, 'Logic')
        self.assertEqual(item._log_level_name, 'WARNING')


# ===========================================================================
# _log_on_change fires / does not fire
# ===========================================================================


class TestLogOnChangeFires(_Base):
    def test_fires_on_value_change(self):
        item = self.sh.items.return_item('logged_basic')
        item(42)
        self.assertTrue(self._fired())

    def test_does_not_fire_when_no_logger(self):
        item = self.sh.items.return_item('no_log')
        item(42)
        self.assertFalse(self._fired())

    def test_fires_on_each_change(self):
        item = self.sh.items.return_item('logged_basic')
        item(1)
        item(2)
        self.assertGreaterEqual(len(self._records()), 2)

    def test_direct_call_fires(self):
        item = self.sh.items.return_item('logged_basic')
        log_on_change(item, 99, 'TestCaller')
        self.assertTrue(self._fired())

    def test_caller_fader_does_not_reach_log_on_change(self):
        # _set_value skips _log_on_change when caller == 'Fader'
        item = self.sh.items.return_item('logged_basic')
        item._set_value(1, 'Fader')
        self.assertFalse(self._fired())


# ===========================================================================
# _log_build_standardtext
# ===========================================================================


class TestLogBuildStandardText(_Base):
    def test_contains_item_path(self):
        item = self.sh.items.return_item('logged_basic')
        txt = build_standardtext(item, 42, 'TestCaller')
        self.assertIn('logged_basic', txt)

    def test_contains_value(self):
        item = self.sh.items.return_item('logged_basic')
        txt = build_standardtext(item, 42, 'TestCaller')
        self.assertIn('42', txt)

    def test_contains_caller(self):
        item = self.sh.items.return_item('logged_basic')
        txt = build_standardtext(item, 42, 'TestCaller')
        self.assertIn('TestCaller', txt)

    def test_contains_source_when_given(self):
        item = self.sh.items.return_item('logged_basic')
        txt = build_standardtext(item, 42, 'Caller', source='my_source')
        self.assertIn('my_source', txt)

    def test_does_not_contain_source_when_none(self):
        item = self.sh.items.return_item('logged_basic')
        txt = build_standardtext(item, 42, 'Caller', source=None)
        # 'None' should not appear as a source string
        self.assertNotIn('(None)', txt)


# ===========================================================================
# _log_build_text (custom template)
# ===========================================================================


class TestLogBuildText(_Base):
    def test_id_substituted(self):
        item = self.sh.items.return_item('logged_custom_text')
        item(1)  # ensure last_value is set
        txt = build_text(item, 42, 'Caller')
        self.assertIn('logged_custom_text', txt)

    def test_value_substituted(self):
        item = self.sh.items.return_item('logged_custom_text')
        item(1)
        txt = build_text(item, 42, 'Caller')
        self.assertIn('42', txt)

    def test_caller_substituted(self):
        item = self.sh.items.return_item('logged_custom_text')
        item(1)
        txt = build_text(item, 42, 'MyCallerName')
        self.assertIn('MyCallerName', txt)

    def test_custom_template_via_direct_set(self):
        item = _item(self.sh, 'tmpl', log_change='item_changes')
        item._log_text = '{id} -> {value}'
        item(1)  # set last_value
        txt = build_text(item, 99, 'C')
        self.assertIn('tmpl', txt)
        self.assertIn('99', txt)


# ===========================================================================
# log_mapping
# ===========================================================================


class TestLogMapping(_Base):
    def test_bool_true_mapped(self):
        item = self.sh.items.return_item('logged_mapped_bool')
        item._log_text = '{mvalue}'
        item(False)  # set last_value
        txt = build_text(item, True, 'C')
        self.assertIn('Switched On', txt)

    def test_bool_false_mapped(self):
        item = self.sh.items.return_item('logged_mapped_bool')
        item._log_text = '{mvalue}'
        item(True)
        txt = build_text(item, False, 'C')
        self.assertIn('Switched Off', txt)

    def test_unmapped_value_uses_original(self):
        item = _item(self.sh, 'unmapped', log_change='item_changes')
        item._log_mapping = {1: 'One', 2: 'Two'}
        item._log_text = '{mvalue}'
        item(0)
        txt = build_text(item, 99, 'C')
        # 99 not in mapping → raw value used
        self.assertIn('99', txt)


# ===========================================================================
# log_rules: lowlimit
# ===========================================================================


class TestLogRulesLowlimit(_Base):
    def test_above_lowlimit_fires(self):
        # lowlimit=10; value 20 > 10 → log fires
        item = self.sh.items.return_item('logged_lowlimit')
        log_on_change(item, 20, 'Logic')
        self.assertTrue(self._fired())

    def test_below_lowlimit_suppressed(self):
        # lowlimit=10; value 5 < 10 → no log
        item = self.sh.items.return_item('logged_lowlimit')
        log_on_change(item, 5, 'Logic')
        self.assertFalse(self._fired())

    def test_at_lowlimit_boundary(self):
        # value == lowlimit; lowlimit > value is False → fires
        item = self.sh.items.return_item('logged_lowlimit')
        log_on_change(item, 10, 'Logic')
        self.assertTrue(self._fired())

    def test_lowlimit_on_non_num_item_ignored(self):
        # lowlimit on str item → ignored (warning issued), log still fires
        item = _item(self.sh, 'str_lowlimit', 'str', log_change='item_changes', log_rules=[{'lowlimit': 5}])
        log_on_change(item, 'hello', 'Logic')
        # Warning should be issued but log should still fire (rule ignored)
        self.assertTrue(self._fired())


# ===========================================================================
# log_rules: highlimit
# ===========================================================================


class TestLogRulesHighlimit(_Base):
    def test_below_highlimit_fires(self):
        # highlimit=100; value 50 < 100 → fires
        item = self.sh.items.return_item('logged_highlimit')
        log_on_change(item, 50, 'Logic')
        self.assertTrue(self._fired())

    def test_at_highlimit_suppressed(self):
        # highlimit <= value → suppress (code: if high_limit <= float(value): return)
        item = self.sh.items.return_item('logged_highlimit')
        log_on_change(item, 100, 'Logic')
        self.assertFalse(self._fired())

    def test_above_highlimit_suppressed(self):
        item = self.sh.items.return_item('logged_highlimit')
        log_on_change(item, 150, 'Logic')
        self.assertFalse(self._fired())

    def test_low_gte_high_ignores_high_logs_warning(self):
        # lowlimit >= highlimit → high limit silently discarded, only low applies
        item = _item(self.sh, 'bad_limits', log_change='item_changes', log_rules=[{'lowlimit': 100}, {'highlimit': 50}])
        # Only lowlimit=100 applies; value=150 >= 100 → fires
        log_on_change(item, 150, 'Logic')
        self.assertTrue(self._fired())


# ===========================================================================
# log_rules: filter
# ===========================================================================


class TestLogRulesFilter(_Base):
    def test_value_in_filter_fires(self):
        # filter=[1,2,3]; value=2 → fires
        item = self.sh.items.return_item('logged_filter')
        log_on_change(item, 2, 'Logic')
        self.assertTrue(self._fired())

    def test_value_not_in_filter_suppressed(self):
        # value=5 not in [1,2,3] → suppress
        item = self.sh.items.return_item('logged_filter')
        log_on_change(item, 5, 'Logic')
        self.assertFalse(self._fired())

    def test_filter_type_mismatch_ignored(self):
        # filter contains int but item is str → type mismatch → entry skipped
        item = _item(self.sh, 'str_filter', 'str', log_change='item_changes', log_rules=[{'filter': [1, 2, 3]}])
        # Mismatch: filter entries are int, item is str → no valid filter entries remain
        # → value passes through and log fires
        log_on_change(item, 'hello', 'Logic')
        self.assertTrue(self._fired())


# ===========================================================================
# log_rules: exclude
# ===========================================================================


class TestLogRulesExclude(_Base):
    def test_value_in_exclude_suppressed(self):
        # exclude=[99]; value=99 → suppress
        item = self.sh.items.return_item('logged_exclude')
        log_on_change(item, 99, 'Logic')
        self.assertFalse(self._fired())

    def test_value_not_in_exclude_fires(self):
        # value=50 not in [99] → fires
        item = self.sh.items.return_item('logged_exclude')
        log_on_change(item, 50, 'Logic')
        self.assertTrue(self._fired())

    def test_filter_and_exclude_both_set_exclude_ignored(self):
        # Having both filter and exclude: exclude is discarded, warning issued
        item = _item(self.sh, 'both', log_change='item_changes', log_rules=[{'filter': [1, 2]}, {'exclude': [99]}])
        # Only filter applies; value=1 in filter → fires
        log_on_change(item, 1, 'Logic')
        self.assertTrue(self._fired())
        # value=99 also in filter? No → suppressed
        self.handler.clear()
        log_on_change(item, 99, 'Logic')
        self.assertFalse(self._fired())


# ===========================================================================
# _get_rule
# ===========================================================================


class TestGetRule(_Base):
    def test_lowlimit_entry_returned(self):
        item = self.sh.items.return_item('logged_lowlimit')
        result = get_rule(item, 'lowlimit')
        self.assertEqual(result, 10.0)

    def test_highlimit_entry_returned(self):
        item = self.sh.items.return_item('logged_highlimit')
        result = get_rule(item, 'highlimit')
        self.assertEqual(result, 100.0)

    def test_filter_entry_returned_as_list(self):
        item = self.sh.items.return_item('logged_filter')
        result = get_rule(item, 'filter')
        self.assertIsInstance(result, list)
        self.assertIn(1, [float(x) for x in result])

    def test_exclude_entry_returned_as_list(self):
        item = self.sh.items.return_item('logged_exclude')
        result = get_rule(item, 'exclude')
        self.assertIsInstance(result, list)

    def test_missing_rule_returns_default(self):
        item = self.sh.items.return_item('logged_basic')
        # logged_basic has no rules → lowlimit should be None
        result = get_rule(item, 'lowlimit')
        self.assertIsNone(result)

    def test_missing_filter_returns_empty_list(self):
        item = self.sh.items.return_item('logged_basic')
        result = get_rule(item, 'filter')
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
