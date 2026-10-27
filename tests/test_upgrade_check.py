#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for tools/upgrade_check.py: every check runs against a small installation created in a temp dir.
"""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import textwrap
import unittest
from pathlib import Path

from ruamel.yaml import YAML

TOOL_PATH = os.path.join(os.path.dirname(__file__), '..', 'tools', 'upgrade_check.py')


def load_tool():
    spec = importlib.util.spec_from_file_location('upgrade_check', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tool = load_tool()


class InstallationTestCase(unittest.TestCase):
    """A temp installation with helpers to write its files."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='SHNG_upgrade.')
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        self.project = tool.Project(self.base)

    def write(self, relative: str, text: str) -> Path:
        path = self.base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip('\n'), encoding='utf-8')
        return path

    def read(self, relative: str) -> str:
        return (self.base / relative).read_text(encoding='utf-8')

    def plugin_meta(self, name: str, attributes=(), prefixes=()):
        lines = ['plugin:', f'    classname: {name.title()}', 'item_attributes:']
        lines += [f'    {a}:\n        type: str' for a in attributes] or ['    {}']
        if prefixes:
            lines += ['item_attribute_prefixes:'] + [f'    {p}:\n        type: str' for p in prefixes]
        self.write(f'plugins/{name}/plugin.yaml', '\n'.join(lines) + '\n')

    def run_check(self, name: str, fix: bool = False):
        return tool.CHECKERS[name].run(self.project, fix)


class TestInstances(InstallationTestCase):
    def setUp(self):
        super().setUp()
        self.plugin_meta('avm', attributes=['avm_data_type'])
        self.plugin_meta('knx', attributes=['knx_dpt'])
        self.write(
            'etc/plugin.yaml',
            """
            # the fritzboxes
            fritzbox_1:
                plugin_name: avm
                instance: fb6360     # keep this comment
            fritzbox_2:
                plugin_name: avm
            knx:
                plugin_name: knx
            """,
        )
        self.write(
            'etc/items/wan.yaml',
            """
            wan:
                type: foo
                avm_data_type@fb6360: uptime
                knx_dpt@fb6360: '1'
            """,
        )

    def test_finds_but_does_not_change_anything_without_fix(self):
        before = self.read('etc/plugin.yaml'), self.read('etc/items/wan.yaml')

        findings = self.run_check('instances')

        self.assertEqual(2, len(findings))
        self.assertFalse(any(f.fixed for f in findings))
        self.assertEqual(before, (self.read('etc/plugin.yaml'), self.read('etc/items/wan.yaml')))

    def test_section_without_instance_gets_default(self):
        self.run_check('instances', fix=True)

        sections = YAML(typ='safe').load(self.read('etc/plugin.yaml'))
        self.assertEqual('default', sections['fritzbox_2']['instance'])
        self.assertNotIn('instance', sections['knx'])
        self.assertIn('# keep this comment', self.read('etc/plugin.yaml'))

    def test_item_attributes_of_the_plugin_follow_the_section_name(self):
        self.run_check('instances', fix=True)

        items = self.read('etc/items/wan.yaml')
        self.assertIn('avm_data_type@fritzbox_1: uptime', items)
        self.assertIn("knx_dpt@fb6360: '1'", items)

    def test_second_run_finds_nothing(self):
        self.run_check('instances', fix=True)

        self.assertEqual([], self.run_check('instances'))

    def test_fix_backs_up_changed_files(self):
        self.run_check('instances', fix=True)

        backups = list((self.base / 'etc' / tool.BACKUP_DIR).rglob('*.yaml'))
        self.assertEqual({'plugin.yaml', 'wan.yaml'}, {p.name for p in backups})
        self.assertIn('avm_data_type@fb6360', [p for p in backups if p.name == 'wan.yaml'][0].read_text())

    def test_single_section_with_instance_loses_the_suffix(self):
        self.write(
            'etc/plugin.yaml',
            """
            knx:
                plugin_name: knx
                instance: bus1
            """,
        )
        self.write('etc/items/a.yaml', "a:\n    knx_dpt@bus1: '5'\n")

        self.run_check('instances', fix=True)

        self.assertEqual("a:\n    knx_dpt: '5'\n", self.read('etc/items/a.yaml'))

    def test_disabled_sections_are_not_counted(self):
        self.write(
            'etc/plugin.yaml',
            """
            fritzbox_1:
                plugin_name: avm
                instance: fb6360
            fritzbox_2:
                plugin_name: avm
                plugin_enabled: false
            """,
        )

        findings = self.run_check('instances')

        self.assertEqual(1, len(findings))
        self.assertEqual('wan.yaml', findings[0].path.name)

    def test_prefix_attributes_are_renamed_too(self):
        self.plugin_meta('stateengine', prefixes=['se_'])
        self.write(
            'etc/plugin.yaml',
            """
            se_a:
                plugin_name: stateengine
                instance: one
            se_b:
                plugin_name: stateengine
                instance: two
            """,
        )
        self.write('etc/items/s.yaml', 's:\n    se_item_x@one: foo\n    se_item_x@two: bar\n')

        self.run_check('instances', fix=True)

        self.assertEqual('s:\n    se_item_x@se_a: foo\n    se_item_x@se_b: bar\n', self.read('etc/items/s.yaml'))

    def test_two_sections_with_the_same_instance_cannot_be_fixed(self):
        self.write(
            'etc/plugin.yaml',
            """
            a:
                plugin_name: avm
                instance: same
            b:
                plugin_name: avm
                instance: same
            """,
        )

        findings = self.run_check('instances')

        self.assertTrue(any(not f.fixable and 'same' in f.message for f in findings))


