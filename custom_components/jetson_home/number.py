"""Circulation minutes/hour without changing mode or fan speed implicitly."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
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
            if key not in known and (
                "fanOnDuration" in mapping(zone.circulation.get("settings"))
                or "fanOnDurationSetting" in zone.circulation
            ):
                known.add(key)
                entities.append(JetsonCirculationMinutes(coordinator, zone))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonCirculationMinutes(JetsonEntity, NumberEntity):
    _attr_translation_key = "circulation_minutes"
    _attr_icon = "mdi:fan-clock"
    _attr_native_min_value = 0
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:circulation_minutes"

    @property
    def available(self) -> bool:
        return super().available and self.zone.circulation_minutes is not None

    @property
    def native_value(self) -> int | None:
        return self.zone.circulation_minutes

    @property
    def extra_state_attributes(self) -> dict:
        mode = self.zone.circulation_mode
        return {"circulation_mode": mode.lower() if mode else None, "applies_in_mode": "circulate"}

    async def async_set_native_value(self, value: float) -> None:
        minutes = number(value)
        if minutes is None or not minutes.is_integer() or not 0 <= minutes <= 60:
            raise user_error("circulation_out_of_range")
        await self.coordinator.command("set_circulation_duration", self.zone, int(minutes))
