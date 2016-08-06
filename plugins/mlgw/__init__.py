#!/usr/bin/env python3
#
#########################################################################
#  Copyright 2015, 2016 Martin Sinn                         m.sinn@gmx.de
#  Version 1.1.1
#########################################################################
#  Free for non-commercial use
#
#  Plugin for the software SmartHomeNG, which allows to control and read
#  Bang & Olufsen devices through the B&O Masterlin Gateway.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
######################################################################### 

import logging
import socket
import threading
#import struct
import time
import ast
from lib.model.smartplugin import SmartPlugin


# logger = logging.getLogger(__name__)
log_telegrams = 4
loglevel_keepalivetelegrams = logging.DEBUG      # DEBUG
loglevel_receivedtelegrams = logging.INFO        # INFO
loglevel_unhandledtelegrams = logging.INFO
loglevel_senttelegrams = logging.INFO            # INFO


def _hexbyte( byte ):
    resultstr = hex( byte )
    if byte < 16:
        resultstr = resultstr[:2] + "0" + resultstr[2]
    return resultstr

def _hexword( byte1, byte2 ):
    resultstr = _hexbyte( byte2 )
    resultstr = _hexbyte( byte1 ) + resultstr[2:]
    return resultstr


# Dictionary for items to listen for
# { listenerkey: item }, listenerkey = 256 * room + cmd
listenerlightdict = {}
listenercontroldict = {}
listenersourcestatusdict = {}
listenerspeakermodedict = {}


#########################################################################################
###### Installation-specific data

# Dictionary to lookup room names, filled from plugin.conf
roomdict = dict( [] )
reverse_roomdict = {}

# Dictionary to lookup MLN names, filled from plugin.conf
mlndict = dict( [] )
reverse_mlndict = {}


#########################################################################################
###### Dictionaries with MLGW Protokoll Data

payloadtypedict = dict( [
    (0x01, "Beo4 Command"), (0x02, "Source Status"), (0x03, "Pict&Snd Status"),
    (0x04, "Light and Control command"), (0x05, "All standby notification"), 
    (0x06, "BeoRemote One control command"), (0x07, "BeoRemote One source selection"),
    (0x20, "MLGW virtual button event"), (0x30, "Login request"), (0x31, "Login status"),
    (0x32, "Change password request"), (0x33, "Change password response"), 
    (0x34, "Secure login request"), (0x36, "Ping"), (0x37, "Pong"), 
    (0x38, "Configuration change notification"), (0x39, "Request Serial Number"), 
    (0x3a, "Serial Number"), (0x40, "Location based event")
    ] )

#payloaddirectiondict = dict( [
#    (0x01, "-> Beolink"), (0x02, "Beolink ->"), (0x03, "Beolink ->"),
#    (0x04, "Beolink ->"), (0x05, "MLGW ->"), 
#    (0x06, "-> Beolink"), (0x07, "-> Beolink"),
#    (0x20, "bidirectional"), (0x30, "-> MLGW"), (0x31, "MLGW ->"),
#    (0x32, "-> MLGW"), (0x33, "MLGW ->"), 
#    (0x34, "-> MLGW"), (0x36, "-> MLGW"), (0x37, "MLGW ->"), 
#    (0x38, "MLGW ->"), (0x39, "-> MLGW"), 
#    (0x3a, "MLGW ->"), (0x40, "-> MLGW")
#    ] )

beo4commanddict = dict( [
    # Source selection:
    (0x0c, "Standby"), (0x47, "Sleep"), (0x80, "TV"), (0x81, "Radio"), (0x82, "DTV2"), 
    (0x83, "Aux_A"), (0x85, "V.Mem"), (0x86, "DVD"), (0x87, "Camera"), (0x88, "Text"), 
    (0x8a, "DTV"), (0x8b, "PC"), (0x0d, "Doorcam"), (0x91, "A.Mem"), (0x92, "CD"), 
    (0x93, "N.Radio"), (0x94, "N.Music"), (0x97, "CD2"), 
    # Digits:
    (0x00, "Digit-0"), (0x01, "Digit-1"), (0x02, "Digit-2"), (0x03, "Digit-3"), 
    (0x04, "Digit-4"), (0x05, "Digit-5"), (0x06, "Digit-6"), (0x07, "Digit-7"), 
    (0x08, "Digit-8"), (0x09, "Digit-9"), 
    # Source control:
    (0x1e, "STEP_UP"), (0x1f, "STEP_DW"), (0x32, "REWIND"), (0x33, "RETURN"), 
    (0x34, "WIND"), (0x35, "Go / Play"), (0x36, "Stop"), (0xd4, "Yellow"), 
    (0xd5, "Green"), (0xd8, "Blue"), (0xd9, "Red"), 
    # Sound and picture control:
    (0x0d, "Mute"), (0x1c, "P.Mute"), (0x2a, "Format"), (0x44, "Sound / Speaker"), 
    (0x5c, "Menu"), (0x60, "Volume UP"), (0x64, "Volume DOWN"), (0xda, "Cinema_On"), 
    (0xdb, "Cinema_Off"), 
    # Other controls:
    (0x14, "BACK"), (0x7f, "Exit"), 
    # Continue functionality:
    (0x7e, "Key Release"), 
    # Functions:
    # Cursor functions:
    (0x13, "SELECT"), (0xca, "Cursor_Up"), (0xcb, "Cursor_Down"), (0xcc, "Cursor_Left"), 
    (0xcd, "Cursor_Right"), 
    #    
    (0x9b, "Light"),  (0x9c, "Command"),
    #  Dummy for 'Listen for all commands'
    (0xff, "<all>")
    ] )

