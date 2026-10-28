#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Operations that touch many items of the same yaml file (rename_item and remove_references rewriting
every referencing item) parse and save each file once, not once per touched item.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.shyaml as shyaml
from tests.test_item_rename import _PersistedBase


class _YamlIoCounter:
    """Calls through to yamlfile.load()/save() and counts them per file name."""

    def __init__(self):
        self.loads = {}
        self.saves = {}

    def __enter__(self):
        real_load, real_save = shyaml.yamlfile.load, shyaml.yamlfile.save
        counter = self

        def load(yf):
            counter.loads[os.path.basename(yf.filename)] = counter.loads.get(os.path.basename(yf.filename), 0) + 1
            return real_load(yf)

        def save(yf):
            counter.saves[os.path.basename(yf.filename)] = counter.saves.get(os.path.basename(yf.filename), 0) + 1
            return real_save(yf)

        self._patches = [
            mock.patch.object(shyaml.yamlfile, 'load', load),
            mock.patch.object(shyaml.yamlfile, 'save', save),
        ]
        for patch in self._patches:
            patch.start()
        return self

    def __exit__(self, *exc):
        for patch in self._patches:
            patch.stop()


class _ManyReferencesBase(_PersistedBase):
    def _build(self, referencing, filename='f'):
        """A persisted target and *referencing* items that all reference it by eval and on_change."""
        items = self.sh.items
        items.create_item('target', {'type': 'num'}, persist=True, filename=filename)
        for index in range(referencing):
            items.create_item(
                f'ref{index}',
                {'type': 'num', 'eval': 'sh.target() + 1', 'on_change': ['target = value']},
                persist=True,
                filename=filename,
            )
        return items.return_item('target')


class TestRenameParsesEachFileOnce(_ManyReferencesBase):
    def _rename_io(self, referencing):
        target = self._build(referencing)
        with _YamlIoCounter() as io:
            self.sh.items.rename_item(target, 'renamed')
        return io

    def test_yaml_io_does_not_grow_with_the_number_of_referencing_items(self):
        few = self._rename_io(2)
        self.setUp()
        many = self._rename_io(12)

        self.assertEqual(few.loads, many.loads)
        self.assertEqual(few.saves, many.saves)

    def test_every_reference_is_rewritten_in_the_file(self):
        target = self._build(12)

        _, report = self.sh.items.rename_item(target, 'renamed')

        data = self._read_file('f')
        self.assertEqual(12, len(report['rewritten_references']))
        for index in range(12):
            self.assertEqual('sh.renamed() + 1', data[f'ref{index}']['eval'])
            self.assertEqual(['renamed = value'], data[f'ref{index}']['on_change'])


class TestRemoveReferencesParsesEachFileOnce(_ManyReferencesBase):
    def _remove_io(self, referencing):
        self._build(referencing)
        with _YamlIoCounter() as io:
            self.sh.items.remove_references('target')
        return io

    def test_yaml_io_does_not_grow_with_the_number_of_referencing_items(self):
        few = self._remove_io(2)
        self.setUp()
        many = self._remove_io(12)

        self.assertEqual(few.loads, many.loads)
        self.assertEqual(few.saves, many.saves)

    def test_every_unambiguous_reference_is_removed_from_the_file(self):
        self._build(12)

        result = self.sh.items.remove_references('target')

        data = self._read_file('f')
        self.assertEqual(12, len(result['removed']))
        for index in range(12):
            self.assertNotIn('eval', data[f'ref{index}'])
            self.assertEqual(['target = value'], data[f'ref{index}']['on_change'])


class TestRenameWithReferencesInSeveralFiles(_ManyReferencesBase):
    def test_each_referencing_file_is_parsed_and_saved_once(self):
        target = self._build(3, filename='f')
        for index in range(3):
            self.sh.items.create_item(
                f'other{index}', {'type': 'num', 'eval': 'sh.target() + 1'}, persist=True, filename='g'
            )

        with _YamlIoCounter() as io:
            self.sh.items.rename_item(target, 'renamed')

        self.assertEqual(1, io.saves['g'])
        self.assertEqual(1, io.loads['g'])
        for index in range(3):
            self.assertEqual('sh.renamed() + 1', self._read_file('g')[f'other{index}']['eval'])
            self.assertEqual('sh.renamed() + 1', self._read_file('f')[f'ref{index}']['eval'])


class TestBatchedRewriteIsBestEffort(_ManyReferencesBase):
    def test_a_failing_reference_does_not_keep_the_others_out_of_the_file(self):
        target = self._build(4)
        failing = self.sh.items.return_item('ref1')
        real_edit_item = self.sh.items.edit_item

        def edit_item(item, config, **kwargs):
            if item is failing:
                raise RuntimeError('simulated failure')
            return real_edit_item(item, config, **kwargs)

        self.sh.items.edit_item = edit_item

        _, report = self.sh.items.rename_item(target, 'renamed')

        data = self._read_file('f')
        self.assertEqual(['ref1'], [path for path, _ in report['failed_references']])
        self.assertEqual('sh.target() + 1', data['ref1']['eval'])
        for index in (0, 2, 3):
            self.assertEqual('sh.renamed() + 1', data[f'ref{index}']['eval'])

    def test_changes_made_before_an_exception_ending_the_batch_are_saved(self):
        self._build(2)
        items = self.sh.items

        with self.assertRaises(RuntimeError):
            with items._yaml_batch():
                items.edit_item(items.return_item('ref0'), {'type': 'num', 'eval': '5'})
                raise RuntimeError('batch aborted')

        self.assertEqual('5', self._read_file('f')['ref0']['eval'])


class TestNoStaleDocumentAfterTheBatch(_ManyReferencesBase):
    def test_a_file_changed_after_the_rename_is_read_afresh(self):
        target = self._build(2)
        self.sh.items.rename_item(target, 'renamed')
        path = os.path.join(self.tmpdir.name, 'f.yaml')
        with open(path) as fh:
            text = fh.read()
        with open(path, 'w') as fh:
            fh.write(text.replace('sh.renamed() + 1', 'sh.renamed() + 99'))

        config = self.sh.items.current_config_for_edit(self.sh.items.return_item('ref0'))

        self.assertEqual('sh.renamed() + 99', config['eval'])


if __name__ == '__main__':
    unittest.main()
