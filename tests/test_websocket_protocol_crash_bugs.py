#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression tests for two crash bugs in the admin and smartvisu websocket
protocols (modules/websocket/admin.py, smartvisu.py):

1. `reply` was only ever assigned at the very end of the per-message command
   dispatch. A handler raising before reaching that point (e.g. a 'item'
   command missing the 'id' key) left `reply` unbound; the fallback send and
   the except block's own log message both reference `reply`, so the
   UnboundLocalError happened *again*. That second, unhandled exception
   escaped the per-message try/except and aborted the whole
   `async for message in websocket` loop -- silently dropping every message
   that arrived after the bad one, not just the bad one itself. Present in
   both admin.py and smartvisu.py.

2. admin.py's prepare_monitor() set `path_parts = 0` (an int) instead of `[]`
   when `path is None`. A mixed monitor list like `[None, "some.item"]`
   slipped past the `data['items'] != [None]` guard and reached
   `len(path_parts)`, raising TypeError. This one does NOT hit bug (1)'s
   failure mode -- by the time it's raised, `answer` has already been set to
   `{}` (right before the risky call), so the `if answer != {}:` guard skips
   the reply-sending code entirely and the loop keeps running. The actual
   damage is narrower: the client's monitor request silently fails with an
   ERROR-level log instead of being handled. smartvisu.py's equivalent
   already correctly used `[]` here, so this one is admin.py-only.
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

from modules.websocket.admin import Protocol as AdminProtocol
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


class TestAdminProtocolMissingKey(_ProtocolMissingKeyTestBase, unittest.IsolatedAsyncioTestCase):
    protocol_class = AdminProtocol
    acl_attr = 'adm_acl'
    clients_attr = 'adm_clients'
    protocol_method = 'adm_protocol'


class TestSmartvisuProtocolMissingKey(_ProtocolMissingKeyTestBase, unittest.IsolatedAsyncioTestCase):
    protocol_class = SmartvisuProtocol
    acl_attr = 'sv_acl'
    clients_attr = 'sv_clients'
    protocol_method = 'smartVISU_protocol_v4'


class TestAdminPrepareMonitorMalformedList(unittest.IsolatedAsyncioTestCase):
    async def test_none_entry_does_not_raise(self):
        proto = _make_protocol(AdminProtocol, 'adm_acl', 'adm_clients')
        fake_item = MagicMock()
        fake_item.conf = {'acl': 'rw'}
        fake_item.return_value = 42
        proto.items.return_item.return_value = fake_item
        proto.update_visuitem = MagicMock()

        # must not raise TypeError: object of type 'int' has no len()
        answer = await proto.prepare_monitor({'items': [None, 'some.item']}, '127.0.0.1:1')

        # and the valid entry must still have been processed despite the
        # None entry being present in the same request
        self.assertEqual(answer['items'], [['some.item', 42]])


if __name__ == '__main__':
    unittest.main(verbosity=2)
