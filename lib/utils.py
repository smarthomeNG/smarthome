#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016- Christian Strassburg              c.strassburg@gmx.de
#  Copyright 2017- Serge Wagener                     serge@wagener.family
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

"""
This library contails the Utile-class for SmartHomeNG.

New helper-functions are going to be implemented in this library.

"""

import logging

import sys
import re
import hashlib
import ipaddress
import socket
import subprocess

logger = logging.getLogger(__name__)

TIMEFRAME_REGEX = re.compile(r'^(\d+)([ihdwmy]?)$', re.VERBOSE | re.IGNORECASE)


class Utils(object):

    @staticmethod
    def is_mac(mac):
        """
        Validates a MAC address

        :param mac: MAC address
        :type string: str

        :return: True if value is a MAC
        :rtype: bool
        """

        mac = str(mac)
        # notation without separators
        if len(mac) == 12:
            for c in mac:
                # each digit is hex
                if c not in '0123456789abcdefABCDEF':
                    return False
            return True

        # notation with separators -> 12 digits + 5 separators
        if len(mac) != 17:
            return False
        octets = re.split('[: -]', mac)
        # 6 groups...
        if len(octets) != 6:
            return False
        for o in octets:
            # ... of 2 digits each
            if len(o) != 2:
                return False
        # and each digit is hex
        for c in ''.join(octets):
            if c not in '0123456789abcdefABCDEF':
                return False
        return True

    @staticmethod
    def is_ip(string):
        """
        FUTURE: Checks if a string is a valid ip-address (v4 or v6)
        ACTUAL: redirects to ipv4 only check for backwards compatibility

        :param string: String to check
        :type string: str

        :return: True if an ip, false otherwise.
        :rtype: bool
        """

        return Utils.is_ipv4(string)
        # later: return (Utils.is_ipv4(string) or Utils.is_ipv6(string))

    @staticmethod
    def is_ipv4(string):
        """
        Checks if a string is a valid ip-address (v4)

        :param string: String to check
        :type string: str

        :return: True if an ip, false otherwise.
        :rtype: bool
        """

        try:
            ipaddress.IPv4Address(string)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_ipv6(string):
        """
        Checks if a string is a valid ip-address (v6)

        :param string: String to check
        :type string: str

        :return: True if an ipv6, false otherwise.
        :rtype: bool
        """

        try:
            ipaddress.IPv6Address(string)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def is_hostname(string):
        """
        Checks if a string is a valid hostname

        The hostname has is checked to have a valid format

        :param string: String to check
        :type string: str

        :return: True if a hostname, false otherwise.
        :rtype: bool
        """

        try:
            return bool(re.match("^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9])\\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$", string))
        except TypeError:
            return False

    @staticmethod
    def get_local_ipv4_address():
        """
        Get local ipv4 address of the interface with the default gateway.
        Return '127.0.0.1' if no suitable interface is found
        NOTE: if more than one IP addresses are available and no external
        gateway is configured, thie method returns one of the configured
        addresses, but not deterministically.

        :return: IPv4 address as a string
        :rtype: string
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            if 's' in locals():
                s.close()
        return IP

    @staticmethod
    def get_local_ipv6_address():
        """
        Get local ipv6 address of the interface with the default gateway.
        Return '::1' if no suitable interface is found

        :return: IPv6 address as a string
        :rtype: string
        """
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            s.connect(('fda2:ffff:ffff:ffff:ffff:ffff:ffff:ffff', 1))
            IP = s.getsockname()[0]
        except:
            IP = '::1'
        finally:
            if 's' in locals():
                s.close()
        return IP


    @staticmethod
    def is_knx_groupaddress(groupaddress):
        """
        Checks if the passed string is a valid knx goup address

        The checked format is:
           main group (0-31 = 5 bits)
           middle group (0-7 = 3 bits)
           subgroup (0-255 = 8 bits)

        :param groupaddress: String to check
        :type groupaddress: str

        :return: True if a groupaddress can be recognized, false otherwise.
        :rtype: bool
        """
        if groupaddress == '':
            return True

        g = groupaddress.split('/')
        if len(g) != 3:
            return False
        if not(Utils.is_int(g[0]) and Utils.is_int(g[1]) and Utils.is_int(g[2])):
            return False
        if (int(g[0]) < 0) or (int(g[0]) > 31):
            return False
        if (int(g[1]) < 0) or (int(g[1]) > 7):
            return False
        if (int(g[2]) < 0) or (int(g[2]) > 255):
            return False
        return True


    @staticmethod
    def is_timeframe(string):
        """
        Checks if a string is a timeframe. A timeframe consists of a
        number and an optional unit identifier (e.g. 2h, 30m, ...).
        Unit identifiers are: i for minutes, h for hours, d for days,
        w for weeks, m for months, y for years. If omitted milliseconds
        are assumed.

        :param string: String to check.
        :type string: str

        :return: True if a timeframe can be recognized, false otherwise.
        :rtype: bool
        """

        try:
            return bool(TIMEFRAME_REGEX.search(string))
        except TypeError:
            return False

    @staticmethod
    def to_timeframe(value):
        """
        Converts a timeframe value to milliseconds. See is_timeframe() method.
        The special value 'now' is supported for the current time.

        :param value : value to convert
        :type value: str, int, ...

        :return: True if cant be converted and is true, False otherwise.
        :rtype: bool
        """

        minute = 60 * 1000
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        month = 30 * day
        year = 365 * day
        frames = {'i': minute, 'h': hour, 'd': day, 'w': week, 'm': month, 'y': year}

        if value == 'now':
            value = '0'

        if not Utils.is_timeframe(value):
            raise Exception('Invalid value for boolean conversion: ' + value)

        amount, unit = TIMEFRAME_REGEX.match(value).groups()
        if unit in frames:
            return int(float(amount) * frames[unit])
        else:
            return int(amount)

    @staticmethod
    def is_int(string):
        """
        Checks if a string is a integer.

        :param string: String to check.
        :type string: str

        :return: True if a cast to int works, false otherwise.
        :rtype: bool
        """

        try:
            int(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def is_float(string):
        """
        Checks if a string is a float.

        :param string: String to check.
        :type string: str

        :return: True if a cast to float works, false otherwise.
        :rtype: bool
        """

        try:
            float(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def to_bool(value, default='exception'):
        """
        Converts a value to boolean.

        Raises exception if value is a string and can't be converted and if no default value is given
        Case is ignored. These string values are allowed:
        - True: 'True', "1", "true", "yes", "y", "t", "on"
        - False: "", "0", "faLse", "no", "n", "f", "off"
        Non-string values are passed to bool constructor.

        :param value : value to convert
        :param default: optional, value to return if value can not be parsed, if default is not set this method throws an exception
        :type value: str, object, int, ...
        :type value: str, object, int, ...

        :return: True if cant be converted and is true, False otherwise.
        :rtype: bool
        """
        # -> should it be possible to cast strings: 0 -> False and non-0 -> True (analog to integer values)?
        if isinstance(value, str):
            if value.lower() in ("yes", "y", "true", "t", "1", "on"):
                return True
            if value.lower() in ("no", "n", "false", "f", "0", "off", ""):
                return False
            if default == 'exception':
                raise Exception('Invalid value for boolean conversion: ' + value)
            else:
                return default
        return bool(value)

    @staticmethod
    def create_hash(plaintext):
        """
        Create hash (currently sha512) for given plaintext value

        :param plaintext: plaintext
        :type plaintext: str

        :return: hash of plaintext, lowercase letters
        :rtype: str
        """

        hashfunc = hashlib.sha512()
        hashfunc.update(plaintext.encode())
        return "".join(format(b, "02x") for b in hashfunc.digest())

    @staticmethod
    def is_hash(value):
        """
        Check if value is a valid hash (currently sha512) value

        :param value: value to check
        :type value: str

        :return: True: given value can be a sha512 hash, False: given value can not be a sha512 hash
        :rtype: bool
        """

        # a valid sha512 hash is a 128 charcter long string value
        if value is None or not isinstance(value, str) or len(value) != 128:
            return False

        # and its a hexedecimal value
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_hashed_password(pwd_to_check, hashed_pwd):
        """
        Check if given plaintext password matches the hashed password
        An empty password is always rejected

        :param pwd_to_check: plaintext password to check
        :type pwd_to_check: str
        :param hashed_pwd: hashed password
        :type hashed_pwd: str

        :return: True: password matches, False: password does not match
        :rtype: bool
        """

        if pwd_to_check is None or pwd_to_check == '':
            # No password given -> return "not matching"
            return False

        # todo: check pwd_to_check for minimum length? <- msinn: not here, password policy at a central point

        return Utils.create_hash(pwd_to_check) == hashed_pwd.lower()

    @staticmethod
    def strip_quotes(string):
        """
        If a string contains quotes as first and last character, this function
        returns the string without quotes, otherwise the string is returned unchanged

        :param string: string to check for quotes
        :type string: str

        :return: string with quotes stripped
        :rtype: str
        """
        if type(string) is str:
            string = string.strip()
            if len(string) >= 2:
                if string[0] in ['"', "'"]:        # check if string starts with ' or "
                    if string[-1] == string[0]:    # and end with it
                        if string.count(string[0]) == 2:  # if they are the only one
                            string = string[1:-1]  # remove them
        return string


    @staticmethod
    def string_to_list(string):
        """
        Convert a string to a list

        If the parameter is not of type str, the parameter gest returned unchanged

        If parameter string is
        - a list, it gets returned unchanged
        - a simple datatype other than string, it gets returned unchanged
        - an empty string, it gets returned unchanged
        - a non-empty string, it gets converted to a list of len=1
        - format [<str>,<str>], it gets converted to a list

        :param string: string to convert
        :type string: str

        :return: list of unchanged value
        """
        if isinstance(string, list):
            return string
        if not isinstance(string, str):
            return string
        if len(string) == 0:
            return string
        if string[0] != '[':
            return [string]
        hl = Utils.strip_square_brackets(string).split(',')
        rl = []
        for e in hl:
            er = e.strip()
            if Utils.strip_quotes(er) != er:
                er = Utils.strip_quotes(er)
            else:
                if er.find('.') != -1:
                    er=float(er)
                else:
                    er=int(er)
            rl.append(er)
        return rl


    @staticmethod
    def strip_square_brackets(string):
        """
        If a string contains square brackets as first and last character, this function
        returns the string without the brackets, otherwise the string is returned unchanged

        :param string: string to check for square brackets
        :type string: str

        :return: string with square brackets stripped
        :rtype: str
        """
        if type(string) is str:
            string = string.strip()
            if len(string) >= 2:
                if string[0] == '[':           # check if string starts with [
                    if string[-1] == ']':      # and end with ]
                        string = string[1:-1]  # remove them
        return string

    @staticmethod
    def strip_quotes_fromlist(string):
        """
        If a string representation of a list contains quotes as first and last character of
        a list entry, this function returns the string representation without the qoutes,
        otherwise the string is returned unchanged

        :param string: string representation of a list to check for quotes
        :type string: str

        :return: string representation with square quotes stripped
        :rtype: str
        """
        if type(string) is str:
            string = string.strip()
            if len(string) >= 2:
                string2 = Utils.strip_square_brackets(string)
                if string2 != string:
                    str_list = string2.split(',')
                    string3 = ''
                    for s in str_list:
                        if string3 != '':
                            string3 += ', '
                        string3 += Utils.strip_quotes(s)
                    string = string3
        return string


    @staticmethod
    def get_type(var):
        """
        returns the type of the passed variable

        :param var: Variable to get the type of
        :return: type of the var
        :rtype: str
        """

        return str(type(var))[8:-2]


    @staticmethod
    def execute_subprocess(commandline, wait=True):
        """
        Executes a subprocess via a shell and returns the output written to stdout by this process as a string
        """
        # call date command
        p = subprocess.Popen(commandline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
        # Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
        # Wait for process to terminate. The optional input argument should be a string to be sent to the child process, or None, if no data should be sent to the child.
        (result, err) = p.communicate()
    #    logger.warning("get_process_info: commandline='{}', result='{}', err='{}'".format(command, result, err))

    #    print("result="+str(result))
    #    print("err="+str(err))
        if wait:
            # Wait for date to terminate. Get return returncode
            p.wait()
        return (str(result, encoding='utf-8', errors='strict'), str(err, encoding='utf-8', errors='strict'))

#--------------------------------------------------------------------------------------------

class Version():

    @staticmethod
    def check_list(versl):

        while len(versl) < 4:
            if isinstance(versl[0], str):
                versl.append('0')
            else:
                versl.append(0)
        while len(versl) > 4:
            del versl[-1]
        return versl

    @classmethod
    def to_list(cls, vers):
        """
        Split version number to list and get rid of non-numeric parts

        :param vers:

        :return: version as list
        :rtype: list
        """
        if len(vers) == 0:
            vers = '0'
        if vers[0].lower() == 'v':
            vers = vers[1:]

        # create list with [major,minor,revision,build]
        vsplit = vers.split('.')
        vsplit = cls.check_list(vsplit)

        # get rid of non numeric parts
        vlist = []
        build = 0
        if vsplit == '':
            return ''
        for v in vsplit:
            if v[-1].isalpha():
                build += ord(v[-1].lower()) - 96
                v = v[:-1]
            vi = 0
            try:
                vi = int(v)
            except:
                pass
            vlist.append(vi)
        vlist[3] += build
        return vlist

    @classmethod
    def to_string(cls, versl):

        if versl == [0, 0, 0, 0]:
            return ''
        import copy
        versl2 = copy.deepcopy(versl)
        cls.check_list(versl2)
        if versl2 == '':
            return ''

        if versl2[3] == 0:
            del versl2[3]
        versls = [str(int) for int in versl2]
        vers = ".".join(versls)

        return 'v' + vers

    @classmethod
    def format(cls, vers):

        return cls.to_string(cls.to_list(str(vers)))

    @classmethod
    def compare(cls, v1, v2, operator):
        """
        Compare two version numbers and return if the condition is met

        :param v1:
        :param v2:
        :param operator:
        :type v1: str or list of int
        :type v2: str or list of int
        :type operator: str

        :return: true if condition is met
        :rtype: bool
        """
        if isinstance(v1, str):
            v1 = cls.to_list(v1)
        if isinstance(v2, str):
            v2 = cls.to_list(v2)

        result = False
        if v1 == v2 and operator in ['>=', '==', '<=']:
            result = True
        if v1 < v2 and operator in ['<', '<=']:
            result = True
        if v1 > v2 and operator in ['>', '>=']:
            result = True
        # logger.warning(f"_compare_versions: v1={v1}, v2={v2}, operator='{operator}', result={result}")
        return result

#--------------------------------------------------------------------------------------------

def get_python_version():
    PYTHON_VERSION = str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2]) + ' ' + str(sys.version_info[3])
    if sys.version_info[3] != 'final':
        PYTHON_VERSION += ' '+str(sys.version_info[4])
    return PYTHON_VERSION


def execute_subprocess(commandline, wait=True):
    """
    Executes a subprocess via a shell and returns the output written to stdout by this process as a string
    """
    p = subprocess.Popen(commandline, stdout=subprocess.PIPE, shell=True)
    # Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
    # Wait for process to terminate. The optional input argument should be a string to be sent to the child process, or None, if no data should be sent to the child.
    (result, err) = p.communicate()
    # logger.warning("execute_subprocess: commandline='{}', result='{}', err='{}'".format(command, result, err))
    print("err='{}'".format(err))
    if wait:
        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()
    return str(result, encoding='utf-8', errors='strict')


def running_virtual():
    """
    Return if we run in a virtual environment (venv or virtualenv).
    """

    # The check for sys.real_prefix covers virtualenv,
    # the equality of non-empty sys.base_prefix with sys.prefix covers venv.
    return (getattr(sys, 'base_prefix', sys.prefix) != sys.prefix or
            hasattr(sys, 'real_prefix'))

