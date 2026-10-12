# Writing a device plugin with SmartDevicePlugin (SDP) 2.0

*Deutsche Fassung: [`sdp_plugin_guide.de.md`](sdp_plugin_guide.de.md)*

Audience: plugin authors. You know how a SmartHomeNG plugin is structured
(`plugin.yaml`, `__init__.py`, items) and want to connect a device that speaks
some command/reply protocol. How SDP works inside is in
[`sdp_architecture.md`](sdp_architecture.md); a complete worked example is in
[`sdp_commands_tutorial.md`](sdp_commands_tutorial.md).

Contents

1. [Is SDP the right base?](#1-is-sdp-the-right-base)
2. [Anatomy of an SDP plugin](#2-anatomy-of-an-sdp-plugin)
3. [The plugin class: declarations](#3-the-plugin-class-declarations)
4. [plugin.yaml](#4-pluginyaml)
5. [commands.py reference](#5-commandspy-reference)
6. [Command classes](#6-command-classes)
7. [Datatypes](#7-datatypes)
8. [Lookups](#8-lookups)
9. [Models](#9-models)
10. [The read/write model](#10-the-readwrite-model)
11. [Hooks: adding device logic](#11-hooks-adding-device-logic)
12. [Runtime template values](#12-runtime-template-values)
13. [Several devices behind one connection (custom tokens)](#13-several-devices-behind-one-connection-custom-tokens)
14. [Generating item structs](#14-generating-item-structs)
15. [Testing](#15-testing)
16. [Migrating a 1.x SDP plugin to 2.0](#16-migrating-a-1x-sdp-plugin-to-20)
17. [Checklist and pitfalls](#17-checklist-and-pitfalls)

---

## 1. Is SDP the right base?

SDP fits when:

- one plugin instance talks to one connection (TCP, HTTP, UDP, serial),
- the device protocol is a set of commands, each reading and/or writing one
  value,
- replies (or unsolicited notifications) can be told apart by a regular
  expression, a JSON-RPC id, or a request/reply sequence.

SDP does not fit, or only with substantial custom code, when one instance
manages many devices with discovery and per-host state (e.g.
`plugins/yamahayxc`), when values arrive as large documents needing
structural processing (cloud APIs, browse trees), or when authentication
flows dominate.

## 2. Anatomy of an SDP plugin

```
plugins/<name>/
    __init__.py      plugin class: declarations, optional hooks (often < 20 lines)
    commands.py      commands, lookups, optional models / item_templates  (required)
    datatypes.py     custom DT_* value converters                          (optional)
    protocol.py      custom SDPProtocol subclass                           (optional, rare)
    plugin.yaml      metadata, parameters, item attributes, generated item_structs
    tests/           characterization / contract / behaviour tests
    webif/           optional web interface
```

A complete real plugin, `plugins/epson/__init__.py`, minus licence header and
standalone boilerplate:

```python
from lib.model.sdp.command import SDPCommandParseStr
from lib.model.sdp.declarations import TransportRule
from lib.model.sdp.globals import CONN_SER_ASYNC
from lib.model.smartdeviceplugin import SmartDevicePlugin, Standalone


class epson(SmartDevicePlugin):
    """Device class for Epson projectors."""

    PLUGIN_VERSION = '1.0.0'

    TRANSPORTS = (TransportRule(CONN_SER_ASYNC, requires='serialport'),)
    COMMAND_CLASS = SDPCommandParseStr
    LINE_TERMINATED = True
```

The standalone boilerplate (top of `__init__.py`, copy it from
`dev/sample_smartdevice_plugin/__init__.py`) sets `builtins.SDP_standalone`
and lets you run the file directly for struct generation:

```python
import builtins
import os
import sys

if __name__ == '__main__':
    builtins.SDP_standalone = True

    class SmartPlugin:
        pass

    class SmartPluginWebIf:
        pass

    BASE = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-3])
    sys.path.insert(0, BASE)

elif not hasattr(builtins, 'SDP_standalone'):
    builtins.SDP_standalone = False

# ... imports and class ...

if __name__ == '__main__':
    s = Standalone(MyPlugin, sys.argv[0])
```

The `elif not hasattr(...)` guard matters: loading `commands.py` imports the
package a second time under its package name; overwriting a `True` with
`False` there breaks standalone mode.

## 3. The plugin class: declarations

Device defaults are class attributes (`lib/model/smartdeviceplugin.py`):

| Attribute | Type | Default | Meaning |
|---|---|---|---|
| `TRANSPORTS` | `tuple[TransportRule, ...]` | `()` | transport selection; first matching rule wins |
| `PROTOCOL` | type name or class | `None` | protocol wrapping the transport (`PROTO_JSONRPC`, `PROTO_RESEND`, or your class) |
| `COMMAND_CLASS` | class or class name in `lib.model.sdp.command` | `None` → `SDPCommand` | how commands build payloads and parse replies |
| `LINE_TERMINATED` | bool | `False` | append the `terminator` parameter to every payload and read replies up to it |
| `JSON_MOVE_KEYS` | `tuple[str, ...]` | `()` | JSON-RPC only: per-send kwargs moved into the request `params` |
| `CUSTOM_TOKEN` | `CustomTokenSpec` | `None` | several devices behind one connection, see section 13 |

`TransportRule(use, requires=None)`: `use` is a connection type
(`CONN_NET_TCP_CLI`, `CONN_NET_TCP_REQ`, `CONN_NET_UDP_SRV`, `CONN_SER_DIR`,
`CONN_SER_ASYNC`, `CONN_NULL`) or a connection class; `requires` names the
plugin parameter that must be set.

```python
TRANSPORTS = (
    TransportRule(CONN_NET_TCP_CLI, requires='host'),
    TransportRule(CONN_SER_ASYNC, requires='serialport'),
)
```

- Both `host` and `serialport` configured → the first rule is used, warning.
- Neither → error "none of ['host', 'serialport'] is configured", plugin
  disabled. Add `TransportRule(CONN_NULL)` last only if the plugin should load
  without a device (sample plugin).
- A `conn_type` set in `etc/plugin.yaml` is ignored with a warning.

Which transport for which device:

| Device talks | Transport | Replies arrive |
|---|---|---|
| persistent TCP socket, line or byte stream | `CONN_NET_TCP_CLI` | asynchronously via callback; reconnects itself |
| HTTP request/response | `CONN_NET_TCP_REQ` | as return value of the request |
| HTTP + UDP push notifications | `CONN_NET_UDP_SRV` | request return value + UDP callback |
| serial, strict request → reply | `CONN_SER_DIR` | as return value, read up to `limit_response` |
| serial, device also pushes | `CONN_SER_ASYNC` | asynchronously via reader thread |

Asynchronous transports mean a reply is not linked to its request: SDP
identifies the command from the reply text via `reply_pattern` (section 5).

## 4. plugin.yaml

### Plugin section

```yaml
plugin:
    ...
    sdp_minversion: '2.0.0'     # quoted; plugin is not loaded on older SDP
    suspendable: true           # SDP implements suspend/resume
    classname: MyPlugin
```

### Parameters SDP reads

SDP only sees parameters your `plugin.yaml` declares (metadata drops
undeclared ones), so declare what your device needs, with sensible defaults.

| Parameter | Default if undeclared | Purpose |
|---|---|---|
| `host`, `port` | — / 0 | network target; `host` selects network rules |
| `serialport`, `baudrate`, `bytesize`, `parity`, `stopbits` | — / 9600 / 8 / N / 1 | serial settings |
| `terminator` | `''` | line terminator for `LINE_TERMINATED`; write `"\r"` / `"\n"` in double quotes |
| `timeout` | 1.0 | transport read timeout (s) |
| `binary` | False | serial transports return `bytes` instead of `str` |
| `autoreconnect` | transports: True; plugin-scheduled reconnect: off | reconnect after loss — declare it explicitly |
| `autoconnect` | value of `autoreconnect` (False if that is undeclared) | connect on demand when sending |
| `connect_retries`, `connect_cycle` | 3, 5 | attempts per round, seconds between |
| `retry_cycle` | 30 | seconds between rounds (TCP client) |
| `retry_suspend` | 0 | failed rounds until the plugin suspends itself (TCP client; 0 = never) |
| `send_retries`, `send_retries_cycle` | 0, 1 | resend unanswered commands; `> 0` without `PROTOCOL` selects the resend protocol |
| `send_timeout` | 5 | JSON-RPC: seconds until an unanswered message is resent |
| `model` | — | selects a model from `commands.py` (section 9) |
| `cycle` | — | plugin-wide cycle for `x_read_cyclic` items |
| `delay_initial_read` | 0 | seconds after connect before initial reads (minimum 1) |
| `resume_initial_read` | — | repeat initial reads after every reconnect/resume |
| `suspend_item` | — | item path toggling suspend mode |
| `recursive_custom` | — | custom attribute index (or list) inherited by child items |
| `loop_guard_count`, `loop_guard_window`, `loop_guard_source` | 0, 5, '' | suppress a write repeated `count` times within `window` s (only callers starting with `source`, if set) |

Do not declare `conn_type`, `protocol` or `command_class` in new plugins; the
declarations replace them.

### Item attributes

SDP finds your item attributes by **suffix**; the prefix is yours (`ex_`,
`denon_`, …). Declare the ones you support in `item_attributes`:

| Suffix | Type | Effect |
|---|---|---|
| `_command` | str | binds the item to a command; the item receives that command's values |
| `_read` | bool | the item requests its value (initial, cyclic, group reads) — command must be readable |
| `_write` | bool | item changes are sent — command must be writable |
| `_read_group` | list(str) | read groups the item's command belongs to |
| `_read_cycle` | num | cyclic read interval in seconds |
| `_read_cyclic` | bool | cyclic read with the plugin-wide `cycle` |
| `_read_initial` | bool | read on connect |
| `_readafterwrite` | num | read the command again this many seconds after a write |
| `_read_group_trigger` | str | setting the item reads the group; `0` reads all readable commands |
| `_lookup` | str | item holds lookup table `name[#fwd\|rev\|rci\|list]`; a `fwd` item can be written to replace the table |
| `_valid_list` | str | item holds the valid list of the named command; writing it replaces the list |
| `_custom1` … `_custom3` | str | free values for your plugin; custom tokens (section 13) |

Copy and adapt the full block from `dev/sample_smartdevice_plugin/plugin.yaml`.

## 5. commands.py reference

`commands.py` is a plain Python module. SDP reads these module-level names:

| Name | Required | Content |
|---|---|---|
| `commands` | yes | the command tree |
| `lookups` | no | translation tables (section 8) |
| `models` | no | command lists per model (section 9) |
| `item_templates` | no | attribute sets the struct generator can insert |

### Command tree

Commands are dicts; any nesting of section dicts groups them. The command
name is the dotted path: `{'zone1': {'control': {'power': {...}}}}` defines
`zone1.control.power`.

**`item_type` marks a command.** A dict with `item_type` is a command; a dict
without it is a section, and SDP flattens its dict-valued children into
`section.child`. Leave out `item_type` on a command and its `cmd_settings`,
`params` or `item_attrs` dicts become bogus commands. Always set `item_type`.

### Command keys

| Key | Default | Meaning |
|---|---|---|
| `read` | `True` | the value can be requested from the device |
| `write` | `False` | item values can be sent to the device |
| `opcode` | `''` | payload for reads and writes when `read_cmd` / `write_cmd` are absent |
| `read_cmd` | — | payload for reads |
| `write_cmd` | — | payload for writes |
| `item_type` | `'bool'` | shng item type; marks the dict as command; used by the struct generator |
| `dev_datatype` | `'raw'` | `DT_` class converting values (`'int'` → `DT_int`); unknown → error log, `DT_raw` |
| `reply_pattern` | — | regex (or list) identifying replies of this command; tokens below |
| `cmd_settings` | — | value checks for writes (below) |
| `lookup` | — | lookup table name (section 8); disables `cmd_settings` checks |
| `params` | — | `SDPCommandJSON`: JSON-RPC params; `SDPCommandViessmann`: encoding params |
| `custom_disabled` | `False` | exclude this command from custom token handling |
| `send_retries` | — | per-command override of `send_retries` (resend protocol) |
| `item_attrs` | — | struct generator directives (section 14); no runtime effect |
| `param_values` | — | accepted, not used by any command class |

Set `read` and `write` explicitly on every command; `read` defaults to `True`.

### reply_pattern

Received data without a known command (asynchronous transports, push
notifications) is matched against the `reply_pattern`s of **all** commands
with `re.search`. Every matching command gets the data. Hence:

- anchor patterns (`^…$`) and make them unique across commands;
- `'*'` stands for the command's `read_cmd` (else `opcode`), used verbatim as
  regex;
- with `SDPCommandParseStr`, exactly one capture group extracts the value;
  zero groups pass the whole reply to the datatype; more than one is an error.
  Use `(?:…)` for grouping without capture.

Tokens replaced when commands are loaded (and again when a lookup or valid
list changes):

| Token | Replaced by |
|---|---|
| `{LOOKUP}` | `(k1\|k2\|…)` — the escaped device-side keys of the command's lookup table (a capture group) |
| `{VALID_LIST}` | `(v1\|v2\|…)` from `cmd_settings['valid_list']` |
| `{VALID_LIST_CI}` | same, case-insensitive |
| `{VALID_LIST_RE}` | `(re1\|re2\|…)` from `valid_list_re` |
| `{CUSTOM_PATTERN1..3}` | `CUSTOM_TOKEN.reply_re` for that index |
| `{PARAM:name}` | `template_vars['name']` when commands are loaded — before `_post_init()`, so effectively the plugin parameter |

### cmd_settings (write checks)

Applied to written values when the command has no `lookup`. Only the first
present of `valid_list_ci`, `valid_list`, `valid_list_re`, or the min/max
group applies.

| Key | Effect |
|---|---|
| `valid_list` | value must be in the list |
| `valid_list_ci` | same, case-insensitive |
| `valid_list_re` | value must `fullmatch` one of the regexes |
| `valid_min`, `valid_max` | outside → write refused |
| `force_min`, `force_max` | outside → clamped |

Min/max keys are checked in the order `valid_min`, `valid_max`, `force_min`,
`force_max`: a value outside a `valid_*` bound is refused before a `force_*`
bound could clamp it. Use either `valid_*` or `force_*` per side (the sample
`commands.py` comment "precedence over min" does not match the code).

A refused write resets the item to its previous value.

## 6. Command classes

| Class | Payload | Substitutions in `opcode` / `read_cmd` / `write_cmd` | Reply value |
|---|---|---|---|
| `SDPCommand` | command string verbatim; `data` = DT value | none | `DT.get_shng_data(reply)` |
| `SDPCommandStr` | parsed string; request args from `template_vars` | `{OPCODE}`, `{VALUE}`, `{PARAM:x}`, `{CUSTOM_PARAMn:x}`, `{CUSTOM_ATTRn}` | `DT.get_shng_data(reply)` (bytes decoded) |
| `SDPCommandParseStr` | parsed string, then `str.format()` | as `SDPCommandStr`, plus on writes `{RAW_VALUE}`, `{RAW_VALUE_UPPER}`, `{RAW_VALUE_LOWER}`, `{RAW_VALUE_CAP}` | capture group of `reply_pattern` → DT |
| `SDPCommandJSON` | JSON-RPC method; `data` = `params` | in `params`: `'{VALUE}'`, `'{CUSTOM_ATTRn}'`, `'{ID}'` / key `playerid` from per-send kwarg `playerid`, tuple = eval expression | `DT.get_shng_data(reply['result'])` |
| `SDPCommandViessmann` | opcode; `data` = `params` dict | `'VAL'`, tuple = eval expression | DT with `len`/`mult`/`signed` |

Notes:

- `{VALUE}` is the datatype-converted value (`str(DT.get_send_data(v))`);
  `{RAW_VALUE*}` is the unconverted item value.
- `SDPCommandParseStr` runs `str.format()` on write commands: literal braces
  must be doubled (`{{`, `}}`).
- `SDPCommandStr` adds `request_method`, `params`, `headers`, `data`,
  `cookies`, `files` from `template_vars` (parameters or runtime values) to
  every `data_dict` — that is how HTTP devices get headers or POST bodies.
- Tuple values in `params` are `eval()`ed with the item value spliced in.
  Anything that can write the item can inject code; see the warning in
  `dev/sample_smartdevice_plugin/commands.py`.

## 7. Datatypes

Generic classes in `lib/model/sdp/datatypes.py`: `DT_raw` (unchanged),
`DT_none`, `DT_bool`, `DT_int`, `DT_num`, `DT_str`, `DT_list`, `DT_dict`,
`DT_tuple`, `DT_bytes`, `DT_bytearray`, `DT_json`, `DT_webservices`.

`DT_bool` uses Python truthiness: the device string `'0'` becomes `True`.
Devices that send `0`/`1`, `ON`/`OFF` etc. need their own datatype.

Custom datatypes go into `<plugin>/datatypes.py`; every `DT_*` class there is
picked up and referenced without prefix (`'dev_datatype': 'onoff'`). Example
from `plugins/epson/datatypes.py`:

```python
import lib.model.sdp.datatypes as DT


class DT_onoff(DT.Datatype):
    def get_send_data(self, data, **kwargs):
        return 'ON' if data else 'OFF'

    def get_shng_data(self, data, type=None, **kwargs):
        return False if data == '0' else True if data == '1' else None
```

`get_send_data(value)` converts item → device, `get_shng_data(data)` device →
item. Raise an exception for unconvertible input; SDP logs it and skips the
value.

## 8. Lookups

A lookup table maps device values to item values:

```python
lookups = {
    'INPUT': {'CD': 'CD', 'TUNER': 'Radio', 'SAT/CBL': 'TV'},
}
```

- Receiving: the reply value is looked up forward (device → item).
- Sending: the item value is looked up in reverse, case-insensitively; a value
  that already is a device key is sent as is.
- `'reply_pattern': '^SI{LOOKUP}$'` only matches known device values.
- Items can hold a table: `x_lookup: INPUT` (forward dict), `INPUT#rev`,
  `INPUT#rci` (lower-cased reverse), `INPUT#list` (item values, e.g. for a
  visu dropdown). Writing a new dict to the forward item replaces the table at
  runtime (`update_lookup()`), including all derived items and reply patterns.
- With models: `{'ALL': {...tables...}, 'model1': {...overrides...}}`.

## 9. Models

The `model` parameter selects a command set. Two styles:

1. `commands` has the top-level key `'ALL'` (shared commands) plus one key per
   model; the model's commands are merged over `ALL`. A configured model not
   present in `commands`, `lookups` or `structs` stops the plugin.
2. `commands` without `ALL`, plus a `models` dict listing command paths (or
   section prefixes) per model, with optional `'ALL'` for shared ones. A
   configured model missing in `models` stops the plugin; so does a configured
   model when `commands.py` has neither `ALL` nor `models`.

Without `model`, all commands are loaded. See the three annotated styles in
`dev/sample_smartdevice_plugin/commands.py` (its note that a model without
`models` dict loads all commands does not match the code).

## 10. The read/write model

- `read` / `write` describe what the **device** can do.
- Every item bound to a command receives that command's values — from read
  replies, from notifications, or from your plugin code via
  `dispatch_data()` / `_dispatch_callback()`. `x_read` / `x_write` on the item
  only decide whether the item requests or sends.
- `send_command(cmd)` without a value is refused for commands not declared
  readable (debug log, returns `False`).
- A command with `read: False` and `write: False` is a pseudo command: it
  exists for the plugin to fill (kodi's `info.*`) or as a receive-only target
  of a `reply_pattern`.

This allows "one request, many values": a readable command requests a status
block, and receive-only commands pick their lines from it by
`reply_pattern` (see the tutorial).

## 11. Hooks: adding device logic

Override only what the device needs. Hooks in the stable contract:

| Hook | Called | Typical use | Example |
|---|---|---|---|
| `_post_init()` | end of `__init__` | own attributes, `template_vars`, `self._webif = WebInterface` | `plugins/lms` |
| `on_connect(by)` | connection established | subscribe to notifications, query status — **call `super().on_connect(by)`** (starts initial and cyclic reads) | `plugins/lms`, `plugins/kodi` |
| `on_disconnect(by)` | connection lost | cleanup — **call `super()`** (schedules reconnect) | sample plugin |
| `on_suspend()` / `on_resume()` | after suspend / resume | device-side sleep/wake | sample plugin |
| `_do_before_send(command, value, kwargs)` | before building the payload | return `(False, result)` to handle a command in the plugin; add per-send kwargs | `plugins/kodi` |
| `_transform_send_data(data_dict, **kwargs)` | after building the payload | add framing; **call `super()`** with `LINE_TERMINATED` | — |
| `_transform_received_data(data)` | first thing on receive | clean/decode raw data | `plugins/lms` (URL unquoting) |
| `_process_additional_data(command, data, value, custom, by)` | after an item update | follow-up reads, derived values via `self._dispatch_callback(cmd, value, by)` | `plugins/lms`, `plugins/denon`, `plugins/pioneer` |
| `_send(data_dict, **kwargs)` | hand-off to the connection | rarely needed | — |

Also available: `set_custom_item(item, command, index, value)` (called during
item parsing per custom value), `run_standalone()` (diagnostics, viessmann),
`send_command(cmd, value=None, return_result=False, raise_on_error=False,
**kwargs)`, `read_all_commands(group)`, `custom_tokens(index)`,
`set_suspend(active, by)`, `update_lookup(table, data)`.

Prefer declarations and `commands.py` over code: in 2.0, epson, pioneer and
denon need no `_set_device_defaults()`, no `on_data_received()` override and
no terminator handling.

JSON-RPC plugins: the JSON-RPC protocol reports the JSON **method** as
`command`, not the SDP command name; override `on_data_received()` and map
methods to commands (`plugins/kodi`).

## 12. Runtime template values

`self.template_vars` is a `ChainMap` whose first map is yours and whose
fallback are the plugin parameters. `{PARAM:x}` and `{CUSTOM_PARAMn:x}` in
command strings read from it at send time:

```python
def _post_init(self):
    self.template_vars['CURRENT_LIST_ID'] = {}     # filled later per player
```

Per-send values go into `kwargs` in `_do_before_send()` (they are not kept
between sends), e.g. kodi's `kwargs['playerid'] = self._playerid`.

## 13. Several devices behind one connection (custom tokens)

```python
CUSTOM_TOKEN = CustomTokenSpec(
    index=1,                                                   # uses x_custom1
    token_re='([0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}',          # finds the token in replies
    reply_re='(?:[0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2}',        # for {CUSTOM_PATTERN1}
    recursive=True,                                            # children inherit x_custom1
)
```

(`plugins/lms`, one token per player MAC.) Items under a player item with
`lms_custom1: aa:bb:cc:dd:ee:ff` bind to `command#aa:bb:cc:dd:ee:ff`.
Command strings put the token in with `{CUSTOM_ATTR1}`, reply patterns
accept any token with `{CUSTOM_PATTERN1}`, and received values go to the
items of the token found in the reply. Only tokens used by bound items are
accepted. Send to one device with `self.send_command('cmd' + CUSTOM_SEP + token)`.

## 14. Generating item structs

From the shng base directory:

```bash
python plugins/<name>/__init__.py -s
```

writes `item_structs` into `plugins/<name>/plugin.yaml` (`-a` adds
`visu_acl`, `-l` lower-cases item names). Each section gets a `read` item
triggering its read group, each command an item with `x_command`, `x_read`,
`x_write` and read groups.

Per-command `item_attrs` directives:

| Directive | Generates |
|---|---|
| `initial: True` | `x_read_initial: true` |
| `cycle: n` | `x_read_cycle: n` |
| `cyclic: True` | `x_read_cyclic: true` |
| `enforce: True` | `enforce_updates: true` |
| `read_group_levels: n` | only the last `n` read group levels (0: none) |
| `read_groups: [{'name': g, 'trigger': 'path'}]` | extra read group plus trigger item (leading dots go up) |
| `lookup_item: True\|'fwd'\|'rev'\|'rci'\|'list'` | `lookup` child item holding the table |
| `custom1..3: v` | `x_customN: v` |
| `attributes: {...}` | attributes copied verbatim |
| `item_template: name` | attributes from `item_templates[name]` |

On a section, `initial` / `cycle` apply to its `read` trigger item.

The generator rewrites the whole `plugin.yaml`: comments and the `%YAML`
header disappear, strings are re-quoted, and a `"\n"` terminator default
comes back as `"\n\n\n"`. Review the diff and fix such values before
committing.

## 15. Testing

Plugin tests live in `plugins/<name>/tests/test_*.py` and use core helpers:

- **Characterization snapshot** (records what the plugin sends and sets for a
  generated struct; 3 lines):

  ```python
  from tests.sdp_harness.characterize import characterize_plugin

  class TestCharacterization(unittest.TestCase):
      def test_matches_snapshot(self):
          characterize_plugin(self, 'epson', 'epson', 'ALL', {'serialport': '/dev/null'})
  ```

  Create or update the snapshot with `SDP_SNAPSHOT_UPDATE=1 pytest …`.
- **Contract test**: `SdpPluginContractTest` (`tests/plugin_contract/sdp.py`),
  see `dev/sample_smartdevice_plugin/tests/test_contract.py`.
- **Behaviour tests**: `load_sdp_plugin()` from `tests/sdp_harness` loads the
  plugin through the real loader with a `RecordingConnection`; feed replies
  with `rig.plugin.on_data_received(by, data)`, check
  `rig.connection.payloads` and item values, fire jobs with
  `rig.plugin_jobs()['read_initial_values'].fire()`. Example:
  `doc/dev/sdp/example_mpd/tests/test_mpd_example.py`.

Use a literal IP as `host` in tests: the TCP client is constructed before the
harness replaces it, and a host name means a DNS lookup per test.

## 16. Migrating a 1.x SDP plugin to 2.0

1. `plugin.yaml`: `sdp_minversion: '2.0.0'`; remove `conn_type`, `protocol`,
   `command_class` parameters; rename `send_retries_timeout` → `send_timeout`;
   drop `message_timeout`/`message_repeat` (copied from the old template, never
   read by SDP — the resend settings are `send_retries`, `send_retries_cycle`,
   `send_timeout`).
2. Replace `_set_device_defaults()` by declarations: connection choice →
   `TRANSPORTS`, protocol → `PROTOCOL`, command class → `COMMAND_CLASS`,
   terminator escaping and appending → `LINE_TERMINATED`, JSON key moving →
   `JSON_MOVE_KEYS`, custom token setup → `CUSTOM_TOKEN`. Writes to
   `self._parameters` still work and win, with a debug hint.
3. Remove `_use_callbacks` (callbacks are always on; a warning is logged).
4. Remove copies of `on_data_received()` and `_transform_send_data()` that
   only re-implemented base behaviour. epson before 2.0:

   ```python
   def _set_device_defaults(self):
       if PLUGIN_ATTR_SERIAL_PORT in self._parameters and self._parameters[PLUGIN_ATTR_SERIAL_PORT]:
           self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_SER_ASYNC
       else:
           ...
           self._parameters[PLUGIN_ATTR_CONNECTION] = CONN_NULL
       b = self._parameters[PLUGIN_ATTR_CONN_TERMINATOR].encode()
       b = b.decode('unicode-escape').encode()
       self._parameters[PLUGIN_ATTR_CONN_TERMINATOR] = b

   def _transform_send_data(self, data=None, **kwargs): ...   # append terminator
   def on_data_received(self, by, data, command=None): ...    # 45-line copy of the base
   ```

   epson 2.0: the three declarations shown in section 2.
5. Replace access to removed registries (`_items_write`, `_items_read_all`,
   `_commands_read`, `_commands_initial`, `_items_custom`, …) by public calls:
   `custom_tokens()`, `read_all_commands()`, `get_items_for_mapping()`.
6. Own connection classes: constructor `(config, hooks, scheduler, name)`,
   setup in `_setup()`, settings from `self._config` (`self._config.extra`
   for non-standard ones), defaults in `CONFIG_DEFAULTS`. `self._params` no
   longer exists.
7. Revisit `read` flags: an action command (play, stop, …) marked
   `read: True` is now sent by read-all and initial reads. Mark it
   `read: False`; its items still receive values.
8. Call `super().on_connect(by)` in an overridden `on_connect()`.

Behaviour changes users see:

- a plugin with `TRANSPORTS` and neither `host` nor `serialport` is disabled
  with an error instead of running on the dummy connection;
- items bound to write-only or pseudo commands receive device and plugin
  values;
- reading a command not declared readable is refused;
- plugins setting `_use_callbacks` and external connection classes using the
  old constructor log a one-time warning.

## 17. Checklist and pitfalls

- [ ] `sdp_minversion: '2.0.0'` in `plugin.yaml`
- [ ] every command has `item_type`, `read` and `write`
- [ ] every reply pattern anchored and unique across commands
- [ ] `terminator` declared (double quotes) when `LINE_TERMINATED`
- [ ] boolean device values use a custom datatype, not `DT_bool`
- [ ] action commands are `read: False`
- [ ] overridden `on_connect` / `on_disconnect` / `_transform_send_data` call `super()`
- [ ] item attributes declared for every suffix you document
- [ ] struct generated, `plugin.yaml` diff reviewed
- [ ] characterization or behaviour tests in `plugins/<name>/tests/`
