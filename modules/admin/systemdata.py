#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
#  Copyright 2016-      René Frieß                  rene.friess@gmail.com
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

import os
import sys
import socket
import platform
import pwd
import psutil
import datetime
import time
import json

import cherrypy


import bin.shngversion as shngversion

from lib.shpypi import Shpypi
from lib.shtime import Shtime
from lib.utils import Utils
import lib.config
import lib.daemon


class SystemData:

    def __init__(self):

        self.pypi_sorted_package_list = []

        self.shpypi = Shpypi.get_instance()
        return


    # -----------------------------------------------------------------------------------
    #    SYSTEMINFO  -  Old Interface methods (from backend)
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def systeminfo_json(self):
        """
        Return System inforation as json (
        for Angular tests only)

        :return:
        """
#        now = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        now = str(self.module.shtime.now())
        system = platform.system()
        vers = platform.version()
        # node = platform.node()
        node = socket.getfqdn()
        arch = platform.machine()
        user = pwd.getpwuid(os.geteuid()).pw_name  # os.getlogin()

        ipv6 = Utils.get_local_ipv6_address()
        ip = Utils.get_local_ipv4_address()

        space = os.statvfs(self._sh.base_dir)
        freespace = space.f_frsize * space.f_bavail / 1024 / 1024

        rt = Shtime.get_instance().runtime_as_dict()
        sh_runtime_seconds = rt['total_seconds']

        pyversion = "{0}.{1}.{2} {3}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2],
                                             sys.version_info[3])

        response = {}
        response['now'] = now
        response['system'] = system
        response['sh_vers'] = shngversion.get_shng_version()
        response['sh_desc'] = shngversion.get_shng_description()
        response['plg_vers'] = shngversion.get_plugins_version()
        response['plg_desc'] = shngversion.get_plugins_description()
        response['sh_dir'] = self._sh.base_dir

        response['vers'] = vers
        response['node'] = node
        response['arch'] = arch
        response['user'] = user
        response['freespace'] = freespace
        response['uptime'] = time.mktime(datetime.datetime.now().timetuple()) - psutil.boot_time()
        response['sh_uptime'] = sh_runtime_seconds
        response['pyversion'] = pyversion
        response['ip'] = ip
        response['ipv6'] = ipv6
        response['pid'] = str(lib.daemon.read_pidfile(self._sh._pidfile))

        self.logger.debug("admin: systeminfo_json: response = {}".format(response))
        return json.dumps(response)


    # -----------------------------------------------------------------------------------
    #    SYSTEMINFO: PyPI Check
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def pypi_json(self):
        """
        returns a list of python package information dicts as json structure:

        The json response contains the following information:

            name                             str    Name of package
            vers_installed                   str    Installed version of that package
            is_required                      bool   is package required by SmartHomeNG?
            is_required_for_testsuite        bool   is package required for the testsuite?
            is_required_for_docbuild         bool   is package required for building documentation with Sphinx?
            vers_req_source                   str    requirements as defined inrequirements.txt
            vers_req_min                     str    required minimum version
            vers_req_max                     str    required maximum version
            vers_req_msg                     str
            vers_ok                          bool   installed version meets requirements
            vers_recent                      bool   installed version is the req_max or the newest on PyPI

            pypi_version                     str    newest package version on PyPI
            pypi_version_ok                  bool   is newest package version on PyPI ok for install on SmartHomeNG?
            pypi_version_not_available_msg   str    error message or empty
            pypi_doc_url                     str    url of the package's documentation on PyPI

            sort                             str    string for sorting (is_required + name)


        :return: information about packahge requirements including PyPI information
        :rtype: json structure
        """
        self.logger.info("pypi_json")

        if self.pypi_sorted_package_list != []:
            # return list, if it already has been prepared
            self.logger.info("Returning a previously prepared PpyPI package list")
            return json.dumps(self.pypi_sorted_package_list)

