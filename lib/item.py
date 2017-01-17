#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Christian Straßburg           c.strassburg@gmx.de
# Copyright 2016-2017   Martin Sinn                         m.sinn@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import datetime
import logging
import os
import pickle
import threading
import math
import json

from lib.constants import (ITEM_DEFAULTS, FOO, KEY_ENFORCE_UPDATES, KEY_CACHE, KEY_CYCLE, KEY_CRONTAB, KEY_EVAL,
                           KEY_EVAL_TRIGGER, KEY_NAME,KEY_TYPE, KEY_VALUE, PLUGIN_PARSE_ITEM,
                           KEY_AUTOTIMER,KEY_THRESHOLD,
                           KEY_ATTRIB_COMPAT, ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST)


ATTRIB_COMPAT_DEFAULT_FALLBACK = ATTRIB_COMPAT_V12
ATTRIB_COMPAT_DEFAULT = ''


logger = logging.getLogger(__name__)



#####################################################################
# Cast Methods
#####################################################################

def _cast_str(value):
    if isinstance(value, str):
        return value
    else:
        raise ValueError


def _cast_list(value):
    if isinstance(value, list):
        return value
    else:
        raise ValueError


def _cast_dict(value):
    if isinstance(value, dict):
        return value
    else:
        raise ValueError


def _cast_foo(value):
    return value


# TODO: Candidate for Utils.to_bool()
# write testcase and replace
# -> should it be possible to cast 0 -> False and non-0 to True?
def _cast_bool(value):
    if type(value) in [bool, int, float]:
        if value in [False, 0]:
            return False
        elif value in [True, 1]:
            return True
        else:
            raise ValueError
    elif type(value) in [str, str]:
        if value.lower() in ['0', 'false', 'no', 'off', '']:
            return False
        elif value.lower() in ['1', 'true', 'yes', 'on']:
            return True
        else:
            raise ValueError
    else:
        raise TypeError


def _cast_scene(value):
    return int(value)


def _cast_num(value):
    """
    cast a passed value to int or float

    :param value: numeric value to be casted, passed as str, float or int
    :return: numeric value, passed as int or float
    """
    if value == '':
        return 0
    if isinstance(value, float):
        return value
    try:
        return int(value)
    except:
        pass
    try:
        return float(value)
    except:
        pass
    raise ValueError


#####################################################################
# Methods for handling of duration_value strings
#####################################################################

def _split_duration_value_string(value): 
    """
    splits a duration value string into its thre components
    
    components are:
    - time
    - value
    - compat

    :param value: raw attribute string containing duration, value (and compatibility)
    :return: three strings, representing time, value and compatibility attribute
    """
    time, __, value = value.partition('=')
    value, __, compat = value.partition('=')
    time = time.strip()
    value = value.strip()
    # remove quotes, if present
    if value != '' and ((value[0] == "'" and value[-1] == "'") or (value[0] == '"' and value[-1] == '"')):
        value = value[1:-1]
    compat = compat.strip().lower()
    if compat == '':
        compat = ATTRIB_COMPAT_DEFAULT
    return (time, value, compat)


def _join_duration_value_string(time, value, compat=''): 
    """
    joins a duration value string from its thre components
    
    components are:
    - time
    - value
    - compat

    :param time: time (duration) parrt for the duration_value_string
    :param value: value (duration) parrt for the duration_value_string
    """
    result = str(time)
    if value != '' or compat != '':
        result = result + ' ='
        if value != '':
            result = result + ' ' + value
        if compat != '':
           result = result + ' = ' + compat
    return result
    
    
#####################################################################
# Cache Methods
#####################################################################
def _cache_read(filename, tz):
    ts = os.path.getmtime(filename)
    dt = datetime.datetime.fromtimestamp(ts, tz)
    value = None
    with open(filename, 'rb') as f:
        value = pickle.load(f)
    return (dt, value)


def _cache_write(filename, value):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(value, f)
    except IOError:
        logger.warning("Could not write to {}".format(filename))


#####################################################################
# Fade Method
#####################################################################
def _fadejob(item, dest, step, delta):
    if item._fading:
        return
    else:
        item._fading = True
    if item._value < dest:
        while (item._value + step) < dest and item._fading:
            item(item._value + step, 'fader')
            item._lock.acquire()
            item._lock.wait(delta)
            item._lock.release()
    else:
        while (item._value - step) > dest and item._fading:
            item(item._value - step, 'fader')
            item._lock.acquire()
            item._lock.wait(delta)
            item._lock.release()
    if item._fading:
        item._fading = False
        item(dest, 'Fader')


