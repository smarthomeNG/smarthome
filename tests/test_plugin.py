
import common
import unittest
import lib.plugin
import lib.item
from lib.model.smartplugin import SmartPlugin
import threading

class TestConfig(unittest.TestCase):
    def props(self,cls):   
        return [i for i in cls.__dict__.keys() if i[:1] != '_']
    def test_plugins(self):
        plugins = lib.plugin.Plugins(MockSmartHome(), "resources/plugin.conf")
        self.assertIsNone(plugins.get_plugin("wol1") )
        self.assertIsNotNone(plugins._plugins )
        if 0:
            for p in plugins._threads: 
                print(p.name)
                print(p.plugin)
                print(self.props(p.plugin))
                print(dir(p.plugin))
                import inspect
                print(inspect.getmembers(p.plugin, lambda a:not(inspect.isroutine(a))))

        wolplug= plugins.get_plugin("wol_ww") 

        self.assertIsNotNone(wolplug )
        self.assertEqual(wolplug.name,"wol_ww" )
        self.assertIsNone(wolplug.ident )
        plugins.start()
        self.assertEqual(wolplug.ident,wolplug.get_ident())
        self.assertEqual(wolplug.plugin, wolplug.get_implementation())
        self.assertIsNotNone(wolplug.get_ident() )
        
        plugins.stop()
#        print(plugins.get_plugin("wol").get_ident() )
        
    def test_plugininstance(self):
        sh=MockSmartHome()
        # load pluginsA
        plugins = lib.plugin.Plugins(sh, "resources/plugin.conf")
        sh._plugins=plugins
        wolplug= plugins.get_plugin("wol")
        self.assertEqual(wolplug.plugin.get_instance_name(),"")

        config_mock = {'key3', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock,"key3"))
        config_mock = {'key3@*', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@false*', 'value3'}
        self.assertFalse(wolplug.plugin.has_iattr(config_mock, "key3"))

        wolplug = plugins.get_plugin("wol_ww")
        #wolplug.plugin.ALLOW_MULTIINSTANCE= False
        #wolplug.plugin.set_instance_name("")
        self.assertTrue(isinstance(wolplug.plugin, SmartPlugin))
        self.assertTrue(wolplug.plugin.is_multi_instance_capable())
        self.assertEqual(wolplug.plugin.get_instance_name(),"bind")

        config_mock = {'key3@bind', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@*', 'value3'}
        self.assertTrue(wolplug.plugin.has_iattr(config_mock, "key3"))
        config_mock = {'key3@false', 'value3'}
        self.assertFalse(wolplug.plugin.has_iattr(config_mock, "key3"))

        config_mock = {}
        config_mock["key3@*"] = "value3"
        self.assertEqual(wolplug.plugin.get_iattr_value(config_mock, "key3"), "value3")
        config_mock = {}
        config_mock["key3@bind"] = "value2"
        self.assertEqual(wolplug.plugin.get_iattr_value(config_mock, "key3"), "value2")
        config_mock = {}
        config_mock["key3@bind2"] = "value4"
        self.assertIsNone(wolplug.plugin.get_iattr_value(config_mock, "key3"))
        
        if 0:
            print(sh._plugins)        
            for plug in sh.return_plugins():
                print(plug)
        #load items
        item_conf = None
        item_conf = lib.config.parse("resources/plugin_items.conf", item_conf)
#        print(item_conf.items())
        for attr, value in item_conf.items():
            if isinstance(value, dict):
                child_path = attr
                try:
                    child = lib.item.Item(sh, sh, child_path, value)
                except Exception as e:
                    self.logger.error("Item {}: problem creating: ()".format(child_path, e))
                else:
                    #vars(sh)[attr] = child
                    sh.add_item(child_path, child)
                    sh.children.append(child)
#        for item in sh.return_items():
#            item._init_prerun()
#        for item in sh.return_items():
#            item._init_run()
#       
        if 0: self.dump_items(sh)

        it = sh.return_item("item3.item3b.item3b1.item3b1a")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),2)
        it = sh.return_item("item3.item3b.item3b1")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),1)
        it = sh.return_item("item3.item3b")
        self.assertIsNotNone(it)
        self.assertEqual(len(it.get_method_triggers()),0)
        sh.scheduler.add(wolplug.name, wolplug.plugin.update_item, prio=5, cycle=300, offset=2)
        wolplug.plugin.testprint()
        wolplug.plugin.wake_on_lan("11:22:33:44:55:66")

    def _update_dummy(self):
        print("update dummy")
    def dump_items(self, sh ):
        for item in sh.return_items():
            print(item)
            for meth in item.get_method_triggers():
                print('   ' + meth.__self__.get_info())

    def _test_configsave(self):
        import configparser
        plugins = lib.plugin.Plugins(MockSmartHome(), "resources/plugin.conf")
        item_conf = None
        item_conf = lib.config.parse("resources/plugin_items.conf", item_conf)
        print(item_conf)
        for attr, value in item_conf.items():
            if isinstance(value, dict):
                child_path = attr
                try:
                    child = lib.item.Item(self, self, child_path, value)
                except Exception as e:
                    print("Item {}: problem creating: ()".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    sh.add_item(child_path, child)
                    sh.children.append(child)
        config = configparser.RawConfigParser( )
        #config.read('resources/plugin_items.conf')
        config.read_dict(item_conf)
        print(config)
        with open('example.cfg', 'w') as configfile:
            config.write(configfile)

class MockSmartHome():
    
    class MockScheduler():
        def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None): 
            print(name) 
            if isinstance(obj.__self__, SmartPlugin):
                name = name +'_'+ obj.__self__.get_instance_name()
            print(name)  
            print( obj) 
            print(obj.__self__.get_instance_name())
    __logs = {}
    __item_dict = {}
    __items = []
    children = []
    _plugins = []
    scheduler = MockScheduler()
    def add_log(self, name, log):
        self.__logs[name] = log
    def now(self):
        import datetime
        return datetime.datetime.now()
    def add_item(self, path, item):
        if path not in self.__items:
            self.__items.append(path)
        self.__item_dict[path] = item
    def return_item(self, string):
        if string in self.__items:
            return self.__item_dict[string]
    def return_items(self):
        for item in self.__items:
            yield self.__item_dict[item]
    def return_plugins(self):
        for plugin in self._plugins:
            yield plugin   
if __name__ == '__main__':
    unittest.main(verbosity=2)