reverse_beo4commanddict = {}

### for '0x02: Source Status'

selectedsourcedict = dict( [
    (0x0b, "TV"), (0x15, "V.Mem"), (0x1f, "DTV"), (0x29, "DVD"), 
    (0x6f, "Radio"), (0x79, "A.Mem"), (0x8d, "CD"),
    #  Dummy for 'Listen for all sources'
    (0xfe, "<all>")
    ] )
    
reverse_selectedsourcedict = {}

sourceactivitydict = dict( [
    (0x00, "Unknown"), (0x01, "Stop"), (0x02, "Playing"), (0x03, "Wind"), 
    (0x04, "Rewind"), (0x05, "Record lock"), (0x06, "Standby")
    ] )

pictureformatdict = dict( [
    (0x00, "Not known"), (0x01, "Known by decoder"), (0x02, "4:3"), (0x03, "16:9"), 
    (0x04, "4:3 Letterbox middle"), (0x05, "4:3 Letterbox top"), 
    (0x06, "4:3 Letterbox bottom"), (0xff, "Blank picture")
    ] )


### for '0x03: Picture and Sound Status'

soundstatusdict = dict( [
    (0x00, "Not muted"), (0x01, "Muted")
    ] )

speakermodedict = dict( [
    (0x01, "Center channel"), (0x02, "2ch stereo"), (0x03, "Front surround"),
    (0x04, "4ch stereo"), (0x05, "Full surround"),
    #  Dummy for 'Listen for all modes'
    (0xfd, "<all>")
    ] )

reverse_speakermodedict = {}

screenmutedict = dict( [
    (0x00, "not muted"), (0x01, "muted")
    ] )

#screenactivedict = dict( [
#    (0x00, "not active"), (0x01, "active")
#    ] )

cinemamodedict = dict( [
    (0x00, "Cinemamode=off"), (0x01, "Cinemamode=on")
    ] )

stereoindicatordict = dict( [
    (0x00, "Mono"), (0x01, "Stereo")
    ] )


### for '0x04: Light and Control command'

lctypedict = dict( [
    (0x01, "LIGHT"), (0x02, "CONTROL")
    ] )


### for '0x31: Login Status

loginstatusdict = dict( [
    (0x00, "OK"), (0x01, "FAIL")
    ] )


# ########################################################################################
# ##### Decode MLGW Protokoll packet to readable string

## Get decoded string for mlgw packet's payload type
#
def _getpayloadtypestr( payloadtype ):
        result = payloadtypedict.get( payloadtype )
        if result == None:
            result = "UNKNOWN (type=" + _hexbyte( payloadtype ) + ")"
        return result

def _getraumstr( raum ):
    result = roomdict.get( raum )
    if result == None:
        result = "Room=" + str( raum )
    return result

def _getmlnstr( mln ):
    result = mlndict.get( mln )
    if result == None:
        result = "MLN=" + str( mln )
    return result
    
def _getbeo4commandstr( command ):
        result = beo4commanddict.get( command )
        if result == None:
            result = "Cmd=" + _hexbyte( command )
        return result

def _getselectedsourcestr( source ):
        result = selectedsourcedict.get( source )
        if result == None:
            result = "Src=" + _hexbyte( source )
        return result

def _getspeakermodestr( source ):
        result = speakermodedict.get( source )
        if result == None:
            result = "mode=" + _hexbyte( source )
        return result

def _getdictstr( mydict, mykey ):
        result = mydict.get( mykey )
        if result == None:
            result = _hexbyte( mykey )
        return result


