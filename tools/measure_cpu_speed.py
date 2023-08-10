#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-       Martin Sinn                         m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
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

import timeit
import os
import sys
import platform

BASE = os.path.dirname(os.path.dirname(os.path.abspath(os.path.basename(__file__))))

VERSION = '0.1.0'


def measure():

    #return round(timeit.timeit('"|".join(str(i) for i in range(99999))', number=1000), 2)
    return round(timeit.timeit('"|".join(str(i) for i in range(50000))', number=1000), 2)

def read_cpuinfo():

    try:
        with open('/proc/cpuinfo') as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('model name'):
                print('cpu '+ line)
                break
    except:
        print("cpu model name\t: Could not determine cpu model - unable to read /proc/cpuinfo")
        print()


# ==================================================================================
#   Main Routine of the tool
#
if __name__ == '__main__':
    print('')
    print(os.path.basename(__file__) + ' v' + VERSION + ' - Check the cpu speed')
    print('')

    version = platform.python_version()
    print(f"Python version\t: {version}")
    print()

    read_cpuinfo()

    sys.stdout.write(f"test duration\t: ")
    sys.stdout.flush()
    print(f"{measure()} seconds")
    print()
