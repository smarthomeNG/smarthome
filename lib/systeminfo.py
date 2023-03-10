#!/usr/bin/env python3
# -*- coding: utf8 -*-
#########################################################################
#  Copyright 2023-      Martin Sinn                         m.sinn@gmx.de
#  Copyright 2016-      René Frieß                  rene.friess@gmail.com
#########################################################################
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import os
import logging
import sys
import platform
import subprocess

try:
    import utils
    import cpuinfo
except:
    import lib.utils as utils
    import lib.cpuinfo as cpuinfo

try:
    import lib.shyaml as shyaml
    yaml_support = True
except:
    yaml_support = False


def _run_and_get_stdout(command, pipe_command=None):
    from subprocess import Popen, PIPE

    # Run the command normally
    if not pipe_command:
        p1 = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    # Run the command and pipe it into another command
    else:
        p2 = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        p1 = Popen(pipe_command, stdin=p2.stdout, stdout=PIPE, stderr=PIPE)
        p2.stdout.close()

    # Get the stdout and stderr
    stdout_output, stderr_output = p1.communicate()
    stdout_output = stdout_output.decode(encoding='UTF-8')
    stderr_output = stderr_output.decode(encoding='UTF-8')

    return p1.returncode, stdout_output


def _get_field_actual(cant_be_number, raw_string, field_names):
    for line in raw_string.splitlines():
        for field_name in field_names:
            field_name = field_name.lower()
            if ':' in line:
                left, right = line.split(':', 1)
                left = left.strip().lower()
                right = right.strip()
                if left == field_name and len(right) > 0:
                    if cant_be_number:
                        if not right.isdigit():
                            return right
                    else:
                        return right

    return None

def _get_field(cant_be_number, raw_string, convert_to, default_value, *field_names):
    retval = _get_field_actual(cant_be_number, raw_string, field_names)

    # Convert the return value
    if retval and convert_to:
        try:
            retval = convert_to(retval)
        except Exception:
            retval = default_value

    # Return the default if there is no return value
    if retval is None:
        retval = default_value

    return retval


# ==========================================================================================

class Systeminfo:

    @classmethod
    def read_linuxinfo(cls):
        """
        Read info from /etc/os-release

        e.g.:
            PRETTY_NAME="Debian GNU/Linux 9 (stretch)"
            NAME="Debian GNU/Linux"
            VERSION_ID="9"
            VERSION="9 (stretch)"
            ID=debian
            HOME_URL="https://www.debian.org/"
            SUPPORT_URL="https://www.debian.org/support"
            BUG_REPORT_URL="https://bugs.debian.org/"

        or:
            PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"
            NAME="Raspbian GNU/Linux"
            VERSION_ID="10"
            VERSION="10 (buster)"
            VERSION_CODENAME=buster
            ID=raspbian
            ID_LIKE=debian
            HOME_URL="http://www.raspbian.org/"
            SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
            BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"

        """
        os_release = {}
        pf = platform.system().lower()
        if pf == 'linux':
            if os_release == {}:
                try:
                    with open('/etc/os-release') as fp:
                        for line in fp:
                            if line.startswith('#'):
                                continue
                            key, val = line.strip().split('=')
                            os_release[key] = val
                except:
                    os_release = {}
        return os_release


    @classmethod
    def read_macosinfo(cls):

        output = subprocess.Popen(["sw_vers", ], stdout=subprocess.PIPE).communicate()
        os, vers, build, extra = output[0].decode().split('\n')
        os = os.split('\t')[2]
        vers = vers.split('\t')[2]
        build = build.split('\t')[2]
        os_release = os + ' ' + vers + ' (build ' + build + ')'
        return os_release

    # ---------

    @classmethod
    def get_ostype(cls):
        pf = platform.system().lower()
        return pf


    @classmethod
    def get_osflavor(cls):
        pf = platform.system().lower()

        if pf == 'linux':
            os_release = cls.read_linuxinfo()
            if os_release == {}:
                return pf
            return os_release.get('ID', 'linux')
        else:
            return ''


    @classmethod
    def get_osname(cls):
        pf = platform.system().lower()

        if pf == 'linux':
            os_release = cls.read_linuxinfo()
            if os_release == {}:
                return pf
            return utils.Utils.strip_quotes(os_release.get('PRETTY_NAME', 'Linux'))
        elif pf == 'darwin':
            os_release = cls.read_macosinfo()
            return os_release
        else:
            return pf


    @classmethod
    def get_oskernelversion(cls):

        return getattr(platform.uname(),'release')


    @classmethod
    def get_osversion(cls):

        pf = platform.system().lower()

        if pf == 'linux':
            os_release = cls.read_linuxinfo()
            if os_release == {}:
                return pf
            return utils.Utils.strip_quotes(os_release.get('VERSION_ID', '?'))
        elif pf == 'darwin':
            return platform.platform().split('-')[1]
        else:
            return ''


    # ==========================================================================================

    cpuinfo_dict = None


    @classmethod
    def ensure_cpuinfo(cls):
        if cls.cpuinfo_dict is None:
            cls.cpuinfo_dict = cpuinfo.get_cpu_info()
        return


    @classmethod
    def get_cpuinfo(cls):
        cls.ensure_cpuinfo()
        return cls.cpuinfo_dict


    @classmethod
    def get_cpuarch(cls):
        cls.ensure_cpuinfo()
        return cls.cpuinfo_dict.get('arch_string_raw', '')
        #return cls.cpuinfo_dict.get('arch', '')


    @classmethod
    def get_cpubrand(cls):
        cls.ensure_cpuinfo()
        return cls.cpuinfo_dict.get('brand_raw', '')


    @classmethod
    def get_cpucores(cls):
        cls.ensure_cpuinfo()
        return cls.cpuinfo_dict.get('count', '')


    @classmethod
    def get_cpubits(cls):
        cls.ensure_cpuinfo()
        return cls.cpuinfo_dict.get('bits', '')


    @classmethod
    def get_cpu_speed(cls):
        if yaml_support:
            pass

        return None     # None = No previous measuremend stored


    @classmethod
    def check_cpu_speed(cls):
        if yaml_support:
            pass

        return

    # ==========================================================================================

    proc_cpuinfo = None


    @classmethod
    def ensure_proc_cpuinfo(cls):
        if os.path.exists('/proc/cpuinfo'):
            if cls.proc_cpuinfo is None:
                returncode, output = _run_and_get_stdout(['cat', '/proc/cpuinfo'])
                cls.proc_cpuinfo = output
        else:
            cls.proc_cpuinfo = ''


    @classmethod
    def running_on_rasppi(self):
        """
        Returns True, if running on a Raspberry Pi
        """
        if self.get_rasppi_revision() != '':