## Get decoded string for a mlgw packet
#
#   The raw message (mlgw packet) is handed to this function. 
#   The result of this function is a human readable string, describing the content
#   of the mlgw packet
#
#  @param message   raw mlgw telegram
#  @returns         telegram as a human readable string
#
def _getpayloadstr( message ):
    if message[2] == 0:            # payload length is 0
        resultstr = "[No payload]"
    elif message[1] == 0x01:       # Beo4 Command
        resultstr = _getmlnstr( message[4] )
        resultstr = resultstr + " " + _hexbyte( message[5] )
        resultstr = resultstr + " " + _getbeo4commandstr(message[6])

    elif message[1] == 0x02:       # Source Status
        resultstr = _getmlnstr( message[4] ) 
        resultstr = resultstr + " " + _getselectedsourcestr( message[5] ) 
        resultstr = resultstr + " " + _hexword( message[6], message[7] )
        resultstr = resultstr + " " + _hexword( message[8], message[9] )
        resultstr = resultstr + " " + _getdictstr( sourceactivitydict, message[10] )
        resultstr = resultstr + " " + _getdictstr( pictureformatdict, message[11] )

    elif message[1] == 0x03:       # Picture and Sound Status
        resultstr = _getmlnstr( message[4] )
        if message[5] != 0x00:
            resultstr = resultstr + " " + _getdictstr( soundstatusdict, message[5] )
        resultstr = resultstr + " " + _getdictstr( speakermodedict, message[6] )
        resultstr = resultstr + " Vol=" + str( message[7] )
        if message[9] != 0x00:
            resultstr = resultstr + " Scrn:" + _getdictstr( screenmutedict, message[8] )
        if message[11] != 0x00:
            resultstr = resultstr + " Scrn2:" + _getdictstr( screenmutedict, message[10] )
        if message[12] != 0x00:
            resultstr = resultstr + " " + _getdictstr( cinemamodedict, message[12] )
        if message[13] != 0x01:
            resultstr = resultstr + " " + _getdictstr( stereoindicatordict, message[13] )

    elif message[1] == 0x04:       # Light and Control command
        resultstr = _getraumstr( message[4] ) + " " + _getdictstr( lctypedict, message[5] ) + " " + _getbeo4commandstr( message[6] )

    elif message[1] == 0x30:       # Login request
        wrk = message[4:4+message[2]]
        for i in range(0, message[2]):
            if wrk[i] == 0: wrk[i] = 0x7f
        wrk = wrk.decode('utf-8')
        resultstr = wrk.split(chr(0x7f))[0] + " / " + wrk.split(chr(0x7f))[1]

    elif message[1] == 0x31:       # Login status
        resultstr = _getdictstr( loginstatusdict, message[4] )

    elif message[1] == 0x3a:       # Serial Number
        resultstr = message[4:4+message[2]].decode('utf-8')

    else:                               # Display raw payload
        resultstr = ""
        for i in range(0, message[2]):
            if i > 0:
                resultstr = resultstr + " "
            resultstr = resultstr + _hexbyte(message[4+i])
    return resultstr


# ########################################################################################
# ##### mlgwBase class

## Class to handle mlgw connection
#
class mlgwBase():

    ## The constructor: Initialize thread
    #  @param self       The object pointer.
    #
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        global reverse_beo4commanddict
        global reverse_selectedsourcedict
        global reverse_speakermodedict
                
        self._host = ''
        self._tcpip = None
        self._port = None
        self.buffersize = 1024
        self._mysocket = None
        self.telegramlogging = False

        reverse_beo4commanddict = {v.upper(): k for k, v in beo4commanddict.items()}
        reverse_selectedsourcedict = {v.upper(): k for k, v in selectedsourcedict.items()}
        reverse_speakermodedict = {v.upper(): k for k, v in speakermodedict.items()}
        self.logger.info("mlgw: beo4commanddict=" + str(beo4commanddict))
        self.logger.info("mlgw: reverse_beo4commanddict=" + str(reverse_beo4commanddict))
        self.logger.info("mlgw: selectedsourcedict=" + str(selectedsourcedict))
        self.logger.info("mlgw: reverse_selectedsourcedict=" + str(reverse_selectedsourcedict))
        self.logger.info("mlgw: speakermodedict=" + str(speakermodedict))
        self.logger.info("mlgw: reverse_speakermodedict=" + str(reverse_speakermodedict))


    ## Open tcp connection to mlgw
    #  @param self      The object pointer.
    #  @param host      Hostname of mlgw.
    #  @param port      Port for mlgw protocol.
    #
    def OpenConnection(self, host=None, port=None):
        self._host = host
        self._port = port
        self.connected = 0

        # get ip address for hostname
        try:
            self._tcpip = socket.gethostbyname( self._host )
        except Exception as e:
            self.logger.error("mlgw: Error resolving '%s': %s" % (host, e))
            return

        # open socket to masterlink gateway
        self._mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
             self._mysocket.connect( (self._tcpip, self._port) )
        except Exception as e:
            self.logger.error("mlgw: Error opening connection to %s: %s" % (self._tcpip, e))
            return
        if self._tcpip != host:
            self.logger.info("mlgw: Opened connection to ML Gateway '" + host + "' on IP " + self._tcpip + ":" + str( self._port ))
        else:
            self.logger.info("mlgw: Opened connection to ML Gateway on IP " + self._tcpip + ":" + str( self._port ))
        self.connected = 1
        return


    ## Close connection to mlgw
    #  @param self       The object pointer.
    #
    def CloseConnection(self):
        if self.connected == 0:
            return
        self.connected = 0
        self._mysocket.close()
        self.logger.info("mlgw: Closed connection to ML Gateway")
        return
        
    
    ## Send command to mlgw
    #  @param self       The object pointer.
    #  @param type       mlgw command type.
    #  @param payload    Payload for the mlgw command.
    #
    def SendCommand(self, type, payload ):
        if self.connected == 0:
            return
        self._telegram = bytearray()
        self._telegram.append(0x01)             # byte[0] SOH
        self._telegram.append(type)             # byte[1] Type
        self._telegram.append(len(payload))     # byte[2] Length
        self._telegram.append(0x00)             # byte[3] Spare
        for i in range(0, len(payload)):
            self._telegram.append(payload[i])
        self._mysocket.send( self._telegram )

        if self.telegramlogging:
            if type == 0x36:
                loglevel = loglevel_keepalivetelegrams
            else:
                loglevel = loglevel_senttelegrams
            self.logger.log(loglevel, "mlgw: >SENT: " + _getpayloadtypestr( type ) + ": " + _getpayloadstr( self._telegram ))  # debug
        return


    ## Send Beo4 command to mlgw
    #  @param self       The object pointer.
    #  @param type       mlgw command type.
    #  @param payload    Payload for the mlgw command.
    #
    def SendBeo4Command(self, mln, dest, cmd ):
        self._payload = bytearray()
        self._payload.append(mln)              # byte[0] MLN
        self._payload.append(dest)             # byte[1] Dest-Sel (0x00, 0x01, 0x05, 0x0f)
        self._payload.append(cmd)              # byte[2] Beo4 Command
