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
Host power actions (power off, reboot) via the operating system's own commands.

No privilege handling is done here: the commands run as the user SmartHomeNG runs
as, so the operating system's configuration (polkit, sudoers, ...) decides whether
they are permitted.
"""

import platform
import subprocess
from typing import Literal

PowerAction = Literal['poweroff', 'reboot']

# argv per lower-case platform.system() name; add an entry to support another OS
POWER_COMMANDS: dict[str, dict[PowerAction, list[str]]] = {
    'linux': {'poweroff': ['poweroff'], 'reboot': ['reboot']},
    'darwin': {'poweroff': ['shutdown', '-h', 'now'], 'reboot': ['shutdown', '-r', 'now']},
    'windows': {'poweroff': ['shutdown', '/s', '/t', '0'], 'reboot': ['shutdown', '/r', '/t', '0']},
}


def _platform_name(platform_name: str | None) -> str:
    """Returns platform_name, or the lower-case name of the running platform if it is None."""
    return platform_name if platform_name is not None else platform.system().lower()


def is_supported(platform_name: str | None = None) -> bool:
    """
    Tells whether power actions are available on a platform.

    :param platform_name: lower-case platform.system() name, defaults to the running platform
    """
    return _platform_name(platform_name) in POWER_COMMANDS


def run_power_action(action: PowerAction, platform_name: str | None = None, timeout: float = 15) -> tuple[bool, str]:
    """
    Runs the platform's command for a power action and waits for it to return.

    The command normally returns as soon as the operating system has accepted the request;
    the host then terminates SmartHomeNG itself.

    :param action: 'poweroff' or 'reboot'
    :param platform_name: lower-case platform.system() name, defaults to the running platform
    :param timeout: seconds to wait for the command to return
    :return: (True, '') on success, otherwise (False, error text from the command or its failure)
    :raises ValueError: if action is not a known power action
    """
    if action not in ('poweroff', 'reboot'):
        raise ValueError(f"unknown power action '{action}'")
    name = _platform_name(platform_name)
    if name not in POWER_COMMANDS:
        return False, f"power actions are not supported on platform '{name}'"

    argv = POWER_COMMANDS[name][action]
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return False, f"command '{argv[0]}' not found"
    except subprocess.TimeoutExpired:
        return False, f"command '{' '.join(argv)}' timed out after {timeout} seconds"
    except OSError as e:
        return False, f"command '{' '.join(argv)}' failed: {e}"

    if result.returncode != 0:
        text = (result.stderr or result.stdout).strip()
        return False, text or f"command '{' '.join(argv)}' exited with code {result.returncode}"
    return True, ''
