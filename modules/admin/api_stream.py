#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2026-      SmartHomeNG contributors
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import json
import logging
import queue
import secrets
import threading
import time
import uuid

import cherrypy

from lib.item import Items
from .rest import ApiDoc, ApiParam, RESTResource

STREAM_TOKEN_TTL = 30  # seconds a minted stream token stays valid/unused
SERIES_POLL_INTERVAL = 1.0  # generator wakeup cadence for checking due series polls


class StreamController(RESTResource):
    """
    Server-Sent-Events replacement for the legacy websocket ``/adm`` push
    protocol (see ``modules/websocket/admin.py``): live item value changes
    and live series (history) polling, addressed to a REST client instead
    of a persistent websocket.

    ``GET /api/stream/token`` mints a short-lived, single-use token (JWT
    auth via the normal Authorization header). ``GET /api/stream?token=..``
    opens the actual SSE connection - browsers' native EventSource API
    cannot set custom headers, so the long-lived session JWT never reaches
    this request; the single-use token is the credential instead. The
    connection has no subscriptions until the client PATCHes them in via
    ``PATCH /api/stream/{connectionId}``.
    """

    REST_map = {'PATCH': 'edit'}

    def __init__(self, module):
        self._sh = module._sh
        self.module = module
        self.logger = logging.getLogger(
            __name__.split('.')[0] + '.' + __name__.split('.')[1] + '.' + __name__.split('.')[2][4:]
        )
        self.items = None

        self._lock = threading.Lock()
        self._streams = {}
        self._stream_tokens = {}

    # GET /api/stream/token, GET /api/stream?token=<t>
    def read(self, id=None, **params):
        if self.items is None:
            self.items = Items.get_instance()
        self.set_response_headers()

        if id == 'token':
            token_valid, error_text = self.REST_test_jwt_token()
            if not token_valid:
                cherrypy.response.status = 401
                return json.dumps({'result': 'error', 'description': error_text})
            return json.dumps({'token': self._mint_stream_token()})

        token = params.get('token', '')
        if not self._consume_stream_token(token):
            raise cherrypy.HTTPError(401, 'Invalid or expired stream token')

        return self._stream_generator()

    read.expose_resource = True
    read.authentication_needed = False
    read.api_doc = [
        ApiDoc(
            summary='Mint a short-lived, single-use token for opening an SSE stream',
            method='get',
            path='/stream/token',
            tags=['stream'],
            response_example='{"token": "<stream token>"}',
        ),
        ApiDoc(
            summary='Open a live SSE stream (item value / series push)',
            method='get',
            path='/stream',
            auth=False,
            tags=['stream'],
            params=[
                ApiParam(name='token', location='query', required=True, description='Stream token from /stream/token')
            ],
            description='Not JWT-authenticated (EventSource cannot set headers) - '
            'authenticated instead by the single-use token minted via /stream/token.',
        ),
    ]

    # PATCH /api/stream/{connectionId}
    def edit(self, resource, **params):
        if self.items is None:
            self.items = Items.get_instance()
        connection_id = resource
        with self._lock:
            entry = self._streams.get(connection_id)
        if entry is None:
            raise cherrypy.HTTPError(404, f"Stream connection '{connection_id}' not found")

        body = cherrypy.request.body.read()
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError as e:
            raise cherrypy.HTTPError(400, f'Invalid JSON body: {e}')

        with self._lock:
            for path in data.get('removeItems', []) or []:
                self._remove_item_subscription(entry, path)
            for path in data.get('addItems', []) or []:
                self._add_item_subscription(entry, path)
            for sid in data.get('removeSeries', []) or []:
                self._remove_series_subscription(entry, sid)
            for spec in data.get('addSeries', []) or []:
                self._add_series_subscription(entry, spec)

        return json.dumps({'result': 'ok'})

    edit.expose_resource = True
    edit.authentication_needed = True
    edit.api_doc = [
        ApiDoc(
            summary='Add/remove item and series subscriptions on a live stream',
            method='patch',
            path='/stream/{connectionId}',
            tags=['stream'],
            params=[ApiParam(name='connectionId', location='path', required=True)],
            request_body='SubscriptionPatch',
            request_example=(
                '{"addItems": ["item.path"], "removeItems": [], '
                '"addSeries": [{"sid": "s1", "item": "item.path", "series": "avg", '
                '"start": "48h", "end": "now", "count": 10}], "removeSeries": []}'
            ),
        )
    ]

    # Stream tokens
    def _mint_stream_token(self):
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._stream_tokens[token] = time.time() + STREAM_TOKEN_TTL
        return token

    def _consume_stream_token(self, token):
        with self._lock:
            expiry = self._stream_tokens.pop(token, None)
        return expiry is not None and expiry >= time.time()

    # Subscriptions
    def _make_item_trigger(self, q):
        def _trigger(item, caller=None, source=None, dest=None):
            prop = item.property
            q.put(
                {
                    'type': 'item',
                    'path': prop.path,
                    'value': item(),
                    'last_change': prop.last_change,
                    'last_change_by': prop.last_change_by,
                    'last_update': prop.last_update,
                    'last_update_by': prop.last_update_by,
                    'last_value': prop.last_value,
                }
            )

        return _trigger

    def _add_item_subscription(self, entry, path):
        if path in entry['triggers']:
            return True
        item = self.items.return_item(path)
        if item is None:
            self.logger.warning(f"Stream: cannot subscribe to unknown item '{path}'")
            return False
        cb = self._make_item_trigger(entry['queue'])
        item.add_method_trigger(cb)
        entry['triggers'][path] = (item, cb)
        return True

    def _remove_item_subscription(self, entry, path):
        info = entry['triggers'].pop(path, None)
        if info is None:
            return
        item, cb = info
        try:
            item.remove_method_trigger(cb)
        except ValueError:
            pass

    def _add_series_subscription(self, entry, spec):
        sid = spec.get('sid')
        item_path = spec.get('item')
        if not sid or not item_path:
            self.logger.warning(f"Stream: ignoring series subscription without 'sid'/'item': {spec}")
            return False
        entry['series'][sid] = {
            'item': item_path,
            'series': spec.get('series'),
            'start': spec.get('start'),
            'end': spec.get('end'),
            'count': spec.get('count'),
            'next_poll': 0.0,
        }
        return True

    def _remove_series_subscription(self, entry, sid):
        entry['series'].pop(sid, None)

    def _poll_due_series(self, connection_id, q):
        with self._lock:
            entry = self._streams.get(connection_id)
            series_items = list(entry['series'].items()) if entry else []

        now = time.time()
        for sid, series_params in series_items:
            if series_params['next_poll'] > now:
                continue
            item = self.items.return_item(series_params['item'])
            if item is None or not hasattr(item, 'series'):
                continue
            try:
                reply = item.series(
                    series_params['series'], series_params['start'], series_params['end'], series_params['count']
                )
            except Exception as e:
                self.logger.warning(f"Stream {connection_id}: series poll failed for sid='{sid}': {e}")
                continue
            if not reply:
                continue

            with self._lock:
                if sid in entry['series']:
                    entry['series'][sid]['next_poll'] = reply.get('update', now + 5)
            # only the datapoint array crosses the wire - reply's other keys are internal cadence bookkeeping
            q.put({'type': 'series', 'sid': sid, 'series': reply.get('series')})

    # The SSE connection itself
    def _format_event(self, event_type, data):
        return f'event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n'

    def _cleanup_stream(self, connection_id):
        with self._lock:
            entry = self._streams.pop(connection_id, None)
        if entry is None:
            return
        for path, (item, cb) in entry['triggers'].items():
            try:
                item.remove_method_trigger(cb)
            except ValueError:
                pass
        self.logger.info(
            f'Stream {connection_id}: closed, released {len(entry["triggers"])} item trigger(s), '
            f'{len(entry["series"])} series subscription(s)'
        )

    def _stream_generator(self):
        cherrypy.response.headers['Content-Type'] = 'text/event-stream'
        cherrypy.response.headers['Cache-Control'] = 'no-cache'
        cherrypy.response.headers['X-Accel-Buffering'] = 'no'
        cherrypy.response.stream = True

        connection_id = str(uuid.uuid4())
        q = queue.Queue()
        with self._lock:
            self._streams[connection_id] = {'queue': q, 'triggers': {}, 'series': {}}
        self.logger.info(f'Stream {connection_id}: opened')

        def _generate():
            try:
                yield self._format_event('connection', {'connectionId': connection_id})
                while True:
                    try:
                        event = q.get(timeout=SERIES_POLL_INTERVAL)
                        yield self._format_event(event['type'], event)
                    except queue.Empty:
                        pass
                    self._poll_due_series(connection_id, q)
            finally:
                self._cleanup_stream(connection_id)

        return _generate()
