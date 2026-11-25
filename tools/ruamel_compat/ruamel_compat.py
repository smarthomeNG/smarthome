#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  This file is part of SmartHomeNG
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

"""
Compare how YAML files fare with different ruamel.yaml versions.

Every YAML file of a corpus goes through two pipelines with the ruamel.yaml version of the running
interpreter:

``shng``
    lib/shyaml.py as it is in this tree: ``yaml_load()`` (with and without ordering), and the round trip
    ``yaml_load_roundtrip()`` -> ``yaml_dump_roundtrip()`` that the admin interface and ``Items.create_item()``
    use to edit configuration files.
``plain``
    ruamel.yaml's own round trip (``YAML(typ='rt')``, 4 space indentation, quotes preserved) as a reference.

For each file and pipeline the run records the loaded data (type-exact), the logged warnings/errors, the
file after saving it unchanged and after one edit, whether the saved file reads back to the same data,
which comments got lost and how many lines changed. A token table records how values like ``yes``,
``1:20`` or ``010`` are read, written and read again.

Commands::

    ruamel_compat.py run [--corpus DIR ...] --out RESULT.json
        run the current interpreter's ruamel.yaml (the built-in corpus is always included)
    ruamel_compat.py compare OLD.json NEW.json
        report the differences between two runs
    ruamel_compat.py matrix VERSION [VERSION ...] [--corpus DIR ...] [--workdir DIR]
        install each ruamel.yaml version into a venv of its own below --workdir, run each one and compare
        every version with the first

Real configurations make the best corpus, e.g. ``--corpus etc --corpus plugins``; only ``.yaml`` files are
read, ``_pv_*`` and ``priv_*`` directories are skipped.
"""

import argparse
import collections
import datetime
import difflib
import io
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Any

TOOL_DIR = Path(__file__).resolve().parent
BASE_DIR = TOOL_DIR.parent.parent
BUILTIN_CORPUS = TOOL_DIR / 'corpus'

#: values whose interpretation differs between YAML 1.1 and 1.2 or between parsers
TOKENS = (
    'yes', 'Yes', 'on', 'off', 'no', 'y', 'n', 'NO', 'true', 'True', '1:20', '8:30', '08:30', '23:59:59',
    '010', '0o10', '0x1F', '1_000', '.5', '1e3', '0123', '0049123456', '1.10', '1.2.3', '1/2/3', '~', 'null',
    '2026-10-27', "'quoted'",
)  # fmt: skip

#: the result entries whose differences are reported first by compare (data, not formatting)
DATA_KEYS = ('safe', 'safe_ordered', 'data', 'reload_same', 'log')

Canon = list[Any]


def canon(value: Any) -> Canon:
    """Return *value* as JSON-serializable list that keeps the Python type of every node."""
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, int):
        return ['int', value]
    if isinstance(value, float):
        return ['float', repr(value)]
    if value is None:
        return ['null']
    if isinstance(value, datetime.datetime):
        return ['datetime', value.isoformat()]
    if isinstance(value, datetime.date):
        return ['date', value.isoformat()]
    if isinstance(value, str):
        return ['str', str(value)]
    if isinstance(value, dict):
        return ['map', [[canon(k), canon(v)] for k, v in value.items()]]
    if isinstance(value, (list, tuple)):
        return ['seq', [canon(v) for v in value]]
    return ['other', type(value).__name__, str(value)]


def first_leaf_path(data: Any, path: tuple = ()) -> tuple | None:
    """Path (keys/indexes) of the first scalar in *data*, None if it has none."""
    if isinstance(data, dict):
        children = data.items()
    elif isinstance(data, list):
        children = enumerate(data)
    else:
        return path or None
    for key, value in children:
        found = first_leaf_path(value, path + (key,))
        if found is not None:
            return found
    return None


