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

import lib.shyaml as shyaml
from lib.item import Items
from lib.utils import Utils

import jwt
from .rest import RESTResource
from .itemdata import ItemData


class ItemsController(RESTResource, ItemData):
    # PATCH isn't in RESTResource's REST_defaults (DELETE/GET/POST/PUT/OPTIONS
    # only) — add it here rather than there, since this is the only
    # controller in the admin module that needs it so far.
    REST_map = {'PATCH': 'edit'}

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

        if id == 'attributes':
            # /api/items/attributes  — core item attribute catalog (modules/core/items.yaml)
            self.logger.info('ItemsController GET /api/items/attributes')
            return json.dumps(self._core_item_attributes())

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

    def _core_item_attributes(self):
        """
        Read the core item-attribute catalog (modules/core/items.yaml's
        ``item_attributes:`` section) and shape it for the admin frontend:
        ``{<name>: {"type": ..., "valid_list": [...]}}`` — ``valid_list`` is
        omitted (not null) for attributes that don't define one, matching
        the shape api_plugins.py uses for plugin item attributes.

        :return: dict of attribute name -> {"type": ..., ["valid_list": ...]}
        :rtype: dict
        """
        filename = os.path.join(self._sh.get_basedir(), 'modules', 'core', 'items.yaml')
        data = shyaml.yaml_load(filename, ordered=True) or {}
        item_attributes = data.get('item_attributes', {}) or {}

        result = {}
        for name, definition in item_attributes.items():
            entry = {'type': definition.get('type')}
            valid_list = definition.get('valid_list')
            if valid_list is not None:
                entry['valid_list'] = valid_list
            description = definition.get('description')
            if description is not None:
                entry['description'] = description
            result[name] = entry
        return result

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
        same shape as a static item definition), and optionally "persist"
        (bool, default True) and "filename" (str, default None — falls back
        to Items.create_item()'s own default resolution).

        If id contains a dot, the part before the last dot is resolved as
        the parent item — it must already exist, or this is a 400, not a
        silent top-level fallback.
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body)
            config = data.get('config')
            persist = data.get('persist', True)
            filename = data.get('filename')
        except (json.JSONDecodeError, AttributeError, TypeError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body — expected {"config": ...}')

        parent_path, _, _leaf = id.rpartition('.')
        parent_item = None
        if parent_path:
            parent_item = self.items.return_item(parent_path)
            if parent_item is None:
                raise cherrypy.HTTPError(400, f"Parent item '{parent_path}' not found")

        self.logger.info(f'ItemsController POST /api/items/{id}: config={config!r}')

        try:
            item = self.items.create_item(id, config, parent=parent_item, persist=persist, filename=filename)
        except ValueError as e:
            raise cherrypy.HTTPError(400, str(e))
        if item is None:
            raise cherrypy.HTTPError(400, f"Item '{id}' was not created — its name collides with an existing attribute")
        return json.dumps({'result': 'ok'})

    add.expose_resource = True
    add.authentication_needed = True

    # ======================================================================
    #  PATCH /api/items/{item_path}
    #
    def edit(self, id=None):
        """
        Handle PATCH requests — edit an existing item's attributes in place.

        Request body: JSON object with a "config" key — the COMPLETE new
        attribute set (same convention as add()/POST — omitting a key
        resets it to its default, there is no partial-patch/delete-sentinel
        scheme). No "persist"/"filename" — editing never moves an item to a
        different file; it always persists to whatever file it was already
        defined in.

        Editing an item that other items structurally depend on (via
        ``trigger:``/``hysteresis_input:``) is allowed — those incoming
        registrations live on the edited item's own object and survive
        the edit untouched, since edit_item() mutates in place rather than
        replacing the object.
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body)
            config = data.get('config')
        except (json.JSONDecodeError, AttributeError, TypeError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body — expected {"config": ...}')

        self.logger.info(f'ItemsController PATCH /api/items/{id}: config={config!r}')

        try:
            self.items.edit_item(item, config)
        except ValueError as e:
            raise cherrypy.HTTPError(400, str(e))
        return json.dumps({'result': 'ok'})

    edit.expose_resource = True
    edit.authentication_needed = True

    # ======================================================================
    #  DELETE /api/items/{item_path}
    #
    def delete(self, id=None, persist=None):
        """
        Handle DELETE requests — remove an item at runtime.

        :param persist: Optional query parameter ('true'/'false', default
                         True if omitted) — whether to also remove the
                         item's entry from its source yaml file.

        Deliberately a query parameter, not a JSON request body: DELETE
        isn't in cherrypy's default `methods_with_bodies`
        ('POST', 'PUT', 'PATCH'), so cherrypy never runs its normal body
        wrapping/processing for it — request.body.fp ends up as the raw
        cheroot KnownLengthRFile, whose read() doesn't accept the
        (size, fp_out) signature cherrypy's own Entity.read() calls it
        with, crashing with a TypeError on every DELETE. The query string
        is parsed unconditionally regardless of method, so it doesn't hit
        this.
        """
        if id is None:
            raise cherrypy.HTTPError(400, 'Item path required')

        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        persist_value = True
        if persist is not None:
            try:
                persist_value = Utils.to_bool(persist)
            except Exception:
                raise cherrypy.HTTPError(400, "Invalid 'persist' parameter — expected true/false")

        self.logger.info(f'ItemsController DELETE /api/items/{id}: persist={persist_value!r}')

        try:
            self.items.remove_item(item, persist=persist_value)
        except ValueError as e:
            raise cherrypy.HTTPError(400, str(e))
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
        result = [
            {'item': ref_item.property.path, 'attribute': attr, 'value': value, 'unambiguous': unambiguous}
            for ref_item, attr, value, unambiguous in refs
        ]
        return json.dumps(result)

    references.expose_resource = True
    references.authentication_needed = True

    # ======================================================================
    #  POST /api/items/{item_path}/remove_references
    #
    def remove_references(self, id, *vpath, **params):
        """
        Handle POST requests for the /remove_references sub-resource —
        strip dangling unambiguous references to this item from every
        other item (see Items.remove_references()). Intended to be
        called right before deleting this item.

        Sub-resource methods reached via vpath (like this one and
        references()) aren't verb-gated by RESTResource's dispatcher —
        only the top-level REST_map/REST_defaults methods are. Since this
        one is destructive (unlike references(), which is read-only),
        the method check is enforced explicitly here.
        """
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, 'Method not allowed')

        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        self.logger.info(f'ItemsController POST /api/items/{id}/remove_references')

        result = self.items.remove_references(id)
        return json.dumps(result)

    remove_references.expose_resource = True
    remove_references.authentication_needed = True

    # ======================================================================
    #  POST /api/items/{item_path}/rename
    #
    def rename(self, id, *vpath, **params):
        """
        Handle POST requests for the /rename sub-resource — rename an
        item in place, optionally moving it to a new parent (see
        ~/.claude/handoff/shng-rename-item-design.md).

        Request body: JSON object with a "new_path" key — the COMPLETE
        new path, not just a leaf name, since a different parent segment
        triggers a move rather than a plain rename — and an optional
        "filename" key, an explicit override for which yaml file the
        moved item's node lands in (only meaningful when persisted).

        Sub-resource methods reached via vpath aren't verb-gated by
        RESTResource's dispatcher — checked explicitly here, same
        reasoning as remove_references().
        """
        if cherrypy.request.method != 'POST':
            raise cherrypy.HTTPError(405, 'Method not allowed')

        if self.items is None:
            self.items = Items.get_instance()

        item = self.items.return_item(id)
        if item is None:
            raise cherrypy.HTTPError(404, f"Item '{id}' not found")

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body)
            new_path = data.get('new_path')
            filename = data.get('filename')
        except (json.JSONDecodeError, AttributeError, TypeError):
            raise cherrypy.HTTPError(400, 'Invalid JSON body — expected {"new_path": ...}')

        self.logger.info(f'ItemsController POST /api/items/{id}/rename: new_path={new_path!r}')

        try:
            _renamed_item, report = self.items.rename_item(item, new_path, filename=filename)
        except ValueError as e:
            raise cherrypy.HTTPError(400, str(e))

        return json.dumps({'result': 'ok', 'new_path': new_path, **report})

    rename.expose_resource = True
    rename.authentication_needed = True


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
