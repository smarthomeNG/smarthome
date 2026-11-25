#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Standalone.create_struct_yaml() rewrites the plugin's plugin.yaml; every value outside the
generated ``item_structs`` section must read back unchanged, including strings with line breaks.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import ruamel.yaml as ruamel_yaml
from ruamel.yaml import YAML

import tests.common as common

common.register_shng_log_levels()

from tests._sdp_standalone_export_helper import build_synthetic_standalone

_COMMANDS_SRC = """
commands = {
    'power': {'read': True, 'write': True, 'opcode': 'PW', 'item_type': 'bool', 'dev_datatype': 'raw'},
}

models = {'ALL': ['power']}
"""

_PLUGIN_YAML_TEXT = """\
plugin:
    type: interface
    version: 1.0.0

parameters:
    terminator:
        type: str
        default: "\\n"
        description:
            de: Zeilenende
    cr_terminator:
        type: str
        default: "\\r"
    crlf_terminator:
        type: str
        default: "\\r\\n"
    paragraphs:
        type: str
        default: "one\\n\\ntwo\\n"
    colon_line:
        type: str
        default: "see:\\nnext line"
    lines:
        type: str
        description:
            de: |
                first line
                second line
            fr: |
                Options:
                - a
                - b

                tail
            en: 'folded
                 text'
"""


def _load(path):
    return YAML(typ='safe').load(path.read_text(encoding='utf8'))


class TestStructExportKeepsValues(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self._representers = {
            cls: cls.yaml_representers[str] for cls in (ruamel_yaml.Dumper, ruamel_yaml.representer.SafeRepresenter)
        }

    def tearDown(self):
        for cls, representer in self._representers.items():
            cls.add_representer(str, representer)

    def test_values_outside_item_structs_are_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_synthetic_standalone(
                tmp, 'valuekeeper', _COMMANDS_SRC, {'plugin': {'type': 'interface'}}
            )
            plugin_yaml = standalone.plugin_path / 'plugin.yaml'
            plugin_yaml.write_text(_PLUGIN_YAML_TEXT, encoding='utf8')
            before = _load(plugin_yaml)

            standalone.create_struct_yaml()

            after = _load(plugin_yaml)
            self.assertEqual(after['parameters'], before['parameters'])
            self.assertEqual(after['plugin'], before['plugin'])


if __name__ == '__main__':
    unittest.main()
