#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Characterization snapshots of SDP plugins: sends, dispatched values, jobs and item changes per probe.

Snapshots are regenerated with SDP_SNAPSHOT_UPDATE=1.
"""

from __future__ import annotations

import importlib
import io
import json
import os
import re
import tempfile
import unittest
from collections.abc import Callable, Iterable
from typing import Any
from unittest.mock import patch

from ruamel.yaml import YAML

from lib.model.sdp.globals import CMD_ATTR_CMD_SETTINGS, CMD_ATTR_LOOKUP, CMD_ATTR_REPLY_PATTERN
from tests.sdp_harness import RecordingConnection, SDPRig, load_sdp_plugin

try:
    import re._parser as sre_parse
except ImportError:  # Python < 3.11: `re` is a module, the parser is top-level sre_parse
    import sre_parse

#: environment variable; if set to 1, snapshots are rewritten instead of compared
SNAPSHOT_UPDATE_ENV = 'SDP_SNAPSHOT_UPDATE'

INSTANCE_SUFFIX = '@instance'

_LOADER = YAML(typ='safe')
_DUMPER = YAML()
_DUMPER.default_flow_style = False


def items_yaml_from_struct(plugin_dir: str, struct: str, root: str = 'dev', root_attrs: dict | None = None) -> str:
    """
    Item yaml of item struct ``struct`` of the plugin, mounted at ``root``, without ``@instance``.

    :param root_attrs: additional attributes for the root item
    """

    def strip(node: Any) -> Any:
        if isinstance(node, dict):
            return {k.removesuffix(INSTANCE_SUFFIX): strip(v) for k, v in node.items()}
        return node

    with open(os.path.join(plugin_dir, 'plugin.yaml')) as f:
        meta = _LOADER.load(f)
    tree = strip(meta['item_structs'][struct])
    out = io.StringIO()
    _DUMPER.dump({root: {**(root_attrs or {}), **tree}}, out)
    return out.getvalue()


_CATEGORY_SAMPLES = {
    sre_parse.CATEGORY_DIGIT: '1',
    sre_parse.CATEGORY_NOT_DIGIT: 'a',
    sre_parse.CATEGORY_SPACE: ' ',
    sre_parse.CATEGORY_NOT_SPACE: 'a',
    sre_parse.CATEGORY_WORD: 'a',
    sre_parse.CATEGORY_NOT_WORD: ' ',
}

_REPEAT_OPS = tuple(
    getattr(sre_parse, name) for name in ('MAX_REPEAT', 'MIN_REPEAT', 'POSSESSIVE_REPEAT') if hasattr(sre_parse, name)
)
"""Repeat opcodes of the running interpreter; possessive repeats exist from Python 3.11."""

_ATOMIC_GROUP = getattr(sre_parse, 'ATOMIC_GROUP', None)
"""Atomic group opcode, None before Python 3.11."""


def _sample(parsed) -> str:
    out = []
    for op, arg in parsed:
        if op is sre_parse.LITERAL:
            out.append(chr(arg))
        elif op is sre_parse.NOT_LITERAL:
            out.append('a' if chr(arg) != 'a' else 'b')
        elif op is sre_parse.ANY:
            out.append('a')
        elif op is sre_parse.IN:
            out.append(_sample_in(arg))
        elif op is sre_parse.BRANCH:
            out.append(_sample(arg[1][0]))
        elif op is sre_parse.SUBPATTERN:
            out.append(_sample(arg[-1]))
        elif op in _REPEAT_OPS:
            low, high, sub = arg
            out.append(_sample(sub) * max(low, min(1, high)))
        elif op is _ATOMIC_GROUP:
            out.append(_sample(arg))
        # anchors, lookarounds and group references contribute no characters
    return ''.join(out)


def _sample_in(items) -> str:
    negate = items and items[0][0] is sre_parse.NEGATE
    if negate:
        excluded = {chr(a) for op, a in items if op is sre_parse.LITERAL}
        return next(c for c in 'aA1 ' if c not in excluded)
    op, arg = items[0]
    if op is sre_parse.LITERAL:
        return chr(arg)
    if op is sre_parse.RANGE:
        return chr(arg[0])
    if op is sre_parse.CATEGORY:
        return _CATEGORY_SAMPLES.get(arg, 'a')
    return 'a'


SAMPLE_BOUND_KEYS = ('valid_min', 'valid_max', 'force_min', 'force_max')
"""Order in which min/max settings become write samples; fixed so snapshots do not depend on MINMAXKEYS precedence."""


def sample_for_pattern(pattern: str) -> str | None:
    """A deterministic string matching regex ``pattern``, None if none is found."""
    try:
        sample = _sample(sre_parse.parse(pattern))
    except (re.error, StopIteration):
        return None
    return sample if re.search(pattern, sample) else None


def attribute_prefix(plugin_dir: str) -> str:
    """The plugin's item attribute prefix, from its ``<prefix>_command`` attribute."""
    with open(os.path.join(plugin_dir, 'plugin.yaml')) as f:
        attrs = _LOADER.load(f).get('item_attributes') or {}
    return next(name.removesuffix('_command') for name in attrs if name.endswith('_command'))


