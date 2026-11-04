"""Base entity for a Jetson zone."""

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JetsonCoordinator
from .models import Zone


class JetsonNamedEntity(CoordinatorEntity[JetsonCoordinator]):
    """Use HA's translated names while retaining user-supplied zone/load names."""

    _attr_has_entity_name = True

    def _set_name_placeholders(self, **values: str) -> None:
        if getattr(self, "_attr_translation_placeholders", None) != values:
            self._attr_translation_placeholders = values
            # HA caches translated names. Explicit configuration refreshes may
            # change the proper name used in the translation's placeholder.
            self.__dict__.pop("name", None)
            self.__dict__.pop("translation_placeholders", None)


class JetsonEntity(JetsonNamedEntity):
    def __init__(self, coordinator: JetsonCoordinator, zone: Zone) -> None:
        super().__init__(coordinator)
        self.zone_key = zone.key
        self._initial_zone = zone
        self._initial_device_info = coordinator.device_infos[zone.key]
        self._set_name_placeholders(zone=zone.name)

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_infos.get(self.zone_key, self._initial_device_info)

    @property
    def zone(self) -> Zone:
        return self.coordinator.data.zones.get(self.zone_key, self._initial_zone)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._set_name_placeholders(zone=self.zone.name)
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        return (
            super().available and self.zone_key in self.coordinator.data.zones and self.zone.online
        )
