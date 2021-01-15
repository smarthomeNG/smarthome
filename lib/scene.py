#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2017   Martin Sinn                         m.sinn@gmx.de
# Copyright 2013-2013   Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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

"""
This file implements scenes in SmartHomeNG
"""

import logging
import os.path
import csv

from lib.item import Items
from lib.logic import Logics

from lib.utils import Utils
import lib.shyaml as yaml

logger = logging.getLogger(__name__)


_scenes_instance = None    # Pointer to the initialized instance of the Plugins class (for use by static methods)


class Scenes():
    """
    This class loads all scene definitions from /scenes folder and adds the necessary triggers
    for the scenes to function.

    :Note: The scene definitions are stored in /scenes files with the extension .conf but don't follow the file format for conf-files of smarthome.py!

    :param smarthome: Main SmartHomeNG object
    :type smarthome: object
    """

    def __init__(self, smarthome):
        self._sh = smarthome

        global _scenes_instance
        if _scenes_instance is not None:
            import inspect
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            logger.critical("A second 'scenes' object has been created. There should only be ONE instance of class 'Scenes'!!! Called from: {} ({})".format(calframe[1][1], calframe[1][3]))

        _scenes_instance = self

        self.items = Items.get_instance()
        self.logics = Logics.get_instance()

        self._scenes = {}
        self._learned_values = {}
        self._scenes_dir = smarthome._scenes_dir
        if not os.path.isdir(self._scenes_dir):
            logger.warning("Directory scenes not found. Ignoring scenes.".format(self._scenes_dir))
            return

        self._learned_values = {}
        #   for item in smarthome.return_items():
        for item in self.items.return_items():
            if item.type() == 'scene':
                self.scene_file = os.path.join(self._scenes_dir, item.id())

                scene_file_yaml = yaml.yaml_load(self.scene_file+'.yaml', ordered=False, ignore_notfound=True)
                if scene_file_yaml is not None:
                    # Reading yaml file with scene definition
                    for state in scene_file_yaml:
                        actions = scene_file_yaml[state].get('actions', None)
                        if actions is not None:
                            if isinstance(actions, dict):
                                actions = [ actions ]
                            if isinstance( actions, list ):
                                for action in actions:
                                    if isinstance(action, dict):
                                        self._add_scene_entry(item, str(state),
                                                              action.get('item', ''), str(action.get('value', '')),
                                                              action.get('learn', ''), scene_file_yaml[state].get('name', ''))
                                    else:
                                        logger.warning("Scene {}, state {}: action '{}' is not a dict".format(item, state, action))
                            else:
                                logger.warning("Scene {}, state {}: actions are not a list".format(item, state))
                    self._load_learned_values(str(item.id()))
                else:
                    # Trying to read conf file with scene definition
                    scene_conf_file = self.scene_file + '.conf'
                    try:
                        with open(scene_conf_file, 'r', encoding='UTF-8') as f:
                            reader = csv.reader(f, delimiter=' ')
                            for row in reader:
                                if row == []:  # ignore empty lines
                                    continue
                                if row[0][0] == '#':  # ignore comments
                                    continue
                                self._add_scene_entry(item, row[0], row[1], row[2])
                    except Exception as e:
                        logger.warning("Problem reading scene file {0}: No .yaml or .conf file found with this name".format(self.scene_file))
                        continue
                item.add_method_trigger(self._trigger)


    def _eval(self, value):
        """
        Evaluate a scene value

        :param value: value expression to evaluate
        :type value: str

        :return: evaluated value or None
        :rtype: type of evaluated expression or None
        """
        sh = self._sh  # noqa
        try:
            rvalue = eval(value)
        except Exception as e:
            logger.warning(" - Problem evaluating: {} - {}".format(value, e))
            return value
        return rvalue


    def _get_learned_value(self, scene, state, ditem):
        try:
            lvalue = self._learned_values[scene +'#'+ str(state) +'#'+ ditem.id()]
        except:
            return None
        logger.debug(" - Return learned value {} for scene/state/ditem {}".format(lvalue, scene +'#'+ str(state) +'#'+ ditem.id()))
        return lvalue


    def _set_learned_value(self, scene, state, ditem, lvalue):
        self._learned_values[scene +'#'+ str(state) +'#'+ ditem.id()] = lvalue
        logger.debug(" - Learned value {} for scene/state/ditem {}".format(lvalue, scene +'#'+ str(state) +'#'+ ditem.id()))


    def _save_learned_values(self, scene):
        """
        Save learned values for the scene to a file to make them persistant
        """
        logger.info("Saving learned values for scene {}:".format(scene))
        logger.info(" -> from dict self._learned_values {}:".format(self._learned_values))
        learned_dict = {}
        for key in self._learned_values:
            lvalue = self._learned_values[key]
            kl = key.split('#')
            if kl[0] == scene:
                fkey = kl[1]+'#'+kl[2]
                learned_dict[fkey] = lvalue
                logger.debug(" - Saving value {} for state/ditem {}".format(lvalue, fkey))
        logger.info(" -> to dict learned_dict {}:".format(learned_dict))
        scene_learnfile = os.path.join(self._scenes_dir, scene+'_learned')
        yaml.yaml_save(scene_learnfile+'.yaml', learned_dict)
        return


    def _load_learned_values(self, scene):
        """
        Load learned values for the scene from a file
        """
        scene_learnfile = os.path.join(self._scenes_dir, scene+'_learned')
        learned_dict = yaml.yaml_load(scene_learnfile+'.yaml', ordered=False, ignore_notfound=True)
        logger.info("Loading learned values for scene {} from file {}:".format(scene, scene_learnfile))
        logger.info(" -> loaded dict learned_dict {}:".format(learned_dict))
        if learned_dict is not None:
            if learned_dict != {}:
                logger.info("Loading learned values for scene {}".format(scene))
            for fkey in learned_dict:
                key = scene + '#' + fkey
                lvalue = learned_dict[fkey]
                self._learned_values[key] = lvalue
                logger.debug(" - Loading value {} for state/ditem {}".format(lvalue, key))

        logger.info(" -> to dict self._learned_values {}:".format(self._learned_values))
        return


    def _trigger_setstate(self, item, state, caller, source, dest):
        """
        Trigger: set values for a scene state
        """
        logger.info("Triggered scene {} ({}) with state {} ({}):".format(item.id(), str(item), state, self.get_scene_action_name(item.id(), state)))
        for ditem, value, name, learn in self._scenes[item.id()][str(state)]:
            if learn:
                lvalue = self._get_learned_value(item.id(), state, ditem)
                if lvalue is not None:
                    rvalue = lvalue
                else:
                    rvalue = value
            else:
                rvalue = self._eval(value)
            if rvalue is not None:
                if str(rvalue) == str(value):
                    logger.info(" - Item {} set to {}".format(ditem, rvalue))
                else:
                    logger.info(" - Item {} set to {} ( from {} )".format(ditem, rvalue, value))
                try:
                    ditem(value=rvalue, caller='Scene', source=item.id())
                except Exception as e:
                    logger.warning(" - ditem '{}', value '{}', exception {}".format(ditem, rvalue, e))
        return


    def _trigger_learnstate(self, item, state, caller, source, dest):
        """
        Trigger: learn values for a scene state
        """
        logger.info("Triggered 'learn' for scene {} ({}), state {} ({}):".format(item.id(), str(item), state, self.get_scene_action_name(item.id(), state)))
        for ditem, value, name, learn in self._scenes[item.id()][str(state)]:
            if learn:
                self._set_learned_value(item.id(), state, ditem, ditem())
        self._save_learned_values(str(item.id()))
        return


    def _trigger(self, item, caller, source, dest):
        """
        Trigger a scene
        """
        if not item.id() in self._scenes:
            return
        if str(item()&127) in self._scenes[item.id()]:
            state = item()
            if Utils.is_int(state):
                state = int(state)
            else:
                logger.error("Invalid state '{}' for scene {}".format(state, item.id()))
                return

            if (state >= 0) and (state < 64):
                # set state
                self._trigger_setstate(item, state, caller, source, dest)
            elif (state >= 128) and (state < 128+64):
                # learn state
                self._trigger_learnstate(item, state&127, caller, source, dest)
            else:
                logger.error("Invalid state '{}' for scene {}".format(state, item.id()))


    def _add_scene_entry(self, item, state, ditemname, value, learn=False, name=''):
        """
        Adds a single assignement entry to the loaded scenes

        :param item: item defing the scene (type: scene)
        :param row: list of: state number, item to assign to, value to assign to item
        :param name: name of the scene state
        :type item: item object
        :type row: list (with 3 entries)
        :type name: str
        """
        logger.debug("_add_scene_entry: item = {}, state = {}, ditemname = {}, value = {}, learn = {}, name = {}".format(item.id(), state, ditemname, value, learn, name))
        value = item.get_stringwithabsolutepathes(value, 'sh.', '(', 'scene')
