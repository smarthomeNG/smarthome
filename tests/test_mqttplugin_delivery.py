#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Delivery of one MQTT message to the items subscribed to its topic.

Runs the real mqtt module dispatch (modules/mqtt) together with the real
MqttPlugin base class (lib/model/mqttplugin.py). Only the broker client and
the items are stand-ins.
"""

import datetime
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from tests.mqtt_harness import Message, make_mqtt_module


class _RecordingItem:
    """Item stand-in: reports its type and records every value written to it."""

    def __init__(self, path, item_type):
        self.writes = []
        self.reads = 0
        self.reprs = 0
        self._type = item_type
        self.property = MagicMock(path=path, type=item_type)

    def type(self):
        return self._type

    @staticmethod
    def last_update():
        return datetime.datetime(2026, 1, 2, 3, 4, 5)

    last_change = last_update

    def __repr__(self):
        self.reprs += 1
        return f'<item {self.property.path}>'

    def __call__(self, value=None, caller=None, **kwargs):
        if value is None:
            self.reads += 1
            return self.writes[-1] if self.writes else None
        self.writes.append(value)


def _make_plugin(module):
    with patch('lib.model.mqttplugin.Modules') as mock_modules:
        mock_modules.get_instance.return_value.get_module.return_value = module
        from lib.model.mqttplugin import MqttPlugin

        return MqttPlugin()


class TestSeveralItemsOnOneTopic(unittest.TestCase):
    TOPIC = 'device/state'

    def _deliver(self, items, payload):
        module = make_mqtt_module()
        plugin = _make_plugin(module)
        for item in items:
            plugin.add_subscription(self.TOPIC, item.type(), None, item)
        plugin.start_subscriptions()

        module._on_mqtt_message(None, None, Message(self.TOPIC, payload))

    def test_each_item_is_updated_once_per_message(self):
        temperature = _RecordingItem('dev.temperature', 'num')
        humidity = _RecordingItem('dev.humidity', 'num')

        self._deliver([temperature, humidity], b'21.5')

        self.assertEqual(len(temperature.writes), 1)
        self.assertEqual(len(humidity.writes), 1)

    def test_each_item_receives_payload_cast_to_its_own_type(self):
        active = _RecordingItem('dev.active', 'bool')
        mode = _RecordingItem('dev.mode', 'str')

        self._deliver([active, mode], b'on')

        self.assertEqual(active.writes, [True])
        self.assertEqual(mode.writes, ['on'])


class TestDeliveryLoggingCost(unittest.TestCase):
    """Building log messages must not cost anything while the log levels are off."""

    TOPIC = 'device/state'

    def _subscribe(self, item, **subscription):
        module = make_mqtt_module()
        plugin = _make_plugin(module)
        plugin.add_subscription(self.TOPIC, item.type(), None, item, **subscription)
        plugin.start_subscriptions()
        return module, plugin

    def _set_level(self, level, *loggers):
        for logger in loggers:
            self.addCleanup(logger.setLevel, logger.level)
            logger.setLevel(level)

    def _deliver(self, module):
        module._on_mqtt_message(None, None, Message(self.TOPIC, b'{"temp": 21.5}'))

    def _deliver_with_level(self, item, level):
        module, plugin = self._subscribe(item, select='temp')
        self._set_level(level, module.logger, plugin.logger)
        self._deliver(module)

    def test_item_is_not_formatted_for_disabled_log_levels(self):
        item = _RecordingItem('dev.temperature', 'num')

        self._deliver_with_level(item, logging.WARNING)

        self.assertEqual(item.reprs, 0)

    def test_item_value_is_not_read_for_disabled_log_levels(self):
        item = _RecordingItem('dev.temperature', 'num')

        self._deliver_with_level(item, logging.WARNING)

        self.assertEqual(item.reads, 0)

    def test_delivery_is_still_logged_when_debug_is_enabled(self):
        item = _RecordingItem('dev.temperature', 'num')
        module, plugin = self._subscribe(item, select='temp')
        self._set_level(logging.DEBUG, module.logger, plugin.logger)

        with self.assertLogs(module.logger, level='DEBUG') as module_logs:
            with self.assertLogs(plugin.logger, level='DEBUG') as plugin_logs:
                self._deliver(module)

        self.assertTrue(any("for item 'dev.temperature'" in line for line in plugin_logs.output), plugin_logs.output)
        self.assertTrue(any('_callback_to_plugin' in line and 'device/state' in line for line in module_logs.output))


class TestSelectFromDictPayload(unittest.TestCase):
    TOPIC = 'device/state'

    def _deliver(self, subscriptions, payload):
        """Subscribe (item, select) pairs on one topic through the plugin, then deliver one message."""
        module = make_mqtt_module()
        plugin = _make_plugin(module)
        for item, select in subscriptions:
            plugin.add_subscription(self.TOPIC, item.type(), None, item, select=select)
        plugin.start_subscriptions()

        module._on_mqtt_message(None, None, Message(self.TOPIC, payload))

    def test_item_receives_the_selected_key_cast_to_its_type(self):
        temperature = _RecordingItem('dev.temperature', 'num')

        self._deliver([(temperature, 'temp')], b'{"temp": 21.5, "hum": 40}')

        self.assertEqual(temperature.writes, [21.5])

    def test_items_on_one_topic_each_receive_their_own_key_once(self):
        temperature = _RecordingItem('dev.temperature', 'num')
        humidity = _RecordingItem('dev.humidity', 'num')

        self._deliver([(temperature, 'temp'), (humidity, 'hum')], b'{"temp": 21.5, "hum": 40}')

        self.assertEqual(temperature.writes, [21.5])
        self.assertEqual(humidity.writes, [40])

    def test_key_missing_from_the_payload_leaves_the_item_untouched(self):
        temperature = _RecordingItem('dev.temperature', 'num')
        humidity = _RecordingItem('dev.humidity', 'num')

        self._deliver([(temperature, 'temp'), (humidity, 'hum')], b'{"temp": 21.5}')

        self.assertEqual(temperature.writes, [21.5])
        self.assertEqual(humidity.writes, [])

    def test_selected_bool_reaches_a_bool_item_as_bool(self):
        active = _RecordingItem('dev.active', 'bool')

        self._deliver([(active, 'state.on')], b'{"state": {"on": true}}')

        self.assertEqual(active.writes, [True])

    def test_selected_false_is_delivered(self):
        active = _RecordingItem('dev.active', 'bool')

        self._deliver([(active, 'on')], b'{"on": false}')

        self.assertEqual(active.writes, [False])

    def test_invalid_expression_is_logged_and_the_item_gets_no_values(self):
        temperature = _RecordingItem('dev.temperature', 'num')

        with self.assertLogs(level='ERROR'):
            self._deliver([(temperature, 'temp[')], b'{"temp": 21.5}')

        self.assertEqual(temperature.writes, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