#####################################################################
# Item Class
#####################################################################


class Item():

    def __init__(self, smarthome, parent, path, config):
        self._autotimer = False
        self._cache = False
        self.cast = _cast_bool
        self.__changed_by = 'Init:None'
        self.__children = []
        self.conf = {}
        self._crontab = None
        self._cycle = None
        self._enforce_updates = False
        self._eval = None
        self._eval_trigger = False
        self._fading = False
        self._items_to_trigger = []
        self.__last_change = smarthome.now()
        self.__last_update = smarthome.now()
        self._lock = threading.Condition()
        self.__logics_to_trigger = []
        self._name = path
        self.__prev_change = smarthome.now()
        self.__methods_to_trigger = []
        self.__parent = parent
        self._path = path
        self._sh = smarthome
        self._threshold = False
        self._type = None
        self._value = None
        if hasattr(smarthome, '_item_change_log'):
            self._change_logger = logger.info
        else:
            self._change_logger = logger.debug
        #############################################################
        # Initialize attribute assignment compatibility
        #############################################################
        global ATTRIB_COMPAT_DEFAULT
        if ATTRIB_COMPAT_DEFAULT == '':
            if hasattr(smarthome, '_'+KEY_ATTRIB_COMPAT):
                config_attrib = getattr(smarthome,'_'+KEY_ATTRIB_COMPAT)
                if str(config_attrib) in [ATTRIB_COMPAT_V12, ATTRIB_COMPAT_LATEST]:
                    logger.info("Global configuration: '{}' = '{}'.".format(KEY_ATTRIB_COMPAT, str(config_attrib)))
                    ATTRIB_COMPAT_DEFAULT = config_attrib
                else:
                    logger.warning("Global configuration: '{}' has invalid value '{}'.".format(KEY_ATTRIB_COMPAT, str(config_attrib)))
            if ATTRIB_COMPAT_DEFAULT == '':
                ATTRIB_COMPAT_DEFAULT = ATTRIB_COMPAT_DEFAULT_FALLBACK
        #############################################################
        # Item Attributes
        #############################################################
        for attr, value in config.items():
            if not isinstance(value, dict):
                if attr in [KEY_CYCLE, KEY_NAME, KEY_TYPE, KEY_VALUE]:
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_EVAL]:
                    value = self.get_stringwithabsolutepathes(value, 'sh.', '(', KEY_EVAL)
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_CACHE, KEY_ENFORCE_UPDATES]:  # cast to bool
                    try:
                        setattr(self, '_' + attr, _cast_bool(value))
                    except:
                        logger.warning("Item '{0}': problem parsing '{1}'.".format(self._path, attr))
                        continue
                elif attr in [KEY_CRONTAB]:  # cast to list
                    if isinstance(value, str):
                        value = [value, ]
                    setattr(self, '_' + attr, value)
                elif attr in [KEY_EVAL_TRIGGER]:  # cast to list
                    if isinstance(value, str):
                        value = [value, ]
                    expandedvalue = []
                    for path in value:
                        expandedvalue.append(self.get_absolutepath(path, KEY_EVAL_TRIGGER))
                    setattr(self, '_' + attr, expandedvalue)
                elif attr == KEY_AUTOTIMER:
                    time, value, compat = _split_duration_value_string(value)
                    timeitem = None
                    valueitem = None
                    if time.lower().startswith('sh.') and time.endswith('()'):
                        timeitem = self.get_absolutepath(time[3:-2], KEY_AUTOTIMER)
                        time = 0
                    if value.lower().startswith('sh.') and value.endswith('()'):
                        valueitem = self.get_absolutepath(value[3:-2], KEY_AUTOTIMER)
                        value = ''
                    value = self._castvalue_to_itemtype(value, compat)
                    self._autotimer = [ (self._cast_duration(time), value), compat, timeitem, valueitem]
                elif attr == KEY_THRESHOLD:
                    low, __, high = value.rpartition(':')
                    if not low:
                        low = high
                    self._threshold = True
                    self.__th_crossed = False
                    self.__th_low = float(low.strip())
                    self.__th_high = float(high.strip())
                    logger.debug("Item {}: set threshold => low: {} high: {}".format(self._path, self.__th_low, self.__th_high))
                else:
                    self.conf[attr] = value
        #############################################################
        # Child Items
        #############################################################
        for attr, value in config.items():
            if isinstance(value, dict):
                child_path = self._path + '.' + attr
                try:
                    child = Item(smarthome, self, child_path, value)
                except Exception as e:
                    logger.exception("Item {}: problem creating: {}".format(child_path, e))
                else:
                    vars(self)[attr] = child
                    smarthome.add_item(child_path, child)
                    self.__children.append(child)
        #############################################################
        # Cache
        #############################################################
        if self._cache:
            self._cache = self._sh._cache_dir + self._path
            try:
                self.__last_change, self._value = _cache_read(self._cache, self._sh._tzinfo)
                self.__last_update = self.__last_change
                self.__changed_by = 'Cache:None'
            except Exception as e:
                logger.warning("Item {}: problem reading cache: {}".format(self._path, e))
        #############################################################
        # Type
        #############################################################
        #__defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
        if self._type is None:
