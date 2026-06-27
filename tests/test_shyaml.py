#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/shyaml.py

Coverage:
  - yaml_load()             — valid file, missing file, malformed YAML
  - yaml_load_fromstring()  — string input, ordered dict
  - yaml_save()             — round-trip write + reload
  - yaml_save_roundtrip()   — ruamel-based round-trip preserving comments
  - yaml_load_roundtrip()   — ruamel-based load
  - setInDict() / get_parent() / get_key()  — path helpers
  - Shyaml class            — getvalue, setvalue, getnode
"""

import os
import sys
import tempfile
import textwrap
import unittest
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import lib.shyaml as shyaml


# ===========================================================================
# yaml_load
# ===========================================================================


class TestYamlLoad(unittest.TestCase):
    def _write_tmpfile(self, content):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8')
        f.write(textwrap.dedent(content))
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    # --- happy path ---

    def test_loads_simple_dict(self):
        path = self._write_tmpfile("""
            key1: value1
            key2: 42
        """)
        result = shyaml.yaml_load(path)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['key2'], 42)

    def test_loads_nested_dict(self):
        path = self._write_tmpfile("""
            outer:
                inner: hello
                num: 7
        """)
        result = shyaml.yaml_load(path)
        self.assertEqual(result['outer']['inner'], 'hello')
        self.assertEqual(result['outer']['num'], 7)

    def test_loads_list_value(self):
        path = self._write_tmpfile("""
            items:
                - alpha
                - beta
                - gamma
        """)
        result = shyaml.yaml_load(path)
        self.assertEqual(result['items'], ['alpha', 'beta', 'gamma'])

    def test_loads_boolean_values(self):
        path = self._write_tmpfile("""
            flag_true: true
            flag_false: false
        """)
        result = shyaml.yaml_load(path)
        self.assertIs(result['flag_true'], True)
        self.assertIs(result['flag_false'], False)

    def test_loads_null_as_none(self):
        path = self._write_tmpfile("""
            empty: null
        """)
        result = shyaml.yaml_load(path)
        self.assertIsNone(result['empty'])

    def test_ordered_returns_ordered_dict(self):
        path = self._write_tmpfile("""
            z_key: last
            a_key: first
        """)
        result = shyaml.yaml_load(path, ordered=True)
        self.assertIsInstance(result, OrderedDict)

    # --- error path ---

    def test_missing_file_returns_none(self):
        result = shyaml.yaml_load('/nonexistent/path/file.yaml', ignore_notfound=True)
        self.assertIsNone(result)

    def test_missing_file_without_ignore_also_returns_none(self):
        # With ignore_notfound=False a warning is logged but None still returned
        result = shyaml.yaml_load('/nonexistent/path/file.yaml')
        self.assertIsNone(result)

    def test_malformed_yaml_returns_none(self):
        path = self._write_tmpfile("""
            key: [unclosed bracket
        """)
        result = shyaml.yaml_load(path)
        self.assertIsNone(result)


# ===========================================================================
# yaml_load_fromstring
# ===========================================================================


class TestYamlLoadFromString(unittest.TestCase):
    # yaml_load_fromstring returns a (data, errstr) tuple

    def test_simple_dict(self):
        data, err = shyaml.yaml_load_fromstring('key: value\nnum: 3\n')
        self.assertEqual(data['key'], 'value')
        self.assertEqual(data['num'], 3)
        self.assertEqual(err, '')

    def test_empty_string_returns_none_data(self):
        data, err = shyaml.yaml_load_fromstring('')
        self.assertIsNone(data)

    def test_nested_structure(self):
        yaml_str = textwrap.dedent("""
            parent:
                child: value
        """)
        data, err = shyaml.yaml_load_fromstring(yaml_str)
        self.assertEqual(data['parent']['child'], 'value')

    def test_ordered_returns_ordered_dict(self):
        data, err = shyaml.yaml_load_fromstring('z: 1\na: 2\n', ordered=True)
        self.assertIsInstance(data, OrderedDict)
        keys = list(data.keys())
        self.assertEqual(keys[0], 'z')
        self.assertEqual(keys[1], 'a')

    def test_list_at_top_level(self):
        data, err = shyaml.yaml_load_fromstring('- one\n- two\n- three\n')
        self.assertEqual(data, ['one', 'two', 'three'])

    def test_malformed_yaml_returns_none_with_error(self):
        data, err = shyaml.yaml_load_fromstring('key: [unclosed')
        self.assertIsNone(data)
        self.assertNotEqual(err, '')


# ===========================================================================
# yaml_save + round-trip
# ===========================================================================


class TestYamlSave(unittest.TestCase):
    def test_save_and_reload(self):
        f = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
        f.close()
        self.addCleanup(os.unlink, f.name)

        data = {'key1': 'value1', 'num': 42, 'nested': {'a': 1}}
        shyaml.yaml_save(f.name, data)

        reloaded = shyaml.yaml_load(f.name)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded['key1'], 'value1')
        self.assertEqual(reloaded['num'], 42)
        self.assertEqual(reloaded['nested']['a'], 1)

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'test.yaml')
            shyaml.yaml_save(path, {'x': 1})
            self.assertTrue(os.path.exists(path))


class TestYamlRoundtrip(unittest.TestCase):
    """yaml_load_roundtrip / yaml_save_roundtrip use ruamel.yaml."""

    def test_roundtrip_preserves_data(self):
        src = textwrap.dedent("""\
            # A comment
            key1: value1
            key2: 42
        """)
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8')
        f.write(src)
        f.close()
        self.addCleanup(os.unlink, f.name)

        data = shyaml.yaml_load_roundtrip(f.name)
        self.assertIsNotNone(data)
        self.assertEqual(data['key1'], 'value1')
        self.assertEqual(data['key2'], 42)

    def test_save_roundtrip_writes_file(self):
        f = tempfile.NamedTemporaryFile(suffix='.yaml', delete=False)
        f.close()
        self.addCleanup(os.unlink, f.name)

        data = shyaml.yaml_load_roundtrip(f.name) or shyaml.get_emptynode()
        data['newkey'] = 'newvalue'
        shyaml.yaml_save_roundtrip(f.name, data, create_backup=False)

        reloaded = shyaml.yaml_load(f.name)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded['newkey'], 'newvalue')


# ===========================================================================
# Path helpers: setInDict, get_parent, get_key
# ===========================================================================


class TestPathHelpers(unittest.TestCase):
    def test_set_in_dict_top_level(self):
        d = {}
        shyaml.setInDict(d, 'key', 'value')
        self.assertEqual(d['key'], 'value')

    def test_set_in_dict_nested_path(self):
        d = {'a': {'b': {}}}
        shyaml.setInDict(d, 'a.b.c', 'deep')
        self.assertEqual(d['a']['b']['c'], 'deep')

    def test_get_parent_simple(self):
        self.assertEqual(shyaml.get_parent('outer.inner'), 'outer')

    def test_get_parent_deep(self):
        self.assertEqual(shyaml.get_parent('a.b.c.d'), 'a.b.c')

    def test_get_parent_single_key(self):
        # Single key has no parent — returns empty string
        self.assertEqual(shyaml.get_parent('key'), '')

    def test_get_key_simple(self):
        self.assertEqual(shyaml.get_key('outer.inner'), 'inner')

    def test_get_key_deep(self):
        self.assertEqual(shyaml.get_key('a.b.c.d'), 'd')

    def test_get_key_single(self):
        self.assertEqual(shyaml.get_key('only'), 'only')


# ===========================================================================
# Shyaml class
# ===========================================================================


class TestYamlfileClass(unittest.TestCase):
    """Tests for the yamlfile class (path without .yaml extension expected)."""

    def _make_file(self, content):
        """Write content to a temp .yaml file; return path WITHOUT .yaml."""
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8')
        f.write(textwrap.dedent(content))
        f.close()
        self.addCleanup(os.unlink, f.name)
        # yamlfile appends YAML_FILE (.yaml) internally, so strip it
        return f.name[:-5]  # remove '.yaml'

    def test_getvalue_top_level(self):
        path = self._make_file("""
            key1: hello
            key2: 99
        """)
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getvalue('key1'), 'hello')
        self.assertEqual(yf.getvalue('key2'), 99)

    def test_getvalue_nested(self):
        path = self._make_file("""
            outer:
                inner: world
        """)
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getvalue('outer.inner'), 'world')

    def test_getvalue_missing_returns_none(self):
        path = self._make_file('key: value\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertIsNone(yf.getvalue('nonexistent'))

    def test_getnode_returns_subtree(self):
        path = self._make_file("""
            section:
                a: 1
                b: 2
        """)
        yf = shyaml.yamlfile(path)
        yf.load()
        node = yf.getnode('section')
        self.assertIsNotNone(node)

    def test_setvalue_and_reload(self):
        path = self._make_file('key: original\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setvalue('key', 'modified')
        yf.save()
        yf2 = shyaml.yamlfile(path)
        yf2.load()
        self.assertEqual(yf2.getvalue('key'), 'modified')

    def test_setvalue_none_removes_top_level_key(self):
        path = self._make_file("""
            first: 1
            second: 2
        """)
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setvalue('first', None)
        self.assertIsNone(yf.getvalue('first'))
        self.assertEqual(yf.getvalue('second'), 2)

    def test_setvalue_none_removes_top_level_key_persists_after_save(self):
        path = self._make_file('first: 1\nsecond: 2\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setvalue('first', None)
        yf.save()
        yf2 = shyaml.yamlfile(path)
        yf2.load()
        self.assertIsNone(yf2.getvalue('first'))
        self.assertEqual(yf2.getvalue('second'), 2)

    def test_setvalue_none_removes_nested_key(self):
        path = self._make_file("""
            parent:
                child: 1
                sibling: 2
        """)
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setvalue('parent.child', None)
        self.assertIsNone(yf.getvalue('parent.child'))
        self.assertEqual(yf.getvalue('parent.sibling'), 2)

    def test_setvalue_after_loading_null_root(self):
        # A file whose only top-level key was removed (setvalue(path, None)'s
        # "cleanup empty parent" branch) ends up with a literal `null` root.
        # Loading that must not leave self.data as None, or every subsequent
        # setvalue() silently no-ops (TypeError swallowed in setInDict).
        path = self._make_file('null\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setvalue('new', {'type': 'num'})
        yf.save()

        yf2 = shyaml.yamlfile(path)
        yf2.load()
        self.assertEqual(yf2.getnode('new'), {'type': 'num'})

    def test_setleafvalue_creates_branch_and_leaf(self):
        # setvalue requires the parent branch to exist; setleafvalue creates it.
        path = self._make_file('existing: yes\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        yf.setleafvalue('new.nested', 'key', 'deep_value')
        yf.save()
        yf2 = shyaml.yamlfile(path)
        yf2.load()
        self.assertEqual(yf2.getvalue('new.nested.key'), 'deep_value')

    def test_getnodetype_leaf(self):
        # yamlfile uses 'leaf' (not 'scalar') for terminal value nodes
        path = self._make_file('key: value\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getnodetype('key'), 'leaf')

    def test_getnodetype_branch(self):
        # yamlfile uses 'branch' (not 'map') for non-terminal nodes
        path = self._make_file('section:\n    child: x\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getnodetype('section'), 'branch')

    def test_getvaluetype_str(self):
        path = self._make_file('key: hello\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getvaluetype('key'), 'str')

    def test_getvaluetype_int(self):
        path = self._make_file('key: 42\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getvaluetype('key'), 'int')

    def test_getvaluetype_bool(self):
        path = self._make_file('key: true\n')
        yf = shyaml.yamlfile(path)
        yf.load()
        self.assertEqual(yf.getvaluetype('key'), 'bool')


if __name__ == '__main__':
    unittest.main()
