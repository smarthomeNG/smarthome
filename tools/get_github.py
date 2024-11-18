#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2024-      Sebastian Helms           Morg @ knx-user-forum
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.10
#  and up.
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################


# this tools downloads the githubplugin Plugin from my personal repo to
# alleviate the hen-egg-problem with installing foreign plugins
#
# after running this tool, configure "priv_githubplugin" as plugin in shng
# and install plugins as you like

import os
import sys

try:
    from git import Repo  # noqa
except Exception:
    print('Bitte Modul gitpython installieren ("pip3 install gitpython") und das Programm erneut starten.')

oldcwd = os.getcwd()

# get shng base dir and switch there
BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
os.chdir(BASE)

# set some filenames / paths
plg = 'priv_githubplugin'
url = 'https://github.com/Morg42/ghp.git'

target = os.path.join('plugins', plg)

if os.path.exists(target) or os.path.islink(target):
    print('Der Ordner (oder Link) plugins/priv_githubplugin existiert bereits. Ausführung wird beendet.')
    sys.exit(1)

print(f'cloning repo at {target} from {url}...')

# clone repo from url
try:
    repo = Repo.clone_from(url, target)
except Exception as e:
    print(f'Fehler beim clone: {e}')
    sys.exit(2)

print("""
Plugin wurde installiert. Bitte folgenden Eintrag in etc/plugin.yaml eintragen:


github:
    plugin_name: priv_githubplugin


Danach SmartHomeNG neu starten.

Wenn das Plugin nicht mehr benötigt wird (z.B. weil es aus dem develop-Zweig von
shng vorhanden ist), kann der Ordner plugins/priv_githubplugin komplett gelöscht
werden. Dann muss der Eintrag in etc/plugins angepasst oder entfernt werden.

Viel Spaß!
""")
