#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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
# coding: utf-8
"""
A pythonic library to discover and control Teufel Raumfeld speakers
"""

import socket
try:
    from urllib.parse import urlparse  # python3
except ImportError:
    from urlparse import urlparse      # python2
from pysimplesoap.client import SoapClient
from pysimplesoap.simplexml import SimpleXMLElement
from pysimplesoap.helpers import fetch
from pysimplesoap.transport import get_Http




import http
import logging
import lib.connection
import lib.tools
import os
import re
import socket
import threading



logger = logging.getLogger('')


__version__ = '0.2'
__all__ = ['discover', 'RaumfeldDevice']


class Raumfeld():

    def __init__(self, smarthome):
        self._sh = smarthome
        logger.debug("Raumfeld plugin init")
        
        self.discover()
        
        if len(self._devices) > 0:
                logger.info('found %s raumfeld devices' %len(self._devices))
        else:
                logger.info("no raumfeld device found")
                
        #Discover items from time to time / every minute
        self._sh.scheduler.add('Raumfeld Discover', self.discover, prio=5, cycle=60)

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)
        
    def stop(self):
        self.alive = False
        self.close()
        
    def discover(self):
        # discovery returns a list of RaumfeldDevices
        self._devices = discover(timeout=1, retries=1)
        logger.debug('Devices: %s' % self._devices)
        

    def parse_item(self, item):
        
        if 'device_name' in item.conf:
            return self.update_item
            
        if 'stream_url' in item.conf:
            return self.update_item
        
        return None

    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Raumfeld':  
            raumfeldDevice = None
            
            if self._devices is None:
                return None;
            
            for d in self._devices:
                logger.debug('its device: %s' %d)
                
                if d.friendly_name == item.conf['device_name']:
                    raumfeldDevice = d
                    logger.debug('found device: %s' %d)
                    break

            if raumfeldDevice is None:
                logger.debug('no raumfeld device specified. no device found by name %s' %deviceName)
                return None
                
            logger.debug('raumfeld device found')
            
            if True == item():
                logger.info('play stream %s' %item.conf['stream_url'])
                raumfeldDevice.av_transport.SetAVTransportURI(InstanceID=1,CurrentURI=item.conf['stream_url'],CurrentURIMetaData='')
                raumfeldDevice.play()
            else:
                logger.info('stop stream %s' %item.conf['stream_url'])
                raumfeldDevice.pause()
                return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = Raumfeld('smarthome-dummy')
    myplugin.run()

    
#Raumfeld Code von https://github.com/tfeldmann/python-raumfeld


def discover(timeout=1, retries=1):
    """Discover Raumfeld devices in the network

    :param timeout: The timeout in seconds
    :param retries: How often the search should be retried
    :returns: A list of raumfeld devices
    """
    locations = []

    group = ('239.255.255.250', 1900)
    service = 'ssdp:urn:schemas-upnp-org:device:MediaRenderer:1'  # 'ssdp:all'
    message = '\r\n'.join(['M-SEARCH * HTTP/1.1',
                           'HOST: {group[0]}:{group[1]}',
                           'MAN: "ssdp:discover"',
                           'ST: {st}',
                           'MX: 1', '', '']).format(group=group, st=service)

    socket.setdefaulttimeout(timeout)
    for _ in range(retries):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        # socket options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # send group multicast
        sock.sendto(message.encode('utf-8'), group)

        while True:
            try:
                response = sock.recv(2048).decode('utf-8')
                for line in response.split('\r\n'):
                    if line.startswith('Location: '):
                        location = line.split(' ')[1].strip()
                        if not location in locations:
                            locations.append(location)
            except socket.timeout:
                break
    devices = [RaumfeldDevice(location) for location in locations]

    # only return 'Virtual Media Player'
    return [device for device in devices
            if device.model_description == 'Virtual Media Player']


class RaumfeldDevice(object):

    def __init__(self, location):
        self.location = location

        # parse location url
        scheme, netloc, path, _, _, _ = urlparse(location)
        self.address = '%s://%s' % (scheme, netloc)

        # parse device description
        Http = get_Http()
        self.http = Http(timeout=1)
        xml = fetch(self.location, self.http)
        d = SimpleXMLElement(xml)
        self.friendly_name = str(next(d.device.friendlyName()))
        self.model_description = str(next(d.device.modelDescription()))
        self.model_name = str(next(d.modelName()))

        # set up soap clients
        self.rendering_control = SoapClient(
            location='%s/RenderingService/Control' % self.address,
            action='urn:upnp-org:serviceId:RenderingControl#',
            namespace='http://schemas.xmlsoap.org/soap/envelope/',
            soap_ns='soap', ns='s', exceptions=True)
        self.av_transport = SoapClient(
            location='%s/TransportService/Control' % self.address,
            action='urn:schemas-upnp-org:service:AVTransport:1#',
            namespace='http://schemas.xmlsoap.org/soap/envelope/',
            soap_ns='soap', ns='s', exceptions=True)

    def play(self):
        """Start playing"""
        self.av_transport.Play(InstanceID=1, Speed=2)

    def pause(self):
        """Pause"""
        self.av_transport.Pause(InstanceID=1)

    @property
    def volume(self):
        """get/set the current volume"""
        return self.rendering_control.GetVolume(InstanceID=1).CurrentVolume

    @volume.setter
    def volume(self, value):
        self.rendering_control.SetVolume(InstanceID=1, DesiredVolume=value)

    @property
    def mute(self):
        """get/set the current mute state"""
        response = self.rendering_control.GetMute(InstanceID=1, Channel=1)
        return response.CurrentMute == 1

    @mute.setter
    def mute(self, value):
        self.rendering_control.SetMute(InstanceID=1,
                                       DesiredMute=1 if value else 0)

    def __repr__(self):
        return ('<RaumfeldDevice(location="{0}", name="{1}")>'
                .format(self.location, self.friendly_name))

    def __str__(self):
        return self.friendly_name


if __name__ == '__main__':
    print('Library version %s' % __version__)
    devices = discover()
    print('Devices: %s' % devices)
    if len(devices) > 0:
        device = devices.pop()
        print('Volume: %s' % device.volume)
        print('Muted: %s' % device.mute)
    else:
        print('No Raumfeld devices found!')