def edit(data: Any) -> Any:
    """Make the edit of the test: change the first scalar and add a mapping of ambiguous values."""
    if not isinstance(data, dict):
        return data
    leaf = first_leaf_path(data)
    if leaf:
        node = data
        for key in leaf[:-1]:
            node = node[key]
        node[leaf[-1]] = 'CHANGED'
    data['zz_added'] = {'a': 'yes', 'b': True, 'c': '1:20', 'd': 'on', 'e': '010', 'f': None}
    return data


def comments(text: str) -> collections.Counter:
    """The comment texts of a YAML text (``#`` at the start of a line or after a blank)."""
    found = collections.Counter()
    for line in text.splitlines():
        match = re.search(r'(^|\s)#(.*)$', line)
        if match and line.count("'") % 2 == 0 and line.count('"') % 2 == 0:
            found[match.group(2).strip()] += 1
    return found


def changed_lines(original: str, saved: str) -> int:
    """Number of lines that differ between the two texts (a replaced block counts its longer side)."""
    matcher = difflib.SequenceMatcher(None, original.splitlines(), saved.splitlines(), autojunk=False)
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in matcher.get_opcodes() if tag != 'equal')


def attempt(function) -> dict:
    """Run *function*; return {'ok': True, 'value': ...} or {'ok': False, 'error': ...}."""
    try:
        return {'ok': True, 'value': function()}
    except Exception as e:
        return {'ok': False, 'error': f'{type(e).__name__}: {e}'}


class LogCapture(logging.Handler):
    """Collects the WARNING and ERROR messages of lib.shyaml."""

    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages: list[str] = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class ShngPipeline:
    """lib/shyaml.py of this tree."""

    name = 'shng'

    def __init__(self):
        sys.path.insert(0, str(BASE_DIR))
        import lib.shyaml

        self.shyaml = lib.shyaml
        self.capture = LogCapture()
        logger = logging.getLogger('lib.shyaml')
        logger.addHandler(self.capture)
        logger.setLevel(logging.WARNING)
        logger.disabled = False
        logger.propagate = False

    def read(self, path: Path) -> dict:
        """Load and save *path* the way SmartHomeNG does; see run_file()."""
        s = self.shyaml
        result = {}
        self.capture.messages.clear()
        result['safe'] = attempt(lambda: canon(s.yaml_load(str(path))))
        result['safe_ordered'] = attempt(lambda: canon(s.yaml_load(str(path), ordered=True)))
        result['log'] = list(self.capture.messages)
        loaded = attempt(lambda: s.yaml_load_roundtrip(str(path), raise_on_error=True))
        if not loaded['ok']:
            result['saved'] = result['edited'] = loaded
            return result
        result['data'] = canon(loaded['value'])
        result['saved'] = attempt(lambda: s.yaml_dump_roundtrip(loaded['value']))
        result['edited'] = attempt(lambda: s.yaml_dump_roundtrip(edit(s.yaml_load_roundtrip(str(path), True))))
        if result['saved']['ok']:
            result['reload_same'] = attempt(lambda: self._reload(result['saved']['value']) == result['data'])
        return result

    def _reload(self, text: str) -> Canon:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'reload.yaml'
            target.write_text(text, encoding='utf-8')
            return canon(self.shyaml.yaml_load_roundtrip(str(target), raise_on_error=True))

    def token(self, text: str) -> tuple[Any, str]:
        """Read *text* like yaml_load() and return the value and the saved file text."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'token.yaml'
            target.write_text(text, encoding='utf-8')
            value = self.shyaml.yaml_load(str(target))
            saved = self.shyaml.yaml_dump_roundtrip(self.shyaml.yaml_load_roundtrip(str(target), True))
        return value, saved

    def reread(self, saved: str) -> Any:
        """Read a saved file text like yaml_load()."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'token.yaml'
            target.write_text(saved, encoding='utf-8')
            self.capture.messages.clear()
            value = self.shyaml.yaml_load(str(target))
            if value is None and self.capture.messages:
                raise ValueError(self.capture.messages[-1].splitlines()[-1])
            return value