#        self._payload.append(0x00)             # byte[3] Sec-Source
#        self._payload.append(0x00)             # byte[3] Link
        self.SendCommand(0x01, self._payload)
        return
        

    ## Receive message from mlgw
    #  @param self       The object pointer.
    #
    def ReceiveCommand(self):
        if self.connected == 0:
            return

        try:
            self._mlgwdata = self._mysocket.recv(self.buffersize)
        except KeyboardInterrupt:
            self.logger.error("mlgw: KeyboardInterrupt, terminating...")
            self.CloseConnection()
            sys.exit(1)

        self._payloadstr = _getpayloadstr( self._mlgwdata )
        if self._mlgwdata[0] != 0x01:
            self.logger.error("mlgw: Received telegram with SOH byte <> 0x01")
        if self._mlgwdata[3] != 0x00:
            self.logger.error("mlgw: Received telegram with spare byte <> 0x00")
        if self.telegramlogging:
            loglevel = loglevel_receivedtelegrams
            if self._mlgwdata[1] == 0x37:
                loglevel = loglevel_keepalivetelegrams
            self.logger.log(loglevel, "mlgw: <RCVD: '" + _getpayloadtypestr( self._mlgwdata[1] ) + "': " + str(self._payloadstr))  # debug
        return (self._mlgwdata[1], str(self._payloadstr))
        

    ## Get serial number of mlgw
    #  @param self       The object pointer.
    #
    def GetSerial(self):
        if self.connected == 0:
            return
      # Request serial number
        self.SendCommand(0x39, '')
        (result, self._serial) = self.ReceiveCommand()
        self.logger.warning("mlgw: Serial number of ML Gateway is " + self._serial)  # info
        return


    ## Test and login if nessary
    #  @param self      The object pointer.
    #  @param username  Username for login to mlgw.
    #  @param password  Password for login to mlgw.
    #
    def Login(self, username, password):
        if self.connected == 0:
            return
        # send Ping
        self.SendCommand(0x36, '')
        (result, self.wrkstr) = self.ReceiveCommand()
        if result == 0x31:
            self.logger.info("mlgw: Login required for this ML Gateway")
            self._wrkstr = username + chr(0x00) + password
            self._payload = bytearray()
            for i in range(0, len(self._wrkstr)):
                self._payload.append(ord(self._wrkstr[i])) 
            self.SendCommand(0x30, self._payload)   # Login Request
            (result, self._wrkstr) = self.ReceiveCommand()
            if self._wrkstr == 'FAIL':
                self.logger.error("mlgw: Login not successful, user / password combination is not valid!")
                self.CloseConnection()
            else:
                self.logger.info("mlgw: Login successful, connection established")
        else:
            self.logger.info("mlgw: Connection established")
        return




#########################################################################################

