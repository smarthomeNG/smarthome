#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHome.py.   http://smarthome.sourceforge.net/
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
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import time
from smbus import SMBus

logger = logging.getLogger('')

class Plugin():

    def __init__(self, smarthome):
        self._sh = smarthome
        self.driver = I2CDriver()
        self.ports = {}
        self.items = []

    def run(self):
        self.alive = True
        while self.alive :
            self.driver.refresh()
            for item in self.items:
                port = self.ports[item.id()]
                if item._type == 'num':
                    item(port.read(), 'I2C')
                elif item._type == 'bool':
                    item(port.get(), 'I2C')                    
            time.sleep(0.1)

    def stop(self):
        self.alive = False

    def parse_item(self, item):        
        if 'i2c_chip_addr' in item.conf:
            if item._type == 'num' or item._type == 'bool':
                bus_address = int(item.conf['i2c_buss'], 0) if 'i2c_buss' in item.conf else 0                
                chip_address = int(item.conf['i2c_chip_addr'], 0)
                bit_offset = int(item.conf['i2c_bit_offset'], 0) if 'i2c_bit_offset' in item.conf else None
                chip = self.driver.get_chip(bus_address, chip_address);
                port = Port(chip, bit_offset)
                self.ports[item.id()] = port
                self.items.append(item)
                return self.update_item
            else:
                logger.warn('Only items of type [num] and [bool] are supported')

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None):        
        port = self.ports[item.id()]
        if item._type == 'num':
            port.write(item())
        elif item._type == 'bool':
            port.set(bool(item()))

class I2CDriver():        
    def __init__(self):
        self.busses = {}
        
    def get_bus(self, bus_address):
        if not bus_address in self.busses:
            self.busses[bus_address] = Bus(SMBus(bus_address))
        return self.busses[bus_address]
    
    def get_chip(self, bus_address, chip_address):
        bus = self.get_bus(bus_address)
        return bus.get_chip(chip_address)
    
    def refresh(self):
        for bus_address in self.busses:
            self.busses[bus_address].refresh()
        
class Bus():    
    def __init__(self, bus):
        self.bus = bus
        self.chips = {}
        
    def get_chip(self, chip_address):
        if not chip_address in self.chips:
            self.chips[chip_address] = Chip(self.bus, chip_address)
        return self.chips[chip_address]
    
    def refresh(self):
        for chip_address in self.chips:
            self.chips[chip_address].refresh()
    
class Chip():
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.data = 0
    
    def refresh(self):
        self.data = self.bus.read_byte(self.address)
        
    def read(self):
        return self.data
    
    def write(self, data):
        self.data = data    
        self.bus.write_byte(self.address, self.data)
            
class Port():    
    def __init__(self, chip, bit = None):
        self.chip = chip
        self.bit = bit
        
    def write(self, val):
        self.chip.write(val)
        
    def read(self):
        return self.chip.read()
    
    def on(self):
        if self.bit == None:
            logger.warn('Bit position should be provided for [on] command')
            return
        
        data = self.chip.read()
        data |= (1 << self.bit)
        self.chip.write(data)    
        
    def off(self):
        if self.bit == None:
            logger.warn('Bit position should be provided for [off] command')
            return
        
        data = self.chip.read()
        data &= ~(1 << self.bit)
        self.chip.write(data)    
    
    def toggle(self):
        if self.bit == None:
            logger.warn('Bit position should be provided for [toggle] command')
            return
        
        data = self.chip.read()
        data ^= (1 << self.bit)
        self.chip.write(data)    
                
    def set(self, val):    
        if self.bit == None:
            logger.warn('Bit position should be provided for [set] command')
            return
        
        if isinstance(val, bool):
            if val:
                self.on()
            else:
                self.off()
        else:
            logger.warn('Value should be of type boolean')
        
    def get(self):
        data = self.chip.read()
        return (data & (1 << self.bit) > 0)
        