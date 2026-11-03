# Validation status and installation-day checks

## Completed on November 3, 2026

- **48 passing tests** of the independent protocol client, data model, and device topology. Protocol requests run against a local HTTP mock service.
- Covered real HTTP methods/bodies, discovery, optional features, empty accounts, legacy temperature fields, auth exchange, expiry, rotating refresh tokens, parallel refresh, one-time 401 retry, persistent 401, permission errors, 429 handling, redirects, malformed JSON, schema drift, invalid inputs, device-unreachable results, and no replay of failed writes.
- Checked humidity-control eligibility against the exact app condition plus valid advertised target limits.
- Checked all reconstructed schema references and key HVAC/humidity enums; no unresolved constructor/method placeholders or extraction failures.
- Python syntax, linting, and formatting verified for the custom integration, tests, and probe.
- OpenAPI 3.1 and JSON Schema documents passed structural validation. This checks document structure, not live API compatibility.
- Cross-checked Home Assistant 2026.10's public climate/humidifier properties, Probatio config-flow schemas, coordinator entry handling, and automatic options-reload API against the project's published source/docs.
- Added hardware-inventory and air-quality tests for stable gateway/device/zone identities, cross-system ID separation, parent fallback/cycles, restricted access, null measurements, and optional endpoint failures. Energy-monitor metadata is tested without claiming consumption telemetry.
- Cross-checked `via_device_id` registry linking, sensor device classes, and the current density/ratio unit enums against Home Assistant 2026.10's source.

Fixtures are invented from recovered types, not captured from a physical device. The tests deliberately load the protocol modules without Home Assistant. Home Assistant runtime setup, config-flow UI, entity/platform loading, and real equipment communication remain untested.

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

The account has no commissioned systems, so no system-specific board/equipment/zone endpoints or physical controls could be tested. No device commands were sent. Credentials were held only in process memory and not saved; the redacted local result contains only route names, statuses, schema outcomes, counts, and token-change/lifetime metadata. Account records, email addresses, device IDs, installation UUIDs, and token values are omitted from published artifacts.

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
11. Confirm the hub, air-quality monitor, and energy monitor appear as separate devices with the reported model/serial and gateway links. Zone aggregate entities should remain on their zone service device.
12. Compare permitted CO₂/PM2.5/TVOC values and units with the app. Check limited Jetson Care access, missing readings, and connectivity behavior. Energy W/kWh entities remain pending a verified read endpoint and should not appear as fabricated measurements.

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
