#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2021-     Martin Sinn                          m.sinn@gmx.de
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

from . import common
import os
import tempfile
import unittest
import logging

import bin.shngversion as shngversion
from lib.model.smartplugin import SmartPlugin
from lib.shpypi import Requirements_files

from tests.mock.core import MockSmartHome


logger = logging.getLogger(__name__)

# from lib.utils import Version
from lib.utils import Version


# ----------------------------------------------------------

# def test_version_to_list(vers):
#     versl = Version.to_list(vers)
#     versd = Version.to_string(versl)
#     print(f"{vers:12} -> {str(versl):14} -> {versd}")
#
#     return
#
#
# def test_version_compare(vers1, vers2, operator):
#     result = Version.compare(vers1, vers2, operator)
#     print(f"v1={str(vers1):15} v2={str(vers2):15}, op= {operator:2} -> {result}")


# ----------------------------------------------------------


class TestModule(unittest.TestCase):
    def test_version_numbers(self):

        logger.warning('')
        logger.warning('=== Begin test_version_numbers:')

        # test_version_to_list('1.2.1')
        # test_version_to_list('v1.2.1')
        # test_version_to_list('1.2.1a')

        self.assertEqual([1, 2, 1, 0], Version.to_list('1.2.1'))
        self.assertEqual([1, 2, 1, 0], Version.to_list('v1.2.1'))
        self.assertEqual([1, 2, 1, 1], Version.to_list('1.2.1a'))

        self.assertEqual('v1.2.1', Version.to_string([1, 2, 1, 0]))
        self.assertEqual('v1.2.1.1', Version.to_string([1, 2, 1, 1]))

        # test_version_to_list('1.2')
        # test_version_to_list('v1.2')
        # test_version_to_list('1.2a')

        self.assertEqual([0, 0, 0, 0], Version.to_list(''))
        self.assertEqual([1, 2, 0, 0], Version.to_list('1.2'))
        self.assertEqual([1, 2, 0, 0], Version.to_list('v1.2'))

        self.assertEqual('v1.2.0', Version.to_string([1, 2, 0, 0]))
        self.assertEqual('v1.2.1', Version.to_string([1, 2, 1, 0]))

        # test_version_to_list('1.2.3.4.5')
        # test_version_to_list('v1.2a.3.4.5')
        # test_version_to_list('1.2a.3a.4.5')

        self.assertEqual([1, 2, 3, 4], Version.to_list('1.2.3.4.5'))
        self.assertEqual([1, 2, 3, 5], Version.to_list('v1.2a.3.4.5'))
        self.assertEqual([1, 2, 3, 6], Version.to_list('1.2a.3a.4.5'))

        # test_version_to_list('')
        # test_version_to_list('1.9.0.1')

        self.assertEqual([1, 2, 0, 1], Version.to_list('1.2a'))
        self.assertEqual([1, 9, 0, 1], Version.to_list('1.9.0.1'))

        # An empty component (e.g. from '1.2..3' or a trailing separator
        # '1.2.3.') must be treated as 0, like any other non-numeric part -
        # not crash to_list() with IndexError on v[-1] (v == '', indexing
        # an empty string raises).
        self.assertEqual([1, 2, 0, 3], Version.to_list('1.2..3'))
        self.assertEqual([1, 2, 3, 0], Version.to_list('1.2.3.'))

        # test_version_compare('1.2', '1.3', '<')
        # test_version_compare('1.2', '1.3', '>')
        # test_version_compare('1.2', '1.3', '=')
        # test_version_compare('1.2', '1.3', '<=')
        # test_version_compare('1.2', '1.3', '>=')

        self.assertTrue(Version.compare('1.2', '1.3', '<'))
        self.assertFalse(Version.compare('1.2', '1.3', '>'))
        self.assertFalse(Version.compare('1.2', '1.3', '='))
        self.assertTrue(Version.compare('1.2', '1.3', '<='))
        self.assertFalse(Version.compare('1.2', '1.3', '>='))

        # test_version_compare('1.2.3a', [1,2,3,4,5], '<')
        # test_version_compare('1.2.3a', [1,2,3,104,5], '<')
        # test_version_compare('1.2', '1.2.3.4.5', '>')
        # test_version_compare('1.2', '1.2.3.4.5', '=')
        # test_version_compare('1.2', '1.2.3.4.5', '<=')
        # test_version_compare('1.2', '1.2.3.4.5', '>=')

        self.assertTrue(Version.compare('1.2.3a', [1, 2, 3, 4, 5], '<'))
        self.assertTrue(Version.compare('1.2.3a', [1, 2, 3, 104, 5], '<'))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '>'))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '='))
        self.assertTrue(Version.compare('1.2', '1.2.3.4.5', '<='))
        self.assertFalse(Version.compare('1.2', '1.2.3.4.5', '>='))

        logger.warning('=== End test_version_numbers:')


