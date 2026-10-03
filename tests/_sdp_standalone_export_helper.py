#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Shared helper for tests exercising Standalone.create_struct_yaml() (the
struct.yaml generator in `lib.model.smartdeviceplugin`'s standalone mode)
on synthetic plugins written into a temporary directory.

Each synthetic plugin lives in its own uniquely-named top-level package
(``synthplugins_<name>``): once a package name is imported in a process,
sys.path changes don't make Python re-resolve it to a different directory.

Paths are pathlib.Path throughout, including Standalone.plugin_path on
the instances this builds - matching what Standalone.__init__ itself now
sets it to, so create_struct_yaml()'s `self.plugin_path / 'plugin.yaml'`
works the same way here as it does for a real CLI invocation.
"""

import builtins
import logging
import sys
from pathlib import Path


builtins.SDP_standalone = False  # noqa

from lib.model.smartdeviceplugin import Standalone  # noqa: E402


def _new_standalone(plugin_dir: Path, plugin_name: str, mod_prefix: str, acl: bool, lc: bool) -> Standalone:
    standalone = Standalone.__new__(Standalone)
    standalone.plugin_name = plugin_name
    standalone.plugin_mod_path = f'{mod_prefix}.{plugin_name}'
    standalone.plugin_path = plugin_dir
    standalone.struct_mode = True
    standalone.acl = acl
    standalone.lc = lc
    standalone.item_tree = {}
    standalone.item_templates = {}
    standalone.yaml = None
    standalone.cmdlist = []
    standalone.logger = logging.getLogger(f'test.sdp_standalone.{plugin_name}')
    standalone.logger.setLevel(logging.CRITICAL)
    standalone.params = {}
    return standalone


def build_synthetic_standalone(
    dest_root: Path, plugin_name: str, commands_src: str, plugin_yaml: dict, acl: bool = False, lc: bool = False
) -> Standalone:
    """Writes a minimal, hand-authored commands.py + plugin.yaml (not
    copied from a real plugin) into an isolated package under dest_root,
    and returns a Standalone instance ready to call create_struct_yaml()
    on."""
    import lib.shyaml as shyaml

    dest_root = Path(dest_root)
    pkg_name = f'synthplugins_{plugin_name}'
    plugin_dir = dest_root / pkg_name / plugin_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir.parent / '__init__.py').touch()
    (plugin_dir / '__init__.py').touch()

    (plugin_dir / 'commands.py').write_text(commands_src)
    shyaml.yaml_save(plugin_dir / 'plugin.yaml', plugin_yaml)

    dest_root_str = str(dest_root)
    if dest_root_str not in sys.path:
        sys.path.insert(0, dest_root_str)

    return _new_standalone(plugin_dir, plugin_name, pkg_name, acl, lc)
