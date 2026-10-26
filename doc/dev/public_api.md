# SmartHomeNG public API and versioning

**Status: draft.** Decisions marked *(decided)* were taken by the lead developer; items marked
*(proposed)* still need a decision.

SmartHomeNG follows [Semantic Versioning 2.0.0](https://semver.org/) from release **2.0.0** on.
Semver rule 1 requires a declared public API. This document declares it, and the tooling in
`tools/` checks changes against it.

## What is public API *(decided)*

Only what is listed here is covered by the version number. The authoritative, machine-readable
list is [`tools/api_surface.yaml`](../../tools/api_surface.yaml); this document does not repeat it.

1. **Addon-author Python API** - public (non-underscore) classes, methods, functions and
   `UPPER_CASE` constants of the lib modules that plugins and modules import, including
   `SmartPlugin`, `SmartDevicePlugin` (SDP), `MqttPlugin`, `Item`/`Items`, `Utils`, `Shtime`,
   `lib.constants` and `lib.metadata`. For classes, `__init__` and `__call__` signatures count.
2. **User-facing configuration** - the parameters declared in `modules/*/module.yaml`
   (the keys users write into `etc/*.yaml`), the command line flags of `bin/smarthome.py`, the item
   attributes catalogued in `modules/core/items.yaml`, struct syntax and the logic-script
   namespace. A core test keeps the catalog in step with the attribute keys in `lib/constants.py`.
3. **smartVISU websocket protocol** - the commands accepted and sent by
   `modules/websocket/smartvisu.py`. Third-party visualisations depend on it.

### Not public API *(decided)*

- Names starting with an underscore, and modules whose file name starts with an underscore
  (e.g. `lib/item/_internal/`).
- The admin REST API and the admin websocket protocol. Their only client is the first-party
  shngadmin.
- Web interface assets and templates, `tools/`, `tests/`, log message texts.
- Third-party dependency pins in `requirements.txt`.
- The supported Python range (see below: it is a support policy, not API).

## Version numbers

| Component | Scheme |
|---|---|
| Core | `X.Y.Z`; `develop` carries a pre-release `X.Y.Z-dev.N` until the release; `release.sh` sets `-dev.0` (no change since the release, only the bump) right after a release, and `N` is raised by hand when a plugin needs a specific development state *(decided)* |
| Plugins, modules | `X.Y.Z` in `plugin.yaml`/`module.yaml`, identical to `PLUGIN_VERSION` in the code |
| SmartDevicePlugin | `SDP_VERSION`, gated by `sdp_minversion` in `plugin.yaml` |

A requirement field (`sh_minversion`, `sh_maxversion`, `sdp_minversion`, `py_*`) may carry a fourth
numeric level (`1.12.2.2`) for historic reasons. It orders between `1.12.2` and `1.12.3` and is
accepted only in requirement fields, never in a component's own version.

Build metadata after `+` (commit, branch) is informative and ignored when comparing versions.

## Which change demands which bump

| Change | Bump |
|---|---|
| Removed or renamed public name; changed signature that breaks existing callers; changed parameter type; new mandatory parameter; narrowed `valid_*`; removed command line flag or websocket command | **major** |
| Raised `sh_minversion` of a plugin or module *(decided)* | **major** |
| Changed default value of a configuration parameter declared in a `module.yaml` (including the core parameters of `smarthome.yaml`) *(decided)* | **major** |
| Raised `py_minversion` *(decided)* - Python versions are dropped on the Python EOL schedule, announced in the release notes | **minor** |
| New public name, optional parameter, command line flag, websocket command, or widened `valid_*` | **minor** |
| Bug fix, internal change, documentation | **patch** |

While a component is below 1.0.0 nothing forces a major bump *(decided)*.

*(proposed)* Deprecate in a minor release (logged warning, documented in the release notes), remove
in the next major release.

Releases before 2.0.0 are not reclassified.

## Keeping the declaration, the tool and the code in sync

`tools/api_surface.yaml` is the single source of truth for the Python, configuration, CLI and
websocket surface. It is data, not code: widening or narrowing the API is a one-line edit there.
The tool derives everything from the surface file and the git history, so there is no snapshot file
to keep up to date.

```bash
# what does the current work demand relative to the last release?
tools/api_snapshot.py diff v2.0.0 HEAD

# release notes section (Markdown), grouped into Breaking / Needs review / Additions
tools/api_snapshot.py diff v2.0.0 v2.1.0 --format markdown

# gate: exit code 1 if the changes require a major bump
tools/api_snapshot.py diff origin/develop HEAD --fail-on major
```

Per commit or change set:

1. Run the diff against the base (`origin/develop` or the last release tag).
2. If the surface itself changed (new module exposed to plugins, new config file), edit
   `tools/api_surface.yaml` in the same commit and update this document if the *categories* change.
3. Bump the version of every touched component to at least the level the diff reports. A `review`
   result is a judgement call: a constant's value or a parameter default changed, and only a human
   knows whether callers can notice.
4. At release time, generate the Markdown report and add it to the release notes.

## Enforcement

`tools/check_versions.py` checks the version numbers; the pre-push hooks run it on what a push
would publish (the remote tip to the local tip, or the fork point from `origin/develop` for a new
branch):

- **Plugins** (`plugins` repo hook): for every plugin with changes - the version is valid semver
  `X.Y.Z` and equals `PLUGIN_VERSION`; it is higher than before if shipped files changed (tests,
  `*.rst`, `*.md` and `_pv_*` do not count); it is bumped at least as far as the `plugin.yaml` diff
  demands (`parameters`, `item_attributes`, `logic_parameters`, `plugin_functions`,
  `item_structs`, and the `sh_/py_/sdp_` min/max versions); `sh_minversion` is not above the core
  version.
- **Core** (`shng` repo hook): `shNG_version` is valid semver, did not go down, and is high enough
  for the API changes since the last `vX.Y.Z` release tag.

Errors block the push. `review` results are printed as warnings.

```bash
# the same check by hand
tools/check_versions.py core --base origin/develop
tools/check_versions.py plugins --repo plugins --base origin/develop

# write the demanded plugin bumps into plugin.yaml and PLUGIN_VERSION (working tree, uncommitted)
tools/check_versions.py plugins --repo plugins --base origin/develop --fix
```

`--fix` resolves the errors a version bump resolves ("not bumped", "bump too small"): it sets the
version to the base version raised by the demanded level, keeping quotes, comments and the layout of
`PLUGIN_VERSION`. It refuses files with uncommitted changes. Review and commit the result, then run
the check again. Invalid versions, a version that went down, mismatches between `plugin.yaml` and
`PLUGIN_VERSION`, and `sh_minversion` above the core version have to be fixed by hand.

Deliberate exceptions, e.g. the release commit that resets `sh_minversion` everywhere: put
`no-version-bump: <plugin>[, <plugin>...]` or `no-version-bump: core` as a line in a commit message
of the pushed range, or push with `--no-verify`. `--warn-only` reports errors but exits 0.

The core hook is versioned in `.githooks/`. The plugins hook is generated: re-run
`tools/install-hooks.sh` after updating.

## Limits of the tool

- Whether a plugin change deserves a patch or a minor bump beyond what its `plugin.yaml` shows is
  not decidable by the tool; it only enforces the minimum.
- Static analysis only (`ast` and YAML): behaviour changes with an unchanged signature are
  invisible, e.g. a different value passed to callers, changed timing, or a stricter check.
- Base classes are resolved by simple class name within the surface; two unrelated classes with the
  same name in different modules can be confused for inheritance.
- Websocket commands are found by the patterns `command == '<name>'` and `'cmd': '<name>'`; payload
  changes are not detected.
- Item attributes are covered by name, type and valid values as catalogued in `items.yaml`, not by
  their semantics.