# ----------------------------------------------------------


class TestSemverPrecedence(unittest.TestCase):
    """
    Version.compare() orders version strings by semver.org rule 11, extended
    with an optional legacy 4th numeric 'sub-patch' level.
    """

    def test_prerelease_sorts_below_its_release(self):
        self.assertTrue(Version.compare('1.13.0-dev.1', '1.13.0', '<'))
        self.assertFalse(Version.compare('1.13.0-dev.1', '1.13.0', '>='))

    def test_semver_org_precedence_chain(self):
        chain = [
            '1.0.0-alpha',
            '1.0.0-alpha.1',
            '1.0.0-alpha.beta',
            '1.0.0-beta',
            '1.0.0-beta.2',
            '1.0.0-beta.11',
            '1.0.0-rc.1',
            '1.0.0',
        ]
        for lower, higher in zip(chain, chain[1:]):
            with self.subTest(lower=lower, higher=higher):
                self.assertTrue(Version.compare(lower, higher, '<'))
                self.assertTrue(Version.compare(higher, lower, '>'))

    def test_build_metadata_is_ignored(self):
        self.assertTrue(Version.compare('1.13.0-dev.1+abc1234.develop', '1.13.0-dev.1+ffff000.master', '=='))
        self.assertTrue(Version.compare('1.13.0+abc1234', '1.13.0', '>='))
        self.assertTrue(Version.compare('1.13.0-dev.1+zzz', '1.13.0-dev.2+aaa', '<'))

    def test_sub_patch_level_sorts_between_patch_releases(self):
        self.assertTrue(Version.compare('1.12.2', '1.12.2.2', '<'))
        self.assertTrue(Version.compare('1.12.2.2', '1.12.2.10', '<'))
        self.assertTrue(Version.compare('1.12.2.2', '1.12.3', '<'))
        self.assertTrue(Version.compare('1.12.2.2', '1.13.0-dev.1', '<'))

    def test_format_keeps_prerelease_and_build(self):
        self.assertEqual('v1.13.0-dev.1', Version.format('1.13.0-dev.1'))
        self.assertEqual('v1.13.0-dev.1+abc1234.develop', Version.format('v1.13-dev.1+abc1234.develop'))
        self.assertEqual('v1.13.0+abc1234', Version.format('1.13.0+abc1234'))
        self.assertEqual('v1.12.2.2', Version.format('1.12.2.2'))
        self.assertEqual('v1.6.0', Version.format('1.6'))
        self.assertEqual('', Version.format(''))

    def test_is_semver_accepts_only_strict_three_part_versions(self):
        for ok in ('0.0.1', '1.12.2', '2.0.0-dev.1', '1.0.0-rc.1+build.5', '1.0.0+sha-1', '10.20.30'):
            with self.subTest(version=ok):
                self.assertTrue(Version.is_semver(ok))
        for bad in (
            '',
            '1.2',
            '1.2.3.4',
            'v1.2.3',
            '01.2.3',
            '1.02.3',
            '1.2.3-',
            '1.2.3-01',
            '1.2.3+',
            '1.2.3-a..b',
            '1.2.3a',
            ' 1.2.3',
        ):
            with self.subTest(version=bad):
                self.assertFalse(Version.is_semver(bad))

    def test_strip_build_removes_only_the_build_part(self):
        self.assertEqual('v1.13.0-dev.1', Version.strip_build('v1.13.0-dev.1+abc1234.develop'))
        self.assertEqual('2.0.0', Version.strip_build('2.0.0+abc1234'))
        self.assertEqual('1.12.2.2', Version.strip_build('1.12.2.2'))
        self.assertEqual('', Version.strip_build(''))

    def test_short_and_v_prefixed_forms_equal_full_form(self):
        self.assertTrue(Version.compare('1.6', '1.6.0', '=='))
        self.assertTrue(Version.compare('v1.13.0-dev.1', '1.13.0-dev.1', '=='))
        self.assertTrue(Version.compare('1.13-dev.1', '1.13.0-dev.1', '=='))


