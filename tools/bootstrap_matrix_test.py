#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  This file is part of SmartHomeNG
#  https://github.com/smarthomeNG/smarthome
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################
"""
Multi-Python-version install/startup smoke test for SmartHomeNG.

Clones shng + plugins once into a scratch workdir, creates one venv per
target Python version (discovered from .github/workflows/unittests.yml),
installs requirements, generates a minimal etc/ config, and runs
`bin/smarthome.py -f -e` for a short window before sending SIGTERM -
watching for python-version/package incompatibilities (as opposed to the
expected "device not reachable" noise from running with no real hardware).

Two actions:

    build-matrix   Scan plugins/*/plugin.yaml for mandatory parameters
                   without a default, synthesize a dummy value per
                   declared type, and save the result to a JSON file.
                   Run this whenever plugins are added/changed - it is
                   NOT run implicitly by `run`, since it is the slower,
                   plugin-set-dependent step and its output is meant to
                   be reused across many `run` invocations.

    run            Phases 0-4: for each target Python version, ensure the
                   interpreter is installed, create a venv, install
                   requirements, and smoke-test the core (no plugins
                   enabled). If --plugins is given, also runs phase 5:
                   one plugin at a time, loading dummy parameters from
                   the matrix file (regenerating on the fly - with a
                   warning - for any plugin missing from it).

Examples:

    tools/bootstrap_matrix_test.py build-matrix
    tools/bootstrap_matrix_test.py run --yes
    tools/bootstrap_matrix_test.py run --yes --python-versions 3.11,3.12 \\
        --shng-branch develop --plugins-branch develop
    tools/bootstrap_matrix_test.py run --yes --plugins hue2,avm,mqtt
    tools/bootstrap_matrix_test.py run --yes --plugins all
"""

