"""Named equipment connectivity diagnostics on the containing system device."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JetsonCoordinator
from .models import equipment_identifier, optional_text


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for system in coordinator.data.systems.values():
            for item in system.equipment:
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


class JetsonConnectivity(CoordinatorEntity[JetsonCoordinator], BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Connection"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: JetsonCoordinator, system_id: str, equipment_id: str) -> None:
        super().__init__(coordinator)
        self.system_id = system_id
        self.equipment_id = equipment_id
        self.key = equipment_identifier(system_id, equipment_id)
        self._attr_unique_id = f"{self.key}:connectivity"
        self._initial_device_info = coordinator.device_infos[self.key]

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

    @property
    def name(self) -> str:
        equipment = self.equipment or {}
        label = (
            optional_text(equipment.get("name"))
            or optional_text(equipment.get("type"))
            or "Equipment"
        )
        return f"{label} connection"

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
