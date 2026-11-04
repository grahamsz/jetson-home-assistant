"""Views of schemas recovered from Jetson Home 1.2.8; no HA dependency."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any

AIR_QUALITY_LEVELS = ("excellent", "good", "fair", "poor", "unhealthy")
AIR_QUALITY_LIMITS = {"co2": 5000, "pm25": 1000, "tvoc": 60000}
HVAC_MODE_STATES = {
    "Off": "off",
    "Heat": "heat",
    "Cool": "cool",
    "Auto": "heat_cool",
    "FanOnly": "fan_only",
}
HVAC_ACTIVITY_STATES = {
    "Cooling": "cooling",
    "Heating": "heating",
    "Circulating": "fan",
    "Dehumidifying": "drying",
}
STATUS_SENSOR_OPTIONS = {
    "hvac_mode": tuple(HVAC_MODE_STATES.values()),
    "fan_mode": ("auto", "1", "2", "3"),
    "hvac_activity": ("off", "idle", *HVAC_ACTIVITY_STATES.values()),
}


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value) if isfinite(value) else None
    return None


def optional_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


@dataclass
class Zone:
    """A zone with its containing system and current feature state."""

    system_id: str
    system_name: str
    zone_id: str
    name: str
    status: dict[str, Any]
    connection_status: str | None = None
    equipment_ids: list[str] = field(default_factory=list)
    air_quality: dict[str, Any] | None = None

    @property
    def key(self) -> str:
        return f"{self.system_id}:{self.zone_id}"

    @property
    def features(self) -> dict[str, Any]:
        return mapping(self.status.get("features"))

    @property
    def ambient(self) -> dict[str, Any]:
        return mapping(self.features.get("ambientTemperature"))

    @property
    def circulation(self) -> dict[str, Any]:
        return mapping(self.features.get("circulation"))

    @property
    def humidity(self) -> dict[str, Any]:
        return mapping(self.features.get("humidity"))

    @property
    def online(self) -> bool:
        # Missing health is allowed by SystemOverview. Unknown health is not online.
        return self.connection_status in (None, "Connected")

    @property
    def mode(self) -> str | None:
        return mapping(self.ambient.get("settings")).get(
            "mode", self.ambient.get("mode", self.ambient.get("hvacMode"))
        )

    @property
    def action(self) -> str | None:
        return self.ambient.get("status", self.ambient.get("hvacStatus"))

    @property
    def hvac_mode_state(self) -> str | None:
        return HVAC_MODE_STATES.get(self.mode)

    @property
    def hvac_activity_state(self) -> str | None:
        if self.action == "Off":
            if self.hvac_mode_state == "off":
                return "off"
            return "idle" if self.hvac_mode_state is not None else None
        return HVAC_ACTIVITY_STATES.get(self.action)

    @property
    def current_temperature(self) -> float | None:
        return number(self.ambient.get("currentTemperature", self.ambient.get("current")))

    @property
    def setpoint(self) -> dict[str, Any]:
        return mapping(
            mapping(self.ambient.get("settings")).get("setpoint", self.ambient.get("setpoint"))
        )

    @property
    def target_temperature(self) -> float | None:
        return number(self.setpoint.get("value"))

    @property
    def temperature_capabilities(self) -> dict[str, Any]:
        result = mapping(
            mapping(self.ambient.get("capabilities")).get("setpoint", self.ambient.get("setpoint"))
        )
        return {
            **result,
            "min": result.get("min", result.get("minValue")),
            "max": result.get("max", result.get("maxValue")),
        }

    @property
    def current_humidity(self) -> float | None:
        return number(self.humidity.get("currentRelativeHumidity"))

    @property
    def humidity_capabilities(self) -> dict[str, Any]:
        return mapping(self.humidity.get("capabilities"))

    @property
    def humidity_limits(self) -> dict[str, Any]:
        return mapping(self.humidity_capabilities.get("setpoint"))

    @property
    def supports_humidifier(self) -> bool:
        modes = self.humidity_capabilities.get("modes")
        low, high, step = (
            number(self.humidity_limits.get(key)) for key in ("min", "max", "precision")
        )
        return (
            isinstance(modes, list)
            and "Humidify" in modes
            and low is not None
            and high is not None
            and step is not None
            and 0 <= low <= high <= 100
            and step > 0
        )

    @property
    def fan_max(self) -> int:
        value = number(
            mapping(mapping(self.circulation.get("capabilities")).get("fanSpeedSetting")).get("max")
        )
        # This app's FanSpeedSetting union is Auto, 1, 2, 3.
        return min(3, max(0, int(value))) if value is not None else 0

    @property
    def fan_setting(self) -> str | int | None:
        return mapping(self.circulation.get("settings")).get(
            "fanSpeed", mapping(self.circulation.get("fanSpeedSetting")).get("value")
        )

    @property
    def fan_mode_state(self) -> str | None:
        value = self.fan_setting
        if value == "Auto":
            return "auto"
        speed = number(value)
        return str(int(speed)) if speed in (1, 2, 3) else None

    @property
    def air_quality_access(self) -> str | None:
        return mapping(self.air_quality).get("access")

    @property
    def air_quality_missing_entitlement(self) -> str | None:
        if (
            self.air_quality_access == "limited"
            and mapping(self.air_quality).get("missingEntitlement") == "jetson_care"
        ):
            return "jetson_care"
        return None

    @property
    def air_quality_overall(self) -> str | None:
        value = mapping(mapping(self.air_quality).get("current")).get("overall")
        return value if value in AIR_QUALITY_LEVELS else None

    def pollutant(self, kind: str) -> float | None:
        if self.air_quality_access != "full" or kind not in AIR_QUALITY_LIMITS:
            return None
        current = mapping(mapping(self.air_quality).get("current"))
        value = number(mapping(current.get(kind)).get("value"))
        return value if value is not None and 0 <= value <= AIR_QUALITY_LIMITS[kind] else None


@dataclass
class System:
    """API system and its reported hardware inventory."""

    system_id: str
    name: str
    boards: list[dict[str, Any]] = field(default_factory=list)
    equipment: list[dict[str, Any]] = field(default_factory=list)
    equipment_error: str | None = None
    boards_error: str | None = None


@dataclass
class Snapshot:
    """Current zone measurements and system-wide hardware discovery."""

    systems: dict[str, System] = field(default_factory=dict)
    zones: dict[str, Zone] = field(default_factory=dict)
    air_quality_errors: dict[str, str] = field(default_factory=dict)
    system_health_error: str | None = None


@dataclass(frozen=True)
class Device:
    """A registry device plan, independent of Home Assistant imports."""

    identifier: str
    name: str
    via_identifier: str | None = None
    model: str | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    is_service: bool = False


def system_identifier(system_id: str) -> str:
    return f"system:{system_id}"


def board_identifier(system_id: str, board_id: str) -> str:
    return f"board:{system_id}:{board_id}"


def equipment_identifier(system_id: str, equipment_id: str) -> str:
    return f"equipment:{system_id}:{equipment_id}"


def equipment_for_zone(system: System, zone: Zone) -> list[dict[str, Any]]:
    """Use reported zone memberships; never assign an unrelated monitor."""
    equipment = {item["id"]: item for item in system.equipment}

    def associated(item: dict, seen: set[str]) -> bool:
        if item["id"] in seen:
            return False
        seen = seen | {item["id"]}
        zone_ids = item.get("zoneIds") if isinstance(item.get("zoneIds"), list) else []
        if item["id"] in zone.equipment_ids or zone.zone_id in zone_ids:
            return True
        if zone_ids:
            return False
        parent_id = item.get("parentEquipmentId")
        parent = equipment.get(parent_id) if isinstance(parent_id, str) else None
        return associated(parent, seen) if parent else False

    return [item for item in system.equipment if associated(item, set())]


def build_devices(snapshot: Snapshot) -> dict[str, Device]:
    """Present one aggregate device per system, regardless of its equipment count."""
    return {
        system_identifier(system.system_id): Device(
            system_identifier(system.system_id),
            system.name,
            model="Jetson Home",
            manufacturer="Jetson",
            is_service=True,
        )
        for system in snapshot.systems.values()
    }


def device_aliases(snapshot: Snapshot) -> dict[str, str]:
    """Resolve stable zone/equipment keys to their containing system device."""
    aliases = {}
    for system in snapshot.systems.values():
        root = system_identifier(system.system_id)
        aliases[root] = root
        for board in system.boards:
            aliases[board_identifier(system.system_id, board["id"])] = root
        for item in system.equipment:
            aliases[equipment_identifier(system.system_id, item["id"])] = root
    for zone in snapshot.zones.values():
        aliases[zone.key] = system_identifier(zone.system_id)
    return aliases


def system_for_legacy_identifier(snapshot: Snapshot, identifier: str) -> str | None:
    """Also recognize old records for equipment/zones no longer in inventory."""
    if current := device_aliases(snapshot).get(identifier):
        return current
    matches = [
        system_identifier(system_id)
        for system_id in snapshot.systems
        if identifier.startswith(
            (f"board:{system_id}:", f"equipment:{system_id}:", f"{system_id}:")
        )
    ]
    return matches[0] if len(matches) == 1 else None
