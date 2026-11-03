"""Contract and failure-path tests against a local HTTP server."""

import asyncio
import json
import time
import unittest
from pathlib import Path

import aiohttp
from aiohttp import web
from protocol_loader import (
    api,
    models,
    polling,
    sample_air_quality,
    sample_equipment,
    sample_status,
)


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.calls = []
        self.saved = []
        self.behavior = None
        self.status = sample_status()
        self.boards = [{"id": "b1", "type": "Arctic", "serialNumber": "invented-hub-serial"}]
        self.equipment = sample_equipment()
        self.air_quality = sample_air_quality()
        application = web.Application()
        application.router.add_route("*", "/{tail:.*}", self.handle)
        self.runner = web.AppRunner(application)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await site.start()
        port = self.runner.addresses[0][1]
        self.session = aiohttp.ClientSession()
        self.client = api.JetsonClient(
            self.session,
            api.Tokens("old-access", "old-refresh", time.time() + 3600, "user-1"),
            install_id="install-1",
            on_tokens=self.saved.append,
            base_url=f"http://127.0.0.1:{port}",
        )

    async def asyncTearDown(self):
        await self.session.close()
        await self.runner.cleanup()

    async def handle(self, request):
        body = await request.json() if request.can_read_body else None
        self.calls.append((request.method, request.raw_path, body, dict(request.headers)))
        if self.behavior:
            response = await self.behavior(request, body)
            if response is not None:
                return response
        path = request.path
        if path in ("/v1/auth/refresh", "/v1/auth/verify/magic-link"):
            return web.json_response(
                {
                    "accessToken": "new-access",
                    "refreshToken": "new-refresh",
                    "expiresIn": 3600,
                    "userId": "user-1",
                }
            )
        if path == "/v1/systems":
            return web.json_response(
                {
                    "systems": [
                        {
                            "id": "s1",
                            "name": "Test system",
                            "health": {"connectionStatus": "Connected"},
                        }
                    ]
                }
            )
        if path == "/v1/systems/s1/zones":
            return web.json_response(
                {"zones": [{"id": "z1", "name": "Test zone", "equipmentIds": ["e1"]}]}
            )
        if path == "/v1/zones/z1/status":
            return web.json_response(self.status)
        if path == "/v1/systems/s1/boards":
            return web.json_response({"boards": self.boards})
        if path == "/v1/systems/s1/equipment":
            return web.json_response({"equipment": self.equipment})
        if path == "/v1/zones/z1/airQuality":
            return web.json_response(self.air_quality)
        if path.endswith("/humidity/settings"):
            return web.json_response(
                {"mode": body.get("mode", "Off"), "setpoint": body.get("setpoint", {"value": 40})}
            )
        return web.json_response({"result": "ok"})

    async def test_discovery_and_nested_fields(self):
        zones = await self.client.get_zones()
        zone = zones["s1:z1"]
        self.assertEqual(
            (zone.current_temperature, zone.target_temperature, zone.current_humidity),
            (21.25, 22, 38.5),
        )
        self.assertTrue(zone.supports_humidifier)
        self.assertEqual(zone.fan_max, 3)
        self.assertEqual(zone.equipment_ids, ["e1"])
        self.assertEqual(
            [x[1] for x in self.calls],
            ["/v1/systems", "/v1/systems/s1/zones", "/v1/zones/z1/status"],
        )
        self.assertEqual(self.calls[-1][3]["Authorization"], "Bearer old-access")
        self.assertEqual(self.calls[-1][3]["X-App-Install-ID"], "install-1")
        self.assertEqual(self.calls[-1][3]["app-version"], "1.2.8")

    async def test_empty_account_is_supported(self):
        async def behavior(request, body):
            return web.json_response({"systems": []})

        self.behavior = behavior
        self.assertEqual(await self.client.get_zones(), {})

    async def test_authentication_wire_format(self):
        await self.client.request_magic_link("test@example.invalid")
        self.assertEqual(
            self.calls[-1][2], {"email": "test@example.invalid", "appScheme": "jetsonhome"}
        )
        self.assertNotIn("Authorization", self.calls[-1][3])
        tokens = await self.client.verify_magic_link("test@example.invalid", "test-token")
        self.assertEqual(tokens.refresh_token, "new-refresh")
        self.assertEqual(self.saved[-1].access_token, "new-access")

    async def test_expired_access_rotates_and_persists_before_discovery(self):
        self.client.tokens.expires_at = 0
        await self.client.get_zones()
        self.assertEqual(self.calls[0][1:3], ("/v1/auth/refresh", {"refreshToken": "old-refresh"}))
        self.assertEqual(self.calls[1][3]["Authorization"], "Bearer new-access")
        self.assertEqual(self.saved[0].refresh_token, "new-refresh")

    async def test_parallel_expiry_only_refreshes_once(self):
        self.client.tokens.expires_at = 0
        await asyncio.gather(*(self.client.request("GET", "/v1/systems") for _ in range(5)))
        self.assertEqual(sum(call[1] == "/v1/auth/refresh" for call in self.calls), 1)

    async def test_401_refreshes_and_retries_once(self):
        async def behavior(request, body):
            if request.headers.get("Authorization") == "Bearer old-access":
                return web.json_response({}, status=401)

        self.behavior = behavior
        await self.client.request("GET", "/v1/systems")
        self.assertEqual(
            [x[1] for x in self.calls], ["/v1/systems", "/v1/auth/refresh", "/v1/systems"]
        )

    async def test_persistent_401_does_not_loop(self):
        async def behavior(request, body):
            if request.path != "/v1/auth/refresh":
                return web.json_response({}, status=401)

        self.behavior = behavior
        with self.assertRaises(api.JetsonAuthError):
            await self.client.request("GET", "/v1/systems")
        self.assertEqual(len(self.calls), 3)

    async def test_refresh_revocation_triggers_reauth(self):
        self.client.tokens.expires_at = 0

        async def behavior(request, body):
            return web.json_response({}, status=403)

        self.behavior = behavior
        with self.assertRaises(api.JetsonAuthError):
            await self.client.get_zones()

    async def test_403_on_resource_is_permission_error_without_refresh(self):
        async def behavior(request, body):
            return web.json_response({}, status=403)

        self.behavior = behavior
        with self.assertRaises(api.JetsonHTTPError):
            await self.client.get_zones()
        self.assertEqual(len(self.calls), 1)

    async def test_all_mode_and_scalar_temperature_commands(self):
        for mode in ("Off", "Heat", "Cool", "Auto", "FanOnly"):
            await self.client.set_mode("z1", mode)
            self.assertEqual(
                self.calls[-1][:3], ("POST", "/v1/zones/z1/hvac/mode", {"value": mode})
            )
        await self.client.set_temperature("z1", 22.5)
        self.assertEqual(
            self.calls[-1][:3],
            ("POST", "/v1/zones/z1/ambientTemperature/setpoint", {"value": 22.5}),
        )

    async def test_fan_and_humidity_patch_payloads(self):
        await self.client.set_fan_speed("z1", 2)
        self.assertEqual(
            self.calls[-1][:3], ("PATCH", "/v1/zones/z1/circulation/settings", {"fanSpeed": 2})
        )
        await self.client.set_fan_speed("z1", "Auto")
        await self.client.set_humidity_settings(
            "z1", {"mode": "Humidify", "setpoint": {"value": 45}}
        )
        self.assertEqual(
            self.calls[-1][:3],
            (
                "PATCH",
                "/v1/zones/z1/humidity/settings",
                {"mode": "Humidify", "setpoint": {"value": 45}},
            ),
        )
        await self.client.set_humidity_settings("z1", {"mode": "Off"})

    async def test_unreachable_result_is_not_success(self):
        async def behavior(request, body):
            return web.json_response({"result": "unreachable", "error": "sensitive detail"})

        self.behavior = behavior
        with self.assertRaisesRegex(api.JetsonError, "could not reach"):
            await self.client.set_temperature("z1", 22)
        self.assertEqual(len(self.calls), 1)

    async def test_transient_write_failure_is_not_replayed(self):
        async def behavior(request, body):
            return web.json_response({"secret": "not for logs"}, status=503)

        self.behavior = behavior
        with self.assertRaises(api.JetsonError) as error:
            await self.client.set_mode("z1", "Heat")
        self.assertNotIn("secret", str(error.exception))
        self.assertEqual(len(self.calls), 1)

    async def test_rate_limit_suppresses_subsequent_requests(self):
        async def behavior(request, body):
            return web.json_response({}, status=429, headers={"Retry-After": "120"})

        self.behavior = behavior
        for _ in range(2):
            with self.assertRaises(api.JetsonRateLimitError):
                await self.client.get_zones()
        self.assertEqual(len(self.calls), 1)

    async def test_redirect_does_not_forward_credentials(self):
        async def behavior(request, body):
            return web.Response(status=302, headers={"Location": "/unexpected"})

        self.behavior = behavior
        with self.assertRaises(api.JetsonHTTPError):
            await self.client.get_zones()
        self.assertEqual(len(self.calls), 1)

    async def test_malformed_json_fails_cleanly(self):
        async def behavior(request, body):
            return web.Response(text="{bad", content_type="application/json")

        self.behavior = behavior
        with self.assertRaisesRegex(api.JetsonError, "invalid JSON"):
            await self.client.get_zones()

    async def test_schema_drift_fails_instead_of_erasing_entities(self):
        async def behavior(request, body):
            return web.json_response({"different": []})

        self.behavior = behavior
        with self.assertRaisesRegex(api.JetsonError, "systems list"):
            await self.client.get_zones()

    async def test_invalid_input_never_reaches_network(self):
        invalid = [
            self.client.set_mode("z1", "Dehumidify"),
            self.client.set_temperature("z1", float("nan")),
            self.client.set_fan_speed("z1", True),
            self.client.set_fan_speed("z1", 1.0),
            self.client.set_humidity_settings("z1", {}),
            self.client.set_humidity_settings("z1", {"mode": "Dehumidify"}),
            self.client.set_humidity_settings("z1", {"setpoint": {"value": 101}}),
        ]
        for action in invalid:
            with self.assertRaises(ValueError):
                await action
        self.assertEqual(self.calls, [])

    async def test_missing_features_is_schema_error(self):
        self.status = {}
        with self.assertRaisesRegex(api.JetsonError, "features"):
            await self.client.get_zones()

    async def test_snapshot_discovers_hardware_and_zone_air_quality(self):
        snapshot = await self.client.get_snapshot()
        self.assertEqual(snapshot.systems["s1"].boards[0]["id"], "b1")
        self.assertEqual(len(snapshot.systems["s1"].equipment), 3)
        zone = snapshot.zones["s1:z1"]
        self.assertEqual(
            (
                zone.air_quality_overall,
                zone.pollutant("co2"),
                zone.pollutant("pm25"),
                zone.pollutant("tvoc"),
            ),
            ("good", 650, 4.5, 250),
        )
        self.assertEqual(len(self.calls), 6)
        self.assertEqual(sum(call[1] == "/v1/systems" for call in self.calls), 1)

    async def test_energy_hardware_does_not_invent_energy_telemetry(self):
        snapshot = await self.client.get_snapshot()
        devices = models.build_devices(snapshot)
        monitor = devices["equipment:s1:em1"]
        self.assertEqual(monitor.via_identifier, "board:s1:b1")
        self.assertEqual(monitor.model, "EM-001")
        self.assertTrue(all("/energy" not in call[1] for call in self.calls))

    async def test_no_air_monitor_means_no_air_quality_request(self):
        self.equipment = [item for item in self.equipment if item["type"] != "Sensor"]
        snapshot = await self.client.get_snapshot()
        self.assertIsNone(snapshot.zones["s1:z1"].air_quality)
        self.assertFalse(any("airQuality" in call[1] for call in self.calls))

    async def test_limited_air_quality_cannot_expose_numeric_readings(self):
        self.air_quality["access"] = "limited"
        self.air_quality["missingEntitlement"] = "jetson_care"
        snapshot = await self.client.get_snapshot()
        zone = snapshot.zones["s1:z1"]
        self.assertEqual(zone.air_quality_overall, "good")
        self.assertIsNone(zone.pollutant("co2"))
        self.assertIsNone(zone.pollutant("pm25"))
        self.assertIsNone(zone.pollutant("tvoc"))

    async def test_failed_air_quality_does_not_disable_climate(self):
        async def behavior(request, body):
            if request.path.endswith("/airQuality"):
                return web.json_response({}, status=503)

        self.behavior = behavior
        snapshot = await self.client.get_snapshot()
        self.assertEqual(snapshot.zones["s1:z1"].current_temperature, 21.25)
        self.assertIsNone(snapshot.zones["s1:z1"].air_quality)
        self.assertIn("s1:z1", snapshot.air_quality_errors)

    async def test_inventory_failure_preserves_previous_hardware_links(self):
        first = models.build_devices(await self.client.get_snapshot())

        async def behavior(request, body):
            if request.path.endswith("/equipment") or request.path.endswith("/boards"):
                return web.json_response({}, status=503)

        self.behavior = behavior
        snapshot = await self.client.get_snapshot()
        self.assertEqual(models.build_devices(snapshot), first)
        self.assertIsNotNone(snapshot.systems["s1"].equipment_error)
        self.assertIsNotNone(snapshot.systems["s1"].boards_error)
        self.assertEqual(snapshot.zones["s1:z1"].target_temperature, 22)

    async def test_missing_inventory_permission_does_not_disable_climate(self):
        async def behavior(request, body):
            if request.path.endswith("/equipment") or request.path.endswith("/boards"):
                return web.json_response({}, status=403)

        self.behavior = behavior
        snapshot = await self.client.get_snapshot()
        self.assertEqual(snapshot.zones["s1:z1"].current_temperature, 21.25)
        self.assertFalse(snapshot.systems["s1"].equipment)
        self.assertIsNotNone(snapshot.systems["s1"].equipment_error)

    async def test_invalid_air_quality_response_does_not_disable_climate(self):
        self.air_quality = {"unexpected": True}
        snapshot = await self.client.get_snapshot()
        self.assertIn("s1:z1", snapshot.air_quality_errors)
        self.assertIsNone(snapshot.zones["s1:z1"].air_quality)

    async def test_auth_failure_on_optional_endpoint_still_requires_login(self):
        async def behavior(request, body):
            if request.path.endswith("/airQuality"):
                return web.json_response({}, status=401)

        self.behavior = behavior
        with self.assertRaises(api.JetsonAuthError):
            await self.client.get_snapshot()

    async def test_empty_snapshot_before_installation(self):
        async def behavior(request, body):
            return web.json_response({"systems": []})

        self.behavior = behavior
        snapshot = await self.client.get_snapshot()
        self.assertFalse(snapshot.systems)
        self.assertFalse(snapshot.zones)
        self.assertEqual(len(self.calls), 1)

    async def test_air_monitor_is_not_assigned_to_unrelated_zone(self):
        for item in self.equipment:
            if item["id"] == "aq1":
                item["zoneIds"] = ["z2"]
        snapshot = await self.client.get_snapshot()
        self.assertIsNone(snapshot.zones["s1:z1"].air_quality)
        self.assertFalse(any("airQuality" in call[1] for call in self.calls))

    async def test_malformed_hardware_id_is_optional_inventory_error(self):
        self.equipment = [{"model": "EM-001", "type": "EnergyMonitor"}]
        snapshot = await self.client.get_snapshot()
        self.assertIsNotNone(snapshot.systems["s1"].equipment_error)
        self.assertEqual(snapshot.zones["s1:z1"].current_temperature, 21.25)

    async def test_regular_updates_read_only_known_zone_status_and_air_quality(self):
        previous = await self.client.get_snapshot()
        self.calls.clear()
        self.status["features"]["ambientTemperature"]["currentTemperature"] = 23
        self.air_quality["current"]["co2"]["value"] = 700
        current = await self.client.get_updates(previous)
        self.assertEqual(
            [call[1] for call in self.calls], ["/v1/zones/z1/status", "/v1/zones/z1/airQuality"]
        )
        self.assertEqual(current.zones["s1:z1"].current_temperature, 23)
        self.assertEqual(current.zones["s1:z1"].pollutant("co2"), 700)
        self.assertEqual(previous.zones["s1:z1"].current_temperature, 21.25)
        self.assertEqual(previous.zones["s1:z1"].pollutant("co2"), 650)

    async def test_regular_updates_without_air_monitor_read_only_status(self):
        self.equipment = [item for item in self.equipment if item["type"] != "Sensor"]
        previous = await self.client.get_snapshot()
        self.calls.clear()
        await self.client.get_updates(previous)
        self.assertEqual([call[1] for call in self.calls], ["/v1/zones/z1/status"])

    async def test_air_quality_failure_does_not_reuse_previous_reading(self):
        previous = await self.client.get_snapshot()

        async def behavior(request, body):
            if request.path.endswith("/airQuality"):
                return web.json_response({}, status=503)

        self.behavior = behavior
        failed = await self.client.get_updates(previous)
        self.assertEqual(failed.zones["s1:z1"].current_temperature, 21.25)
        self.assertIsNone(failed.zones["s1:z1"].pollutant("co2"))
        self.assertIn("s1:z1", failed.air_quality_errors)
        self.behavior = None
        recovered = await self.client.get_updates(failed)
        self.assertFalse(recovered.air_quality_errors)
        self.assertEqual(recovered.zones["s1:z1"].pollutant("co2"), 650)

    async def test_access_changes_take_effect_without_configuration_discovery(self):
        previous = await self.client.get_snapshot()
        self.air_quality["access"] = "limited"
        current = await self.client.get_updates(previous)
        self.assertEqual(current.zones["s1:z1"].air_quality_access, "limited")
        self.assertIsNone(current.zones["s1:z1"].pollutant("co2"))
        self.assertEqual(previous.zones["s1:z1"].pollutant("co2"), 650)

    async def test_connectivity_refresh_does_not_change_discovered_configuration(self):
        previous = await self.client.get_snapshot()
        self.calls.clear()
        for item in self.equipment:
            item.update(name="Changed name", zoneIds=["new-zone"], connectionStatus="Disconnected")
        self.equipment.append({"id": "new-equipment", "connectionStatus": "Connected"})

        async def behavior(request, body):
            if request.path == "/v1/systems":
                return web.json_response(
                    {
                        "systems": [
                            {
                                "id": "s1",
                                "name": "Changed system",
                                "health": {"connectionStatus": "Disconnected"},
                            },
                            {"id": "new-system", "name": "New system"},
                        ]
                    }
                )

        self.behavior = behavior
        current = await self.client.get_updates(previous, refresh_connectivity=True)
        self.assertEqual(set(current.systems), {"s1"})
        self.assertEqual(set(current.zones), {"s1:z1"})
        self.assertEqual(current.systems["s1"].name, "Test system")
        self.assertEqual(len(current.systems["s1"].equipment), 3)
        self.assertEqual(current.systems["s1"].equipment[1]["zoneIds"], ["z1"])
        self.assertEqual(current.systems["s1"].equipment[1]["name"], "Return air monitor")
        self.assertEqual(current.systems["s1"].equipment[1]["connectionStatus"], "Disconnected")
        self.assertFalse(current.zones["s1:z1"].online)
        self.assertTrue(previous.zones["s1:z1"].online)
        self.assertEqual(current.zones["s1:z1"].pollutant("co2"), 650)
        self.assertEqual(
            [call[1] for call in self.calls],
            [
                "/v1/systems",
                "/v1/systems/s1/equipment",
                "/v1/zones/z1/status",
                "/v1/zones/z1/airQuality",
            ],
        )

    async def test_missing_equipment_connection_becomes_unknown_until_discovery(self):
        previous = await self.client.get_snapshot()
        self.equipment = []
        current = await self.client.get_updates(previous, refresh_connectivity=True)
        self.assertEqual(len(current.systems["s1"].equipment), 3)
        self.assertTrue(
            all(item["connectionStatus"] == "Unknown" for item in current.systems["s1"].equipment)
        )

    async def test_connectivity_failure_keeps_configuration_and_zone_readings(self):
        previous = await self.client.get_snapshot()

        async def behavior(request, body):
            if request.path in ("/v1/systems", "/v1/systems/s1/equipment"):
                return web.json_response({}, status=503)

        self.behavior = behavior
        current = await self.client.get_updates(previous, refresh_connectivity=True)
        self.assertIsNotNone(current.system_health_error)
        self.assertIsNotNone(current.systems["s1"].equipment_error)
        self.assertIsNone(current.zones["s1:z1"].connection_status)
        self.assertEqual(current.zones["s1:z1"].current_temperature, 21.25)
        self.assertEqual(models.build_devices(current), models.build_devices(previous))

    async def test_auth_failure_during_connectivity_refresh_is_not_ignored(self):
        previous = await self.client.get_snapshot()

        async def behavior(request, body):
            if request.path == "/v1/systems":
                return web.json_response({}, status=401)

        self.behavior = behavior
        with self.assertRaises(api.JetsonAuthError):
            await self.client.get_updates(previous, refresh_connectivity=True)

    async def test_poller_discovers_once_and_refreshes_connectivity_every_five_minutes(self):
        now = [0.0]
        poller = polling.JetsonPoller(self.client, clock=lambda: now[0])
        await poller.refresh()
        self.assertEqual(len(self.calls), 6)
        for moment, expected in ((30, 2), (299, 2), (300, 4), (330, 2), (600, 4)):
            now[0] = moment
            self.calls.clear()
            await poller.refresh()
            self.assertEqual(len(self.calls), expected, moment)
            self.assertFalse(any(call[1].endswith(("/boards", "/zones")) for call in self.calls))
        self.assertEqual(poller.configuration_revision, 1)

    async def test_manual_configuration_refresh_finds_new_zones_and_removals(self):
        poller = polling.JetsonPoller(self.client)
        await poller.refresh()

        async def behavior(request, body):
            if request.path == "/v1/systems/s1/zones":
                return web.json_response({"zones": [{"id": "z2", "name": "New zone"}]})
            if request.path == "/v1/zones/z2/status":
                return web.json_response(self.status)

        self.behavior = behavior
        self.assertEqual(set((await poller.refresh()).zones), {"s1:z1"})
        updated = await poller.refresh(discover=True)
        self.assertEqual(set(updated.zones), {"s1:z2"})
        self.assertEqual(poller.configuration_revision, 2)
        self.calls.clear()
        self.assertEqual(set((await poller.refresh()).zones), {"s1:z2"})
        self.assertEqual([call[1] for call in self.calls], ["/v1/zones/z2/status"])

    async def test_failed_configuration_refresh_keeps_last_good_configuration(self):
        poller = polling.JetsonPoller(self.client)
        previous = await poller.refresh()

        async def behavior(request, body):
            if request.path.endswith("/zones"):
                return web.json_response({}, status=503)

        self.behavior = behavior
        with self.assertRaises(api.JetsonError):
            await poller.refresh(discover=True)
        self.assertIs(poller.snapshot, previous)
        self.assertEqual(poller.configuration_revision, 1)
        self.calls.clear()
        current = await poller.refresh()
        self.assertEqual(set(current.zones), {"s1:z1"})
        self.assertEqual(len(self.calls), 2)

    async def test_failed_measurement_refresh_does_not_mutate_last_good_state(self):
        poller = polling.JetsonPoller(self.client)
        previous = await poller.refresh()
        self.status = {}
        with self.assertRaises(api.JetsonError):
            await poller.refresh()
        self.assertIs(poller.snapshot, previous)
        self.assertEqual(previous.zones["s1:z1"].current_temperature, 21.25)

    async def test_empty_configuration_does_not_poll_discovery_in_background(self):
        async def empty(request, body):
            return web.json_response({"systems": []})

        self.behavior = empty
        now = [0.0]
        poller = polling.JetsonPoller(self.client, clock=lambda: now[0])
        self.assertFalse((await poller.refresh()).systems)
        self.behavior = None
        self.calls.clear()
        now[0] = 1000
        self.assertFalse((await poller.refresh()).systems)
        self.assertEqual(self.calls, [])
        self.assertEqual(set((await poller.refresh(discover=True)).systems), {"s1"})

    async def test_configuration_refresh_waits_for_in_progress_measurement_poll(self):
        poller = polling.JetsonPoller(self.client)
        await poller.refresh()
        entered = asyncio.Event()
        release = asyncio.Event()
        blocked = False

        async def behavior(request, body):
            nonlocal blocked
            if request.path == "/v1/zones/z1/status" and not blocked:
                blocked = True
                entered.set()
                await release.wait()

        self.behavior = behavior
        self.calls.clear()
        update = asyncio.create_task(poller.refresh())
        await asyncio.wait_for(entered.wait(), timeout=2)
        discover = asyncio.create_task(poller.refresh(discover=True))
        try:
            await asyncio.sleep(0)
            self.assertEqual([call[1] for call in self.calls], ["/v1/zones/z1/status"])
        finally:
            release.set()
        _, latest = await asyncio.gather(update, discover)
        self.assertIs(poller.snapshot, latest)
        self.assertEqual(poller.configuration_revision, 2)
        self.assertEqual(
            [call[1] for call in self.calls[:3]],
            ["/v1/zones/z1/status", "/v1/zones/z1/airQuality", "/v1/systems"],
        )


