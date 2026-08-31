# `lib/item` — Modularisation History

A short record of how `lib/item/item.py` (SmartHomeNG's central `Item` class)
went from a single monolithic file to a core file plus a set of focused
sub-modules. For how the resulting code actually works — the item tree,
value updates, dependency wiring — see
[`lib_item_architecture.md`](lib_item_architecture.md) instead; this document
is about the *history* of the split, not its mechanics.

## Why

`item.py` started out as one ~3 000-line file holding every concern of the
`Item` object: type handling, history tracking, eval expressions,
log-change rules, the hysteresis state machine, autotimer/cycle scheduling,
path resolution, attribute parsing, value casting, trigger registration,
stack inspection, fade/ramp, JSON serialisation — all in one class body.
That made the file hard to navigate and risky to change: an edit to, say,
the hysteresis logic sat in the same file (and often the same review diff)
as unrelated eval or logging code.

## What was done

Work proceeded test-first: a comprehensive unit-test suite was written
*before* any production code moved, so every extraction could be verified
immediately against a green baseline. Ten test files (~240 tests) were added
up front, covering the areas about to be extracted; a few gaps found along
the way added another three files (~80 tests).

With that safety net in place, each concern was pulled out of `Item` into
its own module in four rounds, following the same pattern every time:

1. Write the extracted logic as plain module-level functions taking the
   `Item` instance as an explicit argument (`func(item, ...)`), touching only
   its single-underscore attributes and public methods — this sidesteps
   Python's name-mangling for `__dunder` attributes without exposing new
   public API.
2. Where a `__dunder` attribute genuinely needs to be reached from outside,
   add a thin proxy method or property on `Item`.
3. Replace the original method body in `item.py` with a one-line delegate
   call into the new module, so the public API and every scheduler/plugin
   callback keep working unchanged.
4. Run the full test suite before moving to the next piece.

Roughly a dozen concerns were split out this way — type/list/dict handling,
history tracking, log-change rules, eval/on_change/on_update execution, the
hysteresis state machine, path resolution, autotimer/cycle handling, value
casting, trigger registration, attribute parsing, call-stack inspection,
fade/ramp, JSON serialisation, item removal, and tree navigation — along
with the deletion of a couple of dead methods no longer called from
anywhere. All of them ended up living under `lib/item/_internal/`, imported
back into `item.py` and (for the trickier eval-namespace case) documented
separately in [`eval_env.md`](eval_env.md), since extracting `eval()` calls
into another module changes what names are visible to a user's eval
expression — a correctness issue distinct from the split itself.

Throughout, no extraction introduced a regression: the test suite stayed
green after every step across all four rounds.

## Result

`item.py` now holds the parts that genuinely need to be one class —
construction, the public API, `__call__`/`__update`, properties — while the
rest lives in single-purpose modules under `_internal/`, each with its own
test file. The class remains one `Item` object with one identity; the split
is an internal code-organisation choice, not a change to how items behave.
