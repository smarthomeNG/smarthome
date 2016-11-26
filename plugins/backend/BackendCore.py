#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2016 Bernd Meiners,
#                 Christian Strassburg            c.strassburg@gmx.de
#                 René Frieß                      rene.friess@gmail.com
#                 Martin Sinn                     m.sinn@gmx.de
#				  Dirk Wallmeier				  dirk@wallmeier.info
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
import platform
import collections
import datetime
import pwd
import html
import subprocess
import socket
import sys
import threading
import lib.config
from lib.model.smartplugin import SmartPlugin
from .utils import *

class Backend:

    def find_visu_plugin(self):
        """
        look for the configured instance of the visu protocol plugin.
        """
        if self.visu_plugin is not None:
            return

        for p in self._sh._plugins:
            if p.__class__.__name__ == "WebSocket":
                self.visu_plugin = p
        if self.visu_plugin is not None:
            try:
                self.visu_plugin_version = self.visu_plugin.get_version()
            except:
                self.visu_plugin_version = '1.0.0'
            self.visu_plugin_build = self.visu_plugin_version[4:]
            if self.visu_plugin_build < '2':
                self.visu_plugin = None
                self.logger.warning("Backend: visu protocol plugin v{0} is too old to support BackendServer, please update".format(self.visu_plugin_version))


    @cherrypy.expose
    def index(self):
        self.find_visu_plugin()

        tmpl = self.env.get_template('main.html')
        return tmpl.render(visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def main_html(self):
        self.find_visu_plugin()

        tmpl = self.env.get_template('main.html')
        return tmpl.render(visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def reload_translation_html(self, lang=''):
        if lang != '':
            load_translation(lang)
        else:
            load_translation(get_translation_lang())
        return self.index()

    @cherrypy.expose
    def system_html(self):
        self.find_visu_plugin()
        now = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        system = platform.system()
        vers = platform.version()
        #node = platform.node()
        node = socket.getfqdn()
        arch = platform.machine()
        user = pwd.getpwuid(os.geteuid()).pw_name  # os.getlogin()
        python_packages = self.getpackages()

        req_dict = {}
        req_dict_base = parse_requirements("%s/requirements/base.txt" % self._sh_dir)

        # parse plugins and look for requirements
        _conf = lib.config.parse(self._sh._plugin_conf)

        plugin_names = []
        for plugin in _conf:
            plugin_name = _conf[plugin]['class_path'].strip()
            if not plugin_name in plugin_names: #only unique plugin names, e.g. if multiinstance is used
                plugin_names.append(plugin_name)

        req_dict = req_dict_base.copy()
        for plugin_name in plugin_names:
            file_path = "%s/requirements/%s.txt" % (self._sh_dir, plugin_name)
            if os.path.isfile(file_path):
                plugin_dict = parse_requirements(file_path)
                for key in plugin_dict:
                    if key not in req_dict:
                        req_dict[key] = plugin_dict[key] + ' ('+plugin_name.replace('plugins.','')+')'
                    else:
                        req_dict[key] = req_dict[key] + ', ' + plugin_dict[key] + ' ('+plugin_name.replace('plugins.','')+')'


        ip = self._bs.get_local_ip_address()

        space = os.statvfs(self._sh_dir)
        freespace = space.f_frsize * space.f_bavail/1024/1024

        get_uptime = subprocess.Popen('uptime', stdout=subprocess.PIPE)
        uptime = get_uptime.stdout.read().decode()
        # return SmarthomeNG runtime
        rt = str(self._sh.runtime())
        daytest = rt.split(' ')
        if len(daytest) == 3:
            days = int(daytest[0])
            hours, minutes, seconds = [float(val) for val in str(daytest[2]).split(':')]
        else:
            days = 0
            hours, minutes, seconds = [float(val) for val in str(daytest[0]).split(':')]
        sh_uptime = self.age_to_string(days, hours, minutes, seconds)
        
        pyversion = "{0}.{1}.{2} {3}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2], sys.version_info[3])

        tmpl = self.env.get_template('system.html')
        return tmpl.render(now=now, system=system, sh_vers=self._sh.env.core.version(), vers=vers, node=node, arch=arch, user=user,
                                freespace=freespace, uptime=uptime, sh_uptime=sh_uptime, pyversion=pyversion,
                                ip=ip, python_packages=python_packages, requirements=req_dict, visu_plugin=(self.visu_plugin is not None))

    def get_process_info(self, command):
        """
        returns output from executing a given command via the shell.
        """
        self.find_visu_plugin()
        ## get subprocess module
        import subprocess

        ## call date command ##
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        # Talk with date command i.e. read data from stdout and stderr. Store this info in tuple ##
        # Interact with process: Send data to stdin. Read data from stdout and stderr, until end-of-file is reached.
        # Wait for process to terminate. The optional input argument should be a string to be sent to the child process, or None, if no data should be sent to the child.
        (result, err) = p.communicate()

        ## Wait for date to terminate. Get return returncode ##
        p_status = p.wait()
        return str(result, encoding='utf-8', errors='strict')

    def getpackages(self):
        """
        returns a list with the installed python packages and its versions
        """
        self.find_visu_plugin()
        
        # check if pypi service is reachable
        if self.pypi_timeout <= 0:
            pypi_available = False
            pypi_unavailable_message = translate('PyPI Prüfung deaktiviert')
        else:
            pypi_available = True
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.pypi_timeout)
                sock.connect(('pypi.python.org',443))
                sock.close()
            except:
                pypi_available = False
                pypi_unavailable_message = translate('PyPI nicht erreichbar')
        
        import pip
        import xmlrpc
        installed_packages = pip.get_installed_distributions()
        pypi = xmlrpc.client.ServerProxy('https://pypi.python.org/pypi')
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
                    package['version_available'] = [translate('Keine Antwort von PyPI')]
            else:
                package['version_available'] = pypi_unavailable_message
            packages.append(package)

        sorted_packages = sorted([(i['key'], i['version_installed'], i['version_available']) for i in packages])
        return sorted_packages

    @cherrypy.expose
    def services_html(self):
        """
        shows a page with info about some services needed by smarthome
        """
        self.find_visu_plugin()
        knxd_service = self.get_process_info("systemctl status knxd.service")
        smarthome_service = self.get_process_info("systemctl status smarthome.service")
        knxd_socket = self.get_process_info("systemctl status knxd.socket")

        knxdeamon = ''
        if self.get_process_info("ps cax|grep eibd") != '':
            knxdeamon = 'eibd'
        if self.get_process_info("ps cax|grep knxd") != '':
            if knxdeamon != '':
                knxdeamon += ' and '
            knxdeamon += 'knxd'
        
        sql_plugin = False
        for x in self._sh._plugins:
            if x.__class__.__name__ == "SQL":
                sql_plugin = True
                break

        tmpl = self.env.get_template('services.html')
        return tmpl.render(knxd_service=knxd_service, smarthome_service=smarthome_service, knxd_socket=knxd_socket,
                           sql_plugin=sql_plugin, visu_plugin=(self.visu_plugin is not None), lang=get_translation_lang(),
                           develop=self.developer_mode, knxdeamon=knxdeamon)

    @cherrypy.expose
    def disclosure_html(self):
        """
        display disclosure
        """
        self.find_visu_plugin()

        tmpl = self.env.get_template('disclosure.html')
        return tmpl.render(smarthome=self._sh, visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def db_dump_html(self):
        """
        returns the smarthomeNG sqlite database as download
        """
        self._sh.sql.dump('%s/var/db/smarthomedb.dump' % self._sh_dir)
        mime = 'application/octet-stream'
        return cherrypy.lib.static.serve_file("%s/var/db/smarthomedb.dump" % self._sh_dir, mime, "%s/var/db/" % self._sh_dir)

    @cherrypy.expose
    def log_dump_html(self):
        """
        returns the smarthomeNG logfile as download
        """
        mime = 'application/octet-stream'
        return cherrypy.lib.static.serve_file("%s/var/log/smarthome.log" % self._sh_dir, mime,
                                              "%s/var/log/" % self._sh_dir)

    @cherrypy.expose
    def log_view_html(self, text_filter="", log_level_filter="ALL", page=1):
        """
        returns the smarthomeNG logfile as view
        """
        self.find_visu_plugin()

        fobj = open("%s/var/log/smarthome.log" % self._sh_dir)
        log_lines = []
        start = (int(page)-1) * 1000
        end = start + 1000
        counter = 0
        log_level_hit = False
        total_counter = 0
        for line in fobj:
            line_text = self.html_escape(line)
            if log_level_filter != "ALL" and not self.validate_date(line_text[0:10]) and log_level_hit:
                if start <= counter < end:
                    log_lines.append(line_text)
                counter += 1
            else:
                log_level_hit = False
            if (log_level_filter == "ALL" or line_text.find(log_level_filter) in [19, 20, 21, 22, 23]) and text_filter in line_text:
                if start <= counter < end:
                    log_lines.append(line_text)
                    log_level_hit = True
                counter += 1
        fobj.close()
        num_pages = -(-counter // 1000)
        if num_pages == 0:
            num_pages = 1
        tmpl = self.env.get_template('log_view.html')
        return tmpl.render(smarthome=self._sh, current_page=int(page), pages=num_pages, log_lines=log_lines, text_filter=text_filter,
                           log_level_filter=log_level_filter, visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def logics_view_html(self, file_path, logic, trigger=None, reload=None, enable=None, save=None, logics_code=None):
        """
        returns the smarthomeNG logfile as view
        """
        self.find_visu_plugin()

        self.process_logics_action(logic, trigger, reload, enable, save, logics_code)

        mylogic = self._sh.return_logic(logic)

        fobj = open(file_path)
        file_lines = []
        for line in fobj:
            file_lines.append(self.html_escape(line))
        fobj.close()
        tmpl = self.env.get_template('logics_view.html')
        return tmpl.render(smarthome=self._sh, logic=mylogic, logic_lines=file_lines, file_path=file_path,
                           updates=self.updates_allowed, visu_plugin=(self.visu_plugin is not None))
    @cherrypy.expose
    def items_html(self):
        """
        display a list of items
        """
        self.find_visu_plugin()
        
        tmpl = self.env.get_template('items.html')
        return tmpl.render(smarthome=self._sh, items=sorted(self._sh.return_items(), key=lambda k: str.lower(k['_path']), reverse=False), visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def items_json_html(self):
        """
        returns a list of items as json structure
        """
        items_sorted = sorted(self._sh.return_items(), key=lambda k: str.lower(k['_path']), reverse=False)
        parent_items_sorted = []
        for item in items_sorted:
            if "." not in item._path:
                parent_items_sorted.append(item)

        item_data = self._build_item_tree(parent_items_sorted)
        return json.dumps(item_data)

    @cherrypy.expose
    def cache_check_json_html(self):
        """
        returns a list of items as json structure
        """
        cache_path = "%s/var/cache/" % self._sh_dir
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(cache_path) if isfile(join(cache_path, f))]
        not_item_related_cache_files = []
        for file in onlyfiles:
            if not file.find(".") == 0:  #filter .gitignore etc.
                item = self._sh.return_item(file)
                if item is None:
                    file_data = {}
                    file_data['last_modified']= datetime.datetime.fromtimestamp(
                        int(os.path.getmtime(cache_path+file))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    file_data['created'] = datetime.datetime.fromtimestamp(
                        int(os.path.getctime(cache_path+file))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                    file_data['filename'] = file
                    not_item_related_cache_files.append(file_data)

        return json.dumps(not_item_related_cache_files)

    @cherrypy.expose
    def cache_file_delete_html(self, filename=''):
        """
        deletes a file from cache
        """
        if len(filename) > 0:
            file_path = "%s/var/cache/%s" % (self._sh_dir, filename)
            os.remove(file_path);

        return

    @cherrypy.expose
    def create_hash_json_html(self, plaintext):
        return json.dumps(create_hash(plaintext))

    @cherrypy.expose
    def item_change_value_html(self, item_path, value):
        """
        returns a list of items as json structure
        """
        item_data = []
        item = self._sh.return_item(item_path)
        if self.updates_allowed:
            item(value, caller='Backend')

        return

    def disp_str(self, val):
        s = str(val)
        if s == 'False':
            s = '-'
        elif s == 'None':
            s = '-'
        return s

    def age_to_string(self, days, hours, minutes, seconds):
        s = ''
        if days > 0:
            s += str(int(days)) + ' '
            if days == 1:
                s += translate('Tag')
            else:
                s += translate('Tage')
            s += ', '
        if (hours > 0) or (s != ''):
            s += str(int(hours)) + ' '
            if hours == 1:
                s += translate('Stunde')
            else:
                s += translate('Stunden')
            s += ', '
        if (minutes > 0) or (s != ''):
            s += str(int(minutes)) + ' '
            if minutes == 1:
                s += translate('Minute')
            else:
                s += translate('Minuten')
            s += ', '
        if days > 0:
            s += str(int(seconds))
        else:
            s += str("%.2f" % seconds)
        s += ' ' + translate('Sekunden')
        return s
            
    def disp_age(self, age):
        days = 0
        hours = 0
        minutes = 0
        seconds = age
        if seconds >= 60:
            minutes = int(seconds / 60)
            seconds = seconds - 60 * minutes
            if minutes > 59:
                hours = int(minutes / 60)
                minutes = minutes - 60 * hours
                if hours > 23:
                    days = int(hours / 24)
                    hours = hours - 24 * days
        return self.age_to_string(days, hours, minutes, seconds)

    @cherrypy.expose
    def item_detail_json_html(self, item_path):
        """
        returns a list of items as json structure
        """
        item_data = []
        item = self._sh.return_item(item_path)
        if item is not None:
            if item.type() is None or item.type() is '':
                prev_value = ''
                value = ''
            else:
                prev_value = item.prev_value()
                value = item._value

            if isinstance(prev_value, datetime.datetime):
                prev_value = str(prev_value)

            if 'str' in item.type():
                value = html.escape(value)
                prev_value = html.escape(prev_value)

            cycle = ''
            crontab = ''
            for entry in self._sh.scheduler._scheduler:
                if entry == item._path:
                    if self._sh.scheduler._scheduler[entry]['cycle']:
                        cycle = self._sh.scheduler._scheduler[entry]['cycle']
                    if self._sh.scheduler._scheduler[entry]['cron']:
                        crontab = html.escape(str(self._sh.scheduler._scheduler[entry]['cron']))
                    break

            changed_by = item.changed_by()
            if changed_by[-5:] == ':None':
                changed_by = changed_by[:-5]

            if item.prev_age() < 0:
                prev_age = ''
            else:
                prev_age = self.disp_age(item.prev_age())
            if str(item._cache) == 'False':
                cache = 'off'
            else:
                cache = 'on'
            if str(item._enforce_updates) == 'False':
                enforce_updates = 'off'
            else:
                enforce_updates = 'on'

            item_conf_sorted = collections.OrderedDict(sorted(item.conf.items(), key=lambda t: str.lower(t[0])))
            if item_conf_sorted.get('sv_widget', '') != '':
                item_conf_sorted['sv_widget'] = self.html_escape(item_conf_sorted['sv_widget'])

            logics = []
            for trigger in item.get_logic_triggers():
                logics.append(self.html_escape(format(trigger)))
            triggers = []
            for trigger in item.get_method_triggers():
                trig = format(trigger)
                trig = trig[1:len(trig) - 27]
                triggers.append(self.html_escape(format(trig.replace("<", ""))))

            data_dict = {'path': item._path,
                         'name': item._name,
                         'type': item.type(),
                         'value': value,
                         'age': self.disp_age(item.age()),
                         'last_update': str(item.last_update()),
                         'last_change': str(item.last_change()),
                         'changed_by': changed_by,
                         'previous_value': prev_value,
                         'previous_age': prev_age,
                         'previous_change': str(item.prev_change()),
                         'enforce_updates': enforce_updates,
                         'cache': cache,
                         'eval': html.escape(self.disp_str(item._eval)),
                         'eval_trigger': self.disp_str(item._eval_trigger),
                         'cycle': str(cycle),
                         'crontab': str(crontab),
                         'autotimer': self.disp_str(item._autotimer),
                         'threshold': self.disp_str(item._threshold),
                         'config': json.dumps(item_conf_sorted),
                         'logics': json.dumps(logics),
                         'triggers': json.dumps(triggers),
                         }

            if item.type() == 'foo':
                data_dict['value'] = str(item._value)

            item_data.append(data_dict)
            return json.dumps(item_data)
        else:
            self.logger.error("Requested item %s is None, check if item really exists." % item_path)
            return

    def _build_item_tree(self, parent_items_sorted):
        item_data = []

        for item in parent_items_sorted:
            nodes = self._build_item_tree(item.return_children())
            tags = []
            tags.append(len(nodes))
            item_data.append({'path': item._path, 'name': item._name, 'tags': tags, 'nodes': nodes})

        return item_data


    @cherrypy.expose
    def logics_html(self, logic=None, trigger=None, reload=None, enable=None, save=None):
        """
        display a list of all known logics
        """
        self.find_visu_plugin()
        self.process_logics_action(logic, trigger, reload, enable, save)

        tmpl = self.env.get_template('logics.html')
        return tmpl.render( smarthome = self._sh, updates = self.updates_allowed, visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def schedules_html(self):
        """
        display a list of all known schedules
        """
        self.find_visu_plugin()
        
        tmpl = self.env.get_template('schedules.html')
        return tmpl.render( smarthome = self._sh, visu_plugin=(self.visu_plugin is not None))

    @cherrypy.expose
    def plugins_html(self):
        """
        display a list of all known plugins
        """
        self.find_visu_plugin()
        
        conf_plugins = {}
        _conf = lib.config.parse(self._sh._plugin_conf)
        for plugin in _conf:
            #self.logger.warning("plugins_html: class_name='{0}', class_path='{1}'".format(_conf[plugin]['class_name'], _conf[plugin]['class_path']))
            conf_plugins[_conf[plugin]['class_name']] =  _conf[plugin]['class_path']
            #self.logger.warning("plugins_html: conf_plugins='{0}'".format(conf_plugins))
        
        plugins = []
        for x in self._sh._plugins:
            plugin = dict()
            plugin['classname'] = x.__class__.__name__
            plugin['classpath'] = conf_plugins[x.__class__.__name__]
            if isinstance(x, SmartPlugin):
                plugin['smartplugin'] = True
                plugin['instancename'] = x.get_instance_name()
                plugin['multiinstance'] = x.is_multi_instance_capable()
                plugin['version'] = x.get_version()
            else:
                plugin['smartplugin'] = False
            plugins.append(plugin)
        plugins_sorted = sorted(plugins, key=lambda k: k['classpath']) 

        tmpl = self.env.get_template('plugins.html')
        return tmpl.render( smarthome = self._sh, plugins=plugins_sorted, visu_plugin=(self.visu_plugin is not None))
        
        
       
        
    @cherrypy.expose
    def threads_html(self):
        """
        display a list of all threads
        """
        self.find_visu_plugin()
        
        threads = []
        for t in threading.enumerate():
            thread = dict()
            thread['sort'] = str(t.name).lower()
            thread['name'] = t.name
            thread['id'] = t.ident
            thread['alive'] = t.is_alive()
            threads.append(thread)
        threads_sorted = sorted(threads, key=lambda k: k['sort']) 
        threads_count = len(threads_sorted)
            
        tmpl = self.env.get_template('threads.html')
        return tmpl.render( smarthome = self._sh, threads=threads_sorted, threads_count=threads_count, visu_plugin=(self.visu_plugin is not None))


    @cherrypy.expose
    def logging_html(self):
        """
        display a list of all loggers
        """
        self.find_visu_plugin()
        
        loggerDict = logging.Logger.manager.loggerDict
        loggerDict_sorted = sorted(loggerDict)
        
        tmpl = self.env.get_template('logging.html')
        return tmpl.render( smarthome = self._sh, loggerDict_sorted=loggerDict_sorted, logging=logging, visu_plugin=(self.visu_plugin is not None))


    @cherrypy.expose
    def visu_html(self):
        """
        display a list of all connected visu clients
        """
        self.find_visu_plugin()
            
        clients = []
        if self.visu_plugin is not None:
            if self.visu_plugin_build == '2':
                for c in self.visu_plugin.return_clients():
                    client = dict()
                    deli = c.find(':')
                    client['ip'] = c[0:c.find(':')]
                    client['port'] = c[c.find(':')+1:]
                    try:
                        client['name'] = socket.gethostbyaddr(client['ip'])[0]
                    except:
                        client['name'] = client['ip']
                    clients.append(client)

            if self.visu_plugin_build > '2':
                # self.logger.warning("BackendServer: Language '{0}' not found, using standard language instead".format(language))
                # yield client.addr, client.sw, client.swversion, client.hostname, client.browser, client.browserversion
                # for c, sw, swv, ch in self.visu_plugin.return_clients():
                for clientinfo in self.visu_plugin.return_clients():
                    c = clientinfo.get('addr', '')
                    client = dict()
                    deli = c.find(':')
                    client['ip'] = c[0:c.find(':')]
                    client['port'] = c[c.find(':')+1:]
                    try:
                        client['name'] = socket.gethostbyaddr(client['ip'])[0]
                    except:
                        client['name'] = client['ip']
                    client['sw'] = clientinfo.get('sw', '')
                    client['swversion'] = clientinfo.get('swversion', '')
                    client['hostname'] = clientinfo.get('hostname', '')
                    client['browser'] = clientinfo.get('browser', '')
                    client['browserversion'] = clientinfo.get('browserversion', '')
                    clients.append(client)
                    
        clients_sorted = sorted(clients, key=lambda k: k['name']) 
        
        tmpl = self.env.get_template('visu.html')
        return tmpl.render( visu_plugin=(self.visu_plugin is not None), visu_plugin_build=self.visu_plugin_build, clients=clients_sorted )


    @cherrypy.expose
    def reboot(self):
        passwd = request.form['password']
        rbt1 = subprocess.Popen(["echo", passwd], stdout=subprocess.PIPE)
        rbt2 = subprocess.Popen(["sudo", "-S", "reboot"], stdin=rbt1.
                                stdout, stdout=subprocess.PIPE)
        print(rbt2.communicate()[0])
        return redirect('/services.html')

    def validate_date(self, date_text):
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def process_logics_action(self, logic=None, trigger=None, reload=None, enable=None, save=None, logics_code=None):
        self.logger.debug(
            "Backend: logics_html: trigger = '{0}', reload = '{1}', enable='{2}', save='{3}'".format(trigger, reload, enable, save))
        if enable is not None:
            self.logger.debug("Backend: logics[_view]_html: Enable/Disable logic = '{0}'".format(logic))
            if self.updates_allowed:
                if logic in self._sh.return_logics():
                    mylogic = self._sh.return_logic(logic)
                    if mylogic.enabled:
                        mylogic.disable()
                    else:
                        mylogic.enable()
                else:
                    self.logger.warning("Backend: Logic '{0}' not found".format(logic))
            else:
                self.logger.warning(
                    "Backend: Logic enabling/disabling is not allowed. (Change 'updates_allowed' in plugin.conf")

        if trigger is not None:
            self.logger.debug("Backend: logics[_view]_html: Trigger logic = '{0}'".format(logic))
            if self.updates_allowed:
                if logic in self._sh.return_logics():
                    self._sh.trigger(logic, by='Backend')
                else:
                    self.logger.warning("Backend: Logic '{0}' not found".format(logic))
            else:
                self.logger.warning(
                    "Backend: Logic triggering is not allowed. (Change 'updates_allowed' in plugin.conf")

        if save is not None:
            self.logger.debug("Backend: logics_view_html: Save logic = '{0}'".format(logic))

            if self.updates_allowed:
                if logic in self._sh.return_logics():
                    mylogic = self._sh.return_logic(logic)

            f = open(mylogic.filename, 'w')
            f.write(logics_code)
            f.close()
            reload = True

        if reload is not None:
            self.logger.debug("Backend: logics[_view]_html: Reload logic = '{0}'".format(logic))
            if self.updates_allowed:
                if logic in self._sh.return_logics():
                    mylogic = self._sh.return_logic(logic)
                    self.logger.info("Backend: logics_html: Reload logic='{0}', filename = '{1}'".format(logic,
                                                                                                         os.path.basename(
                                                                                                             mylogic.filename)))
                    mylogic.generate_bytecode()
                    self._sh.trigger(logic, by='Backend', value="Init")
                else:
                    self.logger.warning("Backend: Logic '{0}' not found".format(logic))
            else:
                self.logger.warning("Backend: Logic reloads are not allowed. (Change 'updates_allowed' in plugin.conf")

        return