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

from .rest import RESTResource


class SchedulersController(RESTResource):

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.base_dir = self._sh.get_basedir()
        self.logger = logging.getLogger(__name__)

        return


    # ======================================================================
    #  GET /api/schedulers
    #
    def read(self, id=None):
        """
        Handle GET requests for schedulers API
        """
        schedule_list = []

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

                if schedule['cycle'] == None:
                    schedule['cycle'] = '-'
                if schedule['cron'] == None:
                    schedule['cron'] = '-'

                nl = entry.split('.')
                if nl[0].lower() in ['items', 'logics', 'plugins']:
                    schedule['group'] = nl[0].lower()
                    schedule['group'] = schedule['group'][:-1]  # items -> item, logics -> logic, plugins -> plugin
                    del nl[0]
                    schedule['name'] = '.'.join(nl)

                schedule_list.append(schedule)

        schedule_list_sorted = sorted(schedule_list, key=lambda k: k['fullname'].lower())
        return json.dumps(schedule_list_sorted)

    read.expose_resource = True
    read.authentication_needed = True

