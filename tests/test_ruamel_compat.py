#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for tools/ruamel_compat: a run over the built-in corpus with the installed ruamel.yaml, and the comparison."""

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

TOOL_PATH = os.path.join(os.path.dirname(__file__), '..', 'tools', 'ruamel_compat', 'ruamel_compat.py')


def load_tool():
    spec = importlib.util.spec_from_file_location('ruamel_compat', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load_tool()


class TestRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.result = tool.command_run([], Path(cls._tmp.name) / 'result.json')

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_every_corpus_file_runs_through_both_pipelines(self):
        corpus = sorted(p.name for p in tool.BUILTIN_CORPUS.glob('*.yaml'))
        labels = sorted(label.split('/', 1)[1] for label in self.result['files'])

        self.assertEqual(corpus, labels)
        for entry in self.result['files'].values():
            self.assertEqual({'shng', 'plain'}, set(entry))

    def test_broken_files_are_errors_in_both_pipelines(self):
        for label, entry in self.result['files'].items():
            if label.startswith('corpus/err_'):
                with self.subTest(label):
                    self.assertFalse(entry['plain']['safe']['ok'])
                    self.assertTrue(any('error' in message for message in entry['shng']['log']))

    def test_duplicate_keys_are_logged_by_shng(self):
        log = self.result['files']['corpus/dup_keys.yaml']['shng']['log']

        self.assertTrue(any('duplicate key "a"' in message for message in log))

    def test_tokens_are_recorded(self):
        for pipeline in ('shng', 'plain'):
            self.assertEqual(set(tool.TOKENS), set(self.result['tokens'][pipeline]))
        self.assertEqual("'yes'", self.result['tokens']['shng']['yes']['read'])

    def test_comparing_a_run_with_itself_shows_no_difference(self):
        report = '\n'.join(tool.command_compare(self.result, self.result))

        self.assertNotIn('UNUSABLE', report)
        self.assertNotRegex(report, r' [1-9]\d* files differ')


class TestFirstDifference(unittest.TestCase):
    def test_path_into_canon_data(self):
        old = tool.canon({'a': {'b': [1, 2]}})
        new = tool.canon({'a': {'b': [1, 3]}})

        self.assertEqual(('/a/b[1]', ['int', 2], ['int', 3]), tool.first_difference(old, new))

    def test_line_of_a_text(self):
        self.assertEqual((' line 2', 'b', 'c'), tool.first_difference('a\nb', 'a\nc'))

    def test_missing_key(self):
        where, old, new = tool.first_difference(tool.canon({'a': 1}), tool.canon({}))

        self.assertEqual('/a', where)
        self.assertEqual('<missing>', new)


if __name__ == '__main__':
    unittest.main()
