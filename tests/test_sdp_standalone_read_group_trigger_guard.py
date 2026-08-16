#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for Standalone.find_read_group_triggers()
(lib.model.smartdeviceplugin): a read_groups entry missing its required
'trigger' key crashed struct generation with a bare TypeError
('NoneType' object is not subscriptable) instead of a clear error
pointing at the actual misconfigured commands.py entry.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

import tests.common as common

common.register_shng_log_levels()

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
                'read_groups': [{'name': 'somegroup'}],
            },
        },
    },
}
"""


class TestReadGroupsEntryMissingTrigger(unittest.TestCase):
    def test_struct_export_does_not_crash_on_missing_trigger_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp, 'missingtrigger', commands_src=_COMMANDS_SRC, plugin_yaml={'plugin': {'type': 'interface'}}
            )
            standalone.create_struct_yaml()  # must not raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
