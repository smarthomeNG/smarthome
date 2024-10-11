
import os

import datetime
import dateutil.tz
import logging

import bin.shngversion

import lib.config

import lib.item
import lib.log
import lib.plugin
from lib.shtime import Shtime
from lib.module import Modules
import lib.utils
from lib.model.smartplugin import SmartPlugin
from lib.constants import (YAML_FILE, CONF_FILE, DEFAULT_FILE, BASES, DIRS)

from tests.common import BASE


#logging.addLevelName(29, 'NOTICE')
#logging.addLevelName(13, 'DBGHIGH')
#logging.addLevelName(12, 'DBGMED')
#logging.addLevelName(11, 'DBGLOW')

logger = logging.getLogger('Mockup')



class MockScheduler():

    def __init__(self):
        # set scheduler_instance to MockScheduler instance
        import lib.scheduler
        lib.scheduler._scheduler_instance = self


    def add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None):
        logger.warning('MockScheduler (add): {}, cron={}, cycle={}, value={}, offset={}'.format( name, str(cron), str(cycle), str(value), str(offset) ))
        try:
            if isinstance(obj.__self__, SmartPlugin):
                name = name +'_'+ obj.__self__.get_instance_name()
        except:
            pass

    def remove(self, name):
        logger.warning('MockScheduler (remove): {}'.format( name ))


class MockSmartHome():

    cwd = os.getcwd()
    print(f"MockSmartHome: cwd={cwd}")
    print(f"MockSmartHome: __file__={__file__}")

    _base_dir = BASE
    base_dir = _base_dir     # for external modules using that var (backend, ...?)
    _default_language = 'de'

    shng_status = {'code': 20, 'text': 'Running'}

    _restart_on_num_workers = 30

    _etc_dir = os.path.join(_base_dir, 'tests', 'resources', 'etc')
    _structs_dir = os.path.join(_base_dir, 'tests', 'resources', 'structs')
    _var_dir = os.path.join(_base_dir, 'var')
    _lib_dir = os.path.join(_base_dir, 'lib')
    _env_dir = os.path.join(_lib_dir, 'env' + os.path.sep)

    _module_conf_basename = os.path.join(_etc_dir,'module')
    _module_conf = ''	# is filled by module.py while reading the configuration file, needed by Backend plugin

    _plugin_conf_basename = os.path.join(_etc_dir,'plugin')
    _plugin_conf = ''	# is filled by plugin.py while reading the configuration file, needed by Backend plugin

    _env_logic_conf_basename = os.path.join( _env_dir ,'logic')
#    _items_dir = os.path.join(_base_dir, 'items'+os.path.sep)
    _logic_conf_basename = os.path.join(_etc_dir, 'logic')
    _logic_dir = os.path.join(_base_dir, 'tests', 'resources', 'logics'+os.path.sep)
    # for now, later remove _logic_dir, see lib/smarthome.py
    _logics_dir = _logic_dir
#    _cache_dir = os.path.join(_var_dir,'cache'+os.path.sep)
    _log_conf_basename = os.path.join(_etc_dir, 'logging')
#    _smarthome_conf_basename = None

    # the APIs available though the smarthome object instance:
    shtime = None

    plugins = None
    items = None
    logics = None
    scheduler = None
    modules = None

    _SmartHome__items = []


    def initialize_vars(self):
        # the APIs available though the smarthome object instance:
        self.shtime = None

        self.items = None
        self.plugins = None
        self.logics = None
        self.scheduler = None

        self.plugin_load_complete = False
        self.item_load_complete = False
        self.plugin_start_complete = False

        self._smarthome_conf_basename = None
        self.__event_listeners = {}
        self.__all_listeners = []
        self.modules = None
        self.__children = []


    def __init__(self):
        #VERSION = '1.8.'
        #VERSION += '2c.man'
        #self.version = VERSION

        self.version = bin.shngversion.shNG_version

        MODE = 'default'
        self._mode = MODE

        self.initialize_vars()

        self.python_bin = os.environ.get('_','')
        self.__logs = {}
#        self.__item_dict = {}
#        self.__items = []
        self.children = []
        self._use_modules = 'True'
        self._moduledict = {}
        # if self.shtime is None:
        #    self.shtime = Shtime.get_instance()
        #    self.shtime = Shtime(self)

        # prevent instantiating a second logs instance
        global logs_instance
        try:
            self.logs = logs_instance
        except NameError:
            logs_instance = self.logs = lib.log.Logs(self)   # initialize object for memory logs and extended log levels for plugins


        #############################################################
        # setup logging
        self.init_logging(self._log_conf_basename, MODE)


        self.scheduler = MockScheduler()

        # make sure not to instantiate a second shtime
        if lib.shtime._shtime_instance is None:
            lib.shtime._shtime_instance = self.shtime = Shtime(self)
        else:
            self.shtime = Shtime.get_instance()
        # Start()