import argparse
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print('ERROR: PyYAML is required to run this script (pip install pyyaml)', file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SHNG_REPO_URL = 'https://github.com/smarthomeNG/smarthome.git'
PLUGINS_REPO_URL = 'https://github.com/smarthomeNG/plugins.git'
WORKFLOW_REL_PATH = '.github/workflows/unittests.yml'

DEFAULT_WORKDIR = Path.home() / '.shng_matrix_test'
DEFAULT_MATRIX_FILE = Path(__file__).resolve().parent / 'plugin_dummy_matrix.json'

START_TIMEOUT = 25  # seconds to let the core settle after start before SIGTERM
STOP_TIMEOUT = 15  # seconds to wait for clean exit after SIGTERM before SIGKILL

# Parameter type -> dummy value, per the canonical types handled by
# lib/metadata.py's _convert_valuetotype(). Anything not listed falls back
# to a plain string (matches the 'foo' catch-all type).
DUMMY_VALUE_BY_TYPE = {
    'bool': False,
    'int': 0,
    'scene': 0,
    'float': 0.0,
    'num': 0.0,
    'str': 'dummy',
    'password': 'dummy',
    'list': [],
    'dict': {},
    'ip': '127.0.0.1',
    'ipv4': '127.0.0.1',
    'ipv6': '::1',
    'mac': '00:00:00:00:00:00',
    'knx_ga': '0/0/0',
    'foo': 'dummy',
}

# Regex buckets for classifying captured output. Checked in order;
# IGNORABLE is checked first so a line matching both is treated as noise.
IGNORABLE_PATTERNS = [
    r'ConnectionRefusedError',
    r'ConnectionResetError',
    r'TimeoutError',
    r'timed? ?out',
    r'No route to host',
    r'Network is unreachable',
    r'Name or service not known',
    r'nodename nor servname provided',
    r'gaierror',
    r'\[Errno 11[013]\]',  # EAGAIN/EHOSTUNREACH/ECONNREFUSED family
    r'Permission denied.*(tty|serial|/dev/)',
    r'could not open port',
    r'Broken pipe',
    r'EOF occurred in violation of protocol',
    r'Bridge not found',
    r'device not reachable',
    r'host(name)? .* not reachable',
]

ACTIONABLE_PATTERNS = [
    r'ModuleNotFoundError',
    r'ImportError',
    r'SyntaxError',
    r'No matching distribution found',
    r'Could not find a version that satisfies the requirement',
    r'ERROR: Could not build wheels',
    r'error: Microsoft Visual C\+\+',
    r"AttributeError: module '.*' has no attribute",
    r'DeprecationWarning.*removed in Python',
    r'TypeError: .*positional argument',
    r'ImportWarning',
]

IGNORABLE_RE = re.compile('|'.join(IGNORABLE_PATTERNS), re.IGNORECASE)
ACTIONABLE_RE = re.compile('|'.join(ACTIONABLE_PATTERNS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def run(cmd, cwd=None, check=True, capture=False, env=None, timeout=None):
    """Thin wrapper around subprocess.run with consistent logging."""
    print(f'$ {" ".join(cmd)}' + (f'   (cwd={cwd})' if cwd else ''))
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=capture, text=True, env=env, timeout=timeout)


def confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        print(f'{prompt} [auto-confirmed via --yes]')
        return True
    reply = input(f'{prompt} [y/N] ').strip().lower()
    return reply in ('y', 'yes')


def which(binary: str) -> str | None:
    return shutil.which(binary)


# ---------------------------------------------------------------------------
# Phase 0: discover target Python versions
# ---------------------------------------------------------------------------


def discover_python_versions(shng_repo: Path) -> list[str]:
    """
    Read the python-version matrix straight out of the CI workflow that
    actually gates merges - the most authoritative source of "supported",
    more so than prose docs which can go stale.
    """
    workflow_path = shng_repo / WORKFLOW_REL_PATH
    if not workflow_path.is_file():
        print(f'WARNING: {workflow_path} not found, falling back to a hardcoded guess', file=sys.stderr)
        return ['3.10', '3.11', '3.12', '3.13', '3.14']

    with open(workflow_path) as f:
        text = f.read()

    try:
        data = yaml.safe_load(text)
        for job in data.get('jobs', {}).values():
            versions = job.get('strategy', {}).get('matrix', {}).get('python-version')
            if versions:
                return [str(v) for v in versions]
    except Exception as e:
        print(f'WARNING: YAML parse of workflow failed ({e}), falling back to regex', file=sys.stderr)

    match = re.search(r'python-version:\s*\[([^\]]+)\]', text)
    if match:
        return [v.strip().strip('\'"') for v in match.group(1).split(',')]

    raise RuntimeError(f'Could not determine python-version matrix from {workflow_path}')


# ---------------------------------------------------------------------------
# Phase 1: ensure each Python version is installed
# ---------------------------------------------------------------------------


def find_interpreter(version: str) -> str | None:
    for candidate in (f'python{version}', f'python3.{version.split(".")[-1]}'):
        path = which(candidate)
        if path:
            return path
    return None


def ensure_python_apt(version: str, assume_yes: bool) -> str | None:
    if not which('apt-get'):
        return None
    pkgs = [f'python{version}', f'python{version}-venv', f'python{version}-dev']
    check = run(['apt-cache', 'show', pkgs[0]], check=False, capture=True)
    if check.returncode != 0 or not check.stdout.strip():
        print(f'apt: package {pkgs[0]} not available in configured repos')
        return None
    if not confirm(f'Install via apt: sudo apt-get install -y {" ".join(pkgs)} ?', assume_yes):
        return None
    result = run(['sudo', 'apt-get', 'install', '-y'] + pkgs, check=False)
    if result.returncode != 0:
        print(f'apt install of {pkgs[0]} failed (exit {result.returncode})')
        return None
    return find_interpreter(version)


def ensure_python_brew(version: str, assume_yes: bool) -> str | None:
    if not which('brew'):
        return None
    formula = f'python@{version}'
    check = run(['brew', 'list', formula], check=False, capture=True)
    if check.returncode == 0:
        return find_interpreter(version)
    if not confirm(f'Install via Homebrew: brew install {formula} ?', assume_yes):
        return None
    result = run(['brew', 'install', formula], check=False)
    if result.returncode != 0:
        print(f'brew install of {formula} failed (exit {result.returncode})')
        return None
    return find_interpreter(version)


def ensure_python_pyenv(version: str, assume_yes: bool) -> str | None:
    if not which('pyenv'):
        return None
    versions = run(['pyenv', 'versions', '--bare'], check=False, capture=True).stdout
    matching = [v for v in versions.splitlines() if v.startswith(version + '.')]
    if matching:
        full_version = sorted(matching)[-1]
    else:
        latest = run(['pyenv', 'install', '--list'], check=False, capture=True).stdout
        candidates = [v.strip() for v in latest.splitlines() if re.fullmatch(rf'{re.escape(version)}\.\d+', v.strip())]
        if not candidates:
            print(f'pyenv: no installable version found matching {version}.x')
            return None
        full_version = sorted(candidates)[-1]
        if not confirm(f'Install via pyenv: pyenv install {full_version} ?', assume_yes):
            return None
        result = run(['pyenv', 'install', full_version], check=False)
        if result.returncode != 0:
            print(f'pyenv install of {full_version} failed (exit {result.returncode})')
            return None
    root = run(['pyenv', 'root'], check=False, capture=True).stdout.strip()
    candidate = Path(root) / 'versions' / full_version / 'bin' / 'python3'
    return str(candidate) if candidate.is_file() else None


def ensure_python_source_build(version: str, assume_yes: bool, workdir: Path) -> str | None:
    """
    Last-resort fallback: build from source (documented at
    doc/user/source/referenz/python/python_installation.rst). Uses
    `make altinstall` deliberately - never `make install` - so the
    system's default python3 is never overwritten.
    """
    full_version = version if version.count('.') == 2 else f'{version}.0'
    src_dir = workdir / f'Python-{full_version}-src'
    if not confirm(
        f'No package manager has Python {version}. Build from source into {src_dir}? '
        f'This requires build tooling (build-essential, libssl-dev, zlib1g-dev, ...) to be '
        f'installed already.',
        assume_yes,
    ):
        return None
    url = f'https://www.python.org/ftp/python/{full_version}/Python-{full_version}.tar.xz'
    tarball = workdir / f'Python-{full_version}.tar.xz'
    if not tarball.is_file():
        run(['curl', '-fsSL', '-o', str(tarball), url])
    src_dir.mkdir(parents=True, exist_ok=True)
    run(['tar', '-xf', str(tarball), '-C', str(src_dir), '--strip-components=1'])
    run(['./configure', '--prefix', str(workdir / 'python-installs' / full_version)], cwd=src_dir)
    ncpu = os.cpu_count() or 2
    run(['make', f'-j{ncpu}'], cwd=src_dir)
    run(['make', 'altinstall'], cwd=src_dir)
    candidate = workdir / 'python-installs' / full_version / 'bin' / f'python{version}'
    return str(candidate) if candidate.is_file() else None


def ensure_python(version: str, assume_yes: bool, workdir: Path) -> str | None:
    existing = find_interpreter(version)
    if existing:
        print(f'Python {version} already available at {existing}')
        return existing

    system = platform.system()
    if system == 'Linux':
        order = [
            lambda: ensure_python_apt(version, assume_yes),
            lambda: ensure_python_pyenv(version, assume_yes),
            lambda: ensure_python_source_build(version, assume_yes, workdir),
        ]
    elif system == 'Darwin':
        order = [lambda: ensure_python_brew(version, assume_yes), lambda: ensure_python_pyenv(version, assume_yes)]
    else:
        print(f'Unsupported OS {system!r} - install Python {version} manually and re-run', file=sys.stderr)
        return None

    for attempt in order:
        result = attempt()
        if result:
            return result
    return None


# ---------------------------------------------------------------------------
# Phase 2: shared repo checkout + per-version venv/install
# ---------------------------------------------------------------------------


def clone_or_update(url: str, dest: Path, branch: str):
    if dest.is_dir() and (dest / '.git').is_dir():
        run(['git', 'fetch', 'origin', branch], cwd=dest)
        run(['git', 'checkout', branch], cwd=dest)
        run(['git', 'reset', '--hard', f'origin/{branch}'], cwd=dest)
    else:
        run(['git', 'clone', '--branch', branch, url, str(dest)])


def build_requirements(shng_dir: Path):
    """
    requirements/all.txt (and base.txt) are gitignored, generated files -
    tools/build_requirements.py assembles them by walking plugins/*. It is
    deliberately written to run with a bare interpreter (no third-party
    deps of its own, see the comment in lib/shpypi.py about not needing
    ruamel.yaml), so this can run with whatever python invoked this script,
    once per checkout - it does not depend on the target venv/version.
    """
    run([sys.executable, 'tools/build_requirements.py'], cwd=shng_dir)


def setup_repos(workdir: Path, shng_branch: str, plugins_branch: str) -> Path:
    shng_dir = workdir / 'shng'
    clone_or_update(SHNG_REPO_URL, shng_dir, shng_branch)
    clone_or_update(PLUGINS_REPO_URL, shng_dir / 'plugins', plugins_branch)
    build_requirements(shng_dir)
    return shng_dir


def create_venv(python_bin: str, venv_path: Path) -> Path:
    if not venv_path.is_dir():
        run([python_bin, '-m', 'venv', str(venv_path)])
    venv_python = venv_path / 'bin' / 'python3'
    return venv_python


def pip_install(venv_python: Path, requirements_file: Path, log_path: Path) -> tuple[bool, str]:
    result = subprocess.run(
        [str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], capture_output=True, text=True
    )
    out = result.stdout + result.stderr

    result = subprocess.run(
        [str(venv_python), '-m', 'pip', 'install', '-r', str(requirements_file)], capture_output=True, text=True
    )
    out += result.stdout + result.stderr
    log_path.write_text(out)
    return result.returncode == 0, out


# ---------------------------------------------------------------------------
# Phase 3: minimal config generation
# ---------------------------------------------------------------------------


def write_minimal_logging_yaml(etc_dir: Path):
    """
    Based on templates/logging.yaml.default, but with the console handler
    enabled (commented out by default) at WARNING - enough to see actual
    errors (module import failures, plugin init exceptions) without the
    NOTICE/INFO/DEBUG firehose every plugin/module logger produces at
    startup. File handlers are kept too, for post-mortem digging on a
    specific actionable failure.
    """
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'shng_simple': {
                'format': '%(asctime)s %(levelname)-8s %(name)-19s %(message)s',
                'datefmt': '%Y-%m-%d  %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'shng_simple',
                'level': 'WARNING',
                'stream': 'ext://sys.stdout',
            },
            'shng_warnings_file': {
                '()': 'lib.log.ShngTimedRotatingFileHandler',
                'formatter': 'shng_simple',
                'level': 'NOTICE',
                'utc': False,
                'when': 'midnight',
                'backupCount': 1,
                'filename': './var/log/smarthome-warnings.log',
                'encoding': 'utf8',
            },
        },
        'loggers': {
            'lib': {'level': 'WARNING'},
            'lib.smarthome': {'level': 'NOTICE'},
            'modules': {'level': 'WARNING'},
            'plugins': {'level': 'WARNING'},
            'logics': {'level': 'WARNING'},
            'items': {'level': 'WARNING'},
        },
        'root': {'level': 'WARNING', 'handlers': ['console', 'shng_warnings_file']},
    }
    with open(etc_dir / 'logging.yaml', 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False)


