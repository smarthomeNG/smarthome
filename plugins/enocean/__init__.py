#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013-2014 Robert Budde                   robert@ing-budde.de
#  Copyright 2014 Alexander Schwithal                 aschwith
#########################################################################
#  Enocean plugin for SmartHome.py.      http://mknx.github.io/smarthome/
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

import serial
import os
import sys
import logging
import struct
import time
import threading
from . import eep_parser

FCSTAB = [
    0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15,
    0x38, 0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d,
    0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
    0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d,
    0xe0, 0xe7, 0xee, 0xe9, 0xfc, 0xfb, 0xf2, 0xf5,
    0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
    0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85,
    0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba, 0xbd,
    0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
    0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea,
    0xb7, 0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2,
    0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
    0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32,
    0x1f, 0x18, 0x11, 0x16, 0x03, 0x04, 0x0d, 0x0a,
    0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
    0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a,
    0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b, 0x9c,
    0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
    0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec,
    0xc1, 0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4,
    0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
    0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44,
    0x19, 0x1e, 0x17, 0x10, 0x05, 0x02, 0x0b, 0x0c,
    0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
    0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b,
    0x76, 0x71, 0x78, 0x7f, 0x6A, 0x6d, 0x64, 0x63,
    0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
    0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13,
    0xae, 0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb,
    0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8D, 0x84, 0x83,
    0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb,
    0xe6, 0xe1, 0xe8, 0xef, 0xfa, 0xfd, 0xf4, 0xf3
    ]

PACKET_SYNC_BYTE              = 0x55

PACKET_TYPE_RADIO             = 0x01   # Packet Type Radio ERP1
PACKET_TYPE_RESPONSE          = 0x02
PACKET_TYPE_EVENT             = 0x04   # Event
PACKET_TYPE_COMMON_COMMAND    = 0x05
PACKET_TYPE_SMART_ACK_COMMAND = 0x06   # Smart Ack command
PACKET_REMOTE_MAN_COMMAND     = 0x07   # Remote management command
PACKET_TYPE_RADIO_MESSAGE     = 0x09
PACKET_TYPE_RADIO_ERP2        = 0x0A   # ERP2 protocol radio telegram


CO_WR_RESET            = 0x02
CO_RD_VERSION          = 0x03
CO_WR_BIST             = 0x06          # Perform built in self test
CO_RD_IDBASE           = 0x08          # Read base ID number
CO_WR_LEARNMODE        = 0x23          # Function: Enables or disables learn mode of Controller.
CO_RD_LEARNMODE        = 0x24          # Function: Reads the learn-mode state of Controller.
CO_RD_NUMSECUREDEVICES = 0x29          # Read number of taught in secure devices
CO_RD_SECUREDEVICE     = 0x30          # Read secure device by ID

SENT_RADIO_PACKET              = 0xFF
SENT_ENCAPSULATED_RADIO_PACKET = 0xA6

logger = logging.getLogger('EnOcean')

