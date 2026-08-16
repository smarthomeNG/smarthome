# SmartHomeNG Database Plugin — Developer Documentation

This document describes the internal design of the `database` plugin, the module-split refactoring it went through, and the associated bug fixes and improvements. It is aimed at Python developers who are already familiar with SmartHomeNG basics.

> **Status (verified 2026-08-16 against `plugins/database/` and `lib/db.py` on `develop`):** The `utils.py`/`buffer.py`/`store.py` split described in §3, and the `val_quality` no-data-gap feature described in §6, have both shipped — the module layout and even the function names (`encode_value`, `decode_value`, `to_timestamp`, `from_timestamp`, `apply_table_names` in `utils.py`) match what was proposed here almost exactly. `query.py` and `maintenance.py` were **not** split out — `_series`, `_single`, `remove_older_than_maxage` and `_query` still live in `__init__.py` (now ~2450 lines, still the largest file in the plugin). Most of the bug fixes (§7) and performance improvements (§8) below have shipped; status is annotated inline per item. `lib/db.py` itself also went through a separate, later hardening pass (bounded lock timeouts, a hang watchdog, self-healing `commit()`/`rollback()`) not originally scoped here — not detailed in this document since it belongs to `lib/db.py`'s own docs, not the plugin's.

---

## 1. Overview

The `database` plugin persists item values to a relational database (SQLite, MySQL, or PostgreSQL via `lib/db.py`). Its distinguishing feature compared to a plain event log is that **every row records not just a value but how long that value was active** — the `duration` column. This makes it straightforward to compute time-weighted averages, cumulative energy totals, and similar analytics directly in SQL.

Four concepts are central to understanding the plugin:

| Concept | Description |
|---|---|
| **log table** | The historical record. One row per value-change event, with `time`, `duration`, and the value itself. |
| **item table** | A single-row-per-item snapshot of the *latest* value. Used for fast lookups without scanning the log. |
| **buffer** | An in-memory dict (keyed by item id) that accumulates incoming changes between database writes. |
| **dump cycle** | A scheduler job that runs every 60 seconds and flushes the buffer to SQL in a single transaction. |

---

## 2. Architecture Before the Module Split

*(Historical — see §3 for the current, already-implemented layout.)*

The plugin used to be implemented as a single file:

```
plugins/database/__init__.py   (1 891 lines)
```

Everything lived inside the `Database(SmartPlugin)` class:

- SQL DDL and schema setup (`_setup` dict, `_initialize_db`)
- Low-level CRUD helpers (`insertItem`, `updateItem`, `readItem`, `insertLog`, `updateLog`, `readLog`, …)
- Buffer management (`_buffer`, `_buffer_lock`, `_dump`)
- Analytics queries (`_series`, `_single`, the `_query` dispatcher)
- Maintenance tasks (`remove_older_than_maxage`, `_remove_orphans`)
- Plugin lifecycle (`__init__`, `run`, `stop`, `parse_item`, `update_item`)
- CSV export (`dump`)
- Web interface glue

![Current architecture](img/current_architecture.svg)

The consequence of this monolithic design is tight coupling: a one-line change to buffering logic requires touching the same file as a SQL schema migration. Testing any single concern requires instantiating the full `SmartPlugin` stack. Bug fixes in one area risk inadvertently breaking another.

---

## 3. Architecture After the Module Split

**Implemented.** `utils.py`, `buffer.py` and `store.py` have been extracted, each matching this section's original proposal closely (see the verified function/class names below). `query.py` and `maintenance.py` were **not** extracted — `_series`/`_single` (analytics) and `remove_older_than_maxage`/orphan cleanup (maintenance) remain methods on `Database` in `__init__.py`, which at ~2450 lines is still the largest file in the plugin, not the thin orchestrator originally envisioned here.

The public API — all method names called by items, the web interface, and user automations — is preserved on the `Database` class as thin delegates to the extracted stores, giving **full backward compatibility** (see `insertItem`/`readItem`/etc. in `__init__.py`, which now just call `self._item_store.insert(...)` / `self._item_store.find(...)`).

```
plugins/database/
├── __init__.py        # Database(SmartPlugin) — public API, plus _series/_single/
│                       # remove_older_than_maxage/_query (not extracted, see above)
├── utils.py            # Pure functions, no side-effects — implemented
├── buffer.py            # BufferManager — owns buffer dict + lock — implemented
├── store.py             # ItemStore + LogStore — SQL CRUD — implemented
├── constants.py         # (existing, now also holds BufferEntry and the
│                        #  QUALITY_VALID/QUALITY_NO_DATA quality flags — see §6)
└── webif/               # (existing)
```