## Class to handle asynchronously incoming telegrams from the mlgw
#
# This class starts a thread to listen for incomming telegrams.
#
# Right now, this thread writes the decoded telegrams to the log, doing nothing else with it.
#
class mlgwlistener(threading.Thread):

    ## The constructor: Initialize thread
    #  @param self       The object pointer.
    #  @param mymlgwbase Calling class, which defines the used tcp socket and defines 
    #                    the connected state.
    #
    def __init__( self, mymlgwbase ): 
        self.logger = logging.getLogger(__name__)
        threading.Thread.__init__(self)
        self.name = 'mlgwListener'
        self._mlgwbase = mymlgwbase
        self._mlgwbase._mysocket.settimeout(5)

    ## Run thread
    #  @param self The object pointer.
    #
    def run( self ):
        if self._mlgwbase.connected == 0:
            return
        
        self.logger.debug("Listener Started")
        timeoutcount = 0
        while self._mlgwbase.connected: 
            try:
                self._mlgwdata = self._mlgwbase._mysocket.recv(self._mlgwbase.buffersize)
            except socket.timeout:
                timeoutcount += 1
            except e:
                self.logger.info("mlgw: mlgwlistener error '{0}'".format(e))
            else:
                timeoutcount = 0
                self._payloadstr = _getpayloadstr( self._mlgwdata )
                if self._mlgwdata[0] != 0x01:
                    self.logger.error("Received telegram with SOH byte <> 0x01")
                if self._mlgwdata[3] != 0x00:
                    self.logger.error("Received telegram with spare byte <> 0x00")
                if self._mlgwbase.telegramlogging:
                    if self._mlgwdata[1] == 0x37:
                        loglevel = loglevel_keepalivetelegrams
                    elif log_telegrams > 1:
                        loglevel = loglevel_receivedtelegrams
                    else:
                        loglevel = loglevel_unhandledtelegrams
#                    self.logger.log(logging.WARNING, "mlgw: loglevel="+str(loglevel)+", log_telegrams="+str(log_telegrams))
                    if log_telegrams > 1:
                        self.logger.log(loglevel, "<RCVD: " + _getpayloadtypestr( self._mlgwdata[1] ) + ": " + str(self._payloadstr))  # info
                if (self._mlgwdata[0] == 0x01) and (self._mlgwdata[3] == 0x00) and (self._mlgwdata[1] != 0x37):
                    # process telegram
                    telegram_handled = self.processtelegram()
                    if (telegram_handled == False) and (log_telegrams >= 1):
                        self.logger.log(loglevel, "UNHANDLED: " + _getpayloadtypestr( self._mlgwdata[1] ) + ": " + str(self._payloadstr))  # info
            if timeoutcount > 12:
                self.logger.error("No answer received to mlgw-ping")
            if timeoutcount > 11:
                # send Ping (after 60 seconds of inactivity)
                self._mlgwbase.SendCommand(0x36, "")
                
        self.logger.debug("Listener Stopped")


    ## Process incomming telegram
    #  @param self The object pointer.
    #
    def processtelegram( self ):
        ishandled = False

        ##### LIGHT and CONTROL telegrams
        if self._mlgwdata[1] == 0x04:
            cmd =  _getbeo4commandstr(self._mlgwdata[6])
            # LIGHT telegram
            if self._mlgwdata[5] == 0x01:
                # ignore commands: 0x58, Key Release, Light
                if self._mlgwdata[6] in [0x58, 0x7e, 0x9b]:
                    return True
                # update item, which is listening for all commands (return command string)
                item = listenerlightdict.get(_hexword(self._mlgwdata[4], 255))
                if item != None:
#                    self.logger.warning('processtelegram: L&C telegram: room='+str(self._mlgwdata[4])+', LC=LIGHT, command='+cmd+', item='+str(item))
                    item(cmd, 'mlgw', 'LIGHT <ALL>')
                    ishandled = True
                # update item (return 1)
                item = listenerlightdict.get(_hexword(self._mlgwdata[4], self._mlgwdata[6]))
                if item != None:
#                    self.logger.warning('processtelegram: L&C telegram: room='+str(self._mlgwdata[4])+', LC=LIGHT, command='+cmd+', item='+str(item))
                    item(1, 'mlgw', 'LIGHT '+cmd)
                    ishandled = True

            # CONTROL telegram
            elif self._mlgwdata[5] == 0x02:
                # ignore commands: 0x58, Key Release, Command
                if self._mlgwdata[6] in [0x58, 0x7e, 0x9c]:
                    return True
                # update item, which is listening for all commands (return command string)
                item = listenercontroldict.get(_hexword(self._mlgwdata[4], 255))	# room
                if item != None:
#                    self.logger.warning('processtelegram: L&C telegram: room='+str(self._mlgwdata[4])+', LC=CONTROL, command='+cmd+', item='+str(item))
                    item(cmd, 'mlgw', 'CONTROL <ALL>')
                    ishandled = True
                # update item (return 1)
                item = listenercontroldict.get(_hexword(self._mlgwdata[4], self._mlgwdata[6]))
                if item != None:
#                    self.logger.warning('processtelegram: L&C telegram: room='+str(self._mlgwdata[4])+', LC=CONTROL, command='+cmd+', item='+str(item))
                    item(1, 'mlgw', 'CONTROL '+cmd)
                    ishandled = True

        ##### SOURCE STATUS telegrams
        elif self._mlgwdata[1] == 0x02:
            source =  _getselectedsourcestr(self._mlgwdata[5])	# source
            # update item, which is listening for all commands (return source string)
            item = listenersourcestatusdict.get(_hexword(self._mlgwdata[4], 254))	# mln
            if item != None:
