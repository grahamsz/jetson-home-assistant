"""Named equipment connectivity diagnostics on the containing system device."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import JetsonCoordinator
from .entity import JetsonEntity, JetsonNamedEntity
from .models import equipment_identifier, mapping, optional_text


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for key, zone in coordinator.data.zones.items():
            if (key, "humidifying") not in known and zone.supports_humidifier:
                known.add((key, "humidifying"))
                entities.append(JetsonHumidifying(coordinator, zone))
            if (key, "connection") not in known and "connectionStatus" in mapping(
                zone.status.get("connectivity")
            ):
                known.add((key, "connection"))
                entities.append(JetsonZoneConnectivity(coordinator, zone))
            if (key, "schedule") not in known and isinstance(zone.status.get("schedule"), dict):
                known.add((key, "schedule"))
                entities.append(JetsonSchedulePaused(coordinator, zone))
        for system in coordinator.data.systems.values():
            for item in system.equipment:
                # A relay accessory does not necessarily report connectivity.
                if item.get("type") == "Humidifier" and item.get("connectionStatus") not in (
                    "Connected",
                    "Disconnected",
                ):
                    continue
                key = equipment_identifier(system.system_id, item["id"])
                if key not in known and item.get("connectionStatus") in (
                    "Unknown",
                    "Connected",
                    "Disconnected",
                ):
                    known.add(key)
                    entities.append(JetsonConnectivity(coordinator, system.system_id, item["id"]))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonHumidifying(JetsonEntity, BinarySensorEntity):
    """Actual humidification demand, suitable for Recorder/history_stats."""

    _attr_translation_key = "humidifying"
    _attr_icon = "mdi:air-humidifier"

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:humidifying"

    @property
    def available(self) -> bool:
        return super().available and self.zone.supports_humidifier

    @property
    def is_on(self) -> bool | None:
        status = self.zone.humidity.get("status")
        return status == "Humidifying" if status in ("Off", "Humidifying") else None


class JetsonSchedulePaused(JetsonEntity, BinarySensorEntity):
    _attr_translation_key = "schedule_paused"
    _attr_icon = "mdi:calendar-pause"

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:schedule_paused"

    @property
    def available(self) -> bool:
        return super().available and bool(self.zone.schedule)

    @property
    def is_on(self) -> bool | None:
        return self.zone.schedule_paused

    @property
    def extra_state_attributes(self) -> dict:
        kind = optional_text(self.zone.schedule.get("kind"))
        return {
            "schedule_id": optional_text(self.zone.schedule.get("id")),
            "schedule_kind": kind.lower() if kind else None,
        }


class JetsonZoneConnectivity(JetsonEntity, BinarySensorEntity):
    _attr_translation_key = "zone_connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:connectivity"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and self.zone_key in self.coordinator.data.zones

    @property
    def is_on(self) -> bool | None:
        status = mapping(self.zone.status.get("connectivity")).get("connectionStatus")
        return status == "Connected" if status in ("Connected", "Disconnected") else None

    @property
    def extra_state_attributes(self) -> dict:
        issues = self.zone.connectivity_issues
        return {"issues": issues, "issue_count": len(issues) if issues is not None else None}


class JetsonConnectivity(JetsonNamedEntity, BinarySensorEntity):
    _attr_translation_key = "equipment_connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: JetsonCoordinator, system_id: str, equipment_id: str) -> None:
        super().__init__(coordinator)
        self.system_id = system_id
        self.equipment_id = equipment_id
        self.key = equipment_identifier(system_id, equipment_id)
        self._attr_unique_id = f"{self.key}:connectivity"
        self._initial_device_info = coordinator.device_infos[self.key]
        self._update_equipment_name()

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_infos.get(self.key, self._initial_device_info)

    @property
    def equipment(self) -> dict | None:
        system = self.coordinator.data.systems.get(self.system_id)
        return (
            next((item for item in system.equipment if item["id"] == self.equipment_id), None)
            if system
            else None
        )

    def _update_equipment_name(self) -> None:
        equipment = self.equipment or {}
        label = (
            optional_text(equipment.get("name"))
            or optional_text(equipment.get("type"))
            or self.equipment_id
        )
        self._set_name_placeholders(equipment=label)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_equipment_name()
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        system = self.coordinator.data.systems.get(self.system_id)
        return (
            super().available
            and system is not None
            and system.equipment_error is None
            and self.equipment is not None
        )

    @property
    def is_on(self) -> bool | None:
        status = (self.equipment or {}).get("connectionStatus")
        return status == "Connected" if status in ("Connected", "Disconnected") else None
