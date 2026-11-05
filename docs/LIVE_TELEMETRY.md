# Newer status fields and supply/return findings

Authorized reads on November 3–4, 2026 returned fields absent from the recovered app schemas. The [live OpenAPI supplement](live-openapi.json) records these observations separately; it is not a complete vendor specification.

## Zone status additions

`GET /v1/zones/{zoneId}/status` returned:

| Field | HA representation |
| --- | --- |
| `connectivity.connectionStatus` | Zone connection diagnostic binary sensor; fresh value takes priority over cached system health |
| `connectivity.issues` | issues and issue_count attributes on that connection entity; nonempty item structure remains unknown |
| `health.telemetryStatus` | Telemetry status diagnostic sensor, preserving the reported string |
| `health.observedAt` | `last_device_reading` attribute on Telemetry status; excluded from recorded attributes |

These use the already-polled zone response and add no requests. Connection and freshness diagnostics remain readable when a zone reports disconnected; ordinary controls/readings still respect connectivity. Current was observed for telemetryStatus, but the full enum is not established. An API response timestamp and a real device observation are different facts; the attribute reports observedAt, not the time HA fetched it.

Version 0.6.1 replaces the standalone Last device reading sensor with the attribute on the existing Telemetry status entity. It uses HA's `_unrecorded_attributes` mechanism, so the timestamp is available in current state/templates but is not retained as a historical attribute. The reported telemetry status remains independent of the timestamp. HA can still emit live attribute updates and Recorder state rows; this change removes timestamp-as-state history and stored timestamp attributes, not every possible database write. The old timestamp entity registry record is removed for known zones in this account, including disabled/custom-named records. Other entities/accounts and existing Recorder history are left intact; history expires under the normal retention policy.

## Heat-pump operation additions

`GET /v1/equipment/{equipmentId}/heatpump/status` returned an operation object for the indoor unit. It was absent for the offline outdoor unit. Reported fields become named diagnostics on the system device:

| Field | Entity suffix | Type |
| --- | --- | --- |
| `mode` | Unit mode | Reported string |
| `status` | Unit activity | Reported string |
| `fanSpeedStatus` | Fan speed status | Enum displaying 0=Off, 1=Low, 2=Medium, 3=High |
| `fanSpeedSetpoint` | Fan speed setpoint | Enum displaying 1=Low, 2=Medium, 3=High |
| `fanLevelStatus` | Fan level | Number, scale unestablished |
| `fanLevelSetting` | Fan level setting | Number, scale unestablished |
| `fanOperatingMode` | Fan operating mode | Reported string; constantAirflow observed |

The indoor unit reported mode/status Off while the zone remained configured for Heat, which is why controller operation and selected thermostat mode are separate entities. The user confirmed the Low/Medium/High speed mapping; these are discrete speeds, not RPM, percentages, airflow, or pressure. The level fields remain numeric because their scale is not established. The speed enums retain numeric string states for history/automations and expose `raw_value` for inspection. Unexpected speed values remain unknown rather than receiving a guessed label. No unit-level controls are added. Missing operation fields do not become zeros or off states.

Version 0.6.0 also exposes zone Fan activity (Off/Running) and Fan speed (Off/Low/Medium/High), separate from the selected Fan mode. They use the already-read `features.circulation` response and add no requests. See [fan history and source precedence](HISTORY.md).

Known HeatPumpIdu/HeatPumpOdu equipment is polled at the normal reading interval. A legacy HeatPump aggregate is used only when component types are absent, avoiding duplicate operation sensors for the same system. Each failure is isolated from climate/energy; absent/offline fields make the affected operation entities unavailable.

## TEMCO supply and return sensors

Inventory identified a ReturnAir TEMCO-AQM and a SupplyAir TEMCO-TH, both connected at the observation. Their generic `GET /v1/equipment/{equipmentId}/status` responses contained only health.faults as an empty array. This confirms a status route, not pressure/temperature/humidity telemetry from each physical sensor.

The tested per-sensor suffixes sensor/status, sensor/current, sensor/readings, readings, telemetry/current, measurements, plus return airQuality and supply temperatureHumidity returned 404. System sensors and telemetry/current also returned 404. These bounded guesses do not prove that no other read interface exists.

No pressure readings were obtained. Heat-pump telemetry/metrics/pressure guesses returned HTTP 405, but an intentionally nonexistent sibling path also returned 405 with Allow: POST. This is a generic routing pattern, not proof of those endpoints. No guessed POST or equipment configuration write was attempted. The app's surfacePressure signal is weather-related and must not be relabeled as duct or refrigerant pressure.

## Air-quality access and stale samples

The zone air-quality endpoint returned access full with CO₂, PM2.5, and TVOC values, despite the earlier subscription hypothesis. This establishes access for those reads, not a permanent entitlement policy. Zone readings are not separate supply/return measurements.

Those AQ samples were older than the thermostat/power data. The user's freshness fix is included: samples older than one hour, missing/invalid/naive/future timestamps, settling pollutants, and missing numeric values become unavailable. A stopped fan does not by itself invalidate a recent sample. The source last_updated_at, per-pollutant measured_at/settling, access, and missing entitlement attributes help distinguish these conditions.