def to_json(value: Any) -> Any:
    """JSON-serializable form of a recorded value."""
    if isinstance(value, (bytes, bytearray)):
        return {'bytes': bytes(value).hex()}
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json(v) for v in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return repr(value)


class Characterizer:
    """Runs probes against a loaded plugin and collects the record."""

    def __init__(self, rig: SDPRig, prefix: str, excluded_items: Iterable[str] = ()) -> None:
        self.rig = rig
        self.plugin = rig.plugin
        self.prefix = prefix
        self.excluded = set(excluded_items)
        self.record: dict[str, Any] = {}
        if not isinstance(rig.connection, RecordingConnection):
            raise TypeError('characterization needs a recording connection')
        self.conn: RecordingConnection = rig.connection
        self.dispatched: list = []
        dispatch = self.plugin._dispatch_callback

        def record_dispatch(command, value, by=None):
            self.dispatched.append([command, to_json(value)])
            return dispatch(command, value, by)

        self.plugin._dispatch_callback = record_dispatch

    # item access

    def attr(self, item, name: str) -> Any:
        """Value of the plugin item attribute ``<prefix>_<name>`` of ``item``, or None."""
        return item.conf.get(f'{self.prefix}_{name}')

    def items(self) -> list:
        """All items of the plugin's item tree, sorted by path, without excluded items."""
        return sorted(
            (i for i in self.rig.sh.items.return_items() if i.property.path not in self.excluded),
            key=lambda i: i.property.path,
        )

    def values(self) -> dict[str, Any]:
        """Current values of all items, by path."""
        return {i.property.path: to_json(i()) for i in self.items()}

    def changed_since(self, before: dict[str, Any]) -> dict[str, Any]:
        """Items whose value differs from ``before``, with their new value."""
        return {path: val for path, val in self.values().items() if before.get(path) != val}

    # recording helpers

    def take_sent(self) -> list:
        """Sent data_dicts since the last call, emptying the record."""
        sent = [to_json(d) for d in self.conn.sent]
        self.conn.sent.clear()
        return sent

    def take_dispatched(self) -> list:
        """Dispatched (command, value) pairs since the last call, emptying the record."""
        dispatched = list(self.dispatched)
        self.dispatched.clear()
        return dispatched

    def jobs(self) -> list[str]:
        """Names of the plugin's current scheduler jobs."""
        return sorted(self.rig.plugin_jobs())

    def write_value(self, item) -> Any:
        """A value for writing ``item``, different from its current value and accepted by its command if known."""
        command = self.attr(item, 'command')
        cmd = self.plugin._commands.get_commandlist(command) if command else {}
        candidates: list = []
        lookup = cmd.get(CMD_ATTR_LOOKUP)
        table = self.plugin.get_lookup(lookup) if lookup else None
        if table:
            candidates += list(table.values())[:2]
        settings = cmd.get(CMD_ATTR_CMD_SETTINGS) or {}
        for key in ('valid_list', 'valid_list_ci'):
            candidates += list(settings.get(key) or [])[:2]
        candidates += [settings[key] for key in SAMPLE_BOUND_KEYS if key in settings]
        candidates += {
            'bool': [True, False],
            'num': [1, 2],
            'str': ['x', 'y'],
            'list': [['x'], []],
            'dict': [{'x': 1}, {}],
        }.get(item.type(), [1, 2])
        current = item()
        return next((c for c in candidates if c != current), candidates[0])

    # probes

    def probe_initial(self) -> None:
        """Run the plugin, fire the initial read; record sends and jobs."""
        self.plugin.run()
        self.record['jobs_after_run'] = self.jobs()
        job = self.rig.job('read_initial_values')
        if job:
            job.fire()
        self.record['initial_sends'] = self.take_sent()
        self.record['initial_dispatched'] = self.take_dispatched()

    def probe_writes(self) -> None:
        """Write every write-enabled item once; record sends, new jobs and changed items per write."""
        writes = []
        for item in self.items():
            if not (self.attr(item, 'command') and self.attr(item, 'write')):
                continue
            value = self.write_value(item)
            jobs_before = set(self.jobs())
            values_before = self.values()
            item(value, 'characterization')
            writes.append(
                {
                    'item': item.property.path,
                    'value': to_json(value),
                    'sent': self.take_sent(),
                    'dispatched': self.take_dispatched(),
                    'new_jobs': sorted(set(self.jobs()) - jobs_before),
                    'changed': self.changed_since(values_before),
                }
            )
        self.record['writes'] = writes

    def probe_reads(self) -> None:
        """Send every read-enabled item's command for reading; record sends and changed items."""
        reads = []
        seen = set()
        for item in self.items():
            command = self.attr(item, 'command')
            if not (command and self.attr(item, 'read')) or command in seen:
                continue
            seen.add(command)
            values_before = self.values()
            self.plugin.send_command(command)
            reads.append(
                {
                    'command': command,
                    'sent': self.take_sent(),
                    'dispatched': self.take_dispatched(),
                    'changed': self.changed_since(values_before),
                }
            )
        self.record['reads'] = reads

    def probe_replies(self) -> None:
        """Feed one sampled reply per reply_pattern of every command as device data."""
        replies = []
        commands = self.plugin._commands.get_commandlist()
        for command in sorted(commands):
            for pattern in commands[command].get(CMD_ATTR_REPLY_PATTERN) or []:
                sample = sample_for_pattern(pattern)
                if sample is not None:
                    replies.append({'reply_to': command, **self.inbound(sample)})
        self.record['replies'] = replies

    def inbound(self, data: Any, command: str | None = None) -> dict[str, Any]:
        """Hand ``data`` to the plugin as received from the device; return the effects."""
        values_before = self.values()
        error = None
        try:
            self.plugin.on_data_received('characterization', data, command)
        except Exception as e:
            error = f'{type(e).__name__}: {e}'
        return {
            'data': to_json(data),
            'command': command,
            'dispatched': self.take_dispatched(),
            'changed': self.changed_since(values_before),
            'sent': self.take_sent(),
            'exception': error,
        }

    def probe_inbound(self, name: str, messages: Iterable[Inbound]) -> None:
        """Record the effects of inbound ``(data, command)`` messages under ``name``."""
        with patch('time.sleep'):
            self.record[name] = [self.inbound(data, command) for data, command in messages]

    def run_standard(self, replies: bool = True) -> dict[str, Any]:
        """Run the initial, write, read and (optionally) reply probes; return the record."""
        with patch('time.sleep'):
            self.probe_initial()
            self.probe_writes()
            self.probe_reads()
            if replies:
                self.probe_replies()
        return self.record


