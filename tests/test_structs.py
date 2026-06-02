"""
Tests for partial struct inclusion (struct sub-path resolution).

Covers:
  - _resolve_partial_struct()               in lib/config.py
  - add_struct_to_item_template()           in lib/config.py
  - Structs._resolve_partial_struct_def()   in lib/item/structs.py
  - Structs.merge_substruct_to_struct()     in lib/item/structs.py

Test scenarios
--------------
Successful partial resolution
  Single-level sub-path:   'plugin.master.bar'
  Multi-level sub-path:    'plugin.master.bar.child1'
  User-defined prefix:     'my.custom.sensor.temperature'

Error cases
  Sub-item not found:      'plugin.master.nonexistent'
  Sub-path is a scalar:    'plugin.master.bar.type'   (type='str' is scalar)
  No struct matches:       'completely.unknown.path'

Longest-match-first concurrency
  Both 'plugin.master' and 'plugin.master.bar' are registered.
  'plugin.master.bar.direct_child' must resolve against 'plugin.master.bar'
  (longer prefix), NOT against 'plugin.master' with sub-path 'bar.direct_child'.
"""

import collections
import logging
import unittest

from lib.config import _resolve_partial_struct, add_struct_to_item_template
from lib.item.structs import Structs

from . import common  # noqa: F401  (ensures sys.path includes the project root)


# ---------------------------------------------------------------------------
# Register SmartHomeNG custom log levels so Structs' logger calls don't fail.
# lib/log.py normally does this at startup; we replicate the minimum needed here.
# ---------------------------------------------------------------------------

def _ensure_shng_loglevels():
    for name, value in [('NOTICE', 29), ('DBGHIGH', 13), ('DBGMED', 12),
                        ('DBGLOW', 11), ('DEVELOP', 9)]:
        if not hasattr(logging.getLoggerClass(), name.lower()):
            def _make_method(v):
                def logForLevel(self, message, *args, **kwargs):
                    if self.isEnabledFor(v):
                        self._log(v, message, args, **kwargs)
                return logForLevel
            logging.addLevelName(value, name)
            setattr(logging, name, value)
            setattr(logging.getLoggerClass(), name.lower(), _make_method(value))


_ensure_shng_loglevels()


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_base_struct_dict():
    """
    Base fixture with two registered top-level structs.

    plugin.master:
        foo      — simple dict (type: num)
        bar      — dict with child1 (bool) and child2 (num + unit); also has scalar 'type'
        baz      — simple dict (type: list)

    my.custom.sensor:
        temperature  — dict with type, unit, and sub-item 'reading'
        humidity     — simple dict

    No intermediate registrations — partial path resolution is the only way to
    reach sub-trees of these structs.
    """
    return {
        'plugin.master': collections.OrderedDict([
            ('foo', collections.OrderedDict([('type', 'num')])),
            ('bar', collections.OrderedDict([
                ('type', 'str'),
                ('child1', collections.OrderedDict([('type', 'bool')])),
                ('child2', collections.OrderedDict([('type', 'num'), ('unit', 'km')])),
            ])),
            ('baz', collections.OrderedDict([('type', 'list')])),
        ]),
        'my.custom.sensor': collections.OrderedDict([
            ('temperature', collections.OrderedDict([
                ('type', 'num'),
                ('unit', '°C'),
                ('reading', collections.OrderedDict([('type', 'num'), ('precision', '2')])),
            ])),
            ('humidity', collections.OrderedDict([('type', 'num'), ('unit', '%')])),
        ]),
    }


def _make_concurrency_struct_dict():
    """
    Extended fixture: adds 'plugin.master.bar' as a separately registered struct
    alongside 'plugin.master'.  Used exclusively for the longest-match-first tests.

    plugin.master.bar  (separately registered):
        type          — scalar 'foo_type'
        direct_child  — dict with special: yes

    With this setup, 'plugin.master.bar.direct_child' must resolve against
    'plugin.master.bar' (the longer registered prefix).
    """
    d = _make_base_struct_dict()
    d['plugin.master.bar'] = collections.OrderedDict([
        ('type', 'foo_type'),
        ('direct_child', collections.OrderedDict([('type', 'str'), ('special', 'yes')])),
    ])
    return d


