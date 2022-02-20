#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  MD_Datatype and derived classes for MultiDevice plugin
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
#
#########################################################################

import json

# default / reference datatypes
datatypes = (
    'int', 'num', 'str', 'dict', 'list', 'tuple', 'bytes', 'bytearray', 'json'
)


class Datatype(object):
    """ Datatype class for conversion tasks

    This is one of the most important classes. By declaration, it contains
    information about the data type and format needed by a device and methods
    to convert its value from selected Python data types used in items to the
    (possibly) special data formats required by devices and vice versa.

    Datatypes are specified in subclasses of Datatype with a nomenclature
    convention of DT_<device data type of format>.

    All datatype classes are imported from Datatypes.py into the 'DT' module.

    New devices probably create the need for new data types.

    For details concerning API and implementation, refer to the reference
    classes as examples.

    As nearly all return values are possible, error handling cannot be done via
    return code. In consequence, errors are transmitted via exceptions, either
    explicitly or by just letting it happen (e.g. int('abc') -> ValueError) The
    whole data type conversion is enclosed in try/except higher up. Keep it
    simple here :)

    This class describes the basic structure of all derived datatype classes.

    Basically, it defines the conversion from item value to device "value" and
    vice versa, e.g. bool <-> text, float <-> encoded number, or str <-> int
    for clear text status messages in SmartHomeNG.

    To define own Datatype classes, define derived class and overwrite at least
    get_shng_data() and/or get_send_data().
    """
    def __init__(self, fail_silent=True):
        """
        :param fail_silent: keep silent on data conversion error or raise exception
        :type fail_silent: bool
        """
        self._silent = fail_silent

    def get_send_data(self, data, **kwargs):
        """
        take (item value) data and return value in a format fit for the device
        In the base class, this just returns whatever it gets.

        If errors occur while converting, raise an exception.

        :param data: arbitrary data (usually item value)
        :return: data in device-compatible format
        """
        return data

    def get_shng_data(self, data, type=None, **kwargs):
        """
        take data from device reply and try and convert it into SmartHomeNG-
        compatible type (item type).

        By default, this returns data according to the default item type
        associated with this Datatype class.
        Optionally, the desired return type can be specified (as string), in
        which case the method is expected to return the requested type. As a
        basic 'casting show' is implemented in the base class, derived classes
        may call the base class' get_shng_data if 'type' is specified.
        Beware of special needs if converting complex data types.

        If errors occur while converting, raise an exception.

        :param data: value to convert
        :param type: type of return value
        :type type: str
        :return: converted value
        """
        if type is None or type not in datatypes:
            return data

        if type == 'int':
            try:
                return int(data)
            except ValueError:
                if self._silent:
                    return 0
                else:
                    raise

        if type == 'num':
            try:
                return float(data)
            except ValueError:
                if self._silent:
                    return 0
                else:
                    raise

        if type == 'str':
            return str(data)

        if type == 'dict':
            try:
                return dict(data)
            except ValueError:
                if self._silent:
                    return {}
                else:
                    raise

        if type == 'list':
            try:
                return list(data)
            except ValueError:
                if self._silent:
                    return []
                else:
                    raise

        if type == 'tuple':
            try:
                return tuple(data)
            except ValueError:
                if self._silent:
                    return ()
                else:
                    raise

        if type == 'bytes':
            try:
                return bytes(str(data), 'utf-8')
            except ValueError:
                if self._silent:
                    return b''
                else:
                    raise

        if type == 'bytearray':
            try:
                return bytearray(str(data), 'utf-8')
            except ValueError:
                if self._silent:
                    return bytearray(b'')
                else:
                    raise

        if type == 'json':
            try:
                return json.dumps(data)
            except ValueError:
                if self._silent:
                    return None
                else:
                    raise


class DT_none(Datatype):
    """ don't pass on anything. Maybe needed someplace... """
    def get_send_data(self, data, **kwargs):
        return None

    def get_shng_data(self, data, type=None, **kwargs):
        return None


class DT_raw(Datatype):
    """ pass on data, identical to base class """
    pass


class DT_bool(Datatype):
    """ cast to bool """
    def get_send_data(self, data, **kwargs):
        return bool(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return bool(data)

        return super().get_shng_data(data, type)


class DT_int(Datatype):
    """ cast to int """
    def get_send_data(self, data, **kwargs):
        return int(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return int(data)

        return super().get_shng_data(data, type)


class DT_num(Datatype):
    """ cast to float """
    def get_send_data(self, data, **kwargs):
        return float(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return float(data)

        return super().get_shng_data(data, type)


class DT_str(Datatype):
    """ cast to str """
    def get_send_data(self, data, **kwargs):
        return str(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            if isinstance(data, (bytes, bytearray)):
                return data.decode('utf-8')
            else:
                return str(data)
        return super().get_shng_data(data, type)


class DT_list(Datatype):
    """ enlist """
    def get_send_data(self, data, **kwargs):
        return list(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return list(data)
        return super().get_shng_data(data, type)


class DT_dict(Datatype):
    """ dict-ate """
    def get_send_data(self, data, **kwargs):
        return dict(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return dict(data)
        return super().get_shng_data(data, type)


class DT_tuple(Datatype):
    """ toupling (meh...) """
    def get_send_data(self, data, **kwargs):
        return tuple(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return tuple(data)
        return super().get_shng_data(data, type)


class DT_bytes(Datatype):
    def get_send_data(self, data, **kwargs):
        return bytes(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return bytes(data)
        return super().get_shng_data(data, type)


class DT_bytearray(Datatype):
    def get_send_data(self, data, **kwargs):
        return bytearray(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return bytearray(data)
        return super().get_shng_data(data, type)


class DT_json(Datatype):
    def get_send_data(self, data, **kwargs):
        return json.dumps(data)

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return json.loads(data)
        return super().get_shng_data(data, type)


class DT_webservices(Datatype):
    """ extract value of key 'value' from json data, e.g. for webservices plugin """
    def get_send_data(self, data, **kwargs):
        return data

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            js = json.loads(data)
            arg = js.get('value', None)
            return arg
        return super().get_shng_data(data, type)
