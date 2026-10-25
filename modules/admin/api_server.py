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
import threading
from pathlib import Path

import cherrypy

from .gitpull import PullTarget, check_repo, has_upstream, pull_all, pull_repo
from .rest import ApiDoc, RESTResource

import bin.shngversion
import lib.daemon
import lib.backup as backup
from lib.constants import DIR_ETC, DIR_MODULES
from lib.shpypi import Shpypi
from lib.syspower import PowerAction, is_supported, run_power_action


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
        p.wait()

    return str(result, encoding='utf-8', errors='strict')


# ======================================================================
#  Controller for REST API /api/server
#
class ServerController(RESTResource):
    """
    Controller for REST API /api/server
    """

    STOP_DELAY = 1.0  # seconds between sending the stop response and stopping the core

    PULL_STATUS_TIMEOUT = 15.0  # seconds per fetch when checking the checkouts for new commits

    PULL_ACTIONS: dict[str, PullTarget] = {'pull_core': 'core', 'pull_plugins': 'plugins', 'pull_all': 'all'}

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)  # not used?
        self.modules_dir = self._sh.get_config_dir(DIR_ETC)  # not used?
        self._pull_lock = threading.Lock()

    # ======================================================================
    #  /api/server
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
        http_user_dict = self.module.mod_http.get_user_dict()
        # http_user_dict always has only one entry
        response['login_required'] = any(u.get('password_hash') for u in http_user_dict.values())
        # Include websocket connection info so the frontend can set wsPort/wsHost
        # during APP_INITIALIZER (getServerBasicinfo) rather than waiting for the
        # later getServerinfo() call from TopNavigationComponent.  Without these
        # fields the frontend starts routing with wsPort='' and WebSocket-dependent
        # components (e.g. resource graphs) skip their connection on first load.
        response['websocket_port'] = self.module.websocket_port
        response['websocket_host'] = self.module.websocket_host
        # Also needed before initial routing, same reason as websocket_*
        # above: the frontend's default-route redirect resolves during the
        # router's initial navigation, which happens right after this
        # APP_INITIALIZER call completes - info() below runs too late for it.
        response['start_page'] = self.module.start_page

        return json.dumps(response)

    # ======================================================================
    #  /api/server/info
    #
    def info(self):
        """
        returns information if the root of the REST API is called

        Note: the root of the REST API is not protected by authentication
        """
        client_ip = cherrypy.request.wsgi_environ.get('REMOTE_ADDR')

        pull_availability = self.pull_availability
        response = {}
        response['default_language'] = self._sh.get_defaultlanguage()
        def_lang = response['default_language'].lower()
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
        response['client_ip'] = client_ip
        response['itemtree_fullpath'] = self.module.itemtree_fullpath
        response['itemtree_searchstart'] = self.module.itemtree_searchstart
        response['tz'] = self.module.shtime.tz()
        response['tzname'] = str(self.module.shtime.tzname())
        response['tznameST'] = str(self.module.shtime.tznameST())
        response['tznameDST'] = str(self.module.shtime.tznameDST())
        response['core_branch'] = bin.shngversion.get_shng_branch()
        response['plugins_branch'] = bin.shngversion.get_plugins_branch()
        response['websocket_host'] = self.module.websocket_host
        response['websocket_port'] = self.module.websocket_port
        response['log_chunksize'] = self.module.log_chunksize
        response['developer_mode'] = self.module.developer_mode
        response['click_dropdown_header'] = self.module.click_dropdown_header
        response['dark_mode'] = self.module.dark_mode
        response['resource_graph_period'] = self.module.resource_graph_period
        response['restart_stops_only'] = self._sh._mode in ('foreground', 'debug', 'interactive')
        response['system_power_available'] = self.system_power_available
        response['core_pull_available'] = pull_availability['core']
        response['plugins_pull_available'] = pull_availability['plugins']
        response['help_local_available'] = os.path.isfile(
            os.path.join(self._sh.get_basedir(), 'doc', 'user', 'build', 'html', 'index.html')
        )

        response['daemon_knx'] = self.get_knx_daemon()
        response['daemon_ow'] = self.get_1wire_daemon()
        response['daemon_mqtt'] = self.get_mqtt_daemon()
        response['daemon_node_red'] = self.get_node_red_daemon()
        response['backup_stem'] = ''
        try:
            response['backup_stem'] = self._sh._backup_name_stem
        except Exception:
            pass
        response['last_backup'] = backup.get_lastbackuptime()
        # response['pid'] = str(lib.daemon.read_pidfile(self._sh._pidfile))
        self.logger.info('ServerController.info(): response = {}'.format(response))
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
            if get_process_info('ps cax|grep eibd') != '':
                daemon = 'eibd'
            if get_process_info('ps cax|grep knxd') != '':
                if daemon != 'SERVICES.INACTIVE':
                    daemon += ' and knxd'
                else:
                    daemon = 'knxd'
                    # get version of installed knx daemon (knxd v0.14.30 outputs version to stderr instead of stdout)
                    wrk = get_process_info('knxd -l?V|grep knxd', append_error=True)
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
            if get_process_info('ps cax|grep owserver') != '':
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
            if get_process_info('ps cax|grep mosquitto') != '':
                daemon = 'mosquitto'
                # get version of installed mosquitto broker
                wrk = get_process_info('/usr/sbin/mosquitto -h|grep version')
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
            if get_process_info('ps cax|grep node-red') != '':
                daemon = 'node-red'
                # get version of installed node-red
                wrk = get_process_info('node-red --help|grep Node-RED')
                wrk = wrk.split()
                if wrk != []:
                    daemon += ' ' + wrk[1]
        return daemon

    # ======================================================================
    #  /api/server/status
    #
    def status(self):
        """
        return status of SmartHomeNG server software

        :return: status dict
        """
        try:
            response = self._sh.shng_status
        except AttributeError:
            response = {'code': -1, 'text': 'unknown'}

        # self.logger.debug("ServerController.index(): /{} - response '{}'".format(id, response))
        return json.dumps(response)

    # ======================================================================
    #  /api/server/restart
    #
    def restart(self):
        """
        restart the SmartHomneNG server software

        :return: status dict
        """
        self.logger.info('ServerController.restart()')

        status = self._sh.shng_status
        if status['code'] == 20:
            self._sh.restart('admin interface')
            response = {'result': 'ok'}
        else:
            response = {'result': 'error', 'text': "SmartHomeNG is not in state 'running'"}

        self.logger.info("ServerController.update(): /{} - response '{}'".format(id, response))
        return json.dumps(response)

    @property
    def system_power_available(self):
        """True if smarthome.yaml allows host power actions and the platform supports them."""
        return bool(self._sh._allow_system_power) and is_supported()

    def system_power(self, action: PowerAction):
        """
        power off or reboot the host the core runs on

        :param action: 'poweroff' or 'reboot'
        :return: status dict
        """
        self.logger.info(f'ServerController.system_power({action})')

        if not self.system_power_available:
            response = {'result': 'error', 'text': 'System power actions are not enabled (allow_system_power)'}
        else:
            ok, text = run_power_action(action)
            response = {'result': 'ok'} if ok else {'result': 'error', 'text': text}

        self.logger.info(f"ServerController.system_power(): response '{response}'")
        return json.dumps(response)

    @property
    def pull_repos(self) -> dict[str, Path]:
        """The checkouts the pull actions operate on, in pull order."""
        base = Path(self.base_dir)
        return {'core': base, 'plugins': base / 'plugins'}

    @property
    def pull_availability(self) -> dict[str, bool]:
        """Per checkout: True if its branch has an upstream, i.e. it can be pulled."""
        return {name: has_upstream(path) for name, path in self.pull_repos.items()}

    # /api/server/pull_status
    def pull_status(self):
        """
        fetch the upstream of the core and plugins checkout and report how each stands against it

        Only remote-tracking refs change, never the working tree. Refused while a pull is running.

        :return: status dict with one gitpull.RepoCheck per checkout in 'repos'
        """
        self.logger.info('ServerController.pull_status()')

        if not self._pull_lock.acquire(blocking=False):
            response = {'result': 'error', 'text': 'A pull is already running', 'repos': []}
        else:
            try:
                repos = [check_repo(name, path, self.PULL_STATUS_TIMEOUT) for name, path in self.pull_repos.items()]
            finally:
                self._pull_lock.release()
            response = {'result': 'ok', 'repos': repos}

        self.logger.info(f"ServerController.pull_status(): response '{response}'")
        return json.dumps(response)

    # /api/server/pull_core, pull_plugins, pull_all
    def pull(self, target: PullTarget):
        """
        fast-forward the core and/or plugins checkout to its upstream

        Only files on disk change; the running core keeps its loaded code until it is restarted.
        A second pull is refused while one is running.

        :param target: 'core', 'plugins' or 'all' (all or none, see gitpull.pull_all)
        :return: status dict with the per-repository results in 'repos'
        """
        self.logger.info(f'ServerController.pull({target})')

        if not self._pull_lock.acquire(blocking=False):
            response = {'result': 'error', 'text': 'A pull is already running', 'repos': []}
        else:
            try:
                repos = self.pull_repos
                if target == 'all':
                    results = pull_all(list(repos.items()))
                else:
                    results = [pull_repo(target, repos[target])]
            finally:
                self._pull_lock.release()
            failed = any(r['status'] == 'error' for r in results)
            response = {'result': 'error' if failed else 'ok', 'repos': results}

        self.logger.info(f"ServerController.pull(): response '{response}'")
        return json.dumps(response)

    # /api/server/stop
    def stop(self):
        """
        stop the SmartHomeNG server software without restarting it

        The core is stopped after STOP_DELAY seconds, so that the response
        reaches the client. Exit code 0 keeps a systemd service from
        restarting the core (only exit code 5 forces a restart).

        :return: status dict
        """
        self.logger.info('ServerController.stop()')

        if self._sh.shng_status['code'] == 20:
            threading.Timer(self.STOP_DELAY, self._sh.stop, kwargs={'exitcode': 0}).start()
            response = {'result': 'ok'}
        else:
            response = {'result': 'error', 'text': "SmartHomeNG is not in state 'running'"}

        self.logger.info(f"ServerController.stop(): response '{response}'")
        return json.dumps(response)

    # ======================================================================
    #  /api/server/pypi
    #
    def pypi(self):
        """
        Returns PyPI package requirement and availability information.

        Uses the Shpypi singleton's package_list when already populated so
        that in-place updates by the scheduler's lookup_pypi_releasedata job
        are reflected — mirroring the cache behaviour of the legacy endpoint.
        """
        shpypi = Shpypi.get_instance()
        if shpypi.package_list:
            source = shpypi.package_list
        else:
            source = shpypi.get_packagelist()
        sorted_list = sorted(source, key=lambda k: k['sort'], reverse=False)
        return json.dumps(sorted_list)

    # ======================================================================
    #  GET /api/server/
    #
    def read(self, id=''):
        """
        Handle GET requests for server API
        """
        self.logger.info(f"ServerController.read('{id}')")

        if id is None:
            return self.root()
        elif id == 'status':
            return self.status()
        elif id == 'info':
            return self.info()
        elif id == 'pypi':
            return self.pypi()
        elif id == 'pull_status':
            return self.pull_status()

        return None

    read.expose_resource = True
    read.authentication_needed = True
    read.public_root = True
    read.api_doc = [
        ApiDoc(
            summary=(
                'Basic server info: default_language, client_ip, login_required, '
                'websocket_host, websocket_port, start_page. Public even though '
                'flagged authentication_needed in code - exempted at the bare path '
                'via public_root. Also (ab)used as a lightweight reachability '
                'heartbeat.'
            ),
            method='get',
            path='/server/',
            tags=['server'],
            auth=False,
        ),
        ApiDoc(
            summary=(
                'Extended server info: timezone, core/plugins git branch, developer_mode, '
                'dark_mode default, resource_graph_period, restart_stops_only, system_power_available, core_pull_available, plugins_pull_available, and more.'
            ),
            method='get',
            path='/server/info',
            tags=['server'],
        ),
        ApiDoc(summary='shng core running/stopped status', method='get', path='/server/status/', tags=['server']),
        ApiDoc(summary='PyPI package/version check data', method='get', path='/server/pypi', tags=['server']),
        ApiDoc(
            summary=(
                'Fetch the upstream of the core and plugins checkout and report per checkout how it stands against it '
                '(state current/behind/ahead/diverged/blocked/no_upstream/unknown, behind, ahead, text). Changes '
                'remote-tracking refs only, never the working tree.'
            ),
            method='get',
            path='/server/pull_status',
            tags=['server'],
        ),
    ]

    def update(self, id='', level=None):
        """
        Handle PUT requests for server API
        """
        self.logger.info(f"ServerController.update('{id}'), level='{level}'")

        if id == 'restart':
            return self.restart()
        if id == 'stop':
            return self.stop()
        if id in self.PULL_ACTIONS:
            return self.pull(self.PULL_ACTIONS[id])
        if id in ('poweroff', 'reboot'):
            return self.system_power(id)

        return None

    update.expose_resource = True
    update.authentication_needed = True
    update.api_doc = [
        ApiDoc(summary='Restart shng core', method='put', path='/server/restart/', tags=['server']),
        ApiDoc(summary='Stop shng core without restarting it', method='put', path='/server/stop/', tags=['server']),
        ApiDoc(
            summary=(
                'Fast-forward the core checkout to its upstream (git pull --ff-only). Only files on disk change, '
                'the running core needs a restart to use them. Response: result and per-repository results '
                '(repo, status, text, changed).'
            ),
            method='put',
            path='/server/pull_core/',
            tags=['server'],
        ),
        ApiDoc(
            summary='Same as pull_core, for the plugins checkout',
            method='put',
            path='/server/pull_plugins/',
            tags=['server'],
        ),
        ApiDoc(
            summary=(
                'Fast-forward core and plugins checkouts, or neither: nothing is pulled unless both have an '
                'upstream, can be fast-forwarded and have no local changes in the way. Same response as pull_core.'
            ),
            method='put',
            path='/server/pull_all/',
            tags=['server'],
        ),
        ApiDoc(
            summary='Power off the host (requires allow_system_power in smarthome.yaml)',
            method='put',
            path='/server/poweroff/',
            tags=['server'],
        ),
        ApiDoc(
            summary='Reboot the host (requires allow_system_power in smarthome.yaml)',
            method='put',
            path='/server/reboot/',
            tags=['server'],
        ),
    ]
