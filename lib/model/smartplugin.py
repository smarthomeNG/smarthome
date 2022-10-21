#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2017-      Martin Sinn                       m.sinn@gmx.de
#  Copyright 2016       Christian Strassburg      c.strassburg(a)gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

#import lib.scheduler

from lib.model.smartobject import SmartObject

from lib.shtime import Shtime
from lib.module import Modules
import lib.shyaml as shyaml
from lib.utils import Utils
from lib.item.items import Items
from lib.item.item import Item
from lib.translation import translate as lib_translate
import logging
import os

shitems = Items.get_instance()


class SmartPlugin(SmartObject, Utils):
    """
    The class SmartPlugin implements the base class of all smart-plugins.
    The implemented methods are described below.

    In addition the methods implemented in lib.utils.Utils are inherited.
    """

    ALLOW_MULTIINSTANCE = None

    __instance = ''       #: Name of this instance of the plugin
    _sh = None            #: Variable containing a pointer to the main SmartHomeNG object; is initialized during loading of the plugin; :Warning: Don't change it
    _configfilename = ''  #: Configfilename of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _configname = ''      #: Configname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _shortname = ''       #: Shortname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    _classname = ''       #: Classname of the plugin; is initialized during loading of the plugin; :Warning: Don't change it
    shtime = None         #: Variable containing a pointer to the SmartHomeNG time handling object; is initialized during loading of the plugin; :Warning: Don't change it

    _stop_on_item_change = True  # Plugin needs to be stopped on/before item changes
                                 # needed by self.remove_item(), don't change unless you know how and why

    _pluginname_prefix = 'plugins.'

    _item_dict = {}         # dict to hold the items assigned to the plugin and their plugin specific information
    _item_lookup_dict = {}  # dict for the reverse lookup from a device_command to an item, contains a list of items for each device_command
    _add_translation = None

    _parameters = {}    # Dict for storing the configuration parameters read from /etc/plugin.yaml

    logger = logging.getLogger(__name__)

    alive = False

    # Initialization of SmartPlugin class called by super().__init__() from the plugin's __init__() method
    def __init__(self, **kwargs):
        pass

    def deinit(self, items=[]):
        """
        If the Plugin needs special code to be executed before it is unloaded, this method
        has to be overwritten with the code needed for de-initialization

        If called without parameters, all registered items are unregistered.
        items is a list of items (or a single Item() object).
        """
        if self.alive:
            self.stop()

        if not items:
            items = self.get_items()
        elif not isinstance(items, list):
            items = [items]

        for item in items:
            if item.path() in self._item_dict:
                self.remove_item(item)

    def add_item(self, item, config_data_dict={}, device_command=None):
        """
        For items that are used/handled by a plugin, this method stores the configuration information
        that is individual for the plugin. The configuration information is/has to be stored in a dictionary

        The configuration information can be retrieved later by a call to the method get_item_configdata(<item_path>)

        If data is beeing received by the plugin, a 'device_command' has to be specified as an optional 3rd parameter.
        This allows a reverse lookup. The method get_itemlist_for_device_command(<device_command>) returns a list
        of items for the items that have defined the <device_command>. In most cases, the list will have only one
        entry, but if multiple items should receive data from the same device (or command), the list can have more than
        one entry.

        :param item: item
        :param config_data_dict: Dictionary with the plugin-specific configuration information for the item
        :param device_command: String identifing the origin (source/kind) of received data
        :type item: Item
        :type config_data_dict: dict
        :type device_command: str

        :return: True, if the information has been added
        :rtype: bool
        """
        if item.path() in self._item_dict:
            self.logging.warning(f"Trying to add an existing item: {item.path()}")
            return False

        self._item_dict[item.path()] = {
            'item': item,
# TODO: besseren Namen für 'has_trigger_method'? zB 'is_updating' oder so...
            'has_trigger_method': False,
            'device_command': device_command,
            'config_data': config_data_dict
        }

        if device_command:
            if device_command not in self._item_lookup_dict:
                self._item_lookup_dict[device_command] = []
            self._item_lookup_dict[device_command].append(item)

        return True

    def remove_item(self, item):
        """
        Remove configuration data for an item (and remove the item from the device_command's list

        :param item: item to remove
        :type item: Item

        :return: True, if the information has been removed
        :rtype: bool
        """
        # check if plugin is running
        if self.alive:
            if self._stop_on_item_change:
                self.stop()
            else:
                return False

        if item.path() not in self._item_dict:
            # There is no information stored for that item
            return False

        # remove data from item_dict early in case of concurrent actions
        data = self._item_dict[item.path()]
        del self._item_dict[item.path()]

        # remove item from self._item_lookup_dict if present
        command = data.get('device_command')
        if command:
            # if a device_command was given for the item, the item is being removed from the list of the device_command
            if item in self._item_lookup_dict[command]:
                self._item_lookup_dict[command].remove(item)

        # unregister item update method
        self.unparse_item(item)

        return True

