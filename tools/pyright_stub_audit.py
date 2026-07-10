#!/usr/bin/env python3
"""
Enumerate every top-level package imported across a repo's .py files
(honoring the repo's own pyright `exclude` patterns), then check which of
those packages are actually installed in the venv vs. only resolved via a
typings/ stub — and report a suggested action for each.

Why: pyright's typings/ stubPath takes priority over a real installed
package (verified empirically — a stub fully shadows the real source, it
is never merged or used as a fallback-on-error). So a stub left in place
for a package that later gets pip-installed for real silently hides that
package's actual types from then on. This script surfaces that drift.

Usage:
    python tools/pyright_stub_audit.py --repo plugins

Dry-run by default — only prints a report. Pass --apply-create to write
empty stub files for not-installed/no-stub packages. Deletion of stubs
that now shadow an installed package is never done automatically (the
stub may have hand-written content); the report just flags it.
"""

import argparse
import ast
import fnmatch
import json
import subprocess
import sys
import tomllib
import warnings
from pathlib import Path

# Legacy plugin code has plenty of invalid-escape-sequence string literals
# (e.g. regex patterns written without a raw-string prefix). ast.parse()
# still parses them fine — the warning is just noise for this audit.
warnings.filterwarnings('ignore', category=SyntaxWarning)

ALWAYS_SKIP_DIR_NAMES = {'__pycache__', '.git'}

# First-party namespaces: resolved via extraPaths/the repo itself, not
# something you'd pip-install or stub — never candidates for either.
FIRST_PARTY_TOP_LEVEL = {'lib', 'plugins', 'modules', 'tests', 'tools', 'bin', 'dev', '__future__'}


def load_pyright_exclude(repo_root: Path) -> list[str]:
    pyproject = repo_root / 'pyproject.toml'
    if not pyproject.is_file():
        return []
    with pyproject.open('rb') as f:
        data = tomllib.load(f)
    return data.get('tool', {}).get('pyright', {}).get('exclude', [])


