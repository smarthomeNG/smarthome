#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.copy_item() (lib/item/items.py) — copies an item's
entire subtree to a new path as an independent clone, reusing
create_item() for the actual write/construct step. See its docstring
for the design rationale (only persisted items, defaults to the
source's own file, rewrites in-subtree self-references).
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.item.item
import lib.item.items
import lib.plugin
from lib.item.items import Items
from tests.mock.core import MockSmartHome


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None
    lib.plugin._plugins_instance = None
    lib.plugin.Plugins._plugins = []


class _Base(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'

    def tearDown(self):
        _reset()

    def _read_file(self, filename):
        import lib.shyaml as shyaml

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        yf.load()
        return yf.data


class TestCopyItemBasic(_Base):
    def test_copy_creates_an_independent_item_with_the_same_config(self):
        original = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=True)

        copy, _report = self.sh.items.copy_item(original, 'new')

        self.assertIsNotNone(copy)
        self.assertIsNot(copy, original)
        self.assertEqual(copy.property.path, 'new')
        self.assertIsNotNone(self.sh.items.return_item('old'))
        self.assertIsNotNone(self.sh.items.return_item('new'))
        self.assertEqual(copy._eval, '1')

    def test_copy_leaves_the_original_untouched(self):
        original = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=True)

        self.sh.items.copy_item(original, 'new')

        self.assertEqual(original.property.path, 'old')
        self.assertEqual(original._eval, '1')
        self.assertIs(self.sh.items.return_item('old'), original)

    def test_copy_to_same_path_raises(self):
        original = self.sh.items.create_item('old', {'type': 'num'}, persist=True)

        with self.assertRaises(ValueError):
            self.sh.items.copy_item(original, 'old')

    def test_copy_non_persisted_item_raises(self):
        original = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        with self.assertRaises(ValueError):
            self.sh.items.copy_item(original, 'new')

    def test_copy_refuses_colliding_name(self):
        original = self.sh.items.create_item('old', {'type': 'num'}, persist=True)
        self.sh.items.create_item('scheduler_clash', {'type': 'num'}, persist=False)

        copy, _report = self.sh.items.copy_item(original, 'scheduler')

        self.assertIsNone(copy)


class TestCopyItemCascadesToChildren(_Base):
    def test_copy_duplicates_the_whole_subtree(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}}, persist=True
        )
        original = self.sh.items.return_item('old')

        self.sh.items.copy_item(original, 'new')

        child = self.sh.items.return_item('new.child')
        grandchild = self.sh.items.return_item('new.child.grandchild')
        self.assertIsNotNone(child)
        self.assertIsNotNone(grandchild)
        self.assertIs(child.return_parent(), self.sh.items.return_item('new'))
        # the source subtree survives fully intact
        self.assertIsNotNone(self.sh.items.return_item('old.child'))
        self.assertIsNotNone(self.sh.items.return_item('old.child.grandchild'))

    def test_include_children_false_copies_only_the_item_itself(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'eval': '1', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, _report = self.sh.items.copy_item(original, 'new', include_children=False)

        self.assertEqual(copy._eval, '1')
        self.assertIsNone(self.sh.items.return_item('new.child'))
        # the source subtree survives fully intact
        self.assertIsNotNone(self.sh.items.return_item('old.child'))
        self.assertIsNotNone(self.sh.items.return_item('old.child.grandchild'))

    def test_include_children_false_writes_no_child_blocks_to_the_yaml_file(self):
        self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}}, persist=True)
        original = self.sh.items.return_item('old')

        self.sh.items.copy_item(original, 'new', include_children=False)

        data = self._read_file('created')
        self.assertNotIn('child', data['new'])
        self.assertIn('child', data['old'])