# TODO: harmonize name with key name self._item_dict['has_trigger_method']
    def register_updating(self, item):
        """
        Mark item in self._item_dict as registered in shng for updating
        (usually done by returning self.update_item from self.parse_item)

        This method is called by the item object itself
        """
        if item.path() not in self._item_dict:
            self.add_item(item)
        self._item_dict[item.path()]['has_trigger_method'] = True

    def get_item_config(self, item):
        """
        Returns the plugin-specific configuration information for the given item

        :param item: item to get config info for
        :type item: class Item

        :return: dict with the configuration information for the given item
        :rtype: dict
        """
        return self._item_dict[item.path()].get('config_data')

# TODO: maybe call this get_item_names to be more intuitive?
#       get_item_paths would be syntactically correct, but weird
    def get_item_path_list(self):
        """
        Return list of stored item paths
        """
        return self._item_dict.keys()

    def get_items(self):
        """
        Return list of stored items
        """
        return [self._item_dict[item_path]['item'] for item_path in self._item_dict]

    def get_trigger_items(self):
        """
        Return list of stored items which were marked by register_updating()
        """
        return [self._item_dict[item_path]['item'] for item_path in self._item_dict if self._item_dict[item_path]['has_trigger_method']]

    def get_items_for_command(self, device_command):
        """
        Returns a list of items that should receive data for the given device_command

        :param device_command: device_command, for which the receiving items should be returned
        :type device_command: str

        :return: List of items
        :rtype: list
        """
        return self._item_lookup_dict.get(device_command, [])

    def unparse_item(self, item):
        """
        Ensure that changes to <item> are no longer propagated to this plugin
        """
        try:
            item._remove_method_trigger(self.update_item)
            return True
        except Exception:
            return False

    def get_configname(self):
        """
        return the name of the plugin instance as defined in plugin.yaml (section name)

        :note: Only available in SmartHomeNG versions **beyond** v1.4

        :return: name of the plugin instance as defined in plugin.yaml
        :rtype: str
        """
        return self._configname


    def _set_configname(self, configname):
        """
        set the name of the plugin instance as defined in plugin.yaml (section name)

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :note: Only available in SmartHomeNG versions **beyond** v1.4

        :param configname: name of the plugin instance as defined in plugin.yaml
        :type configname: str
        """
        self._configname = configname


    def get_shortname(self):
        """
        return the shortname of the plugin (name of it's directory)

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :return: shortname of the plugin
        :rtype: str
        """
        return self._shortname


    def _set_shortname(self, shortname):
        """
        ...

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :param shortname: short name of the plugin (name of it's directory)
        :type shortname: str
        """
        self._shortname = shortname


    def get_instance_name(self):
        """
        Returns the name of this instance of the plugin

        :return: instance name
        :rtype: str
        """
        return self.__instance


    def _set_instance_name(self, instance):
        """
        set instance name of the plugin

        :Note: Usually **you don't need to call this method**, since the instance name is set during startup from the plugin configuration in etc/plugin.yaml

        :param instance: Name of this instance of the plugin
        :type instance: str
        """
        if hasattr(self, 'ALLOW_MULTIINSTANCE') and self.ALLOW_MULTIINSTANCE:
            self.__instance = instance
        elif hasattr(self, 'ALLOW_MULTIINSTANCE') and not self.ALLOW_MULTIINSTANCE:
            self.logger.warning("Plugin '{}': Only multi-instance capable plugins allow setting a name for an instance".format(self.get_shortname()))


    def get_fullname(self):
        """
        return the full name of the plugin (shortname & instancename)

        :note: Only available in SmartHomeNG versions v1.3c and up

        :return: full name of the plugin
        :rtype: str
        """
        if self.get_instance_name() == '':
            return self.get_shortname()
        else:
