#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Checks that version numbers of plugins and the core follow Semantic Versioning (doc/dev/public_api.md).

For every plugin changed between two git refs the plugin version must be valid semver, equal to
PLUGIN_VERSION in the code, bumped when code changed, and bumped at least as far as the changes to its
plugin.yaml demand (removed parameter: major, new function: minor, ...). For the core the version must be
valid semver and at least as high as the API changes since the last release demand.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api_snapshot import DEFAULT_SURFACE, Change, Level, Snapshot, Surface, diff, snapshot, snapshot_ref  # noqa: E402
from lib.utils import Version  # noqa: E402

_RANK = {'none': 0, 'patch': 1, 'minor': 2, 'major': 3}
_CORE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)')


def bump_between(old: str, new: str) -> str:
    """Kind of version step from old to new: 'major', 'minor', 'patch', 'none' or 'down'."""
    if Version.compare(new, old, '<'):
        return 'down'
    if Version.compare(new, old, '=='):
        return 'none'
    old_core, new_core = _CORE.match(old), _CORE.match(new)
    for kind, o, n in zip(('major', 'minor', 'patch'), old_core.groups(), new_core.groups()):
        if int(n) > int(o):
            return kind
    return 'patch'


def _bump_version(version: str, kind: str) -> str:
    """The version after a 'major', 'minor' or 'patch' bump; the pre-release part is dropped."""
    major, minor, patch = (int(n) for n in _CORE.match(version).groups())
    return {'major': f'{major + 1}.0.0', 'minor': f'{major}.{minor + 1}.0', 'patch': f'{major}.{minor}.{patch + 1}'}[
        kind
    ]


def required_bump(changes: list[Change], base_version: str) -> str:
    """Smallest bump that the changes demand; below 1.0.0 a breaking change needs only a minor bump."""
    levels = {c.level for c in changes}
    if Level.MAJOR in levels:
        return 'minor' if _CORE.match(base_version).group(1) == '0' else 'major'
    return 'minor' if Level.MINOR in levels else 'patch'


@dataclass(frozen=True)
class Finding:
    """One result of a check; errors fail it, warnings only inform."""

    severity: str  # 'error', 'warning', or 'fixed' (an error --fix has resolved)
    target: str  # plugin name or 'core'
    message: str
    fix_version: str | None = None  # version --fix writes for this error, if a bump resolves it


_NOT_CODE_SUFFIXES = ('.rst', '.md')
_PLUGIN_VERSION = re.compile(r"""^\s*PLUGIN_VERSION\s*=\s*\(?\s*['"]([^'"]+)['"]""", re.MULTILINE)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True, text=True).stdout


