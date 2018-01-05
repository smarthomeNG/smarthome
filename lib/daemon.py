#!/usr/bin/env python3
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
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
This file contains the functions needed to run SmartHomeNG as a deamon
"""

import logging
import os
import sys
import psutil

logger = logging.getLogger(__name__)


def daemonize(pidfile,stdin='/dev/null', stdout='/dev/null', stderr=None):
    """
    This method domonizes the sh.py process and redirects standard file descriptors.
    
    :param pidfile: Path to pidfile 
    :param stdin: Path to new stdin, default value is "/dev/null"
    :param stdout: Path to new stdout, default value is "/dev/null"
    :param stderr: Path to new stderr, default value is None, but if stderr is None it is mapped to stdout
    :type pidfile: string 
    :type stdin: string
    :type stdout: string
    :type stderr: string
    """
    
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
            write_pidfile(pid, pidfile)
            sys.exit(0) 
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
    This method writes the PID to the pidfile.
    
    :param pid: PID of SmartHomeNG
    :param pidfile: Name of the pidfile to write to
    :type pid: int
    :type pidfile: str
    """
    
    fd = open(pidfile, 'w+')
    fd.write("%s" % pid)
    fd.close()


def read_pidfile(pidfile):
    """
    This method reads the pidfile and returns the PID.
    
    :param pidfile: Name of the pidfile to check
    :type pidfile: str
    
    :return: PID of SmartHomeNG or 0 if it is not running
    :rtype: int
    """
    
    if os.path.isfile(pidfile):
        fd = open(pidfile,'r')
        line = fd.readline()
        return int(line)
    return 0


def check_sh_is_running(pidfile):
    """
    This method deamonizes the sh.py process and redirects standard file descriptors.
    
    :param pidfile: Name of the pidfile to check
    :type pidfile: str
    
    :return: True: if SmartHomeNG is running, False: if SmartHome is not running
    :rtype: bool
    """
    
    pid = read_pidfile(pidfile)
    return psutil.pid_exists(pid) if pid > 0 and pid != os.getpid() else False


def kill(pidfile, waittime=15):
    """
    This method kills the process identified by pidfile.
    
    :param pidfile: Name of the pidfile identifying the process to kill
    :param waittime: Number of seconds to wait before killing the process
    :type pidfile: str
    :type waittime: int
    """

    pid = read_pidfile(pidfile)
    if psutil.pid_exists(pid):
        p = psutil.Process(pid)
        if p is not None:
            p.terminate()
            try:
                p.wait(timeout=waittime)
            except Exception as e:
                pass
            if p.is_running():
                logger.warning("Killing process")
                p.kill()
