"""
Tests for modules/admin/pullimpact.py - decides, from the files a pull changed, whether the core has to
be restarted or which configured plugins have to be reloaded.
"""

import unittest

from modules.admin.pullimpact import PendingReloads, core_restart_reasons, plugin_configs_by_dir, plugins_impact


class TestCoreRestartReasons(unittest.TestCase):
    def test_code_directories_require_a_restart(self):
        self.assertEqual(core_restart_reasons(['lib/item/items.py', 'modules/admin/api.py']), ['lib', 'modules'])
        self.assertEqual(core_restart_reasons(['bin/smarthome.py']), ['bin'])

    def test_other_files_do_not(self):
        self.assertEqual(core_restart_reasons(['doc/dev/public_api.md', 'tests/test_x.py', 'tools/x.py']), [])

    def test_nothing_changed(self):
        self.assertEqual(core_restart_reasons([]), [])


def impact(files, configs, old=None, new=None):
    """plugins_impact() with the plugin.yaml/requirements contents before and after given as {path: text}."""
    old, new = old or {}, new or {}
    return plugins_impact(files, configs, old.get, new.get)


class TestPluginsImpactCode(unittest.TestCase):
    def test_changed_code_of_a_configured_plugin_needs_a_reload_of_all_its_instances(self):
        result = impact(['hue2/__init__.py'], {'hue2': ['hue_a', 'hue_b']})
        self.assertEqual(result, {'restart': [], 'reload': ['hue_a', 'hue_b']})

    def test_a_plugin_that_is_not_configured_is_ignored(self):
        self.assertEqual(impact(['hue2/__init__.py'], {'mqtt2': ['mqtt']}), {'restart': [], 'reload': []})

    def test_each_plugin_is_listed_once(self):
        result = impact(
            ['hue2/__init__.py', 'hue2/webif/__init__.py', 'mqtt2/__init__.py'], {'hue2': ['h'], 'mqtt2': ['m']}
        )
        self.assertEqual(result['reload'], ['h', 'm'])

    def test_tests_docs_and_markdown_files_do_not_matter(self):
        files = ['hue2/tests/test_x.py', 'hue2/user_doc/config.rst', 'hue2/README.md']
        self.assertEqual(impact(files, {'hue2': ['h']}), {'restart': [], 'reload': []})


def plugin_yaml(**sections):
    """Renders a plugin.yaml with the given top-level sections, each a {key: {field: value}} mapping."""
    lines = []
    for section, entries in sections.items():
        lines.append(f'{section}:')
        for key, fields in entries.items():
            lines.append(f'    {key}:')
            lines.extend(f'        {field}: {value}' for field, value in fields.items())
    return '\n'.join(lines) + '\n'


class TestPluginsImpactMetadata(unittest.TestCase):
    CONFIGS = {'hue2': ['h']}

    def yaml_change(self, old, new):
        return impact(['hue2/plugin.yaml'], self.CONFIGS, old={'hue2/plugin.yaml': old}, new={'hue2/plugin.yaml': new})

    def test_changed_requirements_need_a_restart_to_install_the_packages(self):
        result = impact(['hue2/requirements.txt', 'hue2/__init__.py'], self.CONFIGS)
        self.assertEqual(result, {'restart': ['hue2: requirements.txt changed'], 'reload': []})

    def test_a_new_item_attribute_is_picked_up_by_a_reload(self):
        old = plugin_yaml(item_attributes={'a': {'type': 'str'}})
        new = plugin_yaml(item_attributes={'a': {'type': 'str'}, 'b': {'type': 'bool'}})
        self.assertEqual(self.yaml_change(old, new), {'restart': [], 'reload': ['h']})

    def test_changed_parameters_and_version_are_picked_up_by_a_reload(self):
        old = plugin_yaml(parameters={'p': {'type': 'str'}}, plugin={'meta': {'version': '1.0.0'}})
        new = plugin_yaml(parameters={'p': {'type': 'int'}}, plugin={'meta': {'version': '1.1.0'}})
        self.assertEqual(self.yaml_change(old, new), {'restart': [], 'reload': ['h']})

    def test_a_removed_item_attribute_is_picked_up_by_a_reload(self):
        old = plugin_yaml(item_attributes={'a': {'type': 'str'}, 'b': {'type': 'bool'}})
        new = plugin_yaml(item_attributes={'a': {'type': 'str'}})
        self.assertEqual(self.yaml_change(old, new), {'restart': [], 'reload': ['h']})

    def test_a_changed_definition_needs_a_restart_because_registered_definitions_are_kept_on_reload(self):
        for section in ('item_attributes', 'item_attribute_prefixes', 'item_structs', 'logic_parameters'):
            with self.subTest(section=section):
                old = plugin_yaml(**{section: {'a': {'type': 'str'}}})
                new = plugin_yaml(**{section: {'a': {'type': 'int'}}})
                self.assertEqual(self.yaml_change(old, new), {'restart': [f'hue2: {section} changed'], 'reload': []})

    def test_unparseable_plugin_yaml_needs_a_restart(self):
        result = self.yaml_change('item_attributes: [', plugin_yaml(item_attributes={}))
        self.assertEqual(result, {'restart': ['hue2: plugin.yaml not readable'], 'reload': []})

    def test_removed_plugin_yaml_needs_a_restart(self):
        result = impact(['hue2/plugin.yaml'], self.CONFIGS, old={'hue2/plugin.yaml': plugin_yaml()})
        self.assertEqual(result, {'restart': ['hue2: plugin.yaml removed'], 'reload': []})


