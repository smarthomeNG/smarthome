#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Snapshot of the SmartHomeNG public API surface and semver-level diff of two snapshots.

The surface is the set of names an addon author or user can depend on (see
doc/dev/public_api.md). The analysis is static - nothing from the analysed tree is
imported or executed.
"""

import ast
import argparse
import enum
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Callable
from typing import NamedTuple, TypeAlias, TypedDict

from ruamel import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.utils import Version  # noqa: E402

JsonValue: TypeAlias = str | int | float | bool | None | list['JsonValue'] | dict[str, 'JsonValue']
Snapshot: TypeAlias = dict[str, JsonValue]

DEFAULT_SURFACE = Path(__file__).with_name('api_surface.yaml')


class Level(enum.IntEnum):
    """Minimum version bump a change demands; the value orders reports by severity."""

    MAJOR = 0
    REVIEW = 1
    MINOR = 2


class Change(NamedTuple):
    """One difference between two snapshots."""

    level: Level
    key: str
    reason: str


@dataclass
class Surface:
    """Which files make up the public API."""

    python_globs: list[str] = field(default_factory=list)
    parameter_globs: list[str] = field(default_factory=list)  # module.yaml files declaring config parameters
    item_attribute_globs: list[str] = field(default_factory=list)  # YAML files declaring item attributes
    plugin_metadata_globs: list[str] = field(default_factory=list)  # plugin.yaml files of addons
    cli_file: str | None = None  # script defining the command line with argparse
    websocket_file: str | None = None  # websocket protocol handler dispatching on `command == '<name>'`

    @classmethod
    def load(cls, path: Path) -> 'Surface':
        """Read a surface declaration (YAML mapping of the field names above)."""
        declared = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        unknown = set(declared) - set(cls.__dataclass_fields__)
        if unknown:
            raise ValueError(f'{path}: unknown surface keys {sorted(unknown)}')
        return cls(**declared)

    def top_level_dirs(self) -> list[str]:
        """Repository directories holding surface files, for a partial checkout."""
        patterns = [
            *self.python_globs,
            *self.parameter_globs,
            *self.item_attribute_globs,
            *self.plugin_metadata_globs,
            *(f for f in (self.cli_file, self.websocket_file) if f),
        ]
        return sorted({pattern.split('/')[0] for pattern in patterns})


_API_DUNDERS = ('__init__', '__call__')  # the only special methods whose signature callers depend on


def _is_public(name: str) -> bool:
    return not name.startswith('_') or name in _API_DUNDERS


class Signature(TypedDict):
    """Call interface of a public callable."""

    kind: str  # 'method', 'property', 'classmethod' or 'staticmethod'
    is_async: bool
    positional: list[str]  # without self/cls
    first_optional: int  # index into positional of the first parameter with a default
    keyword_only: dict[str, bool]  # name -> has a default
    var_positional: bool
    var_keyword: bool


_DECORATOR_KINDS = {'property': 'property', 'classmethod': 'classmethod', 'staticmethod': 'staticmethod'}


def _kind(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    for decorator in fn.decorator_list:
        text = ast.unparse(decorator)
        if text in _DECORATOR_KINDS:
            return _DECORATOR_KINDS[text]
        if text.endswith(('.setter', '.getter', '.deleter')):
            return 'property'
    return 'method'


def _signature(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> Signature:
    """Call interface of fn."""
    args = fn.args.posonlyargs + fn.args.args
    kind = _kind(fn)
    names = [a.arg for a in args]
    if kind != 'staticmethod' and names and names[0] in ('self', 'cls'):
        names = names[1:]
    return Signature(
        kind=kind,
        is_async=isinstance(fn, ast.AsyncFunctionDef),
        positional=names,
        first_optional=len(names) - min(len(fn.args.defaults), len(names)),
        keyword_only={a.arg: d is not None for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults)},
        var_positional=fn.args.vararg is not None,
        var_keyword=fn.args.kwarg is not None,
    )


def _diff_signature(old: Signature, new: Signature) -> tuple[Level, str] | None:
    """Level and reason of the most severe signature change, None if callers are unaffected."""
    found: list[tuple[Level, str]] = []
    if old['kind'] != new['kind']:
        found.append((Level.MAJOR, f'changed from {old["kind"]} to {new["kind"]}'))
    if old['is_async'] != new['is_async']:
        found.append((Level.MAJOR, 'sync/async changed'))
    for i, name in enumerate(old['positional']):
        if i >= len(new['positional']) or new['positional'][i] != name:
            found.append((Level.MAJOR, f"positional parameter '{name}' removed, renamed or reordered"))
            break
        if i >= old['first_optional'] and i < new['first_optional']:
            found.append((Level.MAJOR, f"parameter '{name}' became required"))
    for i in range(len(old['positional']), len(new['positional'])):
        required = i < new['first_optional']
        found.append(
            (Level.MAJOR if required else Level.MINOR, f'new {"required" if required else "optional"} parameter')
        )
    for name, has_default in old['keyword_only'].items():
        if name in new['keyword_only']:
            if has_default and not new['keyword_only'][name]:
                found.append((Level.MAJOR, f"keyword-only parameter '{name}' became required"))
        elif name not in new['positional'] and not new['var_keyword']:
            found.append((Level.MAJOR, f"keyword-only parameter '{name}' removed"))
    for name, has_default in new['keyword_only'].items():
        if name not in old['keyword_only']:
            found.append((Level.MINOR if has_default else Level.MAJOR, f"new keyword-only parameter '{name}'"))
    for flag, label in (('var_positional', '*args'), ('var_keyword', '**kwargs')):
        if old[flag] and not new[flag]:
            found.append((Level.MAJOR, f'{label} removed'))
        elif new[flag] and not old[flag]:
            found.append((Level.MINOR, f'{label} added'))
    return min(found) if found else None


@dataclass
class _ClassInfo:
    module: str
    bases: list[str]
    members: dict[str, Signature]


def _find_base(base: str, module: str, classes: dict[tuple[str, str], _ClassInfo]) -> tuple[str, str] | None:
    """Locate a base class by its simple name, preferring the class's own module."""
    name = base.split('.')[-1]
    if (module, name) in classes:
        return module, name
    return next((key for key in sorted(classes) if key[1] == name), None)


