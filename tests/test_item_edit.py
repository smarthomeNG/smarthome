#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for editing an existing item's attributes at runtime (lib/item/items.py
Items.edit_item()).

Coverage
--------
TODO: filled in incrementally, test by test.
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


class FakePlugin:
    """Minimal stand-in for a SmartPlugin implementing PLUGIN_REMOVE_ITEM/
    PLUGIN_PARSE_ITEM, for testing the plugin remove/parse bracket in
    Items.edit_item() without any real plugin machinery."""

    def __init__(self, shortname='fakeplugin'):
        self.removed_items = []
        self.parsed_items = []
        self._shortname = shortname

    def get_shortname(self):
        return self._shortname

    def remove_item(self, item):
        self.removed_items.append(item)
        return True

    def parse_item(self, item):
        self.parsed_items.append(item)
        return None


class FakeStoppablePlugin(FakePlugin):
    """FakePlugin plus the alive/STOP_ON_ITEM_CHANGE/stop()/run() surface
    Items.edit_item() inspects to decide whether to pause a plugin around
    an edit - mirrors test_item_rename.py's FakeStoppablePlugin, same
    pause/resume contract."""

    def __init__(self, stop_on_item_change=True, shortname='fakeplugin'):
        super().__init__(shortname=shortname)
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


def _make_sh():
    _reset()
    return MockSmartHome()


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


class _Base(unittest.TestCase):
    def setUp(self):
        self.sh = _make_sh()
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()


class TestEditItemPreservesIdentity(_Base):
    def test_edit_item_returns_the_same_object(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        edited = self.sh.items.edit_item(item, {'type': 'num'})

        self.assertIs(edited, item)

    def test_edit_item_updates_a_generic_attribute(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'my_custom_attr': 'old'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'my_custom_attr': 'new'})

        self.assertEqual(item.conf['my_custom_attr'], 'new')


