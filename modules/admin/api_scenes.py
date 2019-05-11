#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
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
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import os
import logging
import json
import cherrypy

from lib.item import Items

from .rest import RESTResource


class ScenesController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.items = Items.get_instance()

        return


    # ======================================================================
    #  /api/scenes
    #
    # def root(self):
    #     if self.items == None:
    #         self.items = Items.get_instance()
    #
    #     from lib.scene import Scenes
    #     get_param_func = getattr(Scenes, "get_instance", None)
    #     if callable(get_param_func):
    #         supported = True
    #         self.scenes = Scenes.get_instance()
    #         scene_list = []
    #         if self.scenes is not None:
    #             scene_list = self.scenes.get_loaded_scenes()
    #
    #         disp_scene_list = []
    #         for scene in scene_list:
    #             scene_dict = {}
    #             scene_dict['path'] = scene
    #             #                scene_dict['name'] = str(self._sh.return_item(scene))
    #             scene_dict['name'] = str(self.items.return_item(scene))
    #
    #             action_list = self.scenes.get_scene_actions(scene)
    #             scene_dict['value_list'] = action_list
    #             #                scene_dict[scene] = action_list
    #
    #             disp_action_list = []
    #             for value in action_list:
    #                 action_dict = {}
    #                 action_dict['action'] = value
    #                 action_dict['action_name'] = self.scenes.get_scene_action_name(scene, value)
    #                 action_list = self.scenes.return_scene_value_actions(scene, value)
    #                 for action in action_list:
    #                     if not isinstance(action[0], str):
    #                         action[0] = action[0].id()
    #                 action_dict['action_list'] = action_list
    #
    #                 disp_action_list.append(action_dict)
    #             scene_dict['values'] = disp_action_list
    #             self.logger.debug("scenes_html: disp_action_list for scene {} = {}".format(scene, disp_action_list))
    #
    #             disp_scene_list.append(scene_dict)
    #     else:
    #         supported = False
    #     return json.dumps(disp_scene_list)


    # ======================================================================
    #  GET /api/scenes
    #
    @cherrypy.expose
    def read(self, id=None):
        """
        Handle GET requests for scenes API
        """
        if self.items == None:
            self.items = Items.get_instance()

        from lib.scene import Scenes
        get_param_func = getattr(Scenes, "get_instance", None)
        if callable(get_param_func):
            supported = True
            self.scenes = Scenes.get_instance()
            scene_list = []
            if self.scenes is not None:
                scene_list = self.scenes.get_loaded_scenes()

            disp_scene_list = []
            for scene in scene_list:
                scene_dict = {}
                scene_dict['path'] = scene
                #                scene_dict['name'] = str(self._sh.return_item(scene))
                scene_dict['name'] = str(self.items.return_item(scene))

                action_list = self.scenes.get_scene_actions(scene)
                scene_dict['value_list'] = action_list
                #                scene_dict[scene] = action_list

                disp_action_list = []
                for value in action_list:
                    action_dict = {}
                    action_dict['action'] = value
                    action_dict['action_name'] = self.scenes.get_scene_action_name(scene, value)
                    action_list = self.scenes.return_scene_value_actions(scene, value)
                    for action in action_list:
                        if not isinstance(action[0], str):
                            action[0] = action[0].id()
                    action_dict['action_list'] = action_list

                    disp_action_list.append(action_dict)
                scene_dict['values'] = disp_action_list
                self.logger.debug("scenes_html: disp_action_list for scene {} = {}".format(scene, disp_action_list))

                disp_scene_list.append(scene_dict)
        else:
            supported = False
        return json.dumps(disp_scene_list)

    read.expose_resource = True
    read.authentication_needed = True

