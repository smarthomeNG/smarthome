"""Test-only plugin whose class lives in __init__.py and imports a sibling
submodule, mirroring real plugins like hue2 (class in __init__.py, webif as
a separate locally-imported submodule).

Used by tests/test_plugin_reload.py to verify that reload_plugin() reloads
a plugin's own locally-imported submodules, not just its top-level module.
"""

from lib.model.smartplugin import SmartPlugin

from .helper import get_message
from .dependent_formatter import format_value


class SubmoduleReloadPlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()

    def get_message(self):
        return get_message()

    def get_formatted_value(self):
        return format_value()
