#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the eval namespace, eval variable accessibility, and the legacy
compatibility shim (lib/item/_eval.py, lib/item/_eval_compat.py).

These tests form the before/after gate for the eval-namespace refactoring:
  - Every documented name must be reachable inside an item eval expression.
  - Names that were previously leaked via item.py module globals (datetime,
    time, …) must be available even after the extraction to _eval.py.
  - The compat shim (_eval_compat.py) must log a deprecation warning and
    still return the correct result for expressions using non-documented
    names; it must return _EVAL_FAILED when both namespaces fail.

Test classes
------------
TestMakeEvalEnvKeys
    _make_eval_env() returns a dict containing every documented key.

TestRunEvalDocumentedVars
    run_eval() (via Item.__run_eval) evaluates expressions using each
    documented variable and produces the expected item value.

TestRunEvalItemAccess
    item and item.property are accessible inside eval expressions.

TestRunEvalItemsAccess
    items singleton lookup and value retrieval inside eval expressions.

TestOnChangeNamespace
    'value' and 'sh.' are accessible in on_change / on_update expressions.

TestRunAttributeEvalDirect
    run_attribute_eval() basic numeric and string eval, plus the NameError
    quoting-retry behaviour.

TestEvalCompatShim
    _eval_with_legacy_fallback() logs a deprecation warning and returns the
    result when a name is absent from the explicit namespace but present in
    the legacy namespace; returns _EVAL_FAILED when both fail.

TestRunEvalCompatIntegration
    Full-stack integration: an item whose eval expression uses a name
    available only in the legacy namespace still gets the correct value
    (and a warning is logged).
