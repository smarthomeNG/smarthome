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

import math
import sys
import re
import base64
import functools
import hashlib
import hmac
import secrets
import ipaddress
import socket
import subprocess

logger = logging.getLogger(__name__)

TIMEFRAME_REGEX = re.compile(r'^(\d+)([ihdwmy]?)$', re.VERBOSE | re.IGNORECASE)


PASSWORD_HASH_ALGORITHM = 'pbkdf2_sha256'
#: salted hash of a legacy sha512 hash (Utils.wrap_legacy_password_hash()): the sha512 hex digest is the PBKDF2 input
WRAPPED_HASH_ALGORITHM = 'pbkdf2_sha256_sha512'
PASSWORD_HASH_ITERATIONS = 600_000


def _b64encode(data: bytes) -> str:
    """Return ``data`` as base64 text without padding."""
    return base64.b64encode(data).decode('ascii').rstrip('=')


def _b64decode(text: str) -> bytes:
    """Decode base64 text written by _b64encode()."""
    return base64.b64decode(text + '=' * (-len(text) % 4), validate=True)


def _parse_salted_hash(value: str) -> tuple[str, int, bytes, bytes] | None:
    """
    Return (algorithm, iterations, salt, digest) of a hash created by Utils.hash_password() or
    Utils.wrap_legacy_password_hash(), None for anything else.
    """
    if not isinstance(value, str):
        return None
    parts = value.split('$')
    if len(parts) != 4 or parts[0] not in (PASSWORD_HASH_ALGORITHM, WRAPPED_HASH_ALGORITHM) or not parts[1].isdigit():
        return None
    try:
        return parts[0], int(parts[1]), _b64decode(parts[2]), _b64decode(parts[3])
    except ValueError:
        return None


