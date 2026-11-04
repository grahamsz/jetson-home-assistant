# Validation status and installation-day checks

## Completed on November 3–4, 2026

- **109 passing tests** of the independent protocol client, data model, device grouping, polling scheduler, history-state mappings, registry consolidation, energy, newer telemetry, and air-quality freshness. Protocol requests run against a local HTTP mock service; migration tests use in-memory registry adapters.
- Covered real HTTP methods/bodies, discovery, optional features, empty accounts, legacy temperature fields, auth exchange, expiry, rotating refresh tokens, parallel refresh, one-time 401 retry, persistent 401, permission errors, 429 handling, redirects, malformed JSON, schema drift, invalid inputs, device-unreachable results, and no replay of failed writes.
- Checked humidity-control eligibility against the exact app condition plus valid advertised target limits.
- Checked all reconstructed schema references and key HVAC/humidity enums; no unresolved constructor/method placeholders or extraction failures.
- Python syntax, linting, and formatting verified for the custom integration, tests, and probe.
- OpenAPI 3.1 and JSON Schema documents passed structural validation. This checks document structure, not live API compatibility.
- Cross-checked Home Assistant 2026.10's public climate/humidifier properties, Probatio config-flow schemas, coordinator entry handling, and automatic options-reload API against the project's published source/docs.
- Added hardware-inventory and air-quality tests for stable gateway/device/zone identities, cross-system ID separation, parent fallback/cycles, restricted access, null measurements, and optional endpoint failures.
- Cross-checked `via_device_id` registry linking, sensor device classes, and the current density/ratio unit enums against Home Assistant 2026.10's source.
- Checked startup versus measurement request counts, five-minute connectivity scheduling, explicit discovery of new/removed zones, unchanged topology during health reads, failure rollback, access changes, empty-account background silence, and serialization of overlapping measurement/configuration requests. The options-menu wiring still needs a live HA runtime check.
- Checked consolidation of legacy board/equipment/zone records into one system device, stable entity IDs, disabled entities and inherited areas, multiple accounts/systems, idempotency, and keeping records with unrelated entities or child components. These are adapter tests, not a live HA registry migration.
- Checked selected HVAC mode versus actual activity, off versus idle, valid fan settings, and unknown/invalid state handling. The new enum sensors use existing status data; actual Recorder writes still need an HA runtime check.
- Checked keyed energy/load responses, null versus zero, signed power, invalid numbers, source freshness, daily corrections, local-midnight/DST reset calculation, malformed responses, component-unit selection, and optional endpoint failure isolation.
- Checked newer zone connectivity priority, telemetry metadata, health-only outdoor responses, raw operation fields without invented units, and the user's one-hour stale-AQ cutoff including recovery, timezone offsets, invalid/future timestamps, settling, and idle-fan behavior.

Fixtures are synthetic examples based on recovered types and observed response shapes; private captures are excluded from the repository. The tests load the protocol modules without Home Assistant and use in-memory adapters for registry tests. A user-provided HA screenshot confirms the earlier layout appeared with one system, a hub, six equipment connection entities, and a zone with four entities. It does not show the raw air-quality response or establish subscription access. Consolidation, new entities, displayed values, Recorder/Energy statistics, and physical control behavior still need live HA validation.

## Live endpoint checks: November 3, 2026

At the user's request, production magic-link sign-in requests were sent using the prototype's client, `appScheme: "jetsonhome"`, and a generated installation UUID. Both returned HTTP 200, and the user confirmed email receipt. A newly supplied magic-link token was then exchanged directly with the fixed API endpoint, without navigating to the link. The subsequent checks used the integration's protocol client.

| Method / endpoint | Observed result | Validation scope |
| --- | --- | --- |
| `POST /v1/auth/sign-in/magic-link` | HTTP 200; email received | JSON object parsed; full response schema not checked |
| `POST /v1/auth/verify/magic-link` | HTTP 200 | Matched recovered response schema; access-token lifetime 3,600 seconds |
| `GET /v1/users/me` | HTTP 200 | Matched recovered account response schema |
| `GET /v1/systems` | HTTP 200; `systems: []` | Matched recovered response schema; zero systems, so populated entries remain untested |
| `GET /v1/airQuality/classification` | HTTP 200 | Matched recovered classification response schema; this is a classification definition, not an installed sensor reading |
| `POST /v1/auth/refresh` | HTTP 200 | Matched recovered response schema; new access token, same refresh token, 3,600-second lifetime |

A second `/v1/systems` read succeeded with the refreshed credentials. The refresh was requested immediately to exercise the protocol; waiting for natural expiry was not tested. One unchanged refresh token does not establish its long-term rotation or revocation rules. JSON Schema matching does not execute the original app's annotated Zod refinement/transform callbacks.

At that initial check the account returned no commissioned systems. Later populated-account reads are recorded below. No device commands were sent. Credentials were held only in process memory and not saved; the redacted initial result contains only route names, statuses, schema outcomes, counts, and token-change/lifetime metadata. Private account/device records and token values are omitted from published artifacts.

## Populated-account reads: November 3–4, 2026

Authorized GETs returned HTTP 200 for systems, boards, equipment, zones, zone status, zone air quality, and indoor/outdoor heat-pump status. The current zone response added connectivity/issues and health telemetry status/observation time. The indoor unit added an operation object; the outdoor response contained health only. Both supply and return TEMCOs reported Connected, but their generic equipment-status responses contained only `health.faults: []`.

