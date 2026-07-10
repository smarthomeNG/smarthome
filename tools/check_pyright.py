#!/usr/bin/env python3
"""
Run pyright and print only the diagnostics for files under the current
working directory (or --root).

Why: pyright's own `exclude` config only stops it from independently
walking a directory for *unreferenced* files. A file that's actually
imported — e.g. a plugin importing lib.item.items via the plugins repo's
extraPaths — still gets fully analyzed and reported, exclude or not (this
is documented pyright behavior, not a bug). Since the shng core repo and
the plugins repo share import graphs but are checked from two different
project roots, a plain `pyright` run from either repo pulls in the
other's diagnostics too. This wrapper filters them back out by file path.

Usage (from either repo root, or any subdirectory of it):
    python tools/check_pyright.py [pyright args...]

Exit code mirrors pyright's own convention: 0 if no errors were found
within scope, 1 otherwise (regardless of what pyright found outside scope).
"""

import argparse
import json
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=os.getcwd(), help='Only report diagnostics under this path (default: cwd)')
    parser.add_argument('--pyright', default='pyright', help='Path to the pyright executable')
    args, pyright_args = parser.parse_known_args()

    root = os.path.realpath(args.root) + os.sep

    proc = subprocess.run([args.pyright, '--outputjson', *pyright_args], capture_output=True, text=True)

    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode

    diagnostics = [d for d in report['generalDiagnostics'] if os.path.realpath(d['file']).startswith(root)]

    for d in diagnostics:
        line = d['range']['start']['line'] + 1
        col = d['range']['start']['character'] + 1
        print(
            f'{d["file"]}:{line}:{col} - {d["severity"]}: {d["message"]} ({d["rule"]})'
            if d.get('rule')
            else f'{d["file"]}:{line}:{col} - {d["severity"]}: {d["message"]}'
        )

    errors = sum(1 for d in diagnostics if d['severity'] == 'error')
    warnings = sum(1 for d in diagnostics if d['severity'] == 'warning')
    print(f'\n{errors} errors, {warnings} warnings (scoped to {args.root})')

    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
