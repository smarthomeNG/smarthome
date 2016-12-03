#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016 by Ageman                             ageman@ageman.com
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
import http.server
import socketserver
import json
import threading
from lib.model.smartplugin import SmartPlugin

logger = logging.getLogger('')

class GeofencyServer ( http.server.BaseHTTPRequestHandler):

    def __init__(self, smarthome, logic, *args):
        self.sh = smarthome
        self.logic = logic
        http.server.BaseHTTPRequestHandler.__init__(self, *args)

    def _set_headers(self):
        self.send_response ( 200 )
        self.send_header ( 'Content-type', 'text/html' )
        self.end_headers ( )

    def do_GET(self):
        self._set_headers ( )

    def do_HEAD(self):
        self._set_headers ( )


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(post_data)
        self.sh.trigger ( self.logic, by='geofency', value=data )
        self._set_headers ( )

def handleRequestsUsing(smarthome, logic):
    return lambda *args: GeofencyServer(smarthome, logic, *args)


class Geofency (SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = '0.0.1'

    def __init__(self, smarthome, port='2727', logic=''):
        self.alive = False
        self.handler = handleRequestsUsing(smarthome, logic)
        self.httpd = http.server.HTTPServer ( ('', int(port)) , self.handler)

    def run(self):
        """
        Called by SmartHomeNG to start plugin
        """
        self.alive = True
        # threading.Thread ( target=self.httpd.serve_forever, daemon=True ).start ( )
        self.httpd.serve_forever()

    def stop(self):
        """
        Called by SmarthomeNG to stop plugin
        """
        self.httpd.shutdown()
        self.alive = False
        self.close ( )
