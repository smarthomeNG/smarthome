#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
# Copyright 2016      Christian Strassburg            c.strassburg@gmx.de
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

import lib.plugin
import lib.item
from lib.model.smartplugin import SmartPlugin
import threading

from lib.constants import (CONF_FILE, YAML_FILE)

from tests.mock.core import MockSmartHome

#ITEM_FILE_TYPE = CONF_FILE
ITEM_FILE_TYPE = YAML_FILE

verbose = False


logger = logging.getLogger(__name__)

class TestItem(unittest.TestCase):

    def props(self,cls):
        return [i for i in cls.__dict__.keys() if i[:1] != '_']


    def test__begin(self):
        logger.warning('')
        logger.warning('=== Begin Item Tests:')


    def test_zz_end(self):
        logger.warning('')
        logger.warning('=== End Item Tests.')


    def setUp(self):
        self.sh = MockSmartHome()


    def load_items(self, filename, filetype=None):
        logger.warning("\n\nload_items: ===  Begin of method  ==\n")
        if filetype == None:
            conf_filename = common.BASE + "/tests/resources/"+filename+ITEM_FILE_TYPE
        else:
            conf_filename = common.BASE + "/tests/resources/"+filename+filetype
        item_conf = None
        item_conf = lib.config.parse(conf_filename, item_conf)
        if item_conf == {}:
            logger.warning("\nconfig file '"+conf_filename+"' not found")
        if verbose == True:
            logger.warning('\nload_items: item_conf.items()={}'.format(str(item_conf.items())))
        #lib.item._items_instance = None
        #self.items = lib.item.Items(self)
        #self.sh.items = lib.item.Items(self)
        for attr, value in item_conf.items():
            logger.warning("\nload_items: attr={}, value={}\n".format(attr, value))
            if isinstance(value, dict):
                child_path = attr
                try:
                    #child = lib.item.Item(self.sh, self.sh, child_path, value)
                    #child = lib.item.item.Item(self.sh, self.sh, child_path, value)
                    child = self.create_item(self.sh, self.sh, child_path, value)
                except Exception as e:
                    logger.error("Item {}: problem creating: {}".format(child_path, e))
                else:
                    logger.warning("\nload_items: child_path={}, value={} -> child={}".format(attr, value, child))
                    vars(self.sh)[attr] = child
                    vars(self)[attr] = child
                    self.sh.add_item(child_path, child)
#                    self.items.add_item(child_path, child)
                    self.sh.children.append(child)

        items = self.sh.items.return_items()
        for i in items:
            logger.warning("\nload_items: self.sh.items i = {}".format(i))
        logger.warning("\nload_items: ===  End of method  ==\n")


    # ===================================================================
    # Following tests are about relative item addressing
    #
    def test_item_relative_references(self):
        """
        Tests various aspects around the handling of relative item references
        """
        if verbose == True:
            logger.warning('')
            logger.warning('===== test_item_relative_references:')

        # -----------------------------------------------------------------

