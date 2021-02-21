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

import jwt
from .rest import RESTResource


class ItemsController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.items = Items.get_instance()

        return


    # ======================================================================
    #  GET /api/items
    #
    def read(self, id=None):
        """
        Handle GET requests
        """

        if self.items is None:
            self.items = Items.get_instance()

        if id == 'structs':
            # /api/items/structs
            self.logger.info("ItemsController.root(): item_name = {}".format(id))
            result = self.items.return_struct_definitions(all=False)

            return json.dumps(result)

            #raise cherrypy.NotFound
            #self.logger.info("LogController (GET): logfiles = {}".format(logs))
            #return json.dumps({'logs':logs, 'default': self.root_logname})

        return None

    read.expose_resource = True
    read.authentication_needed = True

class ItemsListController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.items = Items.get_instance()

        return

    # ======================================================================
    #  GET /api/items
    #
    def read(self, id=None):
        """
        Handle GET requests
        """

        if self.items is None:
            self.items = Items.get_instance()

        items_sorted = sorted(self.items.return_items(), key=lambda k: str.lower(k['_path']), reverse=False)

        item_list = []
        for item in items_sorted:
            item_list.append(item._path)
        return json.dumps(item_list)

    read.expose_resource = True
    read.authentication_needed = True
