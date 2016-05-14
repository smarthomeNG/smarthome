#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  iAQ-Stick plugin for SmartHome.py.    http://mknx.github.io/smarthome/
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

#/etc/udev/rules.d/99-iaqstick.rules
#SUBSYSTEM=="usb", ATTR{idVendor}=="03eb", ATTR{idProduct}=="2013", MODE="666"
#udevadm trigger

import logging
import usb.core
import usb.util
from time import sleep

logger = logging.getLogger('iAQ_Stick')

class iAQ_Stick():
    def __init__(self, smarthome, update_cycle = "10"):
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._items = {}
        self._devs = {}

    def read(self, dev):
        in_data = bytes()
        try:
            while True:
                ret = bytes(dev.read(0x81, 0x10, self._intf, 1000))
                if len(ret) == 0:
                    break
                in_data += ret
        except Exception as e:
            logger.error("iaqstick: read - {}".format(e))
            pass
        return in_data

    def xfer_type1(self, dev, msg):
        out_data = bytes('@{:04X}{}\n@@@@@@@@@@'.format(self._devs[dev]['type1_seq'], msg), 'utf-8')
        self._devs[dev]['type1_seq'] = (self._devs[dev]['type1_seq'] + 1) & 0xFFFF
        ret = dev.write(0x02, out_data[:16], self._intf, 1000)
        return self.read(dev).decode('iso-8859-1')

    def xfer_type2(self, dev, msg):
        out_data = bytes('@', 'utf-8') + self._devs[dev]['type2_seq'].to_bytes(1, byteorder='big') + bytes('{}\n@@@@@@@@@@@@@'.format(msg), 'utf-8')
        self._devs[dev]['type2_seq'] = (self._devs[dev]['type2_seq'] + 1) if (self._devs[dev]['type2_seq'] < 0xFF) else 0x67
        ret = dev.write(0x02, out_data[:16], self._intf, 1000)
        in_data = bytes()
        return self.read(dev)

    def _init_dev(self, dev):
        try:
            if dev.is_kernel_driver_active(self._intf):
                dev.detach_kernel_driver(self._intf)
            dev.set_configuration(0x01)
            usb.util.claim_interface(dev, self._intf)
            dev.set_interface_altsetting(self._intf, 0x00)
            vendor = usb.util.get_string(dev, 0x101, 0x01, 0x409)
            product = usb.util.get_string(dev, 0x101, 0x02, 0x409)
            self._devs[dev] = {'type1_seq':0x0001, 'type2_seq':0x67}
            ret = self.xfer_type1(dev, '*IDN?')
            pos1 = ret.find('S/N:') + 4
            id = '{:s}-{:d}'.format(bytes.fromhex(ret[pos1:pos1+12]).decode('ascii'), int(ret[pos1+14:pos1+20], 16))
            logger.info('iaqstick: Vendor: {} / Product: {} / Stick-ID: {}'.format(vendor, product, id))
            if (id not in self._items):
                logger.warning('iaqstick: no specific item for Stick-ID {} - use \'iaqstick_id\' to distinguish multiple sticks!'.format(id))
            #ret = self.xfer_type1(dev, 'KNOBPRE?')
            #ret = self.xfer_type1(dev, 'WFMPRE?')
            #ret = self.xfer_type1(dev, 'FLAGS?')
            return id
        except Exception as e:
            logger.error("iaqstick: init interface failed - {}".format(e))
            return None

    def run(self):
        devs = usb.core.find(idVendor=0x03eb, idProduct=0x2013, find_all=True)
        if devs is None:
            logger.error('iaqstick: iAQ Stick not found')
            return
        logger.debug('iaqstick: {} iAQ Stick connected'.format(len(devs)))
        self._intf = 0

        for dev in devs:
            id = self._init_dev(dev)
            if id is not None:
                self._devs[dev]['id'] = id

        self.alive = True
        self._sh.scheduler.add('iAQ_Stick', self._update_values, prio = 5, cycle = self._update_cycle)
        logger.info("iaqstick: init successful")

    def stop(self):
        self.alive = False
        for dev in self._devs:
            try:
                usb.util.release_interface(dev, self._intf)
                if dev.is_kernel_driver_active(self._intf):
                    dev.detach_kernel_driver(self._intf)
            except Exception as e:
                logger.error("iaqstick: releasing interface failed - {}".format(e))
        try:
            self._sh.scheduler.remove('iAQ_Stick')
        except Exception as e:
            logger.error("iaqstick: removing iAQ_Stick from scheduler failed - {}".format(e))

    def _update_values(self):
        logger.debug("iaqstick: updating {} sticks".format(len(self._devs)))
        for dev in self._devs:
            logger.debug("iaqstick: updating {}".format(self._devs[dev]['id']))
            try:
                self.xfer_type1(dev, 'FLAGGET?')
                meas = self.xfer_type2(dev, '*TR')
                ppm = int.from_bytes(meas[2:4], byteorder='little')
                logger.debug('iaqstick: ppm: {}'.format(ppm))
                #logger.debug('iaqstick: debug?: {}'.format(int.from_bytes(meas[4:6], byteorder='little')))
                #logger.debug('iaqstick: PWM: {}'.format(int.from_bytes(meas[6:7], byteorder='little')))
                #logger.debug('iaqstick: Rh: {}'.format(int.from_bytes(meas[7:8], byteorder='little')*0.01))
                #logger.debug('iaqstick: Rs: {}'.format(int.from_bytes(meas[8:12], byteorder='little')))
                id = self._devs[dev]['id']
                if id in self._items:
                    if 'ppm' in self._items[id]:
                        for item in self._items[id]['ppm']['items']:
                            item(ppm, 'iAQ_Stick', 'USB')
                if '*' in self._items:
                    if 'ppm' in self._items['*']:
                        for item in self._items['*']['ppm']['items']:
                            item(ppm, 'iAQ_Stick', 'USB')
            except Exception as e:
                logger.error("iaqstick: update failed - {}".format(e))
                logger.error("iaqstick: Trying to recover ...")
                broken_id = self._devs[dev]['id']
                del self._devs[dev]
                __devs = usb.core.find(idVendor=0x03eb, idProduct=0x2013, find_all=True)
                for __dev in __devs:
                    if (__dev not in self._devs):
                        id = self._init_dev(__dev)
                        if id == broken_id:
                            logger.error("iaqstick: {} was ressurrected".format(id))
                            self._devs[__dev]['id'] = id
                        else:
                            logger.error("iaqstick: found other yet unknown stick: {}".format(id))

    def parse_item(self, item):
        if 'iaqstick_info' in item.conf:
            logger.debug("parse item: {0}".format(item))
            if 'iaqstick_id' in item.conf:
                id = item.conf['iaqstick_id']
            else:
                id = '*'
            info_tag = item.conf['iaqstick_info'].lower()
            if not id in self._items:
                self._items[id] = {'ppm': {'items': [item], 'logics': []}}
            else:
                self._items[id]['ppm']['items'].append(item)
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = Plugin('iaqstick')
    myplugin.run()