class TestPluginAlias(InstallationTestCase):
    def setUp(self):
        super().setUp()
        self.write('etc/plugin.yaml', 'knx:\n    plugin_name: knx\nmqtt:\n    plugin_name: mqtt\n')
        self.write(
            'etc/logics/lights.py',
            """
            # sh.knx in a comment stays
            text = "sh.knx in a string stays"
            sh.knx.send('1/1/1', 1)
            sh.plugins.mqtt.publish('a', 1)
            self.sh.knx.stays()
            x = sh.mqtt
            """,
        )

    def test_attribute_access_gets_plugins_in_between(self):
        self.run_check('plugin-alias', fix=True)

        code = self.read('etc/logics/lights.py')
        self.assertIn("sh.plugins.knx.send('1/1/1', 1)", code)
        self.assertIn('x = sh.plugins.mqtt', code)
        self.assertIn("sh.plugins.mqtt.publish('a', 1)", code)
        self.assertIn('# sh.knx in a comment stays', code)
        self.assertIn('"sh.knx in a string stays"', code)
        self.assertIn('self.sh.knx.stays()', code)

    def test_detection_does_not_change_files(self):
        before = self.read('etc/logics/lights.py')

        findings = self.run_check('plugin-alias')

        self.assertEqual(2, len(findings))
        self.assertEqual(before, self.read('etc/logics/lights.py'))

    def test_item_evals_are_rewritten(self):
        self.write('etc/items/a.yaml', "a:\n    eval: sh.knx.read('1/2/3')\n    other: sh.knxfoo\n")

        self.run_check('plugin-alias', fix=True)

        self.assertEqual(
            "a:\n    eval: sh.plugins.knx.read('1/2/3')\n    other: sh.knxfoo\n", self.read('etc/items/a.yaml')
        )

    def test_a_section_named_like_a_top_level_item_is_left_alone(self):
        self.write('etc/items/knx.yaml', 'knx:\n    type: foo\n')

        findings = self.run_check('plugin-alias', fix=True)

        self.assertIn('sh.knx.send', self.read('etc/logics/lights.py'))
        self.assertTrue(any(not f.fixable and "'knx'" in f.message for f in findings))

    def test_a_section_named_like_a_smarthome_attribute_is_left_alone(self):
        self.write('etc/plugin.yaml', 'trigger:\n    plugin_name: knx\nalive:\n    plugin_name: mqtt\n')
        self.write('etc/logics/lights.py', 'sh.trigger.send()\nsh.alive.send()\n')

        findings = self.run_check('plugin-alias', fix=True)

        self.assertEqual('sh.trigger.send()\nsh.alive.send()\n', self.read('etc/logics/lights.py'))
        self.assertEqual({'trigger', 'alive'}, {f.message.split("'")[1] for f in findings if not f.fixable})

    def test_a_section_named_like_a_removed_sh_method_or_core_item_is_left_alone(self):
        self.write('etc/plugin.yaml', 'now:\n    plugin_name: knx\nenv:\n    plugin_name: mqtt\n')
        self.write('etc/logics/lights.py', 'sh.now.send()\nsh.env.send()\n')

        self.run_check('plugin-alias', fix=True)

        self.assertEqual('sh.now.send()\nsh.env.send()\n', self.read('etc/logics/lights.py'))

    def test_second_run_finds_nothing(self):
        self.run_check('plugin-alias', fix=True)

        self.assertEqual([], self.run_check('plugin-alias'))


