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
import sys
import socket
import platform
if os.name != 'nt':
    import pwd
import psutil
import datetime
import time
import json
import cherrypy

import bin.shngversion as shngversion
from .rest import RESTResource

#import bin.shngversion
import lib.daemon
import lib.backup as backup
from lib.shpypi import Shpypi
from lib.shtime import Shtime
from lib.utils import Utils
from lib.constants import (DIR_ETC, DIR_MODULES)


# ======================================================================
#  Functions to be moved to utils
#
def get_process_info(command, wait=True, append_error=False):
    """
    returns output from executing a given command via the shell.
    """
    ## get subprocess module
    import subprocess

    ## call date command ##
    if append_error:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    else:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    # Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
    # Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
    # Wait for process to terminate. The optional input argument should be a string to be sent to the child process, or None, if no data should be sent to the child.
    (result, err) = p.communicate()
#    logger.warning("get_process_info: command='{}', result='{}', err='{}'".format(command, result, err))

    if wait:
        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()

    return str(result, encoding='utf-8', errors='strict')


# ======================================================================
#  Controller for REST API /api/server
#
class SystemController(RESTResource):
    """
    Controller for REST API /api/server
    """

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)  # not used?
        self.modules_dir = self._sh.get_config_dir(DIR_ETC)  # not used?


    # ======================================================================
    #  /api/system
    #
    def root(self):
        """
        returns information if the root of the REST API is called

        Note: the root of the REST API is not protected by authentication
        """
        client_ip = cherrypy.request.wsgi_environ.get('REMOTE_ADDR')

        response = {}
        response['default_language'] = self._sh.get_defaultlanguage()
        response['client_ip'] = client_ip
        return json.dumps(response)


    # ======================================================================
    #  /api/system/info
    #
    def info(self):
        """
        returns information if the root of the REST API is called

        Note: the root of the REST API is not protected by authentication
        """

        now = str(self.module.shtime.now())
        tzname = self.module.shtime.tzname()
        system = platform.system()

        #self.read_linuxinfo()
        #vers = Utils.strip_quotes(self.os_release.get('PRETTY_NAME', ''))
        vers = self._sh.systeminfo.get_osname()
        if vers == '':
            vers = platform.version()
        arch = platform.machine()
        # node = platform.node()
        node = socket.getfqdn()
        if os.name != 'nt':
            user = pwd.getpwuid(os.geteuid()).pw_name  # os.getlogin()
        else:
            user = os.getlogin()

        if os.name != 'nt':
            space = os.statvfs(self._sh.base_dir)
            freespace = space.f_frsize * space.f_bavail / 1024 / 1024
        else:
            space = psutil.disk_usage(self._sh.base_dir)
            freespace = space.free / 1024 / 1024

        rt = Shtime.get_instance().runtime_as_dict()
        sh_runtime_seconds = rt['total_seconds']

        pyversion = "{0}.{1}.{2} {3}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2],
                                             sys.version_info[3])

        response = {}
        response['tzname'] = tzname

        # Hardware
        response['hardware'] = self._sh.systeminfo.get_rasppi_info()
        if response['hardware'] == '':
            response['hardware'] = self._sh.systeminfo.get_cpubrand()
        response['arch'] = arch
        response['rasppi'] = self._sh.systeminfo.running_on_rasppi()
        if self._sh.systeminfo.cpu_speed_class is not None:
            response['hwspeed'] = self._sh.systeminfo.cpu_speed_class

        # Betriebssystem
        response['system'] = system
        response['ostype'] = self._sh.systeminfo.get_ostype()
        response['osflavor'] = self._sh.systeminfo.get_osflavor()
        response['vers'] = vers
        response['node'] = node
        # ip = Utils.get_local_ipv4_address()
        ip = Utils.get_all_local_ipv4_addresses()
        if '127.0.0.1' in ip:
            ip.remove('127.0.0.1')
            #ip.append('127.0.0.1')
        if len(ip) == 1:
            response['ip'] = ip[0]
        else:
            response['ip'] = str(ip)
        ipv6 = Utils.get_local_ipv6_address()
        # ipv6 = Utils.get_all_local_ipv6_addresses()
        response['ipv6'] = str(ipv6)
        response['user'] = user
        response['freespace'] = freespace
        response['now'] = now
        response['uptime'] = time.mktime(datetime.datetime.now().timetuple()) - psutil.boot_time()
        response['tz'] = self.module.shtime.tz()
        response['tzname'] = str(self.module.shtime.tzname())
        response['tznameST'] = str(self.module.shtime.tznameST())
        response['tznameDST'] = str(self.module.shtime.tznameDST())

        # Dienste
        response['daemon_knx'] = self.get_knx_daemon()
        response['daemon_ow'] = self.get_1wire_daemon()
        response['daemon_mqtt'] = self.get_mqtt_daemon()
        response['daemon_node_red'] = self.get_node_red_daemon()

        # Python
        response['pyversion'] = pyversion
        response['pyvirtual'] = lib.utils.running_virtual()
        response['pypath'] = self._sh.python_bin
        if os.name != 'nt':
            response['pid'] = str(lib.daemon.read_pidfile(self._sh._pidfile))
        else:
            response['pid'] = str(os.getpid())

        # SmartHomeNG
        response['sh_dir'] = self._sh.base_dir
        response['core_branch'] = shngversion.get_shng_branch()
        response['sh_vers'] = shngversion.get_shng_version()
        response['sh_desc'] = shngversion.get_shng_description()
        response['plugins_branch'] = shngversion.get_plugins_branch()
        response['plg_vers'] = shngversion.get_plugins_version()
        response['plg_desc'] = shngversion.get_plugins_description()
        response['sh_uptime'] = sh_runtime_seconds
        response['default_language'] = self._sh.get_defaultlanguage()
        def_lang = self._sh.get_defaultlanguage().lower()
        if def_lang == 'de':
            response['locale'] = 'de-DE'
        elif def_lang == 'en':
            response['locale'] = 'en-GB'
        elif def_lang == 'fr':
            response['locale'] = 'fr-FR'
        elif def_lang == 'es':
            response['locale'] = 'es-ES'
        else:
            response['locale'] = ''
        response['fallback_language_order'] = self._sh._fallback_language_order

        # ShngAdmin
        response['client_ip'] = cherrypy.request.wsgi_environ.get('REMOTE_ADDR')
        response['developer_mode'] = self.module.developer_mode
        response['websocket_host'] = self.module.websocket_host
        response['websocket_port'] = self.module.websocket_port
        response['click_dropdown_header'] = self.module.click_dropdown_header
        response['itemtree_fullpath'] = self.module.itemtree_fullpath
        response['itemtree_searchstart'] = self.module.itemtree_searchstart
        response['log_chunksize'] = self.module.log_chunksize
        response['backup_stem'] = ''
        try:
            response['backup_stem'] = self._sh._backup_name_stem
        except:
            pass
        response['last_backup'] = backup.get_lastbackuptime()

        self.logger.info("SystemController.info(): response = {}".format(response))
        return json.dumps(response)


    def get_knx_daemon(self):
        """
        Tests it knxd or eibd are running
        """
        # knxd_service = get_process_info("systemctl status knxd.service")
        # smarthome_service = get_process_info("systemctl status smarthome.service")
        # knxd_socket = get_process_info("systemctl status knxd.socket")

        daemon = 'SERVICES.INACTIVE'
        if os.name != 'nt':
            if get_process_info("ps cax|grep eibd") != '':
                daemon = 'eibd'
            if get_process_info("ps cax|grep knxd") != '':
                if daemon != 'SERVICES.INACTIVE':
                    daemon += ' and knxd'
                else:
                    daemon = 'knxd'
                    # get version of installed knx daemon (knxd v0.14.30 outputs version to stderr instead of stdout)
                    wrk = get_process_info("knxd -l?V|grep knxd", append_error=True)
                    wrk = wrk.split()
                    wrk = wrk[1].split(':')
                    if wrk != []:
                        daemon += ' v' + wrk[0]
        return daemon


    def get_1wire_daemon(self):
        """
        Tests it 1wire are running
        """
        daemon = 'SERVICES.INACTIVE'
        if os.name != 'nt':
            if get_process_info("ps cax|grep owserver") != '':
                daemon = 'owserver'
                # get version of installed owserver
                wrk = get_process_info("owserver -V|grep 'owserver version'", append_error=True)
                wrk = wrk.split()
                if wrk != []:
                    daemon += ' v' + wrk[2]
        return daemon


    def get_mqtt_daemon(self):
        """
        Tests it 1wire are running
        """
        daemon = 'SERVICES.INACTIVE'
        if os.name != 'nt':
            # test id mqtt broker is running
            if get_process_info("ps cax|grep mosquitto") != '':
                daemon = 'mosquitto'
                # get version of installed mosquitto broker
                wrk = get_process_info("/usr/sbin/mosquitto -h|grep version")
                wrk = wrk.split()
                if wrk != []:
                    daemon += ' v' + wrk[2]
        return daemon


    def get_node_red_daemon(self):
        """
        Tests it 1wire are running
        """
        daemon = 'SERVICES.INACTIVE'
        if os.name != 'nt':
            if get_process_info("ps cax|grep node-red") != '':
                daemon = 'node-red'
                # get version of installed node-red
                wrk = get_process_info("node-red --help|grep Node-RED")
                wrk = wrk.split()
                if wrk != []:
                    daemon += ' ' + wrk[1]
        return daemon


    # ======================================================================
    #  /api/system/status
    #
    # def status(self):
    #     """
    #     return status of SmartHomeNG server software
    #
    #     :return: status dict
    #     """
    #     try:
    #         response = self._sh.shng_status
    #     except:
    #         response = {'code': -1, 'text': 'unknown'}
    #
    #     # self.logger.debug("ServerController.index(): /{} - response '{}'".format(id, response))
    #     return json.dumps(response)


    # # ======================================================================
    # #  /api/server/restart
    # #
    # def restart(self):
    #     """
    #     restart the SmartHomneNG server software
    #
    #     :return: status dict
    #     """
    #     self.logger.info("ServerController.restart()")
    #
    #     status = self._sh.shng_status
    #     if status['code'] == 20:
    #         self._sh.restart('admin interface')
    #         response = {'result': 'ok'}
    #     else:
    #         response = {'result': 'error', 'text': "SmartHomeNG is not in state 'running'"}
    #
    #     self.logger.info("ServerController.update(): /{} - response '{}'".format(id, response))
    #     return json.dumps(response)
    #
    #
    # ======================================================================
    #  GET /api/system/
    #
    def read(self, id=''):
        """
        Handle GET requests for server API
        """
        self.logger.info(f"ServerController.read('{id}')")

        if id is None:
            return self.root()
        # elif id == 'status':
        #     return self.status()
        elif id == 'info':
            return self.info()

        return None

    read.expose_resource = True
    read.authentication_needed = True
    # read.public_root = True


    def update(self, id='', level=None):
        """
        Handle PUT requests for server API
        """
        self.logger.info(f"ServerController.update('{id}'), level='{level}'")

        # if id == 'restart':
        #     return self.restart()

        return None

    # update.expose_resource = True
    # update.authentication_needed = True