#            logger.debug("Item {}: no type specified.".format(self._path))
#            return
            self._type = FOO  # MSinn
        if self._type not in ITEM_DEFAULTS:
            logger.error("Item {}: type '{}' unknown. Please use one of: {}.".format(self._path, self._type, ', '.join(list(ITEM_DEFAULTS.keys()))))
            raise AttributeError
        self.cast = globals()['_cast_' + self._type]
        #############################################################
        # Value
        #############################################################
        if self._value is None:
            self._value = ITEM_DEFAULTS[self._type]
        try:
            self._value = self.cast(self._value)
        except:
            logger.error("Item {}: value {} does not match type {}.".format(self._path, self._value, self._type))
            raise
        self.__prev_value = self._value
        #############################################################
        # Cache write/init
        #############################################################
        if self._cache:
            if not os.path.isfile(self._cache):
                _cache_write(self._cache, self._value)
                logger.warning("Item {}: Created cache for item: {}".format(self._cache, self._cache))
        #############################################################
        # Crontab/Cycle
        #############################################################
        if self._crontab is not None or self._cycle is not None:
            cycle = self._cycle
            if cycle is not None:
                cycle = self._build_cycledict(cycle)
            self._sh.scheduler.add(self._path, self, cron=self._crontab, cycle=cycle)
        #############################################################
        # Plugins
        #############################################################
        for plugin in self._sh.return_plugins():
            if hasattr(plugin, PLUGIN_PARSE_ITEM):
                update = plugin.parse_item(self)
                if update:
                    self.add_method_trigger(update)


    def _castvalue_to_itemtype(self, value, compat):
        """
        casts the value to the type of the item, if backward compatibility 
        to version 1.2 (ATTRIB_COMPAT_V12) is not enabled
        
        If backward compatibility is enabled, the value is returned unchanged
        
        :param value: value to be casted
        :param compat: compatibility attribute
        :return: return casted valu3
        """
        # casting of value, if compat = latest
        if compat == ATTRIB_COMPAT_LATEST:
            if self._type != None:
                mycast = globals()['_cast_' + self._type]
                try:
                    value = mycast(value)
                except:
                    logger.warning("Item {}: Unable to cast '{}' to {}".format(self._path, str(value), self._type))
                    if isinstance(value, list):
                        value = []
                    elif isinstance(value, dict):
                        value = {}
                    else:
                        value = mycast('')
            else:
                logger.warning("Item {}: Unable to cast '{}' to {}".format(self._path, str(value), self._type))
        return value
        

    def _cast_duration(self, time): 
        """
        casts a time valuestring (e.g. '5m') to an duration integer
        used for autotimer, timer, cycle
    
        supported formats for time parameter:
        - seconds as integer (45)
        - seconds as a string ('45')
        - seconds as a string, traild by 's' ('45s')
        - minutes as a string, traild by 'm' ('5m'), is converted to seconds (300)
        
        :param time: string containing the duration
        :param itempath: item path as aditional information for logging
        :return: number of seconds as an integer
        """
        if isinstance(time, str):
            try:
                time = time.strip()
                if time.endswith('m'):
                    time = int(time.strip('m')) * 60
                elif time.endswith('s'):
                    time = int(time.strip('s'))
                else:
                    time = int(time)
            except Exception as e:
                logger.warning("Item {}: _cast_duration ({}) problem: {}".format(self._path, time, e))
                time = False
        elif isinstance(time, int):
            time = int(time)
        else:
            logger.warning("Item {}: _cast_duration ({}) problem: unable to convert to int".format(self._path, time))
            time = False
        return(time)
    

    def _build_cycledict(self, value):
        """
        builds a dict for a cycle parameter from a duration_value_string
        
        This dict is to be passed to the scheduler to circumvemt the parameter
        parsing within the scheduler, which can't to casting

        :param value: raw attribute string containing duration, value (and compatibility)
        :return: cycle-dict for a call to scheduler.add 
        """
        time, value, compat = _split_duration_value_string(value)
        time = self._cast_duration(time)
        value = self._castvalue_to_itemtype(value, compat)
        cycle = {time: value}
        return cycle
    

    def expand_relativepathes(self, attr, begintag, endtag):
        """
        converts a configuration attribute containing relative item pathes
        to absolute pathes
        
        The begintag and the endtag remain in the result string!

        :param attr: Name of the attribute
        :param begintag: string that signals the beginning of a relative path is following
        :param endtag: string that signals the end of a relative path
        """
        if attr in self.conf:
            if (begintag != '') and (endtag != ''):
                self.conf[attr] = self.get_stringwithabsolutepathes(self.conf[attr], begintag, endtag, attr)
            elif (begintag == '') and (endtag == ''):
                self.conf[attr] = self.get_absolutepath(self.conf[attr], attr)
        return
        

    def get_stringwithabsolutepathes(self, evalstr, begintag, endtag, attribute=''):
        """
        converts a string containing relative item pathes
        to a string with absolute item pathes
        
        The begintag and the endtag remain in the result string!

        :param evalstr: string with the statement that may contain relative item pathes
        :param begintag: string that signals the beginning of a relative path is following
        :param endtag: string that signals the end of a relative path
        :param attribute: string with the name of the item's attribute, which contains the relative path
        :return: string with the statement containing absolute item pathes
        """
        if evalstr.find(begintag+'.') == -1:
            return evalstr

