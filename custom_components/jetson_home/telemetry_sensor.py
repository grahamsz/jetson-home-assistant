"""Zone freshness and observed per-unit operation diagnostics."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory

from .coordinator import JetsonCoordinator
from .energy import timestamp
from .entity import JetsonEntity, JetsonNamedEntity
from .models import equipment_identifier, mapping, optional_text
from .telemetry import SPEED_OPERATION_OPTIONS, operation_speed_state, operation_value


class JetsonZoneTelemetrySensor(JetsonEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "telemetry_status"
    _unrecorded_attributes = frozenset({"last_device_reading"})

    def __init__(self, coordinator, zone) -> None:
        super().__init__(coordinator, zone)
        self._attr_unique_id = f"{zone.key}:telemetry_status"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.zone_key in self.coordinator.data.zones
            and (self.zone.telemetry_status is not None or self.zone.observed_at is not None)
        )

    @property
    def native_value(self) -> str | None:
        return self.zone.telemetry_status

    @property
    def extra_state_attributes(self) -> dict:
        observed = timestamp(self.zone.observed_at)
        return {"last_device_reading": observed.isoformat() if observed else None}


class JetsonHeatPumpSensor(JetsonNamedEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: JetsonCoordinator, system_id: str, equipment_id: str, field: str
    ) -> None:
        super().__init__(coordinator)
        self.system_id = system_id
        self.equipment_id = equipment_id
        self.field = field
        self.key = equipment_identifier(system_id, equipment_id)
        self._initial_device_info = coordinator.device_infos[self.key]
        self._attr_unique_id = f"{self.key}:operation:{field}"
        self._attr_translation_key = f"operation_{field.lower()}"
        self._update_equipment_name()
        if field in SPEED_OPERATION_OPTIONS:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(SPEED_OPERATION_OPTIONS[field])

    @property
    def status(self) -> dict:
        system = self.coordinator.data.systems.get(self.system_id)
        return system.heatpump_status.get(self.equipment_id, {}) if system else {}

    def _update_equipment_name(self) -> None:
        system = self.coordinator.data.systems.get(self.system_id)
        equipment = (
            next((item for item in system.equipment if item["id"] == self.equipment_id), {})
            if system
            else {}
        )
        label = optional_text(equipment.get("name")) or self.equipment_id
        self._set_name_placeholders(equipment=label)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_equipment_name()
        super()._handle_coordinator_update()

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_infos.get(self.key, self._initial_device_info)

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.key not in self.coordinator.data.heatpump_errors
            and self.field in mapping(self.status.get("operation"))
            and mapping(self.status.get("health")).get("connectionStatus") in (None, "Connected")
        )

    @property
    def native_value(self) -> str | float | None:
        if self.field in SPEED_OPERATION_OPTIONS:
            return operation_speed_state(self.status, self.field)
        return operation_value(self.status, self.field)

    @property
    def extra_state_attributes(self) -> dict | None:
        if self.field in SPEED_OPERATION_OPTIONS:
            return {"raw_value": mapping(self.status.get("operation")).get(self.field)}
        return None