class TestShAttributeNames(unittest.TestCase):
    def test_covers_everything_the_smarthome_class_defines(self):
        from lib.smarthome import SmartHome

        public = {name for name in dir(SmartHome) if not name.startswith('__')}

        self.assertEqual(set(), public - tool.smarthome_attribute_names())

    def test_covers_attributes_set_on_the_instance(self):
        names = tool.smarthome_attribute_names()

        self.assertLessEqual({'items', 'plugins', 'trigger', 'alive', 'shtime', 'item_count', 'version'}, names)


class TestPluginClass(InstallationTestCase):
    def setUp(self):
        super().setUp()
        self.plugin_meta('avm')
        self.plugin_meta('hue')

    def test_class_path_becomes_plugin_name(self):
        self.write(
            'etc/plugin.yaml',
            """
            fritz:
                class_name: AVM
                class_path: plugins.avm
                host: 1.2.3.4
            """,
        )

        self.run_check('plugin-class', fix=True)

        section = YAML(typ='safe').load(self.read('etc/plugin.yaml'))['fritz']
        self.assertEqual({'plugin_name': 'avm', 'host': '1.2.3.4'}, section)

    def test_old_plugin_version_is_kept_as_plugin_version(self):
        self.write('etc/plugin.yaml', 'bridge:\n    class_name: HUE\n    class_path: plugins.hue._pv_1_1_83\n')

        self.run_check('plugin-class', fix=True)

        section = YAML(typ='safe').load(self.read('etc/plugin.yaml'))['bridge']
        self.assertEqual({'plugin_name': 'hue', 'plugin_version': '1.1.83'}, section)

    def test_ignored_keys_next_to_plugin_name_are_removed(self):
        self.write('etc/plugin.yaml', 'fritz:\n    plugin_name: avm\n    class_path: plugins.avm\n')

        self.run_check('plugin-class', fix=True)

        self.assertEqual({'plugin_name': 'avm'}, YAML(typ='safe').load(self.read('etc/plugin.yaml'))['fritz'])

    def test_plugin_outside_of_the_plugins_directory_needs_manual_work(self):
        text = 'own:\n    class_name: Own\n    class_path: myplugins.own\n'
        self.write('etc/plugin.yaml', text)

        findings = self.run_check('plugin-class', fix=True)

        self.assertEqual(1, len(findings))
        self.assertFalse(findings[0].fixable)
        self.assertEqual(text, self.read('etc/plugin.yaml'))

    def test_unknown_plugin_is_not_converted(self):
        self.write('etc/plugin.yaml', 'x:\n    class_name: X\n    class_path: plugins.missing\n')

        findings = self.run_check('plugin-class', fix=True)

        self.assertFalse(findings[0].fixable)
        self.assertIn('class_path', self.read('etc/plugin.yaml'))


