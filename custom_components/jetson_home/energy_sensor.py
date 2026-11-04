"""Main, per-load, and heat-strip power on the shared system device."""

from datetime import datetime
from urllib.parse import quote

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .coordinator import JetsonCoordinator
from .energy import EnergyView
from .entity import JetsonNamedEntity
from .models import optional_text, system_identifier


class JetsonEnergySensor(JetsonNamedEntity, SensorEntity):
    def __init__(
        self,
        coordinator: JetsonCoordinator,
        system_id: str,
        load_key: str | None,
        *,
        energy: bool,
        heat_strips: bool = False,
    ) -> None:
        super().__init__(coordinator)
        self.system_id = system_id
        self.load_key = load_key
        self.is_energy = energy
        self.is_heat_strips = heat_strips
        self._system_key = system_identifier(system_id)
        self._initial_device_info = coordinator.device_infos[self._system_key]
        meter = f":load:{quote(load_key, safe='')}" if load_key is not None else ""
        suffix = "heat_strips_power" if heat_strips else "energy_today" if energy else "power"
        self._attr_unique_id = f"{self._system_key}{meter}:{suffix}"
        self._attr_translation_key = (
            "heat_strips_power"
            if heat_strips
            else f"{'main' if load_key is None else 'load'}_{suffix}"
        )
        self._update_load_name()
        self._attr_device_class = SensorDeviceClass.ENERGY if energy else SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = (
            UnitOfEnergy.KILO_WATT_HOUR if energy else UnitOfPower.WATT
        )
        # The API reports a calendar-day total. Explicit resets preserve corrections
        # within the day instead of treating every downward correction as a reset.
        self._attr_state_class = SensorStateClass.TOTAL if energy else SensorStateClass.MEASUREMENT

    @property
    def view(self) -> EnergyView:
        system = self.coordinator.data.systems.get(self.system_id)
        return EnergyView(system.energy or {}) if system else EnergyView({})

    def _update_load_name(self) -> None:
        if self.load_key is None:
            self._set_name_placeholders()
            return
        descriptor = self.view.loads.get(self.load_key, {})
        label = optional_text(descriptor.get("name")) or getattr(
            self, "_attr_translation_placeholders", {}
        ).get("load", self.load_key)
        self._set_name_placeholders(load=label)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._update_load_name()
        super()._handle_coordinator_update()

    @property
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_infos.get(self._system_key, self._initial_device_info)

    @property
    def available(self) -> bool:
        view = self.view
        max_age = max(300, 2 * self.coordinator.update_interval.total_seconds())
        return (
            super().available
            and self.system_id not in self.coordinator.data.energy_errors
            and (self.load_key is None or self.load_key in view.loads)
            and (not self.is_heat_strips or self.load_key in view.heat_strip_loads)
            and view.is_fresh(dt_util.utcnow(), max_age, energy=self.is_energy)
            and (not self.is_energy or view.reset_time is not None)
        )

    @property
    def native_value(self) -> float | None:
        if self.is_heat_strips:
            return self.view.heat_strip_power(self.load_key)
        return self.view.value(self.load_key, energy=self.is_energy)

    @property
    def last_reset(self) -> datetime | None:
        return self.view.reset_time if self.is_energy else None

    @property
    def extra_state_attributes(self) -> dict:
        view = self.view
        updated = view.updated_at(self.is_energy)
        result = {"source_updated_at": updated.isoformat() if updated else None}
        if self.is_energy:
            result["source_timezone"] = view.data.get("timezone")
            result["period_date"] = view.data.get("today", {}).get("date")
        return result
