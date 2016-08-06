#!/usr/bin/env python
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2012-2013 KNX-User-Forum e.V.       http://knx-user-forum.de/
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
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import sys
import serial
import logging
import socket
import threading
import struct
import time
import datetime
import array

logger = logging.getLogger("")

# Some "Constants"
CONST_BUSMEMBER_MAINBOARD     = 0x11
CONST_BUSMEMBER_SLAVEBOARDS   = 0x10
CONST_BUSMEMBER_CONTROLBOARDS = 0x20
CONST_BUSMEMBER_ME            = 0x2F #used as sender when communicating with the helios system
CONST_MAP_VARIABLES_TO_ID = {
        "outside_temp"    : {"varid" : 0x32, 'type': 'temperature',  'bitposition': -1, 'read': True, 'write': False },
        "exhaust_temp"    : {"varid" : 0x33, 'type': 'temperature',  'bitposition': -1, 'read': True, 'write': False },
        "inside_temp"     : {"varid" : 0x34, 'type': 'temperature',  'bitposition': -1, 'read': True, 'write': False },
        "incoming_temp"   : {"varid" : 0x35, 'type': 'temperature',  'bitposition': -1, 'read': True, 'write': False },
        "bypass_temp"     : {"varid" : 0xAF, 'type': 'temperature',  'bitposition': -1, 'read': True, 'write': True  },
        "fanspeed"        : {"varid" : 0x29, 'type': 'fanspeed',     'bitposition': -1, 'read': True, 'write': True  },
        "max_fanspeed"    : {"varid" : 0xA5, 'type': 'fanspeed',     'bitposition': -1, 'read': True, 'write': True  },
        "min_fanspeed"    : {"varid" : 0xA9, 'type': 'fanspeed',     'bitposition': -1, 'read': True, 'write': True  },
        "power_state"     : {"varid" : 0xA3, 'type': 'bit',          'bitposition':  0, 'read': True, 'write': True  },
        "bypass_disabled" : {"varid" : 0xA3, 'type': 'bit',          'bitposition':  3, 'read': True, 'write': True  }
    }
CONST_TEMPERATURE = array.array('i', [
                                -74,-70,-66,-62,-59,-56,-54,-52,-50,-48,-47,-46,-44,-43,-42,-41,-40,-39,-38,-37,-36,
                                -35,-34,-33,-33,-32,-31,-30,-30,-29,-28,-28,-27,-27,-26,-25,-25,-24,-24,-23,-23,-22,
                                -22,-21,-21,-20,-20,-19,-19,-19,-18,-18,-17,-17,-16,-16,-16,-15,-15,-14,-14,-14,-13,
                                -13,-12,-12,-12,-11,-11,-11,-10,-10,-9,-9,-9,-8,-8,-8,-7,-7,-7,-6,-6,-6,-5,-5,-5,-4,
                                -4,-4,-3,-3,-3,-2,-2,-2,-1,-1,-1,-1,0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5,5,6,6,6,7,7,
                                7,8,8,8,9,9,9,10,10,10,11,11,11,12,12,12,13,13,13,14,14,14,15,15,15,16,16,16,17,17,
                                18,18,18,19,19,19,20,20,21,21,21,22,22,22,23,23,24,24,24,25,25,26,26,27,27,27,28,28,
                                29,29,30,30,31,31,32,32,33,33,34,34,35,35,36,36,37,37,38,38,39,40,40,41,41,42,43,43,
                                44,45,45,46,47,48,48,49,50,51,52,53,53,54,55,56,57,59,60,61,62,63,65,66,68,69,71,73,
                                75,77,79,81,82,86,90,93,97,100,100,100,100,100,100,100,100,100])


class HeliosException(Exception):
    pass