### Module responsibilities

*(Verified against the actual `plugins/database/` source, not the original proposal — signatures below are the real ones, which differ in a few names/parameter orders from what was originally sketched here.)*

**`utils.py`** — pure functions only, importable without any database connection:

- `encode_value(item_type, value) -> dict` — maps a Python value to the three SQL columns (`val_str`/`val_num`/`val_bool`), as a dict, not a tuple.
- `decode_value(item_type, val_str, val_num, val_bool) -> value` — reverse.
- `to_timestamp(dt) -> int` — converts a `datetime` to milliseconds-since-epoch.
- `from_timestamp(ts, tzinfo=None) -> datetime` — reverse.
- `apply_table_names(query, table_names) -> str` — substitutes `{item}`/`{log}`/`{item_columns}`/`{log_columns}` placeholders.
- `build_where_clause(item_id, *, time=None, time_start=None, ...) -> (sql, params)` — not in the original proposal; replaces the `_slice_condition` flag-trick mentioned in §9 (see the function's own docstring, which references that replacement explicitly).

**`buffer.py`** — `BufferManager`:

- Owns `self._buffer: dict` and `self._lock: threading.Lock`, plus `register()`/`deregister()` for item lifecycle.
- `push(item, entry: BufferEntry)` — appends an entry (acquires lock).
- `close_open(item, end_ts)` / `set_last_duration(item, duration)` — back-fill the duration of the last open (`duration=None`) entry.
- `push_invalid(item, start_ts)` — opens a `QUALITY_NO_DATA` gap entry (see §6).
- `pop_all(item)` / `restore(item, entries)` — drain an item's pending writes for `_dump()`, and put them back if the write fails.

**`store.py`** — `ItemStore` and `LogStore`:

- `ItemStore`: `insert`, `update`, `find`, `find_all`, `count`, `delete` — operates on the `{item}` table.
- `LogStore`: `insert`, `update`, `upsert`, `find`, `find_range`, `count`, `count_all`, `delete_range`, `oldest_time`, `latest_time`, `edge_value`, `aggregate` — operates on the `{log}` table.
- Both classes receive a `lib.db.Database` connection and a `table_names` dict; they contain no plugin business logic.

**`query.py` / `maintenance.py`** — **not extracted.** The analytics logic (`_series`, `_single`) and the maintenance logic (`remove_older_than_maxage`, orphan-id reassignment) originally proposed for these two modules still live as methods on `Database` in `__init__.py`.

**`__init__.py`** — `Database(SmartPlugin)`:

- Creates and wires `BufferManager`/`ItemStore`/`LogStore`.
- Implements `run`, `stop`, `parse_item`, `update_item`, `_dump` (the scheduler callback) — plus `_series`/`_single`/`remove_older_than_maxage` (not extracted, see above).
- Re-exports all legacy method names (`insertLog`, `readItem`, etc.) as one-line delegates to the store objects — confirmed backward-compatible (see §10).

![Proposed architecture](img/proposed_architecture.svg)
*(Diagram predates the actual split above and shows `query.py`/`maintenance.py` as extracted, which they were not — kept for the general before/after shape, not as a literal file listing.)*

---

## 4. Data Flow

This section traces what happens when an item value changes.

![Data flow](img/data_flow.svg)

> **Note:** the actual `_dump()` (`plugins/database/__init__.py:1716`) does not call a `BufferManager.close_open_entries()` method — no such method exists on `BufferManager` (which has `close_open(item, end_ts)`/`set_last_duration(item, duration)` instead, operating per-item, not as a bulk "close everything" pass). The still-open (`duration=None`) most-recent entry for an item is not written to the log table until it is closed by a later value change or by `finalize=True` at shutdown. Whether the step-by-step description below still matches in every detail was not fully re-verified line-by-line against the current `_dump()`/`update_item()` code; treat it as directionally correct but confirm against source before relying on specifics.

### Step-by-step

1. **Item changes.** SmartHomeNG calls `Database.update_item(item, caller, source, dest)`. The method checks whether the item has the `database` attribute and bails out early if not.

2. **Duration is calculated retroactively.** The database does not know in advance how long a value will be active. When a *new* value arrives, the plugin looks up the *previous* buffer entry for this item. It calculates:

   ```python
   duration = now_ms - prev_entry.time_ms
   ```

   and writes that duration back into the previous entry before flushing it.

3. **New buffer entry appended.** The new value is pushed into the buffer with `duration=None`, meaning "this value is still active, duration not yet known":

   ```python
   buffer[item_id].append(BufferEntry(time=now_ms, duration=None, value=value, quality=0))
   ```

4. **Dump cycle.** Every 60 seconds the SmartHomeNG scheduler calls `Database._dump()`. This method:

   a. Calls `BufferManager.close_open_entries(now_ms)` — for the most recent entry of each item, sets `duration = now_ms - entry.time_ms` temporarily (the value is still active, but we need *something* for the SQL row; on the next dump this row will be updated with the real duration).

   b. Calls `BufferManager.pop_all()` to drain the buffer atomically.

   c. For each entry, calls `LogStore.insert` or `LogStore.update` as appropriate.

   d. Calls `ItemStore.update` to refresh the latest-value snapshot.

The result is that every log row always has a non-null `duration`, and the duration of the most recent row is continuously extended on each dump cycle.

---

## 5. Database Schema

The plugin manages two tables. Their names are configurable via `db_prefix`; the defaults are `log` and `item`.

### `{prefix}item` — latest-value snapshot

```sql
CREATE TABLE {item} (
    id       INTEGER PRIMARY KEY,  -- DB-generated autoincrement, see §7 bug 4
    name     VARCHAR(255),
    time     BIGINT,       -- ms since epoch of last change
    val_str  TEXT,
    val_num  REAL,
    val_bool BOOLEAN,
    changed  BIGINT        -- ms since epoch of last write
);
CREATE UNIQUE INDEX {item}_id   ON {item} (id);
CREATE INDEX        {item}_name ON {item} (name);
```

One row per tracked item. `id` is assigned by the database itself via `INTEGER PRIMARY KEY` autoincrement (`ItemStore.insert()` reads it back via the cursor's `lastrowid`) — corrected from the original `MAX(id)+1`-based allocation described as buggy in §7, bug 4.

### `{prefix}log` — historical log

```sql
CREATE TABLE {log} (
    time     BIGINT,       -- ms since epoch when value became active
    item_id  INTEGER,
    duration BIGINT,       -- ms the value was active
    val_str  TEXT,
    val_num  REAL,
    val_bool BOOLEAN,
    changed  BIGINT        -- ms since epoch of last write
);
CREATE UNIQUE INDEX {log}_{item}_id_time    ON {log} (item_id, time);
CREATE INDEX        {log}_{item}_id_changed ON {log} (item_id, changed);
```

### Polymorphic value encoding

Each row stores a value in one of three typed columns. The mapping is:

| Item type | `val_str` | `val_num` | `val_bool` |
|---|---|---|---|
| `num` | NULL | the number | NULL |
| `bool` | NULL | 0 or 1 | 0 or 1 |
| `str` | the string | NULL | NULL |

`val_str = NULL` does **not** mean "no value was recorded". It means the item is not a string type. Aggregation queries must filter by `item_id` first, and then read the appropriate column based on the known item type.

![Schema](img/schema.svg)

---

## 6. The Missing-Value Problem and Solution

**Implemented** (schema version 7, `QUALITY_VALID`/`QUALITY_NO_DATA` in `constants.py`, `item.db_mark_invalid()`/`item.db_mark_valid()` wired up in `parse_item()`) — described below as it exists today, not as a proposal.

### Problem

Consider a solar inverter that reports power output every 30 seconds while the sun is up, but goes completely offline at night (or on a cloudy day). SmartHomeNG items retain their last known value indefinitely — there is no built-in concept of "value expired" or "data source offline". The database therefore records the last inverter reading as valid and continuously active, potentially for many hours. Any time-weighted average or energy calculation over that period will be wrong.

### Why `None` Does Not Work

SmartHomeNG items are strongly typed. Setting `item(None)` is silently ignored or raises an exception depending on the item type. There is no standard mechanism to represent "this item has no valid data right now" at the item level.

### Solution: `val_quality` Column

A new column is added to the log table:

```sql
ALTER TABLE {log} ADD COLUMN val_quality TINYINT DEFAULT 0;
```

Quality codes:

| Value | Meaning |
|---|---|
| `0` | Valid — normal recorded value |
| `1` | No data available — value should be ignored in aggregations |

### New Item Methods

The plugin injects two methods onto every tracked item:

```python
item.db_mark_invalid()   # injects a quality=1 log entry at current time
item.db_mark_valid()     # injects a quality=0 log entry (data available again)
```

A user automation or driver plugin can call `inverter_power.db_mark_invalid()` when it detects the inverter has gone offline. The database will record a log entry with `val_quality=1` at that moment, and `db_mark_valid()` when the inverter comes back online.

### Implicit Re-validation

If a new value arrives via `update_item()` while a gap is still open, the plugin **automatically closes the gap** — no explicit `db_mark_valid()` call is required.

- The gap duration is calculated from the gap's own open timestamp, not from the item's last regular `prev_change()`. This is important: if the gap was opened at `T1` but the item had last changed at `T0 < T1`, using `prev_change()` would produce a wrong (too long) duration.
- After closing the gap, the new value is written to the buffer as a normal `val_quality=0` entry.
- There is no separate `_gap_items` tracking dict in the actual implementation — gap state is read directly from `BufferManager.last_entry(item)`: an open gap is `duration is None and quality == QUALITY_NO_DATA`. A subsequent `db_mark_valid()` is a no-op because `_mark_item_valid()` checks the same condition and returns early if it no longer holds (see `plugins/database/__init__.py:_mark_item_valid`).

This means the typical driver usage is simply:

```python
# device goes offline
item.db_mark_invalid()

# device comes back online — just set the new value; gap closes automatically
item(new_value, 'driver')

# db_mark_valid() is only needed when closing the gap *before* the first
# new value is available
```

### Updated Aggregation Queries

All analytics queries gain a `WHERE val_quality = 0` (or `COALESCE(val_quality, 0) = 0` for backward compatibility with older rows) filter:

```sql
SELECT SUM(val_num * duration) / SUM(duration)
FROM {log}
WHERE item_id = ?
  AND time BETWEEN ? AND ?
  AND COALESCE(val_quality, 0) = 0
```

### `BufferEntry` Namedtuple

The in-memory buffer entries are updated to carry quality:

```python
from collections import namedtuple
BufferEntry = namedtuple('BufferEntry', ['time', 'duration', 'value', 'quality'])
```

![Quality feature](img/quality_feature.svg)

---

## 7. Identified Bug Fixes

All six items below were verified against current source on 2026-08-16; status is noted per item.

### 1. `UnboundLocalError` in `remove_older_than_maxage`

**Fixed.** `item_id = None` is now initialized before the `try` block, with the comment `# initialise before try so the except clause can reference it safely` (`plugins/database/__init__.py:2051`).

In the exception handler, the variable `item_id` is referenced but may not have been assigned if the earlier `readItem` call raised before the assignment. Fix: initialize `item_id = None` before the try block and guard the delete call.

### 2. `len(None)` crash in `_dump`

**Superseded by the buffer-manager rewrite**, not fixed as a standalone patch. The `_dump()` method no longer calls `readLog()` at all — it iterates entries popped from `BufferManager` (`self._buffer_mgr.pop_all(item)`), so the specific `len(result)`-on-`None` code path described here no longer exists in this form.

`readLog(...)` can return `None` when the database is unavailable. The dump code calls `len(result)` unconditionally. Fix: add a `if result is None: continue` guard.

### 3. Negative duration stored without correction

**Fixed**, though not by clamping inside the buffer/store layer as originally sketched — the clamp lives in `update_item()` itself: `plugins/database/__init__.py:534-540` computes `end - start`, and if negative, logs `'Negative duration clamped to 0: ...'` and sets `end = start` before the value ever reaches the buffer.

When the system clock jumps backward (NTP correction, DST, VM resume), `duration = now - prev_time` can be negative. Negative durations corrupt time-weighted averages. Fix: clamp to `max(0, duration)` before storing.

### 4. `insertItem` race condition

**Fixed**, using the suggested approach. The `{item}` table's schema (v2 in the `_setup` dict) now declares `id INTEGER PRIMARY KEY`, with the inline comment `# id declared as INTEGER PRIMARY KEY so the DB handles auto-increment; avoids the previous MAX(id)+1 race condition on multi-connection setups`. `ItemStore.insert()` reads the new id back via the cursor's own `lastrowid` rather than a follow-up `SELECT`.

New item IDs are allocated with:

```sql
SELECT MAX(id) + 1 FROM {item}
```

This is not atomic. Two threads starting simultaneously can both read the same `MAX(id)` and attempt to insert the same new `id`, causing a unique-index violation. Fix: use `INSERT OR IGNORE` / `INSERT IGNORE` with a database-generated autoincrement id, or hold the lock for the full read-then-insert sequence.

### 5. `readTotalLogCount` silently ignores its parameters

**Fixed.** `readTotalLogCount(self, cur=None)` no longer accepts `id`/`time_start`/`time_end` at all — its docstring states the signature was corrected because those parameters were "silently ignored" (`plugins/database/__init__.py:1123`), and it now delegates to `LogStore.count_all()`, an unfiltered total by design (per-item/time-ranged counts go through the separate `readLogCount()` method instead, which does build a `WHERE` clause).

The method accepts `item_id` and `time_start`/`time_end` parameters but the SQL query it issues contains no `WHERE` clause, returning a count across the entire log table. Fix: add the appropriate `WHERE item_id = ? AND time BETWEEN ? AND ?` clause.

### 6. `fetchone()` returns `''` instead of `None` on cursor failure

**Effectively fixed, as part of a broader `lib/db.py` hardening pass** (see the status note at the top of this document). `fetchone()`'s `cur=None` path now raises the original exception on failure rather than swallowing it into a return value — `''` is only ever returned when there was no connection to query in the first place (`self._conn is None`), which is a distinct, legitimate case, not an error being hidden.

In `lib/db.py`, when `cursor.fetchone()` raises an exception, the except block returns an empty string `''`. Callers test `if result is None`, so the error is invisible and subsequent code unpacks `''` as a row. Fix: return `None` consistently from all error paths.

---

## 8. Performance Improvements

### 1. Double preparation of SQL statements in `_query()`

**Fixed.** `_query()` now calls `self._prepare(query)` exactly once, with the inline comment `# prepare once` (`plugins/database/__init__.py:2367`).

The current `_query()` helper calls `self._db.prepare(sql)` and then immediately calls `self._db.execute(sql, ...)` which internally calls `prepare` again. The first call is redundant. Fix: remove the standalone `prepare` call.

### 2. Debug string formatting runs unconditionally

**Fixed.** No remaining `logger.debug(... % ...)` eager-interpolation calls were found in `plugins/database/__init__.py`; `_query()`'s docstring notes debug formatting now only runs `when self.logger.isEnabledFor(logging.DEBUG)`.

Several hot paths contain:

```python
self.logger.debug("query: %s params: %s" % (sql, params))
```

The `%` string interpolation runs even when debug logging is disabled, allocating strings unnecessarily. Fix: use lazy `%` formatting via the logging API:

```python
self.logger.debug("query: %s params: %s", sql, params)
```

### 3. `_initialize_db()` called on every query

**Fixed**, exactly as proposed. `self._db_initialized` is set in `__init__`/`_initialize_db()`, and `_query()` checks it first with the comment `# fast-path: avoid full init check on every query` (`plugins/database/__init__.py:2350`).

`_initialize_db()` checks whether the schema tables exist and creates them if not. It is currently called at the start of every `_query()` invocation. The schema check involves a `SELECT` against the database metadata on every single query. Fix: add a boolean flag `self._db_initialized` that is set to `True` after the first successful initialization, and skip the call when the flag is set.

---

## 9. Code Quality Improvements

### 1. Replace `_slice_condition` flag trick

**Fixed**, in `utils.py` rather than `__init__.py`. `build_where_clause()` builds an explicit list of condition strings joined by `AND`; its docstring states directly: "Replaces the previous `_slice_condition` flag-trick, which passed `1 = :flag` to bypass conditions when parameters were `None`."

The current code uses a mutable flag variable to decide whether to prefix a SQL fragment with `AND` or `WHERE`. Replace with an explicit list of condition strings joined by `AND` and prepended with `WHERE` only when the list is non-empty. This is clearer and less error-prone.

### 2. Merge duplicated `_item_value_tuple` branches

**Fixed**, via the `utils.py` extraction rather than an in-place merge — `_item_value_tuple()` now just delegates to `utils.encode_value()`, whose `'num'`/`'bool'` branch is already merged (`return {'val_str': None, 'val_num': float(value), 'val_bool': int(bool(value))}`).

The `'num'` and `'bool'` branches in `_item_value_tuple` produce nearly identical output (both write to `val_num`). Merge them into a single branch:

```python
if item_type in ('num', 'bool'):
    return (None, float(value), int(bool(value)))
```

### 3. Use `csv` module in `dump()`

**Not done.** `dump()` (`plugins/database/__init__.py:827`) still writes the CSV file with manual `s.join(h)`/`f.write()` calls, no `import csv`/`csv.writer` in the file.

The CSV export method manually escapes commas and quotes. Replace with Python's standard `csv.writer`, which handles all edge cases correctly.

### 4. `isinstance()` instead of `type() ==`

**Fixed** (or never present in this form) — no `type(x) ==` pattern found anywhere in `plugins/database/__init__.py`.

Replace all occurrences of `type(x) == SomeType` with `isinstance(x, SomeType)` to correctly handle subclasses and to follow Python best practices.

### 5. Remove deprecated connection parameters from `lib/db.py`

**Addressed**, though as part of the later, separately-scoped `lib/db.py` hardening pass rather than this refactor specifically (see the status note at the top of this document) — `lib/db.py` now explicitly type-converts known connection kwargs (`_numeric_connect_keys`, `_bool_connect_keys`) and injects pymysql-family timeout defaults (`connect_timeout`/`read_timeout`/`write_timeout`) rather than passing raw config strings through.

`lib/db.py` passes keyword arguments to database drivers that have been deprecated or renamed in recent driver versions. Update to current parameter names.

### 6. Consistent `snake_case` naming

**Achieved via the module split (§3), not via renaming.** The `Database` class's public methods are still `camelCase` (`insertItem`, `readLog`, `updateLog`, etc.), but they are now one-line delegates to `snake_case` methods on `ItemStore`/`LogStore` (`insert`, `update`, `find`, `find_range`, ...) — so the "internally all new code calls snake_case" intent is met, just not by renaming the public surface.

Several methods use `camelCase` names (`insertItem`, `readLog`, `updateLog`, etc.) inherited from the original implementation. New code uses `snake_case`. The public camelCase names are kept as aliases for backward compatibility; internally all new code calls the snake_case variants.

---

## 10. Migration Strategy

*(This section originally described the plan; §3's status note above confirms the outcome — `utils.py`/`buffer.py`/`store.py` shipped, `query.py`/`maintenance.py` did not. The subsections below are corrected to match what was actually built, per point.)*

### Backward Compatibility

**Confirmed accurate in principle** — all method names currently used by items, the web interface, and user automations (`insertLog`, `readItem`, `readLog`, `updateItem`, `dump`, etc.) do remain on the `Database` class as one-line delegates. The illustrative code below is corrected to match the real delegate targets, which differ in method name/signature from the original sketch (real store methods use `find`/`find_range` rather than `read`, and take a `BufferEntry`/positional args rather than raw value columns):

```python
# In Database(__init__.py), actual current code:
def readItem(self, id, cur=None):
    return self._item_store.find(id, cur=cur)

def insertItem(self, name, cur=None):
    return self._item_store.insert(name, cur=cur)
```

No external caller needs to be updated.

### Incremental Approach

Because the public API is stable, the refactoring proceeded one module at a time, largely as planned — **with step 4 not completed**:

1. Extract `utils.py` first — it has no dependencies on anything else and can be unit-tested immediately. — done.
2. Extract `store.py` next — replace the inline SQL calls with `ItemStore`/`LogStore` instances. — done.
3. Extract `buffer.py` — replace `self._buffer` and `self._buffer_lock` usages. — done.
4. Extract `query.py` and `maintenance.py`. — **not done**; `_series`/`_single`/`remove_older_than_maxage` remain in `__init__.py`.
5. `__init__.py` becomes the thin orchestrator in the final step. — **not achieved**, as a direct consequence of step 4 not happening; `__init__.py` is still ~2450 lines.

Each step produced a diff that is reviewable in isolation and can be validated against the existing test suite.

### Schema Migration

**Implemented, but via the plugin's existing versioned-schema mechanism, not a bespoke probe.** The `val_quality` column is schema version `'7'` in the `_setup` dict already used for every other schema change (`plugins/database/__init__.py`, versions `'1'`–`'6'`), processed by `lib.db.Database.setup()`'s existing version-table check — not a new `try: SELECT ... except: ALTER TABLE` probe as originally sketched here:

```python
'7': [
    'ALTER TABLE {log} ADD COLUMN val_quality TINYINT DEFAULT 0;',
    '/* val_quality column cannot be removed via ALTER TABLE on SQLite <3.35 */',
],
```

Existing databases without the column are upgraded automatically on first startup of the new version, the same way every prior schema version bump has always been applied — quality defaults to `0`/valid for all pre-existing rows via the column's `DEFAULT 0`.