def _show(repo: Path, ref: str, path: str) -> str | None:
    """Content of a file at a git ref, None if it does not exist there."""
    done = subprocess.run(['git', '-C', str(repo), 'show', f'{ref}:{path}'], capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def _is_plugin_dir(name: str) -> bool:
    return not name.startswith(('_', '.', 'priv_'))


def _is_shipped(path: str) -> bool:
    """True for changed files that alter what users run: not tests, not docs, not superseded plugin versions."""
    first = path.split('/')[1]
    return not (first.startswith('_pv_') or first == 'tests' or path.endswith(_NOT_CODE_SUFFIXES))


def _declared_version(yaml_text: str) -> str:
    plugin = (yaml.safe_load(yaml_text) or {}).get('plugin')
    return str(plugin.get('version', '')) if isinstance(plugin, dict) else ''


def _plugin_snapshot(plugin: str, yaml_text: str | None) -> Snapshot:
    """API snapshot of one plugin.yaml given as text."""
    if yaml_text is None:
        return {}
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / plugin / 'plugin.yaml'
        target.parent.mkdir()
        target.write_text(yaml_text, encoding='utf-8')
        return snapshot(Path(tmp), Surface(plugin_metadata_globs=[f'{plugin}/plugin.yaml']))


def _check_plugin(
    repo: Path, base: str, head: str, plugin: str, changed: list[str], core_version: str
) -> list[Finding]:
    head_yaml = _show(repo, head, f'{plugin}/plugin.yaml')
    if head_yaml is None:
        return []
    base_yaml = _show(repo, base, f'{plugin}/plugin.yaml')
    found: list[Finding] = []

    def error(message: str, fix_version: str | None = None) -> None:
        found.append(Finding('error', plugin, message, fix_version))

    new_version = _declared_version(head_yaml)
    if not Version.is_semver(new_version):
        error(f"version '{new_version}' is not a valid semver version (MAJOR.MINOR.PATCH)")
        return found
    code = _show(repo, head, f'{plugin}/__init__.py') or ''
    in_code = _PLUGIN_VERSION.search(code)
    if in_code and in_code.group(1) != new_version:
        error(f'plugin.yaml version {new_version} differs from PLUGIN_VERSION {in_code.group(1)}')
    snap_new = _plugin_snapshot(plugin, head_yaml)
    minimum = snap_new[f'requirement:{plugin}:sh_minversion']['value']
    if minimum and Version.compare(minimum, core_version, '>'):
        error(f'sh_minversion {minimum} is above the core version {core_version}')
    if base_yaml is None:
        return found

    old_version = _declared_version(base_yaml)
    if not Version.is_semver(old_version):
        return found
    actual = bump_between(old_version, new_version)
    if actual == 'down':
        error(f'version went down: {old_version} -> {new_version}')
        return found
    changes = diff(_plugin_snapshot(plugin, base_yaml), snap_new)
    needed = required_bump(changes, old_version)
    demanding = [c for c in changes if c.level != Level.REVIEW]
    if actual == 'none' and any(_is_shipped(path) for path in changed):
        error(f'version {new_version} not bumped although files changed', _bump_version(old_version, needed))
    elif _RANK[actual] < _RANK[needed] and demanding:
        reasons = '; '.join(f'{c.key} ({c.reason})' for c in demanding[:5])
        error(
            f'changes demand a {needed} bump but the version went {old_version} -> {new_version} ({actual}): {reasons}',
            _bump_version(old_version, needed),
        )
    for change in (c for c in changes if c.level == Level.REVIEW):
        found.append(Finding('warning', plugin, f'review: {change.key} ({change.reason})'))
    return found


def check_plugins(repo: Path, base: str, head: str, core_version: str, skip: Collection[str] = ()) -> list[Finding]:
    """Check the version bumps of all plugins in repo changed between base and head."""
    changed_files = _git(repo, 'diff', '--name-only', base, head).split('\n')
    by_plugin: dict[str, list[str]] = {}
    for path in filter(None, changed_files):
        top = path.split('/')[0]
        if '/' in path and _is_plugin_dir(top):
            by_plugin.setdefault(top, []).append(path)
    findings: list[Finding] = []
    for plugin in sorted(by_plugin):
        if plugin in skip:
            findings.append(Finding('warning', plugin, 'version check skipped (no-version-bump trailer)'))
            continue
        findings += _check_plugin(repo, base, head, plugin, by_plugin[plugin], core_version)
    return findings


def _replace_group(text: str, match: re.Match, value: str) -> str:
    return text[: match.start(1)] + value + text[match.end(1) :]


def _fix_plugin(repo: Path, head: str, finding: Finding) -> Finding:
    """Write finding.fix_version into plugin.yaml and PLUGIN_VERSION of a plugin whose files are unmodified."""
    plugin, target = finding.target, finding.fix_version
    texts: dict[str, str] = {}
    for name, pattern in ((f'{plugin}/plugin.yaml', _YAML_VERSION), (f'{plugin}/__init__.py', _PLUGIN_VERSION)):
        committed = _show(repo, head, name)
        found = pattern.search(committed or '')
        if found is None:
            continue
        if (repo / name).read_text(encoding='utf-8') != committed:
            return Finding('error', plugin, f'cannot fix: uncommitted changes in {name}, commit or stash them first')
        texts[name] = _replace_group(committed, found, target)
    old = _declared_version(_show(repo, head, f'{plugin}/plugin.yaml') or '')
    if _declared_version(texts.get(f'{plugin}/plugin.yaml', '')) != target:
        return Finding('error', plugin, 'cannot fix: no version line found in plugin.yaml')
    for name, text in texts.items():
        (repo / name).write_text(text, encoding='utf-8')
    return Finding('fixed', plugin, f'version {old} -> {target}')


def apply_fixes(repo: Path, head: str, findings: list[Finding]) -> list[Finding]:
    """Write the bump of every fixable error into the working tree; other findings pass through."""
    return [_fix_plugin(repo, head, f) if f.severity == 'error' and f.fix_version else f for f in findings]


_CORE_VERSION = re.compile(r"""^shNG_version\s*=\s*['"]([^'"]+)['"]""", re.MULTILINE)
_YAML_VERSION = re.compile(r"""(?ms)^plugin:.*?^[ \t]+version:[ \t]*['"]?([^\s'"#]+)""")
_RELEASE_TAG = re.compile(r'^v?\d+\.\d+\.\d+$')
_CORE_SOURCE_DIRS = ('lib', 'modules', 'bin')


def _core_version(repo: Path, ref: str) -> str:
    found = _CORE_VERSION.search(_show(repo, ref, 'bin/shngversion.py') or '')
    return found.group(1) if found else ''


def _last_release(repo: Path, head: str) -> str | None:
    """The highest strict-semver release tag (vX.Y.Z) reachable from head."""
    tags = [t for t in _git(repo, 'tag', '--merged', head).split() if _RELEASE_TAG.match(t)]
    best: str | None = None
    for tag in tags:
        if best is None or Version.compare(tag, best, '>'):
            best = tag
    return best


def check_core(repo: Path, base: str, head: str, surface: Surface, skip: bool = False) -> list[Finding]:
    """Check the core version: valid semver, not lowered, and high enough for the API changes since the last release."""
    if skip:
        return [Finding('warning', 'core', 'version check skipped (no-version-bump trailer)')]
    version = _core_version(repo, head)
    if not Version.is_semver(version):
        return [Finding('error', 'core', f"shNG_version '{version}' is not a valid semver version (MAJOR.MINOR.PATCH)")]
    found: list[Finding] = []
    base_version = _core_version(repo, base)
    if base_version and Version.is_semver(base_version) and bump_between(base_version, version) == 'down':
        found.append(Finding('error', 'core', f'version went down: {base_version} -> {version}'))
    tag = _last_release(repo, head)
    if tag is None:
        return [*found, Finding('warning', 'core', 'no release tag (vX.Y.Z) found, API changes not checked')]
    released = tag.removeprefix('v')
    changes = diff(snapshot_ref(repo, tag, surface), snapshot_ref(repo, head, surface))
    actual = bump_between(released, version)
    needed = required_bump(changes, released)
    demanding = [c for c in changes if c.level != Level.REVIEW]
    if (
        actual in ('none', 'down')
        and subprocess.run(['git', '-C', str(repo), 'diff', '--quiet', tag, head, '--', *_CORE_SOURCE_DIRS]).returncode
    ):
        found.append(
            Finding('error', 'core', f'version {version} is not above the last release {tag} although files changed')
        )
    elif _RANK[actual] < _RANK[needed] and demanding:
        reasons = '; '.join(f'{c.key} ({c.reason})' for c in demanding[:5])
        found.append(
            Finding(
                'error',
                'core',
                f'changes since {tag} demand a {needed} bump but the version is {version} ({actual}): {reasons}',
            )
        )
    found += [Finding('warning', 'core', f'review: {c.key} ({c.reason})') for c in changes if c.level == Level.REVIEW]
    return found


_TRAILER = re.compile(r'^no-version-bump:\s*(.+)$', re.IGNORECASE | re.MULTILINE)


def skip_targets(repo: Path, base: str, head: str) -> set[str]:
    """Plugins (or 'core') named in `no-version-bump:` trailers of the commits in base..head."""
    messages = _git(repo, 'log', '--format=%B%x00', f'{base}..{head}').split('\x00')
    return {
        name.strip()
        for message in messages
        for found in _TRAILER.findall(message)
        for name in found.split(',')
        if name.strip()
    }


def _running_core_version(core_dir: Path) -> str:
    found = _CORE_VERSION.search((core_dir / 'bin' / 'shngversion.py').read_text(encoding='utf-8'))
    return found.group(1) if found else ''


_ZERO_SHA = '0' * 40
_REFERENCE_BRANCHES = ('origin/develop', 'origin/master')


def _is_known_commit(repo: Path, sha: str) -> bool:
    return (
        subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', f'{sha}^{{commit}}'], capture_output=True).returncode
        == 0
    )


def _fork_point(repo: Path, head: str) -> str | None:
    """Where head left the first reference branch (origin/develop, origin/master) that exists."""
    for branch in _REFERENCE_BRANCHES:
        done = subprocess.run(['git', '-C', str(repo), 'merge-base', branch, head], capture_output=True, text=True)
        if done.returncode == 0:
            return done.stdout.strip()
    return None


def pre_push_ranges(repo: Path, stdin_text: str) -> list[tuple[str, str]]:
    """(base, head) commit ranges a push would publish, from the lines git feeds a pre-push hook."""
    ranges = []
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4 or parts[1] == _ZERO_SHA:
            continue
        head, remote = parts[1], parts[3]
        base = remote if remote != _ZERO_SHA and _is_known_commit(repo, remote) else _fork_point(repo, head)
        if base:
            ranges.append((base, head))
    return ranges


def _findings(args: argparse.Namespace, base: str, head: str) -> list[Finding]:
    skip = skip_targets(args.repo, base, head)
    if args.target == 'plugins':
        core_version = args.core_version or _running_core_version(args.core_dir or args.repo.resolve().parent)
        return check_plugins(args.repo, base, head, core_version, skip)
    return check_core(args.repo, base, head, Surface.load(args.surface), 'core' in skip)


def main(argv: list[str]) -> int:
    """Command line entry; returns the process exit code."""
    parser = argparse.ArgumentParser(description='Check plugin and core version bumps between two git refs.')
    parser.add_argument('target', choices=['plugins', 'core'])
    parser.add_argument('--repo', type=Path, default=Path.cwd(), help='git repository to check (default: cwd)')
    parser.add_argument('--base', help='ref the changes are measured from')
    parser.add_argument('--head', default='HEAD', help='ref to check (default: HEAD)')
    parser.add_argument(
        '--from-pre-push', action='store_true', help='read the pushed ranges from stdin like a pre-push hook'
    )
    parser.add_argument('--core-version', help='core version plugins are checked against')
    parser.add_argument(
        '--core-dir', type=Path, help='core checkout to read the core version from (default: parent of --repo)'
    )
    parser.add_argument('--surface', type=Path, default=DEFAULT_SURFACE, help='API surface declaration (core)')
    parser.add_argument('--warn-only', action='store_true', help='report errors but exit 0')
    parser.add_argument(
        '--fix', action='store_true', help='plugins: write the demanded version bumps into the working tree'
    )
    args = parser.parse_args(argv)
    if args.fix and (args.target != 'plugins' or args.from_pre_push or not args.base or args.head != 'HEAD'):
        parser.error('--fix works on the plugins target with --base and the default --head')

    if args.from_pre_push:
        ranges = pre_push_ranges(args.repo, sys.stdin.read())
    elif args.base:
        ranges = [(args.base, args.head)]
    else:
        parser.error('--base or --from-pre-push is required')
    findings = [f for base, head in ranges for f in _findings(args, base, head)]
    if args.fix:
        findings = apply_fixes(args.repo, args.head, findings)
    for finding in findings:
        print(f'{finding.severity.upper()} {finding.target}: {finding.message}')
    if any(f.severity == 'fixed' for f in findings):
        print('The fixes are uncommitted: review and commit them, then run the check again.')
    return int(any(f.severity == 'error' for f in findings) and not args.warn_only)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
