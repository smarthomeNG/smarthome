"""Test-only dummy plugin that is not derived from SmartPlugin.

Used by tests/test_plugin_classic_rejected.py. Not collected by pytest
(module name doesn't match test_*.py).
"""


class ClassicPlugin:
    def __init__(self, sh):
        self.sh = sh

    def run(self):
        pass

    def stop(self):
        pass