def write_minimal_smarthome_yaml(etc_dir: Path):
    (etc_dir / 'smarthome.yaml').write_text('config_etc: true\n')


def write_plugin_yaml(etc_dir: Path, entries: dict):
    """entries: {config_name: {plugin_name: ..., **params}} or {} for none."""
    with open(etc_dir / 'plugin.yaml', 'w') as f:
        if not entries:
            f.write('# no plugins enabled\n')
        else:
            yaml.safe_dump(entries, f, sort_keys=False)


def prepare_etc(shng_dir: Path, plugin_entries: dict | None = None):
    etc_dir = shng_dir / 'etc'
    for sub in ('items', 'logics', 'structs', 'scenes', 'functions'):
        (etc_dir / sub).mkdir(parents=True, exist_ok=True)
    write_minimal_logging_yaml(etc_dir)
    write_minimal_smarthome_yaml(etc_dir)
    write_plugin_yaml(etc_dir, plugin_entries or {})
    # module.yaml intentionally omitted for the core-only smoke test: no
    # module needs to be loaded just to prove the interpreter/deps work.


# ---------------------------------------------------------------------------
# Phase 4/5: run the smoke test and classify output
# ---------------------------------------------------------------------------


class SmokeResult:
    def __init__(self):
        self.started_ok = False
        self.exited_cleanly = False
        self.exit_code = None
        self.output = ''
        self.findings = []


