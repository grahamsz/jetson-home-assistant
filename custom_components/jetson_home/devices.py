"""Group entities by system and consolidate earlier per-equipment registry rows."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .models import (
    Snapshot,
    build_devices,
    device_aliases,
    equipment_identifier,
    system_for_legacy_identifier,
)


def sync_devices(
    hass: HomeAssistant, entry: ConfigEntry, snapshot: Snapshot
) -> dict[str, dr.DeviceInfo]:
    registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    # The old timestamp state changed for every device sample. Its replacement is
    # an unrecorded attribute on telemetry status; remove only this entry's exact
    # known-zone sensor records, including customized or disabled ones.
    retired = {f"{zone.key}:observed_at" for zone in snapshot.zones.values()}
    retired_connections = {
        f"{equipment_identifier(system.system_id, item['id'])}:connectivity"
        for system in snapshot.systems.values()
        for item in system.equipment
        if item.get("type") == "Humidifier"
        and item.get("connectionStatus") not in ("Connected", "Disconnected")
    }
    for entity in tuple(er.async_entries_for_config_entry(entity_registry, entry.entry_id)):
        if (
            entity.config_entry_id == entry.entry_id
            and entity.platform == DOMAIN
            and (
                (entity.entity_id.startswith("sensor.") and entity.unique_id in retired)
                or (
                    entity.entity_id.startswith("binary_sensor.")
                    and entity.unique_id in retired_connections
                )
            )
        ):
            entity_registry.async_remove(entity.entity_id)
    registered = {}
    for key, device in build_devices(snapshot).items():
        registered[key] = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, key)},
            name=device.name,
            model=device.model,
            manufacturer=device.manufacturer,
            serial_number=device.serial_number,
            entry_type=dr.DeviceEntryType.SERVICE if device.is_service else None,
        )
        registry.async_update_device(registered[key].id, via_device_id=None)

    # Move disabled and unavailable entities too, before removing an old device.
    # Entity unique IDs, entity IDs, custom names/options, and statistics are kept.
    for old in tuple(dr.async_entries_for_config_entry(registry, entry.entry_id)):
        targets = {
            target
            for domain, identifier in old.identifiers
            if domain == DOMAIN
            and (target := system_for_legacy_identifier(snapshot, identifier)) is not None
        }
        if len(targets) != 1:
            continue
        target = registered[next(iter(targets))]
        if old.id == target.id:
            continue
        for entity in er.async_entries_for_device(
            entity_registry, old.id, include_disabled_entities=True
        ):
            if entity.config_entry_id != entry.entry_id or entity.platform != DOMAIN:
                continue
            updates = {"device_id": target.id}
            if entity.area_id is None and old.area_id is not None:
                updates["area_id"] = old.area_id
            if entity.disabled_by is er.RegistryEntryDisabler.DEVICE and target.disabled_by is None:
                updates["disabled_by"] = er.RegistryEntryDisabler.USER
            entity_registry.async_update_entity(entity.entity_id, **updates)
        # Do not remove devices that still own other entities or child components.
        if not er.async_entries_for_device(
            entity_registry, old.id, include_disabled_entities=True
        ) and not dr.async_entries_for_parent_device(registry, old.id):
            registry.async_remove_device(old.id)

    return {
        alias: dr.DeviceInfo(identifiers={(DOMAIN, root)})
        for alias, root in device_aliases(snapshot).items()
    }
