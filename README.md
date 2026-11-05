# Jetson Home for Home Assistant

![Jetson Home](custom_components/jetson_home/brand/icon.png)

Experimental custom integration built by reverse engineering the user-supplied Jetson Home Android app **1.2.8**. It uses the Jetson cloud API. Live authentication and empty-account discovery have been validated, and the user has shown the earlier device layout loaded in HA with reported equipment. The new consolidated layout, displayed readings, and physical controls still need live validation.

## What is included

- One climate entity per advertised temperature zone: current and target temperature, Off/Heat/Cool/Auto/FanOnly commands, and supported fan speeds.
- Temperature and relative-humidity sensors when those features are reported.
- One Home Assistant device per Jetson system, containing all its zone controls/readings and named equipment-connectivity diagnostics. Multiple systems remain separate.
- Separate HVAC mode/activity and selected/current fan mode/activity/speed sensors for Recorder/history, with no additional API calls.
- Main and named per-load power/daily-energy sensors, plus separate heat-strip watts, with source timestamps and local-midnight energy resets.
- Zone connection/issues, telemetry status with a last-device-reading attribute, and reported per-unit operation/fan diagnostics.
- Zone air-quality classification, plus CO₂, PM2.5, and TVOC measurements when a matching monitor and full API access are reported. Restricted access exposes only the overall classification.
- An optional humidifier entity with on/off and target percentage, only when the zone advertises `Humidify` capability and valid limits.
- Schedule-paused status, an explicit Resume schedule button, and a Circulation minutes per hour number (0–60), when their source fields are reported. See [schedule/circulation controls](docs/SCHEDULES.md).
- Email magic-link setup, refresh-token rotation, reauthentication, configurable polling, and allowlisted diagnostics.
- [API guide](docs/API.md), [43-operation endpoint inventory](docs/endpoints.md), [309-definition schema catalog](docs/schema-catalog.md), [OpenAPI 3.1 reference](docs/openapi.json), and [humidity investigation](docs/HUMIDITY.md).
- [Home Assistant device/entity structure](docs/HA_STRUCTURE.md), including power, energy, and diagnostic sensors.
- [Live energy API and HA mapping](docs/ENERGY.md), [new status fields and pressure findings](docs/LIVE_TELEMETRY.md), a [live OpenAPI supplement](docs/live-openapi.json), and [community hardware reports / schedule design](docs/COMMUNITY_REPORTS.md).
- [Separate AQ current and history endpoints](docs/AIR_QUALITY_API.md), including required history parameters, response fields, and live-search limits. These bring the combined API inventory to 47 distinct operations; integration polling is unchanged.

**Status (prototype 0.7.0):** 150 protocol/model/polling/migration/telemetry tests pass, using a local HTTP mock server and in-memory registry adapters. Authorized live reads established populated inventory, zone and heat-pump status, full air-quality access, and the current energy route on November 3–4, 2026. A calendar-day energy reset was observed across local midnight. Earlier auth/empty-account responses matched recovered schemas. HA entity loading, consolidation, Recorder/Energy statistics, and physical controls still need runtime checks. See [validation scope](docs/VALIDATION.md).

Version 0.7.0 adds Schedule paused, Resume schedule, and Circulation minutes per hour. They use existing status data and write only on explicit actions. Resume targets the currently reported paused schedule and kind; circulation duration sends only the selected minutes. See [control behavior](docs/SCHEDULES.md). Main/per-load/heat-strip readings, fan history with Low/Medium/High labels, and English/Spanish/French localization remain available. Last device reading remains an unrecorded attribute, and the stale-AQ fix is preserved: samples older than one hour, settling pollutants, and invalid/missing/future timestamps are unavailable. An idle fan alone does not invalidate recent measurements.

Version 0.4.0 consolidates the earlier hub/equipment/zone rows under the existing system device, moves registered entities before removing empty old rows, and keeps entity IDs. Zone and equipment names distinguish the combined device's entities. Device-based automations referring to removed device IDs need their device selected again; entity-based references keep their IDs. See [grouping and migration](docs/HA_STRUCTURE.md) and [history sensors](docs/HISTORY.md).

