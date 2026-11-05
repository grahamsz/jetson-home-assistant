"""Entity data/translation contracts using small HA adapters, not an HA runtime."""

import importlib
import json
import sys
import unittest
from datetime import UTC, datetime, timedelta
from enum import IntFlag, StrEnum
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from protocol_loader import (
    energy,
    models,
    sample_energy,
    sample_heatpump_status,
    sample_status,
    telemetry,
)

ROOT = Path(__file__).resolve().parents[1] / "custom_components/jetson_home"


class EntityAdapter:
    pass


class CoordinatorAdapter(EntityAdapter):
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return self.coordinator.last_update_success

    def _handle_coordinator_update(self):
        pass


class Features(IntFlag):
    TARGET_TEMPERATURE = 1
    TURN_OFF = 2
    FAN_MODE = 4


class LocalizedError(Exception):
    def __init__(self, **kwargs):
        self.translation = kwargs
        super().__init__(kwargs["translation_key"])


def module(name, **values):
    result = ModuleType(name)
    result.__dict__.update(values)
    return result


def adapters():
    package = module("jetson_entity_contract")
    package.__path__ = [str(ROOT)]
    namespaces = {
        "homeassistant": {},
        "homeassistant.components": {},
        "homeassistant.helpers": {},
        "homeassistant.config_entries": {"ConfigEntry": object},
        "homeassistant.core": {"HomeAssistant": object, "callback": lambda function: function},
        "homeassistant.exceptions": {"HomeAssistantError": LocalizedError},
        "homeassistant.helpers.device_registry": {"DeviceInfo": dict},
        "homeassistant.helpers.entity": {
            "EntityCategory": SimpleNamespace(DIAGNOSTIC="diagnostic", CONFIG="config")
        },
        "homeassistant.helpers.entity_platform": {"AddEntitiesCallback": object},
        "homeassistant.helpers.update_coordinator": {"CoordinatorEntity": CoordinatorAdapter},
        "homeassistant.components.sensor": {
            "SensorEntity": EntityAdapter,
            "SensorDeviceClass": SimpleNamespace(
                **{
                    name: name.lower()
                    for name in (
                        "ENERGY",
                        "POWER",
                        "ENUM",
                        "TEMPERATURE",
                        "HUMIDITY",
                        "CO2",
                        "PM25",
                        "VOLATILE_ORGANIC_COMPOUNDS_PARTS",
                        "TIMESTAMP",
                    )
                }
            ),
            "SensorStateClass": SimpleNamespace(MEASUREMENT="measurement", TOTAL="total"),
        },
        "homeassistant.components.binary_sensor": {
            "BinarySensorEntity": EntityAdapter,
            "BinarySensorDeviceClass": SimpleNamespace(CONNECTIVITY="connectivity"),
        },
        "homeassistant.components.button": {"ButtonEntity": EntityAdapter},
        "homeassistant.components.number": {
            "NumberEntity": EntityAdapter,
            "NumberMode": SimpleNamespace(BOX="box"),
        },
        "homeassistant.components.climate": {
            "ClimateEntity": EntityAdapter,
            "ClimateEntityFeature": Features,
            "HVACMode": StrEnum(
                "HVACMode",
                {name: name.lower() for name in ("OFF", "HEAT", "COOL", "HEAT_COOL", "FAN_ONLY")},
            ),
            "HVACAction": StrEnum(
                "HVACAction",
                {
                    name: name.lower()
                    for name in ("OFF", "IDLE", "HEATING", "COOLING", "FAN", "DRYING")
                },
            ),
        },
        "homeassistant.components.humidifier": {
            "HumidifierEntity": EntityAdapter,
            "HumidifierDeviceClass": SimpleNamespace(HUMIDIFIER="humidifier"),
            "HumidifierAction": SimpleNamespace(HUMIDIFYING="humidifying", IDLE="idle", OFF="off"),
        },
        "homeassistant.const": {
            "PERCENTAGE": "%",
            "ATTR_TEMPERATURE": "temperature",
            "UnitOfTemperature": SimpleNamespace(CELSIUS="°C"),
            "UnitOfPower": SimpleNamespace(WATT="W"),
            "UnitOfEnergy": SimpleNamespace(KILO_WATT_HOUR="kWh"),
            "UnitOfDensity": SimpleNamespace(MICROGRAMS_PER_CUBIC_METER="µg/m³"),
            "UnitOfRatio": SimpleNamespace(PARTS_PER_MILLION="ppm", PARTS_PER_BILLION="ppb"),
            "UnitOfTime": SimpleNamespace(MINUTES="min"),
        },
        "homeassistant.util": {"dt": SimpleNamespace(utcnow=lambda: datetime.now(UTC))},
        "jetson_entity_contract.coordinator": {"JetsonCoordinator": object},
    }
    return {
        **{name: module(name, **values) for name, values in namespaces.items()},
        "jetson_entity_contract": package,
        "jetson_entity_contract.models": models,
        "jetson_entity_contract.energy": energy,
        "jetson_entity_contract.telemetry": telemetry,
    }


class EntityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.modules = patch.dict(sys.modules, adapters())
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.sensor = importlib.import_module("jetson_entity_contract.sensor")
        self.binary = importlib.import_module("jetson_entity_contract.binary_sensor")
        self.climate = importlib.import_module("jetson_entity_contract.climate")
        self.humidifier = importlib.import_module("jetson_entity_contract.humidifier")
        self.button = importlib.import_module("jetson_entity_contract.button")
        self.number = importlib.import_module("jetson_entity_contract.number")
        self.zone = models.Zone("s", "Home", "z", "Main", sample_status())
        self.zone.status.update(
            connectivity={"connectionStatus": "Connected", "issues": []},
            health={"telemetryStatus": "Current", "observedAt": "2026-11-04T07:00:00Z"},
        )
        self.zone.circulation["fanSpeedStatus"] = 0
        self.system = models.System(
            "s",
            "Home",
            equipment=[{"id": "hp1", "name": "Main", "connectionStatus": "Connected"}],
            energy=sample_energy(),
            heatpump_status={"hp1": sample_heatpump_status()},
        )
        self.system.energy["loads"][0]["name"] = "Main"
        self.snapshot = models.Snapshot({"s": self.system}, {self.zone.key: self.zone})
        self.listeners = []
        self.commands = []

        async def command(*args):
            self.commands.append(args)

        self.coordinator = SimpleNamespace(
            data=self.snapshot,
            last_update_success=True,
            update_interval=timedelta(seconds=30),
            command=command,
            device_infos={
                key: {"identifiers": {("jetson_home", "system:s")}}
                for key in ("system:s", "s:z", "equipment:s:hp1")
            },
            async_add_listener=lambda callback: self.listeners.append(callback),
        )
        self.entry = SimpleNamespace(
            runtime_data=self.coordinator, async_on_unload=lambda callback: None
        )
        self.catalogs = {
            language: json.loads(
                (ROOT / "translations" / f"{language}.json").read_text(encoding="utf-8")
            )
            for language in ("en", "es", "fr")
        }

    def label(self, entity, domain="sensor", language="en"):
        # Check our translation metadata; HA itself is responsible for rendering it.
        self.assertFalse(hasattr(entity, "_attr_name"))
        template = self.catalogs[language]["entity"][domain][entity._attr_translation_key]["name"]
        return template.format(**entity._attr_translation_placeholders)

    def test_main_rename_preserves_identity_and_distinguishes_load(self):
        main = self.sensor.JetsonEnergySensor(self.coordinator, "s", None, energy=False)
        daily = self.sensor.JetsonEnergySensor(self.coordinator, "s", None, energy=True)
        load = self.sensor.JetsonEnergySensor(self.coordinator, "s", "hp1", energy=False)
        self.assertEqual(main._attr_unique_id, "system:s:power")
        self.assertEqual(daily._attr_unique_id, "system:s:energy_today")
        self.assertEqual(self.label(main), "Main power")
        self.assertEqual(self.label(daily), "Main energy today")
        self.assertEqual(self.label(load), "Main load power")
        self.assertEqual(self.label(main, language="es"), "Potencia principal")
        self.assertEqual(self.label(main, language="fr"), "Puissance principale")

    def test_separate_heat_strip_sensor_and_missing_field_availability(self):
        strips = self.sensor.JetsonEnergySensor(
            self.coordinator, "s", "hp1", energy=False, heat_strips=True
        )
        main = self.sensor.JetsonEnergySensor(self.coordinator, "s", None, energy=False)
        self.assertTrue(strips.available)
        self.assertEqual(strips.native_value, 5)
        self.assertEqual(main.native_value, 1000)
        self.assertEqual(strips._attr_unique_id, "system:s:load:hp1:heat_strips_power")
        self.assertEqual(self.label(strips), "Main heat strips power")
        self.system.energy["live"]["loads"]["hp1"]["heatStripsPowerW"] = 0
        self.assertEqual(strips.native_value, 0)
        del self.system.energy["live"]["loads"]["hp1"]["heatStripsPowerW"]
        self.assertFalse(strips.available)
        self.assertIsNone(strips.native_value)
        self.assertTrue(main.available)

    async def test_discovery_has_no_duplicate_or_fabricated_heat_strip_sensors(self):
        entities = []
        await self.sensor.async_setup_entry(None, self.entry, entities.extend)
        self.assertTrue(any(entity._attr_unique_id == "s:z:fan_activity" for entity in entities))
        self.assertTrue(any(entity._attr_unique_id == "s:z:fan_speed" for entity in entities))
        self.assertFalse(
            any(entity._attr_unique_id.endswith(":observed_at") for entity in entities)
        )
        strips = [
            entity for entity in entities if entity._attr_unique_id.endswith(":heat_strips_power")
        ]
        self.assertEqual(len(strips), 1)
        count = len(entities)
        for callback in self.listeners:
            callback()
        self.assertEqual(len(entities), count)
        self.assertTrue(
            all(
                entity.device_info == self.coordinator.device_infos["system:s"]
                for entity in entities
            )
        )
        for entity in entities:
            for language in self.catalogs:
                self.assertTrue(self.label(entity, language=language))

    def test_last_device_reading_is_an_unrecorded_attribute_on_stable_telemetry_state(self):
        sensor = self.sensor.JetsonZoneTelemetrySensor(self.coordinator, self.zone)
        self.assertEqual(sensor._attr_unique_id, "s:z:telemetry_status")
        self.assertEqual(sensor.native_value, "Current")
        self.assertEqual(
            sensor.extra_state_attributes, {"last_device_reading": "2026-11-04T07:00:00+00:00"}
        )
        self.assertIn("last_device_reading", sensor._unrecorded_attributes)
        self.zone.status["health"]["observedAt"] = "2026-11-04T07:01:00Z"
        self.assertEqual(sensor.native_value, "Current")
        self.assertEqual(
            sensor.extra_state_attributes["last_device_reading"], "2026-11-04T07:01:00+00:00"
        )
        for invalid in ("bad", "2026-11-04T07:00:00", None):
            self.zone.status["health"]["observedAt"] = invalid
            self.assertIsNone(sensor.extra_state_attributes["last_device_reading"])

    async def test_timestamp_without_status_stays_visible_without_a_timestamp_entity(self):
        self.zone.status["health"].pop("telemetryStatus")
        entities = []
        await self.sensor.async_setup_entry(None, self.entry, entities.extend)
        sensor = next(
            entity for entity in entities if entity._attr_unique_id == "s:z:telemetry_status"
        )
        self.assertTrue(sensor.available)
        self.assertIsNone(sensor.native_value)
        self.assertIsNotNone(sensor.extra_state_attributes["last_device_reading"])

    def test_fan_activity_speed_and_setting_are_independent_entities(self):
        activity = self.sensor.JetsonStatusSensor(self.coordinator, self.zone, "fan_activity")
        speed = self.sensor.JetsonStatusSensor(self.coordinator, self.zone, "fan_speed")
        mode = self.sensor.JetsonStatusSensor(self.coordinator, self.zone, "fan_mode")
        self.assertEqual(
            (activity.native_value, speed.native_value, mode.native_value), ("off", "0", "auto")
        )
        self.zone.circulation["fanSpeedStatus"] = 2
        self.assertEqual(
            (activity.native_value, speed.native_value, mode.native_value), ("running", "2", "auto")
        )

    def test_configuration_renames_update_translation_placeholders(self):
        sensor = self.sensor.JetsonSensor(self.coordinator, self.zone, "temperature")
        self.assertEqual(self.label(sensor), "Main temperature")
        sensor.__dict__["name"] = "Previously cached name"
        self.zone.name = "Upstairs"
        sensor._handle_coordinator_update()
        self.assertNotIn("name", sensor.__dict__)
        self.assertEqual(self.label(sensor), "Upstairs temperature")
        self.assertEqual(sensor._attr_unique_id, "s:z:temperature")

    def test_unit_speed_has_localized_enum_and_levels_stay_numeric(self):
        sensor = self.sensor.JetsonHeatPumpSensor(self.coordinator, "s", "hp1", "fanSpeedStatus")
        level = self.sensor.JetsonHeatPumpSensor(self.coordinator, "s", "hp1", "fanLevelSetting")
        self.assertEqual(sensor.native_value, "0")
        self.assertEqual(sensor.extra_state_attributes, {"raw_value": 0})
        self.assertEqual(sensor._attr_options, ["0", "1", "2", "3"])
        self.assertEqual(level.native_value, 1)
        self.assertTrue(self.label(sensor, language="fr"))

    async def test_climate_labels_preserve_numeric_fan_commands_and_error_translations(self):
        climate = self.climate.JetsonClimate(self.coordinator, self.zone)
        self.assertEqual(self.label(climate, "climate", "es"), "Main")
        self.assertEqual(climate.fan_modes, ["auto", "1", "2", "3"])
        await climate.async_set_fan_mode("2")
        self.assertEqual(self.commands, [("set_fan_speed", self.zone, 2)])
        with self.assertRaises(LocalizedError) as caught:
            await climate.async_set_fan_mode("4")
        self.assertEqual(caught.exception.translation["translation_key"], "unsupported_fan_speed")
        humidifier = self.humidifier.JetsonHumidifier(self.coordinator, self.zone)
        self.assertEqual(self.label(humidifier, "humidifier", "fr"), "Humidificateur de Main")
        connection = self.binary.JetsonZoneConnectivity(self.coordinator, self.zone)
        self.assertTrue(self.label(connection, "binary_sensor", "es"))

    async def test_schedule_entities_follow_reported_state_without_automatic_resume(self):
        self.zone.status["schedule"] = {"id": "weekly-1", "kind": "Weekly", "status": "Active"}
        paused = self.binary.JetsonSchedulePaused(self.coordinator, self.zone)
        button = self.button.JetsonResumeSchedule(self.coordinator, self.zone)
        self.assertTrue(paused.available)
        self.assertFalse(paused.is_on)
        self.assertFalse(button.available)
        self.zone.schedule["status"] = "Paused"
        self.assertTrue(paused.is_on)
        self.assertTrue(button.available)
        self.assertEqual(
            paused.extra_state_attributes, {"schedule_id": "weekly-1", "schedule_kind": "weekly"}
        )
        self.assertFalse(self.commands)
        await button.async_press()
        self.assertEqual(self.commands, [("resume_schedule", self.zone, None)])
        self.zone.status.pop("schedule")
        self.assertFalse(paused.available)
        self.assertIsNone(paused.is_on)
        self.assertFalse(button.available)
        for language in self.catalogs:
            self.assertTrue(self.label(button, "button", language))
            self.assertTrue(self.label(paused, "binary_sensor", language))

    async def test_schedule_controls_appear_when_status_later_reports_a_schedule(self):
        entities = []
        await self.binary.async_setup_entry(None, self.entry, entities.extend)
        await self.button.async_setup_entry(None, self.entry, entities.extend)
        self.assertFalse(
            any(item._attr_unique_id.endswith(":resume_schedule") for item in entities)
        )
        self.zone.status["schedule"] = {"id": "weekly-1", "kind": "Weekly", "status": "Paused"}
        for callback in self.listeners:
            callback()
        self.assertEqual(
            sum(item._attr_unique_id.endswith(":schedule_paused") for item in entities), 1
        )
        self.assertEqual(
            sum(item._attr_unique_id.endswith(":resume_schedule") for item in entities), 1
        )
        for callback in self.listeners:
            callback()
        self.assertEqual(
            sum(item._attr_unique_id.endswith(":resume_schedule") for item in entities), 1
        )

    async def test_number_allows_minutes_without_changing_its_cached_reading_optimistically(self):
        number = self.number.JetsonCirculationMinutes(self.coordinator, self.zone)
        self.assertEqual(number.native_value, 0)
        self.assertTrue(number.available)
        self.assertEqual(
            number.extra_state_attributes,
            {"circulation_mode": "off", "applies_in_mode": "circulate"},
        )
        self.assertEqual(
            (
                number._attr_native_min_value,
                number._attr_native_max_value,
                number._attr_native_step,
            ),
            (0, 60, 1),
        )
        await number.async_set_native_value(30)
        self.assertEqual(self.commands, [("set_circulation_duration", self.zone, 30)])
        self.assertEqual(number.native_value, 0)
        for value in (True, None, -1, 61, 1.5, "15"):
            with self.assertRaises(LocalizedError):
                await number.async_set_native_value(value)
        self.assertEqual(len(self.commands), 1)
        self.zone.circulation["settings"]["fanOnDuration"] = None
        self.assertIsNone(number.native_value)
        self.assertFalse(number.available)
        for language in self.catalogs:
            self.assertTrue(self.label(number, "number", language))


if __name__ == "__main__":
    unittest.main()
