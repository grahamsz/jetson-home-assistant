"""Resume the currently reported paused schedule, without creating a new one."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import JetsonEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for key, zone in coordinator.data.zones.items():
            if key not in known and zone.schedule_target is not None:
                known.add(key)
                entities.append(JetsonResumeSchedule(coordinator, zone))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonResumeSchedule(JetsonEntity, ButtonEntity):
    _attr_translation_key = "resume_schedule"
    _attr_icon = "mdi:calendar-play"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:resume_schedule"

    @property
    def available(self) -> bool:
        return super().available and self.zone.can_resume_schedule

    async def async_press(self) -> None:
        await self.coordinator.command("resume_schedule", self.zone, None)