def _salted_hash(algorithm: str, secret: str) -> str:
    """Return the salted hash of ``secret`` in the format ``<algorithm>$<iterations>$<salt>$<digest>``."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt, PASSWORD_HASH_ITERATIONS)
    return '$'.join((algorithm, str(PASSWORD_HASH_ITERATIONS), _b64encode(salt), _b64encode(digest)))


@functools.lru_cache(maxsize=64)
def _pbkdf2_matches(password: str, iterations: int, salt: bytes, digest: bytes) -> bool:
    """Return True if ``password`` derives to ``digest``."""
    derived = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen=len(digest))
    return hmac.compare_digest(derived, digest)


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
            return bool(
                re.match(
                    '^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9-]*[a-zA-Z0-9])\\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\\-]*[A-Za-z0-9])$',
                    string,
                )
            )
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
        except OSError:
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
        except OSError:
            IP = '::1'
        finally:
            if 's' in locals():
                s.close()
        return IP

    @staticmethod
    def get_all_addresses_for_addressfamily(af: int) -> list:
        """
        Get all addresses for an address-family as a list

        https://stackoverflow.com/questions/270745/how-do-i-determine-all-of-my-ip-addresses-when-i-have-multiple-nics/274644#274644

        :return: addresses
        """
        from netifaces import interfaces, ifaddresses

        ip_list = []
        for interface in interfaces():
            if af in ifaddresses(interface).keys():
                for link in ifaddresses(interface)[af]:
                    ip_list.append(link['addr'])
        return ip_list

    @staticmethod
    def get_all_local_ipv4_addresses() -> list:
        """
        Get ipv4 addresses of all interfaces as a list

        :return: ipv4 addresses
        """
        from netifaces import AF_INET

        return Utils.get_all_addresses_for_addressfamily(AF_INET)

    @staticmethod
    def get_all_local_ipv6_addresses() -> list:
        """
        Get ipv6 addresses of all interfaces as a list

        :return: ipv6 addresses
        """
        from netifaces import AF_INET6

        return Utils.get_all_addresses_for_addressfamily(AF_INET6)

    @staticmethod
    def is_knx_groupaddress(groupaddress: str) -> bool:
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
        if not isinstance(groupaddress, str):
            return False

        if groupaddress == '':
            return True

        g = groupaddress.split('/')
        if len(g) != 3:
            return False
        if not (Utils.is_int(g[0]) and Utils.is_int(g[1]) and Utils.is_int(g[2])):
            return False
        if (int(g[0]) < 0) or (int(g[0]) > 31):
            return False
        if (int(g[1]) < 0) or (int(g[1]) > 7):
            return False
        if (int(g[2]) < 0) or (int(g[2]) > 255):
            return False
        return True

    @staticmethod
    def is_timeframe(string: str) -> bool:
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
    def to_timeframe(value: str) -> int:  # works for Python 3.9 and under
        #    def to_timeframe(value: str | int) -> int:  # works for Python 3.10 and above
        """
        Converts a timeframe value to milliseconds. See is_timeframe() method.
        The special value 'now' is supported for the current time.

        :param value : value to convert
        :type value: str, int, ...

        :return: True if cant be converted and is true, False otherwise.
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
    def is_int(string: str) -> bool:
        """
        Checks if a string is a integer.

        :param string: String to check.

        :return: True if a cast to int works, false otherwise.
        """

        try:
            int(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def is_float(string: str) -> bool:
        """
        Checks if a string is a float.

        :param string: String to check.

        :return: True if a cast to float works, false otherwise.
        """

        try:
            float(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def to_bool(value: str, default: bool = 'exception') -> bool:  # works for Python 3.9 and under
        #    def to_bool(value: str|int|float, default: bool='exception') -> bool:   # works for Python 3.10 and above

        """
        Converts a value to boolean.

        Raises exception if value is a string and can't be converted and if no default value is given
        Case is ignored. These string values are allowed:
        - True: 'True', "1", "true", "yes", "y", "t", "on"
        - False: "", "0", "faLse", "no", "n", "f", "off"
        Non-string values are passed to bool constructor.

        :param value : value to convert
        :param default: optional, value to return if value can not be parsed, if default is not set this method throws an exception

        :return: True if cant be converted and is true, False otherwise.
        """
        # -> should it be possible to cast strings: 0 -> False and non-0 -> True (analog to integer values)?
        if isinstance(value, str):
            if value.lower() in ('yes', 'y', 'true', 't', '1', 'on'):
                return True
            if value.lower() in ('no', 'n', 'false', 'f', '0', 'off', ''):
                return False
            if default == 'exception':
                raise Exception('Invalid value for boolean conversion: ' + value)
            else:
                return default
        return bool(value)

    @staticmethod
    def create_hash(plaintext: str) -> str:
        """
        Create hash (currently sha512) for given plaintext value

        :param plaintext: plaintext

        :return: hash of plaintext, lowercase letters
        """

        hashfunc = hashlib.sha512()
        hashfunc.update(plaintext.encode())
        return ''.join(format(b, '02x') for b in hashfunc.digest())

    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Create a salted hash of a password for the configuration (e.g. ``hashed_password`` of the http module)

        The format is ``pbkdf2_sha256$<iterations>$<salt>$<digest>`` (salt and digest base64 encoded),
        so the work factor can be raised later without invalidating existing hashes.

        :param plaintext: password, must not be empty

        :return: salted password hash
        """
        if not plaintext:
            raise ValueError('an empty password cannot be hashed')
        return _salted_hash(PASSWORD_HASH_ALGORITHM, plaintext)

    @staticmethod
    def wrap_legacy_password_hash(legacy_hash: str) -> str:
        """
        Turn an unsalted sha512 password hash into a salted one without knowing the password

        The result has the format ``pbkdf2_sha256_sha512$<iterations>$<salt>$<digest>``: the PBKDF2 input is the
        legacy hash, so check_hashed_password() derives it from the sha512 hash of the password to check.

        :param legacy_hash: sha512 hash as created by create_hash() (128 hex characters, any case)

        :return: salted password hash
        """
        if not Utils.is_legacy_password_hash(legacy_hash):
            raise ValueError('not an unsalted sha512 password hash')
        return _salted_hash(WRAPPED_HASH_ALGORITHM, legacy_hash.lower())

    @staticmethod
    def is_hash(value: str) -> bool:
        """
        Check if value is a password hash: a salted hash (hash_password(), wrap_legacy_password_hash()) or a
        legacy sha512 hash

        :param value: value to check

        :return: True: given value is a password hash, False: given value is no password hash
        """
        return _parse_salted_hash(value) is not None or Utils.is_legacy_password_hash(value)

    @staticmethod
    def is_legacy_password_hash(value: str) -> bool:
        """
        Check if value is an unsalted sha512 hash (128 hex characters), the password hash format before v2.0

        Such hashes are still accepted, but should be replaced by one created with hash_password() or
        wrap_legacy_password_hash().

        :param value: value to check
        """
        if not isinstance(value, str) or len(value) != 128:
            return False
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_hashed_password(pwd_to_check: str, hashed_pwd: str) -> bool:
        """
        Check if given plaintext password matches the hashed password
        An empty password is always rejected

        Salted hashes (hash_password(), wrap_legacy_password_hash()) and legacy sha512 hashes are accepted. Results for salted hashes
        are cached, since the key derivation is deliberately slow and http basic auth checks every request.

        :param pwd_to_check: plaintext password to check
        :param hashed_pwd: hashed password

        :return: True: password matches, False: password does not match
        """

        if pwd_to_check is None or pwd_to_check == '':
            # No password given -> return "not matching"
            return False

        parsed = _parse_salted_hash(hashed_pwd)
        if parsed is not None:
            algorithm, iterations, salt, digest = parsed
            secret = Utils.create_hash(pwd_to_check) if algorithm == WRAPPED_HASH_ALGORITHM else pwd_to_check
            return _pbkdf2_matches(secret, iterations, salt, digest)
        if Utils.is_legacy_password_hash(hashed_pwd):
            return hmac.compare_digest(Utils.create_hash(pwd_to_check), hashed_pwd.lower())
        return False

    @staticmethod
    def strip_quotes(string: str) -> str:
        """
        If a string contains quotes as first and last character, this function
        returns the string without quotes, otherwise the string is returned unchanged

        :param string: string to check for quotes

        :return: string with quotes stripped
        """
        if type(string) is str:
            string = string.strip()
            if len(string) >= 2:
                if string[0] in ['"', "'"]:  # check if string starts with ' or "
                    if string[-1] == string[0]:  # and end with it
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
                    er = float(er)
                else:
                    er = int(er)
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
                if string[0] == '[':  # check if string starts with [
                    if string[-1] == ']':  # and end with ]
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
    def dewpoint(t: float, rf: float) -> float:
        """
        Return the dew point (Magnus formula)

        :param t: temperature in degrees Celsius
        :param rf: relative humidity in percent (0 < rf <= 100)

        :return: dew point in degrees Celsius, rounded to two decimals
        """
        log = math.log((rf + 0.01) / 100)  # + 0.01 to 'cast' float
        return round((241.2 * log + 4222.03716 * t / (241.2 + t)) / (17.5043 - log - 17.5043 * t / (241.2 + t)), 2)

    @staticmethod
    def rel2abs(t: float, rf: float) -> float:
        """
        Return the absolute humidity from the relative humidity and the temperature

        :param t: temperature in degrees Celsius
        :param rf: relative humidity in percent, or as a fraction (values up to 1)

        :return: absolute humidity in g/m3
        """
        t += 273.15
        if rf > 1:
            rf /= 100
        sat = 611.0 * math.exp(-2.5e6 * 18.0160 / 8.31432e3 * (1.0 / t - 1.0 / 273.16))
        mix = 18.0160 / 28.9660 * rf * sat / (100000 - rf * sat)
        rhov = 100000 / (287.0 * (1 - mix) + 462.0 * mix) / t
        return mix * rhov * 1000

    @staticmethod
    def abs2rel(t: float, ah: float) -> float:
        """
        Return the relative humidity from the absolute humidity and the temperature

        :param t: temperature in degrees Celsius
        :param ah: absolute humidity

        :return: relative humidity in percent
        """
        T = t + 273.15
        ah = ah / 1000
        sat_p = math.exp(77.3450 + 0.0057 * T - 7235 / T) / math.pow(T, 8.2)
        sat_density = 0.0022 * sat_p / T
        return ah / sat_density * 100

    @staticmethod
    def execute_subprocess(commandline, wait=True):
        """
        Executes a subprocess via a shell and returns the output written to stdout and stderr

        :return: tuple (stdout, stderr) as strings
        """
        return _run_shell(commandline, wait, subprocess.PIPE)


# --------------------------------------------------------------------------------------------


class Version:
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
            if v and v[-1].isalpha():
                build += ord(v[-1].lower()) - 96
                v = v[:-1]
            vi = 0
            try:
                vi = int(v)
            except Exception:
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
        vers = '.'.join(versls)

        return 'v' + vers

    _SEMVER_RE = re.compile(r'^v?(?P<core>\d+(?:\.\d+)*)(?:-(?P<pre>[0-9A-Za-z.-]+))?(?:\+(?P<build>[0-9A-Za-z.-]+))?$')

    @classmethod
    def _split(cls, vers):
        """
        Split a version string of the form [v]N[.N...][-prerelease][+build]

        :param vers: version string
        :type vers: str

        :return: numeric parts (padded/cut to 4), prerelease and build (None if absent), or None if vers is not of that form
        :rtype: tuple or None
        """
        m = cls._SEMVER_RE.match(vers)
        if m is None:
            return None
        numbers = cls.check_list([int(n) for n in m.group('core').split('.')])
        return numbers, m.group('pre'), m.group('build')

    _STRICT_SEMVER_RE = re.compile(
        r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
        r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
        r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )

    @classmethod
    def is_semver(cls, vers):
        """
        Test if a string is a valid Semantic Versioning 2.0.0 version (semver.org, rule 2, 9 and 10)

        :param vers: version
        :type vers: str

        :return: True if vers is MAJOR.MINOR.PATCH with optional pre-release and build metadata
        :rtype: bool
        """
        return cls._STRICT_SEMVER_RE.match(vers) is not None

    @staticmethod
    def strip_build(vers):
        """
        Remove the build metadata ('+...') from a version string

        :param vers: version
        :type vers: str

        :return: version without build metadata
        :rtype: str
        """
        return vers.split('+', 1)[0]

    @classmethod
    def format(cls, vers):
        """
        Normalize a version to 'v' + at least three numeric parts, keeping prerelease and build metadata

        :param vers: version
        :type vers: str

        :return: normalized version, '' for an empty version
        :rtype: str
        """
        vers = str(vers)
        parts = cls._split(vers)
        if parts is None:
            return cls.to_string(cls.to_list(vers))
        numbers, pre, build = parts
        core = cls.to_string(numbers)
        if core == '':
            return ''
        return core + ('' if pre is None else '-' + pre) + ('' if build is None else '+' + build)

    @classmethod
    def _precedence_key(cls, vers):
        """
        Build a sort key implementing semver precedence for a version string

        Strings that are not of the form [v]N[.N...][-prerelease][+build] (e.g. legacy letter
        suffixes like '1.2.3a') are ordered by their legacy list form, as releases.

        :param vers: version string
        :type vers: str

        :return: key which orders like the version
        :rtype: tuple
        """
        parts = cls._split(vers)
        if parts is None:
            return cls.to_list(vers), (1,)
        numbers, pre, _ = parts
        if pre is None:
            return numbers, (1,)
        # numeric identifiers rank below alphanumeric ones, which compare in ASCII order
        return numbers, (0, tuple((0, int(i), '') if i.isdigit() else (1, 0, i) for i in pre.split('.')))

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
        if isinstance(v1, str) and isinstance(v2, str):
            v1 = cls._precedence_key(v1)
            v2 = cls._precedence_key(v2)
        else:
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


# --------------------------------------------------------------------------------------------


def get_python_version():
    PYTHON_VERSION = (
        str(sys.version_info[0])
        + '.'
        + str(sys.version_info[1])
        + '.'
        + str(sys.version_info[2])
        + ' '
        + str(sys.version_info[3])
    )
    if sys.version_info[3] != 'final':
        PYTHON_VERSION += ' ' + str(sys.version_info[4])
    return PYTHON_VERSION


def execute_subprocess(commandline, wait=True):
    """
    Executes a subprocess via a shell and returns the output written to stdout by this process as a string

    The output to stderr is not captured.
    """
    return _run_shell(commandline, wait, None)[0]


def _run_shell(commandline, wait, stderr):
    """
    Run ``commandline`` through the shell and return its decoded (stdout, stderr).

    :param wait: wait for the process to terminate after its output has been read
    :param stderr: subprocess.PIPE to capture stderr, None to leave it to the parent
    """
    p = subprocess.Popen(commandline, stdout=subprocess.PIPE, stderr=stderr, shell=True)
    result, err = p.communicate()
    if wait:
        p.wait()
    return str(result, encoding='utf-8', errors='strict'), str(err or b'', encoding='utf-8', errors='strict')


def running_virtual():
    """
    Return if we run in a virtual environment (venv or virtualenv).
    """

    # The check for sys.real_prefix covers virtualenv,
    # the equality of non-empty sys.base_prefix with sys.prefix covers venv.
    return getattr(sys, 'base_prefix', sys.prefix) != sys.prefix or hasattr(sys, 'real_prefix')