####
        package_list = self.shpypi.get_packagelist()

        # sorted_package_list = sorted([(i['name'], i['version_installed'], i['version_available']) for i in package_list])
        self.pypi_sorted_package_list = sorted(package_list, key=lambda k: k['sort'], reverse=False)
        self.logger.info("pypi_json: sorted_package_list = {}".format(self.pypi_sorted_package_list))
        self.logger.info("pypi_json: json.dumps(sorted_package_list) = {}".format(json.dumps(self.pypi_sorted_package_list)))

        return json.dumps(self.pypi_sorted_package_list)
####

        # check if pypi service is reachable
        if self.pypi_timeout <= 0:
            pypi_available = False
#            pypi_unavailable_message = translate('PyPI Prüfung deaktiviert')
            pypi_unavailable_message = 'PyPI Prüfung deaktiviert'
        else:
            pypi_available = True
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.pypi_timeout)
                #                sock.connect(('pypi.python.org', 443))
                sock.connect(('pypi.org', 443))
                sock.close()
            except:
                pypi_available = False
#                pypi_unavailable_message = translate('PyPI nicht erreichbar')
                pypi_unavailable_message = 'PyPI nicht erreichbar'

        import pip
        import xmlrpc
        import pkg_resources
        installed_packages = pkg_resources.working_set
        # installed_packages = pip.get_installed_distributions()
        # pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
        pypi = xmlrpc.client.ServerProxy('https://pypi.org/pypi')

        req_dict = self.get_requirements_info('base')
        req_test_dict = self.get_requirements_info('test')
        req_doc_dict = self.get_requirements_info('doc')
        self.logger.info("pypi_json: req_doc_dict {}".format(req_doc_dict))

        package_list = []

        for dist in installed_packages:
            package = dict()
            package['name'] = dist.key
            package['vers_installed'] = dist.version
            package['is_required'] = False
            package['is_required_for_testsuite'] = False
            package['is_required_for_docbuild'] = False

            package['vers_req_min'] = ''
            package['vers_req_max'] = ''
            package['vers_req_msg'] = ''
            package['vers_req_source'] = ''

            package['vers_ok'] = False
            package['vers_recent'] = False
            package['pypi_version'] = ''
            package['pypi_version_ok'] = True
            package['pypi_version_not_available_msg'] = ''
            package['pypi_doc_url'] = ''

            if pypi_available:
                try:
                    available = pypi.package_releases(dist.project_name)
                    self.logger.debug(
                        "pypi_json: pypi package: project_name {}, availabe = {}".format(dist.project_name,
                                                                                         available))
                    try:
                        package['pypi_version'] = available[0]
                    except:
                        package['pypi_version_not_available_msg'] = '?'
                except:
                    package['pypi_version'] = '--'
