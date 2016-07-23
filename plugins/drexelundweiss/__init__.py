#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2014 KNX-User-Forum e.V. http://knx-user-forum.de/
#
# This file is part of SmartHome.py. http://mknx.github.io/smarthome/
#
# SmartHome.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SmartHome.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import threading
import serial
import os.path
import time


logger = logging.getLogger('')


class DuW():

    def __init__(self, smarthome, tty, LU_ID=130, WP_ID=140, Busmonitor=0):
        self._sh = smarthome
        self._LU_ID = LU_ID
        self._WP_ID = WP_ID
        self._cmd = False
        self.LUregl = {}
        self.WPregl = {}
        self.LUcmdl = {}
        self.WPcmdl = {}
        self.devl = {}
        self._is_connected = False
        self._lock = threading.Lock()
        self.busmonitor = Busmonitor
        self._pollservice = False

        self.devl[1] = {'device': 'aerosilent primus', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_primus.txt'}
        self.devl[2] = {'device': 'aerosilent topo', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_topo.txt'}
        self.devl[3] = {'device': 'aerosilent micro', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_micro.txt'}
        self.devl[4] = {'device': 'aerosmart s', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosmart_s.txt'}
        self.devl[5] = {'device': 'aerosmart m', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosmart_m.txt'}
        self.devl[6] = {'device': 'aerosmart l', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosmart_l.txt'}
        self.devl[7] = {'device': 'aerosmart xls', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosmart_xls.txt'}
        self.devl[8] = {'device': 'aerosilent centro', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_centro.txt'}
        self.devl[9] = {'device': 'termosmart sc', 'cmdpath':
                        smarthome.base_dir + '/plugins/drexelundweiss/termosmart_sc.txt'}
        self.devl[10] = {'device': 'x2', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/x2.txt'}
        self.devl[11] = {'device': 'aerosmart mono', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/aerosmart_mono.txt'}
        self.devl[13] = {'device': 'aerosilent bianco', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_bianco.txt'}
        self.devl[14] = {'device': 'x2 plus', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/x2_plus.txt'}
        self.devl[15] = {'device': 'aerosilent business', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_business.txt'}
        self.devl[17] = {'device': 'aerosilent stratos', 'cmdpath':
                         smarthome.base_dir + '/plugins/drexelundweiss/aerosilent_stratos.txt'}

        try:
            self._port = serial.Serial(tty, 115200, timeout=5)
        except:
            logger.error("DuW: could not open {}.".format(tty))
            return
        else:
            self._is_connected = True

        self._get_device_type()
        if self._cmd:
            self._load_cmd()

    def _get_device_type(self):
            self.alive = True
            if self._is_connected:
                (data, done) = self._read_register('LU\n', 5000, 1, 0)
                if done:
                    if data in self.devl:
                        logger.debug("DuW: device: " +
                                     self.devl[data]['device'])
                        if os.path.isfile(self.devl[data]['cmdpath']):
                            self._cmd = self.devl[data]['cmdpath']
                        else:
                            logger.error(
                                "DuW: no command file found at: " + self.devl[data]['cmdpath'])
                            self._cmd = False

                    else:
                        logger.error("DuW: device not supported: " + str(data))
                        self._cmd = False
                else:
                    logger.error("DuW: Error reading device type!")
                    self._cmd = False
            else:
                self._cmd = False
            self.alive = False

    def _send_DW(self, data, pcb):
        if not self._is_connected:
            return False

        if (pcb == 'LU\n'):
            device_ID = self._LU_ID
        elif(pcb == 'WP\n'):
            device_ID = self._WP_ID
        else:
            logger.error("wrong pcb description")
            return

        if not self._lock.acquire(timeout=2):
            return
        try:
            self._port.write((str(device_ID) + " " + data + "\r\n").encode())
        except Exception as e:
            logger.exception("Drexel: {0}".format(e))
        finally:
            self._lock.release()

    def _get_register_info(self, register, pcb):

        if (pcb == 'LU\n'):
            if register in self.LUcmdl:
                return self.LUcmdl[register]['reginfo']
            else:
                return False
        elif(pcb == 'WP\n'):
            if register in self.WPcmdl:
                return self.WPcmdl[register]['reginfo']
            else:
                return False
        else:
            logger.error("wrong pcb description")
            return

    def _load_cmd(self):
        f = open(self._cmd, "r")
        try:
            for line in f:
                if not self._lock.acquire(timeout=2):
                    return
                try:
                    row = line.split(";")
                    # skip first row
                    if (row[1] == "<Description>"):
                        pass
                    else:
                        if row[7] == 'LU\n':
                            self.LUcmdl[int(row[0])] = {'reginfo': row}
                        elif row[7] == 'WP\n':
                            self.WPcmdl[int(row[0])] = {'reginfo': row}
                        else:
                            logger.debug("DuW: Error in Commandfile: " + line)
                except Exception as e:
                    logger.exception("Drexel: {0}".format(e))
                finally:
                    self._lock.release()
        finally:
            f.close()

    def run(self):

        if not self._cmd:
            self.alive = False
            try:
                if self._is_connected:
                    self._port.close()
            except Exception as e:
                logger.exception(e)
            return

        self.alive = True

        # LU registers init
        for register in self.LUregl:
            reginfo = self.LUregl[register]['reginfo']
            divisor = int(reginfo[4])
            komma = int(reginfo[5])
            for item in self.LUregl[register]['items']:
                (data, done) = self._read_register(
                    reginfo[7], register, int(reginfo[4]), int(reginfo[5]))
                if done:
                    item(data, 'DuW', 'init process')
                else:
                    logger.debug("Drexel: Init LU register: " +
                                 str(register) + " failed!")

        # WP register init
        for register in self.WPregl:
            reginfo = self.WPregl[register]['reginfo']
            divisor = int(reginfo[4])
            komma = int(reginfo[5])
            for item in self.WPregl[register]['items']:
                (data, done) = self._read_register(
                    reginfo[7], register, int(reginfo[4]), int(reginfo[5]))
                if done:
                    item(data, 'DuW', 'init process')
                else:
                    logger.debug("Drexel: Init WP register: " +
                                 str(register) + " failed!")

        # poll DuW interface
        dw_id = 0
        dw_register = 0
        dw_data = 0
        response = bytes()
        self._pollservice = True
        self._port.flushInput()
        try:
            while self.alive:
                if self._port.inWaiting():
                    if not self._lock.acquire(timeout=2):
                        return
                    try:
                        response += self._port.read()
                        if (len(response) != 0):
                            if (response[-1] == 0x20 and dw_id == 0):
                                dw_id = int(response)
                                #logger.debug("Drexel dw_id: "+(str(dw_id)))
                                response = bytes()

                            elif (response[-1] == 0x20 and dw_id != 0 and dw_register == 0):
                                dw_register = int(response)
                                #logger.debug("Drexel dw_register: "+(str(dw_register)))
                                response = bytes()

                            elif (response[-1] == 0x0a):
                                dw_data = int(response)
                                #logger.debug("Drexel dw_data: "+(str(dw_data)))

                                if (self.busmonitor):
                                    if dw_id == self._LU_ID:
                                        if dw_register in self.LUcmdl:
                                            reginfo = self.LUcmdl[
                                                dw_register]['reginfo']
                                            divisor = int(reginfo[4])
                                            komma = int(reginfo[5])
                                            logger.debug("DuW Busmonitor LU register: " + str(dw_register)
                                                         + " " + str(reginfo[1]) + ": " + str(((dw_data / divisor) / (10 ** komma))))
                                        else:
                                            logger.debug(
                                                "DuW Busmonitor: unknown LU register: " + str(dw_register) + " " + str(dw_data))
                                    elif dw_id == self._WP_ID:
                                        if dw_register in self.WPcmdl:
                                            reginfo = self.WPcmdl[dw_register][
                                                'reginfo']
                                            divisor = int(reginfo[4])
                                            komma = int(reginfo[5])
                                            logger.debug("DuW Busmonitor WP register: " + str(dw_register)
                                                         + " " + str(reginfo[1]) + ": " + str(((dw_data / divisor) / (10 ** komma))))
                                        else:
                                            logger.debug(
                                                "DuW Busmonitor: unknown WP register: " + str(dw_register) + " " + str(dw_data))
                                    else:
                                        logger.debug(
                                            "DuW Busmonitor: unknown device ID: " + str(dw_id))

                                if dw_id == self._LU_ID:
                                    if dw_register in self.LUregl:
                                        reginfo = self.LUregl[
                                            dw_register]['reginfo']
                                        divisor = int(reginfo[4])
                                        komma = int(reginfo[5])
                                        for item in self.LUregl[dw_register]['items']:
                                            item(
                                                ((dw_data / divisor)
                                                 / (10 ** komma)),
                                                'DuW', 'Poll')
                                    else:
                                        logger.debug(
                                            "Ignore LU register " + str(dw_register))
                                elif dw_id == self._WP_ID:
                                    if dw_register in self.WPregl:
                                        reginfo = self.WPregl[
                                            dw_register]['reginfo']
                                        divisor = int(reginfo[4])
                                        komma = int(reginfo[5])
                                        for item in self.WPregl[dw_register]['items']:
                                            item(
                                                ((dw_data / divisor)
                                                 / (10 ** komma)),
                                                'DuW', 'Poll')
                                    else:
                                        logger.debug(
                                            "Ignore WP register " + str(dw_register))
                                else:
                                    logger.debug(
                                        "DuW Busmonitor: unknown device ID: " + str(dw_id))

                                dw_id = 0
                                dw_register = 0
                                dw_data = 0
                                response = bytes()
                        else:
                            response = bytes()
                            dw_id = 0
                            dw_register = 0
                            dw_data = 0
                            logger.debug("DuW read timeout: ")
                    except Exception as e:
                        logger.exception("Drexel: {0}".format(e))
                    finally:
                        self._lock.release()
                time.sleep(0.1)
            # exit poll service
            self._pollservice = False
        except Exception as e:
            logger.exception("Drexel: {0}".format(e))

    def stop(self):
        self.alive = False
        # wait until pollservice closed
        while self._pollservice == True:
            pass

        try:
            if self._is_connected:
                self._port.close()
        except Exception as e:
            logger.exception(e)

    def write_DW(self, pcb, register, value):
        self._send_DW("{0:d} {1:d}".format(int(register), int(value)), pcb)

    def req_DW(self, pcb, register):
        self._send_DW("{0:d}".format(int(register)), pcb)

    def _read_register(self, pcb, register, divisor, komma):
        if (pcb == 'LU\n'):
            device_ID = self._LU_ID
        elif(pcb == 'WP\n'):
            device_ID = self._WP_ID
        else:
            logger.error("wrong pcb description")

        self._port.flushInput()
        self.req_DW(pcb, str(register + 1))
        response = bytes()
        dw_id = 0
        dw_register = 0
        dw_data = 0
        if not self._lock.acquire(timeout=2):
            return
        try:
            while self.alive:
                response += self._port.read()
                if len(response) != 0:
                    if (response[-1] == 0x20 and dw_id == 0):
                        dw_id = int(response)
                     # logger.debug("Drexel dw_id: "+str(dw_id))
                        response = bytes()

                    elif response[-1] == 0x20 and dw_id != 0 and dw_register == 0:
                        dw_register = int(response)
                     # logger.debug("Drexel dw_register: "+str(dw_register))
                        response = bytes()

                    elif response[-1] == 0x0a:
                        dw_data = int(response)
                     # logger.debug("Drexel dw_data: "+str(dw_data))
                        break
                        response = bytes()
                else:
                    logger.debug("Drexel read timeout: ")
                    break
                time.sleep(0.1)
        except Exception as e:
            logger.warning("Drexel: {0}".format(e))
        finally:
            self._lock.release()

        if(dw_id == device_ID and (dw_register - 1) == register):
            #logger.debug("Drexel: Read {1} on Register: {0}".format(register,dw_data))
            return (((dw_data / divisor) / (10 ** komma)), 1)
        else:
            logger.error("DuW read errror Device ID: " + str(dw_id)
                         + " register: " + str(dw_register - 1))
            return (0, 0)

    def parse_item(self, item):
        if not self._cmd:
            return None
        if 'DuW_LU_register' in item.conf:
            register = int(item.conf['DuW_LU_register'])
            reginfo = self._get_register_info(register, 'LU\n')
            if reginfo:
                if not register in self.LUregl:
                    self.LUregl[register] = {'reginfo':
                                             reginfo, 'items': [item]}
                else:
                    if not item in self.LUregl[register]['items']:
                        self.LUregl[register]['items'].append(item)

                return self.update_item
            else:
                logger.warning("Drexel: LU register: " + str(register)
                               + " not supported by configured device!")
                return None
        if 'DuW_WP_register' in item.conf:
            register = int(item.conf['DuW_WP_register'])
            reginfo = self._get_register_info(register, 'WP\n')
            if reginfo:
                if not register in self.WPregl:
                    self.WPregl[register] = {'reginfo':
                                             reginfo, 'items': [item]}
                else:
                    if not item in self.WPregl[register]['items']:
                        self.WPregl[register]['items'].append(item)

                return self.update_item
            else:
                logger.warning("Drexel: WP register: " + str(register)
                               + " not supported by configured device!")
                return None

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'DuW':
            if 'DuW_LU_register' in item.conf:
                register = int(item.conf['DuW_LU_register'])
                if register in self.LUregl:
                    reginfo = self.LUregl[register]['reginfo']
                    data = item() * int(reginfo[4]) * (10 ** int(reginfo[5]))
                    if (data < int(reginfo[2]) or data > int(reginfo[3])):
                        logger.error("DuW: value of LU register: " +
                                     str(register) + " out of range, changes ignored!")
                        pass
                    else:
                        if reginfo[6] == 'R/W':
                            logger.debug("DuW: update LU register: " +
                                         str(register) + " " + reginfo[1] + " with: " + str(data))
                            self.write_DW(reginfo[7], register, data)
                        else:
                            logger.warning(
                                "DuW: tried to update read only LU register: " + str(register))
            if 'DuW_WP_register' in item.conf:
                register = int(item.conf['DuW_WP_register'])
                if register in self.WPregl:
                    reginfo = self.WPregl[register]['reginfo']
                    data = item() * int(reginfo[4]) * (10 ** int(reginfo[5]))
                    if (data < int(reginfo[2]) or data > int(reginfo[3])):
                        logger.error("DuW: value of WP register: " +
                                     str(register) + " out of range, changes ignored!")
                        pass
                    else:
                        if reginfo[6] == 'R/W':
                            logger.debug("DuW: update LU register: " +
                                         str(register) + " " + reginfo[1] + " with: " + str(data))
                            self.write_DW(reginfo[7], register, data)
                        else:
                            logger.warning(
                                "DuW: tried to update read only WP register: " + str(register))
