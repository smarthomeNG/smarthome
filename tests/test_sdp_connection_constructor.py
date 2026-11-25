#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Constructor of SDP connections and protocols: configuration, hooks, scheduler, pre-2.0 signature."""

import builtins

builtins.SDP_standalone = False

import logging  # noqa: E402
import unittest  # noqa: E402

from lib.log import Logs  # noqa: E402
from lib.model.sdp.carriers import ConnectionHooks, DeviceConfig  # noqa: E402
from lib.model.sdp.connection import SDPConnection  # noqa: E402
from lib.model.sdp.globals import PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_SUSPEND  # noqa: E402
from lib.model.sdp.protocol import SDPProtocol, SDPProtocolJsonrpc, SDPProtocolResend  # noqa: E402

LOGGER = 'lib.model.sdp.connection'


def setUpModule():
    if not hasattr(logging.getLoggerClass(), 'dbghigh'):
        Logs(None).add_logging_level('DBGHIGH', 15)


class CountingConnection(SDPConnection):
    """Transport counting its instances."""

    instances: list['CountingConnection'] = []

    def _setup(self) -> None:
        CountingConnection.instances.append(self)

    def _on_abort(self) -> None:
        if self._hooks.on_abort:
            self._hooks.on_abort(str(self))


class PortDefaultConnection(SDPConnection):
    CONFIG_DEFAULTS = {'port': 4711}


class LegacySubclass(SDPConnection):
    def __init__(self, data_received_callback, name=None, **kwargs):
        super().__init__(data_received_callback, name, **kwargs)


class Scheduler:
    """Scheduler port keeping jobs by name."""

    def __init__(self) -> None:
        self.jobs: dict = {}

    def scheduler_add(self, name, obj, prio=3, cron=None, cycle=None, value=None, offset=None, next=None) -> None:
        self.jobs[name] = cycle

    def scheduler_get(self, name):
        return self.jobs.get(name)

    def scheduler_remove(self, name) -> None:
        self.jobs.pop(name, None)


def config(**params) -> DeviceConfig:
    return DeviceConfig.from_params(params)


class TestConstructor(unittest.TestCase):
    def setUp(self):
        self.events: list = []
        self.hooks = ConnectionHooks(
            on_data=lambda by, data, command=None: self.events.append(('data', data)),
            on_connect=lambda by: self.events.append(('connect', by)),
            on_disconnect=lambda by: self.events.append(('disconnect', by)),
        )

    def test_config_is_kept(self):
        conn = SDPConnection(config(host='tv'), self.hooks, name='plg')

        self.assertEqual('tv', conn._config.host)

    def test_hooks_receive_events(self):
        conn = SDPConnection(config(), self.hooks)

        conn.on_connect('x')
        conn.on_data_received('x', 'reply')
        conn.on_disconnect('x')

        self.assertEqual([('connect', 'x'), ('data', 'reply'), ('disconnect', 'x')], self.events)

    def test_class_defaults_fill_unset_settings(self):
        self.assertEqual(4711, PortDefaultConnection(config(), self.hooks)._config.port)
        self.assertEqual(23, PortDefaultConnection(config(port=23), self.hooks)._config.port)

    def test_name_in_place_of_hooks_raises(self):
        with self.assertRaises(TypeError):
            SDPConnection(config(), 'plg')

    def test_unexpected_keyword_raises(self):
        with self.assertRaises(TypeError):
            SDPConnection(config(), self.hooks, host='tv')


class TestLegacySignature(unittest.TestCase):
    def setUp(self):
        SDPConnection._warned_legacy.clear()

    def test_legacy_call_is_converted(self):
        connected = []

        with self.assertLogs(LOGGER, 'WARNING'):
            conn = SDPConnection(None, name='plg', host='tv', **{PLUGIN_ATTR_CB_ON_CONNECT: connected.append})
        conn.on_connect('x')

        self.assertEqual(('tv', 'plg', ['x']), (conn._config.host, conn._name, connected))

    def test_legacy_positional_name(self):
        with self.assertLogs(LOGGER, 'WARNING'):
            conn = SDPConnection(None, 'plg')

        self.assertEqual('plg', conn._name)

    def test_legacy_plugin_becomes_scheduler(self):
        scheduler = Scheduler()

        with self.assertLogs(LOGGER, 'WARNING'):
            conn = SDPConnection(None, plugin=scheduler)

        self.assertIs(scheduler, conn._scheduler)

    def test_legacy_subclass_constructor_works(self):
        with self.assertLogs(LOGGER, 'WARNING'):
            conn = LegacySubclass(None, 'plg', port=23)

        self.assertEqual(23, conn._config.port)

    def test_warning_once_per_class(self):
        with self.assertLogs(LOGGER, 'WARNING') as logs:
            SDPConnection(None)
            SDPConnection(None)

        self.assertEqual(1, len(logs.records))


class TestProtocolTransport(unittest.TestCase):
    def setUp(self):
        CountingConnection.instances.clear()
        self.events: list = []
        self.hooks = ConnectionHooks(
            on_data=lambda by, data, command=None: self.events.append(('data', data)),
            on_connect=lambda by: self.events.append(('connect', by)),
            on_abort=lambda by: self.events.append(('abort', by)),
        )

    def test_transport_gets_protocol_config(self):
        proto = SDPProtocol(config(conn_type=CountingConnection, host='tv'), self.hooks, name='plg')

        transport = proto._connection
        self.assertIsInstance(transport, CountingConnection)
        self.assertEqual(('tv', 'plg'), (transport._config.host, transport._name))

    def test_transport_events_reach_protocol_hooks(self):
        proto = SDPProtocol(config(conn_type=CountingConnection), self.hooks)

        proto._connection.on_connect('t')
        proto._connection.on_data_received('t', 'reply')
        proto._connection._on_abort()

        self.assertEqual([('connect', 't'), ('data', 'reply'), ('abort', 'CountingConnection')], self.events)

    def test_jsonrpc_builds_one_transport(self):
        SDPProtocolJsonrpc(config(conn_type=CountingConnection), self.hooks)

        self.assertEqual(1, len(CountingConnection.instances))

    def test_jsonrpc_defaults_reach_transport(self):
        proto = SDPProtocolJsonrpc(config(conn_type=CountingConnection), self.hooks)

        self.assertEqual(9090, proto._connection._config.port)

    def test_jsonrpc_uses_send_timeout(self):
        proto = SDPProtocolJsonrpc(config(conn_type=CountingConnection, send_timeout=12), self.hooks)

        self.assertEqual(6, proto._check_stale_cycle)

    def test_resend_schedules_on_scheduler_port(self):
        scheduler = Scheduler()
        proto = SDPProtocolResend(
            config(conn_type=CountingConnection, send_retries=2, send_retries_cycle=7), self.hooks, scheduler
        )

        proto.on_connect('t')

        self.assertEqual({'resend': 7}, scheduler.jobs)

    def test_legacy_protocol_call_wires_suspend(self):
        SDPConnection._warned_legacy.clear()
        suspended = []

        with self.assertLogs(LOGGER, 'WARNING'):
            proto = SDPProtocol(
                None, conn_type=CountingConnection, **{PLUGIN_ATTR_CB_SUSPEND: lambda on, by: suspended.append(by)}
            )
        proto._connection._on_abort()

        self.assertEqual(['CountingConnection'], suspended)


if __name__ == '__main__':
    unittest.main(verbosity=2)
