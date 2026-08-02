"""Test-only plugin with real run()/stop() implementations.

Used by tests/test_plugin_reload.py to verify that Plugins.start_plugin()
executes run() on the plugin's own dedicated PluginWrapper thread instead of
synchronously on the caller's thread.
"""

import threading

from lib.model.smartplugin import SmartPlugin


class ThreadedRunPlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()
        self.run_thread = None

    def run(self):
        self.alive = True
        self.run_thread = threading.current_thread()

    def stop(self):
        self.alive = False
