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
import time
import copy

import lib.shyaml as shyaml
import lib.config
from lib.module import Modules
from lib.utils import Utils
from lib.logic import Logics
from lib.plugin import Plugins
from lib.scheduler import Scheduler
from lib.constants import (DIR_ETC, DIR_LOGICS, DIR_TPL, BASE_LOGIC)

from .rest import RESTResource


class LogicsController(RESTResource):
    logics = None
    _logicname_prefix = 'logics.'  # prefix for scheduler names

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)

        self.logics_dir = self._sh.get_config_dir(DIR_LOGICS)
        self.template_dir = self._sh.get_config_dir(DIR_TPL)
        self.logics = Logics.get_instance()
        self.logger.info("__init__ self.logics = {}".format(self.logics))
        self.plugins = Plugins.get_instance()
        self.logger.info("__init__ self.plugins = {}".format(str(self.plugins)))
        self.scheduler = Scheduler.get_instance()
        self.logger.info("__init__ self.scheduler = {}".format(self.scheduler))

        self.blockly_plugin_loaded = None
        self.logics_data = {}

        self.logics = Logics.get_instance()


    def get_body(self, text=False):
        """
        Get content body of received request header

        :return:
        """
        cl = cherrypy.request.headers.get('Content-Length', 0)
        if cl == 0:
            # cherrypy.reponse.headers["Status"] = "400"
            # return 'Bad request'
            raise cherrypy.HTTPError(status=411)
        rawbody = cherrypy.request.body.read(int(cl))
        self.logger.debug("ServicesController(): get_body(): rawbody = {}".format(rawbody))
        try:
            if text:
                params = rawbody.decode('utf-8')
            else:
                params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning("ServicesController(): get_body(): Exception {}".format(e))
            return None
        return params


    def logics_initialize(self):
        """
        Initialize access to logics API and test if Blockly plugin is loaded

        This can't be done during __init__, since not all components are loaded/initialized
        at that time.
        """
        if self.logics is not None:
            return

        self.logics = Logics.get_instance()
        if self.logics is None:
            # SmartHomeNG has not yet initialized the logics module (still starting up)
            return

        if self.plugins == None:
            self.plugins = Plugins.get_instance()
        self.yaml_updates = (self.logics.return_config_type() == '.yaml')

        # find out if blockly plugin is loaded
        if self.blockly_plugin_loaded == None:
            self.blockly_plugin_loaded = False
            for x in self.plugins.return_plugins():
                try:
                    if x.get_shortname() == 'blockly':
                        self.blockly_plugin_loaded = True
                except:
                    pass

    def fill_logicdict(self, logicname):
        """
        Returns a dict filled with information of the specified loaded logic
        """
        mylogic = dict()
        loaded_logic = self.logics.return_logic(logicname)
        if loaded_logic is not None:
            mylogic['group'] = loaded_logic.groupnames

            mylogic['name'] = loaded_logic.name
            mylogic['description'] = loaded_logic.description
            try:
                mylogic['enabled'] = loaded_logic._enabled
            except Exception as e:
                self.logger.warning(f"Logic {loaded_logic.name}: Exception {e}")
                mylogic['enabled'] = loaded_logic.enabled
            mylogic['logictype'] = self.logics.return_logictype(loaded_logic.name)
            mylogic['userlogic'] = self.logics.is_userlogic(loaded_logic.name)
            mylogic['filename'] = loaded_logic.filename
            mylogic['pathname'] = loaded_logic._pathname
            mylogic['cycle'] = ''
            if hasattr(self.logics.return_logic(logicname), 'cycle'):
                mylogic['cycle'] = loaded_logic.cycle
                if mylogic['cycle'] == None:
                    mylogic['cycle'] = ''

            mylogic['crontab'] = ''
            if hasattr(loaded_logic, 'crontab'):
                if loaded_logic.crontab is not None:
                    mylogic['crontab'] = Utils.strip_quotes_fromlist(self.list_to_editstring(loaded_logic.crontab))

                mylogic['crontab'] = Utils.strip_square_brackets(mylogic['crontab'])

            mylogic['watch_item'] = ''
            mylogic['watch_item_list'] = []
            if hasattr(loaded_logic, 'watch_item'):
                # Attention: watch_items are always stored as a list in logic object
                mylogic['watch_item'] = Utils.strip_quotes_fromlist(str(loaded_logic.watch_item))
                mylogic['watch_item_list'] = list(loaded_logic.watch_item)

            mylogic['next_exec'] = ''

            if self.scheduler.return_next(self._logicname_prefix + loaded_logic.name):
                mylogic['next_exec'] = self.scheduler.return_next(
                    self._logicname_prefix + loaded_logic.name).strftime('%Y-%m-%d %H:%M:%S%z')

            mylogic['last_run'] = ''
            if loaded_logic.last_run():
                mylogic['last_run'] = loaded_logic.last_run().strftime('%Y-%m-%d %H:%M:%S%z')

            mylogic['visu_acl'] = ''
            if hasattr(loaded_logic, 'visu_acl'):
                if loaded_logic.visu_acl != 'None':
                    mylogic['visu_acl'] = Utils.strip_quotes_fromlist(str(loaded_logic.visu_acl))

        return mylogic

    def list_to_editstring(self, l):
        """
        """
        if type(l) is str:
            self.logger.debug("list_to_editstring: >{}<  -->  >{}<".format(l, l))
            return l

        edit_string = ''
        for entry in l:
            if edit_string != '':
                edit_string += ' | '
            edit_string += str(entry)
        self.logger.debug("list_to_editstring: >{}<  -->  >{}<".format(l, edit_string))
        return edit_string

    def logic_findnew(self, loadedlogics):
        """
        Find new logics (logics defined in /etc/logic.yaml but not loaded)
        """
        _config = {}
        _config.update(
            self.logics._read_logics(self.logics._get_logic_conf_basename(), self.logics.get_logics_dir()))

        self.logger.info("logic_findnew: _config = '{}'".format(_config))
        newlogics = []
        for configlogic in _config:
            if configlogic != '_groups':
                found = False
                for l in loadedlogics:
                    if configlogic == str(l['name']):
                        found = True
                if not found:
                    self.logger.info("LogicsController (logic_findnew): name = {}".format(configlogic))
                    if _config[configlogic] != 'None':
                        mylogic = {}
                        mylogic['name'] = configlogic
                        mylogic['userlogic'] = True
                        mylogic['logictype'] = self.logics.return_logictype(mylogic['name'])
                        if mylogic['logictype'] == 'Python':
                            mylogic['filename'] = _config[configlogic]['filename']
                            mylogic['pathname'] = self.logics.get_logics_dir() + mylogic['filename']
                        elif mylogic['logictype'] == 'Blockly':
                            mylogic['filename'] = _config[configlogic]['filename']
                            mylogic['pathname'] = \
                            os.path.splitext(self.logics.get_logics_dir() + _config[configlogic]['filename'])[
                                0] + '.blockly'
                        else:
                            mylogic['filename'] = ''

                        newlogics.append(mylogic)

        return newlogics


    def get_logics_info(self):
        """
        Get list of logics with info for logic-list
        """

        logics_list = []

        for ln in self.logics.return_loaded_logics():
            logic = self.fill_logicdict(ln)
            if logic['logictype'] == 'Blockly':
                logic['pathname'] = os.path.splitext(logic['pathname'])[0] + '.blockly'
            logics_list.append(logic)
            self.logger.debug(
                "- logic = {}, enabled = {}, , logictype = {}, filename = {}, userlogic = {}, watch_item = {}".format(
                    str(logic['name']), str(logic['enabled']), str(logic['logictype']), str(logic['filename']),
                    str(logic['userlogic']), str(logic['watch_item'])))

        logics_new = sorted(self.logic_findnew(logics_list), key=lambda k: k['name'])
        logics_sorted = sorted(logics_list, key=lambda k: k['name'])
        self.logics_data = {'logics_new': logics_new, 'logics': logics_sorted, 'groups': self.logics._groups}
        return json.dumps(self.logics_data)


    def get_groups_info(self):
        """
        Get information of defined groups
        """
        self.groups_data = {'groups': self.logics._groups}
        return json.dumps(self.groups_data)


    def save_group(self, name, params):

        self.logics._groups[name] = params
        self.logics._save_groups()
        response = {'result': 'ok'}

        return json.dumps(response)


    def delete_group(self, name, params):

        del self.logics._groups[name]
        self.logics._save_groups()
        response = {'result': 'ok'}

        return json.dumps(response)


    def get_logic_info(self, logicname):
        """
        Get code of a logic from file
        """
        wrk = shyaml.yaml_load(self._sh.get_config_file(BASE_LOGIC))
        logic_conf = wrk.get(logicname, {})

        if Utils.get_type(logic_conf.get('watch_item', None)) == 'str':
            self.logger.info("get_logic: logicname = '{}', converting watch_item = '{}' to list".format(logicname, logic_conf['watch_item']))
            logic_conf['watch_item'] = [logic_conf['watch_item']]

        self.logger.info("get_logic: logicname = '{}', logic_conf = '{}'".format(logicname, logic_conf))

        mylogic = self.fill_logicdict(logicname)
        if mylogic.get('name', None) is not None:
            logic_conf['name'] = mylogic['name']
            logic_conf['group'] = mylogic['group']
            logic_conf['next_exec'] = mylogic['next_exec']
            logic_conf['last_run'] = mylogic['last_run']

            # self.logger.warning("type = {}, mylogic = {}".format(type(mylogic), mylogic))
        # self.logger.warning("type = {}, logic_conf = {}".format(type(logic_conf), logic_conf))

        return json.dumps(logic_conf)


    # ======================================================================
    #  /api/logics/<logicname>?action=<action>
    #
    def logic_create_codefile(self, filename, logics_code, overwrite=False):

        pathname = self.logics.get_logics_dir() + filename
        if not overwrite:
            if os.path.isfile(pathname):
                return False

        f = open(pathname, 'w', encoding='UTF-8')
        f.write(logics_code)
        f.close()
        return True


    def logic_create_config(self, logicname, filename):
        """
        Create a new configuration for a logic
        """
        config_list = []
        config_list.append(['filename', filename, ''])
        config_list.append(['enabled', False, ''])
        self.logics.update_config_section(True, logicname, config_list)
        #        self.logics.set_config_section_key(logicname, 'visu_acl', False)


    def get_logic_state(self, logicname):
        """

        :param logicname:
        :param action:
        :return:

        valid actions are: 'loaded'
        """
        self.logger.info(f"LogicsController.get_logic_state(): logicname = {logicname}")
        logic_status = {}
        logic_status['is_loaded'] = self.logics.is_logic_loaded(logicname)
        return json.dumps(logic_status)


    def get_logic_template(self, logicname):
        filename = os.path.join(self.template_dir, 'logic.tpl')
        read_data = None
        try:
            with open(filename, encoding='UTF-8') as f:
                read_data = f.read().replace('example_logic.py', logicname)
        except Exception:
            read_data = '#!/usr/bin/env python3\n' + '# ' + logicname + '\n\n'
        return read_data


    def set_logic_state(self, logicname, action, filename):
        """

        :param logicname:
        :param action:
        :return:

        valid actions are: 'enable', 'disable', 'trigger', 'unload', 'load', 'reload', 'delete', 'create'
        """
        self.logger.info(f"LogicsController.set_logic_state(): logicname = {logicname}, action = {action}")
        if action == 'enable':
            self.logics.enable_logic(logicname)
            return json.dumps( {"result": "ok"} )
        elif action == 'disable':
            self.logics.disable_logic(logicname)
            return json.dumps( {"result": "ok"} )
        elif action == 'trigger':
            self.logics.trigger_logic(logicname, by='Admin')
            return json.dumps( {"result": "ok"} )
        elif action == 'unload':
            self.logics.unload_logic(logicname)
            return json.dumps({"result": "ok"})
        elif action == 'load':
            self.logics.load_logic(logicname)
            if self.logics.is_logic_loaded(logicname):
                return json.dumps({"result": "ok"})
            else:
                return json.dumps({"result": "error", "description": "Logic could not be loaded - for details look at the log"})
        elif action == 'reload':
            self.logics.load_logic(logicname)            # implies unload_logic()
            if self.logics.is_logic_loaded(logicname):
                crontab = self.logics.get_logiccrontab(logicname)
                if (crontab is not None) and ('init' in crontab):
                    self.logger.info("LogicsController.set_logic_state(relaod): Triggering logic because crontab contains 'init' - crontab = '{}'".format(crontab))
                    self.logics.trigger_logic(logicname, by='Admin')
                return json.dumps({"result": "ok"})
            else:
                return json.dumps({"result": "error", "description": "Logic could not be loaded - for details look at the log"})
        elif action == 'delete_with_code':
            self.logger.info(f"set_logic_state: action={action}")
            self.logics.delete_logic(logicname, with_code=True)
            return json.dumps({"result": "ok"})
        elif action == 'delete':
            self.logger.info(f"set_logic_state: action={action}")
            self.logics.delete_logic(logicname)
            return json.dumps({"result": "ok"})
        elif action == 'create':
            self.logger.info(f"set_logic_state: action={action} filename={filename}, logicname={logicname}")
            filename = filename.lower() + '.py'

            if logicname in self.logics.return_defined_logics():
                self.logger.warning("LogicsController.set_logic_state(create): Logic name {} is already used".format(logicname))
                return json.dumps({"result": "error", "description": "Logic name {} is already used".format(logicname)})
            else:
                if not os.path.isfile(os.path.join(self._sh.get_config_dir(DIR_LOGICS), filename)):
                    #create new logic code file, if none is found
                    logics_code = self.get_logic_template(filename)
                    if not self.logic_create_codefile(filename, logics_code):
                        self.logger.error(f"Could not create code-file '{filename}'")
                        return json.dumps({"result": "error", "description": f"Could not create code-file '{filename}'"})

                if self.logics.filename_used_count(filename) > 0:
                    self.logger.error(f"code-file '{filename}' already exists and is used by another logic configuration")
                    return json.dumps({"result": "error", "description": f"code-file '{filename}' already exists and is used by another logic configuration"})

                self.logic_create_config(logicname, filename)
                if not self.logics.load_logic(logicname):
                    self.logger.warning(f"Could not load logic '{logicname}', syntax error")
                return json.dumps( {"result": "ok"} )

        else:
            self.logger.warning("LogicsController.set_logic_state(): logic '"+logicname+"', action '"+action+"' is not supported")
            return json.dumps({"result": "error", "description": "action '"+action+"' is not supported"})

        return


    def save_logic_parameters(self, logicname, params):
        #params = self.get_body()
        self.logger.info(f"LogicsController.save_logic_parameters: logic = {logicname}, params = {params}")

        logic_conf = shyaml.yaml_load_roundtrip(self._sh.get_config_file(BASE_LOGIC))
        sect = logic_conf.get(logicname)
        if sect is None:
            response = {'result': 'error', 'description': "Configuration section '{}' does not exist".format(logicname)}
        else:
            self.logger.info(f"LogicsController.save_logic_parameters: logic = {logicname}, alte params = {dict(sect)}")
            for param, value in params.items():
                if param == 'group':
                    param = 'logic_groupname'
                    # change group(s) for the running logic too
                    self._sh.logics.return_logic(logicname).groupnames = value
                    # if only one group is specified, make it a string
                    if isinstance(value, list) and len(value) == 1:
                        value = value[0]
                if param == 'logic_description':
                    # change descriptipn for the running logic too
                    self._sh.logics.return_logic(logicname).description = value
                if value == None:
                    sect.pop(param, None)
                else:
                    self.logger.info(f"- param = {param}, value = {value}, type(value) = {Utils.get_type(value)}")
                    if (Utils.get_type(value) == 'str') and (value == ''):
                        sect.pop(param, None)
                    elif (Utils.get_type(value) == 'list') and (value == []):
                        sect.pop(param, None)
                    elif (Utils.get_type(value) == 'dict') and (value == {}):
                        sect.pop(param, None)
                    else:
                        sect[param] = value

            self.logger.info("LogicsController.save_logic_parameters: logic = {}, neue params = {}".format(logicname, dict(sect)))


            shyaml.yaml_save_roundtrip(self._sh.get_config_file(BASE_LOGIC), logic_conf, False)
            response = {'result': 'ok'}

        return json.dumps(response)


    def read(self, logicname=None, infotype=None):
        """
        return an object with type info about all logics or of a specific logic (if logicname is given)
        """
        # create a list of dicts, where each dict contains the information for one logic
        self.logger.info("LogicsController.read()")

        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        if self.scheduler is None:
            self.scheduler = Scheduler.get_instance()

        self.logics_initialize()
        if self.logics is None:
            # SmartHomeNG has not yet initialized the logics module (still starting up)
            raise cherrypy.NotFound

        if logicname is None and infotype is None:
            return self.get_logics_info()
        elif logicname is not None and infotype is None:
            return self.get_logic_info(logicname)
        elif logicname is None and infotype == 'groups':
            return self.get_groups_info()
        elif infotype == 'status':
            return self.get_logic_state(logicname)


    read.expose_resource = True
    read.authentication_needed = True


    def update(self, name='', action='', filename=''):
        """
        Handle PUT requests for logics API
        """
        params = self.get_body()
        self.logger.info(f"LogicsController.update(logic-/groupname='{name}', action='{action}'), , params={params} ")

        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        if self.scheduler is None:
            self.scheduler = Scheduler.get_instance()

        self.logics_initialize()
        if self.logics is None:
            return json.dumps({'result': 'Error', 'description': "SmartHomeNG is still initializing"})

        if name != '':
            if action == 'saveparameters':
                return self.save_logic_parameters(name, params)
            elif action == 'savegroup':
                self.logger.info(f"LogicsController.update: group={name}, action={action}, params={params}")
                return self.save_group(name, params)
                #return json.dumps({'result': 'Error', 'description': f"Saving of groups is not yet implemented. Group '{name}' was not saved"})
            elif action == 'deletegroup':
                self.logger.info(f"LogicsController.update: group={name}, action={action}, params={params}")
                return self.delete_group(name, params)
            else:
                self.logger.info(f"LogicsController.update: group={name}, action={action}, filename={filename}")
                return self.set_logic_state(name, action, filename)

        elif not action in ['create', 'load', 'delete', 'delete_with_code']:
            mylogic = self.logics.return_logic(name)
            if mylogic is None:
                self.logger.info(f"Error: No loaded logic with name '{name}' found")
                return json.dumps({'result': 'Error', 'description': f"No loaded logic with name '{name}' found"})

        return None

    update.expose_resource = True
    update.authentication_needed = True
