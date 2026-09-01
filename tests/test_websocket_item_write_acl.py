#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression tests for the item-write ACL check in the admin and smartvisu
websocket protocols (modules/websocket/admin.py, modules/websocket/smartvisu.py).

Both handlers must require acl == 'rw' explicitly (default-deny), matching
the pattern already used on the read/monitor path (prepare_monitor()) -
not refuse a write only when acl == 'ro', which would leave any item
without an explicit 'ro' acl writable under the actual default
(adm_acl/sv_acl = 'deny').
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


class _FakeWebsocket:
    """
    Minimal stand-in for a websockets connection: async-iterates over a fixed
    list of JSON messages, then ends the loop like a closed connection.
    """

    def __init__(self, messages, remote_address=('127.0.0.1', 54321)):
        self._messages = [json.dumps(m) for m in messages]
        self.remote_address = remote_address
        self.secure = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._messages:
            raise StopAsyncIteration
        return self._messages.pop(0)


class _WebsocketItemWriteAclTestBase:
    """
    Shared regression tests for the item-write ACL check, run once per
    protocol (admin, smartvisu) via the concrete subclasses below.
    """

    protocol_class = None
    acl_attr = None  # 'adm_acl' or 'sv_acl'
    clients_attr = None  # 'adm_clients' or 'sv_clients'
    protocol_method = None  # name of the async connection-handler method

    def _make_protocol(self, item_acl):
        proto = self.protocol_class.__new__(self.protocol_class)
        proto.logger = logging.getLogger('test.wsacl')
        setattr(proto, self.acl_attr, 'deny')
        setattr(proto, self.clients_attr, {})
        proto.client_address = lambda ws: f'{ws.remote_address[0]}:{ws.remote_address[1]}'
        proto._sh = MagicMock()
        proto._sh.return_event_listeners.return_value = []
        proto.update_visulog = MagicMock()

        fake_item = MagicMock()
        fake_item.conf = {} if item_acl is None else {'acl': item_acl}
        items = MagicMock()
        items.return_item.return_value = fake_item
        proto.items = items
        proto.logics = MagicMock()
        return proto, fake_item

    async def _run(self, proto):
        ws = _FakeWebsocket([{'cmd': 'item', 'id': 'some.item', 'val': 42}])
        with patch('socket.gethostbyaddr', side_effect=OSError):
            await getattr(proto, self.protocol_method)(ws)

    async def test_write_denied_when_no_acl_set(self):
        # falls back to the protocol's default acl, which is 'deny'
        proto, fake_item = self._make_protocol(item_acl=None)
        await self._run(proto)
        fake_item.assert_not_called()

    async def test_write_denied_when_acl_is_ro(self):
        proto, fake_item = self._make_protocol(item_acl='ro')
        await self._run(proto)
        fake_item.assert_not_called()

    async def test_write_allowed_when_acl_is_rw(self):
        proto, fake_item = self._make_protocol(item_acl='rw')
        await self._run(proto)
        fake_item.assert_called_once()


class TestAdminWebsocketItemWriteAcl(_WebsocketItemWriteAclTestBase, unittest.IsolatedAsyncioTestCase):
    protocol_class = AdminProtocol
    acl_attr = 'adm_acl'
    clients_attr = 'adm_clients'
    protocol_method = 'adm_protocol'


class TestSmartvisuWebsocketItemWriteAcl(_WebsocketItemWriteAclTestBase, unittest.IsolatedAsyncioTestCase):
    protocol_class = SmartvisuProtocol
    acl_attr = 'sv_acl'
    clients_attr = 'sv_clients'
    protocol_method = 'smartVISU_protocol_v4'


if __name__ == '__main__':
    unittest.main(verbosity=2)
