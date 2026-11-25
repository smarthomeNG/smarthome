#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for tools/api_snapshot.py: the public-API snapshot and its semver-level diff.

Each test builds two small source trees on disk, snapshots both and checks the
severity the diff assigns to the difference.
"""

import contextlib
import fnmatch
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = os.path.join(os.path.dirname(__file__), '..')
TOOL_PATH = os.path.join(REPO, 'tools', 'api_snapshot.py')


def load_tool():
    spec = importlib.util.spec_from_file_location('api_snapshot', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApiTreeTestCase(unittest.TestCase):
    """Builds source trees in a temp dir and diffs their API snapshots."""

    def setUp(self):
        self.tool = load_tool()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.surface = self.tool.Surface(python_globs=['lib/*.py'])
        self._trees = 0

    def tree(self, **files):
        """Write {'lib/foo.py': source} files into a fresh tree and return its root."""
        self._trees += 1
        root = Path(self._tmp.name) / f'tree{self._trees}'
        for rel, source in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(source))
        return root

    def changes(self, old_files, new_files):
        """Return {key: Level} for the diff between two file sets."""
        old = self.tool.snapshot(self.tree(**old_files), self.surface)
        new = self.tool.snapshot(self.tree(**new_files), self.surface)
        return {c.key: c.level for c in self.tool.diff(old, new)}


class TestPythonMembers(ApiTreeTestCase):
    def test_removed_public_method_is_major(self):
        old = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n    def stop(self): ...\n'}
        new = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n'}
        self.assertEqual({'member:lib/plug:Plug.stop': self.tool.Level.MAJOR}, self.changes(old, new))

    def test_added_public_method_is_minor(self):
        old = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n'}
        new = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n    def stop(self): ...\n'}
        self.assertEqual({'member:lib/plug:Plug.stop': self.tool.Level.MINOR}, self.changes(old, new))

    def method_change(self, old_sig, new_sig):
        old = {'lib/plug.py': f'class Plug:\n    def run({old_sig}): ...\n'}
        new = {'lib/plug.py': f'class Plug:\n    def run({new_sig}): ...\n'}
        return self.changes(old, new).get('member:lib/plug:Plug.run')

    def test_new_required_parameter_is_major(self):
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a', 'self, a, b'))

    def test_new_optional_parameter_is_minor(self):
        self.assertEqual(self.tool.Level.MINOR, self.method_change('self, a', 'self, a, b=None'))

    def test_renamed_or_reordered_positional_parameter_is_major(self):
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a, b', 'self, a, c'))
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a, b', 'self, b, a'))
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a, b', 'self, a'))

    def test_optional_parameter_becoming_required_is_major(self):
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a=1', 'self, a'))

    def test_required_parameter_becoming_optional_is_compatible(self):
        self.assertIsNone(self.method_change('self, a', 'self, a=1'))

    def test_keyword_only_parameters(self):
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, a', 'self, a, *, b'))
        self.assertEqual(self.tool.Level.MINOR, self.method_change('self, a', 'self, a, *, b=1'))
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, *, b=1', 'self'))
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, *, b=1', 'self, *, b'))
        self.assertEqual(self.tool.Level.MINOR, self.method_change('self, *, b=1', 'self, **kwargs'))

    def test_variadic_parameters(self):
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, *args', 'self'))
        self.assertEqual(self.tool.Level.MAJOR, self.method_change('self, **kwargs', 'self'))
        self.assertEqual(self.tool.Level.MINOR, self.method_change('self', 'self, **kwargs'))

    def test_changing_the_kind_of_callable_is_major(self):
        plain = 'class Plug:\n    def run(self): ...\n'
        prop = 'class Plug:\n    @property\n    def run(self): ...\n'
        coro = 'class Plug:\n    async def run(self): ...\n'
        key = 'member:lib/plug:Plug.run'
        self.assertEqual(self.tool.Level.MAJOR, self.changes({'lib/plug.py': plain}, {'lib/plug.py': prop})[key])
        self.assertEqual(self.tool.Level.MAJOR, self.changes({'lib/plug.py': plain}, {'lib/plug.py': coro})[key])

    def test_unchanged_signature_is_no_change(self):
        self.assertIsNone(self.method_change('self, a, b=1', 'self, a, b=2'))

    def test_constructor_and_call_signatures_are_api(self):
        old = {
            'lib/plug.py': 'class Plug:\n    def __init__(self, a): ...\n    def __call__(self, x): ...\n    def __repr__(self): ...\n'
        }
        new = {
            'lib/plug.py': 'class Plug:\n    def __init__(self, b): ...\n    def __call__(self, y): ...\n    def __repr__(self, z): ...\n'
        }
        self.assertEqual(
            {
                'member:lib/plug:Plug.__init__': self.tool.Level.MAJOR,
                'member:lib/plug:Plug.__call__': self.tool.Level.MAJOR,
            },
            self.changes(old, new),
        )

    def test_underscore_module_files_are_not_api(self):
        old = {'lib/_internal.py': 'def helper(): ...\nclass Impl:\n    def run(self): ...\n'}
        self.assertEqual({}, self.changes(old, {'lib/_internal.py': ''}))

    def test_package_init_is_api(self):
        key = 'member:lib/__init__:Plug.run'
        self.assertEqual(
            {key: self.tool.Level.MAJOR},
            self.changes({'lib/__init__.py': 'class Plug:\n    def run(self): ...\n'}, {'lib/__init__.py': ''}),
        )

    def test_underscore_names_are_not_api(self):
        old = {'lib/plug.py': 'class Plug:\n    def _helper(self): ...\nclass _Internal:\n    def run(self): ...\n'}
        new = {'lib/plug.py': 'class Plug:\n    def _other(self): ...\n'}
        self.assertEqual({}, self.changes(old, new))


class TestInternalMembers(ApiTreeTestCase):
    def test_internal_members_are_not_api(self):
        self.surface = self.tool.Surface(
            python_globs=['lib/*.py'], internal_members=['lib/plug:Plug.start', 'lib/plug:Plug.load_*']
        )
        old = {
            'lib/plug.py': 'class Plug:\n    def run(self): ...\n    def start(self): ...\n    def load_a(self): ...\n'
        }
        new = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n    def start(self, x): ...\n'}
        self.assertEqual({}, self.changes(old, new))

    def test_other_members_stay_api(self):
        self.surface = self.tool.Surface(python_globs=['lib/*.py'], internal_members=['lib/plug:Plug.start'])
        old = {'lib/plug.py': 'class Plug:\n    def run(self): ...\n    def start(self): ...\n'}
        new = {'lib/plug.py': 'class Plug:\n    def start(self): ...\n'}
        self.assertEqual({'member:lib/plug:Plug.run': self.tool.Level.MAJOR}, self.changes(old, new))

    def test_declared_internal_members_exist(self):
        """Every entry of internal_members in tools/api_surface.yaml matches a public member of the core."""
        surface = self.tool.Surface.load(Path(REPO) / 'tools' / 'api_surface.yaml')
        names = [
            key.removeprefix('member:')
            for key in self.tool.snapshot(Path(REPO), self.tool.Surface(python_globs=surface.python_globs))
            if key.startswith('member:')
        ]
        for pattern in surface.internal_members:
            with self.subTest(pattern):
                self.assertTrue(fnmatch.filter(names, pattern), f'{pattern} matches no public member')


class TestModuleLevel(ApiTreeTestCase):
    def test_public_function_signatures_are_tracked(self):
        key = 'function:lib/util:convert'
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.changes({'lib/util.py': 'def convert(a): ...\n'}, {'lib/util.py': ''})
        )
        self.assertEqual(
            {key: self.tool.Level.MAJOR},
            self.changes({'lib/util.py': 'def convert(a): ...\n'}, {'lib/util.py': 'def convert(b): ...\n'}),
        )
        self.assertEqual(
            {key: self.tool.Level.MINOR},
            self.changes({'lib/util.py': 'def convert(a): ...\n'}, {'lib/util.py': 'def convert(a, b=0): ...\n'}),
        )

    def test_constant_removal_is_major_and_value_change_needs_review(self):
        key = 'constant:lib/util:LIMIT'
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.changes({'lib/util.py': 'LIMIT = 5\n'}, {'lib/util.py': ''})
        )
        self.assertEqual(
            {key: self.tool.Level.REVIEW}, self.changes({'lib/util.py': 'LIMIT = 5\n'}, {'lib/util.py': 'LIMIT = 6\n'})
        )
        self.assertEqual({}, self.changes({'lib/util.py': 'LIMIT = 5\n'}, {'lib/util.py': 'LIMIT = 5\n'}))

    def test_dict_constant_keys(self):
        key = 'constant:lib/util:DEFAULTS'
        old = {'lib/util.py': "DEFAULTS = {'a': 1, 'b': 2}\n"}
        self.assertEqual({key: self.tool.Level.MAJOR}, self.changes(old, {'lib/util.py': "DEFAULTS = {'a': 1}\n"}))
        self.assertEqual(
            {key: self.tool.Level.MINOR}, self.changes(old, {'lib/util.py': "DEFAULTS = {'a': 1, 'b': 2, 'c': 3}\n"})
        )
        self.assertEqual(
            {key: self.tool.Level.REVIEW}, self.changes(old, {'lib/util.py': "DEFAULTS = {'a': 1, 'b': 3}\n"})
        )

    def test_list_constant_growth_is_minor_and_shrink_major(self):
        key = 'constant:lib/util:TYPES'
        old = {'lib/util.py': "TYPES = ['num', 'str']\n"}
        self.assertEqual(
            {key: self.tool.Level.MINOR}, self.changes(old, {'lib/util.py': "TYPES = ['num', 'str', 'bool']\n"})
        )
        self.assertEqual({key: self.tool.Level.MAJOR}, self.changes(old, {'lib/util.py': "TYPES = ['num']\n"}))
        self.assertEqual({}, self.changes(old, {'lib/util.py': "TYPES = ['str', 'num']\n"}))

    def test_only_upper_case_module_variables_are_constants(self):
        old = {'lib/util.py': 'logger = object()\nLIMIT = 1\n'}
        self.assertEqual({}, self.changes(old, {'lib/util.py': 'LIMIT = 1\n'}))

    def test_tuple_constant_behaves_like_a_list(self):
        key = 'constant:lib/util:KEYS'
        old = {'lib/util.py': "KEYS = ('a', 'b')\n"}
        self.assertEqual({}, self.changes(old, {'lib/util.py': "KEYS = ('b', 'a')\n"}))
        self.assertEqual({key: self.tool.Level.MAJOR}, self.changes(old, {'lib/util.py': "KEYS = ('a',)\n"}))

    def test_snapshot_is_json_serializable(self):
        snap = self.tool.snapshot(
            self.tree(**{'lib/util.py': "KEYS = ('a', {'b'})\nclass C:\n    def f(self, a): ...\n"}), self.surface
        )
        json.dumps(snap)

    def test_same_class_name_in_two_modules_keeps_both(self):
        old = {'lib/a.py': 'class Item:\n    def run(self): ...\n', 'lib/b.py': 'class Item:\n    def go(self): ...\n'}
        new = {'lib/a.py': 'class Item: ...\n', 'lib/b.py': 'class Item: ...\n'}
        self.assertEqual(
            {'member:lib/a:Item.run': self.tool.Level.MAJOR, 'member:lib/b:Item.go': self.tool.Level.MAJOR},
            self.changes(old, new),
        )


class TestConfigParameters(ApiTreeTestCase):
    """Parameters declared in module.yaml are the keys users write into etc/module.yaml."""

    def setUp(self):
        super().setUp()
        self.surface = self.tool.Surface(parameter_globs=['modules/*/module.yaml'])

    def param_changes(self, old_params, new_params):
        def doc(params):
            body = ''.join(
                f'    {name}:\n' + ''.join(f'        {k}: {v}\n' for k, v in attrs.items())
                for name, attrs in params.items()
            )
            return {'modules/http/module.yaml': f'parameters:\n{body}'}

        return self.changes(doc(old_params), doc(new_params))

    def test_removed_parameter_is_major(self):
        key = 'parameter:http:port'
        self.assertEqual({key: self.tool.Level.MAJOR}, self.param_changes({'port': {'type': 'int'}}, {}))

    def test_added_parameter_is_minor_unless_mandatory(self):
        self.assertEqual(
            {'parameter:http:port': self.tool.Level.MINOR},
            self.param_changes({}, {'port': {'type': 'int', 'default': 80}}),
        )
        self.assertEqual(
            {'parameter:http:port': self.tool.Level.MINOR}, self.param_changes({}, {'port': {'type': 'int'}})
        )
        self.assertEqual(
            {'parameter:http:port': self.tool.Level.MAJOR},
            self.param_changes({}, {'port': {'type': 'int', 'mandatory': 'true'}}),
        )

    def test_type_change_and_becoming_mandatory_are_major(self):
        key = 'parameter:http:port'
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.param_changes({'port': {'type': 'int'}}, {'port': {'type': 'str'}})
        )
        self.assertEqual(
            {key: self.tool.Level.MAJOR},
            self.param_changes({'port': {'type': 'int'}}, {'port': {'type': 'int', 'mandatory': 'true'}}),
        )

    def test_narrowing_and_widening_the_valid_range(self):
        key = 'parameter:http:port'
        base = {'type': 'int', 'valid_min': 0, 'valid_max': 100}
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.param_changes({'port': base}, {'port': base | {'valid_min': 1}})
        )
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.param_changes({'port': base}, {'port': base | {'valid_max': 99}})
        )
        self.assertEqual(
            {key: self.tool.Level.MINOR}, self.param_changes({'port': base}, {'port': base | {'valid_max': 200}})
        )

    def test_valid_list_changes(self):
        key = 'parameter:http:mode'
        old = {'mode': {'type': 'str', 'valid_list': "['a', 'b']"}}
        self.assertEqual(
            {key: self.tool.Level.MAJOR}, self.param_changes(old, {'mode': {'type': 'str', 'valid_list': "['a']"}})
        )
        self.assertEqual(
            {key: self.tool.Level.MINOR},
            self.param_changes(old, {'mode': {'type': 'str', 'valid_list': "['a', 'b', 'c']"}}),
        )

    def test_changed_default_needs_review(self):
        self.assertEqual(
            {'parameter:http:port': self.tool.Level.REVIEW},
            self.param_changes({'port': {'type': 'int', 'default': 80}}, {'port': {'type': 'int', 'default': 8080}}),
        )


class TestItemAttributes(ApiTreeTestCase):
    """Item attributes declared in an items.yaml catalog are the attributes users put on items."""

    def setUp(self):
        super().setUp()
        self.surface = self.tool.Surface(item_attribute_globs=['modules/*/items.yaml'])

    def attr_changes(self, old_yaml, new_yaml):
        old = {'modules/core/items.yaml': 'item_attributes:\n' + textwrap.indent(textwrap.dedent(old_yaml), '    ')}
        new = {'modules/core/items.yaml': 'item_attributes:\n' + textwrap.indent(textwrap.dedent(new_yaml), '    ')}
        return self.changes(old, new)

    def test_removed_added_and_retyped_attribute(self):
        L = self.tool.Level
        cycle_str = 'cycle:\n    type: str\n'
        self.assertEqual({'item_attribute:core:cycle': L.MAJOR}, self.attr_changes(cycle_str, ''))
        self.assertEqual(
            {'item_attribute:core:log': L.MINOR}, self.attr_changes(cycle_str, cycle_str + 'log:\n    type: str\n')
        )
        self.assertEqual(
            {'item_attribute:core:cycle': L.MAJOR}, self.attr_changes(cycle_str, 'cycle:\n    type: bool\n')
        )

    def test_valid_list_narrowing_and_widening(self):
        L = self.tool.Level
        old = 'type:\n    type: str\n    valid_list: [num, str]\n'
        self.assertEqual(
            {'item_attribute:core:type': L.MAJOR},
            self.attr_changes(old, 'type:\n    type: str\n    valid_list: [num]\n'),
        )
        self.assertEqual(
            {'item_attribute:core:type': L.MINOR},
            self.attr_changes(old, 'type:\n    type: str\n    valid_list: [num, str, bool]\n'),
        )


class TestPluginMetadata(ApiTreeTestCase):
    """plugin.yaml declares the config parameters, item attributes, functions and requirements of a plugin."""

    def setUp(self):
        super().setUp()
        self.surface = self.tool.Surface(plugin_metadata_globs=['plugins/*/plugin.yaml'])

    def plugin_changes(self, old, new):
        return self.changes(
            {'plugins/foo/plugin.yaml': textwrap.dedent(old)}, {'plugins/foo/plugin.yaml': textwrap.dedent(new)}
        )

    def test_parameters_logic_parameters_and_item_attributes(self):
        L = self.tool.Level
        old = 'parameters:\n    host: {type: str}\nlogic_parameters:\n    x: {type: str}\nitem_attributes:\n    foo_id: {type: str}\n'
        self.assertEqual(
            {'parameter:foo:host': L.MAJOR, 'logic_parameter:foo:x': L.MAJOR, 'item_attribute:foo:foo_id': L.MAJOR},
            self.plugin_changes(old, 'plugin: {}\n'),
        )
        with_y = old.replace('    x: {type: str}\n', '    x: {type: str}\n    y: {type: str}\n')
        self.assertEqual({'logic_parameter:foo:y': L.MINOR}, self.plugin_changes(old, with_y))

    def test_sections_set_to_none_are_empty(self):
        old = 'parameters: NONE\nplugin_functions: NONE\nitem_structs: NONE\nlogic_parameters: NONE\nitem_attributes: NONE\n'
        self.assertEqual({}, self.plugin_changes(old, old))

    def test_plugin_functions_follow_call_compatibility(self):
        L = self.tool.Level
        old = 'plugin_functions:\n    send:\n        type: str\n        parameters:\n            adr: {type: num}\n'
        key = 'plugin_function:foo:send'
        self.assertEqual({key: L.MAJOR}, self.plugin_changes(old, 'plugin: {}\n'))
        self.assertEqual({key: L.MAJOR}, self.plugin_changes(old, old.replace('type: str', 'type: bool')))
        self.assertEqual({key: L.MAJOR}, self.plugin_changes(old, old + '            val: {type: num}\n'))
        self.assertEqual({key: L.MINOR}, self.plugin_changes(old, old + '            val: {type: num, default: 0}\n'))
        self.assertEqual({key: L.MAJOR}, self.plugin_changes(old, old.replace('adr', 'address')))

    def test_item_structs_are_tracked_by_name(self):
        L = self.tool.Level
        old = 'item_structs:\n    one: {type: bool}\n'
        self.assertEqual({'item_struct:foo:one': L.MAJOR}, self.plugin_changes(old, 'plugin: {}\n'))
        self.assertEqual({'item_struct:foo:two': L.MINOR}, self.plugin_changes(old, old + '    two: {type: bool}\n'))

    def test_raising_a_requirement(self):
        L = self.tool.Level

        def requirement(**fields):
            return 'plugin:\n' + ''.join(f"    {k}: '{v}'\n" for k, v in fields.items())

        self.assertEqual(
            {'requirement:foo:sh_minversion': L.MAJOR},
            self.plugin_changes(requirement(sh_minversion='1.8'), requirement(sh_minversion='1.9.5')),
        )
        self.assertEqual(
            {'requirement:foo:py_minversion': L.MINOR},
            self.plugin_changes(requirement(py_minversion='3.10'), requirement(py_minversion='3.11')),
        )
        self.assertEqual(
            {'requirement:foo:sdp_minversion': L.MAJOR},
            self.plugin_changes(requirement(sdp_minversion='1.0.0'), requirement(sdp_minversion='2.0.0')),
        )
        self.assertEqual(
            {'requirement:foo:sh_minversion': L.MAJOR},
            self.plugin_changes('plugin: {}\n', requirement(sh_minversion='1.8')),
        )

    def test_relaxing_or_keeping_a_requirement_is_no_change(self):
        def requirement(**fields):
            return 'plugin:\n' + ''.join(f"    {k}: '{v}'\n" for k, v in fields.items())

        self.assertEqual({}, self.plugin_changes(requirement(sh_minversion='1.9'), requirement(sh_minversion='1.8')))
        self.assertEqual({}, self.plugin_changes(requirement(sh_minversion='1.9'), 'plugin: {}\n'))
        self.assertEqual(
            {}, self.plugin_changes(requirement(sh_minversion='1.12.2.2'), requirement(sh_minversion='1.12.2.2'))
        )

    def test_lowering_a_maximum_version_is_a_restriction(self):
        L = self.tool.Level

        def requirement(**fields):
            return 'plugin:\n' + ''.join(f"    {k}: '{v}'\n" for k, v in fields.items())

        self.assertEqual(
            {'requirement:foo:sh_maxversion': L.MAJOR},
            self.plugin_changes(requirement(sh_maxversion='1.9'), requirement(sh_maxversion='1.8')),
        )
        self.assertEqual(
            {'requirement:foo:sh_maxversion': L.MAJOR},
            self.plugin_changes('plugin: {}\n', requirement(sh_maxversion='1.8')),
        )
        self.assertEqual(
            {'requirement:foo:py_maxversion': L.MINOR},
            self.plugin_changes('plugin: {}\n', requirement(py_maxversion='3.12')),
        )
        self.assertEqual({}, self.plugin_changes(requirement(sh_maxversion='1.8'), requirement(sh_maxversion='1.9')))


class TestCommandLineAndProtocol(ApiTreeTestCase):
    def test_removed_cli_flag_is_major_and_added_flag_minor(self):
        self.surface = self.tool.Surface(cli_file='bin/app.py')
        old = {
            'bin/app.py': "p.add_argument('-q', '--quiet', action='store_true')\np.add_argument('-f', '--foreground')\n"
        }
        new = {'bin/app.py': "p.add_argument('-f', '--foreground')\np.add_argument('--debug')\n"}
        self.assertEqual(
            {
                'cli:-q': self.tool.Level.MAJOR,
                'cli:--quiet': self.tool.Level.MAJOR,
                'cli:--debug': self.tool.Level.MINOR,
            },
            self.changes(old, new),
        )

    def test_websocket_commands_in_and_out(self):
        self.surface = self.tool.Surface(websocket_file='modules/ws/visu.py')
        old = {
            'modules/ws/visu.py': "if command == 'item':\n    reply = {'cmd': 'item'}\nelif command == 'monitor':\n    pass\n"
        }
        new = {'modules/ws/visu.py': "if command == 'item':\n    reply = {'cmd': 'item'}\n"}
        self.assertEqual({'websocket-in:monitor': self.tool.Level.MAJOR}, self.changes(old, new))


class TestInheritance(ApiTreeTestCase):
    """A class exposes the public members it inherits from classes inside the surface."""

    BASE = 'class Base:\n    def stop(self): ...\n'

    def test_method_moving_to_a_base_class_is_no_change(self):
        old = {'lib/plug.py': self.BASE + 'class Plug(Base):\n    def run(self): ...\n    def stop(self): ...\n'}
        new = {'lib/plug.py': self.BASE + 'class Plug(Base):\n    def run(self): ...\n'}
        self.assertEqual({}, self.changes(old, new))

    def test_inherited_member_disappearing_with_its_base_is_major(self):
        old = {'lib/plug.py': self.BASE + 'class Plug(Base):\n    def run(self): ...\n'}
        new = {'lib/plug.py': 'class Base: ...\nclass Plug(Base):\n    def run(self): ...\n'}
        self.assertEqual(self.tool.Level.MAJOR, self.changes(old, new)['member:lib/plug:Plug.stop'])

    def test_base_in_another_module_is_resolved_by_name(self):
        old = {'lib/base.py': self.BASE, 'lib/plug.py': 'class Plug(Base):\n    def run(self): ...\n'}
        new = {'lib/base.py': 'class Base: ...\n', 'lib/plug.py': 'class Plug(Base):\n    def run(self): ...\n'}
        self.assertEqual(self.tool.Level.MAJOR, self.changes(old, new)['member:lib/plug:Plug.stop'])


class TestSurfaceFile(ApiTreeTestCase):
    def test_surface_is_loaded_from_yaml(self):
        path = self.tree(
            **{
                'surface.yaml': """
            python_globs: ['lib/*.py']
            parameter_globs: ['modules/*/module.yaml']
            item_attribute_globs: ['modules/core/items.yaml']
            cli_file: bin/app.py
            websocket_file: modules/ws/visu.py
            """
            }
        )
        surface = self.tool.Surface.load(path / 'surface.yaml')
        self.assertEqual(
            self.tool.Surface(
                python_globs=['lib/*.py'],
                parameter_globs=['modules/*/module.yaml'],
                item_attribute_globs=['modules/core/items.yaml'],
                cli_file='bin/app.py',
                websocket_file='modules/ws/visu.py',
            ),
            surface,
        )

    def test_unknown_surface_key_is_rejected(self):
        path = self.tree(**{'surface.yaml': 'python_glob: [x]\n'})
        with self.assertRaises(ValueError):
            self.tool.Surface.load(path / 'surface.yaml')


class TestGitRefs(ApiTreeTestCase):
    def git(self, repo, *args):
        identity = ['-c', 'user.name=t', '-c', 'user.email=t@example.org', '-c', 'commit.gpgsign=false']
        subprocess.run(['git', '-C', str(repo), *identity, *args], check=True, capture_output=True)

    def test_snapshot_of_a_git_ref_ignores_the_working_tree(self):
        repo = self.tree(**{'lib/plug.py': 'class Plug:\n    def run(self): ...\n', 'README': 'x\n'})
        self.git(repo, 'init', '-q')
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-q', '-m', 'one')
        self.git(repo, 'tag', 'v1')
        (repo / 'lib/plug.py').write_text('class Plug:\n    def run(self): ...\n    def stop(self): ...\n')
        self.git(repo, 'commit', '-q', '-am', 'two')
        (repo / 'lib/plug.py').write_text('class Plug: ...\n')  # uncommitted
        old = self.tool.snapshot_ref(repo, 'v1', self.surface)
        new = self.tool.snapshot_ref(repo, 'HEAD', self.surface)
        self.assertEqual(
            {'member:lib/plug:Plug.stop': self.tool.Level.MINOR}, {c.key: c.level for c in self.tool.diff(old, new)}
        )

    def test_surface_dir_missing_at_the_ref_gives_an_empty_snapshot(self):
        repo = self.tree(**{'README': 'x\n'})
        self.git(repo, 'init', '-q')
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-q', '-m', 'one')
        self.assertEqual({}, self.tool.snapshot_ref(repo, 'HEAD', self.surface))


class TestReport(ApiTreeTestCase):
    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.tool.main(list(argv))
        return code, out.getvalue()

    def two_trees(self, old_source, new_source):
        surface = self.tree(**{'surface.yaml': "python_globs: ['lib/*.py']\n"}) / 'surface.yaml'
        old = self.tree(**{'lib/plug.py': old_source})
        new = self.tree(**{'lib/plug.py': new_source})
        return surface, old, new

    def test_required_bump_is_the_most_severe_change(self):
        C, L = self.tool.Change, self.tool.Level
        self.assertEqual('patch', self.tool.required_bump([]))
        self.assertEqual('minor', self.tool.required_bump([C(L.MINOR, 'k', 'added')]))
        self.assertEqual('review', self.tool.required_bump([C(L.MINOR, 'k', 'added'), C(L.REVIEW, 'k2', 'x')]))
        self.assertEqual('major', self.tool.required_bump([C(L.REVIEW, 'k2', 'x'), C(L.MAJOR, 'k', 'removed')]))

    def test_text_report_lists_changes_and_the_required_bump(self):
        surface, old, new = self.two_trees('class Plug:\n    def run(self): ...\n', 'class Plug: ...\n')
        code, out = self.run_main('diff', str(old), str(new), '--surface', str(surface))
        self.assertEqual(0, code)
        self.assertIn('MAJOR', out)
        self.assertIn('member:lib/plug:Plug.run', out)
        self.assertIn('required bump: major', out)

    def test_fail_on_sets_the_exit_code(self):
        surface, old, new = self.two_trees('class Plug:\n    def run(self): ...\n', 'class Plug: ...\n')
        args = ('diff', str(old), str(new), '--surface', str(surface))
        self.assertEqual(1, self.run_main(*args, '--fail-on', 'major')[0])
        surface, old, new = self.two_trees('class Plug: ...\n', 'class Plug:\n    def run(self): ...\n')
        self.assertEqual(
            0, self.run_main('diff', str(old), str(new), '--surface', str(surface), '--fail-on', 'major')[0]
        )

    def test_markdown_report_groups_by_severity(self):
        surface, old, new = self.two_trees(
            'LIMIT = 1\nclass Plug:\n    def run(self): ...\n', 'LIMIT = 2\nclass Plug:\n    def stop(self): ...\n'
        )
        _, out = self.run_main('diff', str(old), str(new), '--surface', str(surface), '--format', 'markdown')
        self.assertLess(out.index('Breaking'), out.index('Needs review'))
        self.assertLess(out.index('Needs review'), out.index('Additions'))
        self.assertIn('`member:lib/plug:Plug.run`', out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
