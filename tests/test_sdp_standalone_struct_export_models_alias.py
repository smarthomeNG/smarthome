#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for Standalone.create_struct_yaml()'s models[model]
handling (lib.model.smartdeviceplugin).

In the flat-commands-plus-models-dict branch, per model:

    self.cmdlist = models[model]                      # no copy - same list object
    self.cmdlist += models.get(INDEX_GENERIC, [])      # in-place extend

`models` is the live dict from the imported commands.py module, cached in
sys.modules by Python's import machinery. Binding self.cmdlist directly to
models[model] and then extending it in place permanently appends the
generic ('ALL') command list into that model's own list on the cached
module object. A single one-shot CLI run never notices (the process exits
right after), but calling create_struct_yaml() twice in the same process
- exactly what happens if it's ever invoked as a library call rather than
a fresh `python __init__.py -s` each time - corrupts the model's command
list further on every call.

denon/commands.py has a real per-model 'models' dict (unlike plugins that
only use the '{"ALL": {...}}' generic-key branch, e.g. viessmann), so it
actually exercises this code path.
"""

import copy
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest

import tests.common as common

common.register_shng_log_levels()

from tests._sdp_standalone_export_helper import build_standalone


class TestModelsDictNotMutatedAcrossRuns(unittest.TestCase):
    def test_second_struct_export_leaves_models_dict_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            standalone = build_standalone(tmp, 'denon')
            standalone.create_struct_yaml()

            # commands module is now cached in sys.modules under
            # plugins_denon.denon.commands - inspect its live 'models' dict
            cmd_module = sys.modules['plugins_denon.denon.commands']
            models = cmd_module.models
            model = next(m for m in models if m != 'ALL')
            before = copy.deepcopy(models[model])

            # re-running against the SAME cached module (a fresh Standalone
            # instance, but importlib.import_module hits sys.modules) must
            # not further mutate models[model]
            standalone2 = build_standalone(tmp, 'denon')
            standalone2.create_struct_yaml()

            after = models[model]
            self.assertEqual(
                before,
                after,
                f"models['{model}'] grew from {len(before)} to {len(after)} entries across repeated "
                'struct-export calls - self.cmdlist aliased models[model] instead of copying it',
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
