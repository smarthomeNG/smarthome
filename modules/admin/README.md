# Module admin (README)

This module implements the administration interface for SmartHomeNG.


## Requirements

This module is running under SmmartHomeNG versions beyond develop version v1.5d. It requires Python >= 3.4 as well as ... . You can install the libraries (python modules) with:

```
(sudo apt-get install ...)
sudo pip3 install ...
```

And please pay attention that the lib(s) are installed for Python3 and not an older Python 2.7 that is probably installed on your system. Be carefull to use `pip3` and nor `pip`.

> Note: This module needs the module handling in SmartHomeNG to be activated. Make sure, that `use_modules`in `etc/smarthome.yaml` is **not** set to False!


## Configuration

### etc/module.yaml


```yaml
# etc/module.yaml
admin:
    module_name: admin
```


## API des Moduls admin

This module exposes a JWT-authenticated REST API under `/api/`, consumed by the shngadmin
frontend (a separate repository). The full endpoint-by-endpoint reference — every route,
method, query/body params, and auth requirement — lives in
[openapi.yaml](openapi.yaml); this section is a grouped overview, reconstructed 2026-07-20
from the actual handler code in `api_*.py` and cross-checked against every call site in
shngadmin. Where this file and `openapi.yaml` disagree, trust `openapi.yaml` — it's the
more detailed source.

**`openapi.yaml` is generated, not hand-edited** — same convention as `requirements/*.txt`
(see `lib/shpypi.py`). Its actual source of truth is the `ApiDoc`/`ApiParam` metadata
attached directly to each route's handler method in `api_*.py` (see `rest.py` for the
type definitions) — e.g. `read.api_doc = [ApiDoc(...)]` sitting right next to that same
method's existing `read.expose_resource = True` line. This replaced a hand-maintained
`api.raml` that went stale because nothing forced it to change alongside the code; putting
the metadata in the same few lines as the route it documents is the actual fix, not just a
different file format. After changing a route (or its `ApiDoc`), regenerate with:

```
python tools/build_openapi.py
```

Note: `/admin/` (without `/api`) is *not* part of this API — it's the suburl the built
Angular frontend's static files are served from. An older, unauthenticated set of
JSON/HTML endpoints used to live there before shngadmin migrated to this REST API; they
have since been removed (see the `WebInterface` class docstring in `__init__.py`).

Unless noted otherwise, every endpoint below requires the `Authorization: Bearer <jwt>`
header.

### AUTH API — login and token renewal

- `POST /api/authenticate/user` — log in with SHA-512-hashed credentials, get a JWT. *No auth required.*
- `PUT /api/authenticate/renew` — renew the current JWT before it expires.

### CONFIG API — read/write etc/smarthome.yaml and etc/module.yaml sections

- `GET /api/config/` — all config sections (common, http, websocket, admin, mqtt) in one call.
- `GET /api/config/{common|http|websocket|admin|mqtt}` — a single section (backend only; shngadmin always fetches everything via the bare `GET /config/`).
- `PUT /api/config/core` — save config. Despite the path, this writes *all* sections together in one call, regardless of which id (`core`/`common`/`http`/`admin`/`mqtt`) is used — shngadmin always uses `core`.
- `GET /api/config/check_config_etc/` — dry-run check whether `etc/` needs/can be migrated.
- `PUT /api/config/enable_config_etc/` — (re-)enable the `etc/` config directory.

### ITEMS API — item tree, item CRUD, struct templates

- `GET /api/items/list/` — flat item list.
- `GET /api/items/tree` — item tree structure.
- `GET /api/items/attributes` — core item-attribute catalog.
- `GET /api/items/structs/` — item struct templates (`etc/struct.yaml`).
- `GET /api/items/{itemPath}` — full detail for one item.
- `PUT /api/items/{itemPath}` — live-set an item's value.
- `POST /api/items/{itemPath}` — create a new item.
- `PATCH /api/items/{itemPath}` — replace an item's config (full replace, not a partial patch despite the verb).
- `DELETE /api/items/{itemPath}?persist=&recursive=` — delete an item.
- `POST /api/items/{itemPath}/rename` — rename or move an item (same endpoint for both).
- `POST /api/items/{itemPath}/copy` — copy an item, subtree included by default.
- `GET /api/items/{itemPath}/references` — what references this item (pre-delete check).
- `POST /api/items/{itemPath}/remove_references` — strip other items'/plugins' references to this item.

### PLUGINS API — read-only plugin discovery/info

- `GET /api/plugins/` — **deactivated 2026-07-20** (now 404s). Was an installed-plugin-name → type map, a strict subset of `GET /api/plugins/installed/`, which shngadmin already fetches. Being test-run as removed — see `api_plugins.py`'s `PluginsController.read`.
- `GET /api/plugins/installed/` — full metadata for every plugin in the `plugins/` directory.
- `GET /api/plugins/config/` — configuration of all currently configured plugins.
- `GET /api/plugins/info/` — plugin metadata for the plugin-list page.
- `GET /api/plugins/logicparams/` — plugin-contributed logic-parameter metadata.
- `GET /api/plugins/api/` — plugin API metadata.

### PLUGIN API — single-plugin config CRUD and lifecycle control

- `PUT /api/plugin/{pluginSection}/` — update one plugin's config section.
- `POST /api/plugin/{pluginSection}/` — add a new plugin config section.
- `DELETE /api/plugin/{pluginSection}/` — delete a plugin config section.
- `PUT /api/plugin/{pluginConfigName}?action={start|stop|load|unload|reload}[&filename=]` — lifecycle/state control.

