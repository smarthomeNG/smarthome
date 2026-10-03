#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""commands.py fixture for tests/sdp_harness: a small command tree covering read, write and grouped commands"""

commands = {
    'status': {
        'power': {'read': True, 'write': True, 'opcode': 'PW', 'item_type': 'bool', 'dev_datatype': 'raw'},
        'volume': {'read': True, 'write': True, 'opcode': 'VO', 'item_type': 'num', 'dev_datatype': 'raw'},
    }
}
