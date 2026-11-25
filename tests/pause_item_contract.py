#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Reusable test contract for the ``pause_item`` handling of real plugins.

A plugin test module combines :class:`PauseItemContract` with ``unittest.TestCase`` and names the plugin
class and its parameters. The plugin is loaded through the real plugin loader; its ``stop()`` and
``run()`` are replaced by recorders, so no network or device is touched, while ``parse_item()`` and
``update_item()`` run unchanged.
"""

from __future__ import annotations

import tempfile
from typing import Any, ClassVar

from lib.item.item import Item
from lib.model.smartplugin import SmartPlugin
from tests.sdp_harness import PluginRig, load_plugin

PAUSE_ITEM_PATH = 'dev.pause'
PAUSE_ITEMS_YAML = """
dev:
    pause:
        type: bool
"""
SECOND_SECTION = 'plg2'


class PauseItemContract:
    """
    Mixin with the pause item tests; combine with ``unittest.TestCase``.

    Subclasses set :attr:`CLASS_PATH`, :attr:`CLASS_NAME` and :attr:`PARAMS`. ``PARAMS`` must not contain
    ``pause_item``; the contract adds it. For plugins that support several instances, set
    :attr:`MULTI_INSTANCE` so the plugin runs as instance ``plg`` next to a second instance.
    """

    CLASS_PATH: ClassVar[str]
    CLASS_NAME: ClassVar[str]
    PARAMS: ClassVar[dict[str, Any]] = {}
    MULTI_INSTANCE: ClassVar[bool] = False

    def before_items(self, plugin: SmartPlugin) -> None:
        """Hook called with the loaded plugin before any item is created."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        params = {**self.PARAMS, 'pause_item': PAUSE_ITEM_PATH}
        other_sections = {SECOND_SECTION: params} if self.MULTI_INSTANCE else None
        self.rig: PluginRig = load_plugin(
            self._tmp.name,
            self.CLASS_PATH,
            self.CLASS_NAME,
            PAUSE_ITEMS_YAML,
            params=params,
            before_items=self.before_items,
            other_sections=other_sections,
        )
        self.plugin = self.rig.plugin
        self.pause: Item = self.rig.item(PAUSE_ITEM_PATH)
        self.calls: list[str] = []
        self.plugin.stop = self._record_stop
        self.plugin.run = self._record_run
        if self.MULTI_INSTANCE:
            sibling = self.rig.sh.plugins.return_plugin(SECOND_SECTION)
            sibling.stop = sibling.run = lambda: None

    def _record_stop(self) -> None:
        self.calls.append('stop')
        self.plugin.alive = False

    def _record_run(self) -> None:
        self.calls.append('run')
        self.plugin.alive = True

    def test_item_is_registered_as_pause_item(self) -> None:
        self.assertIs(self.pause, self.plugin._pause_item)

    def test_external_pause_stops_running_plugin(self) -> None:
        self.plugin.alive = True

        self.pause(True, 'test')

        self.assertEqual(['stop'], self.calls)

    def test_external_resume_runs_stopped_plugin(self) -> None:
        self.plugin.alive = False
        self.pause(True, 'test')

        self.pause(False, 'test')

        self.assertEqual(['run'], self.calls)

    def test_external_pause_of_stopped_plugin_is_ignored(self) -> None:
        self.plugin.alive = False

        self.pause(True, 'test')

        self.assertEqual([], self.calls)

    def test_own_write_back_of_pause_is_ignored(self) -> None:
        self.plugin.alive = True
        self.pause(True, self.plugin.get_fullname())
        self.plugin.alive = False
        self.pause(False, self.plugin.get_fullname())

        self.assertEqual([], self.calls)

    def test_instance_name_differs_from_shortname_in_multi_instance_setup(self) -> None:
        if not self.MULTI_INSTANCE:
            self.skipTest('plugin does not run as several instances')

        self.assertNotEqual(self.plugin.get_shortname(), self.plugin.get_fullname())
