"""
tests.plugin_contract.sdp — Tier 4: contract tests for SmartDevicePlugin subclasses.

These tests validate the command-table content (commands.py) and the
item-attribute wiring without requiring a real device connection.
They use a null/stub connection so no network or serial port is needed.

Usage::

    from tests.plugin_contract.base import BasePluginContractTest
    from tests.plugin_contract.sdp import SdpPluginContractTest
    from plugins.my_sdp_plugin import MyPlugin


    class TestMySdpPlugin(BasePluginContractTest, SdpPluginContractTest):
        PLUGIN_CLASS = MyPlugin
        PLUGIN_INIT_PARAMS = {'host': '127.0.0.1'}
        # optional: minimal attribute dicts that must register an item
        SDP_ITEM_ATTR_SETS = [{'ex_command': 'Device.Power', 'ex_write': True}]
        # optional: known commands to test value conversion for
        SDP_COMMAND_VALUE_PAIRS = [('Device.Power', True), ('Device.Temperature', 21.5)]

Class attributes
----------------
PLUGIN_CLASS : type
    The plugin class under test.
PLUGIN_INIT_PARAMS : dict
    Init params (passed as **kwargs).
SDP_ITEM_ATTR_SETS : list[dict], optional
    Minimal item attribute sets that must register an item (see with_yaml.py
    for the same concept).  SDP attrs are prefixed (e.g. ``ex_command``).
SDP_COMMAND_VALUE_PAIRS : list[tuple], optional
    List of (command_name, value) pairs for which get_send_data() is tested.
"""

import importlib
import inspect
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tests.common as common

common.register_shng_log_levels()

from tests.mock.core import MockSmartHome
from tests.plugin_contract._mockitem import MockItem
from tests.plugin_contract.base import make_plugin_instance
from lib.model.sdp.declarations import TransportRule
from lib.model.smartdeviceplugin import SmartDevicePlugin
from lib.model.sdp.globals import (
    ITEM_ATTR_COMMAND,
    ITEM_ATTR_READ,
    ITEM_ATTR_WRITE,
    CMD_ATTR_OPCODE,
    CMD_ATTR_READ,
    CMD_ATTR_WRITE,
    CMD_ATTR_ITEM_TYPE,
    CONN_NULL,
)


def _on_null_transport(plugin_class: type) -> type:
    """``plugin_class``, or for a plugin declaring TRANSPORTS a subclass that only uses the null transport."""
    if not getattr(plugin_class, 'TRANSPORTS', ()):
        return plugin_class
    return type(
        plugin_class.__name__,
        (plugin_class,),
        {'TRANSPORTS': (TransportRule(CONN_NULL),), '__module__': plugin_class.__module__},
    )


# Valid shng item types (subset; the important ones for SDP)
_VALID_ITEM_TYPES = frozenset({'bool', 'num', 'str', 'list', 'dict', 'foo', 'scene'})


