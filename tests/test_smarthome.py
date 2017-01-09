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
import bin.smarthome
import os


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
    def testDirs(self):
        sh = bin.smarthome.SmartHome
        print (sh.base_dir)

        base_dir = sh.base_dir

        _plugin_conf_basename = os.path.join(base_dir + '/etc/plugin'.replace('/', os.path.sep))
        self.assertEqual(sh._plugin_conf_basename,_plugin_conf_basename)
        _plugin_conf = ''  # is filled by plugin.py while reading the configuration file, needed by Backend plugin
        self.assertEqual(sh._plugin_conf,_plugin_conf)
        _env_dir = os.path.join(base_dir + '/lib/env/'.replace('/', os.path.sep))
        self.assertEqual(sh._env_dir,_env_dir)
        _env_logic_conf_basename = os.path.join((_env_dir + 'logic').replace('/', os.path.sep))
        self.assertEqual(sh._env_logic_conf_basename,_env_logic_conf_basename)
        _items_dir = os.path.join(base_dir + '/items/'.replace('/', os.path.sep))
        self.assertEqual(sh._items_dir, _items_dir)
        _logic_conf_basename = os.path.join(base_dir + '/etc/logic'.replace('/', os.path.sep))
        self.assertEqual(sh._logic_conf_basename, _logic_conf_basename)
        _logic_dir = os.path.join(base_dir + '/logics/'.replace('/', os.path.sep))
        self.assertEqual(sh._logic_dir,_logic_dir)
        _cache_dir = os.path.join(base_dir + '/var/cache/'.replace('/', os.path.sep))
        self.assertEqual(sh._cache_dir,_cache_dir)
        _log_config = os.path.join(base_dir + '/etc/logging.yaml'.replace('/', os.path.sep))
        self.assertEqual(sh._log_config, _log_config)
        #_pidfile = os.path.join(base_dir + '/var/run/smarthome.pid'.replace('/', os.path.sep))
        #self.assertEqual(sh.PIDFILE,_pidfile)

if __name__ == '__main__':
    unittest.main(verbosity=2)
