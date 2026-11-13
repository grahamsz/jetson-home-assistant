"""Exercise registry consolidation with in-memory adapters, without HA installed."""

import importlib
import sys
import types
import unittest
from dataclasses import dataclass, field, replace
from enum import StrEnum
from unittest.mock import patch

from protocol_loader import models, sample_equipment, sample_status


class Disabler(StrEnum):
    DEVICE = "device"
    USER = "user"


@dataclass
class DeviceRecord:
    id: str
    identifiers: set
    config_entry_id: str = "account"
    area_id: str | None = None
    disabled_by: str | None = None
    name: str = ""


@dataclass
class EntityRecord:
    entity_id: str
    unique_id: str
    device_id: str
    config_entry_id: str = "account"
    platform: str = "jetson_home"
    area_id: str | None = None
    disabled_by: str | None = None
    name: str | None = None
    options: dict = field(default_factory=dict)


class EntityRegistry:
    def __init__(self):
        self.entities = {}
        self.updates = []
        self.removed = []

    def async_update_entity(self, entity_id, **updates):
        self.entities[entity_id] = replace(self.entities[entity_id], **updates)
        self.updates.append((entity_id, updates))

    def async_remove(self, entity_id):
        self.entities.pop(entity_id)
        self.removed.append(entity_id)


class DeviceRegistry:
    def __init__(self, entities):
        self.devices = {}
        self.entities = entities
        self.children = {}
        self.created = 0
        self.removed = []

    def async_get_or_create(self, *, config_entry_id, identifiers, **metadata):
        for device in self.devices.values():
            if device.config_entry_id == config_entry_id and identifiers & device.identifiers:
                device.name = metadata["name"]
                return device
        self.created += 1
        device = DeviceRecord(f"created-{self.created}", identifiers, config_entry_id)
        device.name = metadata["name"]
        self.devices[device.id] = device
        return device

    def async_update_device(self, device_id, **updates):
        # Topology fields are irrelevant to identity in this in-memory adapter.
        assert set(updates) == {"via_device_id"}
        assert device_id in self.devices

    def async_remove_device(self, device_id):
        # This assertion catches removal before disabled/unavailable entities move.
        assert not any(item.device_id == device_id for item in self.entities.entities.values())
        assert not self.children.get(device_id)
        self.devices.pop(device_id)
        self.removed.append(device_id)


dr = types.ModuleType("homeassistant.helpers.device_registry")
dr.DeviceInfo = dict
dr.DeviceEntryType = types.SimpleNamespace(SERVICE="service")
dr.async_get = lambda hass: hass.devices
dr.async_entries_for_config_entry = lambda registry, entry_id: [
    item for item in registry.devices.values() if item.config_entry_id == entry_id
]
dr.async_entries_for_parent_device = lambda registry, device_id: registry.children.get(
    device_id, []
)
er = types.ModuleType("homeassistant.helpers.entity_registry")
er.RegistryEntryDisabler = Disabler
er.async_get = lambda hass: hass.entities
er.async_entries_for_config_entry = lambda registry, entry_id: [
    item for item in registry.entities.values() if item.config_entry_id == entry_id
]
er.async_entries_for_device = lambda registry, device_id, include_disabled_entities=False: [
    item
    for item in registry.entities.values()
    if item.device_id == device_id and (include_disabled_entities or item.disabled_by is None)
]
config_entries = types.ModuleType("homeassistant.config_entries")
config_entries.ConfigEntry = object
core = types.ModuleType("homeassistant.core")
core.HomeAssistant = object
helpers = types.ModuleType("homeassistant.helpers")
helpers.device_registry = dr
helpers.entity_registry = er
with patch.dict(
    sys.modules,
    {
        "homeassistant": types.ModuleType("homeassistant"),
        "homeassistant.config_entries": config_entries,
        "homeassistant.core": core,
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": dr,
        "homeassistant.helpers.entity_registry": er,
    },
):
    adapter = importlib.import_module("jetson_protocol.devices")


