#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  This file is part of SmartHomeNG
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
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Print a salted password hash for ``hashed_password`` / ``service_hashed_password`` of the http module
(etc/module.yaml) or ``hashed_password`` of the cli plugin.

The password is read without echo; it never appears on the command line or in the shell history.

Usage:
    tools/hash_password.py
"""

import getpass
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.utils import Utils  # noqa: E402


def main() -> int:
    """Ask for the password twice and print its hash; return the exit code."""
    password = getpass.getpass('Password: ')
    if not password:
        print('An empty password cannot be hashed.', file=sys.stderr)
        return 1
    if getpass.getpass('Repeat password: ') != password:
        print('The passwords do not match.', file=sys.stderr)
        return 1
    print(Utils.hash_password(password))
    return 0


if __name__ == '__main__':
    sys.exit(main())
