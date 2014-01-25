 #!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2014 Stephan Schaade          http://knx-user-forum.de/
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
import threading
import socket
import time
import colorsys


logger = logging.getLogger('')


class milight():

    # UDP Broadcast if IP not specified
    def __init__(self, smarthome, udp_ip='255.255.255.255', udp_port='8899', hue_calibrate ='0', white_calibrate='0', bri = 'true' , off = '10'):
        self._sh = smarthome
        self.udp_ip = udp_ip
        self.hue_calibrate = hue_calibrate
        self.white_calibrate = white_calibrate
        self.udp_port = udp_port
        self.bricontrol = bri
        self.cutoff = off
        self.color_map = {             # for reference and future use
            'violet': 0x00,
            'royal_blue': 0x10,
            'baby_blue': 0x20,
            'aqua': 0x30,
            'mint': 0x40,
            'seafoam_green': 0x50,
            'green': 0x60,
            'lime_green': 0x70,
            'yellow': 0x80,
            'yellow_orange': 0x90,
            'orange': 0xA0,
            'red': 0xB0,
            'pink': 0xC0,
            'fusia': 0xD0,
            'lilac': 0xE0,
            'lavendar': 0xF0
        }

        self.on_all = bytearray([0x42, 0x00, 0x55])
        self.on_ch1 = bytearray([0x45, 0x00, 0x55])
        self.on_ch2 = bytearray([0x47, 0x00, 0x55])
        self.on_ch3 = bytearray([0x49, 0x00, 0x55])
        self.on_ch4 = bytearray([0x4B, 0x00, 0x55])

        self.off_all = bytearray([0x41, 0x00, 0x55])
        self.off_ch1 = bytearray([0x46, 0x00, 0x55])
        self.off_ch2 = bytearray([0x48, 0x00, 0x55])
        self.off_ch3 = bytearray([0x4A, 0x00, 0x55])
        self.off_ch4 = bytearray([0x4C, 0x00, 0x55])

        self.white_ch1 = bytearray([0xC5, 0x00, 0x55])
        self.white_ch2 = bytearray([0xC7, 0x00, 0x55])
        self.white_ch3 = bytearray([0xC9, 0x00, 0x55])
        self.white_ch4 = bytearray([0xCB, 0x00, 0x55])

        self.brightness = bytearray([0x4E, 0x00, 0x55])
        self.color = bytearray([0x40, 0x00, 0x55])

        self.max_bright = bytearray([0x4E, 0x3B, 0x55])
        self.discoon = bytearray([0x4D, 0x00, 0x55])
        self.discoup = bytearray([0x44, 0x00, 0x55])
        self.discodown = bytearray([0x43, 0x00, 0x55])

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def send(self, data_s):
        # UDP sent without further encoding
        try:
            family, type, proto, canonname, sockaddr = socket.getaddrinfo(
                self.udp_ip, self.udp_port)[0]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data_s, (sockaddr[0], sockaddr[1]))
            sock.close()
            del(sock)
        except Exception as e:
            logger.warning(
                "miLight UDP: Problem sending data to {}:{}: ".format(self.udp_ip, self.udp_port, e))
            pass
        else:
            logger.debug("miLight UDP: Sending data to {}:{}:{} ".format(
                self.udp_ip, self.udp_port, data_s))

    # on/off switch function  - to switch on off anused before update  brightness / color / disco
    def switch(self, group, value):

        if group == 0:             # group 0 represents all groups
            if value == 0:
                data_s = self.off_all
            else:
                data_s = self.on_all

        if group == 1:
            if value == 0:
                data_s = self.off_ch1
            else:
                data_s = self.on_ch1

        if group == 2:
            if value == 0:
                data_s = self.off_ch2
            else:
                data_s = self.on_ch2

        if group == 3:
            if value == 0:
                data_s = self.off_ch3
            else:
                data_s = self.on_ch3

        if group == 4:
            if value == 0:
                data_s = self.off_ch4
            else:
                data_s = self.on_ch4

        self.send(data_s)           # call UDP send
        
    # dimmer function  - 2nd command after switch (on)
    def dim(self, group, value):

        time.sleep(0.1)             # wait 100 ms
        logger.info(value)
        value = int(value / 8.0)      # for compliance with KNX DPT5
        logger.info(value)
        data_s = self.brightness
        data_s[1] = value           # set Brightness
        self.send(data_s)           # call UDP to send WHITE if switched on
        
    # color function  
    def col(self, group, value):

        if group == 0:              # group 0 represents all groups
            data_s = self.on_all

        if group == 1:
            data_s = self.on_ch1

        if group == 2:
            data_s = self.on_ch2

        if group == 3:
            data_s = self.on_ch3

        if group == 4:
            data_s = self.on_ch4

        self.send(data_s)           # call UDP send   to switch on/off

        time.sleep(0.1)             # wait 100 ms

        data_s = self.color
        data_s[1] = value           # set Color
        self.send(data_s)           # call UDP to send WHITE if switched on
        
    # white function  - 2nd command after switch (on)
    def white(self, group, value):

        time.sleep(0.1)               # wait 100 ms

        if value == 1:
            if group == 1:
                data_s = self.white_ch1
            if group == 2:
                data_s = self.white_ch2
            if group == 3:
                data_s = self.white_ch3
            if group == 4:
                data_s = self.white_ch3
            self.send(data_s)        # call UDP to send WHITE if switched on

    # disco function  - 2nd command after switch (on)
    def disco(self, group, value):
        value = 1                     # Avoid switch off
        logger.info("disco")
        time.sleep(0.1)               # wait 100 ms

        data_s = self.discoon
        logger.info(data_s)
        self.send(data_s)
        
    # disco speed up  - 2nd command after switch (on)
    def disco_up(self, group, value):
        value = 1                      # Avoid switch off
        logger.info("disco up")
        time.sleep(0.1)               # wait 100 ms

        data_s = self.discoup
        logger.info(data_s)
        self.send(data_s) 
        
    # disco speed down - 2nd command after switch (on)
    def disco_down(self, group, value):
        value = 1
        logger.info("disco down")      # Avoid switch off

        time.sleep(0.1)               # wait 100 ms

        data_s = self.discodown
        logger.info(data_s)
        self.send(data_s)
        
        
        
    # rgb calculation
    def huecalc(self, value):
        offset = 0.3 + float(self.hue_calibrate)
  
        re= value[0] / (255.0)
        gn= value[1] / (255.0)
        bl= value[2] / (255.0)


    # trying HLS model for brightnes optimization
        hls =  colorsys.rgb_to_hls(re, gn, bl)
        self.hue =  hls[0]+offset
        if self.hue > 1:
            self.hue = self.hue - 1
           
        self.hue = int((1-self.hue)*255)  
        self.lum = hls[1] *255
        self.sat =  hls[1]
         
       


    def stop(self):
        self.alive = False
        
    # check function to change
    def parse_item(self, item):
        if 'milight_sw' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_dim' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_col' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_white' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_disco' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_disco_up' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_disco_down' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item
        if 'milight_rgb' in item.conf:
            logger.debug("parse item: {0}".format(item))
            return self.update_item    

        else:
            return None

    def parse_logic(self, logic):
        if 'milight' in logic.conf:
            # self.function(logic['name'])
            pass
            
    # update
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'milight':
            logger.info("miLight update item: {0}".format(item.id()))

            if 'milight_sw' in item.conf:
                for channel in item.conf['milight_sw']:
                    logger.info("miLight switching channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())

            if 'milight_dim' in item.conf:
                for channel in item.conf['milight_dim']:
                    logger.info("miLight dimming channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())
                    self.dim(group, item())

            if 'milight_col' in item.conf:
                for channel in item.conf['milight_col']:
                    logger.info("miLight HUE channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.col(group, item())

            if 'milight_white' in item.conf:
                for channel in item.conf['milight_white']:
                    logger.info("miLight set white channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())
                    self.white(group, item())

            if 'milight_disco' in item.conf:
                for channel in item.conf['milight_disco']:
                    logger.info("miLight disco channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())
                    self.disco(group, item())

            if 'milight_disco_up' in item.conf:
                for channel in item.conf['milight_disco_up']:
                    logger.info("miLight increase disco speed channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())
                    self.disco_up(group, item())

            if 'milight_disco_down' in item.conf:
                for channel in item.conf['milight_disco_down']:
                    logger.info("miLight decrease disco speed channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    self.switch(group, item())
                    self.disco_down(group, item())
                    
            if 'milight_rgb' in item.conf:
                for channel in item.conf['milight_rgb']:
                    logger.info("miLight RGB input for  channel: {0}".format(channel))
                    group = int(channel)
                    #logger.info(item())
                    
                    self.switch(group, 1)
                    self.huecalc (item())
                    logger.info("miLight HUE: {0}".format(self.hue))
                    logger.info("miLight LUM: {0}".format(self.lum))
                    calibrate = 178 + int(self.white_calibrate)
                    if self.hue == calibrate:
                            self.white (group,1)
                    else: 
                            self.col(group, self.hue)
                    if self.bricontrol:
                        if self.lum <= self.cutoff:
                            self.switch(group, 0)
                        else:
                            self.switch(group, 1)
                            self.dim(group, self.lum)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = milight('smarthome-dummy')
    myplugin.run()
Enter file contents here