#            return self.get_instance_name() + '@' + self.get_shortname()
            return  self.get_shortname() + '_' + self.get_instance_name()


    def get_classname(self):
        """
        return the classname of the plugin

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :return: classname of the plugin
        :rtype: str
        """
        return self._classname


    def _set_classname(self, classname):
        """
        ...

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :param classname: name of the plugin's class
        :type classname: str
        """
        self._classname = classname


    def get_version(self, extended=False):
        """
        Return plugin version

        :param extended: If True, returned version string contains (pv) if not the latest version is loaded
        :type extended: bool

        :return: plugin version
        :rtype: str
        """
        if extended and ('_pv_' in self._plugin_dir):
            return self.PLUGIN_VERSION + ' (pv)'
        else:
            return self.PLUGIN_VERSION


    def _set_multi_instance_capable(self, mi):
        """
        Sets information if plugin is capable of multi instance handling (derived from metadate),
        but only, if ALLOW_MULTIINSTANCE is not set in source code

        :param mi: True, if plugin is multiinstance capable
        :type mi: bool
        :return: True, if success or ALLOW_MULTIINSTANCE == mi
        :rtype: bool
        """
        if hasattr(self, 'ALLOW_MULTIINSTANCE') and (self.ALLOW_MULTIINSTANCE != None):
            return (self.ALLOW_MULTIINSTANCE == mi)
        else:
            self.ALLOW_MULTIINSTANCE = mi
        return True


    def is_multi_instance_capable(self):
        """
        Returns information if plugin is capable of multi instance handling

        :return: True: If multiinstance capable
        :rtype: bool
        """
        if self.ALLOW_MULTIINSTANCE:
            return True
        else:
            return False


    def get_plugin_dir(self):
        """
        return the directory where the pluing files are stored in

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :return: name of the directory
        :rtype: str
        """
        return self._plugin_dir


    def _set_plugin_dir(self, dir):
        """
        Set the object's local variable `_plugin_dir` to root directory of the plugins.
        You can reference the main object of SmartHmeNG by using self._plugin_dir.

        :Note: Usually **you don't need to call this method**, since it is called during loading of the plugin by PluginWrapper

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :param dir: name of the directory where the plugin resides in
        :type dir: str
        """
        self._plugin_dir = dir


    def get_info(self):
        """
        Returns a small plugin info like: class, version and instance name

        :return: plugin Info
        :rtype: str
        """
        return "Plugin: '{0}.{1}', Version: '{2}', Instance: '{3}'".format(self.__module__, self.__class__.__name__,  self.get_version(),self.get_instance_name())


    def get_parameter_value(self, parameter_name):
        """
        Returns the configured value for the given parameter name

        If the parameter is not defined, None is returned

        :param parameter_name: Name of the parameter for which the value should be retrieved
        :type parameter_name: str

        :return: Configured value
        :rtype: depends on the type of the parameter definition
        """
        return self._parameters.get(parameter_name, None)


    def get_parameter_value_for_display(self, parameter_name):
        """
        Returns the configured value for the given parameter name

        If the parameter is not defined, None is returned
        If the parameter is marked as 'hide', only '*'s are returned

        :param parameter_name: Name of the parameter for which the value should be retrieved
        :type parameter_name: str

        :return: Configured value
        :rtype: depends on the type of the parameter definition
        """
        param = self._parameters.get(parameter_name, None)
        if param == '' or param is None:
            return ''
        if self._hide_parameters.get(parameter_name, False):
            return '******'
        else:
            return param


