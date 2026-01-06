#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016- Christian Strassburg              c.strassburg@gmx.de
#  Copyright 2017- Serge Wagener                     serge@wagener.family
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
from . import common
import unittest
from lib.utils import Utils
#from wakeonlan import WakeOnLan
class LibUtilsTest(unittest.TestCase):

    def test_is_knx_groupaddress(self):
        self.assertFalse(Utils.is_knx_groupaddress("1/2"))
        self.assertTrue(Utils.is_knx_groupaddress("1/2/3"))
        self.assertFalse(Utils.is_knx_groupaddress("-1/2/3"))
        self.assertFalse(Utils.is_knx_groupaddress("32/2/3"))
        self.assertFalse(Utils.is_knx_groupaddress("1/-1/3"))
        self.assertFalse(Utils.is_knx_groupaddress("1/8/3"))
        self.assertFalse(Utils.is_knx_groupaddress("1/2/-1"))
        self.assertFalse(Utils.is_knx_groupaddress("1/2/256"))
        self.assertFalse(Utils.is_knx_groupaddress("a/2/3"))
        self.assertFalse(Utils.is_knx_groupaddress("1/a/3"))
        self.assertFalse(Utils.is_knx_groupaddress("1/2/a"))


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

    def test_is_ipv4(self):
        self.assertFalse(Utils.is_ip(""))
        self.assertFalse(Utils.is_ip(None))
        self.assertFalse(Utils.is_ip(self))

        self.assertTrue(Utils.is_ip("1.2.3.4"))
        self.assertTrue(Utils.is_ip("0.0.0.0"))
        self.assertTrue(Utils.is_ip("255.255.255.255"))
        self.assertFalse(Utils.is_ip("256.256.256.256"))
        self.assertFalse(Utils.is_ip("256.1.1.1"))
        self.assertFalse(Utils.is_ip("1.256.1.1"))
        self.assertFalse(Utils.is_ip("1.1.256.1"))
        self.assertFalse(Utils.is_ip("1.1.1.256"))
        self.assertFalse(Utils.is_ip("2561.256.256.256"))
        self.assertFalse(Utils.is_ip("561.256.256.256"))
        self.assertFalse(Utils.is_ip("161.256.256"))
        self.assertTrue(Utils.is_ip("10.0.0.173"))

    def test_is_ipv6(self):
        self.assertFalse(Utils.is_ipv6(""))
        self.assertFalse(Utils.is_ipv6(None))
        self.assertFalse(Utils.is_ipv6(self))

        self.assertTrue(Utils.is_ipv6("1:2:3:4:5:6:7:8"))
        self.assertTrue(Utils.is_ipv6("2001:db8:a0b:12f0::1"))
        self.assertTrue(Utils.is_ipv6("FF02:0:0:0:0:0:0:2"))
        self.assertTrue(Utils.is_ipv6("F::1"))
        self.assertFalse(Utils.is_ipv6("G::1"))
        self.assertFalse(Utils.is_ipv6("AB:02:3008:8CFD:AB:02:3008:8CFD:02")) # tpp long
        self.assertFalse(Utils.is_ipv6("AB:02:3008:8CFD::02::8CFD")) # can't have two ::

    def test_is_timeframe(self):
        self.assertFalse(Utils.is_timeframe(""))
        self.assertFalse(Utils.is_timeframe("abc"))
        self.assertTrue(Utils.is_timeframe("1"))
        self.assertTrue(Utils.is_timeframe("1i"))
        self.assertTrue(Utils.is_timeframe("1h"))
        self.assertTrue(Utils.is_timeframe("1d"))
        self.assertTrue(Utils.is_timeframe("1m"))
        self.assertTrue(Utils.is_timeframe("1y"))

    def test_to_timeframe(self):
        with self.assertRaises(Exception):
            Utils.to_timeframe("")
        with self.assertRaises(Exception):
            Utils.to_timeframe("abc")
        with self.assertRaises(Exception):
            Utils.to_timeframe("1im")
        with self.assertRaises(Exception):
            Utils.to_timeframe("1abc")

        self.assertEqual(1, Utils.to_timeframe("1"))
        self.assertEqual(60000, Utils.to_timeframe("1i"))
        self.assertEqual(3600000, Utils.to_timeframe("1h"))
        self.assertEqual(86400000, Utils.to_timeframe("1d"))
        self.assertEqual(604800000, Utils.to_timeframe("1w"))
        self.assertEqual(2592000000, Utils.to_timeframe("1m"))
        self.assertEqual(31536000000, Utils.to_timeframe("1y"))

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
        self.assertFalse(Utils.to_bool("off"))
        self.assertFalse(Utils.to_bool(0))

        self.assertTrue(Utils.to_bool(1.2))
        self.assertTrue(Utils.to_bool(True))
        self.assertTrue(Utils.to_bool("yes"))
        self.assertTrue(Utils.to_bool("1"))
        self.assertTrue(Utils.to_bool("y"))
        self.assertTrue(Utils.to_bool("true"))
        self.assertTrue(Utils.to_bool("True"))
        self.assertTrue(Utils.to_bool("t"))
        self.assertTrue(Utils.to_bool("on"))
        self.assertTrue(Utils.to_bool(1))
        self.assertTrue(Utils.to_bool(2))

    def test_create_hash(self):
        with self.assertRaises(Exception):
            Utils.create_hash(None)
        self.assertEqual(Utils.create_hash(''), 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e')
        self.assertEqual(Utils.create_hash('42'), '39ca7ce9ecc69f696bf7d20bb23dd1521b641f806cc7a6b724aaa6cdbffb3a023ff98ae73225156b2c6c9ceddbfc16f5453e8fa49fc10e5d96a3885546a46ef4')
        self.assertEqual(Utils.create_hash('very_secure_password'), '1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d')
        self.assertEqual(Utils.create_hash('1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'), '00faf4a142f087e55edf6e91ea333d9a4bcd9b2d6bba8fab42869c6e00e28a3acba6d5fe3495f037221d633e01b3c7baa6e915028407548f77b5b9710899bfbe')

    def test_is_hash(self):
        self.assertTrue(Utils.is_hash('cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'))
        self.assertTrue(Utils.is_hash('39ca7ce9ecc69f696bf7d20bb23dd1521b641f806cc7a6b724aaa6cdbffb3a023ff98ae73225156b2c6c9ceddbfc16f5453e8fa49fc10e5d96a3885546a46ef4'))
        self.assertTrue(Utils.is_hash('1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))
        self.assertTrue(Utils.is_hash('00faf4a142f087e55edf6e91ea333d9a4bcd9b2d6bba8fab42869c6e00e28a3acba6d5fe3495f037221d633e01b3c7baa6e915028407548f77b5b9710899bfbe'))
        self.assertTrue(Utils.is_hash('1245A9633EDF47B7091F37C4D294B5BE5A9936C81C5359B16D1C4833729965663F1943EF240959C53803FEDEF7AC19BD59C66AD7E7092D7DBF155CE45884607D'))

        self.assertFalse(Utils.is_hash('1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c483372965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))
        self.assertFalse(Utils.is_hash('1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c48337299965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))
        self.assertFalse(Utils.is_hash('1245a9633edf47b7091f37c4d294b5be5a9936c8ic5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))
        self.assertFalse(Utils.is_hash(None))
        self.assertFalse(Utils.is_hash(12648430))
        self.assertFalse(Utils.is_hash(57005.48815))
        self.assertFalse(Utils.is_hash('The Problem with Popplers'))

    def test_check_hashed_password(self):
        # None or empty password should always be rejected
        self.assertFalse(Utils.check_hashed_password(None, 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'))
        self.assertFalse(Utils.check_hashed_password('', 'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e'))

        # Check some passwords
        self.assertTrue(Utils.check_hashed_password('42', '39ca7ce9ecc69f696bf7d20bb23dd1521b641f806cc7a6b724aaa6cdbffb3a023ff98ae73225156b2c6c9ceddbfc16f5453e8fa49fc10e5d96a3885546a46ef4'))
        self.assertTrue(Utils.check_hashed_password('very_secure_password', '1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))
        self.assertTrue(Utils.check_hashed_password('1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d', '00faf4a142f087e55edf6e91ea333d9a4bcd9b2d6bba8fab42869c6e00e28a3acba6d5fe3495f037221d633e01b3c7baa6e915028407548f77b5b9710899bfbe'))

        # Capital letters in hashed_password must not cause the password to be rejected
        self.assertTrue(Utils.check_hashed_password('very_secure_password', '1245A9633EDF47B7091F37C4D294B5BE5A9936C81C5359B16D1C4833729965663F1943EF240959C53803FEDEF7AC19BD59C66AD7E7092D7DBF155CE45884607D'))

        # Changing case in password must cause the password to be rejected
        self.assertFalse(Utils.check_hashed_password('Very_Secure_Password', '1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
