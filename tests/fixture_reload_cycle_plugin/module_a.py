"""Test-only submodule forming a genuine circular import with module_b.py.

Used by tests/test_plugin_reload.py's TestReloadSubmodules to verify that
reload_plugin() falls back safely (does not raise) when a plugin's own
submodules have a circular import - graphlib.TopologicalSorter has no sane
reload order for a true cycle. Kept in its own dedicated fixture plugin
package, separate from fixture_reload_submodule_plugin, so this cycle
doesn't leak into that plugin's own (cycle-free) reload-order tests.
"""

from . import module_b


def value_from_a():
    return f'a+{module_b.value_from_b()}'
