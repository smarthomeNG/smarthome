#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib/model/mqttplugin.py's MqttPlugin._item_values.

MqttPlugin.__init__() used to never set self._item_values, so every plugin
that correctly calls super().__init__() (mqtt, shelly, tasmota,
zigbee2mqtt, ...) still ended up sharing the single class-level dict -
one plugin's item values leaking into another's web interface. __init__()
now sets an instance-level dict; the class-level default is intentionally
kept (not switched to a None sentinel) so plugins that skip
super().__init__() keep working exactly as before, see the TODO/FIXME
comment above the class attribute.
"""

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
