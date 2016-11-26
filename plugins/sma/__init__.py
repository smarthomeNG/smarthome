#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2013 Robert Budde                       robert@projekt131.de
#########################################################################
#  This software is based on Stuart Pittaway's "NANODE SMA PV MONITOR"
#  https://github.com/stuartpittaway/nanodesmapvmonitor
#
#  This software is based on SBF's "SMAspot"
#  https://code.google.com/p/sma-spot/
#
#  SMA-Plugin for SmartHome.py.   http://mknx.github.com/smarthome/
#
#	License: Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)
#	http://creativecommons.org/licenses/by-nc-sa/3.0/
#
#	You are free:
#		to Share — to copy, distribute and transmit the work
#		to Remix — to adapt the work
#	Under the following conditions:
#	Attribution:
#		You must attribute the work in the manner specified by the author or licensor
#		(but not in any way that suggests that they endorse you or your use of the work).
#	Noncommercial:
#		You may not use this work for commercial purposes.
#	Share Alike:
#		If you alter, transform, or build upon this work, you may distribute the resulting work
#		only under the same or similar license to this one.
#
# DISCLAIMER:
#	A user of this plugin acknowledges that he or she is receiving this
#	software on an "as is" basis and the user is not relying on the accuracy
#	or functionality of the software for any purpose. The user further
#	acknowledges that any use of this software will be at his own risk
#	and the copyright owner accepts no responsibility whatsoever arising from
#	the use or application of the software.
#########################################################################

import logging
import threading
import time
import socket
from datetime import datetime
from dateutil import tz
import itertools

BCAST_ADDR = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
ZERO_ADDR = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

SMANET2_HDR = bytes([0x7E, 0xFF, 0x03, 0x60, 0x65])

FCSTAB = [
    0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
    0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
    0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
    0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
    0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
    0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
    0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
    0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
    0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
    0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
    0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
    0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
    0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
    0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
    0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
    0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
    0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
    0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
    0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
    0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
    0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
    0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
    0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
    0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
    0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
    0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
    0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
    0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
    0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
    0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
    0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
    0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78,
]

attribute_to_text = {35: "Fault",
                     51: "Closed",
                     295: "MPP",
                     302: "No derating",
                     303: "Off",
                     307: "OK",
                     308: "On",
                     311: "Open",
                     336: "Contact manufacturer",
                     337: "Contact electrically qualified person",
                     338: "Invalid",
                     381: "Stop",
                     443: "Constant voltage",
                     455: "Warning",
                     557: "Temperature derating",
                     884: "Not active",
                     887: "None",
                     1129: "Yes",
                     1130: "No",
                     0xFFFFFD: "NaN",
                    }

# eval-id: eval-expression
lri_evals = {'num32bit_scaleby1': '(lambda x: x if x not in [0x80000000, 0xFFFFFFFF] else 0)(int.from_bytes(msg[i + 8:i + 12], byteorder="little"))',
             'num32bit_scaleby100.0': '(lambda x: x / 100.0 if x not in [0x80000000, 0xFFFFFFFF] else 0)(int.from_bytes(msg[i + 8:i + 12], byteorder="little"))',
             'num32bit_scaleby1000.0': '(lambda x: x / 1000.0 if x not in [0x80000000, 0xFFFFFFFF] else 0)(int.from_bytes(msg[i + 8:i + 12], byteorder="little"))',
             'num64bit_scaleby1': '(lambda x: x if x not in [0x8000000000000000, 0xFFFFFFFFFFFFFFFF] else 0)(int.from_bytes(msg[i + 8:i + 16], byteorder="little"))',
             'sw_version_decode': '"{}{}.{}{}.{:02d}.{}".format(msg[i + 27] >> 4, msg[i + 27] & 0xf, msg[i + 26] >> 4, msg[i + 26] & 0xf, msg[i + 25], msg[i + 24] if msg[i + 24] > 5 else "NEABRS"[msg[i + 24]])',
             'attribute_decode': '(lambda x: attribute_to_text[x[0]] if x[0] in attribute_to_text else "?")(list(__import__("itertools").dropwhile(lambda attr_tpl: (attr_tpl[1] != 1) or (attr_tpl[0] == 0xFFFFFE), [(int.from_bytes(msg[o:o + 3], byteorder="little"), msg[o + 3]) for o in range(i+8,i+40,4)]))[0])',
            }