#            return self.cpu_info.get('revision_raw', '')
            return self.get_rasppi_revision()
        return ''


    @classmethod
    def get_rasppi_hardware(cls):
        cls.ensure_proc_cpuinfo()
        return _get_field(False, cls.proc_cpuinfo, None, '', 'Hardware')


    @classmethod
    def get_rasppi_revision(cls):
        cls.ensure_proc_cpuinfo()
        return _get_field(False, cls.proc_cpuinfo, None, '', 'Revision')


    @classmethod
    def get_rasppi_serial(cls):
        cls.ensure_proc_cpuinfo()
        return _get_field(False, cls.proc_cpuinfo, None, '', 'Serial')


    @classmethod
    def get_rasppi_info(cls):
        rev_info = {
            '0002'  : {'model': 'Model B Rev 1', 'ram': '256MB', 'revision': ''},
            '0003'  : {'model': 'Model B Rev 1 - ECN0001 (no fuses, D14 removed)', 'ram': '256MB', 'revision': ''},
            '0004'  : {'model': 'Model B Rev 2', 'ram': '256MB', 'revision': ''},
            '0005'  : {'model': 'Model B Rev 2', 'ram': '256MB', 'revision': ''},
            '0006'  : {'model': 'Model B Rev 2', 'ram': '256MB', 'revision': ''},
            '0007'  : {'model': 'Model A', 'ram': '256MB', 'revision': ''},
            '0008'  : {'model': 'Model A', 'ram': '256MB', 'revision': ''},
            '0009'  : {'model': 'Model A', 'ram': '256MB', 'revision': ''},
            '000d'  : {'model': 'Model B Rev 2', 'ram': '512MB', 'revision': ''},
            '000e'  : {'model': 'Model B Rev 2', 'ram': '512MB', 'revision': ''},
            '000f'  : {'model': 'Model B Rev 2', 'ram': '512MB', 'revision': ''},
            '0010'  : {'model': 'Model B+', 'ram': '512MB', 'revision': ''},
            '0013'  : {'model': 'Model B+', 'ram': '512MB', 'revision': ''},
            '900032': {'model': 'Model B+', 'ram': '512MB', 'revision': ''},
            '0011'  : {'model': 'Compute Modul', 'ram': '512MB', 'revision': ''},
            '0014'  : {'model': 'Compute Modul', 'ram': '512MB', 'revision': '', 'manufacturer': 'Embest, China'},
            '0012'  : {'model': 'Model A+', 'ram': '256MB', 'revision': ''},
            '0015'  : {'model': 'Model A+', 'ram': '256MB/512MB', 'revision': '', 'manufacturer': 'Embest, China'},
            #'0015' : {'model': 'Model A+', 'ram': '512MB', 'revision': '', 'manufacturer': 'Embest, China'},

            'a01041': {'model': 'Pi 2 Model B', 'ram': '1GB', 'revision': '1.1', 'manufacturer': 'Sony, UK'},
            'a21041': {'model': 'Pi 2 Model B', 'ram': '1GB', 'revision': '1.1', 'manufacturer': 'Embest, China'},
            'a22042': {'model': 'Pi 2 Model B', 'ram': '1GB', 'revision': '1.2'},
            '900092': {'model': 'Pi Zero v1.2', 'ram': '512MB', 'revision': '1.2'},
            '900093': {'model': 'Pi Zero v1.3', 'ram': '512MB', 'revision': '1.3'},
            '9000C1': {'model': 'Pi Zero W', 'ram': '512MB', 'revision': '1.1'},

            'a02082': {'model': 'Pi 3 Model B', 'ram': '1GB', 'revision': '1.2', 'manufacturer': 'Sony, UK'},
            'a22082': {'model': 'Pi 3 Model B', 'ram': '1GB', 'revision': '1.2', 'manufacturer': 'Embest, China'},
            'a020d3': {'model': 'Pi 3 Model B+', 'ram': '1GB', 'revision': '1.3', 'manufacturer': 'Sony, UK'},

            'a03111': {'model': 'Pi 4', 'ram': '1GB', 'revision': '1.1', 'manufacturer': 'Sony, UK'},
            'b03111': {'model': 'Pi 4', 'ram': '2GB', 'revision': '1.1', 'manufacturer': 'Sony, UK'},
            'b03112': {'model': 'Pi 4', 'ram': '2GB', 'revision': '1.2', 'manufacturer': 'Sony, UK'},
            'c03111': {'model': 'Pi 4', 'ram': '4GB', 'revision': '1.1', 'manufacturer': 'Sony, UK'},
            'c03112': {'model': 'Pi 4', 'ram': '4GB', 'revision': '1.2', 'manufacturer': 'Sony, UK'},
            'd03114': {'model': 'Pi 4', 'ram': '8GB', 'revision': '1.4', 'manufacturer': 'Sony, UK'},
        }
        if cls.get_rasppi_revision() != '':
            result = 'Raspberry '
            info = rev_info.get(cls.get_rasppi_revision(), {})
            if info == {}:
                return result + 'Pi (Rev. ' + cls.get_rasppi_revision() + ')'

            if info.get('model', ''):
                result += info.get('model', '')
            else:
                result += 'Pi'
            if info.get('revision', ''):
                result += ' v' + info.get('revision', '')
            if info.get('ram', ''):
                result += ', '+info.get('ram', '')
            if info.get('manufacturer', ''):
                result += ' (' + info.get('manufacturer', '') + ')'
            return result
        return ''