class PlainPipeline:
    """ruamel.yaml's own round trip as a reference."""

    name = 'plain'

    def __init__(self):
        from ruamel.yaml import YAML

        self.YAML = YAML

    def _rt(self):
        yaml = self.YAML(typ='rt')
        yaml.indent(mapping=4, sequence=4, offset=0)
        yaml.width = 12288
        yaml.allow_unicode = True
        yaml.preserve_quotes = True
        return yaml

    def _dump(self, yaml, data) -> str:
        buffer = io.StringIO()
        yaml.dump(data, buffer)
        return buffer.getvalue()

    def read(self, path: Path) -> dict:
        """Load and save *path* with plain ruamel.yaml; see run_file()."""
        text = path.read_text(encoding='utf-8-sig')
        result = {}
        result['safe'] = attempt(lambda: canon(self.YAML(typ='safe', pure=True).load(text)))
        result['safe_ordered'] = result['safe']
        result['log'] = []
        loaded = attempt(lambda: self._rt().load(text))
        if not loaded['ok']:
            result['saved'] = result['edited'] = loaded
            return result
        result['data'] = canon(loaded['value'])
        result['saved'] = attempt(lambda: self._dump(self._rt(), self._rt().load(text)))
        result['edited'] = attempt(lambda: self._dump(self._rt(), edit(self._rt().load(text))))
        if result['saved']['ok']:
            reloaded = attempt(lambda: canon(self._rt().load(result['saved']['value'])))
            result['reload_same'] = (
                {'ok': True, 'value': reloaded['value'] == result['data']} if reloaded['ok'] else reloaded
            )
        return result

    def token(self, text: str) -> tuple[Any, str]:
        """Read *text* with the safe loader and return the value and the round trip saved text."""
        value = self.YAML(typ='safe', pure=True).load(text)
        return value, self._dump(self._rt(), self._rt().load(text))

    def reread(self, saved: str) -> Any:
        """Read a saved text with the safe loader."""
        return self.YAML(typ='safe', pure=True).load(saved)


def corpus_files(directories: list[Path]) -> list[tuple[str, Path]]:
    """(label, path) of every .yaml file below *directories* (SmartHomeNG reads no other), without _pv_* and priv_*."""
    files = []
    for directory in directories:
        for path in sorted(directory.rglob('*')):
            if path.suffix != '.yaml' or not path.is_file():
                continue
            if any(part.startswith(('_pv_', 'priv_')) for part in path.relative_to(directory).parts):
                continue
            files.append((f'{directory.name}/{path.relative_to(directory)}', path))
    return files


def run_file(pipeline, path: Path) -> dict:
    """Run *pipeline* on one file and add the fidelity figures of the saved and edited file."""
    result = pipeline.read(path)
    original = path.read_text(encoding='utf-8-sig')
    for key in ('saved', 'edited'):
        if result[key].get('ok'):
            text = result[key]['value']
            result[f'{key}_changed_lines'] = changed_lines(original, text)
            result[f'{key}_comments_lost'] = sorted((comments(original) - comments(text)).elements())
    return result


def run_tokens(pipeline) -> dict:
    """How each of TOKENS is read, saved (round trip) and read again."""
    table = {}
    for token in TOKENS:
        row: dict[str, Any] = {}
        try:
            value, saved = pipeline.token(f'v: {token}\n')
            row['read'] = repr(value['v'] if isinstance(value, dict) else value)
            row['saved'] = saved.strip().splitlines()[-1].strip()
            reread = attempt(lambda: pipeline.reread(saved))
            row['reread'] = (
                repr(reread['value']['v'])
                if reread['ok'] and isinstance(reread['value'], dict)
                else (reread.get('error', repr(reread.get('value'))))
            )
        except Exception as e:
            row['error'] = f'{type(e).__name__}: {e}'
        table[token] = row
    return table