#        logger.warning("{}.get_stringwithabsolutepathes('{}'): begintag = '{}', endtag = '{}'".format(self._path, evalstr, begintag, endtag))
        pref = ''
        rest = evalstr
        while (rest.find(begintag+'.') != -1):
            pref += rest[:rest.find(begintag+'.')+len(begintag)]
            rest = rest[rest.find(begintag+'.')+len(begintag):]
            rel = rest[:rest.find(endtag)]
            rest = rest[rest.find(endtag):]
            pref += self.get_absolutepath(rel, attribute)
            
        pref += rest
#        logger.warning("{}.get_stringwithabsolutepathes(): result = '{}'".format(self._path, pref))
        return pref


    def get_absolutepath(self, relativepath, attribute=''):
        """
        Builds an absolute item path relative to the current item

        :param relativepath: string with the relative item path
        :param attribute: string with the name of the item's attribute, which contains the relative path
        :return: string with the absolute item path
        """
        if (len(relativepath) == 0) or ((len(relativepath) > 0)  and (relativepath[0] != '.')):
            return relativepath
        relpath = relativepath.rstrip()
        rootpath = self._path

        while (len(relpath) > 0)  and (relpath[0] == '.'):
            relpath = relpath[1:]
            if (len(relpath) > 0)  and (relpath[0] == '.'):
                if rootpath.rfind('.') == -1:
                    if rootpath == '':
                        relpath = ''
                        logger.error("{}.get_absolutepath(): Relative path trying to access above root level on attribute '{}'".format(self._path, attribute))
                    else:
                        rootpath = ''
                else:
                    rootpath = rootpath[:rootpath.rfind('.')]

        if relpath != '':
            if rootpath != '':
                rootpath += '.' + relpath
            else:
                rootpath = relpath
        logger.info("{}.get_absolutepath('{}'): Result = '{}' (for attribute '{}')".format(self._path, relativepath, rootpath, attribute))
        if rootpath[-5:] == '.self':
            rootpath = rootpath.replace('.self', '')
        rootpath = rootpath.replace('.self.', '.')
        return rootpath
    

    def __call__(self, value=None, caller='Logic', source=None, dest=None):
        if value is None or self._type is None:
            return self._value
        if self._eval:
            args = {'value': value, 'caller': caller, 'source': source, 'dest': dest}
            self._sh.trigger(name=self._path + '-eval', obj=self.__run_eval, value=args, by=caller, source=source, dest=dest)
        else:
            self.__update(value, caller, source, dest)

    def __iter__(self):
        for child in self.__children:
            yield child

    def __setitem__(self, item, value):
        vars(self)[item] = value

    def __getitem__(self, item):
        return vars(self)[item]

    def __bool__(self):
        return bool(self._value)

    def __str__(self):
        return self._name

    def __repr__(self):
        return "Item: {}".format(self._path)

    def _init_prerun(self):
        if self._eval_trigger:
            _items = []
            for trigger in self._eval_trigger:
                _items.extend(self._sh.match_items(trigger))
            for item in _items:
                if item != self:  # prevent loop
                        item._items_to_trigger.append(self)
            if self._eval:
                items = ['sh.' + x.id() + '()' for x in _items]
                if self._eval == 'and':
                    self._eval = ' and '.join(items)
                elif self._eval == 'or':
                    self._eval = ' or '.join(items)
                elif self._eval == 'sum':
                    self._eval = ' + '.join(items)
                elif self._eval == 'avg':
                    self._eval = '({0})/{1}'.format(' + '.join(items), len(items))
                elif self._eval == 'max':
                    self._eval = 'max({0})'.format(','.join(items))
                elif self._eval == 'min':
                    self._eval = 'min({0})'.format(','.join(items))

    def _init_run(self):
        if self._eval_trigger:
            if self._eval:
                self._sh.trigger(name=self._path, obj=self.__run_eval, by='Init', value={'value': self._value, 'caller': 'Init'})

    def __run_eval(self, value=None, caller='Eval', source=None, dest=None):
        if self._eval:
            sh = self._sh  # noqa
            try:
                value = eval(self._eval)
            except Exception as e:
                logger.warning("Item {}: problem evaluating {}: {}".format(self._path, self._eval, e))
            else:
                if value is None:
                    logger.info("Item {}: evaluating {} returns None".format(self._path, self._eval))
                else:
                    self.__update(value, caller, source, dest)

    def __trigger_logics(self):
        for logic in self.__logics_to_trigger:
            logic.trigger('Item', self._path, self._value)

    def __update(self, value, caller='Logic', source=None, dest=None):
        try:
            value = self.cast(value)
        except:
            try:
                logger.warning("Item {}: value {} does not match type {}. Via {} {}".format(self._path, value, self._type, caller, source))
            except:
                pass
            return
        self._lock.acquire()
        _changed = False
        if value != self._value:
            _changed = True
            self.__prev_value = self._value
            self._value = value
            self.__prev_change = self.__last_change
            self.__last_change = self._sh.now()
            self.__changed_by = "{0}:{1}".format(caller, source)
            if caller != "fader":
                self._fading = False
                self._lock.notify_all()
                self._change_logger("Item {} = {} via {} {} {}".format(self._path, value, caller, source, dest))
        self._lock.release()
        if _changed or self._enforce_updates or self._type == 'scene':
