"""Test-only dummy plugin declaring startorder: early in its plugin.yaml.

Used by tests/test_plugin_reload.py to verify that get_pluginthread() can
find plugins loaded at runtime (i.e. via a load_plugin() call outside the
initial bulk __init__ loop) whose startorder routes them into
Plugins.threads_early/threads_late instead of Plugins._threads.
"""

from lib.model.smartplugin import SmartPlugin


class EarlyOrderPlugin(SmartPlugin):
    PLUGIN_VERSION = '1.0.0'

    def __init__(self, sh, *args, **kwargs):
        super().__init__()
