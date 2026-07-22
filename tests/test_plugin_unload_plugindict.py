from . import common
import unittest

from tests.mock.core import MockSmartHome


class TestUnloadPluginClearsPlugindict(unittest.TestCase):
    """
    Regression test for lib/plugin.py's unload_plugin(): its cleanup used
    getattr(self._plugindict, key, None) instead of self._plugindict.get(key,
    None). _plugindict is a plain dict, which has no such attribute, so the
    check was always False and the stale entry was never deleted - leaking a
    reference to the unloaded plugin, and (since load_plugin() only claims
    the plain-name key "if not already set") permanently pinning
    Plugins.get(name) to the *first-ever-loaded* instance across any number
    of later reloads.
    """

    CONF = {
        'plugin_name': 'wol',
        'class_name': 'GoodPlugin',
        'class_path': 'tests.qa_guard_good_plugin',
        'instance': 'inst1',
    }

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_unload_removes_plain_name_entry(self):
        self.plugins.load_plugin('cfg1', self.CONF)
        first = self.plugins._plugindict.get('qa_guard_good_plugin')
        self.assertIsNotNone(first)

        self.plugins.unload_plugin('cfg1')

        self.assertIsNone(
            self.plugins._plugindict.get('qa_guard_good_plugin'),
            'unload_plugin() must clear the plain-name plugindict entry',
        )

    def test_reload_updates_plain_name_lookup_to_the_new_instance(self):
        self.plugins.load_plugin('cfg1', self.CONF)
        first = self.plugins._plugindict.get('qa_guard_good_plugin')

        self.plugins.unload_plugin('cfg1')
        self.plugins.load_plugin('cfg1', self.CONF)

        second = self.plugins._plugindict.get('qa_guard_good_plugin')
        self.assertIsNotNone(second)
        self.assertIsNot(first, second, 'Plugins.get(name) must not keep returning the first-ever-loaded instance')
        self.assertIsNot(first, self.plugins.get('qa_guard_good_plugin'))
        self.assertIs(second, self.plugins.get('qa_guard_good_plugin'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
