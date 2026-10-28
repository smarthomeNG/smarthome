#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the exclusive-operation lock around Items' structural operations
(create_item, edit_item, remove_item, rename_item, copy_item,
remove_references): while one runs, a second one from another thread is
refused with ItemOperationBusyError instead of racing on the item tree and
the yaml files.
"""

import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.plugin
from lib.item.items import ItemOperationBusyError
from tests.test_item_rename import FakePlugin, _PersistedBase


class BlockingRenamePlugin(FakePlugin):
    """Parks inside the rename_item() hook until release() is called, so a
    test can attempt a second operation while the first is mid-flight."""

    def __init__(self):
        super().__init__()
        self.entered = threading.Event()
        self._release = threading.Event()

    def rename_item(self, item, old_path, new_path):
        self.entered.set()
        self._release.wait(timeout=10)
        return super().rename_item(item, old_path, new_path)

    def release(self):
        self._release.set()


class TestItemOperationLock(_PersistedBase):
    def setUp(self):
        super().setUp()
        self.items = self.sh.items
        self.target = self.items.create_item('target', {'type': 'num', 'child': {'type': 'num'}}, persist=True)
        self.other = self.items.create_item('other', {'type': 'num'}, persist=True)
        self.plugin = BlockingRenamePlugin()
        lib.plugin.Plugins._plugins.append(self.plugin)
        self.renamer_error = []

    def _rename_in_background(self, item, new_path):
        def run():
            try:
                self.items.rename_item(item, new_path)
            except Exception as e:
                self.renamer_error.append(e)

        thread = threading.Thread(target=run)
        thread.start()
        self.assertTrue(self.plugin.entered.wait(timeout=10), 'rename never reached the plugin hook')
        return thread

    def _finish(self, thread):
        self.plugin.release()
        thread.join(timeout=10)
        self.assertFalse(thread.is_alive())
        self.assertEqual(self.renamer_error, [])

    def test_operations_are_refused_while_a_rename_is_running(self):
        thread = self._rename_in_background(self.target, 'renamed')
        try:
            attempts = {
                'create_item': lambda: self.items.create_item('fresh', {'type': 'num'}, persist=True),
                'edit_item': lambda: self.items.edit_item(self.other, {'type': 'num', 'name': 'x'}),
                'remove_item': lambda: self.items.remove_item(self.other),
                'rename_item': lambda: self.items.rename_item(self.other, 'other2'),
                'copy_item': lambda: self.items.copy_item(self.other, 'other_copy'),
                'remove_references': lambda: self.items.remove_references('other'),
            }
            for name, attempt in attempts.items():
                with self.subTest(operation=name):
                    with self.assertRaises(ItemOperationBusyError):
                        attempt()
        finally:
            self._finish(thread)

        self.assertIsNotNone(self.items.return_item('other'))
        self.assertIsNone(self.items.return_item('fresh'))
        self.assertIsNotNone(self.items.return_item('renamed'))

    def test_busy_error_names_the_running_operation(self):
        thread = self._rename_in_background(self.target, 'renamed')
        try:
            with self.assertRaises(ItemOperationBusyError) as caught:
                self.items.edit_item(self.other, {'type': 'num'})
        finally:
            self._finish(thread)

        self.assertIn('rename_item', str(caught.exception))
        self.assertIn('target', str(caught.exception))

    def test_operations_work_again_once_the_running_one_finishes(self):
        thread = self._rename_in_background(self.target, 'renamed')
        self._finish(thread)

        self.items.edit_item(self.other, {'type': 'num', 'name': 'x'})
        self.items.create_item('fresh', {'type': 'num'}, persist=True)

        self.assertIsNotNone(self.items.return_item('fresh'))

    def test_lock_is_released_when_an_operation_raises(self):
        self.plugin.release()
        with self.assertRaises(ValueError):
            self.items.rename_item(self.other, 'no_such_parent.other')

        self.items.rename_item(self.other, 'other2')

        self.assertIsNotNone(self.items.return_item('other2'))

    def test_nested_operations_of_the_same_thread_are_not_refused(self):
        copied, _report = self.items.copy_item(self.target, 'target_copy')

        self.assertIsNotNone(self.items.return_item('target_copy.child'))
        self.assertEqual(copied.property.path, 'target_copy')


if __name__ == '__main__':
    unittest.main()
