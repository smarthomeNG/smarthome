from . import common
import unittest
from unittest.mock import patch

from lib.plugin import Plugins
from tests.mock.core import MockSmartHome

common.register_shng_log_levels()

OVERRIDE = {
    'plugin_name': 'wol',
    'class_name': 'GoodPlugin',
    'class_path': 'tests.qa_guard_good_plugin',
    'instance': 'overridetest',
}


class TestClassOverride(unittest.TestCase):
    """class_name/class_path in plugin.yaml are honoured only while Plugins._allow_class_override is set (tests)."""

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_override_is_ignored_with_a_warning_by_default(self):
        broken = dict(OVERRIDE, class_path='tests.module_that_does_not_exist')

        with patch.object(Plugins, '_allow_class_override', False):
            with self.assertLogs('lib.plugin', level='WARNING') as cm:
                loaded = self.plugins.load_plugin('overridetest', broken)

        self.assertTrue(loaded)
        self.assertTrue(any('class_path' in msg and 'overridetest' in msg for msg in cm.output), cm.output)
        self.assertEqual('WakeOnLan', self.plugins._threads[-1].plugin.__class__.__name__)

    def test_section_without_plugin_name_is_not_loaded_without_override(self):
        conf = {'class_name': 'GoodPlugin', 'class_path': 'tests.qa_guard_good_plugin'}

        with patch.object(Plugins, '_allow_class_override', False):
            with self.assertLogs('lib.plugin', level='ERROR') as cm:
                loaded = self.plugins.load_plugin('noname', conf)

        self.assertFalse(loaded)
        self.assertTrue(any('plugin_name' in msg for msg in cm.output), cm.output)

    def test_override_is_used_when_allowed(self):
        with patch.object(Plugins, '_allow_class_override', True):
            loaded = self.plugins.load_plugin('overridetest', dict(OVERRIDE))

        self.assertTrue(loaded)
        self.assertEqual('GoodPlugin', self.plugins._threads[-1].plugin.__class__.__name__)


if __name__ == '__main__':
    unittest.main(verbosity=2)