#: an inbound message: data as received from the device, and the command it answers (or None)
Inbound = tuple[Any, 'str | None']


def characterize_plugin(
    testcase: unittest.TestCase,
    plugin: str,
    class_name: str,
    struct: str,
    params: dict[str, Any],
    *,
    root_attrs: dict[str, Any] | None = None,
    replies: bool = True,
    responder: Callable[[dict], Any] | None = None,
    record_transport: bool = False,
    inbound: dict[str, list[Inbound]] | None = None,
    snapshot: str = 'characterization',
) -> None:
    """
    Characterize ``plugins.<plugin>`` with the items of its struct ``struct`` and compare with its snapshot.

    :param replies: run the reply probe (string-based plugins only)
    :param responder: computes the connection's reply to each sent data_dict
    :param record_transport: record below the plugin's protocol
    :param inbound: plugin-specific inbound messages by probe name
    :param snapshot: snapshot file name without extension
    """
    plugin_dir = os.path.dirname(importlib.import_module(f'plugins.{plugin}').__file__)
    items = items_yaml_from_struct(plugin_dir, struct, root_attrs=root_attrs)
    with tempfile.TemporaryDirectory() as tmp_dir:
        rig = load_sdp_plugin(
            tmp_dir, f'plugins.{plugin}', class_name, items, params=params, record_transport=record_transport
        )
        char = Characterizer(rig, attribute_prefix(plugin_dir))
        char.conn.responder = responder
        try:
            char.run_standard(replies=replies)
            for name, messages in (inbound or {}).items():
                char.probe_inbound(name, messages)
        finally:
            rig.plugin.stop()
    assert_snapshot(testcase, char.record, os.path.join(plugin_dir, 'tests', 'snapshots', f'{snapshot}.json'))


def assert_snapshot(testcase: unittest.TestCase, record: dict[str, Any], path: str) -> None:
    """
    Compare ``record`` with the JSON snapshot at ``path``.

    With SDP_SNAPSHOT_UPDATE=1 or no snapshot yet, the snapshot is written instead; a new snapshot skips the test.
    """
    text = json.dumps(record, indent=1, ensure_ascii=False, sort_keys=False) + '\n'
    if os.environ.get(SNAPSHOT_UPDATE_ENV) == '1' or not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        existed = os.path.exists(path)
        with open(path, 'w') as f:
            f.write(text)
        if not existed:
            testcase.skipTest(f'snapshot {path} created, review and commit it')
        return
    with open(path) as f:
        expected = json.load(f)
    testcase.maxDiff = None
    testcase.assertEqual(expected, json.loads(text))
