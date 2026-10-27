#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Detection of the system daemons shown on the admin system page (KNX, 1-Wire, MQTT broker, Node-RED).

Each detector returns the daemon name with its version if available, or 'SERVICES.INACTIVE' (a
translation key of shngadmin) if it is not running or the platform is Windows.
"""

import os

from lib.utils import Utils, execute_subprocess

INACTIVE = 'SERVICES.INACTIVE'


def shell_output(command: str, include_stderr: bool = False) -> str:
    """
    Run ``command`` through the shell and return its output.

    :param include_stderr: append the output written to stderr (some daemons print their version there)
    """
    if include_stderr:
        stdout, stderr = Utils.execute_subprocess(command)
        return stdout + stderr
    return execute_subprocess(command)


def _is_running(process: str) -> bool:
    """Return True if a process named ``process`` shows up in the process list."""
    return shell_output(f'ps cax|grep {process}') != ''


def _word(text: str, index: int) -> str | None:
    """Return the whitespace separated word ``index`` of ``text``, None if there is none."""
    words = text.split()
    return words[index] if len(words) > index else None


def knx_daemon() -> str:
    """Return which of eibd/knxd is running, with the knxd version if only knxd runs."""
    if os.name == 'nt':
        return INACTIVE
    eibd = _is_running('eibd')
    knxd = _is_running('knxd')
    if eibd and knxd:
        return 'eibd and knxd'
    if eibd:
        return 'eibd'
    if not knxd:
        return INACTIVE
    version = _word(shell_output('knxd -l?V|grep knxd', include_stderr=True), 1)
    return f'knxd v{version.split(":")[0]}' if version else 'knxd'


def onewire_daemon() -> str:
    """Return 'owserver' with its version if the 1-Wire server is running."""
    if os.name == 'nt' or not _is_running('owserver'):
        return INACTIVE
    version = _word(shell_output("owserver -V|grep 'owserver version'", include_stderr=True), 2)
    return f'owserver v{version}' if version else 'owserver'


def mqtt_daemon() -> str:
    """Return 'mosquitto' with its version if the MQTT broker is running."""
    if os.name == 'nt' or not _is_running('mosquitto'):
        return INACTIVE
    version = _word(shell_output('/usr/sbin/mosquitto -h|grep version'), 2)
    return f'mosquitto v{version}' if version else 'mosquitto'


def node_red_daemon() -> str:
    """Return 'node-red' with its version if Node-RED is running."""
    if os.name == 'nt' or not _is_running('node-red'):
        return INACTIVE
    version = _word(shell_output('node-red --help|grep Node-RED'), 1)
    return f'node-red {version}' if version else 'node-red'
