"""
Tests for modules/admin/api_config.py's ConfigController.apply_live_params() - options of
etc/smarthome.yaml flagged `live: True` in modules/core/module.yaml take effect on the
running core when saved from the admin UI; all other options need a restart.
"""

import unittest

from . import common

common.register_shng_log_levels()

from modules.admin.api_config import ConfigController


class _FakeSh:
    def get_basedir(self):
        return common.BASE

    def get_config_dir(self, name):
        return common.BASE + '/' + name


class _FakeModule:
    def __init__(self, sh):
        self._sh = sh


class TestApplyLiveParams(unittest.TestCase):
    def setUp(self):
        self.sh = _FakeSh()
        self.controller = ConfigController(_FakeModule(self.sh))

    def test_live_bool_is_applied(self):
        self.controller.apply_live_params({'allow_system_power': True})
        self.assertIs(self.sh._allow_system_power, True)

    def test_live_bool_given_as_text_is_converted(self):
        self.controller.apply_live_params({'allow_system_power': 'yes'})
        self.assertIs(self.sh._allow_system_power, True)

    def test_live_str_and_num_are_applied(self):
        self.controller.apply_live_params({'pip_command': 'python3 -m pip', 'db_query_timeout': 30})
        self.assertEqual(self.sh._pip_command, 'python3 -m pip')
        self.assertEqual(self.sh._db_query_timeout, 30)

    def test_options_not_flagged_live_are_ignored(self):
        self.controller.apply_live_params({'use_conditional_triggers': 'true', 'tz': 'Europe/Berlin'})
        self.assertFalse(hasattr(self.sh, '_use_conditional_triggers'))
        self.assertFalse(hasattr(self.sh, '_tz'))

    def test_removed_live_option_reverts_to_its_default(self):
        self.sh._allow_system_power = True
        self.controller.apply_live_params({})
        self.assertIs(self.sh._allow_system_power, False)

    def test_removed_live_option_without_default_becomes_unset(self):
        self.sh._pip_command = 'python3 -m pip'
        self.controller.apply_live_params({})
        self.assertFalse(hasattr(self.sh, '_pip_command'))