class EnOcean():

    def __init__(self, smarthome, serialport, tx_id=''):
        self._sh = smarthome
        self.port = serialport
        if (len(tx_id) < 8):
            self.tx_id = 0
            logger.warning('enocean: No valid enocean stick ID configured. Transmitting is not supported')
        else:
            self.tx_id = int(tx_id, 16)
            logger.info('enocean: Stick TX ID configured via plugin.conf to: {0}'.format(tx_id))
        self._tcm = serial.Serial(serialport, 57600, timeout=0.5)
        self._cmd_lock = threading.Lock()
        self._response_lock = threading.Condition()
        self._rx_items = {}
        self._block_ext_out_msg = False
        self.eep_parser = eep_parser.EEP_Parser()

    def eval_telegram(self, sender_id, data, opt):
        for item in self._items:
            # validate id for item id:
            if item.conf['enocean_id'] == sender_id:
                #print ("validated {0} for {1}".format(sender_id,item))
                #print ("try to get value for: {0} and {1}".format(item.conf['enocean_rorg'][0],item.conf['enocean_rorg'][1]))
                rorg = item.conf['enocean_rorg']
                eval_value = item.conf['enocean_value']
                if rorg in RADIO_PAYLOAD_VALUE:  # check if RORG exists
                    pl = eval(RADIO_PAYLOAD_VALUE[rorg]['payload_idx'])
                    #could be nicer
                    for entity in RADIO_PAYLOAD_VALUE:
                        if (rorg == entity) and (eval_value in RADIO_PAYLOAD_VALUE[rorg]['entities']):
                            value_dict = RADIO_PAYLOAD_VALUE[rorg]['entities']
                            value = eval(RADIO_PAYLOAD_VALUE[rorg]['entities'][eval_value])
                            logger.debug("Resulting value: {0} for {1}".format(value, item))
                            if value:  # not shure about this
                                item(value, 'EnOcean', 'RADIO')

    def _process_packet_type_event(self, data, optional):
        event_code = data[0]
        if(event_code == CO_EVENT_SECUREDEVICES):
            logger.info("enocean: secure device event packet received")
        else:
            logger.warning("enocean: unknown event packet received")

    def _rocker_sequence(self, item, sender_id, sequence):
        try:
            for step in sequence:
                event, relation, delay = step.split()             
                #logger.debug("waiting for {} {} {}".format(event, relation, delay))
                if item._enocean_rs_events[event.upper()].wait(float(delay)) != (relation.upper() == "WITHIN"):
                    logger.debug("NOT {} - aborting sequence!".format(step))
                    return
                else:
                    logger.debug("{}".format(step))
                    item._enocean_rs_events[event.upper()].clear()
                    continue          
            value = True
            if 'enocean_rocker_action' in item.conf:
                if item.conf['enocean_rocker_action'].upper() == "UNSET":
                    value = False
                elif item.conf['enocean_rocker_action'].upper() == "TOGGLE":
                    value = not item()
            item(value, 'EnOcean', "{:08X}".format(sender_id))
        except Exception as e:
            logger.error("enocean: error handling enocean_rocker_sequence \"{}\" - {}".format(sequence, e))        

    def _process_packet_type_radio(self, data, optional):
        #logger.warning("enocean: processing radio message with data = [{}] / optional = [{}]".format(', '.join(['0x%02x' % b for b in data]), ', '.join(['0x%02x' % b for b in optional])))

        choice = data[0]
        payload = data[1:-5]
        sender_id = int.from_bytes(data[-5:-1], byteorder='big', signed=False)
        status = data[-1]
        repeater_cnt = status & 0x0F
        logger.info("enocean: radio message: choice = {:02x} / payload = [{}] / sender_id = {:08X} / status = {} / repeat = {}".format(choice, ', '.join(['0x%02x' % b for b in payload]), sender_id, status, repeater_cnt))

        if (len(optional) == 7):
            subtelnum = optional[0]
            dest_id = int.from_bytes(optional[1:5], byteorder='big', signed=False)
            dBm = -optional[5]
            SecurityLevel = optional[6]
            logger.debug("enocean: radio message with additional info: subtelnum = {} / dest_id = {:08X} / signal = {}dBm / SecurityLevel = {}".format(subtelnum, dest_id, dBm, SecurityLevel))

        if sender_id in self._rx_items:
            logger.debug("enocean: Sender ID found in item list")
            # iterate over all eep known for this id and get list of associated items
            for eep,items in self._rx_items[sender_id].items():
                # check if choice matches first byte in eep (this seems to be the only way to find right eep for this particular packet)
                if eep.startswith("{:02X}".format(choice)):
                    # call parser for particular eep - returns dictionary with key-value pairs
                    results = self.eep_parser.Parse(eep, payload, status)
                    #logger.debug("enocean: radio message results = {}".format(results))
                    for item in items:
                        rx_key = item.conf['enocean_rx_key'].upper()
                        if rx_key in results:
                            if 'enocean_rocker_sequence' in item.conf:
                                try:   
                                    if hasattr(item, '_enocean_rs_thread') and item._enocean_rs_thread.isAlive():
                                        if results[rx_key]:
                                            logger.debug("sending pressed event")
                                            item._enocean_rs_events["PRESSED"].set()
                                        else:
                                            logger.debug("sending released event")
                                            item._enocean_rs_events["RELEASED"].set()
                                    elif results[rx_key]:
                                        item._enocean_rs_events = {'PRESSED': threading.Event(), 'RELEASED': threading.Event()}
                                        item._enocean_rs_thread = threading.Thread(target=self._rocker_sequence, name="enocean-rs", args=(item, sender_id, item.conf['enocean_rocker_sequence'].split(','), ))
                                        #logger.info("starting enocean_rocker_sequence thread")
                                        item._enocean_rs_thread.daemon = True
                                        item._enocean_rs_thread.start()
                                except Exception as e:
                                    logger.error("enocean: error handling enocean_rocker_sequence - {}".format(e))
                            else:
                                item(results[rx_key], 'EnOcean', "{:08X}".format(sender_id))
        elif (sender_id <= self.tx_id + 127) and (sender_id >= self.tx_id):
            logger.debug("enocean: Received repeated enocean stick message")
        else:
            logger.info("unknown ID = {:08X}".format(sender_id))

    def _process_packet_type_response(self, data, optional):
        RETURN_CODES = ['OK', 'ERROR', 'NOT SUPPORTED', 'WRONG PARAM', 'OPERATION DENIED']
        if (self._last_cmd_code == SENT_RADIO_PACKET) and (len(data) == 1):
            logger.debug("enocean: sending command returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_WR_RESET) and (len(data) == 1):
            logger.info("enocean: Reset returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_WR_LEARNMODE) and (len(data) == 1):
            logger.info("enocean: Write LearnMode returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_RD_VERSION):
            if (data[0] == 0) and (len(data) == 33):
                logger.info("enocean: Chip ID = 0x{} / Chip Version = 0x{}".format(''.join(['%02x' % b for b in data[9:13]]), ''.join(['%02x' % b for b in data[13:17]])))
                logger.info("enocean: APP version = {} / API version = {} / App description = {}".format('.'.join(['%d' % b for b in data[1:5]]), '.'.join(['%d' % b for b in data[5:9]]), ''.join(['%c' % b for b in data[17:33]])))
            elif (data[0] == 0) and (len(data) == 0):
                logger.error("enocean: Reading version: No answer")
            else:
                logger.error("enocean: Reading version returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_RD_IDBASE):
            if (data[0] == 0) and (len(data) == 5):
                logger.info("enocean: Base ID = 0x{}".format(''.join(['%02x' % b for b in data[1:5]])))
                if (self.tx_id == 0):
                    self.tx_id = int.from_bytes(data[1:5], byteorder='big', signed=False)
                    logger.info("enocean: Transmit ID set set automatically by reading chips BaseID")
                if (len(optional) == 1):
                    logger.info("enocean: Remaining write cycles for Base ID = {}".format(optional[0]))
            elif (data[0] == 0) and (len(data) == 0):
                logger.error("enocean: Reading Base ID: No answer")
            else:
                logger.error("enocean: Reading Base ID returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_WR_BIST):
            if (data[0] == 0) and (len(data) == 2):
                if (data[1] == 0):
                    logger.info("enocean: built in self test result: All OK")
                else:
                    logger.info("enocean: built in self test result: Problem, code = {}".format(data[1]))
            elif (data[0] == 0) and (len(data) == 0):
                logger.error("enocean: Doing built in self test: No answer")
            else:
                logger.error("enocean: Doing built in self test returned code = {}".format(RETURN_CODES[data[0]]))
        elif (self._last_cmd_code == CO_RD_LEARNMODE):
            if (data[0] == 0) and (len(data) == 2):
                logger.info("enocean: Reading LearnMode = 0x{}".format(''.join(['%02x' % b for b in data[1]])))
                if (len(optional) == 1):
                    logger.info("enocean: learn channel = {}".format(optional[0]))
            elif (data[0] == 0) and (len(data) == 0):
                logger.error("enocean: Reading LearnMode: No answer")
        elif (self._last_cmd_code == CO_RD_NUMSECUREDEVICES):
            if (data[0] == 0) and (len(data) == 2):
                logger.info("enocean: Number of taught in devices = 0x{}".format(''.join(['%02x' % b for b in data[1]])))
            elif (data[0] == 0) and (len(data) == 0):
                logger.error("enocean: Reading NUMSECUREDEVICES: No answer")
            elif (data[0] == 2) and (len(data) == 1):
                logger.error("enocean: Reading NUMSECUREDEVICES: Command not supported")
            else:
                logger.error("enocean: Reading NUMSECUREDEVICES: Unknown error")

        else:
            logger.error("enocean: processing unexpected response with return code = {} / data = [{}] / optional = [{}]".format(RETURN_CODES[data[0]], ', '.join(['0x%02x' % b for b in data]), ', '.join(['0x%02x' % b for b in optional])))
        self._response_lock.acquire()
        self._response_lock.notify()
        self._response_lock.release()

    def _startup(self):
        # request one time information
        logger.info("enocean: resetting device")
        self._send_common_command(CO_WR_RESET)
        logger.info("enocean: requesting id-base")
        self._send_common_command(CO_RD_IDBASE)
        logger.info("enocean: requesting version information")
        self._send_common_command(CO_RD_VERSION)
        logger.debug("enocean: ending connect-thread")

    def run(self):
        self.alive = True
        t = threading.Thread(target=self._startup, name="enocean-startup")
        t.daemon = True
        t.start()
        msg = []
        while self.alive:
            readin = self._tcm.read(1000)
            if readin:
                msg += readin
                #logger.debug("enocean: data received")
                # check if header is complete (6bytes including sync)
                # 0x55 (SYNC) + 4bytes (HEADER) + 1byte(HEADER-CRC)
                while (len(msg) >= 6):
                    #check header for CRC
                    if (msg[0] == PACKET_SYNC_BYTE) and (self._calc_crc8(msg[1:5]) == msg[5]):
                        # header bytes: sync; length of data (2); optional length; packet type; crc
                        data_length = (msg[1] << 8) + msg[2]
                        opt_length = msg[3]
                        packet_type = msg[4]
                        msg_length = data_length + opt_length + 7
                        logger.debug("enocean: received header with data_length = {} / opt_length = 0x{:02x} / type = {}".format(data_length, opt_length, packet_type))

                        # break if msg is not yet complete:
                        if (len(msg) < msg_length):
                            break

                        # msg complete
                        if (self._calc_crc8(msg[6:msg_length - 1]) == msg[msg_length - 1]):
                            logger.debug("enocean: accepted package with type = 0x{:02x} / len = {} / data = [{}]!".format(packet_type, msg_length, ', '.join(['0x%02x' % b for b in msg])))
                            data = msg[6:msg_length - (opt_length + 1)]
                            optional = msg[(6 + data_length):msg_length - 1]
                            if (packet_type == PACKET_TYPE_RADIO):
                                self._process_packet_type_radio(data, optional)
                            elif (packet_type == PACKET_TYPE_RESPONSE):
                                self._process_packet_type_response(data, optional)
                            elif (packet_type == PACKET_TYPE_EVENT):
                                self._process_packet_type_event(data, optional)
                            else:
                                logger.error("enocean: received packet with unknown type = 0x{:02x} - len = {} / data = [{}]".format(packet_type, msg_length, ', '.join(['0x%02x' % b for b in msg])))
                        else:
                            logger.error("enocean: crc error - dumping packet with type = 0x{:02x} / len = {} / data = [{}]!".format(packet_type, msg_length, ', '.join(['0x%02x' % b for b in msg])))
                        msg = msg[msg_length:]
                    else:
                        #logger.warning("enocean: consuming [0x{:02x}] from input buffer!".format(msg[0]))
                        msg.pop(0)

    def stop(self):
        self.alive = False
        logger.info("enocean: Thread stopped")

    def parse_item(self, item):
        if 'enocean_rx_key' in item.conf:
            # look for info from the most specific info to the broadest (key->eep->id) - one id might use multiple eep might define multiple keys
            eep_item = item
            while (not 'enocean_rx_eep' in eep_item.conf):
                eep_item = eep_item.return_parent()
                if (eep_item is self._sh):
                    logger.error("enocean: could not find enocean_rx_eep for item {}".format(item))
                    return None
            id_item = eep_item
            while (not 'enocean_rx_id' in id_item.conf):
                id_item = id_item.return_parent()
                if (id_item is self._sh):
                    logger.error("enocean: could not find enocean_rx_id for item {}".format(item))
                    return None

            rx_key = item.conf['enocean_rx_key'].upper()
            rx_eep = eep_item.conf['enocean_rx_eep'].upper()
            rx_id = int(id_item.conf['enocean_rx_id'],16)

            # check if there is a function to parse payload
            if not self.eep_parser.CanParse(rx_eep):
                return None

            if (rx_key in ['A0', 'A1', 'B0', 'B1']):
                logger.warning("enocean: key \"{}\" does not match EEP - \"0\" (Zero, number) should be \"O\" (letter) (same for \"1\" and \"I\") - will be accepted for now".format(rx_key))
                item.conf['enocean_rx_key'] = rx_key = rx_key.replace('0', 'O').replace("1", 'I')

            if (not rx_id in self._rx_items):
                self._rx_items[rx_id] = {rx_eep: [item]}
            elif (not rx_eep in self._rx_items[rx_id]):
                self._rx_items[rx_id][rx_eep] = [item]
            elif (not item in self._rx_items[rx_id][rx_eep]):
                self._rx_items[rx_id][rx_eep].append(item)

            logger.info("enocean: item {} listens to id {:08X} with eep {} key {}".format(item, rx_id, rx_eep, rx_key))
            #logger.info("enocean: self._rx_items = {}".format(self._rx_items))
            return self.update_item

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'EnOcean':
            logger.debug('enocean: item updated externally')
            if self._block_ext_out_msg:
                logger.debug('enocean: sending manually blocked by user. Aborting')
                return
            if 'enocean_tx_eep' in item.conf:
                if isinstance(item.conf['enocean_tx_eep'], str):
                    tx_eep = item.conf['enocean_tx_eep']
                    logger.debug('enocean: item has tx_eep')
                    id_offset = 0
                    if 'enocean_tx_id_offset' in item.conf and (isinstance(item.conf['enocean_tx_id_offset'], str)):
                        logger.debug('enocean: item has valid enocean_tx_id_offset')
                        id_offset = int(item.conf['enocean_tx_id_offset'])
                    #if (isinstance(item(), bool)):
                    #if item.conf['type'] == bool:
                    #Identify send command based on tx_eep coding:
                    if(tx_eep == 'A5_38_08_02'):
                        #if isinstance(item, bool):
                        logger.debug('enocean: item is A5_38_08_02 type')
                        if not item():
                            self.send_dim(id_offset, 0, 0)
                            logger.debug('enocean: sent off command')
                        else:
                            if 'ref_level' in item.level.conf:
                                dim_value = int(item.level.conf['ref_level'])
                                logger.debug('enocean: ref_level found')
                            else:
                                dim_value = 100
                                logger.debug('enocean: no ref_level found. Setting to default 100')
                            self.send_dim(id_offset, dim_value, 0)
                            logger.debug('enocean: sent dim on command')
                    elif(tx_eep == 'A5_38_08_03'):
                        logger.debug('enocean: item is A5_38_08_03 type')
                        self.send_dim(id_offset, item(), 0)
                        logger.debug('enocean: sent dim command')
                    elif(tx_eep == 'A5_38_08_01'):
                        logger.debug('enocean: item is A5_38_08_01 type')
                        self.send_switch(id_offset, item(), 0)
                        logger.debug('enocean: sent switch command')
                    else:
                        logger.error('enocean: error: Unknown tx eep command')
                else:
                    logger.error('enocean: tx_eep is not a string value')
            else:
                logger.debug('enocean: item has no tx_eep value')

    def read_num_securedivices(self):
        self._send_common_command(CO_RD_NUMSECUREDEVICES)
        logger.info("enocean: Read number of secured devices")

    def enter_learn_mode(self, onoff=1):
        if (onoff == 1):
            self._send_common_command(CO_WR_LEARNMODE, [0x01, 0x00, 0x00, 0x00, 0x00],[0xFF])
            logger.info("enocean: entering learning mode")
        else:
            self._send_common_command(CO_WR_LEARNMODE, [0x00, 0x00, 0x00, 0x00, 0x00],[0xFF])
            logger.info("enocean: leaving learning mode")

    def reset_stick(self):
        logger.info("enocean: resetting device")
        self._send_common_command(CO_WR_RESET)

    def block_external_out_messages(self, block=True):
        if block:
            logger.info("enocean: Blocking of external out messages activated")
            self._block_ext_out_msg = True
        elif not block:
            logger.info("enocean: Blocking of external out messages deactivated")
            self._block_ext_out_msg = False
        else:
            logger.info("enocean: invalid argument. Must be True/False")

    def send_bit(self):
        logger.info("enocean: trigger Built-In Self Test telegram")
        self._send_common_command(CO_WR_BIST)

    def version(self):
        logger.info("enocean: request stick version")
        self._send_common_command(CO_RD_VERSION)

    def _send_packet(self, packet_type, data=[], optional=[]):
        length_optional = len(optional)
        if length_optional > 255:
            logger.error("enocean: optional too long ({} bytes, 255 allowed)".format(length_optional))
            return
        length_data = len(data)
        if length_data > 65535:
            logger.error("enocean: data too long ({} bytes, 65535 allowed)".format(length_data))
            return

        packet = bytearray([PACKET_SYNC_BYTE])
        packet += length_data.to_bytes(2, byteorder='big') + bytes([length_optional, packet_type])
        packet += bytes([self._calc_crc8(packet[1:5])])
        packet += bytes(data + optional)
        packet += bytes([self._calc_crc8(packet[6:])])
        #logger.warning("enocean: sending packet with len = {} / data = [{}]!".format(len(packet), ', '.join(['0x%02x' % b for b in packet])))
        self._tcm.write(packet)

    def _send_common_command(self, _code, data=[], optional=[]):
        self._cmd_lock.acquire()
        self._last_cmd_code = _code
        self._send_packet(PACKET_TYPE_COMMON_COMMAND, [_code] + data, optional)
        self._response_lock.acquire()
        # wait 5sec for response
        self._response_lock.wait(5)
        self._response_lock.release()
        self._cmd_lock.release()

    def _send_radio_packet(self, id_offset, _code, data=[], optional=[]):
        if (id_offset < 0) or (id_offset > 127):
            logger.error("enocean: invalid base ID offset range. (Is {}, must be [0 127])".format(id_offset))
            return
        self._cmd_lock.acquire()
        self._last_cmd_code = SENT_RADIO_PACKET
        self._send_packet(PACKET_TYPE_RADIO, [_code] + data + list((self.tx_id + id_offset).to_bytes(4, byteorder='big')) + [0x00], optional)
        self._response_lock.acquire()
        # wait 5sec for response
        self._response_lock.wait(5)
        self._response_lock.release()
        self._cmd_lock.release()

    def send_dim(self,id_offset=0, dim=0, dimspeed=0):
        if (dimspeed < 0) or (dimspeed > 255):
            logger.error("enocean: sending dim command A5_38_08: invalid range of dimspeed")
            return
        logger.debug("enocean: sending dim command A5_38_08")
        if (dim == 0):
            self._send_radio_packet(id_offset, 0xA5, [0x02, 0x00, dimspeed, 0x08])
        elif (dim > 0) and (dim <= 100):
            self._send_radio_packet(id_offset, 0xA5, [0x02, dim, dimspeed, 0x09])
        else:
            logger.error("enocean: sending command A5_38_08: invalid dim value")

    def send_switch(self,id_offset=0, on=0, block=0):
        if (block < 0) and (block > 1):
            logger.error("enocean: sending switch command A5_38_08: invalid range of block (0,1)")
            return
        logger.debug("enocean: sending switch command A5_38_08")
        if (on == 0):
            self._send_radio_packet(id_offset, 0xA5, [0x01, 0x00, 0x00, 0x08])
        elif (on == 1) and (block == 0):
            self._send_radio_packet(id_offset, 0xA5, [0x01, 0x00, 0x00, 0x09])
        else:
            logger.error("enocean: sending command A5_38_08: error")

    def send_learn_dim(self, id_offset=0):
        if (id_offset < 0) or (id_offset > 127):
            logger.error("enocean: ID offset out of range (0-127). Aborting.")
            return
        logger.info("enocean: sending learn telegram for dim command")
        self._send_radio_packet(id_offset, 0xA5, [0x02, 0x00, 0x00, 0x00])

    def send_learn_switch(self, id_offset=0):
        if (id_offset < 0) or (id_offset > 127):
            logger.error("enocean: ID offset out of range (0-127). Aborting.")
            return
        logger.info("enocean: sending learn telegram for switch command")
        self._send_radio_packet(id_offset, 0xA5, [0x01, 0x00, 0x00, 0x00])

    def _calc_crc8(self, msg, crc=0):
        for i in msg:
            crc = FCSTAB[crc ^ i]
        return crc
