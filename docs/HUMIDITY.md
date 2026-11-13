# How humidity control works in this app

The app contains a concrete **humidifier** control path. It has an enable switch and a target relative-humidity percentage. It does not establish a user-facing dehumidification target.

## Confirmed behavior in Jetson Home 1.2.8

The home-screen code reads `GET /v1/zones/{zoneId}/status` and only creates its Humidifier control when:

```text
features.humidity exists
AND features.humidity.capabilities exists
AND features.humidity.capabilities.modes includes "Humidify"
```

The key distinction is between **sensing humidity** and **advertising a controllable humidifier**. `currentRelativeHumidity` can be present without control capabilities. A humidity reading alone does not make the button appear.

Tapping the control opens the app route `/(app)/(active)/humidity`. The page is labelled Humidifier, presents an **Enabled** switch, and changes **HUMIDITY %** with increase/decrease controls. The bounds and increment come from the server's capabilities. There is no fixed target range hard-coded in this traced UI.

Saving calls:

```http
PATCH /v1/zones/{zoneId}/humidity/settings
Content-Type: application/json
Authorization: Bearer <access-token>
```

```json
{"mode":"Humidify","setpoint":{"value":45}}
```

This example means enabled with a target of **45% RH**; it is an illustrative payload, not a suggested household setting. Turning the app switch off sends mode `Off` while retaining the target. The request schema permits changing mode or target separately; at least one field must be supplied. The response type is the full humidity settings object, not `{result: "ok"}`.

## Fields to inspect after installation

### Live confirmation on 2026-11-13

After Jetson enabled the installed humidifier in the system configuration,
`GET /v1/zones/{zoneId}/status` advertised `Humidify` and returned this humidity
feature (account and device identifiers omitted):

```json
{
  "status": "Humidifying",
  "currentRelativeHumidity": 29.8,
  "currentDisplayRelativeHumidity": 30,
  "settings": {"mode": "Humidify", "setpoint": {"value": 40}},
  "capabilities": {
    "modes": ["Off", "Humidify"],
    "setpoint": {"min": 20, "max": 50, "precision": 5}
  }
}
```

These limits describe this installation, not a universal range. The earlier
response lacked capabilities; physical wiring alone had not enabled API control.
No additional humidity read endpoint is necessary: zone status includes the current
RH, target, enable mode, activity, and capabilities. Tested GET requests to
`/humidity`, `/humidity/current`, and `/humidity/capabilities` returned 404;
GET `/humidity/settings` returned 405 with `Allow: PATCH`. The PATCH contract
above remains based on recovered app code and automated protocol tests; this
investigation sent no live humidifier commands.

Home Assistant discovers the existing optional humidifier entity on the next
successful zone poll when these capabilities appear. Re-adding the account is
unnecessary. If it does not appear, reload the integration and check for an
existing disabled humidifier entity. Version 0.7.1 adds regression coverage for
this response and rechecks current capability limits inside the command lock.
Target requests are rounded to the advertised increment; turning on/off preserves
the target, and setting a target does not implicitly turn on the humidifier.

### Field reference

Within `features.humidity`:

| Field | Meaning |
| --- | --- |
| `currentRelativeHumidity` | Current measured RH percentage |
| `currentDisplayRelativeHumidity` | Display-rounded current RH |
| `status` | `Off` or `Humidifying` |
| `settings.mode` | `Off` or `Humidify` |
| `settings.setpoint.value` | Target RH percentage |
| `capabilities.modes` | Advertised controllable modes |
| `capabilities.setpoint.min` / `max` | Supported target limits |
| `capabilities.setpoint.precision` | Supported target increment, in percentage points |

Capabilities are optional in the schema. A device can be enabled in Humidify mode while its current status is Off, because it is not actively adding moisture at that moment. The exact humidity hysteresis, heating/fan interlocks, weather protection, and runtime policy live outside the client code and remain unknown.

## Hardware evidence and what it implies

Equipment schemas explicitly define:

- Equipment type `Humidifier`.
- Model marker `HUM-3P`.
- Humidifier technology `Evaporative` or `Steam`.
- `boardId`, `parentEquipmentId`, and `zoneIds` associations.
- Installation metadata and humidifier create/update schemas.

The create schema describes the parent equipment ID as the **parent heat pump equipment**. `HUM-3P` strongly suggests a third-party humidifier accessory; the meaning of that abbreviation is an inference rather than a vendor statement. Together with the UI labels, these fields support the interpretation that Jetson controls an installed humidifier accessory, rather than the heat pump itself supplying water or steam.

The app does **not** establish the electrical wiring, output voltage, relay type, terminal labels, compatible accessory models, or which 4-ton hardware revisions support the function. No accessory-registration API route is asserted merely from finding the schema. Commissioning should use the installer-supported workflow.

For installation planning, the concrete point to establish with Jetson is whether the supplied 4-ton model supports the desired evaporative/steam humidifier and whether it will be installed, wired, and registered so the zone advertises the Humidify capability. This investigation cannot determine that before the unit is commissioned.