class ModelTests(unittest.TestCase):
    def zone(self, status=None):
        return models.Zone(
            "s1", "Test", "z1", "Zone", sample_status() if status is None else status
        )

    def test_missing_features_are_optional(self):
        zone = self.zone({"features": {}})
        self.assertIsNone(zone.current_temperature)
        self.assertFalse(zone.supports_humidifier)
        self.assertEqual(zone.fan_max, 0)

    def test_humidity_sensor_does_not_imply_control(self):
        zone = self.zone()
        del zone.humidity["capabilities"]
        self.assertEqual(zone.current_humidity, 38.5)
        self.assertFalse(zone.supports_humidifier)

    def test_humidifier_requires_advertised_mode_and_valid_limits(self):
        for change in (
            {"modes": ["Off"]},
            {"setpoint": {"min": 60, "max": 20, "precision": 1}},
            {"setpoint": {"min": 20, "max": 60, "precision": 0}},
        ):
            zone = self.zone()
            zone.humidity_capabilities.update(change)
            self.assertFalse(zone.supports_humidifier)

    def test_legacy_temperature_fields(self):
        zone = self.zone(
            {
                "features": {
                    "ambientTemperature": {
                        "current": 20,
                        "hvacMode": "Cool",
                        "hvacStatus": "Off",
                        "setpoint": {"value": 21, "minValue": 12, "maxValue": 29},
                    }
                }
            }
        )
        self.assertEqual(
            (zone.current_temperature, zone.mode, zone.target_temperature), (20, "Cool", 21)
        )
        self.assertEqual(zone.temperature_capabilities["min"], 12)

    def test_disconnected_system_is_unavailable(self):
        zone = self.zone()
        zone.connection_status = "Disconnected"
        self.assertFalse(zone.online)
        zone.connection_status = "Unknown"
        self.assertFalse(zone.online)

    def test_numbers_exclude_boolean_and_nonfinite(self):
        for value in (True, "40", None, float("inf"), float("nan")):
            self.assertIsNone(models.number(value))

    def test_magic_links_are_parsed_without_following_them(self):
        self.assertEqual(
            api.token_from_link(
                "jetsonhome://magic-link?email=test%40example.invalid&token=abc%2B123",
                "test@example.invalid",
            ),
            "abc+123",
        )
        self.assertEqual(api.token_from_link("  raw-token  ", "test@example.invalid"), "raw-token")
        for link in (
            "",
            "https://example.invalid/?token=x&email=other@example.invalid",
            "https://example.invalid/?other=x",
        ):
            with self.assertRaises(ValueError):
                api.token_from_link(link, "test@example.invalid")

    def test_tokens_do_not_appear_in_repr(self):
        tokens = api.Tokens("access-secret", "refresh-secret", 0)
        self.assertNotIn("secret", repr(tokens))

    def test_registry_plan_keeps_hubs_hardware_and_zone_aggregates_distinct(self):
        zone = self.zone()
        system = models.System("s1", "Test", [{"id": "b1", "type": "Arctic"}], sample_equipment())
        devices = models.build_devices(models.Snapshot({"s1": system}, {zone.key: zone}))
        self.assertTrue(devices["system:s1"].is_service)
        self.assertTrue(devices["s1:z1"].is_service)
        self.assertEqual(devices["s1:z1"].via_identifier, "system:s1")
        self.assertEqual(devices["board:s1:b1"].via_identifier, "system:s1")
        self.assertEqual(devices["equipment:s1:aq1"].via_identifier, "board:s1:b1")
        self.assertEqual(devices["equipment:s1:em1"].via_identifier, "board:s1:b1")
        self.assertFalse(devices["equipment:s1:aq1"].is_service)
        self.assertEqual(devices["equipment:s1:em1"].serial_number, "invented-monitor-serial")
        self.assertIsNone(devices["equipment:s1:aq1"].manufacturer)

    def test_duplicate_equipment_ids_in_different_systems_do_not_merge(self):
        first = models.System("s1", "First", [{"id": "b1"}], sample_equipment())
        second = models.System("s2", "Second", [{"id": "b1"}], sample_equipment())
        devices = models.build_devices(models.Snapshot({"s1": first, "s2": second}))
        self.assertEqual(devices["equipment:s1:em1"].via_identifier, "board:s1:b1")
        self.assertEqual(devices["equipment:s2:em1"].via_identifier, "board:s2:b1")
        self.assertNotEqual(
            devices["equipment:s1:em1"].identifier, devices["equipment:s2:em1"].identifier
        )

    def test_parent_equipment_is_fallback_when_board_is_unknown(self):
        equipment = sample_equipment()
        equipment[1]["boardId"] = "missing-board"
        system = models.System("s1", "Test", [{"id": "b1"}], equipment)
        devices = models.build_devices(models.Snapshot({"s1": system}))
        self.assertEqual(devices["equipment:s1:aq1"].via_identifier, "equipment:s1:hp1")

    def test_bad_parent_cycles_are_not_sent_to_device_registry(self):
        equipment = [
            {"id": "e1", "parentEquipmentId": "e2"},
            {"id": "e2", "parentEquipmentId": "e1"},
            {"id": "e3", "parentEquipmentId": "e3"},
        ]
        devices = models.build_devices(
            models.Snapshot({"s1": models.System("s1", "Test", equipment=equipment)})
        )
        for key in devices:
            seen = set()
            while key is not None:
                self.assertNotIn(key, seen)
                seen.add(key)
                key = devices[key].via_identifier

    def test_null_air_reading_stays_unknown_but_zero_is_valid(self):
        zone = self.zone()
        zone.air_quality = sample_air_quality()
        zone.air_quality["current"]["co2"]["value"] = None
        zone.air_quality["current"]["pm25"]["value"] = 0
        self.assertIsNone(zone.pollutant("co2"))
        self.assertEqual(zone.pollutant("pm25"), 0)
        for invalid in (-1, 60001, True, float("inf")):
            zone.air_quality["current"]["tvoc"]["value"] = invalid
            self.assertIsNone(zone.pollutant("tvoc"))

    def test_zone_membership_can_use_explicit_equipment_ids(self):
        zone = self.zone()
        zone.equipment_ids = ["aq1"]
        equipment = sample_equipment()
        equipment[1]["zoneIds"] = []
        system = models.System("s1", "Test", equipment=equipment)
        self.assertIn("aq1", [item["id"] for item in models.equipment_for_zone(system, zone)])

    def test_peripheral_without_own_zones_can_follow_its_reported_parent(self):
        zone = self.zone()
        equipment = sample_equipment()
        equipment[1]["zoneIds"] = []
        system = models.System("s1", "Test", equipment=equipment)
        self.assertIn("aq1", [item["id"] for item in models.equipment_for_zone(system, zone)])
        equipment[1]["zoneIds"] = ["other-zone"]
        self.assertNotIn("aq1", [item["id"] for item in models.equipment_for_zone(system, zone)])

    def test_zone_association_handles_parent_cycles(self):
        zone = self.zone()
        equipment = [{"id": "a", "parentEquipmentId": "b"}, {"id": "b", "parentEquipmentId": "a"}]
        system = models.System("s1", "Test", equipment=equipment)
        self.assertEqual(models.equipment_for_zone(system, zone), [])

    def test_recovered_schema_references_and_critical_enums(self):
        document = json.loads(
            (Path(__file__).parents[1] / "docs" / "recovered-schemas.json").read_text(
                encoding="utf-8"
            )
        )
        definitions = document["$defs"]
        self.assertFalse(document["x-failures"])
        self.assertEqual(
            definitions["HvacMode"]["enum"], ["Off", "Heat", "Cool", "Auto", "FanOnly"]
        )
        self.assertEqual(definitions["HumidityMode"]["enum"], ["Off", "Humidify"])
        self.assertTrue(all(not name[0].isdigit() for name in definitions))
        todo = [document]
        while todo:
            value = todo.pop()
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertIn(value["$ref"].split("/")[-1], definitions)
                self.assertNotIn("x-unrecovered-constructor", value)
                self.assertNotIn("x-unrecovered-methods", value)
                todo.extend(value.values())
            elif isinstance(value, list):
                todo.extend(value)


if __name__ == "__main__":
    unittest.main()
