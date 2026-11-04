"""Availability follows the app's freshness boundary, not fan settings."""

import unittest
from datetime import UTC, datetime, timedelta

from protocol_loader import models, sample_air_quality


class AirQualityAvailabilityTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 4, 7, tzinfo=UTC)
        self.zone = models.Zone(system_id="s", system_name="Home", zone_id="z", name="Test", status={})
        self.zone.air_quality = sample_air_quality()
        self.current = self.zone.air_quality["current"]
        self.current["lastUpdatedAt"] = self.now.isoformat()

    def test_cutoff_and_recovery_for_all_sensors(self):
        for age, expected in ((0, True), (3600, True), (3601, False), (10800, False), (10, True)):
            self.current["lastUpdatedAt"] = (self.now - timedelta(seconds=age)).isoformat()
            for kind in ("overall", "co2", "pm25", "tvoc"):
                with self.subTest(age=age, kind=kind):
                    self.assertEqual(self.zone.air_quality_available(kind, now=self.now), expected)

    def test_missing_invalid_ambiguous_or_future_timestamp(self):
        for stamp in (
            None,
            "bad",
            "2026-11-04T07:00:00",
            (self.now + timedelta(minutes=5)).isoformat(),
        ):
            self.current["lastUpdatedAt"] = stamp
            self.assertFalse(self.zone.air_quality_available("co2", now=self.now))

    def test_offset_and_idle_fan_preserve_recent_reading(self):
        self.current["lastUpdatedAt"] = "2026-11-04T00:00:00-07:00"
        self.zone.status = {"features": {"circulation": {"status": "Off", "fanSpeedStatus": 0}}}
        self.assertTrue(self.zone.air_quality_available("co2", now=self.now))

    def test_settling_missing_value_and_limited_access(self):
        self.current["co2"]["settling"] = True
        self.assertFalse(self.zone.air_quality_available("co2", now=self.now))
        self.assertTrue(self.zone.air_quality_available("pm25", now=self.now))
        self.current["pm25"]["value"] = None
        self.assertFalse(self.zone.air_quality_available("pm25", now=self.now))
        self.zone.air_quality["access"] = "limited"
        self.assertFalse(self.zone.air_quality_available("tvoc", now=self.now))
        self.assertTrue(self.zone.air_quality_available("overall", now=self.now))
