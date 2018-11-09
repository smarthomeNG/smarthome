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

# import jwt

from lib.module import Modules
from lib.shtime import Shtime

from .systemdata import SystemData
from .itemdata import ItemData
from .schedulerdata import SchedulerData
from .plugindata import PluginData
from .scenedata import SceneData
from .threaddata import ThreadData

suburl = 'admin'


class Admin():
    version = '0.2.1'
    longname = 'Admin module for SmartHomeNG'
    port = 0

    def __init__(self, sh, testparam=''):
        """
        Initialization Routine for the module
        """
        # TO DO: Shortname anders setzen (oder warten bis der Plugin Loader es beim Laden setzt
        self._shortname = self.__class__.__name__
        self._shortname = self._shortname.lower()

        self.logger = logging.getLogger(__name__)
        self._sh = sh
        self.shtime = Shtime.get_instance()
        self.logger.debug("Module '{}': Initializing".format(self._shortname))

        self.logger.debug("Module '{}': Parameters = '{}'".format(self._shortname, str(self._parameters)))

        try:
            self.mod_http = Modules.get_instance().get_module(
                'http')  # try/except to handle running in a core version that does not support modules
        except:
            self.mod_http = None
        if self.mod_http == None:
            self.logger.error(
                "Module '{}': Not initializing - Module 'http' has to be loaded BEFORE this module".format(
                    self._shortname))
            self._init_complete = False
            return

        try:
            self.pypi_timeout = self._parameters['pypi_timeout']
            self.itemtree_fullpath = self._parameters['itemtree_fullpath']
            self.itemtree_searchstart = self._parameters['itemtree_searchstart']
            self.websocket_host = self._parameters['websocket_host']
            self.websocket_port = self._parameters['websocket_port']
        except:
            self.logger.critical(
                "Module '{}': Inconsistent module (invalid metadata definition)".format(self.shortname))
            self._init_complete = False
            return

        mysuburl = ''
        if suburl != '':
            mysuburl = '/' + suburl
        ip = get_local_ipv4_address()
        self.port = self.mod_http._port
        # self.logger.warning('port = {}'.format(self.port))
        self.url_root = 'http://' + ip + ':' + str(self.port) + mysuburl
        self.api_url_root = 'http://' + ip + ':' + str(self.port) + 'api'

    def start(self):
        """
        If the module needs to startup threads or uses python modules that create threads,
        put thread creation code or the module startup code here.

        Otherwise don't enter code here
        """

        self.webif_dir = os.path.dirname(os.path.abspath(__file__)) + '/webif'

        self.logger.info("Module '{}': webif_dir = webif_dir = {}".format(self._shortname, self.webif_dir))
        config = {
            '/': {
                'tools.staticdir.root': self.webif_dir,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static',
                'tools.staticdir.index': 'index.html',
                'error_page.404': self.webif_dir + '/static/index.html',
                #                    'error_page.404': self.error_page,
                #                   'tools.auth_basic.on': False,
                #                   'tools.auth_basic.realm': 'shng_admin_webif',
            }
        }
        config2 = {
            '/': {
                'tools.staticdir.root': self.webif_dir,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static',
                'tools.staticdir.index': 'index.html',
                # 'error_page.404': self.webif_dir + '/static/index.html',
                'error_page.404': self.error_page,
                # 'tools.auth_basic.on': False,
                # 'tools.auth_basic.realm': 'shng_admin_webif',
            }
        }

        # def register_webif(self, app, pluginname, conf, pluginclass='', instance='', description='', webifname='', use_global_basic_auth=True):
        """
        Register an application for CherryPy

        This method is called by a plugin to register a webinterface

        It should be called like this:

            self.mod_http.register_webif(WebInterface( ... ), 
                               self.get_shortname(), 
                               config, 
                               self.get_classname(), self.get_instance_name(),
                               description,
                               webifname,
                               use_global_basic_auth)


        :param app: Instance of the application object
        :param pluginname: Mount point for the application
        :param conf: Cherrypy application configuration dictionary
        :param pluginclass: Name of the plugin's class
        :param instance: Instance of the plugin (if multi-instance)
        :param description: Description of the functionallity of the webif. If left empty, a generic description will be generated
        :param webifname: Name of the webinterface. If left empty, the pluginname is used
        :param use_global_basic_auth: if True, global basic_auth settings from the http module are used. If False, registering plugin provides its own basic_auth
        """

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(self.webif_dir, self, self.url_root),
                                     suburl,
                                     config,
                                     'admin', '',
                                     description='Administrationsoberfläche für SmartHomeNG',
                                     webifname='',
                                     use_global_basic_auth=False)

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebApi(self.webif_dir, self, self.api_url_root),
                                     'api',
                                     config,
                                     'api', '',
                                     description='API der Administrationsoberfläche für SmartHomeNG',
                                     webifname='',
                                     use_global_basic_auth=False)
        return


    def stop(self):
        """
        If the module has started threads or uses python modules that created threads,
        put cleanup code here.

        Otherwise don't enter code here
        """
        #        self.logger.debug("Module '{}': Shutting down".format(self.shortname))
        pass

    def error_page(self, status, message, traceback, version):
        """
        Error 404 page, that redirects to index.html of Angular application

        :param status:
        :param message:
        :param traceback:
        :param version:

        :return: page to display (a redirect)
        :rtype: str
        """
        ip = get_local_ipv4_address()
        mysuburl = ''
        if suburl != '':
            mysuburl = '/' + suburl

        #        page = '<meta http-equiv="refresh" content="0; url=http://' + ip + ':' + str(self.port) + mysuburl + '/" />'
        page = '<meta http-equiv="refresh" content="0; url=' + self.url_root + '/" />'
        self.logger.warning(
            "error_page: status = {}, message = {}, redirecting to = {}, version = {}".format(status, message,
                                                                                              self.url_root, version))
        return page


