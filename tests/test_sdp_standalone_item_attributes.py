#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression tests for Standalone.update_item_attributes() and its use in
create_item() (lib.model.smartdeviceplugin).

Two separate bugs, both around plugin-specific item-attribute prefixes
(e.g. viessmann's plugin.yaml renames the generic '_command' attribute to
'viess_command'):

1. update_item_attributes() did `yaml.get('item_attributes').keys()` -
   AttributeError on any plugin.yaml with no 'item_attributes' section at
   all (a legitimate case - not every SDP plugin renames its attributes).

2. The resolved rename was applied by reassigning bare names
   (ITEM_ATTR_COMMAND etc.) in THIS MODULE's own globals() dict at
   runtime - a self-monkeypatch that only "works" because standalone mode
   is a short-lived, single-purpose process. The custom2/custom3 case was
   additionally broken independently of that: instead of resolving
   ITEM_ATTR_CUSTOM2/3 themselves, create_item derived their prefixed
   name from the (mutated) ITEM_ATTR_CUSTOM1 string via
   `ITEM_ATTR_CUSTOM1[:-1] + '2'` - this only produces the right answer
   when a plugin's custom2/custom3 renames happen to share custom1's
   exact stem with just the trailing digit changed (true for viessmann's
   viess_custom1/2/3, which is why it was never noticed).

The fix mirrors SmartDevicePlugin._set_item_attributes()'s already-
established pattern: resolve into an instance dict (self._item_attrs)
instead of mutating module globals.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

import tests.common as common

common.register_shng_log_levels()

import lib.shyaml as shyaml
from tests._sdp_standalone_export_helper import build_synthetic_standalone

_COMMANDS_SRC = """
commands = {{
    'ALL': {{
        'testcmd': {{
            'read': True,
            'write': False,
            'opcode': 'foo',
            'item_type': 'str',
            {item_attrs}
        }},
    }},
}}
"""


class TestMissingItemAttributesSection(unittest.TestCase):
    def test_struct_export_does_not_crash_without_item_attributes_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp,
                'noattrs',
                commands_src=_COMMANDS_SRC.format(item_attrs=''),
                plugin_yaml={'plugin': {'type': 'interface'}},  # no 'item_attributes' key at all
            )
            standalone.create_struct_yaml()  # must not raise

            result = shyaml.yaml_load(standalone.plugin_path / 'plugin.yaml')
            self.assertIn('testcmd', result['item_structs']['ALL'])

    def test_generic_attribute_name_used_when_no_rename_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp,
                'noattrs2',
                commands_src=_COMMANDS_SRC.format(item_attrs=''),
                plugin_yaml={'plugin': {'type': 'interface'}},
            )
            standalone.create_struct_yaml()

            result = shyaml.yaml_load(standalone.plugin_path / 'plugin.yaml')
            item = result['item_structs']['ALL']['testcmd']
            self.assertIn('_command@instance', item)


class TestCustom2RenameDoesNotRelyOnCustom1Stem(unittest.TestCase):
    """custom2's resolved attribute name must come from the plugin's own
    custom2 declaration, not be derived from custom1's resolved name -
    use deliberately UNRELATED stems ('foo_custom1' vs 'bar_custom2') so
    the custom1-derivation bug can't accidentally produce the right
    answer by coincidence, the way it does for viessmann's viess_custom1/
    viess_custom2 (same stem, only the digit differs)."""

    def test_custom2_uses_its_own_declared_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp,
                'customprefix',
                commands_src=_COMMANDS_SRC.format(item_attrs="'item_attrs': {'custom2': 'somevalue'},"),
                plugin_yaml={
                    'plugin': {'type': 'interface'},
                    'item_attributes': {'foo_custom1': {'type': 'str'}, 'bar_custom2': {'type': 'str'}},
                },
            )
            standalone.create_struct_yaml()

            result = shyaml.yaml_load(standalone.plugin_path / 'plugin.yaml')
            item = result['item_structs']['ALL']['testcmd']
            self.assertIn('bar_custom2@instance', item)
            self.assertNotIn('foo_custom2@instance', item)  # what custom1-string-surgery would produce
            self.assertNotIn('_custom2@instance', item)  # unrenamed generic fallback


if __name__ == '__main__':
    unittest.main(verbosity=2)
