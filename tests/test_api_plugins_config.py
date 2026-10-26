"""
Tests for modules/admin/api_plugins.py's PluginsConfigController.read() - the plugin list of shngadmin's
plugin configuration page.
"""

import json
import shutil
import tempfile
import unittest

from . import common
from tests.mock.core import MockSmartHome

common.register_shng_log_levels()

from modules.admin.api_plugins import PluginsConfigController
from modules.admin.pullimpact import PendingReloads


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh
        self.pending_plugin_reloads = PendingReloads()


class TestReloadPending(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        shutil.copy(common.BASE + '/tests/resources/plugin_disabled_sections.yaml', self.tmpdir + '/plugin.yaml')
        self.sh = MockSmartHome()
        self.plugins = self.sh.with_plugins_from(self.tmpdir + '/plugin')
        self.module = _FakeModule(self.sh)
        self.controller = PluginsConfigController(self.module)
        self.controller.plugins = self.plugins

    def sections(self):
        return json.loads(self.controller.read())['plugin_config']

    def test_marks_the_sections_waiting_for_a_reload(self):
        self.module.pending_plugin_reloads.add(['lone_enabled'])

        sections = self.sections()

        self.assertTrue(sections['lone_enabled']['_reload_pending'])
        self.assertFalse(sections['lone_disabled']['_reload_pending'])

    def test_nothing_is_marked_by_default(self):
        self.assertFalse(any(section['_reload_pending'] for section in self.sections().values()))
