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
import cherrypy

from lib.utils import Utils

from lib.model.module import Module
from lib.module import Modules
from lib.shtime import Shtime

from .systemdata import SystemData
from .itemdata import ItemData
from .plugindata import PluginData

from .rest import RESTResource

from .api_server import *
from .api_auth import *

from .api_config import *
from .api_files import *
from .api_items import *
from .api_functions import *
from .api_loggers import *
from .api_logs import *
from .api_scenes import *
from .api_sched import *
from .api_services import *
from .api_threads import *

from .api_logics import *
from .api_plugins import *
from .api_plugin import *
#from .api_plginst import *


suburl = 'admin'


class Admin(Module):
    version = '1.8.0'
    longname = 'Admin module for SmartHomeNG'
    _port = 0

    _stop_methods = []      # list of stop methods defined by the various controllers of the admin api

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

        # for authentication
        self.send_hash = 'shNG0160$'
        self.jwt_secret = 'SmartHomeNG$0815'

        try:
            self.mod_http = Modules.get_instance().get_module('http')  # try/except to handle running in a core version that does not support modules
        except:
            self.mod_http = None
        if self.mod_http is None:
            self.logger.error(
                "Module '{}': Not initializing - Module 'http' has to be loaded BEFORE this module".format(
                    self._shortname))
            self._init_complete = False
            return

        self._showtraceback = self.mod_http._showtraceback

        try:
            self.login_expiration = self._parameters['login_expiration']
            self.login_autorenew = self._parameters['login_autorenew']
            self.pypi_timeout = self._parameters['pypi_timeout']
            self.itemtree_fullpath = self._parameters['itemtree_fullpath']
            self.itemtree_searchstart = self._parameters['itemtree_searchstart']
            self.websocket_host = self._parameters['websocket_host']
            self.websocket_port = self._parameters['websocket_port']
            self.log_chunksize = self._parameters['log_chunksize']
            self.developer_mode = self._parameters['developer_mode']
            self.click_dropdown_header = self._parameters['click_dropdown_header']
        except:
            self.logger.critical(
                "Module '{}': Inconsistent module (invalid metadata definition)".format(self._shortname))
            self._init_complete = False
            return

        mysuburl = ''
        if suburl != '':
            mysuburl = '/' + suburl
        ip = Utils.get_local_ipv4_address()
        self._port = self.mod_http._port
        # self.logger.warning('port = {}'.format(self._port))
        self.shng_url_root = 'http://' + ip + ':' + str(self._port)         # for links mto plugin webinterfaces
        self.url_root = self.shng_url_root + mysuburl
        self.api_url_root = self.shng_url_root + 'api'
        self.api2_url_root = self.shng_url_root + 'api2'

    def start(self):
        """
        Start the admin module

        Initialization and startup code of the module
        """

        self.webif_dir = os.path.dirname(os.path.abspath(__file__)) + '/webif'

        self.logger.info("Module '{}': webif_dir = webif_dir = {}".format(self._shortname, self.webif_dir))
        # config for Angular app (special: error page)
        config = {
            '/': {
                'tools.staticdir.root': self.webif_dir,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static',
                'tools.staticdir.index': 'index.html',
                'tools.chaching.on': False,
                'tools.caching.force': False,
                'tools.caching.delay': 6,
                'tools.expires.on': True,
                'tools.expires.secs': 6,
                'error_page.404': self.webif_dir + '/static/index.html',
                #                    'error_page.404': self.error_page,
                #                   'tools.auth_basic.on': False,
                #                   'tools.auth_basic.realm': 'shng_admin_webif',
            }
        }
        # API config (special: request.dispatch)
        config_api = {
            '/': {
                'tools.chaching.on': False,
                'tools.caching.force': False,
                'tools.caching.delay': 6,
                'tools.expires.on': True,
                'tools.expires.secs': 6,
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'error_page.404': self._error_page,
                'error_page.400': self._error_page,
                'error_page.401': self._error_page,
                'error_page.405': self._error_page,
                'error_page.411': self._error_page,
                'error_page.500': self._error_page,
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
                               use_global_basic_auth
                               useprefix)


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
        self.mod_http.register_webif(WebInterface(self.webif_dir, self, self.shng_url_root, self.url_root),
                                     suburl,
                                     config,
                                     'admin', '',
                                     description='Administrationsoberfläche für SmartHomeNG',
                                     webifname='',
                                     use_global_basic_auth=False,
                                     useprefix=False)

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebApi(self.webif_dir, self, self.shng_url_root, self.api_url_root),
                                     'api',
                                     config_api,
                                     'api', '',
                                     description='API der Administrationsoberfläche für SmartHomeNG',
                                     webifname='',
                                     use_global_basic_auth=False,
                                     useprefix=False)

        return

    def stop(self):
        """

        """

        self.logger.info(f"Shutting down {self._shortname}")
        for stop_method in self._stop_methods:
            stop_method()
        self.logger.info(f"{self._shortname} shut down ")

    def add_stop_method(self, method, classname=''):
        """
        Class instances that implement their own stop() method should add those methods through this
        Method, so the stop() methods of the admin module can stop those instances too when stopping the module.

        :param method: stop-method to be added
        :param classname: Name of the class (optional)
        :type method: object
        :type classname: str
        """
        self.logger.info("Adding stop method of class {}".format(classname))
        self._stop_methods.append(method)


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
        # ip = Utils.get_local_ipv4_address()
        # mysuburl = ''
        # if suburl != '':
        #     mysuburl = '/' + suburl

        # page = '<meta http-equiv="refresh" content="0; url=http://' + ip + ':' + str(self._port) + mysuburl + '/" />'
        # page = '<meta http-equiv="refresh" content="0; url=' + self.url_root + '/" />'
        page = '404: Page not found!<br>' + message
        self.logger.warning(
            "error_page: status = {}, message = {}".format(status, message))
        return page

    def _error_page(self, status, message, traceback, version):
        """
        Generate html page for errors

        :param status: error number and description
        :param message: detailed error description
        :param traceback: traceback that lead to the error
        :param version: CherryPy version
        :type status: str
        :type message: str
        :type traceback: str
        :type version: str

        :return: html error page
        :rtype: str

        """
        # show_traceback = True
        errno = status.split()[0]
        result = '<link rel="stylesheet" href="/gstatic/bootstrap/css/bootstrap.min.css" type="text/css"/>'
        result += '<link rel="stylesheet" href="/gstatic/css/smarthomeng.css" type="text/css"/>'
        result += '<div class="container mt-4 ml-0">' \
                  '<h1 class="margin-base-vertical">' \
                  '<img src="/gstatic/img/logo_small_120x120.png" width="40" height="40" style="vertical-align:top">'
        result += ' Oops, Error ' + errno + ':'
        result += '</h1><br/>'
        result += '<h3>' + message + '</h3><br/>'

        if not self._showtraceback or (errno == '404'):
            traceback = ''
        else:
            traceback = traceback.replace('\n', '<br>&nbsp;&nbsp;')
            traceback = traceback.replace(' ', '&nbsp;&nbsp;')
            traceback = '&nbsp;&nbsp;' + traceback

            result += '<div class="card">' \
                      '<div class="card-header"><strong>Traceback</strong></div>' \
                      '<div class="card-body text-shng">'
            result += traceback
            result += '</div>' \
                      '</div>'

        result += '</div>'

        return result


