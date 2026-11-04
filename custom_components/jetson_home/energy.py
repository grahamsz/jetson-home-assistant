"""Views of the live-verified energy endpoint, including calendar-day counters."""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .models import mapping, number, optional_text


def timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return result if result.tzinfo is not None else None


@dataclass(frozen=True)
class EnergyView:
    """Read measurements without deriving totals or inventing absent values."""

    data: dict

    @property
    def loads(self) -> dict[str, dict]:
        items = self.data.get("loads")
        if not isinstance(items, list):
            return {}
        return {
            item["key"]: item
            for item in items
            if isinstance(item, dict) and optional_text(item.get("key")) is not None
        }

    def updated_at(self, energy: bool = False) -> datetime | None:
        return timestamp(mapping(self.data.get("today" if energy else "live")).get("asOf"))

    @property
    def heat_strip_loads(self) -> set[str]:
        live = mapping(mapping(self.data.get("live")).get("loads"))
        return {key for key in self.loads if "heatStripsPowerW" in mapping(live.get(key))}

    def heat_strip_power(self, load_key: str | None) -> float | None:
        if load_key not in self.loads:
            return None
        live = mapping(mapping(self.data.get("live")).get("loads"))
        return number(mapping(live.get(load_key)).get("heatStripsPowerW"))

    def is_fresh(self, now: datetime, max_age: float, *, energy: bool = False) -> bool:
        observed = self.updated_at(energy)
        return observed is not None and -60 <= (now - observed).total_seconds() <= max_age

    def value(self, load_key: str | None, *, energy: bool = False) -> float | None:
        section = mapping(self.data.get("today" if energy else "live"))
        if load_key is None:
            value = number(section.get("totalMainEnergyKwh" if energy else "totalMainPowerW"))
        elif load_key in self.loads:
            load = mapping(mapping(section.get("loads")).get(load_key))
            value = number(load.get("energyKwh" if energy else "powerW"))
        else:
            return None
        # Power may legitimately be signed. Negative daily consumption is not a
        # usable counter, and residualEnergyKwh is deliberately never a source.
        return None if energy and value is not None and value < 0 else value

    @property
    def reset_time(self) -> datetime | None:
        today = mapping(self.data.get("today"))
        observed = self.updated_at(energy=True)
        try:
            period = date.fromisoformat(today["date"])
            zone = ZoneInfo(self.data["timezone"])
        except (KeyError, TypeError, ValueError, ZoneInfoNotFoundError):
            return None
        if observed is None or observed.astimezone(zone).date() != period:
            return None
        return datetime.combine(period, time.min, tzinfo=zone)
