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
Single entry point for opting into lib.orb's skyfield backend:
  1) installs the skyfield package itself (pip), if not already present
  2) downloads the skyfield ephemeris file (de421.bsp, ~17MB) it needs, if
     not already present

skyfield is deliberately NOT in lib/requirements.txt - shpypi's core-requirements
check (run by bin/smarthome.py on every startup) runs before smarthome.yaml is
even parsed, so it can't know whether orb_backend is actually set to
'skyfield', and would otherwise install skyfield's dependencies (numpy, sgp4,
jplephem) for every installation regardless of whether it's ever used. Run
this script once instead, then set ``orb_backend: skyfield`` in
etc/smarthome.yaml.

The ephemeris file is the only network access the skyfield backend ever
requires: de421.bsp covers 1899-07-28 through 2053-10-08 and never needs
re-fetching within that range. Re-running this script is always safe and a
no-op once both the package and the file are in place (skyfield.api.Loader
skips its own download if the file already exists at the target path).

Usage:
    tools/fetch_skyfield_data.py
"""

import os
import subprocess
import sys

sh_basedir = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2])
sys.path.insert(0, sh_basedir)

# Keep this in sync with tests/requirements.txt's skyfield line.
SKYFIELD_REQUIREMENT = 'skyfield>=1.49,<2.0.0'

try:
    import skyfield  # noqa: F401
except ImportError:
    print(f"skyfield is not installed. Installing it now ('pip install {SKYFIELD_REQUIREMENT}')...", flush=True)
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', SKYFIELD_REQUIREMENT])
    except subprocess.CalledProcessError as e:
        print(f'ERROR: pip install failed: {e}')
        print(f"Install it manually, then re-run this script: pip install '{SKYFIELD_REQUIREMENT}'")
        sys.exit(1)

try:
    from lib.orb import _BACKENDS, _SkyfieldBackend
except ImportError as e:
    print("Could not import lib.orb - is SmartHomeNG's venv active? ({})".format(e))
    sys.exit(1)

if 'skyfield' not in _BACKENDS:
    print("lib.orb's skyfield backend is still not available after installing skyfield - see the error above.")
    sys.exit(1)

data_dir = _SkyfieldBackend._data_dir()
target = os.path.join(data_dir, 'de421.bsp')

if os.path.exists(target):
    print(f'Skyfield ephemeris data already present at {target} - nothing to do.')
    sys.exit(0)

print(f'Fetching skyfield ephemeris data (de421.bsp, ~17MB) to {data_dir} ...', flush=True)
print('This is a one-time download - the file is valid through 2053 and will not be re-fetched.', flush=True)

try:
    _SkyfieldBackend._ensure_loaded()
except Exception as e:
    print(f'ERROR: could not download skyfield ephemeris data: {e}')
    sys.exit(1)

print(f'Done. Skyfield ephemeris data is now cached at {target}.')
print("You can now set 'orb_backend: skyfield' in etc/smarthome.yaml.")
