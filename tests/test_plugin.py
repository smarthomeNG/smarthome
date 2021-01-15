
from . import common
import unittest

from lib.model.smartplugin import SmartPlugin

from tests.mock.core import MockSmartHome

class TestPlugin(unittest.TestCase):

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + "/tests/resources/plugin")
        self.item_conf = self.sh.with_items_from(common.BASE + "/tests/resources/plugin_items.conf")

    def test_plugin_is_registered(self):
        self.assertIsNotNone(self.plugins.get_pluginthread("wol"))

    def test_plugin_not_registered(self):
        self.assertIsNone(self.plugins.get_pluginthread("wol1"))

    def test_plugin_name(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")
        self.assertEqual(wolplug.name, "wol_ww")

    def test_plugin_implementation(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")
        self.assertEqual(wolplug.plugin, wolplug.get_implementation())

    def test_plugin_ident(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")
        self.assertIsNone(wolplug.ident)
        self.plugins.start()
        self.assertEqual(wolplug.ident, wolplug.get_ident())
        self.assertIsNotNone(wolplug.get_ident())
        self.plugins.stop()

    def test_plugin_instance_not_set(self):
        cliplug = self.plugins.get_pluginthread("cli")
        self.assertEqual(cliplug.plugin.get_instance_name(),"")

    def test_plugin_instance_set(self):
        cliplug = self.plugins.get_pluginthread("wol_ww")
        self.assertEqual(cliplug.plugin.get_instance_name(),"bind")


    def test_plugin_multi_instance_capable_true(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")
        self.assertTrue(isinstance(wolplug.plugin, SmartPlugin))
        self.assertTrue(wolplug.plugin.is_multi_instance_capable())

        cliplug = self.plugins.get_pluginthread("cli")
        self.assertTrue(isinstance(cliplug.plugin, SmartPlugin))
        self.assertTrue(cliplug.plugin.is_multi_instance_capable())


    def test_plugin_multi_instance_capable_false(self):
        pass
        # cliplug = self.plugins.get_pluginthread("cli")
        # self.assertTrue(isinstance(cliplug.plugin, SmartPlugin))
        # self.assertFalse(cliplug.plugin.is_multi_instance_capable())


    def test_plugin_instance_not_set_has_iattr(self):
        wolplug = self.plugins.get_pluginthread("wol")

        config_mock = {'key3', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock,"key3"))
        config_mock = {'key3@*', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@false*', 'value3'}
        self.assertFalse(wolplug.plugin.has_iattr(config_mock, "key3"))

    def test_plugin_instance_set_has_iattr(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")

        config_mock = {'key3@bind', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@*', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@false', 'value3'}
        self.assertFalse(wolplug.plugin.has_iattr(config_mock, "key3"))

    def test_plugin_instance_not_set_get_iattr_value(self):
        wolplug = self.plugins.get_pluginthread("wol")

        config_mock = {'key3@*' : 'value3'}
        self.assertEqual(wolplug.plugin.get_iattr_value(config_mock, "key3"), "value3")
        config_mock = {'key3@bind' : 'value2'}
        self.assertIsNone(wolplug.plugin.get_iattr_value(config_mock, "key3"))
        config_mock = {'key3@bind2' : 'value4'}
        self.assertIsNone(wolplug.plugin.get_iattr_value(config_mock, "key3"))

    def test_plugin_instance_set_get_iattr_value(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")

        config_mock = {'key3@*' : 'value3'}
        self.assertEqual(wolplug.plugin.get_iattr_value(config_mock, "key3"), "value3")
        config_mock = {'key3@bind' : 'value2'}
        self.assertEqual(wolplug.plugin.get_iattr_value(config_mock, "key3"), "value2")
        config_mock = {'key3@bind2', 'value4'}
        self.assertIsNone(wolplug.plugin.get_iattr_value(config_mock, "key3"))

    def test_plugin_instance_not_used_in_item_config(self):
        it = self.sh.items.return_item("item3.item3b.item3b1")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),1)

    def test_plugin_instance_used_in_item_config(self):
        it = self.sh.items.return_item("item3.item3b.item3b1.item3b1a")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),2)

    def test_plugin_instance_no_attributes_item_config(self):
        it = self.sh.items.return_item("item3.item3b")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),0)

    def test_plugin_instance_wol(self):
        wolplug = self.plugins.get_pluginthread("wol_ww")
        self.sh.scheduler.add(wolplug.name, wolplug.plugin.update_item, prio=5, cycle=300, offset=2)
        wolplug.plugin.wake_on_lan("11:22:33:44:55:66")

    def _test_configsave(self):
        import configparser
        item_conf = self.item_conf

        config = configparser.RawConfigParser( )
        #config.read(common.BASE + '/tests/resources/plugin_items.conf')
        config.read_dict(item_conf)
        print(config)
        with open('example.cfg', 'w') as configfile:
            config.write(configfile)

if __name__ == '__main__':
    unittest.main(verbosity=2)