class TestPluginsImpactRepositoryRoot(unittest.TestCase):
    def test_a_changed_package_init_needs_a_restart(self):
        self.assertEqual(impact(['__init__.py'], {}), {'restart': ['plugins package changed'], 'reload': []})

    def test_other_files_in_the_root_do_not_matter(self):
        self.assertEqual(
            impact(['README.md', 'conftest.py', 'pyproject.toml'], {'hue2': ['h']}), {'restart': [], 'reload': []}
        )


class TestPluginConfigsByDir(unittest.TestCase):
    def test_groups_the_instances_of_a_plugin_by_its_directory(self):
        loaded = [('hue_a', 'plugins.hue2'), ('mqtt', 'plugins.mqtt2'), ('hue_b', 'plugins.hue2')]
        self.assertEqual(plugin_configs_by_dir(loaded), {'hue2': ['hue_a', 'hue_b'], 'mqtt2': ['mqtt']})

    def test_plugins_from_other_locations_are_left_out(self):
        loaded = [('y', 'plugins.hue2._pv_1_0'), ('z', 'elsewhere.hue2'), ('w', 'plugins')]
        self.assertEqual(plugin_configs_by_dir(loaded), {})


class TestPendingReloads(unittest.TestCase):
    def test_remembers_added_names_sorted(self):
        pending = PendingReloads()
        pending.add(['b', 'a'])
        pending.add(['c', 'a'])
        self.assertEqual(pending.names(), ['a', 'b', 'c'])

    def test_discard_removes_a_name_and_ignores_unknown_ones(self):
        pending = PendingReloads()
        pending.add(['a', 'b'])
        pending.discard('a')
        pending.discard('unknown')
        self.assertEqual(pending.names(), ['b'])
        self.assertIn('b', pending)
        self.assertNotIn('a', pending)


class TestPluginsImpactEmptySections(unittest.TestCase):
    """plugin.yaml files mark a section without entries as `NONE`, which loads as a string."""

    CONFIGS = {'hue2': ['h']}

    def test_sections_marked_none_are_no_entries(self):
        old = 'item_attributes: NONE\nitem_structs: NONE\nlogic_parameters: NONE\n'
        new = old + 'parameters:\n    p:\n        type: str\n'
        result = impact(
            ['hue2/plugin.yaml'], self.CONFIGS, old={'hue2/plugin.yaml': old}, new={'hue2/plugin.yaml': new}
        )
        self.assertEqual(result, {'restart': [], 'reload': ['h']})

    def test_a_section_turning_from_none_into_entries_is_an_addition(self):
        old = 'item_attributes: NONE\n'
        new = plugin_yaml(item_attributes={'a': {'type': 'str'}})
        result = impact(
            ['hue2/plugin.yaml'], self.CONFIGS, old={'hue2/plugin.yaml': old}, new={'hue2/plugin.yaml': new}
        )
        self.assertEqual(result, {'restart': [], 'reload': ['h']})

    def test_a_document_that_is_not_a_mapping_needs_a_restart(self):
        result = impact(
            ['hue2/plugin.yaml'], self.CONFIGS, old={'hue2/plugin.yaml': '- a\n'}, new={'hue2/plugin.yaml': '- b\n'}
        )
        self.assertEqual(result, {'restart': ['hue2: plugin.yaml not readable'], 'reload': []})
