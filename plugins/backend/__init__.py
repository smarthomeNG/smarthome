#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2016 Bernd Meiners, 
#                 Christian Strassburg            c.strassburg@gmx.de
#                 René Frieß                      rene.friess@gmail.com
#                 Martin Sinn                     m.sinn@gmx.de
#########################################################################
#  Backend plugin for SmartHomeNG
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import cherrypy
import logging
import platform
import collections
import datetime
import pwd
import html
import os
import json
import subprocess
import socket
import sys
import threading
import lib.config
from lib.model.smartplugin import SmartPlugin
from lib.utils import Utils
from jinja2 import Environment, FileSystemLoader

from .BackendCore import Backend as BackendCore
from .BackendBlockly import BackendBlocklyLogics
from .utils import *



class BackendServer(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION='1.1.3'

    def my_to_bool(self, value, attr='', default=False):
        try:
            result = self.to_bool(value)
        except:
            result = default
            self.logger.error("BackendServer: Invalid value '"+str(value)+"' configured for attribute "+attr+" in plugin.conf, using '"+str(result)+"' instead")
        return result

    def get_local_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.10.10.10", 80))
        return s.getsockname()[0]

    def __init__(self, sh, port=None, threads=8, ip='', updates_allowed='True', user="admin", password="", hashed_password="", language="", developer_mode="no", pypi_timeout=5):
        self.logger = logging.getLogger(__name__)
        self._user = user
        self._password = password
        self._hashed_password = hashed_password

        if self._password is not None and self._password != "" and self._hashed_password is not None and self._hashed_password != "":
            self.logger.warning("BackendServer: Both 'password' and 'hashed_password' given. Ignoring 'password' and using 'hashed_password'!")
            self._password = None

        if self._password is not None and self._password != "" and (self._hashed_password is None or self._hashed_password == ""):
            self.logger.warning("BackendServer: Giving plaintext password in configuration is insecure. Consider using 'hashed_password' instead!")
            self._hashed_password = None

        if (self._password is not None and self._password != "") or (self._hashed_password is not None and self._hashed_password != ""):
            self._basic_auth = True
        else:
            self._basic_auth = False
        self._sh = sh

        if self.is_int(port):
            self.port = int(port)
        else:
            self.port = 8383
            if port is not None:
                self.logger.error("BackendServer: Invalid value '"+str(port)+"' configured for attribute 'port' in plugin.conf, using '"+str(self.port)+"' instead")

        if self.is_int(threads):
            self.threads = int(threads)
        else:
            self.threads = 8
            self.logger.error("BackendServer: Invalid value '"+str(threads)+"' configured for attribute 'thread' in plugin.conf, using '"+str(self.threads)+"' instead")

        if ip == '':
            ip = self.get_local_ip_address()
            self.logger.debug("BackendServer: Using local ip address '{0}'".format(ip))
        else:
            pass
        #    if not self.is_ip(ip):
        #         self.logger.error("BackendServer: Invalid value '"+str(ip)+"' configured for attribute ip in plugin.conf, using '"+str('0.0.0.0')+"' instead")
        #         ip = '0.0.0.0'
        language = language.lower()
        if language != '':
            if not load_translation(language):
                self.logger.warning("BackendServer: Language '{0}' not found, using standard language instead".format(language))
        self.developer_mode =  self.my_to_bool(developer_mode, 'developer_mode', False)

        self.updates_allowed = self.my_to_bool(updates_allowed, 'updates_allowed', True)

        if self.is_int(pypi_timeout):
            self.pypi_timeout = int(pypi_timeout)
        else:
            self.pypi_timeout = 5
            if pypi_timeout is not None:
                self.logger.error("BackendServer: Invalid value '" + str(pypi_timeout) + "' configured for attribute 'pypi_timeout' in plugin.conf, using '" + str(self.pypi_timeout) + "' instead")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger.debug("BackendServer running from '{}'".format(current_dir))

        config = {'global': {
            'server.socket_host': ip,
            'server.socket_port': self.port,
            'server.thread_pool': self.threads,
            'engine.autoreload.on': False,
            'tools.staticdir.debug': True,
            'tools.trailing_slash.on': False
            },
            '/': {
                'tools.auth_basic.on': self._basic_auth,
                'tools.auth_basic.realm': 'earth',
                'tools.auth_basic.checkpassword': self.validate_password,
                'tools.staticdir.root': current_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir, 'static')
            }
        }
        self._cherrypy = cherrypy
        self._cherrypy.config.update(config)
        self._cherrypy.tree.mount(Backend(self, self.updates_allowed, language, self.developer_mode, self.pypi_timeout), '/', config = config)

    def run(self):
        self.logger.debug("BackendServer: rest run")
        #server.start()
        self._cherrypy.engine.start()
        self.logger.debug("BackendServer: engine started")
        #cherrypy.engine.block()
        self.alive = True

    def stop(self):
        self.logger.debug("BackendServer: shutting down")
        self._cherrypy.engine.exit()
        self.logger.debug("BackendServer: engine exited")
        self.alive = False

    def parse_item(self, item):
        pass

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        pass

    def validate_password(self, realm, username, password):
        if username != self._user or password is None or password == "":
            return False

        if self._hashed_password is not None:
            return Utils.check_hashed_password(password, self._hashed_password)
        elif self._password is not None:
            return password == self._password

        return False

    

class Backend(BackendCore, BackendBlocklyLogics):
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))+'/templates'))
    env.globals['get_basename'] = get_basename
    env.globals['is_userlogic'] = is_userlogic
    env.globals['_'] = translate
    
    def __init__(self, backendserver=None, updates_allowed=True, language='', developer_mode=False, pypi_timeout = 5):
        self.logger = logging.getLogger(__name__)
        self._bs = backendserver
        self._sh = backendserver._sh
        self.language = language
        self.updates_allowed = updates_allowed
        self.developer_mode = developer_mode
        self.pypi_timeout = pypi_timeout

        self._sh_dir = self._sh.base_dir
        self.visu_plugin = None
        self.visu_plugin_version = '1.0.0'

    def html_escape(self, str):
        return html_escape(str)


#if __name__ == "__main__":
#    server = BackendServer( None, port=8080, ip='0.0.0.0')
#    server.run()
