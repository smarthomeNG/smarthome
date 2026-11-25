"""Test-only submodule that imports its own package for type checking only.

Used by tests/test_plugin_reload.py's TestReloadSubmodules: an import below
`if TYPE_CHECKING:` never runs, so it must not count as a dependency (and
here: as an import cycle with the package) when the reload order is derived.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import SubmoduleReloadPlugin


def get_typed_value(plugin: 'SubmoduleReloadPlugin | None' = None):
    return 'original'
