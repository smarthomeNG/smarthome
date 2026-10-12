# Tutorial: from device protocol to `commands.py` (MPD)

*Deutsche Fassung: [`sdp_commands_tutorial.de.md`](sdp_commands_tutorial.de.md)*

This walks through building an SDP plugin for the Music Player Daemon (MPD)
from its protocol description: which commands to define, how to route
replies, where a custom datatype is needed, and how to test the result. The
finished plugin is in [`example_mpd/`](example_mpd/) and its tests run on the
real SDP stack:

```bash
pytest doc/dev/sdp/example_mpd/tests
```

Background: [`sdp_plugin_guide.md`](sdp_plugin_guide.md) (reference),
[`sdp_architecture.md`](sdp_architecture.md) (internals).

## Choosing the example

Candidates among the plugins not based on SDP:

| Plugin | Size | Protocol | Verdict |
|---|---|---|---|
| `yamahayxc` | 3447 lines | HTTP + UDP events, many hosts per instance, browse/queue/playlist management, feature discovery per host | not simple: SDP is one connection per instance; the zone/power/volume core would map to `CONN_NET_UDP_SRV`, the rest would stay custom code |
| `nut` | 84 lines | NUT text protocol | simplest, but read-only — no writes, lookups or checks to show. (It imports `telnetlib`, which Python 3.13 removed.) |
| `jvcproj` | 408 lines | binary with handshake | needs a custom protocol class — advanced topic |
| `mpd` | 640 lines | line-based text over TCP | reads and writes, multi-line replies, flags, enumerations, value ranges, actions — chosen |

