#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2021-      Martin Sinn                         m.sinn@gmx.de
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

from .rest import ApiDoc, ApiParam, RESTResource


class FunctionsController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        self.items = Items.get_instance()

        return

    # ======================================================================
    #  GET /api/functions
    #
    @cherrypy.expose
    def read(self, id=None):
        """
        Handle GET requests for functions API: the loaded userfunction modules
        """
        from lib.userfunctions import get_userlibs

        return json.dumps(get_userlibs())

    read.expose_resource = True
    read.authentication_needed = True
    read.api_doc = [
        ApiDoc(
            summary='Loaded userfunction modules',
            method='get',
            path='/functions/',
            tags=['functions'],
            response_example='[{"name": "my_uf", "version": "1.0.0", "description": "my userfunctions"}]',
        )
    ]


class FunctionsReloadController(RESTResource):
    def __init__(self, module):

        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.items = Items.get_instance()

        return

    # ======================================================================
    #  /api/functions/reload
    #

    @cherrypy.expose
    def update(self, id=None):
        """
        Handle PUT requests for scenes/reload API
        """
        from lib.scene import Scenes

        self.scenes = Scenes.get_instance()

        from lib.userfunctions import reload
        from lib.userfunctions import reload_all

        if id == 'all':
            # result = self.scenes.reload_scenes()
            result = reload_all()
            return json.dumps(result)
        else:
            result = reload(id)
            return json.dumps(result)

    update.expose_resource = True
    update.authentication_needed = True
    update.api_doc = [
        ApiDoc(
            summary='Reload one function, or `all` to reload every function',
            method='put',
            path='/functions/reload/{name}',
            tags=['functions'],
            params=[ApiParam(name='name', location='path', required=True)],
        )
    ]
