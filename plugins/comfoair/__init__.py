#!/usr/bin/env python
#########################################################################
# Copyright 2013 Stefan Kals
#########################################################################
#  ComfoAir-Plugin for SmartHome.py.  http://mknx.github.com/smarthome/
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
import socket
import time
import serial
import re
import threading
from . import commands

logger = logging.getLogger('ComfoAir')

class ComfoAir():

    def __init__(self, smarthome, host=None, port=0, serialport=None, kwltype='comfoair350'):
        self.connected = False
        self._sh = smarthome
        self._params = {}
        self._init_cmds = []
        self._cyclic_cmds = {}
        self._lock = threading.Lock()
        self._host = host
        self._port = int(port)
        self._serialport = serialport
        self._connection_attempts = 0
        self._connection_errorlog = 60
        self._initread = False
        smarthome.connections.monitor(self)

        # Load controlset and commandset
        if kwltype in commands.controlset and kwltype in commands.commandset:
            self._controlset = commands.controlset[kwltype]
            self._commandset = commands.commandset[kwltype]
            self.log_info('Loaded commands for KWL type \'{}\''.format(kwltype))
        else:
            self.log_err('Commands for KWL type \'{}\' could not be found!'.format(kwltype))
            return None

        # Remember packet config
        self._packetstart = self.int2bytes(self._controlset['PacketStart'], 2)
        self._packetend = self.int2bytes(self._controlset['PacketEnd'], 2)
        self._acknowledge = self.int2bytes(self._controlset['Acknowledge'], 2)
        self._specialchar = self.int2bytes(self._controlset['SpecialCharacter'], 1)
        self._reponsecommandinc = self._controlset['ResponseCommandIncrement']
        self._commandlength = 2
        self._checksumlength = 1
        
    def connect(self):
        if self._serialport is not None:
            self.connect_serial()
        else:
            self.connect_tcp()
        
    def connect_tcp(self):
        self._lock.acquire()
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            self._sock.connect((self._host, self._port))
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                self.log_err('could not connect to {}:{}: {}'.format(self._host, self._port, e))
                self._connection_attempts = self._connection_errorlog
            self._lock.release()
            return
        else:
            self.connected = True
            self.log_info('connected to {}:{}'.format(self._host, self._port))
            self._connection_attempts = 0
            self._lock.release()
    
    def connect_serial(self):
        self._lock.acquire()
        try:
            self._serialconnection = serial.Serial(
                    self._serialport, 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=2)
        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                self.log_err('could not connect to {}: {}'.format(self._serialport, e))
                self._connection_attempts = self._connection_errorlog
            self._lock.release()
            return
        else:
            self.connected = True
            self.log_info('connected to {}'.format(self._serialport))
            self._connection_attempts = 0
            self._lock.release()

    def disconnect(self):
        if self._serialport is not None:
            self.disconnect_serial()
        else:
            self.disconnect_tcp()
        
    def disconnect_tcp(self): 
        self.connected = False
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self._sock.close()
        except:
            pass

    def disconnect_serial(self): 
        self.connected = False
        try:
            self._serialconnection.close()
            self._serialconnection = None
        except:
            pass
        
    def send_bytes(self, packet):
        if self._serialport is not None:
            self.send_bytes_serial(packet)
        else:
            self.send_bytes_tcp(packet)
        
    def send_bytes_tcp(self, packet):
        self._sock.sendall(packet)

    def send_bytes_serial(self, packet):
        self._serialconnection.write(packet)
        
    def read_bytes(self, length):
        if self._serialport is not None:
            return self.read_bytes_serial(length)
        else:
            return self.read_bytes_tcp(length)
        
    def read_bytes_tcp(self, length):
        return self._sock.recv(length)

    def read_bytes_serial(self, length):
        return self._serialconnection.read(length)
 
    def parse_item(self, item):
        # Process the read config
        if 'comfoair_read' in item.conf:
            commandname = item.conf['comfoair_read']
            if (commandname == None or commandname not in self._commandset):
                self.log_err('Item {} contains invalid read command \'{}\'!'.format(item, commandname))
                return None
            
            # Remember the read config to later update this item if the configured response comes in
            self.log_info('Item {} reads by using command \'{}\'.'.format(item, commandname))
            commandconf = self._commandset[commandname]
            commandcode = commandconf['Command']

            if not commandcode in self._params:
                self._params[commandcode] = {'commandname': [commandname], 'items': [item]}
            elif not item in self._params[commandcode]['items']:
                self._params[commandcode]['commandname'].append(commandname)
                self._params[commandcode]['items'].append(item)

            # Allow items to be automatically initiated on startup
            if ('comfoair_init' in item.conf and item.conf['comfoair_init'] == 'true'):
                self.log_info('Item {} is initialized on startup.'.format(item))
                # Only add the item to the initial commands if it is not cyclic. Cyclic commands get called on init because this is the first cycle...
                if not commandcode in self._init_cmds and 'comfoair_read_cycle' not in item.conf:
                    self._init_cmds.append(commandcode)

            # Allow items to be cyclically updated
            if ('comfoair_read_cycle' in item.conf):
                cycle = int(item.conf['comfoair_read_cycle'])
                self.log_info('Item {} should read cyclic every {} seconds.'.format(item, cycle))

                if not commandcode in self._cyclic_cmds:
                    self._cyclic_cmds[commandcode] = {'cycle': cycle, 'nexttime': 0}
                else:
                    # If another item requested this command already with a longer cycle, use the shorter cycle now
                    if self._cyclic_cmds[commandcode]['cycle'] > cycle:
                        self._cyclic_cmds[commandcode]['cycle'] = cycle

        # Process the send config
        if 'comfoair_send' in item.conf:
            commandname = item.conf['comfoair_send']
            if commandname == None:
                return None
            elif commandname not in self._commandset:
                self.log_err('Item {} contains invalid write command \'{}\'!'.format(item, commandname))
                return None
            
            self.log_info('Item {} writes by using command \'{}\''.format(item, commandname))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'ComfoAir' and 'comfoair_send' in item.conf:
            commandname = item.conf['comfoair_send']

            if type(item) != int:
                value = int(item())
            else:
                value = item()

            # Send write command
            self.send_command(commandname, value)

            # If a read command should be sent after write
            if 'comfoair_read' in item.conf and 'comfoair_read_afterwrite' in item.conf:
                readcommandname = item.conf['comfoair_read']
                readafterwrite = item.conf['comfoair_read_afterwrite']
                self.log_info('Attempting read after write for item {}, command {}, delay {}'.format(item, readcommandname, readafterwrite))
                if readcommandname is not None and readafterwrite is not None:
                    aw = float(readafterwrite)
                    time.sleep(aw)
                    self.send_command(readcommandname)
            
            # If commands should be triggered after this write        
            if 'comfoair_trigger' in item.conf:
                trigger = item.conf['comfoair_trigger']
                if trigger == None:
                    self.log_err('Item {} contains invalid trigger command list \'{}\'!'.format(item, trigger))
                else:
                    tdelay = 5 # default delay
                    if 'comfoair_trigger_afterwrite' in item.conf:
                        tdelay = float(item.conf['comfoair_trigger_afterwrite'])
                    if type(trigger) != list:
                        trigger = [trigger] 
                    for triggername in trigger:
                        triggername = triggername.strip()
                        if triggername is not None and readafterwrite is not None:
                            self.log_info('Triggering command {} after write for item {}'.format(triggername, item))
                            time.sleep(tdelay)
                            self.send_command(triggername)

    def handle_cyclic_cmds(self):
        # Read all cyclic commands
        currenttime = time.time()
        for commandcode in list(self._cyclic_cmds.keys()):
            entry = self._cyclic_cmds[commandcode]
            # Is the command already due?
            if entry['nexttime'] <= currenttime:
                commandname = self.commandname_by_commandcode(commandcode)
                self.log_info('Triggering cyclic read command: {}'.format(commandname))
                self.send_command(commandname)
                entry['nexttime'] = currenttime + entry['cycle']
        
    def send_command(self, commandname, value=None):
        try:
            #self.log_debug('Got a new send job: Command {} with value {}'.format(commandname, value))
            
            # Get command config
            commandconf = self._commandset[commandname]
            commandcode = int(commandconf['Command'])
            commandcodebytecount = commandconf['CommandBytes']
            commandtype = commandconf['Type']
            commandvaluebytes = commandconf['ValueBytes']
            #self.log_debug('Command config: {}'.format(commandconf))
            
            # Transform value for write commands
            #self.log_debug('Got value: {}'.format(value))
            if 'ValueTransform' in commandconf and value is not None and value != '' and commandtype == 'Write':
                commandtransform = commandconf['ValueTransform']
                value = self.value_transform(value, commandtype, commandtransform)
                #self.log_debug('Transformed value using method {} to {}'.format(commandtransform, value))
    
            # Build value byte array
            valuebytes = bytearray()
            if value is not None and commandvaluebytes > 0:
                valuebytes = self.int2bytes(value, commandvaluebytes)
            #self.log_debug('Created value bytes: {}'.format(valuebytes))
    
            # Calculate the checksum
            commandbytes = self.int2bytes(commandcode, commandcodebytecount)
            payload = bytearray()
            payload.extend(commandbytes)
            if len(valuebytes) > 0:
                payload.extend(valuebytes)
            checksum = self.calc_checksum(payload)
    
            # Build packet
            packet = bytearray()
            packet.extend(self.int2bytes(self._controlset['PacketStart'], 2))
            packet.extend(commandbytes)
            if len(valuebytes) > 0:
                packet.extend(self.encode_specialchars(valuebytes))
            packet.extend(self.int2bytes(checksum, 1))
            packet.extend(self.int2bytes(self._controlset['PacketEnd'], 2))
            self.log_info('Preparing command {} with value {} (transformed to value byte \'{}\') to be sent.'.format(commandname, value, self.bytes2hexstring(valuebytes)))
            
            # Use a lock to allow only one sender at a time
            self._lock.acquire()

            if not self.connected:
                raise Exception("No connection to ComfoAir.")
            
            try:
                self.send_bytes(packet)
                self.log_info('Successfully sent packet: {}'.format(self.bytes2hexstring(packet)))
            except Exception as e:
                raise Exception('Exception while sending: {}'.format(e))
            
            if commandtype == 'Read':
                packet = bytearray()
                
                # Try to receive a packet start, a command and a data length byte
                firstpartlen = len(self._packetstart) + self._commandlength + 1
                while self.alive and len(packet) < firstpartlen:
                    try:
                        bytestoreceive = firstpartlen - len(packet)
                        self.log_debug('Trying to receive {} bytes for the first part of the response.'.format(bytestoreceive))
                        chunk = self.read_bytes(bytestoreceive)
                        self.log_info('Received {} bytes chunk of response part 1: {}'.format(len(chunk), self.bytes2hexstring(chunk)))
                        if len(chunk)  == 0:
                            raise Exception('Received 0 bytes chunk - ignoring packet!')
                        
                        # Cut away old ACK (but only if the telegram wasn't started already)
                        if len(packet) == 0:
                            chunk = self.remove_ack_begin(chunk)
                        packet.extend(chunk)
                    except socket.timeout:
                        raise Exception("error receiving first part of packet: timeout")
                    except Exception as e:
                        raise Exception("error receiving first part of packet: {}".format(e))
    
                datalen = packet[firstpartlen - 1]
                #self.log_info('Got a data length of: {}'.format(datalen))
                packetlen = firstpartlen + datalen + self._checksumlength + len(self._packetend)
    
                # Try to receive the second part of the packet
                while self.alive and len(packet) < packetlen or packet[-2:] != self._packetend:
                    try:
                        # In case of doubled special characters, the packet can be longer (try one byte more at a time)
                        if len(packet) >= packetlen and packet[-2:] != self._packetend:
                            packetlen = len(packet) + 1
                            self.log_info('Extended packet length because of encoded characters.'.format(self.bytes2hexstring(chunk)))
                        
                        # Receive next chunk
                        bytestoreceive = packetlen - len(packet)
                        self.log_debug('Trying to receive {} bytes for the second part of the response.'.format(bytestoreceive))
                        chunk = self.read_bytes(bytestoreceive)
                        self.log_info('Received {} bytes chunk of response part 2: {}'.format(len(chunk), self.bytes2hexstring(chunk)))
                        packet.extend(chunk)
                        if len(chunk)  == 0:
                            raise Exception('Received 0 bytes chunk - ignoring packet!')
                    except socket.timeout:
                        raise Exception("error receiving second part of packet: timeout")
                    except Exception as e:
                        raise Exception("error receiving second part of packet: {}".format(e))
    
                # Send ACK
                self.send_bytes(self._acknowledge)
                
                # Parse response
                self.parse_response(packet)
        
        except Exception as e:
            self.disconnect()
            self.log_err("send_command failed: {}".format(e))

        finally:            
            # At the end, release the lock
            self._lock.release()

    def parse_response(self, response):
        #resph = self.bytes2int(response)
        self.log_info('Successfully received response: {}'.format(self.bytes2hexstring(response)))

        # A telegram looks like this: start sequence (2 bytes), command (2 bytes), data length (1 byte), data, checksum (1 byte), end sequence (2 bytes, already cut away)
        commandcodebytes = response[2:4]
        commandcodebytes[1] -= self._reponsecommandinc # The request command of this response is -1 (for comfoair 350)
        commandcodebytes.append(0) # Add a data length byte of 0 (always true for read commands)
        commandcode = self.bytes2int(commandcodebytes)

        # Remove begin and checksum to get the data
        rawdatabytes = response[5:-3]

        # Decode special characters
        databytes = self.decode_specialchars(rawdatabytes)
        self.log_debug('Corresponding read command: {}, decoded data: {} (raw: {})'.format(self.bytes2hexstring(commandcodebytes), self.bytes2hexstring(databytes), self.bytes2hexstring(rawdatabytes)))

        # Validate checksum
        packetpart = bytearray()
        packetpart.extend(response[2:5]) # Command and data length
        packetpart.extend(databytes) # Decoded data bytes
        checksum = self.calc_checksum(packetpart)
        receivedchecksum = response[len(response) - len(self._packetend) - 1]
        if (receivedchecksum != checksum):
            self.log_err('Calculated checksum of {} does not match received checksum of {}! Ignoring reponse.'.format(checksum, receivedchecksum))
            return

        # Find items using this response command
        if commandcode in self._params.keys():
            # Iterate over all corresponding items
            for i in range(0, len(self._params[commandcode]['items'])):
                item = self._params[commandcode]['items'][i]
                commandname = self._params[commandcode]['commandname'][i]

                # Get command config
                commandconf = self._commandset[commandname]
                commandtype = commandconf['Type']
                commandvaluebytes = commandconf['ValueBytes']
                commandresppos = 0
                if 'ResponsePosition' in commandconf:
                    commandresppos = commandconf['ResponsePosition']
                commandtransform = ''
                if 'ValueTransform' in commandconf:
                    commandtransform = commandconf['ValueTransform']

                # Is there enough data for the configured position?
                index = commandresppos - 1
                if index + commandvaluebytes <= len(databytes):
                    # Extract value
                    valuebytes = databytes[index:index + commandvaluebytes]
                    rawvalue = self.bytes2int(valuebytes)
                
                    # Tranform value
                    value = self.value_transform(rawvalue, commandtype, commandtransform)
                    self.log_debug('Matched command {} and read transformed value {} (raw value was {}) from byte position {} and byte length {}.'.format(commandname, value, rawvalue, commandresppos, commandvaluebytes))

                    # Update item
                    item(value, 'ComfoAir')
                else:
                    self.log_err('Telegram did not contain enough data bytes for the configured command {} to extract a value!'.format(commandname))

    def run(self):
        self.alive = True
        self._sh.scheduler.add('ComfoAir-init', self.send_init_commands, prio=5, cycle=600, offset=2)
        maxloops = 20
        loops = 0 
        while self.alive and not self._initread and loops < maxloops:  # wait for init read to finish
            time.sleep(0.5)
            loops += 1
        self._sh.scheduler.remove('ComfoAir-init')
                
    def stop(self):
        self._sh.scheduler.remove('ComfoAir-cyclic')
        self.alive = False
        self.disconnect()
       
    def send_init_commands(self):
        try:
            # Do the init read commands
            if self._init_cmds != []:
                if self.connected:
                    self.log_info('Starting initial read commands.')
                    for commandcode in self._init_cmds:
                        commandname = self.commandname_by_commandcode(commandcode)
                        self.send_command(commandname)
    
            # Find the shortest cycle
            shortestcycle = -1
            for commandname in list(self._cyclic_cmds.keys()):
                entry = self._cyclic_cmds[commandname]
                if shortestcycle == -1 or entry['cycle'] < shortestcycle:
                    shortestcycle = entry['cycle']
    
            # Start the worker thread
            if shortestcycle != -1:
                # Balance unnecessary calls and precision
                workercycle = int(shortestcycle / 2)
                self._sh.scheduler.add('ComfoAir-cyclic', self.handle_cyclic_cmds, cycle=workercycle, prio=5, offset=0)
                self.log_info('Added cyclic worker thread ({} sec cycle). Shortest item update cycle found: {} sec.'.format(workercycle, shortestcycle))
        finally:
            self._initread = True

    def remove_ack_begin(self, packet):
        # Cut old ACK responses from ComfoAir before the real message
        acklen = len(self._acknowledge)
        while len(packet) >= acklen and packet[0:acklen] == self._acknowledge:
            packet = packet[acklen:]
        return packet
    
    def calc_checksum(self, packetpart):
        return (sum(packetpart) + 173) % 256
    
    def log_debug(self, text):    
        logger.debug('ComfoAir: {}'.format(text))    

    def log_info(self, text):    
        logger.info('ComfoAir: {}'.format(text))    

    def log_err(self, text):    
        logger.error('ComfoAir: {}'.format(text))    
    
    def int2bytes(self, value, length):
        # Limit value to the passed byte length
        value = value % (2 ** (length * 8))
        return value.to_bytes(length, byteorder='big')
    
    def bytes2int(self, bytesvalue):
        return int.from_bytes(bytesvalue, byteorder='big', signed=False)
    
    def bytes2hexstring(self, bytesvalue):
        return ":".join("{:02x}".format(c) for c in bytesvalue)
                
    def encode_specialchars(self, packet):
        specialchar = self._controlset['SpecialCharacter']
        encodedpacket = bytearray()
        for count in range(len(packet)):
            char = packet[count]
            encodedpacket.append(char)
            if char == specialchar:
                # Encoding works by doubling the special char
                self.log_debug('Encoded special char at position {} of data bytes {}.'.format(count, self.bytes2hexstring(packet)))
                encodedpacket.append(char)
        #self.log_debug('Encoded data bytes: {}.'.format(encodedpacket))
        return encodedpacket
    
    def decode_specialchars(self, packet):
        specialchar = self._controlset['SpecialCharacter']
        decodedpacket = bytearray()
        prevchar = ''
        specialcharremoved = 0
        for count in range(len(packet)):
            char = packet[count]
            if count > 0:
                prevchar = packet[count - 1]
            if char == specialchar and prevchar == specialchar and specialcharremoved == 0:
                # Decoding works by dropping double sepcial chars
                self.log_debug('Decoded special char at position {} of packet {}.'.format(count, self.bytes2hexstring(packet)))
                specialcharremoved = 1
            else:
                decodedpacket.append(char)
                # Reset dropping marker
                specialcharremoved = 0
        return decodedpacket
    
    def value_transform(self, value, commandtype, transformmethod):
        if transformmethod == 'Temperature':
            if commandtype == 'Read':
                return value / 2 - 20
            elif commandtype == 'Write':
                return (value + 20) * 2
        elif transformmethod == 'RPM':
            if commandtype == 'Read':
                return int(1875000 / value)
            elif commandtype == 'Write':
                return int(1875000 / value)
        return value
    
    def commandname_by_commandcode(self, commandcode):
        for commandname in self._commandset.keys():
            if self._commandset[commandname]['Command'] == commandcode:
                return commandname
        return None