`GET /v1/systems/{systemId}/energy/current` returned whole-home and keyed per-load watts and daily kWh. A reset of today's totals and date was observed across local midnight. Pre-midnight load totals did not reconcile with the whole-home total and included a negative residual, so these fields are not combined into a new consumption figure. Energy and status additions are documented in the separate [live OpenAPI supplement](live-openapi.json), [energy reference](ENERGY.md), and [telemetry/pressure findings](LIVE_TELEMETRY.md). The original 309 recovered definitions remain unchanged.

The observed air-quality access was `full`, including CO₂/PM2.5/TVOC. Its source timestamp was several hours older than thermostat/power data. The stale-AQ change intentionally makes such readings unavailable rather than treating a successful HTTP response as a fresh sample. Bounded read-only pressure guesses found no pressure readings; generic HTTP 405 routing was also reproduced with a deliberately nonexistent sibling path and is not evidence of another usable endpoint. No guessed write routes or physical controls were exercised.

## Once the 4T is commissioned

1. Confirm the official app lists the installed equipment and reports the expected zone readings.
2. Record the actual model identifier, board type, and firmware version. Four-ton enum entries occur in multiple product families.
3. Run `tools/probe.py` or add the integration. The empty-account login flow has passed a live protocol test; validate populated equipment, board, zone, and status response shapes before testing controls.
4. Compare indoor temperature, displayed target, mode, current activity, humidity reading, and fan settings with the official app. Test Fahrenheit display conversion separately from API Celsius values.
5. For humidity, inspect `features.humidity.capabilities.modes`. A humidity sensor alone is insufficient; `Humidify` must be advertised. Record min/max/precision and confirm the separately installed humidifier is configured in Jetson's supported workflow.
6. Test one ordinary target-temperature change and verify the new target in the official app. Record cloud propagation delay. Repeat for a supported mode/fan change, including FanOnly's fixed-speed behavior.
7. If a humidifier is installed and advertised, test target and enable/disable separately. Compare configured mode with actual `Humidifying` activity. Do not infer dehumidification control from the ambient `Dehumidifying` status.
8. Observe at least one token renewal and a Home Assistant restart. Confirm rotating tokens survive the config-entry update and options changes reload only once. Check coexistence with the official app account session.
9. Compare behavior during a cloud outage and when the hub is offline. Verify device-unreachable results and stale cloud readings do not look like successful physical changes.
10. Check manual changes while a native schedule or vacation is active. Determine override duration and resume behavior before creating automations that depend on them.
11. Confirm each system appears as one device, containing zone-named climate/readings and equipment-named connection diagnostics. After updating from 0.3.x, confirm entity IDs are retained and empty legacy device rows disappear. Re-select the system device in any automations that used old device IDs.
12. Compare permitted CO₂/PM2.5/TVOC values and units with the app. Check limited access, missing/settling readings, one-hour staleness, fresh-sample recovery, and idle-fan behavior. Inspect source timestamps before comparing samples. Compare whole-home and named-load W/kWh with Jetson, verify timezone and next midnight reset, and inspect Recorder statistics before choosing Energy-dashboard sources.
13. Open Jetson Home's options menu and select **Refresh configuration**. Confirm the scan completes without requesting another email or changing the polling interval. After adding/renaming equipment or a zone in Jetson, confirm routine readings leave the configured topology unchanged until a manual refresh or reload. Compare ordinary measurement traffic with the separate inventory-connectivity reads after five minutes.
14. Verify HVAC mode, Fan mode, and HVAC activity have separate History entries. A selected Heat mode with no current demand should report `heat` and `idle`, respectively; unknown activity should remain unknown. Check fan settings against the app and your Recorder filters/retention.
15. Inspect the overall air-quality sensor's attributes or downloaded integration diagnostics. `access: limited` plus `missing_entitlement: jetson_care` confirms restricted server access. Missing values alone, or a screenshot showing fewer entities, does not prove the subscription state.
16. Inspect zone Connection, Telemetry status, and Last device reading. Compare unit operation mode/status and fan fields to the app where shown. Confirm a health-only unit creates no fabricated operation values, and optional energy/unit-read failures leave thermostat polling running.

## Useful non-secret evidence

The probe exports selected readings and capabilities with names and IDs omitted. Home Assistant diagnostics additionally describe which features exist and whether split temperature targets are reported. Those outputs are suitable for narrowing schema/behavior problems after review.

Do not share authentication links, access/refresh tokens, `.storage/core.config_entries`, raw app logs, or unredacted network captures. Network captures can contain credentials even when routine status values appear harmless. If deeper captures become necessary, keep them local and redact credentials before sharing excerpts.

## Open questions

- Magic-link token lifetime and single-use rules; independent sessions and refresh-token revocation.
- Actual API success/error status codes and rate limits.
- Whether all configured zones expose the same features and whether capabilities change with firmware/installation.
- Auto mode's shared target versus reported heat/cool targets; independent range writes were not established.
- Offline connectivity freshness and system health behavior across supported model families.
- Humidifier hardware compatibility, wiring, interlocks, hysteresis, weather protection, and activation policy.
- What causes the ambient `Dehumidifying` status and whether any independently controlled dehumidification is available outside this app.
- Whether any current firmware provides a local interface; retired/developer client paths do not establish one.
