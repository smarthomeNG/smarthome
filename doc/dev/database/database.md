# SmartHomeNG Database Plugin — Developer Documentation

This document describes the internal design of the `database` plugin and the connection/locking
primitive it builds on (`lib/db.py`'s `Database` class). It is aimed at Python developers who are
already familiar with SmartHomeNG basics.

> **Status (verified 2026-09-07 against `plugins/database/` and `lib/db.py` on
> `database-transaction-refactor` / `db-transaction-refactor`):** Describes the system as it exists
> today. The plugin went through a module split (`utils.py`/`buffer.py`/`store.py` extracted from
> `__init__.py`) and, separately, a locking rewrite that replaced hand-rolled
> `lock()`/`cursor()`/`commit()`/`rollback()`/`release()` sequences throughout both `lib/db.py` and
> the plugin with a single `transaction()` context manager. Both are complete and are described
> below as the current design, not as proposals. Since the previous verification pass, PostgreSQL
> support (optionally with the TimescaleDB extension) was added as a third backend alongside
> SQLite3 and MySQL/MariaDB — covered in §8. For the history of *why* — the incidents that
> motivated the locking rewrite, and the two audit passes that followed it — see this project's
> commit history; this document does not attempt to be a changelog.

---

## 1. Overview

The `database` plugin persists item values to a relational database via `lib/db.py`. Three backends
are supported directly: SQLite3, MySQL/MariaDB (`pymysql`), and PostgreSQL (`psycopg2`/`psycopg`),
optionally extended with TimescaleDB (see §8) — other DB-API 2 drivers work if `lib/db.py`'s
type-conversion tables are extended for them. The `driver` parameter also accepts friendly database
names (`mysql`/`mariadb`, `postgres`/`postgresql`/`timescale`/`timescaledb`) resolved to the real
module name at startup — see §8. Its distinguishing feature compared to a plain event log is that
**every row records not just a value but how long that value was active** — the `duration` column.
This makes it straightforward to compute time-weighted averages, cumulative energy totals, and
similar analytics directly in SQL.

Five concepts are central to understanding the plugin:

| Concept | Description |
|---|---|
| **log table** | The historical record. One row per value-change event, with `time`, `duration`, and the value itself. |
| **item table** | A single-row-per-item snapshot of the *latest* value. Used for fast lookups without scanning the log. |
| **buffer** | An in-memory dict (keyed by item id) that accumulates incoming changes between database writes. |
| **dump cycle** | A scheduler job that runs every `cycle` seconds (default 60) and flushes the buffer to SQL in one transaction. |
| **transaction()** | `lib/db.py`'s locking primitive — acquires the connection's lock, yields a cursor, commits on success or rolls back on exception, always releases. Almost every multi-statement DB access in the plugin goes through it. |

---

## 2. Architecture

```
plugins/database/
├── __init__.py       # Database(SmartPlugin) — plugin lifecycle, public API,
│                     #   legacy CRUD delegates, one-line delegates to every
│                     #   module below
├── utils.py          # Pure functions, no side effects, no DB connection needed
├── buffer.py         # BufferManager — owns the in-memory buffer dict + its lock
├── store.py          # ItemStore + LogStore — SQL CRUD against {item}/{log}
├── maxage.py         # MaxageResolver — per-item database_maxage_action/_interval
│                     #   resolution, shared by maintenance.py/query.py/timescale.py
├── maintenance.py    # MaintenanceManager — age-based cleanup (delete/compact,
│                     #   scheduled) and orphan item/log handling
├── query.py          # QueryEngine — on-demand analytics (item.series/item.db)
│                     #   and native-cagg query routing
├── timescale.py      # TimescaleManager — driver-alias resolution and every
│                     #   PostgreSQL/TimescaleDB feature-activation/status method
├── constants.py      # BufferEntry namedtuple, QUALITY_VALID/QUALITY_NO_DATA, column indices
└── webif/            # Web interface (item/orphan browsing, manual actions)
```

![Architecture](img/architecture.svg)

`__init__.py` was, until recently, ~4000 lines — `_series()`/`_single()` (analytics),
`remove_older_than_maxage()`/`build_orphanlist()` (maintenance), and the TimescaleDB feature set
(§8) all lived directly on `Database`. All four moved out into the dedicated modules listed above,
following the same pattern `buffer.py`/`store.py` already established: `Database` keeps a one-line
delegate for every moved method (`insertLog`, `readItem`, `_compact_maxage`, `timescale_status`,
...), so the public API used by items, the web interface, and user automations is unchanged by any
of this — and so is anything (mainly the test suite) that reaches into a "private" method directly.
Each new module takes a back-reference to the `Database` instance rather than individual
parameters, for the same reason a full dependency-injection split wasn't worth it: the goal here is
file-size/navigability, not decoupling. `__init__.py` is now ~2300 lines.

**`utils.py`** — pure functions, importable without any database connection:

- `encode_value(item_type, value) -> dict` — maps a Python value to the three SQL columns (`val_str`/`val_num`/`val_bool`).
- `decode_value(item_type, val_str, val_num, val_bool) -> value` — reverse.
- `to_timestamp(dt) -> int` / `from_timestamp(ts, tzinfo=None) -> datetime` — ms-since-epoch conversion.
- `apply_table_names(query, table_names) -> str` — substitutes `{item}`/`{log}`/`{item_columns}`/`{log_columns}` placeholders.
- `build_where_clause(item_id, *, time=None, time_start=None, ..., exclude_gaps=False) -> (sql, params)` — builds a parameterised `WHERE` clause. `exclude_gaps` is opt-in — see §6.

**`buffer.py`** — `BufferManager`:

- Owns `self._buffer: dict` and its lock; `register()`/`deregister()` manage item lifecycle.
- `push(item, entry)` — appends a `BufferEntry`.
- `close_open(item, end_ts)` / `set_last_duration(item, duration)` — back-fill the duration of the last open (`duration=None`) entry, per item (there is no bulk "close everything" call — see §4).
- `push_invalid(item, start_ts)` — opens a `QUALITY_NO_DATA` gap entry (§6).
- `pop_all(item)` / `restore(item, entries)` — drain an item's pending writes for `_dump()`, and put them back if the write fails.

**`store.py`** — `ItemStore` and `LogStore`, both stateless wrappers around a `lib.db.Database`
connection and a `table_names` dict, no plugin business logic:

- `ItemStore`: `insert`, `update`, `find`, `find_all`, `count`, `delete`.
- `LogStore`: `insert`, `update`, `upsert`, `find`, `find_range`, `count`, `count_all`,
  `delete_range`, `oldest_time`, `latest_time`, `edge_value`, `aggregate`.

**`maxage.py`** — `MaxageResolver` (`self._maxage`): `action_for(item)`/`interval_seconds_for(item)`
(database_maxage_action/database_maxage_interval, falling back to the plugin-level defaults) and
`native_relevant_items()`. Small and shared by three other modules on purpose — see §7's action
table and §8's native-aggregation item selection.

**`maintenance.py`** — `MaintenanceManager` (`self._maintenance`): `remove_older_than_maxage()`/
`compact_maxage()` (§7's delete-vs-compact scheduler) and `build_orphanlist()`/
`remove_orphan_items()`/`reassign_orphaned_id()`/`cleanup()` (orphan item/log handling).

**`query.py`** — `QueryEngine` (`self._query_engine` — named to avoid colliding with the
pre-existing `Database._query()` execute/fetchone/fetchall helper): `series()`/`single()` (bound
onto `item.series`/`item.db` in `parse_item()`) plus every `native_cagg_*()` routing method — see
§8's merge/exclusive/additive distinction between `_series()`, `_single()`, and `readLogCount()`.

**`timescale.py`** — `TimescaleManager` (`self._timescale`): `resolve_driver_alias()`/
`resolve_postgres_driver_alias()` (called first in `__init__()`, before any other plugin state
exists — see §8's driver resolution) and every hypertable/compression/native-aggregation/
native-retention/status method. All PostgreSQL/psycopg-specific; every method is a no-op or returns
early on every other driver.

**`__init__.py`** — `Database(SmartPlugin)`:

- Creates and wires `BufferManager`/`ItemStore`/`LogStore`/`MaxageResolver`/`MaintenanceManager`/
  `QueryEngine`/`TimescaleManager`, plus two independent `lib.db.Database` connections: `self._db`
  (regular reads/writes) and `self._db_maint` (maintenance — orphan cleanup,
  `remove_older_than_maxage()`). The two connections are kept separate so a long-running
  maintenance transaction never blocks ordinary item logging, and vice versa.
- Implements `run`/`stop`/`parse_item`/`update_item`/`_dump`/`_initialize_db`/`id` — plugin
  lifecycle and buffer-flush machinery too entangled with each other to split out cleanly — and
  re-exports every legacy method name (`insertLog`, `readItem`, `insertItem`, ...) as a one-line
  delegate to the store objects, on top of the one-line delegates to the four modules above.

---

## 3. Locking and Transactions

`lib.db.Database` (`lib/db.py`) is a thin wrapper around a DB-API 2 connection, shared by every
plugin that needs SQL access. Its central primitive is `transaction()`:

```python
with self._db.transaction() as cur:
    self._log_store.insert(item_id, entry, item_type, now_ms, cur=cur)
    self._item_store.update(item_id, entry, cur=cur)
```

`transaction()` acquires the connection's lock, yields a cursor, commits on clean exit, rolls back
on any exception (re-raising it), and always releases the lock — regardless of which path was
taken. This replaced a large number of hand-rolled `lock()`/`cursor()`/`commit()`/`rollback()`/
`release()` sequences scattered across the plugin, several of which had real gaps: statements
running with no lock at all, writes left uncommitted on the `cur=None` path, and failures that
didn't roll back and so left a corrupted connection for the next caller.

**Two rules that matter for anyone adding a new call site:**

- `self._fdb_lock` is a plain, non-reentrant `threading.Lock`, held for the *entire* `transaction()`
  block. It cannot be nested, and nothing invoked from inside the block may acquire the lock again
  itself — a `cur=None` call to `execute()`/`fetchone()`/`fetchall()`, or `connect()`/`close()`/
  `verify()`/`setup()`, all hit the same lock. `lock()` detects same-thread re-entry and raises
  `RuntimeError` immediately instead of deadlocking. Always pass the yielded `cur` through
  explicitly to every statement run inside the block.
- `cur=None` means "acquire your own lock and commit as a self-contained unit" (typically via an
  internal `transaction()` call). An explicit `cur` means "the caller already holds the lock and
  owns the commit/rollback decision" — the callee must never call `commit()`/`rollback()` itself.
  These are the only two supported shapes; a caller-selectable "commit anyway" flag independent of
  whether `cur` was passed is exactly the pattern that caused several of the bugs `transaction()`
  replaced, and should not be reintroduced.

**Self-healing reconnect.** Every entry point that touches the database (`id()`, `_dump()`,
`_query()`, `run()`) calls `_initialize_db()` first, which attempts to (re)connect if not already
connected, throttled to one real attempt per 20 seconds. None of them crash or exit the plugin on
failure — they log and return a "no data"/`False` result, and the *next* call retries. `verify()`
additionally does an active connectivity probe with its own short timeout, used before trusting an
already-`connected()` socket that may have gone stale server-side.

One consequence worth knowing: `build_orphanlist()` (used by the web interface's orphan list and by
`remove_orphan_items()`) is only ever *triggered* once at startup (`run()`) and, if that attempt
fails because the DB wasn't connected yet, once more per `_dump()` cycle until it succeeds —
piggybacked on the cycle that's already running rather than a separate retry loop.
`self._orphanlist_built` tracks whether it has ever completed successfully; an empty
`self.orphanlist` alone does not mean "confirmed no orphans" — it can also mean "haven't been able
to check yet".

---

## 4. Data Flow

This section traces what happens when an item value changes.

![Data flow](img/data_flow.svg)

1. **Item changes.** SmartHomeNG calls `Database.update_item(item, caller, source, dest)`. The
   method checks whether the item has the `database` attribute and bails out early if not.

2. **Duration is calculated retroactively.** The database does not know in advance how long a value
   will be active. When a *new* value arrives, the plugin looks up the previous buffer entry for
   this item and computes `duration = now_ms - prev_entry.time_ms`, writing that duration back into
   the previous (now-closed) entry. A duration that comes out negative (system clock jumped
   backward — NTP correction, DST, VM resume) is clamped to `0` and logged, rather than corrupting
   time-weighted aggregates with a negative value.

3. **New buffer entry appended**, with `duration=None` — "this value is still active, duration not
   yet known": `BufferEntry(time=now_ms, duration=None, value=value, quality=QUALITY_VALID)`.

4. **Dump cycle.** Every `cycle` seconds (default 60) the scheduler calls `Database._dump()`, which:

   a. Calls `_initialize_db()` — self-healing, see §3. Returns immediately if that fails; buffered
      entries stay buffered for the next cycle.

   b. If `self._orphanlist_built` is still `False`, retries `build_orphanlist()` (see §3).

   c. For each item with pending entries, calls `BufferManager.pop_all(item)` to drain them
      atomically, then `LogStore.insert`/`LogStore.update` inside one `self._db.transaction()`
      block per item.

   d. Calls `ItemStore.update` to refresh the latest-value snapshot.

   e. If a write fails, the popped entries are restored to the buffer (`BufferManager.restore()`)
      for the next cycle rather than being dropped.

There is no bulk "close every open entry" pass — the still-open (`duration=None`) most recent entry
for an item is closed the next time that specific item changes, or at `finalize=True` (plugin
shutdown), via `BufferManager.close_open()`/`set_last_duration()` operating per item.

---

## 5. Database Schema

The plugin manages two tables, named via `db_prefix` (default `log` and `item`), created and
migrated by `lib.db.Database.setup()` against a versioned `_setup` dict — each version is one
forward-only DDL statement, applied in ascending numeric order to any install below that version on
every startup. Current version: **11**.

### `{prefix}item` — latest-value snapshot

```sql
CREATE TABLE {item} (
    id       INTEGER PRIMARY KEY [AUTO_INCREMENT on MySQL/MariaDB],  -- v2, retrofitted v8
    name     VARCHAR(1024),   -- VARCHAR(255) on sqlite (no length ever enforced there); v9-11 on MySQL/MariaDB
    time     BIGINT,          -- ms since epoch of last change
    val_str  TEXT,
    val_num  REAL,
    val_bool BOOLEAN,
    changed  BIGINT           -- ms since epoch of last write
);
CREATE UNIQUE INDEX {item}_id   ON {item} (id);
CREATE INDEX        {item}_name ON {item} (name(191) on MySQL/MariaDB, full column on sqlite);
```

One row per tracked item. `id` is database-generated (bare `INTEGER PRIMARY KEY` autoincrements
implicitly on sqlite via `rowid`; MySQL/MariaDB need the explicit `AUTO_INCREMENT`, added for fresh
installs in schema v2/v8 and retrofitted onto pre-existing installs by v8's `ALTER TABLE`).
`ItemStore.insert()` reads the new id back via the cursor's own `lastrowid`, not a follow-up query —
avoids the `MAX(id)+1` race a prior implementation had.

`name` is `varchar(255)` in the original schema and was never widened for MySQL/MariaDB until v9-11,
which is why the migration is a driver-gated no-op on sqlite and a real `ALTER TABLE` + index
rebuild elsewhere: MySQL/MariaDB reject item paths over 255 characters outright under strict SQL
mode, sqlite never enforced the length at all. The index is deliberately a `name(191)` *prefix*
index on MySQL/MariaDB rather than covering the full widened column — InnoDB's indexed-column byte
limit is charset/row-format dependent (767 bytes on older configurations, 3072 on modern ones), and
a 191-character prefix stays safely under the stricter limit regardless. A prefix index does not
affect the correctness of `WHERE name = ...` lookups, only how much of the value is used to narrow
candidate rows.

### `{prefix}log` — historical log

```sql
CREATE TABLE {log} (
    time         BIGINT,      -- ms since epoch when value became active
    item_id      INTEGER,
    duration     BIGINT,      -- ms the value was active
    val_str      TEXT,
    val_num      REAL,
    val_bool     BOOLEAN,
    changed      BIGINT,      -- ms since epoch of last write
    val_quality  TINYINT DEFAULT 0   -- v7, see §6
);
CREATE UNIQUE INDEX {log}_{item}_id_time    ON {log} (item_id, time);
CREATE INDEX        {log}_{item}_id_changed ON {log} (item_id, changed);
```

### Polymorphic value encoding

Each row stores a value in one of three typed columns:

| Item type | `val_str` | `val_num` | `val_bool` |
|---|---|---|---|
| `num` | NULL | the number | NULL |
| `bool` | NULL | 0 or 1 | 0 or 1 |
| `str` | the string | NULL | NULL |

`val_str = NULL` does **not** mean "no value was recorded" — it means the item is not a string
type. Aggregation queries must know the item's type to read the correct column.

![Schema](img/schema.svg)

### Per-driver type differences

`_setup()` branches on the driver to pick column/DDL variants — sqlite3 and MySQL/MariaDB are
described above; PostgreSQL (`psycopg2`/`psycopg`) differs in three ways:

- `id SERIAL PRIMARY KEY` — a real column-default sequence, auto-increments like sqlite3's bare
  `INTEGER PRIMARY KEY` out of the box, so (unlike MySQL/MariaDB's v8 migration) no retrofit is
  needed.
- `val_quality`/`val_bool` are `SMALLINT`, not `TINYINT` (PostgreSQL has no `TINYINT`). PostgreSQL's
  own `BOOLEAN` is strictly typed and rejects the integer 0/1 `encode_value()` always writes, so
  `val_bool` deliberately stays `SMALLINT` rather than a native `BOOLEAN` column.
- `{item}_name` is a plain, full-column index, not a `name(191)` prefix index — PostgreSQL has no
  InnoDB-style indexed-column byte limit to work around.

---

## 6. Value Quality — No-Data Gaps

A device that goes offline (a solar inverter at night, a sensor that loses connectivity) leaves its
SmartHomeNG item holding its last known value indefinitely — items have no built-in concept of
"value expired", and setting `item(None)` is not a usable substitute (silently ignored or rejected
depending on item type). Left alone, the database would record that stale last reading as valid and
continuously active, corrupting any time-weighted average or energy calculation across the gap.

The `val_quality` column (schema v7) solves this:

| Value | Meaning |
|---|---|
| `0` (`QUALITY_VALID`) | Normal recorded value. |
| `1` (`QUALITY_NO_DATA`) | No data available — value should be ignored in aggregations. All `val_*` columns are `NULL`. |

The plugin injects two methods onto every tracked item:

```python
item.db_mark_invalid()   # opens a QUALITY_NO_DATA gap entry at the current time
item.db_mark_valid()     # explicitly closes an open gap
```

If a new value arrives via `update_item()` while a gap is still open, the gap is closed **implicitly** —
no explicit `db_mark_valid()` call is required. The typical driver usage is just:

```python
item.db_mark_invalid()          # device goes offline
item(new_value, 'driver')        # device comes back — gap closes automatically
```

Gap duration is calculated from the gap's own open timestamp, not the item's last regular
`prev_change()` — those can differ if the gap opened well after the last real value change. There is
no separate tracking dict for open gaps; state is read directly off `BufferManager`'s last entry for
the item (`duration is None and quality == QUALITY_NO_DATA`), so a redundant `db_mark_valid()` call
after the gap has already closed is a harmless no-op.

![Quality feature](img/quality_feature.svg)

**Filtering gaps out of queries.** `utils.build_where_clause()` takes an `exclude_gaps` parameter,
opt-in rather than blanket:

- **On-demand analytics** (`_series()`/`_single()`, via `_fetch_log_base_where()`) always filter
  `(val_quality IS NULL OR val_quality = 0)` unconditionally — a gap row never contributes to a
  displayed series or a computed single value.
- **Compaction** (`LogStore.aggregate()`/`edge_value()`, used by `_compact_maxage()`, §7) passes
  `exclude_gaps=True` explicitly, for the same reason: a gap's `NULL` values must not corrupt the
  computed aggregate, and its (often large) duration must not skew a duration-weighted average.
- **Raw row management** (`delete_range()`/`find_range()`/`count()`) deliberately does *not*
  exclude gaps — a gap marker is still a real row that needs to be counted and cleaned up like any
  other, not silently skipped.

---

## 7. Age-Based Cleanup — Delete vs. Compact

![Age-based cleanup](img/maxage_compaction.svg)

Two independent, configurable mechanisms control how long log data is kept.

**`database_maxage`** (item attribute, in days) / **`default_maxage`** (plugin-level fallback for
items that don't set their own) — how old a log entry has to be before it's eligible for cleanup.
`default_maxage` alone (with no item setting its own `database_maxage`) is sufficient to activate
cleanup — the scheduler's worklist falls back to every item with a plain `database` attribute in
that case, not just ones with an explicit `database_maxage`.

**`database_maxage_action`** (item attribute) / **`default_maxage_action`** (plugin-level fallback)
— what happens to eligible entries. `'delete'` (the default) removes them outright, in
`max_delete_logentries`-sized batches per cycle so a very large backlog doesn't hold the lock for an
unbounded time. Any other value replaces raw entries with **one compacted value per
`database_maxage_interval`** instead of deleting them:

| Action | SQL expression | Valid item types |
|---|---|---|
| `sum` | `SUM(val_num)` | num, bool |
| `avg` | `AVG(val_num * duration) / AVG(duration)` | num, bool |
| `min` / `max` | `MIN(val_num)` / `MAX(val_num)` | num, bool |
| `integrate` | `SUM(val_num * duration)` | num, bool |
| `duty_cycle` (legacy alias: `on`) | `SUM(val_bool * duration) / SUM(duration)` | bool only |
| `countall` | `COUNT(*)` | any |
| `first` / `last` | oldest/newest raw value as-is (`ORDER BY time ASC/DESC LIMIT 1`) | any, including str |

A `database_maxage_action` invalid for the item's actual type (e.g. `sum` on a `str` item — `val_num`
is always `NULL` for strings) is rejected at `parse_item()` time with a logged error and falls back
to `'delete'` for that item. `first`/`last` work for every type because they read back whatever
`encode_value()` already stored, rather than computing anything over it — the only actions usable
for `str` items.

**Compaction (`_compact_maxage()`)** proceeds oldest-first, one `database_maxage_interval`-sized
bucket at a time, bounded by `max_aggregate_intervals` per call. There is no persisted resume
cursor — the next interval to compact is always simply whatever raw data remains oldest for that
item, so a crash or restart mid-compaction is self-healing by construction. Each interval's
aggregate/edge value is computed and its raw rows deleted inside the *same* `transaction()`
(`delete_range()` does **not** exclude gaps here — see §6 — a gap row is still deleted alongside
whatever real data shares its interval, since it contributed nothing to the aggregate but is still a
row to clean up). Delete happens before insert, not after: the aggregate row's timestamp is derived
from the oldest raw row's own timestamp, so inserting first risks colliding with it under the
`(item_id, time)` unique index.

If an interval's aggregate expression produces no value at all (e.g. every row in it has
`duration = NULL` — a crash-orphaned, never-closed buffer entry that reached the log table without
ever going through `_dump()`'s normal duration-fill) but the interval genuinely contains valid rows,
compaction leaves that interval raw rather than deleting data it cannot represent, logs a warning,
and stops for that item — it does not skip past the stalled interval to keep compacting newer ones,
since that would silently reorder which data survives.

**None of this section applies under `timescale_native_aggregation: true`.** `_start_schedulers()`
never registers `remove_older_than_maxage()` in that mode — TimescaleDB continuous aggregates and,
optionally, a native retention policy take over both roles server-side instead. See §8.

---

## 8. PostgreSQL + TimescaleDB Backend

PostgreSQL (`psycopg2`/`psycopg`) is a backend in its own right, with the [TimescaleDB
extension](https://www.timescale.com/) available as an opt-in layer on top of it — hypertables,
native compression, native continuous aggregates, and native retention, each independently toggled
and each falling back cleanly (a logged warning, nothing else affected) if its precondition isn't
met.

### Driver resolution

`driver` accepts the real module names (`psycopg2`, `psycopg`) as well as friendly aliases —
`postgres`/`postgresql`/`timescale`/`timescaledb` (all four resolve identically; TimescaleDB is a
Postgres extension, not a separate driver) and `mysql`/`mariadb` for `pymysql`. Resolution happens
once in `__init__()`, before `self.driver` is used anywhere else:

- `mysql`/`mariadb` → `pymysql` directly (`_DRIVER_ALIASES`, a plain lookup table).
- `postgres`/`postgresql`/`timescale`/`timescaledb` → `_resolve_postgres_driver_alias()` probes
  `importlib.import_module()` for `psycopg2` then `psycopg`, preferring `psycopg2` if both are
  installed. Neither installed → falls back to `'psycopg2'` *without* having confirmed it imports,
  so the resulting error names a real, searchable package instead of the friendly alias.
- Anything else (including an already-real module name) passes through unchanged.

Every later psycopg-specific check in the plugin (hypertable/compression/native-mode gating, the
`_setup()` schema branch in §5) tests `self.driver.lower() in lib.db.Database._psycopg_driver_names`
— the resolved real name, never the original alias.

### Hypertables and compression

Both are set up once, inside `_initialize_db()`'s schema-setup path (`self._db` only — both
operations are database-global, so running them again from `self._db_maint` would just be redundant
work against the already-converted table). Both are non-fatal on failure: a logged warning, and the
table stays a plain, uncompressed table — every other part of the plugin works identically either
way, since a hypertable is queried exactly like a regular table.

- **`timescale_hypertable`** (default **`true`**) — `CREATE EXTENSION IF NOT EXISTS timescaledb`,
  then `create_hypertable('log', 'time', chunk_time_interval => timescale_chunk_interval, ...)`.
  Splits `{log}` into time-based chunks (default width `168h`/7 days), which is what makes
  time-range queries on a large table fast — this is the feature that makes PostgreSQL worth
  choosing over plain MySQL/MariaDB for a large installation in the first place.
- **`timescale_compress`** (default `false`) — native columnar compression on `{log}`, segmented by
  `item_id`, ordered by `time DESC`, with a compression policy compressing everything older than one
  chunk width. The current chunk is deliberately left uncompressed — it's the only one that can hold
  a mutable "open" row (see `_compact_maxage()`'s `find_open()`). Measured 17.39× on a real
  22-million-row dataset; TimescaleDB's own documentation cites 10–20× as typical for time-series
  data. **One-way**: setting this back to `false` only stops future (re-)activation attempts, it
  does not decompress already-compressed chunks.

### Native aggregation

**`timescale_native_aggregation`** (default `false`) replaces the plugin-side compaction described
in §7 with TimescaleDB continuous aggregates, computed server-side instead of by
`_compact_maxage()`. Same `database_maxage`/`database_maxage_action`/`database_maxage_interval`
item attributes still control it — only *where* the aggregation runs changes, not how it's
configured. Activation happens in `run()`, not `_initialize_db()`'s setup path — it needs the real
item list, which `parse_item()` has not populated yet at `__init__()`'s own `_initialize_db()` call:

1. Register an integer-now function (`set_integer_now_func`) TimescaleDB needs for continuous
   aggregates on this bigint-epoch-ms schema. **Not idempotent** — every call after the first
   errors, even re-registering the same function — so this is called with `quiet=True` and the
   "already set" case is tolerated silently in the plugin's own `except` block; anything else is a
   real failure.
2. One continuous aggregate **per distinct `database_maxage_interval` actually in use**, grouped
   across every item sharing that width — not one per item, and not one per
   `database_maxage_action` (an item's action is just an extra column on the shared view). Items
   resolving to action `'delete'` are skipped entirely; native retention (if enabled) drops their
   raw chunks directly instead.

See [img/timescale_native_setup_flow.svg](img/timescale_native_setup_flow.svg) for the full call
sequence including every failure branch, and
[img/query_read_flow.svg](img/query_read_flow.svg) for how `_series()`/`_single()`/`readLogCount()`
each route between raw data and the native caggs — the three differ in an important way:

- **`_series()`** always queries the raw log for the full requested range, and separately queries
  `_native_cagg_series()` for whatever portion of that range predates the raw floor (native
  retention may have dropped it) — a genuine **merge**, prepending cagg tuples to the raw ones so a
  chart gets one continuous line across the boundary.
- **`_single()`** only takes the cagg path when the *entire* requested range predates the raw
  floor; any overlap with still-raw data falls through to the normal precise raw-log query
  instead — **exclusive**, never both, because a single scalar has no boundary to stitch.
- **`readLogCount()`** adds `_native_cagg_count()` to the raw count — safe unconditionally, since
  the two ranges never overlap by construction.

### Native retention

**`timescale_native_retention`** (default `false`, requires `timescale_native_aggregation: true`)
drops old raw-data chunks server-side via `add_retention_policy()`, instead of
`remove_older_than_maxage()`'s per-item `DELETE`. **This is the one significant behavioral
difference from every other backend, and it's a deliberate design decision, not a gap to
"fix":**

- The drop threshold is **one global value for the whole hypertable** — the *longest*
  `database_maxage` across every relevant item, plus one `timescale_chunk_interval` as a safety
  margin — not a per-item value. An item configured for 5 days keeps its raw data until the
  longest-configured item's threshold passes, because chunks are shared across items.
  `remove_older_than_maxage()` never runs at all in this mode (see §7's closing note), even for
  `database_maxage_action: delete` items specifically — reintroducing per-item deletion would
  defeat the reason a coarse global threshold is acceptable, since native compression already
  absorbs the cost of keeping raw data a bit longer than any single item strictly needs.
- **Every item is affected, including ones without `database_maxage` set at all** — there is no
  "leave this item's raw data alone forever" option once native retention is on. If no item and no
  `default_maxage` configures a maxage, activation is skipped with a warning (nothing to retain
  against); otherwise `default_maxage`/`default_maxage_action` are worth setting explicitly so
  items that never opted into cleanup don't fall back to `'delete'` unexpectedly.
- Reversing native aggregation back to plugin-side compaction is **not implemented** and not
  possible without data loss — there is no code path that reads cagg values back out and reinserts
  them into `{log}`.

### Status introspection

`timescale_status()` reality-checks the database itself (`{'hypertable': bool|None, 'native_cagg':
bool|None, 'native_retention': bool|None}`, `{}` on a non-psycopg driver) rather than trusting
`plugin.yaml` — config can drift from what's actually active in the database (e.g. a feature enabled
once, then the parameter reverted, without ever undoing the database-side change). `None` for a key
means the check itself failed (extension not installed → no catalog views to query), distinct from
`False` (checked, genuinely inactive). Not exposed in this plugin's own web interface — consumed by shngadmin's dashboard
database-properties widget.

`run()` also calls `_reconcile_native_retention_reality()` (psycopg drivers only, before any
native-mode setup), which checks specifically whether a **retention policy** is actually active in
the database and self-corrects on drift — an admin editing `plugin.yaml` while shng is stopped, or
an unattended restart, could otherwise leave an active TimescaleDB retention policy (which runs on
its own schedule regardless of shng's state) silently paired with `timescale_native_aggregation:
false`, which would mean plugin-side compaction storing aggregates in-place in chunks TimescaleDB is
dropping out from under it — real, silent data corruption, not just a missed optimization. A policy
active with aggregation disabled in config forces `_timescale_native_aggregation = True` for that
run only (never rewrites `plugin.yaml`, logged at CRITICAL); a policy active with
`timescale_native_retention: false` gets removed to match configured intent (falling back to the
same forced-aggregation fix if removal itself fails); `timescale_native_retention: true` with no
policy actually active and aggregation off is refused for that run (nothing dangerous is happening
yet, so nothing needs forcing, just not created).

### Migrating between backends

`tools/db_migrate.py` moves item and log data directly between any two supported backends (e.g.
SQLite3 → TimescaleDB), independent of SmartHomeNG (run only while it's stopped). Supports resume
and `--dry-run`. Refuses to migrate *from* a source that already has native continuous aggregates
active unless `--force` is given — such a source's raw data past the native-retention floor is
already gone, so a straight raw-table copy would silently produce an incomplete migration with no
error. Budget real time for a large table: a 22-million-row transfer took roughly three hours on the
hardware it was tested against.

---

## 9. Code Flow Diagrams

Detailed, code-level flowcharts for the plugin's major workflows — branches, exception paths, and
requeue/retry logic included, not just the high-level shape already covered in §2/§4/§7/§8 above.

| Workflow | Diagram |
|---|---|
| Plugin startup (`__init__()` → `_initialize_db()` → `run()`) | [img/init_startup_flow.svg](img/init_startup_flow.svg) |
| Item value change (`update_item()`) | [img/item_update_flow.svg](img/item_update_flow.svg) |
| Dump cycle (`_dump()`) | [img/dump_cycle_flow.svg](img/dump_cycle_flow.svg) |
| Age-based cleanup (`remove_older_than_maxage()` / `_compact_maxage()`) | [img/compacting_pruning_flow.svg](img/compacting_pruning_flow.svg) |
| No-data gaps (`db_mark_invalid()`/`db_mark_valid()`, `database_invalid_after`) | [img/invalidity_check_flow.svg](img/invalidity_check_flow.svg) |
| On-demand queries (`_series()`/`_single()`/`readLogCount()` native-cagg routing) | [img/query_read_flow.svg](img/query_read_flow.svg) |
| TimescaleDB native-mode activation (hypertable/compression/native aggregation/retention) | [img/timescale_native_setup_flow.svg](img/timescale_native_setup_flow.svg) |

---

## 10. Further Reading

- `lib/db.py`'s own module docstring and `Database.transaction()`'s docstring cover connection-level
  concerns (reconnect throttling, the hang watchdog, self-healing `commit()`/`rollback()`) not
  repeated here since they apply to every plugin using `lib/db.py`, not just this one.
- This plugin's `user_doc.rst` covers end-user configuration, including the MySQL/MariaDB-specific
  limits mentioned in §5/§7, the PostgreSQL+TimescaleDB setup covered in §8, and worked
  configuration examples for both.
- `doc/user/source/tools/tools_db_migrate.rst` documents `tools/db_migrate.py` (§8) from a user's
  perspective — CLI flags, prerequisites, worked examples.
- For *why* the locking model looks like this — the production incidents and the two audit passes
  that shaped it — see the project's commit history on the `db-transaction-refactor` /
  `database-transaction-refactor` branches; this document intentionally describes the current
  design only, not that process.
