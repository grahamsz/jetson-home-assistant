"""Observed status fields without inferring units or unsupported state enums."""

import unittest

from protocol_loader import (
    models,
    sample_equipment,
    sample_heatpump_status,
    sample_status,
    telemetry,
)


class TelemetryTests(unittest.TestCase):
    def test_observed_operation_fields_and_zero_fan_status(self):
        status = sample_heatpump_status()
        self.assertEqual(telemetry.operation_value(status, "mode"), "Off")
        self.assertEqual(telemetry.operation_value(status, "fanOperatingMode"), "constantAirflow")
        self.assertEqual(telemetry.operation_value(status, "fanSpeedStatus"), 0)
        self.assertEqual(telemetry.operation_value(status, "fanSpeedSetpoint"), 1)
        self.assertEqual(telemetry.operation_value(status, "fanLevelStatus"), 0)
        self.assertEqual(telemetry.operation_value(status, "fanLevelSetting"), 1)

    def test_health_only_response_does_not_create_fake_operation_values(self):
        status = {"health": {"connectionStatus": "Disconnected", "faults": []}}
        for field in telemetry.OPERATION_FIELDS:
            self.assertIsNone(telemetry.operation_value(status, field))
        self.assertIsNone(telemetry.operation_value(status, "pressure"))

    def test_unknown_string_modes_are_preserved_but_invalid_numbers_are_not(self):
        status = sample_heatpump_status()
        status["operation"]["fanOperatingMode"] = "FutureMode"
        self.assertEqual(telemetry.operation_value(status, "fanOperatingMode"), "FutureMode")
        for invalid in (True, "1", float("inf"), float("nan")):
            status["operation"]["fanSpeedStatus"] = invalid
            self.assertIsNone(telemetry.operation_value(status, "fanSpeedStatus"))

    def test_component_heat_pumps_take_priority_over_legacy_aggregate(self):
        equipment = sample_equipment() + [
            {"id": "idu", "type": "HeatPumpIdu"},
            {"id": "odu", "type": "HeatPumpOdu"},
        ]
        system = models.System("s1", "Home", equipment=equipment)
        self.assertEqual(
            [item["id"] for item in models.heatpumps_for_system(system)], ["idu", "odu"]
        )
        system.equipment = sample_equipment()
        self.assertEqual([item["id"] for item in models.heatpumps_for_system(system)], ["hp1"])

    def test_fresh_zone_connection_takes_priority_over_cached_system_health(self):
        zone = models.Zone("s1", "Home", "z1", "Main", sample_status(), "Disconnected")
        zone.status["connectivity"] = {"connectionStatus": "Connected", "issues": []}
        self.assertTrue(zone.online)
        self.assertEqual(zone.connectivity_issues, [])
        zone.connection_status = "Connected"
        zone.status["connectivity"]["connectionStatus"] = "Disconnected"
        self.assertFalse(zone.online)
        zone.status["connectivity"]["connectionStatus"] = "Unexpected"
        self.assertFalse(zone.online)

    def test_freshness_metadata_is_optional_and_not_a_success_timestamp(self):
        zone = models.Zone("s1", "Home", "z1", "Main", sample_status())
        self.assertIsNone(zone.telemetry_status)
        self.assertIsNone(zone.observed_at)
        self.assertIsNone(zone.connectivity_issues)
        zone.status["health"] = {"telemetryStatus": "Current", "observedAt": "2026-11-04T07:00:00Z"}
        self.assertEqual(zone.telemetry_status, "Current")
        self.assertEqual(zone.observed_at, "2026-11-04T07:00:00Z")


if __name__ == "__main__":
    unittest.main()
