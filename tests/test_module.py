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

from lib.model.smartplugin import SmartPlugin

from tests.mock.core import MockSmartHome


logger = logging.getLogger(__name__)


class TestModule(unittest.TestCase):
    def test_module_is_registered1(self):
        logger.warning('')
        logger.warning('=== Begin Module Tests:')

        self.sh = MockSmartHome()
        self.modules = self.sh.with_modules_from(common.BASE + '/tests/resources/module')
        self.assertIsNotNone(self.sh.modules.get_module('dummy'))
        self.assertIsNone(self.sh.modules.get_module('dummyX'))  # Test module ist not registered

        logger.warning('=== End Module Tests')

    def test_failed_load_does_not_reuse_previous_module_instance(self):
        """
        Regression test for lib.module.Modules._load_module(): a module whose
        class can't be resolved (bad classname) must fail cleanly and must not
        leave a previously-loaded module's instance registered under the new,
        failing module's name -- self.loadedmodule used to be reused as-is
        across loop iterations when the class-resolution exec() raised without
        being reassigned.
        """
        self.sh = MockSmartHome()
        self.modules = self.sh.with_modules_from(common.BASE + '/tests/resources/module_stale_reuse')

        good = self.modules.get_module('good')
        self.assertIsNotNone(good)
        self.assertEqual(good.__class__.__name__, 'dummy')

        # the failing module must not be registered at all
        self.assertIsNone(self.modules.get_module('broken'))

        # and must not have contaminated _modules/_moduledict with a second
        # reference to 'good's instance
        self.assertEqual(self.modules._modules.count(good), 1)
        self.assertEqual(list(self.modules._moduledict.values()).count(good), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
