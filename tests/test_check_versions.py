#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for tools/check_versions.py: version bump checks for plugins and the core.

The pure helpers are tested directly; the checks run against small git repositories created in a temp dir.
"""

import contextlib
import importlib.util
import io
import os
import subprocess
import tempfile
import textwrap
import unittest
import unittest.mock
from pathlib import Path

TOOL_PATH = os.path.join(os.path.dirname(__file__), '..', 'tools', 'check_versions.py')


def load_tool():
    spec = importlib.util.spec_from_file_location('check_versions', TOOL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestBumpArithmetic(unittest.TestCase):
    def setUp(self):
        self.tool = load_tool()

    def test_bump_between_names_the_most_significant_part_that_grew(self):
        bump = self.tool.bump_between
        self.assertEqual('major', bump('1.4.2', '2.0.0'))
        self.assertEqual('minor', bump('1.4.2', '1.5.0'))
        self.assertEqual('patch', bump('1.4.2', '1.4.3'))
        self.assertEqual('none', bump('1.4.2', '1.4.2'))
        self.assertEqual('none', bump('1.4.2', '1.4.2+build'))

    def test_a_lower_version_is_down(self):
        self.assertEqual('down', self.tool.bump_between('1.4.2', '1.4.1'))
        self.assertEqual('down', self.tool.bump_between('2.0.0', '2.0.0-dev.1'))

    def test_prerelease_steps_count_as_patch_level(self):
        self.assertEqual('patch', self.tool.bump_between('2.0.0-dev.1', '2.0.0-dev.2'))
        self.assertEqual('patch', self.tool.bump_between('2.0.0-dev.2', '2.0.0'))
        self.assertEqual('major', self.tool.bump_between('1.12.2', '2.0.0-dev.1'))

    def test_required_bump_follows_the_most_severe_change(self):
        C, L = self.tool.Change, self.tool.Level
        required = self.tool.required_bump
        self.assertEqual('patch', required([], '1.0.0'))
        self.assertEqual('minor', required([C(L.MINOR, 'k', 'added')], '1.0.0'))
        self.assertEqual('major', required([C(L.MINOR, 'k', 'added'), C(L.MAJOR, 'k2', 'removed')], '1.0.0'))
        self.assertEqual('patch', required([C(L.REVIEW, 'k', 'default changed')], '1.0.0'))

    def test_below_one_zero_a_breaking_change_needs_only_a_minor_bump(self):
        C, L = self.tool.Change, self.tool.Level
        self.assertEqual('minor', self.tool.required_bump([C(L.MAJOR, 'k', 'removed')], '0.8.1'))
        self.assertEqual('major', self.tool.required_bump([C(L.MAJOR, 'k', 'removed')], '1.0.0'))


class GitRepoTestCase(unittest.TestCase):
    """Creates a git repository in a temp dir and commits file sets to it."""

    def setUp(self):
        self.tool = load_tool()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.git('init', '-q', '-b', 'main')

    def git(self, *args):
        identity = ['-c', 'user.name=t', '-c', 'user.email=t@example.org', '-c', 'commit.gpgsign=false']
        done = subprocess.run(
            ['git', '-C', str(self.repo), *identity, *args], check=True, capture_output=True, text=True
        )
        return done.stdout.strip()

    def commit(self, files, message='change'):
        """Write files ({path: text} or None to delete), commit them and return the new HEAD sha."""
        for rel, text in files.items():
            path = self.repo / rel
            if text is None:
                path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(textwrap.dedent(text))
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)
        return self.git('rev-parse', 'HEAD')


class TestPluginChecks(GitRepoTestCase):
    CORE = 'v2.0.0-dev.1'

    def plugin(self, version, extra='', code_version=None, name='foo', **files):
        """Files of a plugin whose plugin.yaml and code declare the given versions."""
        code_version = version if code_version is None else code_version
        return {
            f'{name}/plugin.yaml': f"plugin:\n    version: '{version}'\n{extra}",
            f'{name}/__init__.py': f"class Foo:\n    PLUGIN_VERSION = '{code_version}'\n",
            **files,
        }

    def check(self, base, skip=()):
        return self.tool.check_plugins(self.repo, base, 'HEAD', self.CORE, skip)

    def errors(self, findings):
        return [f.message for f in findings if f.severity == 'error']

    def assert_clean(self, findings):
        self.assertEqual([], [(f.severity, f.target, f.message) for f in findings])

    def test_code_change_without_version_bump_is_an_error(self):
        base = self.commit(self.plugin('1.0.0'))
        self.commit({'foo/__init__.py': "class Foo:\n    PLUGIN_VERSION = '1.0.0'\n    x = 1\n"})
        self.assertIn('version 1.0.0 not bumped although files changed', ' '.join(self.errors(self.check(base))))

    def test_code_change_with_patch_bump_is_fine(self):
        base = self.commit(self.plugin('1.0.0'))
        self.commit(self.plugin('1.0.1', x='y'))
        self.assert_clean(self.check(base))

    def test_tests_and_docs_do_not_demand_a_bump(self):
        base = self.commit(self.plugin('1.0.0'))
        self.commit({'foo/tests/test_foo.py': 'x = 1\n', 'foo/user_doc.rst': 'doc\n', 'foo/README.md': 'doc\n'})
        self.assert_clean(self.check(base))

    def test_unrelated_plugins_are_not_checked(self):
        base = self.commit({**self.plugin('1.0.0'), **self.plugin('1.0', name='bar')})
        self.commit(self.plugin('1.0.1', name='foo'))
        self.assert_clean(self.check(base))

    def test_version_must_be_semver(self):
        base = self.commit(self.plugin('1.0.0'))
        self.commit(self.plugin('1.1', x='y'))
        self.assertIn("version '1.1' is not a valid semver version", ' '.join(self.errors(self.check(base))))

    def test_new_plugin_needs_no_bump_but_valid_metadata(self):
        base = self.commit({'README': 'x\n'})
        self.commit(self.plugin('0.1.0'))
        self.assert_clean(self.check(base))
        self.commit(self.plugin('0.1', code_version='0.1', x='y'))
        self.assertTrue(self.errors(self.check(base)))

    def test_yaml_and_code_version_must_agree(self):
        base = self.commit(self.plugin('1.0.0'))
        self.commit(self.plugin('1.0.1', code_version='1.0.2'))
        self.assertIn(
            'plugin.yaml version 1.0.1 differs from PLUGIN_VERSION 1.0.2', ' '.join(self.errors(self.check(base)))
        )

    def test_parenthesized_multi_line_plugin_version_is_compared_too(self):
        wrapped = "class Foo:\n    PLUGIN_VERSION = (\n        '{}'  # keep in sync\n    )\n"
        base = self.commit(
            {'foo/plugin.yaml': "plugin:\n    version: '1.0.0'\n", 'foo/__init__.py': wrapped.format('1.0.0')}
        )
        self.commit({'foo/plugin.yaml': "plugin:\n    version: '1.0.1'\n", 'foo/__init__.py': wrapped.format('1.0.2')})
        self.assertIn(
            'plugin.yaml version 1.0.1 differs from PLUGIN_VERSION 1.0.2', ' '.join(self.errors(self.check(base)))
        )

    def test_plugin_without_code_version_skips_the_sync_check(self):
        files = {'foo/plugin.yaml': "plugin:\n    version: '1.0.0'\n", 'foo/__init__.py': 'x = 1\n'}
        base = self.commit(files)
        self.commit({'foo/plugin.yaml': "plugin:\n    version: '1.0.1'\n"})
        self.assert_clean(self.check(base))

    def test_version_must_not_go_down(self):
        base = self.commit(self.plugin('1.0.1'))
        self.commit(self.plugin('1.0.0', x='y'))
        self.assertIn('version went down', ' '.join(self.errors(self.check(base))))

    def test_removed_parameter_demands_a_major_bump(self):
        with_param = 'parameters:\n    host: {type: str}\n'
        base = self.commit(self.plugin('1.2.0', with_param))
        self.commit(self.plugin('1.2.1', 'parameters: NONE\n'))
        self.assertIn('major', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('1.3.0', 'parameters: NONE\n'))
        self.assertIn('major', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('2.0.0', 'parameters: NONE\n'))
        self.assert_clean(self.check(base))

    def test_below_one_zero_a_breaking_change_needs_a_minor_bump(self):
        base = self.commit(self.plugin('0.4.1', 'parameters:\n    host: {type: str}\n'))
        self.commit(self.plugin('0.4.2', 'parameters: NONE\n'))
        self.assertTrue(self.errors(self.check(base)))
        self.commit(self.plugin('0.5.0', 'parameters: NONE\n'))
        self.assert_clean(self.check(base))

    def test_new_function_demands_a_minor_bump(self):
        base = self.commit(self.plugin('1.0.0'))
        functions = 'plugin_functions:\n    ping:\n        type: bool\n'
        self.commit(self.plugin('1.0.1', functions))
        self.assertIn('minor', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('1.1.0', functions))
        self.assert_clean(self.check(base))

    def test_raising_sh_minversion_demands_a_major_bump_and_py_minversion_a_minor_one(self):
        base = self.commit(self.plugin('1.0.0', "    sh_minversion: '1.8'\n    py_minversion: '3.10'\n"))
        self.commit(self.plugin('1.1.0', "    sh_minversion: '1.9'\n    py_minversion: '3.10'\n"))
        self.assertIn('major', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('2.0.0', "    sh_minversion: '1.9'\n    py_minversion: '3.11'\n"))
        self.assert_clean(self.check(base))

    def test_raising_py_minversion_alone_demands_a_minor_bump(self):
        base = self.commit(self.plugin('2.0.0', "    py_minversion: '3.11'\n"))
        self.commit(self.plugin('2.0.1', "    py_minversion: '3.12'\n"))
        self.assertIn('minor', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('2.1.0', "    py_minversion: '3.12'\n"))
        self.assert_clean(self.check(base))

    def test_sh_minversion_above_the_core_version_is_an_error_even_for_a_new_plugin(self):
        base = self.commit({'README': 'x\n'})
        self.commit(self.plugin('1.0.0', "    sh_minversion: '2.0.0'\n"))
        self.assertIn('sh_minversion 2.0.0 is above the core version', ' '.join(self.errors(self.check(base))))
        self.commit(self.plugin('1.0.1', "    sh_minversion: '2.0.0-dev.1'\n"))
        self.assert_clean(self.check(base))

    def test_review_items_are_warnings(self):
        base = self.commit(self.plugin('1.0.0', 'parameters:\n    port: {type: int, default: 80}\n'))
        self.commit(self.plugin('1.0.1', 'parameters:\n    port: {type: int, default: 8080}\n'))
        findings = self.check(base)
        self.assertEqual([], self.errors(findings))
        self.assertEqual(['warning'], [f.severity for f in findings])

    def test_skipped_plugin_only_warns(self):
        base = self.commit(self.plugin('1.0.0', 'parameters:\n    host: {type: str}\n'))
        self.commit(self.plugin('1.0.0', 'parameters: NONE\n'))
        findings = self.check(base, skip=('foo',))
        self.assertEqual([], self.errors(findings))
        self.assertEqual(['warning'], [f.severity for f in findings])


class TestCoreChecks(GitRepoTestCase):
    def setUp(self):
        super().setUp()
        self.surface = self.tool.Surface(python_globs=['lib/*.py'])

    def core(self, version, code='class Plug:\n    def run(self): ...\n'):
        return {'bin/shngversion.py': f"shNG_version = '{version}'\n", 'lib/plug.py': code}

    def check(self, base, skip=False):
        return self.tool.check_core(self.repo, base, 'HEAD', self.surface, skip)

    def errors(self, findings):
        return ' '.join(f.message for f in findings if f.severity == 'error')

    def released(self, version='1.0.0'):
        base = self.commit(self.core(version))
        self.git('tag', f'v{version}')
        return base

    def test_version_must_be_semver(self):
        base = self.released()
        self.commit(self.core('1.1'))
        self.assertIn("shNG_version '1.1' is not a valid semver version", self.errors(self.check(base)))

    def test_breaking_change_since_the_last_release_demands_a_major_version(self):
        base = self.released()
        self.commit(self.core('1.1.0-dev.1', 'class Plug: ...\n'))
        self.assertIn('demand a major bump', self.errors(self.check(base)))
        self.commit(self.core('2.0.0-dev.1', 'class Plug: ...\n'))
        self.assertEqual('', self.errors(self.check(base)))

    def test_additions_demand_a_minor_version(self):
        base = self.released()
        added = 'class Plug:\n    def run(self): ...\n    def stop(self): ...\n'
        self.commit(self.core('1.0.1-dev.1', added))
        self.assertIn('demand a minor bump', self.errors(self.check(base)))
        self.commit(self.core('1.1.0-dev.1', added))
        self.assertEqual('', self.errors(self.check(base)))

    def test_version_at_the_last_release_with_changes_since_is_an_error(self):
        base = self.released()
        self.commit(self.core('1.0.0', 'class Plug:\n    def run(self): ...\n    # reworked\n'))
        self.assertIn('not above the last release v1.0.0', self.errors(self.check(base)))

    def test_version_must_not_go_down(self):
        base = self.commit(self.core('2.0.0-dev.2'))
        self.commit(self.core('2.0.0-dev.1'))
        self.assertIn('version went down', self.errors(self.check(base)))

    def test_without_a_release_tag_the_api_check_is_skipped_with_a_warning(self):
        base = self.commit(self.core('1.0.0'))
        self.commit(self.core('1.0.1', 'class Plug: ...\n'))
        findings = self.check(base)
        self.assertEqual('', self.errors(findings))
        self.assertEqual(['warning'], [f.severity for f in findings])

    def test_the_highest_release_tag_is_the_reference(self):
        base = self.released('1.0.0')
        self.commit(self.core('1.1.0', 'class Plug:\n    def run(self): ...\n    def a(self): ...\n'))
        self.git('tag', 'v1.1.0')
        self.git('tag', 'v1.12.2.2')
        self.commit(self.core('1.1.1-dev.1', 'class Plug:\n    def run(self): ...\n    def a(self): ...\n'))
        self.assertEqual('', self.errors(self.check(base)))

    def test_skip_only_warns(self):
        base = self.released()
        self.commit(self.core('1.0.1-dev.1', 'class Plug: ...\n'))
        findings = self.check(base, skip=True)
        self.assertEqual('', self.errors(findings))
        self.assertEqual(['warning'], [f.severity for f in findings])


class TestPrePushRanges(GitRepoTestCase):
    ZERO = '0' * 40

    def line(self, local_sha, remote_sha, local_ref='refs/heads/work', remote_ref='refs/heads/work'):
        return f'{local_ref} {local_sha} {remote_ref} {remote_sha}\n'

    def test_existing_remote_branch_is_checked_from_its_remote_tip(self):
        first = self.commit({'a': '1\n'})
        second = self.commit({'a': '2\n'})
        self.assertEqual([(first, second)], self.tool.pre_push_ranges(self.repo, self.line(second, first)))

    def test_branch_deletion_is_not_checked(self):
        sha = self.commit({'a': '1\n'})
        self.assertEqual([], self.tool.pre_push_ranges(self.repo, self.line(self.ZERO, sha)))

    def test_new_branch_is_checked_from_where_it_left_origin_develop(self):
        fork = self.commit({'a': '1\n'})
        self.git('update-ref', 'refs/remotes/origin/develop', fork)
        head = self.commit({'a': '2\n'})
        self.assertEqual([(fork, head)], self.tool.pre_push_ranges(self.repo, self.line(head, self.ZERO)))

    def test_new_branch_without_a_reference_branch_is_not_checked(self):
        head = self.commit({'a': '1\n'})
        self.assertEqual([], self.tool.pre_push_ranges(self.repo, self.line(head, self.ZERO)))

    def test_remote_tip_unknown_locally_falls_back_to_the_reference_branch(self):
        fork = self.commit({'a': '1\n'})
        self.git('update-ref', 'refs/remotes/origin/develop', fork)
        head = self.commit({'a': '2\n'})
        self.assertEqual([(fork, head)], self.tool.pre_push_ranges(self.repo, self.line(head, 'f' * 40)))


class TestFix(GitRepoTestCase):
    """--fix writes the version bump the check demands into plugin.yaml and PLUGIN_VERSION."""

    def files(self, version, extra='', comment='', code_version=None, wrapped=False):
        code_version = version if code_version is None else code_version
        yaml_text = f"plugin:\n    type: gateway\n    version: {version}{comment}\n    sh_minversion: '1.8'\n{extra}"
        if wrapped:
            code = f"class Foo:\n    PLUGIN_VERSION = (\n        '{code_version}'  # keep in sync\n    )\n"
        else:
            code = f"class Foo:\n    PLUGIN_VERSION = '{code_version}'{comment}\n"
        return {'foo/plugin.yaml': yaml_text, 'foo/__init__.py': code}

    def fix(self, base):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.tool.main(
                ['plugins', '--repo', str(self.repo), '--base', base, '--core-version', 'v2.0.0-dev.1', '--fix']
            )
        return code, out.getvalue()

    def check_clean(self, base):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.tool.main(
                ['plugins', '--repo', str(self.repo), '--base', base, '--core-version', 'v2.0.0-dev.1']
            )
        return code, out.getvalue()

    def read(self, path):
        return (self.repo / path).read_text()

    def test_unbumped_plugin_gets_a_patch_bump_in_yaml_and_code(self):
        base = self.commit(self.files('1.0.0'))
        self.commit({**self.files('1.0.0'), 'foo/x.py': 'x = 1\n'})
        code, out = self.fix(base)
        self.assertEqual(0, code)
        self.assertIn('FIXED foo: version 1.0.0 -> 1.0.1', out)
        self.assertIn('version: 1.0.1\n', self.read('foo/plugin.yaml'))
        self.assertIn("PLUGIN_VERSION = '1.0.1'", self.read('foo/__init__.py'))

    def test_the_bump_follows_the_demanded_level(self):
        with_param = 'parameters:\n    host: {type: str}\n'
        base = self.commit(self.files('1.2.3', with_param))
        self.commit(self.files('1.2.3', 'parameters: NONE\n'))
        self.assertEqual(0, self.fix(base)[0])
        self.assertIn('version: 2.0.0\n', self.read('foo/plugin.yaml'))
        self.assertIn("'2.0.0'", self.read('foo/__init__.py'))

    def test_an_insufficient_bump_is_raised_to_the_demanded_level(self):
        base = self.commit(self.files('1.2.3'))
        self.commit(self.files('1.2.4', 'plugin_functions:\n    ping:\n        type: bool\n'))
        self.assertEqual(0, self.fix(base)[0])
        self.assertIn('version: 1.3.0\n', self.read('foo/plugin.yaml'))

    def test_below_one_zero_a_breaking_change_gets_a_minor_bump(self):
        base = self.commit(self.files('0.4.1', 'parameters:\n    host: {type: str}\n'))
        self.commit(self.files('0.4.1', 'parameters: NONE\n'))
        self.assertEqual(0, self.fix(base)[0])
        self.assertIn('version: 0.5.0\n', self.read('foo/plugin.yaml'))

    def test_quotes_comments_and_wrapped_assignments_are_kept(self):
        base = self.commit(self.files("'1.0.0'", comment='   # Plugin version', code_version='1.0.0', wrapped=True))
        self.commit(
            {
                **self.files("'1.0.0'", comment='   # Plugin version', code_version='1.0.0', wrapped=True),
                'foo/x.py': 'x = 1\n',
            }
        )
        self.assertEqual(0, self.fix(base)[0])
        self.assertIn("    version: '1.0.1'   # Plugin version\n", self.read('foo/plugin.yaml'))
        self.assertIn("        '1.0.1'  # keep in sync\n    )", self.read('foo/__init__.py'))

    def test_plugin_without_a_code_version_only_changes_the_yaml(self):
        files = {'foo/plugin.yaml': 'plugin:\n    version: 1.0.0\n', 'foo/__init__.py': 'x = 1\n'}
        base = self.commit(files)
        self.commit({**files, 'foo/x.py': 'x = 1\n'})
        self.assertEqual(0, self.fix(base)[0])
        self.assertEqual('x = 1\n', self.read('foo/__init__.py'))
        self.assertIn('version: 1.0.1\n', self.read('foo/plugin.yaml'))

    def test_after_committing_the_fix_the_check_passes(self):
        base = self.commit(self.files('1.0.0', 'parameters:\n    host: {type: str}\n'))
        self.commit({**self.files('1.0.0', 'parameters: NONE\n'), 'foo/x.py': 'x = 1\n'})
        self.assertEqual(1, self.check_clean(base)[0])
        self.fix(base)
        self.commit({}, 'bump')
        self.assertEqual((0, ''), self.check_clean(base))

    def test_uncommitted_edits_in_the_files_are_not_overwritten(self):
        base = self.commit(self.files('1.0.0'))
        self.commit({**self.files('1.0.0'), 'foo/x.py': 'x = 1\n'})
        (self.repo / 'foo' / 'plugin.yaml').write_text(self.files('1.0.0')['foo/plugin.yaml'] + '# local edit\n')
        before = self.read('foo/plugin.yaml')
        code, out = self.fix(base)
        self.assertEqual(1, code)
        self.assertIn('uncommitted changes', out)
        self.assertEqual(before, self.read('foo/plugin.yaml'))

    def test_errors_without_a_mechanical_fix_remain(self):
        base = self.commit(self.files('1.0.0'))
        self.commit({**self.files('1.0', 'x: 1\n'), 'foo/x.py': 'x = 1\n'})
        before = self.read('foo/plugin.yaml')
        code, out = self.fix(base)
        self.assertEqual(1, code)
        self.assertIn('ERROR foo:', out)
        self.assertEqual(before, self.read('foo/plugin.yaml'))

    def test_fix_is_only_available_for_plugins_from_an_explicit_base(self):
        with self.assertRaises(SystemExit):
            self.tool.main(['core', '--repo', str(self.repo), '--base', 'HEAD', '--fix'])
        with self.assertRaises(SystemExit):
            self.tool.main(['plugins', '--repo', str(self.repo), '--from-pre-push', '--fix'])


class TestCommandLine(GitRepoTestCase):
    def run_main(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.tool.main([str(a) for a in argv])
        return code, out.getvalue()

    def plugin_files(self, version, extra=''):
        return {
            'foo/plugin.yaml': f"plugin:\n    version: '{version}'\n{extra}",
            'foo/__init__.py': f"PLUGIN_VERSION = '{version}'\n",
        }

    def test_skip_targets_are_read_from_commit_trailers(self):
        base = self.commit({'a': '1\n'})
        self.commit({'a': '2\n'}, 'one\n\nNo-Version-Bump: foo, bar')
        self.commit({'a': '3\n'}, 'two\n\nno-version-bump: core')
        self.commit({'a': '4\n'}, 'three, mentions no-version-bump: nothing in prose')
        self.assertEqual({'foo', 'bar', 'core'}, self.tool.skip_targets(self.repo, base, 'HEAD'))

    def test_plugins_command_reports_findings_and_fails_on_errors(self):
        base = self.commit(self.plugin_files('1.0.0'))
        self.commit({**self.plugin_files('1.0.0'), 'foo/x.py': 'x = 1\n'})
        code, out = self.run_main('plugins', '--repo', self.repo, '--base', base, '--core-version', 'v2.0.0-dev.1')
        self.assertEqual(1, code)
        self.assertIn('ERROR foo: version 1.0.0 not bumped although files changed', out)

    def test_clean_run_succeeds(self):
        base = self.commit(self.plugin_files('1.0.0'))
        self.commit({**self.plugin_files('1.0.1'), 'foo/x.py': 'x = 1\n'})
        code, out = self.run_main('plugins', '--repo', self.repo, '--base', base, '--core-version', 'v2.0.0-dev.1')
        self.assertEqual((0, ''), (code, out))

    def test_warn_only_turns_errors_into_exit_code_zero(self):
        base = self.commit(self.plugin_files('1.0.0'))
        self.commit({**self.plugin_files('1.0.0'), 'foo/x.py': 'x = 1\n'})
        code, out = self.run_main(
            'plugins', '--repo', self.repo, '--base', base, '--core-version', 'v2.0.0-dev.1', '--warn-only'
        )
        self.assertEqual(0, code)
        self.assertIn('ERROR foo', out)

    def test_trailer_skips_the_plugin_check(self):
        base = self.commit(self.plugin_files('1.0.0'))
        self.commit({**self.plugin_files('1.0.0'), 'foo/x.py': 'x = 1\n'}, 'change\n\nno-version-bump: foo')
        code, out = self.run_main('plugins', '--repo', self.repo, '--base', base, '--core-version', 'v2.0.0-dev.1')
        self.assertEqual(0, code)
        self.assertIn('WARNING foo', out)

    def test_core_version_is_read_from_the_core_checkout(self):
        base = self.commit(self.plugin_files('1.0.0', "    sh_minversion: '2.0.0'\n"))
        core_dir = self.repo / 'core'
        (core_dir / 'bin').mkdir(parents=True)
        (core_dir / 'bin' / 'shngversion.py').write_text("shNG_version = '2.0.0-dev.1'\n")
        self.commit({**self.plugin_files('1.0.1', "    sh_minversion: '2.0.0'\n")})
        code, out = self.run_main('plugins', '--repo', self.repo, '--base', base, '--core-dir', core_dir)
        self.assertEqual(1, code)
        self.assertIn('sh_minversion 2.0.0 is above the core version 2.0.0-dev.1', out)

    def test_from_pre_push_checks_every_pushed_range_read_from_stdin(self):
        base = self.commit(self.plugin_files('1.0.0'))
        head = self.commit({**self.plugin_files('1.0.0'), 'foo/x.py': 'x = 1\n'})
        stdin = io.StringIO(f'refs/heads/work {head} refs/heads/work {base}\n')
        with unittest.mock.patch('sys.stdin', stdin):
            code, out = self.run_main(
                'plugins', '--repo', self.repo, '--from-pre-push', '--core-version', 'v2.0.0-dev.1'
            )
        self.assertEqual(1, code)
        self.assertIn('ERROR foo: version 1.0.0 not bumped', out)

    def test_from_pre_push_with_nothing_to_check_succeeds(self):
        with unittest.mock.patch('sys.stdin', io.StringIO('')):
            code, out = self.run_main(
                'plugins', '--repo', self.repo, '--from-pre-push', '--core-version', 'v2.0.0-dev.1'
            )
        self.assertEqual((0, ''), (code, out))

    def test_core_command(self):
        surface = self.repo / 'surface.yaml'
        surface.write_text("python_globs: ['lib/*.py']\n")
        base = self.commit(
            {'bin/shngversion.py': "shNG_version = '1.0.0'\n", 'lib/plug.py': 'class Plug:\n    def run(self): ...\n'}
        )
        self.git('tag', 'v1.0.0')
        self.commit({'bin/shngversion.py': "shNG_version = '1.1.0-dev.1'\n", 'lib/plug.py': 'class Plug: ...\n'})
        code, out = self.run_main('core', '--repo', self.repo, '--base', base, '--surface', surface)
        self.assertEqual(1, code)
        self.assertIn('ERROR core: changes since v1.0.0 demand a major bump', out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