"""

import logging
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
from lib.item.items import Items
from lib.item._internal._eval import _make_eval_env
from lib.item._internal._eval_compat import _eval_with_legacy_fallback, _EVAL_FAILED
from lib.item._internal._casting import run_attribute_eval
from tests.mock.core import MockSmartHome


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


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


def _item(sh, path, itype='num', **conf):
    """Create and register an item, returning it."""
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh, path, c)
    sh.items.add_item(path, i)
    vars(sh)[path] = i
    return i


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()

    def tearDown(self):
        _reset()


# ===========================================================================
# TestMakeEvalEnvKeys — namespace dict contents
# ===========================================================================


class TestMakeEvalEnvKeys(_Base):
    """_make_eval_env() must expose every documented and legacy-accessible name."""

    def setUp(self):
        super().setUp()
        self.item = _item(self.sh, 'ns_probe')
        self.ns = _make_eval_env(self.item, value=7, caller='Test', source='src', dest='dst')

    # ── documented public API ──────────────────────────────────────────────

    def test_has_sh(self):
        self.assertIn('sh', self.ns)
        self.assertIs(self.ns['sh'], self.sh)

    def test_has_shtime(self):
        self.assertIn('shtime', self.ns)

    def test_has_items(self):
        self.assertIn('items', self.ns)
        self.assertIsNotNone(self.ns['items'])

    def test_has_math(self):
        import math

        self.assertIn('math', self.ns)
        self.assertIs(self.ns['math'], math)

    def test_has_uf(self):
        self.assertIn('uf', self.ns)

    def test_has_env(self):
        self.assertIn('env', self.ns)

    def test_has_value(self):
        self.assertIn('value', self.ns)
        self.assertEqual(self.ns['value'], 7)

    def test_has_datetime(self):
        import datetime

        self.assertIn('datetime', self.ns)
        self.assertIs(self.ns['datetime'], datetime)

    def test_has_time(self):
        import time

        self.assertIn('time', self.ns)
        self.assertIs(self.ns['time'], time)

    # ── trigger-call parameters ────────────────────────────────────────────

    def test_has_caller(self):
        self.assertIn('caller', self.ns)
        self.assertEqual(self.ns['caller'], 'Test')

    def test_has_source(self):
        self.assertIn('source', self.ns)
        self.assertEqual(self.ns['source'], 'src')

    def test_has_dest(self):
        self.assertIn('dest', self.ns)
        self.assertEqual(self.ns['dest'], 'dst')

    # ── item itself ────────────────────────────────────────────────────────

    def test_has_item(self):
        self.assertIn('item', self.ns)
        self.assertIs(self.ns['item'], self.item)

    # ── defaults when called without optional args ─────────────────────────

    def test_value_defaults_to_none(self):
        ns = _make_eval_env(self.item)
        self.assertIsNone(ns['value'])

    def test_caller_defaults_to_none(self):
        ns = _make_eval_env(self.item)
        self.assertIsNone(ns['caller'])


# ===========================================================================
# TestRunEvalDocumentedVars — documented names work in real eval expressions
# ===========================================================================


class TestRunEvalDocumentedVars(_Base):
    """Each documented name must be usable inside an item eval expression."""

    def _run(self, item, value=None, caller='Eval', source=None):
        """Invoke Item.__run_eval directly (bypasses scheduler)."""
        item._Item__run_eval(value=value, caller=caller, source=source)

    # ── value ──────────────────────────────────────────────────────────────

    def test_value_used_in_expression(self):
        """eval: value * 2  with trigger value 5 → item becomes 10."""
        item = _item(self.sh, 'ev_value', eval='value * 2')
        self._run(item, value=5)
        self.assertEqual(item._value, 10)

    def test_value_none_when_not_passed(self):
        """eval: 0 if value is None else 1  with no value → item becomes 0."""
        item = _item(self.sh, 'ev_none_v', eval='0 if value is None else 1')
        self._run(item)
        self.assertEqual(item._value, 0)

    def test_value_integer(self):
        item = _item(self.sh, 'ev_int_v', eval='value + 100')
        self._run(item, value=23)
        self.assertEqual(item._value, 123)

    def test_value_float(self):
        item = _item(self.sh, 'ev_float_v', eval='round(value, 1)')
        self._run(item, value=3.456)
        self.assertAlmostEqual(item._value, 3.5)

    # ── math ───────────────────────────────────────────────────────────────

    def test_math_floor(self):
        item = _item(self.sh, 'ev_math', eval='math.floor(3.9)')
        self._run(item)
        self.assertEqual(item._value, 3)

    def test_math_ceil(self):
        item = _item(self.sh, 'ev_math2', eval='math.ceil(3.1)')
        self._run(item)
        self.assertEqual(item._value, 4)

    # ── datetime ───────────────────────────────────────────────────────────

    def test_datetime_year(self):
        """Documented in examples: datetime.datetime.strptime(...) usage."""
        item = _item(self.sh, 'ev_dt', eval='int(datetime.datetime(2024, 6, 1).year)')
        self._run(item)
        self.assertEqual(item._value, 2024)

    def test_datetime_now_returns_number(self):
        """datetime.datetime.now().year is a positive integer."""
        item = _item(self.sh, 'ev_dt_now', eval='int(datetime.datetime.now().year)')
        self._run(item)
        self.assertGreater(item._value, 2000)

    # ── time ───────────────────────────────────────────────────────────────

    def test_time_time_positive(self):
        """time.time() returns a positive epoch float; cast to bool for num item."""
        item = _item(self.sh, 'ev_time', eval='1 if time.time() > 0 else 0')
        self._run(item)
        self.assertEqual(item._value, 1)

    # ── caller / source ────────────────────────────────────────────────────

    def test_caller_not_none(self):
        """caller is always set (run_eval prepends 'Eval:' if needed)."""
        item = _item(self.sh, 'ev_caller', eval='1 if caller is not None else 0')
        self._run(item, caller='UnitTest')
        self.assertEqual(item._value, 1)

    def test_source_none_when_not_passed(self):
        item = _item(self.sh, 'ev_source', eval='1 if source is None else 0')
        self._run(item)
        self.assertEqual(item._value, 1)

    def test_source_string_when_passed(self):
        item = _item(self.sh, 'ev_source2', eval='1 if source == "trigger.path" else 0')
        self._run(item, source='trigger.path')
        self.assertEqual(item._value, 1)

    # ── sh ─────────────────────────────────────────────────────────────────

    def test_sh_item_access(self):
        """sh.item_name() returns the item's current value."""
        src = _item(self.sh, 'sh_src')
        src(55)
        tgt = _item(self.sh, 'sh_tgt', eval='sh.sh_src()')
        self._run(tgt)
        self.assertEqual(tgt._value, 55)


# ===========================================================================
# TestRunEvalItemAccess — item and item.property
# ===========================================================================