class HeliosBase():

    def __init__(self, tty='/dev/ttyUSB0'):
        self._tty = tty
        self._is_connected = False
        self._port = False
        self._lock = threading.Lock()
     
    def connect(self):
        if self._is_connected and self._port:
            return True
            
        try:
            logger.debug("Helios: Connecting...")
            self._port = serial.Serial(
                self._tty, 
                baudrate=9600, 
                bytesize=serial.EIGHTBITS, 
                parity=serial.PARITY_NONE, 
                stopbits=serial.STOPBITS_ONE, 
                timeout=1)
            self._is_connected = True
            return True
        except:
            logger.error("Helios: Could not open {0}.".format(self._tty))
            return False
        
    def disconnect(self):
        if self._is_connected and self._port:
            logger.debug("HeliosBase: Disconnecting...")
            self._port.close()
            self._is_connected = False
            
    def _createTelegram(self, sender, receiver, function, value):
        telegram = [1,sender,receiver,function,value,0]
        telegram[5] = self._calculateCRC(telegram)
        return telegram
        
    def _waitForSilence(self):
        # Modbus RTU only allows one master (client which controls communication).
        # So lets try to wait a bit and jump in when nobody's speaking.
        # Modbus defines a waittime of 3,5 Characters between telegrams:
        # (1/9600baud * (1 Start bit + 8 Data bits + 1 Parity bit + 1 Stop bit) 
        # => about 4ms
        # Lets go with 7ms!  ;O)
        
        gotSlot = False
        backupTimeout = self._port.timeout
        end = time.time() + 3
        self._port.timeout = 0.07
        while end > time.time():
            chars = self._port.read(1)
            # nothing received so we got a slot of silence...hopefully
            if len(chars) == 0:
                gotSlot = True
                break
        self._port.timeout = backupTimeout
        return gotSlot    

    def _sendTelegram(self, telegram):
        if not self._is_connected:
            return False
        
        logger.debug("Helios: Sending telegram '{0}'".format(self._telegramToString(telegram)))
        self._port.write(bytearray(telegram))
        return True
            
    def _readTelegram(self, sender, receiver, datapoint):
        # sometimes a lot of garbage is received...so lets get a bit robust
        # and read a bit of this junk and see whether we are getting something
        # useful out of it!
        # How long does it take until something useful is received???
        timeout = time.time() + 1
        telegram = [0,0,0,0,0,0]
        while self._is_connected and timeout > time.time():
            char = self._port.read(1)
            if(len(char) > 0):
                byte = bytearray(char)[0]
                telegram.pop(0)
                telegram.append(byte)
                # Telegrams always start with a 0x01, is the CRC valid?, ...
                if (telegram[0] == 0x01 and 
                    telegram[1] == sender and 
                    telegram[2] == receiver and 
                    telegram[3] == datapoint and 
                    telegram[5] == self._calculateCRC(telegram)):
                    logger.debug("Telegram received '{0}'".format(self._telegramToString(telegram)))
                    return telegram[4]
        return None
    
    def _calculateCRC(self, telegram):
        sum = 0
        for c in telegram[:-1]:
            sum = sum + c
        return sum % 256
    
    def _telegramToString(self, telegram):
        str = ""
        for c in telegram:
            str = str + hex(c) + " "
        return str
                            
    def _convertFromRawValue(self, varname, rawvalue):
        value = None
        vardef = CONST_MAP_VARIABLES_TO_ID[varname]
        
        if vardef["type"] == "temperature":
            value = CONST_TEMPERATURE[rawvalue]
        elif vardef["type"] == "fanspeed":
            if rawvalue == 0x01:
                value = 1
            elif rawvalue == 0x03: 
                value = 2
            elif rawvalue == 0x07: 
                value = 3
            elif rawvalue == 0x0F: 
                value = 4
            elif rawvalue == 0x1F: 
                value = 5
            elif rawvalue == 0x3F: 
                value = 6
            elif rawvalue == 0x7F: 
                rawvalue = 7
            elif rawvalue == 0xFF: 
                value = 8
            else:
                value = None
        elif vardef["type"] == "bit":
            value = rawvalue >> vardef["bitposition"] & 0x01
                    
        return value        

    def _convertFromValue(self, varname, value, prevvalue):
        rawvalue = None
        vardef = CONST_MAP_VARIABLES_TO_ID[varname]
        
        if vardef['type'] == "temperature":
            rawvalue = CONST_TEMPERATURE.index(int(value))
        elif vardef["type"] == "fanspeed":
            value = int(value)
            if value == 1:
                rawvalue = 0x01
            elif value == 2: 
                rawvalue = 0x03
            elif value == 3: 
                rawvalue = 0x07
            elif value == 4: 
                rawvalue = 0x0F
            elif value == 5: 
                rawvalue = 0x1F
            elif value == 6: 
                rawvalue = 0x3F
            elif value == 7: 
                rawvalue = 0x7F
            elif value == 8: 
                rawvalue = 0xFF
            else:
                rawvalue = None
        elif vardef["type"] == "bit":
            # for bits we have to keep the other bits of the byte (previous value)
            if value in (True,1,"true","True","1","On","on"):
                rawvalue = prevvalue | (1 << vardef["bitposition"])
            else:
                rawvalue = prevvalue & ~(1 << vardef["bitposition"])
            
        return rawvalue        
        
    def writeValue(self,varname, value):
        if CONST_MAP_VARIABLES_TO_ID[varname]["write"] != True:
            logger.error("Helios: Variable {0} may not be written!".format(varname))
            return False 
        success = False
        
        self._lock.acquire()
        try:
            # if we have got to write a single bit, we need the current (byte) value to
            # reproduce the other bits...
            if CONST_MAP_VARIABLES_TO_ID[varname]["type"] == "bit":
                currentval = None
                if self._waitForSilence():
                    # Send poll request
                    telegram = self._createTelegram(
                        CONST_BUSMEMBER_ME,
                        CONST_BUSMEMBER_MAINBOARD, 
                        0, 
                        CONST_MAP_VARIABLES_TO_ID[varname]["varid"]
                    )
                    self._sendTelegram(telegram)
                    # Read response
                    currentval = self._readTelegram(
                        CONST_BUSMEMBER_MAINBOARD, 
                        CONST_BUSMEMBER_ME, 
                        CONST_MAP_VARIABLES_TO_ID[varname]["varid"]
                    )
                if currentval == None:
                    logger.error("Helios: Sending value to ventilation system failed. Can not read current variable value '{0}'."
                        .format(varname))
                    return False
                rawvalue = self._convertFromValue(varname, value, currentval)
            else:    
                rawvalue = self._convertFromValue(varname, value, None)
                
            # send the new value    
            if self._waitForSilence():
                if rawvalue != None:
                    # Writing value to Control boards
                    telegram = self._createTelegram(
                        CONST_BUSMEMBER_ME,
                        CONST_BUSMEMBER_CONTROLBOARDS, 
                        CONST_MAP_VARIABLES_TO_ID[varname]["varid"], 
                        rawvalue
                    )
                    self._sendTelegram(telegram)
                    
                    # Writing value to Slave boards
                    telegram = self._createTelegram(
                        CONST_BUSMEMBER_ME,
                        CONST_BUSMEMBER_SLAVEBOARDS, 
                        CONST_MAP_VARIABLES_TO_ID[varname]["varid"], 
                        rawvalue
                    )
                    self._sendTelegram(telegram)
                   
                    # Writing value to Mainboard
                    telegram = self._createTelegram(
                        CONST_BUSMEMBER_ME,
                        CONST_BUSMEMBER_MAINBOARD, 
                        CONST_MAP_VARIABLES_TO_ID[varname]["varid"], 
                        rawvalue 
                    )
                    self._sendTelegram(telegram)
                    
                    # send special char
                    self._sendTelegram([telegram[5]])
                    success = True
                else:
                    logger.error("Helios: Sending value to ventilation system failed. Can not convert value '{0}' for variable '{1}'."
                        .format(value,varname))
                    success = False
            else:
                logger.error("Helios: Sending value to ventilation system failed. No free slot for sending telegrams available.")
                success = False
        except Exception, e:
                logger.error("Helios: Exception in writeValue() occurred: {0}".format(e))
        finally:
            self._lock.release()
   
        return success
            
    def readValue(self,varname):
        if CONST_MAP_VARIABLES_TO_ID[varname]["read"] != True:
            logger.error("Variable {0} may not be read!".format(varname))
            return False
        value = None
        
        self._lock.acquire()
        try:
            logger.debug("Helios: Reading value: {0}".format(varname)) 
            if self._waitForSilence():
                # Send poll request
                telegram = self._createTelegram(
                    CONST_BUSMEMBER_ME,
                    CONST_BUSMEMBER_MAINBOARD, 
                    0, 
                    CONST_MAP_VARIABLES_TO_ID[varname]["varid"]
                )
                self._sendTelegram(telegram)
                # Read response
                value = self._readTelegram(
                    CONST_BUSMEMBER_MAINBOARD, 
                    CONST_BUSMEMBER_ME, 
                    CONST_MAP_VARIABLES_TO_ID[varname]["varid"]
                )
                if value is not None:
                    logger.debug("Helios: Value received (raw data): {0} = {1}"
                        .format(varname,hex(value))
                    ) 
                    value = self._convertFromRawValue(varname,value)
                    logger.debug("Helios: Value received (converted): {0} = {1}"
                        .format(varname,value)
                    ) 
                else:
                    logger.error("Helios: No valid value for '{0}' from ventilation system received."
                        .format(varname)
                    ) 
            else:
                logger.warn("Helios: Reading value from ventilation system failed. No free slot to send poll request available.")
        except Exception, e:
                logger.error("Helios: Exception in readValue() occurred: {0}".format(e))
        finally:
            self._lock.release()
   
        return value

    
