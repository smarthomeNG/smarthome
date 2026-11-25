#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""PluginWrapper logs the development state of plugins that are to be removed, before trying to load them."""

import logging
import unittest
from types import SimpleNamespace

from tests import common

common.register_shng_log_levels()

from lib.constants import PLUGIN_STATES, PLUGIN_STATES_TO_BE_REMOVED
from lib.plugin import PluginWrapper


def wrap(state: str):
    """Create a PluginWrapper for a plugin that cannot be imported, with metadata state *state*."""
    meta = SimpleNamespace(get_string=lambda key: state if key == 'state' else '')
    return PluginWrapper(None, 'gone', 'Gone', 'plugins.not_existing_plugin', {}, '', meta, 'etc/plugin.yaml')


class TestPluginState(unittest.TestCase):
    def test_states(self):
        self.assertIn('defunct', PLUGIN_STATES)
        self.assertEqual({'deprecated', 'defunct'}, set(PLUGIN_STATES_TO_BE_REMOVED))

    def test_defunct_plugin_is_reported_before_the_import_fails(self):
        with self.assertLogs('lib.plugin', level=logging.WARNING) as logs:
            wrap('defunct')
        self.assertIn('defunct', logs.output[0])
        self.assertIn('removed', logs.output[0])

    def test_deprecated_plugin_is_reported(self):
        with self.assertLogs('lib.plugin', level=logging.WARNING) as logs:
            wrap('deprecated')
        self.assertIn('deprecated', logs.output[0])

    def test_ready_plugin_has_no_state_warning(self):
        with self.assertLogs('lib.plugin', level=logging.WARNING) as logs:
            wrap('ready')
        self.assertNotIn('ready', logs.output[0])


if __name__ == '__main__':
    unittest.main()
