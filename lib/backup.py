#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2019-     Martin Sinn                          m.sinn@gmx.de
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
import glob
import logging
import zipfile
import shutil
import time
import os
from datetime import datetime
from lib.shtime import Shtime

logger = logging.getLogger(__name__)


def get_backupdate():
    year = str(datetime.today().year)
    month = str(datetime.today().month).zfill(2)
    day = str(datetime.today().day).zfill(2)
    return year + '-' + month + '-' + day


def get_backuptime():
    hour = str(datetime.now().hour).zfill(2)
    minute = str(datetime.now().minute).zfill(2)
    second = str(datetime.now().second).zfill(2)
    return hour + '-' + minute + '-' + second


def make_backup_directories(base_dir):
    """
    Create the backup-dirctory and the restore-directory, if the do not already exist

    :param base_dir:
    :return:
    """
    global backup_dir
    backup_dir = os.path.join(base_dir, 'var','backup')
    restore_dir = os.path.join(base_dir, 'var','restore')

    if not os.path.isdir(backup_dir):
        try:
            os.makedirs(backup_dir)
        except OSError as e:
            logger.error("Cannot create directory - No backup was created - Error {}".format(e))
            return False

    if not os.path.isdir(restore_dir):
        try:
            os.makedirs(restore_dir)
        except OSError as e:
            logger.error("Cannot create directory - No restore was created - Error {}".format(e))
            return False

    return True



def create_backup(conf_base_dir, base_dir, filename_with_timestamp=False, before_restore=False):
    """
    Create a zip file containing the configuration of SmartHomeNG. The zip file is stored in var/backup

    This function can be called without an existing sh object (backup via commandline option), so it may nor
    use any references via 'sh.'

    :param conf_base_dir: basedir for configuration
                          (should be 'extern_conf_dir' to reflect --config_dir option)
    :param base_dir:      var-directory. If empty or ommited, conf_base_dir/var is used.

    :return:
    """

    make_backup_directories(base_dir)
    backup_dir = os.path.join(base_dir, 'var','backup')

    backup_filename = 'shng_config_backup'
    if before_restore:
        backup_filename += '_before_restore'
    if filename_with_timestamp:
        backup_filename += '_' + get_backupdate() + '_' + get_backuptime()
    backup_filename += '.zip'

    etc_dir = os.path.join(conf_base_dir, 'etc')
    items_dir = os.path.join(conf_base_dir, 'items')
    logic_dir = os.path.join(conf_base_dir, 'logics')
    scenes_dir = os.path.join(conf_base_dir, 'scenes')


    # create new zip file
    #backupzip = zipfile.ZipFile(backup_dir + os.path.sep + backup_filename, mode='w')
    backupzip = zipfile.ZipFile(backup_dir + os.path.sep + backup_filename, mode='w', compression=zipfile.ZIP_DEFLATED)
    #backupzip = zipfile.ZipFile(backup_dir + os.path.sep + backup_filename, mode='w', compression=zipfile.ZIP_STORED)

    # backup files from /etc
    #logger.warning("- etc_dir = {}".format(etc_dir))
    source_dir = etc_dir
    arc_dir = 'etc'
    backup_file(backupzip, source_dir, arc_dir, 'holidays.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'logging.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'logic.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'module.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'plugin.yaml')
    backup_file(backupzip, source_dir, arc_dir, 'smarthome.yaml')

    backup_file(backupzip, source_dir, arc_dir, 'struct.yaml')
    struct_files = glob.glob(os.path.join( etc_dir, 'struct_*.yaml'))
    for pn in struct_files:
        fn = os.path.split(pn)[1]
        backup_file(backupzip, source_dir, arc_dir, fn)

    # backup certificate files from /etc
    backup_directory(backupzip, etc_dir, '.cer')
    backup_directory(backupzip, etc_dir, '.key')

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
    logger.info("Zipped files: {}".format(zipped_files))
    backupzip.close()


    #logger.warning("- backup_dir = {}".format(backup_dir))

    shtime = Shtime.get_instance()
    if shtime == None:
        shtime = Shtime(None)

    now = shtime.now()
    logger.info("get_backup_timestamp: now = '{}'".format(now))

    fd = open(os.path.join(backup_dir, 'last_backup'), 'w+', encoding='UTF-8')
    fd.write("%s" % now)
    fd.close()

    return os.path.join(backup_dir, backup_filename)


def get_lastbackuptime():
    """
    This method reads the file 'last_backup' and returns the timestamp.

    :return: last backup time
    :rtype: str
    """

    try:
        if os.path.isfile(os.path.join(backup_dir, 'last_backup')):
            fd = open(os.path.join(backup_dir, 'last_backup'), 'r', encoding='UTF-8')
            line = fd.readline()
            fd.close()
            return line
    except:
        logger.warning("last_backup could not be read!")
    return ""



def backup_file(backupzip, source_dir, arc_dir, filename):
    """
    Backup one file to a zip-archive

    :param backupzip: Name of the zip-archive (full pathname)
    :param source_dir: Directory where the file to backup is located
    :param arc_dir: Name of destination directory in the zip-archive
    :param filename: Name of the file to backup
    """
    if not filename.startswith('.'):
        if os.path.isfile(os.path.join(source_dir, filename)):
            #logger.debug("Zipping file: {}".format(filename))
            backupzip.write(os.path.join(source_dir, filename), arcname=os.path.join(arc_dir, filename))
    return