#        ditem = self._sh.return_item(item.get_absolutepath(ditemname, attribute='scene'))
        ditem = self.items.return_item(item.get_absolutepath(ditemname, attribute='scene'))

        if learn:
            rvalue = self._eval(value)
            if str(rvalue) != value:
                logger.warning("_add_scene_entry - Learn set to 'False', because '{}' != '{}'".format(rvalue, value))
                learn = False

        if ditem is None:
            ditem = self.logics.return_logic(ditemname)
            if ditem is None:
                logger.warning("Could not find item or logic '{}' specified in {}".format(ditemname, self.scene_file))
                return

        if item.id() in self._scenes:
            if state in self._scenes[item.id()]:
                self._scenes[item.id()][state].append([ditem, value, name, learn])
            else:
                self._scenes[item.id()][state] = [[ditem, value, name, learn]]
        else:
            self._scenes[item.id()] = {state: [[ditem, value, name, learn]]}
        return


    # ------------------------------------------------------------------------------------
    #   Following (static) methods of the class Plugins implement the API for plugins in shNG
    # ------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Scenes class, to be used to access the scene-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.scene import Scenes
            scenes = Scenes.get_instance()

            # to access a method (eg. xxx()):
            scenes.xxx()


        :return: scenes instance
        :rtype: object of None
        """
        if _scenes_instance == None:
            return None
        else:
            return _scenes_instance


    def get_loaded_scenes(self):
        """
        Returns a list with the names of all scenes that are currently loaded

        :return: list of scene names
        :rtype: list
        """

        scene_list = []
        for scene in self._scenes:
            scene_list.append(scene)
        return sorted(scene_list)


    def get_scene_actions(self, name):
        """
        Returns a list with the the defined actions for a scene

        :return: list of scene values
        :rtype: list
        """

        value_list = []
        for value in self._scenes[name]:
            value_list.append(int(value))
        value_list = sorted(value_list)
        value_list2 = []
        for value in value_list:
            value_list2.append(str(value))
        return value_list2


    def get_scene_action_name(self, scenename, action):
        """
        Returns the name of a scene-action
        """
        action = str(action)
        try:
            return self._scenes[scenename][action][0][2]
        except:
            logger.warning("get_scene_action_name: unable to get self._scenes['{}']['{}'][0][2] <- {}".format(scenename, action, self._scenes[scenename][action][0]))
            return ''

    def return_scene_value_actions(self, name, state):
        """
        Returns a list with the the defined actions for state of a scene

        :return: list of value actions (destination item name, value to set)
        :rtype: list
        """

        action_list = []
        for action in self._scenes[name][state]:
            lvalue = self._get_learned_value(name, state, action[0])
            if lvalue is not None:
                lvalue = str(lvalue)
            return_action = [ str(action[0]), action[1], action[3], lvalue ]
            action_list.append(return_action)
        return action_list

