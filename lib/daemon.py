#!/usr/bin/env python3
#########################################################################
#  Copyright 2013 Marcus Popp                              marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import signal
import time
import os

logger = logging.getLogger('')


def daemonize():
    pid = os.fork()  # fork first child
    if pid == 0:
        os.setsid()
        pid = os.fork()  # fork second child
        if pid == 0:
            os.chdir('/')
        else:
            time.sleep(0.1)
            os._exit(0)  # exit parent
    else:
        time.sleep(0.1)
        os._exit(0)  # exit parent
    # close files
    for fd in range(0, 1024):
        try:
            os.close(fd)
        except OSError:
            pass
    # redirect I/O
    os.open(os.devnull, os.O_RDWR)  # input
    os.dup2(0, 1)  # output
    os.dup2(0, 2)  # error


def get_pid(filename):
    cpid = str(os.getpid())
    for pid in os.listdir('/proc'):
        if pid.isdigit() and pid != cpid:
            try:
                with open('/proc/{}/cmdline'.format(pid), 'r') as f:
                    cmdline = f.readline()
                    if filename in cmdline:
                        if cmdline.startswith('python'):
                            return int(pid)
            except:
                pass
    return 0


def kill(filename, wait=10):
    pid = get_pid(filename)
    delay = 0.25
    waited = 0
    if pid:
        os.kill(pid, signal.SIGTERM)
        while waited < wait:
            try:
                os.kill(pid, 0)
            except OSError:
                os._exit(0)
            waited += delay
            time.sleep(delay)
        try:
            print("Killing {}".format(os.path.basename(filename)))
            os.kill(pid, signal.SIGKILL)
        except OSError:
            os._exit(0)
