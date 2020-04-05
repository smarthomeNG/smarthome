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
from . import common
import unittest
import logging
import os
import tempfile

import bin.smarthome
from lib.constants import YAML_FILE


logger = logging.getLogger(__name__)

class SmarthomeTest(unittest.TestCase):
    def test_to_bool(self):

        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, None))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, False))
        self.assertIsNone(bin.smarthome.SmartHome.string2bool(self, "werwer"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "No"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "0"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, ""))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "n"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "false"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "False"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, "f"))
        self.assertFalse(bin.smarthome.SmartHome.string2bool(self, 0))

        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,1.2))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,True))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"yes"))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"1"))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"y"))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"true"))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"True"))
        self.assertTrue(bin.smarthome.SmartHome.string2bool(self,"t"))
        # self.assertTrue(bin.smarthome.SmartHome.string2bool(self,1))

    #####################################################################
    # Diplay DEPRECATED warning
    #####################################################################
    def _deprecated_warning(self, n_func=''):
        pass
        
         
    def testConfigInit(self):
        logger.warning('')
        logger.warning('=== Begin Smarthome Tests: testConfigInit')
        
        bin.smarthome.MODE = 'unittest'		# do not daemonize, do not log
        with tempfile.TemporaryDirectory(prefix='SHNG_config.') as ext_conf:
            os.mkdir(os.path.join(ext_conf, 'etc'))
            os.mkdir(os.path.join(ext_conf, 'items'))
            os.mkdir(os.path.join(ext_conf, 'logics'))

            for sh_config in [None, ext_conf]:
                if sh_config is None:
                    sh = bin.smarthome.SmartHome()
                    conf_dir = sh.base_dir
                else:
                    sh = bin.smarthome.SmartHome(extern_conf_dir=sh_config)
                    conf_dir = sh_config
                logger.warning("    test with config files in folder {}".format(conf_dir))
                base_dir = sh.base_dir
                sh.alive = False
                logger.warning("        check paths & basenames")
                _etc_dir = os.path.join(conf_dir, 'etc')
                self.assertEqual(sh._etc_dir, _etc_dir)
                _items_dir = os.path.join(conf_dir, 'items' + os.path.sep)
                self.assertEqual(sh._items_dir, _items_dir)
                _logic_dir = os.path.join(conf_dir, 'logics' + os.path.sep)
                self.assertEqual(sh._logic_dir, _logic_dir)

                _plugin_conf_basename = os.path.join(_etc_dir, 'plugin')
                self.assertEqual(sh._plugin_conf_basename, _plugin_conf_basename)
                _logic_conf_basename = os.path.join(_etc_dir, 'logic')
                self.assertEqual(sh._logic_conf_basename, _logic_conf_basename)
                _log_conf_basename = os.path.join(_etc_dir, 'logging')
                self.assertEqual(sh._log_conf_basename, _log_conf_basename)
                _module_conf_basename = os.path.join(_etc_dir, 'module')
                self.assertEqual(sh._module_conf_basename, _module_conf_basename)

                _cache_dir = os.path.join(base_dir, 'var', 'cache' + os.path.sep)
                self.assertEqual(sh._cache_dir, _cache_dir)
                _env_dir = os.path.join(base_dir, 'lib', 'env' + os.path.sep)
                self.assertEqual(sh._env_dir, _env_dir)
                _env_logic_conf_basename = os.path.join(_env_dir, 'logic')
                self.assertEqual(sh._env_logic_conf_basename, _env_logic_conf_basename)

                logger.warning("        check if .default files are installed")
                configs = ['logging', 'smarthome', 'module', 'plugin']
                
                for c in configs:
                    self.assertTrue(os.path.isfile(os.path.join(_etc_dir, c + YAML_FILE)))

        logger.warning('=== End Smarthome Tests: testConfigInit')


if __name__ == '__main__':
    unittest.main(verbosity=2)