#        self.scheduler = lib.scheduler.Scheduler(self)
        if self.modules is None:
            self.with_modules_from(self._module_conf_basename)
        if self.items is None:
            try:
                lib.item.items._items_instance = None
            except:
                lib.item._items_instance = None
            self.items = lib.item.Items(self)
        if self.plugins is None:
            self.with_plugins_from(self._plugin_conf_basename)


    def get_defaultlanguage(self):
        return self._default_language

    def set_defaultlanguage(self, language):
        self._default_language = language

    def get_basedir(self):
        """
        Function to return the base directory of the running SmartHomeNG installation

        :return: Base directory as an absolute path
        :rtype: str
        """
        return self._base_dir

    def get_confdir(self):
        """
        Function to return the config directory (that contain 'etc', 'logics' and 'items' subdirectories)

        :return: Config directory as an absolute path
        :rtype: str
        """
        return self._extern_conf_dir

    def get_etcdir(self):
        """
        Function to return the etc config directory

        :return: Config directory as an absolute path
        :rtype: str
        """
        return self._etc_dir

    def get_structsdir(self):
        """
        Function to return the etc config directory

        :return: Config directory as an absolute path
        :rtype: str
        """
        return self._structs_dir


    def get_logicsdir(self) -> str:
        """
        Function to return the logics config directory

        :return: Config directory as an absolute path
        """
        return self._logic_dir


    def get_functionsdir(self) -> str:
        """
        Function to return the userfunctions config directory

        :return: Config directory as an absolute path
        """
        return self._functions_dir

    def get_vardir(self):
        """
        Function to return the var directory used by SmartHomeNG

        :return: var directory as an absolute path
        :rtype: str
        """
        return self._var_dir

    def getBaseDir(self):
        """
        Function to return the base directory of the running SmartHomeNG installation

        **getBaseDir()** is deprecated. Use method get_basedir() instead.

        :return: Base directory as an absolute path
        :rtype: str
        """
        return self._base_dir

    def get_config_dir(self, config):
        """
        Function to return a config dir used by SmartHomeNG
        replace / prevent a plethora of get_<foo>dir() functions

        Returns '' for invalid config strings.

        :return: directory as an absolute path
        :rtype: str
        """
        # method would work fine without this check, but...
        # make sure we don't allow "any" function call here
        if config not in DIRS:
            return ''

        if hasattr(self, f'get_{config}dir'):
            return getattr(self, f'get_{config}dir')()
        elif hasattr(self, f'_{config}_dir'):
            return getattr(self, f'_{config}_dir')
        
        return ''


    def get_config_file(self, config, extension=YAML_FILE):
        """
        Function to return a config file used by SmartHomeNG

        Returns '' for invalid config strings.

        :return: file name as an absolute path
        :rtype: str
        """
        # method would work fine without this check, but...
        # make sure we don't allow "any" function call here
        if config not in BASES:
            return ''

        return os.path.join(self.get_etcdir(), config + extension)

    def trigger(self, name, obj=None, by='Logic', source=None, value=None, dest=None, prio=3, dt=None):
        logger.warning('MockSmartHome (trigger): {}'.format(str(obj)))

    def with_plugins_from(self, conf):
        lib.plugin._plugins_instance = None
        lib.plugin.Plugins._plugins = []
        lib.plugin.Plugins._threads = []
        self.plugins = lib.plugin.Plugins(self, conf)
        return self.plugins

    def with_modules_from(self, conf):
        lib.module._modules_instance = None
        lib.module.Modules._modules = []
        lib.module.Modules._moduledict = {}
        self.modules = lib.module.Modules(self, conf)
        return self.modules

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


    def init_logging(self, conf_basename='', MODE='default'):
        """
        This function initiates the logging for SmartHomeNG.
        """
        if conf_basename == '':
            conf_basename = self._log_conf_basename
        #conf_dict = lib.shyaml.yaml_load(conf_basename + YAML_FILE, True)

        if not self.logs.configure_logging():
            conf_basename = self._log_conf_basename + YAML_FILE + '.default'
            print(f"       Trying default logging configuration from:")
            print(f"       {conf_basename}")
            print()
            #conf_dict = lib.shyaml.yaml_load(conf_basename + YAML_FILE + '.default', True)
            if not self.logs.configure_logging('logging.yaml.default'):
                print("ABORTING")
                print()
                exit(1)
            print("Starting with default logging configuration")

        if MODE == 'interactive':  # remove default stream handler
            logging.getLogger().disabled = True
        elif MODE == 'verbose':
            logging.getLogger().setLevel(logging.INFO)
        elif MODE == 'debug':
            logging.getLogger().setLevel(logging.DEBUG)
        elif MODE == 'quiet':
            logging.getLogger().setLevel(logging.WARNING)
        return



    #################################################################
    # Event Methods
    #################################################################
    def add_event_listener(self, events, method):
        """
        This Function adds listeners for a list of events. This function is called from
        plugins interfacing with visus (e.g. visu_websocket)

        :param events: List of events to add listeners for
        :param method: Method used by the visu-interface
        :type events: list
        :type method: object
        """

        for event in events:
            if event in self.__event_listeners:
                self.__event_listeners[event].append(method)
            else:
                self.__event_listeners[event] = [method]
        self.__all_listeners.append(method)


    def return_event_listeners(self, event='all'):
        """
        This function returns the listeners for a specified event.

        :param event: Name of the event or 'all' to return all listeners
        :type event: str

        :return: List of listeners
        :rtype: list
        """

        if event == 'all':
            return self.__all_listeners
        elif event in self.__event_listeners:
            return self.__event_listeners[event]
        else:
            return []



    # ------------------------------------------------------------
    #  Deprecated methods
    # ------------------------------------------------------------

    def now(self):
        return self.shtime.now()

    def tzinfo(self):
        return self.shtime.tzinfo()

    def add_item(self, path, item):
        return self.items.add_item(path, item)

    def return_item(self, string):
        return self.items.return_item(string)

    def return_items(self):
        return self.items.return_items()

    def return_plugins(self):
        #return self.plugins.get_module(name) ???
        return self.plugins

    def return_modules(self):
        return self.modules.return_modules()

    def get_module(self, name):
        return self.modules.get_module(name)



    def string2bool(self, string):
#        if isinstance(string, bool):
#            return string
#        if string.lower() in ['0', 'false', 'n', 'no', 'off']:
#            return False
#        if string.lower() in ['1', 'true', 'y', 'yes', 'on']:
#            return True
#        else:
#            return None
        try:
            return lib.utils.Utils.to_bool(string)
        except Exception as e:
            return None


    def return_none(self):
        return None

