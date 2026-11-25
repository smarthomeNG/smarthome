#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SmartPluginWebIf.init_template_environment()'s opt-in autoescape
(lib/model/smartplugin.py), rendered through a real Jinja2 environment with
a plugin template extending a global template.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

import lib.module
from lib.model.smartplugin import SmartPluginWebIf

GLOBAL_BASE = '<header>{{ header }}</header>{% block body %}{% endblock %}'
PLUGIN_CHILD = '{% extends "base.html" %}{% set header = "<b>title</b>" %}{% block body %}{{ value }}{% endblock %}'


class _NoModules:
    def get_module(self, name):
        return None


class _Plugin:
    def __init__(self, gtemplates_dir):
        self.mod_http = type('ModHttp', (), {'gtemplates_dir': gtemplates_dir})()

    def path_join(self, *parts):
        return os.path.join(*parts)


class _WebIf(SmartPluginWebIf):
    def __init__(self, webif_dir, plugin):
        self.webif_dir = webif_dir
        self.plugin = plugin

    def translate(self, text):
        return text


class TestTemplateAutoescape(unittest.TestCase):
    def setUp(self):
        saved = lib.module._modules_instance
        lib.module._modules_instance = _NoModules()
        self.addCleanup(setattr, lib.module, '_modules_instance', saved)

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        webif_dir = os.path.join(tmp.name, 'webif')
        gtemplates_dir = os.path.join(tmp.name, 'gtemplates')
        os.makedirs(os.path.join(webif_dir, 'templates'))
        os.makedirs(gtemplates_dir)
        with open(os.path.join(gtemplates_dir, 'base.html'), 'w') as f:
            f.write(GLOBAL_BASE)
        with open(os.path.join(webif_dir, 'templates', 'child.html'), 'w') as f:
            f.write(PLUGIN_CHILD)
        self.webif = _WebIf(webif_dir, _Plugin(gtemplates_dir))

    def test_default_does_not_escape(self):
        env = self.webif.init_template_environment()

        html = env.get_template('child.html').render(value='<script>x</script>')

        self.assertIn('<script>x</script>', html)

    def test_listed_template_escapes_its_own_output(self):
        env = self.webif.init_template_environment(autoescape_templates=('child.html',))

        html = env.get_template('child.html').render(value='<script>x</script>')

        self.assertIn('&lt;script&gt;x&lt;/script&gt;', html)

    def test_unlisted_global_template_keeps_its_raw_output(self):
        env = self.webif.init_template_environment(autoescape_templates=('child.html',))

        html = env.get_template('child.html').render(value='v')

        self.assertIn('<header><b>title</b></header>', html)


if __name__ == '__main__':
    unittest.main()
