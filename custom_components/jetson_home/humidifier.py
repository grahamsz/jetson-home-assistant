"""Control the optional, separately installed whole-home humidifier."""

from typing import Any

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import JetsonEntity
from .errors import user_error
from .models import mapping, number


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
                entities.append(JetsonHumidifier(coordinator, zone))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonHumidifier(JetsonEntity, HumidifierEntity):
    _attr_translation_key = "humidifier"
    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:humidifier"

    @property
    def available(self) -> bool:
        return super().available and self.zone.supports_humidifier

    @property
    def is_on(self) -> bool | None:
        mode = mapping(self.zone.humidity.get("settings")).get("mode")
        return mode == "Humidify" if mode in ("Off", "Humidify") else None

    @property
    def action(self) -> HumidifierAction | None:
        status = self.zone.humidity.get("status")
        if status == "Humidifying":
            return HumidifierAction.HUMIDIFYING
        if status == "Off":
            return HumidifierAction.IDLE if self.is_on else HumidifierAction.OFF
        return None

    @property
    def current_humidity(self) -> float | None:
        return self.zone.current_humidity

    @property
    def target_humidity(self) -> float | None:
        return number(
            mapping(mapping(self.zone.humidity.get("settings")).get("setpoint")).get("value")
        )

    @property
    def min_humidity(self) -> float:
        value = number(self.zone.humidity_limits.get("min"))
        return value if value is not None else 0

    @property
    def max_humidity(self) -> float:
        value = number(self.zone.humidity_limits.get("max"))
        return value if value is not None else 100

    @property
    def target_humidity_step(self) -> float:
        value = number(self.zone.humidity_limits.get("precision"))
        return value if value is not None and value > 0 else 1

    async def _update(self, settings: dict) -> None:
        if not self.zone.supports_humidifier:
            raise user_error("unsupported_humidifier")
        await self.coordinator.command("set_humidity_settings", self.zone, settings)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._update({"mode": "Humidify"})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._update({"mode": "Off"})

    async def async_set_humidity(self, humidity: int) -> None:
        value = number(humidity)
        if value is None or not self.min_humidity <= value <= self.max_humidity:
            raise user_error("humidity_out_of_range")
        step = self.target_humidity_step
        value = round(self.min_humidity + round((value - self.min_humidity) / step) * step, 6)
        if not self.min_humidity <= value <= self.max_humidity:
            raise user_error("rounded_humidity_out_of_range")
        await self._update({"setpoint": {"value": value}})
