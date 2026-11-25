#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Data of a single send: per-send keyword arguments, template variables, data_dict."""

import builtins

builtins.SDP_standalone = False

import tempfile  # noqa: E402
import unittest  # noqa: E402

from lib.model.sdp import datatypes as DT  # noqa: E402
from lib.model.sdp.command import SDPCommandParseStr, SDPCommandStr  # noqa: E402
from tests.sdp_harness import load_sdp_plugin  # noqa: E402


class TestPluginSend(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.rig = load_sdp_plugin(
            self._tmp.name, 'tests.fixture_sdp_plugin', 'FixtureSDPRules', '', params={'host': 'h'}
        )
        self.plugin = self.rig.plugin
        self.plugin.run()
        self.seen: list[dict] = []
        before_send = self.plugin._do_before_send

        def capture(command, value, kwargs):
            self.seen.append(dict(kwargs))
            return before_send(command, value, kwargs)

        self.plugin._do_before_send = capture

    def tearDown(self):
        self.plugin.stop()
        self._tmp.cleanup()

    def test_hooks_get_only_per_send_arguments(self):
        self.plugin.send_command('status.power', by='test')

        self.assertEqual([{'by': 'test'}], self.seen)

    def test_template_vars_fill_param_templates(self):
        self.plugin.template_vars['zone'] = '2'

        self.plugin.send_command('status.input')

        self.assertTrue(self.rig.connection.payloads[-1].startswith('IN2/h'), self.rig.connection.payloads)

    def test_template_vars_are_read_on_each_send(self):
        self.plugin.template_vars['zone'] = '2'
        self.plugin.send_command('status.input')
        self.plugin.template_vars['zone'] = '3'

        self.plugin.send_command('status.input')

        self.assertTrue(self.rig.connection.payloads[-1].startswith('IN3/'), self.rig.connection.payloads)

    def test_plugin_parameters_are_not_changed_by_template_vars(self):
        self.plugin.template_vars['host'] = 'x'

        self.assertEqual('h', self.plugin._parameters['host'])


class TestCommandTemplates(unittest.TestCase):
    def command(self, cls, template_vars, **cmd):
        return cls('c', DT.DT_raw, cmd={'read': True, **cmd}, template_vars=template_vars)

    def test_custom_param_template(self):
        cmd = self.command(SDPCommandParseStr, {'LIST': {'p1': '42'}}, read_cmd='LS{CUSTOM_PARAM1:LIST}')

        self.assertEqual('LS42', cmd.get_send_data(None, custom={1: 'p1'})['payload'])

    def test_send_arguments_are_not_kept(self):
        template_vars: dict = {}
        cmd = self.command(SDPCommandParseStr, template_vars, read_cmd='X')

        cmd.get_send_data(None, custom={1: 'p1'}, by='test')

        self.assertEqual({}, template_vars)

    def test_str_data_dict_has_only_request_arguments(self):
        cmd = self.command(SDPCommandStr, {'headers': {'a': '{PARAM:host}'}, 'host': 'h', 'model': 'm'}, opcode='X')

        self.assertEqual({'payload': 'X', 'headers': {'a': 'h'}}, cmd.get_send_data(None, by='test'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
