#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# Copyright 2011-2013   Marcus Popp                        marcus@popp.mx
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
##########################################################################

"""
This library implements logics in SmartHomeNG.

The main class ``Logics`` implements the handling for all logics. This class has a couple
of static methods. These methods implement the API for handling logics from within SmartHomeNG and from plugins.
This API enables plugins to configure new logics or change the configuration of existing plugins.

Each logic is represented by an instance of the class ``Logic``.

The methods of the class Logics implement the API for logics.
They can be used the following way: To call eg. **enable_logic(name)**, use the following syntax:

.. code-block:: python

    from lib.logic import Logics
    logics = Logics.get_instance()

    # to access a method (eg. enable_logic()):
    logics.enable_logic(name)


:Note: Do not use the functions or variables of the main smarthome object any more. They are deprecated. Use the methods of the class **Logics** instead.

:Note: This library is part of the core of SmartHomeNG. Regular plugins should not need to use this API.  It is manily implemented for plugins near to the core like **backend** or **blockly**!

"""
import logging
import os

from collections import OrderedDict

import ast

import lib.config
from lib.shtime import Shtime
import lib.shyaml as shyaml
from lib.utils import Utils

from lib.constants import PLUGIN_PARSE_LOGIC
from lib.constants import (YAML_FILE, CONF_FILE)

from lib.item import Items
from lib.plugin import Plugins
from lib.scheduler import Scheduler

logger = logging.getLogger(__name__)


_logics_instance = None    # Pointer to the initialized instance of the Logics class (for use by static methods)


