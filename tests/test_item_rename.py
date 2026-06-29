#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for Items.rename_item() (lib/item/items.py) — renames an item
in-place (same parent only, v1) by mutating its path, see
~/.claude/handoff/shng-rename-item-design.md for the full design.
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


class FakePlugin:
    """Minimal stand-in for a SmartPlugin implementing PLUGIN_RENAME_ITEM,
    for testing the rename_item() hook call-site without any real plugin
    machinery."""

    def __init__(self):
        self.renamed_items = []

    def rename_item(self, item, old_path, new_path):
        self.renamed_items.append((item, old_path, new_path))
        return True


class FakeStoppablePlugin(FakePlugin):
    """FakePlugin plus the alive/STOP_ON_ITEM_CHANGE/stop()/run() surface
    Items.rename_item() inspects to decide whether (and how often) to
    pause a plugin around a rename — for testing that pausing happens
    once per rename operation, not once per descendant."""

    def __init__(self, stop_on_item_change=True):
        super().__init__()
        self.STOP_ON_ITEM_CHANGE = stop_on_item_change
        self.alive = True
        self.stop_calls = 0
        self.run_calls = 0

    def stop(self):
        self.stop_calls += 1
        self.alive = False

    def run(self):
        self.run_calls += 1
        self.alive = True


class RecordingScheduler:
    """Drop-in replacement for MockScheduler that records calls."""

    def __init__(self):
        self.calls = []

    def add(self, name, obj=None, prio=3, cron=None, cycle=None, value=None, offset=None, next=None, items=None):
        self.calls.append({'action': 'add', 'name': name, 'cron': cron, 'cycle': cycle, 'value': value, 'next': next})

    def remove(self, name):
        self.calls.append({'action': 'remove', 'name': name})

    def adds(self):
        return [c for c in self.calls if c['action'] == 'add']

    def removes(self):
        return [c for c in self.calls if c['action'] == 'remove']

    def added_names(self):
        return [c['name'] for c in self.adds()]


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
        self.sh = MockSmartHome()

    def tearDown(self):
        _reset()


class TestRenameItemBasic(_Base):
    def test_rename_updates_item_path_and_item_dict(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'new')

        self.assertIs(renamed, item)
        self.assertEqual(report, {'rewritten_references': [], 'failed_references': []})
        self.assertEqual(item.property.path, 'new')
        self.assertIsNone(self.sh.items.return_item('old'))
        self.assertIs(self.sh.items.return_item('new'), item)


class TestRenameItemValidatesNewName(_Base):
    def test_rename_refuses_colliding_name(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)
        self.sh.items.create_item('scheduler_clash', {'type': 'num'}, persist=False)

        with self.assertRaises(ValueError):
            self.sh.items.rename_item(item, 'scheduler')

        self.assertEqual(item.property.path, 'old')
        self.assertIsNotNone(self.sh.items.return_item('old'))

    def test_rename_to_same_path_is_a_silent_no_op(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'old')

        self.assertIs(renamed, item)
        self.assertEqual(report, {'rewritten_references': [], 'failed_references': []})
        self.assertEqual(item.property.path, 'old')


class TestRenameItemCascadesToDescendants(_Base):
    def test_rename_updates_descendant_paths(self):
        parent = self.sh.items.create_item(
            'old', {'type': 'num', 'child': {'type': 'num', 'grandchild': {'type': 'num'}}}, persist=False
        )
        child = self.sh.items.return_item('old.child')
        grandchild = self.sh.items.return_item('old.child.grandchild')

        self.sh.items.rename_item(parent, 'new')

        self.assertEqual(child.property.path, 'new.child')
        self.assertEqual(grandchild.property.path, 'new.child.grandchild')
        self.assertIsNone(self.sh.items.return_item('old.child'))
        self.assertIsNone(self.sh.items.return_item('old.child.grandchild'))
        self.assertIs(self.sh.items.return_item('new.child'), child)
        self.assertIs(self.sh.items.return_item('new.child.grandchild'), grandchild)
        self.assertIs(child.return_parent(), parent)