class Helios(HeliosBase): 
    _items = {}
    
    def __init__(self, smarthome, tty, cycle=300):
        HeliosBase.__init__(self, tty)
        self._sh = smarthome
        self._cycle = int(cycle)
        self._alive = False
        
    def run(self):
        self.connect()
        self._alive = True
        self._sh.scheduler.add('Helios', self._update, cycle=self._cycle)

    def stop(self):
        self.disconnect()
        self._alive = False

    def parse_item(self, item):
        if 'helios_var' in item.conf:
            varname = item.conf['helios_var']
            if varname in CONST_MAP_VARIABLES_TO_ID.keys():
                self._items[varname] = item
                return self.update_item
            else:
                logger.warn("Helios: Ignoring unknown variable '{0}'".format(varname))
        
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Helios':
            self.writeValue(item.conf['helios_var'], item()) 
        
    def _update(self):
        logger.info("Helios: Updating values")
        for var in self._items.keys():
            val = self.readValue(var)
            if val != None:
                self._items[var](val,"Helios")

   
def main():
    import argparse 
    
    parser = argparse.ArgumentParser(
    description="Helios ventilation system commandline interface.",
    epilog="Without arguments all readable values using default tty will be retrieved.",
    argument_default=argparse.SUPPRESS)
    parser.add_argument("-t", "--tty", dest="port", default="/dev/ttyUSB0", help="Serial device to use")
    parser.add_argument("-r", "--read", dest="read_var", help="Read variables from ventilation system")
    parser.add_argument("-w", "--write", dest="write_var", help="Write variable to ventilation system")
    parser.add_argument("-v", "--value", dest="value", help="Value to write (required with option -v)")
    parser.add_argument("-d", "--debug", dest="enable_debug", action="store_true", help="Prints debug statements.")
    args = vars(parser.parse_args())
 
    if "write_var" in args.keys() and "value" not in args.keys():
        parser.print_usage()
        return

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    if "enable_debug" in args.keys():
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    try:
        helios = HeliosBase(args["port"])
        helios.connect()
        if not helios._is_connected:
            raise Exception("Not connected")
        
        if "read_var" in args.keys():
            print "{0} = {1}".format(args["read_var"],helios.readValue(args["read_var"]))
        elif "write_var" in args.keys():
            helios.writeValue(args["write_var"],args["value"])
        else:
            for var in CONST_MAP_VARIABLES_TO_ID.keys():
                print "{0} = {1}".format(var,helios.readValue(var))
    except Exception, e:
        print "Exception: {0}".format(e)
        return 1
    finally:
        if helios:
            helios.disconnect()

if __name__ == "__main__":
    sys.exit(main())        
