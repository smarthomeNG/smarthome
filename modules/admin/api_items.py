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
from .itemdata import ItemData


class ItemsController(RESTResource, ItemData):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        ItemData.__init__(self)

        return

    # ======================================================================
    #  GET /api/items
    #  GET /api/items/structs
    #  GET /api/items/tree
    #  GET /api/items/{item_path}
    #
    def read(self, id=None):
        """
        Handle GET requests
        """

        if self.items is None:
            self.items = Items.get_instance()

        if id == 'structs':
            # /api/items/structs
            self.logger.info(f'ItemsController GET /api/items/{id}')
            result = self.items.return_struct_definitions(all=False)
            return json.dumps(result)

        if id == 'tree':
            # /api/items/tree  — returns [count, tree_data] matching the legacy items_json() format
            self.logger.info('ItemsController GET /api/items/tree')
            return self.items_json('tree')

        if id is not None:
            # /api/items/{item_path}  — returns item detail array (same format as legacy endpoint)
            self.logger.info(f'ItemsController GET /api/items/{id}')
            result = self.item_detail_json_html(id)
            if result is None:
                raise cherrypy.HTTPError(404, f"Item '{id}' not found")
            return result

        return None

    read.expose_resource = True
    read.authentication_needed = True

    # ======================================================================
    #  PUT /api/items/{item_path}
    #
    def update(self, id=None):
        """
        Handle PUT requests — set an item value.

        Request body: JSON object with a "value" key.
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body)
            value = data.get('value')
        except (json.JSONDecodeError, AttributeError, TypeError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body — expected {"value": ...}')

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        self.logger.info(f'ItemsController PUT /api/items/{id}: value={value!r}')

        if item.type() and 'num' in item.type():
            if isinstance(value, str):
                if '.' in value or ',' in value:
                    value = float(value.replace(',', '.'))
                else:
                    value = int(value) if value != '' else 0

        item(value, caller='admin')
        return json.dumps({'result': 'ok'})

    update.expose_resource = True
    update.authentication_needed = True

    # ======================================================================
    #  POST /api/items/{item_path}
    #
    def add(self, id=None):
        """
        Handle POST requests — create a new item at runtime.

        Request body: JSON object with a "config" key (item attribute dict,
        same shape as a static item definition).
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body)
            config = data.get('config')
        except (json.JSONDecodeError, AttributeError, TypeError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body — expected {"config": ...}')

        self.logger.info(f'ItemsController POST /api/items/{id}: config={config!r}')

        self.items.create_item(id, config)
        return json.dumps({'result': 'ok'})

    add.expose_resource = True
    add.authentication_needed = True

    # ======================================================================
    #  DELETE /api/items/{item_path}
    #
    def delete(self, id=None):
        """
        Handle DELETE requests — remove an item at runtime.
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        self.logger.info(f'ItemsController DELETE /api/items/{id}')

        self.items.remove_item(item)
        return json.dumps({'result': 'ok'})

    delete.expose_resource = True
    delete.authentication_needed = True

    # ======================================================================
    #  GET /api/items/{item_path}/references
    #
    def references(self, id, *vpath, **params):
        """
        Handle GET requests for the /references sub-resource — best-effort
        list of other items that textually reference this item's path
        (see Items.find_references()).
        """
        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        self.logger.info(f'ItemsController GET /api/items/{id}/references')

        refs = self.items.find_references(id)
        result = [{'item': ref_item.property.path, 'attribute': attr, 'value': value} for ref_item, attr, value in refs]
        return json.dumps(result)

    references.expose_resource = True
    references.authentication_needed = True


class ItemsListController(RESTResource):
    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        self.items = Items.get_instance()

        return

    # ======================================================================
    #  GET /api/items/list
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