class TestRenameItemRekeysScheduler(_Base):
    def setUp(self):
        super().setUp()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def test_rename_removes_old_job_and_adds_new(self):
        item = self.sh.items.create_item('cy', {'type': 'num', 'cycle': '30'}, persist=False)

        self.sh.items.rename_item(item, 'cynew')

        self.assertIn('items.cy', [c['name'] for c in self.recorder.removes()])
        self.assertIn('items.cynew', self.recorder.added_names())


class TestRenameItemPersists(unittest.TestCase):
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

    def test_rename_moves_the_yaml_node_to_the_new_path(self):
        item = self.sh.items.create_item('old', {'type': 'num', 'eval': '1', 'child': {'type': 'num'}}, persist=True)

        self.sh.items.rename_item(item, 'new')

        data = self._read_file('created')
        self.assertNotIn('old', data)
        self.assertEqual(data['new']['eval'], '1')
        self.assertIn('child', data['new'])

    def test_move_to_new_parent_in_a_different_file_moves_the_yaml_node(self):
        self.sh.items.create_item('new_parent', {'type': 'num'}, parent=None, persist=True, filename='parent_file')
        item = self.sh.items.create_item('item', {'type': 'num', 'eval': '1'}, persist=True, filename='item_file')

        self.sh.items.rename_item(item, 'new_parent.item')

        old_data = self._read_file('item_file')
        self.assertNotIn('item', old_data)
        new_data = self._read_file('parent_file')
        self.assertEqual(new_data['new_parent']['item']['eval'], '1')
        self.assertEqual(item._filename, 'parent_file')

    def test_move_with_explicit_filename_overrides_the_default(self):
        self.sh.items.create_item('new_parent', {'type': 'num'}, parent=None, persist=True, filename='parent_file')
        item = self.sh.items.create_item('item', {'type': 'num', 'eval': '1'}, persist=True, filename='item_file')

        self.sh.items.rename_item(item, 'new_parent.item', filename='explicit_file')

        explicit_data = self._read_file('explicit_file')
        self.assertEqual(explicit_data['new_parent']['item']['eval'], '1')
        parent_data = self._read_file('parent_file')
        self.assertNotIn('item', parent_data.get('new_parent', {}))

    def test_move_to_top_level_falls_back_to_the_items_own_current_file(self):
        old_parent = self.sh.items.create_item(
            'old_parent', {'type': 'num'}, parent=None, persist=True, filename='parent_file'
        )
        item = self.sh.items.create_item(
            'old_parent.item', {'type': 'num', 'eval': '1'}, parent=old_parent, persist=True, filename='parent_file'
        )

        self.sh.items.rename_item(item, 'item')

        data = self._read_file('parent_file')
        self.assertNotIn('item', data.get('old_parent', {}))
        self.assertEqual(data['item']['eval'], '1')

    def test_rename_preserves_sibling_items_in_the_same_file(self):
        old_parent = self.sh.items.create_item(
            'old_parent', {'type': 'num'}, parent=None, persist=True, filename='parent_file'
        )
        item = self.sh.items.create_item(
            'old_parent.item', {'type': 'num', 'eval': '1'}, parent=old_parent, persist=True, filename='parent_file'
        )
        self.sh.items.create_item(
            'old_parent.sibling', {'type': 'num'}, parent=old_parent, persist=True, filename='parent_file'
        )

        self.sh.items.rename_item(item, 'item')

        data = self._read_file('parent_file')
        self.assertIn('sibling', data['old_parent'])

    def test_rename_refuses_to_persist_when_the_source_file_fails_to_parse(self):
        path = os.path.join(self.tmpdir.name, 'broken_file.yaml')
        with open(path, 'w', encoding='utf8') as f:
            f.write('a:\n  remark: one\n  remark: two\n')
        original_contents = open(path, encoding='utf8').read()

        item = self.sh.items.create_item('a', {'type': 'num'}, persist=False)
        item._filename = 'broken_file'

        with self.assertRaises(ValueError):
            self.sh.items.rename_item(item, 'b')

        with open(path, encoding='utf8') as f:
            self.assertEqual(f.read(), original_contents)


