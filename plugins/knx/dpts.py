#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.
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
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import struct
import datetime


def en1(value):
    return [int(value) & 0x01]


def de1(payload):
    if len(payload) != 1:
        return None
    return bool(payload[0] & 0x01)


def en2(payload):
    # control, value
    return [(payload[0] << 1) & 0x02 | payload[1] & 0x01]


def de2(payload):
    if len(payload) != 1:
        return None
    return [payload[0] >> 1 & 0x01, payload[0] & 0x01]


def en3(vlist):
    # direction, value
    return [(int(vlist[0]) << 3) & 0x08 | int(vlist[1]) & 0x07]


def de3(payload):
    if len(payload) != 1:
        return None
    # up/down, stepping
    return [payload[0] >> 3 & 0x01, payload[0] & 0x07]


def en4002(value):
    if isinstance(value, str):
        value = value.encode('iso-8859-1', 'replace')
    else:
        value = str(value)
    return [0, ord(value) & 0xff]


def de4002(payload):
    if len(payload) != 1:
        return None
    return payload.decode('iso-8859-1')


def en5(value):
    if value < 0:
        value = 0
    elif value > 255:
        value = 255
    return [0, int(value) & 0xff]


def de5(payload):
    if len(payload) != 1:
        return None
    return round(struct.unpack('>B', payload)[0], 1)


def en5001(value):
    if value < 0:
        value = 0
    elif value > 100:
        value = 100
    return [0, int(value * 255.0 / 100) & 0xff]


def de5001(payload):
    if len(payload) != 1:
        return None
    return round(struct.unpack('>B', payload)[0] * 100.0 / 255, 1)


def en6(value):
    if value < -128:
        value = -128
    elif value > 127:
        value = 127
    return [0, struct.pack('b', int(value))[0]]


def de6(payload):
    if len(payload) != 1:
        return None
    return struct.unpack('b', payload)[0]


def en7(value):
    ret = bytearray([0])
    ret.extend(struct.pack('>H', int(value)))
    return ret


def de7(payload):
    if len(payload) != 2:
        return None
    return struct.unpack('>H', payload)[0]


def en8(value):
    if value < -32768:
        value = -32768
    elif value > 32767:
        value = 32767
    ret = bytearray([0])
    ret.extend(struct.pack('>h', int(value)))
    return ret


def de8(payload):
    if len(payload) != 2:
        return None
    return struct.unpack('>h', payload)[0]


def en9(value):
    s = 0
    e = 0
    if value < 0:
        s = 0x8000
    m = int(value * 100)
    while (m > 2047) or (m < -2048):
        e = e + 1
        m = m >> 1
    num = s | (e << 11) | (int(m) & 0x07ff)
    return en7(num)


def de9(payload):
    if len(payload) != 2:
        return None
    i1 = payload[0]
    i2 = payload[1]
    s = (i1 & 0x80) >> 7
    e = (i1 & 0x78) >> 3
    m = (i1 & 0x07) << 8 | i2
    if s == 1:
        s = -1 << 11
    f = (m | s) * 0.01 * pow(2, e)
    return round(f, 2)


def en10(dt):
    return [0, (dt.isoweekday() << 5) | dt.hour, dt.minute, dt.second]


def de10(payload):
    h = payload[0] & 0x1f
    m = payload[1] & 0x3f
    s = payload[2] & 0x3f
    return datetime.time(h, m, s)


def en11(date):
    return [0, date.day, date.month, date.year - 2000]


def de11(payload):
    d = payload[0] & 0x1f
    m = payload[1] & 0x0f
    y = (payload[2] & 0x7f) + 2000  # sorry no 20th century...
    return datetime.date(y, m, d)


def en12(value):
    if value < 0:
        value = 0
    elif value > 4294967295:
        value = 4294967295
    ret = bytearray([0])
    ret.extend(struct.pack('>I', int(value)))
    return ret


