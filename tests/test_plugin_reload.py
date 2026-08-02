from . import common
import os
import shutil
import tempfile
import threading
import unittest

from tests.mock.core import MockSmartHome

common.register_shng_log_levels()


class TestGetPluginthreadEarlyOrder(unittest.TestCase):
    """
    Regression test for lib/plugin.py's get_pluginthread(): plugins loaded at
    runtime (i.e. any load_plugin() call outside the initial bulk __init__
    loop) with startorder: early/late in their plugin.yaml get appended to
    Plugins.threads_early/threads_late instead of Plugins._threads. Those two
    lists are only ever merged into _threads once, inside __init__ - never
    again afterward. get_pluginthread() only searched _threads, so it could
    never find such a plugin once loaded post-startup, which in turn broke
    unload_plugin() (self._threads.remove(None) raises ValueError, silently
    caught, unload_plugin returns False). Real plugins hit by this:
    plugins/database, plugins/influxdb, plugins/influxdb2 (all
    startorder: early).
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_runtime_loaded_early_order_plugin_is_findable(self):
        loaded = self.plugins.load_plugin(
            'earlytest', {'class_path': 'tests.fixture_earlyorder_plugin', 'class_name': 'EarlyOrderPlugin'}
        )
        self.assertTrue(loaded)

        self.assertIsNotNone(
            self.plugins.get_pluginthread('earlytest'),
            'get_pluginthread() must find a startorder: early plugin loaded at runtime',
        )

    def test_runtime_loaded_early_order_plugin_can_be_unloaded(self):
        loaded = self.plugins.load_plugin(
            'earlytest', {'class_path': 'tests.fixture_earlyorder_plugin', 'class_name': 'EarlyOrderPlugin'}
        )
        self.assertTrue(loaded)

        self.assertTrue(
            self.plugins.unload_plugin('earlytest'),
            'unload_plugin() must succeed for a startorder: early plugin loaded at runtime',
        )


class TestStartPlugin(unittest.TestCase):
    """
    Plugins.start_plugin() must start an already-loaded plugin via its own
    dedicated PluginWrapper thread (thread.start()), the same path bulk
    startup uses (Plugins.start()) - not by calling myplugin.run() directly
    on the caller's thread, which is what reload_plugin() and the admin
    API's 'load' action used to do.
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin')

    def test_start_plugin_runs_on_dedicated_thread_not_caller(self):
        loaded = self.plugins.load_plugin(
            'threadedtest',
            {
                'plugin_name': 'wol',
                'class_name': 'ThreadedRunPlugin',
                'class_path': 'tests.threaded_run_plugin',
                'instance': 'threadedtest',
            },
        )
        self.assertTrue(loaded)
        myplugin = self.plugins.return_plugin('threadedtest')
        self.assertFalse(myplugin.alive)

        result = self.plugins.start_plugin('threadedtest')
        self.assertTrue(result)

        thread = self.plugins.get_pluginthread('threadedtest')
        thread.join(timeout=2)

        self.assertTrue(myplugin.alive)
        self.assertIsNotNone(myplugin.run_thread, 'run() must have executed')
        self.assertNotEqual(
            myplugin.run_thread, threading.current_thread(), 'run() must not execute synchronously on the caller thread'
        )

    def test_start_plugin_returns_false_for_unknown_configname(self):
        self.assertFalse(self.plugins.start_plugin('doesnotexist'))

    def test_start_plugin_does_not_crash_once_thread_has_already_finished(self):
        # ThreadedRunPlugin.run() returns immediately, so its PluginWrapper
        # thread naturally finishes right after start() - is_alive() goes
        # back to False, same as a thread that was *never* started.
        # threading.Thread.start() may only ever be called once per thread
        # object regardless of is_alive() - calling it a second time raises
        # RuntimeError, which start_plugin() must not let escape.
        loaded = self.plugins.load_plugin(
            'threadedtest2',
            {
                'plugin_name': 'wol',
                'class_name': 'ThreadedRunPlugin',
                'class_path': 'tests.threaded_run_plugin',
                'instance': 'threadedtest2',
            },
        )
        self.assertTrue(loaded)
        self.assertTrue(self.plugins.start_plugin('threadedtest2'))

        thread = self.plugins.get_pluginthread('threadedtest2')
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive(), 'fixture plugin run() should have already returned')

        self.assertFalse(self.plugins.start_plugin('threadedtest2'))


