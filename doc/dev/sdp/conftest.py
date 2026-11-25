"""Puts the shng base directory on sys.path for the example plugin tests below this directory."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