#            self.__prev_update = self.__last_update #Multiclick
            self.__last_update = self._sh.now()
            for method in self.__methods_to_trigger:
                try:
                    method(self, caller, source, dest)
                except Exception as e:
                    logger.exception("Item {}: problem running {}: {}".format(self._path, method, e))
            if self._threshold and self.__logics_to_trigger:
                if self.__th_crossed and self._value <= self.__th_low:  # cross lower bound
                    self.__th_crossed = False
                    self.__trigger_logics()
                elif not self.__th_crossed and self._value >= self.__th_high:  # cross upper bound
                    self.__th_crossed = True
                    self.__trigger_logics()
            elif self.__logics_to_trigger:
                self.__trigger_logics()
            for item in self._items_to_trigger:
                args = {'value': value, 'source': self._path}
                self._sh.trigger(name=item.id(), obj=item.__run_eval, value=args, by=caller, source=source, dest=dest)
        if _changed and self._cache and not self._fading:
            try:
                _cache_write(self._cache, self._value)
            except Exception as e:
                logger.warning("Item: {}: could update cache {}".format(self._path, e))
        if self._autotimer and caller != 'Autotimer' and not self._fading:

            _time, _value = self._autotimer[0]
            compat = self._autotimer[1]
            if self._autotimer[2]:
                try:
                    _time = eval('self._sh.'+self._autotimer[2]+'()')
                except:
                    logger.warning("Item '{}': Attribute 'autotimer': Item '{}' does not exist".format(self._path, self._autotimer[2]))
            if self._autotimer[3]:
                try:
                    _value = self._castvalue_to_itemtype(eval('self._sh.'+self._autotimer[3]+'()'), compat)
                except:
                    logger.warning("Item '{}': Attribute 'autotimer': Item '{}' does not exist".format(self._path, self._autotimer[3]))
            self._autotimer[0] = (_time, _value)     # for display of active/last timer configuration in backend

            next = self._sh.now() + datetime.timedelta(seconds=_time)
            self._sh.scheduler.add(self.id() + '-Timer', self.__call__, value={'value': _value, 'caller': 'Autotimer'}, next=next)


    def add_logic_trigger(self, logic):
        self.__logics_to_trigger.append(logic)

    def remove_logic_trigger(self, logic):
        self.__logics_to_trigger.remove(logic)

    def get_logic_triggers(self):
        return self.__logics_to_trigger

    def add_method_trigger(self, method):
        self.__methods_to_trigger.append(method)

    def remove_method_trigger(self, method):
        self.__methods_to_trigger.remove(method)

    def get_method_triggers(self):
        return self.__methods_to_trigger

    def age(self):
        delta = self._sh.now() - self.__last_change
        return delta.total_seconds()

    def autotimer(self, time=None, value=None, compat=ATTRIB_COMPAT_V12):
        if time is not None and value is not None:
            self._autotimer = [(time, value), compat, None, None]
        else:
            self._autotimer = False

    def changed_by(self):
        return self.__changed_by

    def fade(self, dest, step=1, delta=1):
        dest = float(dest)
        self._sh.trigger(self._path, _fadejob, value={'item': self, 'dest': dest, 'step': step, 'delta': delta})

    def id(self):
        return self._path

    def last_change(self):
        return self.__last_change

    def last_update(self):
        return self.__last_update

    #Multiclick
