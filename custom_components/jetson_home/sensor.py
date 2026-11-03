"""Zone temperature, humidity, and optional air-quality sensors."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfDensity, UnitOfRatio, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import JetsonEntity
from .models import AIR_QUALITY_LEVELS

POLLUTANTS = {
    "co2": ("CO₂", SensorDeviceClass.CO2, UnitOfRatio.PARTS_PER_MILLION),
    "pm25": ("PM2.5", SensorDeviceClass.PM25, UnitOfDensity.MICROGRAMS_PER_CUBIC_METER),
    "tvoc": (
        "TVOC",
        SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS_PARTS,
        UnitOfRatio.PARTS_PER_BILLION,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data
    known = set()

    def discover() -> None:
        entities = []
        for key, zone in coordinator.data.zones.items():
            for kind, present in (
                ("temperature", bool(zone.ambient)),
                ("humidity", bool(zone.humidity)),
            ):
                if present and (key, kind) not in known:
                    known.add((key, kind))
                    entities.append(JetsonSensor(coordinator, zone, kind))
            if zone.air_quality is not None:
                kinds = ["overall"]
                if zone.air_quality_access == "full":
                    kinds.extend(POLLUTANTS)
                for kind in kinds:
                    if (key, f"air_quality:{kind}") not in known:
                        known.add((key, f"air_quality:{kind}"))
                        entities.append(JetsonAirQualitySensor(coordinator, zone, kind))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class JetsonSensor(JetsonEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, zone, kind: str) -> None:
        super().__init__(coordinator, zone)
        self.kind = kind
        self._attr_unique_id = f"{zone.key}:{kind}"
        self._attr_name = "Temperature" if kind == "temperature" else "Humidity"
        self._attr_device_class = (
            SensorDeviceClass.TEMPERATURE if kind == "temperature" else SensorDeviceClass.HUMIDITY
        )
        self._attr_native_unit_of_measurement = (
            UnitOfTemperature.CELSIUS if kind == "temperature" else PERCENTAGE
        )

    @property
    def available(self) -> bool:
        feature = self.zone.ambient if self.kind == "temperature" else self.zone.humidity
        return super().available and bool(feature)

    @property
    def native_value(self) -> float | None:
        return (
            self.zone.current_temperature
            if self.kind == "temperature"
            else self.zone.current_humidity
        )


class JetsonAirQualitySensor(JetsonEntity, SensorEntity):
    """An API zone aggregate, not an unverified reading from one physical sensor."""

    def __init__(self, coordinator, zone, kind: str) -> None:
        super().__init__(coordinator, zone)
        self.kind = kind
        self._attr_unique_id = f"{zone.key}:air_quality:{kind}"
        if kind == "overall":
            self._attr_name = "Air quality"
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(AIR_QUALITY_LEVELS)
        else:
            self._attr_name, self._attr_device_class, self._attr_native_unit_of_measurement = (
                POLLUTANTS[kind]
            )
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.zone.air_quality is not None
            and (self.kind == "overall" or self.zone.air_quality_access == "full")
        )

    @property
    def native_value(self) -> str | float | None:
        return (
            self.zone.air_quality_overall
            if self.kind == "overall"
            else self.zone.pollutant(self.kind)
        )
