# Jetson Home for Home Assistant

![Jetson Home](custom_components/jetson_home/brand/icon.png)

Experimental custom integration built by reverse engineering the user-supplied Jetson Home Android app **1.2.8**. It uses the Jetson cloud API. The intended hardware is a Jetson 4-ton heat pump. Live authentication and empty-account discovery have been validated; installed hardware remains untested.

## What is included

- One climate entity per advertised temperature zone: current and target temperature, Off/Heat/Cool/Auto/FanOnly commands, and supported fan speeds.
- Temperature and relative-humidity sensors when those features are reported.
- Reported hubs and physical equipment registered as distinct devices with explicit gateway relationships, model/serial metadata when supplied, and diagnostic equipment-connectivity entities.
- Zone air-quality classification, plus CO₂, PM2.5, and TVOC measurements when a matching monitor and full API access are reported. Restricted access exposes only the overall classification.
- An optional humidifier entity with on/off and target percentage, only when the zone advertises `Humidify` capability and valid limits.
- Email magic-link setup, refresh-token rotation, reauthentication, configurable polling, and allowlisted diagnostics.
- [API guide](docs/API.md), [43-operation endpoint inventory](docs/endpoints.md), [309-definition schema catalog](docs/schema-catalog.md), [OpenAPI 3.1 reference](docs/openapi.json), and [humidity investigation](docs/HUMIDITY.md).
- [Home Assistant device/entity structure](docs/HA_STRUCTURE.md), including what remains unfinished for energy monitoring.

**Status (prototype 0.3.0):** 62 protocol/model/topology/polling tests pass, with protocol requests exercised against a local mock server. Live magic-link verification, account lookup, empty-system discovery, air-quality classification, and token refresh returned HTTP 200 with matching recovered response schemas on November 3, 2026. Formatting, linting, and Python syntax are checked. Real Home Assistant loading and installed-device responses/behavior still require testing. See [validation scope](docs/VALIDATION.md).

Version 0.3.0 separates routine readings from configuration discovery. Discovery runs at startup/reload and through **Refresh configuration** in Jetson Home's options menu. See [polling and manual discovery](docs/POLLING.md).

Version 0.2.1 bundles Jetson's official app icon and website wordmark, with normal/high-resolution images and a dark-theme wordmark. Home Assistant loads these from the integration's `brand` folder. When updating an existing install, copy the complete `jetson_home` folder, restart Home Assistant, and refresh the browser. See [image sources](custom_components/jetson_home/brand/README.md).

## Install with HACS

