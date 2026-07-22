#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Regression test for lib/env/__init__.py's distance and speed unit
conversions.

miles_to_meter/nauticalmiles_to_meter/meter_to_miles/meter_to_nauticalmiles
referenced undefined names 'miles'/'meter' instead of their own 'distance'
parameter - guaranteed NameError on every call.

kn_to_kmh/kmh_to_kn used _nautical_mile (1852, meters) instead of the
km/h-per-knot factor (1.852) - off by exactly 1000x since their
introduction in 2023.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import lib.env as env


class TestDistanceConversions(unittest.TestCase):
    def test_miles_to_meter(self):
        self.assertAlmostEqual(1609.344, env.miles_to_meter(1))

    def test_nauticalmiles_to_meter(self):
        self.assertAlmostEqual(1852, env.nauticalmiles_to_meter(1))

    def test_meter_to_miles(self):
        self.assertAlmostEqual(1, env.meter_to_miles(1609.344))

    def test_meter_to_nauticalmiles(self):
        self.assertAlmostEqual(1, env.meter_to_nauticalmiles(1852))


class TestKnotConversions(unittest.TestCase):
    def test_kn_to_kmh(self):
        self.assertAlmostEqual(18.52, env.kn_to_kmh(10))

    def test_kmh_to_kn(self):
        self.assertAlmostEqual(10, env.kmh_to_kn(18.52))

    def test_kn_to_kmh_roundtrips_with_kmh_to_kn(self):
        self.assertAlmostEqual(7.5, env.kmh_to_kn(env.kn_to_kmh(7.5)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