class Logics():
    """
    This is the main class for the implementation og logics in SmartHomeNG. It implements the API for the
    handling of those logics.
    """

    plugins = None
    scheduler = None

    _config_type = None
    _logicname_prefix = 'logics.'     # prefix for scheduler names



    def __init__(self, smarthome, userlogicconf, envlogicconf):
        logger.info('Start Logics')
        self.shtime = Shtime.get_instance()
        self.items = Items.get_instance()
        self.plugins = Plugins.get_instance()
        self.scheduler = Scheduler.get_instance()

        self._sh = smarthome
        self._userlogicconf = userlogicconf
        self._env_dir = smarthome._env_dir
        self._envlogicconf = envlogicconf
        self._etc_dir = smarthome._etc_dir
        self._logic_dir = smarthome._logic_dir
        self._workers = []
        self._logics = {}
        #self._bytecode = {}
        self.alive = True

        global _logics_instance
        if _logics_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            logger.critical("A second 'logics' object has been created. There should only be ONE instance of class 'Logics'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _logics_instance = self

        self.scheduler = Scheduler.get_instance()

        _config = {}
        self._systemlogics = self._read_logics(envlogicconf, self._env_dir)
        _config.update(self._systemlogics)
        self._userlogics = self._read_logics(userlogicconf, self._logic_dir)
        _config.update(self._userlogics)

        for name in _config:
            self._load_logic(name, _config)


    def _read_logics(self, filename, directory):
        """
        Read the logics configuration file

        :param filename: name of the logics configurtion file
        :param directory: directory where the logics are stored
        """
        logger.debug("Reading Logics from {}.*".format(filename))
        config = lib.config.parse_basename(filename, configtype='logics')
        if config != {}:
            if os.path.isfile(filename+YAML_FILE):
                self._config_type = YAML_FILE
            else:
                self._config_type = CONF_FILE

            for name in config:
                if 'filename' in config[name]:
                    config[name]['pathname'] = directory + config[name]['filename']

        return config


    def _load_logic(self, name, config):
        """
        Load a logic, specified by section name in config
        """
#        logger.debug("_load_logic: Logics.is_logic_loaded(name) = {}.".format( str(Logics.is_logic_loaded(name)) ))
        if self.is_logic_loaded(name):
            return False
        logger.debug("Logic: {}".format(name))
        logic = Logic(self._sh, name, config[name], self)
        if hasattr(logic, '_bytecode'):
            self._logics[name] = logic
            self.scheduler.add(self._logicname_prefix+name, logic, logic._prio, logic._crontab, logic._cycle)
        else:
            return False
        # plugin hook
#        for plugin in self._sh._plugins:
        for plugin in self.plugins.return_plugins():
            if hasattr(plugin, PLUGIN_PARSE_LOGIC):
                update = plugin.parse_logic(logic)
                if update:
                    logic.add_method_trigger(update)
        # item hook
        if hasattr(logic, 'watch_item'):
            if isinstance(logic.watch_item, str):
                logic.watch_item = [logic.watch_item]
            for entry in logic.watch_item:
#                for item in self._sh.match_items(entry):
                for item in self.items.match_items(entry):
                    item.add_logic_trigger(logic)
        return True


    def __iter__(self):
        for logic in self._logics:
            yield logic

    def __getitem__(self, name):
        if name in self._logics:
            return self._logics[name]

    def _delete_logic(self, name):
        if name in self._logics:
            del self._logics[name]


    def return_logics(self):
        """
        Returns a list with the names of all loaded logics

        :return: list of logic names
        :rtype: list
        """
        for logic in self:
            yield logic

    # ------------------------------------------------------------------------------------
    #   Following (static) methods of the class Logics implement the API for logics in shNG
    # ------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Logics class, to be used to access the logics-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.logic import Logics
            logics = Logics.get_instance()

            # to access a method (eg. enable_logic()):
            logics.enable_logic(name)


        :return: logics instance
        :rtype: object or None
        """
        if _logics_instance == None:
            return None
        else:
            return _logics_instance


    def scheduler_add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
        """
        This methods adds a scheduler entry for a logic-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.add method from lib.scheduler
        """
        if name != '':
            name = '.'+name
        name = self._logicname_prefix+self.get_fullname()+name
        self.logger.debug("scheduler_add: name = {}".format(name))
        self.scheduler.add(name, obj, prio, cron, cycle, value, offset, next, from_smartplugin=True)


    def scheduler_change(self, name, **kwargs):
        """
        This methods changes a scheduler entry of a logic-scheduler
        """
        if name != '':
            name = '.'+name
        name = self._logicname_prefix+self.get_fullname()+name
        self.logger.debug("scheduler_change: name = {}".format(name))
        self.scheduler.change(name, kwargs)


    def scheduler_remove(self, name):
        """
        This methods rmoves a scheduler entry of a logic-scheduler

        A plugin identifiction is added to the scheduler name

        The parameters are identical to the scheduler.remove method from lib.scheduler
        """
        if name != '':
            name = '.'+name
        name = self._logicname_prefix+self.get_fullname()+name
        self.logger.debug("scheduler_remove: name = {}".format(name))
        self.scheduler.remove(name, from_smartplugin=False)


    def get_logics_dir(self):
        """
        Returns the path of the dirctory, where the user-logics are stored

        :return: path to logics directory
        :rtype: str
        """
        return self._logic_dir


    def _get_etc_dir(self):
        """
        Returns the path of the dirctory, where the SmartHomeNG configuration (/etc) is stored

        It is not a public method because handling of the configuration file /etc/logic.yaml
        should be done by the api implementation. Only special plugins should access the
        files in /etc themself.

        :return: path to SmartHomeNG configuration directory
        :rtype: str
        """
        return self._etc_dir


    def _get_logic_conf_basename(self):
        """
        Returns the basename of the logic configuration file
        """
#        return self._sh._logic_conf_basename
        return self._userlogicconf

    def reload_logics(self):
        """
        Function to reload all logics

        It generates new bytecode for every logic that is loaded. The configured triggers
        are not loaded from the configuration, so the triggers that where active before the
        reload remain active.
        """
        for logic in self:
            self[logic]._generate_bytecode()


    def is_logic_loaded(self, name):
        """
        Test if a logic is loaded. Given is the name of the section in /etc/logic.yaml

        :param name: logic name (name of the configuration section section)
        :type name: str

        :return: True: Logic is loaded
        :rtype: bool
        """
        if self.return_logic(name) == None:
            return False
        else:
            return True


    def return_logic(self, name):
        """
        Returns (the object of) one loaded logic with given name

        :param name: name of the logic to get
        :type name: str

        :return: object of the logic
        :rtype: object
        """

        return self[name]


    def get_logic_info(self, name, ordered=False):
        """
        Returns a dict with information about the logic

        :param name: name of the logic to get info for
        :type name: str

        :return: information about the logic
        :rtype: dict
        """
        if ordered:
            info = OrderedDict()
        else:
            info = {}
        logic = self.return_logic(name)
        if logic == None:
            return info

        info['name'] = logic._name
        info['enabled'] = logic._enabled

        if self.scheduler.return_next(self._logicname_prefix+logic.name):
            info['next_exec'] = self.scheduler.return_next(self._logicname_prefix+logic.name).strftime('%Y-%m-%d %H:%M:%S%z')

        info['cycle'] = logic._cycle
        info['crontab'] = logic._crontab
        try:
            info['watch_item'] = logic.watch_item
        except:
            info['watch_item'] = ''
        info['userlogic'] = self.is_userlogic(logic.name)
        info['logictype'] = self.return_logictype(logic.name)
        info['filename'] = logic._filename
        info['pathname'] = logic._pathname
        try:
            info['description'] = logic.description
        except:
            info['description'] = ''
        info['visu_access'] = self.visu_access(logic.name)
#        info['watch_item_list'] = []
        return info


    def visu_access(self, name):
        """
        Return if visu may access the logic
        """
        try:
            if self.return_logic(name).visu_acl.lower() in ('true', 'yes', 'rw'):
                return True
        except Exception as e:
            pass
        return False


    def is_logic_enabled(self, name):
        """
        Returns True, if the logic is enabled
        """
        mylogic = self.return_logic(name)
        if mylogic is None:
            logger.warning("logics.is_logic_enabled: No logic found with name {}".format(name))
            return False
        return mylogic.is_enabled()


    def enable_logic(self, name):
        """
        Enable a logic
        """
        mylogic = self.return_logic(name)
        if mylogic is None:
            logger.warning("logics.enable_logic: No logic found with name {}".format(name))
            return False
        mylogic.enable()
#        self.set_config_section_key(name, 'enabled', True)
        self.set_config_section_key(name, 'enabled', None)
        return mylogic._enabled


    def disable_logic(self, name):
        """
        Disable a logic
        """
        mylogic = self.return_logic(name)
        if mylogic is None:
            logger.warning("logics.disable_logic: No logic found with name {}".format(name))
            return False
        mylogic.disable()
        self.set_config_section_key(name, 'enabled', False)
        return mylogic._enabled


    def toggle_logic(self, name):
        """
        Toggle a logic (Invert the enabled/disabled state)
        """
        mylogic = self.return_logic(name)
        if mylogic is None:
            logger.warning("logics.toggle_logic: No logic found with name {}".format(name))
            return False
        if mylogic._enabled:
            mylogic.disable()
        else:
            logger.info("toggle_logic: name = {}".format(name))
            mylogic.enable()
        return mylogic._enabled


    def trigger_logic(self, name, by='unknown', source=None, value=None):
        """
        Trigger a logic
        """
        logger.debug("trigger_logic: Trigger logic = '{}'".format(name))
        if name in self.return_loaded_logics():
            if by == 'unknown':
                by = 'Backend'
            self.scheduler.trigger(self._logicname_prefix+name, by=by, source=source, value=value)
        else:
            logger.warning("trigger_logic: Logic '{}' not found/loaded".format(name))


    def is_userlogic(self, name):
        """
        Returns True if userlogic and False if systemlogic or unknown
        """
        try:
            pathname = str(self.return_logic(name)._pathname)
        except:
            return False
        return os.path.basename(os.path.dirname(pathname)) == 'logics'


    def load_logic(self, name):
        """
        Load a specified logic

        Load a logic as defined in the configuration section. After loading the logic's code,
        the defined schedules and/or triggers are set.

        If a logic is already loaded, it is unloaded and then reloaded.

        :param name: Name of the logic (name of the configuration section)
        :type name: str

        :return: Success
        :rtype: bool
        """
        if self.is_logic_loaded(name):
            self.unload_logic(name)

        _config = self._read_logics(self._get_logic_conf_basename(), self.get_logics_dir())
        if not (name in _config):
            logger.warning("load_logic: FAILED: Logic '{}', _config = {}".format( name, str(_config) ))
            return False

        logger.info("load_logic: Logic '{}', _config = {}".format( name, str(_config) ))
        return self._load_logic(name, _config)


    def unload_logic(self, name):
        """
        Unload a specified logic

        This function unloads a logic. Before unloading, it remove defined schedules and triggers for ``watch_item`` s.

        :param name: Name of the section that defines the logic in the configuration file
        :type name: str
        """
        logger.info("Unload Logic: {}".format(name))
        mylogic = self.return_logic(name)
        if mylogic == None:
            return False

        mylogic._enabled = False
        mylogic._cycle = None
        mylogic._crontab = None

        # Scheduler entfernen
        self.scheduler.remove(self._logicname_prefix+name)

        # watch_items entfernen
        if hasattr(mylogic, 'watch_item'):
            if isinstance(mylogic.watch_item, str):
                mylogic.watch_item = [mylogic.watch_item]
            for entry in mylogic.watch_item:
                # item hook
#                for item in self._sh.match_items(entry):
                for item in self.items.match_items(entry):
                    try:
                        item.remove_logic_trigger(mylogic)
                    except:
                        logger.error("unload_logic: logic = '{}' - cannot remove logic_triggers".format(name))
        mylogic.watch_item = []
        self._delete_logic(name)
        return True


    def get_logiccrontab(self, name):
        """
        Return the crontab string of a logic
        """
        logger.debug("get_logiccrontab: Get crontab of logic = '{}'".format(name))

        mylogic = self.return_logic(name)
        if mylogic is None:
            return None
        else:
            return mylogic._crontab


    def return_logictype(self, name):
        """
        Returns the type of a specified logic (Python, Blockly, None)

        :param name: Name of the logic (name of the configuration section)
        :type name: str

        :return: Logic type ('Python', 'Blockly' or None)
        :rtype: str or None
        """

        logic_type = 'None'
        filename = ''
        if name in self._userlogics:
            try:
                filename = self._userlogics[name].get('filename', '')
            except:
                logger.warning("return_logictype: self._userlogics[name] = '{}'".format(str(self._userlogics[name])))
                logger.warning("return_logictype: self._userlogics = '{}'".format(str(self._userlogics)))
        elif name in self._systemlogics:
            filename = self._systemlogics[name].get('filename', '')
            logic_type = 'Python'
        else:
            logger.info("return_logictype: name {} is not loaded".format(name))
            # load /etc/logic.yaml if logic is not in the loaded logics
            conf_filename = os.path.join(self._get_etc_dir(), 'logic')
            config = shyaml.yaml_load_roundtrip(conf_filename)
            if config is not None:
                if name in config:
                    filename = config[name].get('filename', '')

        if filename != '':
            blocklyname = os.path.splitext(os.path.basename(filename))[0]+'.blockly'
            if os.path.isfile(os.path.join(self.get_logics_dir(), filename)):
                logic_type = 'Python'
                if os.path.isfile(os.path.join(self.get_logics_dir(), blocklyname)):
                    logic_type = 'Blockly'

        logger.debug("return_logictype: name '{}', filename '{}', logic_type '{}'".format(name, filename, logic_type))
        return logic_type


    def return_defined_logics(self, withtype=False):
        """
        Returns the names of defined logics from file /etc/logic.yaml as a list

        If ``withtype`` is specified and set to True, the function returns a dict with names and
        logictypes ('Python', 'Blockly')

        :param withtype: If specified and set to True, the function will additionally return the logic types
        :type withtype: bool

        :return: list of defined logics or dict of defined logics with type
        :rtype: list or dict
        """
        if withtype:
            logic_list = {}
        else:
            logic_list = []

        # load /etc/logic.yaml
        conf_filename = os.path.join(self._get_etc_dir(), 'logic')
        config = shyaml.yaml_load_roundtrip(conf_filename)

        if config is not None:
            for section in config:
                logic_dict = {}
                filename = config[section]['filename']
                blocklyname = os.path.splitext(os.path.basename(filename))[0]+'.xml'
                logic_type = 'None'
                if os.path.isfile(os.path.join(self.get_logics_dir(), filename)):
                    logic_type = 'Python'
                    if os.path.isfile(os.path.join(self.get_logics_dir(), blocklyname)):
                        logic_type = 'Blockly'
                logger.debug("return_defined_logics: section '{}', logic_type '{}'".format(section, logic_type))

                if withtype:
                    logic_list[section] = logic_type
                else:
                    logic_list.append(section)

        return logic_list


    def return_loaded_logics(self):
        """
        Returns a list with the names of all logics that are currently loaded

        :return: list of logic names
        :rtype: list
        """

        logic_list = []
        for logic in self._logics:
            logic_list.append(logic)
        return logic_list


    def return_config_type(self):
        """
        Return the used config type

        After initialization this function returns '.conf', if the used logic configuration file in /etc
        is in the old file format or '.yaml' if the used configuration file is in YAML format.

        To use the following functions for reading and manipulating the logic configuration, the
        configuration file **has to be** in YAML format. Otherwise the functions will not work/return empty results.

        :return: '.yaml', '.conf' or None
        :rtype: str or None
        """
        return self._config_type


    def read_config_section(self, section):
        """
        Read a section from /etc/logic.yaml

        This funtion returns the data from one section of the configuration file as a list of
        configuration entries. A configuration entry is a list with three items:
        - key      configuration key
        - value    configuration value (string or list)
        - comment  comment for the value (string or list)

        :param section: Name of the logic (section)
        :type section: str

        :return: config_list: list of configuration entries. Each entry of this list is a list with three string entries: ['key', 'value', 'comment']
        :rtype: list of lists
        """
        if self.return_config_type() != YAML_FILE:
            logger.error("read_config_section: Editing of configuration only possible with new (yaml) config format")
            return False

        # load /etc/logic.yaml
        conf_filename = os.path.join(self._get_etc_dir(), 'logic')
        _conf = shyaml.yaml_load_roundtrip(conf_filename)

        config_list = []
        if _conf is not None:
            section_dict = _conf.get(section, {})
#            logger.warning("read_config_section: read_config_section('{}') = {}".format(section, str(section_dict) ))
            for key in section_dict:
                if isinstance(section_dict[key], list):
                    value = section_dict[key]
                    comment = []            # 'Comment 6: ' + loaded['a']['c'].ca.items[0][0].value      'Comment 7: ' + loaded['a']['c'].ca.items[1][0].value
                    for i in range(len(value)):
                        if i in section_dict[key].ca.items:
                            try:
                                c = section_dict[key].ca.items[i][0].value
                            except:
                                logger.info("c: {}, Key: {}".format(c, key))
                                c = ''
                            if len(c) > 0 and c[0] == '#':
                                c = c[1:]
                        else:
                            c = ''

                        comment.append(c.strip())
                else:
                    value = section_dict[key]
                    c = ''
                    if key in section_dict.ca.items:
                        try:
                            c = section_dict.ca.items[key][2].value    # if not list: loaded['a'].ca.items['b'][2].value
                        except:
                            logger.info("c2: {}, Key: {}".format(c, key))
                        if len(c) > 0 and c[0] == '#':
                            c = c[1:]
                    comment = c.strip()

#                logger.warning("-> read_config_section: section_dict['{}'] = {}, comment = '{}'".format(key, str(section_dict[key]), comment ))
                config_list.append([key, value, comment])
        return config_list


    def set_config_section_key(self, section, key, value):
        """
        Sets the value of key for a given logic (section)

        :param section: logic to set the key for
        :param key: key for which the value should be set
        :param value: value to set

        """
        # load /etc/logic.yaml
        conf_filename = os.path.join(self._get_etc_dir(), 'logic')
        conf = shyaml.yaml_load_roundtrip(conf_filename)

        logger.info("set_config_section_key: section={}, key={}, value={}".format(section, key, str(value)))
        if value == None:
            if conf[section].get(key, None) != None:
                del conf[section][key]
        else:
            conf[section][key] = value

        # save /etc/logic.yaml
        shyaml.yaml_save_roundtrip(conf_filename, conf, True)

        # activate visu_acl without reloading the logic
        if key == 'visu_acl':
            mylogic = self.return_logic(section)
            if mylogic is not None:
                logger.info(" - key={}, value={}".format(key, value))
#                if value is None:
#                    value = 'false'
                mylogic.visu_acl = str(value)

        return


    def update_config_section(self, active, section, config_list):
        """
        Update file /etc/logic.yaml

        This method creates/updates a section in /etc/logic.yaml. If the section exist, it is cleared
        before new configuration imformation is written to the section

        :param active: True: logic is/should be active, False: Triggers are not written to /etc/logic.yaml
        :param section: name of section to configure in logics configurationfile
        :param config_list: list of configuration entries. Each entry of this list is a list with three string entries: ['key', 'value', 'comment']
        :type active: bool
        :type section: str
        :type config_list: list of lists
        """
        if section == '':
            logger.error("update_config_section: No section name specified. Not updatind logics configuration.")
            return False

        if self.return_config_type() != YAML_FILE:
            logger.error("update_config_section: Editing of configuration only possible with new (yaml) config format")
            return False

        # load /etc/logic.yaml
        conf_filename = os.path.join(self._get_etc_dir(), 'logic')
        conf = shyaml.yaml_load_roundtrip(conf_filename)
        if conf is None:
            conf = shyaml.get_emptynode()

        # empty section
        if conf.get(section, None) == None:
            conf[section] = shyaml.get_emptynode()
        if conf[section].get('filename', None) != None:
            del conf[section]['filename']
        if conf[section].get('cycle', None) != None:
            del conf[section]['cycle']
        if conf[section].get('crontab', None) != None:
            del conf[section]['crontab']
        if conf[section].get('watch_item', None) != None:
            del conf[section]['watch_item']

        # add entries to section
        logger.info("update_config_section: section {}".format(section))
        for c in config_list:
            # process config entries
            key = c[0].strip()
            value = c[1]
            comment = c[2]
            logger.info(" - key={}, value={}, comment={}".format(key, str(value), str(comment)))
            if isinstance(value, str):
                value = value.strip()
                comment = comment.strip()
                if value != '' and value[0] == '[' and value[-1] == ']':
                    # convert a list of triggers to list, if given as a string
                    value = ast.literal_eval(value)
                    if comment != '':
                        comment = ast.literal_eval(comment)
                else:
                    # process single trigger
                    if active or (key == 'filename'):
                        conf[section][key] = value
                        if comment != '':
                            conf[section].yaml_add_eol_comment(comment, key, column=50)
            elif isinstance(value, int) or isinstance(value, bool) or isinstance(value, float):
                comment = comment.strip()
                # process single trigger
                if active:
                    conf[section][key] = value
                    if comment != '':
                        conf[section].yaml_add_eol_comment(comment, key, column=50)
            else:
                logger.warning("update_config_section: unsupported datatype for key '{}'".format(key))

            if active:
                if isinstance(value, list):
                    # process a list of triggers
                    conf[section][key] = shyaml.get_commentedseq(value)
                    listvalue = True
                    for i in range(len(value)):
                        if comment != '':
                            if comment[i] != '':
                                conf[section][key].yaml_add_eol_comment(comment[i], i, column=50)

        if conf[section] == shyaml.get_emptynode():
            conf[section] = None
        shyaml.yaml_save_roundtrip(conf_filename, conf, True)


    def _count_filename_uses(self, conf, filename):
        """
        Count the number of logics (sections) that reference this filename
        """
        count = 0
        for name in conf:
            section = conf.get(name, None)
            fn = section.get('filename', None)
            if fn.lower() == filename.lower():
                count += 1
        return count


    def delete_logic(self, name):
        """
        Deletes a complete logic

        The python code and the section from the configuration file /etc/logic.yaml are
        removed. If it is a blockly logic, the blockly code is removed too.

        If a code file is references by more than the logic that is being deleted, the code
        file will not be deleted. It will only be deleted when the last logic referencing
        this code file is being deleted.

        :param name: name of the logic
        :type name: str

        :return: True, if deletion fas successful
        :rtype: bool
        """
        logger.warning("delete_logic: This routine implements the deletion of logic '{}' (still in testing)".format(name))

        # Logik entladen
        if self.is_logic_loaded(name):
            logger.warning("delete_logic: Logic '{}' unloaded".format(name))
            self.unload_logic(name)

        # load /etc/logic.yaml
        conf_filename = os.path.join(self._get_etc_dir(), 'logic')
        conf = shyaml.yaml_load_roundtrip(conf_filename)

        section = conf.get(name, None)
        if section is None:
            logger.warning("delete_logic: Section '{}' not found in logic configuration.".format(name))
            return False

        # delete code file in ../logics
        filename = section.get('filename', None)
        if filename is None:
            logger.warning("delete_logic: Filename of logic is not defined in section '{}' of logic configuration.".format(name))
        else:
            count = self._count_filename_uses(conf, filename)
            blocklyname = os.path.join(self.get_logics_dir(), os.path.splitext(os.path.basename(filename))[0]+'.blockly')
            filename = os.path.join(self._logic_dir, filename)

            if count < 2:
                # Deletion of the parts of the logic
                if os.path.isfile(blocklyname):
                    os.remove(blocklyname)
                    logger.warning("delete_logic: Blockly-Logic file '{}' deleted".format(blocklyname))
                if os.path.isfile(filename):
                    os.remove(filename)
                    logger.warning("delete_logic: Logic file '{}' deleted".format(filename))
            else:
                logger.warning("delete_logic: Skipped deletion of logic file '{}' because it is used by {} other logic(s)".format(filename, count-1))

        # delete logic configuration from ../etc/logic.yaml
        if conf.get(name, None) is not None:
            del conf[name]
            logger.warning("delete_logic: Section '{}' from configuration deleted".format(name))

        # save /etc/logic.yaml
        shyaml.yaml_save_roundtrip(conf_filename, conf, True)
        return True


# ------------------------------------------------------------------------------------
#   Class Logic
# ------------------------------------------------------------------------------------

class Logic():
    """
    Class for the representation of a loaded logic
    """

    _logicname_prefix = 'logics.'

    def __init__(self, smarthome, name, attributes, logics):
        self.sh = smarthome               # initialize to use 'logic.sh' in logics
        self.logger = logger              # initialize to use 'logic.logger' in logics
        self._name = name
        self.shtime = logics.shtime
        self._logics = logics             # access to the logics api
        self._enabled = True if 'enabled' not in attributes else Utils.to_bool(attributes['enabled'])
        #self.enabled = self._enabled
        self._crontab = None
        self._cycle = None
        self._prio = 3
        #self.last = None
        self._last_run = None
        self._trigger_dict = None
        self._watch_item = []
        self._conf = attributes
        self.scheduler = Logics.get_instance().scheduler
        self.__methods_to_trigger = []
        if attributes != 'None':
            # Fills crontab, cycle and other parameters
            for attribute in attributes:
                if attribute == 'pathname':
                    vars(self)['_pathname'] = attributes[attribute]
                elif attribute == 'filename':
                    vars(self)['_filename'] = attributes[attribute]
                elif attribute == 'watch_item':
                    vars(self)['_watch_item'] = attributes[attribute]
                elif attribute == 'cycle':
                    vars(self)['_cycle'] = attributes[attribute]
                elif attribute == 'crontab':
                    vars(self)['_crontab'] = attributes[attribute]
                elif attribute != 'enabled':
                    vars(self)[attribute] = attributes[attribute]
            self._prio = int(self._prio)
            self._generate_bytecode()
        else:
            logger.error("Logic {} is not configured correctly (configuration has no attibutes)".format(self._name))


    def id(self):
        """
        Returns the id of the loaded logic
        """
        return self._name

    def __str__(self):
        return self._name

    def __call__(self, caller='Logic', source=None, value=None, dest=None, dt=None):
        if self._enabled:
            self.scheduler.trigger(self._logicname_prefix+self._name, self, prio=self._prio, by=caller, source=source, dest=dest, value=value, dt=dt)

    @property
    def name(self):
        """
        Property: name

        :param value: name of the logic
        :type value: str

        :return: name of the item
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):

        self.logger.warning(f"'logic.name' is a readonly property and the value '{value}' can not be assigned to it")
        #if not isinstance(value, str):
        #    self._cast_warning(value)
        #    value = '{}'.format(value)
        #if value == '':
        #    self._item._name = self._item._path
        #else:
        #    self._item._name = value
        return

    def log_readonly_warning(self, prop, value):

        self.logger.warning(f"'logic.{prop}' is a readonly property and the value '{value}' can not be assigned to it")


    @property
    def lname(self):
        """
        Property: lname

        :param value: string with the name of the logic for information in value assignements to items
        :type value: str

        :return: name of the item
        :rtype: str
        """
        return "Logic ' "+self._name+"'"   # string is to be used in item assignements sh.xxx(<value>, logic.lname)

    @lname.setter
    def lname(self, value):

        self.log_readonly_warning('lname', value)
        return


    @property
    def filename(self):
        """
        Property: filename

        :return: filename of the logic
        :rtype: str
        """
        return self._filename

    @filename.setter
    def filename(self, value):

        self.log_readonly_warning('filename', value)
        return


    @property
    def pathname(self):
        """
        Property: pathname

        :return: pathname of the logic
        :rtype: str
        """
        return self._pathname

    @pathname.setter
    def pathname(self, value):

        self.log_readonly_warning('pathname', value)
        return


    @property
    def conf(self):
        """
        Property: conf

        :return: conf of the logic
        :rtype: collections.OrderedDict
        """
        return self._conf

    @conf.setter
    def conf(self, value):

        self.log_readonly_warning('conf', value)
        return


    @property
    def cycle(self):
        """
        Property: cycle

        :return: cycle attribute of the logic
        :rtype: str
        """
        return self._cycle

    @cycle.setter
    def cycle(self, value):

        self.log_readonly_warning('cycle', value)
        return


    @property
    def crontab(self):
        """
        Property: crontab

        :return: crontab attribute of the logic
        :rtype: str
        """
        return self._crontab

    @crontab.setter
    def crontab(self, value):

        self.log_readonly_warning('crontab', value)
        return


    @property
    def prio(self):
        """
        Property: prio

        :return: prio attribute of the logic
        :rtype: str
        """
        return self._prio

    @prio.setter
    def prio(self, value):

        #self.log_readonly_warning('prio', value)
        self._prio = value
        return


    @property
    def trigger_dict(self):
        """
        Property: trigger_dict

        :return: trigger_dict attribute of the logic
        :rtype: dict
        """
        return self._trigger_dict

    @trigger_dict.setter
    def trigger_dict(self, value):

        #self.log_readonly_warning('trigger_dict', value)
        self._trigger_dict = value
        return


    @property
    def watch_item(self):
        """
        Property: watch_item

        :return: watch_item attribute of the logic
        :rtype: list
        """
        return self._watch_item

    @watch_item.setter
    def watch_item(self, value):

        #self.log_readonly_warning('watch_item', value)
        self._watch_item = value
        return


    def enable(self):
        """
        Enables the loaded logic
        """
        self._enabled = True

    def disable(self):
        """
        Disables the loaded logic
        """
        self._enabled = False

    def is_enabled(self):
        """
        Is the loaded logic enabled?
        """
        return self._enabled

    def last_run(self):
        """
        Returns the timestamp of the last run of the logic or None (if the logic wasn't triggered)

        :return: timestamp of last run
        :rtype: datetime timestamp
        """
        return self._last_run

    def set_last_run(self):
        """
        Sets the timestamp of the last run of the logic to now

        This method is called by the scheduler
        """
#        self._last_run = self._sh.now()
        self._last_run = self.shtime.now()


    def trigger(self, by='Logic', source=None, value=None, dest=None, dt=None):
        if self._enabled:
            self.scheduler.trigger(self._logicname_prefix+self._name, self, prio=self._prio, by=by, source=source, dest=dest, value=value, dt=dt)
        else:
            logger.info("trigger: Logic '{}' not triggered because it is disabled".format(self._name))

    def _generate_bytecode(self):
        if hasattr(self, '_pathname'):
            if not os.access(self._pathname, os.R_OK):
                logger.warning("{}: Could not access logic file ({}) => ignoring.".format(self._name, self._pathname))
                return
            try:
                f = open(self._pathname, encoding='UTF-8')
                code = f.read()
                f.close()
                code = code.lstrip('\ufeff')  # remove BOM
                self._bytecode = compile(code, self._pathname, 'exec')
            except Exception as e:
                logger.exception("Exception: {}".format(e))
        else:
            logger.warning("{}: No pathname specified => ignoring.".format(self._name))

    def add_method_trigger(self, method):
        self.__methods_to_trigger.append(method)

    def get_method_triggers(self):
        return self.__methods_to_trigger


