#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Process-wide resolver for SmartHomeNG's ``var`` directory.

The var tree (cache, logs, pidfile, databases, plugin data...) lives at ``<base>/var`` unless
``--var_dir`` was given on the command line. ``bin/smarthome.py`` calls :func:`set_var_dir` once after
parsing the arguments; everything else reads the location through :func:`get_var_dir`,
:func:`resolve_var_path` or ``SmartHome.get_vardir()``, so code that runs before a ``SmartHome`` instance
exists (pidfile, debug logging, ephemeris cache) resolves to the same place.
"""

import os

from lib.constants import DIR_VAR

BASE_DIR = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])

_DEFAULT_VAR_DIR = os.path.join(BASE_DIR, DIR_VAR)
_var_dir = _DEFAULT_VAR_DIR


def get_var_dir() -> str:
    """Return the absolute path of the var directory."""
    return _var_dir


def set_var_dir(path: str | None) -> None:
    """
    Set the var directory.

    :param path: directory to use (``~`` is expanded, relative paths are made absolute); None or '' restores
                 the default ``<base>/var``
    """
    global _var_dir
    _var_dir = os.path.abspath(os.path.expanduser(path)) if path else _DEFAULT_VAR_DIR


def _split_var_prefix(path: str) -> str | None:
    """Return the part of a relative ``path`` below its leading ``var`` segment, or None if it has no such prefix."""
    if os.path.isabs(path):
        return None
    parts = os.path.normpath(path).split(os.path.sep)
    if parts[0] != DIR_VAR:
        return None
    return os.path.join(*parts[1:]) if len(parts) > 1 else ''


def rebase_var_prefix(path: str) -> str:
    """
    Re-root a relative ``var/...`` path under the configured var directory.

    Paths without a leading ``var`` segment (absolute paths, ``plugins/foo/var/x``...) and every path while
    the var directory is the default are returned unchanged.
    """
    if _var_dir == _DEFAULT_VAR_DIR:
        return path
    below_var = _split_var_prefix(path)
    if below_var is None:
        return path
    return os.path.join(_var_dir, below_var) if below_var else _var_dir


def resolve_var_path(path: str) -> str:
    """
    Resolve ``path`` to an absolute path.

    A relative path starting with ``var`` is located below the configured var directory, any other relative
    path below the base directory; absolute paths are returned unchanged (normalised).
    """
    below_var = _split_var_prefix(path)
    if below_var is not None:
        return os.path.join(_var_dir, below_var) if below_var else _var_dir
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(BASE_DIR, path))
