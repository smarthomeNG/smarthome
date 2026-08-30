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


import json
import logging
import os

import lib.db
from lib.model.smartplugin import SmartPlugin
from lib.plugin import Plugins

from .rest import ApiDoc, RESTResource


class DatabaseController(RESTResource):
    """
    Controller for REST API /api/database

    Surfaces read-only connection properties of the configured `database`
    plugin instance, for shngadmin dashboard's optional database-properties
    widget. Not a general-purpose database-plugin API - if a second use case
    needs more than this, extend deliberately rather than growing it ad hoc.
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )
        self.plugins = Plugins.get_instance()

    def _find_database_plugin(self):
        """Returns the first loaded `database` plugin instance, or None."""
        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        if self.plugins is None:
            return None
        for x in self.plugins.return_plugins():
            if isinstance(x, SmartPlugin) and x.get_shortname() == 'database':
                return x
        return None

    def info(self):
        plugin = self._find_database_plugin()
        if plugin is None:
            return {'configured': False}

        driver = getattr(plugin, 'driver', '') or ''
        db = plugin.db()
        params = getattr(db, '_params', {}) or {}
        connected = db.connected()

        response = {
            'configured': True,
            'driver': driver,
            'connected': connected,
            'query_timeout': lib.db._sh_db_query_timeout(),
        }

        if driver == 'sqlite3':
            db_path = params.get('database', '')
            response['database'] = os.path.splitext(os.path.basename(db_path))[0] if db_path else ''
        else:
            response['database'] = params.get('db') or params.get('database') or ''
            if params.get('host'):
                response['host'] = params['host']

        if connected:
            response['version'] = db.version()

        return response

    # ======================================================================
    #  GET /api/database/info
    #
    def read(self, id=None):
        if id == 'info':
            return json.dumps(self.info())
        return None

    read.expose_resource = True
    read.authentication_needed = True
    read.api_doc = [
        ApiDoc(
            summary='Connection properties of the configured database plugin instance, for the dashboard widget',
            method='get',
            path='/database/info',
            tags=['database'],
        )
    ]
