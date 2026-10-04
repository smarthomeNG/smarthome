#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib/model/mqttplugin.py's MqttPlugin._item_values.

MqttPlugin.__init__() must set an instance-level self._item_values, or
every plugin that correctly calls super().__init__() (mqtt, shelly,
tasmota, zigbee2mqtt, ...) ends up sharing the single class-level dict -
one plugin's item values leaking into another's web interface. The
class-level default is intentionally kept (not a None sentinel) so plugins
that skip super().__init__() keep working, see the TODO/FIXME comment
above the class attribute.
"""

import datetime
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()


class TestMqttPluginItemValuesIsInstanceSpecific(unittest.TestCase):
    def _make_plugin(self):
        with patch('lib.model.mqttplugin.Modules') as mock_modules:
            mock_modules.get_instance.return_value.get_module.return_value = MagicMock()
            from lib.model.mqttplugin import MqttPlugin

            return MqttPlugin()

    def test_two_instances_do_not_share_item_values(self):
        from lib.model.mqttplugin import MqttPlugin

        p1 = self._make_plugin()
        p2 = self._make_plugin()

        self.assertIsNot(p1._item_values, p2._item_values)
        self.assertIsNot(p1._item_values, MqttPlugin._item_values)

    def test_writing_to_one_instance_does_not_affect_another(self):
        p1 = self._make_plugin()
        p2 = self._make_plugin()

        p1._item_values['some.item'] = {'value': 42}

        self.assertNotIn('some.item', p2._item_values)


class _StubItem:
    """Minimal item exposing what _update_item_values() reads."""

    class property:
        path = 'some.item'

    @staticmethod
    def last_update():
        return datetime.datetime(2026, 1, 2, 3, 4, 5)

    last_change = last_update


class TestMqttPluginItemValuesJsonPayload(unittest.TestCase):
    """Dict/list payloads must reach the web interface as JSON text, not as JSON objects (-> '[object Object]')."""

    def _stored_value(self, payload):
        with patch('lib.model.mqttplugin.Modules') as mock_modules:
            mock_modules.get_instance.return_value.get_module.return_value = MagicMock()
            from lib.model.mqttplugin import MqttPlugin

            plugin = MqttPlugin()
        plugin._update_item_values(_StubItem, payload)
        return plugin._item_values['some.item']['value']

    def test_dict_payload_is_stored_as_json_text(self):
        payload = {'temp': 21.5, 'unit': 'C'}
        value = self._stored_value(payload)

        self.assertIsInstance(value, str)
        self.assertEqual(json.loads(value), payload)

    def test_list_payload_is_stored_as_json_text(self):
        payload = [1, 'two', {'three': 3}]
        value = self._stored_value(payload)

        self.assertIsInstance(value, str)
        self.assertEqual(json.loads(value), payload)

    def test_scalar_payloads_keep_their_type(self):
        self.assertEqual(self._stored_value(42), 42)
        self.assertEqual(self._stored_value('on'), 'on')
        self.assertEqual(self._stored_value(True), 'True')


if __name__ == '__main__':
    unittest.main(verbosity=2)