The prototype targets **Home Assistant 2026.10 or later**. In HACS, open the three-dot menu and choose **Custom repositories**. Add `https://github.com/grahamsz/jetson-home-assistant` with type **Integration**, then download **Jetson Home (experimental)** and restart Home Assistant. New GitHub releases can be installed through HACS. See [HACS's custom-repository instructions](https://hacs.dev/docs/faq/custom_repositories/).

For a manual install, copy `custom_components/jetson_home` into your Home Assistant configuration directory, producing `/config/custom_components/jetson_home/manifest.json`, then restart Home Assistant. The full project ZIP includes documentation and tests; the integration folder is the part installed in HA.

## Connect and test your account

1. Open **Settings → Devices & services → Add integration → Jetson Home**.
2. Enter the email address used in the Jetson app. Leave the second form open while retrieving the email.
3. Copy the new sign-in link from the email **without opening it**, paste it into the form, and submit. A token parameter alone is also accepted. Links may expire or be single use; those server rules have not been measured. Restart setup to request another link if necessary.
4. An account with no commissioned systems should finish setup with zero devices and entities. Reload the integration and restart HA to check that the login is retained. Live protocol checks succeeded with an empty account; the HA runtime flow remains to be verified.
5. Once equipment is installed, finish Wi-Fi setup and account association in Jetson's official app. This integration does not provision hardware.
6. Check reported temperatures and modes against the official app before relying on automations. Use one ordinary change at a time and confirm the app and equipment respond.

An account with no systems can be added before installation. After commissioning, choose **Refresh configuration** from Jetson Home's options menu, or reload the integration, to discover systems, boards/hubs, equipment, and zones. Devices can be registered from inventory even when their numeric telemetry is not available.

Account setup creates a separate entry and credential set for each email address. Robust handling of account-email changes and two accounts sharing the same physical system is still pending; configure each system through one account for this prototype.

Jetson Home's options menu has **Polling interval** and **Refresh configuration** actions. Routine polling defaults to 30 seconds and can be changed to 30–900 seconds. It reads known zones' status and eligible air quality: `zone_count + air_quality_zone_count` requests per ordinary cycle. Connection status is updated separately on the next poll after five minutes, adding `1 + system_count` reads for configured systems' health/equipment. Those checks update liveness only; they do not discover or rename hardware or change zone membership.

Startup, reload, and **Refresh configuration** perform a full scan: `1 + 3 × system_count + zone_count + air_quality_zone_count` reads. An empty account makes no background discovery requests. For one zone with an air-quality monitor, an ordinary update uses two reads, a connectivity update uses four, and a full configuration refresh uses six. Authentication renewal can add requests. See [request schedules and failure behavior](docs/POLLING.md).

API outages make affected entities unavailable; device communication can still fail even when cloud reads succeed. HTTP 200 with `result: "unreachable"` is treated as a failed command. Optional inventory or air-quality errors are isolated from climate updates. Commands are not optimistically reported as physical changes.

## Installed monitors

The integration registers an API system as a service device, its reported hubs as physical devices, and hardware equipment beneath the reported gateway. Zone-level climate and aggregate measurements stay under a zone service device. Physical equipment keeps its API identifier even when its display name changes. Existing zone entity IDs from 0.1.0 are preserved.

Air-quality telemetry comes from a **zone** endpoint without a physical source ID. It is kept on the zone, rather than copied onto each installed monitor. Detailed pollutant values require `access: full`; Jetson's limited response exposes only the overall level. An API error or null measurement is never reported as zero.

**Energy consumption is not implemented yet.** An installed energy monitor can be registered as hardware and report connectivity, but no W/kWh sensors are created. The bundle contains energy response schemas without an established read route. The presence of hardware alone is insufficient to create usable Energy-dashboard measurements. See [the mapping and remaining work](docs/HA_STRUCTURE.md).

## Humidity

The recovered UI controls a **humidifier**, with `Off` / `Humidify` and a target percentage. The app models third-party evaporative and steam humidifier equipment. A humidity sensor reading alone does not mean humidification is available. The API must advertise the capability. See [the full findings](docs/HUMIDITY.md).

No user-selectable dehumidification target or Dry command was found. An operating status named `Dehumidifying` exists, which does not by itself prove that a user can request it.

## Current limitations

- Requires Jetson's cloud; no supported local control was established from this app. Retired local-network code and a developer-server selector are documented separately.
- Four-ton model identifiers occur in several equipment families. Compatibility cannot be established from tonnage alone.
- Jetson's `Auto` maps to Home Assistant `heat_cool`. The recovered write endpoint accepts **one shared Celsius target**. Separate heat/cool targets are retained as diagnostic attributes if reported, but are not independently writable. The integration intentionally rejects low/high target writes rather than inventing a route.
- Fan modes are `auto`, `1`, `2`, `3`, limited by the zone's advertised maximum. Actual fan behavior in FanOnly and interactions with circulation need hardware validation.
- Target temperatures are rounded to the reported Celsius step, including Fahrenheit requests converted by Home Assistant. Exact Fahrenheit/Celsius rounding behavior needs comparison with hardware.
- Schedules, presets, vacation, energy telemetry, installer settings, and equipment provisioning are documented but not implemented as entities or services.
- Air quality is enabled for zones associated with reported TEMCO-AQM equipment, using explicit zone/equipment membership or the reported parent equipment when the peripheral has no own zone assignment. Missing or different installation metadata may require adjustments after hardware validation.
- A reported hub/monitor is a registry device; that does not guarantee a numeric measurement or a live sensor. Hardware without a reported connectivity field is registered without a fabricated connectivity entity.
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

These tests run the protocol/model modules without importing Home Assistant. They verify real HTTP requests against a local mock service, token rotation/concurrency, failure behavior, command formats, schema references, capability checks, device graph plans, cross-system identity separation, and access-gated pollutant readings. They do not substitute for a Home Assistant runtime test or device testing.

For installation-day discovery without Home Assistant, run `python tools/probe.py --email your-address`. It requests a sign-in email, accepts the link through a hidden terminal prompt, performs only discovery/status GETs after login, and prints selected readings and capabilities with identifiers omitted. It never sends HVAC/humidifier commands or saves tokens. Jetson may rotate tokens independently between sessions; account behavior is unverified.

The source folder and ZIP include the integration, tests, documentation, and the probe. Decompiled app code and downloaded reverse-engineering tools are kept outside the deliverable.

## License and attribution

The integration source is distributed under the repository's [GNU Affero General Public License v3.0](LICENSE). Jetson's brand images remain Jetson Home's artwork and trademarks; see [brand attribution](custom_components/jetson_home/brand/README.md). This is an unofficial integration.
