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
import os
import sys
import psutil

def daemonize(pidfile,stdin='/dev/null', stdout='/dev/null', stderr=None):
    """
    This method domonizes the sh.py process and redirects standard file descriptors.
    
    @type   pidfile: string 
    @param  pidfile: Path to pidfile 
    @type   stdin  : string
    @param  stdin  : Path to new stdin, default value is "/dev/null"
    @type   stdout :
    @param  stdout : Path to new stdout, default value is "/dev/null"
    @type   stderr :
    @param  stderr : Path to new stderr, default value is None, but if stderr is None it is mapped to stdout
   
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


def remove_pidfile(pidfile: str):
    if os.path.exists(pidfile):
        os.remove(pidfile)


def write_pidfile(pid: int, pidfile: str):
    fd = open(pidfile, 'w+')
    fd.write("%s" % pid)
    fd.close()


def read_pidfile(pidfile: str) -> int:
    if os.path.isfile(pidfile):
        fd = open(pidfile,'r')
        line = fd.readline()
        return int(line)
    return 0


def check_sh_is_running(pidfile: str) -> bool:
    return psutil.pid_exists(read_pidfile(pidfile))


def kill(pidfile:str,waittime:int=10):
    pid = read_pidfile(pidfile)
    if psutil.pid_exists(pid):
        p = psutil.Process(pid)
        if p is not None:
            p.terminate()
            p.wait(timeout=waittime)
            if p.is_running():
               p.kill()