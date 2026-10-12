#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Typed data passed between SmartDevicePlugin, protocols and connections."""

import builtins

builtins.SDP_standalone = False

import unittest  # noqa: E402

from lib.model.sdp.carriers import ConnectionHooks, DeviceConfig  # noqa: E402
from lib.model.sdp.globals import (  # noqa: E402
    PLUGIN_ATTR_CB_ON_CONNECT,
    PLUGIN_ATTR_CB_ON_DISCONNECT,
    PLUGIN_ATTR_CB_SUSPEND,
)


class TestDeviceConfigFromParams(unittest.TestCase):
    def test_connection_params_become_fields(self):
        config = DeviceConfig.from_params({'host': 'tv', 'port': 9090, 'timeout': 3})

        self.assertEqual(('tv', 9090, 3), (config.host, config.port, config.timeout))

    def test_unset_fields_keep_base_defaults(self):
        config = DeviceConfig.from_params({})

        self.assertEqual((9600, 1.0, ''), (config.baudrate, config.timeout, config.serialport))

    def test_none_values_are_unset(self):
        config = DeviceConfig.from_params({'host': None})

        self.assertEqual('', config.host)
        self.assertNotIn('host', config.explicit)

    def test_string_values_are_sanitized(self):
        config = DeviceConfig.from_params({'port': '23', 'binary': 'true'})

        self.assertEqual((23, True), (config.port, config.binary))

    def test_json_move_keys_become_tuple(self):
        self.assertEqual(('playerid',), DeviceConfig.from_params({'json_move_keys': ['playerid']}).json_move_keys)

    def test_plugin_specific_params_go_to_extra(self):
        config = DeviceConfig.from_params({'viess_proto': 'KW', 'host': 'x'})

        self.assertEqual({'viess_proto': 'KW'}, dict(config.extra))

    def test_runtime_objects_are_not_config(self):
        config = DeviceConfig.from_params(
            {'plugin': object(), PLUGIN_ATTR_CB_ON_CONNECT: print, PLUGIN_ATTR_CB_SUSPEND: print}
        )

        self.assertEqual({}, dict(config.extra))

    def test_config_is_immutable(self):
        config = DeviceConfig.from_params({'viess_proto': 'KW'})

        with self.assertRaises(AttributeError):
            config.host = 'x'  # type: ignore[misc]
        with self.assertRaises(TypeError):
            config.extra['viess_proto'] = 'P300'  # type: ignore[index]


class TestDeviceConfigWithDefaults(unittest.TestCase):
    def test_defaults_fill_unset_fields(self):
        config = DeviceConfig.from_params({}).with_defaults({'port': 9090})

        self.assertEqual(9090, config.port)

    def test_set_fields_win_over_defaults(self):
        config = DeviceConfig.from_params({'port': 23}).with_defaults({'port': 9090})

        self.assertEqual(23, config.port)

    def test_defaults_count_as_set_for_later_defaults(self):
        config = DeviceConfig.from_params({}).with_defaults({'port': 9090}).with_defaults({'port': 1})

        self.assertEqual(9090, config.port)

    def test_unknown_default_raises(self):
        with self.assertRaises(TypeError):
            DeviceConfig.from_params({}).with_defaults({'hostname': 'x'})


class TestConnectionHooksFromParams(unittest.TestCase):
    def test_callbacks_are_taken_from_params(self):
        def on_data(by, data):
            pass

        def on_connect(by):
            pass

        def on_disconnect(by):
            pass

        hooks = ConnectionHooks.from_params(
            on_data, {PLUGIN_ATTR_CB_ON_CONNECT: on_connect, PLUGIN_ATTR_CB_ON_DISCONNECT: on_disconnect}
        )

        self.assertEqual((on_data, on_connect, on_disconnect), (hooks.on_data, hooks.on_connect, hooks.on_disconnect))

    def test_suspend_callback_becomes_abort_hook(self):
        calls = []

        hooks = ConnectionHooks.from_params(None, {PLUGIN_ATTR_CB_SUSPEND: lambda *a, **kw: calls.append((a, kw))})
        hooks.on_abort('conn')

        self.assertEqual([((True,), {'by': 'conn'})], calls)

    def test_missing_callbacks_are_none(self):
        hooks = ConnectionHooks.from_params(None, {})

        self.assertEqual(
            (None, None, None, None), (hooks.on_data, hooks.on_connect, hooks.on_disconnect, hooks.on_abort)
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
