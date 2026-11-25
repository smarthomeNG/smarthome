"""Test-only submodule, deliberately edited on disk mid-test.

Used by tests/test_plugin_reload.py's TestReloadSubmodules to verify
reload() ordering: dependent_formatter.py imports from this module, so this
one must be reloaded first - if dependent_formatter reloads before this
does, its `from .leaf_dependency import get_value` line rebinds to the
still-stale function.
"""


def get_value():
    return 'original'
