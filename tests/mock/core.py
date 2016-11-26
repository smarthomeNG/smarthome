
import datetime

import lib.item
import lib.plugin
import lib.config
import lib.connection

from lib.model.smartplugin import SmartPlugin

class MockScheduler():

    def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
        print(name)
        if isinstance(obj.__self__, SmartPlugin):
            name = name +'_'+ obj.__self__.get_instance_name()
        print(name)
        print( obj)
        print(obj.__self__.get_instance_name())


class MockSmartHome():

    def __init__(self):
        self.__logs = {}
        self.__item_dict = {}
        self.__items = []
        self.children = []
        self._plugins = []
        self.scheduler = MockScheduler()
        self.connections = lib.connection.Connections()

    def with_plugins_from(self, conf):
        lib.plugin.Plugins._plugins = []
        lib.plugin.Plugins._threads = []
        self._plugins = lib.plugin.Plugins(self, conf)
        return self._plugins

    def with_items_from(self, conf):
        item_conf = lib.config.parse(conf, None)
        for attr, value in item_conf.items():
            if isinstance(value, dict):
                child_path = attr
                try:
                    child = lib.item.Item(self, self, child_path, value)
                except Exception as e:
                    print("Item {}: problem creating: {}".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    self.add_item(child_path, child)
                    self.children.append(child)
        return item_conf

    def add_log(self, name, log):
        self.__logs[name] = log

    def now(self):
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

    def string2bool(self, string):
        if isinstance(string, bool):
            return string
        if string.lower() in ['0', 'false', 'n', 'no', 'off']:
            return False
        if string.lower() in ['1', 'true', 'y', 'yes', 'on']:
            return True
        else:
            return None

