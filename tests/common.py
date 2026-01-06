
import os
import sys
import pathlib

# with Linux standard installation of SmartHomeNG
# realpath of __file__ will be '/usr/local/smarthome/tests/common.py'
# so BASE becomes '/usr/local/smarthome'
if os.name != 'nt':
    BASE = '/'.join(os.path.realpath(__file__).split('/')[:-2])
else:
    BASE = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, BASE)
