"""Explicit seasonal enable switch for the optional humidifier."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import JetsonEntity
from .errors import user_error
from .models import mapping


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for key, zone in coordinator.data.zones.items():
            if key not in known and zone.supports_humidifier:
                known.add(key)
                entities.append(JetsonHumidifierEnabled(coordinator, zone))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonHumidifierEnabled(JetsonEntity, SwitchEntity):
    _attr_translation_key = "humidifier_enabled"
    _attr_icon = "mdi:air-humidifier"

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:humidifier_enabled"

    @property
    def available(self) -> bool:
        return super().available and self.zone.supports_humidifier

    @property
    def is_on(self) -> bool | None:
        mode = mapping(self.zone.humidity.get("settings")).get("mode")
        return mode == "Humidify" if mode in ("Off", "Humidify") else None

    async def _set_enabled(self, enabled: bool) -> None:
        if not self.zone.supports_humidifier:
            raise user_error("unsupported_humidifier")
        await self.coordinator.command(
            "set_humidity_settings", self.zone, {"mode": "Humidify" if enabled else "Off"}
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set_enabled(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set_enabled(False)
