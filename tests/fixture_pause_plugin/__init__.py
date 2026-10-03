#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Test-only SmartPlugin fixtures with a pause item."""

from lib.model.smartplugin import SmartPlugin


class FixturePause(SmartPlugin):
    """Pause item handled by the SmartPlugin base class; records run()/stop() calls."""

    PLUGIN_VERSION = '1.0.0'

    def __init__(self, sh, *args, **kwargs):
        super().__init__()
        self._pause_item_path = self.get_parameter_value('pause_item')
        self.lifecycle: list[str] = []

    def run(self):
        self.lifecycle.append('run')
        self.alive = True

    def stop(self):
        self.lifecycle.append('stop')
        self.alive = False


class FixturePauseSeam(FixturePause):
    """Overrides the pause seam; records the requested pause states instead of stopping/starting."""

    def __init__(self, sh, *args, **kwargs):
        super().__init__(sh, *args, **kwargs)
        self.pause_requests: list[bool] = []

    def on_pause_item_change(self, paused: bool) -> None:
        self.pause_requests.append(paused)


class FixturePauseOwnUpdate(FixturePause):
    """Has its own update_item, delegating the pause item to the base class helper; records other updates."""

    def __init__(self, sh, *args, **kwargs):
        super().__init__(sh, *args, **kwargs)
        self.other_updates: list[str] = []

    def parse_item(self, item):
        if item.property.path == self._pause_item_path:
            return super().parse_item(item)
        return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if self._handle_pause_item(item, caller):
            return
        self.other_updates.append(item.property.path)