class DeviceMigrationTests(unittest.TestCase):
    def setUp(self):
        self.entities = EntityRegistry()
        self.devices = DeviceRegistry(self.entities)
        self.hass = types.SimpleNamespace(devices=self.devices, entities=self.entities)
        self.entry = types.SimpleNamespace(entry_id="account")
        system = models.System("s1", "Home", [{"id": "b1"}], sample_equipment())
        zone = models.Zone("s1", "Home", "z1", "Main", sample_status())
        self.snapshot = models.Snapshot({"s1": system}, {zone.key: zone})
        self.devices.devices["root"] = DeviceRecord("root", {("jetson_home", "system:s1")})

    def legacy(self, key, *, entity_id=None, **entity_settings):
        device = DeviceRecord("old:" + key, {("jetson_home", key)})
        self.devices.devices[device.id] = device
        if entity_id is not None:
            self.entities.entities[entity_id] = EntityRecord(
                entity_id, key + ":feature", device.id, **entity_settings
            )
        return device

    def sync(self):
        return adapter.sync_devices(self.hass, self.entry, self.snapshot)

    def test_existing_devices_consolidate_without_recreating_entity_ids(self):
        for key in models.device_aliases(self.snapshot):
            if key != "system:s1":
                self.legacy(key, entity_id="sensor." + key.replace(":", "_"))
        original_ids = {key: item.unique_id for key, item in self.entities.entities.items()}
        infos = self.sync()
        self.assertEqual(set(self.devices.devices), {"root"})
        self.assertEqual(self.devices.created, 0)
        self.assertEqual(
            {key: item.unique_id for key, item in self.entities.entities.items()}, original_ids
        )
        self.assertTrue(all(item.device_id == "root" for item in self.entities.entities.values()))
        self.assertEqual(infos["s1:z1"]["identifiers"], {("jetson_home", "system:s1")})
        self.assertEqual(infos["equipment:s1:em1"], infos["s1:z1"])

    def test_retired_timestamp_sensor_is_removed_without_touching_other_entities(self):
        self.entities.entities["sensor.my_custom_timestamp"] = EntityRecord(
            "sensor.my_custom_timestamp",
            "s1:z1:observed_at",
            "root",
            disabled_by=Disabler.USER,
            name="My timestamp",
        )
        for entity_id, unique_id, settings in (
            ("sensor.temperature", "s1:z1:temperature", {}),
            ("sensor.telemetry", "s1:z1:telemetry_status", {}),
            ("sensor.other_account", "s1:z1:observed_at", {"config_entry_id": "other"}),
            ("sensor.other_integration", "s1:z1:observed_at", {"platform": "other"}),
            ("sensor.other_zone", "s1:other:observed_at", {}),
            ("binary_sensor.other_domain", "s1:z1:observed_at", {}),
        ):
            self.entities.entities[entity_id] = EntityRecord(
                entity_id, unique_id, "root", **settings
            )
        self.sync()
        self.assertEqual(self.entities.removed, ["sensor.my_custom_timestamp"])
        self.assertEqual(len(self.entities.entities), 6)
        self.sync()
        self.assertEqual(self.entities.removed, ["sensor.my_custom_timestamp"])

    def test_unknown_humidifier_connection_removed_only_for_own_entry(self):
        self.snapshot.systems["s1"].equipment.append(
            {"id": "hum1", "type": "Humidifier", "connectionStatus": "Unknown"}
        )
        for entity_id, settings in (
            ("binary_sensor.hum", {}),
            ("binary_sensor.other_account", {"config_entry_id": "other"}),
            ("binary_sensor.other_platform", {"platform": "other"}),
        ):
            self.entities.entities[entity_id] = EntityRecord(
                entity_id, "equipment:s1:hum1:connectivity", "root", **settings
            )
        self.sync()
        self.assertEqual(self.entities.removed, ["binary_sensor.hum"])
        self.assertIn("binary_sensor.other_account", self.entities.entities)
        self.assertIn("binary_sensor.other_platform", self.entities.entities)

    def test_reported_humidifier_connectivity_is_preserved(self):
        self.snapshot.systems["s1"].equipment.append(
            {"id": "hum1", "type": "Humidifier", "connectionStatus": "Connected"}
        )
        self.entities.entities["binary_sensor.hum"] = EntityRecord(
            "binary_sensor.hum", "equipment:s1:hum1:connectivity", "root"
        )
        self.sync()
        self.assertIn("binary_sensor.hum", self.entities.entities)

    def test_empty_discovery_does_not_remove_unknown_timestamp_records(self):
        self.entities.entities["sensor.timestamp"] = EntityRecord(
            "sensor.timestamp", "s1:z1:observed_at", "root"
        )
        self.snapshot.zones.clear()
        self.sync()
        self.assertIn("sensor.timestamp", self.entities.entities)

    def test_inherited_area_and_disabled_choice_are_preserved(self):
        old = self.legacy(
            "s1:z1",
            entity_id="sensor.temperature",
            disabled_by=Disabler.DEVICE,
            name="My temperature",
            options={"sensor": {"precision": 1}},
        )
        old.area_id = "living-room"
        self.sync()
        entity = self.entities.entities["sensor.temperature"]
        self.assertEqual(entity.device_id, "root")
        self.assertEqual(entity.area_id, "living-room")
        self.assertEqual(entity.disabled_by, Disabler.USER)
        self.assertEqual(entity.name, "My temperature")
        self.assertEqual(entity.options, {"sensor": {"precision": 1}})

    def test_explicit_entity_area_is_not_overwritten(self):
        old = self.legacy("s1:z1", entity_id="climate.main", area_id="bedroom")
        old.area_id = "living-room"
        self.sync()
        self.assertEqual(self.entities.entities["climate.main"].area_id, "bedroom")

    def test_disabled_root_keeps_device_inherited_disable(self):
        self.devices.devices["root"].disabled_by = Disabler.USER
        self.legacy("s1:z1", entity_id="climate.main", disabled_by=Disabler.DEVICE)
        self.sync()
        self.assertEqual(self.entities.entities["climate.main"].disabled_by, Disabler.DEVICE)

    def test_entities_for_removed_equipment_still_move_to_known_system(self):
        self.legacy("equipment:s1:removed", entity_id="binary_sensor.removed")
        self.sync()
        self.assertEqual(self.entities.entities["binary_sensor.removed"].device_id, "root")
        self.assertEqual(set(self.devices.devices), {"root"})

    def test_other_accounts_are_not_changed(self):
        other = self.legacy(
            "equipment:s1:em1", entity_id="binary_sensor.other", config_entry_id="other"
        )
        other.config_entry_id = "other"
        self.sync()
        self.assertIn(other.id, self.devices.devices)
        self.assertEqual(self.entities.entities["binary_sensor.other"].device_id, other.id)

    def test_remaining_unrelated_entities_prevent_device_removal(self):
        old = self.legacy("equipment:s1:em1", entity_id="binary_sensor.other", platform="other")
        self.entities.entities["binary_sensor.ours"] = EntityRecord(
            "binary_sensor.ours", "equipment:s1:em1:connectivity", old.id
        )
        self.sync()
        self.assertEqual(self.entities.entities["binary_sensor.ours"].device_id, "root")
        self.assertEqual(self.entities.entities["binary_sensor.other"].device_id, old.id)
        self.assertIn(old.id, self.devices.devices)

    def test_child_components_prevent_parent_removal(self):
        old = self.legacy("board:s1:b1")
        self.devices.children[old.id] = ["child-component"]
        self.sync()
        self.assertIn(old.id, self.devices.devices)

    def test_unrecognized_devices_are_left_alone(self):
        old = self.legacy("unrecognized", entity_id="sensor.unrecognized")
        self.sync()
        self.assertIn(old.id, self.devices.devices)
        self.assertEqual(self.entities.entities["sensor.unrecognized"].device_id, old.id)

    def test_multiple_systems_remain_separate(self):
        self.snapshot.systems["s2"] = models.System("s2", "Second home")
        self.legacy("s1:z1", entity_id="climate.first")
        self.legacy("s2:z2", entity_id="climate.second")
        self.sync()
        first = self.entities.entities["climate.first"].device_id
        second = self.entities.entities["climate.second"].device_id
        self.assertNotEqual(first, second)
        self.assertEqual(len(self.devices.devices), 2)

    def test_ambiguous_legacy_identifiers_are_not_merged(self):
        self.snapshot.systems["s2"] = models.System("s2", "Second home")
        old = self.legacy("s1:z1", entity_id="climate.ambiguous")
        old.identifiers.add(("jetson_home", "s2:z2"))
        self.sync()
        self.assertEqual(self.entities.entities["climate.ambiguous"].device_id, old.id)

    def test_repeated_sync_is_idempotent(self):
        self.legacy("s1:z1", entity_id="climate.main")
        self.sync()
        removed = list(self.devices.removed)
        self.sync()
        self.assertEqual(self.devices.removed, removed)
        self.assertEqual(set(self.devices.devices), {"root"})


if __name__ == "__main__":
    unittest.main()
