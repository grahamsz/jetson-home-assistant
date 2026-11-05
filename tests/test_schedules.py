"""Absent schedules are unknown; durations do not imply circulation is enabled."""

import unittest

from protocol_loader import models, sample_status


class ScheduleModelTests(unittest.TestCase):
    def setUp(self):
        self.zone = models.Zone("s", "Home", "z", "Main", sample_status())

    def test_missing_null_or_malformed_schedule_is_not_active(self):
        for value in (None, False, "Active", [], {}):
            self.zone.status["schedule"] = value
            self.assertIsNone(self.zone.schedule_paused)
            self.assertIsNone(self.zone.schedule_target)
            self.assertFalse(self.zone.can_resume_schedule)

    def test_active_and_paused_weekly_or_vacation_schedules(self):
        for kind in ("Weekly", "Vacation"):
            self.zone.status["schedule"] = {"id": "schedule-1", "kind": kind, "status": "Active"}
            self.assertFalse(self.zone.schedule_paused)
            self.assertEqual(self.zone.schedule_target, ("schedule-1", kind))
            self.assertFalse(self.zone.can_resume_schedule)
            self.zone.schedule["status"] = "Paused"
            self.assertTrue(self.zone.schedule_paused)
            self.assertTrue(self.zone.can_resume_schedule)

    def test_invalid_or_future_schedule_data_never_becomes_a_resume_target(self):
        for schedule_id, kind, status in (
            (None, "Weekly", "Paused"),
            ("", "Weekly", "Paused"),
            (" ", "Weekly", "Paused"),
            ("s", "Future", "Paused"),
            ("s", "Weekly", "Future"),
            ("s", "Weekly", None),
        ):
            self.zone.status["schedule"] = {"id": schedule_id, "kind": kind, "status": status}
            self.assertFalse(self.zone.can_resume_schedule)

    def test_duration_accepts_full_integer_range_without_enabling_circulation(self):
        for value in (0, 1, 15, 30, 45, 60, 30.0):
            self.zone.circulation["settings"]["fanOnDuration"] = value
            self.assertEqual(self.zone.circulation_minutes, value)
            self.assertEqual(self.zone.circulation_mode, "Off")
        self.zone.circulation["settings"]["mode"] = "Continuous"
        self.assertEqual(self.zone.circulation_minutes, 30)
        self.assertEqual(self.zone.circulation_mode, "Continuous")

    def test_bad_duration_is_not_zero_or_a_fallback_to_old_settings(self):
        self.zone.circulation["fanOnDurationSetting"] = {"value": 15}
        for value in (None, True, False, "30", -1, 61, 1.5, float("inf"), float("nan")):
            self.zone.circulation["settings"]["fanOnDuration"] = value
            self.assertIsNone(self.zone.circulation_minutes)
        del self.zone.circulation["settings"]["fanOnDuration"]
        self.assertEqual(self.zone.circulation_minutes, 15)


if __name__ == "__main__":
    unittest.main()
