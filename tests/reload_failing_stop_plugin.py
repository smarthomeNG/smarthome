"""Test-only plugin whose stop() always raises.

Used by tests/test_plugin_reload.py to verify that reload_plugin() checks
unload_plugin()'s return value and aborts cleanly - instead of proceeding to
reload the module and load a second, fresh instance under the same
configname while the original (unload-failed) instance is still registered.
"""

from lib.model.smartplugin import SmartPlugin


class FailingStopPlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()

    def run(self):
        self.alive = True

    def stop(self):
        raise RuntimeError('simulated failure during plugin shutdown')
