from . import common
import os
import shutil
import tempfile
import unittest

from tests.mock.core import MockSmartHome

common.register_shng_log_levels()


class TestInstanceCountIgnoresDisabledSections(unittest.TestCase):
    """
    A plugin section with ``plugin_enabled: false`` is never loaded, so it must not
    count as a second use of its plugin_name: a lone enabled section next to a
    disabled one keeps the single-instance default (empty instance name).
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin_disabled_sections')

    def test_lone_enabled_section_gets_default_instance(self):
        thread = self.plugins.get_pluginthread('lone_enabled')
        self.assertIsNotNone(thread)
        self.assertEqual(thread.plugin.get_instance_name(), '')

    def test_disabled_section_is_not_loaded(self):
        self.assertIsNone(self.plugins.get_pluginthread('lone_disabled'))


SECOND_SECTION = """
second:
    plugin_name: wol
    class_path: tests.fixture_reload_cycle_plugin
    class_name: CyclePlugin
    instance: second
"""


class TestRefreshPluginConfig(unittest.TestCase):
    """
    Plugins loaded at runtime (admin UI) must see the current plugin.yaml: the usage
    count is refreshed from disk, and a notice is raised when a count rising above 1
    leaves an already loaded instance with the default (unnamed) instance.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        shutil.copy(common.BASE + '/tests/resources/plugin_disabled_sections.yaml', self.tmpdir + '/plugin.yaml')
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(self.tmpdir + '/plugin')

    def _add_second_section(self):
        with open(self.tmpdir + '/plugin.yaml', 'a', encoding='utf8') as f:
            f.write(SECOND_SECTION)

    def test_refresh_counts_section_added_after_startup(self):
        self._add_second_section()
        result = self.plugins.refresh_plugin_config()
        self.assertIn('second', result.conf)
        self.assertEqual(self.plugins._plugins_count, {'wol': 2})

    def test_runtime_loaded_second_section_gets_own_instance(self):
        self._add_second_section()
        conf = self.plugins.refresh_plugin_config().conf
        self.assertTrue(self.plugins.load_plugin('second', conf['second']))
        self.assertEqual(self.plugins.get_pluginthread('second').plugin.get_instance_name(), 'second')

    def test_notice_when_loaded_instance_keeps_default_name(self):
        self._add_second_section()
        with self.assertLogs('lib.plugin', level='WARNING') as logs:
            result = self.plugins.refresh_plugin_config()
        self.assertEqual(len(result.notices), 1)
        self.assertIn('lone_enabled', result.notices[0])
        self.assertIn(result.notices[0], '\n'.join(logs.output))

    def test_notice_is_raised_only_once(self):
        self._add_second_section()
        self.plugins.refresh_plugin_config()
        self.assertEqual(self.plugins.refresh_plugin_config().notices, [])

    def test_no_notice_without_count_change(self):
        self.assertEqual(self.plugins.refresh_plugin_config().notices, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
