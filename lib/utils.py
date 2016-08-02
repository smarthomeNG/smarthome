#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Strassburg  c.strassburg@gmx.de
#########################################################################
# Personal and non-commercial use only, redistribution is prohibited.
#########################################################################

import re
IP_REGEX = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}|0
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}|0
            |
              0x0*[0-9a-f]{1,2}
            )
          ){0,3}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)

class Utils(object):

    @staticmethod
    def is_mac(mac):
        """
        Validates a MAC address

        :param mac: MAC address
        :return: True if value is a MAC

        """
        mac = str(mac)
        if len(mac) == 12:
            for c in mac:
                try:
                    if int(c, 16) > 15:
                        return False
                except:
                    return False
            return True

        octets = re.split('[\:\-\ ]', mac)
        if len(octets) != 6:
            return False
        for i in octets:
            try:
                if int(i, 16) > 255:
                    return False
            except:
                return False
        return True

    @staticmethod
    def is_ip(string):
        """
        Checks if a string is a valid ip.
        :param string: String to check.
        :type string: str
        :return: True if an ip, false otherwise.
        :rtype: bool
        """
        try:
            return bool(IP_REGEX.search(string))
        except TypeError:
            return False

    @staticmethod
    def is_int(string):
        try:
            int(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def is_float(string):
        try:
            float(string)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    @staticmethod
    def to_bool(value):
        """
        Converts a value to boolean. 
        Raises exception if value is a string and can't be converted.
        Case is ignored. These string values are allowed
           True: 'True', "1", "true", "yes", "y", "t"
           False: "", "0", "faLse", "no", "n", "f"
        Non-string values are passed to bool constructor.
        :param value : value to convert
        :type value: str, object, int, ...
        :return: True if cant be converted and is true, False otherwise.
        :rtype: bool

        """
        if type(value) == type(''):
            if value.lower() in ("yes", "y", "true",  "t", "1"):
                return True
            if value.lower() in ("no",  "n", "false", "f", "0", ""):
                return False
            raise Exception('Invalid value for boolean conversion: ' + value)
        return bool(value)