def command_run(corpus: list[Path], out: Path) -> dict:
    """Run both pipelines over the built-in corpus and *corpus*; write and return the result."""
    import ruamel.yaml

    warnings.simplefilter('ignore')
    pipelines = [ShngPipeline(), PlainPipeline()]
    files = corpus_files([BUILTIN_CORPUS, *corpus])
    result = {
        'meta': {
            'ruamel': ruamel.yaml.__version__,
            'python': sys.version.split()[0],
            'date': datetime.datetime.now().isoformat(timespec='seconds'),
        },
        'files': {label: {p.name: run_file(p, path) for p in pipelines} for label, path in files},
        'tokens': {p.name: run_tokens(p) for p in pipelines},
    }
    out.write_text(json.dumps(result, indent=1, default=str), encoding='utf-8')
    print(f'ruamel.yaml {result["meta"]["ruamel"]}: {len(files)} files -> {out}')
    return result


def fidelity(result: dict, pipeline: str) -> collections.Counter:
    """Sum the fidelity figures of one pipeline of a run."""
    figures = collections.Counter()
    for entry in result['files'].values():
        r = entry[pipeline]
        figures['files'] += 1
        figures['load errors'] += not r['safe']['ok'] or any('error' in message for message in r['log'])
        figures['save errors'] += not r['saved'].get('ok', False)
        figures['lines changed by saving'] += r.get('saved_changed_lines', 0)
        figures['lines changed by one edit'] += r.get('edited_changed_lines', 0)
        figures['comments lost'] += len(r.get('saved_comments_lost', []))
        figures['files read back different'] += r.get('reload_same', {}).get('value') is False
    return figures


def first_difference(old: Any, new: Any, path: str = '') -> tuple[str, Any, Any]:
    """Path and values of the first place where two result values (canon data, texts, dicts) differ."""
    if isinstance(old, list) and isinstance(new, list) and old[:1] == new[:1] and old[:1] in (['map'], ['seq']):
        if old[0] == 'map':
            old_items, new_items = (
                dict((json.dumps(k), v) for k, v in old[1]),
                dict((json.dumps(k), v) for k, v in new[1]),
            )
            for key in old_items.keys() | new_items.keys():
                if old_items.get(key) != new_items.get(key):
                    name = json.loads(key)[-1]
                    if key in old_items and key in new_items:
                        return first_difference(old_items[key], new_items[key], f'{path}/{name}')
                    return f'{path}/{name}', old_items.get(key, '<missing>'), new_items.get(key, '<missing>')
        elif len(old[1]) == len(new[1]):
            for index, (o, n) in enumerate(zip(old[1], new[1])):
                if o != n:
                    return first_difference(o, n, f'{path}[{index}]')
    if isinstance(old, dict) and isinstance(new, dict):
        for key in old.keys() | new.keys():
            if old.get(key) != new.get(key):
                return first_difference(old.get(key), new.get(key), f'{path}.{key}')
    if isinstance(old, str) and isinstance(new, str):
        for number, (o, n) in enumerate(zip(old.splitlines(), new.splitlines()), 1):
            if o != n:
                return f'{path} line {number}', o, n
    return path or '/', old, new


def excerpt(value: Any, limit: int = 140) -> str:
    """Short one-line form of a value."""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    text = text.replace('\n', ' | ')
    return text if len(text) <= limit else text[:limit] + '...'


def first_error(result: dict, pipeline: str) -> str | None:
    """Start of the error of a pipeline that failed on every file, else None."""
    entries = [entry[pipeline] for entry in result['files'].values()]
    if entries and all(not entry['saved'].get('ok') for entry in entries):
        lines = [line.strip() for line in entries[0]['saved']['error'].splitlines() if line.strip()]
        return ' '.join(lines[:2])
    return None