#    def has_parameter_value(self, key):
#        """
#        Returns True, if a value is configured for the given parameter name
#
#        :param parameter_name: Name of the parameter for which the value should be retrieved
#        :type parameter_name: str
#
#        :return: True, if a value is configured for the given parameter name
#        :rtype: bool
#        """
#        return (self.get_parameter_value(key) is not None)


    def update_config_section(self, param_dict):
        """
        Update the config section of ../etc/plugin.yaml

        :param param_dict: dict with the parameters that should be updated

        :return:
        """
        param_names = list(self.metadata.parameters.keys())
        self.logger.debug("update_config_section: Beginning to update section '{}' of ../etc/plugin.yaml".format(self._configname))
        self.logger.debug("update_config_section: valid parameter names to update = {}".format(param_names))
        self.logger.info("update_config_section: Config file = '{}', update data = {}".format(self._configfilename, param_dict))

        # read plugin.yaml
        plugin_conf = shyaml.yaml_load_roundtrip(self._configfilename)
        sect = plugin_conf.get(self._configname)
        if sect is None:
            self.logger.error("update_config_section: Config section '{}' not found in ../etc/plugin.yaml".format(self._configname))
            return

        parameters_changed = False
        for param in param_dict:
            if param in param_names:
                if self.metadata.parameters[param]['type'] == 'num':
                    if param_dict[param] == '':
                        this_param = ''
                    else:
                        this_param = float(param_dict[param])
                elif self.metadata.parameters[param]['type'] == 'int':
                    if param_dict[param] == '':
                        this_param = ''
                    else:
                        try:
                            this_param = int(float(param_dict[param]))
                            #this_param = int(param_dict[param])
                        except:
                            self.logger.error(f"update_config_section: Parameter {param} -> Cannot convert '{param_dict[param]}' to type 'int'" )
                            #self.logger.warning("update_config_section: Changing Parameter '{}' -> type = '{}' from '{}' to '{}'".format(param, self.metadata.parameters[param]['type'], sect.get(param, None), this_param))
                else:
                    this_param = param_dict[param]
                self.logger.info("update_config_section: Changing Parameter '{}' -> type = '{}' from '{}' to '{}'".format(param, self.metadata.parameters[param]['type'], sect.get(param, None), this_param))
                if param_dict[param] == '' or param_dict[param] == {} or param_dict[param] == []:
                    try:
                        del sect[param]
                    except KeyError:
                        pass
                else:
                    sect[param] = this_param
                parameters_changed = True
            else:
                self.logger.error("update_config_section: Invalid parameter '{}' specified for update".format(param, param_dict[param]))

        self.logger.debug("update_config_section: Config section content = '{}'".format(sect))
        # write plugin.yaml
        if parameters_changed:
            shyaml.yaml_save_roundtrip(self._configfilename, plugin_conf, True)
        self.logger.debug("update_config_section: Finished updating section '{}' of ../etc/plugin.yaml".format(self._configname))
        return

#---
#plugin_conf = shyaml.yaml_load_roundtrip(config_filename)
#sect = plugin_conf.get(id)
#if sect is None:
#    response = {'result': 'error', 'description': "Configuration section '{}' does not exist".format(id)}
#else:
#    self.logger.debug("update: params = {}".format(params))
#    if params.get('config', {}).get('plugin_enabled', None) == True:
#        del params['config']['plugin_enabled']
#    plugin_conf[id] = params.get('config', {})
#    shyaml.yaml_save_roundtrip(config_filename, plugin_conf, False)
#    response = {'result': 'ok'}


