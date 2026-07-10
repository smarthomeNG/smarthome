#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/shtime.py

Coverage:
  - to_seconds()               — string→int conversion for duration strings
  - seconds_to_displaystring() — int→human-readable display string
  - datetime_transform()       — multi-type datetime normalisation
  - date_transform()           — multi-type date normalisation
  - length_of_year()           — leap-year detection
  - length_of_month()          — days in a month
  - day_of_year()              — ordinal day of year
  - weekday()                  — ISO weekday (1=Mon … 7=Sun)
  - calendar_week()            — ISO week number
  - beginning_of_week()        — Monday date of a given ISO week
  - beginning_of_month()       — first day of a month
  - beginning_of_year()        — first day of a year
  - is_weekend()               — weekend detection
  - time_diff()                — |timedelta| in requested unit (always positive)
  - time_since() / time_until() — convenience wrappers
"""

import datetime
import logging
import sys
import os
import unittest

# Make shng root importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common


# ---------------------------------------------------------------------------
# Register shng's custom log levels before importing shtime.
# lib/translation.py calls logger.dbghigh() which only exists after these
# levels have been added to the Logger class.
# ---------------------------------------------------------------------------
def _register_shng_log_levels():
    for level_num, level_name in [(31, 'NOTICE'), (13, 'DBGHIGH'), (12, 'DBGMED'), (11, 'DBGLOW'), (9, 'DEVELOP')]:
        if not hasattr(logging.getLoggerClass(), level_name.lower()):

            def _make_log_method(lvl):
                def _method(self, message, *args, **kwargs):
                    if self.isEnabledFor(lvl):
                        self._log(lvl, message, args, **kwargs)

                return _method

            logging.addLevelName(level_num, level_name)
            setattr(logging, level_name, level_num)
            setattr(logging.getLoggerClass(), level_name.lower(), _make_log_method(level_num))


_register_shng_log_levels()


from lib.shtime import Shtime


# ---------------------------------------------------------------------------
# Helper: create a fresh Shtime instance, reset the singleton first.
# ---------------------------------------------------------------------------
def _make_shtime(tz='UTC'):
    import lib.shtime as _st_module

    _st_module._shtime_instance = None
    st = Shtime(_MockSh())
    st.set_tz(tz)
    return st


class _MockSh:
    _default_language = 'de'

    def get_config_file(self, basename, extension='.yaml'):
        """Return full path to a holidays config that exists in CI.
        Prefers tests/resources/etc/<basename>.yaml (committed to the repo)
        over etc/<basename>.yaml (instance-specific, absent in CI)."""
        tests_etc = os.path.join(os.path.dirname(__file__), 'resources', 'etc')
        candidate = os.path.join(tests_etc, basename + extension)
        if os.path.isfile(candidate):
            return candidate
        # Fall back to the real etc/ directory (works locally)
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        return os.path.join(base_dir, 'etc', basename + extension)


# ===========================================================================
# to_seconds
# ===========================================================================


class TestToSeconds(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    # --- plain integer / float ---
    def test_int_passthrough(self):
        self.assertEqual(self.st.to_seconds(45), 45)

    def test_float_truncated(self):
        self.assertEqual(self.st.to_seconds(3.9), 3)

    # --- plain string (no suffix = seconds) ---
    def test_string_plain_seconds(self):
        self.assertEqual(self.st.to_seconds('45'), 45)

    def test_string_with_s_suffix(self):
        self.assertEqual(self.st.to_seconds('45s'), 45)

    # --- minutes ---
    def test_string_minutes(self):
        self.assertEqual(self.st.to_seconds('5m'), 300)

    def test_string_minutes_and_seconds(self):
        self.assertEqual(self.st.to_seconds('5m30s'), 330)

    # --- hours ---
    def test_string_hours(self):
        self.assertEqual(self.st.to_seconds('2h'), 7200)

    def test_string_hours_and_minutes(self):
        self.assertEqual(self.st.to_seconds('2h5m'), 7500)

    # --- combined ---
    def test_string_all_units(self):
        self.assertEqual(self.st.to_seconds('2h5m45s'), 7545)

    # --- edge cases ---
    def test_zero(self):
        self.assertEqual(self.st.to_seconds(0), 0)

    def test_empty_string_returns_zero(self):
        # An empty string parses to 0 seconds — no units found, nothing added.
        # This is the documented behaviour: '' is treated as "0 seconds".
        self.assertEqual(self.st.to_seconds(''), 0)

    def test_invalid_string_returns_minus_one(self):
        # A string that can't be parsed at all returns -1.
        self.assertEqual(self.st.to_seconds('notatime', test=True), -1)

    def test_none_returns_minus_one(self):
        self.assertEqual(self.st.to_seconds(None, test=True), -1)


# ===========================================================================
# seconds_to_displaystring
# ===========================================================================


class TestSecondsToDisplayString(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_zero_seconds(self):
        # nothing to display — returns empty string
        self.assertEqual(self.st.seconds_to_displaystring(0), '')

    def test_single_second(self):
        result = self.st.seconds_to_displaystring(1)
        self.assertIn('1', result)

    def test_multiple_seconds(self):
        result = self.st.seconds_to_displaystring(45)
        self.assertIn('45', result)

    def test_one_minute(self):
        result = self.st.seconds_to_displaystring(60)
        self.assertIn('1', result)

    def test_one_hour(self):
        result = self.st.seconds_to_displaystring(3600)
        self.assertIn('1', result)

    def test_one_day(self):
        result = self.st.seconds_to_displaystring(86400)
        self.assertIn('1', result)

    def test_two_days(self):
        result = self.st.seconds_to_displaystring(2 * 86400)
        self.assertIn('2', result)

    def test_combined_contains_all_components(self):
        # 1d 2h 3m 4s
        sec = 86400 + 7200 + 180 + 4
        result = self.st.seconds_to_displaystring(sec)
        # All four values must appear somewhere in the output
        self.assertIn('1', result)
        self.assertIn('2', result)
        self.assertIn('3', result)
        self.assertIn('4', result)

    def test_seconds_only_no_higher_units(self):
        # 30 seconds produces a non-empty result containing '30'
        result = self.st.seconds_to_displaystring(30)
        self.assertNotEqual(result, '')
        self.assertIn('30', result)


# ===========================================================================
# datetime_transform / date_transform
# ===========================================================================


class TestDatetimeTransform(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime('Europe/Berlin')

    def test_datetime_passthrough(self):
        dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
        result = self.st.datetime_transform(dt)
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 6)

    def test_date_to_datetime(self):
        d = datetime.date(2024, 3, 21)
        result = self.st.datetime_transform(d)
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.day, 21)

    def test_string_iso(self):
        result = self.st.datetime_transform('2024-03-21')
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 3)

    def test_string_german_format(self):
        result = self.st.datetime_transform('21.03.2024')
        self.assertEqual(result.day, 21)
        self.assertEqual(result.month, 3)

    def test_timestamp_int(self):
        ts = int(datetime.datetime(2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc).timestamp())
        result = self.st.datetime_transform(ts)
        self.assertIsInstance(result, datetime.datetime)

    def test_invalid_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.st.datetime_transform('not-a-date-at-all-xyz-999')

    def test_invalid_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            self.st.datetime_transform([2024, 1, 1])

    def test_naive_datetime_is_labeled_not_shifted(self):
        # Regression test: a naive datetime must be interpreted as wall-clock
        # time *in the configured timezone*, not as OS-local time that gets
        # converted. force_os_tz creates a genuine OS/configured mismatch.
        st = _make_shtime('Pacific/Honolulu')
        with common.force_os_tz('Europe/Berlin'):
            dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
            result = st.datetime_transform(dt)
            self.assertEqual(result.hour, 12)
            self.assertEqual(result.utcoffset(), datetime.timedelta(hours=-10))


class TestDateTransform(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_returns_date_type(self):
        result = self.st.date_transform('2024-06-01')
        self.assertIsInstance(result, datetime.date)
        self.assertEqual(result.year, 2024)

    def test_date_passthrough(self):
        d = datetime.date(2024, 6, 1)
        result = self.st.date_transform(d)
        self.assertEqual(result, d)


# ===========================================================================
# length_of_year
# ===========================================================================


class TestLengthOfYear(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_non_leap(self):
        self.assertEqual(self.st.length_of_year(2023), 365)

    def test_leap(self):
        self.assertEqual(self.st.length_of_year(2024), 366)

    def test_century_non_leap(self):
        self.assertEqual(self.st.length_of_year(1900), 365)

    def test_400_year_leap(self):
        self.assertEqual(self.st.length_of_year(2000), 366)

    def test_offset_positive(self):
        # 2023 + 1 = 2024 (leap)
        self.assertEqual(self.st.length_of_year(2023, offset=1), 366)

    def test_offset_negative(self):
        # 2024 - 1 = 2023 (non-leap)
        self.assertEqual(self.st.length_of_year(2024, offset=-1), 365)


# ===========================================================================
# length_of_month
# ===========================================================================


class TestLengthOfMonth(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_january(self):
        self.assertEqual(self.st.length_of_month(1, 2024), 31)

    def test_february_leap(self):
        self.assertEqual(self.st.length_of_month(2, 2024), 29)

    def test_february_non_leap(self):
        self.assertEqual(self.st.length_of_month(2, 2023), 28)

    def test_april(self):
        self.assertEqual(self.st.length_of_month(4, 2024), 30)

    def test_december(self):
        self.assertEqual(self.st.length_of_month(12, 2024), 31)

    def test_offset_back_wraps_year(self):
        # January 2024 with offset=-1 → December 2023 (31 days)
        self.assertEqual(self.st.length_of_month(1, 2024, offset=-1), 31)


# ===========================================================================
# day_of_year
# ===========================================================================


class TestDayOfYear(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_jan_1(self):
        self.assertEqual(self.st.day_of_year('2024-01-01'), 1)

    def test_jan_31(self):
        self.assertEqual(self.st.day_of_year('2024-01-31'), 31)

    def test_dec_31_non_leap(self):
        self.assertEqual(self.st.day_of_year('2023-12-31'), 365)

    def test_dec_31_leap(self):
        self.assertEqual(self.st.day_of_year('2024-12-31'), 366)

    def test_march_1_leap(self):
        # Leap year 2024: March 1 is day 61
        self.assertEqual(self.st.day_of_year('2024-03-01'), 61)

    def test_offset_positive(self):
        self.assertEqual(self.st.day_of_year('2024-01-01', offset=1), 2)

    def test_offset_negative(self):
        self.assertEqual(self.st.day_of_year('2024-01-02', offset=-1), 1)


# ===========================================================================
# weekday
# ===========================================================================


class TestWeekday(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_monday(self):
        self.assertEqual(self.st.weekday('2024-01-01'), 1)

    def test_tuesday(self):
        self.assertEqual(self.st.weekday('2024-01-02'), 2)

    def test_saturday(self):
        self.assertEqual(self.st.weekday('2024-01-06'), 6)

    def test_sunday(self):
        self.assertEqual(self.st.weekday('2024-01-07'), 7)

    def test_offset(self):
        # Monday + 1 = Tuesday
        self.assertEqual(self.st.weekday('2024-01-01', offset=1), 2)


# ===========================================================================
# calendar_week
# ===========================================================================


class TestCalendarWeek(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_first_week_2024(self):
        self.assertEqual(self.st.calendar_week('2024-01-01'), 1)

    def test_week_52_2023(self):
        self.assertEqual(self.st.calendar_week('2023-12-31'), 52)

    def test_known_week_24_of_2024(self):
        # 2024-06-10 is in ISO week 24
        self.assertEqual(self.st.calendar_week('2024-06-10'), 24)

    def test_offset_advances_by_one_week(self):
        w = self.st.calendar_week('2024-06-10')
        w_plus1 = self.st.calendar_week('2024-06-10', offset=1)
        self.assertEqual(w_plus1, w + 1)


# ===========================================================================
# beginning_of_week / beginning_of_month / beginning_of_year
# ===========================================================================


class TestBeginningOf(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_beginning_of_week_1_2024(self):
        # ISO week 1 of 2024 starts on Mon 2024-01-01
        result = self.st.beginning_of_week(week=1, year=2024)
        self.assertEqual(result, datetime.date(2024, 1, 1))

    def test_beginning_of_week_with_positive_offset(self):
        # week 1 + 1 = week 2 → starts 2024-01-08
        result = self.st.beginning_of_week(week=1, year=2024, offset=1)
        self.assertEqual(result, datetime.date(2024, 1, 8))

    def test_beginning_of_month(self):
        result = self.st.beginning_of_month(month=6, year=2024)
        self.assertEqual(result, datetime.date(2024, 6, 1))

    def test_beginning_of_month_with_negative_offset(self):
        # March 2024 - 1 month = February 2024
        result = self.st.beginning_of_month(month=3, year=2024, offset=-1)
        self.assertEqual(result, datetime.date(2024, 2, 1))

    def test_beginning_of_year(self):
        result = self.st.beginning_of_year(year=2024)
        self.assertEqual(result, datetime.date(2024, 1, 1))

    def test_beginning_of_year_with_positive_offset(self):
        result = self.st.beginning_of_year(year=2024, offset=1)
        self.assertEqual(result, datetime.date(2025, 1, 1))


# ===========================================================================
# today / tomorrow / yesterday
#
# NOTE: real OS-tz/configured-tz mismatch can't be exercised deterministically
# here because the bug only manifests near midnight relative to the offset
# difference, and "now" is real wall-clock time at test run. These verify the
# contract instead: today() must derive from the configured tz via now().
# ===========================================================================


class TestTodayTomorrowYesterday(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime('Pacific/Honolulu')

    def test_today_matches_now_date_in_configured_tz(self):
        self.assertEqual(self.st.today(), self.st.now().date())

    def test_tomorrow_is_today_plus_one(self):
        self.assertEqual(self.st.tomorrow(), self.st.today() + datetime.timedelta(days=1))

    def test_yesterday_is_today_minus_one(self):
        self.assertEqual(self.st.yesterday(), self.st.today() - datetime.timedelta(days=1))

    def test_today_offset(self):
        self.assertEqual(self.st.today(offset=2), self.st.today() + datetime.timedelta(days=2))


# ===========================================================================
# tzname / tznameST / tznameDST
#
# Regression tests: these must report the *configured* timezone's name, not
# whatever the OS-level timezone happens to be (dateutil's tz.tzlocal() reads
# OS state dynamically, so force_os_tz can genuinely discriminate here).
# ===========================================================================


class TestTzNames(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime('Pacific/Honolulu')

    def test_tzname_reports_configured_tz(self):
        with common.force_os_tz('Europe/Berlin'):
            self.assertEqual(self.st.tzname(), 'HST')

    def test_tznameST_reports_configured_tz(self):
        with common.force_os_tz('Europe/Berlin'):
            self.assertEqual(self.st.tznameST(), 'HST')

    def test_tznameDST_reports_configured_tz(self):
        with common.force_os_tz('Europe/Berlin'):
            self.assertEqual(self.st.tznameDST(), 'HST')

    def test_tzname_distinguishes_st_and_dst_for_dst_observing_zone(self):
        # Pacific/Honolulu has no DST (always HST); Europe/Berlin does
        # (CET in winter, CEST in summer) - use it to confirm ST != DST name.
        st = _make_shtime('Europe/Berlin')
        self.assertEqual(st.tznameST(), 'CET')
        self.assertEqual(st.tznameDST(), 'CEST')


# ===========================================================================
# ts()
#
# Regression test: ts() must not overwrite tzinfo on an already-aware
# datetime (no OS-tz involvement needed - this is purely an
# overwrite-vs-preserve bug).
# ===========================================================================


class TestTs(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime('Europe/Berlin')

    def test_aware_datetime_timestamp_unaffected_by_configured_tz(self):
        # 12:00 UTC must yield the same posix timestamp regardless of shng's
        # configured timezone - ts() must not relabel it to Europe/Berlin.
        utc_dt = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)
        expected = utc_dt.timestamp()
        self.assertEqual(self.st.ts(utc_dt), expected)

    def test_naive_datetime_uses_configured_tz(self):
        naive_dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
        result = self.st.ts(naive_dt)
        expected = naive_dt.replace(tzinfo=self.st.tzinfo()).timestamp()
        self.assertEqual(result, expected)

    def test_explicit_tz_override_still_works(self):
        naive_dt = datetime.datetime(2024, 6, 15, 12, 0, 0)
        honolulu = _make_shtime('Pacific/Honolulu').tzinfo()
        result = self.st.ts(naive_dt, tz=honolulu)
        expected = naive_dt.replace(tzinfo=honolulu).timestamp()
        self.assertEqual(result, expected)


# ===========================================================================
# is_weekend
# ===========================================================================


class TestIsWeekend(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()

    def test_saturday_is_weekend(self):
        self.assertTrue(self.st.is_weekend('2024-01-06'))

    def test_sunday_is_weekend(self):
        self.assertTrue(self.st.is_weekend('2024-01-07'))

    def test_monday_is_not_weekend(self):
        self.assertFalse(self.st.is_weekend('2024-01-08'))

    def test_friday_is_not_weekend(self):
        self.assertFalse(self.st.is_weekend('2024-01-05'))


# ===========================================================================
# time_diff / time_since / time_until
#
# NOTE: time_diff always returns an *absolute* (non-negative) value.
# If dt1 > dt2 the delta is flipped before conversion.
# ===========================================================================


class TestTimeDiff(unittest.TestCase):
    def setUp(self):
        self.st = _make_shtime()
        self.tz = self.st.tzinfo()

    def _dt(self, y, m, d, h=0, mi=0, s=0):
        return datetime.datetime(y, m, d, h, mi, s, tzinfo=self.tz)

    def test_diff_seconds_forward(self):
        dt1 = self._dt(2024, 1, 1, 0, 0, 0)
        dt2 = self._dt(2024, 1, 1, 0, 0, 30)
        self.assertEqual(self.st.time_diff(dt1, dt2, 's'), 30)

    def test_diff_seconds_backward_is_positive(self):
        # time_diff always returns the absolute gap (never negative)
        dt1 = self._dt(2024, 1, 1, 0, 0, 30)
        dt2 = self._dt(2024, 1, 1, 0, 0, 0)
        self.assertEqual(self.st.time_diff(dt1, dt2, 's'), 30)

    def test_diff_minutes(self):
        dt1 = self._dt(2024, 1, 1, 0, 0, 0)
        dt2 = self._dt(2024, 1, 1, 0, 5, 0)
        self.assertAlmostEqual(self.st.time_diff(dt1, dt2, 'm'), 5, places=4)

    def test_diff_hours(self):
        dt1 = self._dt(2024, 1, 1, 0, 0, 0)
        dt2 = self._dt(2024, 1, 1, 3, 0, 0)
        self.assertAlmostEqual(self.st.time_diff(dt1, dt2, 'h'), 3, places=4)

    def test_diff_days(self):
        dt1 = self._dt(2024, 1, 1)
        dt2 = self._dt(2024, 1, 4)
        self.assertAlmostEqual(self.st.time_diff(dt1, dt2, 'd'), 3, places=4)

    def test_diff_integer_days(self):
        dt1 = self._dt(2024, 1, 1)
        dt2 = self._dt(2024, 1, 4)
        self.assertEqual(self.st.time_diff(dt1, dt2, 'id'), 3)

    def test_diff_invalid_resulttype_returns_minus_one(self):
        # 'w' (weeks) is not a supported resulttype; the method logs an error
        # and returns -1.
        dt1 = self._dt(2024, 1, 1)
        dt2 = self._dt(2024, 1, 8)
        self.assertEqual(self.st.time_diff(dt1, dt2, 'w'), -1)

    def test_diff_invalid_input_raises(self):
        dt = self._dt(2024, 1, 1)
        # When datetime_transform can't parse dt2, it raises ValueError.
        # time_diff does not catch this — the caller is responsible for valid input.
        with self.assertRaises(ValueError):
            self.st.time_diff(dt, 'totally-unparseable-xyz-999', 's')

    def test_time_since_past_is_positive(self):
        past = datetime.datetime.now(self.tz) - datetime.timedelta(seconds=10)
        result = self.st.time_since(past, 's')
        self.assertGreater(result, 0)

    def test_time_until_future_is_positive(self):
        future = datetime.datetime.now(self.tz) + datetime.timedelta(seconds=10)
        result = self.st.time_until(future, 's')
        self.assertGreater(result, 0)


if __name__ == '__main__':
    unittest.main()
