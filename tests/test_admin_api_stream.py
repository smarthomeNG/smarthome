#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for modules/admin/api_stream.py's StreamController.

Calls the controller's internal helpers and edit() directly (not through
the real CherryPy dispatch/HTTP layer or an actual SSE connection) - same
convention as test_api_items.py.

Coverage
--------
Stream tokens: mint/consume, single-use, expiry.
Item subscriptions: add registers a real method trigger, remove
    deregisters it, a fired trigger enqueues the expected event shape.
Series subscriptions: add/remove bookkeeping, due-series polling enqueues
    the expected event shape and advances next_poll.
edit(): PATCH applies add/removeItems and add/removeSeries; unknown
    connection id raises 404.
"""

import json
import os
import sys
import time
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import cherrypy

import lib.config
import lib.item.item
import lib.item.items
from lib.item.items import Items
from modules.admin.api_stream import StreamController
from tests.mock.core import MockSmartHome


def _reset():
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _item(sh, path, itype='num', **conf):
    c = {'type': itype}
    c.update(conf)
    i = lib.item.item.Item(sh, sh.items, path, c)
    sh.items.add_item(path, i)
    return i


class _Base(unittest.TestCase):
    def setUp(self):
        _reset()
        self.sh = MockSmartHome()
        module = MagicMock()
        module._sh = self.sh
        module.shtime = self.sh.shtime
        self.controller = StreamController(module)
        self.controller.items = Items.get_instance()

    def tearDown(self):
        _reset()

    def _post_body(self, data):
        body = MagicMock()
        body.read.return_value = json.dumps(data).encode('utf-8')
        request = MagicMock()
        request.body = body
        return patch.object(cherrypy, 'request', request)


class TestStreamTokens(_Base):
    def test_minted_token_is_consumable_once(self):
        token = self.controller._mint_stream_token()

        self.assertTrue(self.controller._consume_stream_token(token))
        self.assertFalse(self.controller._consume_stream_token(token))

    def test_unknown_token_is_rejected(self):
        self.assertFalse(self.controller._consume_stream_token('does-not-exist'))

    def test_expired_token_is_rejected(self):
        token = self.controller._mint_stream_token()
        self.controller._stream_tokens[token] = time.time() - 1

        self.assertFalse(self.controller._consume_stream_token(token))


class TestItemSubscriptions(_Base):
    def setUp(self):
        super().setUp()
        self.entry = {'queue': __import__('queue').Queue(), 'triggers': {}, 'series': {}}

    def test_add_subscription_registers_a_method_trigger(self):
        item = _item(self.sh, 'a')

        self.assertTrue(self.controller._add_item_subscription(self.entry, 'a'))
        self.assertEqual(len(item.get_method_triggers()), 1)

    def test_add_subscription_for_unknown_item_fails(self):
        self.assertFalse(self.controller._add_item_subscription(self.entry, 'does.not.exist'))
        self.assertEqual(self.entry['triggers'], {})

    def test_remove_subscription_deregisters_the_trigger(self):
        item = _item(self.sh, 'a')
        self.controller._add_item_subscription(self.entry, 'a')

        self.controller._remove_item_subscription(self.entry, 'a')

        self.assertEqual(item.get_method_triggers(), [])
        self.assertNotIn('a', self.entry['triggers'])

    def test_trigger_fire_enqueues_item_event(self):
        item = _item(self.sh, 'a')
        self.controller._add_item_subscription(self.entry, 'a')

        item(42, 'test_caller')

        event = self.entry['queue'].get_nowait()
        self.assertEqual(event['type'], 'item')
        self.assertEqual(event['path'], 'a')
        self.assertEqual(event['value'], 42)
        self.assertEqual(event['last_update_by'], 'test_caller:None')
        self.assertEqual(event['last_change_by'], 'test_caller:None')
        self.assertIsNotNone(event['last_change'])
        self.assertIsNotNone(event['last_update'])


class TestSeriesSubscriptions(_Base):
    def setUp(self):
        super().setUp()
        self.entry = {'queue': __import__('queue').Queue(), 'triggers': {}, 'series': {}}

    def test_add_series_subscription_stores_params(self):
        self.controller._add_series_subscription(
            self.entry, {'sid': 's1', 'item': 'a', 'series': 'avg', 'start': '48h', 'end': 'now', 'count': 10}
        )

        self.assertIn('s1', self.entry['series'])
        self.assertEqual(self.entry['series']['s1']['item'], 'a')
        self.assertIsNone(self.entry['series']['s1']['next_poll'])

    def test_add_series_subscription_without_sid_is_ignored(self):
        self.assertFalse(self.controller._add_series_subscription(self.entry, {'item': 'a'}))
        self.assertEqual(self.entry['series'], {})

    def test_remove_series_subscription(self):
        self.controller._add_series_subscription(self.entry, {'sid': 's1', 'item': 'a'})

        self.controller._remove_series_subscription(self.entry, 's1')

        self.assertNotIn('s1', self.entry['series'])

    def test_poll_due_series_enqueues_reply_and_advances_next_poll(self):
        item = _item(self.sh, 'a')
        update_at = self.sh.shtime.now() + timedelta(seconds=100)
        item.series = MagicMock(return_value={'update': update_at, 'series': [[0, 1]]})
        connection_id = 'conn-1'
        self.controller._streams[connection_id] = self.entry
        self.controller._add_series_subscription(
            self.entry, {'sid': 's1', 'item': 'a', 'series': 'avg', 'start': '48h', 'end': 'now', 'count': 10}
        )

        self.controller._poll_due_series(connection_id, self.entry['queue'])

        event = self.entry['queue'].get_nowait()
        self.assertEqual(event['type'], 'series')
        self.assertEqual(event['sid'], 's1')
        self.assertEqual(event['series'], [[0, 1]])
        item.series.assert_called_once_with('avg', '48h', 'now', 10)
        self.assertEqual(self.entry['series']['s1']['next_poll'], update_at)
        self.assertGreater(self.entry['series']['s1']['next_poll'], self.sh.shtime.now())

    def test_poll_due_series_skips_not_yet_due(self):
        item = _item(self.sh, 'a')
        item.series = MagicMock()
        connection_id = 'conn-1'
        self.controller._streams[connection_id] = self.entry
        self.controller._add_series_subscription(self.entry, {'sid': 's1', 'item': 'a'})
        self.entry['series']['s1']['next_poll'] = self.sh.shtime.now() + timedelta(seconds=100)

        self.controller._poll_due_series(connection_id, self.entry['queue'])

        item.series.assert_not_called()
        self.assertTrue(self.entry['queue'].empty())


class TestLazyItemsResolution(_Base):
    """Items.get_instance() returns None at module construction time (Items
    isn't created yet during startup) - self.items must resolve lazily on
    first request, not get cached as None forever from __init__."""

    def test_edit_resolves_items_when_none_at_construction(self):
        self.controller.items = None
        item = _item(self.sh, 'a')
        connection_id = 'conn-1'
        self.controller._streams[connection_id] = {'queue': __import__('queue').Queue(), 'triggers': {}, 'series': {}}

        with self._post_body({'addItems': ['a']}):
            self.controller.edit(connection_id)

        self.assertEqual(len(item.get_method_triggers()), 1)


class TestEdit(_Base):
    def test_edit_unknown_connection_raises_404(self):
        with self.assertRaises(cherrypy.HTTPError) as ctx:
            self.controller.edit('does-not-exist')
        self.assertEqual(ctx.exception.status, 404)

    def test_edit_applies_add_and_remove_items(self):
        item_a = _item(self.sh, 'a')
        item_b = _item(self.sh, 'b')
        connection_id = 'conn-1'
        entry = {'queue': __import__('queue').Queue(), 'triggers': {}, 'series': {}}
        self.controller._streams[connection_id] = entry
        self.controller._add_item_subscription(entry, 'a')

        with self._post_body({'addItems': ['b'], 'removeItems': ['a']}):
            result = json.loads(self.controller.edit(connection_id))

        self.assertEqual(result['result'], 'ok')
        self.assertNotIn('a', entry['triggers'])
        self.assertIn('b', entry['triggers'])
        self.assertEqual(item_a.get_method_triggers(), [])
        self.assertEqual(len(item_b.get_method_triggers()), 1)

    def test_edit_applies_add_and_remove_series(self):
        connection_id = 'conn-1'
        entry = {'queue': __import__('queue').Queue(), 'triggers': {}, 'series': {'old': {}}}
        self.controller._streams[connection_id] = entry

        with self._post_body(
            {
                'addSeries': [{'sid': 'new', 'item': 'a', 'series': 'avg', 'start': '48h', 'end': 'now', 'count': 10}],
                'removeSeries': ['old'],
            }
        ):
            self.controller.edit(connection_id)

        self.assertNotIn('old', entry['series'])
        self.assertIn('new', entry['series'])


if __name__ == '__main__':
    unittest.main()
