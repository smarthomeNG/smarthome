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
from .utils import *
from lib.logic import Logic

# from jinja2 import Environment, FileSystemLoader

from .utils import *
from cherrypy.lib.static import serve_file


class BackendBlocklyLogics:
    """
    Google Blockly for Logics
    """
    @cherrypy.expose
    def logics_blockly_html(self):
        self.find_visu_plugin()

        tmpl = self.env.get_template('logics_blockly.html')
        return tmpl.render(smarthome=self._sh,
                           dyn_sh_toolbox=self._DynToolbox(self._sh), lang=translation_lang,
                           visu_plugin=(self.visu_plugin is not None))

    def _DynToolbox(self, sh):
        return "<sep></sep>\n" + self._build_item_block_tree(self._sh.return_items())

    def _build_item_block_tree(self, items, cname="Items"):
        """
        recursive definiert
        """
        items_sorted = sorted(items, key=lambda k: str.lower(k['_path']),
                              reverse=False)
        if len(items_sorted) == 0:
            return ''
        else:
            # self.logger.debug("\n" + cname + "\n" +
            #                   "|".join(i._name for i in items_sorted))
            parent_items_sorted = []
            last_parent_item = None
            for item in items_sorted:
                if last_parent_item is None or last_parent_item._path not in item._path:
                    parent_items_sorted.append(item)
                    last_parent_item = item

            xml = '<category name="{0} ({1})">\n'.format(
                cname, len(parent_items_sorted))
            for item in parent_items_sorted:
                xml += self._build_item_block(item)
                xml += self._build_item_block_tree(
                    item.return_children(), item._name)
            return xml + '</category>\n'

    def _build_item_block(self, item):
        if item._type in ['bool', 'num', 'str']:
            n, p, t = item._name, item._path, item.type()
            if n == p:
                n = "".join(x.title() for x in p.split('.'))
            block = '<block type="sh_item_obj" name="{0}">'.format(n)
            block += '  <field name="N">{0}</field><field name="P">{1}</field><field name="T">{2}</field>'.format(
                n, p, t)
            block += '</block>\n'
            return block
        else:
            return '\n'

    @cherrypy.expose
    def logics_blockly_load(self):
        fn_xml = self._sh._logic_dir + "blockly_logics.xml"
        return serve_file(fn_xml, content_type='application/xml')

    @cherrypy.expose
    def logics_blockly_save(self, py, xml):
        self._pycode = py
        self._xmldata = xml
        fn_py = self._sh._logic_dir + "blockly_logics.py"
        fn_xml = self._sh._logic_dir + "blockly_logics.xml"
        self.logger.debug(
            "Backend: logics_html: SAVE PY blockly logic = {0}\n '{1}'".format(fn_py, py))
        with open(fn_py, 'w') as fpy:
            fpy.write(py)
        self.logger.debug(
            "Backend: logics_html: SAVE XML blockly logic = {0}\n '{1}'".format(fn_xml, xml))
        with open(fn_xml, 'w') as fxml:
            fxml.write(xml)

        code = self._pycode
        bytecode = compile(code, '<string>', 'exec')
        s = []
        for name in self._sh.scheduler:
            if name.startswith('blockly_runner'):
                # logger.info('Blockly Logics: remove '+ name)
                s.append(name)
        for name in s:
            self._sh.scheduler.remove(name)

        for line in code.splitlines():
            if line and line.startswith('#?#'):
                id, __, trigger = line[3:].partition(':')
                by, __, val = trigger.partition('=')
                by = by.strip()
                val = val.strip()
                # logger.info('Blockly Logics: {} => {} :: {}'.format(id, by, val))
                logic = Logic(self._sh, 'blockly_runner_' + id,
                              {'bytecode': bytecode, })
                if by == 'cycle':
                    self._sh.scheduler.add(
                        'blockly_runner_' + id, logic, prio=3, cron=None, cycle=val)
                    # logger.info('Blockly Logics: cycles     => '+ val)
                elif by == 'crontab':
                    self._sh.scheduler.add(
                        'blockly_runner_' + id, logic, prio=3, cron=val, cycle=None)
                    # logger.info('Blockly Logics: crontabs   => '+ val)
                elif by == 'watchitem':
                    logic.watch_item = val
                    # item = self._sh.return_item(val)
                    # item.add_logic_trigger(logic)
                    # logger.info('Blockly Logics: watchitems => '+ val)