#Application Version: 2.19.0 (Id: Form1.frm 1053 2010-06-30 11:00:09Z patrik.arven@appliedsensor.com )
#
#Device 0:
#Name: iAQ Stick
#Firmware: 1.12p5 $Revision: 346 $
#Protocol: 5
#Hardware: C
#Processor: ATmega32U4
#Serial number: S/N:48303230303415041020
#Web address:
#Plot title: Air Quality Trend
#
#Channels: 5
#... Channel 0:CO2/VOC level
#... Channel 1:Debug
#... Channel 2:PWM
#... Channel 3:Rh
#... Channel 4:Rs
#Knobs: 8
#... Knob CO2/VOC level_warn1:1000
#... Knob CO2/VOC level_warn2:1500
#... Knob Reg_Set:151
#... Knob Reg_P:3
#... Knob Reg_I:10
#... Knob Reg_D:0
#... Knob LogInterval:0
#... Knob ui16StartupBits:1
#Flags: 5
#... WARMUP=&h0000&
#... BURN-IN=&h0000&
#... RESET BASELINE=&h0000&
#... CALIBRATE HEATER=&h0000&
#... LOGGING=&h0000&
#
#@013E;;DEBUG:
#Log:
#buffer_size=&h1400;
#address_base=&h4800;
#readindex=&h0040;
#Write index=&h0000;
#nValues=&h0000;
#Records=&h0000;
#nValues (last)=&h0000;
#uint16_t g_u16_loop_cnt_100ms=&h08D4;
#;\x0A