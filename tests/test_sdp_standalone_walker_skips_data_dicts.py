#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for Standalone's command-tree walker (lib.model.smartdeviceplugin):
it recursed into EVERY dict-valued child of a command node, including
'item_attrs'/'cmd_settings'/'params' - opaque per-command data blobs that
create_item() reads directly off the parent command node, not further
command-tree levels.

create_item() only ever suppressed item-CREATION for the special key
ITSELF (item_attrs/cmd_settings/params/its own 'attributes' sub-key); it
never stopped the walker from recursing INTO them. This was invisible for
every real command definition used elsewhere as a test base (viessmann/
denon/kodi) because none of them happen to nest a dict inside a custom
'attributes' value - but item_attrs.attributes is documented as "add 1:1"
free-form custom item attributes, and nothing prevents one of those
values from being a dict. When it is, the walker treats its keys as
further command-tree levels and manufactures a spurious 'read'-trigger
item nested inside where the real, literal 1:1-copied attribute value
should be the only thing there.
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

            # bug symptom: the walker also descended into item_attrs and
            # its 'attributes' sub-key as if they were command-tree
            # levels, leaving a spurious literal 'item_attrs' branch
            # behind with a manufactured 'read'-trigger item nested in it
            self.assertNotIn('item_attrs', item, "walker treated 'item_attrs'/'attributes' as command-tree nodes")


if __name__ == '__main__':
    unittest.main(verbosity=2)