class TestRunEvalItemAccess(_Base):
    """The 'item' name exposes the Item instance and its property API."""

    def _run(self, item, **kw):
        item._Item__run_eval(**kw)

    def test_item_path_accessible(self):
        """eval: len(item._path) for a known path."""
        i = _item(self.sh, 'path_len_test', eval='len(item._path)')
        self._run(i)
        self.assertEqual(i._value, len('path_len_test'))

    def test_item_type_accessible(self):
        """item._type contains the declared type string."""
        i = _item(self.sh, 'itype_test', itype='str', eval='item._type')
        self._run(i)
        self.assertEqual(i._value, 'str')

    def test_item_property_type(self):
        """item.property.type returns the type string."""
        i = _item(self.sh, 'iprop_type', itype='str', eval='item.property.type')
        self._run(i)
        self.assertEqual(i._value, 'str')

    def test_item_property_path(self):
        """item.property.path returns the full item path."""
        i = _item(self.sh, 'iprop_path', itype='str', eval='item.property.path')
        self._run(i)
        self.assertEqual(i._value, 'iprop_path')

    def test_item_is_the_evaluated_item(self):
        """The 'item' in the namespace is the same object that receives the value."""
        captured = []
        i = _item(self.sh, 'item_identity', eval='captured.append(item) or 42')
        # inject 'captured' into the item's run-eval by patching _make_eval_env
        from lib.item._internal import _eval as eval_mod

        orig = eval_mod._make_eval_env

        def patched(item_, **kw):
            ns = orig(item_, **kw)
            ns['captured'] = captured
            return ns

        with patch.object(eval_mod, '_make_eval_env', patched):
            self._run(i)

        self.assertEqual(len(captured), 1)
        self.assertIs(captured[0], i)


# ===========================================================================
# TestRunEvalItemsAccess — items singleton lookup
# ===========================================================================


class TestRunEvalItemsAccess(_Base):
    """items.return_item() and value retrieval work inside eval expressions."""

    def _run(self, item, **kw):
        item._Item__run_eval(**kw)

    def test_items_return_item_lookup(self):
        """items.return_item('path')() returns the looked-up item's value."""
        src = _item(self.sh, 'lookup_src')
        src(77)
        tgt = _item(self.sh, 'lookup_tgt', eval='items.return_item("lookup_src")()')
        self._run(tgt)
        self.assertEqual(tgt._value, 77)

    def test_items_return_item_missing_returns_none(self):
        """items.return_item() for a non-existent path returns None without crash."""
        tgt = _item(self.sh, 'lookup_miss', eval='0 if items.return_item("does.not.exist") is None else 1')
        self._run(tgt)
        self.assertEqual(tgt._value, 0)

    def test_items_return_item_reflects_updated_value(self):
        """Value lookup reflects the most recent write to the source item."""
        src = _item(self.sh, 'live_src')
        src(10)
        tgt = _item(self.sh, 'live_tgt', eval='items.return_item("live_src")()')
        self._run(tgt)
        self.assertEqual(tgt._value, 10)
        src(20)
        self._run(tgt)
        self.assertEqual(tgt._value, 20)


# ===========================================================================
# TestOnChangeNamespace — on_change / on_update eval namespace
# ===========================================================================


class TestOnChangeNamespace(_Base):
    """on_change and on_update expressions have access to 'value' and 'sh.'."""

    def test_value_in_on_change_expression(self):
        """on_change: target = value  passes the trigger value to the target."""
        target = _item(self.sh, 'oc_tgt')
        source = _item(self.sh, 'oc_src', on_change='oc_tgt = value')
        source(42)
        self.assertEqual(target._value, 42)

    def test_value_arithmetic_in_on_change(self):
        """on_change: target = value * 2  doubles the trigger value."""
        target = _item(self.sh, 'oc_arith_tgt')
        source = _item(self.sh, 'oc_arith_src', on_change='oc_arith_tgt = value * 2')
        source(7)
        self.assertEqual(target._value, 14)

    def test_value_in_on_update_expression(self):
        """on_update fires on every write; value reflects the written value."""
        target = _item(self.sh, 'ou_tgt')
        source = _item(self.sh, 'ou_src', on_update='ou_tgt = value + 1')
        source(9)
        self.assertEqual(target._value, 10)

    def test_value_in_on_update_same_value(self):
        """on_update fires even on same-value write; value is still accessible."""
        target = _item(self.sh, 'ou_same_tgt')
        source = _item(self.sh, 'ou_same_src', on_update='ou_same_tgt = value')
        source(5)
        target(0)  # reset target
        source(5)  # same value again — on_update must still fire
        self.assertEqual(target._value, 5)

    def test_sh_access_in_on_change(self):
        """sh. references work inside on_change expressions."""
        src2 = _item(self.sh, 'oc_sh_src2')
        src2(99)
        target = _item(self.sh, 'oc_sh_tgt')
        source = _item(self.sh, 'oc_sh_src', on_change='oc_sh_tgt = sh.oc_sh_src2()')
        source(1)
        self.assertEqual(target._value, 99)

    def test_math_in_on_change(self):
        """math module is accessible in on_change expressions."""
        target = _item(self.sh, 'oc_math_tgt')
        source = _item(self.sh, 'oc_math_src', on_change='oc_math_tgt = math.floor(value)')
        source(3.9)
        self.assertEqual(target._value, 3)