Version 0.3.0 separates routine readings from configuration discovery. Discovery runs at startup/reload and through **Refresh configuration** in Jetson Home's options menu. See [polling and manual discovery](docs/POLLING.md).

Version 0.2.1 bundles Jetson's official app icon and website wordmark, with normal/high-resolution images and a dark-theme wordmark. Home Assistant loads these from the integration's `brand` folder. When updating an existing install, copy the complete `jetson_home` folder, restart Home Assistant, and refresh the browser. See [image sources](custom_components/jetson_home/brand/README.md).

## Install with HACS

The prototype targets **Home Assistant 2026.10 or later**. In HACS, open the three-dot menu and choose **Custom repositories**. Add `https://github.com/grahamsz/jetson-home-assistant` with type **Integration**, then download **Jetson Home (experimental)** and restart Home Assistant. New GitHub releases can be installed through HACS. See [HACS's custom-repository instructions](https://hacs.dev/docs/faq/custom_repositories/).

For a manual install, copy `custom_components/jetson_home` into your Home Assistant configuration directory, producing `/config/custom_components/jetson_home/manifest.json`, then restart Home Assistant. The full project ZIP includes documentation and tests; the integration folder is the part installed in HA.

## Connect and test your account

1. Open **Settings → Devices & services → Add integration → Jetson Home**.
2. Enter the email address used in the Jetson app. Leave the second form open while retrieving the email.
3. Copy the new sign-in link from the email **without opening it**, paste it into the form, and submit. A token parameter alone is also accepted. Links may expire or be single use; those server rules have not been measured. Restart setup to request another link if necessary.
4. An account with no commissioned systems should finish setup with zero devices and entities. Reload the integration and restart HA to check that the login is retained. Live protocol checks succeeded with an empty account, and the earlier populated-device layout has been observed in HA.
5. Once equipment is installed, finish Wi-Fi setup and account association in Jetson's official app. This integration does not provision hardware.
6. Check reported temperatures and modes against the official app before relying on automations. Use one ordinary change at a time and confirm the app and equipment respond.

An account with no systems can be added before installation. After commissioning, choose **Refresh configuration** from Jetson Home's options menu, or reload the integration, to discover systems, boards/hubs, equipment, and zones. Devices can be registered from inventory even when their numeric telemetry is not available.

Account setup creates a separate entry and credential set for each email address. Robust handling of account-email changes and two accounts sharing the same physical system is still pending; configure each system through one account for this prototype.

Jetson Home's options menu has **Polling interval** and **Refresh configuration** actions. Routine polling defaults to 30 seconds and can be changed to 30–900 seconds. It reads known zones' status, eligible air quality, energy for systems with a known EnergyMonitor, and selected heat-pump units' status. Equipment connection checks run separately after five minutes, adding `1 + system_count` reads. Fresh zone connectivity from the status response takes priority over cached system health. These reads do not discover or rename hardware or change zone membership.

Startup, reload, and **Refresh configuration** perform a full scan. An empty account makes no background discovery requests. For one system, one zone, air quality, an energy monitor, and indoor/outdoor heat-pump units, an ordinary update uses five reads, a connectivity update seven, and a full refresh nine. Authentication renewal can add requests. See [request schedules and failure behavior](docs/POLLING.md).

API outages make affected entities unavailable; device communication can still fail even when cloud reads succeed. HTTP 200 with `result: "unreachable"` is treated as a failed command. Optional inventory or air-quality errors are isolated from climate updates. Commands are not optimistically reported as physical changes.

## Installed monitors

Each API system is one service device named for the system. Its climate entities and sensor names identify the zone, while connection diagnostics identify the relevant equipment. Hubs, equipment, and zone membership remain in the discovered configuration without creating extra HA device rows. Existing zone and equipment entity unique IDs are preserved when display names or grouping change.

Air-quality telemetry comes from a **zone** endpoint without a physical source ID. It is shown as a zone-named reading on the system device, without copying it onto each installed monitor. Detailed pollutant values require `access: full`; Jetson's limited response exposes only the overall level. The overall sensor's attributes show `access` and, when reported, `missing_entitlement: jetson_care`. Account diagnostics include the access state and whether the request failed. An API error or null measurement is never reported as zero.

Power and daily-energy readings use the confirmed energy/current endpoint. The Main total's coverage depends on clamp placement: equipment circuits or whole-home consumption. Named load and heat-strip readings remain separate. Daily kWh sensors use total plus an explicit timezone-aware reset; source freshness and invalid values are checked. Residual, load, and heat-strip values are not added to Main totals. Choose Energy-dashboard roles based on verified coverage and check statistics in your instance; see [energy mapping and caveats](docs/ENERGY.md).

## Humidity

The recovered UI controls a **humidifier**, with `Off` / `Humidify` and a target percentage. The app models third-party evaporative and steam humidifier equipment. A humidity sensor reading alone does not mean humidification is available. The API must advertise the capability. See [the full findings](docs/HUMIDITY.md).

No user-selectable dehumidification target or Dry command was found. An operating status named `Dehumidifying` exists, which does not by itself prove that a user can request it.

## Current limitations

- Requires Jetson's cloud; no supported local control was established from this app. Retired local-network code and a developer-server selector are documented separately.
- Four-ton model identifiers occur in several equipment families. Compatibility cannot be established from tonnage alone.
- Jetson's `Auto` maps to Home Assistant `heat_cool`. The recovered write endpoint accepts **one shared Celsius target**. Separate heat/cool targets are retained as diagnostic attributes if reported, but are not independently writable. The integration intentionally rejects low/high target writes rather than inventing a route.
- Fan modes are `auto`, `1`, `2`, `3`, limited by the zone's advertised maximum. Actual fan behavior in FanOnly and interactions with circulation need hardware validation.
- Target temperatures are rounded to the reported Celsius step, including Fahrenheit requests converted by Home Assistant. Exact Fahrenheit/Celsius rounding behavior needs comparison with hardware.
- Weekly-program/preset/vacation editing, installer settings, and equipment provisioning are documented but not implemented. Schedule pause status and explicit resume are available when reported. No pressure read interface or separate TEMCO temperature/humidity read was established by the tested routes.
- Air quality is enabled for zones associated with reported TEMCO-AQM equipment, using explicit zone/equipment membership or the reported parent equipment when the peripheral has no own zone assignment. Missing or different installation metadata may require adjustments after hardware validation.
- Reported equipment is grouped under the system device. Hardware inventory does not guarantee a numeric measurement; equipment without a connection-status field gets no fabricated connectivity entity.
- Some API fields are explicitly deprecated but still required by the app's schema. The client supports the recovered newer fields and selected older temperature/fan fields; live schema drift may need adjustments.
- Account/device identifiers remain in Home Assistant's local configuration and registries. Access and refresh tokens are stored in Home Assistant config-entry storage. Do not share that storage or authentication links. Diagnostics export an allowlist without tokens, names, addresses, or IDs.

## Development checks

Use Python with the dependencies in `requirements-test.txt`:

```text
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
python -m compileall -q custom_components tests tools
```

These tests run without Home Assistant installed. They verify HTTP requests against a local mock service, token rotation/concurrency, failure behavior, command formats, schema references, capability checks, polling schedules, cross-system identity separation, access-gated pollutant readings, history-state mappings, and consolidation using in-memory registry adapters. They do not substitute for a Home Assistant registry/Recorder runtime test or device testing.

For installation-day discovery without Home Assistant, run `python tools/probe.py --email your-address`. It requests a sign-in email, accepts the link through a hidden terminal prompt, performs only discovery/status GETs after login, and prints selected readings and capabilities with identifiers omitted. It never sends HVAC/humidifier commands or saves tokens. Jetson may rotate tokens independently between sessions; account behavior is unverified.

The source folder and ZIP include the integration, tests, documentation, and the probe. Decompiled app code and downloaded reverse-engineering tools are kept outside the deliverable.

## License and attribution

The integration source is distributed under the repository's [GNU Affero General Public License v3.0](LICENSE). Jetson's brand images remain Jetson Home's artwork and trademarks; see [brand attribution](custom_components/jetson_home/brand/README.md). This is an unofficial integration.
