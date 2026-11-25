"""
Tests for lib/syspower.py - host power actions (poweroff/reboot) behind the admin UI's
"Power off" / "Reboot" buttons.
"""

import sys
import unittest
from unittest.mock import patch

import lib.syspower as syspower


def _python(code):
    return [sys.executable, '-c', code]


class TestIsSupported(unittest.TestCase):
    def test_linux_macos_windows_are_supported(self):
        for name in ('linux', 'darwin', 'windows'):
            self.assertTrue(syspower.is_supported(name), name)

    def test_other_platforms_are_not_supported(self):
        self.assertFalse(syspower.is_supported('freebsd'))

    def test_defaults_to_the_running_platform(self):
        with patch('lib.syspower.platform.system', return_value='Linux'):
            self.assertTrue(syspower.is_supported())
        with patch('lib.syspower.platform.system', return_value='Plan9'):
            self.assertFalse(syspower.is_supported())


class TestRunPowerAction(unittest.TestCase):
    def _run(self, argv, action='poweroff', **kwargs):
        with patch.dict(syspower.POWER_COMMANDS, {'testos': {action: argv}}):
            return syspower.run_power_action(action, platform_name='testos', **kwargs)

    def test_successful_command_reports_ok(self):
        self.assertEqual(self._run(_python('pass')), (True, ''))

    def test_failing_command_reports_its_stderr(self):
        ok, text = self._run(
            _python("import sys; sys.stderr.write('Interactive authentication required'); sys.exit(1)")
        )
        self.assertFalse(ok)
        self.assertIn('Interactive authentication required', text)

    def test_failing_command_without_stderr_reports_exit_code(self):
        ok, text = self._run(_python('import sys; sys.exit(3)'))
        self.assertFalse(ok)
        self.assertIn('3', text)

    def test_missing_binary_is_reported(self):
        ok, text = self._run(['/nonexistent/poweroff-binary'])
        self.assertFalse(ok)
        self.assertIn('/nonexistent/poweroff-binary', text)

    def test_hanging_command_times_out(self):
        ok, text = self._run(_python('import time; time.sleep(30)'), timeout=0.2)
        self.assertFalse(ok)
        self.assertIn('timed out', text)

    def test_unsupported_platform_is_reported(self):
        ok, text = syspower.run_power_action('poweroff', platform_name='plan9')
        self.assertFalse(ok)
        self.assertIn('plan9', text)

    def test_unknown_action_is_rejected(self):
        with self.assertRaises(ValueError):
            syspower.run_power_action('explode', platform_name='linux')