# ===========================================================================
# TestRunAttributeEvalDirect — run_attribute_eval() function
# ===========================================================================


class TestRunAttributeEvalDirect(_Base):
    """run_attribute_eval() evaluates attribute expressions for autotimer/cycle."""

    def _eval(self, item, expr, **kw):
        return run_attribute_eval(item, expr, **kw)

    def test_integer_expression(self):
        item = _item(self.sh, 'ra_int')
        self.assertEqual(self._eval(item, '3 + 4'), 7)

    def test_float_expression(self):
        item = _item(self.sh, 'ra_float')
        result = self._eval(item, '1.5 * 2')
        self.assertAlmostEqual(result, 3.0)

    def test_math_expression(self):
        item = _item(self.sh, 'ra_math')
        self.assertEqual(self._eval(item, 'math.floor(9.9)'), 9)

    def test_returns_zero_for_non_numeric_without_result_type(self):
        """Default result_type='num': non-numeric result is replaced with 0."""
        item = _item(self.sh, 'ra_nonnum')
        result = self._eval(item, '"hello"')
        self.assertEqual(result, 0)

    def test_string_result_type(self):
        """result_type='str': string results are returned as-is."""
        item = _item(self.sh, 'ra_str')
        result = self._eval(item, '"hello"', result_type='str')
        self.assertEqual(result, 'hello')

    def test_name_error_quoting_retry(self):
        """NameError: undefined name is quoted and expression re-evaluated as string.

        The quoting-retry builds  eval('"' + "'high'" + '"')  which evaluates
        to the string  "'high'"  (single quotes preserved inside the outer
        double-quoted string literal).
        """
        item = _item(self.sh, 'ra_quote')
        result = self._eval(item, 'high', result_type='str')
        # outer eval('"\'high\'"') returns the string "'high'" — single quotes included
        self.assertEqual(result, "'high'")

    def test_exception_returns_result_error(self):
        """Unrecoverable exception returns the result_error sentinel."""
        item = _item(self.sh, 'ra_err')
        result = self._eval(item, '1 / 0', result_error=-1)
        self.assertEqual(result, -1)

    def test_sh_reference(self):
        """sh.item() reference works in attribute expressions."""
        src = _item(self.sh, 'ra_sh_src')
        src(5)
        target = _item(self.sh, 'ra_sh_tgt')
        result = self._eval(target, 'sh.ra_sh_src()')
        self.assertEqual(result, 5)


# ===========================================================================
# TestEvalCompatShim — _eval_with_legacy_fallback unit tests
# ===========================================================================