#---


    def get_loginstance(self):
        """
        Returns a prefix for logmessages of multi instance capable plugins.

        The result is an empty string, if the instancename is empty. Otherwise the result
        is a string containing the instance name preseeded by a '@' and traild by ': '.

        This way it is easy to show the instance name in log messages. Just write

        self.logger.info(self.get_loginstance()+"Your text")

        and the logmessage is preseeded by the instance name, if needed.

        :return: instance name for logstring
        :rtype: str
        """
        if self.__instance == '':
            return ''
        else:
            return self.__instance+'@: '


    def __get_iattr(self, attr):
        """
        Returns the given item attribute name for this plugin instance
        (by adding the instance to the attribute name)

        :param attr: name of attribute
        :type attr: str

        :return: attributr
        :rtype: str
        """
        if self.__instance == '':
            return attr
        else:
           return "%s@%s"%(attr, self.__instance)


    def __get_iattr_conf(self, conf, attr):
        """
        returns item attribute name including instance if required and found
        in item configuration

        :param conf: item configuration
        :param attr: attribute name
        :type conf: str
        :type attr: str

        :return: name of item attribute (including instance) or None (if not found)
        :rtype: str
        """
        __attr = self.__get_iattr(attr)
        if __attr in conf:
            return __attr
        elif "%s@*"%attr in conf:
            return "%s@*"%attr
        return None


    def has_iattr(self, conf, attr):
        """
        checks item configuration for an attribute

        :param conf: item configuration
        :param attr: attribute name
        :type conf: str
        :type attr: str

        :return: True, if attribute is in item configuration
        :rtype: Boolean
        """
        __attr = self.__get_iattr_conf(conf, attr)
        return __attr is not None


    def get_iattr_value(self, conf, attr):
        """
        Returns value for an attribute from item config

        :param conf: item configuration
        :param attr: attribute name
        :type conf: str
        :type attr: str

        :return: value of an attribute
        :rtype: str
        """
        __attr = self.__get_iattr_conf(conf, attr)
        return None if __attr is None else conf[__attr]


    def set_attr_value(self, conf, attr, value):
        """
        Set value for an attribute in item configuration

        :param conf: item configuration
        :param attr: attribute name
        :param value: value to set the atteibute to
        :type conf: str
        :type attr: str
        :type value: str
        """
        __attr = self.__get_iattr_conf(conf, attr)
        if __attr is not None:
            conf[self.__get_iattr(attr)] = value


    def __new__(cls, *args, **kargs):
        """
        This method ic called during the creation of an object of the class SmartPlugin.

        It tests, if PLUGIN_VERSION is defined.
        """
        if not hasattr(cls,'PLUGIN_VERSION'):
            raise NotImplementedError("'Plugin' subclasses should have a 'PLUGIN_VERSION' attribute")
        return SmartObject.__new__(cls,*args,**kargs)


    def get_sh(self):
        """
        Return the main object of smarthomeNG (usually refered to as **smarthome** or **sh**)
        You can reference the main object of SmartHomeNG by using self.get_sh() in your plugin

        :note: Only available in SmartHomeNG versions **beyond** v1.3

        :return: the main object of smarthomeNG (usually refered to as **smarthome** or **sh**)
        :rtype: object
        """
        return self._sh


    def _set_sh(self, smarthome):
        """
        Set the object's local variable `_sh` to the main smarthomeNG object.
        You can reference the main object of SmartHomeNG by using self._sh.

        :Note: **Usually you don't need to call this method**, since it is called during loading of the plugin

        :param smarthome: the main object of smarthomeNG
        :type smarthome: object
        """
        self._sh = smarthome

        if self.shtime is None:
            self.shtime = Shtime.get_instance()


    def get_module(self, modulename):
        """
        Test if module http is loaded and if loaded, return a handle to the module
        """
        try:
            mymod = Modules.get_instance().get_module(modulename)
        except:
             mymod = None
        if mymod == None:
            self.logger.error("Module '{}' not loaded".format(modulename))
        else:
            self.logger.info("Using module '{}'".format(str( mymod._shortname ) ) )
        return mymod


    def path_join(self, path, dir):
        """
        Join an existing path and a directory
        """
        return os.path.join( path, dir )


    def parse_logic(self, logic):
        """
        This method is used to parse the configuration of a logic for this plugin. It is
        called for all plugins before the plugins are started (calling all run methods).

        :note: This method should to be overwritten by the plugin implementation.
        """
        pass


    def parse_item(self, item):
        """
        This method is used to parse the configuration of an item for this plugin. It is
        called for all plugins before the plugins are started (calling all run methods).

        :note: This method should to be overwritten by the plugin implementation.
        """
        pass


    def now(self):
        """
        Returns SmartHomeNGs current time (timezone aware)
        """
        return self.shtime.now()

    def scheduler_return_next(self, name):
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        self.logger.debug("scheduler_return_next: name = {}".format(name))
        return self._sh.scheduler.return_next(name, from_smartplugin=True)

    def scheduler_trigger(self, name, obj=None, by=None, source=None, value=None, dest=None, prio=3, dt=None):
        """
        This methods triggers the scheduler entry for a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.trigger method from lib.scheduler
        """
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        if by is None:
            by = 'Plugin {}'.format(name)
        parameters = ', '.join(['{}={!r}'.format(k, v) for k, v in locals().items()
                                if v and not k in ['name', 'self', 'obj']])
        self.logger.debug("scheduler_trigger: name = {}, parameters: {}".format(name, parameters))
        self._sh.scheduler.trigger(name, obj, by, source, value, dest, prio, dt, from_smartplugin=True)

    def scheduler_add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
        """
        This methods adds a scheduler entry for a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.add method from lib.scheduler
        """
        if name != '':
            name = '.'+name
        name = self._pluginname_prefix+self.get_fullname()+name
        parameters = ', '.join(['{}={!r}'.format(k, v) for k, v in locals().items()
                                if v and not k in ['name', 'self', 'obj']])
        self.logger.debug("scheduler_add: name = {}, parameters: {}".format(name, parameters))
        self._sh.scheduler.add(name, obj, prio, cron, cycle, value, offset, next, from_smartplugin=True)


    def scheduler_change(self, name, **kwargs):
        """
        This methods changes a scheduler entry of a plugin-scheduler

        A plugin identification is added to the scheduler name

        The parameters are identical to the scheduler.change method from lib.scheduler
        """
        if name != '':
            name = '.'+name
        name = self._pluginname_prefix+self.get_fullname()+name
        kwargs['from_smartplugin']=True
        parameters = ', '.join(['{}={!r}'.format(k, v) for k, v in kwargs.items()])
        self.logger.debug("scheduler_change: name = {}, parameters: {}".format(name, parameters))
        self._sh.scheduler.change(name, **kwargs)


    def scheduler_remove(self, name):
        """
        This methods removes a scheduler entry of a plugin-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.remove method from lib.scheduler
        """
        if name != '':
            name = '.'+name
        name = self._pluginname_prefix+self.get_fullname()+name
        self.logger.debug("scheduler_remove: name = {}".format(name))
        self._sh.scheduler.remove(name, from_smartplugin=True)


    def scheduler_get(self, name):
        """
        This methods gets a scheduler entry of a plugin-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.get method from lib.scheduler
        """
        if name != '':
            name = '.' + name
        name = self._pluginname_prefix + self.get_fullname() + name
        self.logger.debug("scheduler_get: name = {}".format(name))
        return self._sh.scheduler.get(name, from_smartplugin=True)


    def run(self):
        """
        This method of the plugin is called to start the plugin

        :note: This method needs to be overwritten by the plugin implementation. Otherwise an error will be raised
        """
        raise NotImplementedError("'Plugin' subclasses should have a 'run()' method")


    def stop(self):
        """
        This method of the plugin is called to stop the plugin when SmartHomeNG shuts down

        :note: This method needs to be overwritten by the plugin implementation. Otherwise an error will be raised
        """
        raise NotImplementedError("'Plugin' subclasses should have a 'stop()' method")


    def translate(self, txt, vars=None, block=None):
        """
        Returns translated text
        """
        txt = str(txt)
        if block:
            self.logger.warning("unsuported 3. parameter '{}' used in translation function _( ... )".format(block))

        if self._add_translation is None:
            # test initially, if plugin has additional translations
            translation_fn = os.path.join(self._plugin_dir, 'locale.yaml')
            self._add_translation = os.path.isfile(translation_fn)

        if self._add_translation:
            return lib_translate(txt, vars, additional_translations='plugin/'+self.get_shortname())
        else:
            return lib_translate(txt, vars)


    def init_webinterface(self, WebInterface=None):
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        if WebInterface is None:
            return False

        try:
            # try/except to handle running in a core version that does not support modules
            self.mod_http = Modules.get_instance().get_module('http')
        except:
            self.mod_http = None
        if self.mod_http == None:
            self.logger.warning("Module 'http' not loaded. Not initializing the web interface for the plugin")
            return False

        # set application configuration for cherrypy
        webif_dir = self.path_join(self.get_plugin_dir(), 'webif')
        config = {
            '/': {
                'tools.staticdir.root': webif_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static'
            }
        }

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True