# ===========================================================================
# Tests for lib.config._resolve_partial_struct
# ===========================================================================

class TestResolvePartialStruct(unittest.TestCase):
    """Unit tests for the _resolve_partial_struct() helper in lib/config.py."""

    def setUp(self):
        self.sd = _make_base_struct_dict()
        self.sd_conc = _make_concurrency_struct_dict()

    # --- successful resolution ---

    def test_single_level_subpath(self):
        """'plugin.master.bar' → sub-tree of 'bar' from 'plugin.master'."""
        sub_tree, matched, sub_path = _resolve_partial_struct('plugin.master.bar', self.sd)
        self.assertIsNotNone(sub_tree, "Expected a sub-tree to be returned")
        self.assertIsInstance(sub_tree, dict)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'bar')
        self.assertIn('child1', sub_tree)
        self.assertIn('child2', sub_tree)

    def test_multi_level_subpath(self):
        """'plugin.master.bar.child1' → sub-tree two levels deep."""
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.bar.child1', self.sd)
        self.assertIsNotNone(sub_tree)
        self.assertIsInstance(sub_tree, dict)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'bar.child1')
        self.assertEqual(sub_tree.get('type'), 'bool')

    def test_user_defined_prefix_subpath(self):
        """Three-segment prefix 'my.custom.sensor' plus one sub-path key."""
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'my.custom.sensor.temperature', self.sd)
        self.assertIsNotNone(sub_tree)
        self.assertEqual(matched, 'my.custom.sensor')
        self.assertEqual(sub_path, 'temperature')
        self.assertEqual(sub_tree.get('unit'), '°C')

    def test_three_level_subpath(self):
        """'my.custom.sensor.temperature.reading' — four total segments."""
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'my.custom.sensor.temperature.reading', self.sd)
        self.assertIsNotNone(sub_tree)
        self.assertEqual(matched, 'my.custom.sensor')
        self.assertEqual(sub_path, 'temperature.reading')
        self.assertEqual(sub_tree.get('precision'), '2')

    # --- error cases ---

    def test_subitem_not_found(self):
        """Struct exists but sub-path key is absent → (None, name, path)."""
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.nonexistent', self.sd)
        self.assertIsNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'nonexistent')

    def test_subpath_is_scalar(self):
        """Sub-path navigates to a scalar value → (None, name, path)."""
        # plugin.master.bar.type — 'type' inside 'bar' is a scalar string 'str'
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.bar.type', self.sd)
        self.assertIsNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'bar.type')

    def test_subpath_intermediate_scalar(self):
        """Path traversal hits a scalar at an intermediate step."""
        # plugin.master.foo.type — 'foo' is a dict but 'foo.type' is scalar 'num'
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.foo.type', self.sd)
        self.assertIsNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'foo.type')

    def test_no_matching_prefix(self):
        """No registered struct matches any prefix → (None, None, None)."""
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'completely.unknown.path', self.sd)
        self.assertIsNone(sub_tree)
        self.assertIsNone(matched)
        self.assertIsNone(sub_path)

    def test_single_segment_name(self):
        """A name with no dot cannot have a prefix → (None, None, None)."""
        sub_tree, matched, sub_path = _resolve_partial_struct('unknown', self.sd)
        self.assertIsNone(sub_tree)
        self.assertIsNone(matched)
        self.assertIsNone(sub_path)

    # --- longest-match-first concurrency ---

    def test_longest_prefix_wins_over_shorter(self):
        """
        Both 'plugin.master.bar' and 'plugin.master' are registered.
        'plugin.master.bar.direct_child' must resolve against 'plugin.master.bar'
        (longer prefix), NOT against 'plugin.master' with sub-path 'bar.direct_child'.
        """
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.bar.direct_child', self.sd_conc)
        self.assertIsNotNone(sub_tree)
        self.assertEqual(matched, 'plugin.master.bar',
                         "The longer registered prefix must win")
        self.assertEqual(sub_path, 'direct_child')
        self.assertIn('special', sub_tree)

    def test_shorter_prefix_used_when_longer_doesnt_have_subpath(self):
        """
        When the longer prefix 'plugin.master.bar' doesn't have the requested
        sub-path but the shorter prefix 'plugin.master' does, the shorter one
        should NOT be tried — the greedy algorithm stops at the first prefix match.
        This verifies that the algorithm returns NOT-FOUND rather than silently
        falling back to an unexpected prefix.
        """
        # 'plugin.master.bar' exists but has no 'child1'; 'plugin.master' has bar.child1.
        # The algorithm stops at 'plugin.master.bar' and reports not-found.
        sub_tree, matched, sub_path = _resolve_partial_struct(
            'plugin.master.bar.child1', self.sd_conc)
        self.assertIsNone(sub_tree)
        # matched should be 'plugin.master.bar' (longest registered prefix found)
        self.assertEqual(matched, 'plugin.master.bar')
        self.assertEqual(sub_path, 'child1')