#                self.logger.warning('processtelegram: Source Status telegram: mln='+str(self._mlgwdata[4])+', source='+source+', item='+str(item))
                item(source, 'mlgw', 'SOURCE STATUS <ALL>')
                ishandled = True
            # update item (return 1)
            item = listenersourcestatusdict.get(_hexword(self._mlgwdata[4], self._mlgwdata[5]))	#mln, source
            if item != None:
#                self.logger.warning('processtelegram: Source Status telegram: mln='+str(self._mlgwdata[4])+', source='+source+', item='+str(item))
                item(1, 'mlgw', 'SOURCE STATUS '+source)
                ishandled = True

        ##### PICT&SND STATUS telegrams
        elif self._mlgwdata[1] == 0x03:
            speakermode =  _getspeakermodestr(self._mlgwdata[6])	# speaker mode
            # update item, which is listening for all commands (return speakermode string)
            item = listenerspeakermodedict.get(_hexword(self._mlgwdata[4], 253))	# mln
            if item != None:
#                self.logger.warning('processtelegram: Source Status telegram: mln='+str(self._mlgwdata[4])+', speakermode='+speakermode+', item='+str(item))
                item(speakermode, 'mlgw', 'PICT&SND STATUS <ALL>')
                ishandled = True
            # update item (return 1)
            item = listenerspeakermodedict.get(_hexword(self._mlgwdata[4], self._mlgwdata[6]))	#mln, speakermode
            if item != None:
#                self.logger.warning('processtelegram: Source Status telegram: mln='+str(self._mlgwdata[4])+', speakermode='+speakermode+', item='+str(item))
                item(1, 'mlgw', 'PICT&SND STATUS '+speakermode)
                ishandled = True

        return ishandled


    ## stop thread (a dummy at the ,moment)
    #  @param self The object pointer.
    #
    def stop( self ):
        pass
        
        
#########################################################################################

