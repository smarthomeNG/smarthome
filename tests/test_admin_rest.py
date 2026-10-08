#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/rest.py's RESTResource.

Coverage
--------
set_response_headers(): must tolerate being called with any number of
vpath segments (default.py calls it as `self.set_response_headers(*vpath)`,
and vpath can have more than one element for a sub-resource URL like
/api/items/<path>/references — two segments after the controller mount).

TestSubResourceActionAuthEnforcement: default()'s sub-resource-action
branch (used for actions like /api/items/<path>/rename) must dispatch
through REST_dispatch_execute/REST_check_auth like every other route, so
authentication_needed is always enforced.

TestBareResourceHttpErrorPropagation: cherrypy.HTTPError/HTTPRedirect raised by
a bare-resource verb method (GET/POST/PUT/PATCH/DELETE via REST_defaults/REST_map)
must reach cherrypy with their own status instead of being turned into a
200 {"result": "error"} body; any other exception keeps that JSON form.
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy
import jwt

from modules.admin.rest import RESTResource


class TestSetResponseHeaders(unittest.TestCase):
    def setUp(self):
        self.resource = RESTResource()
        request = MagicMock()
        request.headers = {'Origin': 'http://example.test'}
        response = MagicMock()
        response.headers = {}
        self._patches = [patch.object(cherrypy, 'request', request), patch.object(cherrypy, 'response', response)]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self._patches])

    def test_no_vpath_segments(self):
        self.resource.set_response_headers()  # must not raise

    def test_one_vpath_segment(self):
        self.resource.set_response_headers('item_path')  # must not raise

    def test_two_vpath_segments(self):
        # e.g. /api/items/<path>/references — two segments after the resource id
        self.resource.set_response_headers('d.aussentemperatur.fahrenheit', 'references')  # must not raise


class TestSubResourceActionAuthEnforcement(unittest.TestCase):
    """
    /api/<resource>/<action> (e.g. /api/items/<path>/rename) is dispatched by
    default()'s sub-resource-action branch, not REST_dispatch(). That branch
    must dispatch through REST_dispatch_execute, the only place
    authentication_needed is checked, not call the target method directly.
    """

    class _Resource(RESTResource):
        def rename(self, id, *vpath, **params):
            self.called_with = (id, vpath, params)
            return json.dumps({'result': 'ok', 'id': id})

        rename.expose_resource = True
        rename.authentication_needed = True

    def setUp(self):
        self.resource = self._Resource()
        self.resource.jwt_secret = 'test-secret'  # RESTResource's own default is None (see modules/admin/rest.py)
        request = MagicMock()
        request.headers = {'Origin': 'http://example.test'}
        response = MagicMock()
        response.headers = {}
        self._patches = [patch.object(cherrypy, 'request', request), patch.object(cherrypy, 'response', response)]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self._patches])

    def test_sub_resource_action_rejects_missing_token(self):
        result = self.resource.default('some.item.path', 'rename')

        self.assertFalse(hasattr(self.resource, 'called_with'), 'rename() must not run without a valid token')
        self.assertEqual(json.loads(result)['result'], 'error')

    def test_sub_resource_action_allows_valid_token(self):
        token = jwt.encode({'name': 'tester'}, self.resource.jwt_secret, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        cherrypy.request.headers['Authorization'] = f'Bearer {token}'

        result = self.resource.default('some.item.path', 'rename')

        self.assertTrue(hasattr(self.resource, 'called_with'))
        self.assertEqual(self.resource.called_with[0], 'some.item.path')
        self.assertEqual(json.loads(result)['result'], 'ok')


class TestBareResourceHttpErrorPropagation(unittest.TestCase):
    class _Resource(RESTResource):
        REST_map = {'PATCH': 'edit'}

        def read(self, id=None):
            raise cherrypy.HTTPError(404, 'nothing here')

        read.expose_resource = True

        def add(self, id=None):
            raise cherrypy.HTTPError(409, 'exists')

        add.expose_resource = True

        def edit(self, id=None):
            raise cherrypy.HTTPRedirect('/elsewhere')

        edit.expose_resource = True

        def update(self, id=None):
            raise ValueError('boom')

        update.expose_resource = True

    def setUp(self):
        self.resource = self._Resource()
        self.resource.module = MagicMock(rest_dispatch_force_exception=False)
        request = MagicMock()
        request.headers = {'Origin': 'http://example.test'}
        response = MagicMock()
        response.headers = {}
        self._patches = [patch.object(cherrypy, 'request', request), patch.object(cherrypy, 'response', response)]
        for p in self._patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in self._patches])

    def _dispatch(self, method):
        cherrypy.request.method = method
        return self.resource.REST_dispatch(True, None)

    def test_http_error_keeps_its_status(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self._dispatch('GET')
        self.assertEqual(ctx.exception.code, 404)

    def test_http_error_from_rest_defaults_post(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self._dispatch('POST')
        self.assertEqual(ctx.exception.code, 409)

    def test_http_redirect_propagates_via_rest_map(self):
        with self.assertRaises(cherrypy.HTTPRedirect):
            self._dispatch('PATCH')

    def test_other_exceptions_still_become_json_error(self):
        result = self._dispatch('PUT')

        body = json.loads(result)
        self.assertEqual(body['result'], 'error')
        self.assertIn('ValueError', body['description'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
