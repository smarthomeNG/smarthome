# shngAdmin — How It Works

## Part 1 — What kind of program is this?

Before anything Angular-specific, it helps to know what category of program this is.

shngAdmin is a **Single-Page Application (SPA)**. That means:

- The server sends one HTML file, once, when you first open the browser.
- After that, the browser never loads another page from the server. All navigation happens by JavaScript rewriting the DOM.
- Data comes in and out via HTTP API calls and a WebSocket, just like `requests.get()` in Python, but running inside the browser.

The contrast with a traditional web app (Django, Flask with Jinja templates):

```
TRADITIONAL WEB APP (Django/Flask)
┌────────────────────────────────────────────────────────┐
│ Browser                                                │
│   click "Users" → GET /users/                          │
│                 ← server renders HTML, sends full page │
│   click "Edit"  → GET /users/5/edit/                   │
│                 ← server renders HTML, sends full page │
└────────────────────────────────────────────────────────┘

SINGLE-PAGE APPLICATION (Angular)
┌────────────────────────────────────────────────────────┐
│ Browser                                                │
│   load once   → GET /                                  │
│               ← index.html + all JS bundle             │
│                 (the entire app, pre-compiled)         │
│   click "Items" → JavaScript rewrites the DOM          │
│                   then fires GET /api/items/list/      │
│                ← JSON data only                        │
│   click "Logs"  → JavaScript rewrites the DOM          │
│                   then fires GET /api/logs/            │
│                ← JSON data only                        │
└────────────────────────────────────────────────────────┘
```

