"""Test-only submodule that imports from a sibling submodule.

Used by tests/test_plugin_reload.py's TestReloadSubmodules to verify
reload() ordering. If this module reloads before leaf_dependency.py does,
its `from .leaf_dependency import get_value` line rebinds to whatever
get_value is still cached in sys.modules at that moment - stale, if
leaf_dependency hasn't been reloaded yet - and that stale reference is
then baked into format_value() until the next reload, even though
leaf_dependency's own get_value did get updated.

Named so that a naive alphabetically-sorted reload order gets this wrong:
'dependent_formatter' sorts before 'leaf_dependency'.
"""

from .leaf_dependency import get_value


def format_value():
    return f'[{get_value()}]'