#
# deprecated methods, kept in place in case anybody still uses them
#

    def _get_itemlist(self):
        self._sh._deprecated_warning('SmartPlugin.get_items()')
        return self.get_items()

    def _append_to_itemlist(self, item):
        self._sh._deprecated_warning('SmartPlugin.add_item()')
        self.add_item(item)



try:
    from jinja2 import Environment, FileSystemLoader
except:
    pass
from lib.module import Modules


class SmartPluginWebIf():

    def __init__(self, **kwargs):
        pass

    def init_template_environment(self):
        """
        Initialize the Jinja2 template engine environment

        :return: Jinja2 template engine environment
        :rtype: object
        """
        mytemplates = self.plugin.path_join( self.webif_dir, 'templates' )
        globaltemplates = self.plugin.mod_http.gtemplates_dir
        tplenv = Environment(loader=FileSystemLoader([mytemplates,globaltemplates]))

        tplenv.globals['isfile'] = self.is_staticfile
        tplenv.globals['_'] = self.plugin.translate
        tplenv.globals['len'] = len
        return tplenv


    def is_staticfile(self, path):
        """
        Method tests, if the given pathname points to an existing file in the webif's static
        directory or the global static directory gstatic in the http module

        This method extends the jinja2 template engine

        :param path: path to test
        :param type: str

        :return: True if the file exists
        :rtype: bool
        """
        if path.startswith('/gstatic/'):
#            complete_path = self.plugin.path_join(Modules.get_instance().get_module('http')._gstatic_dir, path[len('/gstatic/'):])
            complete_path = self.plugin.path_join(self.plugin.mod_http.gstatic_dir, path[len('/gstatic/'):])
        else:
            complete_path = self.plugin.path_join(self.webif_dir, path)
        from os.path import isfile as isfile
        result = isfile(complete_path)
        # self.logger.debug("is_staticfile: path={}, complete_path={}, result={}".format(path, complete_path, result))
        return result


    def translate(self, txt):
        """
        Returns translated text

        This method extends the jinja2 template engine
        """
        return self.plugin.translate(txt)