class TestCopyItemPersists(_Base):
    def test_copy_writes_a_new_yaml_node_at_the_new_path(self):
        original = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=True)

        self.sh.items.copy_item(original, 'new')

        data = self._read_file('created')
        self.assertIn('old', data)
        self.assertIn('new', data)
        self.assertEqual(data['new']['eval'], '1')

    def test_copy_defaults_to_the_source_items_own_file_even_under_a_different_parent(self):
        self.sh.items.create_item('new_parent', {'type': 'num'}, parent=None, persist=True, filename='parent_file')
        item = self.sh.items.create_item('item', {'type': 'num', 'eval': '1'}, persist=True, filename='item_file')

        copy, _report = self.sh.items.copy_item(item, 'new_parent.copy')

        self.assertEqual(copy._filename, 'item_file')
        item_file_data = self._read_file('item_file')
        self.assertIn('copy', item_file_data.get('new_parent', {}))
        parent_file_data = self._read_file('parent_file')
        self.assertNotIn('copy', parent_file_data.get('new_parent', {}))

    def test_copy_with_explicit_filename_overrides_the_default(self):
        original = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=True, filename='item_file')

        self.sh.items.copy_item(original, 'new', filename='explicit_file')

        explicit_data = self._read_file('explicit_file')
        self.assertEqual(explicit_data['new']['eval'], '1')
        item_file_data = self._read_file('item_file')
        self.assertNotIn('new', item_file_data)

    def test_copy_preserves_sibling_items_in_the_same_file(self):
        parent = self.sh.items.create_item('parent', {'type': 'num'}, parent=None, persist=True, filename='f')
        self.sh.items.create_item('parent.item', {'type': 'num'}, parent=parent, persist=True, filename='f')
        item = self.sh.items.create_item('parent.other', {'type': 'num'}, parent=parent, persist=True, filename='f')

        self.sh.items.copy_item(item, 'parent.other_copy')

        data = self._read_file('f')
        self.assertIn('item', data['parent'])
        self.assertIn('other', data['parent'])
        self.assertIn('other_copy', data['parent'])


class TestCopyItemMissingParents(_Base):
    def test_copy_under_nonexistent_parent_raises_by_default(self):
        original = self.sh.items.create_item('old', {'type': 'num'}, persist=True)

        with self.assertRaises(ValueError):
            self.sh.items.copy_item(original, 'does.not.exist.new')

    def test_copy_with_create_missing_parents_auto_creates_the_chain(self):
        original = self.sh.items.create_item('old', {'type': 'num'}, persist=True)

        copy, _report = self.sh.items.copy_item(original, 'a.b.new', create_missing_parents=True)

        self.assertIsNotNone(copy)
        self.assertIsNotNone(self.sh.items.return_item('a'))
        self.assertIsNotNone(self.sh.items.return_item('a.b'))
        self.assertIsNotNone(self.sh.items.return_item('a.b.new'))


class TestCopyItemRewritesSelfReferences(_Base):
    def test_copy_rewrites_an_absolute_eval_reference_to_a_sibling_within_the_subtree(self):
        self.sh.items.create_item(
            'old',
            {
                'type': 'num',
                'child_a': {'type': 'num', 'eval': '1'},
                'child_b': {'type': 'num', 'eval': 'sh.old.child_a()'},
            },
            persist=True,
        )
        original = self.sh.items.return_item('old')

        self.sh.items.copy_item(original, 'new')

        copied_child_b = self.sh.items.return_item('new.child_b')
        self.assertEqual(copied_child_b._eval, 'sh.new.child_a()')
        # the original subtree's own reference is untouched
        original_child_b = self.sh.items.return_item('old.child_b')
        self.assertEqual(original_child_b._eval, 'sh.old.child_a()')

    def test_copy_rewrites_a_self_reference_to_the_copied_items_own_new_path(self):
        original = self.sh.items.create_item('old', {'type': 'num', 'eval': 'sh.old()'}, persist=True)

        copy, _report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._eval, 'sh.new()')

    def test_copy_rewrites_bare_trigger_reference_to_a_descendant(self):
        self.sh.items.create_item(
            'old',
            {
                'type': 'num',
                'child': {'type': 'num', 'eval': '1'},
                'watcher': {'type': 'num', 'eval': '2', 'trigger': ['old.child']},
            },
            persist=True,
        )
        original = self.sh.items.return_item('old')

        self.sh.items.copy_item(original, 'new')

        copied_watcher = self.sh.items.return_item('new.watcher')
        self.assertEqual(copied_watcher._trigger, ['new.child'])

    def test_copy_does_not_rewrite_a_reference_to_an_item_outside_the_subtree(self):
        self.sh.items.create_item('unrelated', {'type': 'num', 'eval': '1'}, persist=True)
        self.sh.items.create_item('old', {'type': 'num', 'eval': 'sh.unrelated() + sh.old()'}, persist=True)
        original = self.sh.items.return_item('old')

        copy, _report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._eval, 'sh.unrelated() + sh.new()')