### LOGICS API — logic list, detail, lifecycle, groups, parameters

- `GET /api/logics/[?infotype=groups]` — flat list, or the logic-group tree.
- `GET /api/logics/{logicName}[?infotype=status]` — one logic's detail, or its runtime status.
- `PUT /api/logics/{logicName}?action={trigger|enable|disable|load|unload|reload|delete|create|rename}[&filename=][&newfilename=]` — lifecycle/state actions and rename. (`delete_with_code` is a backend-only variant, also deletes the logic's `.py` file — not currently called by shngadmin.)
- `PUT /api/logics/{logicName}?action=saveparameters` — save the logic's parameter section.
- `PUT /api/logics/{groupName}?action=savegroup` — save a logic group.
- `PUT /api/logics/{groupName}?action=deletegroup` — delete a logic group.

### SCENES API — scene list and reload

- `GET /api/scenes/` — list of configured scenes.
- `PUT /api/scenes/reload/{name}` — reload one scene, or `all` for every scene.

### SCHEDULERS API — scheduler list

- `GET /api/schedulers/` — list of configured schedulers.

### THREADS API — running threads

- `GET /api/threads/` — list of running threads.

### FUNCTIONS API — registered functions

- `GET /api/functions/` — list of registered functions.
- `PUT /api/functions/reload/{name}` — reload one function, or `all` for every function.

### SERVICES API — config-text validation/conversion, cache maintenance

- `PUT /api/services/evalcheck/` — validate a Python `eval:`-style expression.
- `PUT /api/services/yamlcheck/` — validate raw YAML text.
- `PUT /api/services/yamlconvert/` — convert arbitrary config text to YAML.
- `GET /api/services/cachecheck/` — list orphaned cache files.
- `PUT /api/services/cachefile_delete?filename=` — delete one cache file.

### FILES API — raw read/write access to etc/ config files

`filetype` is a closed set: `structs`, `items`, `scenes`, `functions`, `logics` (list files
of that type, or read/write one with `?filename=`), plus the special cases `logging`
(`etc/logging.yaml`) and `backup` (GET only, returns a zip of the whole `etc/` dir).

- `GET /api/files/{filetype}/[?filename=]` — file list, or one file's raw text.
- `POST /api/files/{filetype}/?filename=` — create a new file (409 if it already exists).
- `PUT /api/files/{filetype}/[?filename=]` — save/overwrite a file. For `logging`, the response includes `config_reloaded`/`config_restored` flags — bad YAML is auto-rolled back server-side.
- `DELETE /api/files/{filetype}/[?filename=]` — delete a file.
- `GET /api/files/backup/` — download a config backup.
- `PUT /api/files/restore?filename=` — restore `etc/` from a backup (backend only — no current shngadmin caller found).

### LOGGERS API — logger list, level/handler control

- `GET /api/loggers/` — all loggers with current levels.
- `PUT /api/loggers/{logger}?level=` — set a logger's level.
- `PUT /api/loggers/{logger}?handlers=` — set a logger's handler list.
- `POST /api/loggers/{logger}/` — add a new logger.
- `DELETE /api/loggers/{logger}/` — delete a logger.

### LOGS API — log file list and chunked reading

- `GET /api/logs/` — list of available log files.
- `GET /api/logs/{filename}?chunk=` — one chunk of a log file (`chunk=1` first, `chunk=0` is the server convention for "last chunk").

### SERVER API — bootstrap info, status, restart, PyPI check

- `GET /api/server/` — basic info (`default_language`, `client_ip`, `login_required`, `websocket_host`, `websocket_port`). *No auth required* even though it's flagged `authentication_needed` in code — exempted via `public_root` for exactly this bare path. Also (ab)used as a lightweight reachability heartbeat by shngadmin.
- `GET /api/server/info` — extended info: timezone, core/plugins git branch, `developer_mode`, `dark_mode` default, `resource_graph_period`, `restart_stops_only`, and more.
- `GET /api/server/status/` — shng core running/stopped status.
- `PUT /api/server/restart/` — restart shng core.
- `GET /api/server/pypi` — PyPI package/version check data.

### SYSTEM API — OS/process-level stats

- `GET /api/system/info` — CPU/memory/disk stats for the System Overview page.

### WebSocket API — live item values and time-series charts

Separate from the REST API above: `ws(s)://{host}:{ws_port}/adm`, handled by the
`websocket` module's admin protocol (`modules/websocket/admin.py`), documented in
[websocket_admingui_requests.rst](websocket_admingui_requests.rst). Used for live item
value monitoring and the System Overview page's resource-usage graphs. No JWT is used on
this channel.

##


### Test if module admin is loaded

`admin` is a loadlable module. Therefore there is no guarantiee that it is present in every system. Before you can use this module, you have to make sure ist is loaded. You can do it by calling a method of the main smarthome object. Do it like this:

```
self.classname = self.__class__.__name__

try:
    self.mod_admin = self._sh.get_module('admin')
except:
    self.mod_admin = None
    
if self.mod_admin == None:
    # Do what is necessary if you can't use the admin interface
    # for your plugin. For example:
    self.logger.error('{}: Module ''admin'' not loaded - Abort loading of plugin {0}'.format(self.classname))
    return
```

