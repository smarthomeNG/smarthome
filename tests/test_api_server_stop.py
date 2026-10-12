"""
Tests for modules/admin/api_server.py's ServerController.stop() - the backend for
shngadmin's "Stop Core" button (PUT /api/server/stop/).
"""

import json
import threading
import unittest
from unittest.mock import patch

from . import common

common.register_shng_log_levels()

from modules.admin.api_server import ServerController


class _FakeSh:
    """Records stop() calls; stands in for the SmartHome instance."""

    def __init__(self, status_code):
        self.shng_status = {'code': status_code, 'text': ''}
        self.stopped_with = None
        self.stopped = threading.Event()

    def get_basedir(self):
        return common.BASE

    def get_config_dir(self, name):
        return common.BASE + '/' + name

    def stop(self, signum=None, frame=None, exitcode=5):
        self.stopped_with = exitcode
        self.stopped.set()


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh


def _controller(status_code):
    sh = _FakeSh(status_code)
    controller = ServerController(_FakeModule(sh))
    controller.STOP_DELAY = 0
    return sh, controller


class TestStop(unittest.TestCase):
    def test_running_core_is_stopped_with_exit_code_0(self):
        sh, controller = _controller(20)
        response = json.loads(controller.stop())
        self.assertEqual(response, {'result': 'ok'})
        self.assertTrue(sh.stopped.wait(5))
        self.assertEqual(sh.stopped_with, 0)

    def test_core_not_running_is_not_stopped(self):
        sh, controller = _controller(30)
        response = json.loads(controller.stop())
        self.assertEqual(response['result'], 'error')
        self.assertFalse(sh.stopped.wait(0.2))

    def test_put_stop_dispatches_to_stop(self):
        sh, controller = _controller(20)
        response = json.loads(controller.update('stop'))
        self.assertEqual(response, {'result': 'ok'})
        self.assertTrue(sh.stopped.wait(5))


class TestSystemPower(unittest.TestCase):
    PATCH_TARGET = 'modules.admin.api_server'

    def _controller(self, allowed):
        sh, controller = _controller(20)
        sh._allow_system_power = allowed
        return controller

    def _update(self, controller, action, run_result=(True, ''), supported=True):
        with patch(f'{self.PATCH_TARGET}.run_power_action', return_value=run_result) as run:
            with patch(f'{self.PATCH_TARGET}.is_supported', return_value=supported):
                response = json.loads(controller.update(action))
        return response, run

    def test_poweroff_runs_the_command_when_allowed(self):
        response, run = self._update(self._controller(True), 'poweroff')
        self.assertEqual(response, {'result': 'ok'})
        run.assert_called_once_with('poweroff')

    def test_reboot_runs_the_command_when_allowed(self):
        response, run = self._update(self._controller(True), 'reboot')
        self.assertEqual(response, {'result': 'ok'})
        run.assert_called_once_with('reboot')

    def test_nothing_runs_when_not_allowed(self):
        response, run = self._update(self._controller(False), 'poweroff')
        self.assertEqual(response['result'], 'error')
        run.assert_not_called()

    def test_nothing_runs_on_unsupported_platform(self):
        response, run = self._update(self._controller(True), 'reboot', supported=False)
        self.assertEqual(response['result'], 'error')
        run.assert_not_called()

    def test_command_failure_text_is_returned(self):
        response, _ = self._update(
            self._controller(True), 'poweroff', run_result=(False, 'Interactive authentication required')
        )
        self.assertEqual(response, {'result': 'error', 'text': 'Interactive authentication required'})

    def test_available_only_when_allowed_and_supported(self):
        for allowed, supported, expected in ((True, True, True), (True, False, False), (False, True, False)):
            with patch(f'{self.PATCH_TARGET}.is_supported', return_value=supported):
                self.assertEqual(self._controller(allowed).system_power_available, expected)
