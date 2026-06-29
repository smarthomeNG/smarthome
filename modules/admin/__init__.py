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
from .api_system import *
from .api_threads import *

from .api_logics import *
from .api_plugins import *
from .api_plugin import *
# from .api_plginst import *

suburl = 'admin'


class Admin(Module):
    version = '1.9.0'
    longname = 'Admin module for SmartHomeNG'
    _port = 0

    _stop_methods = []  # list of stop methods defined by the various controllers of the admin api

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
            self.mod_http = Modules.get_instance().get_module(
                'http'
            )  # try/except to handle running in a core version that does not support modules
        except Exception:
            self.mod_http = None
        if self.mod_http is None:
            self.logger.error(
                "Module '{}': Not initializing - Module 'http' has to be loaded BEFORE this module".format(
                    self._shortname
                )
            )
            self._init_complete = False
            return

        self._showtraceback = self.mod_http._showtraceback

        try:
            self.login_expiration = self._parameters['login_expiration']
            self.login_autorenew = self._parameters['login_autorenew']
            self.pypi_timeout = self._parameters['pypi_timeout']
            self.itemtree_fullpath = self._parameters['itemtree_fullpath']
            self.itemtree_searchstart = self._parameters['itemtree_searchstart']
            self.log_chunksize = self._parameters['log_chunksize']
            self.developer_mode = self._parameters['developer_mode']
            self.rest_dispatch_force_exception = self._parameters['rest_dispatch_force_exception']
            self.click_dropdown_header = self._parameters['click_dropdown_header']
        except Exception:
            self.logger.critical(
                "Module '{}': Inconsistent module (invalid metadata definition)".format(self._shortname)
            )
            self._init_complete = False
            return

        # Deprecation: websocket_host/websocket_port belong to the websocket module,
        # not to the admin module.  Warn users who still have them in admin config.
        _dep_host = self._parameters.get('websocket_host')
        _dep_port = self._parameters.get('websocket_port')
        _default_ws_port = 2424
        if _dep_host:
            self.logger.warning(
                "Module '{}': Parameter 'websocket_host' is DEPRECATED in the admin module. "
                "Configure it in the websocket module instead. The websocket module's value will be used.".format(
                    self._shortname
                )
            )
        if _dep_port is not None and _dep_port != _default_ws_port:
            self.logger.warning(
                "Module '{}': Parameter 'websocket_port' is DEPRECATED in the admin module. "
                "Configure it in the websocket module instead. The websocket module's value will be used.".format(
                    self._shortname
                )
            )

        # Stash deprecated fallback values so start() can use them if the
        # websocket module is genuinely absent.  The authoritative lookup is
        # deferred to start() because module __init__ methods run before any
        # module's start() is called, so get_module('websocket') always returns
        # None here even when the websocket module is properly configured.
        self._ws_dep_host = _dep_host or None
        self._ws_dep_port = str(_dep_port) if _dep_port else str(_default_ws_port)
        self._ws_default_port = str(_default_ws_port)
        self.websocket_host = None
        self.websocket_port = str(_default_ws_port)

        mysuburl = ''
        if suburl != '':
            mysuburl = '/' + suburl
        ip = Utils.get_local_ipv4_address()
        self._port = self.mod_http._port
        # self.logger.warning('port = {}'.format(self._port))
        self.shng_url_root = 'http://' + ip + ':' + str(self._port)  # for links mto plugin webinterfaces
        self.url_root = self.shng_url_root + mysuburl
        self.api_url_root = self.shng_url_root + 'api'

    def start(self):
        """
        Start the admin module

        Initialization and startup code of the module
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'start()'}))

        # Resolve websocket host/port now that all modules are started.
        try:
            mod_ws = Modules.get_instance().get_module('websocket')
            if mod_ws is not None:
                actual_port = mod_ws.get_port()
                if actual_port:
                    self.websocket_port = str(actual_port)
                # Use the websocket module's bind IP only when it is a specific
                # address; 0.0.0.0 / :: are wildcard bind addresses that the
                # browser cannot connect to.
                ws_ip = getattr(mod_ws, 'ip', None)
                if ws_ip and ws_ip not in ('0.0.0.0', '::', ''):
                    self.websocket_host = ws_ip
            else:
                self.logger.warning(
                    "Module '{}': Websocket module not found; falling back to admin module parameters.".format(
                        self._shortname
                    )
                )
                self.websocket_host = self._ws_dep_host
                self.websocket_port = self._ws_dep_port
        except Exception as e:
            self.logger.warning("Module '{}': Could not read websocket module config: {}".format(self._shortname, e))

        self.webif_dir = os.path.dirname(os.path.abspath(__file__)) + '/webif'

        self.logger.info("Module '{}': webif_dir = webif_dir = {}".format(self._shortname, self.webif_dir))
        # config for Angular app (special: error page)
        config = {
            '/': {
                'tools.staticdir.root': self.webif_dir,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static/browser',
                'tools.staticdir.index': 'index.html',
                'tools.chaching.on': False,
                'tools.caching.force': False,
                'tools.caching.delay': 6,
                'tools.expires.on': True,
                'tools.expires.secs': 0,
                # fix for path error
                'error_page.404': self._spa_index,
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
                'error_page.404': self._error_page_json,
                'error_page.400': self._error_page_json,
                'error_page.401': self._error_page_json,
                'error_page.405': self._error_page_json,
                'error_page.411': self._error_page_json,
                'error_page.500': self._error_page_json,
            }
        }

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(
            WebInterface(self.webif_dir, self, self.shng_url_root, self.url_root),
            suburl,
            config,
            'admin',
            '',
            description='Administrationsoberfläche für SmartHomeNG',
            webifname='',
            use_global_basic_auth=False,
            useprefix=False,
        )

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(
            WebApi(self.webif_dir, self, self.shng_url_root, self.api_url_root),
            'api',
            config_api,
            'api',
            '',
            description='API der Administrationsoberfläche für SmartHomeNG',
            webifname='',
            use_global_basic_auth=False,
            useprefix=False,
        )

        # Angular's polyfills bundle requests /3rdpartylicenses.txt at the server
        # root (not relative to base-href), so serve it from the root app.
        license_file = os.path.join(self.webif_dir, 'static', '3rdpartylicenses.txt')
        if os.path.isfile(license_file) and '' in cherrypy.tree.apps:
            cherrypy.tree.apps[''].config['/3rdpartylicenses.txt'] = {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': license_file,
            }

    def stop(self):
        """ """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'stop()'}))

        self.logger.info(f'Shutting down {self._shortname}')
        for stop_method in self._stop_methods:
            stop_method()
        self.logger.info(f'{self._shortname} shut down ')

    def add_stop_method(self, method, classname=''):
        """
        Class instances that implement their own stop() method should add those methods through this
        Method, so the stop() methods of the admin module can stop those instances too when stopping the module.

        :param method: stop-method to be added
        :param classname: Name of the class (optional)
        :type method: object
        :type classname: str
        """
        self.logger.info('Adding stop method of class {}'.format(classname))
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
        self.logger.warning('error_page: status = {}, message = {}'.format(status, message))
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
        result += (
            '<div class="container mt-4 ml-0">'
            '<h1 class="margin-base-vertical">'
            '<img src="/gstatic/img/logo_small_120x120.png" width="40" height="40" style="vertical-align:top">'
        )
        result += ' Oops, Error ' + errno + ':'
        result += '</h1><br/>'
        result += '<h3>' + message + '</h3><br/>'

        if not self._showtraceback or (errno == '404'):
            traceback = ''
        else:
            traceback = traceback.replace('\n', '<br>&nbsp;&nbsp;')
            traceback = traceback.replace(' ', '&nbsp;&nbsp;')
            traceback = '&nbsp;&nbsp;' + traceback

            result += (
                '<div class="card">'
                '<div class="card-header"><strong>Traceback</strong></div>'
                '<div class="card-body text-shng">'
            )
            result += traceback
            result += '</div></div>'

        result += '</div>'

        return result

    def _error_page_json(self, status, message, traceback, version):
        """
        JSON error body for the /api tree, used in place of _error_page()'s
        HTML.  The shngadmin frontend reads the message via
        ``err.error.error`` (see e.g. ItemTreeComponent) — until this
        existed, that field was always undefined for every API error
        (the response body was an HTML page, not JSON), silently breaking
        every error-message-driven flow (cycle/collision wording,
        offering to auto-create missing parent items on rename, etc.) —
        callers always fell through to a generic fallback string instead.

        :param status: error number and description, e.g. "400 Bad Request"
        :param message: detailed error description
        :param traceback: traceback that lead to the error
        :param version: CherryPy version
        :type status: str
        :type message: str
        :type traceback: str
        :type version: str

        :return: JSON-encoded error body
        :rtype: str
        """
        cherrypy.response.headers['Content-Type'] = 'application/json'
        errno = status.split()[0]
        body = {'error': message, 'status': errno}
        if self._showtraceback and errno == '500':
            body['traceback'] = traceback
        return json.dumps(body)

    def _spa_index(self, status, message, traceback, version):
        cherrypy.response.status = 200
        cherrypy.response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        cherrypy.response.headers['Pragma'] = 'no-cache'
        cherrypy.response.headers['Expires'] = '0'
        index_path = os.path.join(self.webif_dir, 'static', 'browser', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()


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

        SystemData.__init__(self, self._sh)
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
        self.system = SystemController(self.module)
        self.threads = ThreadsController(self.module)

        return

    @cherrypy.expose(['home', ''])
    def index(self):
        return 'Give SmartHomeNG a REST.'
