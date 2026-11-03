"""Register system, hub, equipment, and zone relationships in Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .models import Snapshot, build_devices


def sync_devices(
    hass: HomeAssistant, entry: ConfigEntry, snapshot: Snapshot
) -> dict[str, dr.DeviceInfo]:
    registry = dr.async_get(hass)
    plans = build_devices(snapshot)
    registered = {}
    # Create identities first so explicit HA parent IDs exist for every link.
    for key, device in plans.items():
        registered[key] = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, key)},
            name=device.name,
            model=device.model,
            manufacturer=device.manufacturer,
            serial_number=device.serial_number,
            entry_type=dr.DeviceEntryType.SERVICE if device.is_service else None,
        )
    result = {}
    for key, device in plans.items():
        parent = registered.get(device.via_identifier)
        parent_id = parent.id if parent else None
        registry.async_update_device(registered[key].id, via_device_id=parent_id)
        result[key] = dr.DeviceInfo(identifiers={(DOMAIN, key)})
        if parent_id is not None:
            result[key]["via_device_id"] = parent_id
    return result
