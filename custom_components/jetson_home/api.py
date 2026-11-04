"""Async client for the HTTPS API recovered from the Android bundle."""

import asyncio
import time
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, quote, urlsplit

import aiohttp

from .const import API_URL
from .models import (
    Snapshot,
    System,
    Zone,
    equipment_for_zone,
    equipment_identifier,
    heatpumps_for_system,
    mapping,
    number,
)


class JetsonError(Exception):
    """A network, protocol, or API failure without a response-body leak."""


class JetsonAuthError(JetsonError):
    """Credentials were rejected or have expired."""


class JetsonRateLimitError(JetsonError):
    """The API requested a pause."""


class JetsonHTTPError(JetsonError):
    """An HTTP failure, retaining the status without the response body."""

    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"Jetson returned HTTP {status}")


@dataclass(repr=False)
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: float
    user_id: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
            "user_id": self.user_id,
        }


def token_from_link(value: str, expected_email: str) -> str:
    """Read a pasted link locally. Never follow email links or send them elsewhere."""
    value = value.strip()
    if not value:
        raise ValueError("A token or magic link is required")
    if "://" not in value:
        return value
    query = parse_qs(urlsplit(value).query)
    token = query.get("token", [""])[0]
    email = query.get("email", [expected_email])[0]
    if not token or email.casefold() != expected_email.casefold():
        raise ValueError("Link is missing a token or belongs to a different email")
    return token


class JetsonClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        tokens: Tokens | None = None,
        *,
        install_id: str = "",
        on_tokens: Callable[[Tokens], None] | None = None,
        base_url: str = API_URL,
    ) -> None:
        self.session = session
        self.tokens = tokens
        self.install_id = install_id
        self.on_tokens = on_tokens
        self.base_url = base_url.rstrip("/")
        self._refresh_lock = asyncio.Lock()
        self._rate_limited_until = 0.0
        self._equipment_cache: dict[str, list[dict[str, Any]]] = {}
        self._boards_cache: dict[str, list[dict[str, Any]]] = {}

    def _save_tokens(self, data: dict[str, Any]) -> Tokens:
        access = data.get("accessToken")
        refresh = data.get("refreshToken")
        expires = number(data.get("expiresIn"))
        if (
            not isinstance(access, str)
            or not access
            or not isinstance(refresh, str)
            or not refresh
            or expires is None
            or expires <= 0
        ):
            raise JetsonError("Authentication response has an unexpected schema")
        old_id = self.tokens.user_id if self.tokens else ""
        user_id = data.get("userId", old_id)
        if not isinstance(user_id, str):
            raise JetsonError("Authentication response has an invalid user ID")
        self.tokens = Tokens(access, refresh, time.time() + expires, user_id)
        # Persist rotating refresh tokens immediately, before any subsequent call.
        if self.on_tokens:
            self.on_tokens(self.tokens)
        return self.tokens

    async def _http(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        *,
        access: str | None = None,
    ) -> dict[str, Any]:
        if time.monotonic() < self._rate_limited_until:
            raise JetsonRateLimitError("Jetson API is rate limited; waiting for the next poll")
        headers = {"Accept": "application/json", "app-version": "1.2.8"}
        if access:
            headers["Authorization"] = f"Bearer {access}"
        if self.install_id:
            headers["X-App-Install-ID"] = self.install_id
        try:
            async with self.session.request(
                method,
                self.base_url + path,
                json=body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
                allow_redirects=False,
            ) as response:
                if response.status == 401:
                    raise JetsonAuthError("Jetson rejected the authentication token")
                if response.status == 429:
                    try:
                        delay = float(response.headers.get("Retry-After", "60"))
                    except ValueError:
                        delay = 60.0
                    if not 1 <= delay <= 3600:
                        delay = 60.0
                    self._rate_limited_until = time.monotonic() + delay
                    raise JetsonRateLimitError("Jetson API rate limit reached")
                if not 200 <= response.status < 300:
                    raise JetsonHTTPError(response.status)
                if response.status == 204:
                    return {}
                try:
                    data = await response.json()
                except (ValueError, aiohttp.ContentTypeError) as err:
                    raise JetsonError("Jetson returned an invalid JSON response") from err
                if not isinstance(data, dict):
                    raise JetsonError("Jetson returned an unexpected response schema")
                return data
        except (aiohttp.ClientError, TimeoutError) as err:
            # Avoid logging the underlying request, URL parameters, or response body.
            raise JetsonError("Unable to communicate with Jetson") from err

    async def request_magic_link(self, email: str) -> None:
        await self._http(
            "POST",
            "/v1/auth/sign-in/magic-link",
            {"email": email, "appScheme": "jetsonhome"},
        )

    async def verify_magic_link(self, email: str, token: str) -> Tokens:
        data = await self._http(
            "POST", "/v1/auth/verify/magic-link", {"email": email, "token": token}
        )
        return self._save_tokens(data)

    async def _refresh(self, rejected_access: str | None = None) -> None:
        async with self._refresh_lock:
            if not self.tokens:
                raise JetsonAuthError("Sign in to Jetson Home first")
            if rejected_access is not None:
                if self.tokens.access_token != rejected_access:
                    return
            elif self.tokens.expires_at > time.time() + 30:
                return
            try:
                data = await self._http(
                    "POST",
                    "/v1/auth/refresh",
                    {"refreshToken": self.tokens.refresh_token},
                )
            except JetsonError as err:
                # Invalid refresh credentials can be returned as 400 or 403 as well.
                if isinstance(err, JetsonAuthError) or (
                    isinstance(err, JetsonHTTPError) and err.status in (400, 403)
                ):
                    raise JetsonAuthError("Jetson sign-in has expired") from err
                raise
            self._save_tokens(data)

    async def request(self, method: str, path: str, body: dict | None = None) -> dict[str, Any]:
        await self._refresh()
        assert self.tokens is not None
        access = self.tokens.access_token
        try:
            return await self._http(method, path, body, access=access)
        except JetsonAuthError:
            await self._refresh(rejected_access=access)
            assert self.tokens is not None
            return await self._http(method, path, body, access=self.tokens.access_token)

    async def get_zones(self, systems: list[dict] | None = None) -> dict[str, Zone]:
        """Discover all account systems/zones and retrieve each zone's status."""
        if systems is None:
            systems = self._items(await self.request("GET", "/v1/systems"), "systems")
        result = {}
        for system in systems:
            system_id = self._id(system)
            path = f"/v1/systems/{quote(system_id, safe='')}/zones"
            zones = self._items(await self.request("GET", path), "zones")
            for zone in zones:
                zone_id = self._id(zone)
                status = await self.request("GET", f"/v1/zones/{quote(zone_id, safe='')}/status")
                if not isinstance(status.get("features"), dict):
                    raise JetsonError("Zone status is missing its features object")
                item = Zone(
                    system_id,
                    str(system.get("name") or "Jetson"),
                    zone_id,
                    str(zone.get("name") or "Zone"),
                    status,
                    mapping(system.get("health")).get("connectionStatus"),
                    [value for value in zone.get("equipmentIds", []) if isinstance(value, str)]
                    if isinstance(zone.get("equipmentIds"), list)
                    else [],
                )
                result[item.key] = item
        return result

    async def _inventory_collection(
        self, system_id: str, kind: str
    ) -> tuple[list[dict], str | None]:
        cache = self._equipment_cache if kind == "equipment" else self._boards_cache
        try:
            data = await self.request("GET", f"/v1/systems/{quote(system_id, safe='')}/{kind}")
            items = self._items(data, kind)
            for item in items:
                self._id(item)
            cache[system_id] = items
            return items, None
        except (JetsonAuthError, JetsonRateLimitError):
            raise
        except JetsonError as err:
            # Keep prior topology during optional endpoint failures, and mark its
            # connectivity data unavailable rather than disrupting climate polling.
            return cache.get(system_id, []), str(err)

    async def get_snapshot(self) -> Snapshot:
        """Fetch configuration and confirmed zone/energy readings."""
        systems = self._items(await self.request("GET", "/v1/systems"), "systems")
        snapshot = Snapshot()
        for item in systems:
            system_id = self._id(item)
            system = System(system_id, str(item.get("name") or "Jetson"))
            system.boards, system.boards_error = await self._inventory_collection(
                system_id, "boards"
            )
            system.equipment, system.equipment_error = await self._inventory_collection(
                system_id, "equipment"
            )
            snapshot.systems[system_id] = system
        snapshot.zones = await self.get_zones(systems)
        await self._update_air_quality(snapshot)
        await self._update_energy(snapshot)
        await self._update_heatpumps(snapshot)
        return snapshot

    async def get_updates(
        self, previous: Snapshot, *, refresh_connectivity: bool = False
    ) -> Snapshot:
        """Refresh known zones without changing the discovered configuration."""
        snapshot = deepcopy(previous)
        snapshot.air_quality_errors.clear()
        if refresh_connectivity and snapshot.systems:
            await self._update_connectivity(snapshot)
        for zone in snapshot.zones.values():
            status = await self.request("GET", f"/v1/zones/{quote(zone.zone_id, safe='')}/status")
            if not isinstance(status.get("features"), dict):
                raise JetsonError("Zone status is missing its features object")
            zone.status = status
            zone.air_quality = None
        await self._update_air_quality(snapshot)
        await self._update_energy(snapshot)
        await self._update_heatpumps(snapshot)
        return snapshot

    async def _update_heatpumps(self, snapshot: Snapshot) -> None:
        snapshot.heatpump_errors.clear()
        for system in snapshot.systems.values():
            system.heatpump_status.clear()
            for item in heatpumps_for_system(system):
                try:
                    data = await self.request(
                        "GET", f"/v1/equipment/{quote(item['id'], safe='')}/heatpump/status"
                    )
                    if not isinstance(data.get("health"), dict) or (
                        "operation" in data and not isinstance(data["operation"], dict)
                    ):
                        raise JetsonError("Jetson returned an invalid heat-pump status response")
                    system.heatpump_status[item["id"]] = data
                except (JetsonAuthError, JetsonRateLimitError):
                    raise
                except JetsonError as err:
                    snapshot.heatpump_errors[equipment_identifier(system.system_id, item["id"])] = (
                        str(err)
                    )

    async def _update_energy(self, snapshot: Snapshot) -> None:
        snapshot.energy_errors.clear()
        for system in snapshot.systems.values():
            system.energy = None
            if not any(item.get("type") == "EnergyMonitor" for item in system.equipment):
                continue
            try:
                data = await self.request(
                    "GET", f"/v1/systems/{quote(system.system_id, safe='')}/energy/current"
                )
                live, today, loads = data.get("live"), data.get("today"), data.get("loads")
                if (
                    not isinstance(live, dict)
                    or not isinstance(today, dict)
                    or not isinstance(loads, list)
                    or not isinstance(live.get("loads"), dict)
                    or not isinstance(today.get("loads"), dict)
                ):
                    raise JetsonError("Jetson returned an invalid energy response")
                keys = []
                for item in loads:
                    if (
                        not isinstance(item, dict)
                        or not isinstance(item.get("key"), str)
                        or not item["key"]
                    ):
                        raise JetsonError("Jetson returned an invalid energy load identifier")
                    keys.append(item["key"])
                if len(set(keys)) != len(keys):
                    raise JetsonError("Jetson returned duplicate energy load identifiers")
                system.energy = data
            except (JetsonAuthError, JetsonRateLimitError):
                raise
            except JetsonError as err:
                snapshot.energy_errors[system.system_id] = str(err)

    async def _update_connectivity(self, snapshot: Snapshot) -> None:
        """Read liveness for configured objects, retaining their identity/metadata."""
        try:
            systems = self._items(await self.request("GET", "/v1/systems"), "systems")
            current = {self._id(item): item for item in systems}
        except (JetsonAuthError, JetsonRateLimitError):
            raise
        except JetsonError as err:
            # A health read failure is not proof of a disconnected system. Zone
            # measurements can still be read; command replies confirm reachability.
            for zone in snapshot.zones.values():
                zone.connection_status = None
            snapshot.system_health_error = str(err)
        else:
            snapshot.system_health_error = None
            for zone in snapshot.zones.values():
                zone.connection_status = (
                    mapping(current[zone.system_id].get("health")).get("connectionStatus")
                    if zone.system_id in current
                    else "Unknown"
                )
        for system in snapshot.systems.values():
            equipment, system.equipment_error = await self._inventory_collection(
                system.system_id, "equipment"
            )
            current_equipment = {item["id"]: item for item in equipment}
            for item in system.equipment:
                # Discovery is explicit: health checks must not add/remove equipment,
                # change memberships/names, or create new zones from returned data.
                item["connectionStatus"] = current_equipment.get(item["id"], {}).get(
                    "connectionStatus", "Unknown"
                )

    async def _update_air_quality(self, snapshot: Snapshot) -> None:
        for zone in snapshot.zones.values():
            system = snapshot.systems[zone.system_id]
            monitors = [
                item
                for item in equipment_for_zone(system, zone)
                if item.get("type") == "Sensor" and item.get("model") == "TEMCO-AQM"
            ]
            if not monitors:
                continue
            try:
                data = await self.request(
                    "GET", f"/v1/zones/{quote(zone.zone_id, safe='')}/airQuality"
                )
                if data.get("access") not in ("full", "limited") or not isinstance(
                    data.get("current"), dict
                ):
                    raise JetsonError("Jetson returned an invalid air-quality response")
                zone.air_quality = data
            except (JetsonAuthError, JetsonRateLimitError):
                raise
            except JetsonError as err:
                snapshot.air_quality_errors[zone.key] = str(err)

    @staticmethod
    def _items(data: dict, key: str) -> list[dict]:
        items = data.get(key)
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            raise JetsonError(f"Jetson response is missing its {key} list")
        return items

    @staticmethod
    def _id(item: dict) -> str:
        value = item.get("id")
        if not isinstance(value, str) or not value:
            raise JetsonError("Jetson returned a missing or invalid identifier")
        return value

    async def set_mode(self, zone_id: str, mode: str) -> None:
        if mode not in {"Off", "Heat", "Cool", "Auto", "FanOnly"}:
            raise ValueError("Unsupported HVAC mode")
        result = await self.request(
            "POST", f"/v1/zones/{quote(zone_id, safe='')}/hvac/mode", {"value": mode}
        )
        self._confirm_control(result)

    async def set_temperature(self, zone_id: str, temperature: float) -> None:
        if number(temperature) is None:
            raise ValueError("Temperature must be finite")
        result = await self.request(
            "POST",
            f"/v1/zones/{quote(zone_id, safe='')}/ambientTemperature/setpoint",
            {"value": temperature},
        )
        self._confirm_control(result)

    @staticmethod
    def _confirm_control(result: dict) -> None:
        if result.get("result") == "unreachable":
            raise JetsonError("Jetson could not reach the device")
        if result.get("result") != "ok":
            raise JetsonError("Jetson did not confirm the command")

    async def set_fan_speed(self, zone_id: str, speed: str | int) -> None:
        if type(speed) not in (str, int) or speed not in ("Auto", 1, 2, 3):
            raise ValueError("Unsupported fan speed")
        await self.request(
            "PATCH",
            f"/v1/zones/{quote(zone_id, safe='')}/circulation/settings",
            {"fanSpeed": speed},
        )

    async def set_humidity_settings(self, zone_id: str, settings: dict) -> None:
        if not settings or set(settings) - {"mode", "setpoint"}:
            raise ValueError("Invalid humidity settings")
        if "mode" in settings and settings["mode"] not in ("Off", "Humidify"):
            raise ValueError("Unsupported humidity mode")
        if "setpoint" in settings:
            setpoint = settings["setpoint"]
            if not isinstance(setpoint, dict) or set(setpoint) != {"value"}:
                raise ValueError("Humidity setpoint requires a value")
            value = number(setpoint["value"])
            if value is None or not 0 <= value <= 100:
                raise ValueError("Humidity must be a percentage")
        response = await self.request(
            "PATCH",
            f"/v1/zones/{quote(zone_id, safe='')}/humidity/settings",
            settings,
        )
        if (
            response.get("mode") not in ("Off", "Humidify")
            or number(mapping(response.get("setpoint")).get("value")) is None
        ):
            raise JetsonError("Jetson did not return confirmed humidity settings")
