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

    class SmartPlugin:
        pass

    class SmartPluginWebIf:
        pass

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-3])
    sys.path.insert(0, BASE)

else:
    # Set the shared standalone flag to False when loaded as part of shNG.
    # SDP uses builtins so all modules in the same process share one flag
    # without any import dependency. This is the established SDP convention —
    # do not change without understanding the full SDP standalone mechanism.
    if not hasattr(builtins, 'SDP_standalone'):
        builtins.SDP_standalone = False
# <--

from lib.model.sdp.command import SDPCommandStr  # command class used by the commands.py examples
from lib.model.sdp.declarations import TransportRule  # set connection transport requirements
from lib.model.sdp.globals import CONN_NULL, CONN_NET_TCP_CLI, CONN_SER_ASYNC  # import all constants you need
from lib.model.smartdeviceplugin import SmartDevicePlugin, Standalone  # needed, obviously

if not SDP_standalone:
    try:
        from .webif import WebInterface  # can be removed if no webif is provided
    except ImportError:
        WebInterface = None


# depending on the complexity of the communication between the device and shng,
# this can be all plugin code needed to run (compare Viessmann plugin)


class SdpExample(SmartDevicePlugin):
    """Example class for SmartDevicePlugin with standalone functionality."""

    PLUGIN_VERSION = '0.1.0'  # adjust, must match version in plugin.yaml
    ALLOW_MULTIINSTANCE = True  # set to False if only one instance should run at a time

    # device defaults (see SmartDevicePlugin class attributes, TRANSPORTS in order of listing); remove unneeded ones
    TRANSPORTS = (
        TransportRule(CONN_NET_TCP_CLI, requires='host'),
        TransportRule(CONN_SER_ASYNC, requires='serialport'),
        TransportRule(CONN_NULL),
    )
    PROTOCOL = None  # protocol type or class wrapping the transport, e.g. PROTO_JSONRPC
    COMMAND_CLASS = SDPCommandStr  # command class or its name, e.g. SDPCommandParseStr; None: SDPCommand
    LINE_TERMINATED = True  # commands end with the terminator parameter, replies are read up to it
    JSON_MOVE_KEYS = ()  # JSON-RPC only: data_dict keys moved into the request params, e.g. ('playerid',)
    CUSTOM_TOKEN = None  # custom commands per device, e.g. CustomTokenSpec(index=1, token_re=..., reply_re=...)

    def _post_init(self):

        # you might want to do additional initialisations after
        # the plugins' __init__ method has finished
        # otherwise, remove this method

        self._my_property = 'foo'

        # runtime values for {PARAM:name} / {CUSTOM_PARAMn:name} templates in commands.py
        self.template_vars['CURRENT_ID'] = {}

        # needed for webif usage
        if not SDP_standalone:
            self._webif = WebInterface

    def on_connect(self, by=None):
        """callback if connection is made."""
        super().on_connect(by)
        self.logger.info('SdpExample plugin connected')

    def on_disconnect(self, by=None):
        """callback if connection is broken."""
        super().on_disconnect(by)
        self.logger.info('SdpExample plugin disconnected')

    # if you want to use the suspend/resume feature, you can overwrite these
    # methods and customize to your liking. If not, you can safely delete them
    # These are then called after suspending or resuming the plugin.

    def on_suspend(self):
        """called when suspend is enabled. Overwrite as needed"""
        self.logger.info('suspend enabled, on_suspend called')

    def on_resume(self):
        """called when suspend is disabled. Overwrite as needed"""
        self.logger.info('suspend disabled, plugin resumed, on_resume called')

    #
    # methods for standalone mode
    #

    def run_standalone(self):
        """
        runs in standalone mode after initialisation.

        Plugin class is loaded, instantiated and initialized; run() has not been
        called. Either call run() yourself, or work around it.
        """
        self.logger.warning(f'SdpExample device using connection class {type(self._connection).__name__}...')

        # now you can do what you like, you are working inside the active plugin class.
        # access to items, logics and the like is not possible, as shng is not running.
        # connection is initialized and can be opened.
        #
        # one common purpose of standalone mode is device discovery or test
        #


# needed to start operation in standalone mode
if __name__ == '__main__':
    s = Standalone(SdpExample, sys.argv[0])