The backend (SmartHomeNG's REST API) never knows or cares about page transitions. It only sees JSON API calls.

---

## Part 2 — The Python analogy for Angular concepts

Angular has four main building blocks. Here's how to think about each one if you come from Python.

```
ANGULAR CONCEPT        PYTHON ANALOGY
───────────────────    ───────────────────────────────────────────
Component              A Python class that owns a piece of the UI.
                       It has data attributes and methods, and a
                       template (like a Jinja2 .html file, but
                       tightly coupled to the class).

Service                A Python class that does work with no UI.
                       HTTP calls, data transformation, shared
                       state. Injected into components, similar to
                       how you'd pass a db session or a requests
                       Session into a function.

Module / Route         Like a Python package's __init__.py that
                       registers a URL blueprint. In modern Angular
                       (which this app uses) these are mostly
                       replaced by plain file imports + a route
                       configuration file.

Template               An HTML file with Angular-specific syntax.
                       Think Jinja2, but instead of {{ var }} for
                       everything, Angular uses:
                         {{ var }}        → render a value
                         [attr]="expr"    → bind HTML attribute
                         (event)="fn()"   → bind event handler
                         *ngIf="cond"     → conditional render
                         *ngFor="x of y"  → loop
                         @if / @for       → modern syntax same idea
```

**Dependency Injection** is the glue. In Python you'd write:

```python
class LogicsComponent:
    def __init__(self, api_service, logger):
        self.api = api_service
        self.log = logger
```

Angular does the same thing automatically. You declare what you need in the constructor, and Angular creates or reuses the instances:

```typescript
// Angular
export class LogicsListComponent {
  constructor(
    private logicsApi: LogicsApiService,   // Angular creates this once, injects it
    private router: Router                  // Angular's built-in router, also injected
  ) {}
}
```

---

## Part 3 — The overall system architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (shngAdmin Angular App)                                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  UI Layer (Components + Templates)                       │   │
│  │  dashboard│system│items│logics│plugins│scenes ...        │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │ calls                               │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │  Service Layer                                           │   │
│  │  API Services          Infrastructure Services           │   │
│  │  server-api            auth        connectivity          │   │
│  │  items-api             websocket   app-config            │   │
│  │  logics-api            log         shared                │   │
│  │  plugins-api           user-prefs  theme                 │   │
│  │  ... (one per feature)                                   │   │
│  └────────┬──────────────────────────┬───────────────────────┘  │
│           │ HTTP (REST)              │ WebSocket                │
└───────────┼──────────────────────────┼──────────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐   ┌─────────────────────────┐
│  SmartHomeNG REST API │   │  SmartHomeNG WebSocket  │
│  http://host:8383/api │   │  ws://host:2424/adm     │
│                       │   │                         │
│  GET  /api/items/...  │   │  Real-time item values  │
│  GET  /api/logics/    │   │  System load/memory/    │
│  PUT  /api/logics/... │   │  disk/thread charts     │
│  POST /api/auth/...   │   │                         │
└───────────────────────┘   └─────────────────────────┘
```

The legacy `/admin/...` endpoints and the `OlddataService` that used to call them (item tree, item details, value changes, system/pypi info) have been removed entirely — everything now goes through `/api/items/...` (`ItemsApiService`) and `/api/server/...` (`ServerApiService.getSystemStats()`/`getPypiInfo()`).

The port `8383` comes from SmartHomeNG's config and is loaded dynamically at startup — the Angular app doesn't hardcode it.

---

## Part 4 — How the app starts up (the boot sequence)

This is the first thing that happens when you open the browser. Understanding it makes the rest much clearer.

```
BOOT SEQUENCE
─────────────────────────────────────────────────────────────────

1. Browser loads index.html
   └─ index.html loads the compiled JS bundle (all Angular code)

2. main.ts runs (this is the Python equivalent of if __name__ == '__main__')
   ├─ Registers global providers:
   │    JWT handler   (reads token from sessionStorage for auth headers)
   │    Translation   (loads i18n JSON files from /assets/i18n/)
   │    HTTP client   (Angular's equivalent of requests.Session)
   │    PrimeNG theme (UI component library styling)
   ├─ Registers two APP_INITIALIZER factories that run in parallel
   │    before any component renders:
   │
   │    getServerBasicinfo()
   │      └─ GET /api/server/
   │         └─ patches loginRequired, wsHost, language into AppConfigService
   │            └─ AppConfigService.authReady$ emits ← unblocks authGuard
   │
   │    checkForUpdate()
   │      └─ HEAD {baseURI}index.html  (cache: 'no-store')
   │         └─ compares ETag/Last-Modified to localStorage['shng.index_fingerprint']
   │            ├─ unchanged → nothing to do
   │            └─ changed   → window.location.replace(url + '?_cb=timestamp')
   │                           (forces cache-miss reload of new bundle)
   │
   └─ Boots AppComponent as the root component

3. TopNavigationComponent.ngOnInit() runs (in parallel with AppComponent)
   └─ GET /api/server/info
      └─ patches wsPort, tz, branches etc. into AppConfigService
         └─ AppConfigService.serverReady$ emits ← this unblocks routing

4. AppComponent.ngOnInit() strips the _cb cache-busting parameter
   from the URL bar via Location.replaceState() on NavigationEnd.

5. appReadyGuard (on every route) watches AppConfigService.serverReady$
   └─ Until step 3 completes, no route activates
   └─ After it completes, the router renders the target route

6. Normal operation: user navigates, components load, each calls its API service
```

The `AppConfigService` acts like a global config dict shared across the whole app. Step 3 populates it. Everything else reads from it.

---

## Part 5 — File and folder layout

```
src/app/
├── app.component.ts/html      ← Root component (top nav bar, router outlet)
├── app.routes.ts              ← URL → component mapping (like urls.py)
├── main.ts                    ← Entry point (like __main__.py)
│
├── common/                    ← Shared across all features
│   ├── services/              ← Business logic, API calls, shared state
│   │   ├── INFRASTRUCTURE:
│   │   │   app-config.service.ts      global config store
│   │   │   auth.service.ts            login/logout/token
│   │   │   connectivity.service.ts    offline detection
│   │   │   websocket.service.ts       raw WebSocket wrapper
│   │   │   websocket-plugin.service.ts  smarthomeng protocol
│   │   │   log.service.ts             logging wrapper
│   │   │   user-preferences.service.ts localStorage prefs
│   │   │   shared.service.ts          formatting utilities
│   │   │   theme.service.ts           light/dark/system theme state
│   │   │   attribute-catalog.service.ts core+plugin item-attribute catalog
│   │   └── API SERVICES (one per backend domain):
│   │       server-api.service.ts      /api/server/
│   │       items-api.service.ts       /api/items/ (tree, details, value
│   │                                  changes, create/edit/rename/copy/
│   │                                  delete — absorbed the old
│   │                                  olddata.service.ts's item-tree
│   │                                  responsibilities, see below)
│   │       logics-api.service.ts      /api/logics/
│   │       plugins-api.service.ts     /api/plugins/
│   │       scenes-api.service.ts      /api/scenes/
│   │       schedulers-api.service.ts  /api/schedulers/
│   │       logs-api.service.ts        /api/logs/
│   │       loggers-api.service.ts     /api/loggers/
│   │       threads-api.service.ts     /api/threads/
│   │       services-api.service.ts    /api/services/
│   │       config-api.service.ts      /api/config/
│   │       files-api.service.ts       /api/files/
│   │       functions-api.service.ts   /api/functions/
│   │       structs-api.service.ts     /api/items/structs/
│   │
│   │   olddata.service.ts has been REMOVED (legacy /admin/ URLs are gone).
│   │
│   ├── models/                ← TypeScript interfaces (like Python dataclasses)
│   │   server-info.ts, item-tree.ts, plugin-info.ts ...
│   │
│   ├── guards/                ← Route access control
│   │   app-ready.guard.ts     waits for serverReady$
│   │   auth.guard.ts          redirects to /login if not authenticated
│   │
│   │   (a legacy per-feature AuthGuardService class guard was removed from
│   │   every feature's *.routes.ts — appReadyGuard + authGuard on the
│   │   parent route are now the only guard layer, see commit 890f68f)
│   │
│   ├── interceptors/          ← HTTP middleware (like Flask before_request)
│   │   connectivity.interceptor.ts
│   │
│   └── components/            ← Reusable UI building blocks
│       offline-banner/        shown when API unreachable
│       code-editor/           CodeMirror 6 editor wrapper
│       dynamic-field/         renders config params by type
│       file-editor-layout/    shared layout shell around code-editor
│
└── FEATURE FOLDERS (each is one nav section):
    ├── dashboard/             status overview (default landing page)
    ├── system/                overview, config, logging
    ├── items/                 item tree browser, create/edit/rename/delete
    ├── logics/                logics list + editor
    ├── plugins/               plugin list + config
    ├── scenes/                scene list
    ├── schedulers/            scheduler display
    ├── logs/                  log file viewer
    ├── services/              eval/yaml tools, cache check
    ├── top-navigation/        nav bar, Help menu, theme picker (own folder,
    │                          not under common/components/)
    ├── login/                 username/password form
    ├── no-access/             shown when a route is blocked for the user
    └── not-found/             wildcard 404 route target
```

---

## Part 6 — The service layer in detail

Services are plain TypeScript classes with no templates. They are singletons — Angular creates one instance per service and reuses it everywhere. Think of them as module-level objects in Python.

### Infrastructure services

These are not about SmartHomeNG features. They handle cross-cutting concerns.

```
AppConfigService
────────────────
Like a global dict that the whole app reads from.
Populated during boot: loginRequired/wsHost/language come from the
APP_INITIALIZER getServerBasicinfo() call; wsPort/tz/branches come
from TopNavigationComponent's getServerinfo() call.

  _config$ = {
    apiUrl:          'http://192.168.1.10:8383',
    wsHost:          '192.168.1.10',
    wsPort:          2424,
    clientIp:        '192.168.1.50',
    tz:              'Europe/Berlin',
    developerMode:   false,
    defaultLanguage: 'de',
    ...
  }

Components read: appConfig.snapshot.developerMode
Services read:   appConfig.snapshot.apiUrl  (to build request URLs)
Boot waits on:   appConfig.serverReady$     (observable, fires once wsPort arrives)
```

```
AuthService
───────────
Owns the login session.

  State:
    sessionStorage['token']  ← JWT string (browser's localStorage equivalent)
    loggedIn$                ← BehaviorSubject<boolean>

  login(username, password)
    → hashes password with SHA-512 + hardcoded salt
    → POST /api/authenticate/user
    ← JWT token → stored in sessionStorage
    → decodes JWT to get currentUser (username, roles, expiry)

  renewToken()
    → checks if within renewAfter window
    → PUT /api/authenticate/renew
    ← new token, replaces old one silently

  isLoggedIn()
    → checks token expiry timestamp
    → triggers renewal if needed
    → returns true/false
```

```
ConnectivityService
───────────────────
Detects when the SmartHomeNG backend goes offline.

  online$   ← BehaviorSubject<boolean>  (true normally, false when API unreachable)
  retryIn$  ← BehaviorSubject<number>   (countdown seconds until next retry)

  Every 10 seconds: heartbeat GET /api/server/
  On failure:       1.5s debounce → online$ emits false → OfflineBanner appears
  On success:       online$ emits true → OfflineBanner hides
  Retry schedule:   2s → 4s → 8s → 16s → 30s → 30s → ...

  The connectivityInterceptor watches every HTTP response.
  Any successful /api/ response also cancels the offline debounce,
  so normal API calls from components count as heartbeats too.
```

```
WebsocketService  (low level)
─────────────────
Raw WebSocket wrapper. Handles connect, disconnect, reconnect backoff, message queue.
Not used directly by components — WebsocketPluginService sits on top of it.

WebsocketPluginService  (SmartHomeNG protocol)
──────────────────────
Speaks the SmartHomeNG WebSocket protocol. Two functions:

  1. MONITORING  (real-time item values)
     getMonitoredItems(itemList, callback)
       → sends:  {cmd: 'monitor', items: ['my.item.path', ...]}
       ← receives updates as item values change
       → calls callback(item, value) for each update

  2. SERIES  (historical chart data)
     getSeriesLoad(period='24h', count=100)
       → sends:  {cmd: 'series', item: 'env.system.load', ...}
       ← receives: [{time: timestamp, value: float}, ...]
       → puts data into systemloadUpdate$ Subject
       → SystemComponent subscribes to that Subject and redraws chart
```

```
SharedService
─────────────
Pure utility functions. No state, no HTTP. Like a Python utils.py module.

  ageToString(seconds)         → "3 days, 4 hours, 12 minutes"
  displayDateTime(isoString)   → "15.03.2025 10:36:52 CET"
  is_knx_groupaddress(str)     → validates "1/2/3" format
  is_ipv4(str), is_ipv6(str), is_mac(str), is_hostname(str) → validators
  getDescription(dict)         → picks the right language from a {de:..., en:..., fr:...} dict
  setGuiLanguage()             → tells TranslateService to switch language
```

```
ThemeService
────────────
Owns light/dark theme state, applies a 'dark-mode' class to <html>.

  Precedence (highest wins):
    1. Explicit local choice  UserPreferencesService.themePreference
                               ('light' | 'dark' | 'system')
    2. OS preference           prefers-color-scheme, live via matchMedia
    3. Server default          AppConfigService.darkModeDefault
                               (etc/module.yaml admin: dark_mode) — only
                               used when the browser has no
                               prefers-color-scheme support at all

AttributeCatalogService
────────────────────────
Loads the combined core + plugin item-attribute catalog for the item
create/edit attribute autocomplete (items/attribute-browser/).

  Sources: ItemsApiService.getCoreItemAttributes(), PluginsApiService
  Groups suggestions by source ('core' or a plugin name).
```

### API services

One service per SmartHomeNG API domain. Each method is essentially a typed wrapper around one HTTP endpoint.

```
PATTERN (same for all API services):

constructor(private http: HttpClient, private config: AppConfigService) {}

getLogics(): Observable<LogicsResponse> {
  return this.http.get<LogicsResponse>(`${this.config.snapshot.apiUrl}/api/logics/`)
    .pipe(catchError(() => of({})));
}
        │                │
        │                └── if the request fails, emit empty object instead of crashing
        └── returns an Observable (like a Promise / async generator)
            Caller does: this.logicsApi.getLogics().subscribe(data => { this.logics = data })
            or:          const data = await firstValueFrom(this.logicsApi.getLogics())
```

```
API SERVICE MAP

ServerApiService
  getServerBasicinfo()  GET /api/server/          → ServerInfo (boot)
  getServerinfo()       GET /api/server/info       → ServerInfo (full, system page)
  getShngServerStatus() GET /api/server/status/
  getSystemStats()      GET /api/system/info       → host, uptime, version, python
                         (replaces OlddataService.getSysteminfo(), now removed)
  getPypiInfo()         GET /api/server/pypi       → required/installed package status
                         (replaces OlddataService.getPypiinfo(), now removed)
  restartShngServer()   PUT /api/server/restart/
  downloadConfigBackup()GET /api/files/backup/     → Blob (file download)

ItemsApiService  (OlddataService, which used to cover the item tree via
                   legacy /admin/... URLs, has been removed entirely — all
                   of that plus full item CRUD now lives here)
  getItemList()          GET /api/items/list/
  getItemTree()          GET /api/items/tree        → item hierarchy
  getItemDetails(path)   GET /api/items/{path}       → value, age, triggers, eval
  changeItemValue(path)  PUT /api/items/{path}       → {value}
  getCoreItemAttributes()GET /api/items/attributes   → attribute catalog (for
                                                        autocomplete)
  createItem(path, config, persist, filename?, createMissingParents?)
                         POST /api/items/{path}       auto-creates missing
                                                        ancestors if requested
  editItem(path, config) PATCH /api/items/{path}      config is the COMPLETE
                                                        new attribute set
  renameItem(path, newPath, filename?)
                         POST /api/items/{path}/rename a changed parent
                                                        segment = a move
  copyItem(path, newPath, filename?, includeChildren?)
                         POST /api/items/{path}/copy   only persisted items;
                                                        includeChildren
                                                        defaults true
  deleteItem(path, persist?, recursive?)
                         DELETE /api/items/{path}?persist=&recursive=
  getItemReferences(path)GET /api/items/{path}/references
  removeReferences(path) POST /api/items/{path}/remove_references

LogicsApiService
  getGroupsInfo()       GET /api/logics/?infotype=groups
  getLogics()           GET /api/logics/
  getLogic(name)        GET /api/logics/{name}
  getLogicState(name)   GET /api/logics/{name}?infotype=status
  setLogicState(name, action, file)
                        PUT /api/logics/{name}?action={action}
                        actions: trigger enable disable load unload reload delete create
  saveLogicParameters() PUT /api/logics/{name}?action=saveparameters
  saveLogicGroup()      PUT /api/logics/{name}?action=savegroup
  deleteLogicGroup()    PUT /api/logics/{name}?action=deletegroup

PluginsApiService
  getInstalledPlugins() GET /api/plugins/installed/
  getPluginsConfig()    GET /api/plugins/config/
  getPluginsInfo()      GET /api/plugins/info/      → PlugininfoType[]
  getPluginsLogicParameters() GET /api/plugins/logicparams/
  setPluginConfig()     PUT /api/plugin/{section}/
  addPluginConfig()     POST /api/plugin/{section}/
  deletePluginConfig()  DELETE /api/plugin/{section}/
  setPluginState(name, action)
                        PUT /api/plugin/{name}?action={action}
                        actions: trigger enable disable load unload reload delete create

ScenesApiService
  getScenes()           GET /api/scenes/
  reloadScene(name)     PUT /api/scenes/reload/{name}
  reloadScenes()        PUT /api/scenes/reload/all

SchedulersApiService
  getSchedulers()       GET /api/schedulers/

LogsApiService
  getLogs()             GET /api/logs/
  readLogfile(file, chunk) GET /api/logs/{file}?chunk={n}

LoggersApiService
  getLoggers()          GET /api/loggers/
  setLoggerLevel(logger, level)  PUT /api/loggers/{logger}?level={level}
  setHandlers(logger, handlers)  PUT /api/loggers/{logger}?handlers={list}
  addLogger(logger)     POST /api/loggers/{logger}/
  deleteLogger(logger)  DELETE /api/loggers/{logger}/

ServicesApiService
  CheckEvalData(expr)   PUT /api/services/evalcheck/    → {expression, type, result}
  CheckYamlText(text)   PUT /api/services/yamlcheck/
  ConvertToYamlText(text) PUT /api/services/yamlconvert/
  getCacheOrphans()     GET /api/services/cachecheck/
  deleteCacheFile(name) PUT /api/services/cachefile_delete?filename=...

ConfigApiService
  getConfig()           GET /api/config/
  saveConfig(data)      PUT /api/config/core/

FilesApiService
  readFile(type, name)  GET /api/files/{type}/?filename={name}
  saveFile(type, name, content) PUT /api/files/{type}/?filename={name}
  deleteFile(type, name) DELETE /api/files/{type}/?filename={name}
  getfileList(type)     GET /api/files/{type}/
```

---

## Part 7 — The TypeScript models (interfaces)

These are the typed shapes of the data that flows between the API and the components. In Python terms, they are equivalent to dataclasses or Pydantic models, but they only exist at compile time — at runtime they are just plain JavaScript objects. There is no validation at runtime, only type checking when you're writing code.

```
ServerInfo
  default_language    str
  client_ip           str
  tz                  str    ('Europe/Berlin')
  tzname              str    ('CET')
  tznameST            str    ('CET')
  tznameDST           str    ('CEST')
  core_branch         str
  plugins_branch      str
  websocket_port      int
  developer_mode      bool
  click_dropdown_header bool
  itemtree_fullpath   str
  itemtree_searchstart str
  daemon_knx          bool
  daemon_mqtt         bool
  ...

PlugininfoType  (one per installed plugin instance)
  pluginname          str
  configname          str    (instance name in plugin.yaml)
  version             str
  state               str    ('running' | 'stopped' | ...)
  smartplugin         bool
  multiinstance       bool
  instancename        str
  webif_url           str    (link to plugin's own web interface)
  parameters[]        PluginParameter[]
  attributes[]        PluginItemAttribute[]
  metadata            PluginMetadata
  stoppable           bool
  stopped             bool

LogicsinfoType  (one per logic)
  name                str
  pathname            str
  userlogic           bool
  group               str
  enabled             bool
  loaded              bool

LogicsGroupType
  name                str
  title               str
  description         str

SceneInfo
  path                str
  name                str
  value_list[]        str[]
  scene_path[]        str[]
  values[]            SceneValue[]

ItemTreeNode
  path                str
  name                str
  tags[]              str[]
  nodes[]             ItemTreeNode[]   ← recursive tree

ItemDetails         (comes from ItemsApiService.getItemDetails(), GET
                      /api/items/{path} — the old legacy /admin/ endpoint
                      this used to come from has been removed)
  value, last_value, previous_value
  type
  eval
  update_age, change_age
  updated_by[], changed_by[]
  crontab, on_change, on_update
  hysteresis_input, hysteresis_thresholds

ItemAttributeInfo, ItemCopyResult, ItemReference,
ItemRemoveReferencesResult, ItemRenameResult
  Added alongside the item create/edit/rename/copy/delete dialogs —
  request/response shapes for ItemsApiService's attribute-catalog and
  mutation endpoints (item-attribute-info.ts, item-copy-result.ts,
  item-reference.ts, item-remove-references-result.ts, item-rename-result.ts)

ConfigParameter     (used in system config tables)
  name                str
  value               any
  default             any
  type                str
  gui_type            str
  valid_list[]        str[]
  description         str | dict   (dict = {de:..., en:..., fr:...})

AppConfig           (internal, not from API)
  apiUrl, dataUrl, hostIp, wsHost, wsPort
  clientIp, tz, tzname, tznameST, tznameDST
  coreBranch, pluginsBranch
  itemtreeFullpath, itemtreeSearchstart
  developerMode, clickDropdownHeader
  darkModeDefault, resourceGraphPeriod, restartStopsOnly
  startPage           str   ('dashboard' by default — see app.routes.ts's
                             default-route redirect)
  fallbackLanguageOrder[], defaultLanguage
```

---

## Part 8 — The UI components (feature by feature)

Every route in the sidebar corresponds to one feature folder. Here's what each does, what data it fetches, and how it's structured internally.

```
TOP-LEVEL LAYOUT
────────────────
AppComponent
├── TopNavigationComponent   ← the nav bar at the top (always visible)
├── OfflineBannerComponent   ← the red "offline" banner (conditionally visible)
└── <router-outlet>          ← this slot is replaced by the active feature component
```

### Dashboard (/dashboard, the default landing page)

```
DashboardOverviewComponent
│
├── Five status cards, top-to-bottom: status+plugins side by side,
│   schedulers, database (optional), logs (full-width)
│
├── System status — one-shot fetch (ServerApiService.getSystemStats(),
│   ItemsApiService.getItemList(), LogicsApiService.getLogics())
│   hostname, SHNG version/uptime, OS, python+venv, item/logic counts
│
├── Stopped plugins — polled 15s (PluginsApiService)
│   count header (n/total), per-row Start button, links to /plugins
│
├── Overdue schedulers — polled 15s (SchedulersApiService)
│   active cyclic/cron entries past their `next` time by more than a
│   grace window; excludes one-shot 'trigger' group entries on purpose
│
├── Database properties (optional) — one-shot fetch
│   (ServerApiService.getDatabaseInfo()); only rendered when a `database`
│   plugin instance is configured; driver/name/host/status/engine version
│
└── Recent warnings/errors — polled 15s (LogsApiService.getMemlogTail())
    tail of env.core.log's WARNING+ in-memory buffer, full-width row

Polled cards + system-status carry a stale/error indicator (icon+tooltip,
dimmed body, keeps last-known-good data on failure). The database card is
the one exception — it fails closed (stays hidden) instead, since there's
nothing to be "stale" about an unconfigured optional feature.
```

### System (/system)

```
SystemComponent
│
├── Data sources:
│   ├── ServerApiService.getSystemStats()   → uptime, version, host info
│   ├── ServerApiService.getPypiInfo()      → Python package requirements
│   └── WebsocketPluginService series data → chart data
│
├── On init:
│   ├── getSystemStats() → displays: host, uptime, sh_uptime, version, python version
│   │     Also shows frontend build version:
│   │     v1.12.2-<commit>.<branch>   (heads/<branch>)
│   │     Generated at build time by scripts/generate-version.js
│   │     (the build-time filesystem path used to also be shown here;
│   │     removed in commit dec097a as meaningless on a deployed instance)
│   ├── getPypiInfo()   → displays: required packages, installed versions, status
│   └── initCharts()
│       ├── Waits for AppConfigService.serverReady$ (take 1) before connecting
│       │   This ensures wsPort is set before the WebSocket connection attempt.
│       ├── WebsocketPluginService.connect()
│       ├── getSeriesLoad()      → subscribes to systemloadUpdate$
│       ├── getSeriesSystemMemory() → subscribes to systemmemoryUpdate$
│       ├── getSeriesSwap()
│       ├── getSeriesMemory()    (Core memory)
│       ├── getSeriesThreads()
│       └── getSeriesWorkerThreads()
│       └── getSeriesDisk()
│
└── Charts rendered with Chart.js (6 time-series line charts):
    Load | System Memory | Swap | Core Memory | Threads | Disk

System has sub-routes:
├── /system → SystemComponent (overview)
├── /system/config → SystemConfigComponent (smarthome.yaml editor)
└── /system/logging → LoggerListComponent (logger configuration)
```

```
SystemConfigComponent
│
├── Data: ConfigApiService.getConfig()  → structured config sections
├── Displays: collapsible table of config parameters per section
├── Each parameter cell: DynamicFieldComponent renders input by type
│   (text, int, bool, list, ipv4, ipv6, mac, knx_groupaddress, ...)
└── On save: ConfigApiService.saveConfig(data) → PUT /api/config/core/
```

### Items (/items)

```
ItemTreeComponent

The legacy OlddataService (/admin/... URLs) has been removed. All item-tree
data access below goes through ItemsApiService (/api/items/...) instead.
│
├── Data sources:
│   ├── ItemsApiService.getItemTree()           → full item hierarchy
│   ├── ItemsApiService.getItemDetails(path)    → details for selected item
│   └── WebsocketPluginService.getMonitoredItems() → live value updates
│
├── Left panel: PrimeNG Tree component (virtual-scrolled)
│   ├── Hierarchical display of all items
│   ├── filterNodes(query): filters tree by item path or name
│   │   Uses configurable searchstart (e.g., filter only within 'home.' prefix)
│   ├── expandAll() / collapseAll()
│   └── On node click: nodeSelect() → getDetails(path)
│
├── Right panel: item details (shown when item selected)
│   ├── Current value, type, update age, change age
│   ├── Updated by (which logic/plugin last wrote to this item)
│   ├── Changed by
│   ├── Eval expression (if set)
│   ├── On_change / on_update / crontab triggers
│   └── Value editor: updateValue(path, value, type)
│         validates range for numeric/scene types
│         calls ItemsApiService.changeItemValue(path, value)
│
├── Bottom panel: monitored items
│   ├── Waits for AppConfigService.serverReady$ before connecting WebSocket
│   │   (ensures wsPort is available before the subscription is sent)
│   ├── monitorItem(path, true): subscribe to live updates
│   ├── WebSocket pushes new value → updateMonitoredItem() updates display
│   ├── monitorItem(path, false): unsubscribe
│   └── Monitored-item paths persist across a full page reload via
│       SharedService (localStorage key 'shng.items.monitored'); fresh
│       data is re-fetched for the restored placeholders on reconnect
│
└── Create/edit/rename/delete dialogs (item-tree/*-dialog/), all backed by
    ItemsApiService:
    ├── create-item-dialog:  accepts a full multi-level path
    │   (mkdir -p style), type-aware attribute inputs sourced from
    │   AttributeCatalogService via attribute-browser/attribute-value-input
    ├── edit-item-dialog:    edits an item's full attribute set
    ├── rename-item-dialog:  single path field; a changed parent segment
    │   is a move, same endpoint
    └── delete-item-dialog:  looks up references first (getItemReferences),
        offers reference cleanup, requires explicit confirmation for
        recursive deletes of items with sub-items
```

### Logics (/logics)

```
LogicsListComponent
│
├── Data: LogicsApiService.getLogics()
│   Returns: {groups: LogicsGroupType[], logics: LogicsinfoType[], logics_new: [...]}
│
├── Displays three sections:
│   ├── User Logics: grouped by logic.group, collapsible per group
│   ├── System Logics: logics where userlogic=false
│   └── New / Available: logics not yet loaded
│
├── Per-logic actions (buttons per row):
│   trigger / enable / disable / load / unload / reload / delete
│   all call: LogicsApiService.setLogicState(name, action)
│
├── Group management:
│   ├── addGroup(): opens dialog, calls setLogicState(name, 'create', filename)
│   ├── saveGroup(): LogicsApiService.saveLogicGroup()
│   └── deleteGroup(): LogicsApiService.deleteLogicGroup()
│
├── Grouped/flat display toggle persisted in localStorage
│   (preference survives page reloads)
└── Group collapse state persisted across navigation via
    LogicsApiService.groupExpanded BehaviorSubject (in-memory, not localStorage)

LogicsEditComponent  (/logics/{name})
│
├── Data: LogicsApiService.getLogic(name), getLogicState(name)
├── CodeMirror 6 code editor (CodeEditorComponent) for logic Python code
├── FilesApiService for reading/writing the .py and .yaml files
└── saveLogicParameters() → PUT /api/logics/{name}?action=saveparameters
```

### Plugins (/plugins)

```
PluginsComponent
│
├── Data: PluginsApiService.getPluginsInfo()  → PlugininfoType[]
│   Sorted by pluginname + configname
│
├── Displays: accordion/card per plugin instance
│   ├── Header: configname, pluginname, version, state indicator
│   ├── Actions: start / stop / reload  (setPluginState)
│   ├── Parameters tab: plugin configuration parameters
│   ├── Attributes tab: item attributes this plugin provides
│   └── Link button: goToLink(webif_url) → opens plugin's own web UI
│
└── developerMode flag from AppConfigService
    (shows/hides extra controls when developerMode=true in smarthomeng config)

PluginConfigComponent  (/plugins/config/{section})
│
├── Data:
│   ├── PluginsApiService.getPluginsConfig()  → current plugin.yaml sections
│   └── PluginsApiService.getPluginsInfo()    → metadata/parameter definitions
│
├── Form-based config editor (DynamicFieldComponent per parameter)
├── setPluginConfig() → PUT /api/plugin/{section}/
├── addPluginConfig() → POST /api/plugin/{section}/
└── deletePluginConfig() → DELETE /api/plugin/{section}/
```

### Scenes (/scenes)

```
ScenesComponent
│
├── Data: ScenesApiService.getScenes() → SceneInfo[]
├── Displays: scene groups, each with:
│   ├── Scene path
│   ├── Value list (possible scene states)
│   └── Action list per value
└── reloadScene(name) / reloadScenes()
```

### Schedulers (/schedulers)

```
SchedulersComponent
│
├── Data: SchedulersApiService.getSchedulers() → SchedulerInfo[]
├── Displays: scheduled task information in tabs
└── developerMode from AppConfigService
```

### Logs (/logs)

```
LogsComponent
│
├── Data: LogsApiService.getLogs() → available log files
└── For each log file: readLogfile(filename, chunk) → paginated log lines
    ├── Auto-scrolls to bottom on initial load, log/timeframe selection,
    │   and fast-forward (chunk === 0), after Angular's change-detection cycle
    └── Log level filter dropdown includes DEVELOP (numeric 9, below DEBUG=10)

LoggerListComponent  (also accessible from /system/logging)
│
├── Data: LoggersApiService.getLoggers()
│   Returns: {loggers: {}, active_plugins: [], active_logics: [], defined_handlers: []}
│
├── Four logger categories:
│   ├── Plugin loggers   (one per active plugin)
│   ├── Logic loggers    (one per active logic)
│   ├── Item loggers     (for item-level logging)
│   └── Advanced loggers (arbitrary named loggers)
│
├── Per logger:
│   ├── Log level selector  → setLoggerLevel(logger, level)
│   │   Levels: DEVELOP (9) | DEBUG | INFO | WARNING | ERROR | CRITICAL
│   ├── Handler assignment  → setHandlers(logger, handlerList)
│   └── Delete button       → deleteLogger(logger)
│
└── Create logger:
    newPluginLogger() / newLogicLogger() / etc. → populates dropdown
    createLogger(name) → LoggersApiService.addLogger(name)
    All add-item dialogs support Enter to confirm and Escape to cancel
```

### Services (/services)

```
ServicesComponent
│
├── Eval checker:
│   ├── Input: expression string
│   └── ServicesApiService.CheckEvalData(expr)
│       → PUT /api/services/evalcheck/
│       ← {expression, type, result}
│
├── YAML checker:
│   ├── Input: YAML text
│   └── ServicesApiService.CheckYamlText(text)
│       → PUT /api/services/yamlcheck/
│
├── YAML converter:
│   ├── Input: old-style config text
│   └── ServicesApiService.ConvertToYamlText(text)
│       → PUT /api/services/yamlconvert/
│
└── Cache checker:
    ├── ServicesApiService.getCacheOrphans()
    │   → GET /api/services/cachecheck/ ← orphaned cache files
    └── deleteCacheFile(filename)
        → PUT /api/services/cachefile_delete?filename=...
```

---

## Part 9 — How data flows through one complete interaction

Let's trace exactly what happens when you navigate to `/logics` and click "Trigger" on a logic.

```
USER ACTION: navigate to /logics
────────────────────────────────────────────────────────────────────

1. Angular Router sees URL change to /logics
   └─ appReadyGuard runs:
      └─ AppConfigService.serverReady$ already emitted? → yes → proceed

2. Router activates LogicsListComponent
   └─ Angular creates new instance, injects: LogicsApiService, Router

3. ngOnInit() runs  (Angular calls this once on component creation)
   └─ this.getLogics()

4. getLogics():
   └─ this.logicsApi.getLogics()
      └─ HTTP GET http://host:8383/api/logics/
         │
         ← Response JSON:
            {
              groups: [{name: 'group1', title: 'My Group', description: '...'}],
              logics: [
                {name: 'my_logic', group: 'group1', enabled: true, loaded: true, ...},
                ...
              ],
              logics_new: ['available_but_not_loaded']
            }

5. .subscribe(data => { ... })
   └─ this.userLogics = data.logics.filter(l => l.userlogic)
   └─ this.systemLogics = data.logics.filter(l => !l.userlogic)
   └─ this.groupList = build grouped structure from data.groups + userLogics
   └─ Angular's change detection sees new data → re-renders the template

6. Template renders:
   <div *ngFor="let group of groupList">      ← loop over groups
     <div *ngFor="let logic of group.logics"> ← loop over logics in group
       <button (click)="triggerLogic(logic.name)">Trigger</button>
     </div>
   </div>


USER ACTION: click "Trigger" on 'my_logic'
────────────────────────────────────────────────────────────────────

1. (click)="triggerLogic('my_logic')" fires

2. triggerLogic(name):
   └─ this.logicsApi.setLogicState('my_logic', 'trigger')
      └─ HTTP PUT http://host:8383/api/logics/my_logic?action=trigger
         │
         ← Response: {result: 'ok', description: 'triggered'}

3. .subscribe(result => {
     if (result.result === 'ok') {
       this.getLogics()   ← refresh the list
     }
   })
```

---

## Part 10 — Observables (the async pattern at the HTTP/service boundary)

Python has `async/await` and generators. Angular uses **RxJS Observables** heavily at the service layer — every API service method below still returns one. You need a mental model for this.

**Note on components specifically**: as of a mid-2026 migration, component-level state is now overwhelmingly held in **Signals** (`signal()`, `computed()`, `linkedSignal()`, and `toSignal()` wrapping an Observable) rather than plain fields set inside `.subscribe()` callbacks; the app is also now zoneless (no `zone.js`). The `Observable`/`BehaviorSubject` material below still fully applies at the service layer. The pattern below (`getLogics().subscribe(data => process(data))`) is now more typical of how a *service* consumes another service's Observable, or how `toSignal()` is fed, than of how a component itself holds state.

```
PYTHON async/await analogy:

# Python
async def get_logics():
    response = await http_client.get('/api/logics/')
    return response.json()

data = await get_logics()
process(data)

# Angular/RxJS equivalent
getLogics(): Observable<LogicsResponse> {
  return this.http.get<LogicsResponse>('/api/logics/')
}

this.getLogics().subscribe(data => {
  process(data)
})
```

The key difference: an Observable is **lazy** — nothing happens until you call `.subscribe()`. It's more like a generator than a coroutine. The important operators you'll see:

```
RXJS OPERATORS (used in this app)

.pipe(
  catchError(() => of({}))   ← if error, emit empty object (like try/except)
)

.pipe(
  takeUntilDestroyed(this.destroyRef)  ← cancel when component is destroyed
)                                         like cancelling an asyncio task

firstValueFrom(observable$)  ← await the first value and return it
                                most similar to Python's await

BehaviorSubject<T>(initialValue)
  ← holds a current value AND emits it to new subscribers immediately
  ← like threading.Event but with a value
  ← .next(newValue) to push a new value
  ← .getValue() to read current value synchronously

Subject<T>
  ← like BehaviorSubject but no initial value; late subscribers miss previous events
```

The `$` suffix on variable names is a convention meaning "this is an Observable". So `serverReady$`, `online$`, `loggedIn$` are all observables.

---

## Part 11 — Authentication flow

```
FIRST VISIT (not logged in)
───────────────────────────────────────────────────────────────

Browser → /                  ← root URL
Router  → redirect to /system
appReadyGuard → wait for serverReady$ → ok
AuthGuardService.canActivate() → isLoggedIn()? → NO
  └─ Router.navigate(['/login'], {queryParams: {returnUrl: '/system'}})

LoginComponent renders login form

User types credentials, clicks Login:
  └─ AuthService.login({username: 'admin', password: 'xxx'})
     ├─ hashes: SHA512('shNG0160$' + 'xxx')  ← client-side, fixed salt
     └─ POST /api/authenticate/user
        body: {username: 'admin', password: '<hash>'}
        ← JWT token: 'eyJhbGc...'

     AuthService stores token:
       sessionStorage['token'] = 'eyJhbGc...'
       this._token = 'eyJhbGc...'
       this.loggedIn$.next(true)

     Decodes JWT payload (no verification, client-side only):
       this.currentUser = {username: 'admin', exp: 1234567890, ...}

     Router.navigate([returnUrl])  ← back to /system


SUBSEQUENT API CALLS
──────────────────────────────────────────────────────────────

@auth0/angular-jwt intercepts every HTTP request:
  ├─ reads token from AuthService.getToken()
  └─ adds header: Authorization: Bearer eyJhbGc...

SmartHomeNG REST API validates the JWT on every request.


TOKEN RENEWAL
──────────────────────────────────────────────────────────────

AuthService.renewToken() is called automatically when the token
is past its renewAfter threshold (some time before actual expiry).
  └─ PUT /api/authenticate/renew
     ← new JWT token
     → overwrites sessionStorage['token']
```

---

## Part 12 — Real-time data (WebSocket)

The charts and item monitoring don't poll the REST API. They use a persistent WebSocket connection.

```
WebSocket lifecycle:
─────────────────────────────────────────────────────────────────

SystemComponent.ngOnInit() and ItemTreeComponent.ngOnInit():
  └─ Both subscribe to AppConfigService.serverReady$ (take 1)
     before connecting.  This ensures wsPort is populated from
     /api/server/info before the WebSocket URL is built.
     Without this, the connection attempt fires before the port
     is known, causing empty charts on first production load.
  └─ websocketPlugin.connect()
     └─ WebsocketService.connect('ws://host:2424/adm')
        └─ new WebSocket(url)
           └─ on open: send identity message
              {cmd: 'identity', sw: 'shngAdmin', ver: '1.0.0', browser: 'Chrome...'}

SystemComponent requests chart data:
  └─ websocketPlugin.getSeriesLoad('24h', 100)
     └─ sends: {cmd: 'series', item: 'env.system.load', ...}

SmartHomeNG sends back:
  ← {cmd: 'series', item: 'env.system.load', series: [{t:..., v:...}, ...]}

WebsocketPluginService receives message:
  └─ updateSeries() → this.systemloadUpdate$.next(seriesData)

SystemComponent is subscribed:
  └─ this.websocketPlugin.systemloadUpdate$.subscribe(data => {
       this.loadChartData = convertToChartFormat(data)
       // Angular re-renders the chart
     })


Item monitoring (ItemTreeComponent):
─────────────────────────────────────────────────────────────────

User clicks "Monitor" button for item 'home.livingroom.temp':
  └─ websocketPlugin.getMonitoredItems(['home.livingroom.temp'], callback)
     └─ sends: {cmd: 'monitor', items: ['home.livingroom.temp']}

SmartHomeNG pushes updates whenever the item changes:
  ← {cmd: 'item', items: [['home.livingroom.temp', 21.5]]}

WebsocketPluginService receives, calls monitorCallbackFunction:
  └─ callback('home.livingroom.temp', 21.5)
     └─ ItemTreeComponent.updateMonitoredItem(path, value) → re-renders

WebSocket reconnect:
  If disconnected: WebsocketService retries with backoff (same intervals as HTTP)
  On reconnect: re-sends all pending messages from messageQueue
```

---

## Part 13 — The UI component library (PrimeNG)

The app uses **PrimeNG 20**, a large library of pre-built Angular UI components. You'll see its names throughout the templates. Quick reference:

```
PrimeNG COMPONENT        WHAT IT RENDERS
─────────────────────    ──────────────────────────────────
p-table                  Data table with sort/filter/pagination
p-tree                   Hierarchical tree (used for item tree)
p-accordion              Collapsible sections
p-dialog                 Modal dialog
p-button                 Styled button
p-dropdown               Select/dropdown
p-inputText              Text input
p-inputSwitch            Toggle switch
p-tabs / p-tabView       Tab container
p-toast                  Notification/toast messages
p-toolbar                Button toolbar
p-card                   Card/panel container
p-tag                    Colored label/badge
```

You don't need to dig into PrimeNG source. If you see `<p-something>` in a template, it's a PrimeNG widget.

---

## Part 14 — Internationalization (i18n)

The app supports English, German, and French.

```
Translation files:    src/assets/i18n/en.json, de.json, fr.json

In templates:
  {{ 'LOGICS.TRIGGER' | translate }}
     │                   │
     │                   └── Angular pipe: transforms the value
     └── translation key

In TypeScript:
  this.translate.instant('SYSTEM.RESTART_CONFIRM')

Language selection:
  UserPreferencesService.language  ← stored in localStorage
  SharedService.setGuiLanguage()   ← calls TranslateService.use('de')
  Fallback order from server config: e.g., ['de', 'en', 'fr']
    → SharedService.getDescription({de: '...', en: '...'})
      picks language[0], falls back to language[1] if missing
```

---

## Part 15 — Complete dependency map

```
                        AppConfigService
                        ┌───────────────────────────────────────────┐
                        │  Single global config store               │
                        │  All services and components read from it │
                        └───────────┬───────────────────────────────┘
                                    │ populated by
                                    ▼
                         ServerApiService.getServerBasicinfo()
                         (APP_INITIALIZER in main.ts — runs before any component)


INFRASTRUCTURE SERVICES (no feature, pure plumbing)

  AuthService ────────────────────────────────────► sessionStorage
       │
       ▼ token
  @auth0/angular-jwt (HTTP interceptor)
       │
       ▼ adds Authorization header to every request
  HttpClient


  ConnectivityService ◄────── connectivityInterceptor (watches /api/ responses)
       │
       ▼ online$
  OfflineBannerComponent


  WebsocketService (raw)
       │ wrapped by
  WebsocketPluginService ──► systemloadUpdate$, monitorCallback, ...
       │                          │
       ▼                          ▼
  SmartHomeNG WebSocket    SystemComponent, ItemTreeComponent


FEATURE COMPONENTS AND THEIR SERVICE DEPENDENCIES

  DashboardOverviewComponent
    ├── ServerApiService        (system stats, pypi, database info)
    ├── ItemsApiService         (item count)
    ├── LogicsApiService        (logic count)
    ├── PluginsApiService       (stopped-plugin list, start action)
    ├── SchedulersApiService    (overdue-scheduler detection)
    └── LogsApiService          (recent warnings/errors tail)

  SystemComponent
    ├── ServerApiService        (system stats, pypi info, restart)
    ├── WebsocketPluginService  (chart series data)
    └── SharedService           (date/time formatting)

  SystemConfigComponent
    └── ConfigApiService        (get/save config)

  ItemTreeComponent
    ├── ItemsApiService         (item tree, item details, value change,
    │                            create/edit/rename/copy/delete, references)
    ├── AttributeCatalogService (attribute autocomplete for create/edit)
    ├── WebsocketPluginService  (monitored item values)
    ├── AppConfigService        (searchstart config)
    └── SharedService           (validators, formatters, monitored-item
                                  persistence)

  LogicsListComponent
    ├── LogicsApiService        (list, state, groups)
    └── Router                  (navigate to edit)

  LogicsEditComponent
    ├── LogicsApiService        (get, save parameters)
    └── FilesApiService         (read/write .py and .yaml files)

  PluginsComponent
    ├── PluginsApiService       (info, state)
    └── AppConfigService        (developerMode)

  PluginConfigComponent
    └── PluginsApiService       (config CRUD)

  ScenesComponent
    └── ScenesApiService

  SchedulersComponent
    └── SchedulersApiService

  LoggerListComponent
    └── LoggersApiService

  LogsComponent
    └── LogsApiService

  ServicesComponent
    └── ServicesApiService      (eval, yaml, cache)

  LoginComponent
    └── AuthService

  TopNavigationComponent
    ├── ServerApiService        (full server info)
    ├── WebsocketPluginService  (connect on startup)
    ├── AuthService             (loggedIn$, for the login link)
    └── ThemeService            (Light/Dark/Follow-System picker)
```

---

## Part 16 — One-line summary of every file

```
INFRASTRUCTURE
  main.ts                      app entry point, registers all global providers + 2 APP_INITIALIZERs;
                                provideZonelessChangeDetection() — no zone.js
  app.component.ts             root shell: strips _cb param on NavigationEnd, renders nav + router slot
  app.routes.ts                URL→component map; '' redirects to the configurable startPage
                                (default 'dashboard'); all feature routes guarded by
                                appReadyGuard + authGuard
  scripts/generate-version.js  run at build time; writes git-version.auto.ts with commit hash + branch
                                (no longer includes the build machine's filesystem path — see dec097a)

  app-config.service.ts        global config dict (wsPort, apiUrl, tz, startPage, etc.)
  auth.service.ts              login/logout/token renewal
  auth.guard.ts                the only route guard checking loginRequired/authReady$
                                (a redundant per-feature AuthGuardService class guard —
                                previously auth-guard.service.ts — was removed, commit 890f68f)
  connectivity.service.ts      heartbeat, offline detection, retry backoff
  connectivity.interceptor.ts  HTTP middleware: cancels offline debounce on API success
  websocket.service.ts         raw WebSocket with reconnect and message queue
  websocket-plugin.service.ts  SmartHomeNG protocol: item monitoring + chart series
  log.service.ts               console.log wrapper (suppressed in production)
  shared.service.ts            formatting/validation utilities + monitored-item localStorage persistence
  user-preferences.service.ts  localStorage wrapper for language + theme preference
  theme.service.ts             light/dark/system theme state, applies .dark-mode to <html>
  attribute-catalog.service.ts core+plugin item-attribute catalog for autocomplete
  app-ready.guard.ts           blocks routes until serverReady$ fires

API SERVICES
  server-api.service.ts        /api/server/ + /api/system/ — server info, system/pypi/database
                                stats, restart, stale-frontend check
  items-api.service.ts         /api/items/ — tree, details, value changes, create/edit/rename/
                                copy/delete, references (absorbed the removed olddata.service.ts)
  logics-api.service.ts        /api/logics/ — logic CRUD and state control
  plugins-api.service.ts       /api/plugins/ and /api/plugin/ — plugin CRUD and state
  scenes-api.service.ts        /api/scenes/ — scene list and reload
  schedulers-api.service.ts    /api/schedulers/ — scheduler info
  logs-api.service.ts          /api/logs/ — log file list, chunked reading, memlog tail
  loggers-api.service.ts       /api/loggers/ — logger CRUD, levels, handlers
  threads-api.service.ts       /api/threads/ — thread info
  services-api.service.ts      /api/services/ — eval/yaml tools, cache management
  config-api.service.ts        /api/config/ — smarthomeng core config
  files-api.service.ts         /api/files/ — generic file read/write/delete
  functions-api.service.ts     /api/functions/ — function reload
  structs-api.service.ts       /api/items/structs/ — struct definitions

  olddata.service.ts has been REMOVED — its /admin/... responsibilities now live in
  items-api.service.ts and server-api.service.ts (see above).

MODELS (data shapes)
  server-info.ts               ServerInfo (server config response shape)
  item-tree.ts                 ItemTree, ItemTreeNode (recursive)
  item-details.ts              ItemDetails (value, age, triggers, eval)
  item-attribute-info.ts       ItemAttributeInfo (attribute catalog entry)
  item-copy-result.ts, item-reference.ts, item-remove-references-result.ts,
  item-rename-result.ts        response shapes for the item copy/rename/reference endpoints
  plugin-info.ts                PlugininfoType, PluginParameter, PluginMetadata
  logics-info.ts               LogicsinfoType, LogicsGroupType
  logics-watch-item.ts         watch_item shape used by logics-info
  scene-info.ts                SceneInfo, SceneValue
  scheduler-info.ts            SchedulerInfo
  loggers-info.ts              LoggersType (loggers, handlers, active_*)
  logfiles-info.ts             LogsType
  memlog-entry.ts              MemlogEntry (in-memory warning/error log tail, dashboard)
  system-info.ts                SystemInfo (from ServerApiService.getSystemStats())
  pypi-info.ts                  PypiInfo (from ServerApiService.getPypiInfo())
  database-info.ts             DatabaseInfo (optional database-plugin connection properties)
  interfaces.ts                TableColumn, ConfigParameter, generic TreeNode

FEATURE COMPONENTS
  dashboard/dashboard-overview/ default landing page: 5 status cards (system, plugins,
                                schedulers, optional database, recent warnings/errors)
  system/system-overview/      uptime, pypi status, real-time charts
  system/system-config/        smarthomeng.yaml config editor table
  items/item-tree/             hierarchical item browser with live value monitoring +
                                create/edit/rename/delete dialogs
  items/attribute-browser/, items/attribute-value-input/
                                type-aware attribute autocomplete/input for item dialogs
  logics/logics-list/          logic list with group management and state control
  logics/logics-edit/          CodeMirror 6 editor for logic code + parameter editor
  logics/logics-groups/        group creation/editing dialog
  plugins/plugin-list/         plugin instance list with start/stop (Load/Unload/Reload
                                moved to plugin-config, see plugins/config/)
  plugins/config/              plugin.yaml config editor
  scenes/scene-list/           scene group and value display
  schedulers/schedulers/       scheduler info display
  logs/logger-list/            logger creation, level and handler assignment
  logs/log-viewer/             log file display with chunked loading
  services/services/           eval checker, yaml tools, cache inspector
  login/                       username/password form → AuthService.login()
  top-navigation/              own top-level folder (not under common/components/):
                                nav bar, language selector, Help menu, theme picker, logout
  no-access/                   shown when a route is blocked for the current user
  not-found/                   wildcard ('**') 404 route target

SHARED COMPONENTS
  offline-banner/              red "offline" bar, retry countdown + button
  code-editor/                 CodeMirror 6 editor wrapper (used in logics-edit, YAML checker, etc.)
  file-editor-layout/          shared layout shell around code-editor
  dynamic-field/               renders a ConfigParameter as the right input type
```
