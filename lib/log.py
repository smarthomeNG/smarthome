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
        Class to implement a log
        This is based on a double ended queue. New entries are appended left and old ones are popped right.
        
        
        As of version 1.7a develop this is used in core at bin/smarthome.py and
        in plugins memlog, operationlog and visu_websocket

        :param smarthome: the SmartHomeNG main object 
        :param name: a descriptive name for the log
        :param mapping: Kind of a headline for the entry which can be anything
            e.g. mappings can be [time, thread, level, message ] and log entry is a 

        :param maxlen: maximum length of the log, defaults to 50
        """
        collections.deque.__init__(self, maxlen=maxlen)
        self.mapping = mapping
        #self.update_hooks = []     # nowhere else found, maybe not needed any more
        self._sh = smarthome        
        self._name = name
        smarthome.add_log(name, self)

    def add(self, entry):
        """
        Just adds a log entry to the left side of the queue. If the queue already holds maxlen
        entries, the rightmost will be discarded automatically.
        """
        self.appendleft(entry)
        for listener in self._sh.return_event_listeners('log'):
            listener('log', {'name': self._name, 'log': [dict(zip(self.mapping, entry))]})

    def last(self, number):
        """
        Returns the last ``number`` entries of the log
        """
        return(list(self)[-number:])

    def export(self, number):
        """
        Returns up to ``number`` entries from the log and prepares them together with the mapping
        """
        return [dict(zip(self.mapping, x)) for x in list(self)[:number]]

    def clean(self, dt):
        """
        Assuming dt to be a datetime: remove all entries that are smaller or equal 
        to this given datetime from the right side of the queue
        """
        while True:
            try:
                entry = self.pop()
            except Exception:
                return
            if entry[0] > dt:
                self.append(entry)
                return
    
