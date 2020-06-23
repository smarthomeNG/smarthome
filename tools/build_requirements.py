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
This script assembles a complete list of requirements for the SmartHomeNG core and all plugins.

The list is not tested for correctness nor checked for contrary 
requirements. 

The procedure is as following:
1) walks the plugins subdirectory and collect all files with requirements
2) read the requirements for the core 
3) read all files with requirements and add them with source of requirement to a dict
4) write it all to a file all.txt in requirements directory

"""

import os
import sys

sh_basedir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

program_name = sys.argv[0]
arguments = sys.argv[1:]
if "-debug_tox" in arguments:
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('build_requirements')
    logger.setLevel(logging.DEBUG)
    logger.debug("sys.path = {}".format(sys.path))

import lib.shpypi as shpypi


# ==========================================================================


selection = 'all'


if not os.path.exists(os.path.join(sh_basedir, 'modules')):
    print ("Directory <shng-root>/modules not found!")
    exit(1)
if not os.path.exists(os.path.join(sh_basedir, 'plugins')):
    print ("Directory <shng-root>/plugins not found!")
    exit(1)
if not os.path.exists(os.path.join(sh_basedir, 'requirements')):
    print ("Directory <shng-root>/requirements not found!")
    exit(1)

req_files = shpypi.Requirements_files()

# req_files.create_requirementsfile('core')
# print("File 'requirements" + os.sep + "core.txt' created.")
# req_files.create_requirementsfile('modules')
# print("File 'requirements" + os.sep + "modules.txt' created.")
fn = req_files.create_requirementsfile('base')
print("File {} created.".format(fn))

# req_files.create_requirementsfile('plugins')
# print("File 'requirements" + os.sep + "plugins.txt' created.")
fn = req_files.create_requirementsfile('all')
print("File {} created.".format(fn))