# ===========================================================================
# Tests for lib.config.add_struct_to_item_template
# ===========================================================================

class TestAddStructToItemTemplate(unittest.TestCase):
    """
    Integration-level tests for add_struct_to_item_template() in lib/config.py.
    Verifies template content and error item insertion.
    """

    def setUp(self):
        self.sd = _make_base_struct_dict()
        self.sd_conc = _make_concurrency_struct_dict()

    def _run(self, struct_name, path='myitem', sd=None):
        if sd is None:
            sd = self.sd
        template = collections.OrderedDict()
        add_struct_to_item_template(path, struct_name, template, sd, '')
        return template

    # --- successful partial inclusion ---

    def test_partial_inclusion_single_level(self):
        """Only 'bar' from 'plugin.master' is merged; siblings 'foo' and 'baz' are absent."""
        template = self._run('plugin.master.bar')
        myitem = template['myitem']
        self.assertIn('child1', myitem)
        self.assertIn('child2', myitem)
        self.assertNotIn('foo', myitem)
        self.assertNotIn('baz', myitem)

    def test_partial_inclusion_multi_level(self):
        """Two-level sub-path: only the deepest requested dict is inserted."""
        template = self._run('plugin.master.bar.child1')
        myitem = template['myitem']
        self.assertIn('type', myitem)
        self.assertEqual(myitem['type'], 'bool')
        self.assertNotIn('child2', myitem)

    def test_partial_inclusion_user_struct(self):
        """User-defined struct with three-segment prefix + one-level sub-path."""
        template = self._run('my.custom.sensor.temperature', path='sensor')
        self.assertIn('sensor', template)
        self.assertEqual(template['sensor'].get('unit'), '°C')
        self.assertIn('reading', template['sensor'])

    def test_direct_struct_lookup_unaffected(self):
        """Full struct name still works exactly as before."""
        template = self._run('plugin.master')
        myitem = template['myitem']
        self.assertIn('foo', myitem)
        self.assertIn('bar', myitem)
        self.assertIn('baz', myitem)

    # --- error cases produce an item with a descriptive name ---

    def test_error_subitem_not_found(self):
        """Struct found but sub-path missing → error item with context."""
        template = self._run('plugin.master.nonexistent')
        name_attr = template.get('myitem', {}).get('name', '')
        self.assertIn('ERROR', name_attr)
        self.assertIn('plugin.master', name_attr)
        self.assertIn('nonexistent', name_attr)

    def test_error_subpath_is_scalar(self):
        """Struct found but sub-path is a scalar → error item mentions scalar."""
        template = self._run('plugin.master.bar.type')
        name_attr = template.get('myitem', {}).get('name', '')
        self.assertIn('ERROR', name_attr)
        self.assertIn('plugin.master', name_attr)
        self.assertIn('bar.type', name_attr)

    def test_error_struct_not_found(self):
        """No matching prefix → original 'struct not found' error."""
        template = self._run('completely.unknown')
        name_attr = template.get('myitem', {}).get('name', '')
        self.assertIn('ERROR', name_attr)
        self.assertIn('completely.unknown', name_attr)

    # --- longest-match-first concurrency ---

    def test_longest_match_wins_in_template(self):
        """
        With both 'plugin.master.bar' and 'plugin.master' registered,
        'plugin.master.bar.direct_child' must use 'plugin.master.bar' as base.
        """
        template = self._run('plugin.master.bar.direct_child', sd=self.sd_conc)
        myitem = template['myitem']
        self.assertIn('special', myitem)
        self.assertNotIn('child2', myitem)

    def test_direct_name_takes_precedence_over_partial(self):
        """
        'plugin.master.bar' is a registered struct name in the concurrency dict.
        It must be returned directly (exact match), not resolved as a partial path
        into 'plugin.master'.  Content must come from the separately-registered
        struct, not from plugin.master's 'bar' sub-tree.
        """
        template = self._run('plugin.master.bar', sd=self.sd_conc)
        myitem = template['myitem']
        # The separately-registered struct has 'direct_child', not 'child1'/'child2'
        self.assertIn('direct_child', myitem)
        self.assertNotIn('child1', myitem)


