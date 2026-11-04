# Research record and provenance

Analysis date: **November 3, 2026**. Source: the user-provided, already extracted APK directory. No original APK ZIP hash is available from that directory, and files outside it were not searched for private account data.

## App identity

| Item | Value |
| --- | --- |
| Display name | Jetson Home |
| Android package | `com.jetsonhome.app` |
| Version from `assets/app.config` | `1.2.8` |
| React Native version recorded in bundle | `0.81.5` |
| Hermes bytecode version | `96` |
| Primary code asset | `assets/index.android.bundle` |
| Asset bytes | `7,991,108` |
| SHA-256 | `fca4fe0ad5872a4ef62516b9012d2ee5775421276f301467ee4d7a4c735ab1cb` |

The app supports over-the-air updates through Expo. Findings are tied to this exact bundle, not every build advertising version 1.2.8 or a later runtime bundle.

## Method

1. Listed extracted APK files and inspected the Expo configuration, protocol files, and compiled bundle signature.
2. Downloaded [P1sec/hermes-dec](https://github.com/P1sec/hermes-dec), version 0.1.8, source revision `2e796663e1fedb93dca51060797ebf3327b3fedb`.
3. Disassembled the Hermes bytecode to `analysis/jetson.hasm` and reconstructed pseudocode to `analysis/jetson.js`.
4. Traced HTTP URL construction, methods, headers, auth response validation, zone-status polling, and climate/humidity UI paths.
5. Extracted declarative schema modules and reconstructed their type information with a symbolic Zod implementation. Only the selected declarative schema modules were evaluated; no application entry point, HTTP calls, refinement callbacks, or device functions were run.
6. Built an independently written asynchronous Python client and custom integration. Tested protocol behavior with synthetic data against a local HTTP server.

The downloaded decoder retains its own license in `tools/hermes-dec`. Decoder source and decoded vendor application code are not included in the integration ZIP. The new integration does not embed the decoder or depend on it at runtime.

## Reproduce locally from the extracted directory

With Python and a local copy of hermes-dec:

```text
python tools/hermes-dec/src/hermes_dec/disassembly/hbc_disassembler.py assets/index.android.bundle analysis/jetson.hasm
python tools/hermes-dec/src/hermes_dec/decompilation/hbc_decompiler.py assets/index.android.bundle analysis/jetson.js
python analysis/inventory.py
node analysis/recover_schemas.cjs
python analysis/build_api_docs.py
```

The helper scripts are in the surrounding analysis workspace, not the runtime integration package. `analysis/read_excerpt.py` prints numbered sections of the pseudocode. `analysis/describe_schema.py` prints compact definitions from the recovered schema JSON.

## Source index

Line numbers below refer to `analysis/jetson.js`, generated with the revision above. Function identifiers are available in the disassembly and remain a useful cross-check independent of pseudocode layout.

| Subject | Location |
| --- | --- |
| Production/staging/local environment constants | L741493–741524 |
| Zone-status hook and 10-second polling | L741811–742001 |
| Zone-status cache freshness / numeric refresh constant | L741929–741933; L763357–763360 |
| Temperature-command 500 ms debounce and optimistic state | L1176775–1176803; L1176978–1176992; L1177042–1177154 |
| Authentication HTTP helpers | L803014–804145 |
| System/equipment/zone schemas | Schema modules 2370–2458 and 2505–2581; extracted in `analysis/schema-evidence.txt` |
| API client default app-version header | L910707–910725 |
| Install ID and bearer header interceptor | L911041–911075 |
| Install ID loaded from secure storage or generated as UUID v4 | L920823–920857; storage key at L920996 |
| Retired local-network mode | L921026–921168 |
| Main HTTP helper functions | L921674–924240 |
| Developer local-server availability check | L970551–970606 |
| Developer Local-environment UI | L970055–970082 |
| Home-screen humidity capability gate | L1132556–1132597 |
| Humidity UI, limits, save, and hooks | L1283041–1284460 |
| BLE provisioning service and endpoint constants | L1319482–1319491 |
| Generic React Native WebSocket registration | L112729–112740; implementation at L121987 onward |
| Sentry EventSource/WebSocket monitoring list | L646940–646951 |
| Energy-monitor MQTT provisioning schema | L904500–904529; monitor message at L1346552 |

`analysis/check_realtime.py` also inspected DEX string tables for MQTT/SSE client clues. The native `text/event-stream` constant points to `expo.modules.kotlin.devtools.ExpoNetworkInspectOkHttpInterceptorsKt.shouldParseBody`, an Expo network-inspection helper. The inventory is saved as `analysis/native-realtime-inventory.txt`. This targeted static check found no native MQTT-client naming clue; obfuscation or dynamically supplied endpoints cannot be ruled out from string searches alone.

## Reconstruction limits

The full pseudocode is not executable source and must not be treated as an exact reconstruction of the original application. In particular, the decoder sometimes prints computed object property writes as numeric register indices; the schema reconstruction corrects this for object writes while preserving literal array indices. Property names, enums, units, and HTTP command bodies central to the integration were reviewed directly in the corresponding decoded code/disassembly.

The symbolic schema layer models primitives, strict/loose objects, arrays, literals, enums, unions, nullable/optional fields, partial/extend/omit, and common limits. It records rather than executes refinement/transform callbacks. JavaScript Date coercion is annotated as a wire-format validation item. Non-declarative validators, server-side checks, dynamic backend defaults, DST behavior, and field-level authorization are not reconstructed. Recovered schema methods/constructors have no unresolved placeholders, but this does not make arbitrary callback validation complete.

An empty extraction-failure list means all selected schema modules were interpreted successfully. It is not evidence that all backend types, routes, or behaviors have been discovered. Bundled duplicate or administrative types can describe functionality the homeowner app does not call. Public schema names omit compiled module numbers; duplicate names receive an `Alternate` suffix, and `x-source-module` retains provenance separately. Neither the schema name nor its source-module number is a field sent to the API. The endpoint list excludes paths inferred solely from type names, UI routes, third-party SDKs, analytics endpoints, or generic network libraries.

## What was not done

User-authorized production checks on November 3–4, 2026 returned HTTP 200 for authentication, inventory, zone/heat-pump status, air quality, and energy/current; see [validation status](VALIDATION.md). Five recovered response schemas matched the initial auth/empty-account data. Later populated-account reads established additional fields and a keyed energy response differing from the bundle. Those observations are recorded separately in [live telemetry](LIVE_TELEMETRY.md), [energy](ENERGY.md), and [live OpenAPI](live-openapi.json). No device discovery on the user's LAN, packet capture, BLE connection, certificate installation, app modification, firmware extraction, OTA changes, hardware wiring, or system commissioning was performed. No physical control commands were sent. Home Assistant runtime compatibility, cloud quota, hardware control behavior, and local-network protocols remain unverified.

The next useful evidence is an HA runtime check of the new entities, energy reset/statistics behavior over more days, and comparison with the official app for one supported control change at a time. Pressure and separate TEMCO temperature/humidity reads were not established by the tested routes. The read-only probe and Home Assistant diagnostics support further checks without exporting credentials.