def command_compare(old: dict, new: dict) -> list[str]:
    """Report how *new* differs from *old*: data first, then saved texts, fidelity and tokens."""
    o_ver, n_ver = old['meta']['ruamel'], new['meta']['ruamel']
    lines = [f'ruamel.yaml {o_ver} -> {n_ver}', '']
    for pipeline in ('shng', 'plain'):
        lines.append(f'== pipeline {pipeline}')
        for version, result in ((o_ver, old), (n_ver, new)):
            error = first_error(result, pipeline)
            if error:
                lines.append(f'  UNUSABLE with {version}: every file fails - {error}')
        if any(first_error(result, pipeline) for result in (old, new)):
            lines.append('')
            continue
        for key in (*DATA_KEYS, 'saved', 'edited'):
            differing = [
                label
                for label in old['files']
                if label in new['files']
                and old['files'][label][pipeline].get(key) != new['files'][label][pipeline].get(key)
            ]
            lines.append(
                f'  {key:13} {len(differing):4} files differ' + (': ' + ', '.join(differing[:12]) if differing else '')
            )
            for label in differing[:5]:
                where, o_value, n_value = first_difference(
                    old['files'][label][pipeline].get(key), new['files'][label][pipeline].get(key)
                )
                lines.append(f'      {label} {where}')
                lines.append(f'        {o_ver}: {excerpt(o_value)}')
                lines.append(f'        {n_ver}: {excerpt(n_value)}')
        o_fid, n_fid = fidelity(old, pipeline), fidelity(new, pipeline)
        lines.append('  fidelity:')
        for figure in o_fid | n_fid:
            lines.append(f'    {figure:28} {o_fid[figure]:8} -> {n_fid[figure]}')
        lines.append('  tokens (read / saved as / read again), where they differ:')
        for token, o_row in old['tokens'][pipeline].items():
            n_row = new['tokens'][pipeline].get(token)
            if o_row != n_row:
                lines.append(f'    {token!r}')
                lines.append(f'      {o_ver}: {excerpt(o_row)}')
                lines.append(f'      {n_ver}: {excerpt(n_row)}')
        lines.append('')
    return lines


def command_matrix(versions: list[str], corpus: list[Path], workdir: Path) -> list[str]:
    """Install each ruamel.yaml version into its own venv, run it and compare every run with the first."""
    workdir.mkdir(parents=True, exist_ok=True)
    results = []
    for version in versions:
        venv = workdir / f'ruamel-{version}'
        python = venv / 'bin' / 'python'
        if not python.exists():
            subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True)
            subprocess.run([str(python), '-m', 'pip', 'install', '-q', f'ruamel.yaml=={version}'], check=True)
        out = workdir / f'result-{version}.json'
        command = [str(python), str(Path(__file__).resolve()), 'run', '--out', str(out)]
        for directory in corpus:
            command += ['--corpus', str(directory)]
        subprocess.run(command, check=True)
        results.append(json.loads(out.read_text(encoding='utf-8')))
    report = []
    for result in results[1:]:
        report += command_compare(results[0], result)
    return report


def main(argv: list[str] | None = None) -> int:
    """Command line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run', help="run the current interpreter's ruamel.yaml")
    run.add_argument('--corpus', type=Path, action='append', default=[], help='additional directory of YAML files')
    run.add_argument('--out', type=Path, required=True, help='result file (JSON)')
    compare = commands.add_parser('compare', help='compare two results')
    compare.add_argument('old', type=Path)
    compare.add_argument('new', type=Path)
    matrix = commands.add_parser('matrix', help='run and compare several ruamel.yaml versions')
    matrix.add_argument('versions', nargs='+', help='ruamel.yaml versions, the first one is the reference')
    matrix.add_argument('--corpus', type=Path, action='append', default=[], help='additional directory of YAML files')
    matrix.add_argument(
        '--workdir', type=Path, default=Path(tempfile.gettempdir()) / 'shng-ruamel-compat', help='venvs and results'
    )
    args = parser.parse_args(argv)

    if args.command == 'run':
        command_run(args.corpus, args.out)
    elif args.command == 'compare':
        load = lambda path: json.loads(path.read_text(encoding='utf-8'))  # noqa: E731
        print('\n'.join(command_compare(load(args.old), load(args.new))))
    else:
        print('\n'.join(command_matrix(args.versions, args.corpus, args.workdir)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
