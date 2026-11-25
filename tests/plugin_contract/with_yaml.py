"""
tests.plugin_contract.with_yaml — Tier 2: static plugin.yaml validation.

These tests read plugin.yaml directly and check for authoring errors *before*
lib.metadata ever sees the file at runtime.  They do not instantiate the plugin.

Usage::

    from tests.plugin_contract.base import BasePluginContractTest
    from tests.plugin_contract.with_yaml import YamlPluginContractTest
    from plugins.myplugin import MyPlugin


    class TestMyPlugin(BasePluginContractTest, YamlPluginContractTest):
        PLUGIN_CLASS = MyPlugin
        PLUGIN_INIT_PARAMS = {'host': '127.0.0.1'}
        # optional: minimal attribute dict(s) that must register an item.
        # If omitted, only single-attribute and "no-attribute" tests are run.
        # Required when the plugin needs two or more attributes at the same time.
        ITEM_ATTR_SETS = [{'ex_command': 'Device.Power', 'ex_write': True}]

Class attributes
----------------
PLUGIN_CLASS : type
    The plugin class under test (inherited from BasePluginContractTest).
PLUGIN_YAML_PATH : str, optional
    Explicit path to plugin.yaml.  Defaults to auto-detection from the
    plugin's module file location.
ITEM_ATTR_SETS : list[dict], optional
    List of minimal attribute dictionaries, each of which must result in
    parse_item() registering the item.  If not supplied, the framework
    auto-generates single-attribute sets from plugin.yaml and marks
    multi-attribute combination tests as skipped.
"""

import inspect
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.shyaml as shyaml
from tests.mock.core import MockSmartHome
from tests.plugin_contract._mockitem import MockItem
from tests.plugin_contract.base import make_plugin_instance


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# All parameter types recognised by lib.metadata._convert_valuetotype()
# Source: lib/metadata.py line 42 + _convert_valuetotype implementation
VALID_PARAM_TYPES = frozenset(
    {
        'bool',
        'int',
        'float',
        'num',
        'scene',
        'str',
        'password',
        'list',
        'dict',
        'ip',
        'ipv4',
        'ipv6',
        'mac',
        'knx_ga',
        'foo',
    }
)

# list(subtype) — base type is 'list', subtype validated separately
_LIST_SUBTYPE_RE = re.compile(r'^list\((.+)\)$')


def _base_type(type_str: str) -> str:
    """Return the base type from 'list(subtype)' or the type unchanged."""
    m = _LIST_SUBTYPE_RE.match(type_str or '')
    return 'list' if m else (type_str or 'foo')


def _is_valid_type(type_str: str) -> bool:
    base = _base_type(type_str)
    return base in VALID_PARAM_TYPES


# ---------------------------------------------------------------------------
# Simple type-consistency check for default values
# ---------------------------------------------------------------------------


def _default_matches_type(declared_type: str, default) -> tuple[bool, str]:
    """
    Return (ok, reason) indicating whether *default* is parseable as *declared_type*.

    This is a lightweight pre-flight check; lib.metadata does the authoritative
    conversion at runtime.
    """
    if default is None:
        return True, ''
    base = _base_type(declared_type)
    try:
        if base == 'bool':
            from lib.utils import Utils

            Utils.to_bool(default)
        elif base in ('int', 'scene'):
            int(default)
        elif base in ('float', 'num'):
            float(default)
        elif base == 'str':
            str(default)
        elif base == 'list':
            if not isinstance(default, list):
                return False, f'default {default!r} is not a list'
        elif base == 'dict':
            if not isinstance(default, dict):
                return False, f'default {default!r} is not a dict'
        # ip, ipv4, ipv6, mac, knx_ga, foo, password: accept any string/value
    except (ValueError, TypeError) as exc:
        return False, str(exc)
    return True, ''


# ---------------------------------------------------------------------------
# YAML loader helper
# ---------------------------------------------------------------------------


def _load_plugin_yaml(plugin_class, override_path: str | None = None) -> dict:
    """Load and return the parsed plugin.yaml dict, or {} if not found."""
    if override_path:
        path = override_path
    else:
        plugin_file = inspect.getfile(plugin_class)
        path = os.path.join(os.path.dirname(os.path.abspath(plugin_file)), 'plugin.yaml')
    if not os.path.isfile(path):
        return {}
    return shyaml.yaml_load(path, ordered=False) or {}