# ==========================================================================================

def main():
    #info = cpuinfo._get_cpu_info_internal()
    #print(type(info))

    print("lib.systeminfo")
    print()
    print(f"Platform           : {platform.platform()}")
    print(f"cpuinfo version    : {cpuinfo.CPUINFO_VERSION_STRING}")
    print()
    print('Operating System Info:')
    print(f"- OS Prettyname    : {Systeminfo.get_osname()}")
    print(f"- OS Type          : {Systeminfo.get_ostype()}")
    print(f"- Kernel Version   : {Systeminfo.get_oskernelversion()}")
    print(f"- OS Distribution  : {Systeminfo.get_osflavor()}")
    print(f"- OS/Distro Version: {Systeminfo.get_osversion()}")
    print()
    print('Hardware Info:')
    print(f"- CPU Architecture : {Systeminfo.get_cpuarch()}")
    print(f"- CPU Brand        : {Systeminfo.get_cpubrand()}")
    print(f"- Processor        : {Systeminfo.get_cpubits()}-bit")
    print(f"- Cores            : {Systeminfo.get_cpucores()}")
    print()
    print('SOC Info:')
    print(f"- Running on RaspPi: {Systeminfo.running_on_rasppi()}")
    print(f"- Hardware         : {Systeminfo.get_rasppi_hardware()}")
    print(f"- Revision         : {Systeminfo.get_rasppi_revision()}")
    print(f"- Serial           : {Systeminfo.get_rasppi_serial()}")
    print(f"- Board Model      : {Systeminfo.get_rasppi_info()}")
    print()

    Systeminfo.ensure_cpuinfo()
    import pprint
#    pprint.pprint(Systeminfo.get_cpuinfo())
#    print()
    return


if __name__ == '__main__':
    main()
#else:
#    _check_arch()