#        if verbose == True:
#            logger.warning('')

        self.load_items('item_items')
        it = self.sh.items.return_item("item_tree")
        self.assertIsNotNone(it)

        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item")
        self.assertIsNotNone(it)
        self.assertEqual(it._type, 'bool')
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item.child")
        self.assertIsNotNone(it)
        self.assertEqual(it._type, 'foo')

        if verbose == True:
            logger.warning('')
            logger.warning('=== eval_trigger Tests:')
        # Attribute with relative references
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item")
        self.assertEqual(it.get_absolutepath('.', 'eval_trigger'), 'item_tree.grandparent.parent.my_item')
        self.assertEqual(it.get_absolutepath('.self', 'eval_trigger'), 'item_tree.grandparent.parent.my_item')
        self.assertEqual(it.get_absolutepath('.child', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child')
        self.assertEqual(it.get_absolutepath('.self.child', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child')
        self.assertEqual(it.get_absolutepath('.child.grandchild', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child.grandchild')
        self.assertEqual(it.get_absolutepath('..', 'eval_trigger'), 'item_tree.grandparent.parent')
        self.assertEqual(it.get_absolutepath('...', 'eval_trigger'), 'item_tree.grandparent')
        self.assertEqual(it.get_absolutepath('....', 'eval_trigger'), 'item_tree')
        self.assertEqual(it.get_absolutepath('.....', 'eval_trigger'), '')
        self.assertEqual(it.get_absolutepath('......', 'eval_trigger'), '')
        self.assertEqual(it.get_absolutepath('..sister', 'eval_trigger'), 'item_tree.grandparent.parent.sister')

        # Attribute w/o relative references
        self.assertEqual(it.get_absolutepath('item_tree.grandparent.parent.my_item', 'eval_trigger'), 'item_tree.grandparent.parent.my_item')
        self.assertEqual(it.get_absolutepath('abc', 'eval_trigger'), 'abc')

        if verbose == True:
            logger.warning('')
            logger.warning('=== eval Tests:')
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item")

        self.assertEqual(it.get_stringwithabsolutepathes('sh..child()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.child()')
        self.assertEqual(it.get_stringwithabsolutepathes('5*sh..child()', 'sh.', '(', 'eval'), '5*sh.item_tree.grandparent.parent.my_item.child()')
        self.assertEqual(it.get_stringwithabsolutepathes('5 * sh..child() + 4', 'sh.', '(', 'eval'), '5 * sh.item_tree.grandparent.parent.my_item.child() + 4')

        # tests for '.self' implementation
        self.assertEqual(it.get_stringwithabsolutepathes('sh..child.changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.child.changed_by()')
        self.assertNotEqual(it.get_stringwithabsolutepathes('sh...changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.changed_by()')
        self.assertEqual(it.get_stringwithabsolutepathes('sh.item_tree.grandparent.parent.my_item.changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.changed_by()')
        self.assertEqual(it.get_stringwithabsolutepathes('sh..self.changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.my_item.changed_by()')
        self.assertEqual(it.get_stringwithabsolutepathes('sh...changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.changed_by()')
        self.assertEqual(it.get_stringwithabsolutepathes('sh...self.changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.parent.changed_by()')
        self.assertNotEqual(it.get_stringwithabsolutepathes('sh.....changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.changed_by()')
        self.assertEqual(it.get_stringwithabsolutepathes('sh....self.changed_by()', 'sh.', '(', 'eval'), 'sh.item_tree.grandparent.changed_by()')

        if verbose == True:
            logger.warning('')
            logger.warning('=== plugin-attribute Tests:')
        # Attribute with relative references
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item")
        it.expand_relativepathes('sv_widget', "'", "'")
        self.assertEqual(it.conf['sv_widget'], "{{ basic.switch('id_schreibtischleuchte', 'item_tree.grandparent.parent.my_item.onoff') }}")

        # Attribute with relative references (sv_widget contains a list)
        it = self.sh.items.return_item("item_tree.svwidget_list")
        it.expand_relativepathes('sv_widget', "'", "'")
        # result should be a list
        self.assertEqual(isinstance(it.conf['sv_widget'],list), True)
        # length of list should be 2
        self.assertEqual(len(it.conf['sv_widget']), 2)
        # test both values of list (first w/o relative path, second with relative path)
        self.assertEqual(it.conf['sv_widget'][0], "{{ basic.switch('id_schreibtischleuchte1', 'item_tree.grandparent.parent.my_item.child.onoff') }}")
        self.assertEqual(it.conf['sv_widget'][1], "{{ basic.switch('id_schreibtischleuchte2', 'item_tree.grandparent.parent.my_item.child.onoff') }}")

        # Attribute w/o relative references
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item.child")
        orig = it.conf['sv_widget']
        it.expand_relativepathes('sv_widget', "'", "'")
        self.assertEqual(it.conf['sv_widget'], orig)
        self.assertEqual(it.conf['sv_widget'], "{{ basic.switch('id_schreibtischleuchte', 'item_tree.grandparent.parent.my_item.child.onoff') }}")

        # Tests for accessing internal attributes of items using relative adressing
        it = self.sh.items.return_item("item_tree.grandparent.parent.my_item")
        self.assertEqual(it.get_absolutepath('.child', 'eval_trigger'), 'item_tree.grandparent.parent.my_item.child')



    # ===================================================================
    # Following tests are about the autotimer attribut and value casting
    #
    def test_item_autotimers(self):
        """
        Tests about the autotimer attribut and value casting
        """
        if verbose == True:
            logger.warning('')
            logger.warning('===== test_item_autotimers:')
#        if verbose == True:
#            logger.warning('')

        self.load_items('item_timers')
        #self.sh.with_items_from('item_timers')

        items = self.sh.items.return_items()
        for i in items:
            logger.warning("test_item_autotimers: self.sh.items i = {}".format(i))

        # -----------------------------------------------------------------

        # Compatibility mode: No value casting for SmartHome v1.2 and older
        it = self.sh.items.return_item("item_tree.timertests.test_item01")		# autotimer = 5m = 42 = compat_1.2
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5m')
        self.assertEqual(it._autotimer_value, '41')

        it = self.sh.items.return_item("item_tree.timertests.test_item02")		# autotimer = 5s = = compat_1.2
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, '0')

        it = self.sh.items.return_item("item_tree.timertests.test_item03")		# autotimer = 5s = None = compat_1.2
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, 'None')


        # Compatibility mode: No value casting for SmartHome v1.2 and older -> item-type ist str
        it = self.sh.items.return_item("item_tree.timertests.test_item11")		# autotimer = 5m = 42 = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5m')
        self.assertEqual(it._autotimer_value, '42')

        it = self.sh.items.return_item("item_tree.timertests.test_item12")		# autotimer = 5s = = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, '0')

        it = self.sh.items.return_item("item_tree.timertests.test_item13")		# autotimer = 5s = None = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, 'None')


        # Compatibility mode: No value casting for SmartHome v1.2 and older -> item-type ist num
        it = self.sh.items.return_item("item_tree.timertests.test_item21")		# autotimer = 5m = 42 = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5m')
        self.assertEqual(it._autotimer_value, '43')

        it = self.sh.items.return_item("item_tree.timertests.test_item22")		# autotimer = 5s = = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, 0)

        it = self.sh.items.return_item("item_tree.timertests.test_item23")		# autotimer = 5s = None = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, 0)


        # Compatibility mode: No value casting for SmartHome v1.2 and older -> item-type ist bool
        it = self.sh.items.return_item("item_tree.timertests.test_item31")		# autotimer = 5m = 42 = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5m')
        self.assertEqual(it._autotimer_value, False)

        it = self.sh.items.return_item("item_tree.timertests.test_item32")		# autotimer = 5s = = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, False)

        it = self.sh.items.return_item("item_tree.timertests.test_item33")		# autotimer = 5s = None = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, False)

        it = self.sh.items.return_item("item_tree.timertests.test_item33")		# autotimer = 5s = 1 = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, False)

        it = self.sh.items.return_item("item_tree.timertests.test_item34")		# autotimer = 5s = True = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5m')
        self.assertEqual(it._autotimer_value, True)

        it = self.sh.items.return_item("item_tree.timertests.test_item35")		# autotimer = 5s = true = latest
        logger.warning("test_item_autotimers: sh.items  it = {}".format(it))
        self.assertIsNotNone(it)
        self.assertEqual(it._autotimer_time, '5s')
        self.assertEqual(it._autotimer_value, False)


    def item_cast_str(self, value):
        try:
            return lib.item.helpers.cast_str(value)
        except AttributeError:
            return lib.item._cast_str(value)

    def item_cast_list(self, value):
        try:
            return lib.item.helpers.cast_list(value)
        except AttributeError:
            return lib.item._cast_list(value)

    def item_cast_dict(self, value):
        try:
            return lib.item.helpers.cast_dict(value)
        except AttributeError:
            return lib.item._cast_dict(value)

    def item_cast_scene(self, value):
        try:
            return lib.item.helpers.cast_scene(value)
        except AttributeError:
            return lib.item._cast_scene(value)

    def item_cast_num(self, value):
        try:
            return lib.item.helpers.cast_num(value)
        except AttributeError:
            return lib.item._cast_num(value)

    def item_cast_bool(self, value):
        try:
            return lib.item.helpers.cast_bool(value)
        except AttributeError:
            return lib.item._cast_bool(value)


    def test_cast_str(self):
        #with self.assertRaises(ValueError):
        #    self.assertTrue(self.item_cast_str(1))
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_str(["ee","ww"]))

        str = 'qwe'
        self.assertEqual(str, self.item_cast_str(str))

    def test_cast_list(self):
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_list(1))
        self.assertIsNotNone(self.item_cast_list([1,2]))
        with self.assertRaises(ValueError):
            self.assertIsNotNone(self.item_cast_list({1, 2}))

    def test_cast_dict(self):
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_dict(1))
        self.assertIsNotNone(self.item_cast_dict({1:1, 2:2}))
        self.assertIsNotNone(self.item_cast_dict({'1':1 , '2': 2}))

        with self.assertRaises(ValueError):
            self.assertIsNotNone(self.item_cast_dict({1, 2}))

    def test_cast_scene(self):
        self.assertEqual(1, self.item_cast_scene('1'))
        self.assertNotEqual(1, self.item_cast_scene('2'))
        self.assertEqual(255, self.item_cast_scene(0xff))

        with self.assertRaises(ValueError):
            self.assertEqual(255, self.item_cast_scene(""))

        with self.assertRaises(ValueError):
            self.assertEqual(1, self.item_cast_scene('l'))

    def test_cast_num(self):
        self.assertEqual(0, self.item_cast_num(''))
        self.assertEqual(0, self.item_cast_num(' '))
        self.assertEqual(1, self.item_cast_num(' 1 '))
        self.assertEqual(1, self.item_cast_num('1'))
        self.assertEqual(1.2, self.item_cast_num('1.2'))
        self.assertEqual(1.2, self.item_cast_num(1.2))
        self.assertEqual(1, self.item_cast_num(int(1.2)))
        self.assertEqual(1.2, self.item_cast_num(float(1.2)))
        with self.assertRaises(ValueError):
            self.assertEqual(10, self.item_cast_num(' 0x0a'))

    def test_cast_bool(self):
        """
        ['0', 'false', 'no', 'off', '']:
            return False
        elif value.lower() in ['1', 'true', 'yes', 'on']:
        :return:
        """
        # true string values
        self.assertTrue(self.item_cast_bool('yes'))
        self.assertTrue(self.item_cast_bool('true'))
        self.assertTrue(self.item_cast_bool('1'))
        self.assertTrue(self.item_cast_bool('on'))
        # true numeric values
        self.assertTrue(self.item_cast_bool(1))
        self.assertTrue(self.item_cast_bool(int(1)))
        self.assertTrue(self.item_cast_bool(float(1)))
        self.assertTrue(self.item_cast_bool(bool(1)))

        # exceptions
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_bool(float(99)))
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_bool(2))
        with self.assertRaises(ValueError):
            self.assertTrue(self.item_cast_bool(-2))

        with self.assertRaises(TypeError):
            self.assertTrue(self.item_cast_bool([]))

        with self.assertRaises(TypeError):
            self.assertTrue(self.item_cast_bool(None))

        #false numeric values
        self.assertFalse(self.item_cast_bool(0))
        self.assertFalse(self.item_cast_bool(int(0)))
        self.assertFalse(self.item_cast_bool(float(0)))
        self.assertFalse(self.item_cast_bool(bool(0)))
        # false string values
        self.assertFalse(self.item_cast_bool(""))
        self.assertFalse(self.item_cast_bool('no'))
        self.assertFalse(self.item_cast_bool('off'))
        self.assertFalse(self.item_cast_bool('false'))
        self.assertFalse(self.item_cast_bool('0'))


    def create_item(self, smarthome, parent, path, config):
        try:
            item = lib.item.item.Item(smarthome, parent, path, config)
        except:
            item = lib.item.Item(smarthome, parent, path, config)
        return item


    def item_fadejob(self, item, dest, step, delta):
        try:
            lib.item.helpers.fadejob(item, dest, step, delta)
        except:
            lib.item._fadejob(item, dest, step, delta)


    def test_fadejob(self):
        #(item, dest, step, delta):
        sh = MockSmartHome()
        conf = {'type': 'num', 'autotimer': '5m = 42 = compat_1.2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01' )
        item = self.create_item(smarthome=sh, parent=sh, path='test_item01', config=conf)
        logger.warning("test_fadejob: item={}".format(item))
        item(10)

        item._fading = True
        self.item_fadejob(item, 0, 5, 1)
        self.assertEqual(10, item._value)

        item._fading = False
        self.item_fadejob(item, 0, 5, 0.1)
        self.assertEqual(0, item._value)

        self.item_fadejob(item, 10, 5, 0.1)
        self.assertEqual(10, item._value)

        self.item_fadejob(item, 100, 200, 1)
        self.assertEqual(100, item._value)


    def test_set(self):

        if verbose == True:
            logger.warning('')
            logger.warning('===== test_set:')
        sh = MockSmartHome()
        conf = {'type': 'num', 'autotimer': '5m = 42 = compat_1.2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item.set(12)
        self.assertEqual(12, item._value)

        item.set('13')
        self.assertEqual(13, item._value)
        self.assertIsNone(item.set('qwe'))
        self.assertEqual(13, item._value)
        item.set('14')

    def test_cast_duration(self):
        if verbose == True:
            logger.warning('')
            logger.warning('===== test_item_relative_references:')
        sh = MockSmartHome()
        conf = {'type': 'num', 'autotimer': '5m = 42 = compat_1.2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        self.assertEqual(300, item._cast_duration('5m'))
        self.assertEqual(23, item._cast_duration('23s'))
        self.assertEqual(42, item._cast_duration(42))
        self.assertEqual(42, item._cast_duration('42'))
        self.assertFalse(item._cast_duration('aa'))
        self.assertFalse(item._cast_duration(None))

    def test_call(self):
        if verbose == True:
            logger.warning('')
            logger.warning('===== test_call:')
        sh = MockSmartHome()
        conf = {'type': 'num', 'autotimer': '5m = 42 = compat_1.2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item(12)
        self.assertEqual(12, item._value)
        self.assertEqual(12, item())
        conf = {'type': 'num', 'eval': '2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item(12)
        self.assertEqual(0, item())
        item.set(12)
        self.assertEqual(12, item())

    def test_run_eval(self):
        sh = MockSmartHome()
        conf = {'type': 'num', 'eval': '2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item._Item__run_eval()
        self.assertEqual(2,item())
        item._eval = 'bla'
        item._Item__run_eval()
        item._eval = 'sh.return_none()'
        item._Item__run_eval()

    def test_jsonvars(self):
        sh = MockSmartHome()
        conf = {'type': 'num', 'eval': '2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item.set('42')

        self.assertDictEqual(item.jsonvars(),{'attributes': {}, 'value': 42, 'type': 'num', 'children': [], 'id': 'test_item01', 'name': 'test_item01'})
      #  __run_eval(self, value=None, caller='Eval', source=None, dest=None):
    def test_to_json(self):
        import json
        sh = MockSmartHome()
        conf = {'type': 'num', 'eval': '2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item.set('42')
        expected = json.dumps({'attributes': {}, 'value': 42, 'type': 'num', 'children': [], 'id': 'test_item01', 'name': 'test_item01'}, sort_keys=True, indent=2)
        self.assertEqual(item.to_json(), expected)

    def test_type(self):
        sh = MockSmartHome()
        conf = {'type': 'num', 'eval': '2'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        self.assertEqual(item.type(), 'num')
        item._type= 'foo'
        self.assertNotEqual(item.type(), 'num')
        self.assertEqual(item.type(), 'foo')

    def test_prev_value(self):
        sh = MockSmartHome()
        conf = {'type': 'num'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')

        self.assertEqual(0,item.prev_value())

        item(12)
        self.assertEqual(0, item.prev_value())

        item(23)
        self.assertEqual(12, item.prev_value())

        item(42)
        self.assertEqual(23, item.prev_value())

    def test_last_prev_change(self):
        import datetime
        import time
        sh = MockSmartHome()
        conf = {'type': 'num'}
        #item = lib.item.item.Item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        item = self.create_item(config=conf, parent=sh, smarthome=sh, path='test_item01')
        sec1 = datetime.datetime.now().time().second
        self.assertEqual(sec1,item.last_change().time().second)
        time.sleep(2)
        item(12)
        self.assertEqual(datetime.datetime.now().time().second,item.last_change().time().second)
        self.assertEqual(sec1, item.prev_change().time().second)
        self.assertEqual(datetime.datetime.now().time().second, item.last_change().time().second)
        sec2 = datetime.datetime.now().time().second
        time.sleep(2)

        item(12)
        self.assertEqual(sec2, item.last_change().time().second)
        self.assertEqual(sec1, item.prev_change().time().second)

        sec3 = datetime.datetime.now().time().second
        item(23)
        self.assertEqual(sec3, item.last_change().time().second)


    def test_split_duration_value_string(self):
        try:
            lib.item.helpers.split_duration_value_string("", lib.item.item.ATTRIB_COMPAT_DEFAULT)
        except AttributeError:
            lib.item._split_duration_value_string("")


    def test_join_duration_value_string(self):
        #logger.warning(lib.item._join_duration_value_string(12,123))
        #(time, value, compat=''):
        pass

    def test_cachewrite_readjson(self):
        import datetime
        from lib.constants import CACHE_JSON

        self.cache_write_load_value(v = True, f=CACHE_JSON)
        self.cache_write_load_value(v=None, f=CACHE_JSON)
        self.cache_write_load_value(v=1, f=CACHE_JSON)
        self.cache_write_load_value(v=123123123, f=CACHE_JSON)
        self.cache_write_load_value(v="foo", f=CACHE_JSON)
        self.cache_write_load_value(v={'active': True, 'list': [{'active': True, 'rrule': 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU', 'time': 'sunset+30m', 'value': 1}, {'active': True, 'rrule': 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU', 'time': 'sunrise-30m', 'value': 0}]}, f=CACHE_JSON)
        self.cache_write_load_value(v={'active': True}, f=CACHE_JSON)
        self.cache_write_load_value(v=[1,2,3,4,5], f=CACHE_JSON)
        self.cache_write_load_value(v=["a","2","3"], f=CACHE_JSON)
        self.cache_write_load_value(v=["a","2","3",2,3,4,5], f=CACHE_JSON)
        # @TODO: not working : self.cache_write_load_value(v=datetime.datetime.now(), f=CACHE_JSON)

    def test_cachewrite_readpickle(self):
        import datetime
        from lib.constants import CACHE_PICKLE

        self.cache_write_load_value(v = True, f=CACHE_PICKLE)
        self.cache_write_load_value(v=None, f=CACHE_PICKLE)
        self.cache_write_load_value(v=1, f=CACHE_PICKLE)
        self.cache_write_load_value(v=123123123, f=CACHE_PICKLE)
        self.cache_write_load_value(v="foo", f=CACHE_PICKLE)
        self.cache_write_load_value(v={'active': True, 'list': [{'active': True, 'rrule': 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU', 'time': 'sunset+30m', 'value': 1}, {'active': True, 'rrule': 'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR,SA,SU', 'time': 'sunrise-30m', 'value': 0}]}, f=CACHE_PICKLE)
        self.cache_write_load_value(v={'active': True}, f=CACHE_PICKLE)
        self.cache_write_load_value(v=[1,2,3,4,5], f=CACHE_PICKLE)
        self.cache_write_load_value(v=["a","2","3"], f=CACHE_PICKLE)
        self.cache_write_load_value(v=["a","2","3",2,3,4,5], f=CACHE_PICKLE)
        self.cache_write_load_value(v=datetime.datetime.now(), f=CACHE_PICKLE)


    def cache_write_load_value(self, v,f):
        from dateutil.tz import gettz

        TZ = gettz('UTC')
        fn = 'test.cache'

        try:
            lib.item.item.cache_write(value=v, filename=fn, cformat=f)
        except:
            lib.item._cache_write(value=v, filename=fn, cformat=f)

        date = cachedvalue = None
        try:
            date, cachedvalue = lib.item.item.cache_read(filename=fn, tz=TZ, cformat=f)
        except:
            date, cachedvalue = lib.item._cache_read(filename=fn, tz=TZ, cformat=f)
        #logger.warning(type(cachedvalue))
        self.assertEqual(v, cachedvalue)


    def test_item_jsondump(self):
        sh = MockSmartHome()

        self.load_items('item_dumps', YAML_FILE)

        #logger.warning(self.sh.return_item("item1").to_json())
        #logger.warning(self.sh.return_item("item3.item3b.item3b1").to_json())
        #logger.warning(self.sh.return_item("item3").to_json())
        import json
        self.assertEqual(json.loads(self.sh.items.return_item("item3").to_json())['name'], self.sh.items.return_item("item3")._name)
        self.assertEqual(json.loads(self.sh.items.return_item("item3").to_json())['id'], self.sh.items.return_item("item3")._path)


if __name__ == '__main__':
    unittest.main(verbosity=2)

