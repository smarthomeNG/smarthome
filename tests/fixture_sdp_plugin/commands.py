#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Commands of the SDP fixture plugin."""

commands = {
    'status': {
        'power': {'read': True, 'write': True, 'opcode': 'PW', 'item_type': 'bool', 'dev_datatype': 'raw'},
        'volume': {'read': True, 'write': True, 'opcode': 'VO', 'item_type': 'num', 'dev_datatype': 'raw'},
        'input': {'read': True, 'read_cmd': 'IN{PARAM:zone}/{PARAM:host}', 'item_type': 'str', 'dev_datatype': 'str'},
        'mode': {'read': False, 'write': True, 'opcode': 'MO', 'item_type': 'str', 'dev_datatype': 'raw'},
        'info': {'read': False, 'write': False, 'item_type': 'str', 'dev_datatype': 'raw'},
    },
    'control': {'key': {'read': False, 'write': True, 'opcode': 'KY', 'item_type': 'bool', 'dev_datatype': 'raw'}},
}

lookups = {'COLORS': {'R': 'Red', 'G': 'Green'}}
