"""
Tests for modules/admin/api_plugin.py's PluginController.handle_plugin_lifecycle() -
the backend for shngadmin's load/unload/reload buttons.
"""

import shutil
import tempfile
import unittest
import lib.shyaml as shyaml
from unittest.mock import patch

from . import common
from tests.mock.core import MockSmartHome

common.register_shng_log_levels()

from modules.admin.api_plugin import PluginController
from modules.admin.pullimpact import PendingReloads

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
        self.pending_plugin_reloads = PendingReloads()


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


class TestLoadActivatesDisabledSection(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        shutil.copy(common.BASE + '/tests/resources/plugin_disabled_sections.yaml', self.tmpdir + '/plugin.yaml')
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(self.tmpdir + '/plugin')
        self.controller = PluginController(_FakeModule(self.sh))
        self.controller.plugins = self.plugins
        patcher = patch.object(self.plugins, 'start_plugin')
        patcher.start()
        self.addCleanup(patcher.stop)

    def _section(self, name):
        return shyaml.yaml_load_roundtrip(self.tmpdir + '/plugin.yaml')[name]

    def test_load_of_disabled_section_enables_and_loads_it(self):
        response = self.controller.handle_plugin_lifecycle('lone_disabled', 'load')
        self.assertEqual(response['result'], 'ok')
        self.assertNotIn('plugin_enabled', self._section('lone_disabled'))
        self.assertIsNotNone(self.plugins.return_plugin('lone_disabled'))

    def test_enabling_keeps_the_rest_of_the_section(self):
        self.controller.handle_plugin_lifecycle('lone_disabled', 'load')
        self.assertEqual(self._section('lone_disabled')['class_name'], 'CyclePlugin')

    def test_load_of_enabled_section_leaves_yaml_untouched(self):
        with open(self.tmpdir + '/plugin.yaml', encoding='utf8') as f:
            before = f.read()
        self.controller.handle_plugin_lifecycle('lone_enabled', 'unload')
        response = self.controller.handle_plugin_lifecycle('lone_enabled', 'load')
        self.assertEqual(response, {'result': 'ok'})
        with open(self.tmpdir + '/plugin.yaml', encoding='utf8') as f:
            self.assertEqual(f.read(), before)

    def test_section_stays_enabled_when_loading_fails(self):
        with patch.object(self.plugins, 'load_plugin', return_value=False):
            response = self.controller.handle_plugin_lifecycle('lone_disabled', 'load')
        self.assertEqual(response['result'], 'error')
        self.assertNotIn('plugin_enabled', self._section('lone_disabled'))


if __name__ == '__main__':
    unittest.main(verbosity=2)


class TestLifecycleClearsPendingReload(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        shutil.copy(common.BASE + '/tests/resources/plugin_disabled_sections.yaml', self.tmpdir + '/plugin.yaml')
        with open(self.tmpdir + '/plugin.yaml', 'a', encoding='utf8') as f:
            f.write(SECOND_SECTION)
            f.write(SECOND_SECTION.replace('second', 'third'))
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(self.tmpdir + '/plugin')
        self.module = _FakeModule(self.sh)
        self.controller = PluginController(self.module)
        self.controller.plugins = self.plugins
        patcher = patch.object(self.plugins, 'start_plugin')
        patcher.start()
        self.addCleanup(patcher.stop)
        self.assertIsNotNone(self.plugins.return_plugin('second'))
        self.module.pending_plugin_reloads.add(['second', 'other'])

    def test_reload_clears_the_plugin_and_only_that_one(self):
        response = self.controller.handle_plugin_lifecycle('second', 'reload')

        self.assertEqual(response['result'], 'ok')
        self.assertEqual(self.module.pending_plugin_reloads.names(), ['other'])

    def test_reload_clears_every_instance_of_the_plugin_because_all_are_reloaded(self):
        self.module.pending_plugin_reloads.add(['third'])

        self.controller.handle_plugin_lifecycle('second', 'reload')

        self.assertEqual(self.module.pending_plugin_reloads.names(), ['other'])

    def test_a_failed_reload_keeps_the_plugin_pending(self):
        with patch.object(self.plugins, 'reload_plugin', return_value=False):
            response = self.controller.handle_plugin_lifecycle('second', 'reload')

        self.assertEqual(response['result'], 'error')
        self.assertEqual(self.module.pending_plugin_reloads.names(), ['other', 'second'])

    def test_unload_clears_the_plugin(self):
        self.controller.handle_plugin_lifecycle('second', 'unload')
        self.assertEqual(self.module.pending_plugin_reloads.names(), ['other'])