#                    package['pypi_version_not_available_msg'] = [translate('Keine Antwort von PyPI')]
                    package['pypi_version_not_available_msg'] = ['Keine Antwort von PyPI']
            else:
                package['pypi_version_not_available_msg'] = pypi_unavailable_message
            #            package['pypi_doc_url'] = 'https://pypi.python.org/pypi/' + dist.project_name
            package['pypi_doc_url'] = 'https://pypi.org/pypi/' + dist.project_name

            if package['name'].startswith('url'):
                self.logger.info(
                    "pypi_json: urllib: package['name'] = >{}<, req_dict.get(package['name'] = >{}<".format(
                        package['name'], req_dict.get(package['name'])))

            # test if package belongs to to SmartHomeNG requirements
            if req_dict.get(package['name'], '') != '':
                package['is_required'] = True
                # tests for min, max versions
                rmin, rmax, rtxt = self.check_requirement(package['name'], req_dict.get(package['name'], ''))
                package['vers_req_source'] = req_dict.get(package['name'], '')
                package['vers_req_min'] = rmin
                package['vers_req_max'] = rmax
                package['vers_req_msg'] = rtxt

            if req_doc_dict.get(package['name'], '') != '':
                package['is_required_for_docbuild'] = True
                # tests for min, max versions
                rmin, rmax, rtxt = self.check_requirement(package['name'], req_doc_dict.get(package['name'], ''))
                package['vers_req_source'] = req_doc_dict.get(package['name'], '')
                package['vers_req_min'] = rmin
                package['vers_req_max'] = rmax
                package['vers_req_msg'] = rtxt

            if req_test_dict.get(package['name'], '') != '':
                package['is_required_for_testsuite'] = True
                # tests for min, max versions
                rmin, rmax, rtxt = self.check_requirement(package['name'], req_test_dict.get(package['name'], ''))
                package['vers_req_source'] = req_test_dict.get(package['name'], '')
                package['vers_req_min'] = rmin
                package['vers_req_max'] = rmax
                package['vers_req_msg'] = rtxt

            if package['is_required']:
                package['sort'] = '1'
            elif package['is_required_for_testsuite']:
                package['sort'] = '2'
            elif package['is_required_for_docbuild']:
                package['sort'] = '3'
            else:
                package['sort'] = '4'
                self.logger.debug("pypi_json: sort=4, package['name'] = >{}<".format(package['name']))

            package['sort'] += package['name']

            # check if installed verison is recent (compared to PyPI)
            if package['is_required']:
                self.logger.info("compare PyPI package {}:".format(package['name']))
                if self.compare_versions(package['vers_installed'], package['pypi_version'], '>='):
                    package['vers_recent'] = True
            else:
                self.logger.info("compare PyPI package {} (for non required):".format(package['name']))
                if package['pypi_version'] != '':
                    if self.compare_versions(package['vers_installed'], package['pypi_version'], '>='):
                        package['vers_recent'] = True

                        # check if installed verison is ok
            if package['is_required'] or package['is_required_for_testsuite'] or package[
                'is_required_for_docbuild']:
                package['vers_ok'] = True
                if self.compare_versions(package['vers_req_min'], package['vers_installed'], '>'):
                    package['vers_ok'] = False
                max = package['vers_req_max']
                if max == '':
                    max = '99999'
                if self.compare_versions(max, package['vers_installed'], '<'):
                    package['vers_ok'] = False
                    package['vers_recent'] = False
                if self.compare_versions(max, package['vers_installed'], '=='):
                    package['vers_recent'] = True
                if package['pypi_version'] != '':
                    if self.compare_versions(package['pypi_version'], package['vers_installed'],
                                             '<') or self.compare_versions(package['pypi_version'], max, '>'):
                        package['pypi_version_ok'] = False

            package_list.append(package)

        # self.logger.warning('installed_packages: {}'.format(installed_packages))
        self.logger.debug('req_dict: {}'.format(req_dict))
        inst_pkgname_list = []
        for pkg in package_list:
            inst_pkgname_list.append(pkg['name'])
        self.logger.debug('pkgname_list: {}'.format(inst_pkgname_list))
        for req in req_dict:
            if not (req in inst_pkgname_list):
                pkg = {}
                pkg['name'] = req
                pkg['vers_installed'] = '-'
                pkg['is_required'] = True
                pkg['is_required_for_testsuite'] = False
                pkg['is_required_for_docbuild'] = False
                # tests for min, max versions
                rmin, rmax, rtxt = self.check_requirement(pkg['name'], req_dict.get(pkg['name'], ''))
                pkg['vers_req_min'] = rmin
                pkg['vers_req_max'] = rmax
                pkg['vers_req_msg'] = rtxt

                pkg['vers_ok'] = False
                pkg['vers_recent'] = False

                pkg['sort'] = '1' + pkg['name']
                package_list.append(pkg)
        ###
                if pypi_available:
                    try:
                        available = pypi.package_releases(pkg['name'])  # (dist.project_name)
                        self.logger.debug(
                            "pypi_json: pypi package: project_name {}, availabe = {}".format(pkg['name'], available))
                        try:
                            pkg['pypi_version'] = available[0]
                            pkg['pypi_version_not_available_msg'] = ""
                            pkg['pypi_version_ok'] = True
                            pkg['pypi_doc_url'] = 'https://pypi.org/pypi/' + pkg['name']

                        except:
                            pkg['pypi_version_not_available_msg'] = '?'
                            pkg['pypi_version_ok'] = False
                            pkg['pypi_doc_url'] = ''

                    except:
                        pkg['pypi_version'] = '--'
