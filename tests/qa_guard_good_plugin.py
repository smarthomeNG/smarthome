"""Test-only dummy plugin that correctly calls super().__init__().

Used by tests/test_plugin_super_init_qa_guard.py to verify the QA guard in
lib/plugin.py's PluginWrapper does NOT warn about a well-behaved plugin.
Not collected by pytest (module name doesn't match test_*.py).
"""

from lib.model.smartplugin import SmartPlugin


class GoodPlugin(SmartPlugin):
    PLUGIN_VERSION = (
        '1.2.0'  # matches plugins/wol/plugin.yaml's declared version, avoids an unrelated version-mismatch check
    )

    def __init__(self, sh, *args, **kwargs):
        super().__init__()
