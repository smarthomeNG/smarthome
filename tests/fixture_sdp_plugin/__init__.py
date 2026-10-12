#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Test-only SmartDevicePlugin fixtures."""

from lib.model.sdp.command import SDPCommandParseStr
from lib.model.sdp.declarations import TransportRule
from lib.model.sdp.globals import (
    CONN_NET_TCP_CLI,
    CONN_NET_TCP_REQ,
    CONN_NULL,
    CONN_SER_ASYNC,
    PLUGIN_ATTR_CONNECTION,
    PROTO_JSONRPC,
)
from lib.model.smartdeviceplugin import SmartDevicePlugin


class FixtureSDP(SmartDevicePlugin):
    """Plain SmartDevicePlugin with no device-specific code."""

    PLUGIN_VERSION = '1.0.0'


class FixtureSDPRules(SmartDevicePlugin):
    """Network or serial line-based device, network preferred."""

    PLUGIN_VERSION = '1.0.0'
    TRANSPORTS = (
        TransportRule(CONN_NET_TCP_CLI, requires='host'),
        TransportRule(CONN_SER_ASYNC, requires='serialport'),
    )
    COMMAND_CLASS = SDPCommandParseStr
    LINE_TERMINATED = True


class FixtureSDPNullFallback(FixtureSDPRules):
    """As FixtureSDPRules, falling back to the null connection."""

    TRANSPORTS = (*FixtureSDPRules.TRANSPORTS, TransportRule(CONN_NULL))


class FixtureSDPLegacyDefaults(FixtureSDPRules):
    """As FixtureSDPRules, selecting the TCP request connection in _set_device_defaults()."""

    def _set_device_defaults(self):
        self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_NET_TCP_REQ


class FixtureSDPProtocol(SmartDevicePlugin):
    """JSON-RPC device on a persistent network connection."""

    PLUGIN_VERSION = '1.0.0'
    TRANSPORTS = (TransportRule(CONN_NET_TCP_CLI, requires='host'),)
    PROTOCOL = PROTO_JSONRPC
    JSON_MOVE_KEYS = ('playerid',)


class FixtureSDPLegacyCallbacks(FixtureSDP):
    """Sets _use_callbacks."""

    def _set_device_defaults(self):
        self._use_callbacks = True
