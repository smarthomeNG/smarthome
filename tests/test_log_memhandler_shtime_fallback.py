#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib/log.py's ShngMemLogHandler.emit().

emit() used to call self._shtime.tzinfo() unconditionally; if self._shtime
was None (only reachable if the handler is used before Shtime is set up -
doesn't happen on a real startup, where Shtime is created before logging is
configured, but does happen in a minimal test harness), this raised
AttributeError, which got caught by the handler's own except-block and
silently dropped the log record instead of storing it. Now falls back to
UTC instead.
"""

import datetime
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

from lib.log import ShngMemLogHandler


class TestShngMemLogHandlerEmitShtimeFallback(unittest.TestCase):
    def _make_handler(self, shtime):
        handler = ShngMemLogHandler.__new__(ShngMemLogHandler)
        handler.formatter = None
        handler._shtime = shtime
        handler._log = MagicMock()
        handler._cache = False
        return handler

    def _make_record(self):
        return logging.LogRecord(
            name='test', level=logging.INFO, pathname=__file__, lineno=1, msg='hello', args=None, exc_info=None
        )

    def test_emit_falls_back_to_utc_when_shtime_is_none(self):
        handler = self._make_handler(shtime=None)

        handler.emit(self._make_record())

        handler._log.add.assert_called_once()
        (logged,), _ = handler._log.add.call_args
        timestamp = logged[0]
        self.assertEqual(timestamp.tzinfo, datetime.timezone.utc)

    def test_emit_uses_shtime_tzinfo_when_available(self):
        fake_tz = datetime.timezone(datetime.timedelta(hours=2))
        fake_shtime = MagicMock()
        fake_shtime.tzinfo.return_value = fake_tz
        handler = self._make_handler(shtime=fake_shtime)

        handler.emit(self._make_record())

        handler._log.add.assert_called_once()
        (logged,), _ = handler._log.add.call_args
        timestamp = logged[0]
        self.assertEqual(timestamp.tzinfo, fake_tz)


if __name__ == '__main__':
    unittest.main(verbosity=2)
