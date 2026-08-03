#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""minimal commands.py fixture: a command with no reply_pattern configured"""

commands = {
    'ALL': {
        'no_pattern_cmd': {
            'read': True,
            'write': True,
            'item_type': 'str',
            'dev_datatype': 'raw',
            # deliberately no 'reply_pattern' key
        }
    }
}
