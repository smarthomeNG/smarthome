#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""commands.py fixture: flat commands dict, no 'ALL' key and no models dict"""

commands = {
    'cmd_a': {'read': True, 'write': False, 'item_type': 'str', 'dev_datatype': 'raw'},
    'cmd_b': {'read': True, 'write': True, 'item_type': 'num', 'dev_datatype': 'raw'},
}
