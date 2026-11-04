"""Base entity for a Jetson zone."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JetsonCoordinator
from .models import Zone


class JetsonEntity(CoordinatorEntity[JetsonCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: JetsonCoordinator, zone: Zone) -> None:
        super().__init__(coordinator)
        self.zone_key = zone.key
        self._initial_zone = zone
        self._initial_device_info = coordinator.device_infos[zone.key]

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_infos.get(self.zone_key, self._initial_device_info)

    @property
    def zone(self) -> Zone:
        return self.coordinator.data.zones.get(self.zone_key, self._initial_zone)

    @property
    def name(self) -> str:
        # Zone names distinguish multiple thermostats/readings on one system device.
        return f"{self.zone.name} {self._attr_name}" if self._attr_name else self.zone.name

    @property
    def available(self) -> bool:
        return (
            super().available and self.zone_key in self.coordinator.data.zones and self.zone.online
        )
