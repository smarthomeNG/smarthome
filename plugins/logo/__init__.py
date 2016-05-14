#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
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

import ctypes
import os
import string
import time
import logging
import threading

logger = logging.getLogger('')


class LOGO:

    def __init__(self, smarthome, io_wait=5, host='192.168.0.76', port=102, version='0BA7'):
        self.host = str(host).encode('ascii')
        self.port = int(port)
        self._version = version
        self._io_wait = float(io_wait)
        self._sock = False
        self._lock = threading.Lock()
        self.connected = False
        self._connection_attempts = 0
        self._connection_errorlog = 2
        self._sh = smarthome
        self._vmIO = 923  # lesen der I Q M AI AQ AM ab VM-Adresse VM923
        self._vmIO_len = 60  # Anzahl der zu lesenden Bytes 60
        self._vm = 0  # lesen der VM ab VM-Adresse VM0
        self._vm_len = 850  # Anzahl der zu lesenden Bytes VM0-850
        self.tableVM_IO = {  # Address-Tab der I,Q,M,AI,AQ,AM im PLC-VM-Buffer
        'I': {'VMaddr': 923, 'bytes': 3, 'bits': 24},
        'Q': {'VMaddr': 942, 'bytes': 2, 'bits': 16},
        'M': {'VMaddr': 948, 'bytes': 3, 'bits': 27},
        'AI': {'VMaddr': 926, 'words': 8},
        'AQ': {'VMaddr': 944, 'words': 2},
        'AM': {'VMaddr': 952, 'words': 16},
        'VM': {'VMaddr': 0, 'bytes': 850}}

    # Hardware Version 0BA8
        self._vmIO_0BA8 = 1024  # lesen der I Q M AI AQ AM ab VM-Adresse VM1024
        self._vmIO_len_0BA8 = 445  # Anzahl der zu lesenden Bytes 445
        self.table_VM_IO_0BA8 = {  # Address-Tab der I,Q,M,AI,AQ,AM im PLC-VM-Buffer
        'I': {'VMaddr': 1024, 'bytes': 8, 'bits': 64},
        'Q': {'VMaddr': 1064, 'bytes': 8, 'bits': 64},
        'M': {'VMaddr': 1104, 'bytes': 14, 'bits': 112},
        'AI': {'VMaddr': 1032, 'words': 16},
        'AQ': {'VMaddr': 1072, 'words': 16},
        'AM': {'VMaddr': 1118, 'words': 64},
        'NI': {'VMaddr': 1256, 'bytes': 16, 'bits':128},
        'NAI': {'VMaddr': 1262, 'words': 64},
        'NQ': {'VMaddr': 1390, 'bytes': 16, 'bits': 128},
        'NAQ': {'VMaddr': 1406, 'words': 32},
        'VM': {'VMaddr': 0, 'bytes': 850}}

        if self._version == '0BA8':
            self.tableVM_IO = self.table_VM_IO_0BA8
            self._vmIO = self._vmIO_0BA8
            self._vmIO_len = self._vmIO_len_0BA8
    # End Hardware Version 0BA8

        self.reads = {}
        self.writes = {}
        self.Dateipfad = '/lib'  # Dateipfad zur Bibliothek
        self.threadLastRead = 0  # verstrichene Zeit zwischen zwei LeseBefehlen

        smarthome.connections.monitor(self)  # damit connect ausgeführt wird

    # libnodave Parameter zum lesen aus LOGO
        self.ph = 0         # Porthandle
        self.di = 0         # Dave Interface Handle
        self.dc = 0
        self.res = 1
        self.rack = 1
        self.slot = 0
        self.mpi = 2
        self.dave = ""
        self.daveDB = 132
        self.daveFlags = 131
        self.daveOutputs = 130
        self.daveInputs = 129
        self.timeOut = 5000000

    # Öffnen der Verbindung zur LOGO
    def connect(self):
        self._lock.acquire()
        try:
            logger.info('LOGO: Try open connection {0}:{1} '.format(self.host, self.port))
            if os.name == 'nt':
                DLL_LOC = self.Dateipfad + '/' + ('libnodave.dll')
                self.dave = ctypes.cdll.LoadLibrary(DLL_LOC)
            if os.name == 'posix':
                DLL_LOC = self.Dateipfad + '/' + ('libnodave.so')
                self.dave = ctypes.cdll.LoadLibrary(DLL_LOC)

            #logger.info('LOGO: DLL-Path: {0}, operating system {1}'.format(DLL_LOC, os.name))

            self.ph = self.dave.openSocket(self.port, self.host)
            if self.ph < 0:
                raise LOGO('Port Handle N.O.K.')

            # Dave Interface handle
            self.di = self.dave.daveNewInterface(self.ph, self.ph, 'IF1', 0,  122, 2)
            #logger.info('LOGO: - Dave Interface Handle: {0}'.format(self.di))

            # Init Adapter
            self.res = self.dave.daveInitAdapter(self.di)
            if self.res is not 0:
                raise LOGO('Init Adapter N.O.K.')

            # dave Connection
            self.dc = self.dave.daveNewConnection(self.di, self.mpi, self.rack, self.slot)
            #logger.info('LOGO: - Dave Connection: {0}'.format(self.dc))

            self.res = self.dave.daveConnectPLC(self.dc)
            self.dave.daveSetTimeout(self.di, self.timeOut)
            if self.res < 0:
                raise LOGO('connection result:{0} '.format(self.res))

        except Exception as e:
            self._connection_attempts -= 1
            if self._connection_attempts <= 0:
                logger.error('LOGO: could not connect to {0}:{1}: {2}'.format(self.host, self.port, e))
                self._connection_attempts = self._connection_errorlog
            self._lock.release()
            return
        else:
            self.connected = True
            logger.info('LOGO: connected to {0}:{1}'.format(self.host, self.port))
            self._connection_attempts = 0
            self._lock.release()

    def run(self):
        self.alive = True
        self._write_read_loop()

    def stop(self):
        self.alive = False
        self.close()

    def _write_read_loop(self):
        threading.currentThread().name = 'logo_cycle'
        logger.debug("LOGO: Starting write-read cycle")
        while self.alive:
            start = time.time()
            t = start - self.threadLastRead
            if len(self.writes) > 0:    # beim Schreiben sofort schreiben
                self._write_cycle()
                self._read_cycle()
                cycletime = time.time() - start
                #logger.debug("LOGO: logo_cycle takes {0} seconds".format(cycletime))
                self.threadLastRead = time.time()
            elif t > self._io_wait:  # erneutes Lesen erst wenn Zeit um ist
                self._read_cycle()
                cycletime = time.time() - start
                #logger.debug("LOGO: logo_cycle takes {0} seconds. Last read: {1}".format(cycletime, t))
                self.threadLastRead = time.time()

    def _write_cycle(self):
        if not self.connected:
            return

        try:
            remove = []    # Liste der bereits geschriebenen Items
            for k, v in self.writes.items():    # zu schreibend Items I1,Q1,M1, AI1, AQ1, AM1, VM850, VM850.2, VMW0
                #logger.debug('LOGO: write_cycle() {0} : {1} '.format(k, v))
                typ = v['typ']  # z.B. I Q M AI AQ AM VM VMW
                value = v['value']
                write_res = -1
                if typ in ['I', 'Q', 'M', 'NI', 'NQ']:  # I1 Q1 M1
                    if value is True:
                        #logger.debug("LOGO: set {0} : {1} : {2} ".format(k, v, value))
                        write_res = self.set_vm_bit(v['VMaddr'], v['VMbit'])    # Setzen
                    else:
                        #logger.debug("LOGO: clear {0} : {1} : {2} ".format(k, v, value))
                        write_res = self.clear_vm_bit(v['VMaddr'], v['VMbit'])  # Löschen

                elif typ in ['AI', 'AQ', 'AM', 'NAI', 'NAQ', 'VMW']:    # AI1 AQ1 AM1 VMW
                    write_res = self.write_vm_word(v['VMaddr'], value)

                elif typ == 'VM':       # VM0 VM10.6
                    if 'VMbit' in v:    # VM10.6
                        if value is True:
                            write_res = self.set_vm_bit(v['VMaddr'], v['VMbit'])
                        else:
                            write_res = self.clear_vm_bit(v['VMaddr'], v['VMbit'])
                    else:               # VM0
                        write_res = self.write_vm_byte(v['VMaddr'], value)
                else:
                    raise LOGO('invalid typ: {1}'.format(typ))

                if write_res is not 0:
                    raise LOGO('LOGO: write failed: {0} {1} '.format(typ, value))
                    self.close()
                else:
                    logger.debug("LOGO: write {0} : {1} : {2} ".format(k, value, v))
                    remove.append(k)  # nach dem Übertragen aus der Liste write entfernen

        except Exception as e:
            logger.error('LOGO: write_cycle(){0} write error {1} '.format(k, e))
            return

        for k in remove:    # nach dem Übertragen aus der Liste writes entfernen - damit das Item nur 1x übertragen wird
            del self.writes[k]

    def _read_cycle(self):
        if not self.connected:
            return

        try:
            pBuf_VMIO = ctypes.create_string_buffer(self._vmIO_len)
            buf_VMIO_p = ctypes.pointer(pBuf_VMIO)  # LesebufferIO

            pBuf_VM = ctypes.create_string_buffer(self._vm_len)
            buf_VM_p = ctypes.pointer(pBuf_VM)  # LesebufferVM

            # lesen der I Q M AI AQ AM
            resVMIO = self.dave.daveReadManyBytes(self.dc, self.daveDB, 1, self._vmIO, self._vmIO_len, buf_VMIO_p)
            if resVMIO is not 0:
                logger.error('LOGO: read_cycle() failed ro read VM_IO-Buffer daveReadManyBytes')
                self.close()
                return

            if not self.connected:
                return

            # lesen der VM
            resVM = self.dave.daveReadManyBytes(self.dc, self.daveDB, 1, self._vm, self._vm_len, buf_VM_p)
            if resVM is not 0:
                logger.error('LOGO: read_cycle() failed ro read VM-Buffer daveReadManyBytes')
                self.close()
                return

            if not self.connected:
                return

            # prüfe Buffer auf Änderung
            for k, v in self.reads.items():
                #logger.debug('LOGO: read_cycle() {0} : {1} '.format(k, v))
                new_value = 0
                item = v['item']

                if v['DataType'] == 'byte':
                    new_value = ord(pBuf_VM[v['VMaddr'] - self._vm])  # VM byte   z.B. VM0
                elif v['DataType'] == 'word':
                    #logger.debug('LOGO: read_cycle() h{0} : l{1} '.format(pBuf_VM[v['VMaddr']-self._vm], pBuf_VM[v['VMaddr']+1-self._vm]))
                    if v['typ'] == 'VMW':                           # VMW word   z.B. VMW0
                        h = ord(pBuf_VM[v['VMaddr'] - self._vm])
                        l = ord(pBuf_VM[v['VMaddr'] + 1 - self._vm])
                    else:                                           # AI AQ AM word z.B, AM1
                        h = ord(pBuf_VMIO[v['VMaddr'] - self._vmIO])
                        l = ord(pBuf_VMIO[v['VMaddr'] + 1 - self._vmIO])
                    new_value = l + (h << 8)
                elif v['DataType'] == 'bit':
                    if v['typ'] == 'VM':                            # VM bit z.B.VM10.6
                        new_byte = ord(pBuf_VM[v['VMaddr'] - self._vm])
                    else:                                           # I Q M bit z.B. M1
                        new_byte = ord(pBuf_VMIO[v['VMaddr'] - self._vmIO])
                    new_value = self.get_bit(new_byte, v['VMbit'])
                else:
                    raise LOGO('{0} invalid DataType in reads: {1}'.format(k, v['DataType']))

                if 'old' in v:  # Variable wurde schon einmal gelesen
                    if v['old'] != new_value:   # Variable hat sich geändert
                        logger.debug("LOGO: read_cycle():{0} newV:{1} oldV:{2} item:{3} ".format(k, new_value, v['old'], v['item']))
                        item(new_value)   # aktualisiere das Item
                        v.update({'old': new_value})    # speichere den aktuellen Zustand
                    #else:   # Variable hat sich nicht geändert
                        #logger.debug("LOGO: read:{0} newV:{1} = oldV:{2} item:{3} ".format(k, new_value, v['old'], v['item']))
                else:   # Variable wurde noch nie gelesen
                    logger.debug('LOGO: read_cycle() first read:{0} value:{1} item:{2}'.format(k, new_value, v['item']))
                    item(new_value)   # aktualisiere das Item zum ersten mal
                    v.update({'old': new_value})    # speichere den aktuellen Zustand

        except Exception as e:
            logger.error('LOGO: read_cycle(){0} read error {1} '.format(k, e))
            return

        if not self.connected:
            return

    def close(self):
        self.connected = False
        try:
            self.disconnect()
            logger.info('LOGO: disconnected {0}:{1}'.format(self.host, self.port))
        except:
            pass

    def disconnect(self):
        self.dave.daveDisconnectPLC(self.dc)
        self.dave.closePort(self.ph)

    def parse_item(self, item):
        if 'logo_read' in item.conf:
            logo_read = item.conf['logo_read']
            if isinstance(logo_read, str):
                logo_read = [logo_read, ]
            for addr in logo_read:
                #logger.debug('LOGO: parse_item {0} {1}'.format(item, addr))
                addressInfo = self.getAddressInfo(addr)
                if addressInfo is not False:
                    addressInfo.update({'value': item()})   # Wert des Items hinzufügen
                    addressInfo.update({'item': item})      # Item hinzufügen
                    self.reads.update({addr: addressInfo})  # zu lesende Items

        if 'logo_write' in item.conf:
            if isinstance(item.conf['logo_write'], str):
                item.conf['logo_write'] = [item.conf['logo_write'], ]
            return self.update_item

    def parse_logic(self, logic):
        pass
        #if 'xxx' in logic.conf:
            # self.function(logic['name'])

    def update_item(self, item, caller=None, source=None, dest=None):
        if 'logo_write' in item.conf:
            if caller != 'LOGO':
                for addr in item.conf['logo_write']:
                    #logger.debug('LOGO: update_item() item:{0} addr:{1}'.format(item, addr))
                    addressInfo = self.getAddressInfo(addr)
                    if addressInfo is not False:
                        addressInfo.update({'value': item()})  # Wert des Items hinzufügen
                        addressInfo.update({'item': item})
                        self.writes.update({addr: addressInfo})   # zu schreibende Items

    def getAddressInfo(self, value):    # I1,Q1,M1, AI1, AQ1, AM1, VM850, VM850.2, VMW0
        try:
            indexDigit = 0
            for c in value:  # indexDigit: ermittle Index der ersten Zahl
                if c.isdigit():
                    break
                else:
                    indexDigit += 1
            indexComma = value.find('.')    # ermittle ob ein Komma vorhanden ist (z.B. VM10.6)
            #logger.debug('LOGO: getAddressInfo() value:{0} iC:{1} iD:{2}'.format(value, indexComma, indexDigit))
            if (len(value) < 2):
                raise LOGO('invalid address {0} indexDigit < 1'.format(value))
            if indexDigit < 1:
                raise LOGO('invalid address {0} indexDigit < 1'.format(value))
            typ = value[0:indexDigit]   # I Q M AI AQ AM VM VMW
            if indexComma == -1:        # kein Komma (z.B. M1)
                address = int(value[indexDigit:len(value)])
            else:               # Komma vorhanden (z.B. VM10.6)
                address = int(value[indexDigit:indexComma])
                bitNr = int(value[indexComma + 1:len(value)])
                if (bitNr < 0) or (bitNr > 8):
                    raise LOGO('invalid address {0} bitNr invalid'.format(value))

            #logger.debug('LOGO: getAddressInfo() typ:{0} address:{1}'.format(typ, address))

            if typ == 'VMW':
                VMaddr = int(self.tableVM_IO['VM']['VMaddr'])   # Startaddresse
            else:
                VMaddr = int(self.tableVM_IO[typ]['VMaddr'])    # Startaddresse

            if typ in ['I', 'Q', 'M', 'NI', 'NQ']:  # I1 Q1 M1
                MaxBits = int(self.tableVM_IO[typ]['bits'])    # Anzahl bits
                if address > MaxBits:
                    raise LOGO('Address out of range. {0}1-{0}{1}'.format(typ, MaxBits))
                q, r = divmod(address - 1, 8)
                VMaddr = VMaddr + q
                bitNr = r
                return {'VMaddr': VMaddr, 'VMbit': bitNr, 'typ': typ, 'DataType': 'bit'}

            elif typ in ['AI', 'AQ', 'AM', 'NAI', 'NAQ']:    # AI1 AQ1 AM1
                MaxWords = int(self.tableVM_IO[typ]['words'])  # Anzahl words
                if address > MaxWords:
                    raise LOGO('Address out of range. {0}1-{0}{1}'.format(typ, MaxWords))
                VMaddr = VMaddr + ((address - 1) * 2)
                return {'VMaddr': VMaddr, 'typ': typ, 'DataType': 'word'}

            elif typ == 'VMW':    # VMW0
                #typ = 'VM'
                MaxBytes = int(self.tableVM_IO['VM']['bytes'])  # Anzahl words
                if address > MaxBytes:
                    raise LOGO('Address out of range. {0}0-{0}{1}'.format(typ, MaxBytes))
                VMaddr = VMaddr + address
                return {'VMaddr': VMaddr, 'typ': typ, 'DataType': 'word'}

            elif (typ == 'VM') and (indexComma == -1):    # VM0
                MaxBytes = int(self.tableVM_IO[typ]['bytes'])  # Anzahl bytes
                if address > MaxBytes:
                    raise LOGO('Address out of range. {0}0-{0}{1}'.format(typ, MaxBytes))
                VMaddr = VMaddr + address
                return {'VMaddr': VMaddr, 'typ': typ, 'DataType': 'byte'}

            elif (typ == 'VM') and (indexComma > 2):    # VM10.6
                MaxBytes = int(self.tableVM_IO[typ]['bytes'])  # Anzahl bytes
                if address > MaxBytes:
                    raise LOGO('Address out of range. {0}0-{0}{1}'.format(typ, MaxBytes))
                VMaddr = VMaddr + address
                return {'VMaddr': VMaddr, 'VMbit': bitNr, 'typ': typ, 'DataType': 'bit'}
            else:
                raise LOGO('invalid typ: {0}'.format(typ))

        except Exception as e:
            logger.error('LOGO: getAddressInfo() {0} : {1} '.format(value, e))
            return False

    def get_bit(self, byteval, idx):
        return ((byteval & (1 << idx)) != 0)