def _effective_members(
    key: tuple[str, str], classes: dict[tuple[str, str], _ClassInfo], seen: tuple[tuple[str, str], ...] = ()
) -> dict[str, Signature]:
    """Public members of a class including those inherited from classes within the surface."""
    info = classes[key]
    members: dict[str, Signature] = {}
    for base in reversed(info.bases):
        base_key = _find_base(base, info.module, classes)
        if base_key and base_key != key and base_key not in seen:
            members.update(_effective_members(base_key, classes, seen + (key,)))
    members.update(info.members)
    return members


def _is_constant(name: str) -> bool:
    return name.isupper() and _is_public(name)


def _jsonable(value: object) -> JsonValue:
    """Convert a literal into its JSON form; tuples and sets become lists."""
    if isinstance(value, (tuple, set, frozenset, list)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return value if isinstance(value, (str, int, float, bool, type(None))) else repr(value)


def _literal(node: ast.expr) -> JsonValue:
    """Value of a literal expression, None for anything computed."""
    try:
        return _jsonable(ast.literal_eval(node))
    except (ValueError, SyntaxError, TypeError):
        return None


def _is_private_module(path: Path) -> bool:
    return path.name.startswith('_') and path.name != '__init__.py'


def _parse(path: Path) -> ast.Module:
    """Parse a source file; syntax warnings of the analysed code are not ours to report."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return ast.parse(path.read_text(encoding='utf-8'))


def snapshot(root: Path, surface: Surface) -> Snapshot:
    """Return the public API entries of the source tree at root."""
    classes: dict[tuple[str, str], _ClassInfo] = {}
    snap: Snapshot = {}
    for path in sorted({p for pattern in surface.python_globs for p in root.glob(pattern)}):
        if _is_private_module(path):
            continue
        module = str(path.relative_to(root)).removesuffix('.py')
        tree = _parse(path)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and _is_public(node.name):
                members = {
                    sub.name: _signature(sub)
                    for sub in node.body
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(sub.name)
                }
                classes[(module, node.name)] = _ClassInfo(module, [ast.unparse(b) for b in node.bases], members)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(node.name):
                snap[f'function:{module}:{node.name}'] = _signature(node)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and _is_constant(target.id):
                        snap[f'constant:{module}:{target.id}'] = _literal(node.value)
    for key in classes:
        for member, signature in _effective_members(key, classes).items():
            snap[f'member:{key[0]}:{key[1]}.{member}'] = signature
    _collect_declared(root, surface.parameter_globs, 'parameters', 'parameter', snap)
    _collect_declared(root, surface.item_attribute_globs, 'item_attributes', 'item_attribute', snap)
    _collect_plugin_metadata(root, surface.plugin_metadata_globs, snap)
    _collect_cli(root, surface, snap)
    _collect_websocket(root, surface, snap)
    return snap


def _collect_declared(root: Path, globs: list[str], section: str, kind: str, snap: Snapshot) -> None:
    """Record the entries of a metadata section (`parameters:`, `item_attributes:`) of YAML files."""
    for path in sorted({p for pattern in globs for p in root.glob(pattern)}):
        declared = (yaml.safe_load(path.read_text(encoding='utf-8')) or {}).get(section) or {}
        for name, spec in declared.items():
            snap[f'{kind}:{path.parent.name}:{name}'] = _parameter(spec if isinstance(spec, dict) else {})


def _collect_cli(root: Path, surface: Surface, snap: Snapshot) -> None:
    """Record every option string passed to add_argument() in the command line script."""
    if surface.cli_file is None or not (root / surface.cli_file).exists():
        return
    tree = _parse(root / surface.cli_file)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    snap[f'cli:{arg.value}'] = None


def _collect_websocket(root: Path, surface: Surface, snap: Snapshot) -> None:
    """Record the commands a websocket handler accepts (`command == 'x'`) and sends (`'cmd': 'x'`)."""
    if surface.websocket_file is None or not (root / surface.websocket_file).exists():
        return
    text = (root / surface.websocket_file).read_text(encoding='utf-8')
    for name in re.findall(r"command\s*==\s*'(\w+)'", text):
        snap[f'websocket-in:{name}'] = None
    for name in re.findall(r"'cmd':\s*'(\w+)'", text):
        snap[f'websocket-out:{name}'] = None


class Parameter(TypedDict):
    """A configuration parameter as declared in a module.yaml."""

    type: str | None
    mandatory: bool
    default: JsonValue
    valid_list: list[JsonValue] | None
    valid_min: int | float | None
    valid_max: int | float | None


def _parameter(spec: dict[str, JsonValue]) -> Parameter:
    return Parameter(
        type=spec.get('type'),
        mandatory=bool(spec.get('mandatory', False)),
        default=spec.get('default'),
        valid_list=spec.get('valid_list'),
        valid_min=spec.get('valid_min'),
        valid_max=spec.get('valid_max'),
    )


def _diff_parameter(old: Parameter, new: Parameter) -> tuple[Level, str] | None:
    """Level and reason of the most severe change to a configuration parameter."""
    found: list[tuple[Level, str]] = []
    if old['type'] != new['type']:
        found.append((Level.MAJOR, f'type {old["type"]} -> {new["type"]}'))
    if new['mandatory'] and not old['mandatory']:
        found.append((Level.MAJOR, 'became mandatory'))
    old_list, new_list = old['valid_list'], new['valid_list']
    if old_list is not None and new_list is not None:
        if set(map(str, old_list)) - set(map(str, new_list)):
            found.append((Level.MAJOR, 'valid_list values removed'))
        elif set(map(str, new_list)) - set(map(str, old_list)):
            found.append((Level.MINOR, 'valid_list values added'))
    elif old_list is None and new_list is not None:
        found.append((Level.MAJOR, 'valid_list restricts the values'))
    for bound, narrower in (('valid_min', lambda o, n: n > o), ('valid_max', lambda o, n: n < o)):
        if (
            old[bound] is None
            and new[bound] is not None
            or (old[bound] is not None and new[bound] is not None and narrower(old[bound], new[bound]))
        ):
            found.append((Level.MAJOR, f'{bound} narrowed'))
        elif new[bound] != old[bound]:
            found.append((Level.MINOR, f'{bound} widened'))
    if old['default'] != new['default']:
        found.append((Level.REVIEW, f'default {old["default"]!r} -> {new["default"]!r}'))
    return min(found) if found else None


def _added_parameter(new: Parameter) -> tuple[Level, str]:
    """A new parameter breaks existing configurations only if it is mandatory."""
    return (Level.MAJOR, 'added as mandatory') if new['mandatory'] else (Level.MINOR, 'added')


def snapshot_ref(repo: Path, ref: str, surface: Surface) -> Snapshot:
    """Return the snapshot of the surface as committed at a git ref, independent of the working tree."""
    tracked = subprocess.run(
        ['git', '-C', str(repo), 'ls-tree', '--name-only', ref], check=True, capture_output=True, text=True
    ).stdout.split()
    wanted = [name for name in surface.top_level_dirs() if name in tracked]
    if not wanted:
        return {}
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(
            ['git', '-C', str(repo), 'archive', ref, '--', *wanted], check=True, capture_output=True
        ).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(tmp, filter='data')
        return snapshot(Path(tmp), surface)


class PluginFunction(Signature):
    """A function a plugin offers to logics, as declared in plugin.yaml."""

    returns: str | None


class Requirement(TypedDict):
    """A version bound a plugin.yaml puts on SmartHomeNG, Python or the SmartDevicePlugin framework."""

    field: str
    value: str  # '' if the bound is not declared


# field -> (bump level of tightening the bound, whether it is a 'min' or 'max' bound)
_REQUIREMENTS = {
    'sh_minversion': (Level.MAJOR, 'min'),
    'sdp_minversion': (Level.MAJOR, 'min'),
    'py_minversion': (Level.MINOR, 'min'),
    'sh_maxversion': (Level.MAJOR, 'max'),
    'sdp_maxversion': (Level.MAJOR, 'max'),
    'py_maxversion': (Level.MINOR, 'max'),
}
# plugin.yaml sections declaring name -> parameter-like spec, and the snapshot kind they produce
_PLUGIN_SPEC_SECTIONS = {
    'parameters': 'parameter',
    'item_attributes': 'item_attribute',
    'logic_parameters': 'logic_parameter',
}


def _section(data: dict[str, JsonValue], name: str) -> dict[str, JsonValue]:
    """A metadata section as a dict; plugins write NONE (or nothing) for an empty one."""
    value = data.get(name)
    return value if isinstance(value, dict) else {}


def _plugin_function(spec: dict[str, JsonValue]) -> PluginFunction:
    declared = spec.get('parameters')
    params = declared if isinstance(declared, dict) else {}

    def optional(p: JsonValue) -> bool:
        return isinstance(p, dict) and ('default' in p or p.get('optional') is True or p.get('mandatory') is False)

    names = list(params)
    first_optional = next((i for i, n in enumerate(names) if optional(params[n])), len(names))
    return PluginFunction(
        kind='method',
        is_async=False,
        positional=names,
        first_optional=first_optional,
        keyword_only={},
        var_positional=False,
        var_keyword=False,
        returns=spec.get('type'),
    )


def _collect_plugin_metadata(root: Path, globs: list[str], snap: Snapshot) -> None:
    """Record what plugin.yaml files declare: config, item attributes, logic parameters, functions, structs, bounds."""
    for path in sorted({p for pattern in globs for p in root.glob(pattern)}):
        data = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
        plugin = path.parent.name
        for section, kind in _PLUGIN_SPEC_SECTIONS.items():
            for name, spec in _section(data, section).items():
                snap[f'{kind}:{plugin}:{name}'] = _parameter(spec if isinstance(spec, dict) else {})
        for name, spec in _section(data, 'plugin_functions').items():
            snap[f'plugin_function:{plugin}:{name}'] = _plugin_function(spec if isinstance(spec, dict) else {})
        for name in _section(data, 'item_structs'):
            snap[f'item_struct:{plugin}:{name}'] = None
        declared = _section(data, 'plugin')
        for requirement in _REQUIREMENTS:
            snap[f'requirement:{plugin}:{requirement}'] = Requirement(
                field=requirement, value=str(declared.get(requirement) or '')
            )


def _diff_plugin_function(old: PluginFunction, new: PluginFunction) -> tuple[Level, str] | None:
    """A plugin function is changed incompatibly if callers' arguments or the result type change."""
    found = [r for r in (_diff_signature(old, new),) if r]
    if old['returns'] != new['returns']:
        found.append((Level.MAJOR, f'return type {old["returns"]} -> {new["returns"]}'))
    return min(found) if found else None


def _diff_requirement(old: Requirement, new: Requirement) -> tuple[Level, str] | None:
    """Level and reason if a version bound got tighter; relaxing a bound is compatible."""
    level, direction = _REQUIREMENTS[old['field']]
    before, after = old['value'], new['value']
    if direction == 'min':
        tighter = after != '' and (before == '' or Version.compare(after, before, '>'))
    else:
        tighter = after != '' and (before == '' or Version.compare(after, before, '<'))
    return (level, f'{old["field"]} {before or "(none)"} -> {after}') if tighter else None


def _diff_constant(old: JsonValue, new: JsonValue) -> tuple[Level, str] | None:
    """Level and reason of a literal constant change; order of list items is not significant."""
    if isinstance(old, dict) and isinstance(new, dict):
        if set(old) - set(new):
            return Level.MAJOR, f'keys removed: {sorted(set(old) - set(new))}'
        changed = sorted(k for k in old if old[k] != new[k])
        if changed:
            return Level.REVIEW, f'values changed: {changed}'
        return (Level.MINOR, f'keys added: {sorted(set(new) - set(old))}') if set(new) - set(old) else None
    if isinstance(old, list) and isinstance(new, list):
        old_items, new_items = (
            {json.dumps(i, sort_keys=True) for i in old},
            {json.dumps(i, sort_keys=True) for i in new},
        )
        if old_items - new_items:
            return Level.MAJOR, 'items removed'
        return (Level.MINOR, 'items added') if new_items - old_items else None
    return None if old == new else (Level.REVIEW, f'{old!r} -> {new!r}')


_DIFFERS: dict[str, Callable[[JsonValue, JsonValue], tuple[Level, str] | None]] = {
    'member': _diff_signature,
    'function': _diff_signature,
    'constant': _diff_constant,
    'parameter': _diff_parameter,
    'item_attribute': _diff_parameter,
    'logic_parameter': _diff_parameter,
    'plugin_function': _diff_plugin_function,
    'requirement': _diff_requirement,
}
_ADDERS: dict[str, Callable[[JsonValue], tuple[Level, str]]] = {
    'parameter': _added_parameter,
    'logic_parameter': _added_parameter,
}


def diff(old: Snapshot, new: Snapshot) -> list[Change]:
    """Return the changes from old to new, most severe first."""
    changes = [Change(Level.MAJOR, key, 'removed') for key in set(old) - set(new)]
    for key in set(new) - set(old):
        adder = _ADDERS.get(key.split(':', 1)[0])
        level, reason = adder(new[key]) if adder else (Level.MINOR, 'added')
        changes.append(Change(level, key, reason))
    for key in set(old) & set(new):
        differ = _DIFFERS.get(key.split(':', 1)[0])
        result = differ(old[key], new[key]) if differ else None
        if result:
            changes.append(Change(result[0], key, result[1]))
    return sorted(changes, key=lambda c: (c.level, c.key))


_BUMPS = {Level.MAJOR: 'major', Level.REVIEW: 'review', Level.MINOR: 'minor'}
_HEADINGS = {Level.MAJOR: 'Breaking (major)', Level.REVIEW: 'Needs review', Level.MINOR: 'Additions (minor)'}


def required_bump(changes: list[Change]) -> str:
    """Minimum version bump the changes demand: 'major', 'review' (human decision), 'minor' or 'patch'."""
    return _BUMPS[min((c.level for c in changes), default=None)] if changes else 'patch'


def format_text(changes: list[Change]) -> str:
    """One line per change, followed by the required bump."""
    lines = [f'{c.level.name:7} {c.key}  [{c.reason}]' for c in changes]
    return '\n'.join([*lines, f'required bump: {required_bump(changes)}']) + '\n'


def format_markdown(changes: list[Change]) -> str:
    """Changes grouped by severity, for release notes."""
    parts = []
    for level, heading in _HEADINGS.items():
        group = [c for c in changes if c.level == level]
        if group:
            parts.append(f'### {heading}\n\n' + ''.join(f'- `{c.key}`: {c.reason}\n' for c in group))
    return '\n'.join(parts) or 'No API changes.\n'


def _snapshot_of(source: str, repo: Path, surface: Surface) -> Snapshot:
    """Snapshot a directory if source is one, otherwise the git ref of that name."""
    return snapshot(Path(source), surface) if Path(source).is_dir() else snapshot_ref(repo, source, surface)


def main(argv: list[str]) -> int:
    """Command line entry; returns the process exit code."""
    parser = argparse.ArgumentParser(description='Diff the SmartHomeNG public API between two git refs or directories.')
    parser.add_argument('command', choices=['diff'])
    parser.add_argument('old', help='git ref or directory')
    parser.add_argument('new', help='git ref or directory')
    parser.add_argument('--repo', type=Path, default=Path.cwd(), help='git repository for refs (default: cwd)')
    parser.add_argument('--surface', type=Path, default=DEFAULT_SURFACE, help='surface declaration (YAML)')
    parser.add_argument('--format', choices=['text', 'markdown'], default='text')
    parser.add_argument('--fail-on', choices=['major', 'review'], help='exit 1 if the changes demand at least this')
    args = parser.parse_args(argv)
    surface = Surface.load(args.surface)
    changes = diff(_snapshot_of(args.old, args.repo, surface), _snapshot_of(args.new, args.repo, surface))
    print((format_markdown if args.format == 'markdown' else format_text)(changes), end='')
    severity = {'major': (Level.MAJOR,), 'review': (Level.MAJOR, Level.REVIEW)}
    return int(bool(args.fail_on) and any(c.level in severity[args.fail_on] for c in changes))


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