def is_excluded(rel_posix: str, name: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if '/' in pattern:
            if fnmatch.fnmatch(rel_posix, pattern) or fnmatch.fnmatch(rel_posix + '/', pattern + '/'):
                return True
            # also match as a prefix (pattern names a whole subtree)
            if rel_posix.startswith(pattern.rstrip('*') if pattern.endswith('*') else pattern + '/'):
                return True
        else:
            if fnmatch.fnmatch(name, pattern):
                return True
    return False


def iter_py_files(repo_root: Path, exclude_patterns: list[str]):
    for dirpath, dirnames, filenames in __import__('os').walk(repo_root):
        d = Path(dirpath)
        rel = d.relative_to(repo_root).as_posix()
        if rel == '.':
            rel = ''
        kept = []
        for dname in dirnames:
            if dname in ALWAYS_SKIP_DIR_NAMES:
                continue
            child_rel = f'{rel}/{dname}' if rel else dname
            if is_excluded(child_rel, dname, exclude_patterns):
                continue
            kept.append(dname)
        dirnames[:] = kept

        for fname in filenames:
            if fname.endswith('.py'):
                file_rel = f'{rel}/{fname}' if rel else fname
                if is_excluded(file_rel, fname, exclude_patterns):
                    continue
                yield d / fname


def extract_imports(py_file: Path) -> set[str]:
    """
    Full dotted import paths (not just the top-level package name) — e.g.
    "openzwave.network" from `from openzwave.network import ZWaveNetwork`.
    A stub for the top-level package alone doesn't resolve a submodule
    import; pyright needs a stub file for the submodule itself too.
    """
    try:
        tree = ast.parse(py_file.read_text(encoding='utf-8', errors='replace'), filename=str(py_file))
    except SyntaxError:
        return set()

    paths = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                paths.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue  # relative import — always local to this package
            if node.module:
                paths.add(node.module)
                # `from pkg import sub` — can't tell statically whether `sub`
                # is a submodule or an attribute of pkg; add it as a
                # candidate submodule path too. Harmless if wrong: an extra
                # unused stub file, not a false error.
                for alias in node.names:
                    if alias.name != '*':
                        paths.add(f'{node.module}.{alias.name}')
    return paths


def is_local_sibling(name: str, importing_files: set[Path]) -> bool:
    """
    True if *name* matches a .py file or package dir sitting right next to
    one of the files that imports it. Several plugins use a legacy
    try/except ImportError shim — `from .x import Y` then a fallback
    `from x import Y` for when the plugin's own directory ends up on
    sys.path directly — so the "package" is really just a sibling source
    file, not anything to stub or pip-install.
    """
    for f in importing_files:
        parent = f.parent
        if (parent / f'{name}.py').is_file() or (parent / name / '__init__.py').is_file():
            return True
    return False


def check_installed(venv_python: Path, package_names: list[str]) -> dict:
    script = (
        'import importlib.util, json, sys\n'
        'names = json.loads(sys.argv[1])\n'
        'out = {}\n'
        'for n in names:\n'
        '    try:\n'
        '        out[n] = importlib.util.find_spec(n) is not None\n'
        '    except Exception:\n'
        '        out[n] = False\n'
        'print(json.dumps(out))\n'
    )
    result = subprocess.run(
        # -I (isolated mode): otherwise `python -c` puts the invoking cwd on
        # sys.path[0], and find_spec() would then "find" any package name
        # that happens to match a directory under wherever this script was
        # run from (e.g. shng root's bin/ matching an import named "bin").
        [str(venv_python), '-I', '-c', script, json.dumps(package_names)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def find_stub(typings_dir: Path, name: str) -> Path | None:
    pkg_dir = typings_dir / name / '__init__.pyi'
    if pkg_dir.is_file():
        return pkg_dir
    flat = typings_dir / f'{name}.pyi'
    if flat.is_file():
        return flat
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--repo', required=True, type=Path, help='Repo root to scan (e.g. plugins)')
    parser.add_argument('--venv-python', type=Path, default=None, help='Venv python to check installs against')
    parser.add_argument(
        '--apply-create', action='store_true', help='Write empty stubs for not-installed/no-stub packages'
    )
    args = parser.parse_args()

    repo_root = args.repo.resolve()
    venv_python = args.venv_python or (repo_root.parent / 'venvs' / 'shng' / 'bin' / 'python3')
    typings_dir = repo_root / 'typings'

    exclude_patterns = load_pyright_exclude(repo_root)
    stdlib = set(sys.stdlib_module_names) | {'__future__'}

    import_sites: dict[str, set[Path]] = {}
    dotted_paths: dict[str, set[str]] = {}  # top-level name -> full dotted import paths seen
    file_count = 0
    for py_file in iter_py_files(repo_root, exclude_patterns):
        file_count += 1
        for path in extract_imports(py_file):
            name = path.split('.')[0]
            if name in stdlib or name in FIRST_PARTY_TOP_LEVEL:
                continue
            import_sites.setdefault(name, set()).add(py_file)
            dotted_paths.setdefault(name, set()).add(path)

    package_names = sorted(import_sites)
    installed = check_installed(venv_python, package_names) if package_names else {}

    rows = []
    for name in package_names:
        is_installed = installed.get(name, False)
        stub_path = find_stub(typings_dir, name)
        has_stub = stub_path is not None
        if not is_installed and is_local_sibling(name, import_sites[name]):
            action = 'local sibling file (no stub needed)'
        elif not is_installed and not has_stub:
            action = 'CREATE stub'
        elif is_installed and has_stub:
            action = 'REVIEW: stub shadows an installed package'
        elif not is_installed and has_stub:
            action = 'ok (stubbed)'
        else:
            action = 'ok (installed)'
        rows.append((name, is_installed, has_stub, len(import_sites[name]), action))

    print(f'Scanned {file_count} files under {repo_root}')
    print(f'{len(package_names)} distinct external packages imported\n')

    name_w = max((len(r[0]) for r in rows), default=4)
    print(f'{"package".ljust(name_w)}  installed  stub  files  action')
    for name, is_installed, has_stub, n_files, action in sorted(rows, key=lambda r: (r[4], r[0])):
        print(
            f'{name.ljust(name_w)}  {str(is_installed).ljust(9)}  {str(has_stub).ljust(4)}  {str(n_files).rjust(5)}  {action}'
        )

    to_create = [r[0] for r in rows if r[4] == 'CREATE stub']
    to_review = [r[0] for r in rows if r[4].startswith('REVIEW')]
    local_siblings = [r[0] for r in rows if r[4].startswith('local sibling')]

    print(
        f'\n{len(to_create)} to create, {len(to_review)} to review (installed but stubbed), '
        f'{len(local_siblings)} local-sibling false positives (skipped, not stubbed)'
    )

    if args.apply_create and to_create:
        typings_dir.mkdir(exist_ok=True)
        files_written = 0
        for name in to_create:
            # A stub for the top-level package alone doesn't resolve
            # `from pkg.sub import X` — pyright needs pkg/sub/__init__.pyi
            # too. Create every level of every dotted path actually seen
            # as a nested package dir, uniformly (leaf included), rather
            # than guessing module-vs-package for the last segment.
            for dotted in dotted_paths[name]:
                parts = dotted.split('.')
                dir_path = typings_dir
                for part in parts:
                    dir_path = dir_path / part
                    dir_path.mkdir(exist_ok=True)
                    init_file = dir_path / '__init__.pyi'
                    if not init_file.exists():
                        init_file.touch()
                        files_written += 1
        print(f'\nCreated {files_written} empty stub file(s) for {len(to_create)} package(s) under {typings_dir}')
    elif to_create:
        print('\nRun with --apply-create to write empty stubs for the CREATE list above.')

    if to_review:
        print('\nStubs shadowing an installed package (not touched — review manually):')
        for name in to_review:
            print(f'  {typings_dir / name / "__init__.pyi"}')


if __name__ == '__main__':
    sys.exit(main())
