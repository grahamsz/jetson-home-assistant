"""Energy parsing, freshness, and local-day resets using synthetic data."""

import unittest
from datetime import UTC, datetime, timedelta

from protocol_loader import energy, sample_energy


class EnergyTests(unittest.TestCase):
    def setUp(self):
        self.data = sample_energy()
        self.view = energy.EnergyView(self.data)

    def test_main_and_keyed_loads_are_separate(self):
        self.assertEqual(self.view.value(None), 1000)
        self.assertEqual(self.view.value("hp1"), 125.5)
        self.assertEqual(self.view.value(None, energy=True), 3.5)
        self.assertEqual(self.view.value("hp1", energy=True), 2.5)
        self.assertEqual(set(self.view.loads), {"hp1"})
        self.assertIsNone(self.view.value("missing"))

    def test_heat_strip_component_and_residual_are_not_added_or_duplicated(self):
        self.data["today"]["residualEnergyKwh"] = -20
        self.assertEqual(self.view.value("hp1"), 125.5)
        self.assertEqual(self.view.value(None, energy=True), 3.5)
        self.assertNotIn("heatStripsPowerW", self.view.loads)
        self.assertIsNone(self.view.value("residualEnergyKwh", energy=True))
        self.assertEqual(self.view.heat_strip_power("hp1"), 5)
        self.assertEqual(self.view.heat_strip_loads, {"hp1"})

    def test_heat_strip_zero_null_and_missing_are_distinct(self):
        load = self.data["live"]["loads"]["hp1"]
        for value, expected in ((0, 0), (None, None), (True, None), ("5", None)):
            load["heatStripsPowerW"] = value
            self.assertEqual(self.view.heat_strip_power("hp1"), expected)
            self.assertIn("hp1", self.view.heat_strip_loads)
        del load["heatStripsPowerW"]
        self.assertNotIn("hp1", self.view.heat_strip_loads)
        self.assertIsNone(self.view.heat_strip_power("hp1"))
        self.assertIsNone(self.view.heat_strip_power("missing"))
        self.assertIsNone(self.view.heat_strip_power(None))

    def test_null_missing_and_zero_are_distinct(self):
        for raw, expected in ((None, None), (0, 0)):
            self.data["live"]["totalMainPowerW"] = raw
            self.data["today"]["totalMainEnergyKwh"] = raw
            self.assertEqual(self.view.value(None), expected)
            self.assertEqual(self.view.value(None, energy=True), expected)
        del self.data["live"]["totalMainPowerW"]
        self.assertIsNone(self.view.value(None))

    def test_invalid_numbers_and_negative_consumption_are_not_measurements(self):
        for raw in (True, "12", float("inf"), float("nan")):
            self.data["live"]["totalMainPowerW"] = raw
            self.assertIsNone(self.view.value(None))
        self.data["live"]["totalMainPowerW"] = -10
        self.assertEqual(self.view.value(None), -10)
        self.data["today"]["totalMainEnergyKwh"] = -1
        self.assertIsNone(self.view.value(None, energy=True))

    def test_stale_future_or_naive_timestamps_are_not_fresh(self):
        observed = self.view.updated_at()
        self.assertTrue(self.view.is_fresh(observed + timedelta(seconds=299), 300))
        self.assertFalse(self.view.is_fresh(observed + timedelta(seconds=301), 300))
        self.assertFalse(self.view.is_fresh(observed - timedelta(seconds=61), 300))
        for value in (None, "not-a-time", "2026-11-04T12:00:00"):
            self.data["live"]["asOf"] = value
            self.assertFalse(self.view.is_fresh(datetime.now(UTC), 300))

    def test_live_and_daily_freshness_are_independent(self):
        observed = self.view.updated_at()
        self.data["today"]["asOf"] = (observed - timedelta(hours=1)).isoformat()
        self.assertTrue(self.view.is_fresh(observed, 300))
        self.assertFalse(self.view.is_fresh(observed, 300, energy=True))

    def test_daily_correction_does_not_change_reset_but_midnight_does(self):
        self.data["timezone"] = "America/Denver"
        self.data["today"].update(date="2026-11-03", asOf="2026-11-03T23:59:53-07:00")
        first = self.view.reset_time
        self.data["today"]["totalMainEnergyKwh"] = 2.1
        self.assertEqual(self.view.reset_time, first)
        self.data["today"].update(
            date="2026-11-04", asOf="2026-11-04T00:00:53-07:00", totalMainEnergyKwh=0.008
        )
        self.assertNotEqual(self.view.reset_time, first)
        self.assertEqual(self.view.reset_time.isoformat(), "2026-11-04T00:00:00-07:00")

    def test_reset_uses_midnight_timezone_offset_not_current_offset(self):
        self.data["timezone"] = "America/Denver"
        self.data["today"].update(date="2026-11-01", asOf="2026-11-01T12:00:00-07:00")
        self.assertEqual(self.view.reset_time.isoformat(), "2026-11-01T00:00:00-06:00")

    def test_bad_timezone_date_or_mismatched_period_disables_daily_reset(self):
        for zone, date_value, as_of in (
            ("Invalid/Zone", "2026-11-04", "2026-11-04T12:00:00Z"),
            ("UTC", "not-a-date", "2026-11-04T12:00:00Z"),
            ("UTC", "2026-11-03", "2026-11-04T12:00:00Z"),
            ("UTC", "2026-11-04", None),
        ):
            self.data["timezone"] = zone
            self.data["today"].update(date=date_value, asOf=as_of)
            self.assertIsNone(self.view.reset_time)


if __name__ == "__main__":
    unittest.main()