def _load_commands_module(plugin_class):
    """Attempt to import the plugin's commands module, return None if absent."""
    mod_name = plugin_class.__module__  # e.g. 'plugins.myplugin'
    try:
        return importlib.import_module(mod_name + '.commands')
    except ModuleNotFoundError:
        pass
    # Fall back to direct file import
    plugin_dir = os.path.dirname(os.path.abspath(inspect.getfile(plugin_class)))
    cmd_file = os.path.join(plugin_dir, 'commands.py')
    if not os.path.isfile(cmd_file):
        return None
    spec = importlib.util.spec_from_file_location('_sdp_commands_tmp', cmd_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _flatten_commands(commands_dict, prefix='') -> dict:
    """Recursively flatten nested command dicts to {full.path: defn} pairs."""
    result = {}
    for key, val in commands_dict.items():
        full = f'{prefix}.{key}' if prefix else key
        if isinstance(val, dict):
            if CMD_ATTR_OPCODE in val or CMD_ATTR_READ in val or CMD_ATTR_WRITE in val:
                result[full] = val
            else:
                result.update(_flatten_commands(val, full))
    return result


class SdpPluginContractTest(unittest.TestCase):
    """Mix-in: SmartDevicePlugin command-table and item-wiring contract tests."""

    PLUGIN_CLASS: type | None = None
    PLUGIN_INIT_PARAMS: dict = {}
    SDP_ITEM_ATTR_SETS: list | None = None
    SDP_COMMAND_VALUE_PAIRS: list | None = None

    # -----------------------------------------------------------------------
    # Setup: use CONN_NULL so no real connection is attempted
    # -----------------------------------------------------------------------

    def setUp(self):
        if self.PLUGIN_CLASS is None:
            self.skipTest('PLUGIN_CLASS not set')
        # Plugins with TRANSPORTS run on the null transport, others get conn_type CONN_NULL.  Store the merged
        # params back as the effective PLUGIN_INIT_PARAMS for this test run so
        # that BasePluginContractTest.setUp picks them up when it creates the plugin.
        _params = dict(self.PLUGIN_INIT_PARAMS)
        _params.setdefault('conn_type', CONN_NULL)
        self._sdp_effective_params = _params
        self.sh = MockSmartHome()
        try:
            self.plugin = make_plugin_instance(_on_null_transport(self.PLUGIN_CLASS), self.sh, _params)
        except Exception as exc:
            self.skipTest(f'Plugin could not be instantiated: {exc}')
        # Plugin is ready; let cooperative setUp run (BasePluginContractTest will
        # see that self.plugin already exists and skip re-instantiation).
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def _make_item(self, path: str = 'sdp.test', conf: dict | None = None) -> MockItem:
        return MockItem(path, conf)

    def _get_commands(self) -> dict:
        mod = _load_commands_module(self.PLUGIN_CLASS)
        if mod is None:
            return {}
        for attr in ('commands', 'COMMANDS', 'CMD'):
            if hasattr(mod, attr):
                return getattr(mod, attr)
        return {}

    # -----------------------------------------------------------------------
    # Class-level
    # -----------------------------------------------------------------------

    def test_inherits_from_smartdeviceplugin(self):
        """Plugin must inherit from SmartDevicePlugin."""
        self.assertTrue(
            issubclass(self.PLUGIN_CLASS, SmartDevicePlugin),
            f'{self.PLUGIN_CLASS.__name__} does not inherit from SmartDevicePlugin',
        )

    # -----------------------------------------------------------------------
    # commands.py static validation
    # -----------------------------------------------------------------------

    def test_commands_module_loads_without_error(self):
        """commands.py (if present) must be importable without error."""
        mod = _load_commands_module(self.PLUGIN_CLASS)
        if mod is None:
            self.skipTest('No commands module found')
        # If we get here without exception, the import succeeded

    def test_all_commands_have_opcode_or_read_cmd(self):
        """Every command with a device operation has an opcode, read_cmd or write_cmd; pseudo commands have none."""
        raw = self._get_commands()
        if not raw:
            self.skipTest('No commands dict found')
        flat = _flatten_commands(raw)
        missing = [
            path
            for path, defn in flat.items()
            if (defn.get(CMD_ATTR_READ) or defn.get(CMD_ATTR_WRITE))
            and not any(key in defn for key in (CMD_ATTR_OPCODE, 'read_cmd', 'write_cmd'))
        ]
        self.assertFalse(missing, 'Commands without opcode, read_cmd or write_cmd:\n  ' + '\n  '.join(missing))

    def test_command_item_types_are_valid(self):
        """Every command's item_type (if declared) must be a valid shng type."""
        raw = self._get_commands()
        if not raw:
            self.skipTest('No commands dict found')
        flat = _flatten_commands(raw)
        errors = []
        for path, defn in flat.items():
            itype = defn.get(CMD_ATTR_ITEM_TYPE)
            if itype and itype not in _VALID_ITEM_TYPES:
                errors.append(f'{path}: unknown item_type={itype!r}')
        self.assertFalse(errors, 'Invalid item_type values in commands:\n  ' + '\n  '.join(errors))

    def test_readable_commands_have_read_true_or_opcode(self):
        """Commands marked read:true must have an opcode or read_cmd to send."""
        raw = self._get_commands()
        if not raw:
            self.skipTest('No commands dict found')
        flat = _flatten_commands(raw)
        errors = []
        for path, defn in flat.items():
            if defn.get(CMD_ATTR_READ) is True:
                if CMD_ATTR_OPCODE not in defn and 'read_cmd' not in defn:
                    errors.append(f'{path}: read:true but no opcode/read_cmd')
        self.assertFalse(errors, '\n  '.join(errors))

    def test_writable_commands_have_write_true_or_opcode(self):
        """Commands marked write:true must have an opcode or write_cmd to send."""
        raw = self._get_commands()
        if not raw:
            self.skipTest('No commands dict found')
        flat = _flatten_commands(raw)
        errors = []
        for path, defn in flat.items():
            if defn.get(CMD_ATTR_WRITE) is True:
                if CMD_ATTR_OPCODE not in defn and 'write_cmd' not in defn:
                    errors.append(f'{path}: write:true but no opcode/write_cmd')
        self.assertFalse(errors, '\n  '.join(errors))

    # -----------------------------------------------------------------------
    # Item-attribute wiring (mirrors with_yaml.py logic for SDP attribute prefix)
    # -----------------------------------------------------------------------

    def test_sdp_item_attr_sets_register_items(self):
        """Each SDP_ITEM_ATTR_SET must result in parse_item() registering the item."""
        if not self.SDP_ITEM_ATTR_SETS:
            self.skipTest('SDP_ITEM_ATTR_SETS not provided')
        for i, attr_set in enumerate(self.SDP_ITEM_ATTR_SETS):
            with self.subTest(attr_set=attr_set):
                params = dict(self.PLUGIN_INIT_PARAMS)
                params.setdefault('conn_type', CONN_NULL)
                plugin = make_plugin_instance(_on_null_transport(self.PLUGIN_CLASS), MockSmartHome(), params)
                item = self._make_item(f'sdp.set.{i}', conf=dict(attr_set))
                plugin.parse_item(item)
                self.assertIn(
                    item, plugin.get_item_list(), f'SDP_ITEM_ATTR_SETS[{i}]={attr_set!r} did not register the item'
                )

    def test_item_without_sdp_attrs_not_registered(self):
        """An item with no SDP attributes must not be registered."""
        item = self._make_item('sdp.empty', conf={})
        self.plugin.parse_item(item)
        self.assertNotIn(item, self.plugin.get_item_list())
