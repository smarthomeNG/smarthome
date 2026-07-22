#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  SmartDevicePlugin for handling devices via network or serial connection.
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

"""INCOMPLETE STUB -- not a working webif, not a copy-paste example.

This was never finished, and it deliberately no longer ships a
templates/index.html: a webif's template has to be written against the
specific item/data/device structure of the plugin it belongs to, none of
which is known at this (generic SDP) level -- there is no single HTML
layout that would be correct for every SmartDevicePlugin. So there is no
generic *example* to provide here, only a (currently unwritten) generic
*Python-side* interface: helpers that introspect an SDPCommands/SDPConnection
instance generically (connection status, the list of defined commands and
their read/write/item_type, currently bound items) without assuming any
particular device's item layout. That interface doesn't exist yet.

If you're writing a plugin's webif, don't start from this file -- write
your own WebInterface class and template against your plugin's actual
data, the same way dev/sample_smartdevice_plugin's plugin code is written
against the current single-connection SmartDevicePlugin API (self._connection,
self._commands), not the multi-device model this stub predates.
"""

from lib.item import Items
from lib.model.smartplugin import SmartPluginWebIf


class WebInterface(SmartPluginWebIf):
    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.items = Items.get_instance()

        self.tplenv = self.init_template_environment()

    # no index()/submit()/get_data_html() here on purpose -- see the module
    # docstring. A real plugin needs its own handlers and its own template.