class TestReloadPluginReturnValues(unittest.TestCase):
    """
    reload_plugin() used to always return True, even when unload_plugin() or
    load_plugin() (steps it calls internally) failed - reporting success to
    callers (e.g. the admin API) while actually leaving the plugin unloaded,
    or - worse, when unload_plugin() itself failed - leaving a second, fresh
    instance registered alongside a still-present, half-unloaded original
    under the same configname.

    Uses tests/resources/plugin_reload.yaml, a dedicated fixture (not the
    shared tests/resources/plugin.yaml), because reload_plugin() re-reads
    its config from disk on every call - the configname under test has to
    exist there, not just in an in-memory dict.
    """

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin_reload')

    def test_reload_returns_false_and_leaves_original_untouched_when_unload_fails(self):
        loaded = self.plugins.load_plugin(
            'failingstop',
            {
                'plugin_name': 'wol',
                'class_name': 'FailingStopPlugin',
                'class_path': 'tests.reload_failing_stop_plugin',
                'instance': 'failingstop',
            },
        )
        self.assertTrue(loaded)
        original = self.plugins.return_plugin('failingstop')
        original.alive = True  # simulate a currently-running plugin, same flag unload_plugin() itself checks

        result = self.plugins.reload_plugin('failingstop')

        self.assertFalse(result, 'reload_plugin() must report failure when unload_plugin() fails')
        self.assertIs(
            self.plugins.return_plugin('failingstop'),
            original,
            'the original instance must still be registered, untouched, after a failed unload',
        )

    def test_reload_returns_false_when_load_fails_after_successful_unload(self):
        # reload_plugin() re-reads its config from disk on every call, so
        # toggling plugin_enabled between the initial load and the reload
        # call is a real, on-disk config change - exactly what re-reading
        # on every reload is meant to pick up - not a mocked failure.
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)
        conf_path = os.path.join(tmpdir, 'plugin_reload_dynamic')

        def write_conf(enabled):
            with open(conf_path + '.yaml', 'w') as f:
                f.write(
                    'gooddisable:\n'
                    '    plugin_name: wol\n'
                    '    class_name: GoodPlugin\n'
                    '    class_path: tests.qa_guard_good_plugin\n'
                    '    instance: gooddisable\n'
                    f'    plugin_enabled: {enabled}\n'
                )

        # with_plugins_from() bulk-loads every section present in conf_path
        # at construction time (same as etc/plugin.yaml at real startup) - no
        # separate load_plugin() call needed/wanted here, that would just
        # register a second, duplicate instance under the same configname.
        write_conf(True)
        sh2 = MockSmartHome()
        plugins2 = sh2.with_plugins_from(conf_path)
        self.assertIsNotNone(plugins2.return_plugin('gooddisable'))

        write_conf(False)
        result = plugins2.reload_plugin('gooddisable')

        self.assertFalse(result, 'reload_plugin() must report failure when load_plugin() fails on reread config')
        self.assertIsNone(
            plugins2.return_plugin('gooddisable'),
            'a disabled plugin must not still be registered after a failed reload',
        )


class TestReloadSubmodules(unittest.TestCase):
    """
    reload_plugin() only ever reload()-ed the plugin's own top-level module
    (mymodule = myplugin.__module__). Real plugins commonly import their own
    sibling submodules (e.g. hue2's __init__.py does `from .webif import
    WebInterface`) - reload()-ing only the top-level module re-executes
    `from .helper import get_message`, but since tests.fixture_reload_
    submodule_plugin.helper is still cached in sys.modules from the original
    load, that import just rebinds to the same, unchanged function - code
    edits to the submodule never take effect.
    """

    HELPER_PATH = os.path.join(common.BASE, 'tests', 'fixture_reload_submodule_plugin', 'helper.py')

    def setUp(self):
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(common.BASE + '/tests/resources/plugin_reload')
        with open(self.HELPER_PATH) as f:
            original_source = f.read()
        self.addCleanup(self._write_helper, original_source)

    def _write_helper(self, source):
        with open(self.HELPER_PATH, 'w') as f:
            f.write(source)

    def test_reload_picks_up_changes_in_a_locally_imported_submodule(self):
        myplugin = self.plugins.return_plugin('submodulereload')
        self.assertEqual(myplugin.get_message(), 'original')

        self._write_helper("def get_message():\n    return 'updated'\n")

        result = self.plugins.reload_plugin('submodulereload')
        self.assertTrue(result)

        myplugin = self.plugins.return_plugin('submodulereload')
        self.assertEqual(
            myplugin.get_message(),
            'updated',
            'reload_plugin() must pick up code changes in a locally-imported submodule, not just the top-level module',
        )

    LEAF_PATH = os.path.join(common.BASE, 'tests', 'fixture_reload_submodule_plugin', 'leaf_dependency.py')

    def test_reload_order_lets_a_dependent_submodule_see_a_deeper_submodules_changes(self):
        # dependent_formatter.py imports from leaf_dependency.py. If
        # dependent_formatter reloads before leaf_dependency does, its
        # `from .leaf_dependency import get_value` line rebinds to a still-
        # stale get_value - the edit below would then never surface through
        # format_value(), even though leaf_dependency.py itself did reload.
        with open(self.LEAF_PATH) as f:
            original_source = f.read()
        self.addCleanup(lambda: open(self.LEAF_PATH, 'w').write(original_source))

        myplugin = self.plugins.return_plugin('submodulereload')
        self.assertEqual(myplugin.get_formatted_value(), '[original]')

        with open(self.LEAF_PATH, 'w') as f:
            f.write("def get_value():\n    return 'updated'\n")

        result = self.plugins.reload_plugin('submodulereload')
        self.assertTrue(result)

        myplugin = self.plugins.return_plugin('submodulereload')
        self.assertEqual(
            myplugin.get_formatted_value(),
            '[updated]',
            'reload_plugin() must reload a dependency submodule before the sibling that imports from it',
        )

    def test_reload_does_not_raise_on_a_circular_import_among_submodules(self):
        # module_a.py and module_b.py (tests/fixture_reload_cycle_plugin/)
        # import from each other - graphlib.TopologicalSorter has no valid
        # order for a true cycle and raises CycleError internally;
        # reload_plugin() must not let that escape, and must still leave a
        # working plugin behind (falls back to reloading the top-level
        # module only, same as the pre-submodule-aware behavior).
        myplugin = self.plugins.return_plugin('cyclereload')
        self.assertEqual(myplugin.get_cycle_value(), 'a+b(of tests.fixture_reload_cycle_plugin.module_a)')

        result = self.plugins.reload_plugin('cyclereload')

        self.assertTrue(result, 'reload_plugin() must not fail just because its submodules have a circular import')
        myplugin = self.plugins.return_plugin('cyclereload')
        self.assertEqual(
            myplugin.get_cycle_value(),
            'a+b(of tests.fixture_reload_cycle_plugin.module_a)',
            'the plugin must still be functional after falling back',
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
