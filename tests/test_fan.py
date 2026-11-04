"""Actual fan activity/speed are independent from selected HVAC/fan settings."""

import unittest

from protocol_loader import models, sample_heatpump_status, sample_status, telemetry


class FanTests(unittest.TestCase):
    def setUp(self):
        self.zone = models.Zone("s", "Home", "z", "Main", sample_status())

    def test_actual_fan_speed_drives_activity_without_changing_selected_mode(self):
        for speed, state, activity in (
            (0, "0", "off"),
            (1, "1", "running"),
            (2, "2", "running"),
            (3, "3", "running"),
        ):
            self.zone.circulation["fanSpeedStatus"] = speed
            self.assertEqual(self.zone.fan_speed_state, state)
            self.assertEqual(self.zone.fan_activity_state, activity)
            self.assertEqual(self.zone.fan_mode_state, "auto")
            self.assertEqual(self.zone.hvac_mode_state, "heat")

    def test_circulation_fallback_only_when_actual_speed_is_absent(self):
        for raw, expected in (
            ("Off", "off"),
            ("Circulating", "running"),
            ("Unknown", None),
            ("FutureState", None),
            (None, None),
        ):
            self.zone.circulation["status"] = raw
            self.assertEqual(self.zone.fan_activity_state, expected)
        self.zone.circulation.update(status="Off", fanSpeedStatus=2)
        self.assertEqual(self.zone.fan_activity_state, "running")
        self.zone.circulation["fanSpeedStatus"] = None
        self.assertIsNone(self.zone.fan_activity_state)

    def test_invalid_or_missing_speed_is_unknown_instead_of_off(self):
        for raw in (None, True, False, "1", -1, 4, 1.5, float("nan"), float("inf")):
            self.zone.circulation["fanSpeedStatus"] = raw
            self.assertIsNone(self.zone.fan_speed_state)
            self.assertIsNone(self.zone.fan_activity_state)

    def test_unit_speed_states_preserve_raw_api_numbers(self):
        status = sample_heatpump_status()
        for speed in range(4):
            status["operation"]["fanSpeedStatus"] = speed
            self.assertEqual(telemetry.operation_speed_state(status, "fanSpeedStatus"), str(speed))
            self.assertEqual(telemetry.operation_value(status, "fanSpeedStatus"), speed)
        for speed in range(1, 4):
            status["operation"]["fanSpeedSetpoint"] = speed
            self.assertEqual(
                telemetry.operation_speed_state(status, "fanSpeedSetpoint"), str(speed)
            )
        for value in (0, None, True, "1", 1.5, 4):
            status["operation"]["fanSpeedSetpoint"] = value
            self.assertIsNone(telemetry.operation_speed_state(status, "fanSpeedSetpoint"))


if __name__ == "__main__":
    unittest.main()