TYPE_LABEL = (0x821E00, 0x8220FF, 0x58000200)

# logical ressource identifier: [eval, recordsize, [request-cmd, -start, -end]]
lris = {0x214800: ['attribute_decode', 40, (0x51800200, 0x214800, 0x2148FF)],
        0x251e00: ['num32bit_scaleby1', 28, (0x53800200, 0x251E00, 0x251EFF)],
        0x260100: ['num64bit_scaleby1', 16, (0x54000200, 0x260100, 0x2622FF)],
        0x262200: ['num64bit_scaleby1', 16, (0x54000200, 0x260100, 0x2622FF)],
        0x263f00: ['num32bit_scaleby1', 28, (0x51000200, 0x263F00, 0x263FFF)],
        0x411E00: ['num32bit_scaleby1', 28, (0x51000200, 0x411E00, 0x4120FF)],
        0x411F00: ['num32bit_scaleby1', 28, (0x51000200, 0x411E00, 0x4120FF)],
        0x412000: ['num32bit_scaleby1', 28, (0x51000200, 0x411E00, 0x4120FF)],
        0x416400: ['attribute_decode', 40, (0x51800200, 0x416400, 0x4164FF)],
        0x451f00: ['num32bit_scaleby100.0', 28, (0x53800200, 0x451F00, 0x4521FF)],
        0x452100: ['num32bit_scaleby1000.0', 28, (0x53800200, 0x451F00, 0x4521FF)],
        0x462E00: ['num64bit_scaleby1', 16, (0x54000200, 0x462E00, 0x462FFF)],
        0x462F00: ['num64bit_scaleby1', 16, (0x54000200, 0x462E00, 0x462FFF)],
        0x464000: ['num32bit_scaleby1', 28, (0x51000200, 0x464000, 0x4642FF)],
        0x464100: ['num32bit_scaleby1', 28, (0x51000200, 0x464000, 0x4642FF)],
        0x464200: ['num32bit_scaleby1', 28, (0x51000200, 0x464000, 0x4642FF)],
        0x464800: ['num32bit_scaleby100.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x464900: ['num32bit_scaleby100.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x464A00: ['num32bit_scaleby100.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x465000: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x465100: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x465200: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x464800, 0x4652FF)],
        0x465300: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x465300, 0x4655FF)],
        0x465400: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x465300, 0x4655FF)],
        0x465500: ['num32bit_scaleby1000.0', 28, (0x51000200, 0x465300, 0x4655FF)],
        0x465700: ['num32bit_scaleby100.0', 28, (0x51000200, 0x465700, 0x4657FF)],
        0x823400: ['sw_version_decode', 40, (0x58000200, 0x823400, 0x8234FF)],
       }

# sh.py-Name: field-id
name_to_id = {'STATUS': 0x214801,
              'DC_STRING1_P': 0x251e01,
              'DC_STRING2_P': 0x251e02,
              'E_TOTAL': 0x260101,
              'E_DAY': 0x262201,
              'AC_P_TOTAL': 0x263f01,
              'AC_P_MAX_NORM': 0x411E01,
              'AC_P_MAX_WARN': 0x411F01,
              'AC_P_MAX_ALRM': 0x412001,
              'GRID_RELAY': 0x416401,
              'DC_STRING1_U': 0x451f01,
              'DC_STRING2_U': 0x451f02,
              'DC_STRING1_I': 0x452101,
              'DC_STRING2_I': 0x452102,
              'OPERATING_TIME': 0x462E01,
              'FEEDING_TIME': 0x462F01,
              'AC_PHASE1_P': 0x464001,
              'AC_PHASE2_P': 0x464101,
              'AC_PHASE3_P': 0x464201,
              'AC_PHASE1_U': 0x464801,
              'AC_PHASE2_U': 0x464901,
              'AC_PHASE3_U': 0x464A01,
              'AC_PHASE1_I': 0x465001,
              'AC_PHASE2_I': 0x465101,
              'AC_PHASE3_I': 0x465201,
              'AC_PHASE1_I2': 0x465301,
              'AC_PHASE2_I2': 0x465401,
              'AC_PHASE3_I2': 0x465501,
              'GRID_FREQUENCY': 0x465701,
              'SW_VERSION': 0x823401,
             }

