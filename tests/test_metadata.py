#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2017-       Martin Sinn                         m.sinn@gmx.de
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
import logging

from lib.metadata import Metadata

from tests.mock.core import MockSmartHome


logger = logging.getLogger(__name__)

class LibMetadataTest(unittest.TestCase):

#    def setUp(self):
#        self.sh = MockSmartHome()
#        self.modules = self.sh.with_modules_from(common.BASE + "/tests/resources/module")

#    def test_check_parameters(self):

    def test_meta_is_registered(self):
        logger.warning('')
        logger.warning('=== Begin Metadata Tests:')

        self.sh = MockSmartHome()
        self.meta = Metadata(self.sh, 'test_resources', 'module', 'tests.resources.test_metadata')
        print()
        print('self.meta: {}'.format(self.meta))
        print()

        args = {}
        # (processed_args, allparams_ok) = self.meta.check_parameters(args)
        (processed_args, allparams_ok, hide_params) = self.meta.check_parameters(args)

        # Test default values for datatypes
        self.assertIsNone(processed_args.get('notype_nodefault', None))
        self.assertEqual(False, processed_args['bool_nodefault'])
        self.assertEqual(0, processed_args['int_nodefault'])
        self.assertEqual(2, processed_args['int_validmin_nodefault'])
        self.assertEqual(-42, processed_args['int_validmax_nodefault'])
        self.assertEqual(0, processed_args['pint_nodefault'])
        self.assertEqual(0, processed_args['float_nodefault'])
        self.assertEqual(0, processed_args['pfloat_nodefault'])
        self.assertEqual('', processed_args['str_nodefault'])
        self.assertEqual('', processed_args['str_validlist_nodefault'])
        self.assertEqual([], processed_args['list_nodefault'])
        self.assertEqual({}, processed_args['dict_nodefault'])
        self.assertEqual('0.0.0.0', processed_args['ip_nodefault'])
        self.assertEqual('00:00:00:00:00:00', processed_args['mac_nodefault'])
        self.assertIsNone(processed_args['foo_nodefault'])

        # Test set default values for parameters
        self.assertEqual(42, processed_args['notype_default1'])
        self.assertEqual('42', processed_args['notype_default2'])
        self.assertEqual(True, processed_args['bool_default'])
        self.assertEqual(42, processed_args['int_default'])
        self.assertEqual(42, processed_args['pint_default'])
        self.assertEqual(4.2, processed_args['float_default'])
        self.assertEqual(4.2, processed_args['pfloat_default'])
        self.assertEqual('42', processed_args['str_default'])
        self.assertEqual('string2', processed_args['str_validlist_default'])
        self.assertEqual('string1', processed_args['str_validlist_invalid_default'])
        self.assertEqual([4,2], processed_args['list_default'])
        self.assertEqual({'answer': 42}, processed_args['dict_default'])
        self.assertEqual('127.0.0.1', processed_args['ip_default'])
        self.assertEqual('01:23:45:67:89:ab', processed_args['mac_default'])
        self.assertEqual(42, processed_args['foo_default'])

        args = {
            'notype_nodefault': True, 'bool_nodefault': '42', 'int_nodefault': -24, 'pint_nodefault': 24,
            'float_nodefault': -24.2, 'pfloat_nodefault': 24.3, 'str_nodefault': 'answer', 'str_validlist_nodefault': 'string2',
            'str_validlist_default': 'x', 'str_validlist_invalid_default': 'string2',
            'list_nodefault': [24,42], 'dict_nodefault': {'question': 24, 'answer': '42'},
            'ip_nodefault': '1.2.3.4', 'mac_nodefault': 'aa:ab:ac:ad:ae:af',
            'foo_nodefault': [4, 2],
            'notype_default1': '24', 'notype_default2': 24, 'bool_default': True, 'int_default': '-x', 'pint_default': -24,
            'float_default': '-x', 'pfloat_default': -24.2, 'str_default': 25,
            'list_default': "[24,'42', 4.2, '4.2']", 'dict_default': {24, '42'},
            'ip_default': '1.2.3.256', 'mac_default': 'aa:ab:ac:ad:ae:ag',
            'foo_default': ['4', 2, [4, '2']]
        }
        # (processed_args, allparams_ok) = self.meta.check_parameters(args)
        (processed_args, allparams_ok, hide_params) = self.meta.check_parameters(args)
        logger.warning("\n=== processed_args: {}".format(processed_args))
        logger.warning("\n=== allparams_ok: {}".format(allparams_ok))
        logger.warning("\n=== hide_params: {}\n".format(hide_params))

        # Test valid parameter configurations
        #self.assertEqual(True, processed_args.get('notype_nodefault', None))
        self.assertEqual(False, processed_args['bool_nodefault'])
        self.assertEqual(-24, processed_args['int_nodefault'])
        self.assertEqual(24, processed_args['pint_nodefault'])
        self.assertEqual(-24.2, processed_args['float_nodefault'])
        self.assertEqual(24.3, processed_args['pfloat_nodefault'])
        self.assertEqual('answer', processed_args['str_nodefault'])
        self.assertEqual('string2', processed_args['str_validlist_nodefault'])
        self.assertEqual([24,42], processed_args['list_nodefault'])
        self.assertEqual({'question': 24, 'answer': '42'}, processed_args['dict_nodefault'])
        self.assertEqual('1.2.3.4', processed_args['ip_nodefault'])
        self.assertEqual('aa:ab:ac:ad:ae:af', processed_args['mac_nodefault'])
        self.assertEqual([4, 2], processed_args['foo_nodefault'])


        # Test invalid parameter configurations
        self.assertEqual('24', processed_args['notype_default1'])
        self.assertEqual(24, processed_args['notype_default2'])
        self.assertTrue(processed_args['bool_default'])
        self.assertEqual(42, processed_args['int_default'])               # default value taken (42 instead of '-x')
        self.assertEqual(0, processed_args['pint_default'])               # valid_min value taken, not default value (0 instead of -24)
        self.assertEqual(4.2, processed_args['float_default'])            # default value taken (42 instead of '-x')
        self.assertEqual(0, processed_args['pfloat_default'])             # valid_min value taken, not default value (0 instead of -24)
        self.assertEqual('25', processed_args['str_default'])             # default value not taken, because 25 can be converted to '25'
        self.assertEqual('string1', processed_args['str_validlist_default'])  # default value taken ('string1' instead of 'x')
        self.assertEqual('string2', processed_args['str_validlist_invalid_default'])
        self.assertEqual([24,'42', 4.2, '4.2'], processed_args['list_default'])       # Test list with mixed datatypes
        self.assertEqual({'answer': 42}, processed_args['dict_default'])  # default value taken ({'answer': 42} instead of invalid dict {24, '42'})
        self.assertEqual('127.0.0.1', processed_args['ip_default'])       # default value taken ('127.0.0.1' instead of invalid ip '1.2.3.256')
        self.assertEqual('01:23:45:67:89:ab', processed_args['mac_default'])  # default value taken (instead of invalid mac 'aa:ab:ac:ad:ae:ag')
        self.assertEqual(['4', 2, [4, '2']], processed_args['foo_default'])   # accepts any data (no default is taken, if a value is specified)

        logger.warning('=== End metadata Tests')



if __name__ == '__main__':
    unittest.main(verbosity=2)
