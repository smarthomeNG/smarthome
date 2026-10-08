"""
Tests for modules/admin/api_plugin.py's PluginController.handle_plugin_lifecycle() -
the backend for shngadmin's load/unload/reload buttons.
"""

import shutil
import tempfile
import unittest
from unittest.mock import patch

from . import common
from tests.mock.core import MockSmartHome

common.register_shng_log_levels()

from modules.admin.api_plugin import PluginController

SECOND_SECTION = """
second:
    plugin_name: wol
    class_path: tests.fixture_reload_cycle_plugin
    class_name: CyclePlugin
    instance: second
"""


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh


class TestLoadReportsInstanceNameNotice(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        shutil.copy(common.BASE + '/tests/resources/plugin_disabled_sections.yaml', self.tmpdir + '/plugin.yaml')
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(self.tmpdir + '/plugin')
        self.controller = PluginController(_FakeModule(self.sh))
        self.controller.plugins = self.plugins
        # the fixture plugin has no run() method; starting its thread is not under test
        patcher = patch.object(self.plugins, 'start_plugin')
        patcher.start()
        self.addCleanup(patcher.stop)

    def _add_second_section(self):
        with open(self.tmpdir + '/plugin.yaml', 'a', encoding='utf8') as f:
            f.write(SECOND_SECTION)

    def test_load_of_second_instance_returns_warning(self):
        self._add_second_section()
        response = self.controller.handle_plugin_lifecycle('second', 'load')
        self.assertEqual(response['result'], 'ok')
        self.assertEqual(len(response['warnings']), 1)
        self.assertIn('lone_enabled', response['warnings'][0])

    def test_repeated_load_does_not_repeat_warning(self):
        self._add_second_section()
        self.controller.handle_plugin_lifecycle('second', 'load')
        self.controller.handle_plugin_lifecycle('second', 'unload')
        response = self.controller.handle_plugin_lifecycle('second', 'load')
        self.assertEqual(response, {'result': 'ok'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
