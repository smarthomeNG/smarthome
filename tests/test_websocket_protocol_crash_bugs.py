#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for a crash-prevention invariant in the smartvisu websocket
protocol (modules/websocket/smartvisu.py):

`reply` must be bound before any handler in the per-message command
dispatch can raise (e.g. a 'item' command missing the 'id' key) - the
fallback send and the except block's own log message both reference
`reply`, so leaving it unbound on an early raise triggers a second,
unhandled UnboundLocalError that escapes the per-message try/except and
aborts the whole `async for message in websocket` loop, silently
dropping every message that arrives after the bad one.
"""

import json
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from modules.websocket.smartvisu import Protocol as SmartvisuProtocol
from tests.test_websocket_item_write_acl import _FakeWebsocket


def _make_protocol(protocol_class, acl_attr, clients_attr):
    proto = protocol_class.__new__(protocol_class)
    proto.logger = logging.getLogger('test.wscrash')
    setattr(proto, acl_attr, 'deny')
    setattr(proto, clients_attr, {})
    proto.client_address = lambda ws: f'{ws.remote_address[0]}:{ws.remote_address[1]}'
    proto._sh = MagicMock()
    proto._sh.return_event_listeners.return_value = []
    proto.update_visulog = MagicMock()
    proto.items = MagicMock()
    proto.logics = MagicMock()
    return proto


async def _run(proto, method_name, messages):
    ws = _FakeWebsocket(messages)
    with patch('socket.gethostbyaddr', side_effect=OSError):
        await getattr(proto, method_name)(ws)
    return ws


class _ProtocolMissingKeyTestBase:
    protocol_class = None
    acl_attr = None
    clients_attr = None
    protocol_method = None

    async def test_missing_key_does_not_kill_connection(self):
        proto = _make_protocol(self.protocol_class, self.acl_attr, self.clients_attr)
        proto.items.return_item.return_value = None
        ws = await _run(proto, self.protocol_method, [{'cmd': 'item'}, {'cmd': 'ping'}])
        # a well-formed message queued after the bad one proves the loop kept
        # running: on the pre-fix code it's left unconsumed in ws._messages
        self.assertEqual(ws._messages, [], 'connection loop stopped consuming messages after the bad one')


class TestSmartvisuProtocolMissingKey(_ProtocolMissingKeyTestBase, unittest.IsolatedAsyncioTestCase):
    protocol_class = SmartvisuProtocol
    acl_attr = 'sv_acl'
    clients_attr = 'sv_clients'
    protocol_method = 'smartVISU_protocol_v4'


if __name__ == '__main__':
    unittest.main(verbosity=2)
