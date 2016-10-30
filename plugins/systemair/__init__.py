#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  Modbus plugin for SmartHome.py.       http://mknx.github.io/smarthome/
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
import logging
from time import sleep
import minimalmodbus
from serial import SerialException
import serial
import threading

logger = logging.getLogger('Systemair')

class Systemair():
    def __init__(self, smarthome, serialport, slave_address="1", update_cycle="30"):
        self._sh = smarthome
        self.instrument = None
        self.slave_address = int(slave_address)
        self._update = {}
        self._update_coil = {}
        self.serialport = serialport
        self.slave_address = slave_address
        minimalmodbus.TIMEOUT = 3
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        self._sh.scheduler.add('Modbus systemair', self._read_modbus, prio=5, cycle=int(update_cycle))
        self.my_reg_items = []
        self.mod_write_repeat = 20  # if port is already open, e.g on auto-update,
                                    # repeat mod_write attempt x times a 1 seconds
        self._lockmb = threading.Lock()    # modbus serial port lock

    def init_serial_connection(self, serialport, slave_address):
        try:
            if self.instrument is None:
                self.instrument = minimalmodbus.Instrument(serialport, int(slave_address))
            return True
        except:
            self.instrument = None
            logger.error("Failed to initialize modbus on {serialport}".format(serialport=serialport))
            return False

    def _read_modbus(self):
        self._lockmb.acquire()
        try:
            # check for working /dev/ttyXXX
            if not self.init_serial_connection(self.serialport, self.slave_address):
                return

            # read all fan registers
            # System air documentation: FAN values starts with 101, but thats incorrect: register starts with 100

            # Luefter / 38 Register
            start_register_fan = 101
            fan_registers = self.instrument.read_registers(start_register_fan-1, 38, functioncode=3)

            for register in fan_registers:
                if start_register_fan in self._update:
                    for item in self._update[start_register_fan]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_fan))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_fan += 1

            # Heater / 21 Register
            start_register_heater = 201
            heater_registers = self.instrument.read_registers(start_register_heater-1, 21, functioncode=3)
            for register in heater_registers:
                if start_register_heater in self._update:
                    for item in self._update[start_register_heater]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_heater))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_heater += 1

            # damper register | 1 register
            start_register_damper = 301
            damper_registers = self.instrument.read_registers(start_register_damper-1, 1, functioncode=3)
            for register in damper_registers:
                if start_register_damper in self._update:
                    for item in self._update[start_register_damper]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_damper))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_damper += 1

            # rotor register | 2 register
            start_register_rotor = 351
            rotor_registers = self.instrument.read_registers(start_register_rotor-1, 2, functioncode=3)
            for register in rotor_registers:
                if start_register_rotor in self._update:
                    for item in self._update[start_register_rotor]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_rotor))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_rotor += 1

            # week programm egister | 59 register
            start_register_week = 401
            week_registers = self.instrument.read_registers(start_register_week-1, 59, functioncode=3)
            for register in week_registers:
                if start_register_week in self._update:
                    for item in self._update[start_register_week]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_week))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_week += 1

            # system register / 7 register
            start_register_system = 501
            system_registers = self.instrument.read_registers(start_register_system-1, 7, functioncode=3)
            for register in system_registers:
                if start_register_system in self._update:
                    for item in self._update[start_register_system]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_system))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_system += 1

            # clock register / 7 register
            start_register_clock = 551
            clock_registers = self.instrument.read_registers(start_register_clock-1, 7, functioncode=3)
            for register in clock_registers:
                if start_register_clock in self._update:
                    for item in self._update[start_register_clock]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_clock))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_clock += 1

            # filter register / 2 register
            start_register_filter = 601
            filter_registers = self.instrument.read_registers(start_register_filter-1, 2, functioncode=3)
            for register in filter_registers:
                if start_register_filter in self._update:
                    for item in self._update[start_register_filter]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_filter))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_filter += 1

            # defrosting register for VTC / 4 register
            start_register_defrosting = 651
            defrosting_registers = self.instrument.read_registers(start_register_defrosting-1, 4, functioncode=3)
            for register in defrosting_registers:
                if start_register_defrosting in self._update:
                    for item in self._update[start_register_defrosting]['items']:
                        try:
                            item(register, 'Systemair', "Reg {}".format(start_register_defrosting))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_defrosting += 1

            # defrosting register for VR/VTR / 2 register
            start_register_defrosting_vtr = 671
            defrosting_registers_vtr = self.instrument.read_registers(start_register_defrosting_vtr-1, 2, functioncode=3)
            for register in defrosting_registers_vtr:
                if start_register_defrosting_vtr in self._update:
                    for item in self._update[start_register_defrosting_vtr]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_defrosting_vtr))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_defrosting_vtr += 1


            # digital input register / 9 register
            start_register_digital = 701
            digital_registers = self.instrument.read_registers(start_register_digital-1, 9, functioncode=3)
            for register in digital_registers:
                if start_register_digital in self._update:
                    for item in self._update[start_register_digital]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_digital))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_digital += 1

            # pcu / 1 Register
            start_register_pcb = 751
            pcb_registers = self.instrument.read_registers(start_register_pcb-1, 9, functioncode=3)
            for register in pcb_registers:
                if start_register_pcb in self._update:
                    for item in self._update[start_register_pcb]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_pcb))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_pcb += 1

            # demand control / 1 Register
            start_register_dem = 851
            dem_registers = self.instrument.read_registers(start_register_dem-1, 9, functioncode=3)
            for register in dem_registers:
                if start_register_dem in self._update:
                    for item in self._update[start_register_dem]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_dem))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_dem += 1

            # wireless network register
            start_register_net = 901
            net_registers = self.instrument.read_registers(start_register_net-1, 119, functioncode=3)
            for register in net_registers:
                if start_register_net in self._update:
                    for item in self._update[start_register_net]['items']:
                        try:
                            item(register, 'systemair_value_from_bus', "Reg {}".format(start_register_net))
                        except Exception as e:
                            logger.error("Modbus: Exception when updating {} {}".format(item, e))
                start_register_net += 1

            # get coils
            for coil_addr, val in self._update_coil.items():
                value = self.instrument.read_bit(coil_addr-1, functioncode=2)
                if value is not None:
                    for item in self._update_coil[coil_addr]['items']:
                        item(value, 'systemair_value_from_bus', "Coil {}".format(coil_addr))

        except Exception as err:
            logger.error(err)
            self.instrument = None
        finally:
            self._lockmb.release()

    def run(self):
        self.alive = True
        self.connect()

    def stop(self):
        self.alive = False

    def connect(self):
        logger.debug("systemair_value_from_bus: connect")

    def update_item(self, item, caller=None, source=None, dest=None):
        # ignore values from bus
        if caller == 'systemair_value_from_bus':
            return
        if item in self.my_reg_items:
            if 'mod_write' in item.conf:
                if self._get_bool(item.conf['mod_write']):
                    self._write_register_value(item)

    def parse_item(self, item):
        if 'systemair_regaddr' in item.conf:
            modbus_regaddr = int(item.conf['systemair_regaddr'])
            logger.debug("systemair_value_from_bus: {0} connected to register {1:#04x}".format(item, modbus_regaddr))
            if not modbus_regaddr in self._update:
                self._update[modbus_regaddr] = {'items': [item], 'logics': []}
            else:
                if not item in self._update[modbus_regaddr]['items']:
                    self._update[modbus_regaddr]['items'].append(item)
            # we need a small list here to make it easier to find our items if update_item is triggered
            self.my_reg_items.append(item) 

        if 'systemair_coiladdr' in item.conf:
            modbus_coiladdr = int(item.conf['systemair_coiladdr'])
            logger.debug("systemair_value_from_bus: {0} connected to coil register {1:#04x}".format(item, modbus_coiladdr))
            if not modbus_coiladdr in self._update_coil:
                self._update_coil[modbus_coiladdr] = {'items': [item], 'logics': []}
            else:
                if not item in self._update_coil[modbus_coiladdr]['items']:
                    self._update_coil[modbus_coiladdr]['items'].append(item)
        return self.update_item

    def _write_register_value(self, item, repeat_count=0):
        try:
            logger.debug('writing register value')
            if 'systemair_regaddr' not in item.conf:
                logger.error('Could not write to modbus. Register address missing!')
                return
            # BUG in Systemair docu, register starts with 100, not 101
            reg_addr = int(item.conf['systemair_regaddr']) - 1
            val = int(item())
            with self._lockmb:
                self.instrument.write_register(reg_addr, value=val)
        except serial.serialutil.SerialException as err:
            if err.args[0].lower() == 'port is already open.':
                if self.mod_write_repeat < repeat_count:
                    logger.error("Could not write register value to systemair modbus. Maximal retries reached.")
                    return
                repeat_count += 1
                logger.warning('Could not write register value to systemair modbus. Port is already open.')
                logger.warning('Repeat {rep} of {max}.'.format(rep=repeat_count, max=self.mod_write_repeat))
                sleep(1)
                self._write_register_value(item, repeat_count)
            pass
        except Exception as err:
            logger.error('Could not write register value to modbus. Error: {err}!'.format(err=err))
            self.instrument = None

    def _get_bool(self, val):
        try:
            val = bool(val)
            return val
        except:
            if val.lower() in ['1', 'true', 'on', 'yes']:
                return True
            return False
