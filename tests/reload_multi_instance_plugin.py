"""Test-only multi-instance plugin.

Used by tests/test_plugin_reload.py to verify that reload_plugin() replaces every
instance of a plugin that is configured more than once.
"""

from lib.model.smartplugin import SmartPlugin


class MultiInstancePlugin(SmartPlugin):
    PLUGIN_VERSION = '1.2.0'  # matches plugins/wol/plugin.yaml's declared version

    def __init__(self, sh, *args, **kwargs):
        super().__init__()

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
