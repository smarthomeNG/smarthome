#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2018-      Martin Sinn                         m.sinn@gmx.de
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

import datetime
import collections
import html
import json

import cherrypy

import lib.config
from lib.item import Items


class ItemData:

    def __init__(self):

        self.items = Items.get_instance()

        return


    # -----------------------------------------------------------------------------------
    #    ITEMS  -  Old Interface methods (from backend)
    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def items_json(self, mode="tree"):
        """
        returns a list of items as json structure

        :param mode:             tree (default) or list structure
        """
        if self.items == None:
            self.items = Items.get_instance()

        items_sorted = sorted(self.items.return_items(), key=lambda k: str.lower(k['_path']), reverse=False)

        if mode == 'tree':
            parent_items_sorted = []
            for item in items_sorted:
                if "." not in item._path:
                    parent_items_sorted.append(item)

            (item_data, item_count) = self._build_item_tree(parent_items_sorted)
            self.logger.info("admin: items_json: In tree-mode, {} items returned".format(item_count))
            return json.dumps([item_count, item_data])
        else:
            item_list = []
            for item in items_sorted:
                item_list.append(item._path)
            self.logger.info("admin: items_json: Not in tree-mode, {} items returned".format(len(item_list)))
            return json.dumps(item_list)


    def _build_item_tree(self, parent_items_sorted):
        item_data = []
        count_sum = 0

        for item in parent_items_sorted:
            (nodes, count) = self._build_item_tree(item.return_children())
            count_sum += count
            tags = []
            tags.append(len(nodes))
            lpath = item._path.split('.')
            if self.module.itemtree_fullpath:
                tree_label = item._path
            else:
                tree_label = lpath[len(lpath)-1]
            item_data.append({'label': tree_label, 'children': nodes,
                              'path': item._path,  'name': item._name, 'tags': tags,
#                              'nodename': lpath[len(lpath)-1], 'nodes': nodes
                              })

        return item_data, len(item_data)+count_sum

    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def item_detail_json_html(self, item_path):
        """
        returns the details of an item as json structure
        """
        if self.items == None:
            self.items = Items.get_instance()

        # self.logger.warning("item_detail_json_html: item_path = {}".format(item_path))

        item_data = []
        item = self.items.return_item(item_path)
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
                if entry == "items." + item._path:
                    if self._sh.scheduler._scheduler[entry]['cycle']:
                        cycle = self._sh.scheduler._scheduler[entry]['cycle']
                    if self._sh.scheduler._scheduler[entry]['cron']:
                        crontab = html.escape(str(self._sh.scheduler._scheduler[entry]['cron']))
                    break
            if cycle == '':
                cycle = '-'
            if crontab == '':
                crontab = '-'

            changed_by = item.changed_by()
            if changed_by[-5:] == ':None':
                changed_by = changed_by[:-5]

            updated_by = item.updated_by()
            if updated_by[-5:] == ':None':
                updated_by = updated_by[:-5]

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
                item_conf_sorted['sv_widget'] = html.escape(item_conf_sorted['sv_widget'])

            logics = []
            for trigger in item.get_logic_triggers():
                logics.append(html.escape(format(trigger)))
            triggers = []
            for trigger in item.get_method_triggers():
                trig = format(trigger)
                trig = trig[1:len(trig) - 27]
                triggers.append(html.escape(format(trig.replace("<", ""))))

            # build on_update and on_change data
            on_update_list = self.build_on_list(item._on_update_dest_var, item._on_update)
            on_change_list = self.build_on_list(item._on_change_dest_var, item._on_change)

            self._trigger_condition_raw = item._trigger_condition_raw
            if self._trigger_condition_raw == []:
                self._trigger_condition_raw = ''

            data_dict = {'path': item._path,
                         'name': item._name,
                         'type': item.type(),
                         'value': value,
                         'change_age': item.age(),
                         'update_age': item.update_age(),
                         'last_update': str(item.last_update()),
                         'last_change': str(item.last_change()),
                         'changed_by': changed_by,
                         'updated_by': updated_by,
                         'previous_value': prev_value,
                         'previous_change_age': item.prev_age(),
                         'previous_update_age': item.prev_update_age(),
                         'previous_update': str(item.prev_update()),
                         'previous_change': str(item.prev_change()),
                         'enforce_updates': enforce_updates,
                         'cache': cache,
                         'eval': html.escape(self.disp_str(item._eval)),
                         'trigger': self.disp_str(item._trigger),
                         'trigger_condition': self.disp_str(item._trigger_condition),
                         'trigger_condition_raw': self.disp_str(self._trigger_condition_raw),
                         'on_update': html.escape(self.list_to_displaystring(on_update_list)),
                         'on_change': html.escape(self.list_to_displaystring(on_change_list)),
                         'log_change': self.disp_str(item._log_change),
                         'cycle': str(cycle),
                         'crontab': str(crontab),
                         'autotimer': self.disp_str(item._autotimer),
                         'threshold': self.disp_str(item._threshold),
                         'threshold_crossed': '',
#                         'config': json.dumps(item_conf_sorted),
#                         'logics': json.dumps(logics),
#                         'triggers': json.dumps(triggers),
                         'config': dict(item_conf_sorted),
                         'logics': logics,
                         'triggers': triggers,
                         'filename': str(item._filename),
                         }
            if item._threshold:
                data_dict['threshold'] = str(item._threshold_data[0]) + ' : ' + str(item._threshold_data[1])
                data_dict['threshold_crossed'] = str(item._threshold_data[2])

            if item._struct is not None:
                data_dict['struct'] = item._struct

            # cast raw data to a string
            if item.type() in ['foo', 'list', 'dict']:
                data_dict['value'] = str(item._value)
                data_dict['previous_value'] = str(prev_value)

            item_data.append(data_dict)
            # self.logger.warning("details: item_data = {}".format(item_data))
            return json.dumps(item_data)
        else:
            self.logger.error("Requested item '{}' is None, check if item really exists.".format(item_path))
            return

    # -----------------------------------------------------------------------------------

    @cherrypy.expose
    def item_change_value_html(self, item_path, value):
        """
        Is called by items.html when an item value has been changed
        """
        self.logger.info("item_change_value_html: item '{}' set to value '{}'".format(item_path, value))
        item_data = []
        try:
            item = self.items.return_item(item_path)
        except Exception as e:
            self.logger.error("item_change_value_html: item '{}' set to value '{}' - Exception {}".format(item_path, value, e))
            return
        if 'num' in item.type():
            if "." in value or "," in value:
                value = float(value)
            else:
                value = int(value)
        item(value, caller='admin')

        return



    def disp_str(self, val):
        s = str(val)
        if s == 'False':
            s = '-'
        elif s == 'None':
            s = '-'
        return s

    def list_to_displaystring(self, l):
        """
        """
        if type(l) is str:
            return l

        edit_string = ''
        for entry in l:
            if edit_string != '':
                edit_string += ' | '
            edit_string += str(entry)
        if edit_string == '':
            edit_string = '-'
        #        self.logger.info("list_to_displaystring: >{}<  -->  >{}<".format(l, edit_string))
        return edit_string

    def build_on_list(self, on_dest_list, on_eval_list):
        """
        build on_xxx data
        """
        on_list = []
        if on_dest_list is not None:
            if isinstance(on_dest_list, list):
                for on_dest, on_eval in zip(on_dest_list, on_eval_list):
                    if on_dest != '':
                        on_list.append(on_dest + ' = ' + on_eval)
                    else:
                        on_list.append(on_eval)
            else:
                if on_dest_list != '':
                    on_list.append(on_dest_list + ' = ' + on_eval_list)
                else:
                    on_list.append(on_eval_list)
        return on_list


