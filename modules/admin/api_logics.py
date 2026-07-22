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
from lib.constants import DIR_ETC, DIR_LOGICS, DIR_TPL, BASE_LOGIC, BASE_LOGIC_GROUPS

from .rest import ApiDoc, ApiParam, RESTResource


class LogicsController(RESTResource):
    logics = None
    _logicname_prefix = 'logics.'  # prefix for scheduler names

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )

        self.etc_dir = self._sh.get_config_dir(DIR_ETC)

        self.logics_dir = self._sh.get_config_dir(DIR_LOGICS)
        self.template_dir = self._sh.get_config_dir(DIR_TPL)
        self.logics = Logics.get_instance()
        self.logger.info('__init__ self.logics = {}'.format(self.logics))
        self.plugins = Plugins.get_instance()
        self.logger.info('__init__ self.plugins = {}'.format(str(self.plugins)))
        self.scheduler = Scheduler.get_instance()
        self.logger.info('__init__ self.scheduler = {}'.format(self.scheduler))

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
        self.logger.debug('ServicesController(): get_body(): rawbody = {}'.format(rawbody))
        try:
            if text:
                params = rawbody.decode('utf-8')
            else:
                params = json.loads(rawbody.decode('utf-8'))
        except Exception as e:
            self.logger.warning('ServicesController(): get_body(): Exception {}'.format(e))
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

        if self.plugins is None:
            self.plugins = Plugins.get_instance()
        self.yaml_updates = self.logics.return_config_type() == '.yaml'

        # find out if blockly plugin is loaded
        if self.blockly_plugin_loaded is None:
            self.blockly_plugin_loaded = False
            for x in self.plugins.return_plugins():
                try:
                    if x.get_shortname() == 'blockly':
                        self.blockly_plugin_loaded = True
                except Exception:
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
                self.logger.warning(f'Logic {loaded_logic.name}: Exception {e}')
                mylogic['enabled'] = loaded_logic.enabled
            mylogic['logictype'] = self.logics.return_logictype(loaded_logic.name)
            mylogic['userlogic'] = self.logics.is_userlogic(loaded_logic.name)
            mylogic['filename'] = loaded_logic.filename
            mylogic['pathname'] = loaded_logic._pathname
            mylogic['cycle'] = ''
            if hasattr(self.logics.return_logic(logicname), 'cycle'):
                mylogic['cycle'] = loaded_logic.cycle
                if mylogic['cycle'] is None:
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
                mylogic['next_exec'] = self.scheduler.return_next(self._logicname_prefix + loaded_logic.name).strftime(
                    '%Y-%m-%d %H:%M:%S%z'
                )

            mylogic['last_run'] = ''
            if loaded_logic.last_run():
                mylogic['last_run'] = loaded_logic.last_run().strftime('%Y-%m-%d %H:%M:%S%z')

            mylogic['visu_acl'] = ''
            if hasattr(loaded_logic, 'visu_acl'):
                if loaded_logic.visu_acl != 'None':
                    mylogic['visu_acl'] = Utils.strip_quotes_fromlist(str(loaded_logic.visu_acl))

        return mylogic

    def list_to_editstring(self, lst):
        """ """
        if type(lst) is str:
            self.logger.debug('list_to_editstring: >{}<  -->  >{}<'.format(lst, lst))
            return lst

        edit_string = ''
        for entry in lst:
            if edit_string != '':
                edit_string += ' | '
            edit_string += str(entry)
        self.logger.debug('list_to_editstring: >{}<  -->  >{}<'.format(lst, edit_string))
        return edit_string

    def logic_findnew(self, loadedlogics):
        """
        Find new logics (logics defined in /etc/logic.yaml but not loaded)
        """
        _config = {}
        _config.update(self.logics._read_logics(self.logics._get_logic_conf_basename(), self.logics.get_logics_dir()))

        self.logger.info("logic_findnew: _config = '{}'".format(_config))
        newlogics = []
        for configlogic in _config:
            if configlogic != '_groups':
                found = False
                for logic in loadedlogics:
                    if configlogic == str(logic['name']):
                        found = True
                if not found:
                    self.logger.info('LogicsController (logic_findnew): name = {}'.format(configlogic))
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
                            mylogic['pathname'] = (
                                os.path.splitext(self.logics.get_logics_dir() + _config[configlogic]['filename'])[0]
                                + '.blockly'
                            )
                        else:
                            mylogic['filename'] = ''

                        newlogics.append(mylogic)

        return newlogics

    def get_logics_info(self):
        """
        Get list of logics with info for logic-list
        """

        # Read group membership from the authoritative file so we never serve
        # stale in-memory data from Logic.groupnames (which is only updated
        # when a logic is loaded or when _update_group_members runs in the
        # same process lifetime).
        logic_conf_raw = shyaml.yaml_load(self._sh.get_config_file(BASE_LOGIC)) or {}

        def _groups_from_conf(logicname):
            sect = logic_conf_raw.get(logicname, {})
            if not isinstance(sect, dict):
                return []
            raw = sect.get('logic_groupname', None)
            if raw is None:
                return []
            return raw if isinstance(raw, list) else [raw]

        logics_list = []

        for ln in self.logics.return_loaded_logics():
            logic = self.fill_logicdict(ln)
            # Override group with the on-disk value (always authoritative)
            logic['group'] = _groups_from_conf(ln)
            if logic['logictype'] == 'Blockly':
                logic['pathname'] = os.path.splitext(logic['pathname'])[0] + '.blockly'
            logics_list.append(logic)
            self.logger.debug(
                '- logic = {}, enabled = {}, , logictype = {}, filename = {}, userlogic = {}, watch_item = {}'.format(
                    str(logic['name']),
                    str(logic['enabled']),
                    str(logic['logictype']),
                    str(logic['filename']),
                    str(logic['userlogic']),
                    str(logic['watch_item']),
                )
            )

        logics_new = sorted(self.logic_findnew(logics_list), key=lambda k: k['name'])
        logics_sorted = sorted(logics_list, key=lambda k: k['name'])

        # Collect group names referenced by logics but not defined in logic_groups.yaml
        known_groups = set(self.logics._groups.keys())
        unknown_groups = {}  # {groupname: [logicname, ...]}
        for logic in logics_sorted + logics_new:
            raw = logic.get('group', None)
            if not raw:
                continue
            refs = raw if isinstance(raw, list) else [raw]
            for ref in refs:
                if ref and ref not in known_groups:
                    unknown_groups.setdefault(ref, [])
                    if logic['name'] not in unknown_groups[ref]:
                        unknown_groups[ref].append(logic['name'])
        if unknown_groups:
            for gname, lnames in unknown_groups.items():
                self.logger.warning(
                    f"Logic group '{gname}' is referenced by {lnames} but not defined in logic_groups.yaml"
                )

        self.logics_data = {
            'logics_new': logics_new,
            'logics': logics_sorted,
            'groups': self.logics._groups,
            'unknown_groups': unknown_groups,
        }
        return json.dumps(self.logics_data)

    def get_groups_info(self):
        """
        Get information of defined groups
        """
        self.groups_data = {'groups': self.logics._groups}
        return json.dumps(self.groups_data)

    def save_group(self, name, params):
        # Separate member list from group metadata before persisting
        members = params.pop('members', None)

        self.logics._groups[name] = params
        self.logics._save_groups()

        if members is not None:
            self._update_group_members(name, members)

        response = {'result': 'ok'}
        return json.dumps(response)

    def _update_group_members(self, groupname, new_members):
        """
        Batch-update logic_groupname in logic.yaml so that exactly the logics
        listed in new_members belong to groupname.  Other group memberships of
        each logic are left untouched.

        The legacy ``_groups`` key (old format where group definitions were
        stored inside logic.yaml) is stripped on every write so it cannot
        accumulate stale data or confuse iteration.
        """
        logic_conf = shyaml.yaml_load_roundtrip(self._sh.get_config_file(BASE_LOGIC))
        changed = False

        # Strip legacy _groups section — group definitions belong in logic_groups.yaml only
        if '_groups' in logic_conf:
            del logic_conf['_groups']
            changed = True

        for logicname, sect in logic_conf.items():
            if not isinstance(sect, dict):
                continue

            raw = sect.get('logic_groupname', None)
            if raw is None:
                current = []
            elif isinstance(raw, str):
                current = [raw]
            else:
                current = list(raw)

            in_new = logicname in new_members
            in_cur = groupname in current

            if in_new == in_cur:
                continue  # nothing to do for this logic

            if in_new:
                current.append(groupname)
            else:
                current.remove(groupname)

            # Write back: empty → remove key; single → scalar; multiple → list
            if not current:
                sect.pop('logic_groupname', None)
            elif len(current) == 1:
                sect['logic_groupname'] = current[0]
            else:
                sect['logic_groupname'] = current

            # Keep the running logic object in sync (lib/logic.py is authoritative)
            running = self._sh.logics.return_logic(logicname)
            if running is not None:
                running.groupnames = current  # [] is accepted; None was wrongly passed before

            changed = True

        if changed:
            shyaml.yaml_save_roundtrip(self._sh.get_config_file(BASE_LOGIC), logic_conf, False)

    def delete_group(self, name, params):
        # Remove all logic_groupname references to this group from logic.yaml
        # and from the in-memory Logic objects before deleting the group record.
        self._update_group_members(name, [])

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
            self.logger.info(
                "get_logic: logicname = '{}', converting watch_item = '{}' to list".format(
                    logicname, logic_conf['watch_item']
                )
            )
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
        self.logger.info(f'LogicsController.get_logic_state(): logicname = {logicname}')
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

    def set_logic_state(self, logicname, action, filename, newfilename=''):
        """

        :param logicname:
        :param action:
        :param filename:
        :param newfilename:
        :return:

        valid actions are: 'enable', 'disable', 'trigger', 'unload', 'load', 'reload', 'delete', 'create', 'rename'
        """
        self.logger.info(f'LogicsController.set_logic_state(): logicname = {logicname}, action = {action}')
        if action == 'enable':
            self.logics.enable_logic(logicname)
            return json.dumps({'result': 'ok'})
        elif action == 'disable':
            self.logics.disable_logic(logicname)
            return json.dumps({'result': 'ok'})
        elif action == 'trigger':
            self.logics.trigger_logic(logicname, by='Admin')
            return json.dumps({'result': 'ok'})
        elif action == 'unload':
            self.logics.unload_logic(logicname)
            return json.dumps({'result': 'ok'})
        elif action == 'load':
            self.logics.load_logic(logicname)
            if self.logics.is_logic_loaded(logicname):
                return json.dumps({'result': 'ok'})
            else:
                return json.dumps(
                    {'result': 'error', 'description': 'Logic could not be loaded - for details look at the log'}
                )
        elif action == 'reload':
            self.logics.load_logic(logicname)  # implies unload_logic()
            if self.logics.is_logic_loaded(logicname):
                crontab = self.logics.get_logiccrontab(logicname)
                if (crontab is not None) and ('init' in crontab):
                    self.logger.info(
                        "LogicsController.set_logic_state(relaod): Triggering logic because crontab contains 'init' - crontab = '{}'".format(
                            crontab
                        )
                    )
                    self.logics.trigger_logic(logicname, by='Admin')
                return json.dumps({'result': 'ok'})
            else:
                return json.dumps(
                    {'result': 'error', 'description': 'Logic could not be loaded - for details look at the log'}
                )
        elif action == 'delete_with_code':
            self.logger.info(f'set_logic_state: action={action}')
            self.logics.delete_logic(logicname, with_code=True)
            return json.dumps({'result': 'ok'})
        elif action == 'delete':
            self.logger.info(f'set_logic_state: action={action}')
            self.logics.delete_logic(logicname)
            return json.dumps({'result': 'ok'})
        elif action == 'create':
            self.logger.info(f'set_logic_state: action={action} filename={filename}, logicname={logicname}')
            filename = filename.lower() + '.py'

            if logicname in self.logics.return_defined_logics():
                self.logger.warning(
                    'LogicsController.set_logic_state(create): Logic name {} is already used'.format(logicname)
                )
                return json.dumps({'result': 'error', 'description': 'Logic name {} is already used'.format(logicname)})
            else:
                if not os.path.isfile(os.path.join(self._sh.get_config_dir(DIR_LOGICS), filename)):
                    # create new logic code file, if none is found
                    logics_code = self.get_logic_template(filename)
                    if not self.logic_create_codefile(filename, logics_code):
                        self.logger.error(f"Could not create code-file '{filename}'")
                        return json.dumps(
                            {'result': 'error', 'description': f"Could not create code-file '{filename}'"}
                        )

                if self.logics.filename_used_count(filename) > 0:
                    self.logger.error(
                        f"code-file '{filename}' already exists and is used by another logic configuration"
                    )
                    return json.dumps(
                        {
                            'result': 'error',
                            'description': f"code-file '{filename}' already exists and is used by another logic configuration",
                        }
                    )

                self.logic_create_config(logicname, filename)
                if not self.logics.load_logic(logicname):
                    self.logger.warning(f"Could not load logic '{logicname}', syntax error")
                return json.dumps({'result': 'ok'})

        elif action == 'rename':
            # filename  = new logic name (required)
            # newfilename = new .py filename stem without extension (optional; keep current if empty)
            new_logicname = filename
            self.logger.info(
                f'set_logic_state: action={action}, old={logicname}, new_logicname={new_logicname}, newfilename={newfilename}'
            )

            if not new_logicname:
                return json.dumps({'result': 'error', 'description': 'New logic name is required'})

            name_changed = new_logicname != logicname
            # newfilename is only sent when the user actually changed the filename field
            file_will_change = bool(newfilename)

            if not name_changed and not file_will_change:
                return json.dumps({'result': 'error', 'description': 'New logic name is identical to the current name'})

            # "Already in use" only matters when the logic name itself changes;
            # if only the filename case changes the name stays the same, which is fine.
            if name_changed and new_logicname in self.logics.return_defined_logics():
                return json.dumps({'result': 'error', 'description': f"Logic name '{new_logicname}' is already in use"})

            # Read current config section
            conf = shyaml.yaml_load_roundtrip(self.logics._logic_conf)
            old_section = conf.get(logicname, None)
            if old_section is None:
                return json.dumps({'result': 'error', 'description': f"Logic '{logicname}' not found in configuration"})

            old_py_filename = old_section.get('filename', '')

            # Determine target .py filename
            if newfilename:
                target_py_filename = newfilename.lower() + '.py'
            else:
                target_py_filename = old_py_filename

            # Guard against shared files: reject if target filename is already used by any logic
            if target_py_filename.lower() != old_py_filename.lower():
                if self.logics.filename_used_count(target_py_filename) > 0:
                    return json.dumps(
                        {
                            'result': 'error',
                            'description': f"Filename '{target_py_filename}' is already used by another logic",
                        }
                    )
                # Rename the .py file on disk
                old_path = os.path.join(self.logics.get_logics_dir(), old_py_filename)
                new_path = os.path.join(self.logics.get_logics_dir(), target_py_filename)
                try:
                    os.rename(old_path, new_path)
                    self.logger.info(
                        f"set_logic_state(rename): renamed file '{old_py_filename}' → '{target_py_filename}'"
                    )
                except OSError as e:
                    return json.dumps({'result': 'error', 'description': f'Could not rename logic file: {e}'})

            if not name_changed:
                # Only the filename changed — update in-place: patch the filename key in the
                # existing YAML section without doing a section delete + recreate, which would
                # destroy the config when old_name == new_name.
                if self.logics.is_logic_loaded(logicname):
                    self.logics.unload_logic(logicname)
                conf = shyaml.yaml_load_roundtrip(self.logics._logic_conf)
                if logicname in conf:
                    conf[logicname]['filename'] = target_py_filename
                    shyaml.yaml_save_roundtrip(self.logics._logic_conf, conf, True)
                    self.logger.info(
                        f"set_logic_state(rename): updated filename for '{logicname}' → '{target_py_filename}'"
                    )
                self.logics.load_logic(logicname)
                self.logger.info(f"set_logic_state(rename): filename-only rename for '{logicname}' complete")
                return json.dumps({'result': 'ok'})

            # Unload old logic before modifying config
            if self.logics.is_logic_loaded(logicname):
                self.logics.unload_logic(logicname)

            # Build config_list from old section, substituting the (possibly new) filename
            config_list = [['filename', target_py_filename, '']]
            for key, value in old_section.items():
                if key != 'filename':
                    config_list.append([key, value, ''])

            # Create new config section (writes to logic.yaml)
            self.logics.update_config_section(True, new_logicname, config_list)

            # Remove old config section directly (delete_logic would try to delete the file)
            conf = shyaml.yaml_load_roundtrip(self.logics._logic_conf)
            if logicname in conf:
                del conf[logicname]
                shyaml.yaml_save_roundtrip(self.logics._logic_conf, conf, True)
                self.logger.info(f"set_logic_state(rename): removed old section '{logicname}' from logic.yaml")

            # Load under the new name
            self.logics.load_logic(new_logicname)
            self.logger.info(f"set_logic_state(rename): logic '{logicname}' renamed to '{new_logicname}'")
            return json.dumps({'result': 'ok'})

        else:
            self.logger.warning(
                "LogicsController.set_logic_state(): logic '"
                + logicname
                + "', action '"
                + action
                + "' is not supported"
            )
            return json.dumps({'result': 'error', 'description': "action '" + action + "' is not supported"})

        return

    def save_logic_parameters(self, logicname, params):
        # params = self.get_body()
        self.logger.info(f'LogicsController.save_logic_parameters: logic = {logicname}, params = {params}')

        logic_conf = shyaml.yaml_load_roundtrip(self._sh.get_config_file(BASE_LOGIC))
        sect = logic_conf.get(logicname)
        if sect is None:
            response = {'result': 'error', 'description': "Configuration section '{}' does not exist".format(logicname)}
        else:
            self.logger.info(f'LogicsController.save_logic_parameters: logic = {logicname}, alte params = {dict(sect)}')
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
                if value is None:
                    sect.pop(param, None)
                else:
                    self.logger.info(f'- param = {param}, value = {value}, type(value) = {Utils.get_type(value)}')
                    if (Utils.get_type(value) == 'str') and (value == ''):
                        sect.pop(param, None)
                    elif (Utils.get_type(value) == 'list') and (value == []):
                        sect.pop(param, None)
                    elif (Utils.get_type(value) == 'dict') and (value == {}):
                        sect.pop(param, None)
                    else:
                        sect[param] = value

            self.logger.info(
                'LogicsController.save_logic_parameters: logic = {}, neue params = {}'.format(logicname, dict(sect))
            )

            shyaml.yaml_save_roundtrip(self._sh.get_config_file(BASE_LOGIC), logic_conf, False)
            response = {'result': 'ok'}

        return json.dumps(response)

    def read(self, logicname=None, infotype=None):
        """
        return an object with type info about all logics or of a specific logic (if logicname is given)
        """
        # create a list of dicts, where each dict contains the information for one logic
        self.logger.info('LogicsController.read()')

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
    read.api_doc = [
        ApiDoc(
            summary='All logics, or the logic-group tree',
            method='get',
            path='/logics/',
            tags=['logics'],
            params=[ApiParam(name='infotype', enum=['groups'])],
        ),
        ApiDoc(
            summary="One logic's detail, or its runtime status",
            method='get',
            path='/logics/{logicName}',
            tags=['logics'],
            params=[
                ApiParam(name='logicName', location='path', required=True),
                ApiParam(name='infotype', enum=['status']),
            ],
        ),
    ]

    def update(self, name='', action='', filename='', newfilename=''):
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
            return json.dumps({'result': 'Error', 'description': 'SmartHomeNG is still initializing'})

        if name != '':
            if action == 'saveparameters':
                return self.save_logic_parameters(name, params)
            elif action == 'savegroup':
                self.logger.info(f'LogicsController.update: group={name}, action={action}, params={params}')
                return self.save_group(name, params)
                # return json.dumps({'result': 'Error', 'description': f"Saving of groups is not yet implemented. Group '{name}' was not saved"})
            elif action == 'deletegroup':
                self.logger.info(f'LogicsController.update: group={name}, action={action}, params={params}')
                return self.delete_group(name, params)
            else:
                self.logger.info(
                    f'LogicsController.update: group={name}, action={action}, filename={filename}, newfilename={newfilename}'
                )
                return self.set_logic_state(name, action, filename, newfilename)

        elif action not in ['create', 'load', 'delete', 'delete_with_code']:
            mylogic = self.logics.return_logic(name)
            if mylogic is None:
                self.logger.info(f"Error: No loaded logic with name '{name}' found")
                return json.dumps({'result': 'Error', 'description': f"No loaded logic with name '{name}' found"})

        return None

    update.expose_resource = True
    update.authentication_needed = True
    update.api_doc = [
        ApiDoc(
            summary='Logic lifecycle/state actions, rename, or save its parameters/group',
            method='put',
            path='/logics/{logicName}',
            tags=['logics'],
            params=[
                ApiParam(name='logicName', location='path', required=True),
                ApiParam(
                    name='action',
                    required=True,
                    enum=[
                        'trigger',
                        'enable',
                        'disable',
                        'load',
                        'unload',
                        'reload',
                        'delete',
                        'delete_with_code',
                        'create',
                        'rename',
                        'saveparameters',
                        'savegroup',
                        'deletegroup',
                    ],
                    description=(
                        'trigger/enable/disable/load/unload/reload/delete/create are the '
                        "frontend's documented lifecycle actions. delete_with_code is a "
                        'backend-only, more destructive sibling of delete (also removes the '
                        '.py file) - deliberately not exposed as a one-click UI action. rename '
                        'additionally takes filename= (new name) and optionally newfilename=. '
                        'saveparameters/savegroup/deletegroup are dispatched through this same '
                        'PUT but act on the parameter section / logic-group config respectively.'
                    ),
                ),
                ApiParam(name='filename'),
                ApiParam(name='newfilename'),
            ],
            request_body='application/json',
            description=(
                'Required for action=saveparameters (parameter dict) and action=savegroup '
                '(group config); empty body otherwise.'
            ),
        )
    ]