## Class mlgw: Implements the plugin for smarthome.py
#
class mlgw(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION='1.1.1'

    ## The constructor: Initialize plugin
    #
    # Store config parameters of plugin. Smarthome.py reads these parameters from plugin.conf
    # and hands them to the __init__ method of the plugin.
    #
    #  @param self      The object pointer.
    #  @param smarthome Defined by smarthome.py.
    #  @param host      Hostname of mlgw.
    #  @param port      Port for mlgw protocol.
    #  @param username  Username for login to mlgw.
    #  @param password  Password for login to mlgw.
    #  @param rooms     List of tuples containing the room definitions.
    #  @param mlns      List of tuples containing the MLN definitions.
    #
    def __init__(self, smarthome, host='mlgw.local', port=9000, username='mlgw', password='mlgw', rooms=[], mlns=[], log_mlgwtelegrams='0'):
        self.logger = logging.getLogger(__name__)
        global roomdict, reverse_roomdict
        global mlndict, reverse_mlndict
        global loglevel_keepalivetelegrams, loglevel_senttelegrams
        global loglevel_receivedtelegrams, loglevel_unhandledtelegrams
        global log_telegrams
        
        log_telegrams = int(log_mlgwtelegrams)
        if log_telegrams < 0: log_telegrams = 0
        if log_telegrams > 4: log_telegrams = 2
        if log_telegrams == 4:
            loglevel_keepalivetelegrams = logging.WARNING
        if log_telegrams >= 3:
            loglevel_senttelegrams = logging.WARNING
        if log_telegrams >= 2:
            loglevel_receivedtelegrams = logging.WARNING
        if log_telegrams >= 1:
            loglevel_unhandledtelegrams = logging.WARNING
        
        self.logger.debug("mlgw: mlgw.__init__()")
        self._mlgwbase = mlgwBase()
        self._mlgwbase.OpenConnection(host, int(port))
        if self._mlgwbase.connected:
            self._mlgwbase.GetSerial()
            self._mlgwbase.Login(username, password)
        self._mlgwbase.telegramlogging = True
        
        self._sh = smarthome
        
        if rooms == []:
            self.logger.warning("mlgw: No rooms defined")
        else:
            roomdict = ast.literal_eval(rooms)
            self.logger.info("mlgw: Rooms defined: " + str(roomdict))
            reverse_roomdict = {v.upper(): k for k, v in roomdict.items()}
            self.logger.info("mlgw: reverse_roomdict=" + str(reverse_roomdict))

        if mlns == []:
            self.logger.warning("mlgw: No MLNs defined")
        else:
            mlndict = ast.literal_eval(mlns)
            self.logger.info("mlgw: MLNs defined: " + str(mlndict))
            reverse_mlndict = {v.upper(): k for k, v in mlndict.items()}
            self.logger.info("mlgw: reverse_mlndict=" + str(reverse_mlndict))
        self.alive = False

    ## Run plugin
    #
    # @param self      The object pointer.
    #
    def run(self):
        if self._mlgwbase.connected == 0:
            return

        self.logger.info("listenerlightdict: " + str(listenerlightdict))
        self.logger.info("listenercontroldict: " + str(listenercontroldict))
        self.logger.info("listenersourcestatusdict: " + str(listenersourcestatusdict))
        self.logger.info("listenerspeakermodedict: " + str(listenerspeakermodedict))

        self.logger.debug("mlgw.run()")
        self.alive = True

        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)
        self.listener = mlgwlistener(self._mlgwbase)
        self.listener.start()

        loop = 1
        while loop == 1:
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                loop = 0;
                self.logger.info("KeyboardInterrupt, terminating...")
        self._mlgwbase.CloseConnection()

    ## Stop plugin
    #
    # @param self      The object pointer.
    #
    def stop(self):
        self.logger.debug("mlgw.stop()")
        self._mlgwbase.CloseConnection()
        if self.alive:
            self.logger.info("mlgw: Waiting for listener-thread to stop")
            self.listener.join()
            self.logger.info("mlgw: Listener-threads stopped")
        self.alive = False


    ## Parse item configuration (not yet implemented)
    #
    # @param self      The object pointer.
    # @param item      Pointer to item configuration.
    #
    def parse_item(self, item):
        global listenerlightdict
        global listenercontroldict
        global listenersourcestatusdict
        global listenerspeakermodedict

        if 'mlgw_send' in item.conf:
            mln = reverse_mlndict.get(item.conf['mlgw_mln'].upper())
            if mln == None:
                try:
                    mln = int(item.conf['mlgw_mln'])
                except:
                    self.logger.error("mlgw: parse item: {0}".format(item) + " - mlgw_mln is not numeric")
                    return None

            if item.conf['mlgw_send'].upper() == 'CMD':
                wrk = None
                if item._type == 'bool':
                    wrk = reverse_beo4commanddict.get(item.conf['mlgw_cmd'].upper())
                    if wrk == None:
                        try:
                            wrk = int( item.conf['mlgw_cmd'], 16 )
                        except:
                            pass
                item.conf['_mlgw_cmd'] = wrk
                self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                return self.update_item
            elif item.conf['mlgw_send'].upper() == 'CH':
                if item._type == 'num':
                    self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                    return self.update_channel
                else:
                    self.logger.error("mlgw: parse item: {0}".format(item) + " - 'mlgw_send' is 'ch' but 'type' is not 'num'")
                    return None

        if 'mlgw_listen' in item.conf:
            room = reverse_roomdict.get(item.conf['mlgw_room'].upper())
            if room == None:
                try:
                    room = int(item.conf['mlgw_room'])
                except:
                    self.logger.error("mlgw: parse item: {0}".format(item) + " - mlgw_room is not numeric")
                    return None

            if item.conf['mlgw_listen'].upper() == 'LIGHT':
                if item._type == 'bool':
                    cmd = reverse_beo4commanddict.get(item.conf['mlgw_cmd'].upper())
                    if cmd == None:
                        try:
                            cmd = int( item.conf['mlgw_cmd'], 16 )
                        except:
                            pass
                elif item._type == 'str':
                    cmd = reverse_beo4commanddict.get('<ALL>')
                item.conf['_mlgw_cmd'] = cmd
                self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                # Dict aufbauen für Listener !!!
                listenerlightdict[_hexword(room, cmd)] = item
                return None     # Keine update routine an sh.py zurueckmelden, item kann nicht gesetzt (gesendet) werden

            if item.conf['mlgw_listen'].upper() == 'CONTROL':
                if item._type == 'bool':
                    cmd = reverse_beo4commanddict.get(item.conf['mlgw_cmd'].upper())
                    if cmd == None:
                        try:
                            cmd = int( item.conf['mlgw_cmd'], 16 )
                        except:
                            pass
                elif item._type == 'str':
                    cmd = reverse_beo4commanddict.get('<ALL>')
                item.conf['_mlgw_cmd'] = cmd
                self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                # Dict aufbauen für Listener !!!
                listenercontroldict[_hexword(room, cmd)] = item
                return None     # Keine update routine an sh.py zurueckmelden (item kann nicht gesetzt werden)

            mln = reverse_mlndict.get(item.conf['mlgw_mln'].upper())
            if mln == None:
                try:
                    mln = int(item.conf['mlgw_mln'])
                except:
                    self.logger.error("mlgw: parse item: {0}".format(item) + " - mlgw_mln is not numeric")
                    return None

            if item.conf['mlgw_listen'].upper() == 'SOURCE STATUS':
                if item._type == 'bool':
                    source = reverse_selectedsourcedict.get(item.conf['mlgw_cmd'].upper())
                    if source == None:
                        try:
                            source = int( item.conf['mlgw_cmd'], 16 )
                        except:
                            pass
                elif item._type == 'str':
                    source = reverse_selectedsourcedict.get('<ALL>')
                item.conf['_mlgw_cmd'] = source
                self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                # Dict aufbauen für Listener !!!
                listenersourcestatusdict[_hexword(mln, source)] = item
                return None     # Keine update routine an sh.py zurueckmelden (item kann nicht gesetzt werden)

            if item.conf['mlgw_listen'].upper() == 'PICT&SND STATUS':
                if item._type == 'bool':
                    source = reverse_speakermodedict.get(item.conf['mlgw_cmd'].upper())
                    if source == None:
                        try:
                            source = int( item.conf['mlgw_cmd'], 16 )
                        except:
                            pass
                elif item._type == 'str':
                    source = reverse_speakermodedict.get('<ALL>')
                item.conf['_mlgw_cmd'] = source
                self.logger.info("mlgw: parse item: {0}".format(item) + ", type=" + item._type + ", item.conf=" + str(item.conf) )
                # Dict aufbauen für Listener !!!
                listenerspeakermodedict[_hexword(mln, source)] = item
                return None     # Keine update routine an sh.py zurueckmelden (item kann nicht gesetzt werden)

        else:
            return None


    ## Parse logic configuration (not yet implemented)
    #
    # @param self      The object pointer.
    # @param logic     Pointer to logic configuration.
    #
    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    ## Update program/channel
    #
    # @param self      The object pointer.
    # @param item      Pointer to item configuration.
    # @param caller    Calling class (e.g. plugin name).
    # @param source    Calling source (e.g. ip / port of visu)
    # @param dest      ???.
    #
    def update_channel(self, item, caller=None, source=None, dest=None):
        if caller != 'mlgw':