class TestEvalCompatShim(_Base):
    """Unit tests for the deprecated legacy-namespace fallback."""

    def setUp(self):
        super().setUp()
        self.item = _item(self.sh, 'shim_probe')
        self.ns = _make_eval_env(self.item)  # explicit namespace, no legacy names

    def test_succeeds_with_os_in_legacy_namespace(self):
        """'os' is not in explicit ns but is in the legacy namespace."""
        exc = NameError("name 'os' is not defined")
        result = _eval_with_legacy_fallback('type(os).__name__', self.ns, self.item, 'test', exc)
        self.assertIsNot(result, _EVAL_FAILED)
        self.assertEqual(result, 'module')

    def test_returns_eval_failed_when_both_namespaces_fail(self):
        """An expression that is syntactically valid but fails in both namespaces
        returns the _EVAL_FAILED sentinel."""
        exc = NameError("name 'totally_unknown_xyz_abc' is not defined")
        result = _eval_with_legacy_fallback('totally_unknown_xyz_abc + 1', self.ns, self.item, 'test', exc)
        self.assertIs(result, _EVAL_FAILED)

    def test_logs_deprecation_warning_on_success(self):
        """A successful legacy-fallback eval emits a warning."""
        exc = NameError("name 'os' is not defined")
        with self.assertLogs('lib.item', level='WARNING') as cm:
            result = _eval_with_legacy_fallback('type(os).__name__', self.ns, self.item, 'test', exc)
        self.assertIsNot(result, _EVAL_FAILED)
        combined = ' '.join(cm.output)
        self.assertIn('os', combined)
        self.assertIn('future release', combined)

    def test_warning_names_missing_variable(self):
        """The warning message includes the name of the missing variable."""
        exc = NameError("name 're' is not defined")
        with self.assertLogs('lib.item', level='WARNING') as cm:
            _eval_with_legacy_fallback("re.sub('x','y','xyz')", self.ns, self.item, 'test', exc)
        self.assertTrue(
            any("'re'" in line or "'re'" in line for line in cm.output), msg='Expected "\'re\'" in warning output'
        )

    def test_logs_warning_on_total_failure(self):
        """When both namespaces fail a warning is still emitted."""
        exc = NameError("name 'totally_unknown_xyz' is not defined")
        with self.assertLogs('lib.item', level='WARNING') as cm:
            _eval_with_legacy_fallback('totally_unknown_xyz', self.ns, self.item, 'test', exc)
        self.assertTrue(len(cm.output) >= 1)

    def test_non_name_error_original_exc_returns_eval_failed(self):
        """A non-NameError original_exc is returned as _EVAL_FAILED immediately.

        Only NameError can be fixed by adding module names to the namespace.
        Runtime errors (TypeError, ZeroDivisionError, KeyError, …) will fail
        identically in both namespaces, so retrying is pointless noise.
        """
        exc = TypeError('unsupported operand')
        result = _eval_with_legacy_fallback('os.getcwd()', self.ns, self.item, 'test', exc)
        self.assertIs(result, _EVAL_FAILED)

    def test_re_module_available_in_legacy(self):
        """The 're' module is part of the legacy namespace."""
        exc = NameError("name 're' is not defined")
        result = _eval_with_legacy_fallback("re.sub('a','b','cat')", self.ns, self.item, 'test', exc)
        self.assertIsNot(result, _EVAL_FAILED)
        self.assertEqual(result, 'cbt')

    def test_datetime_explicitly_in_primary_namespace(self):
        """datetime is in the explicit namespace — no fallback needed."""
        # This should NOT trigger the fallback at all
        result = eval('datetime.datetime(2024, 1, 1).year', self.ns)
        self.assertEqual(result, 2024)

    def test_time_explicitly_in_primary_namespace(self):
        """time is in the explicit namespace — no fallback needed."""
        result = eval('time.time() > 0', self.ns)
        self.assertTrue(result)


# ===========================================================================
# TestRunEvalCompatIntegration — full-stack: item eval uses compat fallback
# ===========================================================================


class TestRunEvalCompatIntegration(_Base):
    """End-to-end: item whose eval uses a non-documented name falls back and
    still produces the correct value, while emitting a deprecation warning."""

    def test_os_name_in_eval_succeeds_via_fallback(self):
        """An item with eval: type(os).__name__ gets the value via compat shim."""
        item = _item(self.sh, 'compat_os', eval='type(os).__name__', itype='str')
        with self.assertLogs('lib.item', level='WARNING') as cm:
            item._Item__run_eval()
        self.assertEqual(item._value, 'module')
        self.assertTrue(any('future release' in line for line in cm.output))

    def test_unknown_name_in_eval_does_not_crash(self):
        """Completely unknown name → both namespaces fail → error logged, no crash,
        item value unchanged."""
        item = _item(self.sh, 'compat_unknown', eval='absolutely_nonexistent_xyz_123')
        item.set(99)
        item._Item__run_eval()  # must not raise
        self.assertEqual(item._value, 99)  # unchanged

    def test_re_in_on_change_succeeds_via_fallback(self):
        """on_change expression using 're' module works via compat fallback."""
        target = _item(self.sh, 'compat_oc_tgt', itype='str')
        source = _item(self.sh, 'compat_oc_src', on_change="compat_oc_tgt = re.sub('o','0','foo')")
        with self.assertLogs('lib.item', level='WARNING') as cm:
            source(1)
        self.assertEqual(target._value, 'f00')
        self.assertTrue(any('future release' in line for line in cm.output))


if __name__ == '__main__':
    unittest.main()