def run_smoke_test(venv_python: Path, shng_dir: Path) -> SmokeResult:
    result = SmokeResult()
    env = os.environ.copy()
    proc = subprocess.Popen(
        [str(venv_python), 'bin/smarthome.py', '-f', '-e'],
        cwd=shng_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )

    deadline = time.time() + START_TIMEOUT
    while time.time() < deadline and proc.poll() is None:
        time.sleep(1)

    if proc.poll() is not None:
        # died on its own before we ever sent a signal - that's the
        # clearest possible actionable/ignorable-classifiable signal
        result.exit_code = proc.returncode
    else:
        result.started_ok = True
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=STOP_TIMEOUT)
            result.exited_cleanly = True
            result.exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            result.exited_cleanly = False
            result.exit_code = proc.returncode

    try:
        result.output = proc.stdout.read() if proc.stdout else ''
    except Exception:
        pass

    result.findings = classify_output(result.output)
    return result


def classify_output(text: str) -> list[str]:
    findings = []
    for line in text.splitlines():
        if IGNORABLE_RE.search(line):
            continue
        if ACTIONABLE_RE.search(line):
            findings.append(line.strip())
    return findings


# ---------------------------------------------------------------------------
# build-matrix: dummy parameters per plugin
# ---------------------------------------------------------------------------


