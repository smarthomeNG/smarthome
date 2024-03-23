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
import ast

import cherrypy

import lib.config
from lib.item import Items

from lib.constants import (ATTRIBUTE_SEPARATOR)


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
        if self.items is None:
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

    def escape_complex_value(self, value):

        wrk = str(value)
        if wrk == '':
            return wrk
        wrk = wrk.replace('&', '&amp;')
        wrk = wrk.replace('>', '&gt;')
        wrk = wrk.replace('<', '&lt;')
        try:
            return str(ast.literal_eval(wrk))
        except:
            self.logger.error(f"escape_complex_value: cannot handle value = '{wrk}'")
            return ''

    @cherrypy.expose
    def item_detail_json_html(self, item_path):
        """
        returns the details of an item as json structure
        """
        if self.items is None:
            self.items = Items.get_instance()

        # self.logger.warning("item_detail_json_html: item_path = {}".format(item_path))

        item_data = []
        item = self.items.return_item(item_path)
        if item is not None:
            if item.type() is None or item.type() == '':
                prev_value = ''
                last_value = ''
                value = ''
            else:
                last_value = item.property.last_value
                if last_value is None:
                    last_value = ''
                prev_value = item.property.prev_value
                if prev_value is None:
                    prev_value = ''
                value = item._value

            if isinstance(prev_value, datetime.datetime):
                prev_value = str(prev_value)

            if isinstance(last_value, datetime.datetime):
                last_value = str(last_value)

            if 'str' in item.type():
                value = html.escape(value)
                prev_value = html.escape(prev_value)
                last_value = html.escape(last_value)

            description = item.property.description
            if description is None:
                description = ''

            #cycle = ''
            crontab = ''
            for entry in self._sh.scheduler._scheduler:
                if entry == "items." + item._path:
            #        if self._sh.scheduler._scheduler[entry]['cycle']:
            #            cycle = self._sh.scheduler._scheduler[entry]['cycle']
                    if self._sh.scheduler._scheduler[entry]['cron']:
                        crontab = html.escape(str(self._sh.scheduler._scheduler[entry]['cron']))
                    break
            #if cycle == '':
            #    cycle = '-'
            if crontab == '':
                crontab = '-'

            cycle = str(item._cycle_time)
            if item._cycle_value is not None:
                cycle += ' ' + ATTRIBUTE_SEPARATOR + ' ' + str(item._cycle_value)

            changed_by = item.property.last_change_by
            if changed_by[-5:] == ':None':
                changed_by = changed_by[:-5]

            updated_by = item.property.last_update_by
            if updated_by[-5:] == ':None':
                updated_by = updated_by[:-5]

            previous_changed_by = item.property.prev_change_by
            if previous_changed_by[-5:] == ':None':
                previous_changed_by = previous_changed_by[:-5]

            previous_updated_by = item.property.prev_update_by
            if previous_updated_by[-5:] == ':None':
                previous_updated_by = previous_updated_by[:-5]

            if str(item._cache) == 'False':
                cache = 'off'
            else:
                cache = 'on'
            if str(item._enforce_updates) == 'False':
                enforce_updates = 'off'
            else:
                enforce_updates = 'on'

            if str(item._enforce_change) == 'False':
                enforce_change = 'off'
            else:
                enforce_change = 'on'

            item_conf_sorted = collections.OrderedDict(sorted(item.conf.items(), key=lambda t: str.lower(t[0])))
            if item_conf_sorted.get('sv_widget', '') != '':
                item_conf_sorted['sv_widget'] = html.escape(item_conf_sorted['sv_widget'])

            logics = []
            for trigger in item.get_logic_triggers():
                logic_name = format(trigger)
                logic_info = self._sh.logics.get_logic_info(logic_name)
                self.logger.info(f"Triggered {logic_name=}, {logic_info=}")
                logic={'name': logic_name, 'description': logic_info.get('description', '')}
                logics.append(logic)
                #logics.append(html.escape(format(trigger)))
            triggers = []
            for trigger in item.get_method_triggers():
                trig = format(trigger)
                trig = trig[1:len(trig) - 27]
                triggers.append(html.escape(format(trig.replace("<", ""))))

            for trigger in item.get_item_triggers():
                trig = "bound item '" + trigger._path + "' (eval)"
                triggers.append(format(trig))

            for trigger in item.get_hysteresis_item_triggers():
                trig = "bound item '" + trigger._path + "' (hysteresis)"
                triggers.append(format(trig))

            # build on_update and on_change data
            on_update_list = self.build_on_list(item._on_update_dest_var, item._on_update)
            on_change_list = self.build_on_list(item._on_change_dest_var, item._on_change)

            self._trigger_condition_raw = item._trigger_condition_raw
            if self._trigger_condition_raw == []:
                self._trigger_condition_raw = ''

            hysteresis_upper_threshold =  str(item._hysteresis_upper_threshold)
            if item._hysteresis_upper_timer is not None:
                hysteresis_upper_threshold += ' ' + ATTRIBUTE_SEPARATOR + ' ' + str(item._hysteresis_upper_timer)

            hysteresis_lower_threshold =  str(item._hysteresis_lower_threshold)
            if item._hysteresis_lower_timer is not None:
                hysteresis_lower_threshold += ' ' + ATTRIBUTE_SEPARATOR + ' ' + str(item._hysteresis_lower_timer)

            autotimer = str(item._autotimer_time)
            if item._autotimer_value is not None:
                autotimer += ' ' + ATTRIBUTE_SEPARATOR + ' ' + str(item._autotimer_value)

            data_dict = {'path': item.property.path,
                         'name': item.property.name,
                         'description': description,
                         'type': item.property.type,
                         'value': value,
                         'change_age': item.property.last_change_age,
                         'update_age': item.property.last_update_age,
                         'last_update': str(item.property.last_update),
                         'last_change': str(item.property.last_change),
                         'changed_by': changed_by,
                         'updated_by': updated_by,
                         'last_value': last_value,
                         'previous_change_age': item.property.prev_change_age,
                         'previous_update_age': item.property.prev_update_age,
                         'previous_update': str(item.property.prev_update),
                         'previous_change': str(item.property.prev_change),
                         'previous_change_by': previous_changed_by,
                         'previous_update_by': previous_updated_by,
                         'previous_value': prev_value,
                         'enforce_updates': enforce_updates,
                         'enforce_change': enforce_change,
                         'cache': cache,
                         'eval': html.escape(self.disp_str(item._eval)),
                         'trigger': self.disp_str(item._trigger),
                         'trigger_condition': self.disp_str(item._trigger_condition),
                         'trigger_condition_raw': self.disp_str(self._trigger_condition_raw),
                         'hysteresis_input': self.disp_str(item._hysteresis_input),
                         'hysteresis_upper_threshold': self.disp_str(hysteresis_upper_threshold),
                         'hysteresis_lower_threshold': self.disp_str(hysteresis_lower_threshold),
                         'on_update': html.escape(self.list_to_displaystring(on_update_list)),
                         'on_change': html.escape(self.list_to_displaystring(str(on_change_list))),
                         'log_change': self.disp_str(item._log_change),
                         'log_level': self.disp_str(item._log_level_name),
                         'log_text': self.disp_str(item._log_text),
                         'log_mapping': self.disp_str(item._log_mapping),
                         'log_rules': self.disp_str(item._log_rules),
                         'cycle': str(cycle),
                         'crontab': str(crontab),
                         'autotimer': self.disp_str(autotimer),
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
            if item.type() in ['foo']:
                data_dict['value'] = str(item._value)
                data_dict['last_value'] = str(last_value)
                data_dict['previous_value'] = str(prev_value)

            # cast list/dict data to a string
            if item.type() in ['list', 'dict']:
                data_dict['value'] = self.escape_complex_value(item._value)
                data_dict['last_value'] = self.escape_complex_value(last_value)
                data_dict['previous_value'] = self.escape_complex_value(prev_value)


            item_data.append(data_dict)
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
        if self.items is None:
            self.items = Items.get_instance()
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

