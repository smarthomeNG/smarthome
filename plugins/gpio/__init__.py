#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2016 <Onkel Andy>                    <onkelandy@hotmail.com>
#########################################################################
#  This file is part of SmartHomeNG.   
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

import logging
from lib.model.smartplugin import SmartPlugin
import RPi.GPIO as GPIO
import threading
import time
from time import sleep

class Raspi_GPIO(SmartPlugin):
    PLUGIN_VERSION = "1.0.0"
    ALLOW_MULTIINSTANCE = False

    def _wait(self,time_lapse):
        time_start = time.time()
        time_end = (time_start + time_lapse)
     
        while time_end > time.time():
            pass

    def __init__(self, sh, cycle=0, mode="board"):
        self.logger = logging.getLogger(__name__)
        self._sh = sh
        self._items = []
        self._cycle = int(cycle)
        self._mode = mode.upper()
        GPIO.setwarnings(False)
        if self._mode == "BCM":
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)    
        self.logger.debug("GPIO: Mode set to {0}".format(self._mode))
        self.alive = False
        self._lock = threading.Lock() 
        

    def run(self):
        self.logger.debug("run method called")
        self.alive = True          
        if self._cycle > 0:
            self._sh.scheduler.add('Raspi_GPIO', self.get_sensors, prio=5, cycle=self._cycle)  
        else:
            self.logger.debug("GPIO: No Cycle defined, just running all the time.")
            self.get_sensors() 
            

    def stop(self):
        self.alive = False
        try:
            self._sh.scheduler.remove('Raspi_GPIO')
        except:
            self.logger.error("GPIO: Removing of scheduler failed: {}".format(sys.exc_info()))
        self._wait(2)
        GPIO.cleanup()
        

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'gpio_in'):
            in_pin = int(item.conf['gpio_in'])
            GPIO.setup(in_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.logger.debug("GPIO: INPUT {0} assigned to pin \'{1}\'".format(item, in_pin))
            self._items.append(item)
            return self.update_item      
        if self.has_iattr(item.conf, 'gpio_out'):
            out_pin = int(self.get_iattr_value(item.conf, 'gpio_out'))
            GPIO.setup(out_pin, GPIO.OUT)
            self.logger.debug("GPIO: OUTPUT {0} assigned to \'{1}\'".format(item, out_pin))
            if (out_pin is None):
                return None
                self.logger.debug("GPIO: No out_pin set")
            else:
                self._items.append(item)
                self.logger.debug("item: {0}".format(item))
            return self.update_item

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if self.has_iattr(item.conf, 'gpio_out'):
            out_pin = int(self.get_iattr_value(item.conf, 'gpio_out'))
            value = item()                   
            self.logger.debug("GPIO: OUTPUT Setting pin {0} ({2}) to {1}.".format(out_pin, value, item.id()))
            self.send(out_pin, value)
        else:
            self.logger.debug("GPIO: No gpio_out")

    def get_sensors(self):   
        if self._cycle > 0:
            try:
                for item in self._items:
                    if self.has_iattr(item.conf, 'gpio_in'):
                        sensor = int(self.get_iattr_value(item.conf, 'gpio_in')) 
                        value = GPIO.input(sensor)
                        item(value, 'GPIO', 'get_sensors')
                        self.logger.debug("GPIO SENSOR READ: {0}  VALUE: {1}".format(sensor,value))
                        self._wait(0.1)
                    if self.has_iattr(item.conf, 'gpio_out'):
                        sensor = int(self.get_iattr_value(item.conf, 'gpio_out'))
                        self.logger.debug("GPIO: Sensor {0} updated {1} seconds before".format(sensor,item.age()))
                        if item.age() >= 1:                             
                            value = GPIO.input(sensor)
                            item(value, 'GPIO', 'get_sensors')
                            self.logger.debug("GPIO: OUTPUT READ: {0}  VALUE: {1}".format(sensor,value))
                            self._wait(0.1)
            except Exception as e:
                self.logger.warning("GPIO ERROR: {0}".format(e))
        else:
            while self.alive:
                sleep(0.1)
                try:
                    for item in self._items:
                        if self.has_iattr(item.conf, 'gpio_in'):
                            sensor = int(self.get_iattr_value(item.conf, 'gpio_in')) 
                            value = GPIO.input(sensor)
                            item(value, 'GPIO', 'get_sensors')
                            self.logger.debug("GPIO: SENSOR READ: {0}  VALUE: {1}".format(sensor,value))
                            self._wait(0.1)
                        if self.has_iattr(item.conf, 'gpio_out'):
                            sensor = int(self.get_iattr_value(item.conf, 'gpio_out')) 
                            self.logger.debug("GPIO: Sensor {0} updated {1} seconds before".format(sensor,item.age()))
                            if item.age() >= 1:                                
                                value = GPIO.input(sensor)
                                item(value, 'GPIO', 'get_sensors')
                                self.logger.debug("GPIO: OUTPUT READ: {0}  VALUE: {1}".format(sensor,value))
                                self._wait(0.1)
                except Exception as e:
                    self.logger.warning("GPIO: ERROR: {0}".format(e))

    def send(self, pin, value):
        self._lock.acquire()
        try:
            GPIO.output(pin, value)
            self.logger.info("GPIO: Pin {0} successfully set to {1}".format(pin, value))
        except:
            self.logger.error("GPIO: Send {0} failed for {1}!".format(value, pin))
        finally:
            self._lock.release()                

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')
    FooClass(None).run()
