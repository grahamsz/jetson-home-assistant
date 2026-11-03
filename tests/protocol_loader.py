"""Load the pure protocol modules without initializing Home Assistant."""

import importlib
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
package = types.ModuleType("jetson_protocol")
package.__path__ = [str(ROOT / "custom_components" / "jetson_home")]
sys.modules.setdefault("jetson_protocol", package)
api = importlib.import_module("jetson_protocol.api")
models = importlib.import_module("jetson_protocol.models")
polling = importlib.import_module("jetson_protocol.polling")


def sample_status():
    """Invented test data following recovered schemas, not a device capture."""
    return {
        "features": {
            "ambientTemperature": {
                "currentTemperature": 21.25,
                "mode": "Heat",
                "status": "Heating",
                "settings": {"mode": "Heat", "setpoint": {"value": 22}},
                "capabilities": {
                    "setpoint": {
                        "min": 10,
                        "max": 30,
                        "precision": {"celsius": 0.5, "fahrenheit": 1},
                    }
                },
            },
            "circulation": {
                "settings": {"mode": "Off", "fanSpeed": "Auto", "fanOnDuration": 0},
                "capabilities": {"fanSpeedSetting": {"max": 3}},
            },
            "humidity": {
                "status": "Off",
                "currentRelativeHumidity": 38.5,
                "settings": {"mode": "Off", "setpoint": {"value": 40}},
                "capabilities": {
                    "modes": ["Off", "Humidify"],
                    "setpoint": {"min": 20, "max": 60, "precision": 1},
                },
            },
        },
    }


def sample_equipment():
    """Hardware IDs are invented; their associations follow the app schema."""
    return [
        {
            "id": "hp1",
            "name": "Heat pump",
            "type": "HeatPump",
            "model": "CDHP-HH1-4T",
            "boardId": "b1",
            "parentEquipmentId": None,
            "zoneIds": ["z1"],
            "connectionStatus": "Connected",
        },
        {
            "id": "aq1",
            "name": "Return air monitor",
            "type": "Sensor",
            "model": "TEMCO-AQM",
            "boardId": "b1",
            "parentEquipmentId": "hp1",
            "zoneIds": ["z1"],
            "role": "ReturnAir",
            "connectionStatus": "Connected",
        },
        {
            "id": "em1",
            "name": "Whole home energy",
            "type": "EnergyMonitor",
            "model": "EM-001",
            "boardId": "b1",
            "parentEquipmentId": None,
            "zoneIds": [],
            "connectionStatus": "Connected",
            "serialNumber": "invented-monitor-serial",
        },
    ]


def sample_air_quality():
    return {
        "access": "full",
        "current": {
            "lastUpdatedAt": "2026-11-03T12:00:00",
            "overall": "good",
            "co2": {"value": 650, "level": "good"},
            "pm25": {"value": 4.5, "level": "excellent"},
            "tvoc": {"value": 250, "level": "good"},
        },
        "history": [],
    }
