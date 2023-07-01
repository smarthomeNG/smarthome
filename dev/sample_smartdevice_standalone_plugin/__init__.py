#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms           Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG
#
#  Example plugin with standalone code for SmartDevicePlugin class
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

# this block is needed for standalone operation
# -->
import builtins
import os
import sys

if __name__ == '__main__':
    # just needed for standalone mode
    builtins.SDP_standalone = True

    class SmartPlugin():
        pass

    class SmartPluginWebIf():
        pass

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-3])
    sys.path.insert(0, BASE)

else:
    builtins.SDP_standalone = False
# <--

from lib.model.sdp.globals import PLUGIN_ATTR_CONNECTION, CONN_NULL         # import all "constants" you need in your own code
from lib.model.smartdeviceplugin import SmartDevicePlugin, Standalone       # needed, obviously

if not SDP_standalone:
    from .webif import WebInterface                                         # can be removed if no webif is provided


# depending on the complexity of the communication between the device and shng,
# this can be all plugin code needed to run (compare Viessmann plugin)


class example(SmartDevicePlugin):
    """ Example class for SmartDevicePlugin with standalone functionality. """
    PLUGIN_VERSION = '0.1.0'                                                # adjust, must match version in plugin.yaml

    def _set_device_defaults(self):

        # you can add initialisations and internal defaults here
        
        # for demonstation purposes, we want to use the null connection
        self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_NULL
        self._use_callbacks = True

        # needed for webif usage
        if not SDP_standalone:
            self._webif = WebInterface

    def _post_init(self):

        # you might want to do additional initialisations after
        # the plugins' __init__ method has finished
        # otherwise, remove this method

        self._my_property = 'foo'

    def on_connect(self, by=None):
        """ callback if connection is made. """
        self.logger.info('example plugin connected')

    def on_disconnect(self, by=None):
        """ callback if connection is broken. """
        self.logger.info('example plugin disconnected')

#
# methods for standalone mode
#

    def run_standalone(self):
        """
        runs in standalone mode after initialisation.

        Plugin class is loaded, instantiated and initialized; run() has not been
        called. Either call run() yourself, or work around it.
        """
        self.logger.warning(f'example device using connection class {self._parameters.get(PLUGIN_ATTR_CONNECTION, "unknown")}...')

        # now you can do what you like, you are working inside the active plugin class.
        # access to items, logics and the like is not possible, as shng is not running.
        # connection is initialized and can be opened.
        #
        # one common purpose of standalone mode is device discovery or test
        #


# needed to start operation in standalone mode
if __name__ == '__main__':
    s = Standalone(example, sys.argv[0])
