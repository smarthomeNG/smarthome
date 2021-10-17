#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2011-2014 Marcus Popp                          marcus@popp.mx
# Copyright 2016      Christian Strassburg            c.strassburg@gmx.de
# Copyright 2016-     Martin Sinn                           m.sinn@gmx.de
# Copyright 2020-     Bernd Meiners                 bernd.meiners@mail.de
#########################################################################
#  This file is part of SmartHomeNG.
#  https://github.com/smarthomeNG/smarthome
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


#####################################################################
# Check mimimum Python Version
#####################################################################
import sys
if sys.hexversion < 0x03060000:
    print("Sorry your python interpreter ({0}.{1}) is too old. Please update to 3.6 or newer.".format(sys.version_info[0], sys.version_info[1]))
    exit()


#####################################################################
# prevent user root
#####################################################################
import os
if not os.name == 'nt':
    # Check only, if not running under Windows
    if os.getegid() == 0:
        print("SmartHomeNG should not run as root")
        # exit()

#####################################################################
# Import minimum set of Python Core Modules
#####################################################################
import argparse
import locale
# locale.getpreferredencoding() gives back platforms default file encoding
# this should be UTF-8 for linux and
# for windows mostly cp1252 (which is bad for SHNG's UTF-8 files)
# https://stackoverflow.com/questions/31469707/changing-the-locale-preferred-encoding-in-python-3-in-windows



#####################################################################
# Read command line arguments
#####################################################################
# argument handling here, because pip3_command is needed before all imports are done
argparser = argparse.ArgumentParser()
arggroup = argparser.add_mutually_exclusive_group()
argparser.add_argument('-p', '--pip3_command', help='set path of pip3 command, if it is not automatically found')
arggroup.add_argument('-i', '--interactive', help='open an interactive shell with tab completion and with verbose logging to the logfile', action='store_true')
arggroup.add_argument('-l', '--logics', help='reload all logics', action='store_true')
arggroup.add_argument('-r', '--restart', help='restart SmartHomeNG', action='store_true')
arggroup.add_argument('-s', '--stop', help='stop SmartHomeNG', action='store_true')
arggroup.add_argument('-V', '--version', help='show SmartHomeNG version', action='store_true')
arggroup.add_argument('--start', help='start SmartHomeNG and detach from console (default)', default=True, action='store_true')
arggroup.add_argument('-cb', '--create_backup', help='create backup of SmartHomeNG configuration (yaml configuration only)', action='store_true')
arggroup.add_argument('-cbt', '--create_backup_t', help='create backup of SmartHomeNG configuration with a timestamp in the filename', action='store_true')
arggroup.add_argument('-rb', '--restore_backup', help='restore backup of configuration to SmartHomeNG installation (yaml configuration only). CAUTION: Existing configuration is overwritten!', action='store_true')
argparser.add_argument('-c', '--config_dir', help='use external config dir (should contain "etc", "logics" and "items" subdirectories)')

arggroup.add_argument('-v', '--verbose', help='verbose (info output) logging to the logfile - DEPRECATED use logging-configuration', action='store_true')
arggroup.add_argument('-d', '--debug', help='stay in the foreground with verbose output - DEPRECATED use logging-configuration', action='store_true')
arggroup.add_argument('-f', '--foreground', help='stay in the foreground', action='store_true')
arggroup.add_argument('-q', '--quiet', help='reduce logging to the logfile - DEPRECATED use logging-configuration', action='store_true')
args = argparser.parse_args()


#####################################################################
# Import Python Core Modules
#####################################################################

import signal
import subprocess
import threading
import time
try:
    import psutil
except:
    pass


#####################################################################
# Base
#####################################################################
BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
sys.path.insert(0, BASE)
PIDFILE= os.path.join(BASE,'var','run','smarthome.pid')

# Only used for Version Check in Plugins to decide if a logger must be explicitly declared
import bin.shngversion
VERSION = bin.shngversion.get_shng_version()


#############################################################
# test if needed Python packages are installed
# - core requirements = libs
from lib.shpypi import Shpypi
shpypi = Shpypi.get_instance()
if shpypi is None:
    shpypi = Shpypi(base=BASE)