def get_local_ipv4_address():
    """
    Get's local ipv4 address of the interface with the default gateway.
    Return '127.0.0.1' if no suitable interface is found

    :return: IPv4 address as a string
    :rtype: string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def translate(s):
    return s


import socket

import lib.config
from lib.item import Items
from lib.plugin import Plugins
from lib.utils import Utils


class WebInterface(SystemData, ItemData, SchedulerData, PluginData, SceneData, ThreadData):

    def __init__(self, webif_dir, module, url_root):
        self._sh = module._sh
        self.logger = logging.getLogger(__name__)
        self.module = module
        self.pypi_timeout = module.pypi_timeout
        self.url_root = url_root

        SystemData.__init__(self)
        ItemData.__init__(self)
        SchedulerData.__init__(self)
        PluginData.__init__(self)
        SceneData.__init__(self)
        ThreadData.__init__(self)

        return


    # -----------------------------------------------------------------------------------
    #    SERVERINFO
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def shng_serverinfo_json(self):
        """

        :return:
        """
        client_ip = cherrypy.request.wsgi_environ.get('REMOTE_ADDR')

        response = {}
        response['default_language'] = self._sh.get_defaultlanguage()
        response['client_ip'] = client_ip
        response['itemtree_fullpath'] = self.module.itemtree_fullpath
        response['itemtree_searchstart'] = self.module.itemtree_searchstart
        response['tz'] = self.module.shtime.tz
        response['tzname'] = str(self.module.shtime.tzname())
        response['websocket_host'] = self.module.websocket_host
        response['websocket_port'] = self.module.websocket_port
        return json.dumps(response)


class WebApi():

    def __init__(self, webif_dir, module, url_root):
        self._sh = module._sh
        self.logger = logging.getLogger(__name__)
        self.module = module
        self.url_root = url_root

        return


    # -----------------------------------------------------------------------------------
    #    LOGIN (Zukunft: /api/authenticate)
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def authenticate(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.warning("api authenticate login: rawbody = {}".format(rawbody))
        credentials = json.loads(rawbody)
        self.logger.warning("api authenticate login: credentials username = {}, password = {}".format(credentials['username'], credentials['password']))


        response = {}
        return json.dumps(response)


    # -----------------------------------------------------------------------------------
    #    SERVERINFO
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def shng_serverinfo2_json(self):
        """

        :return:
        """
        client_ip = cherrypy.request.wsgi_environ.get('REMOTE_ADDR')

        response = {}
        response['default_language'] = self._sh.get_defaultlanguage()
        response['client_ip'] = client_ip
        response['itemtree_fullpath'] = self.module.itemtree_fullpath
        response['itemtree_searchstart'] = self.module.itemtree_searchstart
        response['tz'] = self.module.shtime.tz
        response['tzname'] = str(self.module.shtime.tzname())
        response['websocket_host'] = self.module.websocket_host
        response['websocket_port'] = self.module.websocket_port
        return json.dumps(response)