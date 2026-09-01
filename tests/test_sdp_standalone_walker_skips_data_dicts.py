#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for Standalone's command-tree walker (lib.model.smartdeviceplugin):
it must not recurse into 'item_attrs'/'cmd_settings'/'params' - opaque
per-command data blobs that create_item() reads directly off the parent
command node, not further command-tree levels.

item_attrs.attributes is documented as "add 1:1" free-form custom item
attributes, and nothing prevents one of those values from being a dict -
the walker must not treat its keys as further command-tree levels and
manufacture a spurious 'read'-trigger item nested inside where the real,
literal 1:1-copied attribute value should be the only thing there.
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
commands = {
    'ALL': {
        'testcmd': {
            'read': True,
            'write': False,
            'opcode': 'foo',
            'item_type': 'str',
            'item_attrs': {
                'attributes': {
                    'weird_attr': {'nested': 'value'},
                },
            },
        },
    },
}
"""


class TestWalkerDoesNotDescendIntoCustomAttributeValues(unittest.TestCase):
    def test_dict_valued_custom_attribute_is_copied_literally_not_walked(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp, 'dictattr', commands_src=_COMMANDS_SRC, plugin_yaml={'plugin': {'type': 'interface'}}
            )
            standalone.create_struct_yaml()

            result = shyaml.yaml_load(standalone.plugin_path / 'plugin.yaml')
            item = result['item_structs']['ALL']['testcmd']

            # correct behaviour: 'attributes' 1:1 copy merges the nested
            # dict value straight into the item
            self.assertEqual(item.get('weird_attr'), {'nested': 'value'})

            # must not descend into item_attrs/'attributes' as if they were
            # command-tree levels, leaving a spurious literal 'item_attrs'
            # branch with a manufactured 'read'-trigger item nested in it
            self.assertNotIn('item_attrs', item, "walker treated 'item_attrs'/'attributes' as command-tree nodes")


if __name__ == '__main__':
    unittest.main(verbosity=2)
