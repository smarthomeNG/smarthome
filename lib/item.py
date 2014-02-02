#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 Marcus Popp                          marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import datetime
import logging
import os
import pickle
import threading

logger = logging.getLogger('')


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


def _cast_bool(value):
    if type(value) in [bool, int, float]:
        if value in [False, 0]:
            return False
        elif value in [True, 1]:
            return True
        else:
            raise ValueError
    elif type(value) in [str, str]:
        if value.lower() in ['0', 'false', 'no', 'off']:
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
        # Item Attributes
        #############################################################
        for attr, value in config.items():
            if not isinstance(value, dict):
                if attr in ['cycle', 'eval', 'name', 'type', 'value']:
                    setattr(self, '_' + attr, value)
                elif attr in ['cache', 'enforce_updates']:  # cast to bool
                    try:
                        setattr(self, '_' + attr, _cast_bool(value))
                    except:
                        logger.warning("Item '{0}': problem parsing '{1}'.".format(self._path, attr))
                        continue
                elif attr in ['crontab', 'eval_trigger']:  # cast to list
                    if isinstance(value, str):
                        value = [value, ]
                    setattr(self, '_' + attr, value)
                elif attr == 'autotimer':
                    time, __, value = value.partition('=')
                    if value is not None:
                        self._autotimer = time, value
                elif attr == 'threshold':
                    low, __, high = value.rpartition(':')
                    if not low:
                        low = high
                    self._threshold = True
                    self.__th_crossed = False
                    self.__th_low = float(low)
                    self.__th_high = float(high)
                    logger.debug("Item {}: set threshold => low: {} high: {}}".format(self._path, self.__th_low, self.__th_high))
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
        __defaults = {'num': 0, 'str': '', 'bool': False, 'list': [], 'dict': {}, 'foo': None, 'scene': 0}
        if self._type is None:
            logger.debug("Item {}: no type specified.".format(self._path))
            return
        if self._type not in __defaults:
            logger.error("Item {}: type '{}' unknown. Please use one of: {}.".format(self._path, self._type, ', '.join(list(__defaults.keys()))))
            raise AttributeError
        self.cast = globals()['_cast_' + self._type]
        #############################################################
        # Value
        #############################################################
        if self._value is None:
            self._value = __defaults[self._type]
        try:
            self._value = self.cast(self._value)
        except:
            logger.error("Item {}: value {} does not match type {}.".format(self._path, self._value, self._type))
            raise
        self.__prev_value = self._value
        #############################################################
        # Crontab/Cycle
        #############################################################
        if self._crontab is not None or self._cycle is not None:
            self._sh.scheduler.add(self._path, self, cron=self._crontab, cycle=self._cycle)
        #############################################################
        # Plugins
        #############################################################
        for plugin in self._sh.return_plugins():
            if hasattr(plugin, 'parse_item'):
                update = plugin.parse_item(self)
                if update:
                    self.add_method_trigger(update)

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
        return self._value

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
                _cache_write(self._cache, value)
            except Exception as e:
                logger.warning("Item: {}: could update cache {}".format(self._path, e))
        if self._autotimer and caller != 'Autotimer' and not self._fading:
            _time, _value = self._autotimer
            self.timer(_time, _value, True)

    def add_logic_trigger(self, logic):
        self.__logics_to_trigger.append(logic)

    def add_method_trigger(self, method):
        self.__methods_to_trigger.append(method)

    def age(self):
        delta = self._sh.now() - self.__last_change
        return delta.total_seconds()

    def autotimer(self, time=None, value=None):
        if time is not None and value is not None:
            self._autotimer = time, value
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

    def timer(self, time, value, auto=False):
        try:
            if isinstance(time, str):
                time = time.strip()
                if time.endswith('m'):
                    time = int(time.strip('m')) * 60
                else:
                    time = int(time)
            if isinstance(value, str):
                value = value.strip()
            if auto:
                caller = 'Autotimer'
                self._autotimer = time, value
            else:
                caller = 'Timer'
            next = self._sh.now() + datetime.timedelta(seconds=time)
        except Exception as e:
            logger.warning("Item {}: timer ({}, {}) problem: {}".format(self._path, time, value, e))
        else:
            self._sh.scheduler.add(self.id() + '-Timer', self.__call__, value={'value': value, 'caller': caller}, next=next)

    def type(self):
        return self._type
