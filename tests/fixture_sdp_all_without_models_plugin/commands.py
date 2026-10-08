#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""commands.py fixture: model-specific commands dict with an 'ALL' key and no models dict"""

commands = {
    'ALL': {'cmd_all': {'read': True, 'write': False, 'item_type': 'str', 'dev_datatype': 'raw'}},
    'modelX': {'cmd_x': {'read': True, 'write': False, 'item_type': 'str', 'dev_datatype': 'raw'}},
    'modelY': {'cmd_y': {'read': True, 'write': False, 'item_type': 'str', 'dev_datatype': 'raw'}},
}
