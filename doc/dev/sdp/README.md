# SmartDevicePlugin (SDP) documentation

SDP (`lib/model/smartdeviceplugin.py`, `lib/model/sdp/`) is the base class
for device plugins in SmartHomeNG: a plugin supplies `commands.py`, optional
datatypes and a few class attributes; SDP does item handling, value
conversion, connections, reads, suspend and reconnect. This directory
describes SDP 2.0.0.

| Document | For | Content |
|---|---|---|
| [`sdp_plugin_guide.md`](sdp_plugin_guide.md), [deutsch](sdp_plugin_guide.de.md) | plugin authors | declarations, `plugin.yaml`, full `commands.py` reference, command classes, datatypes, lookups, models, hooks, testing, migration from 1.x |
| [`sdp_commands_tutorial.md`](sdp_commands_tutorial.md), [deutsch](sdp_commands_tutorial.de.md) | plugin authors | worked example: an MPD plugin from protocol to tested `commands.py` |
| [`sdp_architecture.md`](sdp_architecture.md) | SDP developers | layers, modules, typed contracts, init and configuration resolution, send/receive paths, lifecycle, threads, API surface, extension seams, tests, design decisions |
| [`example_mpd/`](example_mpd/) | both | the tutorial plugin with its tests |

Diagrams in [`img/`](img/):

| Diagram | Shows |
|---|---|
| [`sdp_layers.svg`](img/sdp_layers.svg) | layers and their interfaces |
| [`sdp_modules.svg`](img/sdp_modules.svg) | modules and imports |
| [`sdp_init_flow.svg`](img/sdp_init_flow.svg) | `__init__` order, configuration precedence |
| [`sdp_transport_selection.svg`](img/sdp_transport_selection.svg) | choice of transport and protocol |
| [`sdp_send_flow.svg`](img/sdp_send_flow.svg) | item → device |
| [`sdp_receive_flow.svg`](img/sdp_receive_flow.svg) | device → item |
| [`sdp_lifecycle.svg`](img/sdp_lifecycle.svg) | run, connect, reconnect, suspend, stop |
| [`mpd_reply_routing.svg`](img/mpd_reply_routing.svg) | tutorial: one request, many receivers |

Related code to read alongside: `dev/sample_smartdevice_plugin/` (annotated
template), `plugins/epson` (smallest real plugin), `plugins/lms` (custom
tokens, hooks), `plugins/kodi` (JSON-RPC), `plugins/viessmann` (own
protocol).

The example tests run from the shng base directory:

```bash
pytest doc/dev/sdp/example_mpd/tests
```
