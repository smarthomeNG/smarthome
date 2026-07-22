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

TestSubResourceActionAuthEnforcement: regression test for a bug where
default()'s sub-resource-action branch (used for actions like
/api/items/<path>/rename) called the target method directly instead of
going through REST_dispatch_execute/REST_check_auth, so a method with
authentication_needed = True was reachable without a valid JWT.
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
    used to call the target method directly, bypassing the only place
    authentication_needed is checked (REST_dispatch_execute), so a method
    that declared authentication_needed = True was actually reachable
    without a valid JWT.
    """

    class _Resource(RESTResource):
        def rename(self, id, *vpath, **params):
            self.called_with = (id, vpath, params)
            return json.dumps({'result': 'ok', 'id': id})

        rename.expose_resource = True
        rename.authentication_needed = True

    def setUp(self):
        self.resource = self._Resource()
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