#            mln = int(item.conf['mlgw_mln'])
            mln = reverse_mlndict.get(item.conf['mlgw_mln'].upper())
            if mln == None:
                try:
                    mln = int(item.conf['mlgw_mln'])
                except:
                    self.logger.error("mlgw: update_channel: {0}".format(item) + " - mlgw_mln is not numeric")
                    return None
            self.logger.warning("mlgw: update channel: {0}".format(item.id())+", value="+ str(item()) +", (MLN="+str(mln)+")")   # info
            channel = item()
            wrk = channel
            if wrk // 100 != 0:
                self._mlgwbase.SendBeo4Command( mln, 0x00, wrk // 100 )
                wrk = wrk - (100 * wrk // 100)

            if (wrk // 10 != 0) or (channel > 99):
                self._mlgwbase.SendBeo4Command( mln, 0x00, wrk // 10 )
                wrk = wrk - (10 * wrk // 10)
                
            if (wrk != 0) or (channel > 9):
                self._mlgwbase.SendBeo4Command( mln, 0x00, wrk )
        return
        

    ## Update item
    #
    # @param self      The object pointer.
    # @param item      Pointer to item configuration.
    # @param caller    Calling class (e.g. plugin name).
    # @param source    Calling source (e.g. ip / port of visu)
    # @param dest      ???.
    #
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'mlgw':
#            mln = int(item.conf['mlgw_mln'])
            mln = reverse_mlndict.get(item.conf['mlgw_mln'].upper())
            if mln == None:
                try:
                    mln = int(item.conf['mlgw_mln'])
                except:
                    self.logger.error("mlgw: update_item: {0}".format(item) + " - mlgw_mln is not numeric")
                    return None
            if item._type == 'str':
                cmd = reverse_beo4commanddict.get(item().upper())
                if cmd == None:
                    try:
                        cmd = int( item(), 16 )
                    except:
                        pass
            elif item._type == 'bool':
                cmd = item.conf['_mlgw_cmd']
            elif item._type == 'num':
                cmd = item()
            self.logger.warning("mlgw: update item: {0}".format(item.id())+", value="+ str(item()) +", (MLN="+str(mln)+", cmd="+str(cmd)+")")   # info

            if cmd != None:
                self._mlgwbase.SendBeo4Command( mln, 0x00, cmd )
#                self._payload = bytearray()
#                self._payload.append(mln)              # byte[0] MLN
#                self._payload.append(0x00)             # byte[1] Dest-Sel (0x00, 0x01, 0x05, 0x0f)
#                self._payload.append(cmd)              # byte[2] Beo4 Command
##                self._payload.append(0x00)             # byte[3] Sec-Source
##                self._payload.append(0x00)             # byte[3] Link
#                self._mlgwbase.SendCommand(0x01, self._payload)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    rooms = [
        (0x01, "KO"), (0x02, "WZ"), (0x03, "EZ"), (0x04, "FL"), (0x05, "GZ"), 
        (0x06, "AZ"), (0x07, "DU"), (0x08, "HW"), (0x09, "BD"), (0x0a, "SZ"), 
        (0x0b, "TR"), (0x0c, "TE")
    ]
    mlns = [
        (0x01,"BV9-WZ"), (0x02,"BV10-SZ"), (0x03,"BLActive-KO"), 
        (0x04,"BLActive-GZ"), (0x05,"BLActive-BD"), (0x06,"BLActive-DU"), 
        (0x07,"BLActive-AZ"), (0x08,"BLC"), (0x09,"BeoPlayV1-AZ")
    ]
    myplugin = mlgw('mlgw', 'mlgw.local', 9000, 'mlgw', 'mlgw', str(dict(rooms)), str(dict(mlns)), 3 )
    myplugin.run()
    myplugin.stop()
