#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Item attribute access of SmartPlugin for plugins with and without instance name."""

import unittest

from lib.model.smartplugin import SmartPlugin


class _Plugin(SmartPlugin):
    PLUGIN_VERSION = '1.0.0'

    def __init__(self, instance: str = ''):
        if instance:
            self._set_multi_instance_capable(True)
            self._set_instance_name(instance)

    def run(self):
        pass

    def stop(self):
        pass


class TestSetAttrValue(unittest.TestCase):
    def test_existing_attribute_is_overwritten(self):
        conf = {'knx_send': '1/1/1'}
        _Plugin().set_attr_value(conf, 'knx_send', ['1/1/1'])
        self.assertEqual({'knx_send': ['1/1/1']}, conf)

    def test_existing_instance_attribute_is_overwritten(self):
        conf = {'knx_send@fb1': '1/1/1'}
        _Plugin('fb1').set_attr_value(conf, 'knx_send', ['1/1/1'])
        self.assertEqual({'knx_send@fb1': ['1/1/1']}, conf)

    def test_missing_attribute_is_not_added(self):
        conf = {'knx_send@fb2': '1/1/1'}
        _Plugin('fb1').set_attr_value(conf, 'knx_send', ['1/1/1'])
        self.assertEqual({'knx_send@fb2': '1/1/1'}, conf)

    def test_wildcard_attribute_is_set_for_this_instance_only(self):
        conf = {'knx_send@*': '1/1/1'}
        first, second = _Plugin('fb1'), _Plugin('fb2')

        first.set_attr_value(conf, 'knx_send', ['1/1/1'])

        self.assertEqual(['1/1/1'], first.get_iattr_value(conf, 'knx_send'))
        self.assertEqual('1/1/1', second.get_iattr_value(conf, 'knx_send'))

    def test_wrapping_the_value_per_instance_does_not_nest(self):
        conf = {'knx_send@*': '1/1/1'}
        for plugin in (_Plugin('fb1'), _Plugin('fb2')):
            plugin.set_attr_value(conf, 'knx_send', [plugin.get_iattr_value(conf, 'knx_send')])

        self.assertEqual(['1/1/1'], conf['knx_send@fb1'])
        self.assertEqual(['1/1/1'], conf['knx_send@fb2'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
