#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Test-only SmartDevicePlugin fixture; runs on the framework's null connection."""

from lib.model.smartdeviceplugin import SmartDevicePlugin


class FixtureSDP(SmartDevicePlugin):
    """Plain SmartDevicePlugin with no device-specific code."""

    PLUGIN_VERSION = '1.0.0'

    def _set_device_defaults(self):
        self._use_callbacks = True
