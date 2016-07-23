#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Strassburg  c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
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
#  along with SmartHomeNG If not, see <http://www.gnu.org/licenses/>.
#########################################################################
import common
import unittest
from lib.utils import Utils
#from wakeonlan import WakeOnLan
class LibUtilsTest(unittest.TestCase):

    def test_is_mac(self):
        self.assertTrue(True)
        self.assertTrue(Utils.is_mac("11:22:33:44:55:66"))
        self.assertTrue(Utils.is_mac("11-22-33-44-55-66"))
        self.assertTrue(Utils.is_mac("11 22 33 44 55 66"))
        self.assertTrue(Utils.is_mac("112233445566"))
        self.assertTrue(Utils.is_mac("000000000000"))
        self.assertTrue(Utils.is_mac("ffffffffffff"))
        self.assertFalse(Utils.is_mac("1r2233445566"))
        self.assertFalse(Utils.is_mac("gggggggggggg"))
        self.assertFalse(Utils.is_mac("1g:22:33:44:55:66"))
        self.assertFalse(Utils.is_mac(None))
        self.assertFalse(Utils.is_mac(""))
        self.assertFalse(Utils.is_mac(self))

    def test_is_ip(self):
        self.assertFalse(Utils.is_ip(""))
        self.assertFalse(Utils.is_ip(None))
        self.assertFalse(Utils.is_ip(self))

        self.assertTrue(Utils.is_ip("1.2.3.4"))
        self.assertTrue(Utils.is_ip("0.0.0.0"))
        self.assertTrue(Utils.is_ip("255.255.255.255"))
        self.assertFalse(Utils.is_ip("256.256.256.256"))
        self.assertFalse(Utils.is_ip("2561.256.256.256"))
        self.assertFalse(Utils.is_ip("561.256.256.256"))
        self.assertFalse(Utils.is_ip("161.256.256"))
        self.assertTrue(Utils.is_ip("10.0.0.173"))

    def test_is_int(self):
        self.assertFalse(Utils.is_int(""))
        self.assertFalse(Utils.is_int(None))
        self.assertFalse(Utils.is_int(self))

        self.assertFalse(Utils.is_int("1.2.3.4"))
        self.assertFalse(Utils.is_int("xyzabcd"))
        self.assertFalse(Utils.is_int("1.0"))
        self.assertTrue(Utils.is_int("255"))
        self.assertTrue(Utils.is_int("0"))
        self.assertTrue(Utils.is_int("-1"))

    def test_is_float(self):
        self.assertFalse(Utils.is_float(""))
        self.assertFalse(Utils.is_float(None))
        self.assertFalse(Utils.is_float(self))

        self.assertFalse(Utils.is_float("1.2.3.4"))
        self.assertFalse(Utils.is_float("xyzabcd"))
        self.assertTrue(Utils.is_float("255"))
        self.assertTrue(Utils.is_float("0"))
        self.assertTrue(Utils.is_float("-1"))
        self.assertTrue(Utils.is_float("1.0"))
        self.assertTrue(Utils.is_float("0.0"))
        self.assertTrue(Utils.is_float("5.0"))
        self.assertTrue(Utils.is_float("-5.0"))
        self.assertTrue(Utils.is_float("2.01"))
        self.assertTrue(Utils.is_float("-2.01"))

    def test_to_bool(self):
        with self.assertRaises(Exception):
            Utils.to_bool("161.256.256")
        
       # with self.assertRaises(Exception):
       #     Utils.to_bool(self)
        self.assertFalse(Utils.to_bool(None))
        self.assertFalse(Utils.to_bool(False))
        self.assertFalse(Utils.to_bool("No"))
        self.assertFalse(Utils.to_bool("0"))
        self.assertFalse(Utils.to_bool(""))
        self.assertFalse(Utils.to_bool("n"))
        self.assertFalse(Utils.to_bool("false"))
        self.assertFalse(Utils.to_bool("False"))
        self.assertFalse(Utils.to_bool("f"))
        self.assertFalse(Utils.to_bool(0))

        self.assertTrue(Utils.to_bool(1.2))
        self.assertTrue(Utils.to_bool(True))
        self.assertTrue(Utils.to_bool("yes"))
        self.assertTrue(Utils.to_bool("1"))
        self.assertTrue(Utils.to_bool("y"))
        self.assertTrue(Utils.to_bool("true"))
        self.assertTrue(Utils.to_bool("True"))
        self.assertTrue(Utils.to_bool("t"))
        self.assertTrue(Utils.to_bool(1))

if __name__ == '__main__':
    unittest.main(verbosity=2)
