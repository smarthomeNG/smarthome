#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Strassburg c.strassburg(a)gmx.de
# 
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################
from lib.model.smartobject import SmartObject
from lib.utils import Utils
import logging

class SmartPlugin(SmartObject, Utils):
    __instance = '' 
    __sh = None
    logger = logging.getLogger(__name__)
    def get_version(self):
        """
            return plugin version 
            :rtype: str
        """
        return self.PLUGIN_VERSION
    
    def set_instance_name(self, instance):
        """
            set instance name of the plugin
        """
        if self.ALLOW_MULTIINSTANCE:
            self.__instance = instance
        else: 
            self.logger.warning("Plugin does not allow more then one instance") 
    
    def get_instance_name(self):
        """
            return instance name of the plugin
            :rtype: str
        """
        return self.__instance

    def is_multi_instance_capable(self):
        """
            return information if plugin is capable of multi instance handling
            :rtype: bool
        """
        if self.ALLOW_MULTIINSTANCE:
            return True
        else:
            return False
  
    def __get_iattr(self, attr):
        """
            returns item attribute for plugin instance
            
            :rtype: str
        """
        if self.__instance == '':
            return attr
        else:
           return "%s@%s"%(attr, self.__instance)

    def has_iattr(self, conf, attr):
        """
            checks item conf for an attribute
            :rtype: Boolean 
        """
        if self.__get_iattr(attr) in conf or "%s@*"%attr in conf:
            return True
        return False
    
    def get_iattr_value(self, conf, attr):
        """
            returns value for an attribute from item config
        """
        __value = None
        __attr = self.__get_iattr(attr)
        if __attr in conf:
            __value = conf[__attr] 
        elif "%s@*"%attr in conf:
            __value = conf["%s@*"%attr]
        return __value

    
    def __new__(cls, *args, **kargs):
        if not hasattr(cls,'PLUGIN_VERSION'):
            raise NotImplementedError("'Plugin' subclasses should have a 'PLUGIN_VERSION' attribute")
        return SmartObject.__new__(cls,*args,**kargs)

    def set_sh(self, smarthome):
        self.__sh = smarthome

    def get_info(self):
        """ 
           returns a small plugin info like class, version and instance name as string
           :rtype: str
        """
        return "Plugin: '{0}.{1}', Version: '{2}', Instance: '{3}'".format(self.__module__, self.__class__.__name__,  self.get_version(),self.get_instance_name())