def backup_directory(backupzip, source_dir, extenstion='.yaml'):
    """
    Backup all files with a certain extension from the given directory to a zip-archive

    :param backupzip: Name of the zip-archive (full pathname)
    :param source_dir: Directory where the yaml-files to backup are located
    :param extenstion: Extension of the files to backup (default is .yaml)
    """
    path = source_dir.split(os.path.sep)
    dir = path[len(path)-1]
    arc_dir = dir + os.path.sep
    files = []
    for filename in os.listdir(source_dir):
        if filename.endswith(extenstion):
            backup_file(backupzip, source_dir, arc_dir, filename)

    return


def restore_backup(conf_base_dir, base_dir):
    """
    Restore configuration from a zip-archive to the SmartHomeNG instance.

    The zip-archive is read from var/restore. It has to be the only file in that directory

    This function can be called without an existing sh object (backup via commandline option), so it may nor
    use any references via 'sh.'

    :param conf_base_dir: basedir for configuration
                          (should be 'extern_conf_dir' to reflect --config_dir option)
    :param base_dir:       var-directory. If empty or ommited, conf_base_dir/var is used.

    :return:
    """

    make_backup_directories(base_dir)
    restore_dir = os.path.join(base_dir, 'var','restore')

    etc_dir = os.path.join(conf_base_dir, 'etc')
    items_dir = os.path.join(conf_base_dir, 'items')
    logic_dir = os.path.join(conf_base_dir, 'logics')
    scenes_dir = os.path.join(conf_base_dir, 'scenes')

    archive_file = ''
    for filename in os.listdir(restore_dir):
        if filename.endswith('.zip'):
            if not filename.startswith('.'):
                if archive_file == '':
                    archive_file = filename
                else:
                    archive_file = 'MULTIPLE'
                    break

    if archive_file == '':
        logger.error("No zip file found in restore directory - No configuration data was restored")
        return
    elif archive_file == 'MULTIPLE':
        logger.error("Multiple zip files found - No configuration data was restored")
        return
    restorezip_filename = os.path.join(restore_dir, archive_file)

    create_backup(conf_base_dir, base_dir, True, True)
    overwrite = True

    # open existing zip file
    restorezip = zipfile.ZipFile(restorezip_filename, mode='r')
    #restorezip = zipfile.ZipFile(restorezip_filename, mode='r', compression=zipfile.ZIP_STORED)

    # restore files to /etc
    restore_directory(restorezip, 'etc', etc_dir, overwrite)

    # restore files to /items
    restore_directory(restorezip, 'items', items_dir, overwrite)

    # backup files from /logic
    restore_directory(restorezip, 'logics', logic_dir, overwrite)

    # backup files from /scenes
    restore_directory(restorezip, 'scenes', scenes_dir, overwrite)

    # mark zip-file as restored
    os.rename(restorezip_filename, restorezip_filename + '.done')

    # delete last backup timestamp
    filename = os.path.join(backup_dir, 'last_backup')
    try:
        os.remove(filename)
    except OSError:
        pass

    return restorezip_filename


def restore_file(restorezip, arc_dir, filename, dest_dir, overwrite=False):
    """

    :param restorezip: Name of the zip-archive (full pathname)
    :param arc_dir: Name of source directory in the zip-archive
    :param filename: Name of the file to restore
    :param dest_dir: Destinaion directory where the file should be restored to
    :param overwrite: Overwrite file in destination, if it already exists

    :return:
    """
    dest_filename = os.path.join(dest_dir, filename)
    if os.path.isfile(dest_filename) and not overwrite:
        logger.error("File {} not restored - it already exists at destination {}".format(filename, dest_dir))
        return False

    logger.info("Restoring file {} to {} overwrite={}".format(filename, dest_dir, overwrite))

    # copy file (taken from zipfile's extract)
    zip_info = restorezip.getinfo(os.path.join(arc_dir, filename))
    if not(zip_info.filename[-1] == '/'):
        zip_info.filename = os.path.basename(zip_info.filename)
    restorezip.extract(zip_info, path=dest_dir, pwd=None)

    # restore original timestamp
    date_time = time.mktime(zip_info.date_time + (0, 0, -1))
    os.utime(os.path.join(dest_dir, filename), (date_time, date_time))


    return


def restore_directory(restorezip, arc_dir, dest_dir, overwrite=False):
    """
    Restore all files from a certain archive directory to a given destination directory

    :param restorezip: Name of the zip-archive (full pathname)
    :param arc_dir: Name of source directory in the zip-archive
    :param dest_dir: Destinaion directory where the file should be restored to
    :param overwrite: Overwrite file in destination, if it already exists
    """

    for fn in restorezip.namelist():
        if fn.startswith(arc_dir+'/'):
            restore_file(restorezip, arc_dir, os.path.basename(fn), dest_dir, overwrite)
    return


def write_lastbackuptime(timestamp, timefile):
    """
    This method writes the PID to the pidfile and locks it while the process is running.

    :param pid: PID of SmartHomeNG
    :param pidfile: Name of the pidfile to write to
    :type pid: int
    :type pidfile: str
    """

