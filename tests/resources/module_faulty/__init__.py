#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016-2017  Martin Sinn                       m.sinn@gmx.de
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


import logging

class dummy():

    version = '1.x.y'
    longname = 'Dummy module for SmartHomeNG'

    def __init__(self, sh, testparam=''):
        """
        Initialization Routine for the module
        """
        self.shortname = self.__class__.__name__
        self.logger = logging.getLogger(__name__)
        self._sh = sh
        self.logger.debug("Module '{}': Initializing".format(self.shortname))

        self.logger.debug("Module '{}': Parameters = '{}'".format(self.shortname, str(self._parameters)))

        try:
            self._dummy = self._parameters['dummy']
        except:
            self.logger.critical("Module '{}': Inconsistent module (invalid metadata definition)".format(self.shortname))
            self._init_complete = False
            return
                
        
    def start(self):
        """
        If the module needs to startup threads or uses python modules that create threads,
        put thread creation code or the module startup code here.
        
        Otherwise don't enter code here
        """
#        self.logger.debug("Module '{}': Starting up".format(self.shortname))
        pass
        

    def stop(self):
        """
        If the module has started threads or uses python modules that created threads,
        put cleanup code here.
        
        Otherwise don't enter code here
        """
#        self.logger.debug("Module '{}': Shutting down".format(self.shortname))
        pass
    