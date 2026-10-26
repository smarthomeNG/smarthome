from . import common
import unittest

from tests.mock.core import MockSmartHome

common.register_shng_log_levels()


class TestClassicPluginRejected(unittest.TestCase):
    """A plugin class that is not derived from SmartPlugin is not loaded."""

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_plugin_not_derived_from_smartplugin_is_not_loaded(self):
        before = len(list(self.plugins))

        with self.assertLogs('lib.plugin', level='ERROR') as cm:
            loaded = self.plugins.load_plugin(
                'classictest',
                {'plugin_name': 'wol', 'class_name': 'ClassicPlugin', 'class_path': 'tests.classic_style_plugin'},
            )

        self.assertFalse(loaded)
        self.assertEqual(before, len(list(self.plugins)))
        self.assertTrue(any('SmartPlugin' in msg and 'classictest' in msg for msg in cm.output), cm.output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
