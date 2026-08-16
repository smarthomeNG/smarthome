#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Shared helper for tests exercising Standalone.create_struct_yaml() (the
struct.yaml generator in `lib.model.smartdeviceplugin`'s standalone mode)
against real plugins' commands.py.

create_struct_yaml() overwrites plugin.yaml in place, so every test using
this helper must run against an isolated COPY of the plugin directory,
never the real plugins/<name> tree.

Each plugin gets copied under its own uniquely-named top-level package
(``plugins_<name>``, not the real ``plugins``): once a package name is
imported once in a process, sys.path changes don't make Python re-resolve
it to a different directory, so reusing the literal 'plugins' package
name across more than one copy in the same pytest run would make the
second plugin's import silently resolve to the first plugin's copy.

Paths are pathlib.Path throughout, including Standalone.plugin_path on
the instances this builds - matching what Standalone.__init__ itself now
sets it to, so create_struct_yaml()'s `self.plugin_path / 'plugin.yaml'`
works the same way here as it does for a real CLI invocation.
"""

import builtins
import logging
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

builtins.SDP_standalone = False  # noqa

from lib.model.smartdeviceplugin import Standalone  # noqa: E402


def copy_plugin_into(dest_root: Path, plugin_name: str) -> Path:
    """Copies plugins/<plugin_name> into an isolated package under
    dest_root, adds dest_root to sys.path, and returns the copy's path."""
    import shutil

    pkg_name = f'plugins_{plugin_name}'
    src = BASE / 'plugins' / plugin_name
    dst_pkg_dir = dest_root / pkg_name
    dst = dst_pkg_dir / plugin_name
    dst_pkg_dir.mkdir(parents=True, exist_ok=True)
    (dst_pkg_dir / '__init__.py').touch()
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', 'tests', '_pv_*'))

    dest_root_str = str(dest_root)
    if dest_root_str not in sys.path:
        sys.path.insert(0, dest_root_str)

    return dst


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


def build_standalone(dest_root: Path, plugin_name: str, acl: bool = True, lc: bool = False) -> Standalone:
    """Copies plugins/<plugin_name> under dest_root and returns a
    Standalone instance ready to call create_struct_yaml() on, bypassing
    the CLI-argument/cwd-checking __init__()."""
    dst = copy_plugin_into(Path(dest_root), plugin_name)
    return _new_standalone(dst, plugin_name, f'plugins_{plugin_name}', acl, lc)


def build_synthetic_standalone(
    dest_root: Path, plugin_name: str, commands_src: str, plugin_yaml: dict, acl: bool = False, lc: bool = False
) -> Standalone:
    """Writes a minimal, hand-authored commands.py + plugin.yaml (not
    copied from a real plugin) into an isolated package under dest_root,
    and returns a Standalone instance ready to call create_struct_yaml()
    on. For exercising specific commands.py/plugin.yaml shapes that don't
    occur in any of the real plugins used elsewhere as test bases."""
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
