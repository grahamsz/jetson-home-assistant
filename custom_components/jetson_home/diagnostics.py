"""Allowlisted diagnostics without account, device IDs, addresses, or credentials."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .polling import CONNECTIVITY_INTERVAL


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = entry.runtime_data
    return {
        "integration_version": "0.3.0",
        "last_update_success": coordinator.last_update_success,
        "scan_interval_seconds": coordinator.update_interval.total_seconds(),
        "connectivity_interval_seconds": CONNECTIVITY_INTERVAL,
        "configuration_discovery": "startup_or_manual",
        "system_health_available": coordinator.data.system_health_error is None,
        "zones": [
            {
                "online": zone.online,
                "connection_status": zone.connection_status,
                "feature_names": sorted(zone.features),
                "mode": zone.mode,
                "action": zone.action,
                "temperature_capabilities": {
                    key: zone.temperature_capabilities.get(key)
                    for key in ("min", "max", "precision")
                },
                "has_split_targets": "heatValue" in zone.setpoint,
                "fan_max": zone.fan_max,
            }
            for zone in coordinator.data.zones.values()
        ],
        "systems": [
            {
                "board_count": len(system.boards),
                "equipment_count": len(system.equipment),
                "equipment_inventory_available": system.equipment_error is None,
                "board_inventory_available": system.boards_error is None,
                "air_quality_monitor_count": sum(
                    item.get("model") == "TEMCO-AQM" for item in system.equipment
                ),
                "energy_monitor_count": sum(
                    item.get("type") == "EnergyMonitor" for item in system.equipment
                ),
            }
            for system in coordinator.data.systems.values()
        ],
        "air_quality_error_count": len(coordinator.data.air_quality_errors),
        "energy_telemetry_implemented": False,
    }
