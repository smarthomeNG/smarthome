#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Finds (and with ``--fix`` repairs) configuration that does not work with SmartHomeNG 2.0.

The checks look at the user configuration of one installation (``etc/plugin.yaml``, the item, struct, logic,
function and scene files). Without ``--fix`` nothing is changed. With ``--fix`` every changed file is first
copied to ``etc/upgrade_check_backup/<timestamp>/``.

Checks:

``instances``
    Plugin instance names: since 2.0 the name of a ``plugin.yaml`` section is the instance name of a plugin
    that is used by several sections. A section without ``instance:`` gets ``instance: default`` so that it
    keeps the empty instance; item attributes ``attr@old`` are renamed to the new instance name.
``plugin-alias``
    ``sh.<section>`` accesses to plugins become ``sh.plugins.<section>``.
``plugin-class``
    ``class_name`` / ``class_path`` in ``plugin.yaml`` become ``plugin_name`` (and ``plugin_version``).
``removed-api``
    Methods of the ``sh`` object that are removed (``sh.return_item()``, ``sh.now()``, ``sh.base_dir``, ...).
``scenes``
    Scene definitions in the old ``.conf`` format become ``.yaml`` files.
"""

import argparse
import ast
import csv
import functools
import io
import json
import re
import shutil
import sys
import time
import tokenize
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Protocol

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib.shyaml as shyaml  # noqa: E402
from ruamel import yaml as ruamel_yaml  # noqa: E402
from ruamel.yaml.scalarstring import DoubleQuotedScalarString  # noqa: E402

BACKUP_DIR = 'upgrade_check_backup'

#: removed ``sh`` methods and the sub-object that replaces them
SH_METHOD_HOMES: dict[str, str] = {
    **dict.fromkeys(('add_item', 'return_item', 'return_items', 'match_items', 'find_items', 'find_children'), 'items'),
    **dict.fromkeys(('return_modules', 'get_module'), 'modules'),
    'return_plugins': 'plugins',
    **dict.fromkeys(('reload_logics', 'return_logic', 'return_logics'), 'logics'),
    **dict.fromkeys(('now', 'tzinfo', 'utcnow', 'utcinfo', 'runtime'), 'shtime'),
}


#: top level items that the core itself creates (``lib/env/*.yaml``)
CORE_TOP_LEVEL_ITEMS = frozenset({'env'})


@functools.lru_cache(maxsize=1)
def smarthome_attribute_names() -> frozenset[str]:
    """Names of the class members and instance attributes of ``SmartHome``, read from ``lib/smarthome.py``."""
    tree = ast.parse((Path(__file__).resolve().parent.parent / 'lib' / 'smarthome.py').read_text(encoding='utf-8'))
    smarthome = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'SmartHome')
    names = set()
    for node in smarthome.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    for node in ast.walk(smarthome):
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            if isinstance(node.value, ast.Name) and node.value.id == 'self':
                names.add(node.attr)
    return frozenset(n for n in names if not n.startswith('__'))


def reserved_sh_names() -> frozenset[str]:
    """Names a plugin section cannot claim on ``sh``: members of ``SmartHome``, removed methods, core items."""
    return smarthome_attribute_names() | SH_METHOD_HOMES.keys() | CORE_TOP_LEVEL_ITEMS


#: removed ``sh.tools`` functions that have no automatic replacement, with the hint what to use
SH_TOOLS_HINTS: dict[str, str] = {
    'ping': "Network.ping(host) from 'lib.network'",
    'dewpoint': "Utils.dewpoint(t, rf) from 'lib.utils'",
    'rel2abs': "Utils.rel2abs(t, rf) from 'lib.utils'",
    'abs2rel': "Utils.abs2rel(t, ah) from 'lib.utils'",
    'fetch_url': "Http().get_binary(url, require_ok=True) from 'lib.network'",
    'dt2ts': 'dt.timestamp()',
    'dt2js': 'dt.timestamp() * 1000',
}


@dataclass(frozen=True)
class Finding:
    """One problem found in the configuration."""

    checker: str
    path: Path
    message: str
    line: int | None = None
    #: the change can be made by ``--fix``
    fixable: bool = True
    #: the change has been made
    fixed: bool = False

    def as_dict(self, base: Path) -> dict:
        """The finding as a JSON serializable dict, with the path relative to *base*."""
        try:
            path = str(self.path.relative_to(base))
        except ValueError:
            path = str(self.path)
        return {
            'checker': self.checker,
            'path': path,
            'line': self.line,
            'message': self.message,
            'fixable': self.fixable,
            'fixed': self.fixed,
        }


class Project:
    """
    The configuration of one SmartHomeNG installation

    :param base: base directory of the installation
    """

    def __init__(self, base: Path):
        self.base = base
        self.etc = base / 'etc'
        self.plugins_dir = base / 'plugins'
        self._stamp = time.strftime('%Y%m%d-%H%M%S')
        self._backed_up: set[Path] = set()

    @property
    def plugin_yaml(self) -> Path:
        """Path of the plugin configuration."""
        return self.etc / 'plugin.yaml'

    def config_dir(self, name: str) -> Path:
        """The directory below ``etc`` if it exists, else the legacy directory in the base directory."""
        below_etc = self.etc / name
        return below_etc if below_etc.is_dir() else self.base / name

    def files(self, directory: str, pattern: str) -> list[Path]:
        """The files matching *pattern* in a configuration directory, sorted."""
        return sorted(self.config_dir(directory).glob(pattern))

    def item_files(self) -> list[Path]:
        """Item and struct definition files."""
        return self.files('items', '*.yaml') + self.files('structs', '*.yaml')

    def code_files(self) -> list[Path]:
        """Python files of logics and user functions."""
        return self.files('logics', '*.py') + self.files('functions', '*.py')

    def backup(self, path: Path) -> None:
        """Copy *path* to the backup directory, once per run."""
        if path in self._backed_up or not path.exists():
            return
        self._backed_up.add(path)
        try:
            relative = path.relative_to(self.base)
        except ValueError:
            relative = Path(path.name)
        target = self.etc / BACKUP_DIR / self._stamp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)

    def write_text(self, path: Path, text: str) -> None:
        """Write *text* to *path* after backing up the old content."""
        self.backup(path)
        path.write_text(text, encoding='utf-8', errors='surrogateescape')

    def remove(self, path: Path) -> None:
        """Delete *path* after backing it up."""
        self.backup(path)
        path.unlink()


class Checker(Protocol):
    """A check of the configuration; checkers register themselves with :func:`register`."""

    name: ClassVar[str]
    description: ClassVar[str]

    def run(self, project: Project, fix: bool) -> list[Finding]:
        """Find the problems; with *fix* also repair them and report them as fixed."""
        ...


CHECKERS: dict[str, Checker] = {}


def register(cls: type) -> type:
    """Class decorator adding an instance of a checker class to :data:`CHECKERS`."""
    CHECKERS[cls.name] = cls()
    return cls


def read_text(path: Path) -> str:
    """The text of a file."""
    return path.read_text(encoding='utf-8', errors='surrogateescape')


def load_plugin_sections(project: Project) -> dict[str, dict] | None:
    """The sections of ``plugin.yaml``, or None if the file does not exist or is not readable."""
    if not project.plugin_yaml.is_file():
        return None
    try:
        return shyaml.yaml_load_roundtrip(str(project.plugin_yaml), raise_on_error=True)
    except Exception:
        return None


def is_enabled(section: Mapping) -> bool:
    """False if the section is switched off with ``plugin_enabled: false``."""
    return str(section.get('plugin_enabled', True)).strip().lower() not in ('false', '0', 'no', 'off')


def enabled_sections(sections: Mapping) -> dict[str, Mapping]:
    """The enabled plugin sections by name; entries that are not mappings are skipped."""
    return {name: s for name, s in sections.items() if isinstance(s, Mapping) and is_enabled(s)}


def plugin_name_of(section: Mapping) -> str:
    """The lowercase plugin name of a section."""
    return str(section.get('plugin_name') or '').strip().lower()


def code_tokens(text: str) -> list[tokenize.TokenInfo]:
    """The Python tokens of *text*, without whitespace and comments."""
    ignored = {tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT, tokenize.ENDMARKER}
    return [t for t in tokenize.generate_tokens(io.StringIO(text).readline) if t.type not in ignored]


def sh_accesses(tokens: list[tokenize.TokenInfo]) -> Iterator[tuple[int, list[tokenize.TokenInfo]]]:
    """Yield the index of every ``sh`` name token (not preceded by a dot) with the tokens of its attribute chain."""
    for i, token in enumerate(tokens):
        if token.type != tokenize.NAME or token.string != 'sh':
            continue
        if i > 0 and tokens[i - 1].string == '.':
            continue
        chain = []
        j = i + 1
        while j + 1 < len(tokens) and tokens[j].string == '.' and tokens[j + 1].type == tokenize.NAME:
            chain.append(tokens[j + 1])
            j += 2
        if chain:
            yield i, chain


def apply_edits(text: str, edits: Iterable[tuple[int, int, int, str]]) -> str:
    """
    Apply replacements to *text*

    :param edits: ``(row, start column, end column, replacement)``; rows count from 1
    """
    lines = text.splitlines(keepends=True)
    for row, start, end, replacement in sorted(edits, reverse=True):
        line = lines[row - 1]
        lines[row - 1] = line[:start] + replacement + line[end:]
    return ''.join(lines)


def rewrite_code(text: str, plan: Callable[[list[tokenize.TokenInfo]], list[tuple[tokenize.TokenInfo, str, str]]]):
    """
    Plan and apply token replacements in Python code

    :param plan: gets the tokens of an ``sh`` chain and returns ``(token, replacement, message)`` triples
    :return: the new text and the planned ``(row, message)`` pairs; tokenizing errors yield no changes
    """
    try:
        tokens = code_tokens(text)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return text, []
    edits, notes = [], []
    for _, chain in sh_accesses(tokens):
        for token, replacement, message in plan(chain):
            notes.append((token.start[0], message))
            if replacement is not None:
                edits.append((token.start[0], token.start[1], token.end[1], replacement))
    return apply_edits(text, edits), notes


def rewrite_text(text: str, pattern: re.Pattern, replacement: str) -> tuple[str, list[tuple[int, str]]]:
    """Regex replacement over a text file; returns the new text and the ``(line, matched text)`` pairs."""
    notes = [(text.count('\n', 0, m.start()) + 1, m.group(0)) for m in pattern.finditer(text)]
    return pattern.sub(replacement, text), notes


@register
class InstancesChecker:
    """Instance names of plugins that are used by several ``plugin.yaml`` sections."""

    name = 'instances'
    description = 'plugin instance names (section names instead of instance:)'

    ITEM_KEY = re.compile(r'^(?P<head>\s*(?:-\s+)?)(?P<attr>[A-Za-z0-9_.\-]+)@(?P<inst>[^\s:]+)(?P<tail>\s*:)')

    @staticmethod
    def legacy_instance(section: Mapping) -> str:
        """Instance name as determined until 1.12: the value of ``instance:``, ``default`` meaning none."""
        instance = str(section.get('instance', '')).strip()
        return '' if instance == 'default' else instance.lower()

    @staticmethod
    def new_instance(name: str, section: Mapping, count: int) -> str:
        """Instance name as determined since 2.0 for a section of a plugin that is used by *count* sections."""
        if 'default_instance' in section or section.get('instance', 'foo') == 'default' or count == 1:
            return ''
        return name.lower()

    def plugin_attributes(self, project: Project, plugin: str) -> tuple[set[str], tuple[str, ...]]:
        """Item attribute names and name prefixes that a plugin defines."""
        meta = project.plugins_dir / plugin / 'plugin.yaml'
        try:
            data = ruamel_yaml.YAML(typ='safe').load(meta.read_text(encoding='utf-8')) or {}
        except Exception:
            return set(), ()
        attributes = set((data.get('item_attributes') or {}).keys()) if isinstance(data, dict) else set()
        prefixes = tuple((data.get('item_attribute_prefixes') or {}).keys()) if isinstance(data, dict) else ()
        return attributes, prefixes

    def run(self, project: Project, fix: bool) -> list[Finding]:
        sections = load_plugin_sections(project)
        if sections is None:
            return []
        enabled = enabled_sections(sections)
        by_plugin: dict[str, list[str]] = {}
        for name, section in enabled.items():
            if plugin_name_of(section):
                by_plugin.setdefault(plugin_name_of(section), []).append(name)

        findings: list[Finding] = []
        set_default: list[str] = []
        renames: dict[str, dict[str, str]] = {}
        for plugin, names in by_plugin.items():
            seen: dict[str, str] = {}
            for name in names:
                section = enabled[name]
                legacy = self.legacy_instance(section)
                new = self.new_instance(name, section, len(names))
                if legacy in seen and legacy != '':
                    findings.append(
                        Finding(
                            self.name,
                            project.plugin_yaml,
                            f"sections '{seen[legacy]}' and '{name}' of plugin '{plugin}' use the instance '{legacy}'",
                            fixable=False,
                        )
                    )
                seen.setdefault(legacy, name)
                if legacy == new:
                    continue
                if legacy == '':
                    set_default.append(name)
                    findings.append(
                        Finding(
                            self.name,
                            project.plugin_yaml,
                            f"section '{name}' of plugin '{plugin}' would become instance '{new}'; "
                            "it gets 'instance: default' to keep the unnamed instance",
                            None,
                            True,
                            fix,
                        )
                    )
                else:
                    renames.setdefault(plugin, {})[legacy] = new
        findings += self.item_findings(project, renames, fix)
        if fix and set_default:
            self.set_default_instance(project, sections, set_default)
        return findings

    def item_findings(self, project: Project, renames: dict[str, dict[str, str]], fix: bool) -> list[Finding]:
        """Find (and with *fix* rename) item attribute keys that carry an instance whose name changes."""
        if not renames:
            return []
        attribute_owner: dict[str, str] = {}
        prefix_owner: list[tuple[str, str]] = []
        for plugin in renames:
            attributes, prefixes = self.plugin_attributes(project, plugin)
            attribute_owner.update(dict.fromkeys(attributes, plugin))
            prefix_owner += [(p, plugin) for p in prefixes]

        def owner(attribute: str) -> str | None:
            if attribute in attribute_owner:
                return attribute_owner[attribute]
            return next((plugin for prefix, plugin in prefix_owner if attribute.startswith(prefix)), None)

        findings = []
        for path in project.item_files():
            text = read_text(path)
            changed = []
            for number, line in enumerate(text.splitlines(keepends=True), 1):
                match = self.ITEM_KEY.match(line)
                plugin = owner(match['attr']) if match else None
                new = renames.get(plugin, {}).get(match['inst'].lower()) if plugin else None
                if new is None:
                    changed.append(line)
                    continue
                suffix = f'@{new}' if new else ''
                changed.append(f'{match["head"]}{match["attr"]}{suffix}{match["tail"]}{line[match.end() :]}')
                what = f'@{match["inst"]} -> {suffix or "(none)"}'
                findings.append(
                    Finding(self.name, path, f"item attribute '{match['attr']}': {what}", number, True, fix)
                )
            if fix and ''.join(changed) != text:
                project.write_text(path, ''.join(changed))
        return findings

    def set_default_instance(self, project: Project, sections: Mapping, names: list[str]) -> None:
        """Add ``instance: default`` to the sections and save ``plugin.yaml``."""
        for name in names:
            section = sections[name]
            if 'plugin_name' in section:
                section.insert(list(section.keys()).index('plugin_name') + 1, 'instance', 'default')
            else:
                section['instance'] = 'default'
        project.backup(project.plugin_yaml)
        shyaml.yaml_save_roundtrip(str(project.plugin_yaml), sections, create_backup=False)


@register
class PluginAliasChecker:
    """``sh.<section>`` plugin accesses."""

    name = 'plugin-alias'
    description = 'sh.<plugin> accesses become sh.plugins.<plugin>'

    def top_level_items(self, project: Project) -> set[str]:
        """Names of the top level items; they win over a plugin of the same name."""
        names: set[str] = set()
        for path in project.item_files():
            try:
                data = ruamel_yaml.YAML(typ='safe').load(read_text(path))
            except Exception:
                continue
            if isinstance(data, dict):
                names |= {str(k) for k, v in data.items() if isinstance(v, dict)}
        return names

    def run(self, project: Project, fix: bool) -> list[Finding]:
        sections = load_plugin_sections(project)
        if sections is None:
            return []
        names = set(enabled_sections(sections))
        blocked = names & (reserved_sh_names() | self.top_level_items(project))
        findings = [
            Finding(
                self.name,
                project.plugin_yaml,
                f"section '{name}' has the name of an item or of an attribute of sh: sh.{name} is not the plugin",
                fixable=False,
            )
            for name in sorted(blocked)
        ]
        names -= blocked
        if not names:
            return findings

        def plan(chain):
            first = chain[0]
            if first.string in names:
                return [(first, f'plugins.{first.string}', f'sh.{first.string} -> sh.plugins.{first.string}')]
            return []

        pattern = re.compile(r'(?<![\w.])sh\.(' + '|'.join(sorted(map(re.escape, names))) + r')\b')
        for path in project.code_files():
            text = read_text(path)
            new, notes = rewrite_code(text, plan)
            findings += [Finding(self.name, path, message, row, True, fix) for row, message in notes]
            if fix and new != text:
                project.write_text(path, new)
        for path in project.item_files():
            text = read_text(path)
            new, notes = rewrite_text(text, pattern, r'sh.plugins.\1')
            findings += [
                Finding(self.name, path, f'{match} -> sh.plugins.{match[3:]}', row, True, fix) for row, match in notes
            ]
            if fix and new != text:
                project.write_text(path, new)
        return findings


@register
class PluginClassChecker:
    """``class_name`` / ``class_path`` of plugin sections."""

    name = 'plugin-class'
    description = 'class_name/class_path become plugin_name (+ plugin_version)'

    CLASS_PATH = re.compile(r'^plugins\.(?P<plugin>[A-Za-z0-9_]+)(?:\._pv_(?P<version>[0-9_]+))?$')

    def run(self, project: Project, fix: bool) -> list[Finding]:
        sections = load_plugin_sections(project)
        if sections is None:
            return []
        findings: list[Finding] = []
        changed = False
        for name, section in sections.items():
            if not isinstance(section, Mapping) or not ({'class_name', 'class_path'} & set(section)):
                continue
            class_path = str(section.get('class_path') or '')
            match = self.CLASS_PATH.match(class_path)
            if not section.get('plugin_name') and not match:
                findings.append(
                    Finding(
                        self.name,
                        project.plugin_yaml,
                        f"section '{name}': class_path '{class_path}' is not a plugin below 'plugins'; "
                        "move the plugin to the plugins directory (for example as 'priv_<name>') and use plugin_name",
                        fixable=False,
                    )
                )
                continue
            if not section.get('plugin_name'):
                plugin = match['plugin']
                version = match['version'].replace('_', '.') if match['version'] else None
                if not (project.plugins_dir / plugin).is_dir():
                    findings.append(
                        Finding(
                            self.name,
                            project.plugin_yaml,
                            f"section '{name}': plugin '{plugin}' not found",
                            fixable=False,
                        )
                    )
                    continue
                message = f"section '{name}': class_path '{class_path}' -> plugin_name '{plugin}'"
                message += f" and plugin_version '{version}'" if version else ''
                if fix:
                    section.insert(0, 'plugin_name', plugin)
                    if version and 'plugin_version' not in section:
                        section.insert(1, 'plugin_version', version)
            else:
                message = f"section '{name}': class_name/class_path are ignored since 2.0 and removed"
            if fix:
                for key in ('class_name', 'class_path'):
                    section.pop(key, None)
                changed = True
            findings.append(Finding(self.name, project.plugin_yaml, message, None, True, fix))
        if fix and changed:
            project.backup(project.plugin_yaml)
            shyaml.yaml_save_roundtrip(str(project.plugin_yaml), sections, create_backup=False)
        return findings


@register
class RemovedApiChecker:
    """Removed methods of the ``sh`` object."""

    name = 'removed-api'
    description = 'removed sh.* methods (sh.return_item, sh.now, sh.base_dir, sh.tools, ...)'

    PATTERN = re.compile(r'(?<![\w.])sh\.(' + '|'.join(sorted(SH_METHOD_HOMES, key=len, reverse=True)) + r')\b')

    @staticmethod
    def plan(chain: list[tokenize.TokenInfo]) -> list[tuple[tokenize.TokenInfo, str | None, str]]:
        """Replacements for the tokens of one ``sh`` attribute chain."""
        first = chain[0]
        if first.string in SH_METHOD_HOMES:
            home = SH_METHOD_HOMES[first.string]
            return [(first, f'{home}.{first.string}', f'sh.{first.string} -> sh.{home}.{first.string}')]
        if first.string == 'getBaseDir':
            return [(first, 'get_basedir', 'sh.getBaseDir -> sh.get_basedir')]
        if first.string == 'base_dir':
            return [(first, 'get_basedir()', 'sh.base_dir -> sh.get_basedir()')]
        if first.string == 'string2bool':
            return [(first, None, "sh.string2bool: use Utils.to_bool(value) from 'lib.utils'")]
        if first.string == 'tools' and len(chain) > 1:
            function = chain[1].string
            if function == 'runtime':
                return [(first, 'shtime', 'sh.tools.runtime -> sh.shtime.runtime')]
            return [
                (first, None, f'sh.tools.{function}: use {SH_TOOLS_HINTS.get(function, "lib.utils / lib.network")}')
            ]
        return []

    def run(self, project: Project, fix: bool) -> list[Finding]:
        findings: list[Finding] = []
        for path in project.code_files():
            text = read_text(path)
            new, notes = rewrite_code(text, self.plan)
            for row, message in notes:
                automatic = '->' in message
                findings.append(Finding(self.name, path, message, row, automatic, automatic and fix))
            if fix and new != text:
                project.write_text(path, new)
        for path in project.item_files():
            text = read_text(path)
            new, notes = rewrite_text(text, self.PATTERN, lambda m: f'sh.{SH_METHOD_HOMES[m.group(1)]}.{m.group(1)}')
            findings += [
                Finding(self.name, path, f'{match} -> sh.{SH_METHOD_HOMES[match[3:]]}.{match[3:]}', row, True, fix)
                for row, match in notes
            ]
            if fix and new != text:
                project.write_text(path, new)
        return findings


@register
class ScenesChecker:
    """Scene definitions in the old ``.conf`` format."""

    name = 'scenes'
    description = 'scenes/*.conf become scenes/*.yaml'

    #: reads YAML 1.1 like SmartHomeNG does: 'on', 'no' and the like are booleans there
    PROBE: ClassVar[ruamel_yaml.YAML] = ruamel_yaml.YAML(typ='safe')
    PROBE.version = (1, 1)

    @classmethod
    def value(cls, token: str) -> int | float | str:
        """The token as number if it reads back unchanged, else as string that YAML reads back as string."""
        for convert in (int, float):
            try:
                if str(convert(token)) == token:
                    return convert(token)
            except ValueError:
                pass
        try:
            plain = isinstance(cls.PROBE.load(token), str)
        except Exception:
            plain = False
        return token if plain else DoubleQuotedScalarString(token)

    def convert(self, text: str) -> tuple[dict[int, dict], list[tuple[int, str]]]:
        """
        Convert the content of a ``.conf`` scene file

        :return: the scene as ``{state: {'actions': [...]}}`` and ``(line number, problem)`` pairs for skipped lines
        """
        scene: dict[int, dict] = {}
        problems: list[tuple[int, str]] = []
        for number, row in enumerate(csv.reader(io.StringIO(text), delimiter=' '), 1):
            if not row or row[0].startswith('#'):
                continue
            if len(row) < 3 or not row[0].strip().isdigit():
                problems.append((number, f'line is not "<state> <item> <value>": {" ".join(row)}'))
                continue
            action = {'item': row[1], 'value': self.value(row[2])}
            scene.setdefault(int(row[0]), {'actions': []})['actions'].append(action)
        return scene, problems

    def run(self, project: Project, fix: bool) -> list[Finding]:
        findings: list[Finding] = []
        for path in project.files('scenes', '*.conf'):
            target = path.with_suffix('.yaml')
            scene, problems = self.convert(read_text(path))
            findings += [Finding(self.name, path, message, number, False) for number, message in problems]
            if target.exists():
                findings.append(
                    Finding(self.name, path, f'{target.name} exists already; the .conf file is ignored', None, False)
                )
                continue
            findings.append(
                Finding(self.name, path, f'converted to {target.name}', None, bool(scene), fix and bool(scene))
            )
            if fix and scene:
                yaml = ruamel_yaml.YAML()
                yaml.indent(mapping=4, sequence=4, offset=2)
                buffer = io.StringIO()
                yaml.dump(scene, buffer)
                project.write_text(target, buffer.getvalue())
                project.remove(path)
        return findings


def run_checks(project: Project, names: Iterable[str], fix: bool) -> list[Finding]:
    """Run the named checkers and collect their findings."""
    findings: list[Finding] = []
    for name in names:
        findings += CHECKERS[name].run(project, fix)
    return findings


def format_report(findings: list[Finding], base: Path, fix: bool) -> str:
    """The findings as text, grouped by checker."""
    if not findings:
        return 'Nothing found.'
    lines = []
    for name in CHECKERS:
        group = [f for f in findings if f.checker == name]
        if not group:
            continue
        lines.append(f'{name}: {CHECKERS[name].description}')
        for f in group:
            try:
                path = f.path.relative_to(base)
            except ValueError:
                path = f.path
            where = f'{path}:{f.line}' if f.line else str(path)
            state = 'fixed' if f.fixed else ('fixable' if f.fixable else 'manual')
            lines.append(f'  [{state}] {where}: {f.message}')
    open_ = [f for f in findings if not f.fixed]
    lines.append('')
    if fix:
        lines.append(f'{len(findings) - len(open_)} fixed, {len(open_)} need manual changes or were not changed.')
    else:
        fixable = sum(1 for f in findings if f.fixable)
        lines.append(f'{len(findings)} findings, {fixable} can be fixed with --fix.')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    """Command line entry point; returns 0 if nothing is left to do, 1 if findings remain."""
    parser = argparse.ArgumentParser(description='Check the configuration for changes needed by SmartHomeNG 2.0')
    parser.add_argument(
        '--base', type=Path, default=Path(__file__).resolve().parent.parent, help='SmartHomeNG directory'
    )
    parser.add_argument(
        '--fix', action='store_true', help='repair what can be repaired (backups go to etc/%s)' % BACKUP_DIR
    )
    parser.add_argument('--only', action='append', choices=sorted(CHECKERS), help='run only this check (repeatable)')
    parser.add_argument('--list', action='store_true', help='list the checks')
    parser.add_argument('--json', action='store_true', help='print the findings as JSON')
    args = parser.parse_args(argv)

    if args.list:
        for name, checker in CHECKERS.items():
            print(f'{name:14} {checker.description}')
        return 0
    project = Project(args.base.resolve())
    findings = run_checks(project, args.only or list(CHECKERS), args.fix)
    if args.json:
        print(json.dumps([f.as_dict(project.base) for f in findings], indent=2))
    else:
        print(format_report(findings, project.base, args.fix))
    return 1 if any(not f.fixed for f in findings) else 0


if __name__ == '__main__':
    sys.exit(main())
