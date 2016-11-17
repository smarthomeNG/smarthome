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
from ctypes import c_short
from lib.model.smartplugin import SmartPlugin

logger = logging.getLogger('Systemair')

class Systemair(SmartPlugin):
    PLUGIN_VERSION = "1.3.0.1"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, smarthome, serialport, slave_address="1", update_cycle="30"):
        self._sh = smarthome
        self.instrument = None
        self.slave_address = int(slave_address)
        self._update_coil = {}
        self.serialport = serialport
        self.slave_address = slave_address
        minimalmodbus.TIMEOUT = 3
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        self._sh.scheduler.add(__name__, self._read_modbus, prio=5, cycle=int(update_cycle))
        self.my_reg_items = []
        self.mod_write_repeat = 20  # if port is already open, e.g on auto-update,
                                    # repeat mod_write attempt x times a 1 seconds
        self._lockmb = threading.Lock()    # modbus serial port lock
        self.init_serial_connection(self.serialport, self.slave_address)
        self._reg_sets = [{'name':'fan',	'range':range(101, 138+1)},
                          {'name':'heater',	'range':range(201, 221+1), 'scaled_signed':range(208, 218+1)},
                          {'name':'damper',	'range':range(301, 301+1)},
                          {'name':'rotor',	'range':range(351, 352+1)},
                          {'name':'week',	'range':range(401, 459+1)},
                          {'name':'system',	'range':range(501, 507+1)},
                          {'name':'clock',	'range':range(551, 557+1)},
                          {'name':'filter',	'range':range(601, 602+1)},
                          {'name':'VTC_defr',	'range':range(651, 654+1)},
                          {'name':'VTR_defr',	'range':range(671, 672+1)},
                          {'name':'dig_in',	'range':range(701, 709+1)},
                          {'name':'PCU_PB',	'range':range(751, 751+1)},
                          {'name':'alarms',	'range':range(801, 802+1)},
                          {'name':'demand',	'range':range(851, 859+1)},
                          {'name':'wireless',	'range':range(901, 1020+1)},]

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
            # System air documentation: FAN values starts with 101, but thats incorrect: register starts with 100

            for reg_set in self._reg_sets:
                if 'range_used' in reg_set:
                    read_regs = dict(zip(reg_set['range_used'], self.instrument.read_registers(
                                                                reg_set['range_used'].start -1,
                                                                reg_set['range_used'].stop - reg_set['range_used'].start,
                                                                functioncode = 3)))
                    if 'scaled_signed' in reg_set:
                        for scaled_reg in reg_set['scaled_signed']:
                            read_regs[scaled_reg] = c_short(read_regs[scaled_reg]).value / 10

                    for reg in reg_set['regs_used']:
                        for item in reg_set['regs_used'][reg]:
                            try:
                                item(read_regs[reg], 'systemair_value_from_bus', "Reg {}".format(reg))
                            except Exception as e:
                                logger.error("Modbus: Exception when updating {} {}".format(item, e))

            # get coils
            for coil_addr in self._update_coil:
                value = self.instrument.read_bit(coil_addr-1, functioncode=2)
                if value is not None:
                    for item in self._update_coil[coil_addr]:
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
            if self.has_iattr(item.conf, 'mod_write'):
                if self.to_bool(self.get_iattr_value(item.conf, 'mod_write')):
                    self._write_register_value(item)

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'systemair_regaddr'):
            modbus_regaddr = int(self.get_iattr_value(item.conf, 'systemair_regaddr'))
            logger.debug("systemair_value_from_bus: {0} connected to register {1:#04x}".format(item, modbus_regaddr))
            self.my_reg_items.append(item)
            for reg_set in self._reg_sets:
                if modbus_regaddr in reg_set['range']:

                    if not 'regs_used' in reg_set:
                        reg_set['regs_used'] = dict()
                    if not modbus_regaddr in reg_set['regs_used']:
                        reg_set['regs_used'][modbus_regaddr] = set()
                    reg_set['regs_used'][modbus_regaddr].add(item)

                    if 'range_used' in reg_set:
                        reg_set['range_used'] = range(min(reg_set['range_used'].start, modbus_regaddr), max(reg_set['range_used'].stop, modbus_regaddr + 1))
                    else:
                        reg_set['range_used'] = range(modbus_regaddr, modbus_regaddr + 1)
                    logger.debug("systemair: adding reg {} to reg_set {} {}".format(modbus_regaddr, reg_set['name'], reg_set['range_used']))
                    logger.debug("systemair: regs used: {}".format(reg_set['regs_used']))
                    break

        if self.has_iattr(item.conf, 'systemair_coiladdr'):
            modbus_coiladdr = int(self.get_iattr_value(item.conf, 'systemair_coiladdr'))
            logger.debug("systemair_value_from_bus: {0} connected to coil register {1:#04x}".format(item, modbus_coiladdr))
            if not modbus_coiladdr in self._update_coil:
                self._update_coil[modbus_coiladdr] = set()

            self._update_coil[modbus_coiladdr].add(item)

        return self.update_item

    def _write_register_value(self, item, repeat_count=0):
        try:
            logger.debug('writing register value')
            if not self.has_iattr(item.conf, 'systemair_regaddr'):
                logger.error('Could not write to modbus. Register address missing!')
                return
            # BUG in Systemair docu, register starts with 100, not 101
            reg_addr = int(self.get_iattr_value(item.conf, 'systemair_regaddr')) - 1
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
