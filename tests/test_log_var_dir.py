#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/log.py's handling of a custom var directory (``smarthome.py --var_dir``).

Coverage
--------
rebase_handler_filenames(): file handler names that are relative 'var/...' paths follow the
configured var dir; other handlers and paths are left alone; the default var dir changes nothing.

debug_logging_config(): the default debug logfile lives in the configured var dir.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib import vardir
from lib.log import debug_logging_config, rebase_handler_filenames


def _config():
    return {
        'handlers': {
            'warnings': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': './var/log/smarthome-warnings.log',
            },
            'details': {'class': 'lib.log.ShTimedRotatingFileHandler', 'filename': 'var/log/smarthome-details.log'},
            'elsewhere': {'class': 'logging.FileHandler', 'filename': '/var/log/syslog'},
            'plugin_local': {'class': 'logging.FileHandler', 'filename': 'plugins/foo/var/x.log'},
            'console': {'class': 'logging.StreamHandler', 'stream': 'ext://sys.stdout'},
        }
    }


class TestRebaseHandlerFilenames(unittest.TestCase):
    def setUp(self):
        vardir.set_var_dir(None)
        self.addCleanup(vardir.set_var_dir, None)

    def test_default_var_dir_leaves_config_unchanged(self):
        config = _config()
        rebase_handler_filenames(config)
        self.assertEqual(config, _config())

    def test_var_relative_filenames_follow_var_dir(self):
        vardir.set_var_dir('/srv/other/var')
        config = _config()
        rebase_handler_filenames(config)
        self.assertEqual(config['handlers']['warnings']['filename'], '/srv/other/var/log/smarthome-warnings.log')
        self.assertEqual(config['handlers']['details']['filename'], '/srv/other/var/log/smarthome-details.log')

    def test_other_paths_and_handlers_untouched(self):
        vardir.set_var_dir('/srv/other/var')
        config = _config()
        rebase_handler_filenames(config)
        self.assertEqual(config['handlers']['elsewhere'], _config()['handlers']['elsewhere'])
        self.assertEqual(config['handlers']['plugin_local'], _config()['handlers']['plugin_local'])
        self.assertEqual(config['handlers']['console'], _config()['handlers']['console'])

    def test_config_without_handlers_is_tolerated(self):
        vardir.set_var_dir('/srv/other/var')
        config = {}
        rebase_handler_filenames(config)
        self.assertEqual(config, {})


class TestDebugLogfileDefault(unittest.TestCase):
    def setUp(self):
        vardir.set_var_dir(None)
        self.addCleanup(vardir.set_var_dir, None)

    def test_default_logfile_in_default_var_dir(self):
        config = debug_logging_config()
        self.assertEqual(
            os.path.abspath(config['handlers']['shng_debug_file']['filename']),
            os.path.join(vardir.BASE_DIR, 'var', 'log', 'smarthome-debug.log'),
        )

    def test_default_logfile_follows_var_dir(self):
        vardir.set_var_dir('/srv/other/var')
        config = debug_logging_config()
        self.assertEqual(config['handlers']['shng_debug_file']['filename'], '/srv/other/var/log/smarthome-debug.log')


if __name__ == '__main__':
    unittest.main(verbosity=2)
