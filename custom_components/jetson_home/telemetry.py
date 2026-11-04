"""Observed heat-pump operation fields; numeric speed units remain unestablished."""

from .models import mapping, number, optional_text

OPERATION_FIELDS = {
    "mode": ("Unit mode", False),
    "status": ("Unit activity", False),
    "fanSpeedStatus": ("Fan speed status", True),
    "fanSpeedSetpoint": ("Fan speed setpoint", True),
    "fanLevelStatus": ("Fan level", True),
    "fanLevelSetting": ("Fan level setting", True),
    "fanOperatingMode": ("Fan operating mode", False),
}


def operation_value(status: dict, field: str) -> str | float | None:
    if field not in OPERATION_FIELDS:
        return None
    value = mapping(status.get("operation")).get(field)
    return number(value) if OPERATION_FIELDS[field][1] else optional_text(value)
