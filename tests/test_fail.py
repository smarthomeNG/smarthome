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

    def test_fail(self):

        logger.warning('')
        logger.warning('=== Begin Fail Test:')

        self.assertIsNotNone(None)

        logger.warning('=== End Fail Test')


if __name__ == '__main__':
    unittest.main(verbosity=2)