The `mpd` plugin's own code (`plugins/mpd/__init__.py`) and the MPD protocol
documentation (https://mpd.readthedocs.io/en/latest/protocol.html) are the
sources for the protocol facts below. The example covers a subset of it.

## Step 1: understand the wire protocol

- TCP, port 6600, persistent connection. On connect MPD sends `OK MPD <version>`.
- A request is one line ending in `\n`.
- A reply is a block of `key: value` lines closed by a line `OK`; an error is
  a single line `ACK [error@command_listNum] {command} message`.

```
> status
< volume: 42
< repeat: 0
< random: 1
< state: pause
< elapsed: 12.500
< OK
> setvol 50
< OK
```

The two facts that shape the whole `commands.py`:

1. **One request returns many values.** `status` answers volume, flags,
   state, elapsed time at once; `currentsong` answers title, artist, album.
2. **Writes are separate verbs** (`setvol 50`, `random 1`, `pause 1`, `next`)
   whose reply is just `OK`; the new value shows up in the next `status`.

## Step 2: inventory

List what you want as items, how to read it, how to write it:

| Item | Read via | Reply line | Write | Type |
|---|---|---|---|---|
| state | `status` | `state: play\|pause\|stop` | — | str |
| volume | `status` | `volume: 42` | `setvol <0..100>` | num |
| random, repeat | `status` | `random: 0\|1` | `random 0\|1` | bool |
| elapsed | `status` | `elapsed: 12.500` | — | num |
| title, artist, album | `currentsong` | `Title: …`, `Artist: …`, `Album: …` | — | str |
| pause | — | — | `pause 0\|1` | bool |
| play, stop, next, previous | — | — | `play`, `stop`, … | bool (trigger) |

## Step 3: transport, command class, plugin class

- Persistent TCP, replies come asynchronously → `CONN_NET_TCP_CLI`. The TCP
  client splits the stream at the terminator and delivers one line per call.
- Lines end in `\n` → `LINE_TERMINATED = True` and a `terminator` parameter
  with default `"\n"`.
- Values must be cut out of `key: value` lines → `SDPCommandParseStr`
  (one capture group in `reply_pattern` = the value).

```python
class MpdSdp(SmartDevicePlugin):
    PLUGIN_VERSION = '0.1.0'
    ALLOW_MULTIINSTANCE = True

    TRANSPORTS = (TransportRule(CONN_NET_TCP_CLI, requires='host'),)
    COMMAND_CLASS = SDPCommandParseStr
    LINE_TERMINATED = True
```

## Step 4: routing a multi-line reply

![MPD reply routing](img/mpd_reply_routing.svg)

With an asynchronous transport SDP does not know which request a line
answers. It matches each received line against the `reply_pattern` of every
command, and every match gets the line. So the design is:

- **one readable command per request** — it sends `status` and owns one line
  of the block;
- **receive-only or write-only commands for the other lines** — they never
  send `status` themselves, they only match their line.

```python
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
    'elapsed': {
        'read': False,
        'write': False,
        'item_type': 'num',
        'dev_datatype': 'num',
        'reply_pattern': r'^elapsed: ([\d.]+)$',
    },
    ...
}
```

Why not `read: True, read_cmd: 'status'` on every status command? It would
work, but initial, cyclic and group reads send each readable command once:
five readable status commands mean five identical `status` requests per
cycle. Items bound to a non-readable command still receive its values
(read/write model, guide section 10), so nothing is lost.

`{LOOKUP}` is replaced by `(play|pause|stop)` — the keys of the `STATE`
table — so the pattern only matches known states and contains the capture
group. The value then goes through the forward lookup:

```python
lookups = {'STATE': {'play': 'playing', 'pause': 'paused', 'stop': 'stopped'}}
```

Anchor every pattern (`^…$`). MPD's `currentsong` sends `Time:` while
`status` sends `time:`; anchored, case-sensitive patterns keep them apart.

Lines nobody matches (`OK`, the `OK MPD …` greeting, `file: …`) are discarded.

## Step 5: writes and value checks

```python
'volume': {
    'read': False,
    'write': True,
    'write_cmd': 'setvol {VALUE}',
    'item_type': 'num',
    'dev_datatype': 'int',
    'reply_pattern': r'^volume: (-?\d+)$',
    'cmd_settings': {'force_min': 0, 'force_max': 100},
},
```

- `{VALUE}` is replaced by the datatype-converted item value: `DT_int` turns
  `50.0` into `50`.
- `force_max: 100` clamps: an item set to 150 sends `setvol 100`. With
  `valid_max` the write would be refused and the item reset instead.
- `write_cmd` instead of `opcode`: the command has no read form, and the
  struct generator assigns read groups only to commands with `opcode` or
  `read_cmd`.
- The `reply_pattern` lets the `volume` item follow `status` replies although
  the command is not readable. (`-?` because MPD reports `volume: -1` when it
  has no mixer.)

## Step 6: a datatype for flags

MPD sends flags as `0`/`1`. `DT_bool` uses Python truthiness, and the string
`'0'` is truthy — `random: 0` would set the item to `True`. Sending is wrong
too: `str(True)` gives `random True`. A three-line datatype in
`example_mpd/datatypes.py` fixes both directions:

```python
class DT_mpdflag(DT.Datatype):
    """MPD flag: ``1``/``0`` on the wire, bool in shng."""

    def get_send_data(self, data, **kwargs):
        return 1 if data else 0

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return data == '1'
        return super().get_shng_data(data, type)
```

Referenced as `'dev_datatype': 'mpdflag'` (without `DT_`):

```python
'random': {
    'read': False,
    'write': True,
    'write_cmd': 'random {VALUE}',
    'item_type': 'bool',
    'dev_datatype': 'mpdflag',
    'reply_pattern': r'^random: ([01])$',
},
```

`control.pause` reuses it: `pause 1` pauses, `pause 0` resumes.

## Step 7: actions

`play`, `stop`, `next`, `previous` carry no value. As bool items with
`enforce_updates`, every set triggers the command — including setting
`False`. One hook restricts them to truthy values:

```python
ACTIONS = ('control.play', 'control.stop', 'control.next', 'control.previous')

def _do_before_send(self, command, value, kwargs):
    """Drop falsy writes to action commands."""
    if command in self.ACTIONS and not value:
        return False, True
    return True, True
```

Returning `(False, True)` ends `send_command()` with success, so the item is
not reset. Actions are `read: False`: a read-all (`x_read_group_trigger: 0`)
or an initial read never sends them.

## Step 8: errors from the device

`ACK …` lines match no pattern and would vanish silently. The receive hook
sees every line first:

```python
def _transform_received_data(self, data):
    """Log MPD error lines; they match no reply_pattern and are discarded afterwards."""
    if isinstance(data, str) and data.startswith('ACK'):
        self.logger.warning(f'MPD reports error: {data}')
    return data
```

## Step 9: plugin.yaml

What SDP needs from `example_mpd/plugin.yaml`:

```yaml
plugin:
    sdp_minversion: '2.0.0'
    classname: MpdSdp
parameters:
    host:        {type: str, mandatory: true}
    port:        {type: int, default: 6600}
    terminator:  {type: str, default: "\n"}     # double quotes: real newline
    resume_initial_read: {type: bool, default: true}
    ...
item_attributes:
    mpds_command: ...
    mpds_read: ...
    mpds_write: ...
    mpds_read_group: ...
    mpds_read_cycle: ...
    mpds_read_initial: ...
    mpds_read_group_trigger: ...
    mpds_lookup: ...
```

`resume_initial_read: true` refreshes all values after every reconnect. The
prefix `mpds_` avoids a clash with the existing `mpd` plugin's `mpd_command`.

## Step 10: generate the item structs

```bash
python doc/dev/sdp/example_mpd/__init__.py -s
```

Excerpt of the result in `plugin.yaml`:

```yaml
item_structs:
    status:
        read:
            type: bool
            enforce_updates: true
            mpds_read_group_trigger@instance: status
        state:
            type: str
            mpds_command@instance: status.state
            mpds_read@instance: true
            mpds_write@instance: false
            mpds_read_group@instance:
            -   status
            mpds_read_initial@instance: true
            mpds_read_cycle@instance: 10
        volume:
            type: num
            mpds_command@instance: status.volume
            mpds_read@instance: false
            mpds_write@instance: true
```

After generating, the `terminator` default read `|4+` followed by a blank
line, which loads as `"\n\n\n"` — every command would have been sent with two
extra empty lines. It was set back to `"\n"` by hand (guide section 14).

Item configuration for the user:

```yaml
wohnzimmer:
    mpd:
        status:
            struct: example_mpd.status
        song:
            struct: example_mpd.currentsong
        control:
            struct: example_mpd.control
```

One sub-item per struct: each struct has its own `read` trigger item, so
listing several structs on one item would merge them into one.

(The struct prefix is the plugin name: `plugin_name` from `etc/plugin.yaml`,
else the last part of `class_path` — here `example_mpd`.)

## Step 11: test it

`example_mpd/tests/test_mpd_example.py` loads the plugin through the real
plugin loader with `load_sdp_plugin()`, replaces the TCP client by a
`RecordingConnection`, and feeds device lines in as the TCP client would:

```python
def receive(self, *lines: str) -> None:
    for line in lines:
        self.plugin.on_data_received('127.0.0.1', line)

def test_status_block_fills_all_status_items(self):
    self.receive('volume: 42', 'repeat: 0', 'random: 1', 'state: pause', 'elapsed: 12.5', 'OK')

    self.assertEqual(42, self.rig.item('mpd.volume')())
    self.assertIs(True, self.rig.item('mpd.random')())
    self.assertEqual('paused', self.rig.item('mpd.state')())
    self.assertEqual(12.5, self.rig.item('mpd.elapsed')())

def test_volume_write_is_clamped(self):
    self.rig.item('mpd.volume')(150, 'test')

    self.assertEqual(['setvol 100\n'], self.rig.connection.payloads)
```

The suite also checks: initial reads send exactly `status\n` and
`currentsong\n`; `random: 0` gives `False`; actions run on `True` only;
receive-only commands are never requested; `ACK` lines are logged and change
nothing; items built from the generated `ALL` struct work
(`items_yaml_from_struct()` — the test harness does not expand `struct:`
itself); without `host` the plugin does not load; and the
`SdpPluginContractTest` checks pass.

## Result

| File | Lines (incl. docstrings) | Content |
|---|---|---|
| `__init__.py` | 74 | licence header, standalone boilerplate, 3 declarations, 2 small hooks |
| `commands.py` | 121 | 13 commands, 1 lookup |
| `datatypes.py` | 17 | `DT_mpdflag` |

For comparison, `plugins/mpd/__init__.py` has 640 lines for a larger command
set, with its own connection handling, reply parsing and polling.

## Possible next steps

- `currentsong` returns only `OK` when nothing is queued; title/artist/album
  then keep their old values. `_process_additional_data()` on `status.state`
  could clear them via `self._dispatch_callback()` when the state is
  `stopped`.
- MPD's `idle` command reports changes without polling; using it means
  re-sending `idle` after each notification (e.g. in
  `_process_additional_data()`), and interrupting it with `noidle` before
  other requests (`_do_before_send()`).
- Further `status` fields (`consume`, `single`, `xfade`, `bitrate`, …) and
  `stats` follow the same pattern as steps 4–6.
