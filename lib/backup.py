#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 Marcus Popp                               marcus@popp.mx
# Copyright 2016 The SmartHomeNG team
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
This library creates a zip file with the configuration of SmartHomeNG.


"""

import copy
import logging
import zipfile
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def get_backupdate():
    year = str(datetime.today().year)
    month = str(datetime.today().month).zfill(2)
    day = str(datetime.today().day).zfill(2)
    return year + '-' + month + '-' + day



def create_backup(conf_base_dir, var_dir=''):
    '''
    Create a zip file containing the configuration of SmartHomeNG. The zip file is stored in var/backup

    This function can be called without an existing sh object (backup via commandline option), so it may nor
    use any references via 'sh.'

    :param conf_base_dir: basedir for configuration
                          (shold be 'extern_conf_dir' to reflect --config_dir option)
    :param var_dir:       var-directory. If empty or ommited, conf_base_dir/var is used.

    :return:
    '''


    # backup_filename = 'shng_config_backup_' + get_backupdate() + '.zip'
    backup_filename = 'shng_config_backup.zip'

    etc_dir = os.path.join(conf_base_dir, 'etc')
    items_dir = os.path.join(conf_base_dir, 'items')
    logic_dir = os.path.join(conf_base_dir, 'logics')
    scenes_dir = os.path.join(conf_base_dir, 'scenes')

    if var_dir == '':
        var_dir = os.path.join(conf_base_dir, 'var')
    backup_dir = var_dir + os.path.sep + 'backup'


    if not os.path.isdir(backup_dir):
        try:
            os.makedirs(backup_dir)
        except OSError as e:
            logger.error("Cannot create directory - No backup was created - Error {}".format(e))
            return


    # create new zip file
    backupzip = zipfile.ZipFile(backup_dir + os.path.sep + backup_filename, mode='w')

    # backup files from /etc
    #logger.warning("- etc_dir = {}".format(etc_dir))
    source_dir = etc_dir
    arc_dir = 'etc'
    backup_file(backupzip, source_dir, arc_dir, 'logging.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'logic.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'module.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'plugin.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'smarthome.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'struct.yaml')

    # backup files from /items
    #logger.warning("- items_dir = {}".format(items_dir))
    backup_directory(backupzip, items_dir)

    # backup files from /logic
    #logger.warning("- logic_dir = {}".format(logic_dir))
    backup_directory(backupzip, logic_dir, '.py')

    # backup files from /scenes
    #logger.warning("- scenes_dir = {}".format(scenes_dir))
    backup_directory(backupzip, scenes_dir)

    zipped_files = backupzip.namelist()
    #logger.warning("Zipped files: {}".format(zipped_files))
    backupzip.close()


    #logger.warning("- backup_dir = {}".format(backup_dir))

    return os.path.join(backup_dir, backup_filename)


def backup_file(backupzip, source_dir, arc_dir, filename):

    if os.path.isfile(os.path.join(source_dir, filename)):
        backupzip.write(os.path.join(source_dir, filename), arcname=os.path.join(arc_dir, filename))
    return


def backup_directory(backupzip, source_dir, extenstion='.yaml'):

    path = source_dir.split(os.path.sep)
    dir = path[len(path)-1]
    arc_dir = dir + os.path.sep
    files = []
    for filename in os.listdir(source_dir):
        if filename.endswith(extenstion):
            backup_file(backupzip, source_dir, arc_dir, filename)

    return