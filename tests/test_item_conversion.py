#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Tests for lib/item_conversion.py, the .conf to YAML converter (tools/conf_to_yaml_converter.py, admin services)."""

import os
import tempfile
import unittest

from tests import common

common.register_shng_log_levels()

import lib.shyaml as shyaml
from lib.item_conversion import convert_yaml, parse_for_convert, yaml_save

CONF = """# Wohnzimmer
[wohnzimmer]
    name = Wohnzimmer
    [[licht]]
        type = bool
        visu_acl = rw
        knx_listen = 1/1/1 | 1/1/2
        enforce_updates = yes
        eval = sh.a() + 1  # inline
        cache = on
        uhrzeit = 8:30
        [[[status]]]
            type = num
            value = 010
"""


class TestConvertYaml(unittest.TestCase):
    def setUp(self):
        self.text = convert_yaml(parse_for_convert(conf_code=CONF))
        self.data, error = shyaml.yaml_load_fromstring(self.text)
        self.assertEqual('', error)

    def test_values_of_the_conf_file_keep_their_meaning(self):
        licht = self.data['wohnzimmer']['licht']
        self.assertEqual('yes', licht['enforce_updates'])
        self.assertEqual('on', licht['cache'])
        self.assertEqual('8:30', licht['uhrzeit'])
        self.assertEqual(['1/1/1', '1/1/2'], licht['knx_listen'])
        self.assertEqual(10, licht['status']['value'])

    def test_comments_are_kept(self):
        self.assertIn('# Wohnzimmer', self.text)
        self.assertIn('# inline', self.text)

    def test_layout(self):
        self.assertNotIn('%YAML', self.text)
        self.assertIn('\n    licht:\n        type: bool\n', self.text)
        self.assertIn('\n\n    licht:', self.text)

    def test_yaml_text_from_the_services_check_is_echoed_without_changing_values(self):
        data, _ = shyaml.yaml_load_fromstring(
            "a:\n    b: yes\n    c:\n      - x\n      - 'on'\n    d: 1:20\n", ordered=True
        )

        echoed, error = shyaml.yaml_load_fromstring(convert_yaml(data))

        self.assertEqual('', error)
        self.assertEqual({'a': {'b': 'yes', 'c': ['x', 'on'], 'd': '1:20'}}, echoed)


class TestYamlSave(unittest.TestCase):
    def test_conf_file_is_saved_as_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = os.path.join(tmp, 'items')
            yaml_save(base, parse_for_convert(conf_code=CONF))
            data = shyaml.yaml_load(base + '.yaml')

        self.assertEqual('yes', data['wohnzimmer']['licht']['enforce_updates'])


if __name__ == '__main__':
    unittest.main()