class TestRenameItemCallsPluginHook(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)

    def test_rename_calls_plugin_rename_item_hook_per_item_in_subtree(self):
        item = self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}}, persist=False)
        child = self.sh.items.return_item('old.child')

        self.sh.items.rename_item(item, 'new')

        self.assertIn((item, 'old', 'new'), self.fake_plugin.renamed_items)
        self.assertIn((child, 'old.child', 'new.child'), self.fake_plugin.renamed_items)


class TestRenameItemPausesEachAffectedPluginOnceForTheWholeOperation(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakeStoppablePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)

    def test_stop_and_run_are_each_called_once_regardless_of_descendant_count(self):
        item = self.sh.items.create_item(
            'old', {'type': 'num', 'a': {'type': 'num'}, 'b': {'type': 'num'}, 'c': {'type': 'num'}}, persist=False
        )

        self.sh.items.rename_item(item, 'new')

        self.assertEqual(self.fake_plugin.stop_calls, 1)
        self.assertEqual(self.fake_plugin.run_calls, 1)
        # the rekey hook itself still runs for every descendant
        self.assertEqual(len(self.fake_plugin.renamed_items), 4)

    def test_plugin_is_alive_again_after_the_rename(self):
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        self.sh.items.rename_item(item, 'new')

        self.assertTrue(self.fake_plugin.alive)

    def test_does_not_pause_a_plugin_with_stop_on_item_change_false(self):
        self.fake_plugin.STOP_ON_ITEM_CHANGE = False
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        self.sh.items.rename_item(item, 'new')

        self.assertEqual(self.fake_plugin.stop_calls, 0)
        self.assertEqual(self.fake_plugin.run_calls, 0)

    def test_does_not_resume_a_plugin_that_was_already_stopped_before_the_rename(self):
        self.fake_plugin.alive = False
        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        self.sh.items.rename_item(item, 'new')

        self.assertEqual(self.fake_plugin.stop_calls, 0)
        self.assertEqual(self.fake_plugin.run_calls, 0)
        self.assertFalse(self.fake_plugin.alive)


class TestRenameItemRewritesReferences(_Base):
    def test_rename_rewrites_eval_reference_in_another_item(self):
        target = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.old()'}, persist=False)

        renamed, report = self.sh.items.rename_item(target, 'new')

        self.assertEqual(source._eval, 'sh.new()')
        self.assertEqual(report, {'rewritten_references': ['source'], 'failed_references': []})

    def test_rename_rewrites_trigger_list_entry_in_another_item(self):
        target = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item('source', {'type': 'num', 'eval': '2', 'trigger': ['old']}, persist=False)

        renamed, report = self.sh.items.rename_item(target, 'new')

        self.assertEqual(source._trigger, ['new'])
        self.assertEqual(report, {'rewritten_references': ['source'], 'failed_references': []})

    def test_rename_rewrites_reference_to_a_descendant(self):
        parent = self.sh.items.create_item('old', {'type': 'num', 'child': {'type': 'num'}}, persist=False)
        source = self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.old.child()'}, persist=False)

        self.sh.items.rename_item(parent, 'new')

        self.assertEqual(source._eval, 'sh.new.child()')

    def test_rename_rewrites_only_the_matching_reference_in_a_multi_dependency_eval(self):
        # Unlike remove_references(), ambiguity (depends on more than one
        # item) doesn't matter here — every match gets rewritten, none
        # are skipped, since nothing is being removed, only repointed.
        target = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=False)
        self.sh.items.create_item('other', {'type': 'num', 'eval': '2'}, persist=False)
        source = self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.old() + sh.other()'}, persist=False)

        self.sh.items.rename_item(target, 'new')
        self.assertEqual(source._eval, 'sh.new() + sh.other()')


