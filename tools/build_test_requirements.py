#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2018-       Martin Sinn                         m.sinn@gmx.de
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
This script assembles the list of requirements actually needed to run the plugin test
suite: the core/module requirements plus the requirements.txt of only those plugins that
have a 'tests' subdirectory.

Installing every plugin's requirements (as 'requirements/all.txt' does) is overkill for
running tests, since pytest only ever imports the handful of plugins that have tests in
the first place - the rest of the ~150+ plugins' dependencies are never touched.

The procedure is as following:
1) walk the plugins subdirectory and find plugins that have a 'tests' subdirectory
   (skipping superseded '_pv_*' plugin versions, same as the rest of this tooling)
2) collect their requirements.txt files
3) reuse Requirements_files' existing 'configured plugins' mechanism to merge those with
   the core/module requirements and write it all to requirements/test_plugins.txt
"""

import os
import sys

sh_basedir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

import bin.shngversion

VERSION = bin.shngversion.get_shng_version()

from lib.shpypi import Shpypi

shpypi = Shpypi.get_instance()
if shpypi is None:
    shpypi = Shpypi(base=sh_basedir, version=VERSION, for_tests=True)

# ==========================================================================

plugins_dir = os.path.join(sh_basedir, 'plugins')

if not os.path.exists(os.path.join(sh_basedir, 'modules')):
    print('Directory <shng-root>/modules not found!')
    exit(1)
if not os.path.exists(plugins_dir):
    print('Directory <shng-root>/plugins not found!')
    exit(1)
if not os.path.exists(os.path.join(sh_basedir, 'requirements')):
    print('Directory <shng-root>/requirements not found!')
    exit(1)

import fnmatch


def _has_test_files(tests_dir):
    # require an actual test_*.py file, not just a 'tests' directory - e.g. stale
    # __pycache__ leftovers from a different branch checkout shouldn't count
    for root, _dirnames, filenames in os.walk(tests_dir):
        if fnmatch.filter(filenames, 'test_*.py'):
            return True
    return False


tested_plugin_files = []
for entry in sorted(os.listdir(plugins_dir)):
    if '_pv' in entry:
        # superseded plugin version directories are never test-relevant
        continue
    plugin_path = os.path.join(plugins_dir, entry)
    if not os.path.isdir(plugin_path):
        continue
    tests_dir = os.path.join(plugin_path, 'tests')
    if not os.path.isdir(tests_dir) or not _has_test_files(tests_dir):
        continue
    req_file = os.path.join(plugin_path, 'requirements.txt')
    if os.path.isfile(req_file):
        tested_plugin_files.append(req_file)
    print(f"Plugin '{entry}' has tests - requirements included.")

shpypi.req_files.set_conf_plugin_files(tested_plugin_files, label='tested plugin ')
fn = shpypi.req_files.create_requirementsfile('test_plugins')
# clear it again so this temporary use doesn't leak into any other requirementsfile build
shpypi.req_files.set_conf_plugin_files([])

print('File {} created.'.format(fn))