class SMA():

    def __init__(self, smarthome, bt_addr, password="0000", update_cycle="60", allowed_timedelta="10"):
        self.logger = logging.getLogger(__name__)
        self._sh = smarthome
        self._update_cycle = int(update_cycle)
        self._fields = {}
        self._requests = []
        self._cmd_lock = threading.Lock()
        self._reply_lock = threading.Condition()
        self._inv_bt_addr = bt_addr
        self._inv_password = password
        self._allowed_timedelta = int(allowed_timedelta)
        self._inv_last_read_timestamp_utc = 0
        self._inv_serial = 0
        self._own_bt_addr_le = bytearray(BCAST_ADDR)
        self._inv_bt_addr_le = bytearray.fromhex(self._inv_bt_addr.replace(':', ' '))
        self._inv_bt_addr_le.reverse()
        self._plugin_active_item = None

    def _update_values(self):
        #logger.warning("sma: signal strength = {}%%".format(self._inv_get_bt_signal_strength()))
        self._cmd_lock.acquire()
        try:
            for request in self._requests:
                if not self.alive:
                    break
                self._inv_send_request(request)
                if not self.alive:
                    break
                self._reply_lock.acquire()
                # wait 5sec for reply
                self._reply_lock.wait(5)
                self._reply_lock.release()
            if ('LAST_UPDATE' in self._fields) and not (self._inv_last_read_timestamp_utc == 0):
                self._inv_last_read_datetime = datetime.fromtimestamp(self._inv_last_read_timestamp_utc, tz.tzlocal())
                #self._inv_last_read_str = self._inv_last_read_datetime.strftime("%d.%m.%Y %H:%M:%S")
                self._inv_last_read_str = self._inv_last_read_datetime.strftime("%d.%m. %H:%M  ")
                for item in self._fields['LAST_UPDATE']['items']:
                    item(self._inv_last_read_str, 'SMA', self._inv_serial)
        except Exception as e:
            self.logger.error("sma: error while updating values - {}".format(e))
        self._cmd_lock.release()

    def run(self):
        self.alive = True
        self._is_connected = False
        if (self._plugin_active_item is None):
            self._plugin_active = True
        else:
            self._plugin_active = self._plugin_active_item()
        # "or self._is_connected" ensures the connection will be closed before terminating
        while (self.alive or self._is_connected):
            #self.logger.warning("sma: state self._is_connected = {} / self._plugin_active = {} / self.alive = {}".format(self._is_connected, self._plugin_active, self.alive))

            # connect to inverter if active but not connected
            if (self._plugin_active and not self._is_connected):
                self._cmd_lock.acquire()
                try:
                    self._btsocket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
                    self._btsocket.connect((self._inv_bt_addr, 1))
                    self.logger.info("sma: via bluetooth connected to {}".format(self._inv_bt_addr))
                    self._send_count = 0
                    self._inv_connect()
                    self._inv_login()
                    if 'OWN_ADDRESS' in self._fields:
                        for item in self._fields['OWN_ADDRESS']['items']:
                            item(self._own_bt_addr, 'SMA', self._inv_serial)
                    if 'INV_ADDRESS' in self._fields:
                        for item in self._fields['INV_ADDRESS']['items']:
                            item(self._inv_bt_addr, 'SMA', self._inv_serial)
                    if 'INV_SERIAL' in self._fields:
                        for item in self._fields['INV_SERIAL']['items']:
                            item(self._inv_serial, 'SMA', self._inv_serial)
                    self._is_connected = True
                except Exception as e:
                    self.logger.error("sma: establishing connection to inverter failed - {}".format(e))
                    # wait for 30sec and try to reconnect
                    time.sleep(30)
                    continue
                self._cmd_lock.release()

                # set time if diff is to big
                try:
                    if self._allowed_timedelta >= 0:
                        self._inv_send_request(lris[name_to_id['STATUS'] & 0xFFFF00][2])
                        msg = self._recv_smanet2_msg()
                        if (msg is not None):
                            host_localtime = int(time.time())
                            inv_localtime = int.from_bytes(msg[45:49], byteorder='little')
                            diff = inv_localtime - host_localtime
                            self.logger.info("sma: inverter timestamp = {}s / host timestamp = {}s / diff = {}s".format(inv_localtime, host_localtime, diff))
                            if (abs(diff) > self._allowed_timedelta) and not (inv_localtime == 0):
                                self._inv_set_time()
                                msg = self._recv_smanet2_msg()
                                if msg is None:
                                    self.logger.debug("sma: could not get reply while setting inverter time\n")
                                else:
                                    self.logger.debug("sma: reply while setting inverter time - len={} data=[{}]\n".format(len(msg), ', '.join(['0x%02x' % b for b in msg[41:]])))
                except Exception as e:
                    self.logger.error("sma: adjusting inverter time failed - {}".format(e))
                    return
                self._sh.scheduler.add('SMA', self._update_values, prio=5, cycle=self._update_cycle)

            # disconnect from inverter and stop updates if not active or if not alive
            if (self._is_connected and not (self._plugin_active and self.alive)):
                self._cmd_lock.acquire()
                try:
                    self._sh.scheduler.remove('SMA')
                except Exception as e:
                    self.logger.error("sma: removing sma.update from scheduler failed - {}".format(e))
                else:
                    self.logger.debug("sma: sma.update removed from scheduler")
                try:
                    self._btsocket.close()
                except Exception as e:
                    self.logger.error("sma: closing connection to inverter failed - {}".format(e))
                else:
                    self.logger.info("sma: connection to inverter closed")
                # set to False under all circumstances to force shutdown
                self._is_connected = False
                self._cmd_lock.release()
                continue

            # receive messages from inverter
            if (self._plugin_active and self._is_connected):
                msg = self._recv_smanet2_msg(no_timeout_warning=True)
                if not self.alive:
                    break
                if (msg is None):
                    #self.logger.debug("sma: no msg...")
                    continue
                if (len(msg) >= 60):
                    i = 41
                    try:
                        while (i < (len(msg) - 11)):
                            full_id = int.from_bytes(msg[i:i + 3], byteorder='little')
                            lri = full_id & 0xFFFF00
                            cls = full_id & 0x0000FF
                            dataType = msg[i + 3]
                            if lri not in lris:
                                self.logger.info("sma: unknown lri={:#06x} / cls={:#02x} / dataType={:#02x} - trying to continue".format(lri, cls, dataType))
                                if ((dataType == 0x00) or (dataType == 0x40)):
                                   i += 28
                                elif ((dataType == 0x08) or (dataType == 0x10)):
                                   i += 40
                                else:
                                    self.logger.error("sma: rx - unknown datatype {:#02x}".format(dataType))
                                    raise
                                continue
                            else:
                                timestamp_utc = int.from_bytes(msg[i + 4:i + 8], byteorder='little')
                                value = eval(lri_evals[lris[lri][0]], dict(msg=msg,i=i,attribute_to_text=attribute_to_text))
                                i += lris[lri][1]
                                self.logger.debug("sma: lri={:#06x} / cls={:#02x} / timestamp={} / value={}".format(lri, cls, timestamp_utc, value))
                                if full_id in self._fields:
                                    for item in self._fields[full_id]['items']:
                                        item(value, 'SMA', self._inv_serial, '{:#06x}'.format(full_id))
                                # update timestamp
                                if (timestamp_utc > self._inv_last_read_timestamp_utc):
                                    self._inv_last_read_timestamp_utc = timestamp_utc
                    except Exception as e:
                        self.logger.error("sma: rx: exception - {}".format(e))
                        self.logger.error("sma: rx - exception when parsing msg - len={} data=[{}]\n".format(len(msg), ', '.join(['0x%02x' % b for b in msg])))
                        continue
                elif (len(msg) == 44):
                    start_id = int.from_bytes(msg[33:36], byteorder='little')
                    end_id = int.from_bytes(msg[37:40], byteorder='little')
                    self.logger.info("sma: inverters returns \"no new data\" in id range from {:#06x} to {:#06x}".format(start_id, end_id))
                else:
                    self.logger.warning("sma: rx - unknown/malformed response!")
                    self.logger.warning("sma: rx - len={} data=[{}]\n".format(len(msg), ', '.join(['0x%02x' % b for b in msg])))
                    seq_num = int.from_bytes(msg[27:29], byteorder='little')
                    self.logger.warning("sma: sma2-seq={} / sma2-data=[{}]\n".format(seq_num, ' '.join(['0x%02x' % b for b in msg[29:]])))
                self._reply_lock.acquire()
                self._reply_lock.notifyAll()
                self._reply_lock.release()
            else:
                time.sleep(2)
        # this is the end of the while-loop

    def stop(self):
        self.alive = False

    def _update_plugin_active(self, item, caller=None, source=None, dest=None):
        self._plugin_active = item()
        self.logger.debug("sma: {} set plugin_active to {}".format(item, self._plugin_active))

    def parse_item(self, item):
        if 'sma' in item.conf:
            field_name = item.conf['sma']
            if field_name in name_to_id:
                field_id = name_to_id[field_name]
                lri = (field_id & 0xFFFF00)
                if lri not in lris:
                    self.logger.error("sma: {} connected to field {} requires unsupported lri {:#06x}".format(item, field_name, lri))
                    return None
                self.logger.debug("sma: {} connected to field {} ({:#06x})".format(item, field_name, field_id))
                if not field_id in self._fields:
                    self._fields[field_id] = {'items': [item], 'logics': []}
                else:
                    self._fields[field_id]['items'].append(item)
                field_request = lris[lri][2]
                if not field_request in self._requests:
                    self._requests.append(field_request)
            elif (field_name == "PLUGIN_ACTIVE"):
                self._plugin_active_item = item
                return self._update_plugin_active
            else:
                self.logger.debug("sma: {0} connected to field {1})".format(item, field_name))
                if not field_name in self._fields:
                    self._fields[field_name] = {'items': [item], 'logics': []}
                else:
                    if not item in self._fields[field_name]['items']:
                        self._fields[field_name]['items'].append(item)
        # return None to indicate "read-only"
        return None

    # receive function for SMANET1 messages
    def _recv_smanet1_msg(self, timeout=2.0, no_timeout_warning=False):
        try:
            # wait for sfd
            msg = bytearray()
            self._btsocket.settimeout(timeout)
            while (len(msg) < 4):
                msg += self._btsocket.recv(4)
                while (msg[0] != 0x7E):
                    msg.pop(0)
            # get level 1 length and validate
            if ((msg[1] ^ msg[2] ^ msg[3]) != 0x7E):
                self.logger.warning("sma: rx: length fields invalid")
                return None
            length = int.from_bytes(msg[1:3], byteorder='little')
            if (length < 18):
                self.logger.warning("sma: rx: length to small: {}".format(length))
                return None
            # get remaining bytes
            while (len(msg) < length):
                # receive at most only precisely the number of bytes that are
                # missing for this msg (allow follow-up msgs))
                msg += self._btsocket.recv(length - len(msg))
            # check src and dst addr and check
            if (msg[4:10] != self._inv_bt_addr_le):
                self.logger.warning("sma: rx: unknown src addr")
                return None
            if (msg[10:16] != self._own_bt_addr_le) and (msg[10:16] != ZERO_ADDR) and (msg[10:16] != BCAST_ADDR):
                self.logger.warning("sma: rx: wrong dst addr")
                return None

        except socket.timeout:
            if not no_timeout_warning:
                self.logger.warning("sma: rx: timeout exception - could not receive msg within {}s".format(timeout))
            msg = None
        except Exception as e:
            self.logger.error("sma: rx: exception - {}".format(e))
            msg = None
        return msg

    def _recv_smanet2_msg(self, no_timeout_warning=False):
        # allow receiving SMANET2 msgs which consist of multiple SMANET1
        # msgs!!!
        retries = 10
        smanet2_msg = bytearray()
        while self.alive:
            retries -= 1
            if (retries == 0):
                self.logger.warning("sma: recv smanet2 msg - retries used up!")
                return []
            smanet1_msg = self._recv_smanet1_msg(no_timeout_warning=no_timeout_warning)
            if smanet1_msg is None:
                break

            # get cmdcode - check for last message code (0x0001)
            smanet2_msg += smanet1_msg[18::]
            cmdcode_recv = int.from_bytes(smanet1_msg[16:18], byteorder='little')
            if (cmdcode_recv == 0x0001):
                break

        if (smanet2_msg == b'') and no_timeout_warning:
            return None

        if (smanet2_msg[0:5] != SMANET2_HDR):
            self.logger.warning("sma: no SMANET2 msg")
            self.logger.warning("sma: recv: len={} / data=[{}]".format(len(smanet2_msg), ' '.join(['0x%02x' % b for b in smanet2_msg])))
            return None

        # remove escape characters
        i = 0
        while True:
            if (smanet2_msg[i] == 0x7d):
                smanet2_msg[i + 1] ^= 0x20
                del(smanet2_msg[i])
            i += 1
            if (i == len(smanet2_msg)):
                break

        crc = self._calc_crc16(smanet2_msg[1:-3])
        if (crc != int.from_bytes(smanet2_msg[-3:-1], byteorder='little')):
            self.logger.warning("sma: crc: crc16 error - {:04x}".format(crc))
            self.logger.warning("sma: crc: len={} / data=[{}]".format(len(smanet2_msg), ' '.join(['0x%02x' % b for b in smanet2_msg])))
            return None
        return smanet2_msg

    def _recv_smanet1_msg_with_cmdcode(self, cmdcodes_expected=[0x0001]):
        retries = 3
        while self.alive:
            retries -= 1
            if (retries == 0):
                self.logger.warning("sma: recv msg with cmdcode - retries used up!")
                return None
            msg = self._recv_smanet1_msg()
            # get cmdcode
            if (msg != []) and (int.from_bytes(msg[16:18], byteorder='little') in cmdcodes_expected):
                break
        return msg

    def _send_msg(self, msg):
        if (len(msg) >= 0x3a):
            # calculate crc starting with byte 19 and append with LE byte-oder
            msg += self._calc_crc16(msg[19::]).to_bytes(2, byteorder='little')
            # add escape sequences starting with byte 19
            i = 19
            while True:
                if (msg[i] in [0x7d, 0x7e, 0x11, 0x12, 0x13]):
                    msg[i] ^= 0x20
                    msg.insert(i, 0x7d)
                i += 1
                if (i == len(msg)):
                    break
            # add msg delimiter
            msg += bytes([0x7e])
        # set length fields
        msg[1:3] = len(msg).to_bytes(2, byteorder='little')
        msg[3] = msg[1] ^ msg[2] ^ 0x7e
        #print("tx: len={} / data=[{}]".format(len(msg), ' '.join(['0x%02x' % b for b in msg])))
        self._btsocket.send(msg)

    def _calc_crc16(self, msg):
        crc = 0xFFFF
        for i in msg:
            crc = (crc >> 8) ^ FCSTAB[(crc ^ i) & 0xFF]
        crc ^= 0xFFFF
        #print("crc16 = {:x}".format(crc))
        return crc

    def _inv_connect(self):
        # receive broadcast-msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0002])

        # extract net-id from the 0x0002 msg
        self._net_id = msg[22]

        # reply with wildcard src addr
        msg[4:10] = ZERO_ADDR
        msg[10:16] = self._inv_bt_addr_le
        self._send_msg(msg)

        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x000a])
        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0005, 0x000c])
        # receive msg from inverter
        msg = self._recv_smanet1_msg_with_cmdcode([0x0005])

        if (msg == []):
            raise

        # extract own bluetooth addr
        self._own_bt_addr_le = msg[26:32]
        self.logger.info("sma: own bluetooth address: {}".format(':'.join(['%02x' % b for b in self._own_bt_addr_le[::-1]])))

        # first SMA net2 msg
        retries = 10
        while (retries > 0) and self.alive:
            retries -= 1
            # level1
            cmdcode = 0x0001
            msg = bytearray([0x7E, 0, 0, 0])
            msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
            # sma-net2 level
            ctrl = 0xA009
            self._send_count = (self._send_count + 1) & 0x7FFF
            msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x00]) + self._inv_bt_addr_le + bytes([0x00] + [0x00] + [0, 0, 0, 0]) + (self._send_count | 0x8000).to_bytes(2, byteorder='little')
            msg += bytes([0x00, 0x02, 0x00] + [0x00] + [0x00, 0x00, 0x00, 0x00] + [0x00, 0x00, 0x00, 0x00])
            # send msg to inverter
            self._send_msg(msg)
            # receive msg from inverter
            msg = self._recv_smanet2_msg()
            if (msg != []):
                break

        if (retries == 0):
            self.logger.warning("sma: connect - retries used up!")
            return

        # second SMA net2 msg
        cmdcode = 0x0001
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
        # sma-net2 level
        ctrl = 0xA008
        self._send_count = (self._send_count + 1) & 0x7FFF
        msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x03]) + self._inv_bt_addr_le + bytes([0x00] + [0x03] + [0, 0, 0, 0]) + (self._send_count | 0x8000).to_bytes(2, byteorder='little')
        msg += bytes([0x0E, 0x01, 0xFD, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        # send msg
        self._send_msg(msg)

    def _inv_login(self):
        timestamp_utc = int(time.time())
        password_pattern = [0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88, 0x88]
        password_pattern[0:len(self._inv_password)] = [((0x88 + ord(char)) & 0xff) for char in self._inv_password]

        retries = 5
        while (retries > 0) and self.alive:
            retries -= 1
            # level1
            cmdcode = 0x0001
            msg = bytearray([0x7E, 0, 0, 0])
            msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
            # sma-net2 level
            ctrl = 0xA00E
            self._send_count = (self._send_count + 1) & 0x7FFF
            msg += SMANET2_HDR + ctrl.to_bytes(2, byteorder='little') + BCAST_ADDR + bytes([0x00, 0x01]) + self._inv_bt_addr_le + \
                bytes([0x00] + [0x01] + [0, 0, 0, 0]) + (self._send_count | 0x8000).to_bytes(2, byteorder='little')
            msg += bytes([0x0C, 0x04, 0xFD, 0xFF, 0x07, 0x00, 0x00, 0x00, 0x84, 0x03, 0x00, 0x00])
            msg += timestamp_utc.to_bytes(4, byteorder='little')
            msg += bytes([0x00, 0x00, 0x00, 0x00] + password_pattern)
            # send msg to inverter
            self._send_msg(msg)
            # send msg to inverter
            self._send_msg(msg)
            # receive msg from inverter
            msg = self._recv_smanet2_msg()
            if (msg != []):
                break

        if (retries == 0):
            self.logger.warning("sma: login - retries used up!")
            return

        # extract serial
        self._inv_serial = int.from_bytes(msg[17:21], byteorder='little')
        self.logger.info("sma: inverter serial = {}".format(self._inv_serial))

    def _inv_get_bt_signal_strength(self):
        cmdcode = 0x0003
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
        msg += bytes([0x05, 0x00])
        self._send_msg(msg)
        msg = self._recv_smanet1_msg_with_cmdcode([0x0004])
        # extract signal strength
        return ((msg[22] * 100.0) / 0xff)

    def _inv_send_request(self, request_set):
        # send request
        # level1
        cmdcode = 0x0001
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
        # sma-net2 level
        self._send_count = (self._send_count + 1) & 0x7FFF
        msg += SMANET2_HDR + bytes([0x09, 0xA0]) + BCAST_ADDR + bytes([0x00, 0x00]) + self._inv_bt_addr_le + bytes([0x00] + [0x00] + [0, 0, 0, 0]) + (self._send_count | 0x8000).to_bytes(2, byteorder='little')
        msg += request_set[0].to_bytes(4, byteorder='little') + request_set[1].to_bytes(4, byteorder='little') + request_set[2].to_bytes(4, byteorder='little')
        # send msg to inverter
        #self.logger.debug("sma: requesting {:#06x}-{:#06x}...".format(request_set[1], request_set[2]))
        self._send_msg(msg)

    def _inv_set_time(self):
        # level1
        cmdcode = 0x0001
        msg = bytearray([0x7E, 0, 0, 0])
        msg += self._own_bt_addr_le + self._inv_bt_addr_le + cmdcode.to_bytes(2, byteorder='little')
        # sma-net2 level
        self._send_count = (self._send_count + 1) & 0x7FFF
        msg += SMANET2_HDR + bytes([0x10, 0xA0]) + BCAST_ADDR + bytes([0x00, 0x00]) + self._inv_bt_addr_le + bytes([0x00] + [0x00] + [0, 0, 0, 0]) + (self._send_count | 0x8000).to_bytes(2, byteorder='little')
        msg += int(0xF000020A).to_bytes(4, byteorder='little') + int(0x00236D00).to_bytes(4, byteorder='little') + int(0x00236D00).to_bytes(4, byteorder='little') + int(0x00236D00).to_bytes(4, byteorder='little')
        local_time = int(time.time()).to_bytes(4, byteorder='little')
        msg += local_time + local_time + local_time + round((datetime.now()-datetime.utcnow()).total_seconds()).to_bytes(4, byteorder='little') + local_time + bytes([0x01, 0x00, 0x00, 0x00])
#        msg += local_time + local_time + local_time + time.localtime().tm_gmtoff.to_bytes(4, byteorder='little') + local_time + bytes([0x01, 0x00, 0x00, 0x00])
        # send msg to inverter
        self._send_msg(msg)