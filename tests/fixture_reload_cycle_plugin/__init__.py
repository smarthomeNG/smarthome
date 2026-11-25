"""Test-only plugin whose submodules have a circular import between them.

Used by tests/test_plugin_reload.py's TestReloadSubmodules to verify that
reload_plugin() falls back safely rather than raising when a plugin's own
submodules can't be topologically ordered.
"""

from lib.model.smartplugin import SmartPlugin

from . import module_a


class CyclePlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()

    def get_cycle_value(self):
        return module_a.value_from_a()
