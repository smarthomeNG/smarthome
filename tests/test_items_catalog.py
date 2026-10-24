#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests that modules/core/items.yaml, the item attribute catalog, agrees with the attribute keys
the item code defines in lib/constants.py.

The catalog is part of the public API (doc/dev/public_api.md); an attribute missing from it, or
listed under a different name than the code uses, is invisible to the API checks.
"""

import os
import unittest

import yaml

import tests.common as common  # noqa: F401  (puts the shng base dir on sys.path)
import lib.constants as constants

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'modules', 'core', 'items.yaml')

# KEY_* constants that are no catalogued item attribute: plugin config keys, log_rules sub-keys, deprecated 'value'
NOT_ITEM_ATTRIBUTES = {
    'KEY_VALUE',
    'KEY_INSTANCE',
    'KEY_DEFAULT_INSTANCE',
    'KEY_WEBIF_PAGELENGTH',
    'KEY_CLASS_PATH',
    'KEY_CLASS_NAME',
    'KEY_ATTRIB_COMPAT',
    'KEY_LOG_RULES_LOWLIMIT',
    'KEY_LOG_RULES_HIGHLIMIT',
    'KEY_LOG_RULES_FILTER',
    'KEY_LOG_RULES_EXCLUDE',
    'KEY_LOG_RULES_ITEMVALUE',
}


def catalog():
    with open(CATALOG_PATH, encoding='utf-8') as f:
        return yaml.safe_load(f)['item_attributes']


def code_attributes():
    return {
        value
        for name, value in vars(constants).items()
        if name.startswith('KEY_') and name not in NOT_ITEM_ATTRIBUTES and isinstance(value, str)
    }


class TestItemAttributeCatalog(unittest.TestCase):
    def test_every_item_attribute_of_the_code_is_in_the_catalog(self):
        self.assertEqual([], sorted(code_attributes() - set(catalog())))

    def test_every_catalog_attribute_exists_in_the_code(self):
        self.assertEqual([], sorted(set(catalog()) - code_attributes()))

    def test_every_attribute_has_a_type_and_english_and_german_description(self):
        for name, spec in catalog().items():
            with self.subTest(attribute=name):
                self.assertIn('type', spec)
                self.assertTrue(spec['description']['en'].strip())
                self.assertTrue(spec['description']['de'].strip())

    def test_type_attribute_lists_the_item_types_of_the_code(self):
        self.assertEqual(set(constants.ITEM_TYPES), set(catalog()['type']['valid_list']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
