#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
What a pull of the core or plugins repository demands of the running core: a restart, or a reload of
the plugins whose files changed.
"""

import threading
from typing import Callable, Iterable, TypedDict

from ruamel.yaml import YAML, YAMLError

CORE_CODE_DIRS = ('bin', 'lib', 'modules')


def core_restart_reasons(files: list[str]) -> list[str]:
    """
    Returns the code directories of the core repository that contain changed files.

    The running core executes what it loaded at startup, so a change in any of them needs a restart.
    Documentation, tests and tools do not.

    :param files: changed paths, relative to the repository root
    """
    touched = {path.split('/', 1)[0] for path in files}
    return [directory for directory in CORE_CODE_DIRS if directory in touched]


class PullImpact(TypedDict):
    """What a pull of the plugins repository demands of the running core."""

    restart: list[str]  # why a restart is needed, empty if none is
    reload: list[str]  # configuration names (sections of etc/plugin.yaml) of the plugins to reload


# files in a plugin directory that the running plugin never loads
_INERT_DIRS = ('tests', 'user_doc')
_INERT_SUFFIXES = ('.md', '.rst')

# plugin.yaml sections that are registered once at startup and keep their first definition on a reload
_STARTUP_ONLY_SECTIONS = ('item_attributes', 'item_attribute_prefixes', 'item_structs', 'logic_parameters')


def _is_inert(relpath: str) -> bool:
    """Tells whether a file below a plugin directory is irrelevant to the running plugin."""
    return relpath.split('/')[0] in _INERT_DIRS or relpath.endswith(_INERT_SUFFIXES)


def _entries(document: dict, section: str) -> dict:
    """Returns the entries of a plugin.yaml section; a section without entries is empty or marked `NONE`."""
    entries = document.get(section)
    return entries if isinstance(entries, dict) else {}


def _metadata_restart_reasons(directory: str, old: str, new: str) -> list[str]:
    """
    Returns why a change of a plugin's plugin.yaml needs a restart, [] if a reload picks it up.

    Item attributes, attribute prefixes, item structs and logic parameters are registered when the first
    instance loads; a reload registers new entries but keeps the registered definition of an existing one.
    So only a changed definition needs a restart; added and removed entries do not.

    :param directory: plugin directory, for the reason text
    :param old: plugin.yaml before the pull
    :param new: plugin.yaml after the pull
    """
    try:
        before, after = YAML(typ='safe').load(old) or {}, YAML(typ='safe').load(new) or {}
    except YAMLError:
        return [f'{directory}: plugin.yaml not readable']
    if not isinstance(before, dict) or not isinstance(after, dict):
        return [f'{directory}: plugin.yaml not readable']

    reasons = []
    for section in _STARTUP_ONLY_SECTIONS:
        old_entries, new_entries = _entries(before, section), _entries(after, section)
        if any(key in new_entries and new_entries[key] != value for key, value in old_entries.items()):
            reasons.append(f'{directory}: {section} changed')
    return reasons


def _plugin_restart_reasons(
    directory: str, relevant: list[str], read_old: Callable[[str], str | None], read_new: Callable[[str], str | None]
) -> list[str]:
    """Returns why the changed files of one plugin need a restart instead of a reload, [] if none does."""
    if f'{directory}/requirements.txt' in relevant:
        return [f'{directory}: requirements.txt changed']

    metadata = f'{directory}/plugin.yaml'
    if metadata not in relevant:
        return []
    old, new = read_old(metadata), read_new(metadata)
    if new is None:
        return [f'{directory}: plugin.yaml removed']
    return _metadata_restart_reasons(directory, old, new) if old is not None else []


def plugins_impact(
    files: list[str],
    configs_by_dir: dict[str, list[str]],
    read_old: Callable[[str], str | None],
    read_new: Callable[[str], str | None],
) -> PullImpact:
    """
    Decides from the files a pull changed which configured plugins have to be reloaded, and whether
    the changes are of a kind that a reload cannot pick up.

    Plugins that are not configured are ignored. A plugin's changed code, templates and plugin.yaml
    are picked up by a reload of all its instances; a plugin with a change that needs a restart is
    not listed for reload.

    :param files: changed paths, relative to the plugins repository root
    :param configs_by_dir: per plugin directory, the configuration names of its loaded instances
    :param read_old: returns the content of a file before the pull, None if it did not exist
    :param read_new: returns the content of a file after the pull, None if it does not exist
    """
    restart: list[str] = ['plugins package changed'] if '__init__.py' in files else []
    reload: list[str] = []
    for directory, configs in configs_by_dir.items():
        prefix = directory + '/'
        relevant = [path for path in files if path.startswith(prefix) and not _is_inert(path[len(prefix) :])]
        if not relevant:
            continue
        reasons = _plugin_restart_reasons(directory, relevant, read_old, read_new)
        restart.extend(reasons)
        if not reasons:
            reload.extend(configs)
    return {'restart': restart, 'reload': reload}


def plugin_configs_by_dir(loaded: Iterable[tuple[str, str]]) -> dict[str, list[str]]:
    """
    Groups the configuration names of loaded plugin instances by the plugin directory they run from.

    Only plugins loaded from a directory directly below plugins/ are listed; superseded versions
    (plugins.<dir>._pv_*) and plugins from elsewhere are not part of the plugins repository checkout.

    :param loaded: (configuration name, class path) per loaded instance, in load order
    """
    grouped: dict[str, list[str]] = {}
    for configname, classpath in loaded:
        package, _, directory = classpath.partition('.')
        if package == 'plugins' and directory and '.' not in directory:
            grouped.setdefault(directory, []).append(configname)
    return grouped


class PendingReloads:
    """
    Names of the plugin configurations whose files were updated by a pull and that still run the old code.

    Held in memory only: a restart of the core loads the new code, so it needs no record.
    """

    def __init__(self) -> None:
        self._names: set[str] = set()
        self._lock = threading.Lock()

    def add(self, names: Iterable[str]) -> None:
        """Marks the given configurations as running outdated code."""
        with self._lock:
            self._names.update(names)

    def discard(self, name: str) -> None:
        """Forgets a configuration, e.g. after it was reloaded or unloaded; unknown names are ignored."""
        with self._lock:
            self._names.discard(name)

    def names(self) -> list[str]:
        """Returns the marked configurations, sorted."""
        with self._lock:
            return sorted(self._names)

    def __contains__(self, name: object) -> bool:
        with self._lock:
            return name in self._names