#    def prev_update_age(self):
#        delta = self.__last_update - self.__prev_update
#        return delta.total_seconds()

    def prev_age(self):
        delta = self.__last_change - self.__prev_change
        return delta.total_seconds()

    def prev_change(self):
        return self.__prev_change

    def prev_value(self):
        return self.__prev_value

    def remove_timer(self):
        self._sh.scheduler.remove(self.id() + '-Timer')

    def return_children(self):
        for child in self.__children:
            yield child

    def return_parent(self):
        return self.__parent

    def set(self, value, caller='Logic', source=None, dest=None, prev_change=None, last_change=None):
        try:
            value = self.cast(value)
        except:
            try:
                logger.warning("Item {}: value {} does not match type {}. Via {} {}".format(self._path, value, self._type, caller, source))
            except:
                pass
            return
        self._lock.acquire()
        self._value = value
        if prev_change is None:
            self.__prev_change = self.__last_change
        else:
            self.__prev_change = prev_change
        if last_change is None:
            self.__last_change = self._sh.now()
        else:
            self.__last_change = last_change
        self.__changed_by = "{0}:{1}".format(caller, None)
        self._lock.release()
        self._change_logger("Item {} = {} via {} {} {}".format(self._path, value, caller, source, dest))

    def timer(self, time, value, auto=False, compat=ATTRIB_COMPAT_DEFAULT):
        time = self._cast_duration(time)
        value = self._castvalue_to_itemtype(value, compat)
        if auto:
            caller = 'Autotimer'
            self._autotimer = [(time, value), compat, None, None]
        else:
            caller = 'Timer'
        next = self._sh.now() + datetime.timedelta(seconds=time)
        self._sh.scheduler.add(self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller}, next=next)

    def type(self):
        return self._type

    def get_children_path(self):
        return [item._path
                for item in self.__children]

    def jsonvars(self):
        """
        Translation method from object members to json
        :return: Key / Value pairs from object members
        """
        return { "id": self._path,
                 "name": self._name,
                 "value" : self._value,
                 "type": self._type,
                 "attributes": self.conf,
                 "children": self.get_children_path() }
# alternative method to get all class members
#    @staticmethod
#    def get_members(instance):
#        return {k: v
#                for k, v in vars(instance).items()
#                if str(k) in ["_value", "conf"] }
#                #if not str(k).startswith('_')}

    def to_json(self):
       return json.dumps(self.jsonvars(), sort_keys=True, indent=2)