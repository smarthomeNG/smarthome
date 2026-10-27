#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for tools/plugin_metadata_checker.py: the plugin type in plugin.yaml is mandatory and has to be a known value.
"""

import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import textwrap
import unittest

BASE = os.path.join(os.path.dirname(__file__), '..')
TOOL_PATH = os.path.join(BASE, 'tools', 'plugin_metadata_checker.py')
sys.path.insert(0, os.path.join(BASE, 'lib'))


def load_tool():
    spec = importlib.util.spec_from_file_location('plugin_metadata_checker', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load_tool()


class TestPluginType(unittest.TestCase):
    """check_metadata() runs inside a plugins directory that holds one plugin."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='SHNG_plgcheck.')
        self.addCleanup(self._tmp.cleanup)
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)
        os.chdir(self._tmp.name)

    def check(self, type_line: str) -> str:
        """Check a plugin whose global section carries *type_line* (may be empty) and return the report."""
        os.mkdir('foo')
        with open('foo/__init__.py', 'w') as f:
            f.write('class Foo(SmartPlugin):\n    pass\n')
        with open('foo/plugin.yaml', 'w') as f:
            f.write(
                textwrap.dedent(
                    f"""
                    plugin:
                        version: 1.0.0
                        classname: Foo
                        state: ready
                        maintainer: me
                        {type_line}
                    """
                )
            )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tool.check_metadata('foo', False)
        return out.getvalue()

    def type_findings(self, report: str) -> list[str]:
        return [line for line in report.splitlines() if 'type' in line.lower() and line.startswith(('ERROR', 'WARN'))]

    def test_missing_type_is_an_error(self):
        findings = self.type_findings(self.check(''))

        self.assertEqual(1, len(findings))
        self.assertTrue(findings[0].startswith('ERROR'))

    def test_empty_type_is_an_error(self):
        findings = self.type_findings(self.check('type:'))

        self.assertEqual(1, len(findings))
        self.assertTrue(findings[0].startswith('ERROR'))

    def test_unknown_type_is_an_error(self):
        findings = self.type_findings(self.check('type: gadget'))

        self.assertEqual(1, len(findings))
        self.assertTrue(findings[0].startswith('ERROR'))
        self.assertIn('gadget', findings[0])

    def test_known_types_are_accepted(self):
        for plugin_type in ('gateway', 'interface', 'protocol', 'system', 'web'):
            with self.subTest(plugin_type):
                shutil.rmtree('foo', ignore_errors=True)
                self.assertEqual([], self.type_findings(self.check(f'type: {plugin_type}')))
