from . import common
import unittest

from tests.mock.core import MockSmartHome

common.register_shng_log_levels()


class TestPluginRetroactiveParseItem(unittest.TestCase):
    """
    Items can be loaded before a plugin is loaded (e.g. a plugin that is loaded
    at runtime, after the item tree already exists). A freshly loaded plugin
    must still see and parse those pre-existing items.
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

        # items already exist before the new plugin instance gets loaded.
        # itemnew's attribute is scoped to an instance name ('freshinstance')
        # that no already-loaded plugin instance uses, so any trigger it picks
        # up can only come from the plugin instance loaded within the test.
        self.sh.with_items_from(common.BASE + '/tests/resources/item_dumps_dynamic_load.yaml')

    def test_newly_loaded_plugin_sees_preexisting_items(self):
        itemnew = self.sh.items.return_item('itemnew')
        self.assertIsNotNone(itemnew)
        self.assertEqual(len(itemnew.get_method_triggers()), 0)

        # 'freshinstance' is a fresh configname/instance, never loaded before this
        # point — simulates a plugin loaded at runtime, after the item tree already
        # exists
        loaded = self.plugins.load_plugin('freshinstance', {'plugin_name': 'wol', 'instance': 'freshinstance'})
        self.assertTrue(loaded)

        self.assertEqual(len(itemnew.get_method_triggers()), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