class TestRemovedApi(InstallationTestCase):
    def test_removed_methods_are_replaced(self):
        self.write(
            'etc/logics/l.py',
            """
            item = sh.return_item('a.b')
            now = sh.now()
            mods = sh.get_module('admin')
            where = sh.base_dir
            up = sh.tools.runtime()
            ok = sh.items.return_item('c')
            other.sh.now()
            """,
        )

        self.run_check('removed-api', fix=True)

        code = self.read('etc/logics/l.py')
        self.assertIn("item = sh.items.return_item('a.b')", code)
        self.assertIn('now = sh.shtime.now()', code)
        self.assertIn("mods = sh.modules.get_module('admin')", code)
        self.assertIn('where = sh.get_basedir()', code)
        self.assertIn('up = sh.shtime.runtime()', code)
        self.assertIn("ok = sh.items.return_item('c')", code)
        self.assertIn('other.sh.now()', code)

    def test_replacements_that_need_an_import_are_only_reported(self):
        text = "x = sh.tools.dewpoint(20, 50)\nflag = sh.string2bool('yes')\n"
        self.write('etc/logics/l.py', text)

        findings = self.run_check('removed-api', fix=True)

        self.assertEqual(text, self.read('etc/logics/l.py'))
        self.assertEqual(2, len(findings))
        self.assertTrue(all(not f.fixable and not f.fixed for f in findings))
        self.assertIn('Utils.dewpoint', findings[0].message)

    def test_functions_directory_is_checked_too(self):
        self.write('etc/functions/f.py', 'def f():\n    return sh.now()\n')

        self.run_check('removed-api', fix=True)

        self.assertIn('sh.shtime.now()', self.read('etc/functions/f.py'))

    def test_item_evals_are_rewritten(self):
        self.write('etc/items/a.yaml', "a:\n    eval: sh.return_item('b')() + sh.items.x\n")

        self.run_check('removed-api', fix=True)

        self.assertEqual("a:\n    eval: sh.items.return_item('b')() + sh.items.x\n", self.read('etc/items/a.yaml'))

    def test_legacy_layout_is_found_when_there_is_no_etc_directory_for_logics(self):
        self.write('logics/l.py', 'x = sh.now()\n')

        findings = self.run_check('removed-api')

        self.assertEqual(1, len(findings))

    def test_unreadable_python_is_skipped(self):
        self.write('etc/logics/broken.py', 'def (:\n  sh.now(\n')

        self.assertEqual([], self.run_check('removed-api', fix=True))


class TestLibToolsImport(InstallationTestCase):
    def test_lib_tools_imports_are_reported(self):
        text = 'from lib.tools import Tools\nimport lib.tools\nx = lib.tools.Tools()\n'
        self.write('etc/logics/l.py', text)

        findings = self.run_check('removed-api', fix=True)

        self.assertEqual(text, self.read('etc/logics/l.py'))
        self.assertEqual([1, 2, 3], [f.line for f in findings])
        self.assertTrue(all(not f.fixable for f in findings))
        self.assertIn('lib.tools', findings[0].message)


class TestConfFiles(InstallationTestCase):
    def test_leftover_conf_files_are_reported(self):
        self.write('etc/plugin.conf', '[x]\n')
        self.write('etc/items/house.conf', '[a]\n')
        self.write('etc/logics/notes.conf', 'x\n')
        self.write('etc/items/house.yaml', 'a: {}\n')

        findings = self.run_check('conf-files', fix=True)

        names = sorted(f.path.name for f in findings)
        self.assertEqual(['house.conf', 'plugin.conf'], names)
        self.assertTrue(all(not f.fixable for f in findings))
        self.assertTrue((self.base / 'etc' / 'plugin.conf').exists())

    def test_scene_conf_files_are_left_to_the_scenes_check(self):
        self.write('etc/scenes/s.conf', '0 a.b 1\n')

        self.assertEqual([], self.run_check('conf-files'))


class TestModuleParams(InstallationTestCase):
    MODULE_YAML = """
        http:
            module_name: http
        admin:
            module_name: admin
            # keep this comment
            websocket_host: 0.0.0.0
            websocket_port: 2424
            pypi_timeout: 5
            log_chunksize: 100
        """

    def test_removed_parameters_are_reported(self):
        self.write('etc/module.yaml', self.MODULE_YAML)

        findings = self.run_check('module-params')

        self.assertEqual(3, len(findings))
        self.assertTrue(all(f.fixable and not f.fixed for f in findings))

    def test_removed_parameters_are_deleted_with_fix(self):
        self.write('etc/module.yaml', self.MODULE_YAML)

        self.run_check('module-params', fix=True)

        admin = YAML(typ='safe').load(self.read('etc/module.yaml'))['admin']
        self.assertEqual({'module_name': 'admin', 'log_chunksize': 100}, admin)
        self.assertIn('# keep this comment', self.read('etc/module.yaml'))