def de12(payload):
    if len(payload) != 4:
        return None
    return struct.unpack('>I', payload)[0]


def en13(value):
    if value < -2147483648:
        value = -2147483648
    elif value > 2147483647:
        value = 2147483647
    ret = bytearray([0])
    ret.extend(struct.pack('>i', int(value)))
    return ret


def de13(payload):
    if len(payload) != 4:
        return None
    return struct.unpack('>i', payload)[0]


def en14(value):
    ret = bytearray([0])
    ret.extend(struct.pack('>f', int(value)))
    return ret


def de14(payload):
    if len(payload) != 4:
        return None
    return struct.unpack('>f', payload)[0]


def en16000(value):
    enc = bytearray(1)
    enc.extend(value.encode('ascii', 'replace')[:14])
    enc.extend([0] * (15 - len(enc)))
    return enc


def en16001(value):
    enc = bytearray(1)
    enc.extend(value.encode('iso-8859-1', 'replace')[:14])
    enc.extend([0] * (15 - len(enc)))
    return enc


def de16000(payload):
    return payload.rstrip(b'0').decode()


def de16001(payload):
    return payload.rstrip(b'0').decode('iso-8859-1')


def en17(value):
    return [0, int(value) & 0x3f]


def de17(payload):
    if len(payload) != 1:
        return None
    return struct.unpack('>B', payload)[0] & 0x3f


def en20(value):
    return [0, int(value) & 0xff]


def de20(payload):
    if len(payload) != 1:
        return None
    return struct.unpack('>B', payload)[0]


def en24(value):
    enc = bytearray(1)
    enc.extend(value.encode('iso-8859-1', 'replace'))
    enc.append(0)
    return enc


def de24(payload):
    return payload.rstrip(b'\x00').decode('iso-8859-1')


def en232(value):
    return [0, int(value[0]) & 0xff, int(value[1]) & 0xff, int(value[2]) & 0xff]


def de232(payload):
    if len(payload) != 3:
        return None
    return list(struct.unpack('>BBB', payload))


def depa(string):
    if len(string) != 2:
        return None
    pa = struct.unpack(">H", string)[0]
    return "{0}.{1}.{2}".format((pa >> 12) & 0x0f, (pa >> 8) & 0x0f, (pa) & 0xff)


def enga(ga):
    ga = ga.split('/')
    return [int(ga[0]) << 3 | int(ga[1]), int(ga[2])]


def dega(string):
    if len(string) != 2:
        return None
    ga = struct.unpack(">H", string)[0]
    return "{0}/{1}/{2}".format((ga >> 11) & 0x1f, (ga >> 8) & 0x07, (ga) & 0xff)


decode = {
    '1': de1,
    '2': de2,
    '3': de3,
    '4002': de4002,
    '4.002': de4002,
    '5': de5,
    '5001': de5001,
    '5.001': de5001,
    '6': de6,
    '7': de7,
    '8': de8,
    '9': de9,
    '10': de10,
    '11': de11,
    '12': de12,
    '13': de13,
    '14': de14,
    '16000': de16000,
    '16': de16000,
    '16001': de16001,
    '16.001': de16001,
    '17': de17,
    '20': de20,
    '24': de24,
    '232': de232,
    'pa': depa,
    'ga': dega
}

encode = {
    '1': en1,
    '2': en2,
    '3': en3,
    '4002': en4002,
    '4.002': en4002,
    '5': en5,
    '5001': en5001,
    '5.001': en5001,
    '6': en6,
    '7': en7,
    '8': en8,
    '9': en9,
    '10': en10,
    '11': en11,
    '12': en12,
    '13': en13,
    '14': en14,
    '16000': en16000,
    '16': en16000,
    '16001': en16001,
    '16.001': en16001,
    '17': en17,
    '20': en20,
    '24': en24,
    '232': en232,
    'ga': enga
}
# DPT: 19, 28
