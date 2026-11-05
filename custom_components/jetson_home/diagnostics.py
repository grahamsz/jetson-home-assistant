"""Allowlisted diagnostics without account, device IDs, addresses, or credentials."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .models import mapping, optional_text
from .polling import CONNECTIVITY_INTERVAL


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    coordinator = entry.runtime_data
    return {
        "integration_version": "0.7.0",
        "device_grouping": "one_per_system",
        "last_update_success": coordinator.last_update_success,
        "scan_interval_seconds": coordinator.update_interval.total_seconds(),
        "connectivity_interval_seconds": CONNECTIVITY_INTERVAL,
        "configuration_discovery": "startup_or_manual",
        "system_health_available": coordinator.data.system_health_error is None,
        "zones": [
            {
                "online": zone.online,
                "connection_status": zone.effective_connection_status,
                "system_connection_status": zone.connection_status,
                "telemetry_status": zone.telemetry_status,
                "schedule_present": bool(zone.schedule),
                "schedule_kind": optional_text(zone.schedule.get("kind")),
                "schedule_status": optional_text(zone.schedule.get("status")),
                "circulation_minutes_per_hour": zone.circulation_minutes,
                "circulation_mode": zone.circulation_mode,
                "telemetry_observed_at": zone.observed_at,
                "connectivity_issue_count": len(zone.connectivity_issues)
                if zone.connectivity_issues is not None
                else None,
                "feature_names": sorted(zone.features),
                "mode": zone.mode,
                "action": zone.action,
                "temperature_capabilities": {
                    key: zone.temperature_capabilities.get(key)
                    for key in ("min", "max", "precision")
                },
                "has_split_targets": "heatValue" in zone.setpoint,
                "fan_max": zone.fan_max,
                "air_quality_available": zone.air_quality is not None,
                "air_quality_access": zone.air_quality_access,
                "air_quality_missing_entitlement": zone.air_quality_missing_entitlement,
                "air_quality_request_failed": zone.key in coordinator.data.air_quality_errors,
                "air_quality_fresh": zone.air_quality_available("overall"),
                "air_quality_last_updated_at": mapping(
                    mapping(zone.air_quality).get("current")
                ).get("lastUpdatedAt"),
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
                "equipment": [
                    {
                        "type": optional_text(item.get("type")),
                        "model": optional_text(item.get("model")),
                        "role": optional_text(item.get("role")),
                        "connection_status": optional_text(item.get("connectionStatus")),
                    }
                    for item in system.equipment
                ],
                "energy_data_available": system.energy is not None,
                "energy_request_failed": system.system_id in coordinator.data.energy_errors,
                "heatpump_status_count": len(system.heatpump_status),
                "heatpump_operation_count": sum(
                    isinstance(item.get("operation"), dict)
                    for item in system.heatpump_status.values()
                ),
            }
            for system in coordinator.data.systems.values()
        ],
        "air_quality_error_count": len(coordinator.data.air_quality_errors),
        "energy_telemetry_implemented": True,
        "energy_error_count": len(coordinator.data.energy_errors),
        "heatpump_error_count": len(coordinator.data.heatpump_errors),
    }
