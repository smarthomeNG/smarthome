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
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