# ===========================================================================
# Tests for Structs._resolve_partial_struct_def and merge_substruct_to_struct
# ===========================================================================

class MockSH:
    """Minimal SmartHomeNG stand-in for constructing a Structs instance."""
    _etc_dir = ''
    _structs_dir = ''

    def get_config_dir(self, config):
        return ''

    def get_structsdir(self):
        return ''


class TestStructsPartialResolution(unittest.TestCase):
    """
    Tests for partial struct resolution inside struct definitions
    (Structs._resolve_partial_struct_def and merge_substruct_to_struct).
    """

    def setUp(self):
        sh = MockSH()
        self.structs = Structs(sh)
        # Shadow the class-level dicts with instance-level ones for test isolation
        self.structs._struct_definitions = collections.OrderedDict(
            _make_base_struct_dict())
        self.structs._finalized_structs = []
        # Keep a separate instance for concurrency tests
        self.structs_conc = Structs(sh)
        self.structs_conc._struct_definitions = collections.OrderedDict(
            _make_concurrency_struct_dict())
        self.structs_conc._finalized_structs = []

    # --- _resolve_partial_struct_def ---

    def test_def_single_level_subpath(self):
        sub_tree, matched, sub_path = self.structs._resolve_partial_struct_def(
            'plugin.master.bar')
        self.assertIsNotNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'bar')
        self.assertIn('child1', sub_tree)

    def test_def_multi_level_subpath(self):
        sub_tree, matched, sub_path = self.structs._resolve_partial_struct_def(
            'plugin.master.bar.child2')
        self.assertIsNotNone(sub_tree)
        self.assertEqual(sub_tree.get('unit'), 'km')

    def test_def_subitem_not_found(self):
        sub_tree, matched, sub_path = self.structs._resolve_partial_struct_def(
            'plugin.master.missing')
        self.assertIsNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')
        self.assertEqual(sub_path, 'missing')

    def test_def_scalar_path(self):
        sub_tree, matched, sub_path = self.structs._resolve_partial_struct_def(
            'plugin.master.foo.type')
        self.assertIsNone(sub_tree)
        self.assertEqual(matched, 'plugin.master')

    def test_def_no_match(self):
        sub_tree, matched, sub_path = self.structs._resolve_partial_struct_def(
            'nobody.here')
        self.assertIsNone(sub_tree)
        self.assertIsNone(matched)
        self.assertIsNone(sub_path)

    def test_def_longest_match_wins(self):
        sub_tree, matched, sub_path = self.structs_conc._resolve_partial_struct_def(
            'plugin.master.bar.direct_child')
        self.assertIsNotNone(sub_tree)
        self.assertEqual(matched, 'plugin.master.bar')
        self.assertEqual(sub_path, 'direct_child')
        self.assertIn('special', sub_tree)

    # --- merge_substruct_to_struct ---

    def test_merge_full_struct(self):
        """Existing behaviour: merge a full registered struct."""
        main = collections.OrderedDict()
        self.structs.merge_substruct_to_struct(main, 'plugin.master')
        self.assertIn('foo', main)
        self.assertIn('bar', main)
        self.assertIn('baz', main)

    def test_merge_partial_struct_single_level(self):
        """Partial reference: merge only the 'bar' sub-tree of 'plugin.master'."""
        main = collections.OrderedDict()
        self.structs.merge_substruct_to_struct(main, 'plugin.master.bar')
        self.assertIn('child1', main)
        self.assertIn('child2', main)
        self.assertNotIn('foo', main)
        self.assertNotIn('baz', main)

    def test_merge_partial_struct_multi_level(self):
        """Two-level sub-path: only the deepest requested dict is merged."""
        main = collections.OrderedDict()
        self.structs.merge_substruct_to_struct(main, 'plugin.master.bar.child2')
        self.assertIn('type', main)
        self.assertEqual(main['type'], 'num')
        self.assertIn('unit', main)

    def test_merge_subitem_not_found_logs_error(self):
        """Sub-item missing → error logged, main struct unchanged."""
        main = collections.OrderedDict()
        with self.assertLogs('lib.item.structs', level='ERROR') as cm:
            self.structs.merge_substruct_to_struct(
                main, 'plugin.master.nonexistent', main_struct_name='test_struct')
        self.assertEqual(len(main), 0, "main struct must be unchanged on error")
        combined = ' '.join(cm.output)
        self.assertIn('plugin.master', combined)
        self.assertIn('nonexistent', combined)

    def test_merge_scalar_path_logs_error(self):
        """Sub-path is a scalar → error logged, main struct unchanged."""
        main = collections.OrderedDict()
        with self.assertLogs('lib.item.structs', level='ERROR') as cm:
            self.structs.merge_substruct_to_struct(
                main, 'plugin.master.foo.type', main_struct_name='test_struct')
        self.assertEqual(len(main), 0)
        combined = ' '.join(cm.output)
        self.assertIn('plugin.master', combined)

    def test_merge_unknown_struct_logs_error(self):
        """No matching prefix at all → original error logged."""
        main = collections.OrderedDict()
        with self.assertLogs('lib.item.structs', level='ERROR') as cm:
            self.structs.merge_substruct_to_struct(
                main, 'completely.unknown', main_struct_name='test_struct')
        self.assertEqual(len(main), 0)
        combined = ' '.join(cm.output)
        self.assertIn('completely.unknown', combined)

    def test_merge_longest_match_wins(self):
        """'plugin.master.bar.direct_child' uses 'plugin.master.bar', not 'plugin.master'."""
        main = collections.OrderedDict()
        self.structs_conc.merge_substruct_to_struct(main, 'plugin.master.bar.direct_child')
        self.assertIn('special', main)
        self.assertNotIn('foo', main)
        self.assertNotIn('baz', main)

    def test_merge_does_not_overwrite_existing_keys(self):
        """First-wins rule: keys already in main_struct are not overwritten."""
        main = collections.OrderedDict([('type', 'original_type')])
        self.structs.merge_substruct_to_struct(main, 'plugin.master.bar.child1')
        # child1 has 'type: bool' but main already has 'type: original_type'
        self.assertEqual(main['type'], 'original_type')


if __name__ == '__main__':
    unittest.main(verbosity=2)
