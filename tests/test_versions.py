#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2021-     Martin Sinn                          m.sinn@gmx.de
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

from . import common
import unittest
import logging

from lib.model.smartplugin import SmartPlugin

from tests.mock.core import MockSmartHome


logger = logging.getLogger(__name__)

#from lib.utils import Version
from lib.utils import Version


#----------------------------------------------------------

# def test_version_to_list(vers):
#     versl = Version.to_list(vers)
#     versd = Version.to_string(versl)
#     print(f"{vers:12} -> {str(versl):14} -> {versd}")
#
#     return
#
#
# def test_version_compare(vers1, vers2, operator):
#     result = Version.compare(vers1, vers2, operator)
#     print(f"v1={str(vers1):15} v2={str(vers2):15}, op= {operator:2} -> {result}")


#----------------------------------------------------------

class TestModule(unittest.TestCase):


    def test_version_numbers(self):

        logger.warning('')
        logger.warning('=== Begin test_version_numbers:')

        # test_version_to_list('1.2.1')
        # test_version_to_list('v1.2.1')
        # test_version_to_list('1.2.1a')

        self.assertEqual([1,2,1,0], Version.to_list('1.2.1'))
        self.assertEqual([1,2,1,0], Version.to_list('v1.2.1'))
        self.assertEqual([1,2,1,1], Version.to_list('1.2.1a'))

        self.assertEqual('v1.2.1', Version.to_string([1,2,1,0]))
        self.assertEqual('v1.2.1.1', Version.to_string([1,2,1,1]))

        # test_version_to_list('1.2')
        # test_version_to_list('v1.2')
        # test_version_to_list('1.2a')

        self.assertEqual([0,0,0,0], Version.to_list(''))
        self.assertEqual([1,2,0,0], Version.to_list('1.2'))
        self.assertEqual([1,2,0,0], Version.to_list('v1.2'))

        self.assertEqual('v1.2.0', Version.to_string([1,2,0,0]))
        self.assertEqual('v1.2.1', Version.to_string([1,2,1,0]))

        # test_version_to_list('1.2.3.4.5')
        # test_version_to_list('v1.2a.3.4.5')
        # test_version_to_list('1.2a.3a.4.5')

        self.assertEqual([1,2,3,4], Version.to_list('1.2.3.4.5'))
        self.assertEqual([1,2,3,5], Version.to_list('v1.2a.3.4.5'))
        self.assertEqual([1,2,3,6], Version.to_list('1.2a.3a.4.5'))

        # test_version_to_list('')
        # test_version_to_list('1.9.0.1')

        self.assertEqual([1,2,0,1], Version.to_list('1.2a'))
        self.assertEqual([1,9,0,1], Version.to_list('1.9.0.1'))

        # test_version_compare('1.2', '1.3', '<')
        # test_version_compare('1.2', '1.3', '>')
        # test_version_compare('1.2', '1.3', '=')
        # test_version_compare('1.2', '1.3', '<=')
        # test_version_compare('1.2', '1.3', '>=')

        self.assertTrue(Version.compare('1.2', '1.3', '<'))
        self.assertFalse(Version.compare('1.2', '1.3', '>'))
        self.assertFalse(Version.compare('1.2', '1.3', '='))
        self.assertTrue(Version.compare('1.2', '1.3', '<='))
        self.assertFalse(Version.compare('1.2', '1.3', '>='))

        # test_version_compare('1.2.3a', [1,2,3,4,5], '<')
        # test_version_compare('1.2.3a', [1,2,3,104,5], '<')
        # test_version_compare('1.2', '1.2.3.4.5', '>')
        # test_version_compare('1.2', '1.2.3.4.5', '=')
        # test_version_compare('1.2', '1.2.3.4.5', '<=')
        # test_version_compare('1.2', '1.2.3.4.5', '>=')

        self.assertTrue(Version.compare('1.2.3a', [1,2,3,4,5], '<'))
        self.assertTrue(Version.compare('1.2.3a', [1,2,3,104,5], '<'))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '>'))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '='))
        self.assertTrue(Version.compare('1.2', '1.2.3.4.5', '<='))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '>='))

        logger.warning('=== End test_version_numbers:')

if __name__ == '__main__':
    unittest.main(verbosity=2)

