import contextlib
import logging
import os
import sys
import time
import pathlib

# with Linux standard installation of SmartHomeNG
# realpath of __file__ will be '/usr/local/smarthome/tests/common.py'
# so BASE becomes '/usr/local/smarthome'
if os.name != 'nt':
    BASE = '/'.join(os.path.realpath(__file__).split('/')[:-2])
else:
    BASE = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, BASE)


def register_shng_log_levels():
    """Register SmartHomeNG custom log levels if not already present.

    SmartHomeNG defines several levels beyond the standard Python set.
    This helper is idempotent — safe to call multiple times or from
    multiple test modules.
    """
    _levels = [(31, 'NOTICE'), (13, 'DBGHIGH'), (12, 'DBGMED'), (11, 'DBGLOW'), (9, 'DEVELOP')]
    for level, name in _levels:
        if not hasattr(logging.getLoggerClass(), name.lower()):

            def _make_method(lvl):
                def _method(self, msg, *args, **kwargs):
                    if self.isEnabledFor(lvl):
                        self._log(lvl, msg, args, **kwargs)

                return _method

            logging.addLevelName(level, name)
            setattr(logging, name, level)
            setattr(logging.getLoggerClass(), name.lower(), _make_method(level))


@contextlib.contextmanager
def force_os_tz(tz_name):
    """Force the process's OS-level timezone to tz_name for the duration of the block.

    Shtime.set_tz() writes os.environ['TZ'], which on some platforms makes naive
    .astimezone()/.now() calls silently track the *configured* shng timezone too -
    masking bugs where code should use shng's configured tz but instead falls back
    to "whatever the OS thinks". This forces a genuine OS/configured mismatch via
    time.tzset() (POSIX only) so such bugs are actually exercised by tests.
    """
    orig_tz = os.environ.get('TZ')
    os.environ['TZ'] = tz_name
    time.tzset()
    try:
        yield
    finally:
        if orig_tz is None:
            os.environ.pop('TZ', None)
        else:
            os.environ['TZ'] = orig_tz
        time.tzset()