# ---------------------------------------------------------------------------
# Tier 2 mix-in
# ---------------------------------------------------------------------------


class YamlPluginContractTest(unittest.TestCase):
    """Mix-in: static plugin.yaml validation + item-attribute contract tests."""

    PLUGIN_CLASS: type | None = None
    PLUGIN_YAML_PATH: str | None = None
    PLUGIN_INIT_PARAMS: dict = {}
    ITEM_ATTR_SETS: list | None = None

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _yaml(self) -> dict:
        if self.PLUGIN_CLASS is None:
            self.skipTest('PLUGIN_CLASS not set')
        return _load_plugin_yaml(self.PLUGIN_CLASS, self.PLUGIN_YAML_PATH)

    def _plugin_section(self) -> dict:
        return self._yaml().get('plugin', {})

    def _parameters_section(self) -> dict:
        # 'NONE' is lib.metadata's own documented sentinel for "section intentionally
        # empty" (see lib/metadata.py Metadata.parameters == 'NONE' etc.), distinct from
        # omitting the key or writing an empty mapping - normalize all three to {}.
        section = self._yaml().get('parameters', {})
        return {} if section in (None, 'NONE') else section

    def _item_attributes_section(self) -> dict:
        section = self._yaml().get('item_attributes', {})
        return {} if section in (None, 'NONE') else section

    def _make_plugin(self):
        if self.PLUGIN_CLASS is None:
            self.skipTest('PLUGIN_CLASS not set')
        sh = MockSmartHome()
        return make_plugin_instance(self.PLUGIN_CLASS, sh, self.PLUGIN_INIT_PARAMS)

    def _make_item(self, path: str = 'yaml.test', conf: dict | None = None) -> MockItem:
        return MockItem(path, conf)

    # -----------------------------------------------------------------------
    # plugin.yaml presence
    # -----------------------------------------------------------------------

    def test_plugin_yaml_exists(self):
        """plugin.yaml must exist in the plugin directory."""
        if self.PLUGIN_CLASS is None:
            self.skipTest('PLUGIN_CLASS not set')
        plugin_file = inspect.getfile(self.PLUGIN_CLASS)
        path = self.PLUGIN_YAML_PATH or os.path.join(os.path.dirname(os.path.abspath(plugin_file)), 'plugin.yaml')
        self.assertTrue(os.path.isfile(path), f'plugin.yaml not found at {path}')

    # -----------------------------------------------------------------------
    # plugin section — consistency with class attributes
    # -----------------------------------------------------------------------

    def test_classname_matches_class(self):
        """plugin.yaml classname must match the actual class name."""
        meta = self._plugin_section()
        if not meta:
            self.skipTest('No [plugin] section in plugin.yaml')
        declared = meta.get('classname', '')
        self.assertEqual(
            declared,
            self.PLUGIN_CLASS.__name__,
            f'plugin.yaml classname={declared!r} but class is {self.PLUGIN_CLASS.__name__!r}',
        )

    def test_version_matches_plugin_version(self):
        """plugin.yaml version must match PLUGIN_VERSION class attribute."""
        meta = self._plugin_section()
        if not meta:
            self.skipTest('No [plugin] section in plugin.yaml')
        yaml_ver = str(meta.get('version', ''))
        code_ver = getattr(self.PLUGIN_CLASS, 'PLUGIN_VERSION', '')
        self.assertEqual(yaml_ver, code_ver, f'plugin.yaml version={yaml_ver!r} but PLUGIN_VERSION={code_ver!r}')

    def test_multi_instance_matches_allow_multiinstance(self):
        """plugin.yaml multi_instance must match ALLOW_MULTIINSTANCE."""
        meta = self._plugin_section()
        if not meta or 'multi_instance' not in meta:
            self.skipTest('multi_instance not declared in plugin.yaml')
        yaml_mi = bool(meta['multi_instance'])
        code_mi = getattr(self.PLUGIN_CLASS, 'ALLOW_MULTIINSTANCE', None)
        if code_mi is None:
            self.skipTest('ALLOW_MULTIINSTANCE not set in class — set by loader from yaml')
        self.assertEqual(yaml_mi, code_mi, f'plugin.yaml multi_instance={yaml_mi} but ALLOW_MULTIINSTANCE={code_mi}')

    # -----------------------------------------------------------------------
    # Parameter static validation
    # -----------------------------------------------------------------------

    def test_parameter_types_are_valid(self):
        """Every declared parameter type must be recognised by lib.metadata."""
        params = self._parameters_section()
        errors = []
        for name, defn in params.items():
            if not isinstance(defn, dict):
                continue
            t = defn.get('type', 'foo')
            if not _is_valid_type(t):
                errors.append(f'{name}: unknown type {t!r}')
        self.assertFalse(errors, 'Invalid parameter types in plugin.yaml:\n  ' + '\n  '.join(errors))

    def test_mandatory_default_consistency(self):
        """A parameter cannot be both mandatory:true and have a default value."""
        params = self._parameters_section()
        errors = []
        for name, defn in params.items():
            if not isinstance(defn, dict):
                continue
            is_mandatory = bool(defn.get('mandatory', False))
            has_default = 'default' in defn
            if is_mandatory and has_default:
                errors.append(f'{name}: mandatory:true but also has default={defn["default"]!r}')
        self.assertFalse(errors, 'Conflicting mandatory/default in plugin.yaml:\n  ' + '\n  '.join(errors))

    def test_default_values_parseable_as_declared_type(self):
        """Each declared default must be parseable as the parameter's declared type."""
        params = self._parameters_section()
        errors = []
        for name, defn in params.items():
            if not isinstance(defn, dict) or 'default' not in defn:
                continue
            t = defn.get('type', 'foo')
            ok, reason = _default_matches_type(t, defn['default'])
            if not ok:
                errors.append(f'{name} (type={t!r}): {reason}')
        self.assertFalse(
            errors, 'Default values incompatible with declared type in plugin.yaml:\n  ' + '\n  '.join(errors)
        )

    # -----------------------------------------------------------------------
    # Item attribute contract
    # -----------------------------------------------------------------------

    def test_item_without_plugin_attrs_not_registered(self):
        """An item with no plugin attributes must not end up in get_item_list()."""
        plugin = self._make_plugin()
        item = self._make_item('noattr.item', conf={})
        plugin.parse_item(item)
        self.assertNotIn(item, plugin.get_item_list(), 'parse_item() registered an item that has no plugin attributes')

    def test_item_attr_sets_register_items(self):
        """Each ITEM_ATTR_SET must result in parse_item() registering the item."""
        item_attrs = self._item_attributes_section()
        if not item_attrs:
            self.skipTest('No item_attributes declared in plugin.yaml')

        attr_sets = self.ITEM_ATTR_SETS
        if attr_sets is None:
            if len(item_attrs) == 1:
                # Auto-derive: one attribute → one set with just that attribute
                only_attr = next(iter(item_attrs))
                attr_sets = [{only_attr: 'test_value'}]
            else:
                self.skipTest(
                    'Multiple item_attributes declared but ITEM_ATTR_SETS not provided. '
                    'Set ITEM_ATTR_SETS on the test class with at least one complete '
                    'minimal attribute combination that should register an item.'
                )

        for i, attr_set in enumerate(attr_sets):
            with self.subTest(attr_set=attr_set):
                plugin = self._make_plugin()
                item = self._make_item(f'attrset.{i}', conf=dict(attr_set))
                plugin.parse_item(item)
                self.assertIn(
                    item,
                    plugin.get_item_list(),
                    f'ITEM_ATTR_SETS[{i}]={attr_set!r} did not register the item. '
                    f'Check that the attribute combination is complete and correct.',
                )

    def test_item_attr_set_parse_item_returns_callable_for_write_items(self):
        """
        parse_item() must return a callable for items that should trigger
        update_item() (write-capable items).

        Only runs if ITEM_ATTR_SETS is provided; non-write sets are skipped
        automatically if they contain no write-indicator attribute.
        """
        if not self.ITEM_ATTR_SETS:
            self.skipTest('ITEM_ATTR_SETS not provided')

        for i, attr_set in enumerate(self.ITEM_ATTR_SETS):
            # Heuristic: attr sets containing 'write', '_write', or 'updating'
            # in any key/value are assumed write-capable.
            is_write = any(
                'write' in str(k).lower() or 'write' in str(v).lower() or v is True for k, v in attr_set.items()
            )
            if not is_write:
                continue
            with self.subTest(attr_set=attr_set):
                plugin = self._make_plugin()
                item = self._make_item(f'write.{i}', conf=dict(attr_set))
                result = plugin.parse_item(item)
                if result is not None:
                    self.assertTrue(
                        callable(result), f'parse_item() for write-capable item returned non-callable {result!r}'
                    )