#                        pkg['pypi_version_not_available_msg'] = [translate('Keine Antwort von PyPI')]
                        pkg['pypi_version_not_available_msg'] = ['Keine Antwort von PyPI']
                else:
                    pkg['pypi_version_not_available_msg'] = pypi_unavailable_message
        ###

        self.logger.debug('package_list: {}'.format(package_list))


        # sorted_package_list = sorted([(i['name'], i['version_installed'], i['version_available']) for i in package_list])
        self.pypi_sorted_package_list = sorted(package_list, key=lambda k: k['sort'], reverse=False)
        self.logger.info("pypi_json: sorted_package_list = {}".format(self.pypi_sorted_package_list))
        self.logger.info("pypi_json: json.dumps(sorted_package_list) = {}".format(json.dumps(self.pypi_sorted_package_list)))

        return json.dumps(self.pypi_sorted_package_list)


    def get_requirements_info(self, req_group='base'):
        """
        """
        req_dict = {}
        if req_group == 'base':
            #            req_dict_base = parse_requirements("%s/requirements/base.txt" % self._sh.base_dir)
            req_dict_base = parse_requirements(os.path.join(self._sh.base_dir, 'requirements', 'base.txt'))
        elif req_group == 'test':
            req_dict_base = parse_requirements(os.path.join(self._sh.base_dir, 'tests', 'requirements.txt'))
            self.logger.info("get_requirements_info: filepath = {}".format(
                os.path.join(self._sh.base_dir, 'tests', 'requirements.txt')))
        elif req_group == 'doc':
            req_dict_base = parse_requirements(os.path.join(self._sh.base_dir, 'doc', 'requirements.txt'))
            self.logger.info("get_requirements_info: filepath = {}".format(
                os.path.join(self._sh.base_dir, 'doc', 'requirements.txt')))
        else:
            self.logger.error("get_requirements_info: Unknown requirements group '{}' requested".format(req_group))

        if req_group == 'base':
            # parse loaded plugins and look for requirements
            _conf = lib.config.parse(self._sh._plugin_conf)
            plugin_names = []
            for plugin in _conf:
                plugin_name = _conf[plugin].get('class_path', '').strip()
                if plugin_name == '':
                    plugin_name = 'plugins.' + _conf[plugin].get('plugin_name', '').strip()
                if not plugin_name in plugin_names:  # only unique plugin names, e.g. if multiinstance is used
                    plugin_names.append(plugin_name)
            self.logger.info(
                "get_requirements_info: len(_conf) = {}, len(plugin_names) = {}, plugin_names = {}".format(
                    len(_conf), len(plugin_names), plugin_names))

            req_dict = req_dict_base.copy()
            for plugin_name in plugin_names:
                file_path = "%s/%s/requirements.txt" % (self._sh.base_dir, plugin_name.replace("plugins.", "plugins/"))
                if os.path.isfile(file_path):
                    plugin_dict = parse_requirements(file_path)
                    for key in plugin_dict:
                        if key not in req_dict:
                            req_dict[key] = plugin_dict[key] + ' (' + plugin_name.replace('plugins.', '') + ')'
                        else:
                            req_dict[key] = req_dict[key] + '<br/>' + plugin_dict[key] + ' (' + plugin_name.replace(
                                'plugins.', '') + ')'

        if req_group in ['doc', 'test']:
            req_dict = req_dict_base.copy()

        self.logger.info("get_requirements_info: req_dict for group {} = {}".format(req_group, req_dict))
        return req_dict

    def compare_versions(self, vers1, vers2, operator):
        """
        Compare two version numbers and return if the condition is met
        """
        v1s = vers1.split('.')
        while len(v1s) < 4:
            v1s.append('0')
        v1 = []
        for v in v1s:
            vi = 0
            try:
                vi = int(v)
            except:
                pass
            v1.append(vi)

        v2s = vers2.split('.')
        while len(v2s) < 4:
            v2s.append('0')
        v2 = []
        for v in v2s:
            vi = 0
            try:
                vi = int(v)
            except:
                pass
            v2.append(vi)

        result = False
        if v1 == v2 and operator in ['>=', '==', '<=']:
            result = True
        if v1 < v2 and operator in ['<', '<=']:
            result = True
        if v1 > v2 and operator in ['>', '>=']:
            result = True

        self.logger.debug(
            "compare_versions: - - - v1 = {}, v2 = {}, operator = '{}', result = {}".format(v1, v2, operator,
                                                                                            result))
        return result

    def strip_operator(self, string, operator):
        """
        Strip a leading operator from a string and remove quotes, if they exist

        :param string: string to remove the operator from
        :param operator: operator to remove
        :type string: str
        :type operator: str

        :return: string without the operator
        :rtype: str
        """
        if string.startswith(operator):
            return Utils.strip_quotes(string[len(operator):].strip())
        else:
            return Utils.strip_quotes(string.strip())

    def split_operator(self, reqstring):
        """
        split operator and version from string

        :param reqstring: string containing operator and version
        :type reqstring: str

        :return: operator, version
        :rtype: str, str
        """
        if reqstring.startswith('=='):
            operator = '=='
            version = self.strip_operator(reqstring, operator)
        elif reqstring.startswith('<='):
            operator = '<='
            version = self.strip_operator(reqstring, operator)
        elif reqstring.startswith('>='):
            operator = '>='
            version = self.strip_operator(reqstring, operator)
        elif reqstring.startswith('<'):
            operator = '<'
            version = self.strip_operator(reqstring, operator)
        elif reqstring.startswith('>'):
            operator = '>='
            version = self.strip_operator(reqstring, operator)
        else:
            operator = ''
            version = reqstring

        return operator.strip(), version.strip()

    def req_is_pyversion_req_relevant(self, pyreq, package=''):
        """
        Test if requirement has a Python version restriction and if so, test if the restriction
        is relevant.
        """
        pyversion = "{0}.{1}".format(sys.version_info[0], sys.version_info[1])

        pyreq = pyreq.strip().replace('python_version', '')
        pyv_operator = ''
        if pyreq != '':
            self.logger.debug("req_is_pyversion_req_relevant: - - package {}, py_version {}".format(package, pyreq))
            if pyreq.startswith('=='):
                pyv_operator = '=='
                pyreq = self.strip_operator(pyreq, pyv_operator)
                result = self.compare_versions(pyversion, pyreq, pyv_operator)
            elif pyreq.startswith('<='):
                pyv_operator = '<='
                pyreq = self.strip_operator(pyreq, pyv_operator)
                result = self.compare_versions(pyversion, pyreq, pyv_operator)
            elif pyreq.startswith('>='):
                pyv_operator = '>='
                pyreq = self.strip_operator(pyreq, pyv_operator)
                result = self.compare_versions(pyversion, pyreq, pyv_operator)
            elif pyreq.startswith('<'):
                pyv_operator = '<'
                pyreq = self.strip_operator(pyreq, pyv_operator)
                result = self.compare_versions(pyversion, pyreq, pyv_operator)
            elif pyreq.startswith('>'):
                pyv_operator = '>'
                result = pyreq = self.strip_operator(pyreq, pyv_operator)
                self.compare_versions(pyversion, pyreq, pyv_operator)
            else:
                pyv_operator = ''
                self.logger.error(
                    "req_is_pyversion_req_relevant: no operator in front of Python version found - package {}, pyreq = {}".format(
                        package, pyreq))
                result = False

        self.logger.debug(
            "req_is_pyversion_req_relevant: - - - package {}, py_version_operator {}, py_version {}".format(package,
                                                                                                            pyv_operator,
                                                                                                            pyreq))
        return result

    # operator: <, <=, ==, >=, >>
    # source: <name of plugin> or 'core'
    # version_relation: <operator><version>
    # pyversion_relation: <operator><pyversion>
    # version_relations: <version_relation>,<version_relation>
    # py_vers_requirement: <version_relations>;<pyversion_relation>
    # py_vers_requirements: <py_vers_requirement> | <py_vers_requirement>
    # requirement_string: <py_vers_requirements> (<source>)

    def req_split_source(self, req, package=''):
        """
        Splits the requirement source from the requirement string
        """
        self.logger.debug("req_split_source: package {}, req = '{}'".format(package, req))
        req = req.lower().strip()

        # seperate requirement from source
        source = 'core'
        req1 = req
        if '(' in req:
            wrk = req.split('(')
            source = wrk[1][0:wrk[1].find(")")].strip()
            req1 = wrk[0].strip()
        self.logger.debug("req_split_source: - source {}, req1 = '{}'".format(source, req1))

        # seperate requirements for different Python versions
        req2 = req1.split('|')
        reql = []
        for r in req2:
            reql.append(r.strip())
        self.logger.debug("req_split_source: - source {}, reql = {}".format(source, reql))

        req_result = []
        for req in reql:
            # isolate and handle Python version
            wrk = req.split(';')
            sreq = wrk[0].strip()
            if len(wrk) > 1:
                valid = self.req_is_pyversion_req_relevant(wrk[1], package)
            else:
                valid = True

            #            self.logger.info("req_split_source: - - - source {}, py_version_operator {}, py_version {}, sreq = {}".format(source, pyv_operator, pyreq, sreq))

            if valid:
                # check and handle version requirements
                wrkl = sreq.split(',')
                if len(wrkl) > 2:
                    self.logger.error(
                        "req_split_source: More that two requirements for package {} req = {}".format(package,
                                                                                                      reql))
                rmin = ''
                rmax = ''
                for r in wrkl:
                    if r.find('<') != -1 or r.find('<=') != -1:
                        rmax = r
                    if r.find('>') != -1 or r.find('>=') != -1:
                        rmin = r
                    if r.find('==') != -1:
                        rmin = r
                        rmax = r
                req_result.append([source, rmin, rmax])

        self.logger.debug("req_split_source: - package {} req_result = {}".format(package, req_result))
        if len(req_result) > 1:
            self.logger.warning(
                "req_split_source: Cannot reconcile multiple version requirements for package {} for running Python version".format(
                    package))
        else:
            req_result = req_result[0]
        return req_result

    def check_requirement(self, package, req_str):
        """
        """
        pyversion = "{0}.{1}".format(sys.version_info[0], sys.version_info[1])
        req_min = ''
        req_max = ''
        # split requirements
        req_templist = req_str.split('<br/>')  # split up requirements from different plugins and the core

        req_result = []
        for req in req_templist:
            req_result.append(self.req_split_source(req, package))
        self.logger.debug(
            "check_requirement: package {}, len(req_result)={}, req_result = '{}'".format(package, len(req_result),
                                                                                          req_result))

        # Check if requirements from all sources are the same
        if len(req_result) > 1:
            are_equal = True
            for req in req_result:
                if req[1] != req_result[0][1]:
                    are_equal = False
                if req[2] != req_result[0][2]:
                    are_equal = False
            if are_equal:
                req_result = [req_result[0]]

        req_txt = req_result
        # Now we have a list of [ requirement_source, min_version (with operator), max_version (with operator) ]
        if len(req_result) == 1:
            result = req_result[0]
            self.logger.debug(
                "check_requirement: package {}, req_result = >{}<, result = >{}<".format(package, req_result,
                                                                                         result))
            # handle min
            op, req_min = self.split_operator(result[1])
            if req_min == '*':
                req_min = ''
                req_txt = ''
            else:
                if op == '>':
                    req_min += '.0'

            # handle max
            op, req_max = self.split_operator(result[2])
            if req_max == '*':
                req_max = ''
                req_txt = ''
        #            else:
        #            if op == '<':
        #                req_max = ?

        self.logger.debug(
            "check_requirement: package {} ({}), req_result = '{}'".format(package, len(req_result), req_result))
        if req_min != '' or req_max != '':
            req_txt = ''

        return req_min, req_max, req_txt

    def getpackages(self):
        """
        returns a list with the installed python packages and its versions
        """

        # check if pypi service is reachable
        if self.pypi_timeout <= 0:
            pypi_available = False
