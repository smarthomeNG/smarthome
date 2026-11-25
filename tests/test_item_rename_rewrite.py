#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for the pure text-rewrite helpers rename_item() uses to repoint
other items' eval/on_change/on_update/trigger/hysteresis_input text at a
renamed item's new path. See ~/.claude/handoff/shng-rename-item-design.md
for the settled algorithm — boundary-aware prefix replace, no live-tree
resolution needed at rewrite time (unlike find_references()'s detection).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.item.items import Items


class TestRewriteShPathReference(unittest.TestCase):
    def test_rewrites_bare_sh_reference(self):
        result = Items._rewrite_sh_path_reference('sh.old.path()', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.new.path()')

    def test_rewrites_property_accessor_suffix(self):
        result = Items._rewrite_sh_path_reference('sh.old.path.last_change', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.new.path.last_change')

    def test_rewrites_real_child_item_suffix(self):
        result = Items._rewrite_sh_path_reference('sh.old.path.subitem()', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.new.path.subitem()')

    def test_rewrites_plugin_method_suffix(self):
        result = Items._rewrite_sh_path_reference("sh.old.path.db('avg', '1d')", 'old.path', 'new.path')

        self.assertEqual(result, "sh.new.path.db('avg', '1d')")

    def test_does_not_touch_unrelated_longer_identifier(self):
        result = Items._rewrite_sh_path_reference('sh.old.pathitemized()', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.old.pathitemized()')

    def test_does_not_touch_unrelated_reference(self):
        result = Items._rewrite_sh_path_reference('sh.other.path()', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.other.path()')

    def test_rewrites_inside_a_larger_expression(self):
        result = Items._rewrite_sh_path_reference('sh.old.path() * 9 / 5 + 32', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.new.path() * 9 / 5 + 32')

    def test_rewrites_multiple_occurrences(self):
        result = Items._rewrite_sh_path_reference('sh.old.path() + sh.old.path.last_change', 'old.path', 'new.path')

        self.assertEqual(result, 'sh.new.path() + sh.new.path.last_change')


class TestRewriteBarePathReference(unittest.TestCase):
    def test_rewrites_exact_match(self):
        result = Items._rewrite_bare_path_reference('old.path', 'old.path', 'new.path')

        self.assertEqual(result, 'new.path')

    def test_rewrites_descendant_reference(self):
        result = Items._rewrite_bare_path_reference('old.path.subitem', 'old.path', 'new.path')

        self.assertEqual(result, 'new.path.subitem')

    def test_does_not_touch_unrelated_longer_identifier(self):
        result = Items._rewrite_bare_path_reference('old.pathitemized', 'old.path', 'new.path')

        self.assertEqual(result, 'old.pathitemized')

    def test_does_not_touch_unrelated_path(self):
        result = Items._rewrite_bare_path_reference('other.path', 'old.path', 'new.path')

        self.assertEqual(result, 'other.path')
