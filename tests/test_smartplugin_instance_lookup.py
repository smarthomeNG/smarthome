#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Item attribute lookup of SmartPlugin by instance name, section name and the item's ``instance``."""

import unittest
from typing import Collection

from lib.model.smartplugin import SmartPlugin


class _Plugin(SmartPlugin):
    PLUGIN_VERSION = '1.0.0'

    def __init__(self, section: str, instance: str = '', siblings: Collection[str] = ()):
        self._set_configname(section)
        self._siblings = set(siblings)
        if instance:
            self._set_multi_instance_capable(True)
            self._set_instance_name(instance)

    def _sibling_confignames(self) -> set[str]:
        return self._siblings

    def run(self):
        pass

    def stop(self):
        pass


class TestSectionNameMatch(unittest.TestCase):
    def test_default_plugin_matches_attribute_suffixed_with_its_section_name(self):
        default = _Plugin('fb1')
        conf = {'avm_x@fb1': 1}
        self.assertTrue(default.has_iattr(conf, 'avm_x'))
        self.assertEqual(1, default.get_iattr_value(conf, 'avm_x'))


class TestBareAttributeWithoutItemInstance(unittest.TestCase):
    def test_bare_attribute_reaches_only_the_default_plugin(self):
        conf = {'avm_x': 1}
        self.assertTrue(_Plugin('fb1').has_iattr(conf, 'avm_x'))
        self.assertFalse(_Plugin('fb2', 'fb2').has_iattr(conf, 'avm_x'))


class TestItemInstance(unittest.TestCase):
    def test_item_instance_binds_bare_attribute_to_the_named_plugin(self):
        conf = {'avm_x': 1, 'instance': ['fb2']}
        self.assertTrue(_Plugin('fb2', 'fb2').has_iattr(conf, 'avm_x'))
        self.assertFalse(_Plugin('fb3', 'fb3').has_iattr(conf, 'avm_x'))

    def test_default_plugin_skips_bare_attribute_when_item_names_a_sibling_section(self):
        conf = {'avm_x': 1, 'instance': ['fb2']}
        self.assertFalse(_Plugin('fb1', siblings={'fb2'}).has_iattr(conf, 'avm_x'))

    def test_default_plugin_keeps_bare_attribute_when_item_names_another_plugins_section(self):
        conf = {'avm_x': 1, 'instance': ['db_2']}
        self.assertTrue(_Plugin('fb1', siblings={'fb2'}).has_iattr(conf, 'avm_x'))

    def test_list_binds_each_plugin_to_its_own_entry(self):
        conf = {'avm_x': 1, 'db_q': 2, 'instance': ['fb2', 'db_2']}
        self.assertTrue(_Plugin('fb2', 'fb2').has_iattr(conf, 'avm_x'))
        self.assertTrue(_Plugin('db_2', 'db_2').has_iattr(conf, 'db_q'))
        self.assertFalse(_Plugin('db_1', 'db_1').has_iattr(conf, 'db_q'))

    def test_explicit_attribute_wins_over_item_instance(self):
        conf = {'avm_x': 1, 'avm_x@fb1': 2, 'instance': ['fb2']}
        self.assertEqual(2, _Plugin('fb1', siblings={'fb2'}).get_iattr_value(conf, 'avm_x'))
        self.assertEqual(1, _Plugin('fb2', 'fb2').get_iattr_value(conf, 'avm_x'))

    def test_wildcard_reaches_default_plugin_despite_item_instance(self):
        conf = {'avm_x@*': 3, 'instance': ['fb2']}
        self.assertEqual(3, _Plugin('fb1', siblings={'fb2'}).get_iattr_value(conf, 'avm_x'))

    def test_empty_item_instance_binds_bare_attribute_to_the_default_plugin(self):
        conf = {'avm_x': 1, 'instance': ['']}
        self.assertTrue(_Plugin('fb1', siblings={'fb2'}).has_iattr(conf, 'avm_x'))
        self.assertFalse(_Plugin('fb2', 'fb2').has_iattr(conf, 'avm_x'))


class TestSetAttrValue(unittest.TestCase):
    def test_value_found_by_section_name_is_written_back_to_that_key(self):
        conf = {'avm_x@fb1': 1}
        plugin = _Plugin('fb1')
        plugin.set_attr_value(conf, 'avm_x', 2)
        self.assertEqual({'avm_x@fb1': 2}, conf)

    def test_default_plugin_does_not_write_the_bare_key_a_sibling_named_by_the_item_reads(self):
        conf = {'avm_x@*': 1, 'instance': ['fb2']}
        default, sibling = _Plugin('fb1', siblings={'fb2'}), _Plugin('fb2', 'fb2')
        default.set_attr_value(conf, 'avm_x', 2)
        self.assertEqual(2, default.get_iattr_value(conf, 'avm_x'))
        self.assertEqual(1, sibling.get_iattr_value(conf, 'avm_x'))

    def test_value_found_by_the_item_instance_is_written_back_to_the_bare_key(self):
        conf = {'avm_x': 1, 'instance': ['fb2']}
        _Plugin('fb2', 'fb2').set_attr_value(conf, 'avm_x', 2)
        self.assertEqual({'avm_x': 2, 'instance': ['fb2']}, conf)


if __name__ == '__main__':
    unittest.main(verbosity=2)
