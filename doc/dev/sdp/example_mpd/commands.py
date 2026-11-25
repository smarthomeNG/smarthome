#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Commands of the MPD tutorial example.

MPD speaks a line protocol: a request is one line, the reply is a block of
``key: value`` lines closed by ``OK`` (or a single ``ACK ...`` error line).
Each readable command requests a whole block; the receive-only and
write-only commands pick their line out of that block by reply_pattern.
"""

commands = {
    'status': {
        'state': {
            'read': True,
            'write': False,
            'read_cmd': 'status',
            'item_type': 'str',
            'dev_datatype': 'str',
            'reply_pattern': r'^state: {LOOKUP}$',
            'lookup': 'STATE',
            'item_attrs': {'initial': True, 'cycle': 10},
        },
        'volume': {
            'read': False,
            'write': True,
            'write_cmd': 'setvol {VALUE}',
            'item_type': 'num',
            'dev_datatype': 'int',
            'reply_pattern': r'^volume: (-?\d+)$',
            'cmd_settings': {'force_min': 0, 'force_max': 100},
        },
        'random': {
            'read': False,
            'write': True,
            'write_cmd': 'random {VALUE}',
            'item_type': 'bool',
            'dev_datatype': 'mpdflag',
            'reply_pattern': r'^random: ([01])$',
        },
        'repeat': {
            'read': False,
            'write': True,
            'write_cmd': 'repeat {VALUE}',
            'item_type': 'bool',
            'dev_datatype': 'mpdflag',
            'reply_pattern': r'^repeat: ([01])$',
        },
        'elapsed': {
            'read': False,
            'write': False,
            'item_type': 'num',
            'dev_datatype': 'num',
            'reply_pattern': r'^elapsed: ([\d.]+)$',
        },
    },
    'currentsong': {
        'title': {
            'read': True,
            'write': False,
            'read_cmd': 'currentsong',
            'item_type': 'str',
            'dev_datatype': 'str',
            'reply_pattern': r'^Title: (.*)$',
            'item_attrs': {'initial': True, 'cycle': 10},
        },
        'artist': {
            'read': False,
            'write': False,
            'item_type': 'str',
            'dev_datatype': 'str',
            'reply_pattern': r'^Artist: (.*)$',
        },
        'album': {
            'read': False,
            'write': False,
            'item_type': 'str',
            'dev_datatype': 'str',
            'reply_pattern': r'^Album: (.*)$',
        },
    },
    'control': {
        'pause': {
            'read': False,
            'write': True,
            'write_cmd': 'pause {VALUE}',
            'item_type': 'bool',
            'dev_datatype': 'mpdflag',
        },
        'play': {
            'read': False,
            'write': True,
            'write_cmd': 'play',
            'item_type': 'bool',
            'item_attrs': {'enforce': True},
        },
        'stop': {
            'read': False,
            'write': True,
            'write_cmd': 'stop',
            'item_type': 'bool',
            'item_attrs': {'enforce': True},
        },
        'next': {
            'read': False,
            'write': True,
            'write_cmd': 'next',
            'item_type': 'bool',
            'item_attrs': {'enforce': True},
        },
        'previous': {
            'read': False,
            'write': True,
            'write_cmd': 'previous',
            'item_type': 'bool',
            'item_attrs': {'enforce': True},
        },
    },
}

lookups = {'STATE': {'play': 'playing', 'pause': 'paused', 'stop': 'stopped'}}