# ----------------------------------------------------------


class TestVersionDisplay(unittest.TestCase):
    """The version strings shown at startup and in the admin UI are valid semver with build metadata."""

    def test_build_version_appends_sanitized_build_metadata(self):
        self.assertEqual(
            'v2.0.0-dev.1+abc1234.develop', shngversion.build_version('v2.0.0-dev.1', 'abc1234', 'develop')
        )
        self.assertEqual(
            'v2.0.0+abc1234.feature-semver-x', shngversion.build_version('v2.0.0', 'abc1234', 'feature/semver_x')
        )
        self.assertEqual('v2.0.0+manual', shngversion.build_version('v2.0.0', 'manual', ''))
        self.assertEqual('v2.0.0', shngversion.build_version('v2.0.0'))

    def test_build_version_result_is_a_comparable_version(self):
        shown = shngversion.build_version('v2.0.0-dev.1', 'abc1234', 'feature/x')
        self.assertEqual(shown, Version.format(shown))
        self.assertTrue(Version.compare(shown, 'v2.0.0-dev.1', '=='))
        self.assertTrue(Version.compare(shown, 'v2.0.0', '<'))

    def test_shng_version_equals_main_version_apart_from_build_metadata(self):
        shown = shngversion.get_shng_version()
        self.assertTrue(Version.compare(shown, shngversion.get_shng_main_version(), '=='))
        self.assertEqual(shngversion.get_shng_main_version(), Version.strip_build(shown))

    def test_plugins_version_carries_build_metadata_but_the_release_label_does_not(self):
        self.assertEqual(Version.strip_build(shngversion.get_plugins_version()), shngversion.get_shng_plugins_version())
        self.assertNotIn('+', shngversion.get_shng_plugins_version())


class TestShngVersionGate(unittest.TestCase):
    """Plugins are gated by sh_minversion/sh_maxversion against the running (development) version."""

    RUNNING = 'v2.0.0-dev.1+abc1234.develop'

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.requirements = Requirements_files(version=self.RUNNING, for_tests=True)

    def gate(self, **bounds):
        lines = ''.join(f"    {key}: '{value}'\n" for key, value in bounds.items())
        with open(os.path.join(self._tmp.name, 'plugin.yaml'), 'w') as f:
            f.write(f'plugin:\n    version: 1.0.0\n{lines}')
        return self.requirements._test_plugin_versions(os.path.join(self._tmp.name, 'requirements.txt'))

    def test_minversion_at_or_below_the_running_version_is_accepted(self):
        self.assertEqual((True, ''), self.gate(sh_minversion='1.12.2.2'))
        self.assertEqual((True, ''), self.gate(sh_minversion='2.0.0-dev.1'))

    def test_minversion_of_the_unreleased_final_version_is_refused(self):
        self.assertEqual((False, 'SmartHomeNG min version'), self.gate(sh_minversion='2.0.0'))
        self.assertEqual((False, 'SmartHomeNG min version'), self.gate(sh_minversion='2.0.0-dev.2'))

    def test_maxversion_below_the_running_version_is_refused(self):
        self.assertEqual((False, 'SmartHomeNG max version'), self.gate(sh_maxversion='1.12'))
        self.assertEqual((True, ''), self.gate(sh_maxversion='2.0.0'))


class TestGetGitDataDoesNotChangeCwd(unittest.TestCase):
    """
    _get_git_data() must run 'git' scoped to either the core repo or the
    plugins/ repo (a separate nested .git root) via 'git -C <path>', not
    os.chdir(BASE) - the process's cwd must never change no matter how many
    times or in what order core/plugins git data is fetched.
    """

    def test_single_core_call_leaves_cwd_unchanged(self):
        before = os.getcwd()
        shngversion._get_git_data()
        self.assertEqual(before, os.getcwd())

    def test_single_plugins_call_leaves_cwd_unchanged(self):
        before = os.getcwd()
        shngversion._get_git_data('plugins')
        self.assertEqual(before, os.getcwd())

    def test_plugins_call_does_not_leak_into_a_later_core_call(self):
        before = os.getcwd()
        shngversion._get_git_data('plugins')
        shngversion._get_git_data()
        self.assertEqual(before, os.getcwd())


if __name__ == '__main__':
    unittest.main(verbosity=2)
