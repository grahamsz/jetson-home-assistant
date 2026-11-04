"""Temperature, HVAC mode, and fan speed for each thermostat zone."""

from typing import Any, ClassVar

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import JetsonEntity
from .errors import user_error
from .models import number

MODES = {
    HVACMode.OFF: "Off",
    HVACMode.HEAT: "Heat",
    HVACMode.COOL: "Cool",
    HVACMode.HEAT_COOL: "Auto",
    HVACMode.FAN_ONLY: "FanOnly",
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for key, zone in coordinator.data.zones.items():
            if key not in known and zone.ambient:
                known.add(key)
                entities.append(JetsonClimate(coordinator, zone))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonClimate(JetsonEntity, ClimateEntity):
    _attr_translation_key = "thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes: ClassVar[list[HVACMode]] = list(MODES)

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:climate"

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_OFF
        if self.zone.circulation and self.zone.fan_max:
            features |= ClimateEntityFeature.FAN_MODE
        return features

    @property
    def available(self) -> bool:
        return super().available and bool(self.zone.ambient)

    @property
    def current_temperature(self) -> float | None:
        return self.zone.current_temperature

    @property
    def target_temperature(self) -> float | None:
        return self.zone.target_temperature

    @property
    def current_humidity(self) -> float | None:
        return self.zone.current_humidity

    @property
    def min_temp(self) -> float:
        value = number(self.zone.temperature_capabilities.get("min"))
        return value if value is not None else super().min_temp

    @property
    def max_temp(self) -> float:
        value = number(self.zone.temperature_capabilities.get("max"))
        return value if value is not None else super().max_temp

    @property
    def target_temperature_step(self) -> float:
        precision = self.zone.temperature_capabilities.get("precision", {})
        value = number(precision.get("celsius")) if isinstance(precision, dict) else None
        return value if value is not None and value > 0 else 0.5

    @property
    def hvac_mode(self) -> HVACMode | None:
        value = self.zone.hvac_mode_state
        return HVACMode(value) if value is not None else None

    @property
    def hvac_action(self) -> HVACAction | None:
        value = self.zone.hvac_activity_state
        return HVACAction(value) if value is not None else None

    @property
    def fan_modes(self) -> list[str]:
        return ["auto", *(str(speed) for speed in range(1, self.zone.fan_max + 1))]

    @property
    def fan_mode(self) -> str | None:
        return self.zone.fan_mode_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "jetson_mode": self.zone.mode,
            "jetson_status": self.zone.action,
            "heat_target_celsius": self.zone.setpoint.get("heatValue"),
            "cool_target_celsius": self.zone.setpoint.get("coolValue"),
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode not in MODES:
            raise user_error("unsupported_hvac_mode")
        await self.coordinator.command("set_mode", self.zone, MODES[hvac_mode])

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if "target_temp_low" in kwargs or "target_temp_high" in kwargs:
            raise user_error("unsupported_split_targets")
        value = number(kwargs.get(ATTR_TEMPERATURE))
        if value is None or not self.min_temp <= value <= self.max_temp:
            raise user_error("temperature_out_of_range")
        step = self.target_temperature_step
        # HA converts Fahrenheit requests to Celsius, often producing fractions.
        value = round(round(value / step) * step, 6)
        if not self.min_temp <= value <= self.max_temp:
            raise user_error("rounded_temperature_out_of_range")
        if (mode := kwargs.get("hvac_mode")) is not None:
            await self.async_set_hvac_mode(mode)
        await self.coordinator.command("set_temperature", self.zone, value)

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        if not self.zone.circulation or fan_mode not in self.fan_modes:
            raise user_error("unsupported_fan_speed")
        speed = "Auto" if fan_mode == "auto" else int(fan_mode)
        await self.coordinator.command("set_fan_speed", self.zone, speed)