def translate(s):
    # needed for Admin UI
    return s


class WebInterface(SystemData, ItemData, PluginData):

    def __init__(self, webif_dir, module, shng_url_root, url_root):
        self._sh = module._sh
        self.logger = logging.getLogger(__name__)
        self.module = module
        self.pypi_timeout = module.pypi_timeout
        self.shng_url_root = shng_url_root
        self.url_root = url_root

        SystemData.__init__(self)
        ItemData.__init__(self)
        PluginData.__init__(self)

        return


class WebApi(RESTResource):
    """
    :param webif_dir: Directory where the files of the web interface (shngadmin) are stored
    :param module: Instance of the webif object
    :param shng_url_root: ...
    :param url_root: ...
    :type webif_dir: str
    :type module: object
    :type shng_url_root: str
    :type url_root: str
    """

    exposed = True

    def __init__(self, webif_dir, module, shng_url_root, url_root):
        self._sh = module._sh
        self.logger = logging.getLogger(__name__)
        self.module = module
        self.shng_url_root = shng_url_root
        self.url_root = url_root


        # ------------------------------
        # ---  Add REST controllers  ---
        # ------------------------------
        self.authenticate = AuthController(self.module)

        self.config = ConfigController(self.module)
        self.files = FilesController(self.module)
        self.items = ItemsController(self.module)
        self.items.list = ItemsListController(self.module)
        self.functions = FunctionsController(self.module)
        self.functions.reload = FunctionsReloadController(self.module)
        self.logics = LogicsController(self.module)
        self.loggers = LoggersController(self.module)
        self.logs = LogsController(self.module)
        self.plugin = PluginController(self.module, self.jwt_secret)
        self.plugins = PluginsController(self.module)
        self.plugins.api = PluginsAPIController(self.module)
        self.plugins.installed = PluginsInstalledController(self.module)
        self.plugins.config = PluginsConfigController(self.module)
        self.plugins.info = PluginsInfoController(self.module, self.shng_url_root)
        self.plugins.logicparams = PluginsLogicParametersController(self.module)
        self.scenes = ScenesController(self.module)
        self.scenes.reload = ScenesReloadController(self.module)
        self.schedulers = SchedulersController(self.module)
        self.server = ServerController(self.module)
        self.services = ServicesController(self.module)
        self.threads = ThreadsController(self.module)

        return

    @cherrypy.expose(['home', ''])
    def index(self):
        return "Give SmartHomeNG a REST."