class TestEditItemPreservesValueAndHistory(_Base):
    def test_edit_item_preserves_current_value(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(item(), 5)

    def test_edit_item_preserves_history(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')
        prev_value_before = item.prev_value()

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(item.prev_value(), prev_value_before)


class TestEditItemTypeChange(_Base):
    def test_edit_item_casts_preserved_value_to_new_type(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        item(5, caller='test')

        self.sh.items.edit_item(item, {'type': 'str'})

        self.assertEqual(item(), '5')

    def test_edit_item_falls_back_to_type_default_when_cast_fails(self):
        item = self.sh.items.create_item('target', {'type': 'str'}, persist=False)
        item('not a number', caller='test')

        self.sh.items.edit_item(item, {'type': 'num'})

        self.assertEqual(item(), 0)


class TestEditItemAllowsIncomingStructuralReferences(_Base):
    def test_edit_item_type_change_with_live_incoming_trigger_is_safe(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )
        self.assertIn(source, target.get_item_triggers())

        self.sh.items.edit_item(target, {'type': 'str'})

        self.assertIn(source, target.get_item_triggers())

    def test_edit_item_succeeds_when_item_is_a_trigger_target(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target()', 'eval_trigger': 'target'}, persist=False
        )
        self.assertIn(source, target.get_item_triggers())

        self.sh.items.edit_item(target, {'type': 'num', 'eval': '1', 'remark': 'edited'})

        self.assertEqual(target.property.remark, 'edited')
        self.assertIn(source, target.get_item_triggers())

    def test_edit_item_allows_plain_eval_reference_with_no_trigger(self):
        target = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=False)
        self.sh.items.create_item('source', {'type': 'num', 'eval': 'sh.target()'}, persist=False)

        self.sh.items.edit_item(target, {'type': 'num', 'eval': '1', 'remark': 'edited'})


class TestEditItemRewiresOwnOutgoingTriggers(_Base):
    def test_edit_item_moving_its_own_trigger_rewires_correctly(self):
        target_a = self.sh.items.create_item('target_a', {'type': 'num', 'eval': '1'}, persist=False)
        target_b = self.sh.items.create_item('target_b', {'type': 'num', 'eval': '2'}, persist=False)
        source = self.sh.items.create_item(
            'source', {'type': 'num', 'eval': 'sh.target_a()', 'eval_trigger': 'target_a'}, persist=False
        )
        self.assertIn(source, target_a.get_item_triggers())
        self.assertNotIn(source, target_b.get_item_triggers())

        self.sh.items.edit_item(source, {'type': 'num', 'eval': 'sh.target_b()', 'eval_trigger': 'target_b'})

        self.assertNotIn(source, target_a.get_item_triggers())
        self.assertIn(source, target_b.get_item_triggers())


class TestEditItemRewiresScheduler(_Base):
    def test_edit_item_changing_cycle_removes_old_job_and_adds_new(self):
        item = self.sh.items.create_item('cy', {'type': 'num', 'cycle': '30'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'cycle': '60'})

        self.assertIn('items.cy', [c['name'] for c in self.recorder.removes()])
        cycle_adds = [c for c in self.recorder.adds() if c['name'] == 'items.cy']
        self.assertEqual(cycle_adds[-1]['cycle'], 60)


class TestEditItemRebindsPlugins(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')
        self.fake_plugin = FakePlugin()
        lib.plugin.Plugins._plugins.append(self.fake_plugin)

    def test_edit_item_calls_plugin_remove_then_parse(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        self.assertIn(item, self.fake_plugin.parsed_items)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertIn(item, self.fake_plugin.removed_items)
        self.assertEqual(self.fake_plugin.parsed_items.count(item), 2)


class TestEditItemPausesAndResumesStoppablePlugins(_Base):
    """Regression test: edit_item() used to call plugin.remove_item(), which
    stops a STOP_ON_ITEM_CHANGE plugin internally, but never called run()
    again afterward - any such plugin (e.g. one driving a background
    asyncio loop) stayed dead after any item edit touching it. Fixed by
    giving edit_item() the same pause-once/resume-once wrapper
    Items.rename_item() already had."""

    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')

    def test_stoppable_plugin_is_resumed_after_edit(self):
        plugin = FakeStoppablePlugin(stop_on_item_change=True)
        lib.plugin.Plugins._plugins.append(plugin)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(plugin.stop_calls, 1)
        self.assertEqual(plugin.run_calls, 1)
        self.assertTrue(plugin.alive)

    def test_plugin_already_stopped_before_edit_is_left_stopped(self):
        plugin = FakeStoppablePlugin(stop_on_item_change=True)
        plugin.alive = False
        lib.plugin.Plugins._plugins.append(plugin)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(plugin.stop_calls, 0)
        self.assertEqual(plugin.run_calls, 0)
        self.assertFalse(plugin.alive)

    def test_non_stop_on_item_change_plugin_is_never_paused(self):
        plugin = FakeStoppablePlugin(stop_on_item_change=False)
        lib.plugin.Plugins._plugins.append(plugin)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(plugin.stop_calls, 0)
        self.assertEqual(plugin.run_calls, 0)
        self.assertTrue(plugin.alive)


class TestEditItemScopesPauseToRelevantPlugins(_Base):
    """Regression test: edit_item() used to pause every STOP_ON_ITEM_CHANGE
    plugin in the whole installation on every item edit, regardless of
    whether that plugin had anything to do with the edited item - the root
    cause of the matter plugin's self-edit-during-startup recursion.
    plugin.remove_item()/plugin.parse_item() still run for every plugin
    unconditionally (unchanged, verified below); only the stop()/run()
    bracket is scoped down, via Items.plugin_attributes/
    plugin_attribute_prefixes, to plugins with a plausible stake in this
    specific edit."""

    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')

    def test_plugin_with_no_stake_in_the_item_is_not_paused(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute('owner', 'owner_attr', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(owner.stop_calls, 0)
        self.assertEqual(owner.run_calls, 0)
        # remove_item()/parse_item() still run unconditionally (Option B)
        self.assertIn(item, owner.removed_items)
        self.assertEqual(owner.parsed_items.count(item), 2)

    def test_plugin_whose_owned_attribute_is_unchanged_is_not_paused(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute('owner', 'owner_attr', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num', 'owner_attr': 'x'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'owner_attr': 'x', 'remark': 'edited'})

        self.assertEqual(owner.stop_calls, 0)
        self.assertEqual(owner.run_calls, 0)

    def test_plugin_whose_owned_attribute_changes_is_paused(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute('owner', 'owner_attr', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num', 'owner_attr': 'x'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'owner_attr': 'y'})

        self.assertEqual(owner.stop_calls, 1)
        self.assertEqual(owner.run_calls, 1)

    def test_plugin_owning_attribute_prefix_is_paused_on_prefixed_key_change(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute_prefix('owner', 'owner_', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num', 'owner_mode': 'x'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'owner_mode': 'y'})

        self.assertEqual(owner.stop_calls, 1)
        self.assertEqual(owner.run_calls, 1)

    def test_type_change_pauses_plugin_with_a_stake_even_if_its_own_key_is_unchanged(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute('owner', 'owner_attr', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num', 'owner_attr': 'x'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'str', 'owner_attr': 'x'})

        self.assertEqual(owner.stop_calls, 1)
        self.assertEqual(owner.run_calls, 1)

    def test_type_change_does_not_pause_a_plugin_with_no_stake_at_all(self):
        owner = FakeStoppablePlugin(shortname='owner')
        self.sh.items.add_plugin_attribute('owner', 'owner_attr', {'type': 'str'})
        lib.plugin.Plugins._plugins.append(owner)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'str'})

        self.assertEqual(owner.stop_calls, 0)
        self.assertEqual(owner.run_calls, 0)

    def test_plugin_that_never_registered_any_attribute_is_always_paused(self):
        unregistered = FakeStoppablePlugin(shortname='unregistered')
        lib.plugin.Plugins._plugins.append(unregistered)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertEqual(unregistered.stop_calls, 1)
        self.assertEqual(unregistered.run_calls, 1)


class TestEditItemNotifyPluginsFalse(_Base):
    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')

    def test_notify_plugins_false_skips_remove_parse_and_pause(self):
        plugin = FakeStoppablePlugin(stop_on_item_change=True)
        lib.plugin.Plugins._plugins.append(plugin)
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        plugin.removed_items.clear()
        plugin.parsed_items.clear()

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'}, notify_plugins=False)

        self.assertEqual(plugin.removed_items, [])
        self.assertEqual(plugin.parsed_items, [])
        self.assertEqual(plugin.stop_calls, 0)
        self.assertEqual(plugin.run_calls, 0)
        self.assertEqual(item.property.remark, 'edited')

    def test_notify_plugins_false_logs_notice(self):
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        with self.assertLogs('lib.item.items', level='NOTICE') as cm:
            self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'}, notify_plugins=False)

        self.assertTrue(any('notify_plugins=False' in message for message in cm.output))


class TestEditItemPluginHookFailureIsolation(_Base):
    """Regression test: plugin.remove_item()/plugin.parse_item() calls were
    unguarded - one plugin raising aborted the whole edit (config never
    applied, no other plugin's remove_item()/parse_item() ran). Now
    isolated per plugin, mirroring the stop()/run() bracket's existing
    try/except pattern."""

    def setUp(self):
        super().setUp()
        lib.plugin.Plugins(self.sh, 'test')

    def test_remove_item_failure_in_one_plugin_does_not_block_others_or_the_config_apply(self):
        class RaisingPlugin(FakePlugin):
            def remove_item(self, item):
                raise RuntimeError('boom')

        raiser = RaisingPlugin(shortname='raiser')
        survivor = FakePlugin(shortname='survivor')
        lib.plugin.Plugins._plugins.extend([raiser, survivor])
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)
        survivor.removed_items.clear()

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        self.assertIn(item, survivor.removed_items)
        self.assertEqual(item.property.remark, 'edited')

    def test_parse_item_failure_does_not_leak_a_stale_update_into_the_next_plugin(self):
        class OkPlugin(FakePlugin):
            def parse_item(self, item):
                self.parsed_items.append(item)
                return self.update_item

            def update_item(self, item, caller=None, source=None, dest=None):
                pass

        class RaisingParsePlugin(FakePlugin):
            def __init__(self, shortname):
                super().__init__(shortname=shortname)
                self.call_count = 0

            def parse_item(self, item):
                # only raises from the 2nd call (edit), not the 1st
                # (construction) - Item.__init__'s own parse_item() loop
                # isn't guarded, that's a separate, pre-existing gap
                self.call_count += 1
                if self.call_count > 1:
                    raise RuntimeError('boom')
                self.parsed_items.append(item)
                return None

        ok = OkPlugin(shortname='ok')
        raiser = RaisingParsePlugin(shortname='raiser')
        lib.plugin.Plugins._plugins.extend([ok, raiser])
        item = self.sh.items.create_item('target', {'type': 'num'}, persist=False)

        self.sh.items.edit_item(item, {'type': 'num', 'remark': 'edited'})

        # 2, not 3: one from create_item()'s own parse_item() pass, one
        # from edit_item()'s. A 3rd would mean raiser's failed parse_item()
        # call leaked ok's stale `update` value into its own iteration.
        triggers = item.get_method_triggers()
        self.assertEqual(triggers.count(ok.update_item), 2)


class TestEditItemPersists(unittest.TestCase):
    def setUp(self):
        _reset()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.sh = MockSmartHome()
        self.sh._items_dir = self.tmpdir.name
        self.sh._created_items_file = 'created'
        self.recorder = RecordingScheduler()
        self.sh.scheduler = self.recorder

    def tearDown(self):
        _reset()

    def _read_file(self, filename):
        import lib.shyaml as shyaml

        yf = shyaml.yamlfile(os.path.join(self.tmpdir.name, filename))
        yf.load()
        return yf.data

    def test_edit_item_persists_new_config_to_its_existing_file(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'eval': '1'}, persist=True)

        self.sh.items.edit_item(item, {'type': 'num', 'eval': '2'})

        data = self._read_file('created')
        self.assertEqual(data['target']['eval'], '2')

    def test_edit_item_omitted_attribute_is_removed_from_file(self):
        item = self.sh.items.create_item('target', {'type': 'num', 'eval': '1', 'remark': 'old'}, persist=True)

        self.sh.items.edit_item(item, {'type': 'num', 'eval': '1'})

        data = self._read_file('created')
        self.assertNotIn('remark', data['target'])

    def test_edit_item_preserves_childs_yaml_entry(self):
        self.sh.items.create_item('parent', {'type': 'num', 'eval': '1', 'child': {'type': 'str'}}, persist=True)
        parent = self.sh.items.return_item('parent')

        self.sh.items.edit_item(parent, {'type': 'num', 'eval': '2'})

        data = self._read_file('created')
        self.assertIn('child', data['parent'])
        self.assertEqual(data['parent']['child']['type'], 'str')