class TestRenameItemPluginHookFailureIsBestEffort(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')

    def test_one_plugins_rename_item_raising_does_not_abort_the_rename(self):
        class RaisingPlugin:
            def rename_item(self, item, old_path, new_path):
                raise RuntimeError('boom')

        good_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(RaisingPlugin())
        lib.plugin.Plugins._plugins.append(good_plugin)

        item = self.sh.items.create_item('old', {'type': 'num'}, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'new')

        self.assertEqual(item.property.path, 'new')
        self.assertIn((item, 'old', 'new'), good_plugin.renamed_items)


class TestRenameItemReferenceRewriteFailureIsBestEffort(_Base):
    def test_one_referencing_items_edit_failure_is_reported_not_raised(self):
        target = self.sh.items.create_item('old', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.old()'}, persist=False)
        other_source = self.sh.items.create_item('other_source', {'type': 'num', 'eval': 'sh.old()'}, persist=False)

        original_edit_item = self.sh.items.edit_item

        def failing_edit_item(item, config):
            if item is source:
                raise RuntimeError('simulated failure')
            return original_edit_item(item, config)

        self.sh.items.edit_item = failing_edit_item

        renamed, report = self.sh.items.rename_item(target, 'new')

        self.assertEqual(report['rewritten_references'], ['other_source'])
        self.assertEqual(len(report['failed_references']), 1)
        self.assertEqual(report['failed_references'][0][0], 'source')
        self.assertEqual(other_source._eval, 'sh.new()')


class TestReassignParent(_Base):
    def test_reassign_parent_updates_item_parent(self):
        old_parent = self.sh.items.create_item('old_parent', {'type': 'num'}, persist=False)
        new_parent = self.sh.items.create_item('new_parent', {'type': 'num'}, persist=False)
        child = self.sh.items.create_item('old_parent.child', {'type': 'num'}, parent=old_parent, persist=False)
        self.assertIs(child.return_parent(), old_parent)

        child._reassign_parent(new_parent)

        self.assertIs(child.return_parent(), new_parent)


class TestRenameItemMovesAcrossParents(_Base):
    def test_move_top_level_item_to_become_nested(self):
        new_parent = self.sh.items.create_item('new_parent', {'type': 'num'}, persist=False)
        item = self.sh.items.create_item('item', {'type': 'num'}, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'new_parent.item')

        self.assertIs(renamed, item)
        self.assertEqual(item.property.path, 'new_parent.item')
        self.assertIs(item.return_parent(), new_parent)
        self.assertIn(item, list(new_parent.return_children()))
        self.assertIsNone(self.sh.items.return_item('item'))
        self.assertIs(self.sh.items.return_item('new_parent.item'), item)

    def test_move_nested_item_to_become_top_level(self):
        old_parent = self.sh.items.create_item('old_parent', {'type': 'num'}, persist=False)
        item = self.sh.items.create_item('old_parent.item', {'type': 'num'}, parent=old_parent, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'item')

        self.assertEqual(item.property.path, 'item')
        self.assertTrue(item._is_top_of_item_tree())
        self.assertNotIn(item, list(old_parent.return_children()))
        self.assertFalse(hasattr(old_parent, 'item'))
        self.assertIs(self.sh.items.return_item('item'), item)
        self.assertIs(getattr(self.sh, 'item', None), item)

    def test_move_nested_item_to_a_different_real_parent(self):
        old_parent = self.sh.items.create_item('old_parent', {'type': 'num'}, persist=False)
        new_parent = self.sh.items.create_item('new_parent', {'type': 'num'}, persist=False)
        item = self.sh.items.create_item('old_parent.item', {'type': 'num'}, parent=old_parent, persist=False)

        renamed, report = self.sh.items.rename_item(item, 'new_parent.item')

        self.assertEqual(item.property.path, 'new_parent.item')
        self.assertIs(item.return_parent(), new_parent)
        self.assertNotIn(item, list(old_parent.return_children()))
        self.assertFalse(hasattr(old_parent, 'item'))
        self.assertIn(item, list(new_parent.return_children()))
        self.assertIs(self.sh.items.return_item('new_parent.item'), item)

    def test_move_into_own_subtree_is_refused(self):
        parent = self.sh.items.create_item('parent', {'type': 'num', 'child': {'type': 'num'}}, persist=False)

        with self.assertRaises(ValueError) as cm:
            self.sh.items.rename_item(parent, 'parent.child.parent')

        self.assertIn('cannot become a child of itself', str(cm.exception))
        self.assertEqual(parent.property.path, 'parent')

    def test_move_under_nonexistent_parent_is_refused(self):
        item = self.sh.items.create_item('item', {'type': 'num'}, persist=False)

        with self.assertRaises(ValueError):
            self.sh.items.rename_item(item, 'does.not.exist.item')

        self.assertEqual(item.property.path, 'item')
