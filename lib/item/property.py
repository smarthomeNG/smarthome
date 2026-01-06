#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2018-2020   Martin Sinn                         m.sinn@gmx.de
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


"""
--------------------------------------------------------------------------------------------
---
---  Properties of the item, that can be accessed from outside of the item class
---
"""

import copy
import inspect
import logging


class Property:
    """
    Inner class Property of item class.

    This class encapsulates all properties that are publicly available

    An instance of this class is created in the __init__ method of the item class
    """

    def __init__(self, parent):
        self._item = parent
        self.logger = logging.getLogger(__name__)

    def _ro_error(self):
        prop = inspect.stack()[1][3]
        self.logger.error("Cannot set readonly property '{}' of item '{}'".format(prop, self._item._path))
        return

    def _type_error(self, err):
        prop = inspect.stack()[1][3]
        self.logger.error("Cannot set property '{}' of item '{}' to a {} value".format(prop, self._item._path, err))
        return

    def _cast_warning(self, value):
        prop = inspect.stack()[1][3]
        self.logger.warning("Casting value '{}' to required type before assigning it to property '{}' of item '{}'".format(value, prop, self._item._path))
        return

    @property
    def attributes(self):
        """
        Read-Only Property: attributes. List of plugin-specific attribute names

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return list(self._item.conf.keys())

    def init_dynamic_properties(self):
        """
        Initialize dynamic properties to get the values of plugin-specific attributes
        """
        for confattr in self._item.conf.keys():
            setattr(self, confattr, self.get_config_attribute(confattr))
        return

    def get_config_attribute(self, attr):
        return self._item.conf.get(attr, '')

    @property
    def defined_in(self):
        """
        Read-Only Property: defined_in . The filename in which the item was defined

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._filename

    @defined_in.setter
    def defined_in(self, value):
        self._ro_error()
        return

    @property
    def enforce_updates(self):
        """
        Property: enforce_updates

        Available in SmartHomeNG v1.6 and above

        :param value: enforce_update state of the item
        :type value: bool

        :return: enforce_update state of the item
        :rtype: bool
        """
        return self._item._enforce_updates

    @enforce_updates.setter
    def enforce_updates(self, value):

        if isinstance(value, bool):
            self._item._enforce_updates = value
            return
        else:
            self._type_error('non-boolean')
            return

    @property
    def enforce_change(self):
        """
        Property: enforce_change

        Available in SmartHomeNG v1.6 and above

        :param value: enforce_change state of the item
        :type value: bool

        :return: enforce_change state of the item
        :rtype: bool
        """
        return self._item._enforce_change

    @enforce_change.setter
    def enforce_change(self, value):

        if isinstance(value, bool):
            self._item._enforce_change = value
            return
        else:
            self._type_error('non-boolean')
            return

    @property
    def eval(self):
        """
        Property: eval expression

        Available in SmartHomeNG v1.6 and above

        :param value: eval expression of the item
        :type value: str

        :return: eval expression of the item
        :rtype: str
        """
        if self._item._eval:
            return self._item._eval
        return ''

    @eval.setter
    def eval(self, value):

        if isinstance(value, str):
            if value == '':
                self._item._eval = None
            else:
                self._item._eval = value
            return
        else:
            self._type_error('non-non-string')
            return

    @property
    def eval_unexpanded(self):
        """
        Property: eval expression

        Available in SmartHomeNG v1.6 and above

        :param value: eval expression of the item
        :type value: str

        :return: eval expression of the item
        :rtype: str
        """
        if self._item._eval:
            return self._item._eval
        return ''

    @eval_unexpanded.setter
    def eval_unexpanded(self, value):

        if isinstance(value, str):
            self._item._lock.acquire()
            self._item._process_eval(value)
            self._item._lock.release()
            return
        else:
            self._type_error('non-non-string')
            return

    @property
    def last_change(self):
        """
        Read-Only Property: last_change

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_change()

    @last_change.setter
    def last_change(self, value):
        self._ro_error()
        return

    @property
    def last_change_age(self):
        """
        Read-Only Property: last_change_age

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_change_age()

    @last_change_age.setter
    def last_change_age(self, value):
        self._ro_error()
        return

    @property
    def last_change_by(self):
        """
        Read-Only Property: last_change_by

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_change_by()

    @last_change_by.setter
    def last_change_by(self, value):
        self._ro_error()
        return

    @property
    def last_update(self):
        """
        Read-Only Property: last_update

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_update()

    @last_update.setter
    def last_update(self, value):
        self._ro_error()
        return

    @property
    def last_update_age(self):
        """
        Read-Only Property: last_update_age

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_update_age()

    @last_update_age.setter
    def last_update_age(self, value):
        self._ro_error()
        return

    @property
    def last_update_by(self):
        """
        Read-Only Property: last_update_by

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_update_by()

    @last_update_by.setter
    def last_update_by(self, value):
        self._ro_error()
        return

    @property
    def last_trigger(self):
        """
        Read-Only Property: last_trigger

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_trigger()

    @last_trigger.setter
    def last_trigger(self, value):
        self._ro_error()
        return

    @property
    def last_trigger_age(self):
        """
        Read-Only Property: last_trigger_age

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_trigger_age()

    @last_trigger_age.setter
    def last_trigger_age(self, value):
        self._ro_error()
        return

    @property
    def last_trigger_by(self):
        """
        Read-Only Property: last_trigger_by

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_trigger_by()

    @last_trigger_by.setter
    def last_trigger_by(self, value):
        self._ro_error()
        return

    @property
    def last_value(self):
        """
        Read-Only Property: last_value

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_last_value()

    @last_value.setter
    def last_value(self, value):
        self._ro_error()
        return

    @property
    def name(self):
        """
        Property: name

        Available in SmartHomeNG v1.6 and above

        :param value: name of the item
        :type value: str

        :return: name of the item
        :rtype: str
        """
        return self._item._name

    @name.setter
    def name(self, value):

        if not isinstance(value, str):
            self._cast_warning(value)
            value = '{}'.format(value)
        if value == '':
            self._item._name = self._item._path
        else:
            self._item._name = value
        return

    @property
    def description(self):
        """
        Read-Only Property: description

        Available in SmartHomeNG v1.6 and above

        :return: type of the item
        :rtype: str
        """
        return self._item._description

    @description.setter
    def description(self, value):
        self._ro_error()
        return

    @property
    def type(self):
        """
        Read-Only Property: type

        Available in SmartHomeNG v1.6 and above

        :return: type of the item
        :rtype: str
        """
        return self._item._type

    @type.setter
    def type(self, value):
        self._ro_error()
        return

    @property
    def on_change(self):
        """
        Read-Only Property: on_update

        Available in SmartHomeNG v1.6 and above

        :return: path of on_update definitions
        :rtype: str
        """
        return self._item._build_on_xx_list(self._item._on_change_dest_var, self._item._on_change)

    @on_change.setter
    def on_change(self, value):
        self._ro_error()
        return

    @property
    def on_change_unexpanded(self):
        """
        Read-Only Property: on_update

        Available in SmartHomeNG v1.6 and above

        :return: path of on_update definitions
        :rtype: str
        """
        return self._item._build_on_xx_list(self._item._on_change_dest_var_unexp, self._item._on_change_unexpanded)

    @on_change_unexpanded.setter
    def on_change_unexpanded(self, value):
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            if value == [] or self._checkstrtype(value):
                self._item._lock.acquire()
                self._item._process_on_xx_list('on_change', value)
                self._item._lock.release()
            else:
                self._type_error('list containing non-string')
                return
            return
        else:
            self._type_error('non-list')
            return

    @property
    def on_update(self):
        """
        Read-Only Property: on_update

        Available in SmartHomeNG v1.6 and above

        :return: path of on_update definitions
        :rtype: str
        """
        return self._item._build_on_xx_list(self._item._on_update_dest_var, self._item._on_update)

    @on_update.setter
    def on_update(self, value):
        self._ro_error()
        return

    @property
    def on_update_unexpanded(self):
        """
        Read-Only Property: on_update

        Available in SmartHomeNG v1.6 and above

        :return: path of on_update definitions
        :rtype: str
        """
        return self._item._build_on_xx_list(self._item._on_update_dest_var_unexp, self._item._on_update_unexpanded)

    @on_update_unexpanded.setter
    def on_update_unexpanded(self, value):
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            if value == [] or self._checkstrtype(value):
                self._item._lock.acquire()
                self._item._process_on_xx_list('on_update', value)
                self._item._lock.release()
            else:
                self._type_error('list containing non-string')
                return
            return
        else:
            self._type_error('non-list')
            return

    @property
    def path(self):
        """
        Read-Only Property: path

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._path

    @path.setter
    def path(self, value):
        self._ro_error()
        return

    @property
    def prev_change(self):
        """
        Read-Only Property: prev_change

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_change()

    @prev_change.setter
    def prev_change(self, value):
        self._ro_error()
        return

    @property
    def prev_change_age(self):
        """
        Read-Only Property: prev_change_age

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_change_age()

    @prev_change_age.setter
    def prev_change_age(self, value):
        self._ro_error()
        return

    @property
    def prev_change_by(self):
        """
        Read-Only Property: prev_change_by

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_change_by()

    @prev_change_by.setter
    def prev_change_by(self, value):
        self._ro_error()
        return

    @property
    def prev_update(self):
        """
        Read-Only Property: prev_update

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_update()

    @prev_update.setter
    def prev_update(self, value):
        self._ro_error()
        return

    @property
    def prev_update_age(self):
        """
        Read-Only Property: prev_update_age

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_update_age()

    @prev_update_age.setter
    def prev_update_age(self, value):
        self._ro_error()
        return

    @property
    def prev_update_by(self):
        """
        Read-Only Property: prev_update_by

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_update_by()

    @prev_update_by.setter
    def prev_update_by(self, value):
        self._ro_error()
        return

    @property
    def prev_trigger(self):
        """
        Read-Only Property: prev_trigger

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_trigger()

    @prev_trigger.setter
    def prev_trigger(self, value):
        self._ro_error()
        return

    @property
    def prev_trigger_age(self):
        """
        Read-Only Property: prev_trigger_age

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_trigger_age()

    @prev_trigger_age.setter
    def prev_trigger_age(self, value):
        self._ro_error()
        return

    @property
    def prev_trigger_by(self):
        """
        Read-Only Property: prev_trigger_by

        Available in SmartHomeNG v1.9.1 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_trigger_by()

    @prev_trigger_by.setter
    def prev_trigger_by(self, value):
        self._ro_error()
        return

    @property
    def prev_value(self):
        """
        Read-Only Property: prev_value

        Available in SmartHomeNG v1.6 and above

        :return: path of the item
        :rtype: str
        """
        return self._item._get_prev_value()

    @prev_value.setter
    def prev_value(self, value):
        self._ro_error()
        return

    @property
    def trigger(self):
        """
        Property: Triggers of the item

        Available in SmartHomeNG v1.6 and above

        :param value: list of triggers
        :type value: list

        :return: [] if not defined or a list of triggers
        :rtype: list of str
        """
        if self._item._trigger:
            return self._item._trigger
        return []

    def _checkstrtype(self, obj):
        return bool(obj) and all(isinstance(elem, str) for elem in obj)

    @trigger.setter
    def trigger(self, value):

        if isinstance(value, list):
            if value == []:
                self._item._trigger = False
                self._item._trigger_unexpanded = []
            else:
                if self._checkstrtype(value):
                    self._item._trigger = value
                    self._item._trigger_unexpanded = value
                else:
                    self._type_error('list containing non-string')
                    return
            return
        else:
            self._type_error('non-list')
            return

    @property
    def trigger_unexpanded(self):
        """
        Property: Triggers of the item

        Available in SmartHomeNG v1.6 and above

        :param value: list of triggers
        :type value: list

        :return: [] if not defined or a list of triggers
        :rtype: list of str
        """
        if self._item._trigger:
            return self._item._trigger_unexpanded
        return []

    @trigger_unexpanded.setter
    def trigger_unexpanded(self, value):
        if isinstance(value, str):
            value = [value]
        if isinstance(value, list):
            if value == [] or self._checkstrtype(value):
                self._item._lock.acquire()
                self._item._process_trigger_list('trigger', value)
                self._item._lock.release()
            else:
                self._type_error('list containing non-string')
                return
            return
        else:
            self._type_error('non-list')
            return

    @property
    def value(self):
        """
        Property: value

        Available in SmartHomeNG v1.6 and above

        :param value: value of the item
        :type value: <type of the item>

        :return: value of the item
        :rtype: <type of the item>
        """
        return copy.deepcopy(self._item._value)

    @value.setter
    def value(self, value):

        self._item(value, caller='Property', source='Assign')
        return


    @property
    def hysteresis_state(self):
        """
        Property: Inner hysteresis_state

        returns
        - 1  - On   = set the output to True
        - 0  - Stay = leave the output unchaned in last state
        - -1 - Off  = set the output to False

        Available in SmartHomeNG v1.10 and above

        :return: hysteresis state of the item
        :rtype: int
        """
        return self._item.hysteresis_state()

"""
---
---  End of Properties class
---
--------------------------------------------------------------------------------------------
"""
