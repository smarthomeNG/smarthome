#!/usr/bin/env python
# version: 0.4
# date:    2013-07-27
# author:  Joerg Raedler joerg@j-raedler.de
# license: BSD
# purpose: make RPC to a Sunny WebBox, a monitoring system for solar plants
#
# http://www.sma.de/en/produkte/monitoring-systems/sunny-webbox.html
#
# This python module provides a classes that can be used to communicate with a 
# Sunny WebBox. You can use the classes SunnyWebBoxHTTP and SunnyWebBoxUDPStream
# in your own code. 
#
# A small sample program is used if you run the module as a script. The hostname 
# or address must be provided as a parameter.
#
#   Example: python SunnyWebBox.py 123.123.123.123
#    
# Use the --help switch to learn about options for the udp mode and password.

import sys, json, hashlib
import argparse

# handle python 2 and 3
if sys.version_info >= (3, 0):
    py3 = True
    def str2buf(s):
        return bytes(s, 'latin1')
    def buf2str(b):
        return str(b, 'latin1')
else:
    py3 = False
    def str2buf(s):
        return bytes(s)
    def buf2str(b):
        return unicode(b, 'latin1')

class Counter:
    """generate increasing numbers with every call - just for convenience"""

    def __init__(self, start=0):
        self.i = start

    def __call__(self):
        i = self.i
        self.i += 1
        return i

class SunnyWebBoxBase(object):
    """Communication with a 'Sunny WebBox', a monitoring system for solar plants.
       This is an abstract base class, please use SunnyWebBoxHTTP or
       SunnyWebBoxUDPStream instead!
    """

    def __init__(self, host='1.2.3.4', password=''):
        self.host = host
        if password:
            self.pwenc = hashlib.md5(password).hexdigest()
        else:
            self.pwenc = ''
        self.count = Counter(1)
        self.openConnection()

    def openConnection(self):
        raise Exception('Abstract base class, use child class instead!')

    def newRequest(self, name='GetPlantOverview', withPW=False, **params):
        """return a new rpc request structure (dictionary)"""
        r = {'version': '1.0', 'proc': name, 'format': 'JSON'}
        r['id'] = str(self.count())
        if withPW:
            r['passwd'] = self.pwenc
        if params:
            r['params'] = params
        return r

    def _rpc(self, *args):
        raise Exception('Abstract base class, use child class instead!')

    def printOverview(self):
        """print a short overview of the plant data"""
        for v in self.getPlantOverview():
            print("%15s (%15s): %s %s" % 
                (v['name'], v['meta'], v['value'], v['unit']))

    # wrapper methods for the RPC functions

    def getPlantOverview(self):
        res = self._rpc(self.newRequest('GetPlantOverview'))
        return res['overview']

    def getDevices(self):
        res = self._rpc(self.newRequest('GetDevices'))
        return res['devices']

    def getProcessDataChannels(self, deviceKey):
        res = self._rpc(self.newRequest('GetProcessDataChannels', device=deviceKey))
        return res[deviceKey]

    def getProcessData(self, channels):
        res = self._rpc(self.newRequest('GetProcessData', devices=channels))
        # reorder data structure: {devKey: {dict of channels}, ...}
        # return {l['key']: l['channels'] for l in res['devices']}
        r = {}
        for l in res['devices']:
            r[l['key']] = l['channels']
        return r

    def getParameterChannels(self, deviceKey):
        res = self._rpc(self.newRequest('GetParameterChannels', withPW=True, device=deviceKey))
        return res[deviceKey]

    def getParameter(self, channels):
        res = self._rpc(self.newRequest('GetParameter', withPW=True, devices=channels))
        # reorder data structure: {devKey: {dict of channels}, ...}
        # return {l['key']: l['channels'] for l in res['devices']}
        r = {}
        for l in res['devices']:
            r[l['key']] = l['channels']
        return r

    def setParameter(self, *args):
        raise Exception('Not yet implemented!')

class SunnyWebBoxHTTP(SunnyWebBoxBase):
    """Communication with a 'Sunny WebBox' via HTTP."""

    def openConnection(self):
        if py3:
            from http.client import HTTPConnection
        else:
            from httplib import HTTPConnection
        self.conn  = HTTPConnection(self.host)

    def _rpc(self, request):
        """send an rpc request as JSON object via http and read the result"""
        js = json.dumps(request)
        self.conn.request('POST', '/rpc', "RPC=%s" % js)
        tmp = buf2str(self.conn.getresponse().read())
        response = json.loads(tmp)
        if response['id'] != request['id']:
            raise Exception('RPC answer has wrong id!')
        return response['result']

class SunnyWebBoxUDPStream(SunnyWebBoxBase):
    """Communication with a 'Sunny WebBox' via UDP Stream."""

    def openConnection(self):
        from socket import socket, AF_INET, SOCK_DGRAM
        self.udpPort = 34268
        self.ssock = socket(AF_INET, SOCK_DGRAM)
        self.rsock = socket(AF_INET, SOCK_DGRAM)
        self.rsock.bind(("", self.udpPort))
        self.rsock.settimeout(100.0)

    def _rpc(self, request):
        """send an rpc request as JSON object via UDP Stream and read the result"""
        js = ''.join(i+'\0' for i in json.dumps(request, separators=(',',':')))
        self.ssock.sendto(str2buf(js), (self.host, self.udpPort))
        while True:
            data, addr = self.rsock.recvfrom(10*1024)
            if addr[0] == self.host:
                break
        tmp = buf2str(data).replace('\0', '')
        response = json.loads(tmp)
        if response['id'] != request['id']:
            raise Exception('RPC answer has wrong id!')
        return response['result']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SunnyWebBox API - CLI query')
    parser.add_argument('host', help='host name or adress')
    parser.add_argument('-u', '--udp', action='store_true', help='use UDP mode instead of default HTTP mode')
    parser.add_argument('-p', '--password', action='store', help='password', default='')
    args = parser.parse_args()

    if args.udp:
        swb = SunnyWebBoxUDPStream(args.host, password=args.password)
    else:
        swb = SunnyWebBoxHTTP(args.host, password=args.password)

    print('###### Overview:')
    swb.printOverview()

    for d in swb.getDevices():
        devKey = d['key']
        print("\n  #### Device %s (%s):" % (devKey, d['name']))

        print("\n    ## Process data:")
        channels = swb.getProcessDataChannels(devKey)
        data = swb.getProcessData([{'key':devKey, 'channels':channels}])
        for c in data[devKey]:
           print("      %15s (%15s): %s %s" % 
               (c['name'], c['meta'], c['value'], c['unit']))

        print("\n    ## Parameters:")
        channels = swb.getParameterChannels(devKey)
        data = swb.getParameter([{'key':devKey, 'channels':channels}])
        for c in data[devKey]:
            print("      %15s (%15s): %s %s" % 
                (c['name'], c['meta'], c['value'], c['unit']))
