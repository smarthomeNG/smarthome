"""Test-only submodule, deliberately edited on disk mid-test.

Used by tests/test_plugin_reload.py to verify that reload_plugin() reloads
a plugin's own locally-imported submodules, not just its top-level module.
"""


def get_message():
    return 'original'
