# Power, daily energy, and live endpoint findings

Version **0.5.0** adds power and daily energy from a live-verified route. The bundled React app's older GetEnergyCurrentResponse is not the current wire shape: live loads are now keyed maps, while a separate root loads array supplies their labels and equipment IDs.

## Read endpoint

```http
GET /v1/systems/{systemId}/energy/current
Authorization: Bearer <access-token>
```

This returned HTTP 200 in authorized reads on November 3–4, 2026. The exact current structure is described in [live-openapi.json](live-openapi.json). The original [app-callsite OpenAPI](openapi.json) remains separate from these newer observations.

| Field | Observed meaning |
| --- | --- |
| `timezone` | IANA timezone for calendar-day totals |
| `loads[]` | Descriptors with key, kind, equipmentId, type, and name |
| `live.asOf` | Timestamp of the power sample |
| `live.totalMainPowerW` | Whole-home power in W |
| `live.loads[loadKey].powerW` | Per-load power in W |
| `live.loads[loadKey].heatStripsPowerW` | Additional component value observed for the indoor unit; semantics still need verification |
| `today.date` / `today.asOf` | Calendar date and timestamp for daily totals |
| `today.totalMainEnergyKwh` | Whole-home energy accumulated in that day, kWh |
| `today.loads[loadKey].energyKwh` | Per-load energy for that day, kWh |
| `today.residualEnergyKwh` | Backend's residual; a negative value was observed, so it is not used as an HA counter |
| `comparisons[]` | Prior-date entries, with keys yesterday and sameWeekdayLastWeek observed; measurements were null and load maps empty |

The two observed load descriptors were indoor and outdoor heat-pump equipment. Their keys matched equipment IDs in inventory. Consumers must use the stable descriptor key to read the maps; these maps are not arrays and names are not identifiers. Power can remain available from the energy source while a heat pump's separate control/health link reports disconnected.

## Home Assistant entities

All energy entities share their containing system device:

- Whole-home power, W, power device class, measurement state class.
- Whole-home energy today, kWh, energy device class, total state class with explicit last_reset.
- One named power and energy-today sensor per descriptor, with stable load-key-based unique IDs.

The root total is exposed once per system, not duplicated for each zone. No residual sensor, calculated whole-home sum, or additional heat-strip component sensor is created. The observed component could duplicate part of another load; adding it again would not be justified. These reads do not provide separate supply/return temperature, humidity, or pressure readings.

For the Energy dashboard, select the whole-home energy-today sensor as the relevant main energy source and per-load energy-today sensors as individual appliance consumption where appropriate. Do not select the same consumption more than once as a grid source. Sensor state-class/unit compatibility follows [HA's sensor definitions](https://contributors.home-assistant.io/core/entities/sensor/); actual dashboard/Recorder behavior still needs checking in the installed instance.

## Calendar resets and corrections

Two snapshots spanning local midnight showed today.date advancing and whole-home/per-load counters restarting near zero. This establishes one observed calendar-day reset, not a lifetime counter or a billing-grade accuracy guarantee. Earlier main and load totals did not reconcile and produced a negative residual; different coverage periods or other causes were not established.

The integration uses total with last_reset equal to midnight of today.date in the API's timezone. A downward correction within the same day therefore remains a correction, rather than being counted as a new meter cycle. When the date changes, last_reset changes and HA starts a new cycle. This also accounts for daylight-saving offsets at midnight, which can differ from the sample's current UTC offset.

Invalid/missing timezones, dates, timestamps, mismatched asOf/date, and negative daily consumption do not become fabricated counters. Null/missing values stay unknown; valid zero stays zero. Power may be signed. The integration does not import earlier readings into Recorder or fill missing days from null comparisons.

## Schedule and failure behavior

One energy read per configured system with reported EnergyMonitor equipment runs on each normal polling cycle, alongside known-zone readings. Failure, denied access, or malformed data clears that cycle's energy readings and makes affected sensors unavailable while climate can continue. Authentication and rate-limit errors follow the client's existing global handling.

Live and daily timestamps are checked independently. Readings older than max(300 seconds, twice the configured polling interval), or more than 60 seconds in the future, are unavailable. Daily counters additionally require a coherent local date/timezone. Source timestamps and period metadata are available in entity attributes.

The parser and reset rules have mock-server and unit tests, and were checked against the captured live response. The source API was read successfully; HA entity loading, Recorder statistics, and Energy dashboard selection remain runtime-validation items.