#            pypi_unavailable_message = translate('PyPI Prüfung deaktiviert')
            pypi_unavailable_message = 'PyPI Prüfung deaktiviert'
        else:
            pypi_available = True
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.pypi_timeout)
                #                sock.connect(('pypi.python.org', 443))
                sock.connect(('pypi.org', 443))
                sock.close()
            except:
                pypi_available = False
#                pypi_unavailable_message = translate('PyPI nicht erreichbar')
                pypi_unavailable_message = 'PyPI nicht erreichbar'

        import pip
        import xmlrpc
        installed_packages = pip.get_installed_distributions()
        #        pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
        pypi = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
        packages = []
        for dist in installed_packages:
            package = {}
            package['key'] = dist.key
            package['version_installed'] = dist.version
            if pypi_available:
                try:
                    available = pypi.package_releases(dist.project_name)
                    try:
                        package['version_available'] = available[0]
                    except:
                        package['version_available'] = '-'
                except:
#                    package['version_available'] = [translate('Keine Antwort von PyPI')]
                    package['version_available'] = ['Keine Antwort von PyPI']
            else:
                package['version_available'] = pypi_unavailable_message
            packages.append(package)

        sorted_packages = sorted([(i['key'], i['version_installed'], i['version_available']) for i in packages])
        return sorted_packages




