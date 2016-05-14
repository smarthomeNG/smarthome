#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013-2013 Marcus Popp                          marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import os.path
import csv

logger = logging.getLogger('')


class Scenes():

    def __init__(self, smarthome):
        self._scenes = {}
        self._scenes_dir = smarthome.base_dir + '/scenes/'
        if not os.path.isdir(self._scenes_dir):
            logger.warning("Directory scenes not found. Ignoring scenes.".format(self._scenes_dir))
            return
        for item in smarthome.return_items():
            if item.type() == 'scene':
                scene_file = "{}{}.conf".format(self._scenes_dir, item.id())
                try:
                    with open(scene_file, 'r', encoding='UTF-8') as f:
                        reader = csv.reader(f, delimiter=' ')
                        for row in reader:
                            if row == []:  # ignore empty lines
                                continue
                            if row[0][0] == '#':  # ignore comments
                                continue
                            ditem = smarthome.return_item(row[1])
                            if ditem is None:
                                ditem = smarthome.return_logic(row[1])
                                if ditem is None:
                                    logger.warning("Could not find item or logic '{0}' specified in {1}".format(row[1], scene_file))
                                    continue
                            if item.id() in self._scenes:
                                if row[0] in self._scenes[item.id()]:
                                    self._scenes[item.id()][row[0]].append([ditem, row[2]])
                                else:
                                    self._scenes[item.id()][row[0]] = [[ditem, row[2]]]
                            else:
                                self._scenes[item.id()] = {row[0]: [[ditem, row[2]]]}
                except Exception as e:
                    logger.warning("Problem reading scene file {0}: {1}".format(scene_file, e))
                    continue
                item.add_method_trigger(self._trigger)

    def _trigger(self, item, caller, source, dest):
        if not item.id() in self._scenes:
            return
        if str(item()) in self._scenes[item.id()]:
            for ditem, value in self._scenes[item.id()][str(item())]:
                ditem(value=value, caller='Scene', source=item.id())
