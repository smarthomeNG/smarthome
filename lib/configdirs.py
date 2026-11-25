#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Resolver for the directory holding the user configuration (items, logics, structs, scenes, functions...).

With ``config_etc`` (the default) these directories live below ``<conf>/etc``, otherwise directly below
``<conf>``, where ``<conf>`` is the ``--config_dir`` directory or the base directory. ``SmartHome`` and
``lib.backup`` (which also runs from the command line without a ``SmartHome`` instance) resolve the
setting and the directory through this module.
"""

import os

from lib.constants import BASE_SH, DIR_ETC, YAML_FILE
from lib.shyaml import yaml_load
from lib.utils import Utils

CONFIG_ETC_DEFAULT = True


def resolve_config_etc(cmdline: bool, configured: object = None) -> bool:
    """
    Return the effective ``config_etc`` setting.

    :param cmdline: True if ``--config_etc`` was given on the command line; it overrides ``configured``
    :param configured: ``config_etc`` value from ``etc/smarthome.yaml``, None if the key is absent
    """
    if cmdline:
        return True
    if configured is None:
        return CONFIG_ETC_DEFAULT
    return Utils.to_bool(configured, CONFIG_ETC_DEFAULT)


def read_config_etc(extern_conf_dir: str, cmdline: bool = False) -> bool:
    """
    Return the effective ``config_etc`` setting, reading ``etc/smarthome.yaml`` below ``extern_conf_dir``.

    :param extern_conf_dir: configuration base directory (contains ``etc``)
    :param cmdline: True if ``--config_etc`` was given on the command line
    """
    if cmdline:
        return True
    conf = yaml_load(os.path.join(extern_conf_dir, DIR_ETC, BASE_SH + YAML_FILE), ignore_notfound=True)
    configured = conf.get('config_etc') if isinstance(conf, dict) else None
    return resolve_config_etc(False, configured)


def user_conf_dir(extern_conf_dir: str, config_etc: bool) -> str:
    """
    Return the directory that contains the user config directories.

    :param extern_conf_dir: configuration base directory (contains ``etc``)
    :param config_etc: effective ``config_etc`` setting
    """
    return os.path.join(extern_conf_dir, DIR_ETC) if config_etc else extern_conf_dir