def parse_requirements(file_path):
    req_dict = {}
    try:
        fobj = open(file_path)
    except:
        return req_dict

    for rline in fobj:
        line = ''
        if len(rline) > 0:
            if rline.find('#') == -1:
                line = rline.lower().strip()
            else:
                line = line[0:line.find("#")].lower().strip()

        if len(line) > 0:
            if ">" in line:
                if line[0:line.find(">")].lower().strip() in req_dict:
                    req_dict[line[0:line.find(">")].lower().strip()] += " | " + line[line.find(">"):len(
                        line)].lower().strip()
                else:
                    req_dict[line[0:line.find(">")].lower().strip()] = line[line.find(">"):len(line)].lower().strip()
            elif "<" in line:
                if line[0:line.find("<")].lower().strip() in req_dict:
                    req_dict[line[0:line.find("<")].lower().strip()] += " | " + line[line.find("<"):len(
                        line)].lower().strip()
                else:
                    req_dict[line[0:line.find("<")].lower().strip()] = line[line.find("<"):len(line)].lower().strip()
            elif "=" in line:
                if line[0:line.find("=")].lower().strip() in req_dict:
                    req_dict[line[0:line.find("=")].lower().strip()] += " | " + line[line.find("="):len(
                        line)].lower().strip()
                else:
                    req_dict[line[0:line.find("=")].lower().strip()] = line[line.find("="):len(line)].lower().strip()
            else:
                req_dict[line.lower().strip()] = '==*'

    fobj.close()
    return req_dict
