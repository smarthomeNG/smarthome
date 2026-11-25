from . import common
import unittest

from lib.metadata import Metadata

common.register_shng_log_levels()


class TestMetadataWithoutSmartHome(unittest.TestCase):
    """
    Regression test for lib/metadata.py's Metadata class working with
    sh=None - needed for standalone-mode plugin invocation (lib/model/
    smartdeviceplugin.py's Standalone class), which runs with no shng
    instance at all. Metadata must not assume self._sh is always a real
    SmartHome instance: resolving the metadata file's path via
    self._sh.get_basedir(), and checking for the http module in
    get_global_plugin_parameters(), must both tolerate sh=None.
    """

    def test_construction_does_not_require_sh(self):
        meta = Metadata(None, 'test_metadata_standalone', 'plugin', 'tests.resources.test_metadata_standalone')
        self.assertIsNotNone(meta.meta, 'plugin.yaml must still be found and parsed with sh=None')
        self.assertIn('required_param', meta.parameters)
        self.assertIn('optional_param', meta.parameters)

    def test_check_parameters_fills_in_defaults_without_sh(self):
        meta = Metadata(None, 'test_metadata_standalone', 'plugin', 'tests.resources.test_metadata_standalone')
        resolved, all_ok, _ = meta.check_parameters({'required_param': 'given'})

        self.assertTrue(all_ok)
        self.assertEqual(resolved['required_param'], 'given')
        self.assertEqual(resolved['optional_param'], 42, 'the declared default must be filled in')

    def test_check_parameters_reports_missing_mandatory_without_sh(self):
        meta = Metadata(None, 'test_metadata_standalone', 'plugin', 'tests.resources.test_metadata_standalone')
        _, all_ok, _ = meta.check_parameters({})

        self.assertFalse(all_ok, 'a missing mandatory parameter with no default must be reported, not silently ok')


if __name__ == '__main__':
    unittest.main(verbosity=2)
