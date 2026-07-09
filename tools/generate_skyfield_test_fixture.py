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
Regenerates tests/resources/skyfield/de421_excerpt.bsp - the trimmed
ephemeris fixture tests/test_orb.py seeds lib.orb's skyfield backend with,
so the test suite never downloads the full de421.bsp (~17MB) from NASA/NAIF.

Background: tests/requirements.txt installs skyfield unconditionally, so
every *Skyfield/*SkyfieldCached test class in tests/test_orb.py runs for
real in CI. Without this fixture, the first Orb(backend='skyfield') call
would trigger a fresh download per CI job - and unittests.yml runs a 5-way
Python version matrix in parallel, so a single push/PR fires up to 5
simultaneous downloads of the same file from GitHub Actions' shared IP
ranges. That's enough to get rate-limited/blocked by NASA's servers,
failing CI for a reason unrelated to the actual code change.

Uses jplephem's `excerpt` tool to slice a full de421.bsp down to just the
date range tests/test_orb.py's fixed test dates need. This needs to cover:
  - every fixed datetime constant in tests/test_orb.py (currently spanning
    2024-03-20 through 2024-12-21)
  - PLUS lib.orb's cached skyfield backend's default 365-day lookahead
    window (_SkyfieldCachedBackend.CACHE_HORIZON_DAYS) from the LATEST such
    date, since TestSkyfieldCachedMatchesUncached queries with the default
    (uncustomized) horizon

If test_orb.py's fixed dates ever move outside the excerpt's current
2023-12-01..2026-01-15 range, widen the --start/--end below and rerun this
script. jplephem must already be installed (it's a skyfield dependency).

Usage:
    tools/generate_skyfield_test_fixture.py [--source path/to/de421.bsp]

Without --source, downloads the full de421.bsp via lib.orb's normal
skyfield loading path first (one-time network access, same as running
tools/fetch_skyfield_data.py) - use --source to point at an already-cached
copy (e.g. var/cache/skyfield-data/de421.bsp) instead.
"""

import argparse
import os
import subprocess
import sys

sh_basedir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

EXCERPT_START = '2023/12/01'
EXCERPT_END = '2026/01/15'
FIXTURE_PATH = os.path.join(sh_basedir, 'tests', 'resources', 'skyfield', 'de421_excerpt.bsp')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', help='Path to an already-downloaded de421.bsp (skips fetching one)')
    args = parser.parse_args()

    if args.source:
        source = args.source
        if not os.path.exists(source):
            print(f'ERROR: {source} does not exist.')
            sys.exit(1)
    else:
        from lib.orb import _SkyfieldBackend

        print('No --source given - fetching the full de421.bsp via the normal skyfield loading path...')
        _SkyfieldBackend._ensure_loaded()
        source = os.path.join(_SkyfieldBackend._data_dir(), 'de421.bsp')

    os.makedirs(os.path.dirname(FIXTURE_PATH), exist_ok=True)

    print(f'Excerpting {EXCERPT_START}..{EXCERPT_END} from {source} to {FIXTURE_PATH} ...')
    # Shells out to jplephem's own CLI rather than calling its excerpter
    # module directly - that internal API takes pre-parsed Julian dates and
    # DAF/SPK objects (see jplephem.commandline.excerpt), which is more
    # likely to shift across jplephem versions than its documented CLI.
    subprocess.check_call(
        [sys.executable, '-m', 'jplephem', 'excerpt', EXCERPT_START, EXCERPT_END, source, FIXTURE_PATH]
    )

    size_kb = os.path.getsize(FIXTURE_PATH) / 1024
    print(f'Done. Fixture is {size_kb:.0f} KB.')


if __name__ == '__main__':
    main()
