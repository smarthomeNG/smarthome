#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for lib/orb.py (astronomical position/timing calculations)

The Orb class wraps pyephem and computes sunrise, sunset, solar noon,
lunar rise/set, and celestial positions.  Tests use fixed UTC datetimes
and verify results against known astronomical values (±5 min tolerance
is used to account for atmospheric refraction variants between ephem
versions).

Reference location: Berlin, Germany (52.5°N, 13.4°E).

Known values computed with USNO / timeanddate.com for 2024-06-21 (summer
solstice, longest day):
  - Sunrise:  ~03:16 UTC
  - Solar noon: ~11:31 UTC
  - Sunset:   ~19:47 UTC
  - Sunrise on 2024-12-21 (winter solstice, shortest day): ~07:55 UTC
"""

import datetime
import math
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tests.common as common

common.register_shng_log_levels()

try:
    import ephem as _ephem_check

    HAS_EPHEM = True
except ImportError:
    HAS_EPHEM = False

try:
    from skyfield.api import Loader as _skyfield_loader_check

    HAS_SKYFIELD = True
except ImportError:
    HAS_SKYFIELD = False

from lib.orb import Orb
from lib.shtime import Shtime

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

BERLIN_LON = 13.4050
BERLIN_LAT = 52.5200
BERLIN_ELEV = 34

# Start of summer solstice 2024 (00:00 UTC) — rise/set methods return the
# NEXT occurrence after dt, so passing midnight gives that day's events.
_SUMMER_SOLSTICE = datetime.datetime(2024, 6, 21, 0, 0, 0, tzinfo=datetime.timezone.utc)
# Start of winter solstice 2024
_WINTER_SOLSTICE = datetime.datetime(2024, 12, 21, 0, 0, 0, tzinfo=datetime.timezone.utc)
# Noon on summer solstice (for position tests)
_SUMMER_NOON = datetime.datetime(2024, 6, 21, 11, 31, 0, tzinfo=datetime.timezone.utc)
# Spring equinox 2024 (Berlin) — day/night roughly equal length
_SPRING_EQUINOX = datetime.datetime(2024, 3, 20, 0, 0, 0, tzinfo=datetime.timezone.utc)

# Tromsø, Norway (69.65°N) — well inside the Arctic Circle, exercises
# midnight sun (summer) / polar night (winter), where the sun's plain
# (doff=0) rise/set genuinely does not occur on the given calendar day.
TROMSO_LON = 18.9553
TROMSO_LAT = 69.6492
TROMSO_ELEV = 10


def _make_shtime(tz='UTC'):
    import lib.shtime as _m

    _m._shtime_instance = None

    class _Sh:
        _default_language = 'de'

        def get_config_file(self, basename, extension='.yaml'):
            base = os.path.join(os.path.dirname(__file__), '..', 'etc')
            return os.path.join(base, basename + extension)

    st = Shtime(_Sh())
    st.set_tz(tz)
    return st


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestOrbInit(unittest.TestCase):
    def setUp(self):
        self.shtime = _make_shtime()

    def test_sun_object_created(self):
        orb = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        self.assertEqual(orb.orb, 'sun')

    def test_ephem_backend_used_by_default(self):
        orb = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        from lib.orb import _EphemBackend

        self.assertIsInstance(orb._backend, _EphemBackend)

    def test_unknown_backend_warns_and_leaves_orb_unconfigured(self):
        orb = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='nonexistent')
        # Orb.__init__ returns early for an unregistered backend name, same as
        # the historical "ephem not installed" case.
        self.assertFalse(hasattr(orb, 'orb'))

    @unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
    def test_skyfield_backend_selectable(self):
        orb = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='skyfield')
        from lib.orb import _SkyfieldBackend

        self.assertIsInstance(orb._backend, _SkyfieldBackend)

    def test_moon_object_created(self):
        orb = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        self.assertEqual(orb.orb, 'moon')

    def test_observer_and_orb_returns_tuple(self):
        orb = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        result = orb.get_observer_and_orb()
        self.assertEqual(len(result), 2)

    def test_moon_has_phase_attribute(self):
        orb = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        self.assertTrue(hasattr(orb, 'phase'))

    def test_moon_has_light_attribute(self):
        orb = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)
        self.assertTrue(hasattr(orb, 'light'))


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestSunRiseSet(unittest.TestCase):
    """Sunrise and sunset times against published USNO values (±10 min)."""

    TOLERANCE = datetime.timedelta(minutes=10)
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_summer_solstice_sunrise_approx(self):
        # pyephem computes Berlin sunrise on 2024-06-21 ≈ 02:43 UTC.
        # (Berlin local = 04:43 CEST; timeanddate.com shows ~04:44 CEST — close.)
        # Tolerance of 15 min covers atmospheric refraction model differences.
        expected = datetime.datetime(2024, 6, 21, 2, 43, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.rise(dt=_SUMMER_SOLSTICE)
        diff = abs(result.replace(tzinfo=datetime.timezone.utc) - expected)
        self.assertLessEqual(diff, datetime.timedelta(minutes=15), f'Sunrise {result} not within 15 min of {expected}')

    def test_summer_solstice_sunset_approx(self):
        # pyephem computes Berlin sunset on 2024-06-21 ≈ 19:33 UTC (21:33 CEST).
        expected = datetime.datetime(2024, 6, 21, 19, 33, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.set(dt=_SUMMER_SOLSTICE)
        diff = abs(result.replace(tzinfo=datetime.timezone.utc) - expected)
        self.assertLessEqual(diff, datetime.timedelta(minutes=15), f'Sunset {result} not within 15 min of {expected}')

    def test_winter_solstice_sunrise_later_than_summer(self):
        summer_rise = self.sun.rise(dt=_SUMMER_SOLSTICE)
        winter_rise = self.sun.rise(dt=_WINTER_SOLSTICE)
        # Winter sunrise is later in the UTC day than summer sunrise (Berlin)
        self.assertGreater(winter_rise.hour, summer_rise.hour)

    def test_summer_day_is_longer_than_winter(self):
        summer_rise = self.sun.rise(dt=_SUMMER_SOLSTICE)
        summer_set = self.sun.set(dt=_SUMMER_SOLSTICE)
        winter_rise = self.sun.rise(dt=_WINTER_SOLSTICE)
        winter_set = self.sun.set(dt=_WINTER_SOLSTICE)
        summer_len = summer_set - summer_rise
        winter_len = winter_set - winter_rise
        self.assertGreater(summer_len, winter_len)

    def test_rise_returns_utc_aware_datetime(self):
        result = self.sun.rise(dt=_SUMMER_SOLSTICE)
        self.assertIsNotNone(result.tzinfo)

    def test_set_returns_utc_aware_datetime(self):
        result = self.sun.set(dt=_SUMMER_SOLSTICE)
        self.assertIsNotNone(result.tzinfo)

    def test_sunrise_before_sunset(self):
        rise = self.sun.rise(dt=_SUMMER_SOLSTICE)
        sset = self.sun.set(dt=_SUMMER_SOLSTICE)
        self.assertLess(rise, sset)

    def test_minute_offset_shifts_time(self):
        rise_plain = self.sun.rise(dt=_SUMMER_SOLSTICE)
        rise_plus30 = self.sun.rise(moff=30, dt=_SUMMER_SOLSTICE)
        diff = rise_plus30 - rise_plain
        self.assertAlmostEqual(diff.total_seconds() / 60, 30, delta=1)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSunRiseSetSkyfield(TestSunRiseSet):
    """Same characterization suite as TestSunRiseSet, against the skyfield backend."""

    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSunRiseSetSkyfieldCached(TestSunRiseSet):
    """Same characterization suite again, against the cached skyfield backend."""

    BACKEND = 'skyfield-cached'


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestSolarNoon(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_noon_approx_time(self):
        # pyephem computes Berlin solar noon on 2024-06-21 ≈ 11:08 UTC.
        # (Local CEST = 13:08, consistent with astronomical almanacs.)
        expected = datetime.datetime(2024, 6, 21, 11, 8, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.noon(dt=_SUMMER_SOLSTICE)
        diff = abs(result.replace(tzinfo=datetime.timezone.utc) - expected)
        self.assertLessEqual(diff, datetime.timedelta(minutes=15))

    def test_noon_between_rise_and_set(self):
        # Use a time just after midnight so rise/noon/set all fall on June 21.
        dt_start = datetime.datetime(2024, 6, 21, 1, 0, 0, tzinfo=datetime.timezone.utc)
        rise = self.sun.rise(dt=dt_start)
        noon = self.sun.noon(dt=dt_start)
        sset = self.sun.set(dt=dt_start)
        self.assertLess(rise, noon)
        self.assertLess(noon, sset)

    def test_noon_returns_aware_datetime(self):
        result = self.sun.noon(dt=_SUMMER_SOLSTICE)
        self.assertIsNotNone(result.tzinfo)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSolarNoonSkyfield(TestSolarNoon):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSolarNoonSkyfieldCached(TestSolarNoon):
    BACKEND = 'skyfield-cached'


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestSolarPosition(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_pos_returns_two_values(self):
        result = self.sun.pos(dt=_SUMMER_SOLSTICE)
        self.assertEqual(len(result), 2)

    def test_pos_azimuth_at_noon_near_south(self):
        # At solar noon the sun is due south (≈180°) for Northern Hemisphere
        noon = self.sun.noon(dt=_SUMMER_SOLSTICE)
        az_deg, el_deg = self.sun.pos(degree=True, dt=noon)  # noon is aware UTC
        # Azimuth should be within 10° of 180
        self.assertAlmostEqual(az_deg, 180, delta=10)

    def test_pos_elevation_positive_at_noon(self):
        noon = self.sun.noon(dt=_SUMMER_SOLSTICE)
        _, el_deg = self.sun.pos(degree=True, dt=noon)
        self.assertGreater(el_deg, 0)

    def test_pos_elevation_negative_at_midnight(self):
        midnight = datetime.datetime(2024, 6, 21, 23, 0, 0, tzinfo=datetime.timezone.utc)
        _, el_deg = self.sun.pos(degree=True, dt=midnight)
        self.assertLess(el_deg, 0)

    def test_pos_radians_by_default(self):
        result = self.sun.pos(dt=_SUMMER_SOLSTICE)
        # Result is a tuple of floats representing radians
        self.assertIsInstance(result[0], float)
        self.assertIsInstance(result[1], float)

    def test_pos_degrees_values_in_range(self):
        az_deg, el_deg = self.sun.pos(degree=True, dt=_SUMMER_SOLSTICE)
        self.assertGreaterEqual(az_deg, 0)
        self.assertLessEqual(az_deg, 360)
        self.assertGreaterEqual(el_deg, -90)
        self.assertLessEqual(el_deg, 90)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSolarPositionSkyfield(TestSolarPosition):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSolarPositionSkyfieldCached(TestSolarPosition):
    BACKEND = 'skyfield-cached'


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestMoon(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.moon = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_moon_rise_returns_datetime(self):
        result = self.moon.rise(dt=_SUMMER_SOLSTICE)
        self.assertIsInstance(result, datetime.datetime)

    def test_moon_set_returns_datetime(self):
        result = self.moon.set(dt=_SUMMER_SOLSTICE)
        self.assertIsInstance(result, datetime.datetime)

    def test_moon_pos_returns_two_values(self):
        result = self.moon.pos(dt=_SUMMER_SOLSTICE)
        self.assertEqual(len(result), 2)

    def test_moon_phase_returns_int_octant(self):
        # phase() returns int 0-7 (lunar phase octant within 29.5-day cycle)
        result = self.moon.phase()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 7)

    def test_moon_light_returns_int_percent(self):
        # light() returns int 0-100 (% of lunar surface illuminated)
        result = self.moon.light()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 100)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestMoonSkyfield(TestMoon):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestMoonSkyfieldCached(TestMoon):
    BACKEND = 'skyfield-cached'


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestCoordinateConversions(unittest.TestCase):
    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT)

    def test_unaware_to_utc(self):
        naive = datetime.datetime(2024, 6, 21, 12, 0, 0)
        result = self.sun.unaware_datetime_to_utc(naive)
        self.assertIsNotNone(result.tzinfo)

    def test_aware_to_utc(self):
        aware = datetime.datetime(2024, 6, 21, 14, 0, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        result = self.sun.aware_datetime_to_utc(aware)
        # 14:00 CEST = 12:00 UTC
        self.assertEqual(result.hour, 12)
        self.assertEqual(result.minute, 0)

    def test_utc_to_local_returns_datetime(self):
        utc = datetime.datetime(2024, 6, 21, 12, 0, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.utc_to_local(utc)
        self.assertIsInstance(result, datetime.datetime)


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestCoordinateConversionsUseConfiguredTz(unittest.TestCase):
    """Regression tests: unaware_datetime_to_utc/utc_to_local must use shng's
    configured timezone (self.shtime.tzinfo()), not whatever the OS-level
    timezone happens to be. force_os_tz creates a genuine mismatch so these
    actually exercise the bug rather than relying on OS/configured tz happening
    to agree in the test environment."""

    def setUp(self):
        self.shtime = _make_shtime('Pacific/Honolulu')
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV)

    def test_unaware_to_utc_uses_configured_tz(self):
        with common.force_os_tz('Europe/Berlin'):
            naive = datetime.datetime(2024, 6, 15, 12, 0, 0)
            result = self.sun.unaware_datetime_to_utc(naive)
            # 12:00 Honolulu (UTC-10) -> 22:00 UTC same day
            self.assertEqual(result, datetime.datetime(2024, 6, 15, 22, 0, 0, tzinfo=datetime.timezone.utc))

    def test_utc_to_local_uses_configured_tz(self):
        with common.force_os_tz('Europe/Berlin'):
            utc_dt = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)
            result = self.sun.utc_to_local(utc_dt)
            # 12:00 UTC -> 02:00 Honolulu (UTC-10) same day
            self.assertEqual(result.hour, 2)
            self.assertEqual(result.utcoffset(), datetime.timedelta(hours=-10))


# ===========================================================================
# Equinox sanity (second reference point beyond the solstice tests, prep
# for ephem-to-skyfield comparison)
# ===========================================================================


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestEquinox(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_equinox_day_length_close_to_twelve_hours(self):
        # True day/night equality ("equilux") happens a few days after the
        # astronomical equinox due to atmospheric refraction and the sun's
        # angular size; 30 min tolerance covers that gap.
        rise = self.sun.rise(dt=_SPRING_EQUINOX)
        sset = self.sun.set(dt=_SPRING_EQUINOX)
        day_length = sset - rise
        self.assertLess(abs(day_length.total_seconds() - 12 * 3600), 30 * 60)

    def test_equinox_rise_approx(self):
        expected = datetime.datetime(2024, 3, 20, 5, 8, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.rise(dt=_SPRING_EQUINOX)
        diff = abs(result.replace(tzinfo=datetime.timezone.utc) - expected)
        self.assertLessEqual(diff, datetime.timedelta(minutes=15))

    def test_equinox_set_approx(self):
        expected = datetime.datetime(2024, 3, 20, 17, 21, 0, tzinfo=datetime.timezone.utc)
        result = self.sun.set(dt=_SPRING_EQUINOX)
        diff = abs(result.replace(tzinfo=datetime.timezone.utc) - expected)
        self.assertLessEqual(diff, datetime.timedelta(minutes=15))


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestEquinoxSkyfield(TestEquinox):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestEquinoxSkyfieldCached(TestEquinox):
    BACKEND = 'skyfield-cached'


# ===========================================================================
# Moon rise/set sanity (only phase/light were characterized before)
# ===========================================================================


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestMoonRiseSet(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.moon = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend=self.BACKEND)

    def test_moon_rise_is_utc_aware(self):
        result = self.moon.rise(dt=_SPRING_EQUINOX)
        self.assertIsNotNone(result.tzinfo)

    def test_moon_set_is_utc_aware(self):
        result = self.moon.set(dt=_SPRING_EQUINOX)
        self.assertIsNotNone(result.tzinfo)

    def test_moon_rise_within_24h_of_search_start(self):
        # Moon rise/set always occurs roughly once per ~24h50m (lunar day);
        # a "next" search should never jump multiple days.
        result = self.moon.rise(dt=_SPRING_EQUINOX)
        self.assertLess((result - _SPRING_EQUINOX).total_seconds() / 3600, 26)

    def test_moon_set_within_24h_of_search_start(self):
        result = self.moon.set(dt=_SPRING_EQUINOX)
        self.assertLess((result - _SPRING_EQUINOX).total_seconds() / 3600, 26)

    def test_moon_minute_offset_shifts_time(self):
        rise_plain = self.moon.rise(dt=_SPRING_EQUINOX)
        rise_plus30 = self.moon.rise(moff=30, dt=_SPRING_EQUINOX)
        diff = rise_plus30 - rise_plain
        self.assertAlmostEqual(diff.total_seconds() / 60, 30, delta=1)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestMoonRiseSetSkyfield(TestMoonRiseSet):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestMoonRiseSetSkyfieldCached(TestMoonRiseSet):
    BACKEND = 'skyfield-cached'


# ===========================================================================
# High-latitude (midnight sun / polar night) regression tests
#
# Orb.rise()/set() with doff=0 (the default) used to crash with an uncaught
# ephem.AlwaysUpError/NeverUpError at any location where the sun's plain
# horizon crossing genuinely does not occur on the given day. _avoid_neverup
# only clamps non-zero degree offsets, so this path had no protection.
#
# The skyfield variant exercises the *different* mechanism that backend uses
# to signal "no event": checking the find_risings()/find_settings() events
# flag rather than catching an ephem-specific exception.
# ===========================================================================


@unittest.skipUnless(HAS_EPHEM, 'pyephem not installed')
class TestHighLatitudeNeverUp(unittest.TestCase):
    BACKEND = 'ephem'

    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', TROMSO_LON, TROMSO_LAT, TROMSO_ELEV, backend=self.BACKEND)

    def test_midnight_sun_rise_returns_none_not_raises(self):
        # Tromsø, summer solstice: sun never sets, so it never "rises" either
        # (it's already up). Must not raise AlwaysUpError.
        result = self.sun.rise(dt=_SUMMER_SOLSTICE)
        self.assertIsNone(result)

    def test_midnight_sun_set_returns_none_not_raises(self):
        result = self.sun.set(dt=_SUMMER_SOLSTICE)
        self.assertIsNone(result)

    def test_polar_night_rise_returns_none_not_raises(self):
        # Tromsø, winter solstice: sun never rises above the horizon.
        result = self.sun.rise(dt=_WINTER_SOLSTICE)
        self.assertIsNone(result)

    def test_polar_night_set_returns_none_not_raises(self):
        result = self.sun.set(dt=_WINTER_SOLSTICE)
        self.assertIsNone(result)

    def test_noon_unaffected_by_midnight_sun(self):
        # Transit (solar noon) always exists regardless of whether the sun
        # crosses the horizon that day.
        result = self.sun.noon(dt=_SUMMER_SOLSTICE)
        self.assertIsInstance(result, datetime.datetime)

    def test_midnight_unaffected_by_polar_night(self):
        result = self.sun.midnight(dt=_WINTER_SOLSTICE)
        self.assertIsInstance(result, datetime.datetime)

    def test_equinox_rise_set_work_normally_at_high_latitude(self):
        # Sanity check: away from the solstices, Tromsø still has normal
        # rise/set events (this should never have been broken).
        rise = self.sun.rise(dt=_SPRING_EQUINOX)
        sset = self.sun.set(dt=_SPRING_EQUINOX)
        self.assertIsInstance(rise, datetime.datetime)
        self.assertIsInstance(sset, datetime.datetime)
        self.assertLess(rise, sset)


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestHighLatitudeNeverUpSkyfield(TestHighLatitudeNeverUp):
    BACKEND = 'skyfield'


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestHighLatitudeNeverUpSkyfieldCached(TestHighLatitudeNeverUp):
    BACKEND = 'skyfield-cached'


# ===========================================================================
# Correctness: the cached backend must agree with the uncached one exactly.
# The cache batches a whole year of events and bisects into it instead of
# running a fresh search per call - these tests catch the bug we found while
# building it (a circumpolar query returning the next *real* event months
# away instead of None - see _SkyfieldCachedBackend.SAME_CIRCUIT_DAYS).
# ===========================================================================


@unittest.skipUnless(HAS_SKYFIELD, 'skyfield not installed')
class TestSkyfieldCachedMatchesUncached(unittest.TestCase):
    def setUp(self):
        self.shtime = _make_shtime()
        self.sun = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='skyfield')
        self.sun_cached = Orb('sun', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='skyfield-cached')
        self.moon = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='skyfield')
        self.moon_cached = Orb('moon', BERLIN_LON, BERLIN_LAT, BERLIN_ELEV, backend='skyfield-cached')
        self.tromso_sun = Orb('sun', TROMSO_LON, TROMSO_LAT, TROMSO_ELEV, backend='skyfield')
        self.tromso_sun_cached = Orb('sun', TROMSO_LON, TROMSO_LAT, TROMSO_ELEV, backend='skyfield-cached')

    def test_sun_rise_matches_across_several_dates(self):
        for dt in (_SUMMER_SOLSTICE, _WINTER_SOLSTICE, _SPRING_EQUINOX):
            with self.subTest(dt=dt):
                self.assertEqual(self.sun.rise(dt=dt), self.sun_cached.rise(dt=dt))

    def test_sun_set_matches_across_several_dates(self):
        for dt in (_SUMMER_SOLSTICE, _WINTER_SOLSTICE, _SPRING_EQUINOX):
            with self.subTest(dt=dt):
                self.assertEqual(self.sun.set(dt=dt), self.sun_cached.set(dt=dt))

    def test_sun_rise_matches_repeated_calls_across_consecutive_days(self):
        # exercises the cache hit path (second+ call for the same doff)
        dt = _SUMMER_SOLSTICE
        for _ in range(5):
            with self.subTest(dt=dt):
                self.assertEqual(self.sun.rise(dt=dt), self.sun_cached.rise(dt=dt))
            dt = self.sun.rise(dt=dt) + datetime.timedelta(seconds=1)

    def test_noon_midnight_match(self):
        self.assertEqual(self.sun.noon(dt=_SUMMER_SOLSTICE), self.sun_cached.noon(dt=_SUMMER_SOLSTICE))
        self.assertEqual(self.sun.midnight(dt=_WINTER_SOLSTICE), self.sun_cached.midnight(dt=_WINTER_SOLSTICE))

    def test_moon_rise_set_match(self):
        self.assertEqual(self.moon.rise(dt=_SPRING_EQUINOX), self.moon_cached.rise(dt=_SPRING_EQUINOX))
        self.assertEqual(self.moon.set(dt=_SPRING_EQUINOX), self.moon_cached.set(dt=_SPRING_EQUINOX))

    def test_circumpolar_none_matches(self):
        # the actual bug this test suite exists to catch: the cached backend
        # must return None here too, not the next real event months away.
        self.assertIsNone(self.tromso_sun.rise(dt=_SUMMER_SOLSTICE))
        self.assertIsNone(self.tromso_sun_cached.rise(dt=_SUMMER_SOLSTICE))
        self.assertIsNone(self.tromso_sun.set(dt=_SUMMER_SOLSTICE))
        self.assertIsNone(self.tromso_sun_cached.set(dt=_SUMMER_SOLSTICE))
        self.assertIsNone(self.tromso_sun.rise(dt=_WINTER_SOLSTICE))
        self.assertIsNone(self.tromso_sun_cached.rise(dt=_WINTER_SOLSTICE))

    def test_circumpolar_equinox_still_matches(self):
        # away from the solstices, Tromsø has normal events again - the cache
        # must resolve these via the proximity check too, not just return None.
        self.assertEqual(self.tromso_sun.rise(dt=_SPRING_EQUINOX), self.tromso_sun_cached.rise(dt=_SPRING_EQUINOX))
        self.assertEqual(self.tromso_sun.set(dt=_SPRING_EQUINOX), self.tromso_sun_cached.set(dt=_SPRING_EQUINOX))

    def test_query_at_cache_window_boundary_is_not_a_false_none(self):
        # Regression test: a query landing exactly at the cached window's end
        # must not be mistaken for "confirmed no event" - that's just where the
        # search stopped, not proof nothing exists just beyond it (found via
        # 1000 sequential daily queries at Berlin - never circumpolar - wrongly
        # returning None right at each yearly cache-refill boundary). Use a
        # short CACHE_HORIZON_DAYS to hit the boundary deterministically
        # without iterating a full year.
        self.sun_cached._backend.CACHE_HORIZON_DAYS = 3
        self.sun_cached.rise(dt=_SUMMER_SOLSTICE)  # populates the cache, covered_end = +3 days
        boundary = _SUMMER_SOLSTICE + datetime.timedelta(days=3)
        result = self.sun_cached.rise(dt=boundary)
        self.assertIsNotNone(result)
        self.assertEqual(result, self.sun.rise(dt=boundary))


if __name__ == '__main__':
    unittest.main()