def dummy_value_for(ptype: str):
    return DUMMY_VALUE_BY_TYPE.get(ptype, 'dummy')


def compute_dummy_params_for_plugin(plugin_dir: Path) -> dict:
    yaml_path = plugin_dir / 'plugin.yaml'
    if not yaml_path.is_file():
        return {}
    with open(yaml_path) as f:
        data = yaml.safe_load(f) or {}
    params = data.get('parameters')
    if not params or params == 'NONE':
        return {}
    dummy = {}
    for name, definition in params.items():
        if not isinstance(definition, dict):
            continue
        if not definition.get('mandatory'):
            continue
        if 'default' in definition and definition['default'] not in (None, ''):
            continue
        dummy[name] = dummy_value_for(definition.get('type', 'foo'))
    return dummy


def plugin_py_version_bounds(plugin_dir: Path) -> tuple[str | None, str | None]:
    yaml_path = plugin_dir / 'plugin.yaml'
    if not yaml_path.is_file():
        return None, None
    with open(yaml_path) as f:
        data = yaml.safe_load(f) or {}
    meta = data.get('plugin', {})
    return meta.get('py_minversion'), meta.get('py_maxversion')


def build_matrix(shng_dir: Path, matrix_file: Path):
    plugins_dir = shng_dir / 'plugins'
    matrix = {}
    for entry in sorted(plugins_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith('.') or entry.name in ('priv_repos',):
            continue
        if not (entry / 'plugin.yaml').is_file():
            continue
        dummy_params = compute_dummy_params_for_plugin(entry)
        py_min, py_max = plugin_py_version_bounds(entry)
        matrix[entry.name] = {'dummy_params': dummy_params, 'py_minversion': py_min, 'py_maxversion': py_max}
    matrix_file.parent.mkdir(parents=True, exist_ok=True)
    with open(matrix_file, 'w') as f:
        json.dump({'generated_at': datetime.now().isoformat(), 'plugins': matrix}, f, indent=2, sort_keys=True)
    print(f'Wrote matrix for {len(matrix)} plugins to {matrix_file}')


def load_matrix(matrix_file: Path) -> dict:
    if not matrix_file.is_file():
        return {}
    with open(matrix_file) as f:
        return json.load(f).get('plugins', {})


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def python_version_in_range(version: str, py_min: str | None, py_max: str | None) -> bool:
    def to_tuple(v):
        return tuple(int(x) for x in v.split('.'))

    v = to_tuple(version)
    if py_min and v < to_tuple(str(py_min)):
        return False
    if py_max and v > to_tuple(str(py_max)):
        return False
    return True


def cmd_build_matrix(args):
    workdir = Path(args.workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)
    shng_dir = setup_repos(workdir, args.shng_branch, args.plugins_branch)
    build_matrix(shng_dir, Path(args.matrix_file))


def cmd_run(args):
    workdir = Path(args.workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    shng_dir = setup_repos(workdir, args.shng_branch, args.plugins_branch)

    versions = (
        [v.strip() for v in args.python_versions.split(',')]
        if args.python_versions
        else discover_python_versions(shng_dir)
    )
    print(f'Target Python versions: {", ".join(versions)}')

    requested_plugins: list[str] = []
    if args.plugins:
        if args.plugins.strip().lower() == 'all':
            requested_plugins = sorted(
                p.name for p in (shng_dir / 'plugins').iterdir() if (p / 'plugin.yaml').is_file()
            )
        else:
            requested_plugins = [p.strip() for p in args.plugins.split(',')]

    matrix = load_matrix(Path(args.matrix_file)) if requested_plugins else {}

    report = {'generated_at': datetime.now().isoformat(), 'versions': {}}
    logs_dir = workdir / 'reports' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    for version in versions:
        print(f'\n=== Python {version} ===')
        version_report = {'python_version': version}
        report['versions'][version] = version_report

        python_bin = ensure_python(version, args.yes, workdir)
        if not python_bin:
            version_report['interpreter'] = 'unavailable'
            print(f'SKIP: could not obtain a Python {version} interpreter')
            continue
        version_report['interpreter'] = python_bin

        venv_path = workdir / 'venvs' / f'py_{version}'
        venv_python = create_venv(python_bin, venv_path)

        # Core install uses base.txt only, never all.txt: all.txt bundles
        # every plugin's dependencies into one pip invocation, so a single
        # plugin needing a system-level C library pip can't provide (e.g.
        # rrdtool needs the rrdtool headers, not just a pip package) aborts
        # the *entire* install and masks the result for everything else.
        # Per-plugin requirements are installed individually, just before
        # that plugin's own smoke test, in the loop below.
        ok, pip_out = pip_install(
            venv_python, shng_dir / 'requirements' / 'base.txt', logs_dir / f'py_{version}_pip.log'
        )
        version_report['pip_install_ok'] = ok
        version_report['pip_findings'] = classify_output(pip_out)
        if not ok:
            print(f'pip install FAILED for Python {version} - see {logs_dir}/py_{version}_pip.log')

        prepare_etc(shng_dir, plugin_entries=None)
        core_result = run_smoke_test(venv_python, shng_dir)
        (logs_dir / f'py_{version}_core.log').write_text(core_result.output)
        version_report['core'] = {
            'started_ok': core_result.started_ok,
            'exited_cleanly': core_result.exited_cleanly,
            'exit_code': core_result.exit_code,
            'findings': core_result.findings,
        }
        status = 'OK' if core_result.started_ok and not core_result.findings else 'ISSUES'
        print(f'core smoke test: {status}')

        version_report['plugins'] = {}
        for plugin_name in requested_plugins:
            entry = matrix.get(plugin_name)
            if entry is None:
                print(f'  {plugin_name}: not in matrix file, computing on the fly (run build-matrix to persist this)')
                plugin_dir = shng_dir / 'plugins' / plugin_name
                entry = {
                    'dummy_params': compute_dummy_params_for_plugin(plugin_dir),
                    **dict(zip(('py_minversion', 'py_maxversion'), plugin_py_version_bounds(plugin_dir))),
                }

            if not python_version_in_range(version, entry.get('py_minversion'), entry.get('py_maxversion')):
                version_report['plugins'][plugin_name] = {'skipped': 'outside declared py_min/maxversion'}
                print(f'  {plugin_name}: SKIP (outside declared py_min/maxversion)')
                continue

            plugin_req_file = shng_dir / 'plugins' / plugin_name / 'requirements.txt'
            plugin_report = {}
            if plugin_req_file.is_file():
                pip_ok, pip_out = pip_install(
                    venv_python, plugin_req_file, logs_dir / f'py_{version}_plugin_{plugin_name}_pip.log'
                )
                plugin_report['pip_install_ok'] = pip_ok
                plugin_report['pip_findings'] = classify_output(pip_out)
                if not pip_ok:
                    print(f'  {plugin_name}: pip install of its requirements.txt FAILED')

            plugin_entries = {plugin_name: {'plugin_name': plugin_name, **entry['dummy_params']}}
            prepare_etc(shng_dir, plugin_entries=plugin_entries)
            plugin_result = run_smoke_test(venv_python, shng_dir)
            (logs_dir / f'py_{version}_plugin_{plugin_name}.log').write_text(plugin_result.output)
            plugin_report.update(
                {
                    'started_ok': plugin_result.started_ok,
                    'exited_cleanly': plugin_result.exited_cleanly,
                    'exit_code': plugin_result.exit_code,
                    'findings': plugin_result.findings,
                }
            )
            version_report['plugins'][plugin_name] = plugin_report
            status = 'OK' if plugin_result.started_ok and not plugin_result.findings else 'ISSUES'
            print(f'  {plugin_name}: {status}')

    report_path = workdir / 'reports' / 'matrix_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(f'\nFull report: {report_path}')
    print_markdown_summary(report)


def print_markdown_summary(report: dict):
    print('\n| Python | pip install | core | plugins with issues |')
    print('|---|---|---|---|')
    for version, v in report['versions'].items():
        pip_ok = v.get('pip_install_ok')
        pip_cell = 'ok' if pip_ok else ('n/a' if pip_ok is None else 'FAIL')
        core = v.get('core', {})
        core_cell = 'ok' if core.get('started_ok') and not core.get('findings') else 'ISSUES'
        bad_plugins = [
            name
            for name, res in v.get('plugins', {}).items()
            if not res.get('skipped') and (not res.get('started_ok') or res.get('findings'))
        ]
        print(f'| {version} | {pip_cell} | {core_cell} | {", ".join(bad_plugins) or "-"} |')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class _FullHelpAction(argparse._HelpAction):
    """
    argparse only shows a subparser's own arguments on `<prog> <action> -h`,
    not on the top-level `-h` (which just lists the action names). Print
    the top-level help plus every subcommand's full help in one go instead.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, subparser in action.choices.items():
                    print(f'\n{"=" * 70}\n{name}\n{"=" * 70}')
                    subparser.print_help()
        parser.exit()


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, add_help=False
    )
    parser.add_argument('-h', '--help', action=_FullHelpAction, help='show this help message and exit')
    sub = parser.add_subparsers(dest='action', required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--workdir', default=str(DEFAULT_WORKDIR), help='scratch dir for clones/venvs/reports')
    common.add_argument('--shng-branch', default='develop')
    common.add_argument('--plugins-branch', default='develop')
    common.add_argument('--matrix-file', default=str(DEFAULT_MATRIX_FILE))

    p_build = sub.add_parser('build-matrix', parents=[common], help='(re)generate the plugin dummy-parameter matrix')
    p_build.set_defaults(func=cmd_build_matrix)

    p_run = sub.add_parser('run', parents=[common], help='run the install/startup smoke test matrix')
    p_run.add_argument('--python-versions', help='comma-separated override, e.g. 3.11,3.12 (default: from CI workflow)')
    p_run.add_argument('--plugins', help='comma-separated plugin names, or "all" (default: core only)')
    p_run.add_argument('--yes', action='store_true', help='auto-confirm all install prompts')
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
