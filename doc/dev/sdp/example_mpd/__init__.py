#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  This file is part of SmartHomeNG
#
#  MPD tutorial example for SmartDevicePlugin
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

import builtins
import os
import sys

if __name__ == '__main__':
    builtins.SDP_standalone = True

    class SmartPlugin:
        pass

    class SmartPluginWebIf:
        pass

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-5])
    sys.path.insert(0, BASE)

elif not hasattr(builtins, 'SDP_standalone'):
    builtins.SDP_standalone = False

from lib.model.sdp.command import SDPCommandParseStr
from lib.model.sdp.declarations import TransportRule
from lib.model.sdp.globals import CONN_NET_TCP_CLI
from lib.model.smartdeviceplugin import SmartDevicePlugin, Standalone


class MpdSdp(SmartDevicePlugin):
    """Music Player Daemon, controlled via its line protocol."""

    PLUGIN_VERSION = '0.1.0'
    ALLOW_MULTIINSTANCE = True

    TRANSPORTS = (TransportRule(CONN_NET_TCP_CLI, requires='host'),)
    COMMAND_CLASS = SDPCommandParseStr
    LINE_TERMINATED = True

    #: commands which run on a truthy item value only
    ACTIONS = ('control.play', 'control.stop', 'control.next', 'control.previous')

    def _do_before_send(self, command, value, kwargs):
        """Drop falsy writes to action commands."""
        if command in self.ACTIONS and not value:
            return False, True
        return True, True

    def _transform_received_data(self, data):
        """Log MPD error lines; they match no reply_pattern and are discarded afterwards."""
        if isinstance(data, str) and data.startswith('ACK'):
            self.logger.warning(f'MPD reports error: {data}')
        return data


if __name__ == '__main__':
    s = Standalone(MpdSdp, sys.argv[0])
