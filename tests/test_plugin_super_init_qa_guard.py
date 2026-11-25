from . import common
import unittest

from tests.mock.core import MockSmartHome

common.register_shng_log_levels()


class TestSuperInitQaGuard(unittest.TestCase):
    """
    Regression test for the QA guard in lib/plugin.py's PluginWrapper: a
    plugin whose __init__() skips super().__init__() never gets the
    _smartplugin_super_init_done sentinel set by SmartPlugin.__init__(), so
    PluginWrapper must log a warning naming it. A well-behaved plugin must
    not trigger the warning. Enforcement (_init_complete = False) is
    deliberately still commented out in lib/plugin.py, so both plugins must
    still load successfully.
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_well_behaved_plugin_does_not_warn(self):
        with self.assertNoLogs('lib.plugin', level='WARNING'):
            loaded = self.plugins.load_plugin(
                'goodtest',
                {
                    'plugin_name': 'wol',
                    'class_name': 'GoodPlugin',
                    'class_path': 'tests.qa_guard_good_plugin',
                    'instance': 'goodtest',
                },
            )
        self.assertTrue(loaded)

    def test_plugin_skipping_super_init_warns_by_name(self):
        with self.assertLogs('lib.plugin', level='WARNING') as cm:
            loaded = self.plugins.load_plugin(
                'badtest',
                {
                    'plugin_name': 'wol',
                    'class_name': 'BadPlugin',
                    'class_path': 'tests.qa_guard_bad_plugin',
                    'instance': 'badtest',
                },
            )
        self.assertTrue(loaded)
        self.assertTrue(any('super().__init__()' in msg and 'qa_guard_bad_plugin' in msg for msg in cm.output))


if __name__ == '__main__':
    unittest.main(verbosity=2)