## What about removing humidity?

There is a `Dehumidifying` value in the **ambient-temperature operating-status** enum. It may describe a backend or firmware operating state; the client does not explain the trigger.

However:

- Humidity command modes are only `Off` and `Humidify`.
- HVAC command modes are only `Off`, `Heat`, `Cool`, `Auto`, and `FanOnly`.
- No dehumidification RH target, `Dry` command, or user-facing dehumidifier-control route was found.
- The recovered heat-pump settings schema contains heat-strip enablement and heating/cooling temperature offsets, not a dehumidification target.

Consequently, this APK supports **verified humidifier-control code**, but it does not prove independent active dehumidification control. A status enum alone is insufficient to implement a “dehumidify” command. Jetson's [public cooling explanation](https://jetsonhome.com/us/support/how-heat-pumps-work) says longer cooling cycles improve humidity control; that is compatible with moisture removal during cooling but does not document an independent RH setpoint.

## Home Assistant mapping

### Installed, disabled, and active are different states (0.8.0)

- **No advertised humidifier capability:** do not create the humidifier control,
  enable switch, or activity binary sensor. RH measurement alone is insufficient.
- **Installed and disabled:** capability remains present but `settings.mode` is
  `Off`. Keep the controls and saved target visible; Humidifier enabled is off.
- **Installed and enabled:** `settings.mode` is `Humidify`. Humidifier enabled is
  on, even while the humidifier is idle. This switch uses the same mode setting as
  the humidifier entity and Jetson app; it does not remove equipment configuration.
- **Actually humidifying:** the Humidifier activity binary sensor is on only for
  reported `status: Humidifying`. A reported `Off` status gives off; unexpected or
  missing status is unknown. Offline devices and withdrawn capabilities make the
  entity unavailable, not a fabricated off reading.

The enable switch sends only mode, preserving the saved target. Target changes do
not enable a seasonally disabled humidifier. All entities remain grouped under the
existing system device, with zone names for multi-zone systems. Previously created
entities become unavailable if capabilities disappear; their history is retained.

Relay humidifiers may have `connectionStatus: Unknown` because they have no
independent connection telemetry. Do not infer connectivity from enabled mode or
humidification demand. Version 0.8.0 omits that diagnostic unless Connected or
Disconnected is explicitly reported, and removes this entry's existing unknown
humidifier connection record on configuration refresh/reload.

### Hours of humidification per day

Create a **History Stats** helper using the new Humidifier activity binary sensor,
tracked state `on`, type `time`, start `{{ today_at('00:00') }}`, and end
`{{ now() }}`. This reports hours since local midnight. For daily long-term totals,
use state class `total_increasing`. See the official
[History Stats documentation](https://www.home-assistant.io/integrations/history_stats/).

Equivalent YAML (replace the illustrative entity ID with yours):

```yaml
sensor:
  - platform: history_stats
    name: Humidifier hours today
    unique_id: jetson_humidifier_hours_today
    entity_id: binary_sensor.main_humidifier_activity
    state: "on"
    type: time
    start: "{{ today_at('00:00') }}"
    end: "{{ now() }}"
    state_class: total_increasing
```

Keep the activity entity included in Recorder. Tracking begins with available HA
history; it cannot recover previous runtime or device activity during HA outages.
Accuracy is limited by cloud updates and the configured polling interval. This
measures reported humidification activity, not independently verified water flow.

The prototype exposes an RH sensor whenever humidity telemetry is present. It creates a separate optional **humidifier entity** only when `Humidify` is advertised with valid min/max/precision values. That entity supports on/off, current RH, and target RH. It does not create a dehumidifier entity or claim that humidifier hardware is installed based on temperature or RH sensing alone.

Setting a target does not implicitly enable humidification; enabling is a separate command. Commands are followed by polling. Live reading of a commissioned humidifier is confirmed above; Home Assistant writes and the physical response to those writes have not been tested on hardware.

## Exact local evidence

| Evidence | Decoded source location / schema |
| --- | --- |
| Humidity control visibility | `analysis/jetson.js` L1132556–1132597; home-screen capability check |
| Home-screen humidity navigation | L1133372–1133379 |
| Enable switch and save body | L1283041–1283110; `HumidityControlContent`, generator `#39142` |
| Target bounds and increment | L1283194–1283237 |
| Reads settings and capabilities | L1283868–1283966; `useZoneHumidityControl`, `#39163` |
| Mutation calls API helper | L1284180–1284207; generator `#39175` |
| Actual PATCH URL and method | L923545–923609; `updateHumiditySettings`, generator `#30793` |
| Humidity fields and enums | Schema modules 2426, 2427, 2428 |
| Partial update / full response | Schema module 2573 |
| Accessory types and associations | Schema modules 2375, 2381, 2385, 2386, 2527 |

These line numbers refer to the local pseudocode file generated during this analysis, not to original source files. Relevant excerpts are preserved in `analysis/humidity-evidence.txt`; the full decoded bundle stays outside the integration package.