class TestCopyItemLeavesUncopiedAbsoluteReferencesAlone(_Base):
    def test_absolute_reference_to_a_left_behind_child_is_left_pointing_at_the_original_and_reported(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num'}, 'eval': 'sh.old.child()'}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new', include_children=False)

        self.assertEqual(copy._eval, 'sh.old.child()')
        self.assertEqual(
            report['left_pointing_at_original'], [{'item': 'new', 'attribute': 'eval', 'reference': 'old.child'}]
        )

    def test_absolute_reference_to_an_unrelated_item_is_never_reported(self):
        self.sh.items.create_item('unrelated', {'type': 'num'}, persist=True)
        self.sh.items.create_item('old', {'type': 'num', 'eval': 'sh.unrelated()'}, persist=True)
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._eval, 'sh.unrelated()')
        self.assertEqual(report['left_pointing_at_original'], [])

    def test_bare_trigger_reference_to_a_left_behind_child_is_left_alone_and_reported(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num'}, 'trigger': ['old.child']}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new', include_children=False)

        self.assertEqual(copy._trigger, ['old.child'])
        self.assertEqual(
            report['left_pointing_at_original'], [{'item': 'new', 'attribute': 'trigger', 'reference': 'old.child'}]
        )

    def test_property_accessor_suffix_does_not_confuse_the_copied_check(self):
        """A property accessor like .last_change isn't a separate item —
        the self-reference should be rewritten based on old.child (the
        real item), not treated as "old.child.last_change" not being
        copied."""
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num'}, 'eval': 'sh.old.child.last_change'}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._eval, 'sh.new.child.last_change')
        self.assertEqual(report['left_pointing_at_original'], [])


