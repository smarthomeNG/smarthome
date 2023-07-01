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
import copy

from .rest import RESTResource


class SchedulersController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:])

        return


    def build_task_info(self, obj):

        try:
            task_type = obj.__module__
        except:
            task_type = '?'

        try:
            if task_type == 'lib.logic':
                task_name = obj.name
            elif task_type.startswith('lib.item'):
                task_name = obj._path
            else:
                task_name = obj.__name__
        except:
            task_name = dir(obj)

        if task_type == 'lib.logic':
            task_type = 'logic'
            task_name = "'" + task_name + "'"

        elif task_type.startswith('lib.item'):
                task_name = ''
                task_type = ''

        else:
            if task_type.startswith('plugins.'):
                task_name = task_type.split('.')[1] + '.' + task_name
                task_type = 'plugin method'

            if task_type == '__main__':
                task_name = 'sh.' + task_name
                task_type = 'main method'

            if task_type.startswith('lib.'):
                task_name = task_type.split('.')[1] + '.' + task_name
                task_type = 'lib method'

            task_name += '()'

        return (task_type, task_name)


    # ======================================================================
    #  GET /api/schedulers
    #
    def read(self, id=None):
        """
        Handle GET requests for schedulers API
        """
        schedule_list = []

        # handle all defined schedulers
        for entry in self._sh.scheduler._scheduler:
            schedule = dict()
            s = self._sh.scheduler._scheduler[entry]
            if s['next'] != None and s['cycle'] != '' and s['cron'] != '':
                schedule['fullname'] = entry
                schedule['name'] = entry
                schedule['group'] = 'other'
                schedule['next'] = s['next'].strftime('%Y-%m-%d %H:%M:%S%z')
                schedule['cycle'] = str(s['cycle'])
                #            schedule['cron'] = html.escape(str(s['cron']))
                schedule['cron'] = str(s['cron'])
                schedule['prio'] = s['prio']
                schedule['active'] = s['active']
                schedule['value'] = str(s['value'])

                if schedule['cycle'] == 'None':
                    schedule['cycle'] = '-'
                if schedule['cron'] == 'None':
                    schedule['cron'] = '-'

                nl = entry.split('.')
                if nl[0].lower() in ['items', 'logics', 'plugins']:
                    schedule['group'] = nl[0].lower()
                    schedule['group'] = schedule['group'][:-1]  # items -> item, logics -> logic, plugins -> plugin
                    del nl[0]
                    schedule['name'] = '.'.join(nl)

                (schedule['task_type'], schedule['task_name']) = self.build_task_info(s['obj'])
                schedule_list.append(schedule)

        # Handle all waiting triggers
        triggers = self._sh.scheduler._triggerq.dump()    # returns a list
        for trigger in triggers:
            # trigger holds tuples of (datetime, priority) and (name, obj, by, source, dest, value)
            #(dt, prio), (name, obj, by, source, dest, value) = self._triggerq.get()

            triggerinfo = dict()
            (dt, prio), (name, obj, by, source, dest, value) = trigger

            triggerinfo['fullname'] = 'trigger.' + name
            triggerinfo['name'] = 'trigger.' + name
            triggerinfo['group'] = 'trigger'    # later: 'trigger'
            triggerinfo['next'] = dt.strftime('%Y-%m-%d %H:%M:%S%z')
            triggerinfo['cycle'] = '-'
            triggerinfo['cron'] = '-'
            triggerinfo['prio'] = prio
            #triggerinfo['active'] = True
            triggerinfo['value'] = str(value)
            triggerinfo['by'] = by
        #     # obj, source, dest
            (triggerinfo['task_type'], triggerinfo['task_name']) = self.build_task_info(obj)
            schedule_list.append(triggerinfo)

        schedule_list_sorted = sorted(schedule_list, key=lambda k: k['fullname'].lower())
        return json.dumps(schedule_list_sorted)

    read.expose_resource = True
    read.authentication_needed = True