class TestPasswordHashes(InstallationTestCase):
    LEGACY = 'a' * 128

    def test_legacy_http_hashes_are_reported(self):
        self.write(
            'etc/module.yaml',
            f"""
            http:
                module_name: http
                hashed_password: {self.LEGACY}
                service_hashed_password: pbkdf2_sha256$600000$c2FsdA$ZGlnZXN0
            """,
        )

        findings = self.run_check('password-hash')

        self.assertEqual(1, len(findings))
        self.assertIn('hashed_password', findings[0].message)
        self.assertFalse(findings[0].fixable)

    def test_legacy_cli_hash_is_reported(self):
        self.write('etc/plugin.yaml', f'cli:\n    plugin_name: cli\n    hashed_password: {self.LEGACY}\n')

        findings = self.run_check('password-hash')

        self.assertEqual(['plugin.yaml'], [f.path.name for f in findings])


class TestScenes(InstallationTestCase):
    def test_conf_scene_becomes_yaml(self):
        self.write(
            'etc/scenes/example.conf',
            """
            # a comment
            0 otheritem 2
            1 otheritem 20
            1 LogicName run
            2 otheritem 5.5
            3 otheritem on
            """,
        )

        findings = self.run_check('scenes', fix=True)

        self.assertTrue(all(f.fixed for f in findings))
        self.assertFalse((self.base / 'etc/scenes/example.conf').exists())
        scene = YAML(typ='safe').load(self.read('etc/scenes/example.yaml'))
        self.assertEqual({'actions': [{'item': 'otheritem', 'value': 2}]}, scene[0])
        self.assertEqual(
            [{'item': 'otheritem', 'value': 20}, {'item': 'LogicName', 'value': 'run'}], scene[1]['actions']
        )
        self.assertEqual(5.5, scene[2]['actions'][0]['value'])
        self.assertEqual('on', scene[3]['actions'][0]['value'])

    def test_original_is_backed_up(self):
        self.write('etc/scenes/example.conf', '0 a 1\n')

        self.run_check('scenes', fix=True)

        backups = list((self.base / 'etc' / tool.BACKUP_DIR).rglob('example.conf'))
        self.assertEqual(1, len(backups))

    def test_existing_yaml_is_not_overwritten(self):
        self.write('etc/scenes/example.conf', '0 a 1\n')
        self.write('etc/scenes/example.yaml', '0:\n    actions: []\n')

        findings = self.run_check('scenes', fix=True)

        self.assertEqual('0:\n    actions: []\n', self.read('etc/scenes/example.yaml'))
        self.assertTrue((self.base / 'etc/scenes/example.conf').exists())
        self.assertFalse(any(f.fixed for f in findings))

    def test_broken_lines_are_reported_and_skipped(self):
        self.write('etc/scenes/example.conf', '0 a 1\nbroken line\n1 b\n')

        findings = self.run_check('scenes', fix=True)

        self.assertEqual(2, sum(1 for f in findings if not f.fixable))
        scene = YAML(typ='safe').load(self.read('etc/scenes/example.yaml'))
        self.assertEqual([0], list(scene))


class TestCommandLine(InstallationTestCase):
    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = tool.main(['--base', str(self.base), *args])
        return code, out.getvalue()

    def test_nothing_found_exits_with_zero(self):
        code, output = self.run_main()

        self.assertEqual(0, code)
        self.assertIn('Nothing found', output)

    def test_findings_exit_with_one_until_fixed(self):
        self.write('etc/logics/l.py', 'x = sh.now()\n')

        self.assertEqual(1, self.run_main()[0])
        self.assertEqual(0, self.run_main('--fix')[0])
        self.assertEqual(0, self.run_main()[0])

    def test_only_limits_the_checks(self):
        self.write('etc/logics/l.py', 'x = sh.now()\n')

        code, _ = self.run_main('--only', 'scenes')

        self.assertEqual(0, code)

    def test_json_output(self):
        self.write('etc/logics/l.py', 'x = sh.now()\n')

        _, output = self.run_main('--json')

        findings = json.loads(output)
        self.assertEqual('removed-api', findings[0]['checker'])
        self.assertEqual('etc/logics/l.py', findings[0]['path'])
        self.assertEqual(1, findings[0]['line'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