#***********************************************************************************************

    def int_to_bitarr(integer):
        string = bin(integer)[2:]
        arr = list()

        for bit in xrange(8 - len(string)):
            arr.append(0)

        for bit in string:
            arr.append(int(bit))

        arr.reverse()
        return arr

    #***********************************************************************************************
    #******************************** READ IN BYTE FORMAT ******************************************
    #INPUTS
    def get_input_byte(self, input_):
        if self.read_bytes(self.daveInputs, 0, input_, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #OUTPUTS
    def get_output_byte(self, output):
        if self.read_bytes(self.daveOutputs, 0, output, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #MARKS
    def get_marker_byte(self, marker):
        if self.read_bytes(self.daveFlags, 0, marker, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #VM
    def get_vm_byte(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 1):
            return self.dave.daveGetU8(self.dc)
        return -1

    #******************************** READ IN BIT FORMAT ******************************************
    #INPUTS
    def get_input(self, input, byte):
        m_byte = self.get_input_byte(input)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    #OUTPUTS
    def get_output(self, output, byte):
        m_byte = self.get_output_byte(output)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    def outputs(self):
        Q1 = self.get_output(0, 0)
        Q2 = self.get_output(0, 1)
        Q3 = self.get_output(0, 2)
        Q4 = self.get_output(0, 3)

        s = ('Q1 : ' + str(Q1))
        s += (', Q2 : ' + str(Q2))
        s += (', Q3 : ' + str(Q3))
        s += (', Q4 : ' + str(Q4))
        return s

    #MARKS
    def get_marker(self, marker, byte):
        m_byte = self.get_marker_byte(marker)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    #VM
    def get_vm(self, vm, byte):
        m_byte = self.get_vm_byte(vm)
        if m_byte >= 0:
            byte_arr = int_to_bitarr(m_byte)
            return byte_arr[byte]
        return False

    #******************************** READ IN WORD & DOUBLE FORMAT ********************************
    #VM
    def get_vm_word(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 2):
            return self.dave.daveGetU16(self.dc)
        return -1

    def get_vm_double(self, vm):
        if self.read_bytes(self.daveDB, 1, vm, 4):
            return self.dave.daveGetU32(self.dc)
        return -1

    #******************************** WRITE IN BYTE FORMAT ****************************************
    #OUTPUTS
    def write_output_byte(self, output, value):
        buffer = ctypes.c_byte(int(value))
        buffer_p = ctypes.pointer(buffer)
        return self.dave.daveWriteBytes(self.dc, self.daveOutputs, 0, output, 1, buffer_p)

    #MARKS
    def write_marker_byte(self, mark, value):
        buffer = ctypes.c_byte(int(value))
        buffer_p = ctypes.pointer(buffer)
        return self.dave.daveWriteBytes(self.dc, self.daveFlags, 0, mark, 1, buffer_p)

    #VM
    def write_vm_byte(self, vm, value):
        buffer = ctypes.c_byte(int(value))
        buffer_p = ctypes.pointer(buffer)
        return self.dave.daveWriteBytes(self.dc, self.daveDB, 1, vm, 1, buffer_p)

    #******************************** WRITE IN WORD & DOUBLE FORMAT *******************************
    #VM WORD
    def write_vm_word(self, vm, value):
        writeBuffer = ctypes.create_string_buffer(2)
        buffer_p = ctypes.pointer(writeBuffer)  # LesebufferIO
        writeBuffer[0] = ((value & 0xFF00) >> 8)
        writeBuffer[1] = (value & 0x00FF)
        #logger.debug('LOGO: write_vm_word() vm:{0} value:{1} w0:{2} w1:{3}'.format(vm, value,  writeBuffer[0],  writeBuffer[1]))
        return self.dave.daveWriteBytes(self.dc, self.daveDB, 1, vm, 2, buffer_p)

    #VM WORD
    def write_vm_double(self, vm):
        writeBuffer = ctypes.create_string_buffer(4)
        pBuf = ctypes.pointer(writeBuffer)  # LesebufferIO
        writeBuffer[0] = ((value & 0xFF000000) >> 32)
        writeBuffer[1] = ((value & 0x00FF0000) >> 16)
        writeBuffer[2] = ((value & 0x0000FF00) >> 8)
        writeBuffer[3] = (value & 0x000000FF)
        #logger.debug('LOGO: write_vm_word() vm:{0} value:{1} w0:{2} w1:{3}'.format(vm, value,  writeBuffer[0],  writeBuffer[1]))
        return self.dave.daveWriteBytes(self.dc, self.daveDB, 1, vm, 2, pBuf)

    #******************************** WRITE IN BIT FORMAT *****************************************
    #OUTPUTS
    def set_output_bit(self, output, position):
        return self.dave.daveSetBit(self.dc, self.daveOutputs, 0, output, position)

    def clear_output_bit(self, output, position):
        return self.dave.daveClrBit(self.dc, self.daveOutputs, 0, output, position)

    #VM
    def set_vm_bit(self, vm, position):
        return self.dave.daveSetBit(self.dc, self.daveDB, 1, vm, position)

    def clear_vm_bit(self, vm, position):
        return self.dave.daveClrBit(self.dc, self.daveDB, 1, vm, position)

    #MARKS
    def set_mark_bit(self, mark, position):
        return self.dave.daveSetBit(self.dc, self.daveFlags, 0, mark, position)

    def clear_mark_bit(self, mark, position):
        return self.dave.daveClrBit(self.dc, self.daveFlags, 0, mark, position)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = LOGO('smarthome-dummy')
    myplugin.connect()
    myplugin.run()
