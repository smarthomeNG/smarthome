#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 Marcus Popp                          marcus@popp.mx
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import collections
import time


class Log(collections.deque):

    def __init__(self, smarthome, name, mapping, maxlen=50):
        """
        Class to implement a log (deprecated? -> old logging!)
        As of version 1.6 develop this is used in core at bin/smarthome.py and
        in plugins memlog, operationlog
        """
        collections.deque.__init__(self, maxlen=maxlen)
        self.mapping = mapping
        self.update_hooks = []
        self._sh = smarthome
        self._name = name
        smarthome.add_log(name, self)

    def add(self, entry):
        self.appendleft(entry)
        for listener in self._sh.return_event_listeners('log'):
            listener('log', {'name': self._name, 'log': [dict(zip(self.mapping, entry))]})

    def last(self, number):
        return(list(self)[-number:])

    def export(self, number):
        return [dict(zip(self.mapping, x)) for x in list(self)[:number]]

    def clean(self, dt):
        while True:
            try:
                entry = self.pop()
            except Exception:
                return
            if entry[0] > dt:
                self.append(entry)
                return
    