class TestCopyItemFlagsRelativeReferences(_Base):
    def test_relative_child_reference_inside_a_fully_copied_subtree_is_silent(self):
        # 'sh..child()' is the sh.-embedded form of the bare '.child' relative
        # reference - one extra dot, since the mandatory 'sh.' prefix supplies
        # the first one.
        self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}, 'eval': 'sh..child()'}, persist=True)
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new')

        # relative TEXT is never rewritten - still correct since new.child
        # exists (runtime ._eval is always expanded to absolute regardless,
        # for every item - check the persisted YAML instead).
        data = self._read_file('created')
        self.assertEqual(data['new']['eval'], 'sh..child()')
        self.assertEqual(report['relative_references_flagged'], [])
        self.assertIsNotNone(self.sh.items.return_item('new.child'))

    def test_relative_child_reference_left_behind_by_include_children_false_is_flagged(self):
        self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}, 'eval': 'sh..child()'}, persist=True)
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new', include_children=False)

        data = self._read_file('created')
        self.assertEqual(data['new']['eval'], 'sh..child()')
        self.assertEqual(len(report['relative_references_flagged']), 1)
        flagged = report['relative_references_flagged'][0]
        self.assertEqual(flagged['item'], 'new')
        self.assertEqual(flagged['attribute'], 'eval')
        self.assertEqual(flagged['reference'], '.child')
        self.assertEqual(flagged['resolved_original_target'], 'old.child')
        self.assertEqual(flagged['reason'], 'not_copied')

    def test_relative_reference_escaping_the_subtree_is_silent_when_the_target_stays_the_same(self):
        # 'sh...sibling()' is the sh.-embedded form of the bare '..sibling'
        # (two-dot, one-level-up) relative reference.
        self.sh.items.create_item(
            'group',
            {'type': 'foo', 'old': {'type': 'num', 'eval': 'sh...sibling()'}, 'sibling': {'type': 'num'}},
            persist=True,
        )
        original = self.sh.items.return_item('group.old')

        # copied under the SAME parent - '..sibling' still resolves to 'group.sibling' either way
        copy, report = self.sh.items.copy_item(original, 'group.new')

        data = self._read_file('created')
        self.assertEqual(data['group']['new']['eval'], 'sh...sibling()')
        self.assertEqual(report['relative_references_flagged'], [])

    def test_relative_reference_escaping_the_subtree_is_flagged_when_the_target_changes(self):
        self.sh.items.create_item(
            'group1',
            {'type': 'foo', 'old': {'type': 'num', 'eval': 'sh...sibling()'}, 'sibling': {'type': 'num'}},
            persist=True,
        )
        self.sh.items.create_item('group2', {'type': 'foo', 'sibling': {'type': 'num'}}, persist=True)
        original = self.sh.items.return_item('group1.old')

        copy, report = self.sh.items.copy_item(original, 'group2.new')

        data = self._read_file('created')
        self.assertEqual(data['group2']['new']['eval'], 'sh...sibling()')
        self.assertEqual(len(report['relative_references_flagged']), 1)
        flagged = report['relative_references_flagged'][0]
        self.assertEqual(flagged['reference'], '..sibling')
        self.assertEqual(flagged['resolved_original_target'], 'group1.sibling')
        self.assertEqual(flagged['resolved_new_target'], 'group2.sibling')
        self.assertEqual(flagged['reason'], 'target_may_differ')

    def test_bare_relative_trigger_reference_left_behind_is_flagged(self):
        self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}, 'trigger': ['.child']}, persist=True)
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new', include_children=False)

        self.assertEqual(copy._trigger, ['.child'])
        self.assertEqual(len(report['relative_references_flagged']), 1)
        self.assertEqual(report['relative_references_flagged'][0]['reason'], 'not_copied')


class TestCopyItemCoversCycleAutotimerAndHysteresisThresholds(_Base):
    def test_cycle_self_reference_is_rewritten_when_target_is_copied(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num'}, 'cycle': '5 = sh.old.child()'}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._cycle_value, 'sh.new.child()')
        self.assertEqual(report['left_pointing_at_original'], [])

    def test_autotimer_self_reference_left_behind_is_flagged(self):
        self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num'}, 'autotimer': '5 = sh.old.child()'}, persist=True
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new', include_children=False)

        self.assertEqual(copy._autotimer_value, 'sh.old.child()')
        self.assertEqual(
            report['left_pointing_at_original'], [{'item': 'new', 'attribute': 'autotimer', 'reference': 'old.child'}]
        )

    def test_hysteresis_thresholds_are_rewritten_when_target_is_copied(self):
        self.sh.items.create_item(
            'old',
            {
                'type': 'num',
                'child': {'type': 'num'},
                'hysteresis_upper_threshold': 'sh.old.child()',
                'hysteresis_lower_threshold': 'sh.old.child() - 1',
            },
            persist=True,
        )
        original = self.sh.items.return_item('old')

        copy, report = self.sh.items.copy_item(original, 'new')

        self.assertEqual(copy._hysteresis_upper_threshold, 'sh.new.child()')
        self.assertEqual(copy._hysteresis_lower_threshold, 'sh.new.child() - 1')
        self.assertEqual(report['left_pointing_at_original'], [])


if __name__ == '__main__':
    unittest.main()
