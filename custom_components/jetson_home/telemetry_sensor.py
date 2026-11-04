"""Zone freshness and observed per-unit operation diagnostics."""

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import JetsonCoordinator
from .energy import timestamp
from .entity import JetsonEntity
from .models import equipment_identifier, mapping, optional_text
from .telemetry import OPERATION_FIELDS, operation_value


class JetsonZoneTelemetrySensor(JetsonEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, zone, kind: str) -> None:
        super().__init__(coordinator, zone)
        self.kind = kind
        self._attr_unique_id = f"{zone.key}:{kind}"
        self._attr_name = (
            "Telemetry status" if kind == "telemetry_status" else "Last device reading"
        )
        if kind == "observed_at":
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.zone_key in self.coordinator.data.zones
            and getattr(self.zone, self.kind) is not None
        )

    @property
    def native_value(self) -> str | datetime | None:
        return (
            self.zone.telemetry_status
            if self.kind == "telemetry_status"
            else timestamp(self.zone.observed_at)
        )


class JetsonHeatPumpSensor(CoordinatorEntity[JetsonCoordinator], SensorEntity):
    _attr_has_entity_name = True
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

    @property
    def status(self) -> dict:
        system = self.coordinator.data.systems.get(self.system_id)
        return system.heatpump_status.get(self.equipment_id, {}) if system else {}

    @property
    def name(self) -> str:
        system = self.coordinator.data.systems.get(self.system_id)
        equipment = (
            next((item for item in system.equipment if item["id"] == self.equipment_id), {})
            if system
            else {}
        )
        return f"{optional_text(equipment.get('name')) or 'Heat pump'} {OPERATION_FIELDS[self.field][0]}"

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
        return operation_value(self.status, self.field)
