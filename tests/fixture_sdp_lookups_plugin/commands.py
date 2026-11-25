#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""minimal commands.py fixture for testing SDPCommands lookup-table isolation"""

commands = {
    'ALL': {
        'dummy': {
            'read': True,
            'write': False,
            'opcode': '00',
            'reply_pattern': '*',
            'item_type': 'bool',
            'dev_datatype': 'raw',
        }
    }
}

lookups = {'ALL': {'colors': {'R': 'Red', 'G': 'Green'}}, 'modelB': {'colors': {'B': 'Blue'}}}
