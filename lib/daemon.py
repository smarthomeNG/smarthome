#!/usr/bin/env python3
#########################################################################
# Copyright 2016-     Christian Strassburg            c.strassburg@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#  https://github.com/smarthomeNG/smarthome
#
#  SmartHomeNG.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
This file contains the functions needed to run SmartHomeNG as a daemon
"""

import logging
import os
import sys
import psutil
import errno
import portalocker

logger = logging.getLogger(__name__)


def daemonize(pidfile,stdin='/dev/null', stdout='/dev/null', stderr=None):
    """
    This method daemonizes the sh.py process and redirects standard file descriptors.

    :param pidfile: Path to pidfile
    :param stdin: Path to new stdin, default value is "/dev/null"
    :param stdout: Path to new stdout, default value is "/dev/null"
    :param stderr: Path to new stderr, default value is None, but if stderr is None it is mapped to stdout
    :type pidfile: string
    :type stdin: string
    :type stdout: string
    :type stderr: string
    """
    if os.name == 'nt':
        return

    # use stdout file if stderr is none
    if (not stderr):
        stderr = stdout

    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as  e:
        print("fork #1 failed: %d (%s)" % (e.errno, e.strerror) , file=sys.stderr)
        sys.exit(1)

    # decouple from parent environment
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            print ("Daemon PID %d" % pid )
            sys.exit(0)
        else:
            write_pidfile(os.getpid(), pidfile)

    except OSError as  e:
        print("fork #2 failed: %d (%s)" % (e.errno, e.strerror) , file=sys.stderr)
        sys.exit(1)

    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+')
    os.close(sys.stdin.fileno())
    os.close(sys.stdout.fileno())
    os.close(sys.stderr.fileno())
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def remove_pidfile(pidfile):
    """
    This method removes the pidfile.

    :param pidfile: Name of the pidfile to write to
    :type pidfile: str
    """

    if os.path.exists(pidfile):
        os.remove(pidfile)


def write_pidfile(pid, pidfile):
    """
    This method writes the PID to the pidfile and locks it while the process is running.

    :param pid: PID of SmartHomeNG
    :param pidfile: Name of the pidfile to write to
    :type pid: int
    :type pidfile: str
    """
    if os.name == 'nt':
        return

    with open(pidfile, 'w+') as fh:
        fh.write("%s" % pid)

    global _pidfile_handle
    try:
        _pidfile_handle = open(pidfile, 'r')
        #print(f"_pidfile_handle = '{_pidfile_handle}'")
        # LOCK_EX - acquire an exclusive lock
        # LOCK_NB - non blocking
        portalocker.lock(_pidfile_handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
    # don't close _pidfile_handle or lock is gone!!!
    except portalocker.AlreadyLocked as e:
        print("Could not lock pid file: %d (%s)" % (e.errno, e.strerror) , file=sys.stderr)


def read_pidfile(pidfile):
    """
    This method reads the pidfile and returns the PID.

    :param pidfile: Name of the pidfile to check
    :type pidfile: str

    :return: PID of SmartHomeNG or 0 if it is not running
    :rtype: int
    """

    try:
        if os.path.isfile(pidfile):
            fd = open(pidfile,'r')
            line = fd.readline()
            pid = int(line)
            return pid
    except ValueError:
        logger.warning("PID could not be read, maybe a false write or a corrupt filesystem? Please check the file system ASAP!")
    return 0


def check_sh_is_running(pidfile):
    """
    This method checks whether another smarthome process process is already running.

    :param pidfile: Name of the pidfile to check
    :type pidfile: str

    :return: True: if SmartHomeNG is running, False: if SmartHome is not running
    :rtype: bool
    """

    pid = read_pidfile(pidfile)
    #print("daemon.check_sh_is_running: pidfile={}, pid={}, psutil.pid_exists(pid)={}".format(pidfile, pid, psutil.pid_exists(pid)))
    isRunning = False
    if pid > 0 and psutil.pid_exists(pid):
        #print("daemon.check_sh_is_running: pid={}, psutil.pid_exists(pid)={}".format(pid, psutil.pid_exists(pid)))
        try:
            fh = open(pidfile, 'r')
            # LOCK_EX - acquire an exclusive lock
            # LOCK_NB - non blocking
            portalocker.lock(fh, portalocker.LOCK_EX | portalocker.LOCK_NB)
            print("daemon.check_sh_is_running: portalocker.lock erfolgreich")
            # pidfile not locked, so sh is terminated
        except portalocker.LockException:
            isRunning = True
        finally:
            if fh:
                fh.close()
    return isRunning


def kill(pidfile, waittime=15):
    """
    This method kills the process identified by pidfile.

    :param pidfile: Name of the pidfile identifying the process to kill
    :param waittime: Number of seconds to wait before killing the process
    :type pidfile: str
    :type waittime: int
    """

    pid = read_pidfile(pidfile)
    if pid == 0:
        logger.error("A Process ID of 0 can not be killed, please kill SmartHomeNG manually")
    elif psutil.pid_exists(pid):
        logger.warning("Stopping SmartHomeNG, please wait...")
        p = psutil.Process(pid)
        if p is not None:
            p.terminate()
            try:
                p.wait(timeout=waittime)
            except Exception as e:
                pass
            if p.is_running():
                logger.warning("Trying to terminate SmartHomeNG timed out, killing process")
                p.kill()
                try:
                    p.wait(timeout=5)
                except Exception as e:
                    pass
    else:
        logger.warning("No instance of SmartHomeNG running")
