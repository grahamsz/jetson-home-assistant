"""Coordinator command guards and fresh schedule targeting without HA installed."""

import asyncio
import importlib.util
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from protocol_loader import api, models, polling, sample_status
from test_entities import ROOT, LocalizedError, adapters, module


class DataCoordinatorAdapter:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, hass, logger, *, config_entry, update_interval, **kwargs):
        self.hass = hass
        self.config_entry = config_entry
        self.update_interval = update_interval
        self.last_update_success = True
        self.refreshes = 0

    async def async_request_refresh(self):
        self.refreshes += 1


class CommandTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        modules = adapters()
        modules[
            "homeassistant.helpers.update_coordinator"
        ].DataUpdateCoordinator = DataCoordinatorAdapter
        modules["homeassistant.helpers.update_coordinator"].UpdateFailed = RuntimeError
        modules["homeassistant.exceptions"].ConfigEntryAuthFailed = LocalizedError
        modules["jetson_entity_contract.api"] = api
        modules["jetson_entity_contract.polling"] = polling
        modules["jetson_entity_contract.devices"] = module(
            "jetson_entity_contract.devices", sync_devices=lambda *args: {}
        )
        context = patch.dict(sys.modules, modules)
        context.start()
        self.addCleanup(context.stop)
        spec = importlib.util.spec_from_file_location(
            "jetson_entity_contract.coordinator_real", ROOT / "coordinator.py"
        )
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        self.entry = SimpleNamespace(options={}, async_start_reauth=Mock())
        self.client = SimpleNamespace(
            resume_schedule=AsyncMock(),
            set_circulation_duration=AsyncMock(),
            set_humidity_settings=AsyncMock(),
        )
        self.coordinator = loaded.JetsonCoordinator(object(), self.entry, self.client)
        self.zone = models.Zone("s", "Home", "z", "Main", sample_status())
        self.zone.status["schedule"] = {"id": "old-id", "kind": "Weekly", "status": "Paused"}
        self.coordinator.data = models.Snapshot(zones={self.zone.key: self.zone})

    async def test_humidity_rechecks_capabilities_after_waiting_for_lock(self):
        await self.coordinator.command_lock.acquire()
        task = asyncio.create_task(
            self.coordinator.command("set_humidity_settings", self.zone, {"mode": "Humidify"})
        )
        await asyncio.sleep(0)
        self.zone.humidity.pop("capabilities")
        self.coordinator.command_lock.release()
        with self.assertRaises(LocalizedError):
            await task
        self.client.set_humidity_settings.assert_not_awaited()

    async def test_humidity_uses_current_limits_and_step(self):
        self.zone.humidity_capabilities["setpoint"] = {"min": 20, "max": 50, "precision": 5}
        for target in (55, 43):
            with self.assertRaises(LocalizedError):
                await self.coordinator.command(
                    "set_humidity_settings", self.zone, {"setpoint": {"value": target}}
                )
        self.client.set_humidity_settings.assert_not_awaited()
        await self.coordinator.command(
            "set_humidity_settings", self.zone, {"setpoint": {"value": 45}}
        )
        self.client.set_humidity_settings.assert_awaited_once_with("z", {"setpoint": {"value": 45}})
        self.assertEqual(self.coordinator.refreshes, 1)

    async def test_resume_targets_latest_schedule_after_waiting_for_command_lock(self):
        await self.coordinator.command_lock.acquire()
        task = asyncio.create_task(self.coordinator.command("resume_schedule", self.zone, None))
        await asyncio.sleep(0)
        replacement = models.Zone("s", "Home", "z", "Main", sample_status())
        replacement.status["schedule"] = {"id": "new-id", "kind": "Vacation", "status": "Paused"}
        self.coordinator.data.zones[self.zone.key] = replacement
        self.coordinator.command_lock.release()
        await task
        self.client.resume_schedule.assert_awaited_once_with("new-id", "Vacation")
        self.assertEqual(self.coordinator.refreshes, 1)

    async def test_no_resume_for_missing_active_or_unknown_schedule(self):
        for schedule in (
            None,
            {},
            {"id": "s", "kind": "Weekly", "status": "Active"},
            {"id": "s", "kind": "Weekly", "status": "Unknown"},
            {"id": "s", "kind": "Future", "status": "Paused"},
        ):
            self.zone.status["schedule"] = schedule
            with self.assertRaises(LocalizedError) as caught:
                await self.coordinator.command("resume_schedule", self.zone, None)
            self.assertEqual(
                caught.exception.translation["translation_key"], "schedule_unavailable"
            )
        self.client.resume_schedule.assert_not_awaited()
        self.assertEqual(self.coordinator.refreshes, 0)

    async def test_removed_offline_or_failed_zone_never_sends_controls(self):
        self.zone.connection_status = "Disconnected"
        with self.assertRaises(LocalizedError):
            await self.coordinator.command("resume_schedule", self.zone, None)
        self.zone.connection_status = "Connected"
        self.coordinator.last_update_success = False
        with self.assertRaises(LocalizedError):
            await self.coordinator.command("resume_schedule", self.zone, None)
        self.coordinator.last_update_success = True
        self.coordinator.data.zones.clear()
        with self.assertRaises(LocalizedError):
            await self.coordinator.command("resume_schedule", self.zone, None)
        self.client.resume_schedule.assert_not_awaited()

    async def test_duration_requires_current_reported_feature_and_refreshes_after_success(self):
        await self.coordinator.command("set_circulation_duration", self.zone, 30)
        self.client.set_circulation_duration.assert_awaited_once_with("z", 30)
        self.assertEqual(self.coordinator.refreshes, 1)
        self.zone.circulation["settings"]["fanOnDuration"] = None
        with self.assertRaises(LocalizedError) as caught:
            await self.coordinator.command("set_circulation_duration", self.zone, 15)
        self.assertEqual(caught.exception.translation["translation_key"], "circulation_unavailable")
        self.assertEqual(self.client.set_circulation_duration.await_count, 1)

    async def test_backend_failure_does_not_report_success_or_repeat_resume(self):
        self.client.resume_schedule.side_effect = api.JetsonError("Unconfirmed")
        with self.assertRaises(LocalizedError) as caught:
            await self.coordinator.command("resume_schedule", self.zone, None)
        self.assertEqual(caught.exception.translation["translation_key"], "command_failed")
        self.client.resume_schedule.assert_awaited_once()
        self.assertEqual(self.coordinator.refreshes, 0)

    async def test_auth_failure_starts_reauthentication_without_replaying_resume(self):
        self.client.resume_schedule.side_effect = api.JetsonAuthError("Expired")
        with self.assertRaises(LocalizedError) as caught:
            await self.coordinator.command("resume_schedule", self.zone, None)
        self.assertEqual(caught.exception.translation["translation_key"], "reauth_required")
        self.entry.async_start_reauth.assert_called_once_with(self.coordinator.hass)
        self.client.resume_schedule.assert_awaited_once()
        self.assertEqual(self.coordinator.refreshes, 0)


if __name__ == "__main__":
    unittest.main()