core_reqs = shpypi.test_core_requirements(logging=False, pip3_command=args.pip3_command)
if core_reqs == 0:
    print("Starting SmartHomeNG again...")
    python_bin = sys.executable
    if ' ' in python_bin:
        python_bin = '"'+python_bin+'"'
    command = python_bin + ' ' + os.path.join(BASE, 'bin', 'smarthome.py')
    try:
        p = subprocess.Popen(command, shell=True)
    except subprocess.SubprocessError as e:
        print("Restart command '{}' failed with error {}".format(command,e))
    time.sleep(10)
    print()
    exit(0)
elif core_reqs == -1:
    print("ERROR: Unable to install core requirements")
    print("Use the commandline option --pip3_command to specify the path to the command")
    print()
    exit(1)

#####################################################################
# Import SmartHomeNG Modules
#####################################################################
#import lib.config
import lib.daemon
#import lib.item
#import lib.log
#import lib.logic
#import lib.module
#import lib.network
#import lib.plugin
#import lib.scene
#import lib.scheduler
#import lib.tools
#import lib.orb
import lib.backup
#import lib.translation
#import lib.shyaml

from lib.smarthome import SmartHome


#####################################################################
# Globals
#####################################################################

MODE = 'default'
#TZ = gettz('UTC')





#####################################################################
# Private Methods
#####################################################################

def _reload_logics():
    """
    Reload logics through the commandline with option -l
    """
    pid = lib.daemon.read_pidfile(PIDFILE)
    if pid:
        os.kill(pid, signal.SIGHUP)


#####################################################################
# Main
#####################################################################

if __name__ == '__main__':
    try:
        if locale.getdefaultlocale() == (None, None):
            locale.setlocale(locale.LC_ALL, 'C')
        else:
            locale.setlocale(locale.LC_ALL, '')
    except:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    extern_conf_dir = BASE
    if args.config_dir is not None:
        extern_conf_dir = os.path.normpath(args.config_dir)

    lib.backup.make_backup_directories(BASE)

    if args.interactive:
        MODE = 'interactive'
        import code
        import rlcompleter  # noqa
        try:
            import readline
        except:
            print("ERROR: module 'readline' is not installed. Without this module the interactive mode can't be used")
            exit(1)
        import atexit
        # history file
        histfile = os.path.join(os.environ['HOME'], '.history.python')
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        atexit.register(readline.write_history_file, histfile)
        readline.parse_and_bind("tab: complete")
        sh = SmartHome(MODE=MODE, extern_conf_dir=extern_conf_dir)
        _sh_thread = threading.Thread(target=sh.start)
        _sh_thread.start()
        shell = code.InteractiveConsole(locals())
        shell.interact()
        exit(0)
    elif args.logics:
        _reload_logics()
        exit(0)
    elif args.version:
        import bin.shngversion
        VERSION = bin.shngversion.get_shng_version()
        print("{}".format(VERSION))
        exit(0)
    elif args.stop:
        lib.daemon.kill(PIDFILE, 30)
        exit(0)
    elif args.restart:
        time.sleep(5)
        lib.daemon.kill(PIDFILE, 30)
        pass
    elif args.debug:
        MODE = 'debug'
    elif args.quiet:
        pass
    elif args.verbose:
        MODE = 'verbose'
        pass
    elif args.foreground:
        MODE = 'foreground'
        pass
    elif args.create_backup:
        fn = lib.backup.create_backup(extern_conf_dir, BASE)
        if fn:
            print("Backup of configuration created at: \n{}".format(fn))
        exit(0)
    elif args.create_backup_t:
        fn = lib.backup.create_backup(extern_conf_dir, BASE, filename_with_timestamp=True)
        if fn:
            print("Backup of configuration created at: \n{}".format(fn))
        exit(0)
    elif args.restore_backup:
        fn = lib.backup.restore_backup(extern_conf_dir, BASE)
        if fn is not None:
            print("Configuration has been restored from: \n{}".format(fn))
            print("Restart SmartHomeNG to use the restored configuration")
        exit(0)
    # check for pid file
    if lib.daemon.check_sh_is_running(PIDFILE):
        print("SmartHomeNG already running with pid {}".format(lib.daemon.read_pidfile(PIDFILE)))
        print("Run 'smarthome.py -s' to stop it or 'smarthome.py -r' to restart it.")
        exit()
    if MODE == 'debug':
        lib.daemon.write_pidfile(psutil.Process().pid, PIDFILE)
    # Starting SmartHomeNG
    sh = SmartHome(MODE=MODE, extern_conf_dir=extern_conf_dir)
    sh.start()

