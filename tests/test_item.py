
import common
import unittest
import lib.plugin
import lib.item
from lib.model.smartplugin import SmartPlugin
import threading

class TestConfig(unittest.TestCase):
    def props(self,cls):   
        return [i for i in cls.__dict__.keys() if i[:1] != '_']
        
    def test_item_relative(self):
        sh=MockSmartHome()
        
        #load items
        item_conf = None
        item_conf = lib.config.parse("resources/item_items.conf", item_conf)
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
       
        if 0: self.dump_items(sh)

        print()
        it = sh.return_item("item_tree.grandparent.parent.my_item")
        self.assertIsNotNone(it)
        self.assertEqual(it._type, 'bool')
        it = sh.return_item("item_tree.grandparent.parent.my_item.child")
        self.assertIsNotNone(it)
        self.assertEqual(it._type, 'foo')

        print('== eval_trigger Tests:')
        # Attribute with relative references
        it = sh.return_item("item_tree.grandparent.parent.my_item")
        self.assertEqual(it.get_absolutepath('.', 'eval_trigger'), 'item_tree.grandparent.parent.my_item')
        self.assertEqual(it.get_absolutepath('.child', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child')
        self.assertEqual(it.get_absolutepath('.child.grandchild', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child.grandchild')
        self.assertEqual(it.get_absolutepath('..', 'eval_trigger'), 'item_tree.grandparent.parent')
        self.assertEqual(it.get_absolutepath('...', 'eval_trigger'), 'item_tree.grandparent')
        self.assertEqual(it.get_absolutepath('....', 'eval_trigger'), 'item_tree')
        self.assertEqual(it.get_absolutepath('.....', 'eval_trigger'), '')
        self.assertEqual(it.get_absolutepath('......', 'eval_trigger'), '')
        self.assertEqual(it.get_absolutepath('..sister', 'eval_trigger'), 'item_tree.grandparent.parent.sister')

        # Attribute w/o relative references
        print()
        self.assertEqual(it.get_absolutepath('item_tree.grandparent.parent.my_item', 'eval_trigger'), 'item_tree.grandparent.parent.my_item')
        self.assertEqual(it.get_absolutepath('abc', 'eval_trigger'), 'abc')

        print('== eval Tests:')
        it = sh.return_item("item_tree.grandparent.parent.my_item")
        print(it.get_stringwithabsolutepathes('sh..child()', 'sh.', '(', 'eval'))
        self.assertEqual(it.get_stringwithabsolutepathes('sh..child()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.child()')
        self.assertEqual(it.get_stringwithabsolutepathes('5*sh..child()', 'sh.', '(', 'eval'), '5*sh.item_tree.grandparent.parent.my_item.child()')
        self.assertEqual(it.get_stringwithabsolutepathes('5 * sh..child() + 4', 'sh.', '(', 'eval'), '5 * sh.item_tree.grandparent.parent.my_item.child() + 4')
        print()

        print('== Plugin Tests:')
        # Attribute with relative references
        it = sh.return_item("item_tree.grandparent.parent.my_item")
        it.expand_relativepathes('sv_widget', "'", "'")
        self.assertEqual(it.conf['sv_widget'], "{{ basic.switch('id_schreibtischleuchte', 'item_tree.grandparent.parent.my_item.onoff') }}")

        # Attribute w/o relative references
        it = sh.return_item("item_tree.grandparent.parent.my_item.child")
        orig = it.conf['sv_widget']
        it.expand_relativepathes('sv_widget', "'", "'")
        self.assertEqual(it.conf['sv_widget'], orig)
        self.assertEqual(it.conf['sv_widget'], "{{ basic.switch('id_schreibtischleuchte', 'item_tree.grandparent.parent.my_item.child.onoff') }}")
        print()


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

