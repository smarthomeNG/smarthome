#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# todo
# put your name and email here and delete these two todo lines
#  Copyright 2016 <AUTHOR>                                        <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.   
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.1
#  upwards.
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
#
#########################################################################

import logging
from lib.model.smartplugin import SmartPlugin

#
# you need to adapt this sample plugin at least everywhere where a todo is found
#

# todo
# instead of PluginName you name your plugin
class PluginClassName(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """
    
    # todo
    # change ALLOW_MULTIINSTANCE to true if your plugin will support multiple instances (seldom)
    ALLOW_MULTIINSTANCE = False
    
    # todo
    # set the version number of you plugin
    # a.b should reflect the version of SmartHomeNG that is first compatible with this
    # plugin
    # c is the version of your plugin
    # a sample plugin with a 23rd revision starting for SmartHomeNG 1.2 would be '1.2.23'
    PLUGIN_VERSION = "a.b.c"


    def __init__(self, sh, *args, **kwargs):
        """
        Initalizes the plugin. The parameters describe for this method are pulled from the entry in plugin.conf.

        :param sh:  The instance of the smarthome object, save it for later references
        """
        # attention:
        # if your plugin runs standalone, sh will likely be None so do not rely on it later or check it within your code
        
        self._sh = sh
        self.logger = logging.getLogger(__name__) 	# get a unique logger for the plugin and provide it internally

        # todo:
        # put any initialization for your plugin here
        

    def run(self):
        """
        Run method for the plugin
        """        
        self.logger.debug("run method called")
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)


    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.debug("stop method called")
        self.alive = False


    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference

        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.

        """
        # todo 
        # change 'foo_itemtag' into your attribute name
        # you might also check for other attribute names if your plugin supports multiple attributes
        if self.has_iattr(item.conf, 'foo_itemtag'):
            self.logger.debug("parse item: {0}".format(item))

        # todo
        # if interesting item for sending values:
        #   return update_item

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Write items values

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        # todo 
        # change 'foo_itemtag' into your attribute name
        if item():
            if self.has_iattr(item.conf, 'foo_itemtag'):
                self.logger("update_item ws called with item '{}' from caller '{}', source '{}' and dest '{}'".format(item, caller, source, dest))
                pass

        # PLEASE CHECK CODE HERE. The following was in the old skeleton.py and seems not to be 
        # valid any more 
        # # todo here: change 'plugin' to the plugin name
        # if caller != 'plugin':  
        #    logger.info("update item: {0}".format(item.id()))


"""
If the plugin is run standalone e.g. for test purposes the follwing code will be executed
"""
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    # todo
    # change PluginClassName appropriately
    PluginClassName(None).run()

